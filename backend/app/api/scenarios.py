"""
Digital Twin & What-If Scenario Analysis API Router.
Enables CISO and risk teams to simulate security investments, control failures,
and adversary campaigns without modifying the baseline operational environment.
Always marks outputs as SIMULATED SCENARIO.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.database.session import get_sync_db
from app.database.models import RiskAssessment, Asset, SecurityControl, ScenarioRecord
from app.api.auth import get_current_user
from app.optimization_engine.solver import optimizer
from app.scenarios.what_if_engine import get_available_interventions, calculate_what_if_scenario

router = APIRouter(prefix="/scenarios", tags=["Digital Twin & What-If Simulator"])

class ControlInterventionRequest(BaseModel):
    intervention_id: str
    custom_investment_cost: Optional[float] = None
    custom_baseline_criticality: Optional[float] = None

@router.get("/interventions")
def list_interventions():
    """Returns the list of 7 enterprise security interventions for What-If simulation."""
    return get_available_interventions()

@router.post("/simulate-control")
def simulate_control_intervention(
    request: ControlInterventionRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Executes a real Before -> Control -> After calculation using the centralized FAIR risk engine.
    """
    custom_baseline = None
    if request.custom_baseline_criticality:
        custom_baseline = {"asset_criticality": request.custom_baseline_criticality}

    try:
        result = calculate_what_if_scenario(
            intervention_id=request.intervention_id,
            custom_cost=request.custom_investment_cost,
            custom_baseline=custom_baseline
        )
        latest_assessment = db.query(RiskAssessment).filter(
            RiskAssessment.organization_id == current_user.organization_id
        ).order_by(RiskAssessment.timestamp.desc()).first()
        result["timestamp"] = latest_assessment.timestamp.isoformat() if latest_assessment else datetime.utcnow().isoformat()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class WhatIfSimulationRequest(BaseModel):
    name: Optional[str] = "Interactive What-If Simulation"
    mfa_coverage: Optional[float] = 72.0          # 0-100%
    edr_coverage: Optional[float] = 85.0          # 0-100%
    patch_cadence_score: Optional[float] = 70.0   # 0-100%
    network_segmentation: Optional[float] = 60.0  # 0-100%
    threat_likelihood_mod: Optional[float] = 1.0  # 0.5x to 2.0x
    custom_spend_mfa: Optional[float] = None      # e.g. ₹20 Lakh
    log4j_exploited: Optional[bool] = None        # True/False
    control_effectiveness_boost: Optional[float] = None # e.g. +20%
    budget_cap: Optional[float] = None            # e.g. ₹50 Lakh
    asset_internet_exposed_target: Optional[str] = None # asset ID/name

from app.risk_engine.fair_model import run_fair_analysis
from app.risk_engine.likelihood import calculate_loss_event_frequency

