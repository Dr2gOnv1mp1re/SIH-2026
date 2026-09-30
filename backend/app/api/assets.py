from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.database.session import get_sync_db
from app.database.models import Asset, BusinessService, Vulnerability
from app.api.auth import get_current_user
from app.risk_engine.calculator import calculate_asset_criticality

router = APIRouter(prefix="/assets", tags=["Enterprise Asset Inventory"])

class AssetCreateRequest(BaseModel):
    name: str
    asset_type: str
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    owner: Optional[str] = "IT Operations"
    department: Optional[str] = "Core Banking"
    operating_system: Optional[str] = "Linux RHEL 8"
    business_service_id: Optional[str] = None
    business_importance: float = 80.0
    data_sensitivity: float = 80.0
    revenue_dependency: float = 80.0
    downtime_tolerance_hours: float = 1.0
    regulatory_importance: float = 85.0
    internet_exposed: bool = False
    tags: Optional[List[str]] = []

@router.get("")
def list_assets(
    asset_type: Optional[str] = Query(None),
    internet_exposed: Optional[bool] = Query(None),
    min_criticality: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    query = db.query(Asset).filter(Asset.organization_id == current_user.organization_id)
    
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if internet_exposed is not None:
        query = query.filter(Asset.internet_exposed == internet_exposed)
    if min_criticality is not None:
        query = query.filter(Asset.criticality_score >= min_criticality)
    if search:
        query = query.filter(Asset.name.ilike(f"%{search}%") | Asset.hostname.ilike(f"%{search}%") | Asset.ip_address.ilike(f"%{search}%"))
    
    assets = query.order_by(Asset.criticality_score.desc()).all()
    return assets

@router.get("/template-csv")
def get_asset_csv_template():
    """Returns standard CSV template format for organizational asset import."""
    template_headers = (
        "name,asset_type,ip_address,hostname,owner,department,operating_system,"
        "business_importance,data_sensitivity,revenue_dependency,downtime_tolerance_hours,"
        "regulatory_importance,internet_exposed\n"
        "Core Payment Gateway Cluster,application,194.143.12.8,pay-gw-01.bank.in,Fintech Ops,Payments,Linux RHEL 8,95,95,95,0.5,90,true\n"
        "Customer Records Oracle DB,database,10.100.4.12,db-cust-01.internal,Database Team,Retail Banking,Oracle Enterprise Linux,98,98,90,1.0,95,false\n"
        "Corporate Identity Server,server,10.100.1.10,iam-dc01.corp.internal,IAM Ops,Security,Windows Server 2022,90,85,80,2.0,85,false\n"
    )
    from fastapi.responses import Response
    return Response(
        content=template_headers,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=asset_inventory_template.csv"}
    )

@router.get("/export-csv")
def export_assets_csv(current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    """Exports all organization assets into downloadable CSV format."""
    import csv
    import io
    from fastapi.responses import Response

    assets = db.query(Asset).filter(
        Asset.organization_id == current_user.organization_id
    ).order_by(Asset.criticality_score.desc()).all()

    output = io.StringIO()
    fieldnames = [
        "id", "name", "asset_type", "ip_address", "hostname", "owner", "department",
        "operating_system", "criticality_score", "current_risk_score", "expected_annual_loss",
        "internet_exposed", "business_importance", "data_sensitivity", "revenue_dependency"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for a in assets:
        writer.writerow({
            "id": a.id,
            "name": a.name,
            "asset_type": a.asset_type,
            "ip_address": a.ip_address or "",
            "hostname": a.hostname or "",
            "owner": a.owner or "",
            "department": a.department or "",
            "operating_system": a.operating_system or "",
            "criticality_score": a.criticality_score,
            "current_risk_score": a.current_risk_score,
            "expected_annual_loss": a.expected_annual_loss,
            "internet_exposed": a.internet_exposed,
            "business_importance": a.business_importance,
            "data_sensitivity": a.data_sensitivity,
            "revenue_dependency": a.revenue_dependency
        })

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=organization_asset_inventory.csv"}
    )

@router.get("/{asset_id}")
def get_asset(asset_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.organization_id == current_user.organization_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    vulns = db.query(Vulnerability).filter(Vulnerability.affected_asset_id == asset_id).all()
    bs = db.query(BusinessService).filter(BusinessService.id == asset.business_service_id).first() if asset.business_service_id else None
    
    return {
        "asset": asset,
        "business_service": bs,
        "vulnerabilities": vulns,
        "vulnerability_count": len(vulns),
        "critical_vulnerabilities": sum(1 for v in vulns if v.severity == "CRITICAL")
    }

@router.post("")
def create_asset(request: AssetCreateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    crit = calculate_asset_criticality(
        request.business_importance,
        request.data_sensitivity,
        request.revenue_dependency,
        request.regulatory_importance,
        request.internet_exposed,
        request.downtime_tolerance_hours
    )
    asset = Asset(
        organization_id=current_user.organization_id,
        name=request.name,
        asset_type=request.asset_type,
        ip_address=request.ip_address,
        hostname=request.hostname,
        owner=request.owner,
        department=request.department,
        operating_system=request.operating_system,
        business_service_id=request.business_service_id,
        business_importance=request.business_importance,
        data_sensitivity=request.data_sensitivity,
        revenue_dependency=request.revenue_dependency,
        downtime_tolerance_hours=request.downtime_tolerance_hours,
        regulatory_importance=request.regulatory_importance,
        internet_exposed=request.internet_exposed,
        criticality_score=crit,
        current_risk_score=round(crit * 0.8, 1),
        expected_annual_loss=round(crit * 25000.0, 2),
        tags=request.tags or []
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

class AssetUpdateRequest(BaseModel):
    name: Optional[str] = None
    asset_type: Optional[str] = None
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    operating_system: Optional[str] = None
    business_service_id: Optional[str] = None
    business_importance: Optional[float] = None
    data_sensitivity: Optional[float] = None
    revenue_dependency: Optional[float] = None
    downtime_tolerance_hours: Optional[float] = None
    regulatory_importance: Optional[float] = None
    internet_exposed: Optional[bool] = None
    tags: Optional[List[str]] = None

@router.put("/{asset_id}")
def update_asset(asset_id: str, request: AssetUpdateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.organization_id == current_user.organization_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    for field, val in request.dict(exclude_unset=True).items():
        if val is not None:
            setattr(asset, field, val)
            
    # Recalculate criticality
    asset.criticality_score = calculate_asset_criticality(
        asset.business_importance,
        asset.data_sensitivity,
        asset.revenue_dependency,
        asset.regulatory_importance,
        asset.internet_exposed,
        asset.downtime_tolerance_hours
    )
    db.commit()
    db.refresh(asset)
    return asset

@router.delete("/{asset_id}")
def delete_asset(asset_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.organization_id == current_user.organization_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    db.delete(asset)
    db.commit()
    return {"status": "SUCCESS", "message": f"Asset {asset_id} successfully deleted."}

class CSVContentImportRequest(BaseModel):
    csv_content: str

@router.post("/import-csv")
def import_assets_csv(
    request: CSVContentImportRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Parses and ingests an enterprise asset inventory CSV, computes FAIR criticality parameters,
    and stores records into the organization's inventory.
    """
    import csv
    import io

    content = request.csv_content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="CSV content is empty.")

    reader = csv.DictReader(io.StringIO(content))
    imported_assets = []
    errors = []

    for idx, row in enumerate(reader, start=1):
        name = row.get("name", "").strip()
        if not name:
            errors.append(f"Row {idx}: Missing required 'name' field.")
            continue

        try:
            asset_type = row.get("asset_type", "server").strip().lower()
            ip_address = row.get("ip_address", "").strip() or None
            hostname = row.get("hostname", "").strip() or None
            owner = row.get("owner", "Enterprise Operations").strip()
            department = row.get("department", "Core Technology").strip()
            operating_system = row.get("operating_system", "Linux RHEL 8").strip()

            biz_imp = float(row.get("business_importance", 80.0))
            data_sens = float(row.get("data_sensitivity", 80.0))
            rev_dep = float(row.get("revenue_dependency", 80.0))
            downtime_tol = float(row.get("downtime_tolerance_hours", 1.0))
            reg_imp = float(row.get("regulatory_importance", 85.0))
            
            raw_exposed = str(row.get("internet_exposed", "false")).lower()
            internet_exposed = raw_exposed in ("true", "1", "yes", "t")

            crit = calculate_asset_criticality(
                biz_imp, data_sens, rev_dep, reg_imp, internet_exposed, downtime_tol
            )

            new_asset = Asset(
                organization_id=current_user.organization_id,
                name=name,
                asset_type=asset_type,
                ip_address=ip_address,
                hostname=hostname,
                owner=owner,
                department=department,
                operating_system=operating_system,
                business_importance=biz_imp,
                data_sensitivity=data_sens,
                revenue_dependency=rev_dep,
                downtime_tolerance_hours=downtime_tol,
                regulatory_importance=reg_imp,
                internet_exposed=internet_exposed,
                criticality_score=crit,
                current_risk_score=round(crit * 0.8, 1),
                expected_annual_loss=round(crit * 35000.0, 2),
                tags=["CSV_IMPORTED", "ORGANIZATION_DATA"]
            )
            db.add(new_asset)
            imported_assets.append(name)
        except Exception as err:
            errors.append(f"Row {idx} ({name}): Failed to parse - {str(err)}")

    if imported_assets:
        db.commit()

    return {
        "status": "SUCCESS" if imported_assets else "FAILED",
        "imported_count": len(imported_assets),
        "imported_names": imported_assets,
        "errors": errors,
        "data_origin": "ORGANIZATION-PROVIDED DATA",
        "message": f"Successfully imported {len(imported_assets)} organizational assets into Quantum Risk AI."
    }


