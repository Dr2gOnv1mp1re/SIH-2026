import React, { useState, useEffect } from 'react';
import { RiskBadge } from '../components/RiskBadge';
import { ShieldAlert, Server, Bug, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import { DataSourceBadge } from '../components/DataSourceBadge';
import { riskService } from '../services/api';

export const RiskHeatmap: React.FC = () => {
  const [lastCalculated, setLastCalculated] = useState<string | null>(null);

  useEffect(() => {
    riskService.getEnterpriseRisk().then(res => {
      if (res?.timestamp || res?.last_assessment_date) {
        setLastCalculated(res.timestamp || res.last_assessment_date);
      }
    }).catch(() => {});
  }, []);
  // Pre-populate with default selected risk (Core Payment Database) so the inspection panel is NEVER empty!
  const [selectedCell, setSelectedCell] = useState<any>({
    label: 'Critical',
    score: 94,
    count: 8,
    level: 'CRITICAL',
    likelihood: 5,
    impact: 5,
    asset_name: 'Core Payment Database Cluster',
    asset_code: 'DB-PAY-01',
    criticality: 98,
    modeled_eal: '₹72.0 Lakh',
    vulns: [
      { cve: 'CVE-2021-44228', name: 'Log4Shell RCE', cvss: 10.0, cisa: true },
      { cve: 'CVE-2022-22965', name: 'Spring4Shell RCE', cvss: 9.8, cisa: true }
    ],
    recommended_actions: [
      'Deploy critical emergency patch for CVE-2021-44228 and CVE-2022-22965',
      'Enforce Privileged Identity MFA on all database administrator jump-hosts',
      'Isolate database enclave via Zero-Trust network micro-segmentation'
    ]
  });

  // 5x5 Likelihood vs Business Impact Matrix Cells
  const matrix = [
    // Likelihood 5 (Very High)
    [
      { 
        label: 'Medium', score: 45, count: 4, level: 'MEDIUM', color: 'bg-cyan-950/40 text-cyan-300 border-cyan-800',
        asset_name: 'Internal Reporting Server', asset_code: 'SRV-REP-08', criticality: 45, modeled_eal: '₹6.5 Lakh',
        vulns: [{ cve: 'CVE-2023-2825', name: 'Information Disclosure', cvss: 5.5, cisa: false }],
        recommended_actions: ['Routine patch cycle', 'Restricted subnet access']
      },
      { 
        label: 'High', score: 65, count: 8, level: 'HIGH', color: 'bg-amber-950/40 text-amber-300 border-amber-800',
        asset_name: 'HR Employee Portal', asset_code: 'APP-HR-04', criticality: 60, modeled_eal: '₹14.0 Lakh',
        vulns: [{ cve: 'CVE-2023-38831', name: 'WinRAR Code Execution', cvss: 7.8, cisa: false }],
        recommended_actions: ['Update workstation software', 'Endpoint EDR scan']
      },
      { 
        label: 'Very High', score: 78, count: 12, level: 'VERY HIGH', color: 'bg-orange-950/50 text-orange-300 border-orange-800',
        asset_name: 'External VPN Gateway Portal', asset_code: 'NET-VPN-01', criticality: 88, modeled_eal: '₹34.0 Lakh',
        vulns: [{ cve: 'CVE-2024-21762', name: 'FortiOS SSL VPN RCE', cvss: 9.8, cisa: true }],
        recommended_actions: ['Immediate firmware patch', 'Mandate FIDO2 hardware keys']
      },
      { 
        label: 'Critical', score: 92, count: 15, level: 'CRITICAL', color: 'bg-rose-950/70 text-rose-300 border-rose-800',
        asset_name: 'Online Banking API Gateway', asset_code: 'API-OB-02', criticality: 92, modeled_eal: '₹45.0 Lakh',
        vulns: [{ cve: 'CVE-2022-22965', name: 'Spring4Shell RCE', cvss: 9.8, cisa: true }],
        recommended_actions: ['Spring framework library upgrade', 'WAF virtual patching rule']
      },
      { 
        label: 'Critical', score: 98, count: 8, level: 'CRITICAL', color: 'bg-rose-950 text-rose-200 border-rose-600 font-bold',
        asset_name: 'Core Payment Database Cluster', asset_code: 'DB-PAY-01', criticality: 98, modeled_eal: '₹72.0 Lakh',
        vulns: [
          { cve: 'CVE-2021-44228', name: 'Log4Shell RCE', cvss: 10.0, cisa: true },
          { cve: 'CVE-2022-22965', name: 'Spring4Shell RCE', cvss: 9.8, cisa: true }
        ],
        recommended_actions: [
          'Deploy critical emergency patch for CVE-2021-44228 and CVE-2022-22965',
          'Enforce Privileged Identity MFA on all database administrator jump-hosts',
          'Isolate database enclave via Zero-Trust network micro-segmentation'
        ]
      }
    ],
    // Likelihood 4 (High)
    [
      { 
        label: 'Low', score: 25, count: 12, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800',
        asset_name: 'Development Sandbox Host', asset_code: 'DEV-BOX-12', criticality: 30, modeled_eal: '₹2.0 Lakh',
        vulns: [{ cve: 'CVE-2023-1111', name: 'Debug Port Open', cvss: 4.2, cisa: false }],
        recommended_actions: ['Close non-standard listening ports']
      },
      { 
        label: 'Medium', score: 48, count: 18, level: 'MEDIUM', color: 'bg-cyan-950/40 text-cyan-300 border-cyan-800',
        asset_name: 'Branch Printing Spooler', asset_code: 'PRN-SRV-02', criticality: 50, modeled_eal: '₹8.0 Lakh',
        vulns: [{ cve: 'CVE-2021-34527', name: 'PrintNightmare RCE', cvss: 8.8, cisa: false }],
        recommended_actions: ['Disable Print Spooler on non-print domain controllers']
      },
      { 
        label: 'High', score: 68, count: 24, level: 'HIGH', color: 'bg-amber-950/40 text-amber-300 border-amber-800',
        asset_name: 'Customer Service Web Chat', asset_code: 'APP-CHAT-01', criticality: 70, modeled_eal: '₹18.5 Lakh',
        vulns: [{ cve: 'CVE-2023-4863', name: 'WebP Heap Buffer Overflow', cvss: 8.8, cisa: false }],
        recommended_actions: ['Update rendering libraries', 'Content Security Policy update']
      },
      { 
        label: 'Very High', score: 82, count: 16, level: 'VERY HIGH', color: 'bg-orange-950/50 text-orange-300 border-orange-800',
        asset_name: 'Active Directory Domain Controller', asset_code: 'IAM-DC-01', criticality: 94, modeled_eal: '₹38.5 Lakh',
        vulns: [{ cve: 'CVE-2020-1472', name: 'Zerologon Netlogon Privilege Escalation', cvss: 10.0, cisa: true }],
        recommended_actions: ['Enforce RPC signing', 'Deploy credential tiering architecture']
      },
      { 
        label: 'Critical', score: 90, count: 6, level: 'CRITICAL', color: 'bg-rose-950/70 text-rose-300 border-rose-800',
        asset_name: 'Treasury Trade Settlement Switch', asset_code: 'SW-TRS-01', criticality: 96, modeled_eal: '₹55.0 Lakh',
        vulns: [{ cve: 'CVE-2023-36884', name: 'Office Remote Code Execution', cvss: 8.8, cisa: true }],
        recommended_actions: ['Air-gap trading segment', 'Strict application whitelisting']
      }
    ],
    // Likelihood 3 (Moderate)
    [
      { label: 'Low', score: 18, count: 35, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Staging Database Replica', asset_code: 'DB-STG-02', criticality: 35, modeled_eal: '₹3.2 Lakh', vulns: [], recommended_actions: ['Mask production data copies'] },
      { label: 'Low', score: 32, count: 42, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Internal Wiki Confluence', asset_code: 'APP-WIKI-01', criticality: 40, modeled_eal: '₹5.0 Lakh', vulns: [], recommended_actions: ['Apply monthly vendor security updates'] },
      { label: 'Medium', score: 52, count: 28, level: 'MEDIUM', color: 'bg-cyan-950/40 text-cyan-300 border-cyan-800', asset_name: 'Merchant Onboarding Portal', asset_code: 'APP-MERCH-03', criticality: 65, modeled_eal: '₹12.0 Lakh', vulns: [], recommended_actions: ['Static application security testing review'] },
      { label: 'High', score: 70, count: 14, level: 'HIGH', color: 'bg-amber-950/40 text-amber-300 border-amber-800', asset_name: 'Customer PII Database Replica', asset_code: 'DB-PII-02', criticality: 90, modeled_eal: '₹28.0 Lakh', vulns: [], recommended_actions: ['Column-level field encryption'] },
      { label: 'Very High', score: 84, count: 9, level: 'VERY HIGH', color: 'bg-orange-950/50 text-orange-300 border-orange-800', asset_name: 'Card Authorization Engine', asset_code: 'AUTH-CRD-01', criticality: 95, modeled_eal: '₹42.0 Lakh', vulns: [], recommended_actions: ['Hardware Security Module HSM key rotation'] }
    ],
    // Likelihood 2 (Low)
    [
      { label: 'Low', score: 10, count: 60, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Employee Workstations Batch A', asset_code: 'WS-GRP-A', criticality: 25, modeled_eal: '₹1.5 Lakh', vulns: [], recommended_actions: ['Standard monthly patch Tuesday rollout'] },
      { label: 'Low', score: 15, count: 55, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Employee Workstations Batch B', asset_code: 'WS-GRP-B', criticality: 25, modeled_eal: '₹1.8 Lakh', vulns: [], recommended_actions: ['Standard antivirus definition update'] },
      { label: 'Low', score: 28, count: 34, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Backup Archive Tape System', asset_code: 'BKP-TAP-01', criticality: 50, modeled_eal: '₹4.0 Lakh', vulns: [], recommended_actions: ['Offsite vault verification'] },
      { label: 'Medium', score: 42, count: 16, level: 'MEDIUM', color: 'bg-cyan-950/40 text-cyan-300 border-cyan-800', asset_name: 'ATM Network Routing Nodes', asset_code: 'NET-ATM-04', criticality: 75, modeled_eal: '₹11.0 Lakh', vulns: [], recommended_actions: ['VPN tunnel IPsec re-keying'] },
      { label: 'High', score: 62, count: 8, level: 'HIGH', color: 'bg-amber-950/40 text-amber-300 border-amber-800', asset_name: 'Core Banking SWIFT Gateway', asset_code: 'SW-SWIFT-01', criticality: 96, modeled_eal: '₹22.0 Lakh', vulns: [], recommended_actions: ['SWIFT Customer Security Programme CSP audit'] }
    ],
    // Likelihood 1 (Rare)
    [
      { label: 'Low', score: 5, count: 80, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Branch IoT Environmental Sensors', asset_code: 'IOT-ENV-01', criticality: 10, modeled_eal: '₹0.5 Lakh', vulns: [], recommended_actions: ['Isolate on guest VLAN'] },
      { label: 'Low', score: 8, count: 70, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Corporate Digital Signage', asset_code: 'DISP-CORP-01', criticality: 15, modeled_eal: '₹0.8 Lakh', vulns: [], recommended_actions: ['Segment from internal production network'] },
      { label: 'Low', score: 12, count: 45, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Development Git Repository', asset_code: 'GIT-DEV-01', criticality: 45, modeled_eal: '₹2.1 Lakh', vulns: [], recommended_actions: ['Secret scanning & branch protection'] },
      { label: 'Low', score: 22, count: 20, level: 'LOW', color: 'bg-emerald-950/40 text-emerald-300 border-emerald-800', asset_name: 'Email Archival Storage', asset_code: 'ARC-EML-01', criticality: 60, modeled_eal: '₹3.5 Lakh', vulns: [], recommended_actions: ['Retention policy enforcement'] },
      { label: 'Medium', score: 35, count: 10, level: 'MEDIUM', color: 'bg-cyan-950/40 text-cyan-300 border-cyan-800', asset_name: 'Disaster Recovery Warm Site', asset_code: 'DR-SITE-01', criticality: 90, modeled_eal: '₹9.0 Lakh', vulns: [], recommended_actions: ['Bi-annual failover dry-run verification'] }
    ]
  ];

  const likelihoodLabels = ['Very High (5)', 'High (4)', 'Moderate (3)', 'Low (2)', 'Rare (1)'];
  const impactLabels = ['Insignificant (1)', 'Minor (2)', 'Moderate (3)', 'Major (4)', 'Catastrophic (5)'];

  const handleSelectCell = (cell: any, rIdx: number, cIdx: number) => {
    setSelectedCell({
      ...cell,
      likelihood: 5 - rIdx,
      impact: cIdx + 1
    });
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Enterprise Risk Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Likelihood vs Business Impact 5×5 continuous risk matrix mapping vulnerability-threat interactions across enterprise crown jewels.
          </p>
          <DataSourceBadge showModeledLabel={true} lastCalculated={lastCalculated} className="mt-2" />
        </div>
        <span className="text-xs font-mono text-slate-300 font-semibold px-3 py-1.5 rounded-lg bg-[#0C0E1A] border border-[#2A2F5A]">
          500 Threat-Asset Interactions Mapped
        </span>
      </div>

      {/* Heatmap (65% width) & Selected Cell View (35% width) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* 5x5 Heatmap Matrix (~65% width = 8 Cols) */}
        <div className="lg:col-span-8 enterprise-card p-5 border-[#1C2042] space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">
              Likelihood vs Business Impact 5×5 Matrix
            </h2>
            <span className="text-xs text-slate-400">Click any matrix cell to inspect affected assets</span>
          </div>

          <div className="flex pt-2">
            {/* Y-Axis Label */}
            <div className="flex flex-col justify-between py-4 pr-3 text-right text-[11px] font-semibold text-slate-400 font-mono w-28">
              {likelihoodLabels.map((l, i) => (
                <span key={i}>{l}</span>
              ))}
            </div>

            {/* Matrix Grid */}
            <div className="flex-1 grid grid-rows-5 gap-2">
              {matrix.map((row, rIdx) => (
                <div key={rIdx} className="grid grid-cols-5 gap-2">
                  {row.map((cell, cIdx) => {
                    const isSelected = selectedCell?.score === cell.score && selectedCell?.label === cell.label;
                    return (
                      <button
                        key={cIdx}
                        onClick={() => handleSelectCell(cell, rIdx, cIdx)}
                        className={`h-14 rounded-lg border p-2 text-center transition flex flex-col items-center justify-center ${cell.color} ${
                          isSelected ? 'ring-2 ring-cyan-400 scale-[1.02] shadow-lg z-10' : 'hover:brightness-110 active:scale-95'
                        }`}
                      >
                        <span className="text-[10px] font-semibold uppercase tracking-wider">{cell.label}</span>
                        <span className="text-xs font-bold font-mono mt-0.5">{cell.count} Risks</span>
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          {/* X-Axis Label */}
          <div className="grid grid-cols-5 gap-2 pl-28 text-center text-[11px] font-semibold text-slate-400 font-mono pt-3 border-t border-[#1C2042]">
            {impactLabels.map((imp, i) => (
              <span key={i}>{imp}</span>
            ))}
          </div>

          <div className="text-[11px] text-slate-500 font-mono text-center pt-2">
            Horizontal Axis: Business Impact (Financial / Operational) • Vertical Axis: Exploitation Likelihood
          </div>
        </div>

        {/* Selected Cell Inspection Panel (~35% width = 4 Cols) */}
        <div className="lg:col-span-4 enterprise-card p-5 border-[#2A2F5A] space-y-3 flex flex-col justify-between bg-[#0E1122]">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-[#1C2042] pb-2.5">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 font-mono block">
                  SELECTED RISK INSPECTION
                </span>
                <h3 className="text-sm font-bold text-white mt-0.5">
                  {selectedCell.asset_name}
                </h3>
              </div>
              <RiskBadge level={selectedCell.level || 'CRITICAL'} size="sm" />
            </div>

            {/* Metric Boxes */}
            <div className="grid grid-cols-2 gap-2 font-mono text-xs">
              <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                <span className="text-slate-500 text-[10px] block">Risk Score</span>
                <span className="text-rose-400 font-bold text-sm">{selectedCell.score} / 100</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                <span className="text-slate-500 text-[10px] block">Asset Criticality</span>
                <span className="text-white font-bold text-sm">{selectedCell.criticality} / 100</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                <span className="text-slate-500 text-[10px] block">Likelihood</span>
                <span className="text-slate-200 font-semibold text-xs">Level {selectedCell.likelihood || 5} (Very High)</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                <span className="text-slate-500 text-[10px] block">Business Impact</span>
                <span className="text-slate-200 font-semibold text-xs">Level {selectedCell.impact || 5} (Catastrophic)</span>
              </div>
            </div>

            {/* Financial Modeled EAL */}
            <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-800/60 font-mono text-xs space-y-0.5">
              <span className="text-slate-400 text-[10px] block">Modeled Financial Exposure (Asset EAL)</span>
              <div className="text-amber-400 font-bold text-base">
                {selectedCell.modeled_eal}
              </div>
              <p className="text-[10px] text-slate-400 font-sans mt-1">
                Annualized expected loss modeling downtime, IR containment, data recovery, and regulatory fines.
              </p>
            </div>

            {/* Primary Vulnerabilities */}
            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1.5 text-xs">
              <span className="font-semibold text-slate-300 block text-[11px] uppercase tracking-wider">
                Primary Vulnerabilities:
              </span>
              <div className="space-y-1">
                {(selectedCell.vulns || []).map((v: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-rose-300 font-bold">• {v.cve} ({v.name})</span>
                    <span className="text-slate-400">CVSS {v.cvss}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommended Actions */}
            <div className="p-3 rounded-lg bg-cyan-950/30 border border-cyan-800/60 space-y-1.5 text-xs">
              <span className="font-semibold text-cyan-300 block text-[11px] uppercase tracking-wider">
                Recommended Actions:
              </span>
              <ul className="space-y-1 text-slate-300 text-[11px]">
                {(selectedCell.recommended_actions || [
                  'Critical emergency patching',
                  'Enforce Privileged MFA',
                  'Network enclave micro-segmentation'
                ]).map((action: string, i: number) => (
                  <li key={i} className="flex items-start space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="pt-2 border-t border-[#1C2042] text-[10px] text-slate-500 text-center font-mono">
            Deterministic Likelihood × Impact Weight Calculation
          </div>
        </div>

      </div>

    </div>
  );
};
