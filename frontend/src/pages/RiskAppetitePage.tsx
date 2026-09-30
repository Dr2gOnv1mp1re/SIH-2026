import React, { useState } from 'react';
import { 
  Target, 
  ShieldAlert, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  DollarSign, 
  Layers, 
  Sliders, 
  ArrowRight,
  TrendingDown,
  Building2
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { useDataset } from '../context/DatasetContext';

export const RiskAppetitePage: React.FC = () => {
  const { isSihDataset, originLabel, sihMetrics } = useDataset();

  const [enterpriseAppetite, setEnterpriseAppetite] = useState<number>(10000000); // ₹1.00 Crore
  const [criticalAssetAppetite, setCriticalAssetAppetite] = useState<number>(1000000); // ₹10.0 Lakh
  const [isEditing, setIsEditing] = useState<boolean>(false);

  const currentEal = isSihDataset && sihMetrics?.total_modeled_expected_annual_loss
    ? sihMetrics.total_modeled_expected_annual_loss
    : 46000000; // ₹4.60 Crore

  const postMitigationEal = isSihDataset
    ? 20000000
    : 10000000;

  const isBreached = currentEal > enterpriseAppetite;
  const breachAmount = Math.max(0, currentEal - enterpriseAppetite);

  const formatInr = (val: number) => {
    if (!val && val !== 0) return '₹0';
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Crore`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} Lakh`;
    return `₹${Math.round(val).toLocaleString('en-IN')}`;
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Board-Approved Cyber Risk Appetite & Tolerance Framework
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950/80 text-amber-300 border border-amber-800">
              BOARD GOVERNANCE
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800">
              {originLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl">
            Formal board risk appetite thresholds establishing the boundary between acceptable operational cyber risk and unacceptable capital balance sheet exposure.
          </p>
        </div>

        <button
          onClick={() => setIsEditing(!isEditing)}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/80 border border-cyan-700 text-cyan-300 hover:bg-cyan-900 text-xs font-semibold transition"
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>{isEditing ? 'Close Calibration' : 'Calibrate Thresholds'}</span>
        </button>
      </div>

      {/* Threshold Calibration Drawer */}
      {isEditing && (
        <div className="p-5 rounded-xl bg-[#0A0C1A] border border-[#2A2F5A] space-y-4 font-mono text-xs">
          <div className="font-bold text-white text-sm flex items-center gap-2">
            <Building2 className="w-4 h-4 text-cyan-400" />
            <span>Board Risk Appetite Threshold Calibration (INR)</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-slate-400 block text-[11px]">Enterprise Risk Appetite Ceiling (₹ / year):</label>
              <input
                type="number"
                value={enterpriseAppetite}
                onChange={(e) => setEnterpriseAppetite(parseFloat(e.target.value) || 0)}
                className="w-full bg-[#12152A] border border-[#2A2F5A] rounded-lg px-3 py-2 text-white font-bold"
              />
              <span className="text-[10px] text-cyan-400">Current: {formatInr(enterpriseAppetite)}</span>
            </div>
            <div className="space-y-1">
              <label className="text-slate-400 block text-[11px]">Single Crown Jewel Critical Asset Appetite (₹ / asset):</label>
              <input
                type="number"
                value={criticalAssetAppetite}
                onChange={(e) => setCriticalAssetAppetite(parseFloat(e.target.value) || 0)}
                className="w-full bg-[#12152A] border border-[#2A2F5A] rounded-lg px-3 py-2 text-white font-bold"
              />
              <span className="text-[10px] text-cyan-400">Current: {formatInr(criticalAssetAppetite)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Risk Appetite Status Banner */}
      <div className={`p-5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
        isBreached 
          ? 'bg-rose-950/40 border-rose-800 text-rose-200' 
          : 'bg-emerald-950/40 border-emerald-800 text-emerald-200'
      }`}>
        <div className="flex items-start space-x-3">
          {isBreached ? (
            <AlertTriangle className="w-6 h-6 text-rose-400 flex-shrink-0 mt-0.5" />
          ) : (
            <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0 mt-0.5" />
          )}
          <div>
            <div className="font-bold text-sm uppercase tracking-wide font-mono">
              {isBreached ? 'BOARD RISK APPETITE THRESHOLD BREACHED' : 'ENTERPRISE RISK WITHIN APPROVED BOARD APPETITE'}
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              {isBreached
                ? `Current baseline cyber loss (${formatInr(currentEal)}) exceeds the board-authorized threshold (${formatInr(enterpriseAppetite)}) by ${formatInr(breachAmount)}. Mandatory remediation capital allocation required.`
                : `Current cyber exposure is fully compliant with board risk limits.`}
            </p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded text-xs font-bold font-mono ${
          isBreached ? 'bg-rose-900 text-rose-200 border border-rose-700' : 'bg-emerald-900 text-emerald-200 border border-emerald-700'
        }`}>
          {isBreached ? 'BREACH STATUS: ACTIVE' : 'STATUS: COMPLIANT'}
        </span>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="BOARD APPETITE CEILING"
          value={formatInr(enterpriseAppetite)}
          subtitle="Max Acceptable Exposure / Year"
          icon={Target}
          variant="cyan"
          badge="THRESHOLD"
        />
        <MetricCard
          title="CURRENT ANNUAL LOSS (EAL)"
          value={formatInr(currentEal)}
          subtitle="Unmitigated Risk Baseline"
          icon={ShieldAlert}
          variant={isBreached ? 'rose' : 'emerald'}
          badge="CURRENT"
        />
        <MetricCard
          title="EXPOSURE EXCEEDANCE (GAP)"
          value={formatInr(breachAmount)}
          subtitle="Capital Required to Mitigate"
          icon={DollarSign}
          variant="amber"
          badge="GAP"
        />
        <MetricCard
          title="POST-OPTIMIZATION EAL"
          value={formatInr(postMitigationEal)}
          subtitle="Within Appetite (Compliant)"
          icon={ShieldCheck}
          variant="emerald"
          badge="TARGET STATE"
        />
      </div>

      {/* Visual Appetite Comparison Bar */}
      <div className="enterprise-card p-6 border-[#1C2042] space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
          Visual Exposure vs Risk Appetite Comparison
        </h2>

        <div className="space-y-4 font-mono text-xs">
          {/* Current EAL bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-300 font-semibold">Current Baseline Exposure:</span>
              <span className="text-rose-400 font-bold">{formatInr(currentEal)} (Exceeds Appetite)</span>
            </div>
            <div className="h-3 w-full bg-[#0C0E1A] rounded-full overflow-hidden border border-[#1C2042] relative">
              <div 
                className="h-full bg-rose-500 rounded-full" 
                style={{ width: '92%' }}
              />
              <div 
                className="absolute top-0 bottom-0 w-0.5 bg-amber-400 z-10" 
                style={{ left: '22%' }}
                title="Board Appetite Ceiling"
              />
            </div>
          </div>

          {/* Post-Optimization EAL bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-300 font-semibold">Post-Optimization EAL (OR-Tools Portfolio):</span>
              <span className="text-emerald-400 font-bold">{formatInr(postMitigationEal)} (Within Appetite)</span>
            </div>
            <div className="h-3 w-full bg-[#0C0E1A] rounded-full overflow-hidden border border-[#1C2042]">
              <div 
                className="h-full bg-emerald-500 rounded-full" 
                style={{ width: '20%' }}
              />
            </div>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-[#0C0E1A] border border-[#1C2042] text-[11px] text-slate-400 flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Target className="w-4 h-4 text-amber-400" />
            <span>Amber marker indicates Board Authorized Risk Ceiling ({formatInr(enterpriseAppetite)})</span>
          </span>
          <span className="text-emerald-400 font-bold font-mono">95% Post-Mitigation Compliance</span>
        </div>
      </div>

    </div>
  );
};

export default RiskAppetitePage;
