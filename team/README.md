# QUANTUM RISK AI — Team Work Division & Technical Ownership
## Smart India Hackathon (SIH 2026) — Final Round

**Project Title:** AI-Powered Continuous Cyber Risk Quantification and Investment Optimization Platform  
**Target Organization:** ABC Bank Ltd. (Tier-1 Scheduled Commercial Bank)  
**Team Structure:** 4 Core Engineers across Backend Architecture, Financial Mathematics, Machine Learning, and Optimization/Governance.

---

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       QUANTUM RISK AI ARCHITECTURE                                      │
├──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────┤
│         MEMBER 1         │         MEMBER 2         │         MEMBER 3         │        MEMBER 4       │
│  Backend & Core Data     │ Quantitative Risk & FAIR │  Predictive AI & Graphs  │ Optimization & CISO   │
├──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • FastAPI REST Gateway   │ • Open FAIR Methodology  │ • XGBoost Risk Forecast  │ • OR-Tools Knapsack   │
│ • SQLite/Postgres DB     │ • Single Loss Expectancy │ • Tree SHAP Attribution  │ • Prerequisite DAG    │
│ • JWT Auth & 6-Role RBAC │ • Annualized Rate (ARO)  │ • Attack Graph Analysis  │ • CISO Approval Flow  │
│ • NVD & CISA Connectors  │ • Modeled EAL (₹4.60 Cr) │ • Dijkstra Choke Points  │ • Blockchain Audit    │
│ • CSV Ingest & Export    │ • 10,000 MC Iterations   │ • MITRE ATT&CK Mapping   │ • React 19 / Vite UI  │
└──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────┘
```

---

## Member 1: Backend Architecture, Persistence & Telemetry Connectors
**Lead Engineer:** Member 1 — Backend & Core Data Architecture  
**Focus:** High-throughput async REST API, relational schema, authentication, telemetry ingestion, and truthfulness.

### Primary Responsibilities
1. **API Gateway & Middleware:** Architected the FastAPI backend with dual `/api` and `/api/v1` routing, Starlette async engine, and CORS middleware for local and enterprise deployments.
2. **Database & Data Modeling:** Designed SQLAlchemy relational models encompassing 100 enterprise assets, 500 mapped CVEs, 20 security controls, and 6 banking scenarios. Implemented zero-configuration SQLite fallback for offline evaluator environments alongside PostgreSQL support.
3. **Authentication & RBAC:** Implemented OAuth2 JWT bearer token authentication with passlib bcrypt hashing, enforcing granular access control across all 6 enterprise roles (`CISO`, `SECURITY_ANALYST`, `RISK_ANALYST`, `EXECUTIVE`, `AUDITOR`, `ADMIN`).
4. **Real-World Connector Subsystem:** Authored the `CyberSecurityConnector` abstract interface and concrete implementations for:
   - **NIST NVD API v2.0:** Live HTTP querying with resilient canonical local fallback.
   - **CISA KEV Catalog:** Real-time exploit tracking feed with cached resilience.
   - **MITRE ATT&CK Enterprise v14.1:** Kill-chain mapping for APT28, APT29, FIN7, and Lazarus.
   - **Wazuh EDR & OpenVAS GMP:** Diagnostic connectors adhering to *Connection Truthfulness* (reporting `NOT CONFIGURED` or `DEMO DATA` rather than falsely claiming `CONNECTED`).
5. **Asset CSV Lifecycle:** Built `/api/v1/assets/template-csv`, `/api/v1/assets/export-csv`, and `/api/v1/assets/import-csv` allowing organizations to upload their own infrastructure inventory and dynamically compute FAIR criticality scores.

### Owned Files & Directories
- `backend/app/main.py`
- `backend/app/core/` (`config.py`, `security.py`)
- `backend/app/database/` (`models.py`, `session.py`, `seed_data.py`)
- `backend/app/connectors/` (`base.py`, `nvd.py`, `cisa_kev.py`, `mitre_attack.py`, `wazuh.py`, `openvas.py`, `__init__.py`)
- `backend/app/api/auth.py`, `backend/app/api/assets.py`, `backend/app/api/vulnerabilities.py`, `backend/app/api/integrations.py`
- `backend/tests/test_connectors.py`, `backend/tests/test_asset_csv.py`, `backend/tests/test_auth_and_rbac.py`

### Owned Endpoints
- `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- `GET /api/v1/assets`, `POST /api/v1/assets`, `GET /api/v1/assets/{id}`, `DELETE /api/v1/assets/{id}`
- `GET /api/v1/assets/template-csv`, `GET /api/v1/assets/export-csv`, `POST /api/v1/assets/import-csv`
- `GET /api/v1/vulnerabilities`, `GET /api/v1/vulnerabilities/{id}`
- `GET /api/v1/integrations/status`, `POST /api/v1/integrations/sync/{source}`
- `GET /health`

