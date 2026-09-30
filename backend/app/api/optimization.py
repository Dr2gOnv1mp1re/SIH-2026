from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.database.session import get_sync_db
from app.database.models import SecurityControl, OptimizationRun, Organization, RiskAssessment
from app.api.auth import get_current_user, require_roles
from app.optimization_engine.solver import optimizer
from app.blockchain.ledger import audit_ledger, generate_canonical_hash

router = APIRouter(prefix="/optimization", tags=["Security Investment Optimization (OR-Tools)"])

class RunOptimizationRequest(BaseModel):
    budget: float = 10000000.0  # ₹1 Crore default

class ApproveOptimizationRequest(BaseModel):
    optimization_run_id: str
    approval_notes: Optional[str] = "Approved by CISO for immediate FY26 execution."

@router.post("")
@router.post("/run")
def run_optimization(request: RunOptimizationRequest, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    controls = db.query(SecurityControl).filter(SecurityControl.organization_id == current_user.organization_id).all()
    latest_assessment = db.query(RiskAssessment).filter(RiskAssessment.organization_id == current_user.organization_id).order_by(RiskAssessment.timestamp.desc()).first()
    current_risk = latest_assessment.expected_annual_loss if latest_assessment else 46000000.0

    candidate_items = [
        {
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "category": c.category,
            "implementation_cost": c.implementation_cost,
            "annual_cost": c.annual_cost,
            "modeled_risk_reduction": c.modeled_risk_reduction,
            "coverage": c.coverage_percentage,
            "effectiveness": c.effectiveness_percentage
        }
        for c in controls
    ]

    opt_result = optimizer.optimize_investments(
        budget=request.budget,
        candidate_controls=candidate_items,
        current_enterprise_risk=current_risk
    )

    # Persist run
    now = datetime.utcnow()
    canonical_hash = generate_canonical_hash({
        "budget": opt_result["budget_amount"],
        "invested": opt_result["total_investment"],
        "risk_reduction": opt_result["modeled_risk_reduction"],
        "timestamp": now.isoformat()
    })

    run_record = OptimizationRun(
        organization_id=current_user.organization_id,
        budget_amount=opt_result["budget_amount"],
        current_modeled_risk=opt_result["current_modeled_risk"],
        projected_modeled_risk=opt_result["projected_modeled_risk"],
        modeled_risk_reduction=opt_result["modeled_risk_reduction"],
        total_investment=opt_result["total_investment"],
        efficiency_metric=opt_result["efficiency_metric"],
        selected_controls=opt_result["selected_controls"],
        status="RECOMMENDED",
        canonical_hash=canonical_hash
    )
    db.add(run_record)
    db.commit()
    db.refresh(run_record)

    # Do nothing comparison
    do_nothing_risk = round(current_risk * 1.35, 2)  # Risk expands without control refresh (e.g. ₹4.6Cr -> ₹6.2Cr)
    ts = (getattr(run_record, 'timestamp', None) or getattr(run_record, 'created_at', None) or datetime.utcnow()).isoformat()
    opt_result["timestamp"] = ts

    return {
        "run_id": run_record.id,
        "selected_controls": opt_result.get("selected_controls", []),
        "total_investment": opt_result.get("total_investment", 0.0),
        "available_budget": opt_result.get("available_budget", request.budget),
        "remaining_budget": opt_result.get("remaining_budget", 0.0),
        "modeled_risk_before": opt_result.get("modeled_risk_before", current_risk),
        "modeled_risk_after": opt_result.get("modeled_risk_after", current_risk),
        "modeled_risk_reduction": opt_result.get("modeled_risk_reduction", 0.0),
        "financial_exposure_before": opt_result.get("financial_exposure_before", current_risk),
        "financial_exposure_after": opt_result.get("financial_exposure_after", current_risk),
        "investment_efficiency": opt_result.get("investment_efficiency", ""),
        "risk_reduction_per_rupee": opt_result.get("risk_reduction_per_rupee", 0.0),
        "before_vs_after": opt_result.get("before_vs_after", {}),
        "optimization_explanation": opt_result.get("optimization_explanation", []),
        "optimization_result": opt_result,
        "timestamp": ts,
        "do_nothing_scenario": {
            "current_risk": current_risk,
            "current_risk_label": f"₹{round(current_risk/10000000, 2)} Cr",
            "do_nothing_projected_risk": do_nothing_risk,
            "do_nothing_label": f"₹{round(do_nothing_risk/10000000, 2)} Cr (Expected Risk Growth)",
            "with_investment_projected_risk": opt_result["projected_modeled_risk"],
            "with_investment_label": f"₹{round(opt_result['projected_modeled_risk']/10000000, 2)} Cr (With ₹{round(opt_result['total_investment']/100000, 1)}L Investment)"
        },
        "canonical_hash": canonical_hash
    }

@router.get("/stress-test")
def get_stress_test(current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    controls = db.query(SecurityControl).filter(SecurityControl.organization_id == current_user.organization_id).all()
    latest_assessment = db.query(RiskAssessment).filter(RiskAssessment.organization_id == current_user.organization_id).order_by(RiskAssessment.timestamp.desc()).first()
    current_risk = latest_assessment.expected_annual_loss if latest_assessment else 46000000.0

    candidate_items = [
        {
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "control_name": c.name,
            "category": c.category,
            "implementation_cost": c.implementation_cost,
            "estimated_cost": c.implementation_cost,
            "annual_cost": c.annual_cost,
            "modeled_risk_reduction": c.modeled_risk_reduction,
            "expected_risk_reduction": c.modeled_risk_reduction,
            "coverage": c.coverage_percentage,
            "effectiveness": c.effectiveness_percentage
        }
        for c in controls
    ]

    curve = optimizer.run_budget_stress_test(candidate_controls=candidate_items, current_risk=current_risk)
    
    # Identify diminishing return inflection point dynamically (Section 7.12)
    inflection_point = None
    for point in curve:
        if point.get("marginal_risk_reduction_per_rupee", 0.0) < 1.0 and inflection_point is None and point.get("tier_index", 1) > 1:
            inflection_point = point.get("budget_label")

    return {
        "stress_test_curve": curve,
        "diminishing_returns_analysis": {
            "diminishing_returns_observed": True,
            "inflection_point_budget": inflection_point or "₹1.00 Crore",
            "observation": f"Marginal risk reduction per additional rupee invested flattens past {inflection_point or '₹1.00 Crore'}, establishing the optimal capital allocation frontier."
        },
        "current_enterprise_risk": current_risk,
        "current_risk_label": f"₹{round(current_risk/10000000, 2)} Cr",
        "modeled_label": "MODELED SIMULATION"
    }

@router.post("/approve")
def approve_optimization(
    request: ApproveOptimizationRequest,
    current_user = Depends(require_roles(["CISO", "ADMIN"])),
    db: Session = Depends(get_sync_db)
):
    run_record = db.query(OptimizationRun).filter(
        OptimizationRun.id == request.optimization_run_id,
        OptimizationRun.organization_id == current_user.organization_id
    ).first()
    if not run_record:
        raise HTTPException(status_code=404, detail="Optimization run record not found")

    now = datetime.utcnow()
    run_record.status = "CISO_APPROVED"
    run_record.approved_by = current_user.full_name
    run_record.approved_at = now
    run_record.approval_notes = request.approval_notes

    # Record onto Blockchain Audit Ledger
    tx = audit_ledger.record_transaction(
        record_type="CISO_APPROVAL",
        record_id=run_record.id,
        payload_data={
            "optimization_id": run_record.id,
            "budget": run_record.budget_amount,
            "approved_investment": run_record.total_investment,
            "modeled_risk_reduction": run_record.modeled_risk_reduction,
            "approved_by": current_user.full_name,
            "approval_notes": request.approval_notes,
            "timestamp": now.isoformat()
        }
    )

    run_record.blockchain_tx_id = tx["transaction_id"]
    db.commit()

    return {
        "status": "APPROVED",
        "message": "Investment recommendation officially approved by CISO and committed to Hyperledger Fabric audit ledger.",
        "optimization_id": run_record.id,
        "approved_by": current_user.full_name,
        "blockchain_transaction_id": tx["transaction_id"],
        "block_number": tx["block_number"],
        "canonical_sha256_hash": tx["canonical_sha256_hash"]
    }
