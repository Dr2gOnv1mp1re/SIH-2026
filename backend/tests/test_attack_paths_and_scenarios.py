import pytest
from fastapi.testclient import TestClient
from app.main import app

def get_auth_header(client):
    res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_attack_path_graph_analysis():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        res = client.get("/api/v1/attack-paths", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "critical_attack_paths" in data
        assert len(data["critical_attack_paths"]) >= 1
        
        path = data["critical_attack_paths"][0]
        assert "start_point" in path
        assert "target_asset" in path
        assert path["path_length"] >= 3
        assert path["path_risk_score"] > 70.0
        assert path["modeled_financial_impact"] > 0
        assert "nodes" in data
        assert "edges" in data

def test_what_if_scenario_simulation():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        payload = {
            "name": "Zero-Day Exploit on Payment Gateway",
            "log4j_exploited": True,
            "mfa_coverage_delta": -20.0
        }
        res = client.post("/api/v1/scenarios/simulate", json=payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "simulated_modeled_risk" in data
        assert "baseline_modeled_risk" in data
        assert data["simulated_modeled_risk"] > 0
