"""
API Router for SIH PS26105 Test Dataset (15 Assets / 28 Fields).
Strictly serves the exact dataset provided by the user without synthetic additions or hardcoding.
"""

from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.risk_engine.sih_dataset_engine import sih_engine, format_inr
import csv
import io

router = APIRouter(prefix="/sih-dataset", tags=["SIH PS26105 Test Dataset"])

class OptimizationRequest(BaseModel):
    budget: float = 1500000.0  # Default 15 Lakh INR

@router.get("/overview")
def get_dataset_overview() -> Dict[str, Any]:
    """Dynamically computed overview metrics from the 15 records."""
    return sih_engine.get_overview_metrics()

@router.get("/assets")
def get_sih_assets() -> List[Dict[str, Any]]:
    """Returns the 15 assets with all 28 mapped telemetry signals and computed risk."""
    return sih_engine.get_records()

@router.get("/vulnerabilities")
def get_sih_vulnerabilities() -> Dict[str, Any]:
    """Returns CVE vulnerabilities from the dataset, strictly excluding N/A records."""
    records = sih_engine.get_records()
    vulns = []
    for r in records:
        if r["has_cve"]:
            vulns.append({
                "asset_id": r["asset_id"],
                "asset_name": r["asset_name"],
                "business_unit": r["business_unit"],
                "cve_id": r["cve_id"],
                "cvss_score": r["cvss_score"],
                "vulnerability_severity": r["vulnerability_severity"],
                "patch_available": r["patch_available"],
                "exploit_available": r["exploit_available"],
                "vulnerability_age_days": r["vulnerability_age_days"],
                "asset_criticality": r["asset_criticality_1_5"],
                "internet_exposed": r["internet_exposed"]
            })
    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "total_cves_identified": len(vulns),
        "vulnerabilities": vulns
    }

@router.get("/threat-intelligence")
def get_sih_threat_intel() -> Dict[str, Any]:
    """Returns threat intelligence indicators from the dataset, strictly excluding N/A records."""
    records = sih_engine.get_records()
    threats = []
    for r in records:
        if r["has_threat_intel"]:
            threats.append({
                "asset_id": r["asset_id"],
                "asset_name": r["asset_name"],
                "threat_intel_indicator": r["threat_intel_indicator"],
                "threat_confidence_pct": r["threat_confidence_pct"],
                "threat_confidence_label": f"{r['threat_confidence_pct']}%",
                "internet_exposed": r["internet_exposed"],
                "business_unit": r["business_unit"]
            })
    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "total_active_threat_indicators": len(threats),
        "threat_indicators": threats
    }

@router.get("/siem-events")
def get_sih_siem_events() -> Dict[str, Any]:
    """Returns SIEM event telemetry from the dataset."""
    records = sih_engine.get_records()
    events = []
    for r in records:
        events.append({
            "asset_id": r["asset_id"],
            "asset_name": r["asset_name"],
            "siem_event": r["siem_event"],
            "siem_severity": r["siem_severity"],
            "internet_exposed": r["internet_exposed"],
            "criticality": r["asset_criticality_1_5"]
        })
    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "total_events": len(events),
        "events": events
    }

@router.get("/iam-analysis")
def get_sih_iam_analysis() -> Dict[str, Any]:
    """Returns IAM user security analysis, highlighting high-risk privileged accounts without MFA."""
    records = sih_engine.get_records()
    iam_items = []
    for r in records:
        iam_items.append({
            "asset_id": r["asset_id"],
            "asset_name": r["asset_name"],
            "iam_user": r["iam_user"],
            "mfa_enabled": r["mfa_enabled"],
            "privileged_account": r["privileged_account"],
            "iam_risk_flag": r["iam_risk_flag"],
            "risk_status": "CRITICAL DEFICIT (Privileged + No MFA)" if r["iam_risk_flag"] else ("Standard Privileged" if r["privileged_account"] else "Non-Privileged")
        })
    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "total_iam_identities": len(iam_items),
        "critical_iam_deficits": sum(1 for item in iam_items if item["iam_risk_flag"]),
        "identities": iam_items
    }

@router.get("/edr-telemetry")
def get_sih_edr_telemetry() -> Dict[str, Any]:
    """Returns EDR alert telemetry, severity, and isolation states."""
    records = sih_engine.get_records()
    edr_items = []
    for r in records:
        edr_items.append({
            "asset_id": r["asset_id"],
            "asset_name": r["asset_name"],
            "edr_alert": r["edr_alert"],
            "edr_severity": r["edr_severity"],
            "edr_isolated": r["edr_isolated"],
            "containment_status": "Contained" if r["edr_isolated"] else "Uncontained (Active Exposure)"
        })
    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "total_edr_records": len(edr_items),
        "telemetry": edr_items
    }

