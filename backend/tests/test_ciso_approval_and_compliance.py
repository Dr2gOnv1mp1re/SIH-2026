import pytest
from fastapi.testclient import TestClient
from app.main import app

def get_ciso_header(client):
    res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_ciso_approval_workflow():
    with TestClient(app) as client:
        headers = get_ciso_header(client)
        # 1. Get decision context
        ctx_res = client.get("/api/v1/ciso/decision", headers=headers)
        assert ctx_res.status_code == 200
        ctx_data = ctx_res.json()
        assert "current_modeled_risk_score" in ctx_data or "current_modeled_risk" in ctx_data
        assert "recommended_portfolio" in ctx_data
        assert "budget_utilization" in ctx_data

        # 2. Approve plan
        approve_res = client.post("/api/v1/ciso/approve", json={
            "decision_notes": "Authorized by CISO for immediate execution."
        }, headers=headers)
        assert approve_res.status_code == 200
        app_data = approve_res.json()
        assert app_data["status"] == "APPROVED"
        assert "blockchain_transaction_id" in app_data
        assert "canonical_sha256_hash" in app_data

def test_compliance_matrix_gaps():
    with TestClient(app) as client:
        headers = get_ciso_header(client)
        res = client.get("/api/v1/compliance", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "frameworks_summary" in data
        assert len(data["frameworks_summary"]) >= 3
        # Check Indian banking frameworks included
        framework_names = [f["name"] for f in data["frameworks_summary"]]
        assert any("RBI" in name or "SEBI" in name or "NIST" in name or "ISO" in name for name in framework_names)

def test_executive_and_board_reports():
    with TestClient(app) as client:
        headers = get_ciso_header(client)
        res = client.post("/api/v1/reports/generate", json={"report_type": "BOARD_SUMMARY"}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "title" in data
        assert "key_metrics" in data
        assert "executive_summary" in data
        assert "governance_status" in data
