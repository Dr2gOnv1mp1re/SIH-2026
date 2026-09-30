"""
Quantum Risk AI — Modular Cybersecurity Connectors Package.
Exposes standard connectors:
- NVDConnector
- CISAKEVConnector
- MITREAttackConnector
- WazuhConnector
- OpenVASConnector
"""

from typing import List, Dict, Any
from app.connectors.base import CyberSecurityConnector, ConnectorStatus
from app.connectors.nvd import NVDConnector
from app.connectors.cisa_kev import CISAKEVConnector
from app.connectors.mitre_attack import MITREAttackConnector
from app.connectors.wazuh import WazuhConnector
from app.connectors.openvas import OpenVASConnector

# Singleton instances initialized for platform operations
nvd_connector = NVDConnector()
cisa_kev_connector = CISAKEVConnector()
mitre_attack_connector = MITREAttackConnector()
wazuh_connector = WazuhConnector()
openvas_connector = OpenVASConnector()

ALL_CONNECTORS: List[CyberSecurityConnector] = [
    nvd_connector,
    cisa_kev_connector,
    mitre_attack_connector,
    wazuh_connector,
    openvas_connector
]

def get_all_connectors() -> List[CyberSecurityConnector]:
    return ALL_CONNECTORS

def get_connectors_status_summary() -> List[Dict[str, Any]]:
    """Runs health check probes across all 5 connectors and returns status summary."""
    summary = []
    for c in ALL_CONNECTORS:
        health = c.health_check()
        summary.append({
            "name": c.source_name,
            "status": health["status"],
            "endpoint": c.endpoint,
            "message": health["message"],
            "last_synced": c.last_sync_timestamp.isoformat() if c.last_sync_timestamp else "Cached / Demo Seed",
            "records_ingested": c.total_records_ingested
        })
    return summary
