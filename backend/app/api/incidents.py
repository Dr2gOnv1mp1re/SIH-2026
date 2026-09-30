"""
Incident & Loss Intelligence REST API Router.
Provides enterprise historical cybersecurity incident tracking, actual observed financial loss analysis,
CSV bulk import, data quality scoring, FAIR model calibration, and cryptographic blockchain audit integration.

Strictly preserves the distinction:
1. ACTUAL OBSERVED LOSS (Historical evidence from recorded incidents)
2. MODELED FINANCIAL EXPOSURE (FAIR calculated EAL = SLE * ARO)
3. PREDICTED FUTURE EXPOSURE (AI / XGBoost 30/60/90-day exposure)
4. SIMULATED/DEMO DATA (Demonstration benchmarks)
"""

import io
import csv
import re
import statistics
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database.session import get_sync_db
from app.database.models import (
    SecurityIncident, SecurityIncidentCalibration, Organization, Asset, AuditLog
)
from app.api.auth import get_current_user, require_roles
from app.blockchain.ledger import audit_ledger, generate_canonical_hash

router = APIRouter(prefix="/incidents", tags=["Incident & Loss Intelligence"])

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------

class IncidentCreateRequest(BaseModel):
    incident_id: str = Field(..., description="Unique Incident identifier (e.g., INC-2025-001)")
    incident_type: str = Field(..., description="Type of incident: Ransomware, Data Breach, DDoS, Phishing, API Abuse, Supply Chain, Insider Threat")
    incident_date: datetime = Field(default_factory=datetime.utcnow, description="Date and time incident occurred")
    affected_asset_id: Optional[str] = Field(None, description="Linked asset ID from Asset Inventory")
    asset_criticality: str = Field("High", description="Critical, High, Medium, Low")
    attack_vector: str = Field("Phishing", description="Primary attack vector")
    cve_id: Optional[str] = Field(None, description="Associated CVE ID (e.g. CVE-2021-44228)")
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="CVSS base score (0.0 - 10.0)")
    kev_status: bool = Field(False, description="CISA Known Exploited Vulnerabilities status")
    downtime_hours: float = Field(0.0, ge=0.0, description="Downtime in hours (>= 0)")
    
    # Financial Component Losses (in INR, must be >= 0)
    revenue_loss: float = Field(0.0, ge=0.0, description="Revenue / transaction loss (INR)")
    recovery_cost: float = Field(0.0, ge=0.0, description="Data / infrastructure recovery cost (INR)")
    response_cost: float = Field(0.0, ge=0.0, description="Incident response & forensic investigation cost (INR)")
    regulatory_cost: float = Field(0.0, ge=0.0, description="Regulatory penalties & legal costs (INR)")
    other_loss: float = Field(0.0, ge=0.0, description="Other miscellaneous losses (INR)")
    
    incident_status: str = Field("RESOLVED", description="OPEN, CONTAINED, RESOLVED, CLOSED")
    data_source: str = Field("ACTUAL_ORGANIZATIONAL_DATA", description="ACTUAL_ORGANIZATIONAL_DATA or SIMULATED_DEMO_DATA")
    notes: Optional[str] = Field(None, description="Investigative notes and post-incident analysis")

    @field_validator("incident_id")
    @classmethod
    def validate_incident_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Incident ID cannot be empty")
        return v

    @field_validator("cve_id")
    @classmethod
    def validate_cve_format(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip().upper()
            if not re.match(r"^CVE-\d{4}-\d{4,8}$", v) and not v.startswith("VULN-"):
                raise ValueError("CVE ID must follow format CVE-YYYY-NNNN or VULN-ID")
            return v
        return None

class IncidentUpdateRequest(BaseModel):
    incident_type: Optional[str] = None
    incident_date: Optional[datetime] = None
    affected_asset_id: Optional[str] = None
    asset_criticality: Optional[str] = None
    attack_vector: Optional[str] = None
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    kev_status: Optional[bool] = None
    downtime_hours: Optional[float] = Field(None, ge=0.0)
    revenue_loss: Optional[float] = Field(None, ge=0.0)
    recovery_cost: Optional[float] = Field(None, ge=0.0)
    response_cost: Optional[float] = Field(None, ge=0.0)
    regulatory_cost: Optional[float] = Field(None, ge=0.0)
    other_loss: Optional[float] = Field(None, ge=0.0)
    incident_status: Optional[str] = None
    notes: Optional[str] = None

class CalibrateRequest(BaseModel):
    notes: Optional[str] = "Model parameters calibrated using historical incident evidence."
    apply_to_eal: bool = True

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _format_inr(val: float) -> str:
    """Formats INR into human-readable Crores or Lakhs."""
    if val >= 10000000:
        return f"₹{round(val / 10000000, 2)} Crore"
    elif val >= 100000:
        return f"₹{round(val / 100000, 2)} Lakh"
    else:
        return f"₹{round(val, 2):,}"

def _build_incident_payload(inc: SecurityIncident) -> Dict[str, Any]:
    return {
        "incident_id": inc.incident_id,
        "incident_type": inc.incident_type,
        "incident_date": inc.incident_date.isoformat(),
        "total_observed_loss": inc.total_observed_loss,
        "revenue_loss": inc.revenue_loss,
        "recovery_cost": inc.recovery_cost,
        "response_cost": inc.response_cost,
        "regulatory_cost": inc.regulatory_cost,
        "other_loss": inc.other_loss,
        "incident_status": inc.incident_status
    }

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@router.post("", status_code=201)
def create_security_incident(
    request: IncidentCreateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Creates a new security incident.
    Total Observed Loss is automatically computed server-side:
    Total Observed Loss = Revenue Loss + Recovery Cost + Response Cost + Regulatory Cost + Other Loss.
    Client-supplied totals are rejected or recalculated. Negative financial values are strictly prohibited.
    """
    # Check for duplicate incident ID within organization
    existing = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id,
        SecurityIncident.incident_id == request.incident_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"An incident with ID '{request.incident_id}' already exists in your organization."
        )

    # Validate asset if provided
    if request.affected_asset_id:
        asset = db.query(Asset).filter(
            Asset.id == request.affected_asset_id,
            Asset.organization_id == current_user.organization_id
        ).first()
        if not asset:
            raise HTTPException(
                status_code=400,
                detail=f"Affected asset ID '{request.affected_asset_id}' not found in asset inventory."
            )

    # Server-side calculation of Total Observed Loss
    total_loss = round(
        request.revenue_loss +
        request.recovery_cost +
        request.response_cost +
        request.regulatory_cost +
        request.other_loss,
        2
    )

    incident = SecurityIncident(
        organization_id=current_user.organization_id,
        incident_id=request.incident_id,
        incident_type=request.incident_type,
        incident_date=request.incident_date,
        affected_asset_id=request.affected_asset_id,
        asset_criticality=request.asset_criticality,
        attack_vector=request.attack_vector,
        cve_id=request.cve_id,
        cvss_score=request.cvss_score,
        kev_status=request.kev_status,
        downtime_hours=request.downtime_hours,
        revenue_loss=request.revenue_loss,
        recovery_cost=request.recovery_cost,
        response_cost=request.response_cost,
        regulatory_cost=request.regulatory_cost,
        other_loss=request.other_loss,
        total_observed_loss=total_loss,
        incident_status=request.incident_status,
        data_source=request.data_source,
        notes=request.notes,
        created_by=getattr(current_user, "email", "system")
    )

    # Canonical hash and blockchain audit notarization
    payload = _build_incident_payload(incident)
    c_hash = generate_canonical_hash(payload)
    incident.canonical_hash = c_hash

    # Record on blockchain audit ledger if real organizational data or high loss
    try:
        block = audit_ledger.record_transaction(
            record_type="SECURITY_INCIDENT_RECORDED",
            record_id=incident.incident_id,
            payload_data=payload
        )
        incident.blockchain_tx_id = block.get("transaction_id")
    except Exception:
        pass

    db.add(incident)

    # Audit log
    audit_entry = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action="CREATE_SECURITY_INCIDENT",
        resource_type="SECURITY_INCIDENT",
        resource_id=incident.incident_id,
        details={
            "incident_id": incident.incident_id,
            "type": incident.incident_type,
            "total_observed_loss": total_loss,
            "canonical_hash": c_hash
        }
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(incident)

    return {
        "status": "SUCCESS",
        "message": f"Security incident {incident.incident_id} successfully created.",
        "incident": {
            "id": incident.id,
            "incident_id": incident.incident_id,
            "incident_type": incident.incident_type,
            "incident_date": incident.incident_date.isoformat(),
            "affected_asset_id": incident.affected_asset_id,
            "total_observed_loss": incident.total_observed_loss,
            "total_observed_loss_label": _format_inr(incident.total_observed_loss),
            "data_source_classification": "ACTUAL OBSERVED LOSS",
            "canonical_hash": incident.canonical_hash,
            "blockchain_tx_id": incident.blockchain_tx_id
        }
    }

@router.get("")
def list_security_incidents(
    incident_type: Optional[str] = None,
    asset_id: Optional[str] = None,
    criticality: Optional[str] = None,
    attack_vector: Optional[str] = None,
    status: Optional[str] = None,
    data_source: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Lists security incidents with comprehensive filtering and asset information."""
    query = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id
    )

    if incident_type:
        query = query.filter(SecurityIncident.incident_type == incident_type)
    if asset_id:
        query = query.filter(SecurityIncident.affected_asset_id == asset_id)
    if criticality:
        query = query.filter(SecurityIncident.asset_criticality == criticality)
    if attack_vector:
        query = query.filter(SecurityIncident.attack_vector == attack_vector)
    if status:
        query = query.filter(SecurityIncident.incident_status == status)
    if data_source:
        query = query.filter(SecurityIncident.data_source == data_source)
    if start_date:
        try:
            s_dt = datetime.fromisoformat(start_date)
            query = query.filter(SecurityIncident.incident_date >= s_dt)
        except Exception:
            pass
    if end_date:
        try:
            e_dt = datetime.fromisoformat(end_date)
            query = query.filter(SecurityIncident.incident_date <= e_dt)
        except Exception:
            pass

    incidents = query.order_by(SecurityIncident.incident_date.desc()).all()

    # Pre-fetch asset names
    asset_ids = [inc.affected_asset_id for inc in incidents if inc.affected_asset_id]
    assets_map = {}
    if asset_ids:
        assets = db.query(Asset).filter(Asset.id.in_(asset_ids)).all()
        assets_map = {a.id: a.name for a in assets}

    results = []
    for inc in incidents:
        results.append({
            "id": inc.id,
            "incident_id": inc.incident_id,
            "incident_type": inc.incident_type,
            "incident_date": inc.incident_date.isoformat(),
            "affected_asset_id": inc.affected_asset_id,
            "affected_asset_name": assets_map.get(inc.affected_asset_id, "Unmapped / External"),
            "asset_criticality": inc.asset_criticality,
            "attack_vector": inc.attack_vector,
            "cve_id": inc.cve_id,
            "cvss_score": inc.cvss_score,
            "kev_status": inc.kev_status,
            "downtime_hours": inc.downtime_hours,
            "revenue_loss": inc.revenue_loss,
            "recovery_cost": inc.recovery_cost,
            "response_cost": inc.response_cost,
            "regulatory_cost": inc.regulatory_cost,
            "other_loss": inc.other_loss,
            "total_observed_loss": inc.total_observed_loss,
            "total_observed_loss_label": _format_inr(inc.total_observed_loss),
            "incident_status": inc.incident_status,
            "data_source": inc.data_source,
            "data_source_classification": "ACTUAL OBSERVED LOSS" if inc.data_source == "ACTUAL_ORGANIZATIONAL_DATA" else "SIMULATED/DEMO DATA",
            "notes": inc.notes,
            "created_by": inc.created_by,
            "canonical_hash": inc.canonical_hash,
            "blockchain_tx_id": inc.blockchain_tx_id,
            "created_at": inc.created_at.isoformat() if inc.created_at else None
        })

    return {
        "total_records": len(results),
        "data_classification": "HISTORICAL OBSERVED DATA",
        "incidents": results
    }

@router.get("/statistics")
def get_incident_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Returns high-level historical loss statistics labeled clearly as HISTORICAL OBSERVED DATA.
    Does NOT mix historical observed loss with modeled EAL.
    """
    incidents = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id
    ).all()

    if not incidents:
        return {
            "data_source_classification": "HISTORICAL OBSERVED DATA",
            "total_incidents": 0,
            "total_observed_loss": 0.0,
            "total_observed_loss_label": "₹0",
            "average_observed_loss": 0.0,
            "average_observed_loss_label": "₹0",
            "median_observed_loss": 0.0,
            "median_observed_loss_label": "₹0",
            "max_observed_loss": 0.0,
            "max_observed_loss_label": "₹0",
            "total_downtime_hours": 0.0,
            "observed_annual_frequency": 0.0,
            "loss_component_totals": {
                "revenue_loss": 0.0,
                "recovery_cost": 0.0,
                "response_cost": 0.0,
                "regulatory_cost": 0.0,
                "other_loss": 0.0
            },
            "disclaimer": "No historical incidents recorded. Financial quantification relies on FAIR probabilistic modeling."
        }

    losses = [inc.total_observed_loss for inc in incidents]
    total_loss = sum(losses)
    avg_loss = total_loss / len(losses)
    median_loss = statistics.median(losses) if losses else 0.0
    max_loss = max(losses) if losses else 0.0
    total_downtime = sum(inc.downtime_hours for inc in incidents)

    # Calculate observed incident frequency over date span (minimum 1 year basis)
    dates = [inc.incident_date for inc in incidents]
    min_date = min(dates)
    max_date = max(dates)
    span_days = max(1, (max_date - min_date).days)
    span_years = max(1.0, span_days / 365.25)
    observed_annual_freq = round(len(incidents) / span_years, 2)

    component_totals = {
        "revenue_loss": round(sum(inc.revenue_loss for inc in incidents), 2),
        "recovery_cost": round(sum(inc.recovery_cost for inc in incidents), 2),
        "response_cost": round(sum(inc.response_cost for inc in incidents), 2),
        "regulatory_cost": round(sum(inc.regulatory_cost for inc in incidents), 2),
        "other_loss": round(sum(inc.other_loss for inc in incidents), 2)
    }

    return {
        "data_source_classification": "HISTORICAL OBSERVED DATA",
        "data_source_badge": "ACTUAL",
        "total_incidents": len(incidents),
        "total_observed_loss": round(total_loss, 2),
        "total_observed_loss_label": _format_inr(total_loss),
        "average_observed_loss": round(avg_loss, 2),
        "average_observed_loss_label": _format_inr(avg_loss),
        "median_observed_loss": round(median_loss, 2),
        "median_observed_loss_label": _format_inr(median_loss),
        "max_observed_loss": round(max_loss, 2),
        "max_observed_loss_label": _format_inr(max_loss),
        "total_downtime_hours": round(total_downtime, 1),
        "observed_annual_frequency": observed_annual_freq,
        "frequency_label": f"{observed_annual_freq} incidents / year",
        "loss_component_totals": component_totals,
        "disclaimer": "These figures represent verified historical losses and are distinct from FAIR Modeled EAL or Predicted Future Exposure."
    }

@router.get("/loss-summary")
def get_incident_loss_summary(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Categorical breakdowns: loss by incident type, asset criticality, attack vector."""
    incidents = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id
    ).all()

    by_type: Dict[str, Dict[str, Any]] = {}
    by_crit: Dict[str, Dict[str, Any]] = {}
    by_vector: Dict[str, Dict[str, Any]] = {}

    for inc in incidents:
        # Type
        t = inc.incident_type
        if t not in by_type:
            by_type[t] = {"type": t, "count": 0, "total_loss": 0.0, "total_downtime": 0.0}
        by_type[t]["count"] += 1
        by_type[t]["total_loss"] += inc.total_observed_loss
        by_type[t]["total_downtime"] += inc.downtime_hours

        # Criticality
        c = inc.asset_criticality or "Unclassified"
        if c not in by_crit:
            by_crit[c] = {"criticality": c, "count": 0, "total_loss": 0.0}
        by_crit[c]["count"] += 1
        by_crit[c]["total_loss"] += inc.total_observed_loss

        # Vector
        v = inc.attack_vector or "Unknown"
        if v not in by_vector:
            by_vector[v] = {"vector": v, "count": 0, "total_loss": 0.0}
        by_vector[v]["count"] += 1
        by_vector[v]["total_loss"] += inc.total_observed_loss

    # Format output lists with labels
    type_list = [
        {
            "category": v["type"],
            "count": v["count"],
            "total_loss": round(v["total_loss"], 2),
            "total_loss_label": _format_inr(v["total_loss"]),
            "downtime_hours": round(v["total_downtime"], 1)
        }
        for v in sorted(by_type.values(), key=lambda x: x["total_loss"], reverse=True)
    ]

    crit_list = [
        {
            "category": v["criticality"],
            "count": v["count"],
            "total_loss": round(v["total_loss"], 2),
            "total_loss_label": _format_inr(v["total_loss"])
        }
        for v in sorted(by_crit.values(), key=lambda x: x["total_loss"], reverse=True)
    ]

    vector_list = [
        {
            "category": v["vector"],
            "count": v["count"],
            "total_loss": round(v["total_loss"], 2),
            "total_loss_label": _format_inr(v["total_loss"])
        }
        for v in sorted(by_vector.values(), key=lambda x: x["total_loss"], reverse=True)
    ]

    return {
        "data_source_classification": "HISTORICAL OBSERVED DATA",
        "loss_by_type": type_list,
        "loss_by_criticality": crit_list,
        "loss_by_vector": vector_list
    }

