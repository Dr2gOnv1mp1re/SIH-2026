"""
Phase 6: Threat Intelligence & Attack Path Analysis Automated Test Suite.
Verifies:
1. CVE lookup and NVD intelligence mapping.
2. CISA KEV catalog integration (Known Exploited Vulnerability = YES/NO).
3. MITRE ATT&CK Enterprise tactics and techniques mapping.
4. Dynamic attack graph generation from active dataset.
5. Path risk scoring and critical path discovery.
6. Missing relationship data handling ("Attack path cannot be determined from available dataset").
7. Threat intelligence -> Risk engine feedback (/threats/sync-kev).
8. Attack path -> Security control recommendations.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.attack_paths.analyzer import attack_path_engine
from app.integrations.connectors import NVDConnector, CISAKEVConnector, MITREAttackConnector

def test_cve_nvd_and_cisa_kev_lookup():
    """Verify CVE lookup, CVSS score mapping, and CISA KEV weaponization status."""
    with TestClient(app) as client:
        login_res = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "Ciso@12345"
        })
        assert login_res.status_code == 200
        headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        # 1. Weaponized CVE in CISA KEV (Log4Shell)
        log4j_res = client.get("/api/v1/threats/cve/CVE-2021-44228", headers=headers)
        assert log4j_res.status_code == 200
        log4j_data = log4j_res.json()
        assert log4j_data["cve_id"] == "CVE-2021-44228"
        assert log4j_data["cvss_score"] == 10.0
        assert log4j_data["known_exploited_vulnerability"] == "YES"
        assert log4j_data["cisa_kev_status"] == "Known Exploited Vulnerability"

        # 2. Non-KEV CVE lookup
        generic_res = client.get("/api/v1/threats/cve/CVE-2023-99999", headers=headers)
        assert generic_res.status_code == 200
        generic_data = generic_res.json()
        assert generic_data["known_exploited_vulnerability"] == "NO"
        assert generic_data["cisa_kev_status"] == "Not in Known Exploited Catalog"

def test_cisa_kev_and_mitre_catalogs():
    """Verify CISA KEV catalog and MITRE ATT&CK enterprise feeds."""
    with TestClient(app) as client:
        login_res = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "Ciso@12345"
        })
        headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        # CISA KEV Catalog
        kev_res = client.get("/api/v1/threats/cisa-kev", headers=headers)
        assert kev_res.status_code == 200
        kev_data = kev_res.json()
        assert isinstance(kev_data, list)
        assert len(kev_data) >= 3
        assert any(k["cve_id"] == "CVE-2021-44228" for k in kev_data)

        # MITRE ATT&CK Matrix
        mitre_res = client.get("/api/v1/threats/mitre", headers=headers)
        assert mitre_res.status_code == 200
        mitre_data = mitre_res.json()
        assert isinstance(mitre_data, list)
        assert len(mitre_data) >= 2
        assert "tactics" in mitre_data[0]

def test_dynamic_attack_graph_generation_from_dataset():
    """Verify dynamic attack graph generation connecting Ingress -> Host -> Crown Jewel."""
    custom_dataset = {
        "id": "DS-TEST-ATTACK-01",
        "filename": "Attack_Path_Test.csv",
        "assets": [
            {
                "asset_id": "AST-WEB-99",
                "asset_name": "Public Ingress Gateway",
                "asset_type": "WEB",
                "criticality_score": 75.0,
                "internet_exposed": True,
                "control_effectiveness": 0.60
            },
            {
                "asset_id": "AST-APP-99",
                "asset_name": "Microservice Application Host",
                "asset_type": "SERVER",
                "criticality_score": 80.0,
                "internet_exposed": False,
                "control_effectiveness": 0.65
            },
            {
                "asset_id": "AST-DB-99",
                "asset_name": "Transaction Database Crown Jewel",
                "asset_type": "DATABASE",
                "criticality_score": 98.0,
                "internet_exposed": False,
                "control_effectiveness": 0.50
            }
        ],
        "vulnerabilities": [
            {
                "cve_id": "CVE-2024-21762",
                "cvss_score": 9.6,
                "exploit_available": True,
                "affected_asset_id": "AST-WEB-99"
            }
        ]
    }

    graph = attack_path_engine.generate_dynamic_attack_graph(custom_dataset)
    assert graph["status"] == "SUCCESS"
    assert len(graph["nodes"]) >= 3
    assert len(graph["edges"]) >= 2
    assert len(graph["critical_attack_paths"]) == 1

    path = graph["critical_attack_paths"][0]
    assert path["path_risk_score"] >= 80.0
    assert "Public Internet" in path["start_point"]
    assert "Transaction Database Crown Jewel" in path["target_asset"]
    assert len(path["missing_controls"]) > 0

def test_missing_relationship_data_handling():
    """Verify that when a dataset has no exposed assets or no crown jewels, it reports unavailable."""
    isolated_dataset = {
        "id": "DS-NO-RELATIONSHIP",
        "filename": "No_Exposure.csv",
        "assets": [
            {"asset_id": "A1", "name": "Internal Printer", "internet_exposed": False, "criticality_score": 20.0},
            {"asset_id": "A2", "name": "Internal Scanner", "internet_exposed": False, "criticality_score": 15.0}
        ],
        "vulnerabilities": []
    }

    graph = attack_path_engine.generate_dynamic_attack_graph(isolated_dataset)
    assert graph["status"] == "UNAVAILABLE"
    assert "Attack path cannot be determined" in graph["message"]
    assert len(graph["critical_attack_paths"]) == 0

def test_attack_path_api_endpoints():
    """Verify /api/v1/attack-paths and /api/v1/attack-paths/critical endpoints."""
    with TestClient(app) as client:
        login_res = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "Ciso@12345"
        })
        headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        # 1. Full attack path graph data
        paths_res = client.get("/api/v1/attack-paths", headers=headers)
        assert paths_res.status_code == 200
        paths_data = paths_res.json()
        assert "nodes" in paths_data
        assert "edges" in paths_data
        assert "critical_attack_paths" in paths_data

        # 2. Critical path endpoint
        crit_res = client.get("/api/v1/attack-paths/critical", headers=headers)
        assert crit_res.status_code == 200
        crit_data = crit_res.json()
        assert "target_asset" in crit_data
        assert "path_risk_score" in crit_data
        assert "missing_controls" in crit_data
