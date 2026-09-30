"""
Control Effectiveness & Defense-in-Depth Mitigation Engine.
Calculates how deployed technical controls reduce the likelihood and magnitude of cyber events.
"""

from typing import Dict, Any, List, Optional

def calculate_control_mitigation_factor(
    coverage_percentage: float,       # 0 - 100%
    effectiveness_percentage: float,  # 0 - 100%
    maturity_level: int = 3,          # 1 to 5 CMMI
    diminishing_returns: float = 0.90
) -> Dict[str, Any]:
    """
    Calculates Control Resistance Strength (0.0 to 1.0) and Residual Weakness (1.0 - Strength).
    """
    cov = max(0.0, min(100.0, coverage_percentage)) / 100.0
    eff = max(0.0, min(100.0, effectiveness_percentage)) / 100.0
    mat_mult = 0.60 + (maturity_level / 5.0) * 0.40  # 1->0.68, 3->0.84, 5->1.0

    # Composite mitigation factor capped at 0.85 (defense-in-depth always leaves residual risk)
    strength = min(0.85, cov * eff * mat_mult * diminishing_returns)
    residual_weakness = max(0.15, 1.0 - strength)

    return {
        "control_strength": round(strength, 3),
        "residual_weakness": round(residual_weakness, 3),
        "coverage_percentage": coverage_percentage,
        "effectiveness_percentage": effectiveness_percentage,
        "maturity_level": maturity_level,
        "modeled_label": "MODELED CONTROL RESISTANCE"
    }

def aggregate_portfolio_mitigation(
    controls: List[Dict[str, Any]]
) -> float:
    """
    Aggregates defense-in-depth across multiple controls with diminishing return synergy.
    """
    if not controls:
        return 0.0

    # Serial defense: 1 - prod(1 - eff_i)
    unmitigated = 1.0
    for ctrl in controls:
        cov = ctrl.get("coverage_percentage", 70.0) / 100.0
        eff = ctrl.get("effectiveness_percentage", 75.0) / 100.0
        dim = ctrl.get("diminishing_return_factor", 0.85)
        single_eff = cov * eff * dim
        unmitigated *= (1.0 - single_eff)

    return round(min(0.90, max(0.0, 1.0 - unmitigated)), 3)
