import React, { useState, useEffect } from 'react';
import { 
  GitBranch, 
  CheckCircle2, 
  ShieldAlert, 
  AlertTriangle, 
  ArrowRight, 
  DollarSign, 
  Layers, 
  ShieldCheck, 
  Activity, 
  TrendingDown, 
  Info, 
  Lock,
  ExternalLink,
  Cpu
} from 'lucide-react';
import { AttackGraphViewer } from '../components/AttackGraphViewer';
import { attackPathService, sihDatasetService } from '../services/api';
import { useDataset } from '../context/DatasetContext';
import { DataSourceBadge } from '../components/DataSourceBadge';

export const AttackPaths: React.FC = () => {
  const { isSihDataset, originLabel } = useDataset();
  const [graphData, setGraphData] = useState<any>(null);
  const [sihPaths, setSihPaths] = useState<any[]>([]);
  const [selectedPathIndex, setSelectedPathIndex] = useState<number>(0);

  useEffect(() => {
    if (isSihDataset) {
      fetchSihPaths();
    } else {
      fetchGraph();
    }
  }, [isSihDataset]);

  const fetchGraph = async () => {
    try {
      const data = await attackPathService.getGraph();
      setGraphData(data);
    } catch (e) {
      console.error('Failed to load attack path graph:', e);
    }
  };

  const fetchSihPaths = async () => {
    try {
      const paths = await sihDatasetService.getAttackPaths();
      setSihPaths(paths);
      setSelectedPathIndex(0);
    } catch (e) {
      console.error('Failed to load SIH attack paths:', e);
    }
  };

  const formatInr = (val: number) => {
    if (!val) return '₹0';
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)} Lakh`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  // SIH path rendering
  const activeSihPath = sihPaths[selectedPathIndex] || sihPaths[0];

  // ABC Demo path rendering
  const demoPaths = graphData?.critical_attack_paths || [];
  const currentDemoPath = demoPaths[selectedPathIndex] || demoPaths[0];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Attack Paths & Financial Risk Impact Engine
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-950/80 text-rose-300 border border-rose-800">
              MODELED ATTACK PATH
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950/80 text-purple-300 border border-purple-800">
              {originLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl">
            {isSihDataset
              ? "Empirical lateral movement chains constructed from the 15 SIH assets combining Internet Exposure, Exploitable CVEs, Privileged Accounts without MFA, SIEM Alerts, and Unisolated EDR telemetry. Mapped to MITRE ATT&CK framework."
              : "Graph-theoretic lateral movement simulation directly connected to the centralized FAIR financial risk engine. Traces multi-hop adversary paths from perimeter ingress to core crown jewel databases."}
          </p>
          <DataSourceBadge showModeledLabel={true} className="mt-2" />
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono text-cyan-300 font-bold px-3 py-1.5 rounded-lg bg-[#0C0E1A] border border-[#2A2F5A] flex items-center space-x-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            <span>{isSihDataset ? "15 ASSETS ANALYZED" : "DIRECT RISK ENGINE SYNC"}</span>
          </span>
        </div>
      </div>

      {/* SIH EMPIRICAL ATTACK CHAINS VIEW */}
      {isSihDataset ? (
        <div className="space-y-6">
          
          {/* Path Selector Tabs */}
          <div className="flex items-center space-x-2 border-b border-[#1C2042] pb-2 overflow-x-auto">
            {sihPaths.map((p, idx) => (
              <button
                key={p.path_id}
                onClick={() => setSelectedPathIndex(idx)}
                className={`px-3 py-2 rounded-lg text-xs font-mono font-bold transition flex items-center space-x-2 ${
                  selectedPathIndex === idx
                    ? 'bg-rose-950/90 text-rose-200 border border-rose-600 shadow-sm'
                    : 'bg-[#12152A] text-slate-400 border border-[#1C2042] hover:text-white'
                }`}
              >
                <GitBranch className="w-3.5 h-3.5" />
                <span>{p.path_id}: {p.name}</span>
              </button>
            ))}
          </div>

          {activeSihPath && (
            <div className="space-y-6">
              
              {/* Path Overview Card */}
              <div className="enterprise-card p-6 border-[#1C2042] space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1C2042] pb-3">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                        {activeSihPath.risk_rating} RISK CHAIN
                      </span>
                      <h2 className="text-base font-bold text-white">{activeSihPath.name}</h2>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      Adversary Entry: <strong className="text-rose-300">{activeSihPath.entry_point}</strong> → Target Crown Jewel: <strong className="text-amber-300">{activeSihPath.target_crown_jewel}</strong>
                    </p>
                  </div>
                  <div className="flex items-center space-x-4 bg-[#0C0E1A] px-4 py-2 rounded-lg border border-[#2A2F5A] font-mono">
                    <div>
                      <div className="text-[10px] text-slate-400">Combined Probability</div>
                      <div className="text-cyan-300 font-bold text-sm">{(activeSihPath.combined_probability * 100).toFixed(0)}%</div>
                    </div>
                    <div className="border-l border-[#1C2042] pl-4">
                      <div className="text-[10px] text-slate-400">Modeled Potential Impact</div>
                      <div className="text-rose-400 font-bold text-sm">{activeSihPath.potential_financial_impact_label}</div>
                    </div>
                  </div>
                </div>

                {/* MITRE ATT&CK Hop Sequence */}
                <div className="space-y-3 pt-2">
                  <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400 block">
                    Sequential Attack Traversal & MITRE ATT&CK Mapping:
                  </span>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                    {activeSihPath.hops.map((hop: any) => (
                      <div key={hop.step} className="p-4 rounded-xl bg-[#0C0E1A] border border-[#1C2042] space-y-2 relative">
                        <div className="flex items-center justify-between">
                          <span className="w-6 h-6 rounded-full bg-rose-950 text-rose-300 border border-rose-800 flex items-center justify-center font-bold text-xs">
                            {hop.step}
                          </span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-bold">
                            MITRE
                          </span>
                        </div>
                        <div className="font-mono font-bold text-xs text-white">{hop.asset}</div>
                        <p className="text-xs text-slate-300 leading-snug">{hop.action}</p>
                        <div className="text-[10px] font-mono text-cyan-300 pt-1 border-t border-[#1C2042]">
                          {hop.mitre_technique}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Methodology Notice */}
                <div className="p-3.5 rounded-lg bg-[#0E1122] border border-[#1C2042] text-xs text-slate-400 flex items-start space-x-2.5">
                  <Info className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-slate-200">Attack Path Methodology Notice:</strong> The CSV provides discrete asset security signals rather than a direct topology graph. The risk engine infers reachable attack paths by combining public internet exposure, weaponized CVE exploits, unsegmented privileged credentials lacking MFA, and unisolated EDR alerts against critical business crown jewels.
                  </div>
                </div>
              </div>

            </div>
          )}

        </div>
      ) : (
        /* ABC BANK DEMO GRAPH VIEW */
        <>
          <AttackGraphViewer />

          {/* Attack Path Selector Tabs */}
          {demoPaths.length > 0 && (
            <div className="flex items-center space-x-2 border-b border-[#1C2042] pb-2 overflow-x-auto">
              {demoPaths.map((p: any, idx: number) => (
                <button
                  key={p.id || idx}
                  onClick={() => setSelectedPathIndex(idx)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition flex items-center space-x-2 ${
                    selectedPathIndex === idx
                      ? 'bg-rose-950/80 text-rose-200 border border-rose-700 shadow-sm'
                      : 'bg-[#12152A] text-slate-400 border border-[#1C2042] hover:text-white'
                  }`}
                >
                  <GitBranch className="w-3.5 h-3.5" />
                  <span>{p.name?.split('→')[0]} → Crown Jewel ({p.path_risk_score}/100)</span>
                </button>
              ))}
            </div>
          )}

          {currentDemoPath && (
            <div className="space-y-6">
              <div className="enterprise-card p-5 border-[#1C2042] space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1C2042] pb-3">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                        {currentDemoPath.path_tag || 'CRITICAL PATH'}
                      </span>
                      <h2 className="text-base font-bold text-white">{currentDemoPath.name}</h2>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      Path Length: <strong className="text-slate-200">{currentDemoPath.path_length} Hops</strong> from <span className="text-rose-300">{currentDemoPath.start_point}</span> to <span className="text-amber-300 font-bold">{currentDemoPath.target_asset}</span>
                    </p>
                  </div>
                  <div className="flex items-center space-x-4 bg-[#0C0E1A] px-4 py-2 rounded-lg border border-[#2A2F5A] font-mono">
                    <div>
                      <div className="text-[10px] text-slate-400">Path Risk Score</div>
                      <div className="text-rose-400 font-bold text-sm">{currentDemoPath.path_risk_score} / 100</div>
                    </div>
                    <div className="border-l border-[#1C2042] pl-4">
                      <div className="text-[10px] text-slate-400">Modeled EAL</div>
                      <div className="text-amber-400 font-bold text-sm">{formatInr(currentDemoPath.modeled_financial_impact)} / yr</div>
                    </div>
                  </div>
                </div>

                {currentDemoPath.chain_sequence && (
                  <div className="space-y-2">
                    <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400 block">
                      Traceable Lateral Movement Chain:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-xs font-mono">
                      {currentDemoPath.chain_sequence.map((step: string, i: number) => (
                        <div key={i} className="p-2.5 rounded-lg bg-[#0C0E1A] border border-[#1C2042] text-slate-300 flex items-center space-x-2">
                          <span className="w-5 h-5 rounded bg-rose-950 text-rose-300 border border-rose-800 flex items-center justify-center font-bold text-[10px] flex-shrink-0">
                            {i+1}
                          </span>
                          <span className="text-[11px] truncate leading-tight">{step.replace(/^\d+\.\s*/, '')}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

    </div>
  );
};
