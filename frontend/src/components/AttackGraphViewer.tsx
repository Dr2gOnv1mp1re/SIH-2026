import React from 'react';
import { Shield, Server, Database, Globe, Key, ArrowRight, Bug, Network, AlertTriangle } from 'lucide-react';

interface AttackGraphViewerProps {
  onSelectPath?: (pathId: string) => void;
}

export const AttackGraphViewer: React.FC<AttackGraphViewerProps> = () => {
  const nodes = [
    { id: 'internet', label: '1. Public Internet', sub: 'Attacker Ingress', icon: Globe, color: 'border-rose-800/80 bg-rose-950/40 text-rose-300', badge: 'Threat Origin' },
    { id: 'waf', label: '2. Edge WAF / Proxy', sub: 'Header Bypass', icon: Shield, color: 'border-cyan-800/80 bg-cyan-950/40 text-cyan-300', badge: 'Defense Bypass' },
    { id: 'web', label: '3. Internet Web App', sub: 'Portal Ingress', icon: Server, color: 'border-rose-800/80 bg-rose-950/50 text-rose-300', badge: 'CVE-2021-44228' },
    { id: 'log4j', label: '4. Log4j JNDI RCE', sub: 'LDAP Lookup', icon: Bug, color: 'border-rose-600 bg-rose-950/70 text-rose-200 font-bold', badge: 'CVSS 10.0 RCE' },
    { id: 'server', label: '5. App Server Host', sub: 'Root Privilege', icon: Server, color: 'border-amber-800/80 bg-amber-950/40 text-amber-300', badge: 'RHEL 8.8 Host' },
    { id: 'api', label: '6. Payment API', sub: 'Microservice Pivot', icon: Network, color: 'border-amber-800/80 bg-amber-950/50 text-amber-300', badge: 'Spring4Shell' },
    { id: 'iam', label: '7. Active Directory', sub: 'Domain Admin', icon: Key, color: 'border-purple-800/80 bg-purple-950/40 text-purple-300', badge: 'Lateral Movement' },
    { id: 'db', label: '8. Core Payment DB', sub: 'Crown Jewel', icon: Database, color: 'border-rose-500 bg-rose-950 text-rose-100 font-bold', badge: 'Target (Crit 98)' },
  ];

  return (
    <div className="enterprise-card p-5 border-[#1C2042] space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1C2042] pb-3">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <span>Critical Attack Path Visualizer — Modeled Adversary Chain</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono font-bold">
              Risk: 94 / 100 • 7 Hops
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Traces documented multi-hop reachability from Public Ingress through Log4j RCE to Core Payment Database
          </p>
        </div>
        <div className="text-xs font-mono text-amber-400 font-bold bg-[#0C0E1A] px-3 py-1 rounded-lg border border-[#2A2F5A]">
          Target Modeled Exposure: ₹72.0 Lakh EAL
        </div>
      </div>

      {/* Visual Attack Path Nodes Chain */}
      <div className="py-2 overflow-x-auto">
        <div className="flex items-center space-x-1.5 min-w-[980px]">
          {nodes.map((node, i) => {
            const Icon = node.icon;
            const isLast = i === nodes.length - 1;
            return (
              <React.Fragment key={node.id}>
                <div className={`flex-1 rounded-xl p-2.5 border ${node.color} flex flex-col items-center text-center space-y-1 shadow-sm min-w-[105px]`}>
                  <Icon className="w-4 h-4 mb-0.5" />
                  <span className="text-[11px] font-semibold text-white leading-tight">{node.label}</span>
                  <span className="text-[9px] text-slate-400 font-mono leading-tight">{node.sub}</span>
                  <span className="text-[8px] uppercase font-bold tracking-wider px-1 py-0.2 rounded bg-[#0A0B16] border border-[#1C2042]/80 font-mono">
                    {node.badge}
                  </span>
                </div>
                {!isLast && (
                  <div className="flex flex-col items-center px-0.5 flex-shrink-0">
                    <ArrowRight className="w-3.5 h-3.5 text-rose-400" />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Path Mitigation Recommendation */}
      <div className="p-3 rounded-lg bg-[#0C0E1A] border border-[#1C2042] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
        <div className="flex items-center space-x-2 text-slate-300">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span><strong>Critical Path Bottleneck Interception:</strong> Apply Log4j automated patch (₹18L) + Zero-Trust Micro-segmentation on Payment DB Subnet (₹20L).</span>
        </div>
        <span className="text-emerald-400 font-bold font-mono pl-2 flex-shrink-0">
          -₹57.6L Modeled Risk Reduction (ROI 3.06x)
        </span>
      </div>
    </div>
  );
};
