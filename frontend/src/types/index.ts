export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'CISO' | 'SECURITY_ANALYST' | 'RISK_ANALYST' | 'EXECUTIVE' | 'AUDITOR';
}

export interface Organization {
  id: string;
  name: string;
  industry: string;
  country: string;
  employee_count: number;
  annual_revenue: number;
  cybersecurity_budget: number;
  risk_appetite_enterprise: number;
  risk_appetite_critical_asset: number;
  financial_assumptions: Record<string, any>;
}

export interface Asset {
  id: string;
  name: string;
  asset_type: string;
  ip_address?: string;
  hostname?: string;
  owner?: string;
  department?: string;
  operating_system?: string;
  business_service_id?: string;
  business_importance?: number;
  data_sensitivity?: number;
  revenue_dependency?: number;
  downtime_tolerance_hours?: number;
  regulatory_importance?: number;
  internet_exposed?: boolean;
  criticality_score?: number;
  current_risk_score?: number;
  expected_annual_loss?: number;
  status?: string;
  tags?: string[];
}

export interface Vulnerability {
  id: string;
  affected_asset_id?: string;
  cve_id: string;
  title: string;
  description?: string;
  cvss_score: number;
  severity: string;
  exploit_available?: boolean;
  active_exploitation?: boolean;
  patch_available?: boolean;
  remediation_status?: string;
  remediation_guidance?: string;
  discovery_date?: string;
  source?: string;
  evidence?: Record<string, any>;
}

export interface Threat {
  id?: string;
  threat_actor: string;
  threat_type: string;
  attack_technique: string;
  threat_severity: string;
  active_campaign: boolean;
  exploit_cves: string[];
  target_asset_types?: string[];
  relevance_score: number;
  first_seen?: string;
  last_seen?: string;
}

export interface SecurityControl {
  id: string;
  code: string;
  name: string;
  category: string;
  coverage_percentage?: number;
  effectiveness_percentage?: number;
  maturity_level?: number;
  implementation_cost: number;
  annual_cost?: number;
  modeled_risk_reduction?: number;
  status?: string;
  prerequisites?: string[];
}

export interface EnterpriseRiskResponse {
  enterprise_risk_score: number;
  risk_level: string;
  expected_annual_loss: number;
  expected_annual_loss_label: string;
  modeled_loss_min: number;
  modeled_loss_max: number;
  confidence_percentage: number;
  risk_appetite_enterprise: number;
  appetite_status: string;
  risk_contributors: {
    critical_vulnerability_pct: number;
    active_exploitation_pct: number;
    asset_criticality_pct: number;
    internet_exposure_pct: number;
    weak_control_segmentation_pct: number;
    other_environmental_factors_pct: number;
  };
  modeled_label: string;
  last_assessment_date: string;
  disclaimer: string;
}

export interface OptimizationResult {
  budget_amount: number;
  total_investment: number;
  current_modeled_risk: number;
  projected_modeled_risk: number;
  modeled_risk_reduction: number;
  efficiency_metric: number;
  selected_controls: SecurityControl[];
  unselected_controls: SecurityControl[];
  modeled_label: string;
  efficiency_label: string;
  disclaimer: string;
}

export interface OptimizationRunResponse {
  run_id: string;
  optimization_result: OptimizationResult;
  do_nothing_scenario: {
    current_risk: number;
    current_risk_label: string;
    do_nothing_projected_risk: number;
    do_nothing_label: string;
    with_investment_projected_risk: number;
    with_investment_label: string;
  };
  canonical_hash: string;
}

export interface AIPredictionResponse {
  model_used: string;
  baseline_comparison: string;
  model_metadata: Record<string, any>;
  predicted_30d_risk_score: number;
  current_eal: number;
  predicted_30d_eal: number;
  predicted_60d_eal: number;
  predicted_90d_eal: number;
  trend: string;
  confidence_percentage: number;
  shap_explanation: Array<{
    feature: string;
    impact_value: number;
    direction: string;
    pct_contribution?: number;
    feature_value?: number;
  }>;
  modeled_label: string;
  disclaimer: string;
}

export interface BlockchainBlock {
  block_number: number;
  timestamp: string;
  previous_block_hash: string;
  canonical_sha256_hash: string;
  record_type: string;
  record_id: string;
  payload_snapshot: Record<string, any>;
  transaction_id: string;
  verification_status: string;
}

export interface DemoStep {
  step: number;
  title: string;
  description: string;
  risk_score: number;
  enterprise_eal: number;
  eal_label: string;
  state_badge: string;
  action_summary: string;
}
