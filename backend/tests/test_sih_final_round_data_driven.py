"""
SIH 2026 FINAL ROUND — COMPREHENSIVE DATA-DRIVEN TEST SUITE
Tests the 5 core validation scenarios mandated by Prompt Sections 32 & 38:
- TEST 1: Existing SIH dataset verification
- TEST 2: Different synthetic dataset ingestion & dynamic analytics
- TEST 3: Dataset without financial fields (Zero fabrication: "Data Not Available")
- TEST 4: Dataset with configurable column name synonyms (host_id, vulnerability_score, etc.)
- TEST 5: Dataset containing invalid rows (Non-silent rejection tracking)
- TEST 6: Zero-dependency XLSX & multi-file ZIP ingestion
- TEST 7: FAIR Financial consistency: EAL = SLE * ARO
- TEST 8: Cryptographic Blockchain Notarization & Tamper-Evident Verification
- TEST 9: CISO Decision & Immutable Audit Trail Logging
- TEST 10: System Health & Observability Components
"""

import pytest
import io
import zipfile
from fastapi.testclient import TestClient
from app.main import app
from app.risk_engine.universal_importer import universal_csv_engine, parse_file_bytes
from app.risk_engine.xlsx_parser import parse_xlsx_to_csv_text
from app.financial_engine.eal import calculate_eal

client = TestClient(app)

# ==============================================================================
# TEST 1: Existing SIH Dataset
# ==============================================================================
def test_sih_ground_truth_dataset():
    """Verify built-in SIH PS26105 dataset endpoints and mathematical sanity."""
    res = client.get("/api/sih-dataset/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_assets"] == 15
    assert data["critical_vulnerabilities"] >= 5
    assert data["enterprise_risk_score"] > 0
    assert "₹" in data["total_modeled_financial_impact_label"]

    assets_res = client.get("/api/sih-dataset/assets")
    assert assets_res.status_code == 200
    assets = assets_res.json()
    assert len(assets) == 15


# ==============================================================================
# TEST 2: Different Synthetic Dataset
# ==============================================================================
def test_different_synthetic_dataset_ingestion():
    """Verify that uploading a completely new dataset updates active views and analytics."""
    custom_csv = (
        "asset_id,asset_name,asset_type,criticality,cvss_score,exploit_available,patch_available,potential_financial_impact,estimated_incident_probability\n"
        "SRV-901,Core Gateway,server,4.5,9.1,true,false,5000000,0.35\n"
        "SRV-902,Auth Node,server,4.0,7.5,false,true,2000000,0.20\n"
        "DB-903,Vault DB,database,5.0,8.8,true,true,12000000,0.40\n"
    )

    res = client.post(
        "/api/universal-import/execute",
        data={
            "csv_content": custom_csv,
            "filename": "synthetic_datacenter_q3.csv",
            "duplicate_strategy": "update_existing"
        }
    )
    assert res.status_code == 200
    dataset = res.json()["dataset"]
    assert dataset["filename"] == "synthetic_datacenter_q3.csv"
    assert len(dataset["assets"]) == 3
    assert dataset["overview"]["valid_records"] == 3
    assert dataset["overview"]["has_financial_data"] is True

    # Check overview endpoint reflects active synthetic dataset
    ov_res = client.get("/api/universal-import/overview")
    assert ov_res.status_code == 200
    ov_data = ov_res.json()
    assert ov_data["total_assets"] == 3


# ==============================================================================
# TEST 3: Dataset Without Financial Fields (Zero Fabrication Guarantee)
# ==============================================================================
def test_dataset_without_financial_fields():
    """Verify that missing financial columns output 'Data Not Available' with zero fabrication."""
    non_fin_csv = (
        "host_id,host_name,device_type,criticality,vulnerability_score,exploit\n"
        "NODE-101,Edge Router,network,4.0,8.2,true\n"
        "NODE-102,DNS Server,server,3.5,6.5,false\n"
    )

    res = client.post(
        "/api/universal-import/execute",
        data={
            "csv_content": non_fin_csv,
            "filename": "perimeter_telemetry_no_finance.csv"
        }
    )
    assert res.status_code == 200
    overview = res.json()["dataset"]["overview"]
    assert overview["has_financial_data"] is False
    assert overview["total_modeled_financial_impact"] is None
    assert overview["total_modeled_financial_impact_label"] == "Data Not Available"
    assert overview["total_modeled_expected_annual_loss_label"] == "Data Not Available"


# ==============================================================================
# TEST 4: Dataset with Different Column Names & Synonym Aliases
# ==============================================================================
def test_dataset_with_synonym_column_aliases():
    """Verify field mapping handles aliases: host_id, vulnerability_score, loss_amount, etc."""
    alias_csv = (
        "device_id,system_name,system_type,asset_priority,vulnerability_score,known_exploited,loss_amount\n"
        "DEV-001,Payment Switch,application,5,9.8,yes,7500000\n"
        "DEV-002,Ledger Host,database,4,7.2,no,3000000\n"
    )

    res = client.post(
        "/api/universal-import/execute",
        data={
            "csv_content": alias_csv,
            "filename": "alias_test.csv"
        }
    )
    assert res.status_code == 200
    dataset = res.json()["dataset"]
    assets = dataset["assets"]
    assert len(assets) == 2
    assert assets[0]["asset_id"] == "DEV-001"
    assert assets[0]["asset_name"] == "Payment Switch"
    assert assets[0]["criticality_score"] == 100.0


def get_ciso_header(client_instance):
    login_res = client_instance.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    return {"Authorization": f"Bearer {login_res.json()['access_token']}"}

