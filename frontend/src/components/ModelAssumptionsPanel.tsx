import React from 'react';
import { Sliders, X, ShieldAlert, Info, Database, Percent, DollarSign, Globe, Cpu, FileText, CheckCircle2 } from 'lucide-react';

interface ModelAssumptionsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ModelAssumptionsPanel: React.FC<ModelAssumptionsPanelProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-[#0C0E1A] border border-[#1C2042] rounded-xl max-w-3xl w-full p-6 shadow-2xl relative space-y-5 animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#1C2042] pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-cyan-950/80 border border-cyan-800 text-cyan-400">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">
                Model Assumptions & Data Sources
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                FAIR-Aligned Quantitative Cyber Risk Model • Complete Telemetry & Methodological Transparency
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-md hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Data Source Classification Legend (Prompt Requirement 15) */}
        <div className="space-y-2">
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400 block">
            DATA ORIGIN & ASSUMPTION TIERS
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-[10px] font-mono font-bold">
            <div className="px-2 py-1 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800 text-center">
              REAL TELEMETRY
            </div>
            <div className="px-2 py-1 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800 text-center">
              PUBLIC INTELLIGENCE
            </div>
            <div className="px-2 py-1 rounded bg-violet-950/80 text-violet-300 border border-violet-800 text-center">
              USER-PROVIDED DATA
            </div>
            <div className="px-2 py-1 rounded bg-amber-950/80 text-amber-300 border border-amber-800 text-center">
              SIMULATED / SEEDED
            </div>
            <div className="px-2 py-1 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800 text-center col-span-2 sm:col-span-1">
              MODEL ASSUMPTION
            </div>
          </div>
        </div>

        {/* Section 1: Technical Telemetry & Intelligence Sources */}
        <div className="space-y-2">
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400 block">
            TECHNICAL RISK TELEMETRY & THREAT SOURCES
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
            
            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-cyan-400" />
                  Vulnerabilities & CVSS Source
                </span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-800">
                  PUBLIC INTELLIGENCE
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                NVD API v2.0 & CVE JSON 5.0 feed. CVSS v3.1 base scores dictate vulnerability exploitability severity.
              </p>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-cyan-400" />
                  Active Threat Intelligence
                </span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-800">
                  PUBLIC INTELLIGENCE
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                CISA Known Exploited Vulnerabilities (KEV) Catalog & MITRE ATT&CK Matrix v14.1 for active weaponization.
              </p>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-violet-400" />
                  Asset Inventory & Criticality
                </span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-violet-950 text-violet-300 border border-violet-800">
                  USER-PROVIDED DATA
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Enterprise CMDB asset inventory (100 assets). Criticality derived from Business Impact Assessment (BIA).
              </p>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" />
                  Security Controls & Posture
                </span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
                  REAL TELEMETRY
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Wazuh agent endpoint coverage & active SIEM telemetry. Defense-in-depth mitigations mapped to CIS-18.
              </p>
            </div>

          </div>
        </div>

        {/* Section 2: Financial Model Parametric Assumptions */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400 block">
              FINANCIAL LOSS MODEL PARAMETERS (SLE COMPONENTS)
            </span>
            <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
              PROJECT MODEL ASSUMPTION
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="text-slate-400 font-mono text-[10px] uppercase">Core Banking Downtime</div>
              <div className="text-sm font-bold text-white font-mono">₹3,00,000 / hour</div>
              <div className="text-[10px] text-slate-400">Base 8h recovery outage window</div>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="text-slate-400 font-mono text-[10px] uppercase">Forensics / DFIR Rate</div>
              <div className="text-sm font-bold text-white font-mono">₹25,00,0 / hour</div>
              <div className="text-[10px] text-slate-400">Mean 40-hour engagement</div>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="text-slate-400 font-mono text-[10px] uppercase">Data Recovery Base</div>
              <div className="text-sm font-bold text-white font-mono">₹15,00,000</div>
              <div className="text-[10px] text-slate-400">Scaled by data sensitivity score</div>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="text-slate-400 font-mono text-[10px] uppercase">Regulatory / DPDP Fine Base</div>
              <div className="text-sm font-bold text-white font-mono">₹20,00,000 base</div>
              <div className="text-[10px] text-slate-400">DPDP Act 2023 / RBI statutory penalty</div>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="text-slate-400 font-mono text-[10px] uppercase">Business Interruption Base</div>
              <div className="text-sm font-bold text-white font-mono">₹25,00,000</div>
              <div className="text-[10px] text-slate-400">Scaled by revenue dependency</div>
            </div>

            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1">
              <div className="text-slate-400 font-mono text-[10px] uppercase">Monte Carlo Formulation</div>
              <div className="text-sm font-bold text-cyan-400 font-mono">Compound Poisson-Lognormal</div>
              <div className="text-[10px] text-slate-400">λ=LEF, μ=ln(SLE)-σ²/2, σ=0.50</div>
            </div>
          </div>
        </div>

        {/* Section 3: Seeded Baseline & Uncertainty Disclosure */}
        <div className="p-3 rounded-lg bg-[#12152A] border border-amber-900/40 text-xs space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-amber-300 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-amber-400" />
              Simulated Baseline & Modeling Bounds Disclosure
            </span>
            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-amber-950 text-amber-300 border border-amber-800">
              SIMULATED / SEEDED DATA
            </span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            The demonstration dataset (ABC Bank: 100 assets, 500 vulnerabilities, ₹4.60 Crore baseline aggregated EAL) represents calibrated 
            synthetic enterprise data for demonstration and validation purposes. 
            All financial risk outputs are <strong>MODELED ESTIMATES</strong> with an 85% statistical confidence interval (0.76× to 1.35× bounds) 
            and should not be interpreted as guaranteed actual balance-sheet losses.
          </p>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t border-[#1C2042]">
          <span className="text-[10px] font-mono text-slate-400">
            Governance Standard: FAIR-Aligned Quantitative Cyber Risk Framework
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-cyan-700 hover:bg-cyan-600 text-white font-semibold text-xs transition"
          >
            Close Assumptions Panel
          </button>
        </div>

      </div>
    </div>
  );
};