### Judge Interview Talking Points & Deep-Dive Defense
- **Q: "Why does your system report NOT CONFIGURED for Wazuh instead of CONNECTED?"**  
  *A: "In enterprise cybersecurity, integrity is paramount. Unlike superficial demos that fake live connections, Quantum Risk AI implements connection truthfulness. Wazuh and OpenVAS require on-premise credentials and daemon ports (55000 and 9390). Because the hackathon runs without on-premise infrastructure, the platform honestly diagnoses the feed as NOT CONFIGURED and gracefully loads verified cached telemetry with explicit DEMO DATA badges."*
- **Q: "How does the CSV import handle custom organizational assets?"**  
  *A: "The ingestor reads 13 parameters including business importance, data sensitivity, revenue dependency, downtime tolerance, and regulatory importance. It runs our deterministic criticality algorithm, assigns a score from 0-100, tags the records with ORGANIZATION_DATA, and recalculates enterprise risk."*

---

## Member 2: Quantitative Cyber Risk & Financial Modeling (Open FAIR)
**Lead Engineer:** Member 2 — Risk Quantification & Financial Engineering  
**Focus:** Mathematical risk quantification, Open FAIR modeling, Monte Carlo simulations, and loss category monetization.

### Primary Responsibilities
1. **Open FAIR Risk Formulation:** Implemented the international standard Open FAIR (Factor Analysis of Information Risk - ISO/IEC 27005 compliant) quantitative loss formula:
   $$\text{Expected Annual Loss (EAL)} = \text{Single Loss Expectancy (SLE)} \times \text{Annualized Rate of Occurrence (ARO)}$$
2. **Deterministic Banking Loss Breakdown:** Structured enterprise loss modeling across 6 banking loss components:
   - *Downtime & Interruption Loss:* Hourly operational loss ($\text{Criticality} \times \text{Hourly Downtime Rate}$).
   - *Incident Response Loss:* Digital forensics and incident containment costs.
   - *Data Recovery Loss:* Reconstructing corrupted database ledgers and customer tables.
   - *Regulatory & Legal Fines:* Penalties under RBI Cyber Security Framework and Digital Personal Data Protection (DPDP) Act 2023.
   - *Business Interruption Loss:* Loss of fee income and transaction processing volumes.
   - *Reputational Damage:* Modeled customer churn and deposit attrition.
3. **10,000-Iteration Monte Carlo Simulation:** Engineered a high-performance vector simulation engine running 10,000 trials across log-normal and beta-PERT distributions to produce:
   - 10th Percentile (Optimistic exposure: ₹2.10 Cr)
   - 50th Percentile (Median exposure: ₹4.20 Cr)
   - 85th Percentile (Board Risk Tolerance: ₹5.80 Cr)
   - 95th Percentile (Extreme Tail / Cyber VaR: ₹7.90 Cr)
4. **Parametric Assumptions Panel:** Enabled CISO/CFO interactive tuning of hourly downtime costs, IR consultant rates, data recovery baselines, and legal penalties with live balance-sheet recalculation.

### Owned Files & Directories
- `backend/app/risk_engine/` (`calculator.py`, `monte_carlo.py`, `models.py`)
- `backend/app/api/risk.py`, `backend/app/api/financial.py`
- `frontend/src/pages/ExecutiveDashboard.tsx`, `frontend/src/pages/FinancialExposure.tsx`
- `frontend/src/components/MonteCarloChart.tsx`, `frontend/src/components/ModelAssumptionsPanel.tsx`
- `backend/tests/test_risk_engine.py`, `backend/tests/test_financial_and_opt.py`

### Owned Endpoints
- `GET /api/v1/risk/enterprise`, `POST /api/v1/risk/recalculate`
- `GET /api/v1/financial/exposure`, `GET /api/v1/financial/monte-carlo`, `POST /api/v1/financial/assumptions`

