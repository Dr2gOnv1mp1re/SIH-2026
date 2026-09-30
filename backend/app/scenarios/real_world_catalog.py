"""
Authoritative Real-World Cyber Incident & Vulnerability Catalog.
Stores documented public cyber threat intelligence with explicit data provenance tagging.
Authoritative Sources: NVD (NIST), CISA KEV, CISA Advisories, Apache Software Foundation, MITRE ATT&CK.

Technical Honesty Policy:
- Cached datasets are explicitly documented as authoritative public snapshots (not simulated live network scraping).
- Every data point carries an immutable provenance category.
"""

from enum import Enum
from typing import Dict, List, Any, Optional

class SourceType(str, Enum):
    REAL_PUBLIC_DATA = "REAL PUBLIC DATA"
    ORGANIZATION_PROVIDED = "ORGANIZATION PROVIDED"
    ANALYST_INPUT = "ANALYST INPUT"
    MODEL_ASSUMPTION = "MODEL ASSUMPTION"
    SYNTHETIC_DEMO_INPUT = "SYNTHETIC DEMONSTRATION INPUT"
    SIMULATED_DEMO_DATA = "SIMULATED DEMO DATA"

# ==============================================================================
# AUTHORITATIVE PUBLIC THREAT INTELLIGENCE CATALOG
# ==============================================================================

