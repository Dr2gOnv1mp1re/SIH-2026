"""
Backwards-compatible bridge forwarding to centralized risk engine.
Ensures single source of truth for all Monte Carlo simulations.
"""

from app.risk_engine.monte_carlo import run_monte_carlo_simulation

__all__ = ["run_monte_carlo_simulation"]
