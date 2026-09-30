import math
from typing import Dict, List, Any, Optional
from app.risk_engine.loss_magnitude import calculate_single_loss_expectancy
from app.risk_engine.likelihood import calculate_loss_event_frequency

def calculate_asset_criticality(
    business_importance: float,
    data_sensitivity: float,
    revenue_dependency: float,
    regulatory_importance: float,
    internet_exposed: bool,
    downtime_tolerance_hours: float
) -> float:
    """
    Calculates Asset Criticality Score (0-100) based on enterprise metrics.
    Represents the business consequence / impact factor, independent of attack likelihood.
    """
    # Lower tolerance hours means higher criticality penalty
    downtime_factor = 100.0 if downtime_tolerance_hours <= 0.5 else max(10.0, 100.0 - (downtime_tolerance_hours * 8.0))
    internet_factor = 95.0 if internet_exposed else 60.0

    score = (
        business_importance * 0.25 +
        data_sensitivity * 0.25 +
        revenue_dependency * 0.20 +
        regulatory_importance * 0.15 +
        downtime_factor * 0.10 +
        internet_factor * 0.05
    )
    return round(min(100.0, max(0.0, score)), 1)


def get_risk_level(score: float) -> str:
    if score >= 80.0:
        return "CRITICAL"
    elif score >= 60.0:
        return "VERY HIGH"
    elif score >= 40.0:
        return "HIGH"
    elif score >= 20.0:
        return "MEDIUM"
    return "LOW"


def calculate_risk_score(
    threat_likelihood: float,        # 0-100 (Technical threat activity)
    vulnerability_severity: float,   # 0-100 (CVSS * 10)
    asset_criticality: float,        # 0-100 (Business impact factor)
    control_effectiveness: float,    # 0-100 (Technical control strength)
    has_active_exploit: bool = False,
    is_internet_exposed: bool = False,
    in_attack_path: bool = False,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Continuous Cyber Risk Calculation with FAIR-aligned separation:
    1. Technical Likelihood: Threat, CVSS, Exploitability, Controls, Exposure (NO Asset Criticality)
    2. Loss Magnitude / SLE: Asset Criticality & Financial parameters
    3. Expected Annual Loss (EAL): LEF * SLE
    4. Composite Risk Index: Standard 2D matrix combination of Likelihood and Impact
    """
    if not weights:
        weights = {
            "threat": 0.40,
            "vulnerability": 0.60
        }

    # Active exploitation and internet exposure multipliers (affect technical likelihood only)
    exploit_multiplier = 1.35 if has_active_exploit else 1.0
    exposure_multiplier = 1.25 if is_internet_exposed else 1.0
    attack_path_multiplier = 1.20 if in_attack_path else 1.0

    # Control mitigation factor (1.0 = no control, 0.2 = maximum defense-in-depth)
    control_weakness = max(0.20, 1.0 - (control_effectiveness / 100.0) * 0.8)

    # Combined technical vulnerability & threat intensity
    raw_intensity = (
        (threat_likelihood * weights["threat"]) +
        (min(100.0, vulnerability_severity * exploit_multiplier) * weights["vulnerability"])
    )

    # Technical Likelihood Score (0-100) - STRICTLY INDEPENDENT OF ASSET CRITICALITY
    raw_likelihood = (
        raw_intensity *
        control_weakness *
        exposure_multiplier *
        attack_path_multiplier *
        1.15
    )
    likelihood_score = round(min(100.0, max(0.0, raw_likelihood)), 1)

    # FAIR Frequency (LEF / ARO in incidents / year)
    cvss_val = vulnerability_severity / 10.0
    freq_result = calculate_loss_event_frequency(
        threat_activity_level=threat_likelihood,
        cvss_score=cvss_val,
        active_exploitation=has_active_exploit,
        is_internet_facing=is_internet_exposed,
        control_effectiveness=control_effectiveness,
        in_attack_path=in_attack_path
    )
    lef = freq_result["loss_event_frequency"]

    # FAIR Loss Magnitude (SLE in INR) - uses Asset Criticality
    loss_result = calculate_single_loss_expectancy(asset_criticality=asset_criticality)
    sle = loss_result["single_loss_expectancy"]

    # FAIR Expected Annual Loss (EAL)
    eal = round(sle * lef, 2)

    # Composite normalized risk score (0-100) for matrix visualization:
    # Combines Technical Likelihood (0-100) and Asset Consequence (0-100)
    # Uses 2D Risk Matrix geometric weighting
    composite_risk = math.sqrt(likelihood_score * asset_criticality)
    final_score = round(min(100.0, max(0.0, composite_risk)), 1)

    # Decompose contributors for explainability
    vuln_weight = 25.0 if vulnerability_severity > 70 else 15.0
    exploit_weight = 20.0 if has_active_exploit else 5.0
    crit_weight = 20.0 if asset_criticality > 75 else 15.0
    exposure_weight = 15.0 if is_internet_exposed else 5.0
    control_weight = round(control_weakness * 20.0, 1)

    total_raw = vuln_weight + exploit_weight + crit_weight + exposure_weight + control_weight
    other_factor = max(0.0, round(100.0 - total_raw, 1))

    contributors = {
        "critical_vulnerability_pct": round((vuln_weight / total_raw) * 100, 1),
        "active_exploitation_pct": round((exploit_weight / total_raw) * 100, 1),
        "asset_criticality_pct": round((crit_weight / total_raw) * 100, 1),
        "internet_exposure_pct": round((exposure_weight / total_raw) * 100, 1),
        "weak_control_segmentation_pct": round((control_weight / total_raw) * 100, 1),
        "other_environmental_factors_pct": round(other_factor, 1)
    }

    return {
        "risk_score": final_score,
        "risk_level": get_risk_level(final_score),
        "technical_likelihood_score": likelihood_score,
        "likelihood_score": likelihood_score,
        "asset_criticality": asset_criticality,
        "control_weakness": round(control_weakness * 100, 1),
        "loss_event_frequency": lef,
        "annualized_rate_of_occurrence": lef,
        "single_loss_expectancy": sle,
        "expected_annual_loss": eal,
        "loss_breakdown": loss_result["components"],
        "contributors": contributors,
        "modeled_label": "MODELED ESTIMATE"
    }