### Judge Interview Talking Points & Deep-Dive Defense
- **Q: "Why use quantitative financial risk (EAL in ₹) rather than qualitative heatmaps (High/Medium/Low)?"**  
  *A: "Board members and CFOs cannot make capital allocation decisions based on ambiguous 'red-amber-green' matrices. By quantifying risk into Expected Annual Loss (EAL = ₹4.60 Crore), we translate technical CVEs directly into balance-sheet exposure, allowing the CISO to justify security budgets using standard ROI and Net Present Value calculations."*
- **Q: "How did you calibrate the baseline ₹4.60 Crore EAL?"**  
  *A: "We modeled ABC Bank's core digital banking infrastructure: payment switches, core banking databases, API gateways, and branch routers. Factoring in an average hourly downtime cost of ₹3,00,000 and DPDP Act regulatory penalties for high-criticality database compromise, our 10,000-iteration Monte Carlo yields an expected mean loss of ₹4.60 Cr with an 85% Value-at-Risk of ₹5.80 Cr."*

---

## Member 3: Predictive AI, Attack Path Graphs & Threat Intelligence
**Lead Engineer:** Member 3 — Machine Learning & Adversary Modeling  
**Focus:** XGBoost future risk regression, Tree SHAP model explainability, Dijkstra attack path graph algorithms, and adversary campaign tracking.

### Primary Responsibilities
1. **Machine Learning Risk Trajectory Forecasting:** Developed a machine learning regression pipeline predicting 30-day, 60-day, and 90-day cyber exposure based on a 10-dimensional feature vector:
   - *Features:* Total CVE count, Unpatched criticals, Average CVSS score, Exploit velocity, Asset criticality density, Patch lag days, Historical incident frequency, Threat campaign intensity, Internet exposure ratio, Mean Time to Remediate (MTTR).
   - *Algorithm:* XGBoost Regressor (`n_estimators=100`, `max_depth=4`, `learning_rate=0.05`) trained on longitudinal bank telemetry.
2. **Tree SHAP Explainability:** Integrated native C++ TreeExplainer (`shap` library) computing exact Shapley values for every feature contribution. Provides the CISO with intuitive waterfall attributions explaining *why* risk will increase from 82.0 to 91.5 over 90 days if left unpatched.
3. **Attack Path Graph Analysis:** Engineered a directed graph analysis engine modeling enterprise network topologies:
   - *Nodes:* Assets and trust boundaries (DMZ Gateway -> Internal App Server -> Payment Database Crown Jewel).
   - *Edges:* Exploitable vulnerabilities (e.g. CVE-2021-44228 Log4j RCE, CVE-2020-1472 Zerologon).
   - *Algorithms:* Evaluates cumulative breach probability and identifies the critical **choke point** where a single control breaks the entire kill-chain.
4. **Adversary Campaign Profiling:** Mapped MITRE ATT&CK Enterprise v14.1 tactics and active financial threat campaigns (FIN7 Carbanak, LockBit 3.0, APT28 Fancy Bear) against bank infrastructure.

### Owned Files & Directories
- `backend/app/ml_engine/` (`predictor.py`, `shap_explainer.py`, `train.py`)
- `backend/app/api/prediction.py`, `backend/app/api/attack_paths.py`, `backend/app/api/threats.py`
- `frontend/src/pages/AIPredictions.tsx`, `frontend/src/pages/AttackPathAnalysis.tsx`, `frontend/src/pages/ThreatIntelligence.tsx`
- `frontend/src/components/SHAPAttributionChart.tsx`, `frontend/src/components/AttackGraphVisualizer.tsx`
- `backend/tests/test_prediction_and_shap.py`, `backend/tests/test_attack_paths_and_scenarios.py`

### Owned Endpoints
- `GET /api/v1/prediction/future-risk`, `POST /api/v1/prediction/retrain`
- `GET /api/v1/attack-paths/graph`, `GET /api/v1/attack-paths/choke-points`
- `GET /api/v1/threats/intel`, `GET /api/v1/scenarios`, `POST /api/v1/scenarios/simulate`

### Judge Interview Talking Points & Deep-Dive Defense
- **Q: "Why use XGBoost and Tree SHAP instead of Deep Learning or an LLM for risk prediction?"**  
  *A: "In banking cybersecurity and regulatory audits, black-box deep neural networks are unacceptable. XGBoost provides superior tabular performance on structured telemetry, and Tree SHAP offers mathematically proven, game-theoretic attribution. When the CISO asks why risk increased by 9.5 points, SHAP proves that 'Unpatched Criticals' contributed +5.2 points and 'Patch Lag' added +2.8 points."*
