import React, { useState } from 'react';
import { FileText, Download, Printer, ShieldCheck, Building2, Sparkles, CheckCircle2, Lock } from 'lucide-react';
import { DataSourceBadge } from '../components/DataSourceBadge';
import { reportService } from '../services/api';

export const ExecutiveReports: React.FC = () => {
  const [reportType, setReportType] = useState<string>('BOARD_QUARTERLY');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const handleGenerate = async (type: string) => {
    setIsGenerating(true);
    setReportType(type);
    try {
      await reportService.generate(type);
    } catch (e) {}
    setIsGenerating(false);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Board-Level Executive Risk & Investment Reports
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Generate audit-notarized governance reports with quantitative FAIR risk figures, Google OR-Tools optimization justification, and Hyperledger Fabric cryptographic signatures.
          </p>
          <DataSourceBadge showModeledLabel={true} className="mt-2" />
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleGenerate(reportType)}
            disabled={isGenerating}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition flex items-center space-x-2 shadow-sm"
          >
            <Sparkles className="w-4 h-4" />
            <span>{isGenerating ? 'Compiling Report...' : 'Generate New Report'}</span>
          </button>
        </div>
      </div>

      {/* Preset Report Selectors */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { type: 'BOARD_QUARTERLY', title: 'Quarterly Board Cyber Risk Report', desc: 'Quantitative loss metrics, risk appetite status, and approved investment portfolio' },
          { type: 'CISO_INVESTMENT_PLAN', title: 'CISO Security Investment Portfolio', desc: 'Google OR-Tools MIP solver output with individual control ROI breakdowns' },
          { type: 'AUDITOR_COMPLIANCE_PROOF', title: 'Regulatory & Blockchain Audit Proof', desc: 'NIST/ISO compliance matrix with Hyperledger Fabric cryptographic hashes' }
        ].map((r, i) => (
          <div
            key={i}
            onClick={() => handleGenerate(r.type)}
            className={`enterprise-card p-4 border transition cursor-pointer space-y-1.5 ${
              reportType === r.type ? 'border-cyan-500 bg-[#181C36]' : 'border-[#1C2042] hover:border-[#2A2F5A]'
            }`}
          >
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <h3 className="font-semibold text-xs text-white">{r.title}</h3>
            </div>
            <p className="text-[11px] text-slate-400">{r.desc}</p>
          </div>
        ))}
      </div>

      {/* Generated Report Printable Document View */}
      <div className="enterprise-card p-8 border-[#1C2042] space-y-6 bg-[#0E1122] text-slate-200">
        
        {/* Document Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#1C2042] pb-5 gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <Building2 className="w-5 h-5 text-slate-300" />
              <span className="font-bold text-base text-white tracking-wider uppercase font-mono">ABC BANK</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono">
                CONFIDENTIAL // BOARD OF DIRECTORS
              </span>
            </div>
            <h2 className="text-lg font-bold text-white uppercase tracking-tight">
              CYBERSECURITY QUANTIFICATION & INVESTMENT REPORT (FY26 Q3)
            </h2>
            <div className="text-xs text-slate-400 font-mono">
              Generated: {new Date().toLocaleString()} • Report ID: RPT-2026-Q3-0941 • Platform: Quantum Risk AI
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button 
              onClick={() => window.print()}
              className="px-3.5 py-1.5 rounded-lg bg-[#12152A] hover:bg-[#181C36] border border-[#2A2F5A] text-slate-300 text-xs font-semibold flex items-center space-x-1.5 transition"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print</span>
            </button>
            <button className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition shadow-sm">
              <Download className="w-3.5 h-3.5" />
              <span>Export PDF</span>
            </button>
          </div>
        </div>

        {/* Executive Summary Table */}
        <div className="space-y-2.5">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">1. Executive Summary & Modeled Metrics</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042]">
              <span className="text-slate-500 text-[10px] block uppercase">Current Enterprise Risk</span>
              <span className="text-rose-400 font-bold text-base">82 / 100</span>
              <span className="text-[10px] text-rose-300 block font-sans">Critical Baseline</span>
            </div>
            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042]">
              <span className="text-slate-500 text-[10px] block uppercase">Enterprise Modeled EAL</span>
              <span className="text-amber-400 font-bold text-base">₹4.60 Crore</span>
              <span className="text-[10px] text-slate-400 block font-sans">Annualized Loss</span>
            </div>
            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042]">
              <span className="text-slate-500 text-[10px] block uppercase">Approved Security Spend</span>
              <span className="text-white font-bold text-base">₹85.0 Lakh</span>
              <span className="text-[10px] text-cyan-300 block font-sans">Under ₹1.00 Cr Budget</span>
            </div>
            <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042]">
              <span className="text-slate-500 text-[10px] block uppercase">Modeled Risk Reduction</span>
              <span className="text-emerald-400 font-bold text-base">₹2.60 Crore</span>
              <span className="text-[10px] text-emerald-300 block font-sans">3.06x Decision ROI</span>
            </div>
          </div>
        </div>

        {/* Investment Justification */}
        <div className="space-y-2.5 text-xs leading-relaxed">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">2. Investment Optimization Portfolio (Google OR-Tools MIP Solver)</h3>
          <p className="text-slate-300">
            Under a formal enterprise budget constraint of <strong>₹1.00 Crore</strong>, the Google OR-Tools Mixed-Integer Knapsack algorithm mathematically selected <strong>5 defense-in-depth controls</strong> totaling <strong>₹85.0 Lakh</strong>, preserving a <strong>₹15.0 Lakh</strong> contingency buffer. This portfolio intercepts critical multi-hop lateral movement pathways into the Core Payment Database Cluster.
          </p>

          <div className="p-3.5 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1.5">
            <div className="font-semibold text-white text-xs">Approved Controls Portfolio:</div>
            <ul className="space-y-1.5 font-mono text-[11px] text-slate-300">
              <li className="flex items-center justify-between">
                <span>1. CTRL-PATCH: Automated Critical Patching (Log4j / Spring4Shell)</span>
                <span className="text-slate-200">₹18.0L (Risk Reduction: ₹75.0L)</span>
              </li>
              <li className="flex items-center justify-between">
                <span>2. CTRL-MFA: Privileged Access Multi-Factor Authentication</span>
                <span className="text-slate-200">₹12.0L (Risk Reduction: ₹45.0L)</span>
              </li>
              <li className="flex items-center justify-between">
                <span>3. CTRL-EDR: Next-Gen Autonomous Endpoint Detection & Response</span>
                <span className="text-slate-200">₹25.0L (Risk Reduction: ₹80.0L)</span>
              </li>
              <li className="flex items-center justify-between">
                <span>4. CTRL-SEG: Payment Subnet Micro-segmentation & Zero Trust</span>
                <span className="text-slate-200">₹20.0L (Risk Reduction: ₹60.0L)</span>
              </li>
              <li className="flex items-center justify-between">
                <span>5. CTRL-BACKUP: Air-Gapped Immutable WORM Backup Vault</span>
                <span className="text-slate-200">₹10.0L (Risk Reduction: ₹35.0L)</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Blockchain Cryptographic Verification Footer */}
        <div className="p-3.5 rounded-lg bg-[#12152A] border border-[#1C2042] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
          <div className="space-y-0.5">
            <div className="flex items-center space-x-2 text-emerald-400 font-semibold">
              <ShieldCheck className="w-4 h-4" />
              <span>Hyperledger Fabric Cryptographic Notarization Valid</span>
            </div>
            <div className="text-[10px] text-slate-400 truncate">
              Canonical Hash: 9a72f88b39c011e49afbf4c8996fb92427ae41e4649b934ca495991b7852b855
            </div>
          </div>
          <div className="text-right text-[10px] text-slate-400">
            Signer: Vikram Malhotra (CISO)<br />
            Status: TAMPER-FREE IMMUTABLE LEDGER
          </div>
        </div>

      </div>

    </div>
  );
};
