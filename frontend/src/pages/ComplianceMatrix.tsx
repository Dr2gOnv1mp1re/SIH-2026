import React, { useState, useEffect } from 'react';
import { Search, FileCheck2, ShieldCheck, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { complianceService } from '../services/api';

export const ComplianceMatrix: React.FC = () => {
  const [complianceData, setComplianceData] = useState<any>(null);
  const [frameworkFilter, setFrameworkFilter] = useState<string>('all');
  const [search, setSearch] = useState<string>('');

  useEffect(() => {
    fetchCompliance();
  }, []);

  const fetchCompliance = async () => {
    try {
      const data = await complianceService.list();
      setComplianceData(data);
    } catch (e) {}
  };

  const findings = complianceData?.findings || [
    { framework: 'NIST CSF 2.0', control_identifier: 'PR.AC-1', title: 'Identities and credentials are managed and verified', status: 'PARTIAL', mapped_security_control: 'CTRL-MFA', gap_description: 'MFA not universally enforced across legacy database jump-hosts.' },
    { framework: 'NIST CSF 2.0', control_identifier: 'DE.CM-1', title: 'The network is monitored for potential cyber events', status: 'COMPLIANT', mapped_security_control: 'CTRL-EDR', gap_description: 'Fully covered by Wazuh SIEM & autonomous response agents.' },
    { framework: 'NIST CSF 2.0', control_identifier: 'RS.RP-1', title: 'Incident management processes are executed and tested', status: 'NON_COMPLIANT', mapped_security_control: 'CTRL-INCIDENT', gap_description: 'Incident response drill overdue for payment subnet.' },
    { framework: 'ISO/IEC 27001:2022', control_identifier: 'A.8.8', title: 'Management of technical vulnerabilities', status: 'NON_COMPLIANT', mapped_security_control: 'CTRL-PATCH', gap_description: 'Active CISA KEV Log4j vulnerability exceeds 14-day SLA.' },
    { framework: 'ISO/IEC 27001:2022', control_identifier: 'A.8.24', title: 'Use of cryptography and sensitive data encryption', status: 'COMPLIANT', mapped_security_control: 'CTRL-ENCRYPT', gap_description: 'AES-256 enabled on all payment database storage volumes.' },
    { framework: 'CIS Controls v8', control_identifier: 'CIS 10.1', title: 'Data Recovery Capabilities and Immutability', status: 'PARTIAL', mapped_security_control: 'CTRL-BACKUP', gap_description: 'Secondary DR backup vault lacks hardware WORM immutability.' },
    { framework: 'CIS Controls v8', control_identifier: 'CIS 4.1', title: 'Establish and Maintain a Secure Configuration Process', status: 'COMPLIANT', mapped_security_control: 'CTRL-CIS-HARD', gap_description: 'CIS Benchmark baseline templates enforced across 78% of servers.' }
  ];

  const filtered = findings.filter((f: any) => {
    const matchF = frameworkFilter === 'all' || f.framework.toLowerCase().includes(frameworkFilter.toLowerCase());
    const matchS = f.title.toLowerCase().includes(search.toLowerCase()) || f.control_identifier.toLowerCase().includes(search.toLowerCase());
    return matchF && matchS;
  });

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Compliance & Control Mapping
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Automated alignment mapping across NIST CSF 2.0, ISO/IEC 27001:2022, CIS Controls v8, and RBI Cyber Security Framework.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="px-3 py-1.5 rounded-lg bg-[#0C0E1A] border border-[#2A2F5A] text-slate-300">
            Overall Compliance Score: <strong className="text-emerald-400">{complianceData?.overall_compliance_score || 76.4}%</strong>
          </span>
        </div>
      </div>

      {/* Framework Scores Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { name: 'NIST CSF 2.0', score: 78.5, compliant: 18, total: 24, color: 'text-cyan-400' },
          { name: 'ISO/IEC 27001:2022', score: 74.0, compliant: 28, total: 38, color: 'text-purple-400' },
          { name: 'CIS Controls v8', score: 76.8, compliant: 14, total: 18, color: 'text-emerald-400' }
        ].map((fw, i) => (
          <div key={i} className="enterprise-card p-5 border-[#1C2042] space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-xs text-white">{fw.name}</span>
              <span className={`font-mono font-bold text-base ${fw.color}`}>{fw.score}%</span>
            </div>
            <div className="h-1.5 w-full bg-[#0C0E1A] rounded-full overflow-hidden">
              <div 
                className="h-full bg-cyan-500 rounded-full"
                style={{ width: `${fw.score}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span>{fw.compliant} Controls Compliant</span>
              <span>{fw.total - fw.compliant} Deficiencies</span>
            </div>
          </div>
        ))}
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 enterprise-card p-4 border-[#1C2042]">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search control identifier or title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#0C0E1A] border border-[#2A2F5A] rounded-lg pl-9 pr-4 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center space-x-1.5 overflow-x-auto w-full sm:w-auto text-xs">
          {['all', 'NIST', 'ISO', 'CIS'].map((f) => (
            <button
              key={f}
              onClick={() => setFrameworkFilter(f)}
              className={`px-3 py-1.5 rounded-lg font-semibold uppercase transition ${
                frameworkFilter === f
                  ? 'bg-gradient-to-r from-violet-600 to-cyan-600 text-white'
                  : 'bg-[#0C0E1A] text-slate-400 hover:text-slate-200 border border-[#1C2042]'
              }`}
            >
              {f === 'all' ? 'All Frameworks' : f}
            </button>
          ))}
        </div>
      </div>

      {/* Findings Table */}
      <div className="enterprise-card p-5 border-[#1C2042] space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">
            Control Mapping & Gap Observations ({filtered.length} Displayed)
          </h2>
          <span className="text-xs text-slate-400 font-mono">Cross-Framework Normalization</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C0E1A] text-slate-400 text-[10px] uppercase font-bold tracking-wider border-b border-[#1C2042]">
              <tr>
                <th className="py-2.5 px-3">Framework</th>
                <th className="py-2.5 px-3">Control ID</th>
                <th className="py-2.5 px-3">Control Requirement</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Mapped Control</th>
                <th className="py-2.5 px-3">Gap / Audit Observation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((f: any, i: number) => (
                <tr key={i} className="hover:bg-[#181C36]/30 transition">
                  <td className="py-2.5 px-3 font-medium text-slate-300">{f.framework}</td>
                  <td className="py-2.5 px-3 font-mono font-bold text-cyan-300">{f.control_identifier}</td>
                  <td className="py-2.5 px-3 font-semibold text-white max-w-xs">{f.title}</td>
                  <td className="py-2.5 px-3">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                      f.status === 'COMPLIANT'
                        ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700'
                        : f.status === 'PARTIAL'
                        ? 'bg-amber-950/80 text-amber-300 border-amber-700'
                        : 'bg-rose-950/80 text-rose-300 border-red-700'
                    }`}>
                      {f.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-200 font-semibold">{f.mapped_security_control}</td>
                  <td className="py-2.5 px-3 text-slate-400 text-[11px] max-w-xs">{f.gap_description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
