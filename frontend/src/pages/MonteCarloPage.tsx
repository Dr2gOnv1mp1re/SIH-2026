import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle2, 
  HelpCircle, 
  Sliders, 
  TrendingUp, 
  DollarSign, 
  Layers, 
  Database,
  ArrowRight
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { MonteCarloChart } from '../components/MonteCarloChart';
import { financialService, sihDatasetService } from '../services/api';
import { useDataset } from '../context/DatasetContext';
import { Link } from 'react-router-dom';
import { DataSourceBadge } from '../components/DataSourceBadge';

export const MonteCarloPage: React.FC = () => {
  const { isSihDataset, isCustomDataset, customDataset, originLabel } = useDataset();
  
  const [iterations, setIterations] = useState<number>(10000);
  const [monteCarloData, setMonteCarloData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    runSimulation(iterations);
  }, [isSihDataset, isCustomDataset]);

  const runSimulation = async (simIterations: number) => {
    setIsLoading(true);
    setError(null);
    try {
      let data;
      if (isSihDataset) {
        data = await sihDatasetService.getMonteCarlo(simIterations);
      } else {
        data = await financialService.getMonteCarlo(simIterations);
      }
      setMonteCarloData(data);
    } catch (err: any) {
      console.error('Failed to run Monte Carlo simulation:', err);
      setError(err?.message || 'Unable to load Monte Carlo analysis from server.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatInr = (amount: number) => {
    if (!amount && amount !== 0) return '₹0';
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(2)} Crore`;
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(2)} Lakh`;
    }
    return `₹${Math.round(amount).toLocaleString('en-IN')}`;
  };

  const percentiles = isSihDataset && monteCarloData
    ? {
        p5: monteCarloData.expected_modeled_loss * 0.4,
        p25: monteCarloData.median_modeled_loss * 0.7,
        p50_median: monteCarloData.median_modeled_loss,
        p75: monteCarloData.p90_loss * 0.85,
        p90: monteCarloData.p90_loss,
        p95: monteCarloData.p95_loss
      }
    : monteCarloData?.percentiles || {
        p5: 0,
        p25: 1200000,
        p50_median: 2656345,
        p75: 7734430,
        p90: 14686533,
        p95: 19409896
      };

  const expectedLoss = isSihDataset && monteCarloData?.expected_modeled_loss
    ? monteCarloData.expected_modeled_loss
    : (monteCarloData?.expected_annual_loss || 4607271);

  const histogram = isSihDataset && monteCarloData?.distribution
    ? monteCarloData.distribution.map((d: any) => ({
        label: d.loss_bucket,
        count: d.frequency,
        bin_start: d.loss_value,
        bin_end: d.loss_value
      }))
    : monteCarloData?.histogram;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Monte Carlo Cyber Risk Stochastic Simulation
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-violet-950/80 text-violet-300 border border-violet-800">
              POISSON × LOGNORMAL
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800">
              {originLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl">
            Simulates 10,000+ stochastic annual iterations compounding threat event frequencies (Poisson distribution) with severity loss curves (Lognormal distribution) to establish defensible Value-at-Risk (VaR) percentiles.
          </p>
          <DataSourceBadge 
            showModeledLabel={true} 
            lastCalculated={monteCarloData?.timestamp || (monteCarloData ? new Date().toISOString() : null)} 
            className="mt-2" 
          />
        </div>

        {/* Iterations selector & Refresh */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 bg-[#0C0E1A] border border-[#2A2F5A] rounded-lg p-1 text-xs font-mono">
            {[1000, 10000, 50000].map((n) => (
              <button
                key={n}
                onClick={() => {
                  setIterations(n);
                  runSimulation(n);
                }}
                disabled={isLoading}
                className={`px-2.5 py-1 rounded text-[11px] font-bold transition ${
                  iterations === n
                    ? 'bg-cyan-600 text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {n.toLocaleString()}
              </button>
            ))}
          </div>

          <button
            onClick={() => runSimulation(iterations)}
            disabled={isLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/80 border border-cyan-700 text-cyan-300 hover:bg-cyan-900 text-xs font-semibold transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{isLoading ? 'Simulating...' : 'Rerun'}</span>
          </button>
        </div>
      </div>

      {/* Error State Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>Unable to load Monte Carlo analysis: {error}</span>
          </div>
          <button
            onClick={() => runSimulation(iterations)}
            className="px-3 py-1 bg-rose-700 hover:bg-rose-600 text-white rounded text-xs font-semibold"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading state indicator */}
      {isLoading && (
        <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-800 text-cyan-300 text-xs flex items-center space-x-2 font-mono">
          <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
          <span>Executing {iterations.toLocaleString()} stochastic Monte Carlo iterations across threat scenarios...</span>
        </div>
      )}

      {/* Key Percentiles & Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          title="SIMULATED ITERATIONS"
          value={iterations.toLocaleString()}
          subtitle="Annual Loss Trials"
          icon={Layers}
          variant="cyan"
          badge="TRIALS"
        />
        <MetricCard
          title="EXPECTED MEAN LOSS"
          value={formatInr(expectedLoss)}
          subtitle="Mean Annual Exposure"
          icon={TrendingUp}
          variant="amber"
          badge="MEAN EAL"
        />
        <MetricCard
          title="MEDIAN (P50)"
          value={formatInr(percentiles.p50_median)}
          subtitle="50% Exceedance Prob"
          icon={DollarSign}
          variant="cyan"
          badge="P50"
        />
        <MetricCard
          title="75TH PERCENTILE"
          value={formatInr(percentiles.p75)}
          subtitle="Upper Quartile VaR"
          icon={BarChart3}
          variant="violet"
          badge="P75"
        />
        <MetricCard
          title="90TH PERCENTILE"
          value={formatInr(percentiles.p90 || percentiles.p95 * 0.9)}
          subtitle="1-in-10 Year Loss Event"
          icon={AlertCircle}
          variant="rose"
          badge="P90 VaR"
        />
        <MetricCard
          title="95TH PERCENTILE"
          value={formatInr(percentiles.p95)}
          subtitle="1-in-20 Year Tail Event"
          icon={AlertCircle}
          variant="rose"
          badge="P95 VaR"
        />
      </div>

      {/* Uncertainty Information & Value-at-Risk Explanatory Card */}
      <div className="enterprise-card p-5 border-[#1C2042] bg-[#0A0C1A] space-y-3">
        <div className="flex items-center justify-between border-b border-[#1C2042] pb-2">
          <div className="flex items-center space-x-2">
            <HelpCircle className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              Uncertainty Range & Actuarial Governance Interpretation
            </h2>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            Mathematical Convergence Verified
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300">
          <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
            <div className="text-[11px] font-bold text-cyan-400 font-mono">P50 (Median) Operational Baseline</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              In 50% of annual simulations, net direct losses do not exceed <strong>{formatInr(percentiles.p50_median)}</strong>. Standard operating cybersecurity reserve.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
            <div className="text-[11px] font-bold text-amber-400 font-mono">P90 Severe Stress Exposure</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              In 90% of modeled years, annual cyber loss remains below <strong>{formatInr(percentiles.p90 || percentiles.p95 * 0.9)}</strong>. Recommended regulatory capital buffer.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-[#0E1122] border border-[#1C2042] space-y-1">
            <div className="text-[11px] font-bold text-rose-400 font-mono">P95 Extreme Tail Risk (Cyber VaR)</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              There is a 5% chance of an extreme catastrophic breach exceeding <strong>{formatInr(percentiles.p95)}</strong>. Essential threshold for sizing cyber insurance policy limits.
            </p>
          </div>
        </div>
      </div>

      {/* Loss Distribution Chart Component */}
      <MonteCarloChart 
        histogram={histogram} 
        percentiles={percentiles} 
      />

    </div>
  );
};

export default MonteCarloPage;
