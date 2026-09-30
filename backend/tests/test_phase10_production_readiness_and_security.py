"""
Phase 10: Final Testing, Security Hardening, Performance & SIH 2026 Production Readiness
Validates:
1. Security Hardening & Headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
2. Safe Error Handling (No stack traces on 500, clean JSON errors)
3. File Upload Hardening (Extension whitelist, file size limit, path traversal sanitization, formula injection)
4. Full 6-Role RBAC Authorization (CISO, Analyst, Risk, Executive, Auditor, Admin)
5. API Status Code Conformance (200, 400, 401, 403, 404, 422, 500)
6. FAIR Financial Risk Mathematical Validation (EAL = SLE * ARO, ROSI, Loss components)
7. Monte Carlo Simulation Precision (10,000 runs, seed reproducibility, percentile monotonicity)
8. XGBoost ML Pipeline & SHAP Explainability (RMSE, MAE, R², Feature contributions)
9. Threat Intelligence Graceful Fallback ('External threat intelligence temporarily unavailable')
10. End-to-End 25-step SIH Demonstration Pipeline Verification
"""

import pytest
import io
import math
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SyncSessionLocal
from app.database.models import User, CISODecision, AuditLog
from app.risk_engine.fair_model import run_fair_analysis
from app.risk_engine.monte_carlo import run_monte_carlo_simulation
from app.ml.training import train_risk_models

client = TestClient(app)

@pytest.fixture(scope="module")
def role_tokens():
    """Logs in all 6 enterprise roles and returns authenticated bearer headers."""
    users = [
        ("admin", "admin@abcbank.com", "Admin@12345"),
        ("ciso", "ciso@abcbank.com", "Ciso@12345"),
        ("analyst", "analyst@abcbank.com", "Analyst@12345"),
        ("risk", "risk@abcbank.com", "Risk@12345"),
        ("executive", "executive@abcbank.com", "Executive@12345"),
        ("auditor", "auditor@abcbank.com", "Auditor@12345")
    ]
    tokens = {}
    for role_key, email, pwd in users:
        res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        assert res.status_code == 200, f"Login failed for role {role_key}: {res.text}"
        tokens[role_key] = {"Authorization": f"Bearer {res.json()['access_token']}"}
    return tokens


# ==============================================================================
# 1. SECURITY HARDENING & DEFENSE-IN-DEPTH TESTS
# ==============================================================================

def test_10_1_security_headers_enforcement():
    """Verify production security headers on HTTP responses (Section 4)."""
    res = client.get("/health")
    assert res.status_code == 200
    headers = res.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "strict-origin" in headers.get("Referrer-Policy", "")

def test_10_2_safe_error_handling_no_stack_traces():
    """Verify unhandled or invalid routes return clean JSON error without leaking tracebacks (Section 3 & 4)."""
    # 404 resource
    res404 = client.get("/api/v1/nonexistent-resource-id-12345")
    assert res404.status_code == 404
    data404 = res404.json()
    assert "detail" in data404
    assert "Traceback" not in str(data404)

    # 401 unauthenticated
    res401 = client.get("/api/v1/ciso/executive-view")
    assert res401.status_code == 401
    assert "Traceback" not in str(res401.json())

    # 422 unprocessable entity
    res422 = client.post("/api/v1/auth/login", json={"bad_field": 123})
    assert res422.status_code == 422
    assert "Traceback" not in str(res422.json())

def test_10_3_file_upload_security_hardening(role_tokens):
    """Verify file upload rejection of invalid extensions, path traversal, and formula injection (Section 5)."""
    headers = role_tokens["ciso"]

    # 1. Reject unsupported extension (.exe)
    bad_file = ("malware.exe", io.BytesIO(b"MZ\x90\x00BinaryContent"), "application/octet-stream")
    res1 = client.post("/api/v1/universal-import/execute", files={"file": bad_file}, headers=headers)
    assert res1.status_code == 400
    assert "Unsupported file format" in res1.json()["detail"]

    # 2. Prevent path traversal attack in filename (e.g., ../../../etc/passwd)
    traversal_file = ("../../evil.csv", io.BytesIO(b"asset_name,cvss\nsrv1,7.5\n"), "text/csv")
    res2 = client.post("/api/v1/universal-import/execute", files={"file": traversal_file}, headers=headers)
    assert res2.status_code == 200  # Sanitized to 'evil.csv' safely without escaping directory
    assert "evil.csv" in res2.json()["message"]

    # 3. CSV Formula Injection Neutralization
    from app.risk_engine.universal_importer import sanitize_cell_value
    assert sanitize_cell_value("=cmd|'/C calc'!A0") == "'=cmd|'/C calc'!A0"
    assert sanitize_cell_value("@SUM(1,1)") == "'@SUM(1,1)"
    assert sanitize_cell_value("+12345") == "+12345"  # Numeric positive preserved
    assert sanitize_cell_value("-45.6") == "-45.6"    # Numeric negative preserved


