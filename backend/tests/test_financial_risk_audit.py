"""
Automated Financial Risk Engine Audit & Verification Test Suite.
Validates FAIR quantitative consistency, mathematical rigor, decoupling rules,
and dynamic calculation guarantees for SIH evaluation.

Test Suite Coverage:
1. SLE component summation: SLE = sum of the 5 modeled loss components.
2. EAL calculation: EAL = SLE * LEF (or ARO).
3. Unit consistency: All outputs have explicit, mathematically consistent units.
4. Asset criticality affects loss magnitude: Higher criticality strictly increases SLE & EAL.
5. Asset criticality does not directly alter likelihood: Likelihood/LEF remains identical across criticalities.
6. Threat/exploitation affects likelihood: Weaponization and active campaigns increase LEF.
7. Better controls reduce likelihood: Increasing control coverage/effectiveness reduces LEF and residual weakness.
8. Financial outputs are not hardcoded: Changing assumptions dynamically shifts all financial loss metrics.
"""

import pytest
import math
from app.risk_engine.loss_magnitude import calculate_single_loss_expectancy
from app.risk_engine.likelihood import calculate_loss_event_frequency
from app.risk_engine.threat_frequency import calculate_threat_event_frequency
from app.risk_engine.vulnerability_exposure import calculate_vulnerability_exploitability
from app.risk_engine.control_effectiveness import calculate_control_mitigation_factor
from app.risk_engine.fair_model import run_fair_analysis
from app.risk_engine.eal import calculate_eal, calculate_enterprise_aggregated_eal
from app.risk_engine.calculator import calculate_risk_score, calculate_asset_criticality

# ---------------------------------------------------------------------------
# Test 1: SLE Component Summation
# ---------------------------------------------------------------------------
def test_sle_five_component_summation_exactness():
    """
    Test 1: SLE = Downtime Loss + Incident Response Loss + Data Recovery Loss +
                  Regulatory/Legal Loss + Business Interruption Loss.
    """
    assumptions = {
        "hourly_downtime_cost": 350000.0,
        "incident_response_hourly_rate": 30000.0,
        "data_recovery_base_cost": 1800000.0,
        "legal_regulatory_base_cost": 2500000.0,
        "business_interruption_base_cost": 3000000.0,
        "outage_hours": 10.0,
        "incident_response_base_hours": 48.0
    }

    result = calculate_single_loss_expectancy(
        asset_criticality=90.0,
        assumptions_override=assumptions
    )

    comp = result["components"]
    expected_downtime = round(350000.0 * 10.0 * (90.0 / 100.0), 2)
    expected_ir = round(48.0 * 30000.0, 2)
    expected_recovery = round(1800000.0 * (90.0 / 100.0), 2)
    expected_regulatory = round(2500000.0 * (90.0 / 100.0), 2)
    expected_biz = round(3000000.0 * (90.0 / 100.0), 2)

    assert comp["downtime_loss"] == expected_downtime
    assert comp["incident_response_loss"] == expected_ir
    assert comp["data_recovery_loss"] == expected_recovery
    assert comp["regulatory_legal_loss"] == expected_regulatory
    assert comp["business_interruption_loss"] == expected_biz

    sum_of_five = round(
        comp["downtime_loss"] +
        comp["incident_response_loss"] +
        comp["data_recovery_loss"] +
        comp["regulatory_legal_loss"] +
        comp["business_interruption_loss"],
        2
    )

    assert result["single_loss_expectancy"] == sum_of_five
    assert result["mathematical_consistency"]["is_sum_exact"] is True

# ---------------------------------------------------------------------------
# Test 2: EAL Calculation
# ---------------------------------------------------------------------------
def test_eal_calculation_mathematical_consistency():
    """
    Test 2: Expected Annual Loss (EAL) must satisfy EAL = SLE * ARO (or LEF).
    """
    analysis = run_fair_analysis(
        asset_criticality=88.0,
        threat_activity=75.0,
        cvss_score=8.8,
        active_exploitation=True,
        is_internet_exposed=True,
        control_coverage=65.0,
        control_effectiveness=70.0
    )

    sle = analysis["single_loss_expectancy"]
    aro = analysis["annualized_rate_of_occurrence"]
    eal = analysis["expected_annual_loss"]

    expected_eal = round(sle * aro, 2)
    assert eal == expected_eal
    assert analysis["mathematical_consistency"]["is_consistent"] is True