- **Q: "How does the attack path engine identify the choke point?"**  
  *A: "The engine builds a directed acyclic graph from external ingress to the crown jewel database. By calculating edge traversal weights ($P(\text{Exploit}) \times \text{Impact}$), Dijkstra's algorithm identifies the minimum-cost exploit chain. The choke point is the vertex appearing on 100% of critical attack paths—in ABC Bank's topology, patching the Payment Gateway eliminates reachability to the internal database."*

---

## Member 4: Mathematical Investment Optimization, CISO Governance & Blockchain Audit
**Lead Engineer:** Member 4 — Optimization, Governance & Frontend Systems  
**Focus:** Google OR-Tools SCIP Mixed-Integer Knapsack optimization, CISO approval workflows, Hyperledger Fabric/SHA-256 cryptographic audit ledger, and full-stack UI orchestration.

### Primary Responsibilities
1. **Mathematical Optimization Engine (Google OR-Tools):** Formulated and solved the cyber investment optimization problem using SCIP Mixed-Integer Linear Programming (MILP):
   - *Objective Function:* Maximize total modeled risk reduction:
     $$\max \sum_{i=1}^{N} R_i \cdot x_i \quad \text{subject to} \quad \sum_{i=1}^{N} C_i \cdot x_i \le B$$
   - *Prerequisite Control DAG Constraints:* Control $j$ cannot be selected unless prerequisite control $k$ is active ($x_j \le x_k$, e.g., Network Segmentation before Micro-isolation).
   - *Diminishing Returns & Budget Slack:* Solves the knapsack problem to identify optimal allocation (₹85L of ₹1.00 Cr budget yields ₹2.60 Cr risk reduction, achieving an efficiency ratio of 3.06x with 15% budget reserve).
2. **CISO Approval & Governance Workflow:** Built the formal executive decision module allowing CISOs to review the mathematical recommendation, input budget constraints, and execute immutable approval or modification.
3. **Blockchain Audit Layer:** Designed a dual-layer cryptographic ledger:
   - *Decentralized Channel:* Hyperledger Fabric v2.5 channel support.
   - *Local Immutable Fallback:* Genesis-to-latest SHA-256 Merkle-linked chain recording block hashes, cryptographic nonces, and CISO digital signatures.
   - *Tamper Sandbox & Auto-Healing:* Interactive sandbox that simulates malicious database tampering, triggers real-time hash integrity mismatch detection, and executes automatic cryptographic ledger restoration.
4. **Enterprise UI Design System:** Implemented a modern, responsive React 19 + TypeScript interface with TailwindCSS dark mode, glassmorphism, responsive metrics, and explicit Data Origin tagging across all pages.

### Owned Files & Directories
- `backend/app/optimization_engine/` (`solver.py`, `controls.py`)
- `backend/app/blockchain/` (`ledger.py`, `fabric_client.py`)
- `backend/app/api/optimization.py`, `backend/app/api/ciso.py`, `backend/app/api/blockchain.py`, `backend/app/api/demo.py`
- `frontend/src/pages/InvestmentOptimizer.tsx`, `frontend/src/pages/CISOApproval.tsx`, `frontend/src/pages/BlockchainAudit.tsx`, `frontend/src/pages/SystemStatusPage.tsx`
- `backend/tests/test_ciso_approval_and_compliance.py`, `backend/tests/test_full_sih_readiness.py`, `backend/tests/run_evidence_verification.py`

### Owned Endpoints
- `POST /api/v1/optimization/solve`, `GET /api/v1/optimization/stress-test`, `GET /api/v1/optimization/controls`
- `POST /api/v1/ciso/submit-decision`, `GET /api/v1/ciso/history`
- `GET /api/v1/blockchain/ledger`, `POST /api/v1/blockchain/verify`, `POST /api/v1/blockchain/tamper-test`, `POST /api/v1/blockchain/restore`
- `POST /api/v1/demo/reset`

### Judge Interview Talking Points & Deep-Dive Defense
- **Q: "Why doesn't the optimizer spend the entire ₹1.00 Crore budget?"**  
  *A: "This is the power of mathematical integer programming over naive heuristics. Heuristic tools blindly spend until the budget runs out. Google OR-Tools evaluates the marginal risk reduction per rupee spent. At ₹85 Lakh, the 5 highest-leverage controls (Patching, MFA, EDR, Segmentation, Immutable Backup) reduce risk by ₹2.60 Crore (3.06x ROI). Any additional control has diminishing returns. Leaving ₹15 Lakh as an unspent contingency reserve provides superior fiduciary responsibility."*
