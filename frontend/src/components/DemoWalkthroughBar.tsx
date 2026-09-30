import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ChevronRight, 
  ChevronLeft, 
  RotateCcw, 
  CheckCircle2, 
  X,
  Compass
} from 'lucide-react';
import { demoService } from '../services/api';
import { DemoStep } from '../types';

interface DemoWalkthroughBarProps {
  onStepChange?: (step: number) => void;
  onOpenAssistant?: () => void;
  onOpenTamperSandbox?: () => void;
}

// 18-Step sequence with canonical business labels
const SIH_STEPS = [
  { step: 1, title: 'Baseline Risk', route: '/', desc: 'Baseline enterprise cyber risk & initial asset valuation', eal: '₹2.80 Cr' },
  { step: 2, title: 'New Vulnerability', route: '/assets', desc: 'Discovery of perimeter-facing asset exposures', eal: '₹3.20 Cr' },
  { step: 3, title: 'Log4j Exploit', route: '/vulnerabilities', desc: 'CISA KEV weaponized Log4j & Spring4Shell exploits detected', eal: '₹4.60 Cr' },
  { step: 4, title: 'Risk Recalculation', route: '/risk-heatmap', desc: '5x5 Enterprise Risk matrix shifts to Critical 82/100', eal: '₹4.60 Cr' },
  { step: 5, title: 'Financial Impact', route: '/financial-exposure', desc: 'FAIR quantitative Single Loss Expectancy breakdown', eal: '₹87.3L SLE' },
  { step: 6, title: 'EAL', route: '/financial-exposure', desc: 'Annualized Exposure quantified at ₹4.60 Crore Modeled EAL', eal: '₹4.60 Cr EAL' },
  { step: 7, title: 'Monte Carlo', route: '/monte-carlo', desc: '10,000 iterations modeling loss distribution under uncertainty', eal: '90% CI' },
  { step: 8, title: 'Future Risk Prediction', route: '/ai-predictions', desc: 'XGBoost regression forecasting 30-day risk elevation to ₹95L', eal: '₹95.0L (30d)' },
  { step: 9, title: 'SHAP Explanation', route: '/ai-predictions', desc: 'Feature attribution explains active exploit & criticality drivers', eal: '+32% Exploit' },
  { step: 10, title: 'Attack Path', route: '/attack-paths', desc: '5-hop adversary movement chain targeting Core Payment Database', eal: '₹72.0L DB EAL' },
  { step: 11, title: 'Control Recommendation', route: '/controls', desc: 'Defense-in-depth security controls mapped to attack bottlenecks', eal: '20 Controls' },
  { step: 12, title: 'Budget Input', route: '/optimizer', desc: 'Enterprise cybersecurity budget allocation of ₹1.00 Crore', eal: '₹1.00 Cr Budget' },
  { step: 13, title: 'OR-Tools Optimization', route: '/optimizer', desc: 'Knapsack MIP solver selects 5 controls for ₹85 Lakh optimal spend', eal: '₹85.0L Spend' },
  { step: 14, title: 'What-If Analysis', route: '/what-if', desc: 'Simulated scenario demonstrates ₹2.60 Cr modeled risk reduction', eal: '-₹2.60 Cr Delta' },
  { step: 15, title: 'CISO Review', route: '/ciso', desc: 'CISO command center evaluates portfolio and decision metrics', eal: '3.06x ROI' },
  { step: 16, title: 'CISO Approval', route: '/ciso', desc: 'Formal 1-click CISO authorization for FY26 security portfolio', eal: 'Approved' },
  { step: 17, title: 'Blockchain Recording', route: '/blockchain', desc: 'Hyperledger Fabric notarizes SHA-256 decision block on-chain', eal: 'Block #2 Notarized' },
  { step: 18, title: 'Blockchain Verification', route: '/blockchain', desc: 'Cryptographic tamper test confirms zero database tampering', eal: '100% Verified' }
];

