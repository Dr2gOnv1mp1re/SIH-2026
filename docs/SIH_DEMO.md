# Quantum Risk AI — SIH 2026 Master Demonstration Guide
## 18-Step Live Evaluator Walkthrough & Script

### Pre-Demo Verification
Run automated evidence verification in PowerShell before presenting to judges:
```powershell
python backend/tests/run_evidence_verification.py
```
*Expected Output: `>>> ALL 12 EVIDENCE SECTIONS EXECUTED WITH 100% SUCCESS <<<`*

---

### Step-by-Step Evaluator Script

#### Phase 1: Telemetry, Observability & Ingestion (Speaker: Member 1)
- **Step 1: System Observability Dashboard (`/system-status`)**  
  *Talking Point:* "We begin with complete system transparency. Quantum Risk AI monitors 12 subsystems and connectors. Notice our connection truthfulness: NIST NVD and CISA KEV are live and connected; Wazuh and OpenVAS honestly display NOT CONFIGURED rather than faking an on-premise connection."
- **Step 2: Authentication & 6-Role Enterprise RBAC (`/login`)**  
  *Talking Point:* "We log in as Vikram Malhotra, CISO of ABC Bank. The platform enforces strict role separation across 6 roles: CISO, Security Analyst, Risk Analyst, Executive, Auditor, and Admin."
- **Step 3: Enterprise Asset Inventory & CSV Import (`/assets`)**  
  *Talking Point:* "Here are ABC Bank's 100 enterprise assets. Notice our Crown Jewel, the Core Payment Gateway. We can click 'Import Assets CSV', download the standard template, or upload our custom enterprise infrastructure."
- **Step 4: Vulnerability Exposure Registry & CISA KEV Filter (`/vulnerabilities`)**  
  *Talking Point:* "500 CVEs are mapped against our assets. By clicking the prominent 'Filter CISA Known Exploits' button, we instantly isolate 6 active weaponized vulnerabilities including Log4Shell (CVE-2021-44228)."

#### Phase 2: Quantitative Cyber Risk & Monetization (Speaker: Member 2)
- **Step 5: Executive CISO Dashboard (`/dashboard`)**  
  *Talking Point:* "Our enterprise risk score sits at 82.0 (CRITICAL). Unlike qualitative red-amber-green heatmaps, we quantify technical risk directly into currency: an Expected Annual Loss of ₹4.60 Crore."
- **Step 6: Open FAIR Financial Exposure Monetization (`/financial-risk`)**  
  *Talking Point:* "Using the international Open FAIR standard (EAL = SLE × ARO), we break down the ₹4.60 Crore across 6 banking loss categories: downtime, incident response, data recovery, DPDP Act regulatory fines, and business interruption."
- **Step 7: 10,000-Iteration Monte Carlo Simulation (`/financial-risk`)**  
  *Talking Point:* "We run 10,000 Monte Carlo trials showing that while our median loss is ₹4.20 Crore, our 85th percentile Board Risk Tolerance is ₹5.80 Crore, and tail cyber risk reaches ₹7.90 Crore."
- **Step 8: Parametric Assumptions Tuning (`/financial-risk`)**  
  *Talking Point:* "By opening the Parametric Assumptions panel, the CFO can adjust our hourly downtime cost or legal penalties and watch the balance-sheet loss recalculate in real time."

#### Phase 3: Predictive AI & Attack Graphs (Speaker: Member 3)
- **Step 9: Machine Learning 90-Day Trajectory Forecast (`/future-risk`)**  
  *Talking Point:* "Our XGBoost Regressor forecasts that if no remediations are taken, our risk score will surge from 82.0 to 91.5 over the next 90 days due to vulnerability velocity and exploit maturity."
- **Step 10: Native Tree SHAP Attribution Waterfall (`/future-risk`)**  
  *Talking Point:* "We don't use black-box AI. Native C++ Tree SHAP provides exact game-theoretic attributions: Unpatched Critical CVEs contributed +5.2 points, and Patch Lag added +2.8 points."
- **Step 11: Directed Attack Path Analysis (`/attack-paths`)**  
  *Talking Point:* "Our graph engine visualizes the adversary exploit chain from DMZ Gateway to Web Server to our Crown Jewel Payment Database."
- **Step 12: Choke Point Identification (`/attack-paths`)**  
  *Talking Point:* "Dijkstra graph analysis proves that patching the public-facing Payment Gateway is the single critical choke point that eliminates 100% of reachability to the internal database."

#### Phase 4: Optimization, CISO Decision & Blockchain Audit (Speaker: Member 4)
- **Step 13: Google OR-Tools SCIP Knapsack Solver (`/investment-optimizer`)**  
  *Talking Point:* "The Board allocated a budget of ₹1.00 Crore. Instead of spending it all heuristically, Google OR-Tools recommends an optimal ₹85 Lakh investment across 5 high-impact controls."
- **Step 14: Prerequisite DAG & Efficiency Ratio (`/investment-optimizer`)**  
  *Talking Point:* "This ₹85 Lakh investment yields ₹2.60 Crore in modeled risk reduction—achieving a 3.06x ROI efficiency ratio while leaving ₹15 Lakh as an unspent contingency reserve."
- **Step 15: CISO Decision Review (`/ciso-approval`)**  
  *Talking Point:* "'AI recommends; CISO decides.' The CISO reviews the mathematical recommendation, adds implementation notes, and executes formal signoff."
- **Step 16: Immutable Blockchain Ledger Commit (`/blockchain-audit`)**  
  *Talking Point:* "The approval is immediately notarized onto our audit ledger with a canonical SHA-256 hash and CISO signature."
- **Step 17: Cryptographic Tamper Detection Sandbox (`/blockchain-audit`)**  
  *Talking Point:* "Watch what happens when an attacker attempts to modify an off-chain database record. Clicking 'Launch Tamper Test' instantly flags a cryptographic hash mismatch: TAMPERING_DETECTED."
- **Step 18: Self-Healing Auto-Restoration (`/blockchain-audit`)**  
  *Talking Point:* "The CISO clicks 'Restore Ledger'. The system pulls the authentic signed block from the hash tree, automatically heals the corrupted record, and restores the ledger to 100% verified status."
