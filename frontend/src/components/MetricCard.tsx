import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  isPositive?: boolean;
  icon: LucideIcon;
  variant?: 'cyan' | 'rose' | 'emerald' | 'amber' | 'violet' | 'sky';
  badge?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  change,
  isPositive,
  icon: Icon,
  variant = 'cyan',
  badge
}) => {
  const iconColors: Record<string, string> = {
    cyan: 'text-cyan-400 bg-cyan-950/40 border-cyan-800/60',
    rose: 'text-rose-400 bg-rose-950/40 border-rose-800/60',
    emerald: 'text-emerald-400 bg-emerald-950/40 border-emerald-800/60',
    amber: 'text-amber-400 bg-amber-950/40 border-amber-800/60',
    violet: 'text-violet-400 bg-violet-950/40 border-violet-800/60',
    sky: 'text-sky-400 bg-sky-950/40 border-sky-800/60'
  };

  const borderAccents: Record<string, string> = {
    cyan: 'hover:border-cyan-700/60',
    rose: 'hover:border-rose-700/60',
    emerald: 'hover:border-emerald-700/60',
    amber: 'hover:border-amber-700/60',
    violet: 'hover:border-violet-700/60',
    sky: 'hover:border-sky-700/60'
  };

  return (
    <div className={`enterprise-card enterprise-card-hover p-5 relative overflow-hidden ${borderAccents[variant] || borderAccents.cyan}`}>
      <div className="flex items-start justify-between">
        <div className="space-y-1.5 flex-1 pr-2">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">{title}</span>
            {badge && (
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700">
                {badge}
              </span>
            )}
          </div>
          <div className="text-2xl font-bold tracking-tight text-white font-mono">
            {value}
          </div>
        </div>
        <div className={`p-2.5 rounded-lg border flex-shrink-0 ${iconColors[variant] || iconColors.cyan}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {(subtitle || change) && (
        <div className="mt-3 flex items-center justify-between text-xs pt-2.5 border-t border-slate-800/80">
          {subtitle && <span className="text-slate-400 font-medium">{subtitle}</span>}
          {change && (
            <span className={`font-semibold font-mono ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
              {change}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
