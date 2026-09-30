import pytest
import math
from app.risk_engine.likelihood import calculate_loss_event_frequency
from app.risk_engine.threat_frequency import calculate_threat_event_frequency
from app.risk_engine.vulnerability_exposure import calculate_vulnerability_exploitability
from app.risk_engine.control_effectiveness import calculate_control_mitigation_factor
from app.risk_engine.loss_magnitude import calculate_single_loss_expectancy
from app.risk_engine.fair_model import run_fair_analysis
from app.risk_engine.eal import calculate_eal, calculate_enterprise_aggregated_eal
from app.risk_engine.calculator import calculate_risk_score, calculate_asset_criticality
from app.risk_engine.monte_carlo import run_monte_carlo_simulation
from app.optimization_engine.solver import optimizer

def test_asset_criticality_does_not_affect_likelihood_or_frequency():
    """
    Requirement 2 & 5: Likelihood / LEF must NOT use Asset Criticality.
    Two assets with identical technical posture (CVSS, exploits, controls, exposure)
    must produce identical Loss Event Frequency regardless of asset criticality.
    """
    res_high_crit = run_fair_analysis(
        asset_criticality=98.0,
        threat_activity=85.0,
        cvss_score=9.8,
        active_exploitation=True,
        is_internet_exposed=True,
        control_coverage=70.0,
        control_effectiveness=75.0
    )

    res_low_crit = run_fair_analysis(
        asset_criticality=20.0,
        threat_activity=85.0,
        cvss_score=9.8,
        active_exploitation=True,
        is_internet_exposed=True,
        control_coverage=70.0,
        control_effectiveness=75.0
    )

    # Frequency and likelihood must be strictly identical
    assert res_high_crit["loss_event_frequency"] == res_low_crit["loss_event_frequency"], \
        "LEF must not depend on Asset Criticality"
    assert res_high_crit["annualized_rate_of_occurrence"] == res_low_crit["annualized_rate_of_occurrence"]
    assert res_high_crit["threat_event_frequency"] == res_low_crit["threat_event_frequency"]
    assert res_high_crit["vulnerability_exploitability"] == res_low_crit["vulnerability_exploitability"]
    assert res_high_crit["annual_incident_probability"] == res_low_crit["annual_incident_probability"]

    # But loss magnitude (SLE) and EAL must differ because asset criticality reflects consequence
    assert res_high_crit["single_loss_expectancy"] > res_low_crit["single_loss_expectancy"], \
        "Higher asset criticality must increase SLE"
    assert res_high_crit["expected_annual_loss"] > res_low_crit["expected_annual_loss"], \
        "Higher asset criticality must increase EAL via SLE"

def test_financial_sle_five_components_exact_sum():
    """
    Requirement 3: Loss Magnitude must maintain the 5 loss categories:
    - Downtime Loss
    - Incident Response Loss
    - Data Recovery Loss
    - Regulatory / Legal Loss
    - Business Interruption Loss
    And SLE must strictly equal the sum of these 5 components.
    """
    loss_res = calculate_single_loss_expectancy(
        asset_criticality=85.0,
        hourly_downtime_cost=300000.0,
        outage_hours=8.0,
        ir_hours=40.0,
        ir_hourly_rate=25000.0,
        data_recovery_base=1500000.0,
        regulatory_fine_base=2000000.0,
        business_impact_base=2500000.0
    )

    comp = loss_res["components"]
    sum_components = round(
        comp["downtime_loss"] +
        comp["incident_response_loss"] +
        comp["data_recovery_loss"] +
        comp["regulatory_legal_loss"] +
        comp["business_interruption_loss"],
        2
    )

    assert loss_res["single_loss_expectancy"] == sum_components, \
        f"SLE ({loss_res['single_loss_expectancy']}) must equal sum of 5 components ({sum_components})"
    assert loss_res["primary_loss_total"] == round(comp["downtime_loss"] + comp["incident_response_loss"] + comp["data_recovery_loss"], 2)
    assert loss_res["secondary_loss_total"] == round(comp["regulatory_legal_loss"] + comp["business_interruption_loss"], 2)

def test_eal_mathematical_consistency():
    """
    Requirement 4: EAL = LEF * SLE (or ARO * SLE) must hold with mathematical exactness.
    """
    fair_res = run_fair_analysis(
        asset_criticality=90.0,
        threat_activity=80.0,
        cvss_score=8.5,
        active_exploitation=False,
        is_internet_exposed=False,
        control_coverage=80.0,
        control_effectiveness=85.0
    )

    sle = fair_res["single_loss_expectancy"]
    aro = fair_res["annualized_rate_of_occurrence"]
    eal = fair_res["expected_annual_loss"]

    expected_product = round(sle * aro, 2)
    assert abs(eal - expected_product) < 0.01, \
        f"EAL ({eal}) must equal SLE ({sle}) * ARO ({aro}) = {expected_product}"
    assert fair_res["mathematical_consistency"]["is_consistent"] is True

