"""
Real-World Incident Scenario Lab API Router (SIH 2026).
Integrates authoritative public CVE/KEV intelligence with the centralized FAIR risk engine,
synthetic enterprise profiling, AI predictive modeling, OR-Tools optimization, and blockchain auditability.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from app.scenarios.real_world_catalog import (
    get_scenario_catalog,
    get_scenario_by_cve,
    SYNTHETIC_ENTERPRISE_DEFAULT
)
from app.scenarios.real_world_engine import scenario_engine

router = APIRouter(prefix="/real-world-scenarios", tags=["Real-World Scenario Lab (SIH 2026)"])

# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================

class ScenarioAnalysisRequest(BaseModel):
    cve_id: Optional[str] = "CVE-2021-44228"
    selected_asset_name: Optional[str] = "Payment Application Server"
    selected_business_service: Optional[str] = "Payment Processing & Settlement"
    enterprise_overrides: Optional[Dict[str, Any]] = None

class WhatIfRequest(BaseModel):
    cve_id: Optional[str] = "CVE-2021-44228"
    enterprise_overrides: Optional[Dict[str, Any]] = None

class OptimizationRequest(BaseModel):
    cve_id: Optional[str] = "CVE-2021-44228"
    budget: Optional[float] = Field(default=5000000.0, description="Available security investment budget in INR")
    enterprise_overrides: Optional[Dict[str, Any]] = None

class CISODecisionRequest(BaseModel):
    cve_id: str
    decision: str = Field(description="APPROVE, REJECT, or REQUEST_REVIEW")
    ciso_name: Optional[str] = "Chief Information Security Officer"
    decision_notes: Optional[str] = "Authorized for enterprise implementation."
    modeled_eal: Optional[float] = 0.0
    recommended_investment: Optional[float] = 0.0
    recommended_controls: Optional[List[str]] = None
    requested_changes: Optional[str] = None

# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@router.get("/catalog")
def list_scenario_catalog():
    """
    Returns available authoritative real-world scenarios in the catalog.
    Includes CVSS scores, CISA KEV status, and source citations.
    """
    return {
        "catalog": get_scenario_catalog(),
        "total_scenarios": len(get_scenario_catalog()),
        "authoritative_sources": ["NVD (NIST)", "CISA KEV", "Apache", "MITRE ATT&CK"],
        "policy": "Cached Authoritative Public Dataset — Zero Hallucination Policy"
    }

@router.get("/catalog/{cve_id}")
def get_scenario_details(cve_id: str):
    """
    Returns full authoritative threat intelligence, CVSS vector breakdown,
    CISA KEV timeline, and source citations for a specific CVE.
    """
    data = get_scenario_by_cve(cve_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Scenario for CVE '{cve_id}' not found.")
    return data

@router.get("/enterprise-profile")
def get_enterprise_profile():
    """
    Returns default synthetic enterprise profile ('ABC Bank — Synthetic Demonstration Environment').
    All fields are clearly labeled as synthetic demonstration inputs.
    """
    return {
        "enterprise_profile": SYNTHETIC_ENTERPRISE_DEFAULT,
        "disclaimer_label": "Synthetic enterprise environment for demonstration",
        "disclaimer_text": "Never implied that ABC Bank is an actual historical victim. All operational figures are synthetic demonstration models for risk quantification."
    }

@router.post("/analyze")
def analyze_real_world_scenario(request: ScenarioAnalysisRequest):
    """
    Executes end-to-end evaluation through the centralized FAIR risk engine:
    Real-world vulnerability + Synthetic enterprise profile ->
    Likelihood (LEF) + Loss Magnitude (SLE) -> Modeled EAL -> Monte Carlo -> XGBoost + SHAP -> Attack Path.
    """
    try:
        result = scenario_engine.analyze_scenario(
            cve_id=request.cve_id or "CVE-2021-44228",
            enterprise_overrides=request.enterprise_overrides,
            selected_asset_name=request.selected_asset_name,
            selected_business_service=request.selected_business_service
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario quantification error: {str(e)}")

@router.post("/what-if")
def run_scenario_what_if(request: WhatIfRequest):
    """
    Executes scenario-specific What-If mitigations (Patch Log4j, DMZ isolation, WAF, Privileged MFA, EDR).
    Recalculates LEF, SLE, EAL, Modeled Risk Reduction, and Cost through FAIR engine.
    """
    try:
        return scenario_engine.run_what_if_analysis(
            cve_id=request.cve_id or "CVE-2021-44228",
            enterprise_overrides=request.enterprise_overrides
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"What-If simulation error: {str(e)}")

@router.post("/optimize")
def optimize_scenario_investment(request: OptimizationRequest):
    """
    Solves budget-constrained knapsack optimization using Google OR-Tools SCIP solver.
    Recommends optimal security controls maximizing modeled risk reduction under the given budget.
    """
    try:
        return scenario_engine.optimize_scenario_investment(
            cve_id=request.cve_id or "CVE-2021-44228",
            budget=request.budget or 5000000.0,
            enterprise_overrides=request.enterprise_overrides
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@router.post("/ciso-decision")
def record_ciso_governance_decision(request: CISODecisionRequest):
    """
    Records human-in-the-loop CISO governance decision (APPROVE, REJECT, REQUEST_REVIEW).
    If APPROVED: Commits an immutable block on the Cryptographic Blockchain Audit Ledger with canonical SHA-256 hash.
    """
    try:
        return scenario_engine.record_ciso_decision(
            cve_id=request.cve_id,
            decision=request.decision,
            ciso_name=request.ciso_name or "Chief Information Security Officer",
            decision_notes=request.decision_notes or "Authorized for enterprise implementation.",
            modeled_eal=request.modeled_eal or 0.0,
            recommended_investment=request.recommended_investment or 0.0,
            recommended_controls=request.recommended_controls,
            requested_changes=request.requested_changes
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CISO decision error: {str(e)}")

@router.get("/history")
def get_scenario_history():
    """
    Returns historical log of analyzed scenarios, CISO decisions, and blockchain audit commit status.
    Supports before/after mitigation exposure comparison.
    """
    return {
        "history": scenario_engine.get_history(),
        "total_records": len(scenario_engine.get_history())
    }
