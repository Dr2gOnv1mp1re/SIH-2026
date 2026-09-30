import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell
} from 'recharts';

interface MonteCarloChartProps {
  histogram?: Array<{ bin_start: number; bin_end: number; count: number; label: string }>;
  percentiles?: { p5: number; p25: number; p50_median: number; p75: number; p95: number };
}

export const MonteCarloChart: React.FC<MonteCarloChartProps> = ({ histogram, percentiles }) => {
  const p = percentiles || {
    p5: 2000000.0,
    p25: 4500000.0,
    p50_median: 7000000.0,
    p75: 11000000.0,
    p95: 24000000.0
  };

  const chartData = histogram || [
    { label: '₹10L-₹20L', count: 420 },
    { label: '₹20L-₹30L', count: 850 },
    { label: '₹30L-₹40L', count: 1420 },
    { label: '₹40L-₹50L', count: 1980 },
    { label: '₹50L-₹60L', count: 1650 },
    { label: '₹60L-₹70L', count: 1300 },
    { label: '₹70L-₹80L', count: 980 },
    { label: '₹80L-₹1.0Cr', count: 720 },
    { label: '₹1.0Cr-₹1.5Cr', count: 450 },
    { label: '₹1.5Cr-₹2.5Cr', count: 230 }
  ];

  return (
    <div className="enterprise-card p-5 border-[#1C2042] space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
            <span>Monte Carlo Stochastic Loss Distribution</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono font-bold">
              10,000 Iterations
            </span>
          </h3>
          <p className="text-xs text-slate-400">Modeled loss distribution under uncertainty across banking operations</p>
        </div>
        <span className="text-[11px] px-2.5 py-1 rounded bg-[#0C0E1A] border border-[#2A2F5A] text-slate-300 font-mono">
          MODELED ESTIMATE
        </span>
      </div>

      {/* Percentiles Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-1">
        <div className="p-2.5 rounded-lg bg-[#0C0E1A] border border-[#1C2042] text-center">
          <div className="text-[10px] text-slate-400 font-semibold uppercase">5th Percentile</div>
          <div className="text-xs font-bold font-mono text-emerald-400 mt-0.5">₹{roundLakh(p.p5)}</div>
        </div>
        <div className="p-2.5 rounded-lg bg-[#0C0E1A] border border-[#1C2042] text-center">
          <div className="text-[10px] text-slate-400 font-semibold uppercase">25th Percentile</div>
          <div className="text-xs font-bold font-mono text-slate-200 mt-0.5">₹{roundLakh(p.p25)}</div>
        </div>
        <div className="p-2.5 rounded-lg bg-cyan-950/40 border border-cyan-700/80 text-center">
          <div className="text-[10px] text-cyan-300 font-bold uppercase">50th (Median)</div>
          <div className="text-xs font-bold font-mono text-white mt-0.5">₹{roundLakh(p.p50_median)}</div>
        </div>
        <div className="p-2.5 rounded-lg bg-[#0C0E1A] border border-[#1C2042] text-center">
          <div className="text-[10px] text-slate-400 font-semibold uppercase">75th Percentile</div>
          <div className="text-xs font-bold font-mono text-amber-400 mt-0.5">₹{roundLakh(p.p75)}</div>
        </div>
        <div className="p-2.5 rounded-lg bg-rose-950/40 border border-red-700/80 text-center">
          <div className="text-[10px] text-rose-300 font-bold uppercase">95th (Worst Case)</div>
          <div className="text-xs font-bold font-mono text-rose-300 mt-0.5">₹{roundLakh(p.p95)}</div>
        </div>
      </div>

      {/* Recharts Histogram */}
      <div className="h-52 w-full pt-1">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="label" stroke="#64748B" fontSize={10} tickLine={false} />
            <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#141C2E', borderColor: '#2A3B54', borderRadius: '6px', fontSize: '11px' }}
              labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
              formatter={(val: any) => [`${val} simulated loss outcomes`, 'Frequency']}
            />
            <Bar dataKey="count" radius={[3, 3, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={index > 7 ? '#EF4444' : (index >= 4 ? '#3B82F6' : '#2563EB')} 
                  opacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="text-[10px] text-slate-500 font-mono text-center pt-1 border-t border-[#1C2042]">
        Modeled loss distribution under uncertainty • 10,000 Pseudo-Random Monte Carlo Trials
      </div>
    </div>
  );
};

function roundLakh(val: number): string {
  if (val >= 10000000) {
    return `${(val / 10000000).toFixed(2)} Cr`;
  }
  return `${(val / 100000).toFixed(1)} L`;
}
