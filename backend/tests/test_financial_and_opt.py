import pytest
from app.financial_engine.eal import calculate_eal, calculate_single_loss_expectancy
from app.financial_engine.monte_carlo import run_monte_carlo_simulation
from app.optimization_engine.solver import optimizer
from app.blockchain.ledger import audit_ledger, generate_canonical_hash

def test_financial_eal_calculation():
    eal_res = calculate_eal(
        risk_score=82.0,
        asset_criticality=95.0,
        has_active_exploit=True,
        is_internet_exposed=True
    )
    assert eal_res["expected_annual_loss"] > 0
    assert eal_res["loss_range_min"] < eal_res["expected_annual_loss"] < eal_res["loss_range_max"]
    assert eal_res["modeled_label"] == "MODELED ESTIMATE"

def test_monte_carlo_percentiles():
    sim = run_monte_carlo_simulation(base_loss=46000000.0, base_probability=0.35, num_iterations=1000)
    p = sim["percentiles"]
    assert p["p5"] <= p["p25"] <= p["p50_median"] <= p["p75"] <= p["p95"], "Percentiles must be strictly monotonically ordered"

def test_optimization_never_exceeds_budget():
    budget = 5000000.0  # ₹50 Lakh budget
    candidate_controls = [
        {"code": "CTRL-PATCH", "name": "Automated Patching", "implementation_cost": 1800000.0, "modeled_risk_reduction": 7500000.0},
        {"code": "CTRL-MFA", "name": "Privileged MFA", "implementation_cost": 1200000.0, "modeled_risk_reduction": 4500000.0},
        {"code": "CTRL-EDR", "name": "EDR / XDR", "implementation_cost": 2500000.0, "modeled_risk_reduction": 8000000.0},
        {"code": "CTRL-SEG", "name": "Network Segmentation", "implementation_cost": 2000000.0, "modeled_risk_reduction": 6000000.0},
        {"code": "CTRL-BACKUP", "name": "Immutable Backup", "implementation_cost": 1000000.0, "modeled_risk_reduction": 3500000.0}
    ]
    res = optimizer.optimize_investments(budget=budget, candidate_controls=candidate_controls, current_enterprise_risk=46000000.0)
    assert res["total_investment"] <= budget, f"Optimizer total investment ({res['total_investment']}) exceeded budget ({budget})!"
    assert res["modeled_risk_reduction"] > 0

def test_blockchain_tamper_detection():
    # 1. Record authentic transaction
    payload = {"assessment_id": "TEST-2026-01", "risk_score": 82.0, "eal": 46000000.0}
    block = audit_ledger.record_transaction("TEST_ASSESSMENT", "TEST-2026-01", payload)
    
    # 2. Verify authentic
    verify_valid = audit_ledger.verify_record_integrity("TEST-2026-01", payload)
    assert verify_valid["is_valid"] is True
    assert verify_valid["verification_status"] == "VERIFIED"

    # 3. Simulate tampering (e.g. attacker modifies risk score in DB)
    tampered_payload = dict(payload)
    tampered_payload["risk_score"] = 20.0  # Falsified risk reduction
    verify_tampered = audit_ledger.verify_record_integrity("TEST-2026-01", tampered_payload)
    assert verify_tampered["is_valid"] is False
    assert verify_tampered["verification_status"] == "TAMPERING_DETECTED"