# ---------------------------------------------------------------------------
# Test 3: Unit Consistency
# ---------------------------------------------------------------------------
def test_unit_consistency_across_financial_engine():
    """
    Test 3: Verify dimensional analysis and unit metadata across all returns:
    - Probability: dimensionless in [0, 1] per year
    - Frequency (LEF / ARO / TEF): events or incidents / year
    - Loss Magnitude / SLE: INR (₹) / incident
    - Annual Loss / EAL: INR (₹) / year
    """
    analysis = run_fair_analysis(
        asset_criticality=92.0,
        threat_activity=85.0,
        cvss_score=9.8
    )

    units = analysis["units"]
    assert "INR / year" in units["expected_annual_loss"]
    assert "INR / incident" in units["single_loss_expectancy"]
    assert "incidents / year" in units["loss_event_frequency"]
    assert "events / year" in units["threat_event_frequency"]
    assert "probability" in units["annual_incident_probability"]

    # Numerical boundary checks
    assert 0.0 <= analysis["annual_incident_probability"] <= 1.0
    assert analysis["loss_event_frequency"] > 0.0
    assert analysis["single_loss_expectancy"] > 0.0
    assert analysis["expected_annual_loss"] > 0.0

# ---------------------------------------------------------------------------
# Test 4: Asset Criticality Affects Loss Magnitude & EAL
# ---------------------------------------------------------------------------
def test_asset_criticality_affects_loss_magnitude_and_eal():
    """
    Test 4: Higher asset criticality must strictly increase SLE and EAL.
    """
    low_crit = run_fair_analysis(
        asset_criticality=30.0,
        threat_activity=70.0,
        cvss_score=8.0
    )

    high_crit = run_fair_analysis(
        asset_criticality=95.0,
        threat_activity=70.0,
        cvss_score=8.0
    )

    assert high_crit["single_loss_expectancy"] > low_crit["single_loss_expectancy"], \
        "Higher criticality must yield higher SLE"
    assert high_crit["expected_annual_loss"] > low_crit["expected_annual_loss"], \
        "Higher criticality must yield higher EAL"
    assert high_crit["primary_loss_total"] > low_crit["primary_loss_total"]
    assert high_crit["secondary_loss_total"] > low_crit["secondary_loss_total"]

# ---------------------------------------------------------------------------
# Test 5: Asset Criticality Does NOT Directly Alter Likelihood
# ---------------------------------------------------------------------------
def test_asset_criticality_does_not_directly_alter_likelihood():
    """
    Test 5: Asset Criticality must remain solely in the consequence/impact stage.
    Changing asset criticality from 10.0 to 100.0 must leave TEF, Exploitability,
    LEF, ARO, and Probability 100% UNCHANGED.
    """
    run_10 = run_fair_analysis(
        asset_criticality=10.0,
        threat_activity=85.0,
        cvss_score=9.0,
        active_exploitation=True,
        is_internet_exposed=True,
        control_coverage=75.0,
        control_effectiveness=80.0
    )

    run_100 = run_fair_analysis(
        asset_criticality=100.0,
        threat_activity=85.0,
        cvss_score=9.0,
        active_exploitation=True,
        is_internet_exposed=True,
        control_coverage=75.0,
        control_effectiveness=80.0
    )

    assert run_10["threat_event_frequency"] == run_100["threat_event_frequency"], \
        "TEF must be independent of Asset Criticality"
    assert run_10["vulnerability_exploitability"] == run_100["vulnerability_exploitability"], \
        "Vulnerability exploitability must be independent of Asset Criticality"
    assert run_10["loss_event_frequency"] == run_100["loss_event_frequency"], \
        "LEF must be independent of Asset Criticality"
    assert run_10["annualized_rate_of_occurrence"] == run_100["annualized_rate_of_occurrence"], \
        "ARO must be independent of Asset Criticality"
    assert run_10["annual_incident_probability"] == run_100["annual_incident_probability"], \
        "Annual probability must be independent of Asset Criticality"

