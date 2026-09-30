import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["HEALTHY", "ok"]
        assert "components" in data

def test_auth_and_login():
    with TestClient(app) as client:
        # Login as CISO
        response = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "Ciso@12345"
        })
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["user"]["role"] == "CISO"
        
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test get me
        me_res = client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "ciso@abcbank.com"

        # Test get enterprise risk
        risk_res = client.get("/api/v1/risk/enterprise", headers=headers)
        assert risk_res.status_code == 200
        assert "enterprise_risk_score" in risk_res.json()
        assert "expected_annual_loss" in risk_res.json()

        # Test run optimization
        opt_res = client.post("/api/v1/optimization/run", json={"budget": 10000000.0}, headers=headers)
        assert opt_res.status_code == 200
        opt_data = opt_res.json()
        assert opt_data["optimization_result"]["total_investment"] <= 10000000.0
        assert opt_data["optimization_result"]["modeled_risk_reduction"] > 0

        # Test AI prediction
        ai_res = client.get("/api/v1/ai/predictions", headers=headers)
        assert ai_res.status_code == 200
        assert "predicted_30d_risk_score" in ai_res.json()
        assert "shap_explanation" in ai_res.json()

        # Test Blockchain blocks
        bc_res = client.get("/api/v1/blockchain/blocks", headers=headers)
        assert bc_res.status_code == 200
        assert bc_res.json()["total_blocks"] >= 1
