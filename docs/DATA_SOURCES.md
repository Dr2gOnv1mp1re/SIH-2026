# Quantum Risk AI — External Telemetry, Data Ingestion & Truthfulness
## Public Threat Feeds, EDR Integrations, and Explicit Origin Tagging

### 1. Architectural Philosophy: Connection Truthfulness
In real-world cybersecurity, asserting false connections undermines trust and misleads leadership. Quantum Risk AI enforces a strict policy of **Connection Truthfulness**:
- If an on-premise security scanner or EDR manager (e.g. Wazuh, OpenVAS) is unreachable or lacks production credentials, the system **NEVER** reports `CONNECTED`.
- Instead, it transparently displays `NOT CONFIGURED` or `DEMO DATA` with diagnostic messages, while falling back to validated local telemetry.

---

### 2. Supported Data Sources & Integrations

```
┌───────────────────────────────────────┬──────────────────────┬───────────────────────────────┐
│ Feed / Source                         │ Primary Protocol     │ Truthful Status in Platform   │
├───────────────────────────────────────┼──────────────────────┼───────────────────────────────┤
│ NIST National Vulnerability DB (NVD)  │ HTTPS REST API v2.0  │ CONNECTED (Live + Cache)      │
│ CISA Known Exploited Vulns (KEV)      │ HTTPS JSON Catalog   │ CONNECTED (Live + Cache)      │
│ MITRE ATT&CK Enterprise v14.1         │ Structured Taxonomy  │ CONNECTED (Internal Graph)    │
│ Wazuh Host EDR / SIEM                 │ REST API (Port 55000)│ NOT CONFIGURED / DEMO DATA    │
│ OpenVAS / Greenbone Vulnerability Mgr │ GMP (Port 9390)      │ NOT CONFIGURED / DEMO DATA    │
│ Enterprise Asset Ingest               │ RFC 4180 CSV Ingest  │ ORGANIZATION-PROVIDED DATA    │
└───────────────────────────────────────┴──────────────────────┴───────────────────────────────┘
```

---

### 3. Detailed Feed Specifications

#### 3.1 NIST National Vulnerability Database (NVD 2.0)
- **Endpoint:** `https://services.nvd.nist.gov/rest/json/cves/2.0`
- **Purpose:** Ingestion of discovered CVE identifiers, CVSS v3.1 base metrics, attack vectors, and Common Platform Enumerations (CPE).
- **Fallback Strategy:** If NIST API experiences rate limiting (HTTP 429) or network interruption, the connector gracefully fails over to the verified local canonical NVD cache without disrupting risk calculations.

#### 3.2 CISA Known Exploited Vulnerabilities (KEV)
- **Endpoint:** `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`
- **Purpose:** Identifies vulnerabilities with documented in-the-wild weaponization. Active CISA KEV presence applies an immediate threat multiplier (1.4x) to the affected asset's breach probability.
- **Filtering:** High-priority visual filter in the Vulnerability Registry isolating active weaponized CVEs (Log4j, Spring4Shell, Fortinet RCE, Zerologon).

#### 3.3 MITRE ATT&CK Enterprise Framework (v14.1)
- **Structure:** Matrix of Tactics (TA0001 Initial Access through TA0010 Exfiltration) and Techniques (T1190, T1068, T1021, T1567).
- **Attribution:** Maps specific CVEs to active financial sector threat actors:
  - *FIN7 (Carbanak Financial Syndicate):* Public-facing exploit delivery (T1190).
  - *LockBit 3.0 Ransomware:* Double extortion and data encryption (T1486).
  - *APT28 (Fancy Bear):* Advanced persistent lateral movement.

#### 3.4 Wazuh EDR & OpenVAS GMP Connectors
- **Implementation:** Real network probes testing TCP sockets and HTTPS endpoints.
- **Truthful Status:** Because the SIH hackathon evaluation takes place outside of ABC Bank's private data center, these feeds display `NOT CONFIGURED: On-premise endpoint not configured in .env. Operating in DEMO DATA mode.`

---

### 4. Explicit Data Origin Tagging
To ensure complete transparency, every major page in the Quantum Risk AI UI displays an explicit data provenance tag:
- **Assets Page:** `ORIGIN: SYNTHETIC DEMO DATA (ABC BANK)` or `ORIGIN: ORGANIZATION-PROVIDED DATA` (when imported via CSV).
- **Vulnerabilities Page:** `ORIGIN: REAL PUBLIC INTELLIGENCE (NIST NVD & CISA KEV)`
- **Threat Intelligence:** `ORIGIN: REAL PUBLIC INTELLIGENCE (MITRE ATT&CK v14.1)`
- **Financial Risk:** `ORIGIN: MODELED FINANCIAL DATA (FAIR ENGINE)`
- **Future Predictions:** `ORIGIN: AI-PREDICTED RISK TRAJECTORY (XGBOOST + SHAP)`
- **Investment Optimizer:** `ORIGIN: MATHEMATICALLY OPTIMIZED ALLOCATION (GOOGLE OR-TOOLS)`
- **Blockchain Audit:** `ORIGIN: CRYPTOGRAPHIC AUDIT EVIDENCE (FABRIC / SHA-256)`
