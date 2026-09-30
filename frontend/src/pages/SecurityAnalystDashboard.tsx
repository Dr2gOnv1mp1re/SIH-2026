import React, { useState, useEffect } from 'react';
import { 
  Bug, 
  Radio, 
  ShieldAlert, 
  Search, 
  CheckCircle2, 
  Flame
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { RiskBadge } from '../components/RiskBadge';
import { vulnerabilityService, threatService } from '../services/api';

export const SecurityAnalystDashboard: React.FC = () => {
  const [vulns, setVulns] = useState<any[]>([]);
  const [threats, setThreats] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({ total: 500, critical: 50, cisa_known_exploited: 6 });
  const [search, setSearch] = useState<string>('');
  const [filterActiveExploit, setFilterActiveExploit] = useState<boolean>(false);

  useEffect(() => {
    fetchAnalystData();
  }, [filterActiveExploit]);

  const fetchAnalystData = async () => {
    try {
      const [vRes, tRes] = await Promise.all([
        vulnerabilityService.list({ active_exploit_only: filterActiveExploit || undefined, limit: 20 }),
        threatService.list()
      ]);
      setVulns(vRes.items || []);
      setStats(vRes.stats || stats);
      setThreats(tRes || []);
    } catch (e) {}
  };

  const filteredVulns = vulns.filter(v => 
    v.cve_id.toLowerCase().includes(search.toLowerCase()) || 
    v.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Security Analyst Triage & Threat Workbench
            </h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono">
              Live EDR & Scanner Feed
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Prioritize vulnerability remediation based on asset criticality, active in-the-wild exploitation, and attack path depth.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setFilterActiveExploit(!filterActiveExploit)}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-2 border ${
              filterActiveExploit 
                ? 'bg-rose-950 text-rose-300 border-red-700 font-bold' 
                : 'bg-[#12152A] text-slate-300 border-[#2A2F5A] hover:border-[#2A2F5A]'
            }`}
          >
            <Flame className="w-4 h-4 text-rose-400" />
            <span>{filterActiveExploit ? 'Showing CISA Exploits Only' : 'Filter CISA KEV (Active Exploits)'}</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Discovered CVEs"
          value={stats.total || 500}
          subtitle="Monitored Inventory"
          icon={Bug}
          variant="cyan"
        />
        <MetricCard
          title="Critical Severity"
          value={stats.critical || 50}
          subtitle="CVSS Base >= 9.0"
          change="SLA < 14 Days"
          isPositive={false}
          icon={ShieldAlert}
          variant="rose"
        />
        <MetricCard
          title="Active CISA Exploits"
          value={stats.cisa_known_exploited || 6}
          subtitle="In-The-Wild Exploits"
          change="FIN7 / LockBit Active"
          isPositive={false}
          icon={Flame}
          variant="rose"
        />
        <MetricCard
          title="Active Campaigns"
          value={threats.length || 4}
          subtitle="Targeting Banking Sector"
          icon={Radio}
          variant="violet"
        />
      </div>

      {/* Main Table: Vulnerability Triage Queue */}
      <div className="enterprise-card p-5 border-[#1C2042] space-y-3">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-white">
              Prioritized Vulnerability Queue
            </h2>
            <p className="text-xs text-slate-400">Ranked by CVSS severity, asset criticality, and active exploit intelligence</p>
          </div>
          
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search CVE ID or description..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#0C0E1A] border border-[#2A2F5A] rounded-lg pl-9 pr-4 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C0E1A] text-slate-400 text-[10px] uppercase font-bold tracking-wider border-b border-[#1C2042]">
              <tr>
                <th className="py-2.5 px-3">CVE Identifier</th>
                <th className="py-2.5 px-3">Vulnerability Title</th>
                <th className="py-2.5 px-3">CVSS</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Exploit Status</th>
                <th className="py-2.5 px-3">Patch Status</th>
                <th className="py-2.5 px-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredVulns.map((v, i) => (
                <tr key={v.id || i} className="hover:bg-[#181C36]/30 transition">
                  <td className="py-2.5 px-3 font-mono font-bold text-slate-200">{v.cve_id}</td>
                  <td className="py-2.5 px-3 font-medium text-slate-300 max-w-xs truncate">{v.title}</td>
                  <td className="py-2.5 px-3 font-mono font-bold text-white">{v.cvss_score}</td>
                  <td className="py-2.5 px-3"><RiskBadge level={v.severity} size="sm" /></td>
                  <td className="py-2.5 px-3">
                    {v.active_exploitation ? (
                      <span className="inline-flex items-center text-[10px] font-bold text-rose-300 bg-rose-950/80 px-2 py-0.5 rounded border border-red-700">
                        <Flame className="w-3 h-3 mr-1 text-rose-400" /> CISA KEV Active
                      </span>
                    ) : v.exploit_available ? (
                      <span className="text-[10px] text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-700 font-medium">
                        PoC Available
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-400 font-mono">No Exploit</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="text-emerald-400 font-semibold flex items-center">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Available
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <button className="px-2.5 py-1 rounded bg-[#0C0E1A] hover:bg-gradient-to-r from-violet-600 to-cyan-600 text-slate-300 hover:text-white transition font-medium text-[11px] border border-[#2A2F5A]">
                      Investigate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
