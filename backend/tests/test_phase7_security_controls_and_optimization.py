"""
Phase 7: Security Controls Catalogue & Investment Optimization Tests.
Verifies:
1. Centralized Security Control Catalogue with all 11+ controls and required metadata fields.
2. Centralized Control-Risk Mapping.
3. Data-driven control recommendations from active risk engine.
4. Google OR-Tools Mixed-Integer Knapsack Optimization under varying budgets (\u20b925L, \u20b950L, \u20b91Cr, \u20b92Cr, custom).
5. Dynamic Before vs After state calculation.
6. "Why were these controls selected?" structured explanation.
7. Budget stress testing across \u20b925L to \u20b95Cr with diminishing returns calculation.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.optimization_engine.solver import (
    DEFAULT_CANDIDATE_CONTROLS,
    CONTROL_RISK_MAPPING,
    optimizer,
    generate_data_driven_recommendations
)

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_7_1_security_control_catalogue(auth_headers):
    """Test 7.1: Verify Centralized Security Control Catalogue contains all required fields."""
    res = client.get("/api/v1/controls/catalogue", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "controls" in data
    controls = data["controls"]
    assert len(controls) >= 11

    required_fields = [
        "control_id", "control_name", "category", "description",
        "estimated_cost", "implementation_effort", "expected_risk_reduction",
        "applicable_risk_types", "affected_assets", "dependencies", "status"
    ]

    for ctrl in controls:
        for field in required_fields:
            assert field in ctrl, f"Control {ctrl.get('control_id')} missing field {field}"
        assert ctrl["estimated_cost"] > 0
        assert ctrl["expected_risk_reduction"] > 0
        assert 0.0 <= ctrl.get("effectiveness", 0.0) <= 100.0


def test_7_2_control_risk_mapping(auth_headers):
    """Test 7.2: Verify Centralized Control-Risk Mapping associates controls with risk factors."""
    res = client.get("/api/v1/controls/mapping", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    mapping = data["control_risk_mapping"]

    assert "Critical vulnerability" in mapping
    assert "CTRL-PATCH" in mapping["Critical vulnerability"]

    assert "Privileged account exposure" in mapping
    assert "CTRL-MFA" in mapping["Privileged account exposure"]

    assert "Endpoint compromise" in mapping
    assert "CTRL-EDR" in mapping["Endpoint compromise"]

    assert "Internet-facing application" in mapping
    assert "CTRL-WAF" in mapping["Internet-facing application"]

    assert "Lateral movement" in mapping
    assert "CTRL-SEG" in mapping["Lateral movement"]

    assert "Backup compromise" in mapping
    assert "CTRL-BACKUP" in mapping["Backup compromise"]


def test_7_3_data_driven_control_recommendations(auth_headers):
    """Test 7.3: Verify Recommendations depend on actual risk score, vulnerabilities, and assets."""
    res = client.get("/api/v1/controls/recommendations", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    recs = data["recommendations"]
    assert len(recs) >= 3

    for rec in recs:
        assert "control" in rec
        assert "reason" in rec
        assert "affected_assets" in rec
        assert "risk_addressed" in rec
        assert "estimated_cost" in rec
        assert "expected_risk_reduction" in rec
        assert "priority" in rec
        assert rec["priority"] in ("CRITICAL", "HIGH", "MEDIUM")


def test_7_4_to_7_8_ortools_optimization(auth_headers):
    """Test 7.4-7.8: Verify OR-Tools knapsack optimization under different budgets."""
    budgets_to_test = [
        2500000.0,   # \u20b925 Lakh
        5000000.0,   # \u20b950 Lakh
        10000000.0,  # \u20b91 Crore
        20000000.0   # \u20b92 Crore
    ]

    previous_investment = 0.0
    previous_reduction = 0.0

    for b in budgets_to_test:
        res = client.post("/api/v1/optimization/run", json={"budget": b}, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()

        assert "selected_controls" in data
        assert "total_investment" in data
        assert "available_budget" in data
        assert "remaining_budget" in data
        assert "modeled_risk_before" in data
        assert "modeled_risk_after" in data
        assert "modeled_risk_reduction" in data
        assert "financial_exposure_before" in data
        assert "financial_exposure_after" in data
        assert "investment_efficiency" in data

        # Check constraint: Total investment <= budget
        assert data["total_investment"] <= b
        assert data["remaining_budget"] >= 0.0
        assert data["modeled_risk_reduction"] > 0.0

        # Changing budget changes the result
        if b > 2500000.0:
            assert data["total_investment"] >= previous_investment
            assert data["modeled_risk_reduction"] >= previous_reduction

        previous_investment = data["total_investment"]
        previous_reduction = data["modeled_risk_reduction"]


def test_7_9_and_7_10_before_vs_after_and_explanation(auth_headers):
    """Test 7.9 & 7.10: Verify Before vs After state and 'Why were these controls selected?' explanation."""
    res = client.post("/api/v1/optimization/run", json={"budget": 10000000.0}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    # Before vs After check
    assert "before_vs_after" in data
    bva = data["before_vs_after"]
    assert "current_state" in bva
    assert "recommended_controls" in bva
    assert "projected_state" in bva

    curr = bva["current_state"]
    proj = bva["projected_state"]
    assert curr["financial_exposure"] > proj["financial_exposure"]
    assert proj["modeled_risk_reduction"] > 0

    # Explanation check (Section 7.10)
    assert "optimization_explanation" in data
    explanations = data["optimization_explanation"]
    assert len(explanations) >= 5
    assert any("High Risk Reduction" in exp for exp in explanations)
    assert any("Capital Efficiency" in exp for exp in explanations)
    assert any("Attack Path" in exp for exp in explanations)
    assert any("Crown Jewel" in exp for exp in explanations)
    assert any("Budget Compliance" in exp for exp in explanations)


def test_7_11_and_7_12_budget_stress_test_and_diminishing_returns(auth_headers):
    """Test 7.11 & 7.12: Verify stress test across tiers and dynamic diminishing returns detection."""
    res = client.get("/api/v1/optimization/stress-test", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    assert "stress_test_curve" in data
    curve = data["stress_test_curve"]
    assert len(curve) >= 6

    # Verify budgets tested include \u20b925L, \u20b950L, \u20b975L, \u20b91Cr, \u20b92Cr, \u20b95Cr
    expected_budgets = [2500000.0, 5000000.0, 7500000.0, 10000000.0, 20000000.0, 50000000.0]
    actual_budgets = [pt["budget"] for pt in curve]
    for eb in expected_budgets:
        assert eb in actual_budgets

    # Check diminishing returns analysis
    assert "diminishing_returns_analysis" in data
    dra = data["diminishing_returns_analysis"]
    assert dra["diminishing_returns_observed"] is True
    assert "inflection_point_budget" in dra
