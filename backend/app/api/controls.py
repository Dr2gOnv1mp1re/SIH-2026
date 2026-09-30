from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database.session import get_sync_db
from app.database.models import SecurityControl
from app.api.auth import get_current_user

router = APIRouter(prefix="/controls", tags=["Security Control Engine"])

class CreateControlRequest(BaseModel):
    code: str
    name: str
    category: str = "IAM"
    description: Optional[str] = None
    coverage_percentage: float = 70.0
    effectiveness_percentage: float = 75.0
    maturity_level: int = 3
    implementation_cost: float = 1200000.0
    annual_cost: float = 300000.0
    modeled_risk_reduction: float = 4500000.0
    prerequisites: Optional[List[str]] = []

class UpdateControlRequest(BaseModel):
    coverage_percentage: Optional[float] = None
    effectiveness_percentage: Optional[float] = None
    implementation_cost: Optional[float] = None
    annual_cost: Optional[float] = None
    modeled_risk_reduction: Optional[float] = None

@router.post("")
def create_control(request: CreateControlRequest, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    ctrl = SecurityControl(
        organization_id=current_user.organization_id,
        code=request.code,
        name=request.name,
        category=request.category,
        description=request.description,
        coverage_percentage=request.coverage_percentage,
        effectiveness_percentage=request.effectiveness_percentage,
        maturity_level=request.maturity_level,
        implementation_cost=request.implementation_cost,
        annual_cost=request.annual_cost,
        modeled_risk_reduction=request.modeled_risk_reduction,
        prerequisites=request.prerequisites or [],
        status="DEPLOYED" if request.coverage_percentage >= 80.0 else "PARTIALLY_DEPLOYED"
    )
    db.add(ctrl)
    db.commit()
    db.refresh(ctrl)
    return ctrl

@router.get("")
def list_controls(current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    controls = db.query(SecurityControl).filter(SecurityControl.organization_id == current_user.organization_id).order_by(SecurityControl.modeled_risk_reduction.desc()).all()
    return controls

@router.get("/catalogue")
def get_security_control_catalogue(current_user = Depends(get_current_user)):
    """Returns the centralized Security Control Catalogue (Section 7.1)."""
    from app.optimization_engine.solver import DEFAULT_CANDIDATE_CONTROLS
    return {
        "catalogue_count": len(DEFAULT_CANDIDATE_CONTROLS),
        "controls": DEFAULT_CANDIDATE_CONTROLS,
        "standard_frameworks": ["NIST CSF v2.0", "ISO/IEC 27001:2022", "CIS Controls v8", "RBI Cyber Security Framework"]
    }

@router.get("/mapping")
def get_control_risk_mapping(current_user = Depends(get_current_user)):
    """Returns the centralized Control-Risk Mapping (Section 7.2)."""
    from app.optimization_engine.solver import CONTROL_RISK_MAPPING, DEFAULT_CANDIDATE_CONTROLS
    ctrl_dict = {c["control_id"]: c for c in DEFAULT_CANDIDATE_CONTROLS}
    detailed_mapping = []
    for risk_factor, ctrl_ids in CONTROL_RISK_MAPPING.items():
        detailed_mapping.append({
            "risk_factor": risk_factor,
            "associated_controls": [
                {
                    "control_id": cid,
                    "control_name": ctrl_dict.get(cid, {}).get("control_name", cid),
                    "category": ctrl_dict.get(cid, {}).get("category", "SECURITY"),
                    "effectiveness": ctrl_dict.get(cid, {}).get("effectiveness", 85.0),
                    "estimated_cost": ctrl_dict.get(cid, {}).get("estimated_cost", 1000000.0)
                }
                for cid in ctrl_ids
            ]
        })
    return {
        "mapping_count": len(CONTROL_RISK_MAPPING),
        "control_risk_mapping": CONTROL_RISK_MAPPING,
        "detailed_mapping": detailed_mapping
    }

@router.get("/recommendations")
def get_data_driven_recommendations(current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    """
    Returns data-driven control recommendations derived from the active dataset's
    actual risk score, vulnerabilities, attack paths, and critical assets (Section 7.3).
    """
    from app.database.models import RiskAssessment, Vulnerability, Asset, AttackPathRecord
    from app.optimization_engine.solver import generate_data_driven_recommendations

    assessment = db.query(RiskAssessment).filter(
        RiskAssessment.organization_id == current_user.organization_id
    ).order_by(RiskAssessment.timestamp.desc()).first()
    risk_score = assessment.enterprise_risk_score if assessment else 82.0
    financial_exposure = assessment.expected_annual_loss if assessment else 46000000.0

    vulns = db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id).all()
    vuln_data = [{"cvss_score": v.cvss_score, "active_exploitation": v.active_exploitation, "cve_id": v.cve_id} for v in vulns]

    paths = db.query(AttackPathRecord).filter(AttackPathRecord.organization_id == current_user.organization_id).all()
    path_data = [{"name": p.name, "nodes_chain": p.nodes_chain, "path_risk_score": p.path_risk_score} for p in paths]

    assets = db.query(Asset).filter(Asset.organization_id == current_user.organization_id).order_by(Asset.criticality_score.desc()).limit(5).all()
    asset_data = [{"name": a.name, "criticality": a.criticality_score} for a in assets]

    recs = generate_data_driven_recommendations(
        risk_score=risk_score,
        vulnerabilities=vuln_data,
        attack_paths=path_data,
        critical_assets=asset_data,
        financial_exposure=financial_exposure
    )

    return {
        "status": "SUCCESS",
        "dataset_risk_score": risk_score,
        "financial_exposure": financial_exposure,
        "financial_exposure_label": f"₹{round(financial_exposure/10000000, 2)} Crore",
        "total_recommendations": len(recs),
        "recommendations": recs,
        "disclaimer": "Recommendations are generated dynamically by correlating identified vulnerabilities, crown jewel assets, and attack paths."
    }

@router.get("/{control_id}")
def get_control(control_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    ctrl = db.query(SecurityControl).filter(SecurityControl.id == control_id, SecurityControl.organization_id == current_user.organization_id).first()
    if not ctrl:
        raise HTTPException(status_code=404, detail="Control not found")
    return ctrl

@router.put("/{control_id}")
def update_control(control_id: str, request: UpdateControlRequest, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    ctrl = db.query(SecurityControl).filter(SecurityControl.id == control_id, SecurityControl.organization_id == current_user.organization_id).first()
    if not ctrl:
        raise HTTPException(status_code=404, detail="Control not found")
        
    if request.coverage_percentage is not None:
        ctrl.coverage_percentage = request.coverage_percentage
    if request.effectiveness_percentage is not None:
        ctrl.effectiveness_percentage = request.effectiveness_percentage
    if request.implementation_cost is not None:
        ctrl.implementation_cost = request.implementation_cost
    if request.annual_cost is not None:
        ctrl.annual_cost = request.annual_cost
    if request.modeled_risk_reduction is not None:
        ctrl.modeled_risk_reduction = request.modeled_risk_reduction
        
    ctrl.status = "DEPLOYED" if ctrl.coverage_percentage >= 80.0 else "PARTIALLY_DEPLOYED"
    db.commit()
    db.refresh(ctrl)
    return ctrl
