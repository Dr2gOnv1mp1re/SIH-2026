"""
Phase 4: Financial Risk Quantification Automated Test Suite.
Verifies:
1. Single Loss Expectancy (SLE) calculation and FAIR loss components.
2. Annualized Rate of Occurrence (ARO) and probability-frequency conversion.
3. Strict mathematical consistency: EAL = SLE * ARO.
4. Enterprise Aggregated EAL = sum(EAL_i).
5. Missing financial data handling (Zero fabrication guarantee).
6. Monte Carlo stochastic simulation under uncertainty (percentiles, distribution).
7. Financial REST API endpoints (/financial/enterprise, /financial/assets, /financial/monte-carlo).
"""

import math
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.risk_engine.financial_service import financial_service

def test_probability_and_frequency_conversion():
    """Verify bidirectional conversion between annual probability P and Poisson ARO."""
    # Test P = 0.50 -> ARO = -ln(0.50) = 0.6931
    aro_50 = financial_service.probability_to_annual_frequency(0.50)
    assert round(aro_50, 3) == 0.693

    # Reverse: ARO = 0.6931 -> P = 1 - exp(-0.6931) = 0.50
    p_reversed = financial_service.annual_frequency_to_probability(aro_50)
    assert round(p_reversed, 2) == 0.50

    # Boundary test: low probability P = 0.05
    aro_05 = financial_service.probability_to_annual_frequency(0.05)
    assert round(aro_05, 3) == 0.051
    assert round(financial_service.annual_frequency_to_probability(aro_05), 2) == 0.05

def test_single_asset_financial_calculation_and_eal_consistency():
    """Verify SLE, ARO, and mathematical consistency EAL = SLE * ARO."""
    asset_with_explicit_impact = {
        "asset_id": "AST-FIN-01",
        "asset_name": "Retail NetBanking Core",
        "criticality_score": 95.0,
        "potential_financial_impact_inr": 20000000.0, # ₹2.00 Crore SLE
        "estimated_incident_probability": 0.40,      # 40% probability
        "control_effectiveness": 0.70
    }

    eval_res = financial_service.calculate_asset_financial_risk(asset_with_explicit_impact)
    assert eval_res["financial_data_available"] is True
    assert eval_res["single_loss_expectancy"] == 20000000.0
    
    expected_aro = financial_service.probability_to_annual_frequency(0.40)
    assert eval_res["annualized_rate_of_occurrence"] == expected_aro
    
    # EAL MUST exactly equal SLE * ARO
    expected_eal = round(eval_res["single_loss_expectancy"] * eval_res["annualized_rate_of_occurrence"], 2)
    assert eval_res["expected_annual_loss"] == expected_eal
    assert eval_res["loss_range_min"] < eval_res["expected_annual_loss"] < eval_res["loss_range_max"]

def test_missing_financial_data_handling_no_fabrication():
    """Verify that when financial data is unavailable, values are null and no fake numbers are hallucinated."""
    asset_missing_financial = {
        "asset_id": "AST-UNKNOWN-01",
        "asset_name": "Internal Workstation No Financials",
        "criticality_score": 0.0,
        "is_missing_financial": True
    }

    eval_res = financial_service.calculate_asset_financial_risk(asset_missing_financial)
    assert eval_res["financial_data_available"] is False
    assert eval_res["single_loss_expectancy"] is None
    assert eval_res["expected_annual_loss"] is None
    assert eval_res["annualized_rate_of_occurrence"] is None
    assert eval_res["sle_label"] == "Financial Data Not Available"
    assert eval_res["eal_label"] == "Financial Data Not Available"

def test_enterprise_financial_aggregation():
    """Verify enterprise EAL is strictly the sum of individual asset EALs: sum(EAL_i)."""
    assets = [
        {
            "asset_id": "A1",
            "asset_name": "Payment Gateway",
            "potential_financial_impact_inr": 10000000.0,
            "estimated_incident_probability": 0.30
        },
        {
            "asset_id": "A2",
            "asset_name": "Customer Portal",
            "potential_financial_impact_inr": 5000000.0,
            "estimated_incident_probability": 0.20
        }
    ]

    evals = [financial_service.calculate_asset_financial_risk(a) for a in assets]
    agg = financial_service.aggregate_enterprise_financial_exposure(evals)

    assert agg["financial_data_available"] is True
    expected_total_eal = round(evals[0]["expected_annual_loss"] + evals[1]["expected_annual_loss"], 2)
    assert agg["enterprise_modeled_eal"] == expected_total_eal
    assert agg["uncertainty_range"]["lower_bound_p10"] < agg["enterprise_modeled_eal"] < agg["uncertainty_range"]["upper_bound_p90"]
    assert len(agg["top_financially_exposed_assets"]) == 2

def test_monte_carlo_simulation_distributions():
    """Verify Monte Carlo simulation samples justified Poisson + Lognormal distributions."""
    sim = financial_service.run_monte_carlo(
        base_sle=15000000.0,  # ₹1.5 Cr SLE
        base_aro=0.50,        # 0.5 incidents / year
        iterations=5000,
        seed=42
    )

    assert sim["num_iterations"] == 5000
    assert "percentiles" in sim
    p = sim["percentiles"]
    assert p["p10"] <= p["p25"] <= p["p50"] <= p["p75"] <= p["p90"] <= p["p95"]
    assert sim["mean"] > 0
    assert len(sim["histogram"]) == 20
    assert sim["classification"] == "SIMULATED / STOCHASTIC UNDER UNCERTAINTY"

def test_financial_api_endpoints_integration():
    """Verify /api/v1/financial/enterprise, /assets, and /monte-carlo endpoints with authentication."""
    with TestClient(app) as client:
        login_res = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "Ciso@12345"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Enterprise financial exposure
        ent_res = client.get("/api/v1/financial/enterprise", headers=headers)
        assert ent_res.status_code == 200
        ent_data = ent_res.json()
        assert "expected_annual_loss" in ent_data
        assert "actual_observed_loss" in ent_data
        assert "modeled_financial_exposure" in ent_data
        assert "simulated_benchmark" in ent_data

        # 2. Asset-level financial exposure list
        assets_res = client.get("/api/v1/financial/assets", headers=headers)
        assert assets_res.status_code == 200
        assets_data = assets_res.json()
        assert "items" in assets_data
        assert len(assets_data["items"]) > 0
        first_asset = assets_data["items"][0]
        assert "single_loss_expectancy" in first_asset
        assert "annualized_rate_of_occurrence" in first_asset
        assert "expected_annual_loss" in first_asset

        # 3. Monte Carlo stochastic simulation endpoint
        mc_res = client.get("/api/v1/financial/monte-carlo?iterations=1000", headers=headers)
        assert mc_res.status_code == 200
        mc_data = mc_res.json()
        assert mc_data["num_iterations"] == 1000
        assert "percentiles" in mc_data
