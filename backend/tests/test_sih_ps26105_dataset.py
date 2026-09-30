import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.risk_engine.sih_dataset_engine import sih_engine, format_inr

client = TestClient(app)

def test_sih_dataset_record_and_column_integrity():
    """Verify exact 15 records and 28 columns are loaded without distortion."""
    records = sih_engine.get_records()
    fields = sih_engine.get_fieldnames()

    assert len(records) == 15, f"Expected exactly 15 records, got {len(records)}"
    assert len(fields) == 28, f"Expected 28 CSV columns, got {len(fields)}"

    asset_ids = [r["asset_id"] for r in records]
    assert len(set(asset_ids)) == 15, "Found duplicate asset IDs!"
    expected_ids = [f"A{str(i).zfill(3)}" for i in range(1, 16)]
    assert asset_ids == expected_ids

def test_sih_dataset_signals_and_na_handling():
    """Verify N/A CVEs are preserved and specific asset records match expectations."""
    records = sih_engine.get_records()
    by_id = {r["asset_id"]: r for r in records}

    # A005 PAYMENT-GW-01
    a005 = by_id["A005"]
    assert a005["asset_name"] == "PAYMENT-GW-01"
    assert a005["cve_id"] == "CVE-2026-1005"
    assert a005["cvss_score"] == 9.9
    assert a005["vulnerability_severity"] == "Critical"
    assert a005["patch_available"] is True
    assert a005["exploit_available"] is True
    assert a005["vulnerability_age_days"] == 30
    assert a005["threat_intel_indicator"] == "Ransomware Group Targeting Sector"
    assert a005["threat_confidence_pct"] == 97.0
    assert a005["estimated_incident_probability"] == 0.42
    assert a005["potential_financial_impact_inr"] == 25000000.0
    assert a005["potential_financial_impact_label"] == "₹2.5 Cr" or "₹2.50 Cr" in a005["potential_financial_impact_label"]
    assert a005["estimated_mitigation_cost_inr"] == 600000.0
    assert a005["estimated_mitigation_cost_label"] == "₹6.0 Lakh" or "₹6 Lakh" in a005["estimated_mitigation_cost_label"]
    assert a005["control_effectiveness"] == 0.58
    assert a005["control_effectiveness_pct"] == "58%"

    # A009 & A010 have N/A CVE
    a009 = by_id["A009"]
    assert a009["cve_id"] == "N/A"
    assert a009["has_cve"] is False
    assert a009["cvss_score"] == 0.0

    a010 = by_id["A010"]
    assert a010["cve_id"] == "N/A"
    assert a010["has_cve"] is False
    assert a010["threat_intel_indicator"] == "Cloud Account Takeover Activity"
    assert a010["threat_confidence_pct"] == 94.0

    # IAM Deficits (Privileged Yes + MFA No)
    iam_deficits = [r["asset_id"] for r in records if r["iam_risk_flag"]]
    assert "A001" in iam_deficits
    assert "A003" in iam_deficits
    assert "A005" in iam_deficits
    assert "A010" in iam_deficits

def test_sih_overview_metrics_zero_hardcoding():
    """Verify overview metrics match dynamic calculations across the 15 records."""
    metrics = sih_engine.get_overview_metrics()
    records = sih_engine.get_records()

    assert metrics["dataset_origin"] == "SIH PS26105 TEST DATA"
    assert metrics["total_assets"] == 15
    assert metrics["total_fields"] == 28
    
    # Financial sums
    expected_impact = sum(r["potential_financial_impact_inr"] for r in records)
    assert metrics["total_modeled_financial_impact"] == expected_impact

    expected_mitigation = sum(r["estimated_mitigation_cost_inr"] for r in records)
    assert metrics["total_estimated_mitigation_cost"] == expected_mitigation

    # Control effectiveness
    expected_avg_ctrl = sum(r["control_effectiveness"] for r in records) / 15.0
    assert abs(metrics["average_control_effectiveness"] - round(expected_avg_ctrl * 100, 1)) < 0.01

def test_sih_monte_carlo_simulation():
    """Verify 10,000-run Monte Carlo simulation runs with realistic percentiles."""
    mc = sih_engine.run_monte_carlo(iterations=10000, seed=42)
    assert mc["simulations_count"] == 10000
    assert mc["expected_modeled_loss"] > 0
    assert mc["p95_loss"] >= mc["median_modeled_loss"]
    assert mc["p99_loss"] >= mc["p95_loss"]
    assert len(mc["distribution"]) > 0

def test_sih_mitigation_optimization():
    """Verify OR-Tools Knapsack optimization adheres to budget constraints."""
    opt = sih_engine.solve_mitigation_optimization(budget=1500000.0)
    assert opt["allocated_investment"] <= 1500000.0
    assert opt["modeled_risk_reduction"] > 0
    assert opt["risk_after_eal"] < opt["risk_before_eal"]
    assert len(opt["selected_controls"]) > 0

def test_sih_api_endpoints():
    """Verify FastAPI routes for SIH dataset return 200 OK and valid JSON."""
    res_overview = client.get("/api/v1/sih-dataset/overview")
    assert res_overview.status_code == 200
    assert res_overview.json()["total_assets"] == 15

    res_assets = client.get("/api/v1/sih-dataset/assets")
    assert res_assets.status_code == 200
    assert len(res_assets.json()) == 15

    res_vulns = client.get("/api/v1/sih-dataset/vulnerabilities")
    assert res_vulns.status_code == 200
    vulns = res_vulns.json()["vulnerabilities"]
    # All returned vulns must have non-N/A CVEs
    for v in vulns:
        assert v["cve_id"] != "N/A"

    res_fin = client.get("/api/v1/sih-dataset/financial-risk")
    assert res_fin.status_code == 200
    assert res_fin.json()["classification"] == "MODELED / ESTIMATED FINANCIAL INPUT"

    res_opt = client.post("/api/v1/sih-dataset/optimize", json={"budget": 1200000.0})
    assert res_opt.status_code == 200
    assert res_opt.json()["allocated_investment"] <= 1200000.0

    res_ciso = client.get("/api/v1/sih-dataset/ciso")
    assert res_ciso.status_code == 200
    assert "top_risk_assets" in res_ciso.json()