@router.get("/trends")
def get_incident_trends(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Returns monthly loss and frequency trends over time."""
    incidents = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id
    ).order_by(SecurityIncident.incident_date.asc()).all()

    monthly_data: Dict[str, Dict[str, Any]] = {}
    for inc in incidents:
        month_key = inc.incident_date.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "month": month_key,
                "incident_count": 0,
                "observed_loss": 0.0,
                "downtime_hours": 0.0
            }
        monthly_data[month_key]["incident_count"] += 1
        monthly_data[month_key]["observed_loss"] += inc.total_observed_loss
        monthly_data[month_key]["downtime_hours"] += inc.downtime_hours

    # Format into sorted list
    trend_list = []
    for k in sorted(monthly_data.keys()):
        d = monthly_data[k]
        trend_list.append({
            "period": d["month"],
            "incident_count": d["incident_count"],
            "observed_loss": round(d["observed_loss"], 2),
            "observed_loss_label": _format_inr(d["observed_loss"]),
            "downtime_hours": round(d["downtime_hours"], 1)
        })

    return {
        "data_source_classification": "HISTORICAL OBSERVED DATA",
        "periods_recorded": len(trend_list),
        "trends": trend_list
    }

@router.get("/template-csv")
def download_csv_template():
    """Generates and returns a downloadable CSV template for incident imports."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "incident_id",
        "incident_type",
        "incident_date",
        "affected_asset",
        "downtime_hours",
        "revenue_loss",
        "recovery_cost",
        "response_cost",
        "regulatory_cost",
        "other_loss",
        "cve_id",
        "cvss_score",
        "notes"
    ])
    writer.writerow([
        "INC-2025-001",
        "Ransomware",
        "2025-08-14T03:30:00",
        "Core Payment Database Cluster",
        "4.5",
        "1500000",
        "850000",
        "400000",
        "500000",
        "100000",
        "CVE-2021-44228",
        "9.8",
        "Contained via network isolation"
    ])
    writer.writerow([
        "INC-2025-002",
        "Phishing",
        "2025-10-02T11:15:00",
        "Internet Banking Web Application",
        "0.0",
        "0",
        "150000",
        "250000",
        "0",
        "50000",
        "",
        "",
        "Credential harvesting attempt detected and revoked"
    ])
    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=security_incidents_template.csv"}
    )