- **Q: "How does the blockchain audit layer prevent an insider from tampering with the approval record?"**  
  *A: "Each block contains the SHA-256 hash of the previous block, a UTC timestamp, block index, and CISO approval signature. In our live Tamper Sandbox demo, we alter a stored database record. The ledger instantly flags Block #3 as corrupted because the recomputed hash fails to match the chain pointer. The system then automatically restores the corrupted block from the cryptographic hash tree."*

---

## Team Integration Matrix & Cross-Functional Workflows

| Step in Platform Pipeline | Primary Owner | Contributing Owner | Integration Output |
|:---|:---:|:---:|:---|
| **1. Data Ingestion & Connectors** | Member 1 | Member 3 | Normalized Asset & CVE records in DB |
| **2. Risk Identification & Scoring** | Member 2 | Member 1 | Individual asset risk & critical CVE ranking |
| **3. Financial Exposure (EAL)** | Member 2 | Member 4 | Baseline EAL: ₹4.60 Cr across 6 loss categories |
| **4. Predictive Risk Forecasting** | Member 3 | Member 2 | 30/60/90-day risk curve & SHAP explanations |
| **5. Attack Path & Choke Points** | Member 3 | Member 1 | Dijkstra exploit graph & critical choke point |
| **6. Investment Knapsack Solve** | Member 4 | Member 2 | ₹85L optimal portfolio yielding ₹2.60 Cr reduction |
| **7. CISO Approval & Decision** | Member 4 | Member 2 | Formal signoff recorded in state |
| **8. Blockchain Notarization** | Member 4 | Member 1 | SHA-256 block added to immutable audit ledger |
| **9. Full-Stack UI Observability** | Member 4 | All Members | 12-subsystem health dashboard with origin tags |

---

## 18-Step SIH Evaluator Demonstration Script & Role Assignments

| Step # | Demonstration Action | Primary Speaker | Key Feature Highlighted |
|:---:|:---|:---:|:---|
| **1** | System Telemetry & Status | **Member 1** | Connection truthfulness across all 12 subsystems |
| **2** | Login & 6-Role RBAC Demo | **Member 1** | CISO, Analyst, Risk, Executive, Auditor, Admin roles |
| **3** | Asset Inventory & CSV Import | **Member 1** | Ingesting custom enterprise CSV + dynamic criticality |
| **4** | Vulnerability Registry & CISA KEV | **Member 1** | Live CISA Known Exploited Vulnerability filter (6 active) |
| **5** | Executive Dashboard Baseline | **Member 2** | Enterprise Risk 82.0 (CRITICAL) & ₹4.60 Cr EAL |
| **6** | Financial Exposure Monetization | **Member 2** | FAIR methodology: Downtime, IR, Legal, Reputational losses |
| **7** | 10,000-Trial Monte Carlo Sim | **Member 2** | 10th, 50th, 85th, and 95th percentile confidence curves |
| **8** | Parametric Assumptions Tuning | **Member 2** | Live sensitivity testing on hourly downtime rates |
| **9** | ML 30/60/90-Day Risk Forecast | **Member 3** | XGBoost trajectory predicting rise from 82.0 to 91.5 |
| **10** | Tree SHAP Attribution Waterfall | **Member 3** | Mathematical attribution (+5.2 pts from unpatched CVEs) |
| **11** | Attack Path Graph Visualization | **Member 3** | DMZ -> App Server -> Crown Jewel Payment DB |
| **12** | Choke Point Identification | **Member 3** | Single control breaking 100% of attack paths |
| **13** | Google OR-Tools Knapsack Solve | **Member 4** | ₹1.00 Cr budget -> ₹85L optimal spend (3.06x ROI) |
| **14** | Prerequisite Control DAG Rules | **Member 4** | Control dependencies and diminishing returns |
| **15** | CISO Executive Approval | **Member 4** | Formal decision submission with post-mitigation risk 38.0 |
| **16** | Blockchain Ledger Verification | **Member 4** | Cryptographic hash verification of all 6 blocks |
| **17** | Tamper Detection Sandbox | **Member 4** | Corrupting block hash -> instant mismatch alert |
| **18** | Self-Healing Auto-Restoration | **Member 4** | Automatic cryptographic recovery of audit trail |
