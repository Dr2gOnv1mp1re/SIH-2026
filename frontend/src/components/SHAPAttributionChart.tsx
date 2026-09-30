import React from 'react';
import { Sparkles, ArrowUpRight, ArrowDownRight, Info } from 'lucide-react';

interface SHAPAttributionChartProps {
  factors?: Array<{
    feature: string;
    impact_value: number;
    direction: string;
    pct_contribution?: number;
  }>;
}

export const SHAPAttributionChart: React.FC<SHAPAttributionChartProps> = ({ factors }) => {
  const items = factors || [
    { feature: 'Active Exploitation (CISA KEV)', impact_value: 7.8, direction: 'INCREASING_RISK', pct_contribution: 32.0 },
    { feature: 'Asset Criticality (Crown Jewels)', impact_value: 6.5, direction: 'INCREASING_RISK', pct_contribution: 27.0 },
    { feature: 'Internet Exposure Surface', impact_value: 4.3, direction: 'INCREASING_RISK', pct_contribution: 18.0 },
    { feature: 'Control Weakness / Missing MFA', impact_value: 3.6, direction: 'INCREASING_RISK', pct_contribution: 15.0 },
    { feature: 'Historical Threat Incidents', impact_value: 1.9, direction: 'INCREASING_RISK', pct_contribution: 8.0 }
  ];

  return (
    <div className="enterprise-card p-5 border-[#1C2042] space-y-4">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-[#1C2042] pb-3">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="uppercase tracking-wide font-mono">WHY IS FUTURE RISK INCREASING?</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            XGBoost predicts the future cyber risk trajectory — SHAP (SHapley Additive exPlanations) mathematically explains why.
          </p>
        </div>
        <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-mono">
          SHAP Model Explainability
        </span>
      </div>

      {/* Horizontal Contribution Bars */}
      <div className="space-y-3 pt-1">
        {items.map((item, idx) => {
          const isIncreasing = item.direction === 'INCREASING_RISK' || item.impact_value > 0;
          const pct = item.pct_contribution || Math.min(100, Math.round((Math.abs(item.impact_value) / 10) * 100));

          return (
            <div key={idx} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  {isIncreasing ? (
                    <ArrowUpRight className="w-4 h-4 text-rose-400 flex-shrink-0" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  )}
                  <span className="font-semibold text-slate-200">{item.feature}</span>
                </div>
                <div className="flex items-center space-x-2 font-mono text-xs">
                  <span className={isIncreasing ? 'text-rose-400 font-bold text-sm' : 'text-emerald-400 font-bold text-sm'}>
                    {isIncreasing ? '+' : '-'}{pct}%
                  </span>
                  <span className="text-slate-500 text-[11px]">(Impact: {item.impact_value > 0 ? '+' : ''}{item.impact_value})</span>
                </div>
              </div>

              {/* Progress track */}
              <div className="h-2 w-full bg-[#0C0E1A] rounded-full overflow-hidden border border-[#1C2042]">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${
                    isIncreasing 
                      ? 'bg-gradient-to-r from-amber-500 to-red-500' 
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.min(100, pct * 1.8)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Footer */}
      <div className="p-3 rounded-lg bg-[#0C0E1A] border border-[#1C2042] text-[11px] text-slate-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <Info className="w-4 h-4 text-purple-400 flex-shrink-0" />
          <span><strong>Key Decision Takeaway:</strong> Active weaponized exploits (+32%) and crown jewel asset criticality (+27%) account for 59% of risk escalation.</span>
        </div>
        <span className="text-purple-300 font-mono font-bold flex-shrink-0">TreeSHAP Exact Kernel</span>
      </div>

    </div>
  );
};