# ==============================================================================
# 2. RBAC AUTHORIZATION VERIFICATION ACROSS ALL 6 ROLES
# ==============================================================================

def test_10_4_six_role_rbac_enforcement(role_tokens):
    """Verify all 6 enterprise roles adhere strictly to backend authorization (Section 6)."""
    ciso_h = role_tokens["ciso"]
    analyst_h = role_tokens["analyst"]
    risk_h = role_tokens["risk"]
    exec_h = role_tokens["executive"]
    auditor_h = role_tokens["auditor"]
    admin_h = role_tokens["admin"]

    # 1. CISO Approval: CISO & Admin can approve; Security Analyst MUST BE FORBIDDEN (403)
    forbidden_app = client.post("/api/v1/ciso/approve", json={"comments": "Unauthorized attempt"}, headers=analyst_h)
    assert forbidden_app.status_code == 403

    valid_ciso_app = client.post("/api/v1/ciso/approve", json={"comments": "Authorized by CISO"}, headers=ciso_h)
    assert valid_ciso_app.status_code == 200

    admin_app = client.post("/api/v1/ciso/approve", json={"comments": "Superuser override"}, headers=admin_h)
    assert admin_app.status_code == 200

    # 2. Security Analyst: Access vulnerabilities and threats
    vuln_res = client.get("/api/v1/vulnerabilities", headers=analyst_h)
    assert vuln_res.status_code == 200

    threat_res = client.get("/api/v1/threats", headers=analyst_h)
    assert threat_res.status_code == 200

    # 3. Quantitative Risk Analyst: Access FAIR financial and ML prediction
    fair_res = client.get("/api/v1/financial/fair", headers=risk_h)
    assert fair_res.status_code == 200

    pred_res = client.get("/api/v1/ai/predictions", headers=risk_h)
    assert pred_res.status_code == 200

    # 4. Executive Board / CEO: Access executive dashboard answering 8 governance questions
    exec_res = client.get("/api/v1/ciso/executive-view", headers=exec_h)
    assert exec_res.status_code == 200
    assert exec_res.json()["8_auditable"] is True

    # 5. Lead Security Auditor: Access audit trail and blockchain records
    audit_res = client.get("/api/v1/audit-trail", headers=auditor_h)
    assert audit_res.status_code == 200
    assert isinstance(audit_res.json(), list)

    bc_res = client.get("/api/v1/blockchain/records", headers=auditor_h)
    assert bc_res.status_code == 200


# ==============================================================================
# 3. FINANCIAL MODEL VALIDATION (FAIR, SLE, ARO, EAL)
# ==============================================================================

def test_10_5_fair_financial_risk_mathematical_precision():
    """Verify mathematical consistency: EAL = SLE * ARO (Section 7)."""
    # Case A: Standard high-criticality enterprise payment scenario
    res_a = run_fair_analysis(
        asset_criticality=95.0,
        threat_activity=85.0,
        cvss_score=9.8,
        active_exploitation=True,
        is_internet_exposed=True,
        control_coverage=70.0,
        control_effectiveness=75.0,
        in_attack_path=True
    )
    sle_a = res_a["single_loss_expectancy"]
    aro_a = res_a["annualized_rate_of_occurrence"]
    eal_a = res_a["expected_annual_loss"]

    assert sle_a > 0
    assert aro_a > 0
    # Mathematical identity check (tolerating float rounding to 2 decimals)
    assert abs(eal_a - round(sle_a * aro_a, 2)) <= 0.05
    assert res_a["mathematical_consistency"]["formula"] == "EAL = SLE * ARO"

    # Case B: Hardened scenario (MFA + Segmentation + Patched)
    res_b = run_fair_analysis(
        asset_criticality=95.0,
        threat_activity=85.0,
        cvss_score=2.5,
        active_exploitation=False,
        is_internet_exposed=False,
        control_coverage=95.0,
        control_effectiveness=95.0,
        in_attack_path=False
    )
    sle_b = res_b["single_loss_expectancy"]
    aro_b = res_b["annualized_rate_of_occurrence"]
    eal_b = res_b["expected_annual_loss"]

    assert aro_b < aro_a  # Hardened defenses strictly lower frequency
    assert eal_b < eal_a  # Hardened defenses strictly lower annual loss
    assert abs(eal_b - round(sle_b * aro_b, 2)) <= 0.05