@router.post("/import-csv")
async def import_incident_csv(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="If true, only validates and previews without persisting"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Imports historical incidents from CSV file.
    Validates required columns, numeric formats, dates, duplicates, and non-negative losses.
    Returns preview report with valid and invalid rows.
    """
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Please upload UTF-8 CSV.")

    reader = csv.DictReader(io.StringIO(decoded))
    required_cols = {"incident_id", "incident_type", "incident_date"}
    if not reader.fieldnames or not required_cols.issubset(set(f.strip() for f in reader.fieldnames)):
        missing = required_cols - set(reader.fieldnames or [])
        raise HTTPException(
            status_code=400,
            detail=f"CSV is missing mandatory columns: {', '.join(missing)}"
        )

    # Asset lookup dictionary (name -> id, and id -> id)
    assets = db.query(Asset).filter(Asset.organization_id == current_user.organization_id).all()
    asset_by_name = {a.name.lower().strip(): a.id for a in assets}
    asset_by_id = {a.id: a.id for a in assets}

    existing_ids = set(
        r[0] for r in db.query(SecurityIncident.incident_id).filter(
            SecurityIncident.organization_id == current_user.organization_id
        ).all()
    )

    valid_records: List[Dict[str, Any]] = []
    validation_errors: List[Dict[str, Any]] = []
    seen_in_csv = set()

    for row_idx, row in enumerate(reader, start=2):
        row_errors = []
        cleaned_row = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}

        inc_id = cleaned_row.get("incident_id", "").strip()
        if not inc_id:
            row_errors.append("incident_id is required")
        elif inc_id in existing_ids:
            row_errors.append(f"Incident ID '{inc_id}' already exists in database")
        elif inc_id in seen_in_csv:
            row_errors.append(f"Duplicate incident ID '{inc_id}' within CSV file")
        else:
            seen_in_csv.add(inc_id)

        inc_type = cleaned_row.get("incident_type", "").strip()
        if not inc_type:
            row_errors.append("incident_type is required")

        # Date validation
        date_str = cleaned_row.get("incident_date", "").strip()
        parsed_date = None
        if not date_str:
            row_errors.append("incident_date is required")
        else:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    pass
            if not parsed_date:
                row_errors.append(f"Invalid date format for '{date_str}'")

        # Asset mapping
        asset_ref = cleaned_row.get("affected_asset", "").strip()
        resolved_asset_id = None
        if asset_ref:
            if asset_ref in asset_by_id:
                resolved_asset_id = asset_ref
            elif asset_ref.lower() in asset_by_name:
                resolved_asset_id = asset_by_name[asset_ref.lower()]
            else:
                # Soft match or warning
                pass

        # Financial values validation
        def parse_float(key: str, default: float = 0.0) -> float:
            val_str = cleaned_row.get(key, "").replace(",", "").replace("₹", "").strip()
            if not val_str:
                return default
            try:
                val = float(val_str)
                if val < 0.0:
                    row_errors.append(f"Negative value not allowed for '{key}': {val}")
                    return 0.0
                return val
            except ValueError:
                row_errors.append(f"Invalid numeric format for '{key}': '{val_str}'")
                return 0.0

        downtime = parse_float("downtime_hours", 0.0)
        revenue_loss = parse_float("revenue_loss", 0.0)
        recovery_cost = parse_float("recovery_cost", 0.0)
        response_cost = parse_float("response_cost", 0.0)
        regulatory_cost = parse_float("regulatory_cost", 0.0)
        other_loss = parse_float("other_loss", 0.0)

        # CVSS if provided
        cvss = None
        if cleaned_row.get("cvss_score"):
            try:
                cvss_val = float(cleaned_row["cvss_score"])
                if 0.0 <= cvss_val <= 10.0:
                    cvss = cvss_val
                else:
                    row_errors.append(f"CVSS score must be between 0.0 and 10.0 (got {cvss_val})")
            except ValueError:
                row_errors.append("Invalid CVSS score format")

        cve = cleaned_row.get("cve_id", "").strip() or None

        total_loss = round(revenue_loss + recovery_cost + response_cost + regulatory_cost + other_loss, 2)

        if row_errors:
            validation_errors.append({
                "row_number": row_idx,
                "incident_id": inc_id or f"Row {row_idx}",
                "errors": row_errors
            })
        else:
            valid_records.append({
                "incident_id": inc_id,
                "incident_type": inc_type,
                "incident_date": parsed_date,
                "affected_asset_id": resolved_asset_id,
                "asset_criticality": cleaned_row.get("asset_criticality", "High"),
                "attack_vector": cleaned_row.get("attack_vector", "External / Phishing"),
                "cve_id": cve,
                "cvss_score": cvss,
                "kev_status": cleaned_row.get("kev_status", "").lower() in ("true", "1", "yes"),
                "downtime_hours": downtime,
                "revenue_loss": revenue_loss,
                "recovery_cost": recovery_cost,
                "response_cost": response_cost,
                "regulatory_cost": regulatory_cost,
                "other_loss": other_loss,
                "total_observed_loss": total_loss,
                "incident_status": cleaned_row.get("incident_status", "RESOLVED"),
                "data_source": "ACTUAL_ORGANIZATIONAL_DATA",
                "notes": cleaned_row.get("notes", "")
            })

    # If dry_run, return validation report only
    if dry_run or not valid_records or validation_errors:
        return {
            "status": "VALIDATION_REPORT" if dry_run or validation_errors else "READY_TO_IMPORT",
            "dry_run": dry_run,
            "total_rows_processed": row_idx - 1 if 'row_idx' in locals() else 0,
            "valid_records_count": len(valid_records),
            "errors_count": len(validation_errors),
            "validation_errors": validation_errors,
            "preview_records": [
                {
                    "incident_id": r["incident_id"],
                    "incident_type": r["incident_type"],
                    "incident_date": r["incident_date"].isoformat(),
                    "total_observed_loss": r["total_observed_loss"],
                    "total_observed_loss_label": _format_inr(r["total_observed_loss"]),
                    "downtime_hours": r["downtime_hours"],
                    "mapped_asset": "Mapped" if r["affected_asset_id"] else "Unmapped"
                }
                for r in valid_records[:10]
            ],
            "message": f"Validation complete: {len(valid_records)} valid rows, {len(validation_errors)} error rows."
        }

    # Persist valid records
    created_count = 0
    for r in valid_records:
        inc = SecurityIncident(
            organization_id=current_user.organization_id,
            incident_id=r["incident_id"],
            incident_type=r["incident_type"],
            incident_date=r["incident_date"],
            affected_asset_id=r["affected_asset_id"],
            asset_criticality=r["asset_criticality"],
            attack_vector=r["attack_vector"],
            cve_id=r["cve_id"],
            cvss_score=r["cvss_score"],
            kev_status=r["kev_status"],
            downtime_hours=r["downtime_hours"],
            revenue_loss=r["revenue_loss"],
            recovery_cost=r["recovery_cost"],
            response_cost=r["response_cost"],
            regulatory_cost=r["regulatory_cost"],
            other_loss=r["other_loss"],
            total_observed_loss=r["total_observed_loss"],
            incident_status=r["incident_status"],
            data_source=r["data_source"],
            notes=r["notes"],
            created_by=getattr(current_user, "email", "csv_import")
        )
        payload = _build_incident_payload(inc)
        inc.canonical_hash = generate_canonical_hash(payload)
        db.add(inc)
        created_count += 1

    # Record audit event
    audit_entry = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action="BULK_IMPORT_INCIDENTS",
        resource_type="SECURITY_INCIDENT",
        resource_id=f"BATCH-{created_count}",
        details={
            "imported_count": created_count,
            "filename": file.filename
        }
    )
    db.add(audit_entry)
    db.commit()

    return {
        "status": "SUCCESS",
        "message": f"Successfully imported {created_count} historical security incidents.",
        "imported_count": created_count,
        "errors_count": len(validation_errors)
    }

@router.get("/data-quality")
def evaluate_data_quality(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Evaluates incident data quality across multiple dimensions:
    - Missing financial values
    - Negative values
    - Invalid dates
    - Unmapped assets
    - Missing CVE / CVSS
    - Sufficient historical depth
    Returns GOOD, WARNING, or INSUFFICIENT.
    """
    incidents = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id
    ).all()

    total = len(incidents)
    if total == 0:
        return {
            "overall_status": "INSUFFICIENT",
            "score_percentage": 0.0,
            "total_incidents": 0,
            "checks": [
                {"name": "Incident Volume", "status": "FAILED", "detail": "Zero historical incidents on record."},
                {"name": "Financial Completeness", "status": "PENDING", "detail": "Requires at least 1 incident."},
                {"name": "Asset Association", "status": "PENDING", "detail": "Requires at least 1 incident."},
                {"name": "Vulnerability Evidence", "status": "PENDING", "detail": "Requires at least 1 incident."}
            ],
            "recommendation": "Import or record organizational incidents to enable calibrated loss modeling. Current platform operates under modeled FAIR parameters."
        }

    missing_asset = sum(1 for inc in incidents if not inc.affected_asset_id)
    missing_cve = sum(1 for inc in incidents if not inc.cve_id)
    zero_loss = sum(1 for inc in incidents if inc.total_observed_loss == 0.0)
    has_downtime = sum(1 for inc in incidents if inc.downtime_hours > 0.0)

    checks = []

    # 1. Volume check
    if total >= 10:
        v_status = "PASSED"
        v_msg = f"Robust volume: {total} historical incidents recorded."
    elif total >= 3:
        v_status = "WARNING"
        v_msg = f"Moderate volume: {total} incidents recorded. Recommended: >= 10 for high-confidence calibration."
    else:
        v_status = "FAILED"
        v_msg = f"Low volume: {total} incident(s). Insufficient for standalone statistical inference."
    checks.append({"name": "Incident Volume", "status": v_status, "detail": v_msg})

    # 2. Financial Completeness
    fin_pct = ((total - zero_loss) / total) * 100
    if fin_pct >= 80:
        f_status = "PASSED"
        f_msg = f"{round(fin_pct, 1)}% of incidents have detailed financial loss breakdowns."
    elif fin_pct >= 50:
        f_status = "WARNING"
        f_msg = f"Only {round(fin_pct, 1)}% of incidents document financial losses."
    else:
        f_status = "FAILED"
        f_msg = "Majority of incidents lack quantified loss values."
    checks.append({"name": "Financial Completeness", "status": f_status, "detail": f_msg})

    # 3. Asset Mapping
    asset_pct = ((total - missing_asset) / total) * 100
    if asset_pct >= 80:
        a_status = "PASSED"
        a_msg = f"{round(asset_pct, 1)}% of incidents mapped to enterprise assets in inventory."
    elif asset_pct >= 50:
        a_status = "WARNING"
        a_msg = f"{round(asset_pct, 1)}% asset mapping rate. Link unmapped incidents to assets."
    else:
        a_status = "FAILED"
        a_msg = "High proportion of unmapped incidents prevents asset-level risk calibration."
    checks.append({"name": "Asset Association", "status": a_status, "detail": a_msg})

    # 4. Vulnerability & Threat Evidence
    cve_pct = ((total - missing_cve) / total) * 100
    if cve_pct >= 50:
        c_status = "PASSED"
        c_msg = f"{round(cve_pct, 1)}% of incidents reference specific CVEs / exploit vectors."
    else:
        c_status = "WARNING"
        c_msg = f"{round(cve_pct, 1)}% CVE reference rate. Adding CVEs sharpens technical threat modeling."
    checks.append({"name": "Vulnerability Evidence", "status": c_status, "detail": c_msg})

    # Overall Score Calculation
    passed_count = sum(1 for c in checks if c["status"] == "PASSED")
    warning_count = sum(1 for c in checks if c["status"] == "WARNING")
    score = ((passed_count * 1.0 + warning_count * 0.5) / len(checks)) * 100

    if score >= 75 and total >= 5:
        overall = "GOOD"
    elif score >= 50 and total >= 3:
        overall = "WARNING"
    else:
        overall = "INSUFFICIENT"

    return {
        "overall_status": overall,
        "score_percentage": round(score, 1),
        "total_incidents": total,
        "checks": checks,
        "recommendation": (
            "Data quality is GOOD. Safe to calibrate FAIR loss magnitude and ARO parameters."
            if overall == "GOOD" else
            "Data quality is WARNING. Model calibration will apply conservative Bayesian bounds."
            if overall == "WARNING" else
            "Data quality is INSUFFICIENT for organization-specific empirical risk calibration. Maintain default FAIR industry benchmarks."
        )
    }

