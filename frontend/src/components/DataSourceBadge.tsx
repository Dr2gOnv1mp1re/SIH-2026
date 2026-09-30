import React from 'react';
import { Database, Clock, Calculator } from 'lucide-react';
import { useDataset } from '../context/DatasetContext';

interface DataSourceBadgeProps {
  lastCalculated?: string | Date | null;
  showModeledLabel?: boolean;
  className?: string;
}

export const DataSourceBadge: React.FC<DataSourceBadgeProps> = ({
  lastCalculated,
  showModeledLabel = false,
  className = ''
}) => {
  const { isSihDataset, isCustomDataset, activeFilename, originLabel } = useDataset();

  // Format timestamp if provided
  const formattedTime = lastCalculated 
    ? (typeof lastCalculated === 'string' 
        ? (lastCalculated.includes('T') ? new Date(lastCalculated).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : lastCalculated)
        : lastCalculated.toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }))
    : null;

  const datasetDisplayName = isCustomDataset
    ? `Uploaded Dataset — ${activeFilename}`
    : (isSihDataset ? 'SIH PS26105 Test Dataset' : 'ABC Bank Demo Dataset');

  return (
    <div className={`flex flex-wrap items-center gap-2 text-xs font-mono ${className}`}>
      {/* Dynamic Data Source Indicator */}
      <div 
        className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-[#0D1226] border border-[#23294E] text-slate-300 shadow-sm"
        title={originLabel}
      >
        <Database className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
        <span className="text-slate-400 font-normal">Data Source:</span>
        <span className="text-cyan-300 font-bold truncate max-w-[240px]">
          {datasetDisplayName}
        </span>
      </div>

      {/* Modeled / Estimated Financial Indicator */}
      {showModeledLabel && (
        <div className="inline-flex items-center space-x-1 px-2 py-1 rounded-md bg-amber-950/60 border border-amber-800/70 text-amber-300 text-[10px] font-bold tracking-wider uppercase">
          <Calculator className="w-3 h-3 text-amber-400" />
          <span>MODELED / ESTIMATED</span>
        </div>
      )}

      {/* Dynamic Last Calculated Timestamp */}
      {formattedTime && (
        <div className="inline-flex items-center space-x-1.5 px-2 py-1 rounded-md bg-[#0A0D1E] border border-[#1C2242] text-slate-400 text-[11px]">
          <Clock className="w-3 h-3 text-slate-500" />
          <span>Last Calculated:</span>
          <span className="text-slate-200 font-semibold">{formattedTime}</span>
        </div>
      )}
    </div>
  );
};
