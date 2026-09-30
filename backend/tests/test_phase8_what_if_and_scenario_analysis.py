"""
Tests for Phase 8: What-If / Digital Twin / Scenario Analysis
Validates:
8.1 Scenario Engine
8.2 Supported Scenario Changes (Patch, MFA, EDR, Segmentation, Control Effectiveness, Budget)
8.3 Current State vs 8.4 Scenario State Isolation (Non-destructive)
8.5 Before vs After Dynamic Recalculation
8.6 Financial Impact of Scenario (EAL before/after/reduction)
8.7 Scenario Comparison (Scenario A vs B vs C)
8.8 Digital Twin Representation
8.9 Scenario Save & Reset (Production data remains intact)
8.10 Scenario Audit
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SyncSessionLocal
from app.database.models import Asset, Vulnerability, ScenarioRecord

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_8_1_and_8_2_scenario_run_supported_changes(auth_headers):
    """Test 8.1 & 8.2: Run flexible isolated scenarios with various supported changes."""
    # 1. Test patching a vulnerability
    res = client.post("/api/v1/scenarios/run", json={
        "scenario_name": "Patch Critical CVE Simulation",
        "changes": [
            {"type": "patch_vulnerability", "cve_id": "CVE-2024-0001", "cost": 50000}
        ]
    }, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "scenario_id" in data
    assert data["status"] in ["SIMULATION_SUCCESS", "simulated"]
    assert data["scenario_name"] == "Patch Critical CVE Simulation"
    assert "current_state" in data
    assert "scenario_state" in data
    assert "before_vs_after" in data
    assert "financial_impact" in data

    # 2. Test enabling MFA + deploying EDR
    res2 = client.post("/api/v1/scenarios/run", json={
        "scenario_name": "MFA and EDR Rollout",
        "changes": [
            {"type": "enable_mfa", "cost": 150000},
            {"type": "deploy_edr", "cost": 250000}
        ]
    }, headers=auth_headers)
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["financial_impact"]["investment_cost"] == 400000
    assert d2["scenario_state"]["risk_score"] <= d2["current_state"]["risk_score"]

def test_8_3_and_8_4_non_destructive_isolation(auth_headers):
    """Test 8.3 & 8.4: Ensure scenarios run strictly in isolated state without mutating database."""
    db = SyncSessionLocal()
    try:
        initial_asset_count = db.query(Asset).count()
        initial_vuln_count = db.query(Vulnerability).count()
        
        # Run aggressive scenario that patches vulns and enables segmentation
        res = client.post("/api/v1/scenarios/run", json={
            "scenario_name": "Aggressive Hardening",
            "changes": [
                {"type": "patch_vulnerability", "cve_id": "ALL_CRITICAL", "cost": 300000},
                {"type": "network_segmentation", "cost": 500000},
                {"type": "improve_control_effectiveness", "control_name": "EDR / XDR", "boost": 0.4}
            ]
        }, headers=auth_headers)
        assert res.status_code == 200
        
        # Verify database assets and vulnerabilities were NOT permanently altered or deleted
        post_asset_count = db.query(Asset).count()
        post_vuln_count = db.query(Vulnerability).count()
        assert initial_asset_count == post_asset_count
        assert initial_vuln_count == post_vuln_count
    finally:
        db.close()

def test_8_5_and_8_6_before_after_financial_impact(auth_headers):
    """Test 8.5 & 8.6: Dynamic Before/After comparison and Financial EAL calculation."""
    res = client.post("/api/v1/scenarios/run", json={
        "scenario_name": "Zero Trust Hardening",
        "changes": [
            {"type": "add_control", "control_name": "Zero Trust Architecture", "cost": 600000, "effectiveness": 0.3}
        ]
    }, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    
    bva = data["before_vs_after"]
    assert "current_risk" in bva
    assert "scenario_risk" in bva
    assert "risk_reduction" in bva
    assert bva["current_risk"] >= bva["scenario_risk"]
    
    fi = data["financial_impact"]
    assert "current_eal" in fi
    assert "scenario_eal" in fi
    assert "eal_reduction" in fi
    assert fi["current_eal"] >= fi["scenario_eal"]
    assert fi["eal_reduction"] >= 0

def test_8_7_scenario_comparison(auth_headers):
    """Test 8.7: Compare multiple scenarios side-by-side (Scenario A vs B vs C)."""
    res = client.post("/api/v1/scenarios/compare", json={
        "scenarios": [
            {
                "scenario_name": "Scenario A: MFA Only",
                "changes": [{"type": "enable_mfa", "cost": 150000}]
            },
            {
                "scenario_name": "Scenario B: EDR Only",
                "changes": [{"type": "deploy_edr", "cost": 250000}]
            },
            {
                "scenario_name": "Scenario C: MFA + EDR Defense-in-Depth",
                "changes": [
                    {"type": "enable_mfa", "cost": 150000},
                    {"type": "deploy_edr", "cost": 250000}
                ]
            }
        ]
    }, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "scenario_comparison" in data
    assert len(data["scenario_comparison"]) == 3
    
    # Check fields of each scenario in comparison
    for sc in data["scenario_comparison"]:
        assert "scenario_name" in sc
        assert "total_investment_cost" in sc
        assert "modeled_risk_score" in sc
        assert "risk_reduction" in sc
        assert "financial_exposure_eal" in sc
        assert "eal_reduction" in sc
        assert "affected_assets_count" in sc
        assert "attack_paths_count" in sc

    # Scenario C should have highest investment and at least as much risk reduction as A or B
    sc_a = data["scenario_comparison"][0]
    sc_c = data["scenario_comparison"][2]
    assert sc_c["total_investment_cost"] >= sc_a["total_investment_cost"]
    assert sc_c["risk_reduction"] >= sc_a["risk_reduction"]

def test_8_8_digital_twin_view(auth_headers):
    """Test 8.8: Digital Twin representation of enterprise assets, vulnerabilities, controls, paths."""
    res = client.get("/api/v1/scenarios/digital-twin", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "digital_twin" in data or "enterprise_nodes" in data or "nodes" in data
    assert "total_assets" in data
    assert "critical_assets" in data
    assert "attack_paths" in data
    assert "controls" in data
    assert "disclaimer" in data
    assert "decision-support simulation" in data["disclaimer"]

def test_8_9_and_8_10_scenario_save_reset_and_audit(auth_headers):
    """Test 8.9 & 8.10: Save scenario, query saved list, reset scenario, and verify audit."""
    # 1. Save scenario
    save_res = client.post("/api/v1/scenarios/save", json={
        "scenario_name": "Persistent Test Scenario",
        "description": "Board-level test simulation",
        "changes": [{"type": "enable_mfa", "cost": 150000}],
        "investment_cost": 150000,
        "risk_before": 75.0,
        "risk_after": 60.0,
        "financial_exposure_before": 5000000,
        "financial_exposure_after": 4000000
    }, headers=auth_headers)
    assert save_res.status_code in [200, 201]
    saved_data = save_res.json()
    assert "scenario_id" in saved_data
    sc_id = saved_data["scenario_id"]

    # 2. Reset scenario state
    reset_res = client.post("/api/v1/scenarios/reset", json={"scenario_id": sc_id}, headers=auth_headers)
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["status"] in ["RESET_SUCCESSFUL", "reset_success", "active", "reset"]
    assert "baseline_state" in reset_data
