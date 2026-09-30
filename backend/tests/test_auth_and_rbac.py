import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_authentication_and_token_issuance():
    with TestClient(app) as client:
        # Valid login
        res = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "Ciso@12345"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "ciso@abcbank.com"
        assert data["user"]["role"] == "CISO"

        # Invalid password
        bad_res = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "InvalidPassword"
        })
        assert bad_res.status_code == 401

        # Non-existent user
        missing_res = client.post("/api/v1/auth/login", json={
            "email": "unknown@abcbank.com",
            "password": "Password@123"
        })
        assert missing_res.status_code == 401

def test_rbac_all_six_enterprise_roles():
    role_credentials = [
        ("CISO", "ciso@abcbank.com", "Ciso@12345"),
        ("SECURITY_ANALYST", "analyst@abcbank.com", "Analyst@12345"),
        ("RISK_ANALYST", "risk@abcbank.com", "Risk@12345"),
        ("EXECUTIVE", "executive@abcbank.com", "Executive@12345"),
        ("AUDITOR", "auditor@abcbank.com", "Auditor@12345"),
        ("ADMIN", "admin@abcbank.com", "Admin@12345")
    ]
    with TestClient(app) as client:
        tokens = {}
        for role, email, password in role_credentials:
            res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
            assert res.status_code == 200, f"Login failed for role {role}"
            tokens[role] = res.json()["access_token"]
            assert res.json()["user"]["role"] == role

        # CISO has access to CISO decision endpoint
        ciso_res = client.get("/api/v1/ciso/decision", headers={"Authorization": f"Bearer {tokens['CISO']}"})
        assert ciso_res.status_code == 200

        # Auditor can view blockchain ledger
        auditor_res = client.get("/api/v1/blockchain/blocks", headers={"Authorization": f"Bearer {tokens['AUDITOR']}"})
        assert auditor_res.status_code == 200
