"""
Comprehensive Automated Test Suite for Real-World Cyber Incident Scenario Lab (SIH 2026).
Verifies:
1. Authoritative CVE data loading & NVD CVSS score
2. CISA KEV known exploitation status & MITRE ATT&CK techniques
3. Authoritative source metadata & citations (NVD, CISA, Apache, MITRE)
4. Data provenance tags on every input and metric
5. Synthetic enterprise profile identification and non-victim labeling
6. Strict Asset Criticality Separation:
   - Same technical conditions + different asset criticality
   - Likelihood (LEF) MUST remain strictly constant
   - Single Loss Expectancy (SLE) and EAL scale dynamically
7. Dynamic financial calculations: Downtime, IR, Recovery, Regulatory, Business Interruption
   (zero hardcoding of ₹4.6Cr, ₹85L, etc.)
8. Modeled attack path graph integration
9. Monte Carlo stochastic simulation integration (P50, P90, P95, Histogram)
10. AI Prediction (XGBoost) and SHAP feature importance integration
11. What-If mitigation recalculations through the FAIR risk engine
12. Google OR-Tools knapsack investment optimization with budget constraints
13. CISO decision governance workflow (Approve, Reject, Request Review)
14. Cryptographic Blockchain Audit Ledger recording with canonical SHA-256 hash
"""

import pytest
from app.scenarios.real_world_catalog import (
    get_scenario_catalog,
    get_scenario_by_cve,
    SYNTHETIC_ENTERPRISE_DEFAULT,
    SourceType
)
from app.scenarios.real_world_engine import scenario_engine
from app.risk_engine.likelihood import calculate_loss_event_frequency
from app.risk_engine.loss_magnitude import calculate_single_loss_expectancy
from app.risk_engine.monte_carlo import run_monte_carlo_simulation
from app.blockchain.ledger import audit_ledger, generate_canonical_hash

# ==============================================================================
# 1. AUTHORITATIVE THREAT DATA & SOURCES VERIFICATION
# ==============================================================================

def test_log4shell_cve_metadata():
    """Verifies Log4Shell authoritative threat metadata from NVD and CISA KEV."""
    scenario = get_scenario_by_cve("CVE-2021-44228")
    assert scenario is not None
    assert scenario["cve_id"] == "CVE-2021-44228"
    assert scenario["short_name"] == "Log4Shell"

    meta = scenario["threat_metadata"]
    # CVSS Score from NVD
    assert meta["cvss_v3_score"]["value"] == 10.0
    assert meta["cvss_v3_score"]["severity"] == "CRITICAL"
    assert "CVSS:3.1" in meta["cvss_v3_score"]["vector"]

    # CISA KEV Known Exploited Vulnerability
    assert meta["known_exploitation"]["value"] is True
    assert "CISA KEV" in meta["known_exploitation"]["source"]
    assert meta["cisa_kev_details"]["known_ransomware_campaign_use"] == "Known"

    # Affected Product & CWE
    assert "Log4j" in meta["affected_products"]["product"]
    assert "CWE-502" in meta["affected_products"]["cwe_id"]

    # MITRE ATT&CK techniques
    tech_ids = [t["id"] for t in meta["mitre_attack_techniques"]]
    assert "T1190" in tech_ids  # Exploit Public-Facing App
    assert "T1059" in tech_ids  # Command & Scripting Interpreter


def test_authoritative_sources_citations():
    """Verifies that all required authoritative source organizations are cited with URLs."""
    scenario = get_scenario_by_cve("CVE-2021-44228")
    sources = scenario["authoritative_sources"]
    assert len(sources) >= 4

    org_names = [s["organization"] for s in sources]
    assert any("NVD" in org or "NIST" in org for org in org_names)
    assert any("CISA" in org for org in org_names)
    assert any("Apache" in org for org in org_names)
    assert any("MITRE" in org for org in org_names)

    # Every source must have URL and retrieved date
    for s in sources:
        assert s["url"].startswith("http")
        assert len(s["retrieved_date"]) > 0
        assert len(s["fields_used"]) > 0