REAL_WORLD_SCENARIOS_CATALOG: Dict[str, Dict[str, Any]] = {
    "CVE-2021-44228": {
        "id": "scenario-log4shell",
        "cve_id": "CVE-2021-44228",
        "name": "Log4Shell — Apache Log4j JNDI Remote Code Execution",
        "short_name": "Log4Shell",
        "status": "ACTIVE_EVALUATION",
        "overview": (
            "A critical remote code execution vulnerability in Apache Log4j (2.0-beta9 through 2.14.1) "
            "enabled attackers to execute arbitrary code via JNDI lookup mechanisms (LDAP, RMI, DNS). "
            "Publicly disclosed on December 9-10, 2021, and actively exploited globally across enterprise infrastructures."
        ),
        "threat_metadata": {
            "cve": {
                "value": "CVE-2021-44228",
                "source_type": SourceType.REAL_PUBLIC_DATA.value,
                "source": "NVD (NIST)",
                "source_url": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228"
            },
            "cvss_v3_score": {
                "value": 10.0,
                "severity": "CRITICAL",
                "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                "source_type": SourceType.REAL_PUBLIC_DATA.value,
                "source": "NVD (NIST)",
                "source_url": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228"
            },
            "known_exploitation": {
                "value": True,
                "status_label": "Known Exploited Vulnerability (Active In the Wild)",
                "source_type": SourceType.REAL_PUBLIC_DATA.value,
                "source": "CISA KEV Catalog",
                "source_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
            },
            "cisa_kev_details": {
                "date_added": "2021-12-10",
                "due_date": "2021-12-24",
                "known_ransomware_campaign_use": "Known",
                "required_action": "Apply immediate updates per vendor instructions or mitigate per CISA advisory.",
                "source_type": SourceType.REAL_PUBLIC_DATA.value,
                "source": "CISA KEV Catalog",
                "source_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
            },
            "affected_products": {
                "product": "Apache Log4j",
                "affected_versions": "2.0-beta9 through 2.14.1 (Java JNDI Lookup component)",
                "patched_versions": "Log4j 2.15.0, 2.16.0, 2.17.1 (Java 8+), 2.12.4 (Java 7)",
                "cwe_id": "CWE-502: Deserialization of Untrusted Data / Improper Input Validation",
                "source_type": SourceType.REAL_PUBLIC_DATA.value,
                "source": "Apache Software Foundation Security Advisory",
                "source_url": "https://logging.apache.org/log4j/2.x/security.html"
            },
            "disclosure_timeline": {
                "reported_to_vendor": "2021-11-24",
                "public_disclosure": "2021-12-09",
                "nvd_published": "2021-12-10",
                "source_type": SourceType.REAL_PUBLIC_DATA.value,
                "source": "NVD / Apache Security Bulletin",
                "source_url": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228"
            },
            "mitre_attack_techniques": [
                {
                    "id": "T1190",
                    "name": "Exploit Public-Facing Application",
                    "tactics": ["Initial Access"],
                    "description": "Adversaries send malicious JNDI string payload via HTTP headers (User-Agent, X-Api-Version).",
                    "source_type": SourceType.REAL_PUBLIC_DATA.value,
                    "source": "MITRE ATT&CK Matrix",
                    "source_url": "https://attack.mitre.org/techniques/T1190/"
                },
                {
                    "id": "T1059",
                    "name": "Command and Scripting Interpreter",
                    "tactics": ["Execution"],
                    "description": "Execution of arbitrary Java bytecode fetched from attacker-controlled LDAP/RMI endpoint.",
                    "source_type": SourceType.REAL_PUBLIC_DATA.value,
                    "source": "MITRE ATT&CK Matrix",
                    "source_url": "https://attack.mitre.org/techniques/T1059/"
                },
                {
                    "id": "T1203",
                    "name": "Exploitation for Client Execution",
                    "tactics": ["Execution"],
                    "description": "Client-side Log4j parsing deserializes remote object reference without validation.",
                    "source_type": SourceType.REAL_PUBLIC_DATA.value,
                    "source": "MITRE ATT&CK Matrix",
                    "source_url": "https://attack.mitre.org/techniques/T1203/"
                },
                {
                    "id": "T1071.001",
                    "name": "Application Layer Protocol: Web Protocols",
                    "tactics": ["Command and Control"],
                    "description": "Outbound LDAP/RMI connections initiated by vulnerable server to attacker C2 servers.",
                    "source_type": SourceType.REAL_PUBLIC_DATA.value,
                    "source": "MITRE ATT&CK Matrix",
                    "source_url": "https://attack.mitre.org/techniques/T1071/001/"
                },
                {
                    "id": "T1105",
                    "name": "Ingress Tool Transfer",
                    "tactics": ["Command and Control"],
                    "description": "Download and staging of second-stage payloads (Cobalt Strike, Web shells, Miners).",
                    "source_type": SourceType.REAL_PUBLIC_DATA.value,
                    "source": "MITRE ATT&CK Matrix",
                    "source_url": "https://attack.mitre.org/techniques/T1105/"
                }
            ],
            "threat_actors_associated": [
                {
                    "actor": "State-Sponsored & Cybercrime Syndicates (FIN7, Cobalt, Hafnium)",
                    "objective": "Initial foothold, credential dumping, lateral movement, ransomware deployment",
                    "source_type": SourceType.REAL_PUBLIC_DATA.value,
                    "source": "CISA Cybersecurity Advisory AA21-356A",
                    "source_url": "https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-356a"
                }
            ]
        },
        "authoritative_sources": [
            {
                "organization": "National Vulnerability Database (NVD / NIST)",
                "title": "CVE-2021-44228 Detail — Apache Log4j Remote Code Execution",
                "url": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228",
                "retrieved_date": "2026-09-17 (Authoritative Cached Dataset)",
                "fields_used": ["CVSS Score 10.0", "Attack Vector (Network)", "Complexity (Low)", "Privileges (None)", "CWE-502"]
            },
            {
                "organization": "Cybersecurity & Infrastructure Security Agency (CISA)",
                "title": "Known Exploited Vulnerabilities Catalog — Log4j RCE",
                "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
                "retrieved_date": "2026-09-17 (Authoritative Cached Dataset)",
                "fields_used": ["Active Exploitation Flag", "Date Added (2021-12-10)", "Ransomware Campaign Use (Known)"]
            },
            {
                "organization": "Cybersecurity & Infrastructure Security Agency (CISA)",
                "title": "Alert (AA21-356A) Mitigating Log4Shell and Other Log4j-Related Vulnerabilities",
                "url": "https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-356a",
                "retrieved_date": "2026-09-17 (Authoritative Cached Dataset)",
                "fields_used": ["Recommended Mitigations", "Attack Chains", "Detection Guidelines"]
            },
            {
                "organization": "Apache Software Foundation",
                "title": "Apache Log4j Security Vulnerabilities Bulletin",
                "url": "https://logging.apache.org/log4j/2.x/security.html",
                "retrieved_date": "2026-09-17 (Authoritative Cached Dataset)",
                "fields_used": ["Affected Versions (2.0-beta9 to 2.14.1)", "Patch Releases (2.15.0+)"]
            },
            {
                "organization": "MITRE Corporation",
                "title": "MITRE ATT&CK Matrix for Enterprise — T1190 Exploit Public-Facing Application",
                "url": "https://attack.mitre.org/techniques/T1190/",
                "retrieved_date": "2026-09-17 (Authoritative Cached Dataset)",
                "fields_used": ["Tactics", "Techniques", "Detection Signatures"]
            }
        ],
        "default_affected_asset": {
            "name": "Payment Application Server (Cluster Primary)",
            "business_service": "Payment Processing & Settlement",
            "asset_type": "APPLICATION_SERVER",
            "environment": "Production Banking DMZ",
            "default_criticality": 88.0
        }
    },

    # Future CISA KEV extensible entries (catalog ready)
    "CVE-2023-34362": {
        "id": "scenario-moveit",
        "cve_id": "CVE-2023-34362",
        "name": "MOVEit Transfer — SQL Injection Remote Code Execution",
        "short_name": "MOVEit Transfer",
        "status": "CATALOG_READY",
        "overview": "A critical SQL injection vulnerability in Progress Software MOVEit Transfer that allowed unauthenticated access and data exfiltration.",
        "threat_metadata": {
            "cve": {"value": "CVE-2023-34362", "source_type": SourceType.REAL_PUBLIC_DATA.value, "source": "NVD (NIST)", "source_url": "https://nvd.nist.gov/vuln/detail/CVE-2023-34362"},
            "cvss_v3_score": {"value": 9.8, "severity": "CRITICAL", "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "source_type": SourceType.REAL_PUBLIC_DATA.value, "source": "NVD (NIST)", "source_url": "https://nvd.nist.gov/vuln/detail/CVE-2023-34362"},
            "known_exploitation": {"value": True, "status_label": "CISA KEV Listed", "source_type": SourceType.REAL_PUBLIC_DATA.value, "source": "CISA KEV", "source_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"}
        },
        "authoritative_sources": [
            {"organization": "NVD (NIST)", "title": "CVE-2023-34362 Detail", "url": "https://nvd.nist.gov/vuln/detail/CVE-2023-34362", "retrieved_date": "2026-09-17", "fields_used": ["CVSS 9.8"]},
            {"organization": "CISA KEV", "title": "CISA KEV Catalog", "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "retrieved_date": "2026-09-17", "fields_used": ["Active Exploitation"]}
        ],
        "default_affected_asset": {
            "name": "Enterprise Secure File Transfer Gateway",
            "business_service": "Customer File Exchange",
            "asset_type": "SERVER",
            "environment": "DMZ",
            "default_criticality": 82.0
        }
    }
}

# ==============================================================================
# SYNTHETIC ENTERPRISE DEFAULT PROFILE
# ==============================================================================

SYNTHETIC_ENTERPRISE_DEFAULT = {
    "enterprise_name": "ABC Bank — Synthetic Demonstration Environment",
    "disclaimer_label": "Synthetic demonstration environment for risk quantification",
    "disclaimer_text": "Never implied that ABC Bank is an actual historical victim. All operational figures are synthetic demonstration models for risk quantification.",
    "industry": "Commercial Retail & Digital Payments Banking",
    "country": "India",
    "currency": "INR (₹)",
    
    # Infrastructure Fleet
    "total_servers": 120,
    "internet_facing_servers": 14,
    "application_servers": 38,
    "database_servers": 12,
    "critical_assets_count": 8,
    "payment_systems_count": 4,

    # Asset Criticality Factor (0-100) — Impacts SLE, NOT Likelihood
    "asset_criticality": 88.0,
    "business_importance": 88.0,
    "data_sensitivity": 92.0,
    "revenue_dependency": 85.0,
    "regulatory_importance": 90.0,
    "downtime_tolerance_hours": 1.0,

    # Dynamic Financial Assumptions (INR)
    "revenue_per_hour": 500000.0,           # ₹5 Lakh / hr gross business revenue
    "transaction_volume_per_hour": 15000,    # UPI & Card transactions / hr
    "hourly_downtime_cost": 300000.0,        # ₹3 Lakh / hr direct operational downtime
    "incident_outage_hours": 8.0,            # 8 hours estimated core containment outage
    "incident_response_hours": 40.0,         # 40 hours external forensics & CERT triage
    "incident_response_hourly_rate": 25000.0,# ₹25,000 / hr specialized forensics rate
    "data_recovery_base_cost": 1500000.0,    # ₹15 Lakh database integrity reconstruction
    "legal_regulatory_base_cost": 2000000.0, # ₹20 Lakh statutory regulatory scrutiny base
    "business_interruption_base_cost": 2500000.0, # ₹25 Lakh customer compensation & churn base

    # Baseline Controls in Place (Before mitigation)
    "control_coverage": 55.0,                # 55% coverage
    "control_effectiveness": 60.0,           # 60% effectiveness
    "is_internet_exposed": True,
    "in_attack_path": True,
    "threat_activity_level": 92.0,           # 92/100 global adversary reconnaissance

    # Budget for optimization
    "available_security_budget": 5000000.0   # ₹50 Lakh
}

def get_scenario_catalog() -> List[Dict[str, Any]]:
    """Returns list of available real-world scenarios with key summary metadata."""
    results = []
    for cve_id, data in REAL_WORLD_SCENARIOS_CATALOG.items():
        results.append({
            "cve_id": data["cve_id"],
            "short_name": data["short_name"],
            "name": data["name"],
            "status": data["status"],
            "overview": data["overview"],
            "cvss_score": data["threat_metadata"]["cvss_v3_score"]["value"],
            "cvss_severity": data["threat_metadata"]["cvss_v3_score"]["severity"],
            "cvss_vector": data["threat_metadata"]["cvss_v3_score"]["vector"],
            "known_exploited": data["threat_metadata"]["known_exploitation"]["value"],
            "source_nvd": data["threat_metadata"]["cve"]["source"],
            "source_cisa": data["threat_metadata"]["known_exploitation"]["source"],
            "default_asset": data["default_affected_asset"]["name"],
            "default_criticality": data["default_affected_asset"]["default_criticality"]
        })
    return results

def get_scenario_by_cve(cve_id: str) -> Optional[Dict[str, Any]]:
    """Returns detailed real-world scenario metadata and sources."""
    normalized = cve_id.upper().strip()
    return REAL_WORLD_SCENARIOS_CATALOG.get(normalized)
