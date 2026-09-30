"""
Phase 3 Continuous Cyber Risk Engine Comprehensive Test Suite.
Validates:
- Central RiskEngine service logic and reproducible formulas
- Score normalization (0-100) and risk levels (Low, Moderate, Medium, High, Critical)
- Multipliers: Criticality, CVSS, Exploit Availability, Internet Exposure, Controls
- Human-readable explainability ("Why is this asset high risk?")
- Vulnerability-level risk and affected asset connectivity
- Enterprise risk aggregation (quadratic crown jewel weighting)
- Top Risk Drivers & Prioritization (/api/v1/risk/drivers)
- Risk History Snapshots & Change Tracking (/api/v1/risk/history)
- Dynamic Recalculation API (/api/v1/risk/recalculate)
- Dataset switching dynamically updating risk endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.risk_engine.engine import risk_engine, get_risk_level
from app.risk_engine.universal_importer import universal_csv_engine

client = TestClient(app)

def test_risk_level_thresholds():
    """Verify standard enterprise risk score normalization and thresholds.
    Scale: 0-19: LOW, 20-59: MEDIUM, 60-79: HIGH, 80-100: CRITICAL
    """
    assert get_risk_level(95.0) == "CRITICAL"
    assert get_risk_level(80.0) == "CRITICAL"
    assert get_risk_level(75.0) == "HIGH"
    assert get_risk_level(60.0) == "HIGH"
    assert get_risk_level(50.0) == "MEDIUM"
    assert get_risk_level(40.0) == "MEDIUM"
    assert get_risk_level(30.0) == "MEDIUM"
    assert get_risk_level(20.0) == "MEDIUM"
    assert get_risk_level(15.0) == "LOW"
    assert get_risk_level(0.0) == "LOW"

def test_asset_risk_calculation_and_explainability():
    """Verify asset risk scoring, contributing factors breakdown, and human-readable explanation."""
    high_risk_asset = {
        "asset_id": "AST-CROWN-01",
        "asset_name": "Core Banking Transaction DB",
        "asset_criticality_1_5": 5.0,
        "internet_exposed": True,
        "control_effectiveness": 0.30, # Weak controls
        "associated_vulnerabilities": [
            {
                "cve_id": "CVE-2024-21762",
                "cvss_score": 9.8,
                "exploit_available": True,
                "patch_available": False,
                "vulnerability_age_days": 45
            }
        ],
        "siem_severity": "Critical",
        "edr_severity": "Critical",
        "edr_isolated": False,
        "privileged_account": True,
        "mfa_enabled": False
    }

    assessment = risk_engine.calculate_asset_risk(high_risk_asset)
    assert assessment["risk_score"] >= 80.0
    assert assessment["risk_level"] == "CRITICAL"
    assert assessment["contributing_factors"]["exposure_multiplier"] == 1.35
    assert assessment["contributing_factors"]["control_weakness_factor"] > 0.80

    reasons = assessment["why_high_risk"]
    assert any("Crown Jewel" in r for r in reasons)
    assert any("Public Internet" in r for r in reasons)
    assert any("CVE-2024-21762" in r for r in reasons)
    assert any("Active Exploit" in r for r in reasons)
    assert any("No Official Patch" in r for r in reasons)
    assert any("Multi-Factor Authentication" in r for r in reasons)

def test_vulnerability_risk_and_asset_connectivity():
    """Verify vulnerability-level risk evaluation considers both CVSS and affected asset criticality."""
    vuln = {
        "cve_id": "CVE-2021-44228",
        "title": "Log4Shell Remote Code Execution",
        "cvss_score": 10.0,
        "exploit_available": True,
        "patch_available": True,
        "vulnerability_age_days": 120,
        "affected_assets": [
            {"asset_id": "AST-001", "asset_name": "Payment Gateway", "criticality": 5.0, "internet_exposed": True}
        ]
    }
    v_eval = risk_engine.calculate_vulnerability_risk(vuln)
    assert v_eval["risk_score"] >= 80.0
    assert v_eval["risk_level"] == "CRITICAL"
    assert v_eval["affected_assets_count"] == 1
    assert "Critical CVSS Base Score (>= 9.0)" in v_eval["risk_factors"]
    assert "Weaponized Exploit Available in Public/Wild" in v_eval["risk_factors"]

def test_enterprise_risk_aggregation():
    """Verify quadratic crown-jewel weighting aggregates underlying assets into enterprise score."""
    assets = [
        {"risk_score": 90.0, "criticality_score": 95.0, "risk_level": "CRITICAL", "expected_annual_loss": 5000000.0},
        {"risk_score": 30.0, "criticality_score": 40.0, "risk_level": "MODERATE", "expected_annual_loss": 500000.0}
    ]
    agg = risk_engine.aggregate_enterprise_risk(assets)
    # The 95-criticality asset with risk 90 has weight (9.5)^2 = 90.25 vs 40-crit weight (4.0)^2 = 16.0
    # Aggregated score should be heavily dominated by the critical asset (> 75)
    assert agg["enterprise_risk_score"] > 75.0
    assert agg["critical_assets"] == 1
    assert agg["total_expected_annual_loss"] == 5500000.0

def test_risk_api_endpoints_and_history_snapshots():
    """Verify /api/v1/risk/ enterprise, assets, vulnerabilities, drivers, and history endpoints."""
    # 1. Login as CISO
    login_res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get enterprise risk
    ent_res = client.get("/api/v1/risk/enterprise", headers=headers)
    assert ent_res.status_code == 200
    ent_data = ent_res.json()
    assert "enterprise_risk_score" in ent_data
    assert "risk_distribution" in ent_data
    assert "data_source" in ent_data

    # 3. Get asset-level risk
    assets_res = client.get("/api/v1/risk/assets", headers=headers)
    assert assets_res.status_code == 200
    assets_data = assets_res.json()
    assert len(assets_data) > 0
    first_asset = assets_data[0]
    assert "why_high_risk" in first_asset
    assert "contributing_factors" in first_asset

    # 4. Get vulnerability-level risk
    vulns_res = client.get("/api/v1/risk/vulnerabilities", headers=headers)
    assert vulns_res.status_code == 200
    assert len(vulns_res.json()) > 0

    # 5. Get top risk drivers
    drivers_res = client.get("/api/v1/risk/drivers", headers=headers)
    assert drivers_res.status_code == 200
    drivers_data = drivers_res.json()
    assert "top_risk_drivers" in drivers_data
    assert "top_risky_assets" in drivers_data

    # 6. Recalculate risk & create history snapshot
    recalc_res = client.post("/api/v1/risk/recalculate", headers=headers)
    assert recalc_res.status_code == 200
    assert recalc_res.json()["status"] == "SUCCESS"
    assert "snapshot" in recalc_res.json()

    # 7. Check history timeline
    hist_res = client.get("/api/v1/risk/history", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert "risk_change" in history[-1]
    assert "change_label" in history[-1]

def test_dynamic_risk_change_on_dataset_switch():
    """Verify that switching active dataset causes /api/v1/risk/enterprise scores to dynamically update."""
    login_res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload low-risk dataset
    low_risk_csv = (
        "asset_id,asset_name,criticality,internet_exposed,control_effectiveness\n"
        "LOW-01,Internal Test Node,1,false,0.95\n"
        "LOW-02,Dev Logging Server,1,false,0.90\n"
    )
    upload_res = client.post(
        "/api/v1/universal-import/execute",
        data={"csv_content": low_risk_csv, "filename": "low_risk_test.csv"}
    )
    assert upload_res.status_code == 200

    # Query enterprise risk — should reflect the low-risk dataset!
    low_ent_res = client.get("/api/v1/risk/enterprise", headers=headers)
    assert low_ent_res.status_code == 200
    low_score = low_ent_res.json()["enterprise_risk_score"]
    assert low_score < 40.0 # Low or Moderate risk

    # Switch back to SIH Dataset
    client.post("/api/v1/datasets/sih_ps26105/activate")
    sih_ent_res = client.get("/api/v1/risk/enterprise", headers=headers)
    assert sih_ent_res.status_code == 200
    sih_score = sih_ent_res.json()["enterprise_risk_score"]
    assert sih_score > low_score