def test_technical_factors_affect_likelihood():
    """
    Requirement 2 & 5: Increasing threat/exposure/vulnerability increases likelihood/LEF;
    improving controls reduces likelihood/LEF.
    """
    base = calculate_loss_event_frequency(
        threat_activity_level=60.0,
        cvss_score=7.0,
        active_exploitation=False,
        is_internet_facing=False,
        control_coverage=70.0,
        control_effectiveness=70.0
    )

    # 1. Increasing threat activity increases LEF
    higher_threat = calculate_loss_event_frequency(
        threat_activity_level=90.0,
        cvss_score=7.0,
        active_exploitation=False,
        is_internet_facing=False,
        control_coverage=70.0,
        control_effectiveness=70.0
    )
    assert higher_threat["loss_event_frequency"] > base["loss_event_frequency"]

    # 2. Internet exposure increases LEF
    exposed = calculate_loss_event_frequency(
        threat_activity_level=60.0,
        cvss_score=7.0,
        active_exploitation=False,
        is_internet_facing=True,
        control_coverage=70.0,
        control_effectiveness=70.0
    )
    assert exposed["loss_event_frequency"] > base["loss_event_frequency"]

    # 3. Active CISA KEV exploitation increases LEF
    exploited = calculate_loss_event_frequency(
        threat_activity_level=60.0,
        cvss_score=7.0,
        active_exploitation=True,
        is_internet_facing=False,
        control_coverage=70.0,
        control_effectiveness=70.0
    )
    assert exploited["loss_event_frequency"] > base["loss_event_frequency"]

    # 4. Improving control coverage and effectiveness decreases residual weakness and reduces LEF
    strengthened_controls = calculate_loss_event_frequency(
        threat_activity_level=60.0,
        cvss_score=7.0,
        active_exploitation=False,
        is_internet_facing=False,
        control_coverage=95.0,
        control_effectiveness=95.0
    )
    assert strengthened_controls["loss_event_frequency"] < base["loss_event_frequency"]
    assert strengthened_controls["control_residual_weakness"] < base["control_residual_weakness"]

def test_calculator_decoupled_technical_likelihood():
    """
    Requirement 6: In calculator.py, technical_likelihood_score must be independent of asset criticality.
    """
    calc_high_crit = calculate_risk_score(
        threat_likelihood=80.0,
        vulnerability_severity=90.0,
        asset_criticality=95.0,
        control_effectiveness=70.0,
        has_active_exploit=True,
        is_internet_exposed=True
    )

    calc_low_crit = calculate_risk_score(
        threat_likelihood=80.0,
        vulnerability_severity=90.0,
        asset_criticality=25.0,
        control_effectiveness=70.0,
        has_active_exploit=True,
        is_internet_exposed=True
    )

    assert calc_high_crit["technical_likelihood_score"] == calc_low_crit["technical_likelihood_score"], \
        "Technical likelihood score must NOT change when asset criticality changes"
    assert calc_high_crit["loss_event_frequency"] == calc_low_crit["loss_event_frequency"], \
        "LEF must NOT change when asset criticality changes"
    assert calc_high_crit["single_loss_expectancy"] > calc_low_crit["single_loss_expectancy"], \
        "SLE must be higher for higher asset criticality"

def test_monte_carlo_poisson_lognormal_distribution():
    """
    Requirement 8: Monte Carlo simulation represents uncertainty in model inputs
    with Poisson frequency and Lognormal severity, yielding monotonic percentiles.
    """
    base_sle = 8728000.0  # ₹87.3 Lakh
    base_lef = 0.52       # 0.52 incidents / year

    sim = run_monte_carlo_simulation(
        base_loss=base_sle,
        loss_event_frequency=base_lef,
        num_iterations=10000,
        seed=42
    )

    p = sim["percentiles"]
    # Monotonicity check
    assert p["p5"] <= p["p10"] <= p["p25"] <= p["p50_median"] <= p["p75"] <= p["p90"] <= p["p95"], \
        "Percentiles must be strictly monotonically non-decreasing"

    # Mean simulated loss should be within reasonable stochastic bounds of EAL = base_sle * base_lef
    theoretical_eal = base_sle * base_lef
    assert 0.70 * theoretical_eal <= sim["mean_expected_loss"] <= 1.35 * theoretical_eal, \
        f"Simulated mean ({sim['mean_expected_loss']}) should be in bounds of theoretical EAL ({theoretical_eal})"

    assert len(sim["histogram"]) == 20
    assert sim["num_iterations"] == 10000

def test_or_tools_optimizer_risk_reduction_dynamic():
    """
    Requirement 12: OR-Tools investment optimizer operates against modeled risk reduction
    without arbitrary hardcodes.
    """
    budget = 10000000.0  # ₹1 Crore
    controls = [
        {"code": "CTRL-PATCH", "name": "Automated Patching", "implementation_cost": 1800000.0, "modeled_risk_reduction": 7500000.0},
        {"code": "CTRL-MFA", "name": "Privileged MFA", "implementation_cost": 1200000.0, "modeled_risk_reduction": 4500000.0},
        {"code": "CTRL-EDR", "name": "Next-Gen EDR", "implementation_cost": 2500000.0, "modeled_risk_reduction": 8000000.0},
        {"code": "CTRL-SEG", "name": "Network Segmentation", "implementation_cost": 2000000.0, "modeled_risk_reduction": 6000000.0},
        {"code": "CTRL-BACKUP", "name": "Immutable Backup Vault", "implementation_cost": 1000000.0, "modeled_risk_reduction": 3500000.0}
    ]

    opt = optimizer.optimize_investments(budget=budget, candidate_controls=controls, current_enterprise_risk=46000000.0)

    assert opt["total_investment"] <= budget
    assert opt["modeled_risk_reduction"] > 0
    assert opt["projected_modeled_risk"] < opt["current_modeled_risk"]
    assert opt["efficiency_metric"] > 0
    assert len(opt["selected_controls"]) > 0
