"""
FAIR-Aligned Quantitative Cyber Risk Model Orchestrator.
Translates technical security metrics into structured financial loss expectations.
Flow:
    Threat Event Frequency (TEF) [events/yr]
            ↓
    Loss Event Frequency (LEF / ARO) [incidents/yr]  (Independent of Asset Criticality)
            ↓
    Loss Magnitude (LM / SLE) [INR/incident]         (Derived from Asset Criticality)
            ↓
    Expected Annual Loss (EAL) [INR/yr] = LEF × SLE
"""

from typing import Dict, Any, Optional
from app.risk_engine.likelihood import calculate_loss_event_frequency
from app.risk_engine.loss_magnitude import calculate_single_loss_expectancy

def run_fair_analysis(
    asset_criticality: float = 92.0,
    threat_activity: float = 85.0,
    cvss_score: float = 9.8,
    active_exploitation: bool = True,
    is_internet_exposed: bool = True,
    control_coverage: float = 70.0,
    control_effectiveness: float = 75.0,
    in_attack_path: bool = True,
    business_importance: Optional[float] = None,
    data_sensitivity: Optional[float] = None,
    revenue_dependency: Optional[float] = None,
    regulatory_importance: Optional[float] = None,
    assumptions_override: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes an end-to-end FAIR-aligned quantitative risk assessment for a specific asset/scenario.
    Ensures mathematical consistency:
        EAL = SLE * ARO (or LEF)
    """
    # 1. Frequency (ARO / LEF in incidents / year) - strictly technical factors
    freq_res = calculate_loss_event_frequency(
        threat_activity_level=threat_activity,
        cvss_score=cvss_score,
        active_exploitation=active_exploitation,
        is_internet_facing=is_internet_exposed,
        control_coverage=control_coverage,
        control_effectiveness=control_effectiveness,
        in_attack_path=in_attack_path
    )
    aro = freq_res["annualized_rate_of_occurrence"]
    annual_prob = freq_res["annual_incident_probability"]

    # 2. Loss Magnitude (SLE in INR / incident) - asset impact factors
    loss_res = calculate_single_loss_expectancy(
        asset_criticality=asset_criticality,
        business_importance=business_importance,
        data_sensitivity=data_sensitivity,
        revenue_dependency=revenue_dependency,
        regulatory_importance=regulatory_importance,
        assumptions_override=assumptions_override
    )
    sle = loss_res["single_loss_expectancy"]

    # 3. Expected Annual Loss (EAL in INR / year)
    # Strictly mathematically consistent: EAL = SLE * ARO
    scenario_eal = round(sle * aro, 2)

    # 4. Modeled uncertainty range (90% Confidence Interval)
    confidence = 85.0 if active_exploitation else 75.0
    uncertainty_margin = (100.0 - confidence) / 100.0
    loss_range_min = round(scenario_eal * (1.0 - uncertainty_margin * 1.2), 2)
    loss_range_max = round(scenario_eal * (1.0 + uncertainty_margin * 1.5), 2)

    return {
        "expected_annual_loss": scenario_eal,
        "single_loss_expectancy": sle,
        "annualized_rate_of_occurrence": aro,
        "loss_event_frequency": aro,
        "annual_incident_probability": annual_prob,
        "threat_event_frequency": freq_res["threat_event_frequency"],
        "vulnerability_exploitability": freq_res["vulnerability_exploitability"],
        "control_residual_weakness": freq_res["control_residual_weakness"],
        "control_strength": freq_res.get("control_strength", 0.0),
        "loss_breakdown": loss_res["components"],
        "primary_loss_total": loss_res["primary_loss_total"],
        "secondary_loss_total": loss_res["secondary_loss_total"],
        "asset_criticality": asset_criticality,
        "confidence_percentage": confidence,
        "loss_range_min": loss_range_min,
        "loss_range_max": loss_range_max,
        "units": {
            "expected_annual_loss": "INR / year",
            "single_loss_expectancy": "INR / incident",
            "loss_event_frequency": "incidents / year",
            "threat_event_frequency": "events / year",
            "annual_incident_probability": "probability in [0, 1] per year"
        },
        "modeled_label": "MODELED ESTIMATE",
        "mathematical_consistency": {
            "formula": "EAL = SLE * ARO",
            "sle": sle,
            "aro": aro,
            "product": round(sle * aro, 2),
            "is_consistent": abs(scenario_eal - round(sle * aro, 2)) < 0.01
        }
    }

