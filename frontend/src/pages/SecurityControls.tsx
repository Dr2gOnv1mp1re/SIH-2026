import React, { useState, useEffect } from 'react';
import { Search, Edit3, Save, Sliders, ShieldCheck, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import { controlService } from '../services/api';
import { SecurityControl } from '../types';

const SEED_CONTROLS: SecurityControl[] = [
  {
    id: 'ctrl-01',
    code: 'CTRL-PATCH',
    name: 'Automated Critical Vulnerability Patching',
    category: 'Vulnerability Management',
    coverage_percentage: 70,
    effectiveness_percentage: 90,
    implementation_cost: 1800000,
    modeled_risk_reduction: 7500000,
    status: 'partial'
  },
  {
    id: 'ctrl-02',
    code: 'CTRL-MFA',
    name: 'Privileged Identity Multi-Factor Authentication',
    category: 'Identity & Access',
    coverage_percentage: 72,
    effectiveness_percentage: 95,
    implementation_cost: 1200000,
    modeled_risk_reduction: 4500000,
    status: 'partial'
  },
  {
    id: 'ctrl-03',
    code: 'CTRL-EDR',
    name: 'Next-Gen EDR / XDR Autonomous Response',
    category: 'Endpoint Security',
    coverage_percentage: 85,
    effectiveness_percentage: 92,
    implementation_cost: 2500000,
    modeled_risk_reduction: 8000000,
    status: 'partial'
  },
  {
    id: 'ctrl-04',
    code: 'CTRL-SEG',
    name: 'Network Zero-Trust Micro-segmentation',
    category: 'Network Security',
    coverage_percentage: 60,
    effectiveness_percentage: 88,
    implementation_cost: 2000000,
    modeled_risk_reduction: 6000000,
    status: 'partial'
  },
  {
    id: 'ctrl-05',
    code: 'CTRL-BACKUP',
    name: 'Immutable WORM Air-Gapped Backup Vault',
    category: 'Data Protection & Resilience',
    coverage_percentage: 65,
    effectiveness_percentage: 94,
    implementation_cost: 1000000,
    modeled_risk_reduction: 3500000,
    status: 'partial'
  },
  {
    id: 'ctrl-06',
    code: 'CTRL-ENCRYPT',
    name: 'Database Field-Level AES-256 Encryption',
    category: 'Data Protection & Resilience',
    coverage_percentage: 90,
    effectiveness_percentage: 95,
    implementation_cost: 1500000,
    modeled_risk_reduction: 4000000,
    status: 'implemented'
  },
  {
    id: 'ctrl-07',
    code: 'CTRL-WAF',
    name: 'Web Application Firewall (WAF) Virtual Patching',
    category: 'Application Security',
    coverage_percentage: 88,
    effectiveness_percentage: 85,
    implementation_cost: 1400000,
    modeled_risk_reduction: 3000000,
    status: 'implemented'
  },
  {
    id: 'ctrl-08',
    code: 'CTRL-TRAIN',
    name: 'Security Awareness & Anti-Phishing Simulation',
    category: 'Human Governance',
    coverage_percentage: 75,
    effectiveness_percentage: 70,
    implementation_cost: 600000,
    modeled_risk_reduction: 1500000,
    status: 'partial'
  },
  {
    id: 'ctrl-09',
    code: 'CTRL-PAM',
    name: 'Privileged Access Management (PAM) Session Recording',
    category: 'Identity & Access',
    coverage_percentage: 65,
    effectiveness_percentage: 85,
    implementation_cost: 1100000,
    modeled_risk_reduction: 2500000,
    status: 'partial'
  },
  {
    id: 'ctrl-10',
    code: 'CTRL-DRIFT',
    name: 'Automated Security Configuration Drift Auditing',
    category: 'Governance & Compliance',
    coverage_percentage: 55,
    effectiveness_percentage: 80,
    implementation_cost: 800000,
    modeled_risk_reduction: 2000000,
    status: 'weak'
  },
  {
    id: 'ctrl-11',
    code: 'CTRL-SIEM',
    name: 'Centralized SIEM Log Ingestion & Threat Hunting',
    category: 'Security Operations',
    coverage_percentage: 92,
    effectiveness_percentage: 90,
    implementation_cost: 2200000,
    modeled_risk_reduction: 5000000,
    status: 'implemented'
  },
  {
    id: 'ctrl-12',
    code: 'CTRL-CSPM',
    name: 'Cloud Security Posture Management (CSPM)',
    category: 'Cloud Infrastructure',
    coverage_percentage: 80,
    effectiveness_percentage: 85,
    implementation_cost: 1200000,
    modeled_risk_reduction: 2800000,
    status: 'implemented'
  },
  {
    id: 'ctrl-13',
    code: 'CTRL-VULN-SLA',
    name: 'Vulnerability Management SLA Enforcement',
    category: 'Vulnerability Management',
    coverage_percentage: 68,
    effectiveness_percentage: 82,
    implementation_cost: 900000,
    modeled_risk_reduction: 3200000,
    status: 'partial'
  },
  {
    id: 'ctrl-14',
    code: 'CTRL-API-SEC',
    name: 'API Gateway Rate Limiting & Schema Validation',
    category: 'Application Security',
    coverage_percentage: 85,
    effectiveness_percentage: 88,
    implementation_cost: 1000000,
    modeled_risk_reduction: 2400000,
    status: 'implemented'
  },
  {
    id: 'ctrl-15',
    code: 'CTRL-SBOM',
    name: 'Software Supply Chain SBOM Attestation',
    category: 'Application Security',
    coverage_percentage: 40,
    effectiveness_percentage: 75,
    implementation_cost: 700000,
    modeled_risk_reduction: 1800000,
    status: 'weak'
  },
  {
    id: 'ctrl-16',
    code: 'CTRL-DR-SYNC',
    name: 'Disaster Recovery Continuous Replication',
    category: 'Data Protection & Resilience',
    coverage_percentage: 82,
    effectiveness_percentage: 90,
    implementation_cost: 1600000,
    modeled_risk_reduction: 3000000,
    status: 'implemented'
  },
  {
    id: 'ctrl-17',
    code: 'CTRL-CTI',
    name: 'Threat Intelligence Ingestion Automation',
    category: 'Security Operations',
    coverage_percentage: 88,
    effectiveness_percentage: 85,
    implementation_cost: 850000,
    modeled_risk_reduction: 2200000,
    status: 'implemented'
  },
  {
    id: 'ctrl-18',
    code: 'CTRL-AD-TIER',
    name: 'Active Directory Tiered Administrative Enclave',
    category: 'Identity & Access',
    coverage_percentage: 50,
    effectiveness_percentage: 90,
    implementation_cost: 1300000,
    modeled_risk_reduction: 3500000,
    status: 'weak'
  },
  {
    id: 'ctrl-19',
    code: 'CTRL-CIS-HARD',
    name: 'Hardened Baseline CIS OS Configuration Templates',
    category: 'Governance & Compliance',
    coverage_percentage: 78,
    effectiveness_percentage: 80,
    implementation_cost: 750000,
    modeled_risk_reduction: 2000000,
    status: 'partial'
  },
  {
    id: 'ctrl-20',
    code: 'CTRL-IR-RETAIN',
    name: 'Incident Response Retainer & Playbook Automation',
    category: 'Security Operations',
    coverage_percentage: 45,
    effectiveness_percentage: 85,
    implementation_cost: 1500000,
    modeled_risk_reduction: 2500000,
    status: 'weak'
  }
];

export const SecurityControls: React.FC = () => {
  const [controls, setControls] = useState<SecurityControl[]>(SEED_CONTROLS);
  const [search, setSearch] = useState<string>('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editCoverage, setEditCoverage] = useState<number>(75);

  useEffect(() => {
    fetchControls();
  }, []);

  const fetchControls = async () => {
    try {
      const data = await controlService.list();
      if (Array.isArray(data) && data.length > 0) {
        setControls(data);
      } else {
        setControls(SEED_CONTROLS);
      }
    } catch (e) {
      setControls(SEED_CONTROLS);
    }
  };

  const handleSaveCoverage = async (ctrl: SecurityControl) => {
    try {
      await controlService.update(ctrl.id, { coverage_percentage: editCoverage });
      setControls(prev => prev.map(c => c.id === ctrl.id ? { ...c, coverage_percentage: editCoverage } : c));
      setEditingId(null);
    } catch (e) {
      setControls(prev => prev.map(c => c.id === ctrl.id ? { ...c, coverage_percentage: editCoverage } : c));
      setEditingId(null);
    }
  };

  const strongCount = controls.filter(c => (c.coverage_percentage || 0) >= 80).length;
  const partialCount = controls.filter(c => (c.coverage_percentage || 0) >= 60 && (c.coverage_percentage || 0) < 80).length;
  const weakCount = controls.filter(c => (c.coverage_percentage || 0) < 60).length;

  const filtered = controls.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.code.toLowerCase().includes(search.toLowerCase()) ||
    c.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Security Control Catalog & Defense-in-Depth Engine
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            20 Defense-in-depth security controls mapped to technical effectiveness %, implementation cost, and Google OR-Tools optimization parameters.
          </p>
        </div>
        <div className="text-xs font-mono text-cyan-400 font-semibold px-3 py-1.5 rounded-lg bg-[#0C0E1A] border border-[#2A2F5A]">
          Defense-in-Depth Layer Active
        </div>
      </div>

      {/* Summary Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="enterprise-card p-4 border-[#1C2042]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Total Controls</span>
          <div className="text-xl font-bold text-white font-mono mt-0.5">20 Controls</div>
          <span className="text-[10px] text-slate-400 block">Catalog Scope</span>
        </div>

        <div className="enterprise-card p-4 border-[#1C2042]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Strong Controls</span>
          <div className="text-xl font-bold text-emerald-400 font-mono mt-0.5">{strongCount} Strong (80%+)</div>
          <span className="text-[10px] text-emerald-300 font-semibold block">High Coverage</span>
        </div>

        <div className="enterprise-card p-4 border-[#1C2042]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Partial Controls</span>
          <div className="text-xl font-bold text-amber-400 font-mono mt-0.5">{partialCount} Partial (60-79%)</div>
          <span className="text-[10px] text-amber-300 font-semibold block">Upgrade Target</span>
        </div>

        <div className="enterprise-card p-4 border-[#1C2042]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Weak Deficiencies</span>
          <div className="text-xl font-bold text-rose-400 font-mono mt-0.5">{weakCount} Weak (&lt;60%)</div>
          <span className="text-[10px] text-rose-300 font-semibold block">Critical Gap</span>
        </div>
      </div>

      {/* Search Bar */}
      <div className="enterprise-card p-4 border-[#1C2042]">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search control code, name, category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#0C0E1A] border border-[#2A2F5A] rounded-lg pl-9 pr-4 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((c) => {
          const isStrong = (c.coverage_percentage || 0) >= 80;
          const isPartial = (c.coverage_percentage || 0) >= 60 && (c.coverage_percentage || 0) < 80;

          return (
            <div key={c.id || c.code} className="enterprise-card p-5 border-[#1C2042] space-y-3 flex flex-col justify-between hover:border-[#2A2F5A] transition">
              <div>
                <div className="flex items-start justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                    {c.code}
                  </span>
                  <span className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded border ${
                    isStrong 
                      ? 'bg-emerald-950 text-emerald-300 border-emerald-800' 
                      : isPartial
                      ? 'bg-amber-950 text-amber-300 border-amber-800'
                      : 'bg-rose-950 text-rose-300 border-rose-800'
                  }`}>
                    {isStrong ? 'Strong' : isPartial ? 'Partial' : 'Weak'}
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-white mt-2 leading-snug">{c.name}</h3>
                <span className="text-[11px] text-slate-400 block mt-0.5">{c.category}</span>
              </div>

              <div className="space-y-2 text-xs font-mono pt-2 border-t border-[#1C2042]">
                {/* Coverage slider/editor */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-slate-300">
                    <span>Coverage:</span>
                    {editingId === (c.id || c.code) ? (
                      <div className="flex items-center space-x-2">
                        <input 
                          type="number" 
                          value={editCoverage}
                          onChange={(e) => setEditCoverage(parseFloat(e.target.value))}
                          className="w-14 bg-[#0A0B16] border border-cyan-500 px-1 py-0.5 rounded text-white font-bold text-xs"
                        />
                        <button 
                          onClick={() => handleSaveCoverage(c)}
                          className="p-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white"
                        >
                          <Save className="w-3 h-3" />
                        </button>
                      </div>
                    ) : (
                      <span 
                        onClick={() => { setEditingId(c.id || c.code); setEditCoverage(c.coverage_percentage || 75); }}
                        className="text-cyan-300 font-bold cursor-pointer hover:underline flex items-center"
                        title="Click to adjust coverage"
                      >
                        {c.coverage_percentage || 75}% <Edit3 className="w-2.5 h-2.5 ml-1 text-slate-500" />
                      </span>
                    )}
                  </div>
                  <div className="h-1.5 w-full bg-[#0C0E1A] rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${
                        isStrong ? 'bg-emerald-500' : isPartial ? 'bg-amber-500' : 'bg-rose-500'
                      }`}
                      style={{ width: `${c.coverage_percentage || 75}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-slate-400">
                  <span>Effectiveness:</span>
                  <span className="text-slate-200 font-medium">{c.effectiveness_percentage || 85}%</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Implementation Cost:</span>
                  <span className="text-slate-200 font-medium">₹{((c.implementation_cost || 0) / 100000).toFixed(1)} Lakh</span>
                </div>
                <div className="flex items-center justify-between text-slate-400 pt-1 border-t border-[#1C2042]/60">
                  <span>Modeled Risk Reduction:</span>
                  <span className="text-emerald-400 font-bold">₹{(((c.modeled_risk_reduction || 0) / 100000)).toFixed(1)} Lakh</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