# ---------------------------------------------------------------------------
# Test 6: Threat and Exploitation Affect Likelihood
# ---------------------------------------------------------------------------
def test_threat_and_exploitation_affect_likelihood():
    """
    Test 6: Active threat campaigns and weaponized CVEs must increase TEF,
    exploitability, and Loss Event Frequency.
    """
    baseline_freq = calculate_loss_event_frequency(
        threat_activity_level=50.0,
        cvss_score=6.0,
        active_exploitation=False,
        is_internet_facing=False
    )

    # Active exploitation
    exploited_freq = calculate_loss_event_frequency(
        threat_activity_level=50.0,
        cvss_score=6.0,
        active_exploitation=True,
        is_internet_facing=False
    )
    assert exploited_freq["loss_event_frequency"] > baseline_freq["loss_event_frequency"]
    assert exploited_freq["vulnerability_exploitability"] > baseline_freq["vulnerability_exploitability"]

    # Higher threat intensity
    high_threat_freq = calculate_loss_event_frequency(
        threat_activity_level=95.0,
        cvss_score=6.0,
        active_exploitation=False,
        is_internet_facing=False
    )
    assert high_threat_freq["loss_event_frequency"] > baseline_freq["loss_event_frequency"]
    assert high_threat_freq["threat_event_frequency"] > baseline_freq["threat_event_frequency"]

# ---------------------------------------------------------------------------
# Test 7: Better Controls Reduce Likelihood Where Appropriate
# ---------------------------------------------------------------------------
def test_better_controls_reduce_likelihood():
    """
    Test 7: Higher control coverage and effectiveness must reduce residual weakness
    and lower Loss Event Frequency.
    """
    weak_controls = calculate_loss_event_frequency(
        threat_activity_level=80.0,
        cvss_score=8.5,
        control_coverage=30.0,
        control_effectiveness=35.0
    )

    strong_controls = calculate_loss_event_frequency(
        threat_activity_level=80.0,
        cvss_score=8.5,
        control_coverage=95.0,
        control_effectiveness=95.0
    )

    assert strong_controls["control_residual_weakness"] < weak_controls["control_residual_weakness"]
    assert strong_controls["control_strength"] > weak_controls["control_strength"]
    assert strong_controls["loss_event_frequency"] < weak_controls["loss_event_frequency"]
    assert strong_controls["annual_incident_probability"] < weak_controls["annual_incident_probability"]

# ---------------------------------------------------------------------------
# Test 8: Financial Outputs Are Not Hardcoded
# ---------------------------------------------------------------------------
def test_financial_outputs_are_dynamic_not_hardcoded():
    """
    Test 8: Changing financial assumptions dynamically modifies SLE, loss breakdown,
    and EAL without static hardcodes.
    """
    base_assumptions = {
        "hourly_downtime_cost": 300000.0,
        "incident_response_hourly_rate": 25000.0,
        "data_recovery_base_cost": 1500000.0,
        "legal_regulatory_base_cost": 2000000.0,
        "business_interruption_base_cost": 2500000.0
    }

    doubled_assumptions = {
        "hourly_downtime_cost": 600000.0,
        "incident_response_hourly_rate": 50000.0,
        "data_recovery_base_cost": 3000000.0,
        "legal_regulatory_base_cost": 4000000.0,
        "business_interruption_base_cost": 5000000.0
    }

    res_base = run_fair_analysis(asset_criticality=92.0, assumptions_override=base_assumptions)
    res_doubled = run_fair_analysis(asset_criticality=92.0, assumptions_override=doubled_assumptions)

    assert res_doubled["single_loss_expectancy"] == round(res_base["single_loss_expectancy"] * 2.0, 2)
    assert res_doubled["expected_annual_loss"] == round(res_base["expected_annual_loss"] * 2.0, 2)
    assert res_doubled["loss_breakdown"]["downtime_loss"] == round(res_base["loss_breakdown"]["downtime_loss"] * 2.0, 2)
    assert res_doubled["loss_breakdown"]["data_recovery_loss"] == round(res_base["loss_breakdown"]["data_recovery_loss"] * 2.0, 2)

    # Enterprise Aggregation Check
    scenarios = [
        {"expected_annual_loss": 4538560.0},
        {"expected_annual_loss": 7280000.0},
        {"expected_annual_loss": 5525000.0}
    ]
    agg = calculate_enterprise_aggregated_eal(scenarios)
    assert agg["enterprise_modeled_eal"] == 4538560.0 + 7280000.0 + 5525000.0
    assert agg["scenario_count"] == 3
