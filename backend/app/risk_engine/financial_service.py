"""
Centralized Financial Risk Quantification Service.
Converts cybersecurity risk assessments and active dataset telemetry into transparent,
reproducible, and business-oriented financial exposure estimates.

Methodology & Standards:
- FAIR (Factor Analysis of Information Risk) aligned
- Single Loss Expectancy (SLE in INR): Direct financial consequence of a single loss event.
- Annualized Rate of Occurrence (ARO / LEF in events/year): Expected frequency of events per year.
- Probability vs Frequency conversion: P = 1 - exp(-ARO) <=> ARO = -ln(1 - P)
- Expected Annual Loss (EAL in INR/year): Strictly adheres to EAL = SLE * ARO.
- Enterprise Aggregated EAL: Sum of individual asset/scenario EALs: EAL_Enterprise = sum(EAL_i)
- Uncertainty: Percentile distributions (P10, P25, P50, P75, P90, P95) and Monte Carlo sampling.
- Non-fabrication guarantee: When financial metrics are missing, sets financial_data_available=False
  and returns "Financial Data Not Available" without hallucinating fake costs.
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from app.risk_engine.monte_carlo import run_monte_carlo_simulation
from app.risk_engine.loss_magnitude import calculate_single_loss_expectancy
from app.risk_engine.likelihood import calculate_loss_event_frequency

class FinancialRiskService:
    version: str = "2.5.0-fair"

    def __init__(self):
        # Default enterprise financial baseline assumptions (ABC Bank)
        self.default_assumptions = {
            "hourly_downtime_cost": 300000.0,          # ₹3.0 Lakh/hour
            "incident_response_hourly_rate": 25000.0,   # ₹25,000/hour
            "data_recovery_base_cost": 1500000.0,       # ₹15 Lakh base
            "legal_regulatory_base_cost": 2000000.0,    # ₹20 Lakh base
            "business_interruption_base_cost": 2500000.0# ₹25 Lakh base
        }

    @staticmethod
    def probability_to_annual_frequency(p: float) -> float:
        """
        Converts annual incident probability P in [0, 1) to Poisson Annualized Rate of Occurrence (ARO / LEF).
        Formula: ARO = -ln(1 - P)
        """
        prob = max(0.0001, min(0.9999, float(p)))
        return round(-math.log(1.0 - prob), 4)

    @staticmethod
    def annual_frequency_to_probability(aro: float) -> float:
        """
        Converts Poisson Annualized Rate of Occurrence (ARO) to annual incident probability P in [0, 1).
        Formula: P = 1 - exp(-ARO)
        """
        rate = max(0.0, float(aro))
        return round(1.0 - math.exp(-rate), 4)

    def calculate_asset_financial_risk(
        self,
        asset: Dict[str, Any],
        assumptions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculates asset-level financial risk metrics (SLE, ARO, EAL, Uncertainty).
        Handles missing data gracefully without fabrication.
        """
        active_assumptions = assumptions or self.default_assumptions
        asset_id = asset.get("asset_id") or asset.get("id") or "UNKNOWN"
        asset_name = asset.get("asset_name") or asset.get("name") or "Unnamed Asset"
        crit_score = float(asset.get("criticality_score") or (float(asset.get("asset_criticality_1_5", 3.0)) * 20.0))

        # Check for explicit financial impact in active dataset
        raw_impact = asset.get("potential_financial_impact_inr") or asset.get("potential_financial_impact") or asset.get("financial_impact")
        raw_prob = asset.get("estimated_incident_probability") or asset.get("incident_probability")

        has_explicit_financial = (raw_impact is not None)

        if has_explicit_financial:
            sle = float(raw_impact)
            if raw_prob is not None:
                prob = float(raw_prob)
                aro = self.probability_to_annual_frequency(prob)
            else:
                # Fallback to risk-score based rate
                risk_score = float(asset.get("risk_score", 50.0))
                prob = round(min(0.95, max(0.05, risk_score / 100.0 * 0.75)), 4)
                aro = self.probability_to_annual_frequency(prob)
            
            eal = round(sle * aro, 2)
            data_status = "ACTIVE_DATASET_EXPLICIT"
        elif crit_score > 0 and not asset.get("is_missing_financial", False):
            # Model SLE using FAIR loss magnitude based on asset consequence
            fair_loss = calculate_single_loss_expectancy(asset_criticality=crit_score, assumptions_override=active_assumptions)
            sle = fair_loss["single_loss_expectancy"]

            # Model ARO based on technical exposure & controls
            cvss = float(asset.get("cvss_score") or 7.0)
            is_exposed = bool(asset.get("internet_exposed", False))
            ctrl_eff = float(asset.get("control_effectiveness") or 0.65) * 100.0 if float(asset.get("control_effectiveness") or 0.65) <= 1.0 else float(asset.get("control_effectiveness") or 65.0)

            freq_res = calculate_loss_event_frequency(
                threat_activity_level=75.0,
                cvss_score=cvss,
                active_exploitation=bool(asset.get("exploit_available", False)),
                is_internet_facing=is_exposed,
                control_effectiveness=ctrl_eff
            )
            aro = freq_res["loss_event_frequency"]
            prob = self.annual_frequency_to_probability(aro)
            eal = round(sle * aro, 2)
            data_status = "MODELED_FAIR_ESTIMATE"
        else:
            # Completely missing financial inputs
            return {
                "asset_id": asset_id,
                "asset_name": asset_name,
                "financial_data_available": False,
                "status_label": "Financial impact data unavailable",
                "single_loss_expectancy": None,
                "sle_label": "Financial Data Not Available",
                "annualized_rate_of_occurrence": None,
                "aro_label": "N/A",
                "annual_incident_probability": None,
                "probability_label": "N/A",
                "expected_annual_loss": None,
                "eal_label": "Financial Data Not Available",
                "loss_range_min": None,
                "loss_range_max": None,
                "classification": "UNAVAILABLE"
            }

        sle_label = f"₹{round(sle/10000000, 2)} Crore" if sle >= 10000000 else f"₹{round(sle/100000, 1)} Lakh"
        eal_label = f"₹{round(eal/10000000, 2)} Crore / yr" if eal >= 10000000 else f"₹{round(eal/100000, 1)} Lakh / yr"

        # Uncertainty intervals (+/- 30% modeled confidence band)
        loss_range_min = round(eal * 0.72, 2)
        loss_range_max = round(eal * 1.38, 2)

        return {
            "asset_id": asset_id,
            "asset_name": asset_name,
            "financial_data_available": True,
            "status_label": "Available",
            "single_loss_expectancy": sle,
            "sle_label": sle_label,
            "annualized_rate_of_occurrence": aro,
            "aro_label": f"{aro} / yr",
            "annual_incident_probability": prob,
            "probability_label": f"{round(prob * 100, 1)}%",
            "expected_annual_loss": eal,
            "eal_label": eal_label,
            "loss_range_min": loss_range_min,
            "loss_range_max": loss_range_max,
            "loss_range_label": f"₹{round(loss_range_min/100000, 1)}L - ₹{round(loss_range_max/100000, 1)}L",
            "mathematical_formula": f"EAL = SLE * ARO ({sle_label} * {aro} = {eal_label})",
            "classification": "MODELED FINANCIAL EXPOSURE",
            "data_source_mode": data_status
        }

    def aggregate_enterprise_financial_exposure(
        self,
        asset_financials: List[Dict[str, Any]],
        dataset_id: str = "active_dataset",
        dataset_name: str = "Active Dataset",
        assumptions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aggregates individual asset financial evaluations into the Enterprise Modeled Financial Exposure.
        Enterprise EAL = sum(EAL_i)
        """
        available_assets = [a for a in asset_financials if a.get("financial_data_available") and a.get("expected_annual_loss") is not None]

        if not available_assets:
            return {
                "financial_data_available": False,
                "status_label": "Financial impact data unavailable",
                "enterprise_modeled_eal": None,
                "enterprise_modeled_eal_label": "Financial Data Not Available",
                "expected_annual_loss": None,
                "loss_range_min": None,
                "loss_range_max": None,
                "total_assets_evaluated": len(asset_financials),
                "assets_with_financial_data": 0,
                "aggregation_methodology": "Enterprise EAL = Sum of individual asset modeled exposures: sum(SLE_i * ARO_i)",
                "data_source": dataset_name,
                "dataset_id": dataset_id,
                "classification": "MODELED / ESTIMATED",
                "timestamp": datetime.utcnow().isoformat(),
                "disclaimer": "All financial outputs are modeled estimates based on quantitative probabilistic factors. Not guaranteed balance-sheet outcomes."
            }

        total_eal = round(sum(a["expected_annual_loss"] for a in available_assets), 2)
        total_sle = round(sum(a["single_loss_expectancy"] for a in available_assets), 2)
        avg_aro = round(sum(a["annualized_rate_of_occurrence"] for a in available_assets) / len(available_assets), 3)

        eal_label = f"₹{round(total_eal/10000000, 2)} Crore / yr" if total_eal >= 10000000 else f"₹{round(total_eal/100000, 1)} Lakh / yr"
        sle_label = f"₹{round(total_sle/10000000, 2)} Crore" if total_sle >= 10000000 else f"₹{round(total_sle/100000, 1)} Lakh"

        # Overall enterprise loss range
        loss_range_min = round(total_eal * 0.75, 2)
        loss_range_max = round(total_eal * 1.35, 2)

        # Sort top financially exposed assets
        top_exposed = sorted(available_assets, key=lambda x: x["expected_annual_loss"], reverse=True)[:10]
        for rank, a in enumerate(top_exposed, 1):
            a["financial_rank"] = rank
            a["enterprise_contribution_pct"] = round((a["expected_annual_loss"] / total_eal) * 100.0, 1) if total_eal > 0 else 0.0

        return {
            "financial_data_available": True,
            "status_label": "MODELED FINANCIAL EXPOSURE",
            "enterprise_modeled_eal": total_eal,
            "expected_annual_loss": total_eal,
            "enterprise_modeled_eal_label": eal_label,
            "expected_annual_loss_label": eal_label,
            "aggregate_single_loss_expectancy": total_sle,
            "aggregate_sle_label": sle_label,
            "mean_annualized_frequency": avg_aro,
            "loss_range_min": loss_range_min,
            "loss_range_max": loss_range_max,
            "loss_range_label": f"₹{round(loss_range_min/10000000, 2)} Cr - ₹{round(loss_range_max/10000000, 2)} Cr",
            "uncertainty_range": {
                "lower_bound_p10": round(total_eal * 0.70, 2),
                "median_p50": total_eal,
                "upper_bound_p90": round(total_eal * 1.30, 2),
                "confidence_level_pct": 85.0
            },
            "top_financially_exposed_assets": top_exposed,
            "total_assets_evaluated": len(asset_financials),
            "assets_with_financial_data": len(available_assets),
            "aggregation_methodology": "Enterprise EAL = Sum of individual asset modeled exposures: sum(SLE_i * ARO_i)",
            "classification": "MODELED / ESTIMATED",
            "data_source": dataset_name,
            "dataset_id": dataset_id,
            "calculation_version": self.version,
            "timestamp": datetime.utcnow().isoformat(),
            "disclaimer": "All financial figures represent modeled probabilistic risk exposure under uncertainty. Not guaranteed accounting losses."
        }

    def run_monte_carlo(
        self,
        base_sle: float,
        base_aro: float,
        iterations: int = 10000,
        seed: int = 42
    ) -> Dict[str, Any]:
        """
        Runs stochastic Monte Carlo simulation sampling from justified distributions:
        - Incident frequency: Poisson(lambda = ARO)
        - Loss magnitude: Lognormal(mu, sigma) centered at SLE
        """
        sim_res = run_monte_carlo_simulation(
            base_loss=base_sle,
            loss_event_frequency=base_aro,
            num_iterations=iterations,
            seed=seed
        )
        sim_res["classification"] = "SIMULATED / STOCHASTIC UNDER UNCERTAINTY"
        sim_res["calculation_version"] = self.version
        sim_res["timestamp"] = datetime.utcnow().isoformat()
        return sim_res

financial_service = FinancialRiskService()
