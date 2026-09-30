"""
Master End-to-End Pipeline Audit for Quantum Risk AI (SIH 2026 Demonstration).
Verifies the complete 16-step demonstration sequence:
1. LOGIN & AUTH
2. ASSET INVENTORY & CRITICALITY
3. VULNERABILITY INGESTION & CISA KEV
4. THREAT INTELLIGENCE
5. RISK ENGINE
6. FINANCIAL RISK (FAIR SLE & EAL)
7. MONTE CARLO SIMULATION
8. XGBOOST PREDICTION
9. SHAP LOCAL EXPLANATIONS
10. ATTACK PATH TO ASSETS & LOSS
11. WHAT-IF SCENARIOS (7 CONTROLS)
12. OR-TOOLS INVESTMENT OPTIMIZATION
13. CISO APPROVAL WORKFLOW
14. BLOCKCHAIN RECORDING
15. BLOCKCHAIN TAMPER VERIFICATION
16. DATA PROVENANCE & EXECUTIVE SUMMARY
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)


def test_master_sixteen_step_sih_pipeline(client):
    # Step 1: LOGIN (CISO Role)
    login_res = client.post("/api/v1/auth/login", json={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: ASSET INVENTORY & CRITICALITY
    assets_res = client.get("/api/v1/assets", headers=headers)
    assert assets_res.status_code == 200
    assets = assets_res.json()
    assert len(assets) > 0
    # Ensure crown jewel database has criticality >= 90
    db_asset = next((a for a in assets if "Database" in a.get("name", "") or "DB" in a.get("hostname", "") or "Payment" in a.get("name", "")), None)
    assert db_asset is not None
    assert db_asset["criticality_score"] >= 80.0
    
    # Step 3: VULNERABILITY INGESTION & CISA KEV
    vuln_res = client.get("/api/v1/vulnerabilities", headers=headers)
    assert vuln_res.status_code == 200
    vulns = vuln_res.json()
    assert vulns["stats"]["total"] > 0
    assert vulns["stats"]["cisa_known_exploited"] >= 1
    
    # Step 4: THREAT INTELLIGENCE
    threats_res = client.get("/api/v1/threats", headers=headers)
    assert threats_res.status_code == 200
    assert len(threats_res.json()) > 0
    
    # Step 5: TECHNICAL RISK
    risk_res = client.get("/api/v1/risk/enterprise", headers=headers)
    assert risk_res.status_code == 200
    risk_data = risk_res.json()
    assert risk_data["enterprise_risk_score"] > 0
    
    # Step 6: FINANCIAL RISK (FAIR Model SLE & EAL)
    fin_res = client.get("/api/v1/financial/enterprise", headers=headers)
    assert fin_res.status_code == 200
    fin_data = fin_res.json()
    assert fin_data["expected_annual_loss"] > 0
    assert "loss_components" in fin_data
    assert fin_data["loss_components"]["total_potential_loss"] > 0
    
    # Step 7: MONTE CARLO SIMULATION
    mc_res = client.get("/api/v1/financial/monte-carlo?iterations=1000", headers=headers)
    assert mc_res.status_code == 200
    mc_data = mc_res.json()
    assert mc_data["num_iterations"] == 1000
    assert "percentiles" in mc_data
    p = mc_data["percentiles"]
    assert p["p5"] <= p["p25"] <= p["p50_median"] <= p["p75"] <= p["p95"]
    
    # Step 8: XGBOOST PREDICTION
    pred_res = client.get("/api/v1/ai/predictions", headers=headers)
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert pred_data["predicted_30d_risk_score"] > 0
    
    # Step 9: SHAP EXPLANATION
    assert len(pred_data["shap_explanation"]) >= 3
    for s in pred_data["shap_explanation"]:
        assert "feature" in s
    
    # Step 10: ATTACK PATH & BUSINESS IMPACT
    ap_res = client.get("/api/v1/attack-paths", headers=headers)
    assert ap_res.status_code == 200
    ap_data = ap_res.json()
    assert len(ap_data["critical_attack_paths"]) >= 1
    path = ap_data["critical_attack_paths"][0]
    assert path["path_risk_score"] >= 80.0
    assert path["modeled_financial_impact"] > 0
    
    # Step 11: WHAT-IF SCENARIOS (7 CONTROLS)
    interventions_res = client.get("/api/v1/scenarios/interventions", headers=headers)
    assert interventions_res.status_code == 200
    ints = interventions_res.json()
    assert len(ints) == 7
    
    whatif_res = client.post("/api/v1/scenarios/simulate-control", json={"intervention_id": "patching"}, headers=headers)
    assert whatif_res.status_code == 200
    whatif_data = whatif_res.json()
    assert whatif_data["after"]["modeled_risk_reduction"] > 0
    
    # Step 12: OR-TOOLS INVESTMENT OPTIMIZATION
    opt_res = client.post("/api/v1/optimization/run", json={"budget": 10000000.0}, headers=headers)
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    run_id = opt_data["run_id"]
    res_opt = opt_data["optimization_result"]
    assert res_opt["total_investment"] <= 10000000.0
    assert res_opt["total_investment"] > 0
    assert len(res_opt["selected_controls"]) > 0
    
    # Step 13: CISO APPROVAL
    ciso_res = client.post("/api/v1/optimization/approve", json={
        "optimization_run_id": run_id,
        "approval_notes": "Master SIH 2026 End-to-End Demonstration Approved."
    }, headers=headers)
    assert ciso_res.status_code == 200
    assert ciso_res.json()["status"] == "APPROVED"
    
    # Step 14: BLOCKCHAIN AUDIT
    bc_res = client.get("/api/v1/blockchain/blocks", headers=headers)
    assert bc_res.status_code == 200
    blocks = bc_res.json()["blocks"]
    assert len(blocks) >= 2
    
    # Step 15: BLOCKCHAIN VERIFICATION & TAMPER PROOF
    verify_res = client.post(f"/api/v1/blockchain/verify/{run_id}", headers=headers)
    assert verify_res.status_code == 200
    assert verify_res.json()["verification_status"] == "VERIFIED"
    
    # Step 16: DATA PROVENANCE REGISTRY
    prov_res = client.get("/api/v1/provenance", headers=headers)
    assert prov_res.status_code == 200
    prov_data = prov_res.json()
    assert prov_data["total_sources_registered"] >= 15
    assert "REAL_PUBLIC_DATA" in prov_data["categories"]
