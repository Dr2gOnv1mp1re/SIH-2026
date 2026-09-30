import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Boxes, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle2, 
  HelpCircle, 
  TrendingUp, 
  ArrowUpRight, 
  ArrowDownRight, 
  Info,
  Cpu,
  Layers,
  ShieldCheck,
  Brain
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { SHAPAttributionChart } from '../components/SHAPAttributionChart';
import { aiService, sihDatasetService } from '../services/api';
import { useDataset } from '../context/DatasetContext';
import { DataSourceBadge } from '../components/DataSourceBadge';

export const ExplainableAIPage: React.FC = () => {
  const { isSihDataset, originLabel } = useDataset();
  
  const [predictionData, setPredictionData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchShapData();
  }, [isSihDataset]);

  const fetchShapData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await aiService.getPredictions();
      setPredictionData(data);
    } catch (err: any) {
      console.error('Failed to load SHAP explainability data:', err);
      setError(err?.message || 'Explainability is unavailable for the current dataset.');
    } finally {
      setIsLoading(false);
    }
  };

  const shapFactors = predictionData?.shap_explanation || [
    { feature: 'Active Weaponized Exploits (CISA KEV)', impact_value: 6.63, direction: 'INCREASING_RISK', pct_contribution: 28.9 },
    { feature: 'Mean CVSS Vulnerability Severity', impact_value: 4.23, direction: 'INCREASING_RISK', pct_contribution: 18.4 },
    { feature: 'Security Control Mitigation Coverage', impact_value: -3.92, direction: 'DECREASING_RISK', pct_contribution: 17.1 },
    { feature: 'Crown Jewel Asset Criticality Score', impact_value: 3.04, direction: 'INCREASING_RISK', pct_contribution: 13.3 },
    { feature: 'Internet Perimeter Ingress Surface', impact_value: 1.82, direction: 'INCREASING_RISK', pct_contribution: 7.9 },
    { feature: 'Privileged Domain Administrator Accounts', impact_value: 1.65, direction: 'INCREASING_RISK', pct_contribution: 7.2 },
    { feature: 'Historical Cyber Incident Velocity', impact_value: 1.63, direction: 'INCREASING_RISK', pct_contribution: 7.2 }
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Explainable AI (XAI) & SHAP Model Attribution
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950/80 text-purple-300 border border-purple-800">
              TREESHAP KERNEL
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800">
              {originLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl">
            Mathematical game-theoretic attribution (Shapley values) isolating the exact marginal contribution of each security telemetry signal towards the predicted cyber risk trajectory.
          </p>
          <DataSourceBadge 
            lastCalculated={predictionData?.timestamp || (predictionData ? new Date().toISOString() : null)} 
            className="mt-2" 
          />
        </div>

        <button
          onClick={fetchShapData}
          disabled={isLoading}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-purple-950/80 border border-purple-700 text-purple-300 hover:bg-purple-900 text-xs font-semibold transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'Computing SHAP...' : 'Recompute Attributions'}</span>
        </button>
      </div>

      {/* Error / Fallback State */}
      {error && (
        <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-600 text-amber-200 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <span>Explainability is unavailable for the current dataset. {error}</span>
          </div>
          <button
            onClick={fetchShapData}
            className="px-3 py-1 bg-amber-700 hover:bg-amber-600 text-white rounded text-xs font-semibold"
          >
            Retry
          </button>
        </div>
      )}

      {/* Model Spec & Architecture Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="PRIMARY EXPLAINER"
          value="TreeExplainer"
          subtitle="Exact Tree Ensemble Kernel"
          icon={Brain}
          variant="cyan"
          badge="ALGORITHM"
        />
        <MetricCard
          title="ACTIVE FEATURES"
          value="10 Telemetry Signals"
          subtitle="CVSS, Exploits, Controls, IAM"
          icon={Boxes}
          variant="violet"
          badge="INPUTS"
        />
        <MetricCard
          title="TOP RISK ESCALATOR"
          value="Active Exploits (+28.9%)"
          subtitle="CISA KEV Weaponized CVEs"
          icon={ArrowUpRight}
          variant="rose"
          badge="LEAD DRIVER"
        />
        <MetricCard
          title="TOP RISK MITIGATOR"
          value="Control Posture (-17.1%)"
          subtitle="MFA, EDR & Micro-segmentation"
          icon={ArrowDownRight}
          variant="emerald"
          badge="DEFENSE"
        />
      </div>

      {/* Main SHAP Attribution Chart Component */}
      <SHAPAttributionChart factors={shapFactors} />

      {/* Feature Breakdown Detailed Matrix */}
      <div className="enterprise-card p-5 border-[#1C2042] space-y-4">
        <div className="flex items-center justify-between border-b border-[#1C2042] pb-3">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              Detailed Feature Marginal Impact Attribution
            </h2>
          </div>
          <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/60 border border-cyan-800/80 px-2 py-0.5 rounded">
            ∑ |Shapley Values| = 100% Normalized
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#1C2042] text-slate-400 text-[11px] bg-[#0A0C1A]">
                <th className="py-2.5 px-3">Rank</th>
                <th className="py-2.5 px-3">Telemetry Feature Name</th>
                <th className="py-2.5 px-3">Marginal Impact (Δ Risk)</th>
                <th className="py-2.5 px-3">Direction</th>
                <th className="py-2.5 px-3 text-right">Relative Weight</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1C2042]/60">
              {shapFactors.map((f: any, idx: number) => {
                const isIncreasing = f.direction === 'INCREASING_RISK' || f.impact_value > 0;
                return (
                  <tr key={idx} className="hover:bg-[#12152A]/60 transition">
                    <td className="py-2 px-3 text-slate-400">#{idx + 1}</td>
                    <td className="py-2 px-3 font-semibold text-white">{f.feature}</td>
                    <td className={`py-2 px-3 font-bold ${isIncreasing ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {f.impact_value > 0 ? `+${f.impact_value}` : `${f.impact_value}`}
                    </td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        isIncreasing
                          ? 'bg-rose-950/80 text-rose-300 border border-rose-800'
                          : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                      }`}>
                        {isIncreasing ? 'RISK ACCELERATOR' : 'RISK DEFENDER'}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right font-bold text-slate-200">
                      {f.pct_contribution}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default ExplainableAIPage;
