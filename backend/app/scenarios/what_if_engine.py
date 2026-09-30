"""
What-If / Digital Twin Scenario Analysis Engine.
Implements real, dynamic quantitative risk simulations using the centralized FAIR risk engine.

Simulates specific interventions:
1. Critical vulnerability patching (Updates CVSS & Exploitability -> Updates LEF & EAL)
2. Privileged-account MFA (Updates IAM Control Strength -> Updates LEF & EAL)
3. EDR / XDR Autonomous Detection (Updates Host Controls & MTTD/MTTC -> Updates LEF, SLE & EAL)
4. Network micro-segmentation (Breaks Lateral Attack Path -> Updates LEF & EAL)
5. Zero Trust Architecture (Updates Threat Ingress & Multi-Factor Verification -> Updates LEF & EAL)
6. Immutable backup (Cuts Outage Duration & Data Loss -> Updates SLE & EAL, LEF unchanged)
7. Reduced internet exposure (Removes Public Vector -> Updates TEF & LEF & EAL, SLE unchanged)
"""

from typing import Dict, Any, List, Optional
from app.risk_engine.fair_model import run_fair_analysis

INTERVENTION_CATALOG = {
    "patching": {
        "id": "patching",
        "name": "Critical Vulnerability Patching (Log4Shell & CVEs)",
        "category": "Vulnerability Management",
        "default_cost": 1500000.0,  # ₹15 Lakhs
        "description": "Rapid deployment of security updates (e.g., Log4j 2.17.1 / virtual patching at WAF) neutralizing remote code execution vectors.",
        "affected_assets": [
            "Internet-Facing App Gateway (PRD-WEB-01)",
            "Payment API Microservice (PAY-SVC-01)"
        ],
        "affected_attack_paths": [
            "PATH-001: Internet-to-Core-Payment-DB"
        ],
        "parameter_effect": {
            "cvss_score_after": 3.1,
            "active_exploitation_after": False,
            "control_coverage_delta": 15.0,
            "control_effectiveness_delta": 20.0,
            "sle_affected": False,
            "lef_affected": True,
            "rationale": "Removes the high-severity exploit vector. Asset valuation and potential impact if breached remain unchanged, but incident frequency drops drastically."
        }
    },
    "mfa": {
        "id": "mfa",
        "name": "Privileged-Account Hardware FIDO2 MFA",
        "category": "Identity & Access Management",
        "default_cost": 2000000.0,  # ₹20 Lakhs
        "description": "Enforce phishing-resistant hardware MFA on all domain administrators, API service accounts, and privileged bastion hosts.",
        "affected_assets": [
            "Active Directory / IAM Cluster (IAM-CORP-DC1)",
            "Payment API Microservice (PAY-SVC-01)"
        ],
        "affected_attack_paths": [
            "PATH-001: Internet-to-Core-Payment-DB",
            "PATH-003: Credential-Pivot-Admin"
        ],
        "parameter_effect": {
            "control_coverage_after": 98.0,
            "control_effectiveness_after": 95.0,
            "sle_affected": False,
            "lef_affected": True,
            "rationale": "Hardens identity authentication against credential theft and unauthorized lateral pivot. Asset loss magnitude remains unaffected."
        }
    },
    "edr": {
        "id": "edr",
        "name": "Next-Gen EDR / XDR Autonomous Containment",
        "category": "Endpoint & Threat Detection",
        "default_cost": 3500000.0,  # ₹35 Lakhs
        "description": "Deploy automated detection and endpoint isolation agents across 100% of servers, dropping MTTD from days to minutes.",
        "affected_assets": [
            "Payment App Server (PAY-APP-01)",
            "Payment API Microservice (PAY-SVC-01)",
            "Core Payment Database Cluster (DB-PAY-PRD-01)"
        ],
        "affected_attack_paths": [
            "PATH-001: Internet-to-Core-Payment-DB"
        ],
        "parameter_effect": {
            "control_coverage_after": 99.0,
            "control_effectiveness_after": 92.0,
            "ir_hours_after": 10.0,            # down from 40 hrs
            "outage_hours_after": 2.0,          # down from 8.0 hrs
            "sle_affected": True,
            "lef_affected": True,
            "rationale": "Autonomous endpoint isolation halts ransomware and payload execution (lowering LEF) while rapid containment cuts incident response engagement and business interruption downtime (lowering SLE)."
        }
    },
    "microsegmentation": {
        "id": "microsegmentation",
        "name": "Zero-Trust Network Micro-Segmentation",
        "category": "Network Security",
        "default_cost": 4000000.0,  # ₹40 Lakhs
        "description": "Enforce strict host-to-host cryptographic microsegmentation policies, preventing lateral movement from web tier to payment database.",
        "affected_assets": [
            "Payment App Server (PAY-APP-01)",
            "Payment API Microservice (PAY-SVC-01)",
            "Core Payment Database Cluster (DB-PAY-PRD-01)"
        ],
        "affected_attack_paths": [
            "PATH-001: Internet-to-Core-Payment-DB",
            "PATH-002: Lateral-DB-Pivot"
        ],
        "parameter_effect": {
            "in_attack_path_after": False,
            "control_effectiveness_delta": 25.0,
            "sle_affected": False,
            "lef_affected": True,
            "rationale": "Breaks the lateral traversal chain. Even if the web tier is compromised, the payment database cannot be reached laterally."
        }
    },
    "zero_trust": {
        "id": "zero_trust",
        "name": "Comprehensive Zero Trust Architecture (ZTA)",
        "category": "Enterprise Architecture",
        "default_cost": 6500000.0,  # ₹65 Lakhs
        "description": "Continuous contextual verification of identity, device health, and network telemetry with least-privilege dynamic access control.",
        "affected_assets": [
            "All Enterprise Production Nodes (PRD-WEB-01, PAY-SVC-01, PAY-APP-01, IAM-CORP-DC1, DB-PAY-PRD-01)"
        ],
        "affected_attack_paths": [
            "All Ingress & Lateral Attack Paths"
        ],
        "parameter_effect": {
            "in_attack_path_after": False,
            "control_coverage_after": 98.0,
            "control_effectiveness_after": 96.0,
            "threat_activity_delta": -30.0,
            "sle_affected": False,
            "lef_affected": True,
            "rationale": "Eliminates implicit trust across all zones, reducing threat likelihood and blocking multi-stage exploit chains."
        }
    },
    "immutable_backup": {
        "id": "immutable_backup",
        "name": "Air-Gapped Immutable Backups & Fast Restore",
        "category": "Resilience & Business Continuity",
        "default_cost": 2500000.0,  # ₹25 Lakhs
        "description": "Deploy WORM (Write Once Read Many) air-gapped immutable snapshot storage with sub-hour recovery orchestration.",
        "affected_assets": [
            "Core Payment Database Cluster (DB-PAY-PRD-01)"
        ],
        "affected_attack_paths": [
            "PATH-001: Ransomware / Data Destruction Extortion"
        ],
        "parameter_effect": {
            "outage_hours_after": 1.0,           # down from 8.0 hrs
            "data_recovery_base_cost_after": 200000.0,  # down from 15 Lakhs
            "sle_affected": True,
            "lef_affected": False,
            "rationale": "Backups do NOT reduce adversary attack frequency or vulnerability exploitability (LEF is unchanged). However, instant restoration from immutable snapshots halves downtime and eliminates extortion/data reconstruction costs (reducing SLE)."
        }
    },
    "reduced_exposure": {
        "id": "reduced_exposure",
        "name": "Attack Surface Reduction / Removed Internet Exposure",
        "category": "Perimeter Defense",
        "default_cost": 1000000.0,  # ₹10 Lakhs
        "description": "De-publish public administrative ports and migrate internal management APIs behind authenticated Zero-Trust App Connectors.",
        "affected_assets": [
            "Internet-Facing App Gateway (PRD-WEB-01)"
        ],
        "affected_attack_paths": [
            "PATH-001: Direct Internet Ingress"
        ],
        "parameter_effect": {
            "is_internet_exposed_after": False,
            "threat_activity_after": 35.0,  # internal threat level only
            "sle_affected": False,
            "lef_affected": True,
            "rationale": "Shielding the asset behind internal access brokers drops external threat event frequency by removing internet search engine / botnet indexing."
        }
    }
}


