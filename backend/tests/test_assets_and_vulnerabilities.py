import pytest
from fastapi.testclient import TestClient
from app.main import app

def get_auth_header(client):
    res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_asset_inventory_and_criticality():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        res = client.get("/api/v1/assets", headers=headers)
        assert res.status_code == 200
        assets = res.json()
        assert len(assets) >= 100

        # Check crown jewel payment database
        crown_jewels = [a for a in assets if a["criticality_score"] >= 90.0]
        assert len(crown_jewels) > 0
        payment_db = next((a for a in crown_jewels if "Payment" in a["name"] or a["code"] == "DB-PAY-01"), None)
        assert payment_db is not None
        assert payment_db["asset_type"].lower() == "database"

def test_vulnerability_ingestion_and_cisa_kev():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        res = client.get("/api/v1/vulnerabilities", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "stats" in data
        assert data["stats"]["total"] == 500
        assert data["stats"]["critical"] == 50
        assert data["stats"]["cisa_known_exploited"] >= 6

        # Check filtering by active exploitation
        cisa_res = client.get("/api/v1/vulnerabilities?active_exploit_only=true", headers=headers)
        assert cisa_res.status_code == 200
        cisa_data = cisa_res.json()
        for v in cisa_data["items"]:
            assert v["active_exploitation"] is True