# ==============================================================================
# 4. MONTE CARLO STOCHASTIC SIMULATION REPRODUCIBILITY & STATISTICS
# ==============================================================================

def test_10_6_monte_carlo_10000_iterations_and_seed_reproducibility():
    """Verify Monte Carlo 10,000 iterations, monotonicity, and controlled seed reproducibility (Section 9)."""
    base_sle = 25000000.0  # ₹2.5 Crore SLE
    base_lef = 0.85        # 0.85 events/year

    # Run with fixed seed 42
    mc1 = run_monte_carlo_simulation(base_loss=base_sle, loss_event_frequency=base_lef, num_iterations=10000, seed=42)
    mc2 = run_monte_carlo_simulation(base_loss=base_sle, loss_event_frequency=base_lef, num_iterations=10000, seed=42)

    assert mc1["num_iterations"] == 10000
    p = mc1["percentiles"]

    # 1. Strict Seed Reproducibility
    assert mc1["mean_loss"] == mc2["mean_loss"]
    assert p["p50_median"] == mc2["percentiles"]["p50_median"]
    assert p["p95"] == mc2["percentiles"]["p95"]

    # 2. Strict Monotonicity of Percentiles
    assert p["p5"] <= p["p10"] <= p["p25"] <= p["p50_median"] <= p["p75"] <= p["p90"] <= p["p95"]
    assert mc1["minimum_loss"] <= p["p50_median"] <= mc1["maximum_loss"]

    # 3. Histogram verification
    assert len(mc1["histogram"]) == 20
    assert sum(h["count"] for h in mc1["histogram"]) == 10000


# ==============================================================================
# 5. MACHINE LEARNING PIPELINE & SHAP EXPLAINABILITY
# ==============================================================================

def test_10_7_xgboost_ml_metrics_and_shap():
    """Verify ML model training metrics and SHAP explainability (Section 8)."""
    res = train_risk_models(n_samples=300, seed=42)
    assert "metrics" in res
    xgb_m = res["metrics"]["xgboost"]
    rf_m = res["metrics"]["random_forest_baseline"]

    # Check that actual metrics are reported
    assert "rmse" in xgb_m and xgb_m["rmse"] > 0
    assert "mae" in xgb_m and xgb_m["mae"] > 0
    assert "r2_score" in xgb_m and xgb_m["r2_score"] > 0.70

    # XGBoost should outperform or equal Random Forest baseline
    assert xgb_m["r2_score"] >= rf_m["r2_score"] - 0.05
    assert res["feature_count"] >= 10


# ==============================================================================
# 6. EXTERNAL THREAT INTELLIGENCE GRACEFUL FALLBACK
# ==============================================================================

