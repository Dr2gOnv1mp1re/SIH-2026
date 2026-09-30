import pytest
from app.risk_engine.calculator import calculate_asset_criticality, calculate_risk_score, get_risk_level

def test_asset_criticality_calculation():
    # Payment Database (High business importance, high data sensitivity, low downtime tolerance)
    crit_db = calculate_asset_criticality(
        business_importance=98.0,
        data_sensitivity=95.0,
        revenue_dependency=95.0,
        regulatory_importance=98.0,
        internet_exposed=False,
        downtime_tolerance_hours=0.2
    )
    assert crit_db >= 90.0, f"Expected Payment DB criticality >= 90, got {crit_db}"

    # Employee Workstation
    crit_endpoint = calculate_asset_criticality(
        business_importance=45.0,
        data_sensitivity=45.0,
        revenue_dependency=30.0,
        regulatory_importance=40.0,
        internet_exposed=False,
        downtime_tolerance_hours=8.0
    )
    assert crit_endpoint < 60.0, f"Expected Endpoint criticality < 60, got {crit_endpoint}"

def test_risk_score_reproducibility():
    score_1 = calculate_risk_score(
        threat_likelihood=85.0,
        vulnerability_severity=95.0,
        asset_criticality=95.0,
        control_effectiveness=70.0,
        has_active_exploit=True,
        is_internet_exposed=True
    )
    score_2 = calculate_risk_score(
        threat_likelihood=85.0,
        vulnerability_severity=95.0,
        asset_criticality=95.0,
        control_effectiveness=70.0,
        has_active_exploit=True,
        is_internet_exposed=True
    )
    assert score_1["risk_score"] == score_2["risk_score"], "Risk scoring must be strictly deterministic"
    assert score_1["risk_level"] in ("HIGH", "VERY HIGH", "CRITICAL")
    assert "contributors" in score_1
    assert "active_exploitation_pct" in score_1["contributors"]