@router.post("/simulate")
@router.post("/what-if")
def simulate_what_if(
    request: WhatIfSimulationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Simulates digital twin control adjustments through the centralized FAIR risk engine:
        Current (LEF, SLE, EAL) -> Apply Proposed Controls -> New (LEF, SLE, EAL) -> Modeled Risk Reduction
    """
    latest_assessment = db.query(RiskAssessment).filter(
        RiskAssessment.organization_id == current_user.organization_id
    ).order_by(RiskAssessment.timestamp.desc()).first()
    baseline_risk = latest_assessment.expected_annual_loss if latest_assessment else 46000000.0

    # 1. Baseline control parameters
    base_mfa = 72.0
    base_edr = 85.0
    base_patch = 70.0
    base_seg = 60.0
    base_avg_cov = (base_mfa + base_edr + base_patch + base_seg) / 4.0  # 71.75%
    base_avg_eff = 75.0

    # 2. Simulated control adjustments
    mfa_cov = request.mfa_coverage if request.mfa_coverage is not None else base_mfa
    edr_cov = request.edr_coverage if request.edr_coverage is not None else base_edr
    patch_cov = request.patch_cadence_score if request.patch_cadence_score is not None else base_patch
    seg_cov = request.network_segmentation if request.network_segmentation is not None else base_seg

    investment_cost = 0.0
    if request.custom_spend_mfa:
        investment_cost = request.custom_spend_mfa
        # ₹20 Lakh investment raises MFA coverage from 72% to ~98%
        mfa_cov = min(100.0, base_mfa + (request.custom_spend_mfa / 1000000.0) * 13.0)

    if request.control_effectiveness_boost:
        mfa_cov = min(100.0, mfa_cov + request.control_effectiveness_boost)
        edr_cov = min(100.0, edr_cov + request.control_effectiveness_boost)
        patch_cov = min(100.0, patch_cov + request.control_effectiveness_boost)
        seg_cov = min(100.0, seg_cov + request.control_effectiveness_boost)

    sim_avg_cov = (mfa_cov + edr_cov + patch_cov + seg_cov) / 4.0
    sim_avg_eff = min(95.0, base_avg_eff + (sim_avg_cov - base_avg_cov) * 0.4)

    # 3. Threat and exploit conditions
    has_active_exploit = True if request.log4j_exploited is not False else False
    is_internet_exposed = True if (request.asset_internet_exposed_target or True) else False
    threat_mod = request.threat_likelihood_mod or 1.0

    # Baseline FAIR calculation
    baseline_fair = run_fair_analysis(
        asset_criticality=92.0,
        threat_activity=85.0 * threat_mod,
        cvss_score=9.8 if has_active_exploit else 7.0,
        active_exploitation=has_active_exploit,
        is_internet_exposed=is_internet_exposed,
        control_coverage=base_avg_cov,
        control_effectiveness=base_avg_eff,
        in_attack_path=True
    )

    # Simulated FAIR calculation with proposed controls applied
    simulated_fair = run_fair_analysis(
        asset_criticality=92.0,
        threat_activity=85.0 * threat_mod,
        cvss_score=9.8 if has_active_exploit else 7.0,
        active_exploitation=has_active_exploit,
        is_internet_exposed=is_internet_exposed,
        control_coverage=sim_avg_cov,
        control_effectiveness=sim_avg_eff,
        in_attack_path=True if seg_cov < 80.0 else False  # Segmentation breaks lateral attack path!
    )

    # Modeled Enterprise-wide proportional effect
    base_lef = baseline_fair["loss_event_frequency"]
    sim_lef = simulated_fair["loss_event_frequency"]
    reduction_ratio = max(-1.0, min(0.95, (base_lef - sim_lef) / max(0.01, base_lef)))

    simulated_risk = max(1000000.0, round(baseline_risk * (1.0 - reduction_ratio), 2))
    net_risk_reduction = round(baseline_risk - simulated_risk, 2)

    # Persist scenario record
    scenario = ScenarioRecord(
        organization_id=current_user.organization_id,
        name=request.name or "Interactive What-If Scenario",
        description=f"Simulated parameters: MFA {mfa_cov:.1f}%, EDR {edr_cov:.1f}%, Patch {patch_cov:.1f}%, Seg {seg_cov:.1f}%.",
        parameters=request.model_dump(exclude_unset=True) if hasattr(request, "model_dump") else request.dict(exclude_unset=True),
        baseline_risk=baseline_risk,
        simulated_risk=round(simulated_risk, 2),
        modeled_risk_reduction=round(net_risk_reduction, 2)
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    return {
        "scenario_id": scenario.id,
        "name": scenario.name,
        "baseline_modeled_risk": baseline_risk,
        "baseline_label": f"₹{round(baseline_risk/10000000, 2)} Cr",
        "current_likelihood_frequency": base_lef,
        "current_single_loss_expectancy": baseline_fair["single_loss_expectancy"],
        "simulated_modeled_risk": round(simulated_risk, 2),
        "simulated_label": f"₹{round(simulated_risk/10000000, 2)} Cr" if simulated_risk >= 10000000 else f"₹{round(simulated_risk/100000, 1)} L",
        "new_likelihood_frequency": sim_lef,
        "new_single_loss_expectancy": simulated_fair["single_loss_expectancy"],
        "modeled_risk_reduction": round(net_risk_reduction, 2),
        "modeled_reduction_label": f"{'+' if net_risk_reduction >= 0 else ''}₹{round(net_risk_reduction/100000, 1)} L",
        "investment_cost": investment_cost,
        "investment_cost_label": f"₹{round(investment_cost/100000, 1)} Lakh" if investment_cost > 0 else "N/A",
        "simulated_parameters": request.model_dump(exclude_unset=True) if hasattr(request, "model_dump") else request.dict(exclude_unset=True),
        "modeled_label": "SIMULATED SCENARIO",
        "disclaimer": "Digital twin simulations evaluate control adjustments using the centralized FAIR quantitative cyber risk engine."
    }


from app.scenarios.what_if_engine import (
    get_available_interventions,
    calculate_what_if_scenario,
    simulate_flexible_scenario
)

class ScenarioRunRequest(BaseModel):
    scenario_name: Optional[str] = "What-If Simulation"
    changes: List[Dict[str, Any]] = []
    budget: Optional[float] = 10000000.0
    base_dataset_id: Optional[str] = "sih_ps26105"

class SaveScenarioRequest(BaseModel):
    scenario_name: str
    base_dataset_id: Optional[str] = "sih_ps26105"
    changes: List[Dict[str, Any]] = []
    baseline_risk: float = 82.0
    simulated_risk: float = 64.0
    modeled_risk_reduction: float = 18.0
    investment_cost: Optional[float] = 0.0
    financial_exposure_before: Optional[float] = 46000000.0
    financial_exposure_after: Optional[float] = 20000000.0
    attack_paths_affected: Optional[List[str]] = []
    affected_assets: Optional[List[str]] = []

class CompareScenariosRequest(BaseModel):
    scenarios: List[Dict[str, Any]]

@router.post("/run")
def run_scenario(
    request: ScenarioRunRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Executes an isolated What-If scenario with supported changes without mutating production data (Sections 8.1-8.6).
    """
    latest_assessment = db.query(RiskAssessment).filter(
        RiskAssessment.organization_id == current_user.organization_id
    ).order_by(RiskAssessment.timestamp.desc()).first()
    baseline_eal = latest_assessment.expected_annual_loss if latest_assessment else 46000000.0

    res = simulate_flexible_scenario(
        changes=request.changes,
        budget=request.budget or 10000000.0
    )
    res["scenario_name"] = request.scenario_name
    res["base_dataset_id"] = request.base_dataset_id or "sih_ps26105"
    res["timestamp"] = datetime.utcnow().isoformat()
    return res

@router.post("/compare")
def compare_scenarios(
    request: CompareScenariosRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Compares multiple scenarios side-by-side (Scenario A vs B vs C) across
    Cost, Risk, Financial Exposure, Affected Assets, and Attack Paths (Section 8.7).
    """
    comparison_results = []
    for item in request.scenarios:
        s_name = item.get("name", item.get("scenario_name", "Scenario"))
        s_changes = item.get("changes", [])
        s_budget = float(item.get("budget", 10000000.0))

        sim = simulate_flexible_scenario(changes=s_changes, budget=s_budget)
        comp = sim["before_after_comparison"]
        s_state = sim["scenario_state"]

        comparison_results.append({
            "scenario_name": s_name,
            "cost": comp["investment_cost"],
            "total_investment_cost": comp["investment_cost"],
            "cost_label": f"₹{round(comp['investment_cost']/100000, 1)} Lakh" if comp["investment_cost"] > 0 else "₹0",
            "risk_score_before": comp["current_risk"],
            "risk_score_after": comp["scenario_risk"],
            "modeled_risk_score": comp["scenario_risk"],
            "risk_reduction": round(comp["current_risk"] - comp["scenario_risk"], 1),
            "risk_reduction_points": round(comp["current_risk"] - comp["scenario_risk"], 1),
            "financial_exposure_before": comp["current_eal"],
            "financial_exposure_before_label": f"₹{round(comp['current_eal']/10000000, 2)} Cr",
            "financial_exposure_after": comp["scenario_eal"],
            "financial_exposure_eal": comp["scenario_eal"],
            "financial_exposure_after_label": f"₹{round(comp['scenario_eal']/10000000, 2)} Cr",
            "eal_reduction": comp["eal_reduction"],
            "eal_reduction_label": f"₹{round(comp['eal_reduction']/10000000, 2)} Cr",
            "affected_assets": s_state.get("affected_assets", []),
            "affected_assets_count": len(s_state.get("affected_assets", [])),
            "attack_paths": s_state.get("attack_paths", []),
            "attack_paths_count": len(s_state.get("attack_paths", [])),
            "changes_applied": s_changes
        })

    return {
        "status": "SUCCESS",
        "comparison_count": len(comparison_results),
        "scenarios": comparison_results,
        "scenario_comparison": comparison_results,
        "disclaimer": "Scenario comparisons evaluate isolated simulated risk delta without touching production assets."
    }

@router.post("/save")
def save_scenario(
    request: SaveScenarioRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Persists a simulated scenario to the scenario audit ledger (Sections 8.9 & 8.10).
    """
    rec = ScenarioRecord(
        organization_id=current_user.organization_id,
        name=request.scenario_name,
        description=f"Saved scenario with {len(request.changes)} change(s).",
        parameters={"changes": request.changes},
        baseline_risk=request.baseline_risk,
        simulated_risk=request.simulated_risk,
        modeled_risk_reduction=request.modeled_risk_reduction,
        base_dataset_id=request.base_dataset_id or "sih_ps26105",
        created_by=current_user.full_name or current_user.email,
        changes=request.changes,
        status="SAVED",
        investment_cost=request.investment_cost or 0.0,
        financial_exposure_before=request.financial_exposure_before,
        financial_exposure_after=request.financial_exposure_after,
        attack_paths_affected=request.attack_paths_affected or [],
        affected_assets=request.affected_assets or []
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {
        "status": "SAVED",
        "scenario_id": rec.id,
        "scenario_name": rec.name,
        "base_dataset_id": rec.base_dataset_id,
        "created_by": rec.created_by,
        "created_at": rec.created_at.isoformat() if rec.created_at else datetime.utcnow().isoformat(),
        "changes": rec.changes,
        "result": {
            "baseline_risk": rec.baseline_risk,
            "simulated_risk": rec.simulated_risk,
            "modeled_risk_reduction": rec.modeled_risk_reduction
        }
    }

@router.post("/reset")
def reset_scenario_state(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Restores the baseline simulation state without modifying or deleting any uploaded dataset (Section 8.9).
    """
    latest_assessment = db.query(RiskAssessment).filter(
        RiskAssessment.organization_id == current_user.organization_id
    ).order_by(RiskAssessment.timestamp.desc()).first()
    current_risk = latest_assessment.enterprise_risk_score if latest_assessment else 82.0
    current_eal = latest_assessment.expected_annual_loss if latest_assessment else 46000000.0

    return {
        "status": "RESET_SUCCESSFUL",
        "message": "Simulation canvas reset to baseline operational telemetry. No datasets were altered.",
        "baseline_state": {
            "enterprise_risk": current_risk,
            "financial_exposure": current_eal,
            "financial_exposure_label": f"₹{round(current_eal/10000000, 2)} Crore",
            "active_dataset": latest_assessment.dataset_id if latest_assessment else "sih_ps26105"
        }
    }

@router.get("")
def list_scenarios(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    scenarios = db.query(ScenarioRecord).filter(
        ScenarioRecord.organization_id == current_user.organization_id
    ).order_by(ScenarioRecord.created_at.desc()).limit(20).all()
    return scenarios

@router.get("/digital-twin")
def get_digital_twin_state(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Digital Twin representation of the enterprise: Assets, Critical Assets, Vulnerabilities, Controls, Attack Paths, and Risk Levels (Section 8.8).
    """
    from app.database.models import Vulnerability, AttackPathRecord
    assets = db.query(Asset).filter(Asset.organization_id == current_user.organization_id).all()
    critical_assets = [a for a in assets if (a.criticality_score or 0) >= 80.0]
    controls = db.query(SecurityControl).filter(SecurityControl.organization_id == current_user.organization_id).all()
    vulns = db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id).all()
    paths = db.query(AttackPathRecord).filter(AttackPathRecord.organization_id == current_user.organization_id).all()
    latest_assessment = db.query(RiskAssessment).filter(RiskAssessment.organization_id == current_user.organization_id).order_by(RiskAssessment.timestamp.desc()).first()

    return {
        "digital_twin": {
            "entity_name": "ABC Bank Virtual Digital Twin",
            "status": "SYNCHRONIZED_WITH_TELEMETRY",
            "last_sync": datetime.utcnow().isoformat() + "Z"
        },
        "entity_name": "ABC Bank Virtual Digital Twin",
        "twin_status": "SYNCHRONIZED_WITH_TELEMETRY",
        "last_sync": datetime.utcnow().isoformat() + "Z",
        "enterprise_risk_level": latest_assessment.risk_level if latest_assessment else "CRITICAL",
        "enterprise_risk_score": latest_assessment.enterprise_risk_score if latest_assessment else 82.0,
        "financial_exposure": latest_assessment.expected_annual_loss if latest_assessment else 46000000.0,
        "total_assets": len(assets),
        "assets_count": len(assets),
        "critical_assets_count": len(critical_assets),
        "critical_assets": [
            {"id": a.id, "name": a.name, "criticality": a.criticality_score, "type": a.asset_type, "internet_exposed": a.internet_exposed}
            for a in critical_assets[:6]
        ],
        "active_vulnerabilities_count": len(vulns),
        "critical_vulnerabilities": [
            {"cve_id": v.cve_id, "title": v.title, "cvss": v.cvss_score, "active_exploit": v.active_exploitation}
            for v in vulns if (v.cvss_score or 0) >= 9.0 or v.active_exploitation
        ][:5],
        "attack_paths_count": len(paths),
        "attack_paths": [
            {"name": p.name, "path_length": p.path_length, "path_risk_score": p.path_risk_score, "target": p.target_asset_name}
            for p in paths[:4]
        ],
        "controls": [
            {
                "code": c.code,
                "name": c.name,
                "category": c.category,
                "coverage": c.coverage_percentage,
                "effectiveness": c.effectiveness_percentage,
                "status": c.status
            }
            for c in controls
        ],
        "active_controls": [
            {
                "code": c.code,
                "name": c.name,
                "category": c.category,
                "coverage": c.coverage_percentage,
                "effectiveness": c.effectiveness_percentage,
                "status": c.status
            }
            for c in controls
        ],
        "disclaimer": "The Digital Twin is a decision-support simulation, not a claim that it is an exact replica of the real enterprise."
    }

@router.get("/{scenario_id}")
def get_scenario(
    scenario_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    sc = db.query(ScenarioRecord).filter(
        ScenarioRecord.id == scenario_id,
        ScenarioRecord.organization_id == current_user.organization_id
    ).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario record not found")
    return sc