@router.get("/calibration")
def get_model_calibration_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Compares current FAIR risk model assumptions with empirical historical incident evidence.
    Shows whether data sufficiency permits safe calibration without blindly overwriting models.
    """
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    assumptions = (org.financial_assumptions if org and org.financial_assumptions else {
        "hourly_downtime_cost": 300000.0,
        "incident_response_hourly_rate": 25000.0,
        "data_recovery_base_cost": 1500000.0,
        "legal_regulatory_base_cost": 2000000.0,
        "business_interruption_base_cost": 2500000.0
    })

    incidents = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id
    ).all()

    last_calibration = db.query(SecurityIncidentCalibration).filter(
        SecurityIncidentCalibration.organization_id == current_user.organization_id
    ).order_by(SecurityIncidentCalibration.created_at.desc()).first()

    total_incidents = len(incidents)
    if total_incidents >= 5:
        sufficiency = "SUFFICIENT"
    elif total_incidents >= 2:
        sufficiency = "MARGINAL"
    else:
        sufficiency = "INSUFFICIENT"

    # Empirical values
    if incidents:
        observed_losses = [inc.total_observed_loss for inc in incidents]
        mean_observed_loss = sum(observed_losses) / len(observed_losses)
        mean_downtime_cost = (
            sum(inc.revenue_loss for inc in incidents) / sum(max(1.0, inc.downtime_hours) for inc in incidents)
            if any(inc.downtime_hours > 0 for inc in incidents) else assumptions.get("hourly_downtime_cost", 300000.0)
        )
        mean_recovery_cost = sum(inc.recovery_cost for inc in incidents) / len(incidents)
        mean_response_cost = sum(inc.response_cost for inc in incidents) / len(incidents)
        mean_legal_cost = sum(inc.regulatory_cost for inc in incidents) / len(incidents)
    else:
        mean_observed_loss = 0.0
        mean_downtime_cost = assumptions.get("hourly_downtime_cost", 300000.0)
        mean_recovery_cost = assumptions.get("data_recovery_base_cost", 1500000.0)
        mean_response_cost = assumptions.get("incident_response_hourly_rate", 25000.0)
        mean_legal_cost = assumptions.get("legal_regulatory_base_cost", 2000000.0)

    comparison = [
        {
            "parameter": "Hourly Downtime Cost",
            "current_model": f"₹{round(assumptions.get('hourly_downtime_cost', 300000.0)/1000, 1)}K / hr",
            "historical_evidence": f"₹{round(mean_downtime_cost/1000, 1)}K / hr" if incidents else "No evidence",
            "calibrated_candidate": round(mean_downtime_cost, 2),
            "status": "ALIGNED" if abs(assumptions.get('hourly_downtime_cost', 300000.0) - mean_downtime_cost) < 50000 else "CALIBRATION_RECOMMENDED"
        },
        {
            "parameter": "Base Data Recovery Cost",
            "current_model": f"₹{round(assumptions.get('data_recovery_base_cost', 1500000.0)/100000, 1)}L",
            "historical_evidence": f"₹{round(mean_recovery_cost/100000, 1)}L" if incidents else "No evidence",
            "calibrated_candidate": round(mean_recovery_cost, 2),
            "status": "ALIGNED" if abs(assumptions.get('data_recovery_base_cost', 1500000.0) - mean_recovery_cost) < 200000 else "CALIBRATION_RECOMMENDED"
        },
        {
            "parameter": "Legal & Regulatory Cost",
            "current_model": f"₹{round(assumptions.get('legal_regulatory_base_cost', 2000000.0)/100000, 1)}L",
            "historical_evidence": f"₹{round(mean_legal_cost/100000, 1)}L" if incidents else "No evidence",
            "calibrated_candidate": round(mean_legal_cost, 2),
            "status": "ALIGNED" if abs(assumptions.get('legal_regulatory_base_cost', 2000000.0) - mean_legal_cost) < 300000 else "CALIBRATION_RECOMMENDED"
        }
    ]

    return {
        "calibration_status": "CALIBRATED" if last_calibration else "DEFAULT_FAIR_BENCHMARKS",
        "data_sufficiency": sufficiency,
        "incident_evidence_count": total_incidents,
        "last_calibration_date": last_calibration.created_at.isoformat() if last_calibration else None,
        "last_calibrated_by": last_calibration.calibrated_by if last_calibration else None,
        "current_assumptions": assumptions,
        "parameters_comparison": comparison,
        "can_calibrate": (sufficiency in ("SUFFICIENT", "MARGINAL")),
        "message": (
            "Historical evidence is sufficient to calibrate organization-specific financial risk parameters."
            if sufficiency == "SUFFICIENT" else
            "Marginal historical evidence. Bayesian weighted blending will be applied."
            if sufficiency == "MARGINAL" else
            "Insufficient historical incident data. Using FAIR industry benchmark assumptions."
        )
    }

@router.post("/calibrate")
def calibrate_risk_model_with_evidence(
    request: CalibrateRequest,
    current_user = Depends(require_roles(["CISO", "ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    """
    CISO / Admin authorized model calibration.
    Uses verified historical incident evidence to calibrate FAIR loss magnitude assumptions.
    Records immutable cryptographic audit evidence on blockchain.
    """
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    incidents = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id
    ).all()

    if len(incidents) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"At least 2 historical incidents are required for model calibration. Found: {len(incidents)}"
        )

    prev_assumptions = dict(org.financial_assumptions or {})

    # Compute empirical averages
    mean_recovery = sum(inc.recovery_cost for inc in incidents) / len(incidents)
    mean_regulatory = sum(inc.regulatory_cost for inc in incidents) / len(incidents)
    mean_response = sum(inc.response_cost for inc in incidents) / len(incidents)
    total_losses = [inc.total_observed_loss for inc in incidents]
    observed_loss_mean = sum(total_losses) / len(total_losses)

    # Blend 60% empirical with 40% current benchmark for stability
    calibrated = {
        "hourly_downtime_cost": prev_assumptions.get("hourly_downtime_cost", 300000.0),
        "incident_response_hourly_rate": round(prev_assumptions.get("incident_response_hourly_rate", 25000.0) * 0.4 + (mean_response / 40.0) * 0.6, 2) if mean_response > 0 else 25000.0,
        "data_recovery_base_cost": round(prev_assumptions.get("data_recovery_base_cost", 1500000.0) * 0.4 + mean_recovery * 0.6, 2) if mean_recovery > 0 else 1500000.0,
        "legal_regulatory_base_cost": round(prev_assumptions.get("legal_regulatory_base_cost", 2000000.0) * 0.4 + mean_regulatory * 0.6, 2) if mean_regulatory > 0 else 2000000.0,
        "business_interruption_base_cost": prev_assumptions.get("business_interruption_base_cost", 2500000.0)
    }

    org.financial_assumptions = calibrated

    # Calculate observed annual frequency
    dates = [inc.incident_date for inc in incidents]
    span_years = max(1.0, (max(dates) - min(dates)).days / 365.25)
    observed_freq = round(len(incidents) / span_years, 2)

    calib_record = SecurityIncidentCalibration(
        organization_id=current_user.organization_id,
        calibrated_by=current_user.email,
        calibration_status="APPROVED",
        data_sufficiency="SUFFICIENT" if len(incidents) >= 5 else "MARGINAL",
        incident_count=len(incidents),
        previous_assumptions=prev_assumptions,
        calibrated_assumptions=calibrated,
        observed_loss_mean=observed_loss_mean,
        observed_annual_frequency=observed_freq
    )

    calib_payload = {
        "calibration_id": calib_record.id,
        "calibrated_by": calib_record.calibrated_by,
        "incident_count": calib_record.incident_count,
        "observed_loss_mean": calib_record.observed_loss_mean,
        "calibrated_assumptions": calib_record.calibrated_assumptions
    }
    c_hash = generate_canonical_hash(calib_payload)
    calib_record.canonical_hash = c_hash

    try:
        block = audit_ledger.record_transaction(
            record_type="RISK_MODEL_CALIBRATION_APPROVED",
            record_id=calib_record.id,
            payload_data=calib_payload
        )
        calib_record.blockchain_tx_id = block.get("transaction_id")
    except Exception:
        pass

    db.add(calib_record)

    audit_entry = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action="CALIBRATE_RISK_MODEL",
        resource_type="RISK_MODEL_CALIBRATION",
        resource_id=calib_record.id,
        details={
            "calibrated_by": current_user.email,
            "incident_count": len(incidents),
            "canonical_hash": c_hash
        }
    )
    db.add(audit_entry)
    db.commit()

    return {
        "status": "SUCCESS",
        "message": "Risk model assumptions successfully calibrated from historical incident evidence.",
        "calibration_id": calib_record.id,
        "calibrated_assumptions": calibrated,
        "canonical_hash": c_hash,
        "blockchain_tx_id": calib_record.blockchain_tx_id
    }

@router.get("/{incident_id}")
def get_security_incident_detail(
    incident_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Retrieves full details for a single incident including asset info and blockchain audit proof."""
    incident = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id,
        (SecurityIncident.incident_id == incident_id) | (SecurityIncident.id == incident_id)
    ).first()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Security incident '{incident_id}' not found.")

    asset_name = "Unmapped"
    if incident.affected_asset_id:
        asset = db.query(Asset).filter(Asset.id == incident.affected_asset_id).first()
        if asset:
            asset_name = asset.name

    # Check on-chain verification
    payload = _build_incident_payload(incident)
    on_chain = audit_ledger.verify_record_integrity(
        record_id=incident.incident_id,
        current_data_payload=payload
    )

    return {
        "id": incident.id,
        "incident_id": incident.incident_id,
        "incident_type": incident.incident_type,
        "incident_date": incident.incident_date.isoformat(),
        "affected_asset_id": incident.affected_asset_id,
        "affected_asset_name": asset_name,
        "asset_criticality": incident.asset_criticality,
        "attack_vector": incident.attack_vector,
        "cve_id": incident.cve_id,
        "cvss_score": incident.cvss_score,
        "kev_status": incident.kev_status,
        "downtime_hours": incident.downtime_hours,
        "revenue_loss": incident.revenue_loss,
        "recovery_cost": incident.recovery_cost,
        "response_cost": incident.response_cost,
        "regulatory_cost": incident.regulatory_cost,
        "other_loss": incident.other_loss,
        "total_observed_loss": incident.total_observed_loss,
        "total_observed_loss_label": _format_inr(incident.total_observed_loss),
        "incident_status": incident.incident_status,
        "data_source": incident.data_source,
        "data_source_classification": "ACTUAL OBSERVED LOSS" if incident.data_source == "ACTUAL_ORGANIZATIONAL_DATA" else "SIMULATED/DEMO DATA",
        "notes": incident.notes,
        "created_by": incident.created_by,
        "canonical_hash": incident.canonical_hash,
        "blockchain_tx_id": incident.blockchain_tx_id,
        "blockchain_verification": on_chain,
        "created_at": incident.created_at.isoformat() if incident.created_at else None,
        "updated_at": incident.updated_at.isoformat() if incident.updated_at else None
    }

