# Quantum Risk AI — Quantitative Risk Quantification Methodology
## Open FAIR Standard Formulation, Monte Carlo Engine, and Monetization

### 1. The Need for Quantitative Risk
Traditional qualitative risk matrices (High/Medium/Low, Red/Amber/Green) suffer from severe mathematical and decision-making flaws:
1. **Ambiguity:** "High Risk" conveys no actionable scale to a Board of Directors or Chief Financial Officer.
2. **Range Compression:** Extreme variations in loss (e.g. ₹50 Lakh vs ₹50 Crore) get lumped into the identical "High" category.
3. **Inability to Compute ROI:** Qualitative scores cannot be divided by financial investment costs to yield an ROI or cost-benefit ratio.

Quantum Risk AI implements the international standard **Open FAIR (Factor Analysis of Information Risk - ISO/IEC 27005 compliant)** framework.

---

### 2. The Open FAIR Quantitative Formulation

$$\text{Expected Annual Loss (EAL)} = \text{Single Loss Expectancy (SLE)} \times \text{Annualized Rate of Occurrence (ARO)}$$

Where:
- **SLE (Single Loss Expectancy):** The monetary loss expected from a single security incident impacting an enterprise asset.
  $$\text{SLE} = \text{Primary Loss} + \text{Secondary Loss}$$
- **ARO (Annualized Rate of Occurrence):** The estimated frequency per year that the threat actor will successfully breach the asset:
  $$\text{ARO} = \text{Threat Event Frequency (TEF)} \times \text{Vulnerability (V)}$$
  $$\text{Vulnerability} = P(\text{Threat Capability} > \text{Control Resistance})$$

---

### 3. Banking Loss Categorization (ABC Bank Calibration)

For a Tier-1 Scheduled Commercial Bank, single-incident losses are decomposed across 6 distinct categories:

| Loss Category | Parameter / Basis | Example Calculation (Crown Jewel Payment DB) |
|:---|:---|:---:|
| **1. Downtime & Productivity** | $\text{Downtime Hours} \times \text{Hourly Rate}$ | $7.36\text{ hrs} \times ₹3,00,000/\text{hr} = ₹22.08\text{ Lakh}$ |
| **2. Incident Response & Forensics**| Specialized DFIR Retainer & Triage | Fixed Retainer + $40\text{ hrs} @ ₹25,000/\text{hr} = ₹10.00\text{ Lakh}$ |
| **3. Data Recovery & Restoration** | DB Table Rebuild, Integrity Audit | Data Volume Index $\times$ Complexity Factor $= ₹13.80\text{ Lakh}$ |
| **4. Regulatory & Legal Penalties**| RBI Cyber Framework & DPDP Act 2023 | Base Penalty for PII Exposure $= ₹18.40\text{ Lakh}$ |
| **5. Business Interruption** | Transaction fee loss, payment outages | Lost Transaction Volume $= ₹23.00\text{ Lakh}$ |
| **Total Single Incident (SLE)** | Sum of 5 Primary Components | **₹87.28 Lakh** |

---

### 4. Enterprise Monte Carlo Vector Simulation

Rather than relying on static point estimates, Quantum Risk AI runs a **10,000-iteration Monte Carlo simulation** modeling uncertainty in loss frequency and magnitude.

#### Parametric Distributions:
- **Threat Event Frequency (TEF):** Modeled using a **Poisson distribution** ($\lambda = \text{ARO}$).
- **Loss Magnitude:** Modeled using a **Beta-PERT distribution** bounded by:
  - Minimum Loss ($L_{\min} = 0.5 \times \text{Modeled SLE}$)
  - Most Likely Loss ($L_{\text{mode}} = \text{Modeled SLE}$)
  - Maximum Loss ($L_{\max} = 3.5 \times \text{Modeled SLE}$)

#### Simulated Risk Metrics for ABC Bank:
- **10th Percentile (Optimistic):** ₹2.10 Crore
- **50th Percentile (Median / P50):** ₹4.20 Crore
- **Mean Expected Annual Loss (EAL):** **₹4.60 Crore** (Baseline)
- **85th Percentile (Board Risk Tolerance):** ₹5.80 Crore
- **95th Percentile (Cyber VaR / Tail Risk):** ₹7.90 Crore

---

### 5. Asset Criticality Scoring Algorithm

Each asset receives a normalized criticality score $C \in [0, 100]$:
$$C = 0.25 \cdot I_{\text{biz}} + 0.25 \cdot S_{\text{data}} + 0.20 \cdot R_{\text{rev}} + 0.15 \cdot G_{\text{reg}} + 0.10 \cdot E_{\text{net}} + 0.05 \cdot T_{\text{down}}$$
Where:
- $I_{\text{biz}}$: Business Importance [0-100]
- $S_{\text{data}}$: Data Sensitivity [0-100]
- $R_{\text{rev}}$: Revenue Dependency [0-100]
- $G_{\text{reg}}$: Regulatory Importance [0-100]
- $E_{\text{net}}$: Internet Exposed (0 or 100)
- $T_{\text{down}}$: Downtime Tolerance factor ($100 - \min(100, \text{hours} \times 10)$)
