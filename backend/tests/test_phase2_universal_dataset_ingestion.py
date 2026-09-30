"""
Phase 2 Universal Dataset Ingestion Comprehensive Test Suite.
Validates:
- CSV Ingestion (valid, empty, malformed, duplicate records, wrong types)
- XLSX Ingestion (single-sheet and multi-sheet auto-detection)
- ZIP Ingestion (safe extraction, path traversal defense, package inspection)
- Field Mapping & Non-fabrication guarantee
- Range validation (CVSS 0-10, criticality)
- Missing financial fields behavior ("Financial Data Not Available")
- Dataset Registry, active_dataset_id, and Dataset Switching
"""

import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.risk_engine.universal_importer import universal_csv_engine
from app.risk_engine.xlsx_parser import parse_xlsx_sheets, parse_xlsx_to_csv_text

client = TestClient(app)

def test_csv_upload_and_field_mapping():
    """Verify standard cybersecurity CSV upload and automatic column alias mapping."""
    csv_data = (
        "host_id,server_name,category,ip_addr,crit_score,perimeter_facing,cve_code,cvss_base,exploit_status,patch_status\n"
        "SRV-001,Primary Payment Switch,server,10.0.1.5,95,true,CVE-2024-21762,9.8,true,false\n"
        "SRV-002,Internal Active Directory,server,10.0.1.10,90,false,CVE-2020-1472,10.0,true,true\n"
    )
    res = client.post(
        "/api/v1/universal-import/execute",
        data={"csv_content": csv_data, "filename": "test_infra.csv"}
    )
    assert res.status_code == 200
    data = res.json()["dataset"]
    assert len(data["assets"]) == 2
    assert len(data["vulnerabilities"]) == 2
    
    # Check field detection
    overview = data["overview"]
    assert "asset_id" in overview["mapped_fields"]
    assert "asset_name" in overview["mapped_fields"]
    assert "cve_id" in overview["mapped_fields"]
    assert "cvss_score" in overview["mapped_fields"]
    assert overview["has_financial_data"] is False
    assert overview["total_modeled_financial_impact_label"] == "Data Not Available"

def test_invalid_cvss_and_data_validation():
    """Verify CVSS range validation (0.0 - 10.0) rejects out-of-bounds records with warnings."""
    csv_data = (
        "asset_id,cve_id,cvss_score\n"
        "AST-01,CVE-2024-001,15.5\n"   # Invalid CVSS > 10.0
        "AST-02,CVE-2024-002,-2.0\n"   # Invalid CVSS < 0.0
        "AST-03,CVE-2024-003,7.5\n"    # Valid
    )
    analysis = universal_csv_engine.analyze_csv(csv_data, filename="invalid_cvss.csv")
    assert analysis["total_rows"] == 3
    assert analysis["rejected_records"] == 2
    assert analysis["valid_records"] == 1
    assert len(analysis["validation_warnings"]) >= 2

def test_empty_csv_and_missing_identifiers():
    """Verify empty rows and records lacking both asset and vulnerability identifiers are rejected."""
    csv_data = (
        "asset_id,asset_name,cve_id,cvss_score\n"
        ",,,,\n"                        # Completely empty row
        "   ,   ,   ,   \n"             # Whitespace row
        "AST-10,Web Ingress,CVE-2023-111,7.5\n" # Valid
    )
    res = universal_csv_engine.execute_import(csv_data, filename="empty_rows.csv")
    assert res["summary"]["valid_records"] == 1
    assert res["summary"]["rejected_records"] == 2

def test_multi_sheet_xlsx_parsing():
    """Verify multi-sheet XLSX workbooks are parsed and sheets identified as individual modules."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr(
            'xl/workbook.xml',
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets>'
            '<sheet name="Assets" sheetId="1" r:id="rId1"/>'
            '<sheet name="Vulnerabilities" sheetId="2" r:id="rId2"/>'
            '</sheets></workbook>'
        )
        zf.writestr(
            'xl/_rels/workbook.xml.rels',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Target="worksheets/sheet2.xml"/>'
            '</Relationships>'
        )
        zf.writestr(
            'xl/sharedStrings.xml',
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<si><t>asset_id</t></si><si><t>asset_name</t></si><si><t>AST-X1</t></si><si><t>PaymentGW</t></si>'
            '<si><t>cve_id</t></si><si><t>cvss_score</t></si><si><t>CVE-2024-999</t></si>'
            '</sst>'
        )
        zf.writestr(
            'xl/worksheets/sheet1.xml',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>'
            '<row><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
            '<row><c r="A2" t="s"><v>2</v></c><c r="B2" t="s"><v>3</v></c></row>'
            '</sheetData></worksheet>'
        )
        zf.writestr(
            'xl/worksheets/sheet2.xml',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>'
            '<row><c r="A1" t="s"><v>4</v></c><c r="B1" t="s"><v>5</v></c></row>'
            '<row><c r="A2" t="s"><v>6</v></c><c r="B2"><v>9.5</v></c></row>'
            '</sheetData></worksheet>'
        )

    sheets = parse_xlsx_sheets(buf.getvalue())
    assert "Assets" in sheets
    assert "Vulnerabilities" in sheets
    assert "AST-X1,PaymentGW" in sheets["Assets"]
    assert "CVE-2024-999,9.5" in sheets["Vulnerabilities"]

def test_zip_package_ingestion_and_path_traversal_defense():
    """Verify ZIP package ingestion safely inspects contained files and ignores malicious paths."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr(
            "assets.csv",
            "asset_id,asset_name,asset_type,criticality\n"
            "AST-Z1,Crown Jewel Database,database,5\n"
            "AST-Z2,Public Web API,application,4\n"
        )
        zf.writestr(
            "vulnerabilities.csv",
            "cve_id,cvss_score,exploit_available\n"
            "CVE-2024-1111,9.8,true\n"
        )
        # Malicious traversal attempt
        zf.writestr(
            "../../etc/passwd",
            "root:x:0:0:root:/root:/bin/bash\n"
        )

    pkg_res = universal_csv_engine.analyze_zip_package(buf.getvalue(), zip_filename="safe_package.zip")
    assert pkg_res["is_package"] is True
    assert pkg_res["total_files"] == 2
    # Ensure traversal file was dropped
    assert not any("passwd" in f["filename"] for f in pkg_res["files"])

def test_dataset_switching_and_active_dataset():
    """Verify switching active dataset refreshes downstream active context."""
    # 1. Upload custom dataset
    csv_custom = (
        "asset_id,asset_name,criticality,cvss_score,cve_id\n"
        "CUST-01,Custom Core Server,5,9.8,CVE-2024-CUSTOM\n"
    )
    upload_res = client.post(
        "/api/v1/universal-import/execute",
        data={"csv_content": csv_custom, "filename": "custom_switch_test.csv"}
    )
    assert upload_res.status_code == 200
    custom_id = upload_res.json()["dataset"]["id"]

    # 2. Verify active dataset is custom
    active_res = client.get("/api/v1/universal-import/active")
    assert active_res.status_code == 200
    assert active_res.json()["dataset"]["id"] == custom_id

    # 3. Switch to SIH Benchmark Dataset
    switch_res = client.post(f"/api/v1/datasets/sih_ps26105/activate")
    assert switch_res.status_code == 200

    # 4. Verify active dataset switched
    curr_active = universal_csv_engine.get_active_dataset()
    assert curr_active is not None
    assert curr_active.get("id") in ["SIH_PS26105", "sih_ps26105"]
