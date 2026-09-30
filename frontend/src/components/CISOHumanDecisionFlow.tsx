import React from 'react';
import { 
  Sparkles, 
  UserCheck, 
  CheckCircle2, 
  XCircle, 
  RotateCcw, 
  ShieldCheck, 
  ArrowRight,
  Lock
} from 'lucide-react';

export const CISOHumanDecisionFlow: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`enterprise-card p-5 border-[#1C2042] bg-[#0A0D1E] space-y-4 ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1C2042] pb-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
            Human-In-The-Loop Governance Pipeline
          </h2>
        </div>
        <div className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-800">
          MANDATORY EXECUTIVE AUTHORIZATION
        </div>
      </div>

      {/* Visual Pipeline Flow */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs font-mono">
        {/* Step 1: AI Recommendation */}
        <div className="p-3 rounded-lg bg-[#0E1226] border border-[#1C2242] flex flex-col justify-between space-y-2 relative">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-slate-500 font-bold">STAGE 01</span>
            <Sparkles className="w-4 h-4 text-violet-400" />
          </div>
          <div>
            <div className="font-bold text-white text-[11px] tracking-wide">AI RECOMMENDATION</div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              FAIR loss models &amp; OR-Tools compute optimal remediation portfolio.
            </p>
          </div>
          <div className="hidden md:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 text-slate-600">
            <ArrowRight className="w-3.5 h-3.5 text-cyan-500" />
          </div>
        </div>

        {/* Step 2: CISO Review */}
        <div className="p-3 rounded-lg bg-[#0E1226] border border-cyan-700/60 flex flex-col justify-between space-y-2 relative shadow-sm shadow-cyan-950/30">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-cyan-400 font-bold">STAGE 02</span>
            <UserCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <div className="font-bold text-cyan-200 text-[11px] tracking-wide">CISO REVIEW</div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              Executive evaluates budget constraints, risk appetite, and assumptions.
            </p>
          </div>
          <div className="hidden md:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 text-slate-600">
            <ArrowRight className="w-3.5 h-3.5 text-cyan-500" />
          </div>
        </div>

        {/* Step 3: Approve / Modify / Reject */}
        <div className="p-3 rounded-lg bg-[#0E1226] border border-[#1C2242] flex flex-col justify-between space-y-2 relative">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-slate-500 font-bold">STAGE 03</span>
            <div className="flex space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
              <XCircle className="w-3.5 h-3.5 text-rose-400" />
            </div>
          </div>
          <div>
            <div className="font-bold text-white text-[11px] tracking-wide">APPROVE / MODIFY / REJECT</div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              Human executive authorizes, requests revision, or overrides proposed plan.
            </p>
          </div>
          <div className="hidden md:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 text-slate-600">
            <ArrowRight className="w-3.5 h-3.5 text-cyan-500" />
          </div>
        </div>

        {/* Step 4: Audit Record */}
        <div className="p-3 rounded-lg bg-[#0E1226] border border-[#1C2242] flex flex-col justify-between space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-slate-500 font-bold">STAGE 04</span>
            <Lock className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <div className="font-bold text-white text-[11px] tracking-wide">AUDIT RECORD</div>
            <p className="text-[10px] text-slate-400 font-sans mt-0.5">
              Decision committed to immutable SHA-256 blockchain ledger.
            </p>
          </div>
        </div>
      </div>

      {/* Explicit Decision Chain Diagram */}
      <div className="p-3.5 rounded-lg bg-[#070914] border border-[#1C2042] flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs">
        <div className="flex flex-col items-center sm:flex-row sm:items-center gap-2 sm:gap-3 text-slate-300 w-full md:w-auto justify-center">
          <span className="px-2.5 py-1 rounded bg-[#0E1226] border border-violet-700/60 text-violet-300 font-bold text-[11px]">
            AI RECOMMENDATION
          </span>
          <span className="text-cyan-400 font-bold hidden sm:inline">&rarr;</span>
          <span className="text-cyan-400 font-bold sm:hidden">&darr;</span>
          <span className="px-2.5 py-1 rounded bg-[#0E1226] border border-cyan-600 text-cyan-200 font-bold text-[11px] shadow-sm shadow-cyan-950">
            CISO REVIEW
          </span>
          <span className="text-cyan-400 font-bold hidden sm:inline">&rarr;</span>
          <span className="text-cyan-400 font-bold sm:hidden">&darr;</span>
          <span className="px-2.5 py-1 rounded bg-[#0E1226] border border-amber-600/70 text-amber-200 font-bold text-[11px]">
            APPROVE / MODIFY / REJECT
          </span>
          <span className="text-cyan-400 font-bold hidden sm:inline">&rarr;</span>
          <span className="text-cyan-400 font-bold sm:hidden">&darr;</span>
          <span className="px-2.5 py-1 rounded bg-[#0E1226] border border-emerald-600/70 text-emerald-300 font-bold text-[11px]">
            AUDIT RECORD
          </span>
        </div>

        <div className="text-[10px] text-slate-400 italic text-center md:text-right font-sans">
          Strict Human-in-the-Loop Governance: No automated investment execution.
        </div>
      </div>

      {/* Clear Governance Statement */}
      <div className="p-3.5 rounded-lg bg-cyan-950/30 border border-cyan-800/60 flex items-start sm:items-center space-x-2.5 text-xs">
        <span className="text-cyan-400 font-bold font-mono text-[11px] uppercase tracking-wide flex-shrink-0">
          CISO MANDATE:
        </span>
        <p className="text-slate-200 font-semibold tracking-wide">
          "AI provides recommendations. The CISO makes the final decision."
        </p>
      </div>
    </div>
  );
};
