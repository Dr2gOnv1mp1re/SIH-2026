import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Shield, 
  Bot, 
  Building2, 
  UserCheck, 
  RefreshCw, 
  ChevronDown,
  LogOut,
  KeyRound
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { RiskBadge } from './RiskBadge';
import { ChangePasswordModal } from './ChangePasswordModal';

interface NavbarProps {
  onOpenAssistant: () => void;
  onOpenTamperSandbox?: () => void;
  onTriggerRecalculate?: () => void;
  isRecalculating?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ 
  onOpenAssistant, 
  onTriggerRecalculate,
  isRecalculating 
}) => {
  const navigate = useNavigate();
  const { user, organization, switchRole, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleRoleSelect = (role: any) => {
    switchRole(role);
    setIsDropdownOpen(false);
  };

  const handleLogout = () => {
    setIsDropdownOpen(false);
    logout();
    navigate('/login');
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-[#1C2042] bg-[#07080F]/95 backdrop-blur-md px-6 py-2.5">
        <div className="flex items-center justify-between">
          
          {/* Left: Platform Title & Org */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-600 text-white shadow-sm">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-sm tracking-wide text-white uppercase font-mono">
                    QUANTUM RISK AI
                  </span>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-violet-950/80 text-violet-300 border border-violet-800/60 font-mono">
                    SIH 2026
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">Continuous Cyber Risk Quantification & Investment Optimization</p>
              </div>
            </div>

            <div className="hidden lg:flex items-center space-x-2 pl-4 border-l border-[#1C2042]">
              <Building2 className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-semibold text-slate-200">{organization?.name || 'ABC Bank'}</span>
              <span className="text-[10px] text-slate-400 px-1.5 py-0.5 rounded bg-[#12152A] border border-[#1C2042]">
                {organization?.industry || 'Banking'}
              </span>
            </div>
          </div>

          {/* Center: Live Quantified Risk Ticker */}
          <div className="hidden xl:flex items-center space-x-3 px-3.5 py-1 rounded-lg bg-[#12152A] border border-[#1C2042] text-xs">
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
              <span className="text-slate-400 font-medium">Enterprise Risk:</span>
              <span className="font-mono font-bold text-rose-400">82 / 100</span>
            </div>
            <span className="text-[#1C2042]">|</span>
            <div className="flex items-center space-x-1.5">
              <span className="text-slate-400 font-medium">Modeled EAL:</span>
              <span className="font-mono font-bold text-amber-300">₹4.60 Cr</span>
            </div>
            <span className="text-[#1C2042]">|</span>
            <div className="flex items-center space-x-1.5">
              <span className="text-slate-400 font-medium">Budget:</span>
              <span className="font-mono font-bold text-slate-200">₹1.00 Cr</span>
            </div>
            <span className="text-[#1C2042]">|</span>
            <RiskBadge level="CRITICAL" size="sm" />
          </div>

          {/* Right: Actions, AI Assistant, Role Switcher & Profile */}
          <div className="flex items-center space-x-3">
            
            {/* System Status Quick Link */}
            <Link
              to="/system-status"
              className="hidden md:flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-950/40 hover:bg-emerald-900/50 border border-emerald-800/70 text-xs text-emerald-300 font-mono transition"
              title="View Real-Time System Status across all 9 subsystems"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>System: 9/9 OK</span>
            </Link>

            {/* Recalculate Trigger */}
            {onTriggerRecalculate && (
              <button
                onClick={onTriggerRecalculate}
                disabled={isRecalculating}
                className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#12152A] hover:bg-[#181C36] border border-[#1C2042] text-xs text-slate-300 transition"
                title="Continuous Cyber Risk Dynamic Engine Recalculation"
              >
                <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${isRecalculating ? 'animate-spin' : ''}`} />
                <span>{isRecalculating ? 'Recalculating...' : 'Recalculate'}</span>
              </button>
            )}

            {/* AI Decision Assistant Button */}
            <button
              onClick={onOpenAssistant}
              className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-sm transition active:scale-95"
            >
              <Bot className="w-4 h-4" />
              <span>AI Decision Assistant</span>
            </button>

            {/* Role Switcher & Profile Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button 
                type="button"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-[#12152A] border border-[#1C2042] hover:border-[#2A2F5A] text-xs text-slate-200 transition active:scale-95"
              >
                <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
                <div className="text-left">
                  <div className="font-bold text-[11px] leading-none text-white font-mono">{user?.role || 'Sign In'}</div>
                  <div className="text-[10px] text-slate-400 truncate max-w-[90px]">{user?.full_name || 'Anonymous'}</div>
                </div>
                <ChevronDown className={`w-3 h-3 text-slate-400 transition-transform duration-150 ${isDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Click-Activated Role & Profile Dropdown Menu */}
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 rounded-xl bg-[#12152A] border border-[#2A2F5A] p-2 shadow-modal backdrop-blur-xl z-50 animate-in fade-in duration-100">
                  <div className="text-[10px] uppercase font-bold text-slate-400 px-2 py-1 tracking-wider border-b border-[#1C2042] font-mono">
                    Switch Active Role
                  </div>
                  {[
                    { role: 'CISO', name: 'Vikram Malhotra', desc: 'Enterprise Decisions & Approvals' },
                    { role: 'SECURITY_ANALYST', name: 'Priya Sharma', desc: 'Vulnerabilities & Attack Paths' },
                    { role: 'RISK_ANALYST', name: 'Rohan Mehta', desc: 'EAL & Monte Carlo Modeling' },
                    { role: 'EXECUTIVE', name: 'Ananya Verma', desc: 'Board Reports & Financials' },
                    { role: 'AUDITOR', name: 'Sanjay Joshi', desc: 'Blockchain & Compliance Proof' },
                    { role: 'ADMIN', name: 'Admin User', desc: 'System Configuration' }
                  ].map((r) => (
                    <button
                      key={r.role}
                      type="button"
                      onClick={() => handleRoleSelect(r.role)}
                      className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs transition flex flex-col mt-1 ${
                        user?.role === r.role ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/70' : 'hover:bg-[#181C36] text-slate-300'
                      }`}
                    >
                      <span className="font-semibold flex items-center justify-between">
                        {r.role}
                        {user?.role === r.role && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />}
                      </span>
                      <span className="text-[10px] text-slate-400">{r.name} • {r.desc}</span>
                    </button>
                  ))}

                  {/* Actions: Change Password & Logout */}
                  <div className="pt-2 mt-2 border-t border-[#1C2042] space-y-1">
                    <button
                      type="button"
                      onClick={() => {
                        setIsDropdownOpen(false);
                        setIsPasswordModalOpen(true);
                      }}
                      className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs transition flex items-center justify-between text-slate-300 hover:bg-[#181C36] hover:text-white"
                    >
                      <span>Change Password</span>
                      <KeyRound className="w-3.5 h-3.5 text-slate-400" />
                    </button>

                    <button
                      type="button"
                      onClick={handleLogout}
                      className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs transition flex items-center justify-between text-rose-400 hover:bg-rose-950/60 hover:text-rose-300 font-semibold"
                    >
                      <span>Sign Out / Log Out</span>
                      <LogOut className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}
            </div>

          </div>

        </div>
      </header>

      {/* Change Password Modal */}
      <ChangePasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
      />
    </>
  );
};