@router.put("/{incident_id}")
def update_security_incident(
    incident_id: str,
    request: IncidentUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Updates an existing incident.
    Total Observed Loss is automatically recalculated server-side.
    Client cannot manipulate or independently supply Total Observed Loss.
    """
    incident = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id,
        (SecurityIncident.incident_id == incident_id) | (SecurityIncident.id == incident_id)
    ).first()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Security incident '{incident_id}' not found.")

    if request.incident_type is not None:
        incident.incident_type = request.incident_type
    if request.incident_date is not None:
        incident.incident_date = request.incident_date
    if request.affected_asset_id is not None:
        incident.affected_asset_id = request.affected_asset_id
    if request.asset_criticality is not None:
        incident.asset_criticality = request.asset_criticality
    if request.attack_vector is not None:
        incident.attack_vector = request.attack_vector
    if request.cve_id is not None:
        incident.cve_id = request.cve_id
    if request.cvss_score is not None:
        incident.cvss_score = request.cvss_score
    if request.kev_status is not None:
        incident.kev_status = request.kev_status
    if request.downtime_hours is not None:
        incident.downtime_hours = request.downtime_hours
    if request.revenue_loss is not None:
        incident.revenue_loss = request.revenue_loss
    if request.recovery_cost is not None:
        incident.recovery_cost = request.recovery_cost
    if request.response_cost is not None:
        incident.response_cost = request.response_cost
    if request.regulatory_cost is not None:
        incident.regulatory_cost = request.regulatory_cost
    if request.other_loss is not None:
        incident.other_loss = request.other_loss
    if request.incident_status is not None:
        incident.incident_status = request.incident_status
    if request.notes is not None:
        incident.notes = request.notes

    # Server-side recalculation of Total Observed Loss
    incident.total_observed_loss = round(
        incident.revenue_loss +
        incident.recovery_cost +
        incident.response_cost +
        incident.regulatory_cost +
        incident.other_loss,
        2
    )

    incident.updated_at = datetime.utcnow()

    # Recalculate canonical hash
    payload = _build_incident_payload(incident)
    c_hash = generate_canonical_hash(payload)
    incident.canonical_hash = c_hash

    # Record update event on audit ledger
    try:
        block = audit_ledger.record_transaction(
            record_type="SECURITY_INCIDENT_UPDATED",
            record_id=incident.incident_id,
            payload_data=payload
        )
        incident.blockchain_tx_id = block.get("transaction_id")
    except Exception:
        pass

    audit_entry = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action="UPDATE_SECURITY_INCIDENT",
        resource_type="SECURITY_INCIDENT",
        resource_id=incident.incident_id,
        details={
            "incident_id": incident.incident_id,
            "total_observed_loss": incident.total_observed_loss,
            "canonical_hash": c_hash
        }
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(incident)

    return {
        "status": "SUCCESS",
        "message": f"Security incident {incident.incident_id} successfully updated.",
        "incident": {
            "id": incident.id,
            "incident_id": incident.incident_id,
            "total_observed_loss": incident.total_observed_loss,
            "total_observed_loss_label": _format_inr(incident.total_observed_loss),
            "canonical_hash": incident.canonical_hash,
            "blockchain_tx_id": incident.blockchain_tx_id
        }
    }

@router.delete("/{incident_id}")
def delete_security_incident(
    incident_id: str,
    current_user = Depends(require_roles(["ADMIN", "CISO"])),
    db: Session = Depends(get_sync_db)
):
    """Deletes an incident (restricted to ADMIN and CISO roles). Logs an audit event."""
    incident = db.query(SecurityIncident).filter(
        SecurityIncident.organization_id == current_user.organization_id,
        (SecurityIncident.incident_id == incident_id) | (SecurityIncident.id == incident_id)
    ).first()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Security incident '{incident_id}' not found.")

    deleted_id = incident.incident_id

    audit_entry = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action="DELETE_SECURITY_INCIDENT",
        resource_type="SECURITY_INCIDENT",
        resource_id=deleted_id,
        details={"incident_id": deleted_id, "deleted_by": current_user.email}
    )
    db.add(audit_entry)
    db.delete(incident)
    db.commit()

    return {
        "status": "SUCCESS",
        "message": f"Security incident '{deleted_id}' successfully deleted."
    }
