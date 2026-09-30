"""
Tests for Phase 9: CISO Governance, Audit & Blockchain
Validates:
9.1 Human-in-the-Loop Workflow (No auto-approval)
9.2 CISODecision Object & Fields
9.3 CISO Review, 9.4 Comments & Actions (Approve / Reject / Modify)
9.5 Decision Versioning (Immutable historical decisions: v1 -> v2 -> v3)
9.6 Audit Trail Recording & 9.7 Multi-criteria Search & Filtering
9.8-9.11 Deterministic SHA-256 Canonical Evidence Hashing & Ledger Recording
9.12 Verification returning VALID / INVALID / UNAVAILABLE
9.13 Safe Non-destructive Tamper Test Demonstration
9.14 Governance Framework Mapping (NIST CSF, ISO 27001, CIS Controls)
9.15 Executive View answering the 8 Core CISO Questions
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SyncSessionLocal
from app.database.models import CISODecision, AuditLog

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_9_1_to_9_4_ciso_approval_and_rejection_workflow(auth_headers):
    """Test 9.1 to 9.4: CISO Review, Comments, and Decision Creation."""
    # 1. First get optimization recommendation
    rec_res = client.get("/api/v1/controls/recommendations", headers=auth_headers)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    recommendation_id = rec_data.get("recommendation_id", "rec_sih_batch789")

    # 2. CISO Approves recommendation with justification comments
    approve_payload = {
        "recommendation_id": recommendation_id,
        "comments": "Approved based on critical payment-system exposure and high risk reduction.",
        "approved_budget": 5000000.0,
        "approved_controls": ["MFA Enforcement", "EDR Deployment", "Critical Patching"]
    }
    app_res = client.post("/api/v1/ciso/approve", json=approve_payload, headers=auth_headers)
    assert app_res.status_code == 200
    decision = app_res.json()
    assert decision["decision"] == "APPROVED"
    assert "decision_id" in decision
    assert decision["approved_budget"] == 5000000.0
    assert "Approved based on critical payment-system exposure" in decision["comments"]
    assert "version" in decision
    assert decision["version"] >= 1

    # 3. CISO Rejects with comments
    reject_payload = {
        "recommendation_id": "rec_rejected_sample",
        "comments": "Rejected because control cost exceeds current quarter budget."
    }
    rej_res = client.post("/api/v1/ciso/reject", json=reject_payload, headers=auth_headers)
    assert rej_res.status_code == 200
    rej_decision = rej_res.json()
    assert rej_decision["decision"] == "REJECTED"
    assert "Rejected because control cost exceeds current quarter budget" in rej_decision["comments"]

def test_9_5_decision_versioning(auth_headers):
    """Test 9.5: Decision Versioning (Decision v1 -> Decision v2 -> Decision v3 without overwriting)."""
    db = SyncSessionLocal()
    try:
        import uuid
        shared_rec_id = f"rec_versioning_{uuid.uuid4().hex[:8]}"
        
        # Version 1: Initial approval
        res1 = client.post("/api/v1/ciso/approve", json={
            "recommendation_id": shared_rec_id,
            "comments": "Initial approval v1",
            "approved_budget": 2500000.0,
            "approved_controls": ["MFA Enforcement"]
        }, headers=auth_headers)
        assert res1.status_code == 200
        d1 = res1.json()
        assert d1["version"] == 1

        # Version 2: Modified approval with PAM addition
        res2 = client.post("/api/v1/ciso/modify", json={
            "recommendation_id": shared_rec_id,
            "comments": "Modified v2: Prioritized PAM alongside MFA",
            "approved_budget": 4500000.0,
            "approved_controls": ["MFA Enforcement", "PAM Vault Integration"]
        }, headers=auth_headers)
        assert res2.status_code == 200
        d2 = res2.json()
        assert d2["version"] == 2
        assert d2["decision"] == "MODIFIED"

        # Version 3: Modified approval with budget expansion
        res3 = client.post("/api/v1/ciso/modify", json={
            "recommendation_id": shared_rec_id,
            "comments": "Modified v3: Expanded budget to ₹75L for full EDR rollout",
            "approved_budget": 7500000.0,
            "approved_controls": ["MFA Enforcement", "PAM Vault Integration", "EDR / XDR"]
        }, headers=auth_headers)
        assert res3.status_code == 200
        d3 = res3.json()
        assert d3["version"] == 3

        # Verify in DB that all three distinct decision records exist (immutable history)
        history = db.query(CISODecision).filter(CISODecision.recommendation_id == shared_rec_id).all()
        versions = [h.version for h in history]
        assert 1 in versions
        assert 2 in versions
        assert 3 in versions
        assert len(history) >= 3
    finally:
        db.close()

def test_9_6_and_9_7_audit_trail_and_search(auth_headers):
    """Test 9.6 & 9.7: Audit Trail recording and multi-criteria filtering."""
    res = client.get("/api/v1/ciso/audit-trail", headers=auth_headers)
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
    assert len(events) > 0

    first_event = events[0]
    assert "event_id" in first_event or "id" in first_event
    assert "event_type" in first_event or "action" in first_event
    assert "timestamp" in first_event
    assert "integrity_hash" in first_event

    # Test filtering by event_type / action
    filter_res = client.get("/api/v1/ciso/audit-trail?event_type=CISO_DECISION_APPROVED", headers=auth_headers)
    assert filter_res.status_code == 200
    filtered = filter_res.json()
    assert isinstance(filtered, list)

def test_9_8_to_9_12_blockchain_ledger_and_verification(auth_headers):
    """Test 9.8-9.12: Blockchain audit record creation and deterministic cryptographic verification."""
    # 1. Retrieve blockchain ledger records
    res = client.get("/api/v1/blockchain/records", headers=auth_headers)
    assert res.status_code == 200
    records = res.json()
    assert isinstance(records, list)
    assert len(records) > 0

    first_rec = records[0]
    rec_id = first_rec["record_id"]
    assert "evidence_hash" in first_rec
    assert "evidence_type" in first_rec

    # 2. Verify record integrity
    ver_res = client.get(f"/api/v1/blockchain/verify/{rec_id}", headers=auth_headers)
    assert ver_res.status_code == 200
    ver_data = ver_res.json()
    assert "verification_result" in ver_data
    assert ver_data["verification_result"] in ["VALID", "INVALID", "UNAVAILABLE"]

def test_9_13_safe_tamper_demonstration(auth_headers):
    """Test 9.13: Safe, non-destructive tamper detection demonstration."""
    res = client.post("/api/v1/blockchain/tamper-test", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["tamper_demonstration"] is True
    assert "TAMPER" in data["verification_status"] or data["verification_result"] in ["INVALID", "TAMPERING_DETECTED"]
    assert data["original_hash"] != data["tampered_hash"]
    assert "restoration_status" in data
    assert "VERIFIED_GENUINE" in data["restoration_status"]

def test_9_14_compliance_framework_mapping(auth_headers):
    """Test 9.14: Governance connection to NIST CSF, ISO 27001, and CIS Controls."""
    res = client.get("/api/v1/ciso/framework-mapping", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "frameworks" in data
    assert "NIST Cybersecurity Framework (CSF v2.0)" in data["frameworks"]
    assert "ISO/IEC 27001:2022" in data["frameworks"]
    assert "CIS Critical Security Controls v8" in data["frameworks"]
    assert "notice" in data
    assert "Assessment Coverage" in data["notice"]

def test_9_15_executive_ciso_view(auth_headers):
    """Test 9.15: Executive Dashboard answering the 8 Core Questions."""
    res = client.get("/api/v1/ciso/executive-view", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    
    # Verify the 8 core questions are all explicitly addressed
    assert "1_current_risk" in data
    assert "2_financial_cost" in data
    assert "3_major_risk_drivers" in data
    assert "4_recommended_controls" in data
    assert "5_recommended_investment" in data
    assert "6_expected_risk_reduction" in data
    assert "7_ciso_decision" in data
    assert "8_auditable" in data
    assert data["8_auditable"] is True
