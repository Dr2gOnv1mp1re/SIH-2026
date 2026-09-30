import pytest
import io
import csv
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_sync_db, sync_engine, Base
from app.database.models import SecurityIncident, Organization, User, Asset
from app.core.security import create_access_token

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=sync_engine)
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def auth_headers(client):
    db = next(get_sync_db())
    org = db.query(Organization).filter(Organization.name == "ABC Bank").first()
    user = db.query(User).filter(User.email == "ciso@abcbank.com").first()
    token = create_access_token(subject=user.id, role=user.role, org_id=org.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def analyst_headers(client):
    db = next(get_sync_db())
    org = db.query(Organization).filter(Organization.name == "ABC Bank").first()
    user = db.query(User).filter(User.email == "analyst@abcbank.com").first()
    token = create_access_token(subject=user.id, role=user.role, org_id=org.id)
    return {"Authorization": f"Bearer {token}"}

def test_incident_creation_and_auto_loss_calculation(client, auth_headers):
    """
    Requirements 2, 3, 4:
    Total Observed Loss must be automatically computed server-side as the exact sum of
    revenue_loss + recovery_cost + response_cost + regulatory_cost + other_loss.
    Client cannot manually override this total.
    """
    payload = {
        "incident_id": "TEST-INC-2026-099",
        "incident_type": "Ransomware",
        "incident_date": "2026-09-20T10:00:00",
        "asset_criticality": "Critical",
        "attack_vector": "Phishing Spear-Phish",
        "downtime_hours": 3.0,
        "revenue_loss": 300000.0,
        "recovery_cost": 200000.0,
        "response_cost": 150000.0,
        "regulatory_cost": 100000.0,
        "other_loss": 50000.0,
        "incident_status": "RESOLVED",
        "notes": "Automated integration test record."
    }
    expected_total = 300000.0 + 200000.0 + 150000.0 + 100000.0 + 50000.0  # 800,000.0

    res = client.post("/incidents", json=payload, headers=auth_headers)
    assert res.status_code == 201, res.text
    data = res.json()["incident"]
    assert data["incident_id"] == "TEST-INC-2026-099"
    assert data["total_observed_loss"] == expected_total
    assert data["data_source_classification"] == "ACTUAL OBSERVED LOSS"
    assert data["canonical_hash"] is not None

def test_negative_financial_values_rejected(client, auth_headers):
    """Requirement 2 & 4: Prevent negative financial values."""
    payload = {
        "incident_id": "TEST-INC-NEG-001",
        "incident_type": "DDoS",
        "revenue_loss": -50000.0,
        "recovery_cost": 10000.0
    }
    res = client.post("/incidents", json=payload, headers=auth_headers)
    assert res.status_code == 422, "Negative financial loss must be rejected with 422"

def test_duplicate_incident_id_rejected(client, auth_headers):
    """Requirement 4 & 6: Reject duplicate incident ID."""
    payload = {
        "incident_id": "INC-2024-001",  # Already seeded
        "incident_type": "Phishing",
        "revenue_loss": 10000.0
    }
    res = client.post("/incidents", json=payload, headers=auth_headers)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"].lower()

def test_incident_statistics_endpoint(client, auth_headers):
    """
    Requirement 5: Statistics must clearly label values as HISTORICAL OBSERVED DATA
    and compute valid count, sum, average, and frequency.
    """
    res = client.get("/incidents/statistics", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["data_source_classification"] == "HISTORICAL OBSERVED DATA"
    assert data["data_source_badge"] == "ACTUAL"
    assert data["total_incidents"] >= 5
    assert data["total_observed_loss"] >= 4600000.0
    assert data["average_observed_loss"] > 0
    assert data["total_downtime_hours"] >= 4.0

def test_four_way_financial_separation(client, auth_headers):
    """
    Requirements 8, 9, 15:
    Strictly enforce 4-way separation of financial metrics:
    1. ACTUAL OBSERVED LOSS
    2. MODELED FINANCIAL EXPOSURE (FAIR SLE * ARO)
    3. PREDICTED FUTURE EXPOSURE
    4. SIMULATED/DEMO BENCHMARK
    Never mix them or present simulated values as actual losses.
    """
    res = client.get("/api/v1/financial/overview", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    # 1. Actual
    assert "actual_observed_loss" in data
    assert data["actual_observed_loss"]["badge"] == "ACTUAL"
    assert data["actual_observed_loss"]["classification"] == "ACTUAL OBSERVED LOSS"
    assert data["actual_observed_loss"]["amount"] > 0

    # 2. Modeled
    assert "modeled_financial_exposure" in data
    assert data["modeled_financial_exposure"]["badge"] == "MODELED"
    assert data["modeled_financial_exposure"]["classification"] == "MODELED FINANCIAL EXPOSURE"

    # 3. Predicted
    assert "predicted_future_exposure" in data
    assert data["predicted_future_exposure"]["badge"] == "PREDICTED"

    # 4. Simulated
    assert "simulated_benchmark" in data
    assert data["simulated_benchmark"]["badge"] == "SIMULATED"

    # Verify mathematical consistency of FAIR scenarios: SLE * ARO = EAL
    for scenario in data["scenarios_breakdown"]:
        calc_eal = round(scenario["single_loss_expectancy"] * scenario["annualized_rate_of_occurrence"], 2)
        assert abs(scenario["expected_annual_loss"] - calc_eal) < 1.0, \
            f"Scenario {scenario['name']} mathematical inconsistency: {scenario['expected_annual_loss']} != {calc_eal}"

def test_data_quality_endpoint(client, auth_headers):
    """Requirement 7: Data Quality section returning GOOD / WARNING / INSUFFICIENT."""
    res = client.get("/incidents/data-quality", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["overall_status"] in ("GOOD", "WARNING", "INSUFFICIENT")
    assert len(data["checks"]) >= 4
    assert data["score_percentage"] >= 0

def test_model_calibration_endpoint(client, auth_headers, analyst_headers):
    """
    Requirements 11 & 14:
    Model calibration uses empirical evidence and requires CISO / ADMIN authorization.
    """
    # 1. GET calibration status
    res = client.get("/incidents/calibration", headers=auth_headers)
    assert res.status_code == 200
    status_data = res.json()
    assert "data_sufficiency" in status_data
    assert "parameters_comparison" in status_data

    # 2. Security Analyst cannot calibrate (Role restriction)
    res_unauth = client.post("/incidents/calibrate", json={"apply_to_eal": True}, headers=analyst_headers)
    assert res_unauth.status_code == 403, "Analyst should not have permission to approve calibration"

    # 3. CISO can calibrate and record on blockchain
    res_ciso = client.post("/incidents/calibrate", json={"apply_to_eal": True}, headers=auth_headers)
    assert res_ciso.status_code == 200
    calib_data = res_ciso.json()
    assert calib_data["status"] == "SUCCESS"
    assert calib_data["canonical_hash"] is not None

def test_blockchain_verification_of_incident(client, auth_headers):
    """
    Requirement 13:
    Verify that an audited incident record on the blockchain audit ledger
    correctly validates with SHA-256 proof.
    """
    res = client.post("/api/v1/blockchain/verify/INC-2024-001", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["verification_status"] == "VERIFIED"
    assert data["on_chain_hash"] is not None

def test_delete_incident_and_cleanup(client, auth_headers, analyst_headers):
    """Requirements 4 & 14: Incident deletion requires ADMIN or CISO role."""
    # Analyst attempt -> 403
    res_del_unauth = client.delete("/incidents/TEST-INC-2026-099", headers=analyst_headers)
    assert res_del_unauth.status_code == 403

    # CISO attempt -> 200
    res_del = client.delete("/incidents/TEST-INC-2026-099", headers=auth_headers)
    assert res_del.status_code == 200
    assert "deleted" in res_del.json()["message"].lower()