def get_available_interventions() -> List[Dict[str, Any]]:
    """Returns metadata for all available What-If interventions."""
    return [
        {
            "id": v["id"],
            "name": v["name"],
            "category": v["category"],
            "default_cost": v["default_cost"],
            "default_cost_label": f"₹{round(v['default_cost']/100000, 1)} Lakhs",
            "description": v["description"],
            "affected_assets": v["affected_assets"],
            "affected_attack_paths": v["affected_attack_paths"],
            "parameter_effect": v["parameter_effect"]
        }
        for v in INTERVENTION_CATALOG.values()
    ]


def calculate_what_if_scenario(
    intervention_id: str,
    custom_cost: Optional[float] = None,
    custom_baseline: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes a real Before -> Control -> After calculation using the centralized FAIR risk engine.
    Ensures strict adherence to the defined control-effectiveness model:
    - Patching / MFA / Zero Trust / Exposure -> Alters LEF
    - Immutable Backup -> Alters SLE (LEF unchanged)
    - EDR / XDR -> Alters both LEF and SLE
    """
    if intervention_id not in INTERVENTION_CATALOG:
        raise ValueError(f"Unknown intervention: {intervention_id}. Valid options: {list(INTERVENTION_CATALOG.keys())}")

    control_meta = INTERVENTION_CATALOG[intervention_id]
    effect = control_meta["parameter_effect"]
    cost = custom_cost if custom_cost is not None else control_meta["default_cost"]

    # 1. Baseline Parameters (Default Enterprise Profile: Log4Shell Vulnerable State)
    base_params = {
        "asset_criticality": 95.0,
        "threat_activity": 90.0,
        "cvss_score": 9.8,
        "active_exploitation": True,
        "is_internet_exposed": True,
        "control_coverage": 70.0,
        "control_effectiveness": 75.0,
        "in_attack_path": True,
        "assumptions_override": {
            "outage_hours": 8.0,
            "ir_hours": 40.0,
            "data_recovery_base_cost": 1500000.0
        }
    }
    if custom_baseline:
        base_params.update(custom_baseline)

    # 2. Compute BEFORE state using Centralized FAIR Risk Engine
    before_fair = run_fair_analysis(
        asset_criticality=base_params["asset_criticality"],
        threat_activity=base_params["threat_activity"],
        cvss_score=base_params["cvss_score"],
        active_exploitation=base_params["active_exploitation"],
        is_internet_exposed=base_params["is_internet_exposed"],
        control_coverage=base_params["control_coverage"],
        control_effectiveness=base_params["control_effectiveness"],
        in_attack_path=base_params["in_attack_path"],
        assumptions_override=base_params["assumptions_override"]
    )

    # 3. Apply Specific Control Adjustments (AFTER state)
    after_params = dict(base_params)
    after_assumptions = dict(base_params["assumptions_override"])

    if intervention_id == "patching":
        after_params["cvss_score"] = effect["cvss_score_after"]
        after_params["active_exploitation"] = effect["active_exploitation_after"]
        after_params["control_coverage"] = min(100.0, after_params["control_coverage"] + effect["control_coverage_delta"])
        after_params["control_effectiveness"] = min(100.0, after_params["control_effectiveness"] + effect["control_effectiveness_delta"])

    elif intervention_id == "mfa":
        after_params["control_coverage"] = effect["control_coverage_after"]
        after_params["control_effectiveness"] = effect["control_effectiveness_after"]

    elif intervention_id == "edr":
        after_params["control_coverage"] = effect["control_coverage_after"]
        after_params["control_effectiveness"] = effect["control_effectiveness_after"]
        after_assumptions["ir_hours"] = effect["ir_hours_after"]
        after_assumptions["outage_hours"] = effect["outage_hours_after"]

    elif intervention_id == "microsegmentation":
        after_params["in_attack_path"] = effect["in_attack_path_after"]
        after_params["control_effectiveness"] = min(100.0, after_params["control_effectiveness"] + effect["control_effectiveness_delta"])

    elif intervention_id == "zero_trust":
        after_params["in_attack_path"] = effect["in_attack_path_after"]
        after_params["control_coverage"] = effect["control_coverage_after"]
        after_params["control_effectiveness"] = effect["control_effectiveness_after"]
        after_params["threat_activity"] = max(10.0, after_params["threat_activity"] + effect["threat_activity_delta"])

    elif intervention_id == "immutable_backup":
        # LEF remains unchanged! Only SLE parameters change
        after_assumptions["outage_hours"] = effect["outage_hours_after"]
        after_assumptions["data_recovery_base_cost"] = effect["data_recovery_base_cost_after"]

    elif intervention_id == "reduced_exposure":
        after_params["is_internet_exposed"] = effect["is_internet_exposed_after"]
        after_params["threat_activity"] = effect["threat_activity_after"]

    after_params["assumptions_override"] = after_assumptions

    # 4. Compute AFTER state using Centralized FAIR Risk Engine
    after_fair = run_fair_analysis(
        asset_criticality=after_params["asset_criticality"],
        threat_activity=after_params["threat_activity"],
        cvss_score=after_params["cvss_score"],
        active_exploitation=after_params["active_exploitation"],
        is_internet_exposed=after_params["is_internet_exposed"],
        control_coverage=after_params["control_coverage"],
        control_effectiveness=after_params["control_effectiveness"],
        in_attack_path=after_params["in_attack_path"],
        assumptions_override=after_params["assumptions_override"]
    )

    # 5. Financial Delta & Return on Security Investment (ROSI)
    before_eal = before_fair["expected_annual_loss"]
    after_eal = after_fair["expected_annual_loss"]
    net_risk_reduction = round(before_eal - after_eal, 2)
    roi_percentage = round(((net_risk_reduction - cost) / max(1.0, cost)) * 100.0, 1) if cost > 0 else 0.0

    return {
        "intervention_id": intervention_id,
        "modeled_label": "MODELED WHAT-IF SIMULATION",
        "data_provenance": "MODEL OUTPUT (CALCULATED VIA CENTRALIZED FAIR ENGINE)",
        "before": {
            "loss_event_frequency": before_fair["loss_event_frequency"],
            "loss_event_frequency_label": f"{before_fair['loss_event_frequency']} incidents / year",
            "single_loss_expectancy": before_fair["single_loss_expectancy"],
            "single_loss_expectancy_label": f"₹{round(before_fair['single_loss_expectancy']/100000, 2)} Lakhs",
            "expected_annual_loss": before_eal,
            "expected_annual_loss_label": f"₹{round(before_eal/10000000, 2)} Cr" if before_eal >= 10000000 else f"₹{round(before_eal/100000, 2)} Lakhs",
            "annual_incident_probability": before_fair["annual_incident_probability"],
            "annual_incident_probability_label": f"{round(before_fair['annual_incident_probability'] * 100, 1)}%",
            "loss_components": before_fair["loss_breakdown"]
        },
        "control": {
            "control_id": control_meta["id"],
            "control_name": control_meta["name"],
            "category": control_meta["category"],
            "investment_cost": cost,
            "investment_cost_label": f"₹{round(cost/100000, 1)} Lakhs",
            "affected_assets": control_meta["affected_assets"],
            "affected_attack_paths": control_meta["affected_attack_paths"],
            "parameter_effect_model": effect["rationale"],
            "variables_changed": {
                "lef_changed": effect["lef_affected"],
                "sle_changed": effect["sle_affected"]
            }
        },
        "after": {
            "updated_loss_event_frequency": after_fair["loss_event_frequency"],
            "updated_loss_event_frequency_label": f"{after_fair['loss_event_frequency']} incidents / year",
            "updated_single_loss_expectancy": after_fair["single_loss_expectancy"],
            "updated_single_loss_expectancy_label": f"₹{round(after_fair['single_loss_expectancy']/100000, 2)} Lakhs",
            "updated_expected_annual_loss": after_eal,
            "updated_expected_annual_loss_label": f"₹{round(after_eal/10000000, 2)} Cr" if after_eal >= 10000000 else f"₹{round(after_eal/100000, 2)} Lakhs",
            "updated_annual_incident_probability": after_fair["annual_incident_probability"],
            "updated_annual_incident_probability_label": f"{round(after_fair['annual_incident_probability'] * 100, 1)}%",
            "modeled_risk_reduction": net_risk_reduction,
            "modeled_risk_reduction_label": f"₹{round(net_risk_reduction/10000000, 2)} Cr" if net_risk_reduction >= 10000000 else f"₹{round(net_risk_reduction/100000, 2)} Lakhs",
            "return_on_security_investment_percentage": roi_percentage,
            "loss_components": after_fair["loss_breakdown"]
        },
        "mathematical_audit": {
            "formula_before": f"EAL_before ({before_eal}) = SLE_before ({before_fair['single_loss_expectancy']}) × LEF_before ({before_fair['loss_event_frequency']})",
            "formula_after": f"EAL_after ({after_eal}) = SLE_after ({after_fair['single_loss_expectancy']}) × LEF_after ({after_fair['loss_event_frequency']})",
            "delta_reduction": f"Net Risk Reduction = EAL_before - EAL_after = ₹{net_risk_reduction:,.2f} / year"
        }
    }


def simulate_flexible_scenario(
    changes: List[Dict[str, Any]],
    baseline_override: Optional[Dict[str, Any]] = None,
    budget: float = 10000000.0
) -> Dict[str, Any]:
    """
    Applies an arbitrary list of hypothetical changes to an isolated state (Section 8.2 & 8.4).
    Calculates Before vs Scenario state using FAIR quantitative risk analysis without modifying production data.
    """
    # 1. Capture Current Baseline State (Section 8.3)
    base_params = {
        "asset_criticality": 95.0,
        "threat_activity": 90.0,
        "cvss_score": 9.8,
        "active_exploitation": True,
        "is_internet_exposed": True,
        "control_coverage": 70.0,
        "control_effectiveness": 75.0,
        "in_attack_path": True,
        "assumptions_override": {
            "outage_hours": 8.0,
            "ir_hours": 40.0,
            "data_recovery_base_cost": 1500000.0
        }
    }
    if baseline_override:
        base_params.update(baseline_override)

    before_fair = run_fair_analysis(
        asset_criticality=base_params["asset_criticality"],
        threat_activity=base_params["threat_activity"],
        cvss_score=base_params["cvss_score"],
        active_exploitation=base_params["active_exploitation"],
        is_internet_exposed=base_params["is_internet_exposed"],
        control_coverage=base_params["control_coverage"],
        control_effectiveness=base_params["control_effectiveness"],
        in_attack_path=base_params["in_attack_path"],
        assumptions_override=base_params["assumptions_override"]
    )
    current_eal = before_fair["expected_annual_loss"]
    current_risk_score = round(min(100.0, (before_fair["loss_event_frequency"] / 2.0) * 100.0), 1)

    # 2. Apply hypothetical changes to isolated scenario state (Section 8.4)
    after_params = dict(base_params)
    after_assumptions = dict(base_params["assumptions_override"])
    total_investment_cost = 0.0
    affected_assets_set = set()
    attack_paths_affected = []
    simulated_budget = budget

    for chg in changes:
        chg_type = chg.get("change_type", chg.get("type", "")).lower()
        cost = float(chg.get("cost", 0.0))

        if chg_type in ("patch_vulnerability", "remove_vulnerability"):
            after_params["cvss_score"] = float(chg.get("cvss_score", 2.5))
            after_params["active_exploitation"] = False
            total_investment_cost += (cost or 1500000.0)
            affected_assets_set.add("Internet-Facing Web Tier (PRD-WEB-01)")
            affected_assets_set.add("Payment API Gateway (PAY-SVC-01)")
            attack_paths_affected.append("PATH-001: External Exploit -> Core Payment DB (Neutralized)")

        elif chg_type == "enable_mfa":
            after_params["control_coverage"] = min(100.0, after_params["control_coverage"] + 25.0)
            after_params["control_effectiveness"] = min(100.0, after_params["control_effectiveness"] + 20.0)
            total_investment_cost += (cost or 1200000.0)
            affected_assets_set.add("Active Directory Domain Controllers (IAM-CORP-DC1)")
            attack_paths_affected.append("PATH-003: Credential Pivot Chain (Severed)")

        elif chg_type == "deploy_edr":
            after_params["control_coverage"] = min(100.0, after_params["control_coverage"] + 20.0)
            after_assumptions["ir_hours"] = 10.0
            after_assumptions["outage_hours"] = 2.0
            total_investment_cost += (cost or 2500000.0)
            affected_assets_set.add("Payment App Server (PAY-APP-01)")
            affected_assets_set.add("Employee Workstation Fleet")
            attack_paths_affected.append("PATH-004: Ransomware Extortion Chain (Isolated)")

        elif chg_type == "add_network_segmentation":
            after_params["in_attack_path"] = False
            after_params["control_effectiveness"] = min(100.0, after_params["control_effectiveness"] + 15.0)
            total_investment_cost += (cost or 2000000.0)
            affected_assets_set.add("Core Payment Database Cluster (DB-PAY-PRD-01)")
            attack_paths_affected.append("PATH-001: Internet-to-Core-Payment-DB (Broken)")

        elif chg_type == "improve_control_effectiveness":
            delta = float(chg.get("delta", 15.0))
            after_params["control_effectiveness"] = min(100.0, after_params["control_effectiveness"] + delta)
            total_investment_cost += (cost or 800000.0)

        elif chg_type == "add_security_control":
            red_boost = float(chg.get("effectiveness_boost", 10.0))
            after_params["control_coverage"] = min(100.0, after_params["control_coverage"] + red_boost)
            total_investment_cost += (cost or 1000000.0)
            if chg.get("asset"):
                affected_assets_set.add(str(chg.get("asset")))

        elif chg_type == "increase_budget":
            simulated_budget += float(chg.get("delta_budget", 5000000.0))

        elif chg_type == "decrease_budget":
            simulated_budget = max(0.0, simulated_budget - float(chg.get("delta_budget", 5000000.0)))

        elif chg_type == "change_asset_criticality":
            after_params["asset_criticality"] = float(chg.get("criticality", 70.0))
            if chg.get("asset"):
                affected_assets_set.add(str(chg.get("asset")))

        elif chg_type == "disable_control":
            # Control failure / bypass simulation
            after_params["control_coverage"] = max(10.0, after_params["control_coverage"] - 40.0)
            after_params["control_effectiveness"] = max(15.0, after_params["control_effectiveness"] - 35.0)
            after_params["in_attack_path"] = True
            affected_assets_set.add("Compromised Zone")
            attack_paths_affected.append("Lateral Movement Opened (Control Disabled)")

    after_params["assumptions_override"] = after_assumptions

    # 3. Compute AFTER state using Centralized FAIR Risk Engine
    after_fair = run_fair_analysis(
        asset_criticality=after_params["asset_criticality"],
        threat_activity=after_params["threat_activity"],
        cvss_score=after_params["cvss_score"],
        active_exploitation=after_params["active_exploitation"],
        is_internet_exposed=after_params["is_internet_exposed"],
        control_coverage=after_params["control_coverage"],
        control_effectiveness=after_params["control_effectiveness"],
        in_attack_path=after_params["in_attack_path"],
        assumptions_override=after_params["assumptions_override"]
    )
    scenario_eal = after_fair["expected_annual_loss"]
    scenario_risk_score = round(min(100.0, (after_fair["loss_event_frequency"] / 2.0) * 100.0), 1)

    eal_reduction = round(current_eal - scenario_eal, 2)
    risk_change = round(scenario_risk_score - current_risk_score, 1)

    import uuid
    scenario_sim_id = f"scen_{uuid.uuid4().hex[:8]}"

    comp_dict = {
        "current_risk": current_risk_score,
        "scenario_risk": scenario_risk_score,
        "risk_reduction": round(max(0.0, current_risk_score - scenario_risk_score), 1),
        "risk_change": risk_change,
        "current_eal": current_eal,
        "scenario_eal": scenario_eal,
        "eal_reduction": eal_reduction,
        "investment_cost": total_investment_cost,
        "financial_exposure_reduction": eal_reduction
    }

    fin_impact = {
        "current_eal": current_eal,
        "scenario_eal": scenario_eal,
        "eal_reduction": eal_reduction,
        "investment_cost": total_investment_cost,
        "modeled_financial_exposure_reduction": eal_reduction
    }

    return {
        "status": "SIMULATION_SUCCESS",
        "scenario_id": scenario_sim_id,
        "modeled_label": "ISOLATED SCENARIO SIMULATION",
        "current_state": {
            "enterprise_risk": current_risk_score,
            "risk_score": current_risk_score,
            "financial_exposure": current_eal,
            "financial_exposure_label": f"₹{round(current_eal/10000000, 2)} Crore",
            "loss_event_frequency": before_fair["loss_event_frequency"],
            "single_loss_expectancy": before_fair["single_loss_expectancy"],
            "budget": budget,
            "budget_label": f"₹{round(budget/10000000, 2)} Crore" if budget >= 10000000 else f"₹{round(budget/100000, 1)} Lakh",
            "critical_assets": ["Core Payment Database Cluster (DB-PAY-PRD-01)", "IAM Domain Controller", "Payment API Gateway"]
        },
        "scenario_state": {
            "enterprise_risk": scenario_risk_score,
            "risk_score": scenario_risk_score,
            "financial_exposure": scenario_eal,
            "financial_exposure_label": f"₹{round(scenario_eal/10000000, 2)} Crore",
            "loss_event_frequency": after_fair["loss_event_frequency"],
            "single_loss_expectancy": after_fair["single_loss_expectancy"],
            "budget": simulated_budget,
            "budget_label": f"₹{round(simulated_budget/10000000, 2)} Crore" if simulated_budget >= 10000000 else f"₹{round(simulated_budget/100000, 1)} Lakh",
            "affected_assets": sorted(list(affected_assets_set)) if affected_assets_set else ["Production Infrastructure"],
            "attack_paths": attack_paths_affected if attack_paths_affected else ["Baseline Attack Paths"],
            "investment_requirement": total_investment_cost,
            "investment_requirement_label": f"₹{round(total_investment_cost/100000, 1)} Lakh"
        },
        "before_after_comparison": comp_dict,
        "before_vs_after": comp_dict,
        "financial_impact": fin_impact
    }
