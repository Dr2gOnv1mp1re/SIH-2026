# Quantum Risk AI — Machine Learning & Model Explainability
## XGBoost Risk Forecasting and Native C++ Tree SHAP Attribution

### 1. Architectural Goal: Defensible AI for Regulated Banking
In financial institutions subject to Reserve Bank of India (RBI) governance and international regulatory oversight, "black-box" machine learning models are unacceptable. Regulators, auditors, and CISOs demand mathematical explainability:
1. *Why* does the model predict risk will increase?
2. *Which* specific vulnerabilities or threat factors are driving the surge?
3. *What* evidence supports the prioritization of one remediation over another?

Quantum Risk AI pairs **Gradient Boosted Decision Trees (XGBoost Regressor)** with **Tree SHAP (SHapley Additive exPlanations)** to provide mathematically sound, game-theoretic attributions.

---

### 2. Feature Engineering & Vector Schema
The future-risk forecasting model operates on a 10-dimensional enterprise feature vector:

| Feature Index | Feature Name | Description | Value Range |
|:---:|:---|:---|:---:|
| $x_1$ | `critical_vuln_count` | Number of unpatched CVSS $\ge 9.0$ vulnerabilities | $0 - 100$ |
| $x_2$ | `cisa_active_exploit_count` | Weaponized exploits actively used in the wild | $0 - 20$ |
| $x_3$ | `avg_cvss_score` | Mean CVSS v3.1 base score across discovered CVEs | $0.0 - 10.0$ |
| $x_4$ | `crown_jewel_vuln_density` | Critical CVEs residing on tier-1 payment assets | $0 - 50$ |
| $x_5$ | `patch_cadence_lag_days` | Average delay past standard SLA for critical patching | $0 - 180\text{ days}$ |
| $x_6$ | `internet_exposure_ratio` | Percentage of affected systems facing public internet | $0.0 - 1.0$ |
| $x_7$ | `threat_actor_targeting_index` | Relevance score of active financial campaigns | $0 - 100$ |
| $x_8$ | `attack_path_reachability` | Minimum network hops from DMZ to crown jewel | $1 - 10$ |
| $x_9$ | `mean_time_to_remediate (MTTR)`| Historical organizational remediation cycle | $1 - 90\text{ days}$ |
| $x_{10}$ | `compensating_control_coverage`| Proportion of assets protected by active EDR/MFA | $0.0 - 1.0$ |

---

### 3. Model Architecture & Hyperparameters
- **Algorithm:** XGBoost Regressor (`xgboost.XGBRegressor`)
- **Objective:** `reg:squarederror`
- **Number of Estimators:** 100 trees
- **Max Tree Depth:** 4 (prevents overfitting and guarantees fast TreeExplainer execution)
- **Learning Rate ($\eta$):** 0.05
- **Subsample Ratio:** 0.85
- **Colsample By Tree:** 0.85

---

### 4. Mathematical Explainability via Tree SHAP
SHAP values are rooted in cooperative game theory (Lloyd Shapley, 1953). For a given feature vector $x$, the model prediction $f(x)$ is decomposed as:

$$f(x) = \phi_0 + \sum_{i=1}^{M} \phi_i(x)$$

Where:
- $\phi_0 = \mathbb{E}[f(X)]$ is the expected baseline prediction across the training distribution (e.g. baseline risk 72.0).
- $\phi_i(x)$ is the Shapley value (marginal contribution) of feature $i$.
- $M = 10$ is the total number of features.

#### Example Attribution Breakdown (ABC Bank 90-Day Trajectory):
- **Baseline Expected Risk:** 72.0
- **Predicted 90-Day Risk:** **91.5** ($\Delta = +19.5$ points)
- **SHAP Feature Attributions:**
  - $+5.2$ points: *Unpatched Critical CVEs* (Log4Shell, Zerologon)
  - $+4.8$ points: *Active CISA KEV Exploitation*
  - $+3.9$ points: *Patch Cadence Lag* (Over 45 days SLA breach)
  - $+3.2$ points: *Crown Jewel Exposure* (Payment DB directly reachable)
  - $+2.4$ points: *Active FIN7 / LockBit Campaign Targeting*

The CISO can present this exact waterfall chart to the Board of Directors as definitive evidence justifying immediate remediation investment.
