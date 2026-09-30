import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  Shield, 
  ShieldAlert,
  Activity,
  Binary,
  LayoutDashboard,
  FileCheck2,
  Lock,
  ArrowRight,
  Building2,
  Sparkles,
  Mail,
  KeyRound,
  X
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isExpired = searchParams.get('expired') === '1';
  const { switchRole, login, getRolePassword, isLoading } = useAuth();
  const [selectedRole, setSelectedRole] = useState<any>(null);
  const [customPassword, setCustomPassword] = useState<string>('');
  const [isPasswordPromptOpen, setIsPasswordPromptOpen] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const roles = [
    {
      role: 'CISO' as const,
      title: 'Chief Information Security Officer (CISO)',
      user_name: 'Vikram Malhotra',
      email: 'ciso@abcbank.com',
      badge: 'CISO / Approver',
      icon: ShieldAlert,
      color: 'border-cyan-700/50 hover:border-cyan-500 bg-[#12152A]',
      desc: 'Risk appetite governance, attack-path interception, and 1-click investment approval.'
    },
    {
      role: 'SECURITY_ANALYST' as const,
      title: 'Security Analyst',
      user_name: 'Priya Sharma',
      email: 'analyst@abcbank.com',
      badge: 'SecOps / Triage',
      icon: Activity,
      color: 'border-[#1C2042] hover:border-[#2A2F5A] bg-[#0E1122]',
      desc: '500 CVE triage queue, in-the-wild CISA KEV active exploits, and endpoint telemetry.'
    },
    {
      role: 'RISK_ANALYST' as const,
      title: 'Quantitative Risk Analyst',
      user_name: 'Rohan Mehta',
      email: 'risk@abcbank.com',
      badge: 'FAIR / Modeling',
      icon: Binary,
      color: 'border-[#1C2042] hover:border-[#2A2F5A] bg-[#0E1122]',
      desc: 'FAIR SLE loss parameter decomposition, 10k Monte Carlo, and XGBoost risk forecast.'
    },
    {
      role: 'EXECUTIVE' as const,
      title: 'Executive Board / CEO',
      user_name: 'Ananya Verma',
      email: 'executive@abcbank.com',
      badge: 'Board & Leadership',
      icon: LayoutDashboard,
      color: 'border-[#1C2042] hover:border-[#2A2F5A] bg-[#0E1122]',
      desc: 'Board cyber risk overview, expected annual loss trajectory, and investment ROI.'
    },
    {
      role: 'AUDITOR' as const,
      title: 'Lead Security Auditor',
      user_name: 'Sanjay Joshi',
      email: 'auditor@abcbank.com',
      badge: 'Blockchain & Audit',
      icon: FileCheck2,
      color: 'border-[#1C2042] hover:border-[#2A2F5A] bg-[#0E1122]',
      desc: 'Hyperledger Fabric ledger notarization, SHA-256 hash checks, and tamper sandbox.'
    },
    {
      role: 'ADMIN' as const,
      title: 'System Administrator',
      user_name: 'Admin User',
      email: 'admin@abcbank.com',
      badge: 'System Admin',
      icon: Lock,
      color: 'border-[#1C2042] hover:border-[#2A2F5A] bg-[#0E1122]',
      desc: 'System integrations, connector pipelines, organization setup, and model configuration.'
    }
  ];

  const handleCardClick = (r: any) => {
    setSelectedRole(r);
    setCustomPassword(getRolePassword(r.role));
    setIsPasswordPromptOpen(true);
    setError(null);
  };

  const handleDirectSignIn = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!selectedRole) return;
    setError(null);
    try {
      await switchRole(selectedRole.role, customPassword);
      setIsPasswordPromptOpen(false);
      navigate('/');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Invalid password for this account.');
    }
  };

  return (
    <div className="min-h-screen bg-[#07080F] flex flex-col justify-center items-center p-6 text-slate-100">
      
      {/* Background Glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] bg-violet-900/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] bg-cyan-900/15 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-violet-950/10 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-5xl space-y-6 relative z-10">
        
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center space-x-3 p-2 px-4 rounded-xl bg-[#12152A] border border-[#1C2042] shadow-sm">
            <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-600 text-white shadow-sm">
              <Shield className="w-6 h-6" />
            </div>
            <div className="text-left">
              <span className="font-extrabold text-base tracking-wider text-white uppercase font-mono block leading-none">
                QUANTUM RISK AI
              </span>
              <span className="text-[10px] text-cyan-400 font-semibold tracking-wider uppercase font-mono">
                SIH Master Edition
              </span>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Enterprise Role Sign In
          </h1>
          <p className="text-xs text-slate-400 max-w-xl mx-auto">
            Select your member role below to sign in securely. Each account has private password encryption protected on the <strong>ABC Bank</strong> network.
          </p>
        </div>

        {isExpired && !error && (
          <div className="p-3 rounded-lg bg-amber-950/80 border border-amber-800 text-amber-200 text-xs text-center max-w-md mx-auto">
            Session expired. Please log in again.
          </div>
        )}

        {error && (
          <div className="p-3 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-200 text-xs text-center max-w-md mx-auto">
            {error}
          </div>
        )}

        {/* Private Role Selection Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {roles.map((r) => {
            const Icon = r.icon;

            return (
              <div
                key={r.role}
                onClick={() => handleCardClick(r)}
                className={`p-4 rounded-xl border transition text-left flex flex-col justify-between space-y-3 shadow-sm cursor-pointer hover:border-cyan-500/60 hover:bg-[#181C36] active:scale-[0.99] ${r.color}`}
              >
                <div className="space-y-2.5">
                  
                  {/* Top Badge & Icon */}
                  <div className="flex items-center justify-between">
                    <div className="p-2 rounded-lg bg-violet-950/60 border border-violet-800/60 text-violet-400">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[#0A0B16] border border-[#1C2042] text-slate-300 font-mono">
                      {r.badge}
                    </span>
                  </div>

                  {/* Title & Name */}
                  <div>
                    <h3 className="font-bold text-sm text-white leading-tight">{r.title}</h3>
                    <div className="text-xs text-cyan-300 font-semibold mt-0.5">{r.user_name}</div>
                  </div>

                  {/* Private Credentials Box (Password Masked & Private) */}
                  <div className="p-2.5 rounded-lg bg-[#0A0B16] border border-[#1C2042] space-y-1 font-mono text-[11px]">
                    <div className="flex items-center space-x-1.5 text-slate-300 truncate">
                      <Mail className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
                      <span className="truncate">{r.email}</span>
                    </div>

                    <div className="flex items-center justify-between text-slate-400 pt-0.5 border-t border-[#1C2042]">
                      <div className="flex items-center space-x-1.5">
                        <Lock className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
                        <span className="text-slate-400 tracking-widest">••••••••••••</span>
                      </div>
                      <span className="text-[9px] text-emerald-400 font-semibold uppercase">Private Key</span>
                    </div>
                  </div>

                  {/* Role Domain */}
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {r.desc}
                  </p>
                </div>

                {/* Direct Action Trigger */}
                <div className="flex items-center justify-between pt-2.5 border-t border-[#1C2042] text-xs text-cyan-400 font-semibold font-mono">
                  <span>Sign In as {r.role}</span>
                  <ArrowRight className="w-4 h-4 text-cyan-400" />
                </div>
              </div>
            );
          })}
        </div>

        {/* Security & Organization Footer */}
        <div className="flex items-center justify-between text-xs text-slate-500 px-2 font-mono pt-2">
          <div className="flex items-center space-x-1.5">
            <Building2 className="w-4 h-4 text-slate-400" />
            <span>ABC Bank Enterprise Network (2,500 Users)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <Sparkles className="w-4 h-4 text-violet-400" />
            <span>Hyperledger Fabric Tamper-Evident</span>
          </div>
        </div>

      </div>

      {/* Private Password & Confirmation Modal */}
      {isPasswordPromptOpen && selectedRole && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="relative w-full max-w-md rounded-xl enterprise-card border border-[#2A2F5A] shadow-modal flex flex-col overflow-hidden bg-[#12152A]">
            
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1C2042] bg-[#0C0E1A]">
              <div className="flex items-center space-x-2.5">
                <div className="p-1.5 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-600 text-white">
                  <Lock className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">Sign In as {selectedRole.role}</h3>
                  <p className="text-[11px] text-slate-400">{selectedRole.email}</p>
                </div>
              </div>
              <button
                onClick={() => setIsPasswordPromptOpen(false)}
                className="p-1.5 rounded-lg bg-[#181C36] hover:bg-[#2A2F5A] text-slate-400 hover:text-white transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleDirectSignIn} className="p-5 space-y-4">
              {error && (
                <div className="p-3 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-200 text-xs">
                  {error}
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 block">
                  Account Password
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                  <input
                    type="password"
                    required
                    value={customPassword}
                    onChange={(e) => setCustomPassword(e.target.value)}
                    placeholder="Enter your account password"
                    className="w-full bg-[#0C0E1A] border border-[#1C2042] rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
                  />
                </div>
                <p className="text-[11px] text-slate-500">
                  Password is authenticated against the live SHA-256 database. If you changed your password, enter your new password here.
                </p>
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 py-2 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-semibold text-xs transition shadow-sm flex items-center justify-center space-x-2"
                >
                  <span>{isLoading ? 'Authenticating...' : 'Sign In to Dashboard'}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setIsPasswordPromptOpen(false)}
                  className="px-4 py-2 rounded-lg bg-[#181C36] hover:bg-[#2A2F5A] text-slate-300 text-xs font-semibold transition"
                >
                  Cancel
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

    </div>
  );
};