def test_data_provenance_tagging():
    """Verifies that data provenance is explicitly defined on threat and enterprise fields."""
    analysis = scenario_engine.analyze_scenario("CVE-2021-44228")
    prov = analysis["provenance_registry"]

    assert prov["cve_id"]["source_type"] == SourceType.REAL_PUBLIC_DATA.value
    assert prov["cvss_score"]["source_type"] == SourceType.REAL_PUBLIC_DATA.value
    assert prov["known_exploitation"]["source_type"] == SourceType.REAL_PUBLIC_DATA.value
    assert prov["enterprise_name"]["source_type"] == SourceType.SYNTHETIC_DEMO_INPUT.value
    assert prov["hourly_downtime_cost"]["source_type"] == SourceType.SYNTHETIC_DEMO_INPUT.value
    assert prov["asset_criticality"]["source_type"] == SourceType.ANALYST_INPUT.value
    assert prov["modeled_eal"]["source_type"] == SourceType.MODEL_ASSUMPTION.value


# ==============================================================================
# 2. SYNTHETIC ENTERPRISE PROFILE & NON-VICTIM DISCLAIMER
# ==============================================================================

def test_synthetic_enterprise_profile():
    """Verifies synthetic enterprise configuration and prominent non-victim labeling."""
    profile = SYNTHETIC_ENTERPRISE_DEFAULT
    assert "ABC Bank" in profile["enterprise_name"]
    assert "synthetic" in profile["disclaimer_label"].lower() and "demonstration" in profile["disclaimer_label"].lower()
    assert "never implied" in profile["disclaimer_text"].lower()

    # Configurable fleet parameters
    assert profile["total_servers"] > 0
    assert profile["internet_facing_servers"] > 0
    assert profile["hourly_downtime_cost"] > 0
    assert profile["incident_response_hourly_rate"] > 0
    assert profile["data_recovery_base_cost"] > 0


# ==============================================================================
# 3. STRICT ASSET CRITICALITY SEPARATION RULE
# ==============================================================================

def test_asset_criticality_separation_rule():
    """
    FAIR Principle Test:
    Same technical conditions + different asset criticality:
    Likelihood / LEF MUST remain strictly constant!
    Loss magnitude / SLE and EAL MUST change!
    """
    # Baseline technical conditions
    tech_params = {
        "threat_activity_level": 92.0,
        "cvss_score": 10.0,
        "active_exploitation": True,
        "is_internet_facing": True,
        "control_coverage": 55.0,
        "control_effectiveness": 60.0,
        "in_attack_path": True
    }

    # 1. Compute LEF for low asset criticality (e.g. 40.0) vs high (e.g. 95.0)
    lef_result = calculate_loss_event_frequency(**tech_params)
    constant_lef = lef_result["loss_event_frequency"]

    # 2. Run analysis with two different asset criticalities through the engine
    run_low = scenario_engine.analyze_scenario(
        cve_id="CVE-2021-44228",
        enterprise_overrides={"asset_criticality": 40.0}
    )
    run_high = scenario_engine.analyze_scenario(
        cve_id="CVE-2021-44228",
        enterprise_overrides={"asset_criticality": 95.0}
    )

    low_lef = run_low["risk_quantification"]["loss_event_frequency"]
    high_lef = run_high["risk_quantification"]["loss_event_frequency"]

    low_sle = run_low["risk_quantification"]["single_loss_expectancy"]
    high_sle = run_high["risk_quantification"]["single_loss_expectancy"]

    low_eal = run_low["risk_quantification"]["expected_annual_loss"]
    high_eal = run_high["risk_quantification"]["expected_annual_loss"]

    # Invariant: LEF is identical under both runs
    assert low_lef == high_lef == constant_lef

    # Consequence: Higher criticality causes strictly higher SLE and EAL
    assert high_sle > low_sle
    assert high_eal > low_eal

    # Verify mathematical relationship: EAL == round(SLE * LEF, 2)
    assert low_eal == round(low_sle * low_lef, 2)
    assert high_eal == round(high_sle * high_lef, 2)


# ==============================================================================
# 4. DYNAMIC FINANCIAL CALCULATION (ZERO HARDCODING)
# ==============================================================================

