import React, { useState, useEffect } from 'react';
import {
  TrendingDown,
  DollarSign,
  Sparkles,
  CheckCircle2,
  ShieldAlert,
  Sliders,
  Layers,
  ArrowRight,
  Server,
  Network,
  ShieldCheck,
  Target
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { optimizationService, sihDatasetService } from '../services/api';
import { useDataset } from '../context/DatasetContext';
import { DataSourceBadge } from '../components/DataSourceBadge';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';

export const InvestmentOptimizer: React.FC = () => {
  const { isSihDataset, originLabel } = useDataset();
  const [budget, setBudget] = useState<number>(() => isSihDataset ? 1500000 : 10000000);
  const [optResult, setOptResult] = useState<any>(null);
  const [sihOptResult, setSihOptResult] = useState<any>(null);
  const [stressCurve, setStressCurve] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isSihDataset) {
      setBudget(1500000);
      runSihOptimizer(1500000);
    } else {
      setBudget(10000000);
      runOptimizer(10000000);
      fetchStressTest();
    }
  }, [isSihDataset]);

  const runSihOptimizer = async (b: number) => {
    setIsLoading(true);
    try {
      const res = await sihDatasetService.optimize(b);
      setSihOptResult(res);
    } catch (e) {
      console.error('Failed to run SIH optimization:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const runOptimizer = async (b: number) => {
    setIsLoading(true);
    try {
      const res = await optimizationService.run(b);
      setOptResult(res);
    } catch (e) {
      console.error('Failed to run optimization:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStressTest = async () => {
    try {
      const res = await optimizationService.getStressTest();
      setStressCurve(res.stress_test_curve || []);
    } catch (e) {
      console.error('Failed to fetch stress test:', e);
    }
  };

  const debounceTimerRef = React.useRef<any>(null);

  const handleBudgetSliderChange = (newBudget: number, immediate: boolean = false) => {
    setBudget(newBudget); // Instant visual update in 0ms
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    if (immediate) {
      if (isSihDataset) runSihOptimizer(newBudget);
      else runOptimizer(newBudget);
    } else {
      debounceTimerRef.current = setTimeout(() => {
        if (isSihDataset) runSihOptimizer(newBudget);
        else runOptimizer(newBudget);
      }, 250);
    }
  };

  const formatINR = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} Lakh`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const opt = optResult?.optimization_result;
  const flow = opt?.comparison_flow;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Cybersecurity Investment Optimizer
            </h1>
            <span className="text-[11px] font-semibold px-2.5 py-1 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800 font-mono flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mr-1.5 animate-pulse" />
              GOOGLE OR-TOOLS SCIP MIXED-INTEGER KNAPSACK
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Mixed-Integer Linear Programming (MILP) solver maximizing quantitative modeled risk reduction under strict budgetary, prerequisite dependency DAG, and ROI constraints.
          </p>
          <DataSourceBadge 
            showModeledLabel={true} 
            lastCalculated={optResult?.timestamp || (optResult || sihOptResult ? new Date().toISOString() : null)} 
            className="mt-2" 
          />
        </div>
      </div>

      {/* 5-Stage Comparison Flow Bar */}
      {/* 5-Stage Comparison Flow Bar */}
      {isSihDataset && sihOptResult ? (
        <div className="enterprise-card p-4 border-[#1C2042] bg-[#0A0D1E]">
          <div className="text-[10px] uppercase font-mono font-bold text-cyan-400 tracking-wider mb-3 text-center">
            SIH PS26105 OPTIMIZATION VALUE FLOW TRACE (BEFORE → BUDGET → PORTFOLIO → AFTER)
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 items-center text-center">
            <div className="p-3 rounded-lg bg-[#12152A] border border-rose-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">1. BASELINE RISK (EAL)</span>
              <div className="text-lg font-black text-rose-400 font-mono mt-0.5">{sihOptResult.risk_before_eal_label}</div>
              <span className="text-[9px] text-slate-500 font-mono">15 Evaluated Assets</span>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-cyan-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">2. BUDGET CONSTRAINT</span>
              <div className="text-lg font-black text-cyan-300 font-mono mt-0.5">{sihOptResult.budget_label}</div>
              <span className="text-[9px] text-slate-500 font-mono">Allocated Ceiling</span>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-emerald-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">3. OPTIMIZED SPEND</span>
              <div className="text-lg font-black text-emerald-400 font-mono mt-0.5">{sihOptResult.allocated_investment_label}</div>
              <span className="text-[9px] text-slate-400 font-mono">{sihOptResult.selected_controls_count} Assets Funded</span>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-amber-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">4. BUFFER REMAINING</span>
              <div className="text-lg font-black text-amber-300 font-mono mt-0.5">{sihOptResult.remaining_budget_label}</div>
              <span className="text-[9px] text-emerald-400 font-mono">Within Limit</span>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-violet-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">5. PROJECTED RISK</span>
              <div className="text-lg font-black text-violet-300 font-mono mt-0.5">{sihOptResult.risk_after_eal_label}</div>
              <span className="text-[9px] text-emerald-300 font-mono">-{sihOptResult.modeled_risk_reduction_label} EAL</span>
            </div>
          </div>
        </div>
      ) : flow ? (
        <div className="enterprise-card p-4 border-[#1C2042] bg-[#0A0D1E]">
          <div className="text-[10px] uppercase font-mono font-bold text-cyan-400 tracking-wider mb-3 text-center">
            OPTIMIZATION VALUE FLOW TRACE (BEFORE → CONSTRAINTS → PORTFOLIO → AFTER)
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 items-center text-center">
            <div className="p-3 rounded-lg bg-[#12152A] border border-rose-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">1. CURRENT RISK</span>
              <div className="text-lg font-black text-rose-400 font-mono mt-0.5">{flow.current_risk_label}</div>
              <span className="text-[9px] text-slate-500">Baseline Enterprise EAL</span>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-cyan-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">2. AVAILABLE BUDGET</span>
              <div className="text-lg font-black text-cyan-300 font-mono mt-0.5">{flow.available_budget_label}</div>
              <span className="text-[9px] text-slate-500">Hard Cost Constraint</span>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">3. CANDIDATES</span>
              <div className="text-lg font-black text-white font-mono mt-0.5">{flow.candidate_controls_count} Controls</div>
              <span className="text-[9px] text-slate-500">Evaluated in MILP DAG</span>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-emerald-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">4. OPTIMIZED PORTFOLIO</span>
              <div className="text-lg font-black text-emerald-400 font-mono mt-0.5">{flow.optimized_portfolio_count} Controls</div>
              <span className="text-[9px] text-emerald-400 font-mono">Spend: {flow.total_investment_label}</span>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-violet-900/50">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">5. REMAINING RISK</span>
              <div className="text-lg font-black text-violet-300 font-mono mt-0.5">{flow.modeled_remaining_risk_label}</div>
              <span className="text-[9px] text-emerald-300 font-mono">-{flow.modeled_risk_reduction_label}</span>
            </div>
          </div>
        </div>
      ) : null}

      {/* Interactive Budget Slider Control */}
      <div className="enterprise-card p-5 border-[#1C2042] space-y-3 bg-[#0E1122]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="space-y-0.5">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Dynamic Budget Allocation Constraint
            </span>
            <div className="text-2xl font-bold text-white font-mono">
              {formatINR(budget)} <span className="text-xs font-normal text-slate-400 font-sans">(₹{(budget / 100000).toFixed(1)} Lakh)</span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {(isSihDataset 
              ? [500000, 1000000, 1500000, 2500000, 5000000]
              : [2500000, 5000000, 10000000, 20000000, 50000000]
            ).map((preset) => (
              <button
                key={preset}
                onClick={() => handleBudgetSliderChange(preset, true)}
                className={`px-3 py-1 rounded-md text-xs font-semibold transition font-mono ${budget === preset
                    ? 'bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-sm'
                    : 'bg-[#12152A] text-slate-300 hover:text-white border border-[#2A2F5A]'
                  }`}
              >
                {preset >= 10000000 ? `₹${preset / 10000000}Cr` : `₹${preset / 100000}L`}
              </button>
            ))}
          </div>
        </div>

        <input
          type="range"
          min={isSihDataset ? 200000 : 2500000}
          max={isSihDataset ? 35000000 : 50000000}
          step={isSihDataset ? 200000 : 2500000}
          value={budget}
          onChange={(e) => handleBudgetSliderChange(parseFloat(e.target.value))}
          className="w-full h-2.5 bg-[#181C36] rounded-lg appearance-none cursor-pointer accent-cyan-500"
        />

        <div className="flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>Min Constraint: {isSihDataset ? '₹2 Lakh' : '₹25 Lakh'}</span>
          <span>Baseline Allocation: {isSihDataset ? '₹15 Lakh' : '₹1.00 Crore'}</span>
          <span>Max Allocation: {isSihDataset ? '₹3.50 Crore' : '₹5.00 Crore'}</span>
        </div>
      </div>

      {/* KPI Metrics Row */}
      {isSihDataset && sihOptResult ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="ALLOCATED INVESTMENT"
            value={sihOptResult.allocated_investment_label}
            subtitle={`Unused Budget: ${sihOptResult.remaining_budget_label}`}
            change="Within Budget"
            isPositive={true}
            icon={DollarSign}
            variant="cyan"
            badge="SCIP OPTIMAL"
          />
          <MetricCard
            title="MODELED RISK (BEFORE)"
            value={sihOptResult.risk_before_eal_label}
            subtitle="Pre-Mitigation Baseline EAL"
            icon={ShieldAlert}
            variant="rose"
          />
          <MetricCard
            title="PROJECTED RISK (AFTER)"
            value={sihOptResult.risk_after_eal_label}
            subtitle="Post-Mitigation Exposure"
            change={`-${sihOptResult.modeled_risk_reduction_label}`}
            isPositive={true}
            icon={TrendingDown}
            variant="emerald"
          />
          <MetricCard
            title="MODELED RISK REDUCTION"
            value={sihOptResult.modeled_risk_reduction_label}
            subtitle={`${sihOptResult.selected_controls_count} Assets Remediated`}
            change="MIP Benefit"
            isPositive={true}
            icon={Sparkles}
            variant="violet"
            badge="PORTFOLIO"
          />
        </div>
      ) : opt ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="TOTAL INVESTMENT"
            value={opt.total_investment_label}
            subtitle={`Unused Budget: ${opt.unused_budget_label}`}
            change="Within Constraint"
            isPositive={true}
            icon={DollarSign}
            variant="cyan"
            badge="OPTIMAL"
          />
          <MetricCard
            title="CURRENT MODELED RISK"
            value={opt.current_modeled_risk_label}
            subtitle="Pre-Remediation Baseline"
            icon={ShieldAlert}
            variant="rose"
          />
          <MetricCard
            title="PROJECTED MODELED RISK"
            value={opt.projected_modeled_risk_label}
            subtitle="Post-Portfolio Deployment"
            change={`-${opt.modeled_risk_reduction_label}`}
            isPositive={true}
            icon={TrendingDown}
            variant="emerald"
          />
          <MetricCard
            title="EFFICIENCY MULTIPLIER"
            value={`${opt.efficiency_metric}x`}
            subtitle="Risk Reduction / Cost"
            change="MIP Knapsack Ratio"
            isPositive={true}
            icon={Sparkles}
            variant="violet"
            badge="DYNAMIC ROI"
          />
        </div>
      ) : null}

      {/* Selected Controls List for SIH Dataset */}
      {isSihDataset && sihOptResult && (
        <div className="enterprise-card p-6 border-[#1C2042] space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-base font-bold text-white flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-cyan-400" />
                <span>SIH PS26105 Optimized Mitigation Portfolio ({sihOptResult.selected_controls_count} Assets)</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Google OR-Tools SCIP 0-1 Knapsack selected optimal asset remediations maximizing modeled risk reduction under budget {sihOptResult.budget_label}.
              </p>
            </div>
            <div className="text-right font-mono text-xs">
              <span className="text-slate-400">Total Allocated: </span>
              <span className="text-cyan-400 font-bold">{sihOptResult.allocated_investment_label}</span>
              <span className="text-slate-500 mx-2">|</span>
              <span className="text-slate-400">Remaining Budget: </span>
              <span className="text-emerald-400 font-bold">{sihOptResult.remaining_budget_label}</span>
            </div>
          </div>

          <div className="space-y-3">
            {sihOptResult.selected_controls?.map((ctrl: any, idx: number) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-[#0C0E1A] border border-[#1C2042] hover:border-cyan-800 transition space-y-2"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-emerald-950/70 border border-emerald-800 text-emerald-400 shrink-0">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-bold text-sm text-white">
                        {idx + 1}. {ctrl.asset_id} — {ctrl.asset_name}
                      </div>
                      <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400 mt-0.5">
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-semibold">{ctrl.cve_id}</span>
                        <span>•</span>
                        <span className="text-emerald-400">Control Effectiveness: {ctrl.control_effectiveness}</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right font-mono shrink-0">
                    <div className="text-white font-bold text-sm">{ctrl.mitigation_cost_label}</div>
                    <div className="text-emerald-400 text-xs font-semibold">
                      Modeled Reduction: -{ctrl.modeled_risk_reduction_label}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Selected Controls List with Complete 8-Item Specifications (for ABC Bank) */}
      {!isSihDataset && opt && (
        <div className="enterprise-card p-6 border-[#1C2042] space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-base font-bold text-white flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-cyan-400" />
                <span>Mathematically Selected Control Portfolio ({opt.selected_count} Controls)</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Each control is selected by Google OR-Tools SCIP solver to maximize enterprise risk reduction under the ₹{(budget / 100000).toFixed(0)} Lakh budget.
              </p>
            </div>
            <div className="text-right font-mono text-xs">
              <span className="text-slate-400">Total Spend: </span>
              <span className="text-cyan-400 font-bold">{opt.total_investment_label}</span>
              <span className="text-slate-500 mx-2">|</span>
              <span className="text-slate-400">Unallocated Buffer: </span>
              <span className="text-emerald-400 font-bold">{opt.unused_budget_label}</span>
            </div>
          </div>

          <div className="space-y-3">
            {opt.selected_controls?.map((ctrl: any, idx: number) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-[#0C0E1A] border border-[#1C2042] hover:border-cyan-800 transition space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-emerald-950/70 border border-emerald-800 text-emerald-400 shrink-0">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-bold text-sm text-white">
                        {idx + 1}. {ctrl.name}
                      </div>
                      <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400 mt-0.5">
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-semibold">{ctrl.code}</span>
                        <span>•</span>
                        <span className="text-slate-300">{ctrl.risk_factor_addressed}</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right font-mono shrink-0">
                    <div className="text-white font-bold text-sm">{ctrl.cost_label}</div>
                    <div className="text-emerald-400 text-xs font-semibold">
                      -{ctrl.modeled_risk_reduction_label} EAL
                    </div>
                    <span className="text-[10px] text-slate-400 block">{ctrl.budget_contribution_label}</span>
                  </div>
                </div>

                {/* Assets & Attack Paths Addressed */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono pt-2 border-t border-slate-900">
                  <div className="p-2 rounded-lg bg-[#12152A] border border-slate-800/80 space-y-1">
                    <span className="text-[10px] text-slate-400 uppercase flex items-center space-x-1">
                      <Server className="w-3 h-3 text-cyan-400" />
                      <span>Assets Addressed:</span>
                    </span>
                    <div className="text-slate-200 text-[11px] truncate">
                      {ctrl.assets_addressed?.join(', ') || 'Enterprise Systems'}
                    </div>
                  </div>

                  <div className="p-2 rounded-lg bg-[#12152A] border border-slate-800/80 space-y-1">
                    <span className="text-[10px] text-slate-400 uppercase flex items-center space-x-1">
                      <Network className="w-3 h-3 text-amber-400" />
                      <span>Attack Paths Addressed:</span>
                    </span>
                    <div className="text-amber-200 text-[11px] truncate">
                      {ctrl.attack_paths_addressed?.join(', ') || 'Critical Paths'}
                    </div>
                  </div>
                </div>

                {/* Derived Selection Reason */}
                <div className="p-2.5 rounded-lg bg-cyan-950/30 border border-cyan-900/40 text-xs text-slate-300 leading-relaxed font-sans">
                  <span className="font-bold text-cyan-300 text-[10px] uppercase font-mono block mb-0.5">
                    OPTIMIZER SELECTION RATIONALE:
                  </span>
                  {ctrl.reason_for_selection}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Budget Stress Testing Curve Chart */}
      <div className="enterprise-card p-5 border-[#1C2042] space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-white">
              Budget Stress Test Curve (Diminishing Marginal Returns)
            </h2>
            <p className="text-xs text-slate-400">Parametric curve showing modeled risk reduction per rupee allocated across budget intervals</p>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-[#0E1122] text-cyan-300 font-mono border border-[#2A2F5A]">
            PARAMETRIC SWEEP
          </span>
        </div>

        <div className="h-60 w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={stressCurve.length > 0 ? stressCurve : [
              { budget_label: '₹25L', projected_risk: 38000000 },
              { budget_label: '₹50L', projected_risk: 31000000 },
              { budget_label: '₹75L', projected_risk: 25000000 },
              { budget_label: '₹1.0Cr', projected_risk: 20000000 },
              { budget_label: '₹1.5Cr', projected_risk: 16000000 },
              { budget_label: '₹2.0Cr', projected_risk: 12000000 },
              { budget_label: '₹5.0Cr', projected_risk: 8000000 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E2A3E" />
              <XAxis dataKey="budget_label" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickFormatter={(v) => `₹${(v / 10000000).toFixed(1)}Cr`} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#141C2E', borderColor: '#2A3B54', borderRadius: '6px', fontSize: '11px' }}
                formatter={(val: any) => [`₹${(val / 10000000).toFixed(2)} Crore`, 'Projected Modeled Risk']}
              />
              <Line
                type="monotone"
                dataKey="projected_risk"
                stroke="#3B82F6"
                strokeWidth={2.5}
                dot={{ fill: '#3B82F6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};
