import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  Binary, 
  GitBranch, 
  Server, 
  Bug, 
  Radio, 
  Sliders, 
  DollarSign, 
  BarChart3, 
  Sparkles, 
  Boxes, 
  TrendingDown, 
  FileCheck2, 
  Link2, 
  FileText, 
  ScrollText,
  Bot,
  Activity,
  FlaskConical,
  AlertOctagon,
  History,
  Building2,
  Database,
  Target,
  Settings,
  ShieldCheck,
  Award
} from 'lucide-react';

interface SidebarProps {
  onOpenAssistant?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenAssistant }) => {
  const location = useLocation();

  const navSections = [
    {
      title: 'OVERVIEW',
      links: [
        { to: '/', label: 'Executive Overview', icon: LayoutDashboard, aliases: ['/dashboard'] },
        { to: '/ciso', label: 'CISO Command Center', icon: ShieldAlert, aliases: ['/ciso-command-center'] },
        { to: '/executive-board', label: 'Executive Board', icon: Building2, aliases: ['/board'] },
      ]
    },
    {
      title: 'RISK INTELLIGENCE',
      links: [
        { to: '/risk', label: 'Risk Dashboard', icon: Binary, aliases: ['/risk-dashboard', '/risk-heatmap'] },
        { to: '/risk-history', label: 'Risk History', icon: History },
        { to: '/attack-paths', label: 'Attack Paths', icon: GitBranch },
        { to: '/scenario-lab', label: 'Real-World Scenario Lab', icon: FlaskConical },
        { to: '/incidents', label: 'Incident & Loss Intelligence', icon: AlertOctagon, aliases: ['/incident-intelligence', '/loss-intelligence'] },
      ]
    },
    {
      title: 'ENTERPRISE DATA',
      links: [
        { to: '/data-management', label: 'Data Management', icon: Database },
        { to: '/assets', label: 'Asset Inventory', icon: Server },
        { to: '/vulnerabilities', label: 'Vulnerabilities', icon: Bug },
        { to: '/threat-intelligence', label: 'Threat Intelligence', icon: Radio, aliases: ['/threats'] },
        { to: '/security-controls', label: 'Security Controls', icon: Sliders, aliases: ['/controls'] },
      ]
    },
    {
      title: 'FINANCIAL RISK',
      links: [
        { to: '/financial-risk', label: 'Financial Risk', icon: DollarSign, aliases: ['/financial-exposure'] },
        { to: '/monte-carlo', label: 'Monte Carlo', icon: BarChart3 },
        { to: '/risk-appetite', label: 'Risk Appetite', icon: Target },
      ]
    },
    {
      title: 'AI & ANALYTICS',
      links: [
        { to: '/future-risk', label: 'Future Risk', icon: Sparkles },
        { to: '/explainable-ai', label: 'Explainable AI', icon: Boxes, aliases: ['/ai-predictions'] },
        { to: '/scenario-analysis', label: 'Scenario Analysis', icon: FlaskConical, aliases: ['/what-if'] },
      ]
    },
    {
      title: 'INVESTMENT',
      links: [
        { to: '/investment-optimizer', label: 'Investment Optimizer', icon: TrendingDown, aliases: ['/optimizer'] },
        { to: '/budget-stress-test', label: 'Budget Stress Test', icon: Activity },
      ]
    },
    {
      title: 'GOVERNANCE',
      links: [
        { to: '/ciso-decisions', label: 'CISO Decisions', icon: ShieldCheck, aliases: ['/ciso-approval'] },
        { to: '/audit-trail', label: 'Audit Trail', icon: ScrollText, aliases: ['/auditor'] },
        { to: '/blockchain-audit', label: 'Blockchain Audit', icon: Link2, aliases: ['/blockchain'] },
        { to: '/compliance', label: 'Compliance', icon: FileCheck2 },
        { to: '/reports', label: 'Reports', icon: FileText },
      ]
    },
    {
      title: 'SIH FINAL DEMO',
      links: [
        { to: '/sih-demo', label: 'SIH Final Demo', icon: Award, aliases: ['/demo'] },
      ]
    },
    {
      title: 'SYSTEM',
      links: [
        { to: '/system-status', label: 'System Health', icon: Settings, aliases: ['/system-health'] },
      ]
    }
  ];

  const checkIsActive = (to: string, aliases?: string[]) => {
    const current = location.pathname;
    if (to === '/') {
      return current === '/' || current === '/dashboard';
    }
    if (current === to || current.startsWith(to + '/')) {
      return true;
    }
    if (aliases && aliases.some(alias => current === alias || current.startsWith(alias + '/'))) {
      return true;
    }
    return false;
  };

  return (
    <aside className="w-60 border-r border-[#1C2042] bg-[#07080F] flex flex-col flex-shrink-0 h-[calc(100vh-53px)] sticky top-[53px] overflow-y-auto">
      
      {/* Brand Header */}
      <div className="px-4 py-3 border-b border-[#1C2042] bg-[#0A0B16]">
        <div className="text-[11px] font-extrabold uppercase tracking-widest text-center text-slate-200 font-mono">
          QUANTUM RISK AI
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="p-3 space-y-4">
        {navSections.map((section, idx) => (
          <div key={idx} className="space-y-0.5">
            <div className="text-[9px] font-bold uppercase tracking-wider text-violet-400/60 px-2.5 py-0.5 font-mono">
              {section.title}
            </div>
            <div className="space-y-0.5">
              {section.links.map((link) => {
                const Icon = link.icon;
                const isActive = checkIsActive(link.to, link.aliases);
                return (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    className={`flex items-center space-x-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition ${
                      isActive
                        ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/70 font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-[#12152A]'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                    <span className="truncate">{link.label}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}

        {/* AI Decision Assistant Quick Trigger */}
        {onOpenAssistant && (
          <div className="pt-2 border-t border-[#1C2042]">
            <div className="text-[9px] font-bold uppercase tracking-wider text-violet-400/60 px-2.5 py-0.5 font-mono">
              AI ASSISTANT
            </div>
            <button
              onClick={onOpenAssistant}
              className="w-full flex items-center space-x-2 px-2.5 py-1.5 rounded-md text-xs font-medium text-violet-300 bg-violet-950/40 hover:bg-violet-900/40 border border-violet-800/60 transition mt-0.5"
            >
              <Bot className="w-3.5 h-3.5 text-violet-400 flex-shrink-0" />
              <span>Quick Assistant Modal</span>
            </button>
          </div>
        )}
      </div>

      {/* Footer System Status Link */}
      <NavLink 
        to="/system-status"
        className={`mt-auto p-3 border-t border-[#1C2042] bg-[#0A0B16] text-[10px] space-y-1 text-slate-500 font-mono block hover:bg-[#0E1022] transition ${
          checkIsActive('/system-status', ['/system-health']) ? 'border-cyan-800/80 bg-[#0E1228]' : ''
        }`}
      >
        <div className="flex items-center justify-between">
          <span>Engine Status:</span>
          <span className="text-emerald-400 font-semibold flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse" />
            Active
          </span>
        </div>
        <div className="flex items-center justify-between text-slate-400">
          <span>Optimizer:</span>
          <span>Google OR-Tools</span>
        </div>
        <div className="pt-1.5 mt-1.5 border-t border-[#1C2042]/60 flex items-center justify-between text-[9px] text-slate-500 font-mono">
          <span>Quantum Risk AI</span>
          <span className="text-violet-400/90 font-semibold">SIH 2026 Final • Version 1.0</span>
        </div>
      </NavLink>

    </aside>
  );
};

export default Sidebar;