def test_dynamic_financial_calculation():
    """
    Verifies that Downtime, IR, Data Recovery, Legal, and Business Interruption
    are calculated dynamically from inputs and sum to SLE.
    """
    custom_inputs = {
        "asset_criticality": 80.0,
        "hourly_downtime_cost": 400000.0,         # ₹4 Lakh/hr
        "incident_outage_hours": 10.0,            # 10 hrs
        "incident_response_hours": 50.0,          # 50 hrs
        "incident_response_hourly_rate": 30000.0, # ₹30,000/hr
        "data_recovery_base_cost": 2000000.0,     # ₹20 Lakh
        "legal_regulatory_base_cost": 3000000.0,  # ₹30 Lakh
        "business_interruption_base_cost": 4000000.0 # ₹40 Lakh
    }

    analysis = scenario_engine.analyze_scenario(
        cve_id="CVE-2021-44228",
        enterprise_overrides=custom_inputs
    )

    losses = analysis["risk_quantification"]["loss_breakdown"]
    crit_factor = 80.0 / 100.0  # 0.80

    expected_downtime = 400000.0 * 10.0 * crit_factor      # ₹32 Lakh
    expected_ir = 50.0 * 30000.0                           # ₹15 Lakh
    expected_recovery = 2000000.0 * crit_factor             # ₹16 Lakh
    expected_legal = 3000000.0 * crit_factor                # ₹24 Lakh
    expected_biz = 4000000.0 * crit_factor                  # ₹32 Lakh

    expected_sle = expected_downtime + expected_ir + expected_recovery + expected_legal + expected_biz

    assert losses["downtime_loss"] == expected_downtime
    assert losses["incident_response_loss"] == expected_ir
    assert losses["data_recovery_loss"] == expected_recovery
    assert losses["regulatory_legal_loss"] == expected_legal
    assert losses["business_interruption_loss"] == expected_biz

    assert analysis["risk_quantification"]["single_loss_expectancy"] == expected_sle
    expected_eal = round(expected_sle * analysis["risk_quantification"]["loss_event_frequency"], 2)
    assert analysis["risk_quantification"]["expected_annual_loss"] == expected_eal


# ==============================================================================
# 5. MODELED ATTACK PATH
# ==============================================================================

def test_attack_path_generation():
    """Verifies that modeled attack path connects Public Internet to Crown Jewel DB."""
    analysis = scenario_engine.analyze_scenario("CVE-2021-44228")
    path = analysis["modeled_attack_path"]

    assert path["target_crown_jewel"] == "Core Payment Database Cluster"
    assert path["path_length"] >= 5
    assert len(path["nodes"]) >= 5
    assert len(path["edges"]) >= 4

    # Verify origin and crown jewel in nodes
    node_names = [n["name"] for n in path["nodes"]]
    assert any("Public Internet" in name for name in node_names)
    assert any("Core Payment Database" in name for name in node_names)
    assert any("Log4j" in name or "Vulnerable" in name for name in node_names)


# ==============================================================================
# 6. MONTE CARLO STOCHASTIC SIMULATION
# ==============================================================================

def test_monte_carlo_integration():
    """Verifies Monte Carlo simulation returns percentiles P50, P90, P95 and histogram."""
    analysis = scenario_engine.analyze_scenario("CVE-2021-44228")
    mc = analysis["monte_carlo_simulation"]

    assert "p50" in mc
    assert "p90" in mc
    assert "p95" in mc
    assert "mean" in mc
    assert "histogram" in mc

    # Percentiles must be monotonically increasing: P50 <= P90 <= P95
    assert mc["p50"] <= mc["p90"] <= mc["p95"]
    assert len(mc["histogram"]) >= 10


# ==============================================================================
# 7. AI PREDICTION & SHAP EXPLAINABILITY
# ==============================================================================

def test_xgboost_and_shap_integration():
    """Verifies XGBoost prediction horizon and SHAP feature importance attributions."""
    analysis = scenario_engine.analyze_scenario("CVE-2021-44228")
    ai = analysis["ai_prediction"]

    assert "predicted_risk_score" in ai
    assert "predicted_30d_eal" in ai
    assert "confidence_percentage" in ai
    assert "shap_explanations" in ai

    # SHAP explanations must have feature and impact
    shaps = ai["shap_explanations"]
    assert len(shaps) >= 3
    for s in shaps:
        assert "feature" in s
        assert "impact" in s


