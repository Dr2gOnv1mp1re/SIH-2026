import pytest
from fastapi.testclient import TestClient
from app.main import app

def get_auth_header(client):
    res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_prediction_output_and_bounds():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        # Test GET /api/v1/prediction/latest
        res = client.get("/api/v1/prediction/latest", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "predicted_30d_risk_score" in data
        assert 0.0 <= data["predicted_30d_risk_score"] <= 100.0
        assert data["predicted_30d_eal"] > 0
        assert data["predicted_60d_eal"] >= data["predicted_30d_eal"]
        assert data["predicted_90d_eal"] >= data["predicted_60d_eal"]

def test_shap_explanation_features():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        # Test GET /api/v1/prediction/shap
        res = client.get("/api/v1/prediction/shap", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "shap_factors" in data or "shap_attributions" in data
        factors = data.get("shap_factors") or data.get("shap_attributions")
        assert len(factors) >= 3
        for f in factors:
            assert "feature" in f
            assert "direction" in f
            assert f["direction"] in ["INCREASING_RISK", "DECREASING_RISK"]
            assert "impact_value" in f
