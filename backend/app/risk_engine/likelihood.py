"""
Likelihood & Loss Event Frequency (LEF) / ARO Engine.
Under FAIR-aligned quantitative cyber risk methodology:
    Loss Event Frequency (LEF) = Threat Event Frequency (TEF) * Vulnerability Exploitability given controls

Units:
    - Threat Event Frequency (TEF): events / year
    - Vulnerability Exploitability: probability in [0, 1]
    - Control Residual Weakness: fraction in [0, 1]
    - Loss Event Frequency (LEF / ARO): incidents / year
    - Annual Incident Probability: probability in [0, 1] (P = 1 - exp(-LEF))
NOTE: Likelihood and frequency are strictly independent of Asset Criticality.
"""

import math
from typing import Dict, Any, Optional
from app.risk_engine.threat_frequency import calculate_threat_event_frequency
from app.risk_engine.vulnerability_exposure import calculate_vulnerability_exploitability
from app.risk_engine.control_effectiveness import calculate_control_mitigation_factor

def calculate_loss_event_frequency(
    threat_activity_level: float = 85.0,
    cvss_score: float = 9.8,
    active_exploitation: bool = True,
    is_internet_facing: bool = True,
    control_coverage: float = 70.0,
    control_effectiveness: float = 75.0,
    in_attack_path: bool = True
) -> Dict[str, Any]:
    """
    Calculates Annualized Rate of Occurrence (ARO) / Loss Event Frequency (LEF).
    CRITICAL: Does NOT accept or use Asset Criticality.
    """
    # 1. Threat Event Frequency (TEF in events / year)
    tef_res = calculate_threat_event_frequency(
        threat_activity_level=threat_activity_level,
        is_internet_facing=is_internet_facing,
        is_targeted_sector=True,
        has_active_cve_exploit=active_exploitation
    )
    tef = tef_res["threat_event_frequency"]

    # 2. Vulnerability Exploitability (Probability 0.0 to 1.0)
    vuln_res = calculate_vulnerability_exploitability(
        cvss_score=cvss_score,
        active_exploitation=active_exploitation,
        exploit_code_available=True,
        patch_available=True
    )
    vuln_prob = vuln_res["exploitability_probability"]

    # 3. Control Mitigation & Residual Weakness
    ctrl_res = calculate_control_mitigation_factor(
        coverage_percentage=control_coverage,
        effectiveness_percentage=control_effectiveness
    )
    weakness = ctrl_res["residual_weakness"]

    # Attack path multiplier (lateral chain position increases threat contact / exploitability)
    path_mult = 1.20 if in_attack_path else 1.0

    # LEF = TEF * (Vuln * Residual Weakness * Path)
    annualized_occurrence = tef * (vuln_prob * weakness * path_mult)
    # Realistic enterprise bounds for single asset scenario: [0.01, 5.0] incidents / year
    annualized_occurrence = round(max(0.01, min(5.0, annualized_occurrence)), 3)

    # Annual Incident Probability: P(at least 1 loss event in 1 year under Poisson process)
    # P = 1 - exp(-LEF)
    annual_probability = round(1.0 - math.exp(-annualized_occurrence), 4)

    return {
        "annualized_rate_of_occurrence": annualized_occurrence,
        "loss_event_frequency": annualized_occurrence,
        "threat_event_frequency": tef,
        "vulnerability_exploitability": vuln_prob,
        "control_residual_weakness": weakness,
        "control_strength": ctrl_res["control_strength"],
        "annual_incident_probability": annual_probability,
        "in_attack_path": in_attack_path,
        "frequency_unit": "incidents / year",
        "probability_unit": "probability [0, 1] per year",
        "modeled_label": "MODELED ARO / LEF"
    }

