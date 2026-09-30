import React from 'react';

interface RiskBadgeProps {
  level: string;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'md' }) => {
  const lvl = level?.toUpperCase() || 'LOW';
  
  const styles: Record<string, string> = {
    CRITICAL: 'bg-rose-950/70 text-rose-300 border-rose-800/80',
    'VERY HIGH': 'bg-orange-950/70 text-orange-300 border-orange-800/80',
    HIGH: 'bg-amber-950/70 text-amber-300 border-amber-800/80',
    MEDIUM: 'bg-violet-950/70 text-violet-300 border-violet-800/80',
    LOW: 'bg-emerald-950/70 text-emerald-300 border-emerald-800/80',
    VERIFIED: 'bg-emerald-950/70 text-emerald-300 border-emerald-700/80 font-bold',
    TAMPERING_DETECTED: 'bg-rose-950 text-rose-200 border-rose-600 font-extrabold shadow-sm'
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[10px] font-semibold tracking-wider',
    md: 'px-2.5 py-1 text-xs font-bold tracking-wider',
    lg: 'px-3.5 py-1.5 text-xs font-extrabold tracking-widest'
  };

  const styleClass = styles[lvl] || styles.LOW;

  return (
    <span className={`inline-flex items-center rounded-md border uppercase font-mono ${sizeClasses[size]} ${styleClass}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-80" />
      {lvl}
    </span>
  );
};