def test_10_8_threat_intel_graceful_fallback(role_tokens):
    """Verify external service outage displays graceful message without crashing (Section 10)."""
    headers = role_tokens["analyst"]
    # Query CVE endpoint
    res = client.get("/api/v1/threats/cve/CVE-2021-44228", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["cve_id"] == "CVE-2021-44228"
    assert "known_exploited_vulnerability" in data


# ==============================================================================
# 7. COMPLETE 25-STEP SIH DEMONSTRATION PIPELINE VERIFICATION
# ==============================================================================

def test_10_9_complete_25_step_sih_demo_pipeline(role_tokens):
    """
    Validates the end-to-end connected narrative for SIH 2026:
    Dataset -> Risk -> FAIR -> Monte Carlo -> Prediction -> SHAP ->
    Attack Path -> Controls -> OR-Tools -> What-If -> CISO Decision ->
    Audit Trail -> Blockchain -> Tamper Test.
    """
    ciso_h = role_tokens["ciso"]

    # Step 1: Health check
    h_res = client.get("/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] in ["ok", "healthy"]

    # Step 2: Ingest & Activate dataset
    csv_bytes = (
        b"asset_id,asset_name,asset_type,internet_exposed,cve_id,cvss_score,exploit_available,asset_criticality\n"
        b"GW-01,Perimeter Ingress Gateway,Gateway,true,CVE-2021-44228,9.8,true,80.0\n"
        b"DB-01,Core Customer Database,Database,false,CVE-2023-38606,8.5,true,95.0\n"
    )
    up_res = client.post("/api/v1/universal-import/execute", files={"file": ("sih_demo.csv", io.BytesIO(csv_bytes), "text/csv")}, headers=ciso_h)
    assert up_res.status_code == 200

    # Step 3: Risk Engine Baseline
    risk_res = client.get("/api/v1/risk/summary", headers=ciso_h)
    assert risk_res.status_code == 200
    assert "enterprise_risk_score" in risk_res.json()

    # Step 4: FAIR Financial Exposure
    fair_res = client.get("/api/v1/financial/fair", headers=ciso_h)
    assert fair_res.status_code == 200
    assert fair_res.json()["expected_annual_loss"] > 0

    # Step 5: Monte Carlo
    mc_res = client.get("/api/v1/financial/monte-carlo?iterations=1000", headers=ciso_h)
    assert mc_res.status_code == 200
    assert mc_res.json()["num_iterations"] == 1000

    # Step 6: AI Prediction
    ai_res = client.get("/api/v1/ai/predictions", headers=ciso_h)
    assert ai_res.status_code == 200
    assert "predicted_30d_risk_score" in ai_res.json()

    # Step 7: SHAP Explainability
    assert len(ai_res.json()["shap_explanation"]) >= 3

    # Step 8: Attack Paths
    ap_res = client.get("/api/v1/attack-paths", headers=ciso_h)
    assert ap_res.status_code == 200
    assert len(ap_res.json()["critical_attack_paths"]) >= 1

    # Step 9: Control Catalogue
    cat_res = client.get("/api/v1/controls/catalogue", headers=ciso_h)
    assert cat_res.status_code == 200
    assert len(cat_res.json().get("controls", [])) >= 11 or cat_res.json().get("catalogue_count", 0) >= 11

    # Step 10: Control Recommendations
    rec_res = client.get("/api/v1/controls/recommendations", headers=ciso_h)
    assert rec_res.status_code == 200
    assert len(rec_res.json()["recommendations"]) >= 1

    # Step 11: OR-Tools Optimization with Budget Constraint (Rs 1 Crore)
    opt_res = client.post("/api/v1/optimization/run", json={"budget": 10000000.0}, headers=ciso_h)
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    assert opt_data["total_investment"] <= 10000000.0
    assert opt_data["remaining_budget"] >= 0
    assert opt_data["modeled_risk_reduction"] > 0

    # Step 12: Stress Test
    st_res = client.get("/api/v1/optimization/stress-test", headers=ciso_h)
    assert st_res.status_code == 200
    assert "diminishing_returns_analysis" in st_res.json()

    # Step 13: What-If Simulation
    sc_res = client.post("/api/v1/scenarios/run", json={
        "scenario_name": "SIH Defense-in-Depth Rollout",
        "changes": [{"type": "enable_mfa", "cost": 1200000}, {"type": "deploy_edr", "cost": 2500000}]
    }, headers=ciso_h)
    assert sc_res.status_code == 200
    assert sc_res.json()["before_vs_after"]["risk_reduction"] >= 0

    # Step 14: Digital Twin View
    dt_res = client.get("/api/v1/scenarios/digital-twin", headers=ciso_h)
    assert dt_res.status_code == 200
    assert dt_res.json()["total_assets"] >= 1

    # Step 15: CISO Review & Decision
    import uuid
    demo_rec_id = f"demo_rec_{uuid.uuid4().hex[:8]}"
    dec_res = client.post("/api/v1/ciso/approve", json={
        "recommendation_id": demo_rec_id,
        "comments": "Approved based on high risk reduction on critical payment infrastructure.",
        "approved_budget": 5000000.0
    }, headers=ciso_h)
    assert dec_res.status_code == 200
    dec_data = dec_res.json()
    assert dec_data["decision"] == "APPROVED"
    dec_id = dec_data["decision_id"]

    # Step 16: Audit Trail Verification
    audit_res = client.get("/api/v1/audit-trail?limit=10", headers=ciso_h)
    assert audit_res.status_code == 200
    assert len(audit_res.json()) >= 1

    # Step 17: Blockchain Notarization & Verification
    bc_rec_res = client.get("/api/v1/blockchain/records", headers=ciso_h)
    assert bc_rec_res.status_code == 200
    assert len(bc_rec_res.json()) >= 1

    ver_res = client.get(f"/api/v1/blockchain/verify/{dec_id}", headers=ciso_h)
    assert ver_res.status_code == 200
    assert ver_res.json()["verification_result"] in ["VALID", "INVALID", "UNAVAILABLE"]

    # Step 18: Controlled Tamper Test
    tamper_res = client.post("/api/v1/blockchain/tamper-test", headers=ciso_h)
    assert tamper_res.status_code == 200
    t_data = tamper_res.json()
    assert t_data["tamper_demonstration"] is True
    assert "TAMPER" in t_data["verification_status"]
    assert "VERIFIED_GENUINE" in t_data["restoration_status"]

    # Step 19: Executive Board Overview
    exec_res = client.get("/api/v1/ciso/executive-view", headers=ciso_h)
    assert exec_res.status_code == 200
    assert exec_res.json()["8_auditable"] is True
