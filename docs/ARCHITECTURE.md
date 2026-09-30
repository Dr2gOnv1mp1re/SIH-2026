# Quantum Risk AI — System Architecture & Component Design
## Technical Reference Manual (SIH 2026 Round 2)

### 1. Executive Summary & Core Pipeline
Quantum Risk AI is an enterprise-grade cyber risk quantification, predictive forecasting, and mathematical investment optimization platform designed for regulated financial institutions (Tier-1 Scheduled Commercial Banks). The system transforms raw technical vulnerability telemetry into defensible balance-sheet financial exposure (₹ Expected Annual Loss) and computes mathematically optimal control portfolios.

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 END-TO-END PIPELINE                                      │
└──────────────────────────────────────────────────────────────────────────────────────────┘
 REAL CYBERSECURITY DATA   (NIST NVD 2.0 • CISA KEV • MITRE ATT&CK • Wazuh • OpenVAS • CSV)
         ↓
 DATA NORMALIZATION        (Canonical Schema: Asset, Vulnerability, Threat Actor, Control)
         ↓
 RISK IDENTIFICATION       (Asset Criticality [0-100] • CVSS v3.1 Base • Exploit Multiplier)
         ↓
 FINANCIAL RISK (FAIR)     (Open FAIR: EAL = SLE × ARO • 6 Banking Loss Components • Monte Carlo)
         ↓
 PREDICTIVE AI             (XGBoost Regressor • 30/60/90-Day Trajectory Forecast)
         ↓
 SHAP EXPLAINABILITY       (Native C++ TreeExplainer • Feature Importance Attribution Waterfall)
         ↓
 ATTACK-PATH ANALYSIS      (Directed Acyclic Graph • Edge Weights • Choke Point Detection)
         ↓
 CONTROL RECOMMENDATION    (20 Controls across IAM, Network, Endpoint, Backup, AppSec)
         ↓
 OR-TOOLS OPTIMIZATION     (SCIP Mixed-Integer Linear Programming • 0-1 Knapsack with DAG Constraints)
         ↓
 CISO DECISION GOVERNANCE  (Human-in-the-Loop Signoff • Executive Risk Tolerance Enforcement)
         ↓
 BLOCKCHAIN AUDIT LEDGER   (Hyperledger Fabric v2.5 / SHA-256 Merkle Chain • Tamper Detection)
```

---

### 2. Multi-Tier High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               PRESENTATION TIER (FRONTEND)                               │
│  React 19 + TypeScript + Vite + Tailwind CSS + Lucide Icons + Recharts Data Viz          │
│  • Executive CISO Dashboard        • Attack Path Visualizer   • CISO Approval Console   │
│  • Asset Inventory & CSV Lifecycle • Threat Intel & MITRE     • Blockchain Audit Ledger │
│  • Financial Risk (Monte Carlo)    • Investment Optimizer     • System Observability    │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ HTTP/REST (JSON & CSV)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                APPLICATION TIER (FASTAPI)                                │
│  FastAPI Asynchronous Gateway (Starlette Engine) • Dual Routing: /api & /api/v1           │
│  • OAuth2 JWT Authentication & Passlib Bcrypt Hashing                                   │
│  • Granular 6-Role Role-Based Access Control (RBAC)                                      │
│  • Pydantic Request/Response Validation & OpenAPI 3.1 Spec                              │
├─────────────────────────────────────────────┬────────────────────────────────────────────┤
│           CORE COMPUTATIONAL ENGINES        │            INTEGRATION CONNECTORS          │
│  • Open FAIR Quantitative Risk Engine       │  • NIST NVD 2.0 (Live REST + Cache)        │
│  • 10,000-Trial Vectorized Monte Carlo      │  • CISA KEV Exploit Feed (Live + Cache)    │
│  • XGBoost 90-Day Trajectory Forecaster     │  • MITRE ATT&CK Enterprise v14.1 Mapping   │
│  • C++ Tree SHAP Attribution Explainer      │  • Wazuh EDR & OpenVAS GMP Diagnostics    │
│  • Dijkstra Directed Graph Attack Engine    │  • RFC 4180 CSV Ingest & Export Processor  │
│  • Google OR-Tools SCIP Mixed-Integer Solver│                                            │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ SQLAlchemy ORM (Sync & Async)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                DATA & AUDIT TIER (PERSISTENCE)                           │
│  • Primary Relational Database: SQLite (Zero-Config Evaluator) / PostgreSQL Driver       │
│  • Cryptographic Audit Ledger: Hyperledger Fabric v2.5 Channel + Local SHA-256 Chain    │
│  • Local Telemetry Cache: Canonical NVD, CISA KEV, and MITRE ATT&CK Threat Signatures    │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Component Breakdown & Responsibilities

#### 3.1 API Gateway & Routing (`backend/app/main.py`)
- Configures FastAPI with lifespan management, CORS for cross-origin frontend communication, exception handlers, and dual-mount routers (`/api` and `/api/v1`).
- Mounts specialized domain sub-routers:
  - `/auth`: Login, JWT issuance, identity profiling.
  - `/assets`: Infrastructure inventory, CRUD, CSV template/import/export.
  - `/vulnerabilities`: Discovered CVE catalog, CISA KEV filters.
  - `/risk`: Enterprise risk scoring, weight decomposition.
  - `/financial`: Open FAIR monetization, 10,000-trial Monte Carlo.
  - `/prediction`: XGBoost forecasting, Tree SHAP attributions.
  - `/attack-paths`: Graph traversal, breach probabilities, choke points.
  - `/optimization`: Google OR-Tools SCIP Knapsack optimization.
  - `/ciso`: Executive authorization, history, governance.
  - `/blockchain`: Cryptographic ledger, tamper detection sandbox, auto-restoration.
  - `/integrations`: Telemetry connectors and live status observability.
  - `/demo`: 18-step master demonstration state machine.

#### 3.2 Relational Data Layer (`backend/app/database/`)
- Modeled with SQLAlchemy declarative base (`models.py`):
  - `Organization`: Multi-tenant boundary.
  - `User`: Identity with 6 distinct roles.
  - `Asset`: 100 enterprise assets with 13 criticality metrics.
  - `Vulnerability`: 500 discovered CVEs mapped to affected assets.
  - `SecurityControl`: 20 defensive mitigations with cost and reduction values.
  - `AttackPath`: Directed graph hops and breach probabilities.
  - `AuditLog` & `BlockchainBlock`: Cryptographic immutable proof records.

#### 3.3 Connection Truthfulness Engine (`backend/app/connectors/`)
- Enforces absolute honesty regarding telemetry feeds.
- Connectors derive from abstract `CyberSecurityConnector`:
  - `connect()` -> Tests transport layer connectivity.
  - `health_check()` -> Emits verified status (`CONNECTED`, `NOT CONFIGURED`, `DEMO DATA`, `ERROR`).
  - `fetch()` -> Retrieves raw telemetry.
  - `normalize()` -> Maps payloads into canonical schema.
  - `sync_pipeline()` -> Ingests and caches records.
