import pytest
from app.connectors.base import ConnectorStatus
from app.connectors.nvd import NVDConnector
from app.connectors.cisa_kev import CISAKEVConnector
from app.connectors.mitre_attack import MITREAttackConnector
from app.connectors.wazuh import WazuhConnector
from app.connectors.openvas import OpenVASConnector
from app.connectors import get_connectors_status_summary

def test_nvd_connector_health_and_fetch():
    connector = NVDConnector()
    health = connector.health_check()
    assert health["status"] in [ConnectorStatus.CONNECTED, ConnectorStatus.DEMO_DATA, "CONNECTED", "DEMO DATA"]
    assert "source" in health
    
    # Test fetch returns valid records with CVE identifiers
    data = connector.fetch()
    assert len(data) > 0
    assert any("CVE-" in item.get("id", "") for item in data)

def test_cisa_kev_connector_health_and_fetch():
    connector = CISAKEVConnector()
    health = connector.health_check()
    assert health["status"] in [ConnectorStatus.CONNECTED, ConnectorStatus.DEMO_DATA, "CONNECTED", "DEMO DATA"]
    
    data = connector.fetch()
    assert len(data) >= 6
    assert any("CVE-" in item.get("cveID", "") for item in data)

def test_mitre_attack_connector():
    connector = MITREAttackConnector()
    health = connector.health_check()
    assert health["status"] in [ConnectorStatus.CONNECTED, "CONNECTED"]
    
    techniques = connector.fetch()
    assert len(techniques) >= 4
    assert any(t.get("technique_id") == "T1190" for t in techniques)
    
    mapped = connector.get_tactics_for_cve("CVE-2021-44228")
    assert len(mapped) > 0

def test_wazuh_unconfigured_truthfulness():
    connector = WazuhConnector()
    health = connector.health_check()
    # Must never falsely report CONNECTED when endpoint is not configured
    assert health["status"] in [ConnectorStatus.NOT_CONFIGURED, ConnectorStatus.DEMO_DATA, "NOT CONFIGURED", "DEMO DATA"]
    assert "not configured" in health["message"].lower() or "unreachable" in health["message"].lower()
    
    # Sync pipeline should return demo data fallback with proper status
    summary = connector.sync_pipeline()
    assert summary["status"] in [ConnectorStatus.NOT_CONFIGURED, ConnectorStatus.DEMO_DATA, "NOT CONFIGURED", "DEMO DATA"]
    assert summary["stored_count"] > 0

def test_openvas_unconfigured_truthfulness():
    connector = OpenVASConnector()
    health = connector.health_check()
    # Must never falsely report CONNECTED when port/daemon is not configured
    assert health["status"] in [ConnectorStatus.NOT_CONFIGURED, ConnectorStatus.DEMO_DATA, "NOT CONFIGURED", "DEMO DATA"]
    assert "not configured" in health["message"].lower() or "unreachable" in health["message"].lower()
    
    summary = connector.sync_pipeline()
    assert summary["status"] in [ConnectorStatus.NOT_CONFIGURED, ConnectorStatus.DEMO_DATA, "NOT CONFIGURED", "DEMO DATA"]
    assert summary["stored_count"] > 0

def test_connectors_summary():
    summary = get_connectors_status_summary()
    assert len(summary) >= 5
    names = [s["name"] for s in summary]
    assert any("NVD" in n or "NIST" in n for n in names)
    assert any("CISA" in n for n in names)
    assert any("MITRE" in n for n in names)
    assert any("Wazuh" in n for n in names)
    assert any("OpenVAS" in n for n in names)
