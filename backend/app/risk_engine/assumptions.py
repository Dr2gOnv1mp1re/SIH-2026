"""
Centralized Risk Engine Model Assumptions & Parameter Configurations.
Defines explicit quantitative risk boundaries, financial loss factors,
and stochastic distribution assumptions. Never hides assumptions.
"""

from typing import Dict, Any

DEFAULT_RISK_ASSUMPTIONS: Dict[str, Any] = {
    # Organization financial scale (ABC Bank Default)
    "currency": "INR (₹)",
    "annual_revenue": 5000000000.0,       # ₹500 Crore
    "cybersecurity_budget": 10000000.0,    # ₹1.00 Crore
    "enterprise_risk_appetite": 10000000.0,# ₹1.00 Crore max acceptable EAL
    "critical_asset_risk_appetite": 1000000.0, # ₹10 Lakh per critical asset

    # FAIR Loss Magnitude Base Parameters (in INR)
    "hourly_downtime_cost": 300000.0,      # ₹3.0 Lakh / hour
    "incident_response_hourly_rate": 25000.0, # ₹25,000 / hour
    "incident_response_base_hours": 40.0,  # 40 hours typical incident response
    "data_recovery_base_cost": 1500000.0,  # ₹15 Lakh database restoration base
    "legal_regulatory_base_cost": 2000000.0, # ₹20 Lakh regulatory fine base (DPDP / RBI)
    "business_interruption_base_cost": 2500000.0, # ₹25 Lakh customer/merchant impact base

    # Probability & Likelihood Weights
    "threat_weight": 0.40,
    "vulnerability_weight": 0.60,
    "active_exploit_multiplier": 1.35,
    "internet_exposure_multiplier": 1.25,
    "attack_path_multiplier": 1.20,
    "max_control_mitigation": 0.80,        # Maximum 80% risk reduction from controls

    # Stochastic / Monte Carlo Assumptions
    "monte_carlo_default_iterations": 10000,
    "loss_distribution_type": "Lognormal (mu, sigma=0.55)",
    "frequency_distribution_type": "Bernoulli / Poisson",
    "confidence_interval_pct": 90.0,

    # Modeling Metadata
    "model_name": "FAIR-Aligned Quantitative Cyber Risk Engine",
    "framework_version": "v2.6.0",
    "data_type": "Synthetic Telemetry & Historical Threat Feed",
    "disclaimer": "All figures are modeled quantitative estimates derived from FAIR principles. Not guaranteed balance sheet losses."
}

def get_assumptions(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Returns a copy of the default assumptions merged with any overrides."""
    result = dict(DEFAULT_RISK_ASSUMPTIONS)
    if overrides:
        result.update(overrides)
    return result
