import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from app.risk_engine.universal_importer import universal_csv_engine, FIELD_ALIASES

def test_alias_mapping_discovery():
    """Verifies that universal column mapping recognizes variations of cybersecurity headers."""
    headers = [
        "Asset_ID", "server_name", "category", "IP_Address", "host", "criticality_score", "department",
        "CVE", "cvss_v3", "severity_level", "exploitable", "fix_available", "days_open", "details",
        "security_event", "alert_severity", "username", "2fa_enabled", "is_admin",
        "endpoint_alert", "endpoint_severity", "quarantined", "cloud_finding", "cloud_severity",
        "threat_actor", "confidence_score", "incident_probability", "financial_loss", "mitigation_cost", "defense_coverage"
    ]
    mappings = universal_csv_engine.detect_mappings(headers)
    assert len(mappings) == len(headers)
    
    # Check key mappings
    mapped_dict = {m["csv_column"]: m["target_field"] for m in mappings}
    assert mapped_dict["Asset_ID"] == "asset_id"
    assert mapped_dict["server_name"] == "asset_name"
    assert mapped_dict["category"] == "asset_type"
    assert mapped_dict["IP_Address"] == "ip_address"
    assert mapped_dict["criticality_score"] == "asset_criticality"
    assert mapped_dict["department"] == "business_unit"
    assert mapped_dict["CVE"] == "cve_id"
    assert mapped_dict["cvss_v3"] == "cvss_score"
    assert mapped_dict["severity_level"] == "vulnerability_severity"
    assert mapped_dict["exploitable"] == "exploit_available"
    assert mapped_dict["fix_available"] == "patch_available"
    assert mapped_dict["days_open"] == "vulnerability_age_days"

def test_format_a_asset_and_vulnerability_import():
    """Format A: Asset + Vulnerability CSV parsing with 1-to-many relationships."""
    csv_data = (
        "asset_id,asset_name,asset_type,business_unit,asset_criticality,cve_id,cvss_score,severity,exploit_available,patch_available\n"
        "SRV-01,Payment Gateway App,Server,Fintech,5,CVE-2024-21762,9.8,Critical,Yes,Yes\n"
        "SRV-01,Payment Gateway App,Server,Fintech,5,CVE-2021-44228,10.0,Critical,Yes,Yes\n"
        "DB-01,Core Customer DB,Database,Banking,5,CVE-2023-2825,5.5,Medium,No,Yes\n"
    )
    res = universal_csv_engine.execute_import(csv_data, filename="format_a_test.csv")
    assert res["summary"]["assets"] == 2
    assert res["summary"]["vulnerabilities"] == 3
    
    # Check 1-to-many relationship: SRV-01 has 2 CVEs
    srv_asset = next(a for a in res["assets"] if a["asset_id"] == "SRV-01")
    assert len(srv_asset["associated_vulnerabilities"]) == 2
    cve_ids = [v["cve_id"] for v in srv_asset["associated_vulnerabilities"]]
    assert "CVE-2024-21762" in cve_ids
    assert "CVE-2021-44228" in cve_ids

    # Check bidirectional reverse link: CVE-2024-21762 points back to SRV-01
    cve_rec = next(v for v in res["vulnerabilities"] if v["cve_id"] == "CVE-2024-21762")
    assert any(a["asset_id"] == "SRV-01" for a in cve_rec["affected_assets"])

def test_format_b_vulnerability_only_import():
    """Format B: Vulnerability-only CSV without asset columns."""
    csv_data = (
        "cve_id,cvss_score,vulnerability_severity,exploit_available,patch_available,vulnerability_age_days\n"
        "CVE-2026-9001,9.6,Critical,True,True,45\n"
        "CVE-2026-9002,7.2,High,False,True,12\n"
    )
    res = universal_csv_engine.execute_import(csv_data, filename="format_b_test.csv")
    assert res["summary"]["vulnerabilities"] == 2
    assert len(res["vulnerabilities"]) == 2
    assert res["vulnerabilities"][0]["cve_id"] == "CVE-2026-9001"
    assert res["vulnerabilities"][0]["cvss_score"] == 9.6

def test_format_c_asset_only_import():
    """Format C: Asset-only CSV without CVE columns (zero fabricated CVEs)."""
    csv_data = (
        "asset_id,asset_name,asset_type,business_unit,criticality,internet_exposed\n"
        "AST-101,Trade Settlement Switch,Server,Treasury,5,No\n"
        "AST-102,Public Mobile API Gateway,Application,Digital,4,Yes\n"
    )
    res = universal_csv_engine.execute_import(csv_data, filename="format_c_test.csv")
    assert res["summary"]["assets"] == 2
    assert res["summary"]["vulnerabilities"] == 0
    assert len(res["vulnerabilities"]) == 0
    # Assets have empty associated_vulnerabilities
    for a in res["assets"]:
        assert len(a["associated_vulnerabilities"]) == 0