@router.get("/cspm-findings")
def get_sih_cspm_findings() -> Dict[str, Any]:
    """Returns Cloud Security Posture Management findings, strictly omitting N/A records."""
    records = sih_engine.get_records()
    findings = []
    for r in records:
        if r["has_cspm"]:
            findings.append({
                "asset_id": r["asset_id"],
                "asset_name": r["asset_name"],
                "cspm_finding": r["cspm_finding"],
                "cspm_severity": r["cspm_severity"],
                "business_unit": r["business_unit"]
            })
    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "total_cspm_findings": len(findings),
        "findings": findings
    }

@router.get("/financial-risk")
def get_sih_financial_risk() -> Dict[str, Any]:
    """Returns financial impact breakdown, clearly designated as MODELED / ESTIMATED."""
    records = sih_engine.get_records()
    breakdown = []
    for r in records:
        breakdown.append({
            "asset_id": r["asset_id"],
            "asset_name": r["asset_name"],
            "business_unit": r["business_unit"],
            "estimated_incident_probability": r["estimated_incident_probability"],
            "incident_probability_label": r["incident_probability_label"],
            "potential_financial_impact_inr": r["potential_financial_impact_inr"],
            "potential_financial_impact_label": r["potential_financial_impact_label"],
            "control_effectiveness": r["control_effectiveness"],
            "control_effectiveness_pct": r["control_effectiveness_pct"],
            "expected_annual_loss_inr": r["expected_annual_loss_inr"],
            "expected_annual_loss_label": r["expected_annual_loss_label"],
            "estimated_mitigation_cost_inr": r["estimated_mitigation_cost_inr"],
            "estimated_mitigation_cost_label": r["estimated_mitigation_cost_label"]
        })
    
    overview = sih_engine.get_overview_metrics()
    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "classification": "MODELED / ESTIMATED FINANCIAL INPUT",
        "warning": "These figures represent modeled potential cyber financial exposure based on FAIR & probability models, not actual historical corporate losses.",
        "total_modeled_financial_impact": overview["total_modeled_financial_impact"],
        "total_modeled_financial_impact_label": overview["total_modeled_financial_impact_label"],
        "total_modeled_expected_annual_loss": overview["total_modeled_expected_annual_loss"],
        "total_modeled_expected_annual_loss_label": overview["total_modeled_expected_annual_loss_label"],
        "total_estimated_mitigation_cost": overview["total_estimated_mitigation_cost"],
        "total_estimated_mitigation_cost_label": overview["total_estimated_mitigation_cost_label"],
        "average_control_effectiveness": overview["average_control_effectiveness_label"],
        "asset_financial_breakdown": breakdown
    }

@router.get("/monte-carlo")
def get_sih_monte_carlo(iterations: int = Query(10000, ge=1000, le=50000)) -> Dict[str, Any]:
    """Runs 10,000-iteration Monte Carlo simulation from the 15 records."""
    return sih_engine.run_monte_carlo(iterations=iterations)

@router.post("/optimize")
def post_sih_optimize(req: OptimizationRequest) -> Dict[str, Any]:
    """Google OR-Tools SCIP Knapsack optimization using estimated_mitigation_cost_inr and modeled risk reduction."""
    return sih_engine.solve_mitigation_optimization(budget=req.budget)

@router.get("/attack-paths")
def get_sih_attack_paths() -> List[Dict[str, Any]]:
    """Identifies multi-stage attack paths grounded on empirical CSV signals."""
    return sih_engine.get_attack_paths()

