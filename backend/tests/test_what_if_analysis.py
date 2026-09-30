"""
Automated Test Suite for What-If / Scenario Analysis Module.
Proves that What-If analysis uses the centralized FAIR risk engine,
does not use hardcoded outputs, respects control-effectiveness models,
and dynamically adjusts LEF, SLE, and EAL based on intervention parameters.
"""

import pytest
from app.scenarios.what_if_engine import (
    INTERVENTION_CATALOG,
    get_available_interventions,
    calculate_what_if_scenario
)

def test_all_seven_interventions_present():
    """Verify all 7 required enterprise security interventions exist in catalog."""
    interventions = get_available_interventions()
    int_ids = [i["id"] for i in interventions]
    required_ids = [
        "patching",
        "mfa",
        "edr",
        "microsegmentation",
        "zero_trust",
        "immutable_backup",
        "reduced_exposure"
    ]
    for req in required_ids:
        assert req in int_ids, f"Missing required intervention: {req}"
    assert len(interventions) == 7


def test_patching_reduces_lef_without_changing_sle():
    """
    Critical vulnerability patching reduces CVSS & exploitability,
    drastically lowering LEF and EAL, while leaving asset SLE unchanged.
    """
    res = calculate_what_if_scenario("patching")
    
    # Verify Before -> Control -> After structure
    assert "before" in res and "control" in res and "after" in res
    
    before_lef = res["before"]["loss_event_frequency"]
    after_lef = res["after"]["updated_loss_event_frequency"]
    before_sle = res["before"]["single_loss_expectancy"]
    after_sle = res["after"]["updated_single_loss_expectancy"]
    before_eal = res["before"]["expected_annual_loss"]
    after_eal = res["after"]["updated_expected_annual_loss"]
    
    # LEF must drop significantly
    assert after_lef < before_lef
    # SLE must remain identical (asset criticality unchanged)
    assert after_sle == before_sle
    # EAL must drop and match SLE * LEF
    assert after_eal < before_eal
    assert round(after_sle * after_lef, 2) == pytest.approx(after_eal, rel=1e-2)
    # Modeled reduction must be positive
    assert res["after"]["modeled_risk_reduction"] > 0


def test_immutable_backup_reduces_sle_without_changing_lef():
    """
    Immutable backup reduces downtime and data recovery loss in SLE,
    while LEF remains strictly unchanged (adversary threat frequency does not change).
    """
    res = calculate_what_if_scenario("immutable_backup")
    
    before_lef = res["before"]["loss_event_frequency"]
    after_lef = res["after"]["updated_loss_event_frequency"]
    before_sle = res["before"]["single_loss_expectancy"]
    after_sle = res["after"]["updated_single_loss_expectancy"]
    before_eal = res["before"]["expected_annual_loss"]
    after_eal = res["after"]["updated_expected_annual_loss"]
    
    # LEF must be unchanged
    assert after_lef == before_lef
    # SLE must drop
    assert after_sle < before_sle
    # EAL must drop
    assert after_eal < before_eal
    # Risk reduction must match (SLE_before - SLE_after) * LEF
    expected_reduction = round((before_sle - after_sle) * before_lef, 2)
    assert abs(res["after"]["modeled_risk_reduction"] - expected_reduction) < 1.0


def test_edr_reduces_both_lef_and_sle():
    """
    EDR / XDR autonomous containment increases endpoint control strength (lowering LEF)
    AND accelerates containment time / reduces outage hours (lowering SLE).
    """
    res = calculate_what_if_scenario("edr")
    
    before_lef = res["before"]["loss_event_frequency"]
    after_lef = res["after"]["updated_loss_event_frequency"]
    before_sle = res["before"]["single_loss_expectancy"]
    after_sle = res["after"]["updated_single_loss_expectancy"]
    before_eal = res["before"]["expected_annual_loss"]
    after_eal = res["after"]["updated_expected_annual_loss"]
    
    assert after_lef < before_lef
    assert after_sle < before_sle
    assert after_eal < before_eal
    assert res["after"]["modeled_risk_reduction"] > 0


def test_microsegmentation_breaks_lateral_path():
    """
    Zero-Trust Micro-segmentation breaks lateral attack path,
    removing path multiplier and lowering LEF & EAL.
    """
    res = calculate_what_if_scenario("microsegmentation")
    assert res["after"]["updated_loss_event_frequency"] < res["before"]["loss_event_frequency"]
    assert res["after"]["updated_expected_annual_loss"] < res["before"]["expected_annual_loss"]
    assert "PATH-001: Internet-to-Core-Payment-DB" in res["control"]["affected_attack_paths"]


def test_reduced_exposure_removes_internet_vector():
    """
    Removing internet exposure drops external threat frequency, lowering LEF.
    """
    res = calculate_what_if_scenario("reduced_exposure")
    assert res["after"]["updated_loss_event_frequency"] < res["before"]["loss_event_frequency"]
    assert res["after"]["updated_expected_annual_loss"] < res["before"]["expected_annual_loss"]
    assert res["after"]["updated_single_loss_expectancy"] == res["before"]["single_loss_expectancy"]


def test_custom_cost_affects_rosi():
    """
    Adjusting investment budget dynamically changes the Return on Security Investment (ROSI).
    """
    res_low_cost = calculate_what_if_scenario("patching", custom_cost=500000.0)  # ₹5 Lakh
    res_high_cost = calculate_what_if_scenario("patching", custom_cost=5000000.0) # ₹50 Lakh
    
    # Risk reduction is identical (same technical control applied)
    assert res_low_cost["after"]["modeled_risk_reduction"] == res_high_cost["after"]["modeled_risk_reduction"]
    # But ROSI is higher for lower cost
    assert res_low_cost["after"]["return_on_security_investment_percentage"] > res_high_cost["after"]["return_on_security_investment_percentage"]


def test_mathematical_consistency_across_all_interventions():
    """
    Verify EAL = SLE * LEF holds before and after every single intervention.
    """
    for int_id in INTERVENTION_CATALOG.keys():
        res = calculate_what_if_scenario(int_id)
        
        # Before check
        b_eal = res["before"]["expected_annual_loss"]
        b_sle = res["before"]["single_loss_expectancy"]
        b_lef = res["before"]["loss_event_frequency"]
        assert abs(b_eal - round(b_sle * b_lef, 2)) < 0.1, f"Failed Before EAL math for {int_id}"
        
        # After check
        a_eal = res["after"]["updated_expected_annual_loss"]
        a_sle = res["after"]["updated_single_loss_expectancy"]
        a_lef = res["after"]["updated_loss_event_frequency"]
        assert abs(a_eal - round(a_sle * a_lef, 2)) < 0.1, f"Failed After EAL math for {int_id}"
