"""
Security Tool Integrations & Telemetry Connectors API Router.
Coordinates real-world intelligence feeds:
- NVD (National Vulnerability Database)
- CISA KEV (Known Exploited Vulnerabilities Catalog)
- MITRE ATT&CK (Enterprise Tactics & Techniques)
- Wazuh EDR (Endpoint Telemetry & Alerts)
- OpenVAS / Greenbone (Network Vulnerability Scanner)
Truthfulness rule: Status accurately reflects CONNECTED, NOT CONFIGURED, or DEMO DATA.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any, List

from app.api.auth import get_current_user
from app.connectors import (
    nvd_connector,
    cisa_kev_connector,
    mitre_attack_connector,
    wazuh_connector,
    openvas_connector,
    get_connectors_status_summary
)

router = APIRouter(prefix="/integrations", tags=["Security Tool Integrations & Telemetry Connectors"])

@router.get("/status")
def get_integrations_status(current_user = Depends(get_current_user)):
    """Returns active connectivity diagnostics for all 5 security intelligence feeds."""
    connectors_summary = get_connectors_status_summary()
    return {
        "total_connectors": len(connectors_summary),
        "timestamp": datetime.utcnow().isoformat(),
        "connectors": connectors_summary,
        "policy": "Never fabricate connection status. Unconfigured on-prem connectors report NOT CONFIGURED or DEMO DATA."
    }

@router.post("/trigger-sync")
def trigger_connector_sync(connector_id: str = "all", current_user = Depends(get_current_user)):
    """Triggers telemetry ingestion across real-world cybersecurity intelligence sources."""
    results = {}
    
    if connector_id in ("all", "nvd"):
        results["nvd"] = nvd_connector.sync_pipeline(limit=25)
    if connector_id in ("all", "cisa_kev"):
        results["cisa_kev"] = cisa_kev_connector.sync_pipeline(limit=25)
    if connector_id in ("all", "mitre_attack"):
        results["mitre_attack"] = mitre_attack_connector.sync_pipeline(limit=25)
    if connector_id in ("all", "wazuh"):
        results["wazuh"] = wazuh_connector.sync_pipeline(limit=25)
    if connector_id in ("all", "openvas"):
        results["openvas"] = openvas_connector.sync_pipeline(limit=25)

    return {
        "status": "SYNC_COMPLETE",
        "timestamp": datetime.utcnow().isoformat(),
        "synced_connectors": list(results.keys()),
        "sync_details": results,
        "message": "Real-world intelligence feeds synchronized with enterprise risk engine."
    }
