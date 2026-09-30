"""
Expected Annual Loss (EAL) & Enterprise Aggregation Engine.
Distinguishes between:
1. Scenario-Level EAL: EAL_i = SLE_i * ARO_i (or LEF_i)
2. Enterprise Modeled Aggregated EAL: Sum of modeled scenario/asset exposures across the enterprise.

Units:
    - SLE: INR (₹) / incident
    - ARO / LEF: incidents / year
    - EAL: INR (₹) / year
"""

from typing import Dict, Any, List, Optional
from app.risk_engine.loss_magnitude import calculate_single_loss_expectancy
from app.risk_engine.fair_model import run_fair_analysis

def calculate_eal(
    risk_score: Optional[float] = None,       # Backwards-compatible legacy positional argument
    asset_criticality: float = 95.0,
    has_active_exploit: bool = False,
    is_internet_exposed: bool = False,
    threat_activity: Optional[float] = None,
    cvss_score: Optional[float] = None,
    control_coverage: float = 70.0,
    control_effectiveness: float = 75.0,
    in_attack_path: bool = False,
    business_importance: Optional[float] = None,
    data_sensitivity: Optional[float] = None,
    revenue_dependency: Optional[float] = None,
    regulatory_importance: Optional[float] = None,
    assumptions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Backwards-compatible interface calculating scenario/asset EAL.
    Strictly satisfies EAL = SLE * ARO (LEF).
    Decoupled: Asset Criticality only influences SLE, NOT likelihood/LEF.
    """
    # Technical factors only for threat activity:
    # If caller passed legacy risk_score, use it only as technical threat intensity (capped at 100)
    # never as a product of asset criticality
    if threat_activity is not None:
        t_activity = threat_activity
    elif risk_score is not None:
        t_activity = min(100.0, max(10.0, risk_score))
    else:
        t_activity = 88.0 if has_active_exploit else 60.0

    c_score = cvss_score if cvss_score is not None else (9.8 if has_active_exploit else 7.5)

    res = run_fair_analysis(
        asset_criticality=asset_criticality,
        threat_activity=t_activity,
        cvss_score=c_score,
        active_exploitation=has_active_exploit,
        is_internet_exposed=is_internet_exposed,
        control_coverage=control_coverage,
        control_effectiveness=control_effectiveness,
        in_attack_path=in_attack_path,
        business_importance=business_importance,
        data_sensitivity=data_sensitivity,
        revenue_dependency=revenue_dependency,
        regulatory_importance=regulatory_importance,
        assumptions_override=assumptions
    )
    return {
        "expected_annual_loss": res["expected_annual_loss"],
        "single_loss_expectancy": res["single_loss_expectancy"],
        "annualized_rate_of_occurrence": res["annualized_rate_of_occurrence"],
        "loss_event_frequency": res["loss_event_frequency"],
        "annual_incident_probability": res["annual_incident_probability"],
        "threat_event_frequency": res["threat_event_frequency"],
        "vulnerability_exploitability": res["vulnerability_exploitability"],
        "control_residual_weakness": res["control_residual_weakness"],
        "loss_range_min": res["loss_range_min"],
        "loss_range_max": res["loss_range_max"],
        "confidence_percentage": res["confidence_percentage"],
        "loss_breakdown": res["loss_breakdown"],
        "primary_loss_total": res["primary_loss_total"],
        "secondary_loss_total": res["secondary_loss_total"],
        "units": res["units"],
        "modeled_label": "MODELED ESTIMATE",
        "mathematical_consistency": res["mathematical_consistency"],
        "disclaimer": "Modeled estimate based on FAIR-aligned quantitative cyber risk principles. Not a guaranteed balance-sheet loss."
    }

def calculate_enterprise_aggregated_eal(
    scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Aggregates scenario-level modeled exposures into the Enterprise Modeled Aggregated EAL.
    Enterprise Modeled EAL = Sum of Scenario EALs
    """
    if not scenarios:
        return {
            "enterprise_modeled_eal": 0.0,
            "enterprise_modeled_eal_label": "₹0.00",
            "loss_range_min": 0.0,
            "loss_range_max": 0.0,
            "scenario_count": 0,
            "aggregation_formula": "Enterprise Modeled EAL = Sum of All Modeled Scenario Exposures",
            "modeled_label": "MODELED AGGREGATED EAL"
        }

    total_eal = sum(s.get("expected_annual_loss", 0.0) for s in scenarios)
    min_eal = sum(s.get("loss_magnitude_min", s.get("expected_annual_loss", 0.0) * 0.76) for s in scenarios)
    max_eal = sum(s.get("loss_magnitude_max", s.get("expected_annual_loss", 0.0) * 1.35) for s in scenarios)

    eal_label = f"₹{round(total_eal/10000000, 2)} Crore" if total_eal >= 10000000 else f"₹{round(total_eal/100000, 1)} Lakh"

    return {
        "enterprise_modeled_eal": round(total_eal, 2),
        "enterprise_modeled_eal_label": eal_label,
        "loss_range_min": round(min_eal, 2),
        "loss_range_max": round(max_eal, 2),
        "scenario_count": len(scenarios),
        "aggregation_formula": "Enterprise Modeled EAL = Sum of All Modeled Scenario Exposures",
        "modeled_label": "MODELED AGGREGATED EAL",
        "disclaimer": "All figures are modeled aggregated estimates based on quantitative probabilistic methods. Never present as guaranteed losses."
    }

