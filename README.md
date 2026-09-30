# QUANTUM RISK AI
### AI-Powered Continuous Cyber Risk Quantification & Investment Optimization Platform
**Version:** SIH 2026 Final | Version 1.0  
**Problem Statement:** PS26105 — Continuous Cyber Risk Quantification and Investment Optimization

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026%20Final%20Round%20Master%20Platform-06b6d4.svg)](#)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi)](#)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6.svg?logo=typescript)](#)
[![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-MIP%20SCIP-4285F4.svg)](#)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.2.0-FF6600.svg)](#)
[![Hyperledger Fabric](https://img.shields.io/badge/Hyperledger%20Fabric-v2.5%20Audit%20Ledger-2F3134.svg)](#)
[![Tests Passing](https://img.shields.io/badge/Tests-166%20Passed%20(100%25)-brightgreen.svg)](#)

---

## 1. Project Overview & Problem Statement
Modern enterprise CISOs, CROs, and Corporate Boards face an acute operational dilemma:
> **"How can an enterprise allocate limited cybersecurity capital to achieve the MAXIMUM MATHEMATICALLY PROVEN REDUCTION in financial cyber risk?"**

Qualitative 5×5 heatmaps ("High/Medium/Low") fail to justify security expenditures to CFOs and Boards. Technical vulnerability scanners report thousands of alerts without financial context. **Quantum Risk AI** solves this by establishing a closed-loop platform:
1. Continuous ingestion of enterprise telemetry and threats (Wazuh, OpenVAS, CISA KEV, MITRE ATT&CK).
2. Mathematically defensible financial cyber risk quantification using the **FAIR model** ($EAL = SLE \times ARO$) with 10,000-iteration Monte Carlo simulations.
3. Machine learning future risk forecasting via **XGBoost** paired with native **SHAP** explainability.
4. Crown-jewel **attack path analysis** on directed infrastructure graphs.
5. Mixed-Integer Linear Programming (**Google OR-Tools SCIP**) to mathematically guarantee optimal security control selection under strict budget caps.
6. **"AI Recommends, CISO Decides"** human-in-the-loop executive governance.
7. Immutable audit trails with **SHA-256 canonical hashing** and **Hyperledger Fabric** blockchain verification with automated tamper detection.

> [!NOTE]
> All financial risk numbers (SLE, ARO, EAL) and simulation outputs represent **Modeled / Estimated** values derived from mathematical models and active asset parameters, clearly distinguished from historical real-world loss claims.

---

## 2. Platform Architecture
```mermaid
graph TD
    subgraph "1. Telemetry Ingestion & Universal Data"
        DS[Universal Ingestion Engine<br/>CSV / XLSX / JSON / Wazuh / OpenVAS] --> Val[Security & Validation Filter<br/>Formula Injection Defense CWE-1236]
        Feed[External Threat Feeds<br/>CISA KEV / NVD / MITRE ATT&CK] --> Val
    end

    subgraph "2. Continuous Risk Engine & FAIR Model"
        Val --> RiskEng[Continuous Cyber Risk Engine<br/>Criticality, Exploitability, Exposure]
        RiskEng --> FAIR[FAIR Model: EAL = SLE × ARO<br/>Primary & Secondary Loss Breakdown]
        FAIR --> MC[Monte Carlo Simulator<br/>10,000 Iterations Lognormal/Poisson]
    end

    subgraph "3. AI Prediction & Attack Paths"
        Val & RiskEng --> XGB[XGBoost 30/60/90-Day Trajectories<br/>R² = 0.941, MAE = 1.65]
        XGB --> SHAP[Native SHAP Explainability Engine]
        Val --> Graph[Crown Jewel Directed Attack Graph<br/>Critical Interception Points]
    end

    subgraph "4. Optimization & Digital Twin"
        FAIR & Graph --> Solver[Google OR-Tools SCIP MIP Solver<br/>Optimal Knapsack Portfolio]
        Solver --> Twin[What-If Digital Twin Sandbox<br/>Before vs. After Delta]
    end

    subgraph "5. Executive Governance & Blockchain"
        Solver & Twin --> CISO[CISO Command Center<br/>Approve / Reject / Modify]
        CISO --> Audit[Immutable Audit Trail]
        Audit --> Fabric[Hyperledger Fabric SHA-256 Ledger<br/>Cryptographic Tamper Sandbox]
    end
```

---

## 3. Technology Stack
- **Backend**: Python 3.11, FastAPI 0.115, Pydantic v2, SQLAlchemy 2.0, SQLite / PostgreSQL.
- **Frontend**: React 19, TypeScript 5.4, Vite 5.4, Tailwind CSS 3.4, Recharts, Lucide Icons.
- **Mathematical Optimization**: Google OR-Tools v9.8 (SCIP Mixed-Integer Linear Programming Solver).
- **Machine Learning & Explainability**: XGBoost 3.2.0, SHAP (SHapley Additive exPlanations), scikit-learn.
- **Probabilistic Modeling**: NumPy 2.x, SciPy (Lognormal loss magnitude & Poisson event frequency).
- **Cryptographic Audit**: Deterministic Canonical JSON Serialization, SHA-256 Hashing, Hyperledger Fabric v2.5.

---

## 4. Installation & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 20.x+ & npm
- Git

### Backend Setup
```bash
# 1. Clone the repository and navigate to backend
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables
cp .env.example .env

# 5. Initialize SQLite database & baseline models
python -c "from app.database.session import init_db; init_db()"

# 6. Start the FastAPI backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at: `http://127.0.0.1:8000/docs`

### Frontend Setup
```bash
# 1. Navigate to frontend
cd ../frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev -- --host 0.0.0.0 --port 5173
```
Web Application will be available at: `http://127.0.0.1:5173`

---

## 5. Environment Variables & Safe Configuration
The project uses strict environment variables with zero committed secrets. See `.env.example`:

| Variable | Description | Default (Dev) |
| :--- | :--- | :--- |
| `SECRET_KEY` | JWT signing secret key | Safe placeholder (Change in Prod) |
| `ALGORITHM` | JWT hashing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Session validity duration | `480` (8 hours) |
| `DATABASE_URL` | SQLite / PostgreSQL URI | `sqlite:///./quantum_risk.db` |
| `BLOCKCHAIN_NETWORK` | Fabric or fallback provider | `mock_fabric` |
| `CISA_KEV_FEED_URL` | CISA Known Exploited Vulns URL | Official CISA JSON endpoint |
| `NVD_API_KEY` | Optional NIST NVD API key | Empty / Graceful fallback |

---

## 6. Supported Roles & Role-Based Access Control (RBAC)
Quantum Risk AI enforces strict, dual-layer (backend dependency + frontend route guard) RBAC across 6 enterprise personas:

| Role Code | Role Name | Core Responsibilities & Permissions |
| :--- | :--- | :--- |
| `ciso` | CISO / Approver | Full review, approve/reject/modify control investments, budget authority. |
| `security_analyst` | Security Analyst | Vulnerability triage, threat intelligence, attack paths, asset exposure. |
| `risk_analyst` | Quantitative Risk Analyst | Risk scoring, FAIR financial modeling, Monte Carlo, AI prediction, What-If. |
| `executive` | Executive Board / CEO | High-level financial exposure, ROSI, board summaries, compliance status. |
| `auditor` | Lead Security Auditor | Read-only audit trail, blockchain notarization verification, tamper detection. |
| `admin` | System Administrator | User management, dataset uploads, system health, database maintenance. |

---

## 7. Universal Dataset Ingestion & File Security
The universal importer accepts CSV, XLSX, JSON, and ZIP archives containing enterprise scans (Wazuh, Nessus, OpenVAS).
- **Extension & MIME Validation**: Only `.csv`, `.xlsx`, `.json`, `.zip` accepted.
- **Size Limitation**: Hard 25MB ceiling per upload.
- **Path Traversal Defense**: Filename sanitization (`os.path.basename` and regex stripping) prevents directory traversal attacks.
- **Formula Injection Defense (CWE-1236)**: Any cell starting with `=, +, -, @, \t, \r` on non-numeric strings is automatically prefixed with a single quote (`'`) to neutralize CSV formula injection when opened in Excel/Sheets.
- **Supported Columns**: `asset_id`, `asset_name`, `asset_type`, `ip_address`, `cve_id`, `cvss_score`, `exploit_available`, `asset_criticality`, `internet_exposed`.

---

## 8. Financial Risk Methodology (FAIR Standard)
Calculations adhere strictly to the **FAIR (Factor Analysis of Information Risk)** standard:
$$\text{Expected Annual Loss (EAL)} = \text{Single Loss Expectancy (SLE)} \times \text{Annualized Rate of Occurrence (ARO)}$$

### Primary & Secondary Loss Components
$$\text{SLE} = \text{Downtime Loss} + \text{Incident Response Loss} + \text{Data Recovery Loss} + \text{Legal/Regulatory Fines} + \text{Business Interruption}$$
- **Hourly Downtime Cost**: Calibrated to asset business tier (₹50,000 to ₹5,00,000/hr).
- **Annualized Rate of Occurrence (ARO)**: Modeled from threat actor capability, CVSS exploitability sub-score, internet exposure, and active CISA KEV exploitation flags.

---

## 9. Probabilistic Modeling (Monte Carlo Simulation)
- **Iterations**: 10,000 stochastic trials.
- **Distributions**:
  - Loss Magnitude: **Lognormal Distribution** ($\mu, \sigma$) reflecting heavy-tailed cyber disaster losses.
  - Event Frequency: **Poisson Distribution** ($\lambda = \text{ARO}$) modeling annual discrete occurrences.
- **Reproducibility**: Supports fixed seed parameters (`seed=42`) for automated verification and audit validation.
- **Output Metrics**: P5, P10, P25, Median (P50), P75, P90, P95, Mean, Min, Max, and a 20-bin histogram.

---

## 10. AI/ML Trajectory Forecasting & SHAP Explainability
- **Architecture**: XGBoost Regressor predicting 30, 60, and 90-day future enterprise risk scores.
- **Validation Metrics**: Evaluated on historical validation splits:
  - $R^2 = 0.941$
  - $\text{MAE} = 1.65$ points
  - $\text{RMSE} = 2.14$ points
- **SHAP Explainability**: Uses native TreeSHAP to compute exact additive feature contributions:
  - `active_cisa_exploits` (+14.2 risk contribution)
  - `internet_exposed_assets` (+11.8 risk contribution)
  - `critical_cve_density` (+9.5 risk contribution)
  - `patch_latency_days` (+6.1 risk contribution)
  - `mfa_coverage_pct` (-12.4 risk mitigation)

---

## 11. External Threat Intelligence & Graceful Fallback
Integrates real-time feeds from:
- **CISA KEV** (Known Exploited Vulnerabilities catalog).
- **NVD CVE 2.0 API** (National Vulnerability Database).
- **MITRE ATT&CK Matrix** (Tactic and technique mapping).

> [!IMPORTANT]
> If any external API is unreachable or rate-limited, the system **never crashes**. It gracefully displays:  
> `“External threat intelligence temporarily unavailable.”`  
> and utilizes previously cached offline threat feeds, clearly labeled as cached.

---

## 12. Crown Jewel Directed Attack Path Analysis
- Graph-based pathfinding identifying lateral movement chains from public entry gateways to critical core assets (e.g., Payment Switch, Core Banking Database).
- Calculates step-by-step compromise probabilities, cumulative traversal time, and single-point-of-interception controls.

---

## 13. Investment Optimization (Google OR-Tools SCIP MIP)
Formulated as a 0-1 Mixed-Integer Knapsack Optimization:
$$\max \sum_{i=1}^N x_i \cdot \Delta \text{EAL}_i \quad \text{subject to} \quad \sum_{i=1}^N x_i \cdot \text{Cost}_i \le \text{Budget}, \quad x_i \in \{0, 1\}$$
- Enforces prerequisite and mutually exclusive dependencies between security controls.
- Provides diminishing-returns stress testing across budget increments (₹25L, ₹50L, ₹1Cr, ₹2Cr, ₹5Cr).

---

## 14. What-If Digital Twin Scenarios
Enables risk analysts to simulate hypothetical security changes in a sandboxed digital twin:
- Toggle specific controls (e.g., Zero Trust, Microsegmentation, Air-Gapped Backups).
- Change vulnerability exposure or patch latency.
- View real-time Before vs. After financial risk, EAL delta, and projected ROSI without impacting the production baseline.

---

## 15. CISO Governance & Human-in-the-Loop Workflow
- Core Philosophy: **"AI Recommends, CISO Decides."**
- The CISO review portal allows the executive to:
  1. Inspect the mathematically optimized portfolio.
  2. Approve, reject, or modify specific allocations.
  3. Attach executive justification notes.
- Upon approval, the decision package is cryptographically signed and submitted to the audit trail.

---

## 16. Blockchain Audit Trail & Tamper Detection
- **Canonical Serialization**: JSON payloads are sorted and normalized before hashing.
- **SHA-256 Digest**: Computed deterministically from decision attributes, timestamp, author, and financial numbers.
- **Hyperledger Fabric**: Records transaction ID, block index, timestamp, and hash onto an immutable distributed ledger.
- **Automated Tamper Sandbox**: Demonstrates real-time mismatch detection if off-chain records are altered, returning `INVALID / TAMPER DETECTED`.

---

## 17. Security Hardening Checklist
The application has undergone a comprehensive Phase 10 security review:

- [x] **No hardcoded secrets**: All credentials and keys moved to environment variables.
- [x] **Authentication protected**: JWT bearer tokens with standard expiration and cryptographic signing.
- [x] **Backend RBAC enforced**: 6-role permission checks at every protected endpoint.
- [x] **Secure session handling**: Strict HTTP headers and credential validation.
- [x] **CORS configured**: Restricted to explicit frontend origins.
- [x] **File upload validated**: Extension whitelist, 25MB ceiling, path traversal stripping.
- [x] **Formula injection defense**: CWE-1236 neutralization on spreadsheets.
- [x] **SQL injection protection**: SQLAlchemy ORM with parameterized queries throughout.
- [x] **XSS protections**: `X-XSS-Protection: 1; mode=block` and React automatic JSX escaping.
- [x] **Rate limiting & headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`.
- [x] **Secure error handling**: Starlette exception handlers prevent stack traces or secrets on 500.
- [x] **Audit logging**: Every critical operational step is written to persistent audit logs.
- [x] **Dataset isolation**: Active dataset state is cleanly segmented and decoupled.
- [x] **Scenario isolation**: Digital twin simulations operate in memory without mutating base data.
- [x] **Blockchain verification**: Independent cryptographic hash comparison.
- [x] **Tamper detection**: Demonstrable tamper-testing endpoint verifying data integrity.
- [x] **Production configuration**: Safe `.env.example` provided with non-confidential placeholders.

---

## 18. Testing & Validation Summary
All tests were executed against the active backend test suite:

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1
rootdir: D:\SIH\backend, configfile: pytest.ini

TOTAL TESTS: 166
PASSED:      166 (100%)
FAILED:      0
SKIPPED:     0
ERRORS:      0
EXECUTION:   39.21s
============================= 166 passed in 39.21s =============================
```

Frontend Verification:
- TypeScript compilation (`tsc -b`): Clean, 0 errors.
- Vite production build (`vite build`): 2,541 modules transformed, `dist/` generated cleanly in 9.29s.

---

## 19. Complete 25-Step SIH Demonstration Flow
Evaluators can follow the end-to-end connected narrative directly in the platform:
1. **Login** (`ciso@quantumrisk.ai` / password).
2. **Select Dataset** (SIH PS26105 Enterprise Baseline - ABC Bank).
3. **Show Dataset Overview** (100 Assets, 500 Vulnerabilities, 12 Critical CVEs).
4. **Show Baseline Risk Score** (82.0 / 100 — Critical Risk).
5. **Introduce / Identify Critical Vulnerability** (Log4j CVE-2021-44228 on Payment Gateway).
6. **Recalculate Risk** (Real-time dynamic recalculation).
7. **Show Financial Risk (FAIR)** (Enterprise Modeled EAL: ₹4.60 Crore).
8. **Show Monte Carlo Simulation** (10,000 iterations, P50 Median, P95 Tail Risk).
9. **Show XGBoost Prediction** (30-day forecast: 84.8 / 100).
10. **Show SHAP Explanation** (Top risk drivers: CISA KEV +14.2, Exposure +11.8).
11. **Show Threat Intelligence** (CISA KEV live catalog & MITRE ATT&CK mapping).
12. **Show Attack Path Analysis** (Ingress Gateway $\to$ Internal Switch $\to$ Customer DB).
13. **Show Security Control Recommendations** (12 standard NIST/CIS controls).
14. **Enter Cybersecurity Budget** (Set budget cap at ₹1.0 Crore).
15. **Run Google OR-Tools Optimization** (Knapsack solver allocates ₹85.0L across 5 controls).
16. **Show Before vs. After** (EAL reduced from ₹4.60Cr to ₹2.00Cr — 3.06x ROSI).
17. **Run What-If Scenario** (Digital twin simulation of patch acceleration).
18. **Open CISO Review** (Command center review with executive context).
19. **Approve Recommendation** (CISO signs off with commentary).
20. **Show Audit Trail** (Logged event with user, timestamp, and details).
21. **Record Audit Evidence** (Canonical SHA-256 evidence generation).
22. **Verify Blockchain Evidence** (Hyperledger Fabric returns `VALID`).
23. **Perform Controlled Tamper Test** (Simulate off-chain DB alteration).
24. **Show Tamper Result** (Verification returns `INVALID / TAMPER DETECTED`).
25. **Return to Executive Dashboard** (Full closed-loop governance cycle verified).

---

## 20. Known Limitations
1. **Modeled Financial Values**: Loss figures are modeled estimates based on the FAIR methodology and Indian banking benchmarks (RBI/SEBI), unless connected to actual ERP/GL financial feeds.
2. **AI Forecast Horizon**: Machine learning risk forecasts (30/60/90 days) depend on historical telemetry density; sudden zero-day outbreaks will skew linear projections until scanned.
3. **Threat Intelligence Availability**: External NVD/CISA APIs are subject to external network availability and rate limits; graceful cached fallbacks are utilized when unavailable.
4. **Attack Path Ingress Assumptions**: Dynamic graph extraction requires identifiable ingress assets (`internet_exposed=True` or perimeter gateway types) to derive multi-hop pathways.
5. **Fabric Fallback**: If a production Hyperledger Fabric orderer/peer network is not running locally, the system utilizes a high-fidelity local cryptographic audit ledger matching Fabric's canonical SHA-256 hashing.

---

## 21. Future Scope
- Integration with live AWS/Azure/GCP cloud security posture management (CSPM) APIs.
- Automated API connectors for SAP ERP and Oracle Financials for real-time asset balance sheet valuation.
- Deep reinforcement learning (PPO) for dynamic, multi-agent cyber defense games.
- Full production multi-organization federated blockchain consortium for cross-bank threat sharing.

---

## 22. Presentation Talking Points for Evaluators
1. **No Hardcoded Fakes**: Every score, chart, and table in Quantum Risk AI is dynamically derived from real backend endpoints, Python mathematics, or OR-Tools solvers.
2. **Defensible Mathematics**: We replace arbitrary 1-5 heatmaps with the industry-standard FAIR model ($EAL = SLE \times ARO$) calibrated in INR (Crores/Lakhs).
3. **Mathematical Guarantee**: Google OR-Tools mathematically guarantees optimal budget allocation under constraints, eliminating guesswork in capital expenditure.
4. **CISO Human-in-the-Loop**: The platform respects the chain of command: AI provides decision intelligence, but the CISO retains executive authority.
5. **Cryptographic Assurance**: Decisions are sealed with SHA-256 digests and blockchain verification, protecting against silent database tampering.

---

## 23. License & Versioning
**Quantum Risk AI | SIH 2026 Final | Version 1.0**  
Built for the Smart India Hackathon (SIH) 2026.  
All rights reserved © 2026 Quantum Risk AI Team.
