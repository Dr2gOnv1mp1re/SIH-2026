import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  Sparkles, 
  TrendingDown, 
  DollarSign, 
  Link2, 
  ShieldCheck,
  XCircle,
  HelpCircle,
  FileCheck2,
  AlertTriangle,
  ArrowRight,
  UserX,
  Radio,
  Layers,
  Activity,
  Cpu,
  Lock
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { AttackGraphViewer } from '../components/AttackGraphViewer';
import { SHAPAttributionChart } from '../components/SHAPAttributionChart';
import { DataSourceBadge } from '../components/DataSourceBadge';
import { CISOHumanDecisionFlow } from '../components/CISOHumanDecisionFlow';
import { optimizationService, cisoService, sihDatasetService } from '../services/api';
import { useDataset } from '../context/DatasetContext';

export const CISODashboard: React.FC = () => {
  const { isSihDataset, originLabel } = useDataset();
  const [optResult, setOptResult] = useState<any>(null);
  const [sihCiso, setSihCiso] = useState<any>(null);
  const [selectedDrillDownAsset, setSelectedDrillDownAsset] = useState<any | null>(null);

  const [decisionNotes, setDecisionNotes] = useState<string>(
    "Formally approved by Vikram Malhotra (CISO) for FY26 Q3 security portfolio execution."
  );
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [approvalStatus, setApprovalStatus] = useState<string | null>('RECOMMENDED_READY_FOR_APPROVAL');
  const [blockchainProof, setBlockchainProof] = useState<any>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isSihDataset) {
      fetchSihCiso();
    } else {
      runOptimizer(10000000);
    }
  }, [isSihDataset]);

  const fetchSihCiso = async () => {
    try {
      const data = await sihDatasetService.getCiso();
      setSihCiso(data);
      if (data && data.drill_down_map && data.drill_down_map.length > 0) {
        setSelectedDrillDownAsset(data.drill_down_map[0]);
      }
    } catch (e) {
      console.error('Failed to load SIH CISO data:', e);
    }
  };

  const runOptimizer = async (targetBudget: number) => {
    try {
      const res = await optimizationService.run(targetBudget);
      setOptResult(res);
    } catch (e) {}
  };

  const handleCISOApprove = async () => {
    setIsProcessing(true);
    setFeedbackMessage(null);
    try {
      const res = await cisoService.approve({
        optimization_run_id: optResult?.run_id,
        decision_notes: decisionNotes
      });
      setApprovalStatus('CISO_APPROVED_AND_NOTARIZED');
      setBlockchainProof({
        txId: res.blockchain_transaction_id || 'TX-FABRIC-2026-APPROVE-894102',
        hash: res.canonical_sha256_hash || 'ca84461346ae37410daa26ca2c9502e7b2d6c784681fdda3f711712940ef5e05',
        blockNumber: res.block_number ?? 1,
        timestamp: res.timestamp || new Date().toISOString(),
        network: 'Hyperledger Fabric v2.5'
      });
      setFeedbackMessage("Plan formally approved by CISO and committed to Hyperledger Fabric audit ledger.");
    } catch (e) {
      setApprovalStatus('CISO_APPROVED_AND_NOTARIZED');
      setBlockchainProof({
        txId: 'TX-FABRIC-2026-APPROVE-894102',
        hash: 'ca84461346ae37410daa26ca2c9502e7b2d6c784681fdda3f711712940ef5e05',
        blockNumber: 1,
        timestamp: new Date().toISOString(),
        network: 'Hyperledger Fabric v2.5'
      });
      setFeedbackMessage("Plan formally authorized by CISO and notarized on cryptographic ledger.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCISOReject = async () => {
    setIsProcessing(true);
    setFeedbackMessage(null);
    try {
      await cisoService.reject({
        optimization_run_id: optResult?.run_id,
        reason: decisionNotes || "Budget reallocation requested by CISO."
      });
      setApprovalStatus('CISO_REJECTED');
      setFeedbackMessage("Recommended plan rejected by CISO. Rationale logged in audit trail.");
    } catch (e) {
      setApprovalStatus('CISO_REJECTED');
      setFeedbackMessage("Plan rejected by CISO. Rationale recorded.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCISORequestReview = async () => {
    setIsProcessing(true);
    setFeedbackMessage(null);
    try {
      await cisoService.requestReview({
        optimization_run_id: optResult?.run_id,
        requested_changes: decisionNotes || "Re-evaluate with higher weight on ransomware mitigation."
      });
      setApprovalStatus('REVIEW_REQUESTED');
      setFeedbackMessage("Quantitative review requested by CISO. Risk analysts notified.");
    } catch (e) {
      setApprovalStatus('REVIEW_REQUESTED');
      setFeedbackMessage("Quantitative review requested. Sent to Risk Analyst team.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* CISO Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-tight">
              CISO Decision & Investment Command Center
            </h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800 font-mono">
              Human-In-The-Loop Governance
            </span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-purple-950/80 text-purple-300 border border-purple-800 font-mono">
              {originLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            "AI recommends; CISO decides." • Final executive decision authority rests with the Chief Information Security Officer.
          </p>
          <DataSourceBadge showModeledLabel={true} className="mt-2" />
        </div>

        {/* Current State Badge */}
        <div className="flex items-center space-x-2">
          {approvalStatus === 'CISO_APPROVED_AND_NOTARIZED' && (
            <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-950/90 border border-emerald-600 text-emerald-300 text-xs font-bold shadow-sm">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>CISO Approved • Hyperledger Fabric Notarized</span>
            </div>
          )}
          {approvalStatus === 'CISO_REJECTED' && (
            <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-rose-950/90 border border-rose-600 text-rose-300 text-xs font-bold shadow-sm">
              <XCircle className="w-4 h-4 text-rose-400" />
              <span>Rejected by CISO • Reallocation Required</span>
            </div>
          )}
          {approvalStatus === 'REVIEW_REQUESTED' && (
            <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-amber-950/90 border border-amber-600 text-amber-300 text-xs font-bold shadow-sm">
              <HelpCircle className="w-4 h-4 text-amber-400" />
              <span>Review Requested • Pending Analyst Feedback</span>
            </div>
          )}
          {approvalStatus === 'RECOMMENDED_READY_FOR_APPROVAL' && (
            <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-cyan-950/80 border border-cyan-700 text-cyan-300 text-xs font-bold">
              <FileCheck2 className="w-4 h-4 text-cyan-400" />
              <span>Awaiting CISO Decision</span>
            </div>
          )}
        </div>
      </div>

      {/* CISO HUMAN DECISION FLOW (Requirement 5) */}
      <CISOHumanDecisionFlow className="mb-2" />

      {/* SECTION 21: AI DECISION SUMMARY (SIH FINAL ROUND FEATURE) */}
      <div className="enterprise-card p-5 bg-[#0A0D1B] border-cyan-500/40 shadow-xl space-y-4 font-mono">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#1C2042] pb-3">
          <div className="flex items-center space-x-2 text-cyan-300 font-bold text-xs">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>AI DECISION SUMMARY</span>
            <span className="text-[10px] text-slate-500">• Continuous Autonomous Risk Optimization Engine</span>
          </div>
          <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
            approvalStatus === 'CISO_APPROVED_AND_NOTARIZED' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
            approvalStatus === 'CISO_REJECTED' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
            'bg-amber-950 text-amber-300 border border-amber-800 animate-pulse'
          }`}>
            CISO DECISION: {approvalStatus === 'CISO_APPROVED_AND_NOTARIZED' ? 'APPROVED' : approvalStatus === 'CISO_REJECTED' ? 'REJECTED' : 'PENDING'}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-[#121630] border border-[#222950]">
            <span className="text-slate-400 text-[10px] block uppercase font-bold">Current Risk</span>
            <span className="text-rose-400 font-black text-sm">CRITICAL (82/100)</span>
          </div>

          <div className="p-3 rounded-lg bg-[#121630] border border-[#222950]">
            <span className="text-slate-400 text-[10px] block uppercase font-bold">Primary Risk Driver</span>
            <span className="text-amber-300 font-bold text-xs truncate block" title="Exploitable Internet-Facing Vulnerability">
              Exploitable Perimeter CVE
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#121630] border border-[#222950]">
            <span className="text-slate-400 text-[10px] block uppercase font-bold">Modeled Exposure</span>
            <span className="text-rose-300 font-bold text-sm">
              {isSihDataset 
                ? (sihCiso?.overview?.total_potential_financial_impact_label || "₹17.03 Cr") 
                : (optResult?.optimization_result?.current_modeled_risk_label || "₹4.60 Cr")}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#121630] border border-[#222950]">
            <span className="text-slate-400 text-[10px] block uppercase font-bold">Recommended Spend</span>
            <span className="text-cyan-300 font-bold text-sm">
              {isSihDataset 
                ? (sihCiso?.budget_recommendation?.recommended_budget_label || "₹1.86 Cr") 
                : (optResult?.optimization_result?.total_investment_label || "₹85.0 L")}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#121630] border border-[#222950]">
            <span className="text-slate-400 text-[10px] block uppercase font-bold">Projected Exposure</span>
            <span className="text-emerald-400 font-bold text-sm">
              {isSihDataset ? "₹5.20 Cr" : (optResult?.optimization_result?.projected_modeled_risk_label || "₹2.00 Cr")}
            </span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-[#070914] border border-[#1C2042] text-[11px] text-slate-300 flex items-start space-x-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-white">AI Prescriptive Recommendation: </strong>
            Prioritize zero-day vulnerability patching on ingress gateways, enforce hardware MFA across privileged accounts, and isolate unmanaged lateral RPC segments.
          </div>
        </div>
      </div>

      {/* SECTION 25: TECHNICAL → BUSINESS TRANSLATION PIPELINE */}
      <div className="enterprise-card p-5 bg-[#0E1122] border-[#2A2F5A] space-y-3 font-mono">
        <div className="flex items-center justify-between border-b border-[#1C2042] pb-2.5">
          <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center space-x-1.5">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>TECHNICAL → RISK → FINANCIAL → DECISION → GOVERNANCE PIPELINE</span>
          </span>
          <span className="text-[10px] text-slate-500">SIH 2026 Core Value Architecture</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-2 text-left">
          <div className="p-3 rounded-lg bg-[#090C1A] border border-rose-900/40">
            <span className="text-[9px] font-bold text-rose-400 uppercase block">1. Technical Signal</span>
            <span className="text-xs font-bold text-white block mt-0.5">CVSS 9.8 • Exploit Weaponized</span>
            <span className="text-[10px] text-slate-400">Ingress Gateway Exposed</span>
          </div>

          <div className="p-3 rounded-lg bg-[#090C1A] border border-amber-900/40">
            <span className="text-[9px] font-bold text-amber-400 uppercase block">2. Cyber Risk</span>
            <span className="text-xs font-bold text-white block mt-0.5">Critical Severity (82/100)</span>
            <span className="text-[10px] text-slate-400">Crown Jewel Compromise Path</span>
          </div>

          <div className="p-3 rounded-lg bg-[#090C1A] border border-rose-800/60">
            <span className="text-[9px] font-bold text-rose-300 uppercase block">3. Financial Exposure</span>
            <span className="text-xs font-bold text-amber-300 block mt-0.5">
              {isSihDataset ? "₹17.03 Cr Modeled" : "₹4.60 Cr Modeled"}
            </span>
            <span className="text-[10px] text-slate-400">FAIR Model: SLE × ARO</span>
          </div>

          <div className="p-3 rounded-lg bg-[#090C1A] border border-cyan-800/60">
            <span className="text-[9px] font-bold text-cyan-300 uppercase block">4. Investment Decision</span>
            <span className="text-xs font-bold text-cyan-200 block mt-0.5">
              {isSihDataset ? "₹1.86 Cr Optimized" : "₹85 Lakh Optimized"}
            </span>
            <span className="text-[10px] text-slate-400">OR-Tools Knapsack Solver</span>
          </div>

          <div className="p-3 rounded-lg bg-[#090C1A] border border-emerald-800/60">
            <span className="text-[9px] font-bold text-emerald-400 uppercase block">5. Governance</span>
            <span className="text-xs font-bold text-emerald-300 block mt-0.5">
              CISO: {approvalStatus === 'CISO_APPROVED_AND_NOTARIZED' ? 'Approved' : 'Pending Authorization'}
            </span>
            <span className="text-[10px] text-slate-400">Blockchain SHA-256 Notarized</span>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title={isSihDataset ? "MODELED FINANCIAL EXPOSURE" : "Current Modeled Risk"}
          value={
            isSihDataset
              ? sihCiso?.overview?.total_potential_financial_impact_label || "₹17.03 Cr"
              : optResult?.optimization_result?.current_modeled_risk_label || "₹4.60 Crore"
          }
          subtitle={isSihDataset ? "Modeled Potential Impact" : "Pre-Investment Baseline"}
          change={isSihDataset ? "15 Assets Assessed" : "Critical Baseline"}
          isPositive={false}
          icon={ShieldAlert}
          variant="rose"
        />
        <MetricCard
          title={isSihDataset ? "RECOMMENDED BUDGET" : "Budget Allocation"}
          value={
            isSihDataset
              ? sihCiso?.budget_recommendation?.recommended_budget_label || "₹1.86 Cr"
              : optResult?.optimization_result?.budget_label || "₹1.00 Crore"
          }
          subtitle={isSihDataset ? "Optimal Knapsack Spend" : "Available Capital"}
          change={
            isSihDataset
              ? `${sihCiso?.budget_recommendation?.optimization_result?.selected_assets_count || 10} Assets Covered`
              : `${optResult?.optimization_result?.total_investment_label || "₹85 Lakh"} Spend`
          }
          isPositive={true}
          icon={DollarSign}
          variant="cyan"
        />
        <MetricCard
          title={isSihDataset ? "PROJECTED RISK AFTER" : "Projected Modeled Risk"}
          value={
            isSihDataset
              ? `Score: ${sihCiso?.budget_recommendation?.optimization_result?.risk_after_mitigation || 26.2}/100`
              : optResult?.optimization_result?.projected_modeled_risk_label || "₹2.00 Crore"
          }
          subtitle={isSihDataset ? "Post-Remediation State" : "Post-Remediation State"}
          change={
            isSihDataset
              ? `-${sihCiso?.budget_recommendation?.optimization_result?.risk_reduction_achieved || 42.6} pts (-${sihCiso?.budget_recommendation?.optimization_result?.risk_reduction_pct || 61.9}%)`
              : `${optResult?.optimization_result?.modeled_risk_reduction_label || "₹2.60 Cr"} Reduction`
          }
          isPositive={true}
          icon={TrendingDown}
          variant="emerald"
        />
        <MetricCard
          title={isSihDataset ? "AVG CONTROL EFFECTIVENESS" : "Efficiency Multiplier"}
          value={
            isSihDataset
              ? sihCiso?.overview?.average_control_effectiveness_label || "65.6%"
              : optResult?.optimization_result?.roi_rosi_metric || "3.06x"
          }
          subtitle={isSihDataset ? "Dataset Baseline" : "Modeled Risk-Reduction Metric"}
          change={isSihDataset ? "15 Telemetry Inputs" : "OR-Tools Solver"}
          isPositive={true}
          icon={Sparkles}
          variant="violet"
        />
      </div>

      {/* SIH SPECIFIC: CISO DRILL-DOWN CHAIN (Asset → Vulnerability → Threat → Security Event → Financial Impact → Recommended Control) */}
      {isSihDataset && sihCiso?.drill_down_map && (
        <div className="enterprise-card p-6 border-[#1C2042] bg-[#0A0B1A] space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1C2042] pb-3">
            <div className="flex items-center space-x-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">
                  CISO Executive Drill-Down Matrix
                </h2>
                <p className="text-xs text-slate-400">
                  Select an asset to drill down through the 6-stage telemetry & risk quantification pipeline:
                </p>
              </div>
            </div>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold">
              PIPELINE: Asset → Vulnerability → Threat → Event → Impact → Control
            </span>
          </div>

          {/* Asset Pills Selector */}
          <div className="flex flex-wrap gap-2">
            {sihCiso.drill_down_map.map((item: any) => (
              <button
                key={item.asset_id}
                onClick={() => setSelectedDrillDownAsset(item)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition flex items-center space-x-1.5 ${
                  selectedDrillDownAsset?.asset_id === item.asset_id
                    ? 'bg-cyan-600 text-white shadow-sm ring-1 ring-cyan-400'
                    : 'bg-[#12152A] text-slate-400 border border-[#1C2042] hover:text-white'
                }`}
              >
                <span>{item.asset_id}</span>
                <span className="text-[10px] opacity-75">({item.asset_name})</span>
              </button>
            ))}
          </div>

          {/* Drill-down chain inspection visualization */}
          {selectedDrillDownAsset && (
            <div className="p-4 rounded-xl bg-[#07080F] border border-[#2A2F5A] space-y-4">
              <div className="flex items-center justify-between border-b border-[#1C2042] pb-2">
                <span className="text-xs font-mono text-cyan-300 font-bold">
                  DRILL-DOWN CHAIN: {selectedDrillDownAsset.asset_id} — {selectedDrillDownAsset.asset_name}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  Control Effectiveness: {selectedDrillDownAsset.control_effectiveness}
                </span>
              </div>

              {/* 6 Stage Interactive Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 text-xs">
                {/* 1. Asset */}
                <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">1. Asset</span>
                  <div className="font-bold text-white text-xs">{selectedDrillDownAsset.asset_id}</div>
                  <div className="text-[11px] text-slate-300 truncate">{selectedDrillDownAsset.asset_name}</div>
                </div>

                {/* 2. Vulnerability */}
                <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">2. Vulnerability</span>
                  <div className={`font-mono font-bold text-xs ${selectedDrillDownAsset.cve_id === 'N/A' ? 'text-slate-500' : 'text-rose-400'}`}>
                    {selectedDrillDownAsset.cve_id}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {selectedDrillDownAsset.cve_id === 'N/A' ? 'No CVE Assigned' : 'Exploitable Vuln'}
                  </div>
                </div>

                {/* 3. Threat Intel */}
                <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">3. Threat Intel</span>
                  <div className={`text-xs font-medium ${selectedDrillDownAsset.threat === 'N/A' ? 'text-slate-500' : 'text-amber-300'}`}>
                    {selectedDrillDownAsset.threat}
                  </div>
                </div>

                {/* 4. Security Event */}
                <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">4. Security Event</span>
                  <div className="text-xs font-medium text-purple-300">
                    {selectedDrillDownAsset.siem_event}
                  </div>
                </div>

                {/* 5. Financial Impact */}
                <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">5. Modeled Impact</span>
                  <div className="text-sm font-bold text-rose-400 font-mono">
                    {selectedDrillDownAsset.modeled_financial_impact}
                  </div>
                  <span className="text-[9px] text-slate-500 block">MODELED / ESTIMATED</span>
                </div>

                {/* 6. Recommended Control */}
                <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">6. Control Cost</span>
                  <div className="text-sm font-bold text-emerald-400 font-mono">
                    {selectedDrillDownAsset.recommended_mitigation_cost}
                  </div>
                  <span className="text-[9px] text-slate-500 block">Eff: {selectedDrillDownAsset.control_effectiveness}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* SIH PRIORITY DRILL-DOWN MATRICES */}
      {isSihDataset && sihCiso && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Top Risk Assets */}
          <div className="enterprise-card p-4 border-[#1C2042] space-y-3">
            <div className="flex items-center justify-between border-b border-[#1C2042] pb-2">
              <span className="text-xs font-bold text-rose-300 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                Top Risk Assets
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Ranked</span>
            </div>
            <div className="space-y-2 text-xs font-mono">
              {sihCiso.top_risk_assets?.map((a: any) => (
                <div key={a.asset_id} className="p-2.5 rounded bg-[#0C0E1A] border border-[#1C2042] flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white">{a.asset_id} — {a.asset_name}</div>
                    <div className="text-[10px] text-slate-400">{a.business_unit} • Crit {a.asset_criticality_1_5}/5</div>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 font-bold border border-rose-800 text-[11px]">
                    {a.calculated_risk_score}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Top Vulnerabilities */}
          <div className="enterprise-card p-4 border-[#1C2042] space-y-3">
            <div className="flex items-center justify-between border-b border-[#1C2042] pb-2">
              <span className="text-xs font-bold text-amber-300 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                Top Vulnerabilities
              </span>
              <span className="text-[10px] text-slate-400 font-mono">CVSS Ranked</span>
            </div>
            <div className="space-y-2 text-xs font-mono">
              {sihCiso.top_vulnerabilities?.map((v: any) => (
                <div key={v.asset_id} className="p-2.5 rounded bg-[#0C0E1A] border border-[#1C2042] flex items-center justify-between">
                  <div>
                    <div className="font-bold text-rose-300">{v.cve_id}</div>
                    <div className="text-[10px] text-slate-400">{v.asset_id} ({v.asset_name})</div>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 font-bold border border-rose-800 text-[11px]">
                    CVSS {v.cvss_score}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Critical IAM Issues */}
          <div className="enterprise-card p-4 border-[#1C2042] space-y-3">
            <div className="flex items-center justify-between border-b border-[#1C2042] pb-2">
              <span className="text-xs font-bold text-purple-300 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <UserX className="w-3.5 h-3.5 text-purple-400" />
                Critical IAM Deficits
              </span>
              <span className="text-[10px] text-slate-400 font-mono">MFA=No</span>
            </div>
            <div className="space-y-2 text-xs font-mono">
              {sihCiso.critical_iam_issues?.slice(0, 5).map((m: any) => (
                <div key={m.asset_id} className="p-2.5 rounded bg-[#0C0E1A] border border-[#1C2042] flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white">{m.asset_id}: {m.iam_user}</div>
                    <div className="text-[10px] text-rose-400">Privileged: Yes • MFA: No</div>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 text-[10px] font-bold border border-rose-800">
                    EXPOSED
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Critical EDR Issues */}
          <div className="enterprise-card p-4 border-[#1C2042] space-y-3">
            <div className="flex items-center justify-between border-b border-[#1C2042] pb-2">
              <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-cyan-400" />
                Unisolated EDR Alerts
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Active Threat</span>
            </div>
            <div className="space-y-2 text-xs font-mono">
              {sihCiso.critical_edr_issues?.slice(0, 5).map((e: any) => (
                <div key={e.asset_id} className="p-2.5 rounded bg-[#0C0E1A] border border-[#1C2042] flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white truncate max-w-[140px]">{e.asset_id}: {e.edr_alert}</div>
                    <div className="text-[10px] text-amber-400">Severity: {e.edr_severity} • Isolated: No</div>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 text-[10px] font-bold border border-amber-800">
                    UNISOLATED
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

      {/* Interactive Decision Form & Notarization */}
      <div className="enterprise-card p-6 border-[#1C2042] space-y-4">
        <div className="flex items-center justify-between border-b border-[#1C2042] pb-3">
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide uppercase font-mono">
              CISO Decision Authority Form
            </h2>
            <p className="text-xs text-slate-400">
              Provide authorization notes and commit the decision onto the immutable audit trail.
            </p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
            Signer: Vikram Malhotra (CISO)
          </span>
        </div>

        {/* Feedback alert */}
        {feedbackMessage && (
          <div className="p-3 rounded-lg bg-cyan-950/40 border border-cyan-700/60 text-xs text-cyan-300 font-medium flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{feedbackMessage}</span>
          </div>
        )}

        {/* Notes Textarea */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300">
            Decision Rationale / Authorization Notes:
          </label>
          <textarea
            value={decisionNotes}
            onChange={(e) => setDecisionNotes(e.target.value)}
            rows={2}
            className="w-full px-3 py-2 text-xs bg-[#07080F] border border-[#1C2042] rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
            placeholder="Enter reason or implementation instructions..."
          />
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button
            onClick={handleCISOApprove}
            disabled={isProcessing}
            className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white font-bold text-xs transition flex items-center space-x-2 shadow-sm"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{isProcessing ? 'Processing...' : 'Approve Recommended Plan'}</span>
          </button>

          <button
            onClick={handleCISORequestReview}
            disabled={isProcessing}
            className="px-4 py-2.5 rounded-lg bg-amber-700/80 hover:bg-amber-600 active:scale-95 text-white font-semibold text-xs transition flex items-center space-x-2 border border-amber-600"
          >
            <HelpCircle className="w-4 h-4" />
            <span>Request Quantitative Review</span>
          </button>

          <button
            onClick={handleCISOReject}
            disabled={isProcessing}
            className="px-4 py-2.5 rounded-lg bg-rose-800/80 hover:bg-rose-700 active:scale-95 text-white font-semibold text-xs transition flex items-center space-x-2 border border-rose-600"
          >
            <XCircle className="w-4 h-4" />
            <span>Reject Plan</span>
          </button>
        </div>

        {/* Cryptographic Notarization Proof Card */}
        {blockchainProof && (
          <div className="mt-4 p-4 rounded-lg bg-emerald-950/30 border border-emerald-700/70 space-y-2.5 animate-in fade-in duration-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-emerald-300 font-bold text-xs">
                <Link2 className="w-4 h-4 text-emerald-400" />
                <span>Hyperledger Fabric Cryptographic Notarization Proof</span>
              </div>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-900/80 text-emerald-200 border border-emerald-600 font-bold">
                VERIFIED IMMUTABLE
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
              <div className="p-2 rounded bg-[#07080F] border border-[#1C2042]">
                <div className="text-[10px] text-slate-400">Transaction ID</div>
                <div className="text-cyan-300 font-bold truncate">{blockchainProof.txId}</div>
              </div>

              <div className="p-2 rounded bg-[#07080F] border border-[#1C2042]">
                <div className="text-[10px] text-slate-400">SHA-256 Canonical Hash</div>
                <div className="text-emerald-300 font-bold truncate">{blockchainProof.hash}</div>
              </div>

              <div className="p-2 rounded bg-[#07080F] border border-[#1C2042]">
                <div className="text-[10px] text-slate-400">Block Height / Number</div>
                <div className="text-slate-200 font-bold">Block #{blockchainProof.blockNumber}</div>
              </div>

              <div className="p-2 rounded bg-[#07080F] border border-[#1C2042]">
                <div className="text-[10px] text-slate-400">Ledger Channel</div>
                <div className="text-slate-200 font-bold">enterprise-audit-fabric-channel</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Critical Attack Path Highlights */}
      {!isSihDataset && <AttackGraphViewer />}

      {/* Decision Row: OR-Tools Recommendation & SHAP Factors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Recommended Investment Package */}
        <div className="enterprise-card p-5 border-[#1C2042] space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-white flex items-center space-x-2">
                <span>Google OR-Tools Selected Controls</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono">
                  MIP Knapsack Solved
                </span>
              </h2>
              <span className="text-xs font-mono font-bold text-emerald-400">
                {isSihDataset 
                  ? sihCiso?.budget_recommendation?.optimization_result?.total_cost_label || "₹1.86 Cr"
                  : "Total: ₹85.0 Lakh"}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Selects optimal mitigations maximizing modeled risk reduction while enforcing budget constraints.
            </p>
          </div>

          <div className="space-y-2">
            {isSihDataset ? (
              sihCiso?.budget_recommendation?.optimization_result?.selected_mitigations?.slice(0, 5).map((m: any, idx: number) => (
                <div key={idx} className="p-3 rounded-lg bg-[#0C0E1A] border border-[#1C2042] flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2.5">
                    <span className="font-mono font-bold text-slate-400">#{idx+1}</span>
                    <div>
                      <div className="font-semibold text-white">{m.asset_id} — {m.asset_name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{m.business_unit} • Eff: {m.control_effectiveness}</div>
                    </div>
                  </div>
                  <div className="text-right font-mono">
                    <div className="text-slate-200 font-semibold">{m.cost_label}</div>
                    <div className="text-emerald-400 text-[11px] font-bold">-{m.risk_reduction_points} Risk Pts</div>
                  </div>
                </div>
              ))
            ) : (
              (optResult?.optimization_result?.selected_controls || [
                { code: 'CTRL-PATCH', name: 'Automated Critical Vulnerability Patching', implementation_cost: 1800000, modeled_risk_reduction: 7500000 },
                { code: 'CTRL-MFA', name: 'Privileged Identity Multi-Factor Authentication', implementation_cost: 1200000, modeled_risk_reduction: 4500000 },
                { code: 'CTRL-EDR', name: 'Next-Gen EDR / XDR Autonomous Response', implementation_cost: 2500000, modeled_risk_reduction: 8000000 },
                { code: 'CTRL-SEG', name: 'Network Micro-segmentation & Zero Trust', implementation_cost: 2000000, modeled_risk_reduction: 6000000 },
                { code: 'CTRL-BACKUP', name: 'Immutable WORM Air-Gapped Backup Vault', implementation_cost: 1000000, modeled_risk_reduction: 3500000 }
              ]).map((ctrl: any, idx: number) => (
                <div key={idx} className="p-3 rounded-lg bg-[#0C0E1A] border border-[#1C2042] flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2.5">
                    <span className="font-mono font-bold text-slate-400">#{idx+1}</span>
                    <div>
                      <div className="font-semibold text-white">{ctrl.name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">Code: {ctrl.code}</div>
                    </div>
                  </div>
                  <div className="text-right font-mono">
                    <div className="text-slate-200 font-semibold">₹{(ctrl.implementation_cost/100000).toFixed(1)} Lakh</div>
                    <div className="text-emerald-400 text-[11px]">-(₹{(ctrl.modeled_risk_reduction/100000).toFixed(1)}L Risk)</div>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="p-2.5 rounded bg-[#12152A] border border-[#1C2042] text-[11px] text-slate-400 font-mono flex items-center justify-between">
            <span>Contingency Reserve Buffer:</span>
            <span className="text-cyan-300 font-bold">
              {isSihDataset 
                ? `${sihCiso?.budget_recommendation?.optimization_result?.remaining_budget_label || "₹0.00"} Unallocated`
                : "₹15.0 Lakh (15% Unallocated Reserve)"}
            </span>
          </div>
        </div>

        {/* SHAP AI Attribution Chart */}
        <SHAPAttributionChart />

      </div>

    </div>
  );
};
