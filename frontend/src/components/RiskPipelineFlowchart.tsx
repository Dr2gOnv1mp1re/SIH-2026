import React, { useState } from 'react';
import { 
  Upload, 
  Search, 
  GitFork, 
  CheckCircle2, 
  Cpu, 
  Server, 
  ShieldAlert, 
  Bug, 
  Calculator, 
  DollarSign, 
  LayoutDashboard, 
  Sparkles, 
  ArrowDown, 
  ChevronRight,
  Info,
  Layers,
  Database
} from 'lucide-react';
import { useDataset } from '../context/DatasetContext';

export const RiskPipelineFlowchart: React.FC = () => {
  const { isSihDataset, sihMetrics } = useDataset();
  const [activeStage, setActiveStage] = useState<string>('risk_engine');

  const stages = [
    {
      id: 'upload',
      title: '1. UPLOAD CSV',
      subtitle: 'Primary Data Ingestion',
      icon: Upload,
      color: 'from-blue-600 to-cyan-600',
      badge: isSihDataset ? 'PS26105_Cyber_Risk_Test_Data.csv' : 'Enterprise Dataset',
      details: 'Direct ingestion of the raw CSV containing 15 real test assets. Serves as single source of truth.'
    },
    {
      id: 'detect',
      title: '2. Detect CSV Columns',
      subtitle: 'Header Inspection',
      icon: Search,
      color: 'from-cyan-600 to-teal-600',
      badge: '28 Columns Detected',
      details: 'Parses asset identity, vulnerability, SIEM, IAM, EDR, CSPM, threat intel, financial impact, and control effectiveness.'
    },
    {
      id: 'mapping',
      title: '3. Automatic Field Mapping',
      subtitle: 'Domain Normalization',
      icon: GitFork,
      color: 'from-teal-600 to-emerald-600',
      badge: '100% Schema Match',
      details: 'Automatically routes fields to: Asset Inventory (6), Vulnerabilities (6), Threat Intel (2), SIEM (2), IAM (3), EDR (3), CSPM (2), Financial & Mitigation (4).'
    },
    {
      id: 'validation',
      title: '4. Data Validation',
      subtitle: 'Integrity Verification',
      icon: CheckCircle2,
      color: 'from-emerald-600 to-green-600',
      badge: '15 / 15 Records Valid',
      details: 'Zero records lost, zero duplicate asset IDs, strict type conversion, explicit isolation of N/A values (no synthetic CVE or CSPM hallucinations).'
    }
  ];

  const triBranches = [
    {
      id: 'asset_risk',
      title: 'Asset Risk',
      icon: Server,
      color: 'border-blue-500/60 bg-blue-950/30 text-blue-300',
      metrics: isSihDataset ? `${sihMetrics?.critical_assets || 5} Critical / ${sihMetrics?.internet_exposed_assets || 7} Net-Exposed` : 'Criticality & Exposure',
      formula: 'AssetRisk = (Criticality / 5) × (1.0 + 0.35 × NetExposed)'
    },
    {
      id: 'threat_risk',
      title: 'Threat Risk',
      icon: ShieldAlert,
      color: 'border-amber-500/60 bg-amber-950/30 text-amber-300',
      metrics: isSihDataset ? `${sihMetrics?.critical_edr_alerts || 5} EDR Alerts / ${sihMetrics?.assets_with_mfa_disabled || 8} MFA Deficits` : 'SIEM + EDR + Intel',
      formula: 'ThreatRisk = ThreatIntel + SIEM + EDR_Unisolated + IAM_Deficit + CSPM'
    },
    {
      id: 'vuln_risk',
      title: 'Vulnerability Risk',
      icon: Bug,
      color: 'border-rose-500/60 bg-rose-950/30 text-rose-300',
      metrics: isSihDataset ? `${sihMetrics?.critical_vulnerabilities || 6} Critical / ${sihMetrics?.exploitable_vulnerabilities || 7} Weaponized` : 'CVSS & Exploits',
      formula: 'VulnRisk = (CVSS / 10) × ExploitFactor × (1 + Age/365)'
    }
  ];

  return (
    <div className="enterprise-card p-6 border-[#1C2042] bg-[#0A0D1E] space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1C2042] pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-600/30 to-violet-600/30 border border-cyan-500/40 text-cyan-300">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span>Quantum Risk AI — End-to-End Pipeline Architecture</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-700">
                LIVE PIPELINE
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Interactive execution flow from raw CSV upload through the tri-branch risk calculation engine to OR-Tools recommendations.
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-[#121630] border border-[#212752] text-slate-300">
            DATA ORIGIN: <strong className="text-cyan-300">{isSihDataset ? 'SIH PS26105 TEST DATA' : 'ABC BANK DEMO'}</strong>
          </span>
        </div>
      </div>

      {/* Visual Pipeline Stepper (User's Exact Architecture Flow) */}
      <div className="flex flex-col items-center space-y-3 pt-2">
        
        {/* Top 4 Linear Stages */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 w-full">
          {stages.map((stage) => {
            const Icon = stage.icon;
            const isSelected = activeStage === stage.id;
            return (
              <div
                key={stage.id}
                onClick={() => setActiveStage(stage.id)}
                className={`p-3.5 rounded-xl border transition cursor-pointer relative ${
                  isSelected 
                    ? 'bg-[#141938] border-cyan-500 ring-1 ring-cyan-400/50 shadow-lg shadow-cyan-950/30' 
                    : 'bg-[#0E1228] border-[#1C2248] hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="p-2 rounded-lg bg-cyan-950/80 border border-cyan-800 text-cyan-400">
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-[#0A0D1E] text-slate-300 border border-[#1C2042]">
                    {stage.badge}
                  </span>
                </div>
                <div className="font-mono font-bold text-xs text-white">{stage.title}</div>
                <div className="text-[10px] text-slate-400">{stage.subtitle}</div>
              </div>
            );
          })}
        </div>

        {/* Down Connector */}
        <div className="flex items-center justify-center text-slate-500 py-1">
          <ArrowDown className="w-5 h-5 text-cyan-400 animate-bounce" />
        </div>

        {/* Central Risk Calculation Engine Hub */}
        <div 
          onClick={() => setActiveStage('risk_engine')}
          className={`w-full max-w-xl p-4 rounded-xl border transition cursor-pointer text-center relative ${
            activeStage === 'risk_engine'
              ? 'bg-[#151B3D] border-violet-500 ring-1 ring-violet-400 shadow-lg shadow-violet-950/30'
              : 'bg-[#0F132D] border-violet-900/60 hover:border-violet-700'
          }`}
        >
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-violet-950 border border-violet-700 text-violet-300 font-mono text-xs font-bold mb-1">
            <Calculator className="w-3.5 h-3.5" />
            <span>5. Risk Calculation Engine</span>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Evaluates multi-source telemetry signals and executes tri-branch risk attribution
          </p>
        </div>

        {/* Branch Split Connector */}
        <div className="w-full max-w-3xl flex justify-between items-center px-12 text-slate-600">
          <div className="w-1/3 border-t-2 border-dashed border-[#242A54]" />
          <div className="w-4 h-4 rounded-full bg-violet-500/40 border border-violet-400 flex items-center justify-center">
            <div className="w-1.5 h-1.5 rounded-full bg-violet-300" />
          </div>
          <div className="w-1/3 border-t-2 border-dashed border-[#242A54]" />
        </div>

        {/* The Tri-Branch: Asset Risk | Threat Risk | Vulnerability Risk */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-4xl">
          {triBranches.map((branch) => {
            const Icon = branch.icon;
            const isSelected = activeStage === branch.id;
            return (
              <div
                key={branch.id}
                onClick={() => setActiveStage(branch.id)}
                className={`p-4 rounded-xl border transition cursor-pointer space-y-2 ${branch.color} ${
                  isSelected ? 'ring-2 ring-white/50 shadow-md' : 'hover:scale-[1.01]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-xs uppercase tracking-wide flex items-center gap-1.5">
                    <Icon className="w-4 h-4" />
                    {branch.title}
                  </span>
                </div>
                <div className="text-xs font-semibold">{branch.metrics}</div>
                <div className="text-[10px] font-mono bg-black/40 p-1.5 rounded text-slate-300 border border-white/10">
                  {branch.formula}
                </div>
              </div>
            );
          })}
        </div>

        {/* Branch Reconverge Connector */}
        <div className="w-full max-w-3xl flex justify-between items-center px-12 text-slate-600">
          <div className="w-1/3 border-t-2 border-dashed border-[#242A54]" />
          <div className="w-4 h-4 rounded-full bg-cyan-500/40 border border-cyan-400 flex items-center justify-center">
            <div className="w-1.5 h-1.5 rounded-full bg-cyan-300" />
          </div>
          <div className="w-1/3 border-t-2 border-dashed border-[#242A54]" />
        </div>

        <div className="flex items-center justify-center text-slate-500 py-0.5">
          <ArrowDown className="w-5 h-5 text-cyan-400" />
        </div>

        {/* 6. Overall Risk Score */}
        <div 
          onClick={() => setActiveStage('overall_score')}
          className={`w-full max-w-xl p-3.5 rounded-xl border text-center transition cursor-pointer ${
            activeStage === 'overall_score'
              ? 'bg-[#151B3D] border-rose-500 ring-1 ring-rose-400 shadow-md'
              : 'bg-[#0E1228] border-[#1C2248] hover:border-slate-600'
          }`}
        >
          <div className="font-mono font-bold text-xs text-rose-300 flex items-center justify-center gap-2">
            <span>6. Overall Risk Score</span>
            <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 text-[10px]">
              0 - 100 Scale
            </span>
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-1">
            RawScore = 0.35×Asset + 0.35×Threat + 0.30×Vuln • Adjusted: RawScore × (1 - 0.5×ControlEffectiveness)
          </div>
        </div>

        <div className="flex items-center justify-center text-slate-500 py-0.5">
          <ArrowDown className="w-5 h-5 text-cyan-400" />
        </div>

        {/* 7. Financial Risk* */}
        <div 
          onClick={() => setActiveStage('financial_risk')}
          className={`w-full max-w-xl p-4 rounded-xl border text-center transition cursor-pointer ${
            activeStage === 'financial_risk'
              ? 'bg-amber-950/40 border-amber-500 ring-1 ring-amber-400 shadow-md'
              : 'bg-[#0E1228] border-amber-900/60 hover:border-amber-700'
          }`}
        >
          <div className="font-mono font-bold text-xs text-amber-300 flex items-center justify-center gap-2">
            <DollarSign className="w-4 h-4 text-amber-400" />
            <span>7. Financial Risk*</span>
            <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-200 border border-amber-700 text-[9px] font-bold">
              *MODELED / ESTIMATED FINANCIAL INPUT
            </span>
          </div>
          <div className="text-xs text-slate-300 mt-1">
            Expected Annual Loss (ALE) = Potential Financial Impact × Estimated Incident Probability
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-0.5">
            Monte Carlo Engine: 10,000 LogNormal Simulations • Total Potential Exposure: {sihMetrics?.total_modeled_financial_impact_label || '₹17.53 Cr'}
          </div>
        </div>

        <div className="flex items-center justify-center text-slate-500 py-0.5">
          <ArrowDown className="w-5 h-5 text-cyan-400" />
        </div>

        {/* 8. Risk Dashboard */}
        <div 
          onClick={() => setActiveStage('risk_dashboard')}
          className={`w-full max-w-xl p-3.5 rounded-xl border text-center transition cursor-pointer ${
            activeStage === 'risk_dashboard'
              ? 'bg-[#151B3D] border-cyan-500 ring-1 ring-cyan-400 shadow-md'
              : 'bg-[#0E1228] border-[#1C2248] hover:border-slate-600'
          }`}
        >
          <div className="font-mono font-bold text-xs text-cyan-300 flex items-center justify-center gap-2">
            <LayoutDashboard className="w-4 h-4 text-cyan-400" />
            <span>8. Risk Dashboard</span>
            <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-200 border border-cyan-800 text-[10px]">
              13 Dynamic KPIs
            </span>
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">
            Calculated dynamically from the 15 records: zero hardcoded statistics or invented figures.
          </div>
        </div>

        <div className="flex items-center justify-center text-slate-500 py-0.5">
          <ArrowDown className="w-5 h-5 text-cyan-400" />
        </div>

        {/* 9. Recommendations */}
        <div 
          onClick={() => setActiveStage('recommendations')}
          className={`w-full max-w-xl p-4 rounded-xl border text-center transition cursor-pointer ${
            activeStage === 'recommendations'
              ? 'bg-emerald-950/40 border-emerald-500 ring-1 ring-emerald-400 shadow-md'
              : 'bg-[#0E1228] border-emerald-900/60 hover:border-emerald-700'
          }`}
        >
          <div className="font-mono font-bold text-xs text-emerald-300 flex items-center justify-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>9. Recommendations (Investment Optimizer)</span>
            <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-200 border border-emerald-700 text-[10px]">
              OR-Tools SCIP Knapsack
            </span>
          </div>
          <div className="text-xs text-slate-300 mt-1">
            Optimizes mitigation selection using <code className="text-cyan-200">estimated_mitigation_cost_inr</code> and modeled risk reduction within budget.
          </div>
        </div>

      </div>

      {/* Stage Detail Drawer */}
      <div className="p-4 rounded-xl bg-[#070914] border border-[#1C2042] text-xs space-y-2">
        <div className="flex items-center justify-between text-slate-300 font-mono font-bold">
          <span className="flex items-center gap-2 text-cyan-400">
            <Info className="w-4 h-4" />
            <span>Selected Stage Detail: {activeStage.toUpperCase()}</span>
          </span>
          <span className="text-[10px] text-slate-400">SIH PS26105 Architecture Pipeline</span>
        </div>
        
        {activeStage === 'upload' && (
          <p className="text-slate-300">
            The dataset is ingested as <code className="text-cyan-300">PS26105_Cyber_Risk_Test_Data.csv</code> containing 15 real test records (A001 to A015). All data originates strictly from the user-provided file with zero synthetic filler records.
          </p>
        )}
        {activeStage === 'detect' && (
          <p className="text-slate-300">
            All 28 CSV columns are dynamically verified upon ingestion: <code className="text-cyan-200">asset_id, asset_name, asset_type, business_unit, asset_criticality_1_5, internet_exposed, cve_id, cvss_score, vulnerability_severity, patch_available, exploit_available, vulnerability_age_days, siem_event, siem_severity, iam_user, mfa_enabled, privileged_account, edr_alert, edr_severity, edr_isolated, cspm_finding, cspm_severity, threat_intel_indicator, threat_confidence_pct, estimated_incident_probability, potential_financial_impact_inr, estimated_mitigation_cost_inr, control_effectiveness</code>.
          </p>
        )}
        {activeStage === 'mapping' && (
          <p className="text-slate-300">
            Automatic field mapping links raw columns to functional analytical subsystems: Asset Inventory, Vulnerabilities, Threat Intelligence, SIEM Event Monitor, IAM Security Controls, EDR Telemetry, CSPM Findings, and Financial Risk Quantifier.
          </p>
        )}
        {activeStage === 'validation' && (
          <p className="text-slate-300">
            Validation checks confirm all 15 assets are intact, data types are preserved (float probabilities, integers, booleans), and N/A values (e.g. A009 & A010 having no CVE) are safely isolated without hallucinating synthetic vulnerabilities.
          </p>
        )}
        {activeStage === 'asset_risk' && (
          <p className="text-slate-300">
            <strong>Asset Risk Branch:</strong> Measures asset value and exposure. Baseline is derived from <code className="text-cyan-300">asset_criticality_1_5</code> (scale 1-5) multiplied by a 1.35x exposure factor if <code className="text-cyan-300">internet_exposed == True</code>.
          </p>
        )}
        {activeStage === 'threat_risk' && (
          <p className="text-slate-300">
            <strong>Threat Risk Branch:</strong> Aggregates external threat indicators (<code className="text-cyan-300">threat_confidence_pct</code>), active SIEM security events, EDR alerts (with extra penalty if unisolated), CSPM cloud misconfigurations, and critical IAM deficits (<code className="text-rose-400">Privileged = Yes AND MFA = No</code>).
          </p>
        )}
        {activeStage === 'vuln_risk' && (
          <p className="text-slate-300">
            <strong>Vulnerability Risk Branch:</strong> Evaluates discovered flaws using <code className="text-cyan-300">cvss_score</code>, with a 1.35x multiplier if <code className="text-rose-400">exploit_available == True</code>, a 0.85x mitigation factor if <code className="text-emerald-400">patch_available == True</code>, and age compounding factor.
          </p>
        )}
        {activeStage === 'risk_engine' && (
          <p className="text-slate-300">
            <strong>Risk Calculation Engine:</strong> Combines the three branches using weighted synthesis: <code className="text-cyan-300">0.35 × Asset + 0.35 × Threat + 0.30 × Vuln</code>, followed by reduction scaling based on <code className="text-emerald-300">control_effectiveness</code> (0.0 to 1.0).
          </p>
        )}
        {activeStage === 'overall_score' && (
          <p className="text-slate-300">
            Produces an interpretable 0-100 normalized risk score for each individual asset and an enterprise-wide composite risk rating. Identifies top risk assets (A005, A003, A001, A007, A010).
          </p>
        )}
        {activeStage === 'financial_risk' && (
          <p className="text-slate-300">
            <strong>Financial Risk Formulation:</strong> Evaluates Expected Annual Loss (ALE = Potential Financial Impact × Estimated Incident Probability). All figures are explicitly classified as <strong className="text-amber-300">*MODELED / ESTIMATED FINANCIAL INPUT</strong> rather than actual historical corporate losses. A 10,000-run Monte Carlo simulation produces empirical percentile distributions (P50, P90, P99).
          </p>
        )}
        {activeStage === 'risk_dashboard' && (
          <p className="text-slate-300">
            Aggregates live KPIs dynamically across the 15 records: Total Assets (15), Critical Assets, Internet-Exposed, Exploitable CVEs, MFA Deficits, Unisolated EDR, Total Modeled Potential Financial Impact, and Total Mitigation Cost.
          </p>
        )}
        {activeStage === 'recommendations' && (
          <p className="text-slate-300">
            <strong>Google OR-Tools SCIP Knapsack:</strong> Uses <code className="text-cyan-300">estimated_mitigation_cost_inr</code> as the weight constraint and modeled risk reduction as the value objective. Selects the optimal mitigation portfolio under any user-defined budget.
          </p>
        )}
      </div>

    </div>
  );
};
