import React, { useState } from 'react';
import { 
  Database, 
  Layers, 
  FileSpreadsheet, 
  Upload, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldAlert, 
  Sparkles,
  Info,
  X,
  Cpu
} from 'lucide-react';
import { useDataset, DatasetType } from '../context/DatasetContext';
import { UniversalCsvImportModal } from './UniversalCsvImportModal';

export const DatasetSelectorBar: React.FC = () => {
  const { 
    activeDataset, 
    setActiveDataset, 
    isSihDataset, 
    isCustomDataset,
    customDataset,
    sihMetrics, 
    originLabel,
    totalAssetsCount,
    totalVulnsCount,
    totalFieldsCount,
    storedDatasets,
    selectCustomDataset
  } = useDataset();

  const [isImportModalOpen, setIsImportModalOpen] = useState(false);

  return (
    <>
      <div className="w-full bg-[#0a0d1b] border-b border-[#1c2242] px-6 py-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          
          {/* Left: Dataset Selector Dropdown & Origin Badge */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
              <Database className="w-4 h-4 text-cyan-400" />
              <span>ACTIVE DATASET:</span>
            </div>

            <select
              value={activeDataset}
              onChange={(e) => {
                const val = e.target.value;
                if (val.startsWith('stored:')) {
                  const filename = val.replace('stored:', '');
                  selectCustomDataset(filename);
                } else {
                  setActiveDataset(val as DatasetType);
                }
              }}
              className="bg-[#121630] border border-cyan-500/40 text-cyan-200 text-xs font-medium rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-cyan-400 font-mono shadow-inner cursor-pointer"
            >
              <option value="sih_ps26105">SIH PS26105 Test Dataset (15 Assets / 28 Fields)</option>
              {customDataset && (
                <option value="custom_uploaded">
                  User Uploaded: {customDataset.filename} ({customDataset.overview?.total_assets || 0} Assets)
                </option>
              )}
              {storedDatasets && storedDatasets.filter(d => !customDataset || d.filename !== customDataset.filename).map(d => (
                <option key={d.filename} value={`stored:${d.filename}`}>
                  Stored: {d.filename} ({d.total_assets} Assets)
                </option>
              ))}
              <option value="abc_bank">ABC Bank Demo Dataset (100 Assets / Synthetic)</option>
            </select>

            {/* Dynamic Origin Label */}
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-md text-xs font-mono font-bold tracking-wide border shadow-sm ${
              isCustomDataset
                ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300 shadow-emerald-950/20'
                : (isSihDataset 
                    ? 'bg-cyan-950/50 border-cyan-500/50 text-cyan-300 shadow-cyan-950/20' 
                    : 'bg-amber-950/40 border-amber-600/50 text-amber-300')
            }`}>
              <span className={`w-2 h-2 rounded-full ${
                isCustomDataset 
                  ? 'bg-emerald-400 animate-pulse' 
                  : (isSihDataset ? 'bg-cyan-400 animate-pulse' : 'bg-amber-400')
              }`} />
              <span className="truncate max-w-[280px]">{originLabel}</span>
              <span className="text-slate-500 font-normal">|</span>
              <span className="text-white font-bold">{totalAssetsCount} ASSETS</span>
              <span className="text-slate-500 font-normal">|</span>
              <span className="text-rose-300 font-bold">{totalVulnsCount} VULNS</span>
              <span className="text-slate-500 font-normal">|</span>
              <span className="text-slate-300">{totalFieldsCount} FIELDS</span>
            </div>
          </div>

          {/* Center / Right: Dynamic Computed Signals & Import Action */}
          <div className="flex flex-wrap items-center gap-3">
            {isCustomDataset && customDataset?.overview ? (
              <div className="hidden 2xl:flex items-center space-x-3 text-xs font-mono">
                <span className="text-slate-400">Modeled Impact: <strong className="text-rose-400 font-bold">{customDataset.overview.total_modeled_financial_impact_label}</strong></span>
                <span className="text-slate-600">|</span>
                <span className="text-slate-400">Avg Controls: <strong className="text-emerald-400 font-bold">{customDataset.overview.average_control_effectiveness_label}</strong></span>
                <span className="text-slate-600">|</span>
                <span className="text-slate-400">MFA Deficits: <strong className="text-amber-400 font-bold">{customDataset.overview.mfa_disabled}</strong></span>
              </div>
            ) : isSihDataset && sihMetrics ? (
              <div className="hidden 2xl:flex items-center space-x-3 text-xs font-mono">
                <span className="text-slate-400">Modeled Impact: <strong className="text-rose-400 font-bold">{sihMetrics.total_modeled_financial_impact_label}</strong></span>
                <span className="text-slate-600">|</span>
                <span className="text-slate-400">Avg Controls: <strong className="text-emerald-400 font-bold">{sihMetrics.average_control_effectiveness_label}</strong></span>
                <span className="text-slate-600">|</span>
                <span className="text-slate-400">MFA Deficits: <strong className="text-amber-400 font-bold">{sihMetrics.critical_iam_issues}</strong></span>
                <span className="text-slate-600">|</span>
                <span className="text-slate-400">Mitigation: <strong className="text-cyan-300 font-bold">{sihMetrics.total_estimated_mitigation_cost_label}</strong></span>
              </div>
            ) : null}

            <button
              onClick={() => setIsImportModalOpen(true)}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-violet-600 hover:from-cyan-500 hover:to-violet-500 text-xs text-white font-medium transition cursor-pointer shadow-md"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Import CSV</span>
            </button>
          </div>

        </div>
      </div>

      {/* Universal CSV Import Modal */}
      <UniversalCsvImportModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
      />
    </>
  );
};
