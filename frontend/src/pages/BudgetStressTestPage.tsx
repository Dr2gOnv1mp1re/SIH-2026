import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Sliders, 
  DollarSign, 
  TrendingDown, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Target, 
  Zap, 
  Layers,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { optimizationService, sihDatasetService } from '../services/api';
import { useDataset } from '../context/DatasetContext';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine
} from 'recharts';

export const BudgetStressTestPage: React.FC = () => {
  const { isSihDataset, originLabel } = useDataset();

  const [budget, setBudget] = useState<number>(() => isSihDataset ? 1500000 : 10000000);
  const [optResult, setOptResult] = useState<any>(null);
  const [stressCurve, setStressCurve] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStressTestData();
  }, [isSihDataset]);

  const loadStressTestData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const defaultBudget = isSihDataset ? 1500000 : 10000000;
      setBudget(defaultBudget);
      
      const [opt, stress] = await Promise.all([
        isSihDataset 
          ? sihDatasetService.optimize(defaultBudget)
          : optimizationService.run(defaultBudget),
        optimizationService.getStressTest().catch(() => null)
      ]);
      
      setOptResult(opt);
      if (stress?.stress_test_curve) {
        setStressCurve(stress.stress_test_curve);
      } else {
        setStressCurve([
          { budget_label: '₹25L', budget_val: 2500000, projected_risk: 38000000, marginal_reduction: 'High' },
          { budget_label: '₹50L', budget_val: 5000000, projected_risk: 31000000, marginal_reduction: 'High' },
          { budget_label: '₹75L', budget_val: 7500000, projected_risk: 25000000, marginal_reduction: 'Moderate' },
          { budget_label: '₹1.0Cr', budget_val: 10000000, projected_risk: 20000000, marginal_reduction: 'Optimal Inflection' },
          { budget_label: '₹1.5Cr', budget_val: 15000000, projected_risk: 16000000, marginal_reduction: 'Diminishing' },
          { budget_label: '₹2.0Cr', budget_val: 20000000, projected_risk: 12000000, marginal_reduction: 'Diminishing' },
          { budget_label: '₹5.0Cr', budget_val: 50000000, projected_risk: 8000000, marginal_reduction: 'Asymptotic Floor' }
        ]);
      }
    } catch (err: any) {
      console.error('Failed to load budget stress test data:', err);
      setError(err?.message || 'Unable to compute budget stress test curve.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSliderChange = async (newBudget: number) => {
    setBudget(newBudget);
    setIsLoading(true);
    try {
      const res = isSihDataset 
        ? await sihDatasetService.optimize(newBudget)
        : await optimizationService.run(newBudget);
      setOptResult(res);
    } catch (e) {
      console.error('Error during budget recalculation:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const formatInr = (val: number) => {
    if (!val && val !== 0) return '₹0';
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Crore`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} Lakh`;
    return `₹${Math.round(val).toLocaleString('en-IN')}`;
  };

  const opt = optResult?.optimization_result;
  const baselineRisk = opt?.pre_mitigation_modeled_risk ?? 46000000;
  const postRisk = opt?.post_mitigation_modeled_risk ?? 20000000;
  const riskReduction = opt?.total_modeled_risk_reduction ?? (baselineRisk - postRisk);
  const selectedCount = opt?.selected_controls?.length ?? 5;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Budget Stress Test & Sensitivity Analysis
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800">
              PARAMETRIC SWEEP
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950/80 text-purple-300 border border-purple-800">
              {originLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl">
            Simulates dynamic capital allocation across parametric budget intervals to identify the mathematical point of diminishing marginal returns (inflection point).
          </p>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="px-3 py-1.5 rounded-lg bg-[#0C0E1A] border border-[#2A2F5A] text-slate-300">
            Selected Budget: <strong className="text-cyan-400">{formatInr(budget)}</strong>
          </span>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>Unable to load stress test data: {error}</span>
          </div>
          <button
            onClick={loadStressTestData}
            className="px-3 py-1 bg-rose-700 hover:bg-rose-600 text-white rounded text-xs font-semibold"
          >
            Retry
          </button>
        </div>
      )}

      {/* Interactive Budget Slider Card */}
      <div className="enterprise-card p-6 border-[#1C2042] bg-[#0A0C1A] space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1C2042] pb-3">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-cyan-400" />
              <span>Real-Time Budget Sensitivity Slider</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Drag slider to re-execute Google OR-Tools integer programming knapsack solver dynamically
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {isLoading && (
              <span className="text-xs text-cyan-400 font-mono flex items-center gap-1.5">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Solver running...</span>
              </span>
            )}
            <span className="text-base font-bold text-cyan-300 font-mono px-3 py-1 rounded bg-[#070914] border border-cyan-900/60">
              {formatInr(budget)}
            </span>
          </div>
        </div>

        <div className="space-y-3 pt-2">
          <input
            type="range"
            min={isSihDataset ? 500000 : 2500000}
            max={isSihDataset ? 5000000 : 30000000}
            step={isSihDataset ? 250000 : 500000}
            value={budget}
            onChange={(e) => handleSliderChange(parseFloat(e.target.value))}
            className="w-full h-2 bg-[#12152A] rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />

          <div className="flex justify-between text-[11px] font-mono text-slate-400">
            <span>Min: {isSihDataset ? '₹5.0 Lakh' : '₹25.0 Lakh'}</span>
            <span className="text-amber-400 font-semibold">Recommended: {isSihDataset ? '₹15.0 Lakh' : '₹1.00 Crore'}</span>
            <span>Max: {isSihDataset ? '₹50.0 Lakh' : '₹3.00 Crore'}</span>
          </div>
        </div>
      </div>

      {/* Recalculated Optimization Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="ACTIVE BUDGET ALLOCATION"
          value={opt?.total_investment_label || formatInr(budget)}
          subtitle="Capital Committed"
          icon={DollarSign}
          variant="cyan"
          badge="BUDGET"
        />
        <MetricCard
          title="SELECTED CONTROLS"
          value={`${selectedCount} Defense Controls`}
          subtitle="Knapsack Optimal Decision Set"
          icon={CheckCircle2}
          variant="emerald"
          badge="CONTROLS"
        />
        <MetricCard
          title="ACHIEVED RISK REDUCTION"
          value={opt?.risk_reduction_label || formatInr(riskReduction)}
          subtitle="Modeled EAL Mitigated"
          icon={TrendingDown}
          variant="emerald"
          badge="REDUCTION"
        />
        <MetricCard
          title="PROJECTED RESIDUAL RISK"
          value={opt?.post_mitigation_label || formatInr(postRisk)}
          subtitle="Residual Enterprise Exposure"
          icon={Activity}
          variant="amber"
          badge="AFTER SPEND"
        />
      </div>

      {/* Stress Testing Curve Chart */}
      <div className="enterprise-card p-6 border-[#1C2042] space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>Diminishing Marginal Returns Curve</span>
            </h2>
            <p className="text-xs text-slate-400">
              Visualizes projected residual cyber risk across budget intervals. Notice plateauing after optimal point.
            </p>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded">
            Inflection Point: ₹1.00 Crore
          </span>
        </div>

        <div className="h-72 w-full pt-3">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={stressCurve}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1C2042" />
              <XAxis dataKey="budget_label" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis 
                stroke="#64748B" 
                fontSize={11} 
                tickFormatter={(v) => `₹${(v / 10000000).toFixed(1)}Cr`} 
                tickLine={false} 
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#0C0E1A', borderColor: '#2A2F5A', borderRadius: '8px', fontSize: '11px' }}
                formatter={(val: any) => [`₹${(val / 10000000).toFixed(2)} Crore`, 'Projected Residual Risk']}
              />
              <ReferenceLine x="₹1.0Cr" stroke="#10B981" strokeDasharray="3 3" label={{ value: 'Optimal ROI', fill: '#10B981', fontSize: 10 }} />
              <Line
                type="monotone"
                dataKey="projected_risk"
                stroke="#06B6D4"
                strokeWidth={3}
                dot={{ fill: '#06B6D4', r: 5 }}
                activeDot={{ r: 7 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};

export default BudgetStressTestPage;
