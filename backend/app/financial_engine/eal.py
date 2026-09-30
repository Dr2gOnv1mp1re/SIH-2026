"""
Backwards-compatible bridge forwarding to centralized risk engine.
Ensures single source of truth for all financial risk calculations.
"""

from app.risk_engine.eal import (
    calculate_single_loss_expectancy,
    calculate_eal,
    calculate_enterprise_aggregated_eal
)
from app.risk_engine.fair_model import run_fair_analysis

__all__ = [
    "calculate_single_loss_expectancy",
    "calculate_eal",
    "calculate_enterprise_aggregated_eal",
    "run_fair_analysis"
]
