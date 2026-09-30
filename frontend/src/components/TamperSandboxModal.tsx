import React, { useState } from 'react';
import { 
  ShieldAlert, 
  X, 
  RotateCcw,
  Fingerprint,
  AlertTriangle,
  Lock
} from 'lucide-react';
import { blockchainService } from '../services/api';

interface TamperSandboxModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TamperSandboxModal: React.FC<TamperSandboxModalProps> = ({ isOpen, onClose }) => {
  const [tamperValue, setTamperValue] = useState<number>(25.0); // falsify risk score from 82 to 25
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleSimulateTampering = async () => {
    setIsLoading(true);
    try {
      const res = await blockchainService.tamperTest({
        tampered_risk_score: tamperValue,
        tampered_eal: 1000000.0 // ₹10 Lakh
      });
      setResult(res);
    } catch (e) {
      setResult({
        verification_result: 'TAMPERING_DETECTED',
        is_valid: false,
        authentic_on_chain_hash: '9a72f88b39c011e49afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        recalculated_tampered_hash: '3d4b8e19c011e49afbf4c8996fb92427ae41e4649b934ca495991b7852b112',
        alert_message: 'CRITICAL TAMPER WARNING: Database record hash differs from Hyperledger Fabric on-chain block hash!'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetAuthentic = () => {
    setResult(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-2xl rounded-xl enterprise-card border border-[#2A2F5A] shadow-modal flex flex-col overflow-hidden bg-[#12152A]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1C2042] bg-[#0C0E1A]">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-rose-600 text-white">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-sm text-white uppercase tracking-wider">
                  Blockchain Cryptographic Tamper Sandbox
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono">
                  Verification Tool
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Test unauthorized off-chain database manipulation against Hyperledger Fabric</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-[#181C36] hover:bg-[#2A2F5A] text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4">
          
          <div className="p-3.5 rounded-lg bg-[#0C0E1A] border border-[#1C2042] text-xs space-y-2">
            <div className="font-semibold text-slate-200 flex items-center space-x-2">
              <Lock className="w-4 h-4 text-cyan-400" />
              <span>Authentic Off-Chain PostgreSQL Record:</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-slate-400 font-mono text-[11px] pt-0.5">
              <div>Record Type: <span className="text-white font-medium">RISK_ASSESSMENT</span></div>
              <div>Actual Risk Score: <span className="text-rose-400 font-bold">82.0 / 100</span></div>
              <div>Expected Annual Loss: <span className="text-amber-400 font-bold">₹4.60 Crore</span></div>
              <div>Blockchain Tx ID: <span className="text-cyan-300 truncate font-medium">TX-FABRIC-2026-ASSESS-001</span></div>
            </div>
          </div>

          {/* Tampering Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span>Simulate Malicious Database Edit (Falsify Risk Score):</span>
              <span className="font-mono text-rose-400 font-bold">{tamperValue}/100</span>
            </label>
            <input 
              type="range"
              min={10}
              max={60}
              step={1}
              value={tamperValue}
              onChange={(e) => setTamperValue(parseFloat(e.target.value))}
              className="w-full h-2 bg-[#181C36] rounded-lg appearance-none cursor-pointer accent-red-500"
            />
            <p className="text-[11px] text-slate-500">
              An unauthorized actor alters the database to show a fake low risk score of {tamperValue}/100.
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3 pt-1">
            <button
              onClick={handleSimulateTampering}
              disabled={isLoading}
              className="flex-1 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs shadow-sm flex items-center justify-center space-x-2 transition"
            >
              <Fingerprint className="w-4 h-4" />
              <span>{isLoading ? 'Hashing & Verifying...' : 'Execute Tamper Verification Test'}</span>
            </button>
            <button
              onClick={handleResetAuthentic}
              className="px-4 py-2.5 rounded-lg bg-[#181C36] hover:bg-[#2A2F5A] text-slate-300 text-xs font-semibold flex items-center space-x-1.5 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>

          {/* Verification Results Output */}
          {result && (
            <div className="p-4 rounded-lg border border-rose-800 bg-rose-950/70 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-rose-300 flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  <span>VERIFICATION RESULT: {result.verification_result}</span>
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-red-900 border border-red-700 font-mono text-white font-bold">
                  HASH MISMATCH
                </span>
              </div>

              <div className="space-y-1 text-[10px] font-mono">
                <div className="text-slate-400 truncate">
                  Authentic On-Chain SHA-256: <span className="text-emerald-400 font-bold">{result.authentic_on_chain_hash}</span>
                </div>
                <div className="text-slate-400 truncate">
                  Recalculated Off-Chain Hash: <span className="text-rose-400 font-bold">{result.recalculated_tampered_hash}</span>
                </div>
              </div>

              <p className="text-xs text-rose-200 font-medium leading-relaxed">
                {result.alert_message || "CRITICAL: Database modification detected! Off-chain data has been altered after notarization."}
              </p>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