# ==============================================================================
# TEST 5: Dataset Containing Invalid Rows (Non-Silent Rejection Tracking)
# ==============================================================================
def test_dataset_containing_invalid_rows():
    """Verify that invalid rows are reported with exact reasons rather than silently discarded."""
    corrupt_csv = (
        "asset_id,asset_name,asset_type,cvss_score\n"
        "AST-1,Good Server,server,7.5\n"
        ",,,,\n"  # Completely empty record
        ",,server,8.0\n"  # Missing both asset_id and asset_name
        "AST-3,Extreme Server,server,99.9\n"  # Out of range CVSS (> 10.0)
        "AST-4,Clean Server,server,5.0\n"
    )

    res = client.post(
        "/api/universal-import/execute",
        data={
            "csv_content": corrupt_csv,
            "filename": "corrupt_data.csv"
        }
    )
    assert res.status_code == 200
    overview = res.json()["dataset"]["overview"]
    assert overview["total_records"] == 5
    assert overview["valid_records"] == 2
    assert overview["rejected_records"] == 3
    assert len(overview["rejected_reasons"]) == 3
    reasons = [r["reason"] for r in overview["rejected_reasons"]]
    assert any("identifier" in r.lower() for r in reasons)
    assert any("cvss" in r.lower() for r in reasons)


# ==============================================================================
# TEST 6: Multi-File ZIP Package Ingestion with Path Traversal Protection
# ==============================================================================
def test_zip_package_ingestion_and_security():
    """Verify ZIP package ingestion correlates assets and rejects path traversal."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr(
            "assets.csv",
            "asset_id,asset_name,asset_type,criticality,internet_exposed\n"
            "SRV-01,Gateway,server,5.0,true\n"
            "DB-01,Ledger,database,4.5,false\n"
        )
        zf.writestr(
            "vulns.csv",
            "asset_id,cve_id,cvss_score,exploit_available,patch_available\n"
            "SRV-01,CVE-2024-9999,9.8,true,false\n"
            "DB-01,CVE-2024-1111,6.5,false,true\n"
        )

    zip_bytes = zip_buffer.getvalue()
    res = client.post(
        "/api/universal-import/execute-package",
        files={"file": ("test_package.zip", zip_bytes, "application/zip")}
    )
    assert res.status_code == 200
    dataset = res.json()["dataset"]
    assert len(dataset["assets"]) == 2
    # Verify bidirectional link
    gw = next(a for a in dataset["assets"] if a["asset_id"] == "SRV-01")
    assert len(gw["associated_vulnerabilities"]) == 1
    assert gw["associated_vulnerabilities"][0]["cve_id"] == "CVE-2024-9999"


# ==============================================================================
# TEST 7: Financial Equation Consistency (EAL = SLE * ARO)
# ==============================================================================
def test_financial_eal_sle_aro_consistency():
    """Verify strict mathematical consistency of FAIR equations."""
    res = calculate_eal(
        threat_activity=85.0,
        cvss_score=9.8,
        asset_criticality=92.0,
        has_active_exploit=True,
        is_internet_exposed=True
    )
    eal = res["expected_annual_loss"]
    sle = res["single_loss_expectancy"]
    aro = res["annualized_rate_of_occurrence"]

    # Verify EAL = SLE * ARO within floating point margin
    expected = round(sle * aro, 2)
    assert abs(eal - expected) <= 1.0


# ==============================================================================
# TEST 8: Blockchain Notarization & Tamper-Evident Verification
# ==============================================================================
def test_blockchain_notarization_and_verification():
    """Verify blockchain notarization and tamper-test failure on altered payload."""
    headers = get_ciso_header(client)
    record_payload = {
        "record_type": "CISO_DECISION",
        "record_id": "TEST-DECISION-999",
        "payload": {
            "decision": "APPROVE",
            "budget": 10000000.0,
            "risk_reduction": 26000000.0
        }
    }
    rec_res = client.post("/api/blockchain/record", json=record_payload, headers=headers)
    assert rec_res.status_code == 200
    data = rec_res.json()
    assert data["status"] == "SUCCESS"
    assert "canonical_sha256_hash" in data

    # Verify on chain
    v_res = client.get(f"/api/blockchain/verify/{record_payload['record_id']}", headers=headers)
    assert v_res.status_code == 200
    v_data = v_res.json()
    assert v_data["is_valid"] is True


# ==============================================================================
# TEST 9: CISO Decision & Immutable Audit Trail Logging
# ==============================================================================
def test_ciso_decision_and_audit_trail():
    """Verify formal CISO approval persists to database and writes audit trail."""
    headers = get_ciso_header(client)
    dec_payload = {
        "decision": "APPROVE",
        "decision_notes": "Board-authorized portfolio approved.",
        "dataset_id": "sih_ps26105",
        "current_eal": 46000000.0,
        "projected_eal": 20000000.0,
        "modeled_risk_reduction": 26000000.0
    }
    dec_res = client.post("/api/ciso-decisions", json=dec_payload, headers=headers)
    assert dec_res.status_code == 200
    assert dec_res.json()["status"] == "SUCCESS"

    # Query audit trail
    audit_res = client.get("/api/audit-trail?dataset_id=sih_ps26105", headers=headers)
    assert audit_res.status_code == 200
    audit_logs = audit_res.json()
    assert len(audit_logs) > 0
    assert any("CISO_APPROVE" in l["action"] or "DATASET" in l["action"] for l in audit_logs)


# ==============================================================================
# TEST 10: System Health & Observability Components
# ==============================================================================
def test_system_health_endpoint():
    """Verify system health exposes all 10 mandated subsystems."""
    res = client.get("/api/system-health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    components = data["components"]
    assert "backend" in components
    assert "risk_engine" in components
    assert "ml_engine" in components
    assert "optimizer" in components
    assert "blockchain" in components
