import pytest
from fastapi.testclient import TestClient
from app.main import app

def get_auth_header(client):
    res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_get_csv_template():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        response = client.get("/api/v1/assets/template-csv", headers=headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        content = response.text
        assert "name,asset_type,ip_address,hostname" in content
        assert "Core Payment Gateway" in content

def test_export_assets_csv():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        response = client.get("/api/v1/assets/export-csv", headers=headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        content = response.text
        assert "id,name,asset_type,ip_address" in content
        lines = [line for line in content.strip().split("\n") if line]
        assert len(lines) >= 2  # Header + at least one asset

def test_import_assets_csv():
    with TestClient(app) as client:
        headers = get_auth_header(client)
        csv_payload = (
            "name,asset_type,ip_address,hostname,owner,department,operating_system,"
            "business_importance,data_sensitivity,revenue_dependency,downtime_tolerance_hours,"
            "regulatory_importance,internet_exposed\n"
            "Branch Gateway Router 01,network,10.200.1.1,router01.bank.in,NetOps,Infrastructure,Cisco IOS-XE,80,75,70,1.0,80,false\n"
            "HR Employee Portal,application,10.200.2.15,hr.corp.bank.in,IT-HR,Human Resources,Linux RHEL 8,65,70,60,4.0,75,false\n"
        )
        response = client.post(
            "/api/v1/assets/import-csv",
            headers=headers,
            json={"csv_content": csv_payload}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["imported_count"] == 2
        assert len(data["imported_names"]) == 2
        assert data["data_origin"] == "ORGANIZATION-PROVIDED DATA"
        assert "Branch Gateway Router 01" in data["imported_names"]

        # Teardown: Clean up imported test records to preserve canonical 100 assets
        from app.database.session import SyncSessionLocal
        from app.database.models import Asset
        with SyncSessionLocal() as db:
            db.query(Asset).filter(Asset.name.in_(["Branch Gateway Router 01", "HR Employee Portal"])).delete(synchronize_session=False)
            db.commit()
