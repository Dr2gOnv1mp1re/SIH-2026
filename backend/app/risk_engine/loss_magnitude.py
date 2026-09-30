"""
FAIR-Aligned Loss Magnitude (LM) & Single Loss Expectancy (SLE) Engine.
Monetizes cyber risk into explicit, defensible balance-sheet loss components:
- Primary Loss: Operational Downtime, Incident Response & Forensics, Data Recovery.
- Secondary Loss: Regulatory Fines (RBI/DPDP), Business Interruption & Customer Churn.

Units:
    - Single Loss Expectancy (SLE): INR (₹) / incident
    - Primary Loss: INR (₹)
    - Secondary Loss: INR (₹)
"""

from typing import Dict, Any, Optional
from app.risk_engine.assumptions import get_assumptions

def calculate_single_loss_expectancy(
    asset_criticality: float,            # 0-100
    hourly_downtime_cost: float = 300000.0, # ₹3 Lakh/hr
    outage_hours: float = 8.0,
    ir_hours: float = 40.0,
    ir_hourly_rate: float = 25000.0,      # ₹25,000/hr
    data_recovery_base: float = 1500000.0,# ₹15 Lakh
    regulatory_fine_base: float = 2000000.0, # ₹20 Lakh
    business_impact_base: float = 2500000.0, # ₹25 Lakh
    business_importance: Optional[float] = None,
    data_sensitivity: Optional[float] = None,
    revenue_dependency: Optional[float] = None,
    regulatory_importance: Optional[float] = None,
    assumptions_override: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes Single Loss Expectancy (SLE) in Indian Rupees (INR).
    All component losses are derived directly from asset criticality and enterprise scale:
        SLE = Downtime Loss + Incident Response Loss + Data Recovery Loss +
              Regulatory/Legal Loss + Business Interruption Loss
    """
    overrides = assumptions_override or {}
    downtime_rate = overrides.get("hourly_downtime_cost", hourly_downtime_cost)
    outage_h = overrides.get("outage_hours", outage_hours)
    ir_h = overrides.get("incident_response_base_hours", overrides.get("ir_hours", ir_hours))
    ir_rate = overrides.get("incident_response_hourly_rate", ir_hourly_rate)
    recovery_base = overrides.get("data_recovery_base_cost", data_recovery_base)
    reg_base = overrides.get("legal_regulatory_base_cost", regulatory_fine_base)
    biz_base = overrides.get("business_interruption_base_cost", business_impact_base)

    crit_factor = max(0.1, min(1.0, asset_criticality / 100.0))
    
    # Granular factors if available, else fall back to asset criticality factor
    dt_factor = max(0.1, min(1.0, business_importance / 100.0)) if business_importance is not None else crit_factor
    data_factor = max(0.1, min(1.0, data_sensitivity / 100.0)) if data_sensitivity is not None else crit_factor
    reg_factor = max(0.1, min(1.0, regulatory_importance / 100.0)) if regulatory_importance is not None else crit_factor
    biz_factor = max(0.1, min(1.0, revenue_dependency / 100.0)) if revenue_dependency is not None else crit_factor

    # 1. Primary Losses
    downtime_loss = round(downtime_rate * outage_h * dt_factor, 2)
    ir_loss = round(ir_h * ir_rate, 2)
    recovery_loss = round(recovery_base * data_factor, 2)
    primary_loss = round(downtime_loss + ir_loss + recovery_loss, 2)

    # 2. Secondary Losses (Regulatory statutory penalties and reputational/business impact)
    regulatory_loss = round(reg_base * reg_factor, 2)
    business_interruption_loss = round(biz_base * biz_factor, 2)
    secondary_loss = round(regulatory_loss + business_interruption_loss, 2)

    # Total Single Loss Expectancy (SLE) - exactly equals the sum of the 5 modeled loss components
    total_sle = round(downtime_loss + ir_loss + recovery_loss + regulatory_loss + business_interruption_loss, 2)

    return {
        "single_loss_expectancy": total_sle,
        "sle_label": f"₹{round(total_sle/100000, 1)} Lakh" if total_sle < 10000000 else f"₹{round(total_sle/10000000, 2)} Crore",
        "primary_loss_total": primary_loss,
        "secondary_loss_total": secondary_loss,
        "components": {
            "downtime_loss": downtime_loss,
            "incident_response_loss": ir_loss,
            "data_recovery_loss": recovery_loss,
            "regulatory_legal_loss": regulatory_loss,
            "business_interruption_loss": business_interruption_loss,
            "total_potential_loss": total_sle
        },
        "asset_criticality": asset_criticality,
        "currency": "INR (₹)",
        "unit": "INR per incident",
        "units": {
            "single_loss_expectancy": "INR / incident",
            "downtime_loss": "INR",
            "incident_response_loss": "INR",
            "data_recovery_loss": "INR",
            "regulatory_legal_loss": "INR",
            "business_interruption_loss": "INR"
        },
        "mathematical_consistency": {
            "sum_of_five_components": total_sle,
            "is_sum_exact": True,
            "formula": "SLE = Downtime Loss + Incident Response Loss + Data Recovery Loss + Regulatory/Legal Loss + Business Interruption Loss"
        },
        "modeled_label": "MODELED SLE"
    }

