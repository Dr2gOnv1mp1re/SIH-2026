import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def test_full_system_sih_readiness():
    with TestClient(app) as client:
        # ----------------------------------------------------
        # 1. Health & Observability Endpoint
        # ----------------------------------------------------
        health_res = client.get("/health")
        assert health_res.status_code == 200
        health_data = health_res.json()
        assert health_data["status"] in ["HEALTHY", "ok"]
        assert health_data["components"]["backend"] == "OPERATIONAL"
        assert health_data["components"]["optimization_engine"] == "Google OR-Tools Ready"
        assert health_data["components"]["ml_engine"] == "XGBoost + SHAP Loaded"

        # ----------------------------------------------------
        # 2. Authentication & Invalid Credentials Test
        # ----------------------------------------------------
        bad_login = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "WrongPassword123"
        })
        assert bad_login.status_code == 401
        assert "Invalid" in bad_login.json()["detail"]

        # Test unauthenticated access to protected routes
        unauth_res = client.get("/api/v1/risk/enterprise")
        assert unauth_res.status_code == 401

        # ----------------------------------------------------
        # 3. RBAC Test for all 6 roles
        # ----------------------------------------------------
        role_creds = [
            ("CISO", "ciso@abcbank.com", "Ciso@12345"),
            ("SECURITY_ANALYST", "analyst@abcbank.com", "Analyst@12345"),
            ("RISK_ANALYST", "risk@abcbank.com", "Risk@12345"),
            ("EXECUTIVE", "executive@abcbank.com", "Executive@12345"),
            ("AUDITOR", "auditor@abcbank.com", "Auditor@12345"),
            ("ADMIN", "admin@abcbank.com", "Admin@12345")
        ]

        tokens = {}
        for role, email, password in role_creds:
            login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
            assert login_res.status_code == 200, f"Failed login for {role}"
            data = login_res.json()
            assert data["user"]["role"] == role
            tokens[role] = data["access_token"]

        ciso_headers = {"Authorization": f"Bearer {tokens['CISO']}"}
        analyst_headers = {"Authorization": f"Bearer {tokens['SECURITY_ANALYST']}"}

        # Ensure clean canonical baseline state
        client.post("/api/v1/demo/reset", headers=ciso_headers)

        # ----------------------------------------------------
        # 4. Executive Dashboard & Risk Calculations
        # ----------------------------------------------------
        risk_res = client.get("/api/v1/risk/enterprise", headers=ciso_headers)
        assert risk_res.status_code == 200
        risk_data = risk_res.json()
        assert risk_data["enterprise_risk_score"] >= 70.0
        assert risk_data["expected_annual_loss"] == 46000000.0  # ₹4.60 Crore baseline
        assert risk_data["risk_level"] == "CRITICAL"
        assert "risk_contributors" in risk_data

        # Test risk recalculation endpoint
        recalc_res = client.post("/api/v1/risk/recalculate", headers=ciso_headers)
        assert recalc_res.status_code == 200
        assert recalc_res.json()["status"] == "SUCCESS"

        # ----------------------------------------------------
        # 5. Asset Inventory
        # ----------------------------------------------------
        assets_res = client.get("/api/v1/assets", headers=ciso_headers)
        assert assets_res.status_code == 200
        assets_data = assets_res.json()
        assert len(assets_data) == 100  # 100 enterprise assets
        # Check crown jewel payment database
        pay_db = next((a for a in assets_data if "Payment" in a["name"] or a["code"] == "DB-PAY-01"), None)
        assert pay_db is not None
        assert pay_db["criticality_score"] >= 90.0

        # ----------------------------------------------------
        # 6. Vulnerabilities & CISA KEV
        # ----------------------------------------------------
        vuln_res = client.get("/api/v1/vulnerabilities", headers=ciso_headers)
        assert vuln_res.status_code == 200
        vuln_data = vuln_res.json()
        assert vuln_data["stats"]["total"] == 500  # 500 CVEs total
        assert vuln_data["stats"]["critical"] == 50
        assert vuln_data["stats"]["high"] == 180
        assert vuln_data["stats"]["medium"] == 200
        assert vuln_data["stats"]["low"] == 70
        assert vuln_data["stats"]["cisa_known_exploited"] >= 6
        assert len(vuln_data["items"]) > 0

        # ----------------------------------------------------
        # 7. Threat Intelligence
        # ----------------------------------------------------
        threats_res = client.get("/api/v1/threats", headers=ciso_headers)
        assert threats_res.status_code == 200
        threats_data = threats_res.json()
        assert len(threats_data) >= 4

        # ----------------------------------------------------
        # 8. Security Controls
        # ----------------------------------------------------
        controls_res = client.get("/api/v1/controls", headers=ciso_headers)
        assert controls_res.status_code == 200
        controls_data = controls_res.json()
        assert len(controls_data) == 20  # 20 defense-in-depth controls

        # ----------------------------------------------------
        # 9. Financial Risk & FAIR SLE Breakdown
        # ----------------------------------------------------
        fin_res = client.get("/api/v1/financial/enterprise", headers=ciso_headers)
        assert fin_res.status_code == 200
        fin_data = fin_res.json()
        assert fin_data["expected_annual_loss"] == 46000000.0
        assert "loss_components" in fin_data
        assert fin_data["loss_components"]["total_potential_loss"] > 0

        # ----------------------------------------------------
        # 10. Monte Carlo Simulation (10,000 trials)
        # ----------------------------------------------------
        mc_res = client.get("/api/v1/financial/monte-carlo?iterations=10000", headers=ciso_headers)
        assert mc_res.status_code == 200
        mc_data = mc_res.json()
        assert mc_data["num_iterations"] == 10000
        assert "percentiles" in mc_data
        p = mc_data["percentiles"]
        assert p["p5"] <= p["p25"] <= p["p50_median"] <= p["p75"] <= p["p95"]
        assert not any(v != v for v in p.values()) # No NaN check

        # ----------------------------------------------------
        # 11. XGBoost Future Risk Prediction & SHAP
        # ----------------------------------------------------
        ai_res = client.get("/api/v1/ai/predictions", headers=ciso_headers)
        assert ai_res.status_code == 200
        ai_data = ai_res.json()
        assert ai_data["predicted_30d_risk_score"] > 0
        assert ai_data["predicted_30d_eal"] > 0
        assert len(ai_data["shap_explanation"]) >= 3
        # Check SHAP keys
        for item in ai_data["shap_explanation"]:
            assert "feature" in item
            assert "impact_value" in item or "pct_contribution" in item

        # ----------------------------------------------------
        # 12. Attack Path Engine
        # ----------------------------------------------------
        ap_res = client.get("/api/v1/attack-paths", headers=ciso_headers)
        assert ap_res.status_code == 200
        ap_data = ap_res.json()
        assert "critical_attack_paths" in ap_data
        assert len(ap_data["critical_attack_paths"]) >= 1
        main_path = ap_data["critical_attack_paths"][0]
        assert main_path["path_length"] >= 5
        assert main_path["path_risk_score"] >= 90.0
        assert main_path["modeled_financial_impact"] > 0  # Dynamically calculated from FAIR engine

        # ----------------------------------------------------
        # 13. OR-Tools Knapsack Optimization at ₹1.00 Crore Budget
        # ----------------------------------------------------
        opt_res = client.post("/api/v1/optimization/run", json={"budget": 10000000.0}, headers=ciso_headers)
        assert opt_res.status_code == 200
        opt_data = opt_res.json()
        run_id = opt_data["run_id"]
        result = opt_data["optimization_result"]
        assert result["total_investment"] <= 10000000.0
        assert result["total_investment"] > 0
        assert result["modeled_risk_reduction"] > 0
        assert result["projected_modeled_risk"] >= 0
        assert len(result["selected_controls"]) >= 1

        # ----------------------------------------------------
        # 14. Stress-Test Diminishing Returns Curve (₹25L to ₹5Cr)
        # ----------------------------------------------------
        stress_res = client.get("/api/v1/optimization/stress-test", headers=ciso_headers)
        assert stress_res.status_code == 200
        curve = stress_res.json()["stress_test_curve"]
        assert len(curve) >= 6
        # Check budget constraint holds across all points
        for pt in curve:
            assert pt["total_invested"] <= pt["budget"]

        # ----------------------------------------------------
        # 15. What-If Scenario Simulation
        # ----------------------------------------------------
        whatif_res = client.post("/api/v1/scenarios/simulate", json={
            "mfa_coverage": 100.0,
            "edr_coverage": 95.0,
            "patch_cadence_score": 90.0,
            "network_segmentation": 85.0
        }, headers=ciso_headers)
        assert whatif_res.status_code == 200
        whatif_data = whatif_res.json()
        assert whatif_data["simulated_modeled_risk"] < 46000000.0
        assert whatif_data["modeled_risk_reduction"] > 0

        # ----------------------------------------------------
        # 16. CISO Approval & RBAC enforcement
        # ----------------------------------------------------
        # Security Analyst attempt to approve (MUST FAIL WITH 403)
        analyst_approve = client.post("/api/v1/optimization/approve", json={
            "optimization_run_id": run_id,
            "approval_notes": "Attempted by analyst"
        }, headers=analyst_headers)
        assert analyst_approve.status_code == 403

        # Authorized CISO approval (MUST SUCCEED 200)
        ciso_approve = client.post("/api/v1/optimization/approve", json={
            "optimization_run_id": run_id,
            "approval_notes": "Authorized by CISO for SIH FY26 deployment."
        }, headers=ciso_headers)
        assert ciso_approve.status_code == 200
        approve_data = ciso_approve.json()
        assert approve_data["status"] == "APPROVED"
        assert "blockchain_transaction_id" in approve_data

        # ----------------------------------------------------
        # 17. Blockchain Audit & SHA-256 Tamper Test
        # ----------------------------------------------------
        bc_res = client.get("/api/v1/blockchain/blocks", headers=ciso_headers)
        assert bc_res.status_code == 200
        blocks = bc_res.json()["blocks"]
        assert len(blocks) >= 2

        # Verify integrity of approved run
        verify_res = client.post(f"/api/v1/blockchain/verify/{run_id}", headers=ciso_headers)
        assert verify_res.status_code == 200
        assert verify_res.json()["verification_status"] == "VERIFIED"

        # Tamper Test Sandbox
        tamper_res = client.post("/api/v1/blockchain/tamper-test", json={
            "tampered_risk_score": 15.0,
            "tampered_eal": 500000.0
        }, headers=ciso_headers)
        assert tamper_res.status_code == 200
        tamper_data = tamper_res.json()
        assert tamper_data["verification_result"] == "TAMPERING_DETECTED"
        assert tamper_data["is_valid"] is False

        # ----------------------------------------------------
        # 18. Compliance Frameworks
        # ----------------------------------------------------
        comp_res = client.get("/api/v1/compliance", headers=ciso_headers)
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert "findings" in comp_data
        assert "frameworks_supported" in comp_data
        assert any("NIST" in name for name in comp_data["frameworks_supported"])
        assert any("ISO" in name for name in comp_data["frameworks_supported"])

        # ----------------------------------------------------
        # 19. Executive Board Reports
        # ----------------------------------------------------
        report_res = client.post("/api/v1/reports/generate", json={
            "report_type": "EXECUTIVE_BOARD_RISK_REPORT"
        }, headers=ciso_headers)
        assert report_res.status_code == 200
        report_data = report_res.json()
        assert "executive_summary" in report_data
        assert "key_metrics" in report_data

        # ----------------------------------------------------
        # 20. Telemetry Connectors
        # ----------------------------------------------------
        int_res = client.get("/api/v1/integrations/status", headers=ciso_headers)
        assert int_res.status_code == 200
        int_data = int_res.json()
        connector_names = [c["name"] for c in int_data.get("connectors", [])]
        assert any("Wazuh" in name for name in connector_names)
        assert any("OpenVAS" in name for name in connector_names)
        assert any("CISA" in name for name in connector_names)

        # ----------------------------------------------------
        # 21. AI Assistant
        # ----------------------------------------------------
        asst_res = client.post("/api/v1/assistant/query", json={
            "query": "What is our current financial exposure and budget recommendation?"
        }, headers=ciso_headers)
        assert asst_res.status_code == 200
        asst_data = asst_res.json()
        assert "answer" in asst_data
        assert len(asst_data["answer"]) > 20

        # ----------------------------------------------------
        # 22. 18-Step SIH Master Demo Controller
        # ----------------------------------------------------
        steps_res = client.get("/api/v1/demo/steps", headers=ciso_headers)
        assert steps_res.status_code == 200
        assert steps_res.json()["total_steps"] == 18

        for s in range(1, 19):
            step_exec = client.post(f"/api/v1/demo/step/{s}", headers=ciso_headers)
            assert step_exec.status_code == 200
            assert step_exec.json()["current_step"] == s

        # Reset back to baseline for subsequent test runs
        client.post("/api/v1/demo/reset", headers=ciso_headers)

        print("\n\n>>> ALL 22 SYSTEM & SIH READINESS AUDIT TESTS PASSED SUCCESSFULLY! <<<\n")