def test_format_d_telemetry_import():
    """Format D: Cybersecurity telemetry without financial fields (financial gracefully handled as absent)."""
    csv_data = (
        "asset_id,asset_name,siem_event,siem_severity,iam_user,mfa_enabled,privileged_account,edr_alert,edr_isolated\n"
        "AST-T01,DevOps Bastion,SSH Brute Force,High,devops_lead,No,Yes,Suspicious Shell,No\n"
        "AST-T02,Internal Wiki,Normal Login,Low,user_general,Yes,No,No Alert,Yes\n"
    )
    res = universal_csv_engine.execute_import(csv_data, filename="format_d_test.csv")
    assert res["summary"]["assets"] == 2
    assert res["overview"]["has_financial_data"] is False
    assert res["overview"]["total_modeled_financial_impact_label"] == "Data Not Available"

def test_sih_ps26105_real_dataset_ingestion():
    """Full verification against PS26105_Cyber_Risk_Test_Data.csv."""
    csv_path = "PS26105_Cyber_Risk_Test_Data.csv"
    if not os.path.exists(csv_path):
        csv_path = os.path.join("..", "PS26105_Cyber_Risk_Test_Data.csv")
    
    with open(csv_path, "r", encoding="utf-8") as f:
        content = f.read()

    res = universal_csv_engine.execute_import(content, filename="PS26105_Cyber_Risk_Test_Data.csv")
    assert res["summary"]["records"] == 15
    assert res["summary"]["assets"] == 15
    assert res["summary"]["vulnerabilities"] == 13  # A009 and A010 have N/A CVEs, zero hallucination
    assert res["overview"]["total_assets"] == 15
    assert res["overview"]["has_financial_data"] is True
    assert "Cr" in res["overview"]["total_modeled_financial_impact_label"]

    # Verify A005 (Payment Gateway)
    a005 = next(a for a in res["assets"] if a["asset_id"] == "A005")
    assert a005["asset_name"] == "PAYMENT-GW-01"
    assert len(a005["associated_vulnerabilities"]) == 1
    assert a005["associated_vulnerabilities"][0]["cve_id"] == "CVE-2026-1005"
    assert a005["associated_vulnerabilities"][0]["cvss_score"] == 9.9
    assert a005["potential_financial_impact_inr"] == 25000000.0

    # Verify A009 (N/A CVE handled cleanly without phantom CVE)
    a009 = next(a for a in res["assets"] if a["asset_id"] == "A009")
    assert len(a009["associated_vulnerabilities"]) == 0
    assert not any(v["cve_id"] in ("N/A", "0", "0.0") for v in res["vulnerabilities"])

def test_universal_import_api_endpoints():
    """Verifies REST API endpoints under /api/v1/universal-import."""
    with TestClient(app) as client:
        # 1. Detect Mappings
        csv_sample = "asset_id,asset_name,cve_id,cvss_score\nAST-1,Test Server,CVE-2026-001,8.5\n"
        detect_res = client.post(
            "/api/v1/universal-import/analyze-raw",
            json={"csv_content": csv_sample, "filename": "test.csv"}
        )
        assert detect_res.status_code == 200
        data = detect_res.json()
        assert data["total_rows"] == 1
        assert data["detected_unique_assets"] == 1
        assert data["detected_unique_cves"] == 1

        # 2. Execute Import
        exec_res = client.post(
            "/api/v1/universal-import/execute-json",
            json={
                "csv_content": csv_sample,
                "filename": "test_api.csv",
                "duplicate_strategy": "update_existing"
            }
        )
        assert exec_res.status_code == 200
        assert exec_res.json()["status"] == "SUCCESS"

        # 3. Active Dataset
        active_res = client.get("/api/v1/universal-import/active")
        assert active_res.status_code == 200
        assert active_res.json()["active"] is True
        assert active_res.json()["dataset"]["filename"] == "test_api.csv"

        # 4. Assets & Vulnerabilities
        assets_res = client.get("/api/v1/universal-import/assets")
        assert assets_res.status_code == 200
        assert len(assets_res.json()) == 1

        vulns_res = client.get("/api/v1/universal-import/vulnerabilities")
        assert vulns_res.status_code == 200
        assert len(vulns_res.json()) == 1
        assert vulns_res.json()[0]["cve_id"] == "CVE-2026-001"
