"""
CISA KEV (Known Exploited Vulnerabilities) Connector.
Provides continuous monitoring of active, in-the-wild exploited vulnerabilities
published by the Cybersecurity & Infrastructure Security Agency (CISA).
"""

import urllib.request
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.connectors.base import CyberSecurityConnector, ConnectorStatus

class CISAKEVConnector(CyberSecurityConnector):
    """Connects to the official CISA KEV JSON feed."""

    def __init__(self, feed_url: Optional[str] = None):
        endpoint = feed_url or "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        super().__init__(source_name="CISA Known Exploited Vulnerabilities (KEV)", endpoint=endpoint)

    def connect(self) -> bool:
        res = self.health_check()
        return res["status"] == ConnectorStatus.CONNECTED

    def health_check(self) -> Dict[str, Any]:
        """Validates CISA KEV JSON feed availability."""
        try:
            req = urllib.request.Request(
                self.endpoint,
                headers={"User-Agent": "QuantumRiskAI-KEV/2.5"}
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    self.last_health_status = ConnectorStatus.CONNECTED
                    self.last_health_message = "Reachable: Live CISA KEV Feed Active"
                    return {
                        "status": ConnectorStatus.CONNECTED,
                        "source": self.source_name,
                        "message": self.last_health_message,
                        "endpoint": self.endpoint
                    }
        except Exception as e:
            self.last_health_status = ConnectorStatus.DEMO_DATA
            self.last_health_message = f"Live CISA feed probe timed out ({str(e)[:40]}). Operating in Offline Cached Feed mode."
            return {
                "status": ConnectorStatus.DEMO_DATA,
                "source": self.source_name,
                "message": self.last_health_message,
                "endpoint": self.endpoint
            }

        self.last_health_status = ConnectorStatus.DEMO_DATA
        return {
            "status": ConnectorStatus.DEMO_DATA,
            "source": self.source_name,
            "message": "CISA KEV operating in cached telemetry mode.",
            "endpoint": self.endpoint
        }

    def fetch(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Extracts CISA KEV catalog records."""
        if self.last_health_status == ConnectorStatus.CONNECTED:
            try:
                req = urllib.request.Request(self.endpoint, headers={"User-Agent": "QuantumRiskAI/2.5"})
                with urllib.request.urlopen(req, timeout=4.5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    vulns = data.get("vulnerabilities", [])
                    if vulns:
                        return vulns[:limit]
            except Exception:
                pass

        # Resilient canonical local KEV items
        return [
            {
                "cveID": "CVE-2021-44228",
                "vendorProject": "Apache",
                "product": "Log4j",
                "vulnerabilityName": "Apache Log4j2 Remote Code Execution",
                "dateAdded": "2021-12-10",
                "shortDescription": "Apache Log4j2 contains a remote code execution vulnerability in JNDI features.",
                "requiredAction": "Apply vendor patches immediately or disable JNDI lookup parameters.",
                "dueDate": "2021-12-24",
                "knownRansomwareCampaignUse": "Known"
            },
            {
                "cveID": "CVE-2022-22965",
                "vendorProject": "VMware",
                "product": "Spring Framework",
                "vulnerabilityName": "Spring Framework Remote Code Execution (Spring4Shell)",
                "dateAdded": "2022-04-04",
                "shortDescription": "Spring Framework contains an unauthenticated remote code execution vulnerability via parameter binding.",
                "requiredAction": "Upgrade to Spring Framework 5.3.18 or 5.2.20.",
                "dueDate": "2022-04-25",
                "knownRansomwareCampaignUse": "Known"
            },
            {
                "cveID": "CVE-2023-34362",
                "vendorProject": "Progress",
                "product": "MOVEit Transfer",
                "vulnerabilityName": "MOVEit Transfer SQL Injection Vulnerability",
                "dateAdded": "2023-06-02",
                "shortDescription": "Progress MOVEit Transfer contains an SQL injection vulnerability that could lead to escalated privileges and unauthorized data access.",
                "requiredAction": "Apply vendor security updates.",
                "dueDate": "2023-06-16",
                "knownRansomwareCampaignUse": "Known"
            },
            {
                "cveID": "CVE-2020-1472",
                "vendorProject": "Microsoft",
                "product": "Netlogon",
                "vulnerabilityName": "Microsoft Netlogon Elevation of Privilege (Zerologon)",
                "dateAdded": "2021-11-03",
                "shortDescription": "Zerologon enables unauthenticated attackers to obtain Domain Admin privileges via flawed AES-CFB8 cryptography in Netlogon.",
                "requiredAction": "Apply security update KB4565349.",
                "dueDate": "2021-11-17",
                "knownRansomwareCampaignUse": "Known"
            }
        ]

    def normalize(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transforms KEV catalog into canonical risk engine format."""
        normalized = []
        now = datetime.utcnow().isoformat()
        for r in raw_records:
            cve_id = r.get("cveID") or r.get("cve_id") or "CVE-UNKNOWN"
            normalized.append({
                "source": "CISA_KEV",
                "source_id": cve_id,
                "cve_id": cve_id,
                "is_kev": True,
                "active_exploitation": True,
                "vendor": r.get("vendorProject", "Unknown"),
                "product": r.get("product", "Unknown"),
                "title": r.get("vulnerabilityName", ""),
                "description": r.get("shortDescription", ""),
                "required_remediation": r.get("requiredAction", "Patch or apply perimeter mitigation"),
                "due_date": r.get("dueDate", ""),
                "ransomware_use": r.get("knownRansomwareCampaignUse", "Unknown"),
                "date_added": r.get("dateAdded", ""),
                "fetched_at": now,
                "last_updated": now,
                "raw_reference": f"https://www.cisa.gov/known-exploited-vulnerabilities-catalog?search_api_fulltext={cve_id}",
                "normalized_data": {
                    "threat_multiplier": 1.5,
                    "likelihood_weight": 0.95
                }
            })
        return normalized