# ==============================================================================
# 8. WHAT-IF SCENARIO MITIGATION SIMULATOR
# ==============================================================================

def test_what_if_recalculation():
    """Verifies that What-If mitigations recalculate LEF, SLE, and EAL through FAIR engine."""
    what_if = scenario_engine.run_what_if_analysis("CVE-2021-44228")
    sims = what_if["what_if_simulations"]

    assert len(sims) >= 4
    sim_ids = [s["id"] for s in sims]
    assert "whatif-patch" in sim_ids
    assert "whatif-isolate" in sim_ids
    assert "whatif-waf" in sim_ids
    assert "whatif-mfa" in sim_ids

    base_eal = what_if["baseline"]["expected_annual_loss"]

    for s in sims:
        assert s["new_eal"] < base_eal
        assert s["modeled_risk_reduction"] > 0
        assert s["implementation_cost"] > 0
        # Modeled risk reduction == base_eal - new_eal
        assert s["modeled_risk_reduction"] == round(base_eal - s["new_eal"], 2)


# ==============================================================================
# 9. GOOGLE OR-TOOLS KNAPSACK INVESTMENT OPTIMIZER
# ==============================================================================

def test_ortools_knapsack_optimization():
    """Verifies Google OR-Tools solves budget-constrained knapsack problem."""
    budget = 4000000.0  # ₹40 Lakh
    opt_res = scenario_engine.optimize_scenario_investment(
        cve_id="CVE-2021-44228",
        budget=budget
    )

    assert opt_res["allocated_budget"] == budget
    assert opt_res["total_investment"] <= budget
    assert opt_res["remaining_budget"] >= 0.0
    assert opt_res["modeled_risk_reduction"] > 0.0
    assert opt_res["projected_eal"] < opt_res["current_modeled_eal"]
    assert len(opt_res["selected_controls"]) > 0


# ==============================================================================
# 10. CISO DECISION & BLOCKCHAIN AUDIT LEDGER
# ==============================================================================

def test_ciso_decision_and_blockchain_audit():
    """
    Verifies human-in-the-loop CISO governance:
    On APPROVAL -> Commits immutable block to Cryptographic Blockchain Audit Ledger with SHA-256 hash.
    """
    cve = "CVE-2021-44228"

    # 1. Approval Action
    approval_res = scenario_engine.record_ciso_decision(
        cve_id=cve,
        decision="APPROVE",
        ciso_name="Chief Information Security Officer (SIH)",
        decision_notes="Approved automated Log4j patching and Cloud Edge WAF deployment.",
        modeled_eal=35000000.0,
        recommended_investment=3300000.0,
        recommended_controls=["CTRL-PATCH", "CTRL-WAF"]
    )

    assert approval_res["decision"] == "APPROVE"
    assert approval_res["audit_status"] == "COMMITTED_IMMUTABLE"
    assert len(approval_res["canonical_sha256_hash"]) == 64  # Valid SHA-256 hash
    assert approval_res["blockchain_record"] is not None
    assert approval_res["blockchain_record"]["status"] == "COMMITTED_IMMUTABLE"
    assert approval_res["blockchain_record"]["block_number"] >= 1

    # 2. Reject Action
    reject_res = scenario_engine.record_ciso_decision(
        cve_id=cve,
        decision="REJECT",
        ciso_name="Deputy CISO",
        decision_notes="Budget reallocation required.",
        modeled_eal=35000000.0,
        recommended_investment=3300000.0
    )
    assert reject_res["decision"] == "REJECT"
    assert reject_res["blockchain_record"] is None
    assert reject_res["audit_status"] == "GOVERNANCE_RECORDED"


def test_scenario_history_tracking():
    """Verifies that scenario analyses and decisions are recorded in scenario history."""
    history = scenario_engine.get_history()
    assert len(history) > 0
    latest = history[-1]
    assert "cve_id" in latest
    assert "modeled_eal" in latest
    assert "ciso_decision" in latest