export const DemoWalkthroughBar: React.FC<DemoWalkthroughBarProps> = ({ 
  onStepChange,
  onOpenAssistant,
  onOpenTamperSandbox 
}) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<number>(3);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isGuidedMode, setIsGuidedMode] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleGoToStep = (stepNum: number) => {
    if (stepNum < 1 || stepNum > 18) return;
    // 0ms instant UI update
    setCurrentStep(stepNum);

    const stepObj = SIH_STEPS[stepNum - 1];
    if (isGuidedMode && stepObj) {
      navigate(stepObj.route);
    }

    if (onStepChange) onStepChange(stepNum);

    // Asynchronous non-blocking background synchronization
    demoService.executeStep(stepNum).catch(() => {});
  };

  const activeStep = SIH_STEPS[currentStep - 1] || SIH_STEPS[2];
  const progressPercent = Math.round((currentStep / 18) * 100);

  return (
    <>
      {/* Compact Presentation Controller Bar */}
      <div className="w-full bg-[#0A0B16] border-b border-[#1C2042] px-6 py-2 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        
        {/* Step Badge & Linear Progress */}
        <div className="flex items-center space-x-3 w-full sm:w-auto justify-between sm:justify-start">
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-bold text-slate-400 font-mono uppercase tracking-wider">
              SIH GUIDED DEMO
            </span>
            <span className="px-2 py-0.5 rounded bg-violet-950/80 text-violet-300 font-mono font-bold text-[11px] border border-violet-800/70">
              Step {currentStep} of 18
            </span>
          </div>

          {/* Slim progress bar track */}
          <div className="w-20 sm:w-28 h-1.5 bg-[#1C2042] rounded-full overflow-hidden hidden md:block">
            <div 
              className="h-full bg-gradient-to-r from-violet-500 to-cyan-500 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          {/* Prev / Next controls */}
          <div className="flex items-center space-x-1">
            <button
              onClick={() => handleGoToStep(currentStep - 1)}
              disabled={currentStep === 1 || isLoading}
              className="px-2 py-1 rounded bg-[#12152A] hover:bg-[#181C36] disabled:opacity-30 text-slate-300 transition flex items-center space-x-1 font-medium border border-[#1C2042]"
              title="Previous Step"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span className="text-[11px] hidden sm:inline">Previous</span>
            </button>
            <button
              onClick={() => handleGoToStep(currentStep + 1)}
              disabled={currentStep === 18 || isLoading}
              className="px-2.5 py-1 rounded bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 disabled:opacity-30 text-white font-bold transition flex items-center space-x-1 shadow-sm"
              title="Next Step"
            >
              <span className="text-[11px]">Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={async () => {
                try {
                  await demoService.resetDemo();
                } catch (e) {}
                handleGoToStep(1);
              }}
              className="p-1 rounded bg-[#12152A] hover:bg-[#181C36] text-slate-400 hover:text-white transition border border-[#1C2042]"
              title="Reset SIH Demo to Step 1 Baseline"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Current Active Step Title & One-Sentence Summary */}
        <div className="flex-1 max-w-2xl px-3 py-1 rounded-lg bg-[#12152A] border border-[#1C2042] flex items-center justify-between text-xs w-full sm:w-auto">
          <div className="flex items-center space-x-2 truncate">
            <span className="text-slate-400 font-semibold text-[11px]">Current Step:</span>
            <span className="font-bold text-white truncate text-[11px]">
              {activeStep.title} —
            </span>
            <span className="text-slate-300 truncate hidden lg:inline text-[11px]">
              {activeStep.desc}
            </span>
          </div>
          <div className="pl-3 flex-shrink-0 font-mono font-bold text-amber-400 text-[11px]">
            {activeStep.eal}
          </div>
        </div>

        {/* Mode Toggles and Modal Drawer Trigger */}
        <div className="flex items-center space-x-3 text-xs w-full sm:w-auto justify-end">
          {/* Guided Mode Switch */}
          <button
            onClick={() => setIsGuidedMode(!isGuidedMode)}
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded border transition font-medium ${
              isGuidedMode 
                ? 'bg-cyan-950/60 text-cyan-300 border-cyan-700/70 font-semibold' 
                : 'bg-[#12152A] text-slate-400 border-[#1C2042] hover:text-slate-300'
            }`}
            title="Auto-navigates screen to match active step"
          >
            <Compass className="w-3.5 h-3.5" />
            <span className="text-[11px]">{isGuidedMode ? 'Auto-Navigate: ON' : 'Auto-Navigate: OFF'}</span>
          </button>

          {/* View All Steps Modal Button */}
          <button
            onClick={() => setIsModalOpen(true)}
            className="text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 underline"
          >
            View All 18 Steps
          </button>
        </div>

      </div>

      {/* On-Demand "View All Steps" Modal Drawer */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="relative w-full max-w-4xl max-h-[85vh] rounded-xl enterprise-card border border-[#2A2F5A] shadow-modal flex flex-col overflow-hidden bg-[#12152A]">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1C2042] bg-[#0C0E1A]">
              <div className="flex items-center space-x-2.5">
                <Compass className="w-5 h-5 text-cyan-400" />
                <div>
                  <h3 className="font-bold text-sm text-white">18-Step SIH 2026 Master Demonstration Sequence</h3>
                  <p className="text-[11px] text-slate-400">Select any milestone to jump immediately to that stage in the decision lifecycle</p>
                </div>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1.5 rounded-lg bg-[#181C36] hover:bg-[#2A2F5A] text-slate-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Steps Grid */}
            <div className="p-5 overflow-y-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {SIH_STEPS.map((s) => (
                <div
                  key={s.step}
                  onClick={() => {
                    handleGoToStep(s.step);
                    setIsModalOpen(false);
                  }}
                  className={`p-3 rounded-lg border transition cursor-pointer flex flex-col justify-between space-y-2 ${
                    currentStep === s.step
                      ? 'bg-cyan-950/50 border-cyan-500/70 text-cyan-200'
                      : currentStep > s.step
                      ? 'bg-[#0C0E1A] border-[#1C2042] text-slate-300 hover:border-[#2A2F5A]'
                      : 'bg-[#0A0B16] border-[#1C2042]/60 text-slate-500 hover:text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-xs">Step #{s.step}</span>
                    {currentStep > s.step ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    ) : currentStep === s.step ? (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gradient-to-r from-violet-600 to-cyan-600 text-white font-mono">ACTIVE</span>
                    ) : null}
                  </div>

                  <div>
                    <div className="font-semibold text-xs text-white leading-snug">{s.title}</div>
                    <div className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">{s.desc}</div>
                  </div>

                  <div className="pt-1.5 border-t border-[#1C2042]/60 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-slate-500">{s.route}</span>
                    <span className="text-amber-400 font-bold">{s.eal}</span>
                  </div>
                </div>
              ))}
            </div>

          </div>
        </div>
      )}
    </>
  );
};
