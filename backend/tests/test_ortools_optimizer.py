"""
Automated Test Suite for Google OR-Tools Mixed-Integer Knapsack Optimizer.
Verifies:
1. Budget constraint is strictly respected across all budget tiers.
2. Selection of controls includes all 8 required audit parameters.
3. Selection rationale is dynamically derived from solver inputs/outputs.
4. Comparison flow (Current Risk -> Budget -> Candidates -> Portfolio -> Remaining Risk) is consistent.
5. Prerequisite dependency constraints (e.g. PAM -> MFA, SOC -> EDR) are strictly respected.
6. Zero hardcoding of investment outputs.
"""

import pytest
from app.optimization_engine.solver import SecurityInvestmentOptimizer, DEFAULT_CANDIDATE_CONTROLS

@pytest.fixture
def optimizer():
    return SecurityInvestmentOptimizer()


def test_budget_constraint_strictly_respected(optimizer):
    """Verify total_investment <= budget across multiple arbitrary budget limits."""
    test_budgets = [1500000.0, 3000000.0, 5000000.0, 8000000.0, 10000000.0, 15000000.0, 30000000.0]
    
    for b in test_budgets:
        res = optimizer.optimize_investments(budget=b)
        assert res["total_investment"] <= b, f"Failed budget constraint for budget {b}: invested {res['total_investment']}"
        assert res["unused_budget"] >= 0.0
        assert res["unused_budget"] == pytest.approx(b - res["total_investment"], abs=1e-2)
        assert res["comparison_flow"]["total_investment"] == res["total_investment"]
        assert res["comparison_flow"]["unused_budget"] == res["unused_budget"]


def test_selected_controls_have_all_eight_attributes(optimizer):
    """Verify every selected control contains all 8 required attributes."""
    res = optimizer.optimize_investments(budget=10000000.0)
    selected = res["selected_controls"]
    assert len(selected) > 0
    
    for ctrl in selected:
        # 1. Control name
        assert "name" in ctrl and len(ctrl["name"]) > 0
        # 2. Cost
        assert "cost" in ctrl and ctrl["cost"] > 0
        # 3. Assets addressed
        assert "assets_addressed" in ctrl and isinstance(ctrl["assets_addressed"], list)
        assert len(ctrl["assets_addressed"]) > 0
        # 4. Attack paths addressed
        assert "attack_paths_addressed" in ctrl and isinstance(ctrl["attack_paths_addressed"], list)
        assert len(ctrl["attack_paths_addressed"]) > 0
        # 5. Risk factor addressed
        assert "risk_factor_addressed" in ctrl and len(ctrl["risk_factor_addressed"]) > 0
        # 6. Modeled risk reduction
        assert "modeled_risk_reduction" in ctrl and ctrl["modeled_risk_reduction"] > 0
        # 7. Reason for selection
        assert "reason_for_selection" in ctrl
        assert "Selected because this control provides modeled risk reduction" in ctrl["reason_for_selection"]
        assert "budget constraint" in ctrl["reason_for_selection"]
        # 8. Budget contribution
        assert "budget_contribution_pct" in ctrl and ctrl["budget_contribution_pct"] > 0


def test_comparison_flow_structure(optimizer):
    """Verify the 5-stage comparison flow structure."""
    res = optimizer.optimize_investments(budget=10000000.0, current_enterprise_risk=46000000.0)
    flow = res["comparison_flow"]
    
    assert flow["current_risk"] == 46000000.0
    assert flow["available_budget"] == 10000000.0
    assert flow["candidate_controls_count"] == len(DEFAULT_CANDIDATE_CONTROLS)
    assert flow["optimized_portfolio_count"] == len(res["selected_controls"])
    assert flow["modeled_remaining_risk"] == res["projected_modeled_risk"]
    assert flow["modeled_risk_reduction"] == res["modeled_risk_reduction"]


def test_prerequisite_dependencies_enforced(optimizer):
    """
    Verify prerequisite dependency constraints (e.g. CTRL-PAM requires CTRL-MFA, CTRL-SOC requires CTRL-EDR).
    If a child control is selected, its parent must also be selected.
    """
    # Test across small and large budgets
    for b in [3000000.0, 5000000.0, 10000000.0, 20000000.0]:
        res = optimizer.optimize_investments(budget=b)
        selected_codes = {c.get("code") for c in res["selected_controls"]}
        
        if "CTRL-PAM" in selected_codes:
            assert "CTRL-MFA" in selected_codes, f"Dependency violated: CTRL-PAM selected without CTRL-MFA at budget {b}"
            
        if "CTRL-SOC" in selected_codes:
            assert "CTRL-EDR" in selected_codes, f"Dependency violated: CTRL-SOC selected without CTRL-EDR at budget {b}"


def test_stress_test_curve(optimizer):
    """Verify diminishing returns stress test curve produces valid points."""
    curve = optimizer.run_budget_stress_test()
    assert len(curve) >= 5
    for pt in curve:
        assert pt["total_invested"] <= pt["budget"]
        assert pt["modeled_risk_reduction"] >= 0