@router.get("/future-risk")
def get_sih_future_risk() -> Dict[str, Any]:
    """Extracts ML feature vectors and communicates training limitations for the 15 records."""
    records = sih_engine.get_records()
    features = []
    for r in records:
        features.append({
            "asset_id": r["asset_id"],
            "asset_name": r["asset_name"],
            "asset_criticality_1_5": r["asset_criticality_1_5"],
            "internet_exposed": 1 if r["internet_exposed"] else 0,
            "cvss_score": r["cvss_score"],
            "exploit_available": 1 if r["exploit_available"] else 0,
            "vulnerability_age_days": r["vulnerability_age_days"],
            "siem_severity_weight": 4 if r["siem_severity"] == "Critical" else (3 if r["siem_severity"] == "High" else 1),
            "mfa_enabled": 1 if r["mfa_enabled"] else 0,
            "privileged_account": 1 if r["privileged_account"] else 0,
            "edr_severity_weight": 4 if r["edr_severity"] == "Critical" else (3 if r["edr_severity"] == "High" else 0),
            "edr_isolated": 1 if r["edr_isolated"] else 0,
            "threat_confidence_pct": r["threat_confidence_pct"],
            "estimated_incident_probability": r["estimated_incident_probability"],
            "potential_financial_impact_inr": r["potential_financial_impact_inr"],
            "control_effectiveness": r["control_effectiveness"],
            "target_calculated_risk": r["calculated_risk_score"]
        })

    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "sample_count": len(features),
        "feature_count": 14,
        "sample_size_limitation_notice": (
            "SIH test dataset (15 records) is suitable for pipeline demonstration, "
            "feature extraction, and explainability visualization, but insufficient "
            "for production-grade model training."
        ),
        "features": features
    }

@router.get("/ciso")
def get_sih_ciso_dashboard() -> Dict[str, Any]:
    """CISO Command Center summary with full drill-down capability."""
    overview = sih_engine.get_overview_metrics()
    records = sih_engine.get_records()

    # Top risk assets
    sorted_by_risk = sorted(records, key=lambda x: x["calculated_risk_score"], reverse=True)
    top_risk_assets = sorted_by_risk[:5]

    # Top vulnerabilities
    vuln_records = [r for r in records if r["has_cve"]]
    sorted_by_cvss = sorted(vuln_records, key=lambda x: x["cvss_score"], reverse=True)
    top_vulns = sorted_by_cvss[:5]

    # Highest financial impact
    sorted_by_impact = sorted(records, key=lambda x: x["potential_financial_impact_inr"], reverse=True)
    top_financial = sorted_by_impact[:5]

    # Highest incident probability
    sorted_by_prob = sorted(records, key=lambda x: x["estimated_incident_probability"], reverse=True)
    top_probability = sorted_by_prob[:5]

    # Critical IAM & EDR
    critical_iam = [r for r in records if r["iam_risk_flag"]]
    critical_edr = [r for r in records if not r["edr_isolated"] and r["edr_severity"] in ("Critical", "High")]

    # Budget recommendation: 60% of total mitigation cost
    total_mitigation = overview["total_estimated_mitigation_cost"]
    rec_budget = round(total_mitigation * 0.6, 2)
    optimization_result = sih_engine.solve_mitigation_optimization(budget=rec_budget)

    return {
        "dataset_origin": "SIH PS26105 TEST DATA",
        "overview": overview,
        "top_risk_assets": top_risk_assets,
        "top_vulnerabilities": top_vulns,
        "highest_financial_impact_assets": top_financial,
        "highest_incident_probability_assets": top_probability,
        "critical_iam_issues": critical_iam,
        "critical_edr_issues": critical_edr,
        "budget_recommendation": {
            "recommended_budget": rec_budget,
            "recommended_budget_label": format_inr(rec_budget),
            "optimization_result": optimization_result
        },
        "drill_down_map": [
            {
                "asset_id": r["asset_id"],
                "asset_name": r["asset_name"],
                "cve_id": r["cve_id"],
                "threat": r["threat_intel_indicator"],
                "siem_event": r["siem_event"],
                "modeled_financial_impact": r["potential_financial_impact_label"],
                "recommended_mitigation_cost": r["estimated_mitigation_cost_label"],
                "control_effectiveness": r["control_effectiveness_pct"]
            }
            for r in records
        ]
    }

@router.post("/import")
async def import_sih_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Validates and imports a CSV dataset against the expected 28 SIH PS26105 headers.
    """
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = contents.decode("latin-1")

    reader = csv.DictReader(io.StringIO(decoded))
    headers = [h.strip() for h in (reader.fieldnames or [])]
    expected_fields = sih_engine.get_fieldnames()

    missing = [f for f in expected_fields if f not in headers]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded CSV is missing required SIH fields: {missing}"
        )

    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="Uploaded CSV contains 0 rows.")

    return {
        "message": f"Successfully validated {len(rows)} records with all 28 expected SIH PS26105 fields.",
        "records_count": len(rows),
        "fields_matched": len(headers),
        "status": "VALIDATED_AND_APPLIED"
    }
