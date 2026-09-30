import React, { useState, useEffect } from 'react';
import {
  RotateCcw,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  TrendingDown,
  Layers,
  Server,
  Network,
  Cpu,
  Database,
  Lock,
  Zap,
  Info,
  Sliders,
  DollarSign
} from 'lucide-react';
import { DataSourceBadge } from '../components/DataSourceBadge';
import { scenarioService, riskService } from '../services/api';

interface Intervention {
  id: string;
  name: string;
  category: string;
  default_cost: number;
  default_cost_label: string;
  description: string;
  affected_assets: string[];
  affected_attack_paths: string[];
  parameter_effect: {
    sle_affected: boolean;
    lef_affected: boolean;
    rationale: string;
  };
}

export const WhatIfSimulator: React.FC = () => {
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [selectedIntervention, setSelectedIntervention] = useState<string>('patching');
  const [customCost, setCustomCost] = useState<number>(1500000);
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Digital Twin Sliders State
  const [activeTab, setActiveTab] = useState<'presets' | 'sliders'>('presets');
  const [mfaCoverage, setMfaCoverage] = useState<number>(72);
  const [edrCoverage, setEdrCoverage] = useState<number>(85);
  const [patchScore, setPatchScore] = useState<number>(70);
  const [segmentation, setSegmentation] = useState<number>(60);
  const [sliderResult, setSliderResult] = useState<any>(null);
  const [baselineTimestamp, setBaselineTimestamp] = useState<string | null>(null);

  // Fetch intervention list and baseline timestamp on mount
  useEffect(() => {
    loadInterventions();
    riskService.getEnterpriseRisk().then(res => {
      if (res?.timestamp || res?.last_assessment_date) {
        setBaselineTimestamp(res.timestamp || res.last_assessment_date);
      }
    }).catch(() => {});
  }, []);

  // Run simulation when intervention or cost changes
  useEffect(() => {
    if (selectedIntervention) {
      runControlSimulation(selectedIntervention, customCost);
    }
  }, [selectedIntervention, customCost]);

  // Run slider simulation when slider values change (debounced for smooth 60fps interaction)
  useEffect(() => {
    if (activeTab === 'sliders') {
      const timer = setTimeout(() => {
        runSliderSimulation();
      }, 250);
      return () => clearTimeout(timer);
    }
  }, [mfaCoverage, edrCoverage, patchScore, segmentation, activeTab]);

  const loadInterventions = async () => {
    try {
      const data = await scenarioService.getInterventions();
      if (data && data.length > 0) {
        setInterventions(data);
        const first = data[0];
        setSelectedIntervention(first.id);
        setCustomCost(first.default_cost);
      }
    } catch (e) {
      console.error('Failed to load interventions:', e);
    }
  };

  const runControlSimulation = async (intId: string, cost: number) => {
    setIsLoading(true);
    try {
      const res = await scenarioService.simulateControl({
        intervention_id: intId,
        custom_investment_cost: cost
      });
      setSimulationResult(res);
    } catch (e) {
      console.error('Simulation error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const runSliderSimulation = async () => {
    try {
      const res = await scenarioService.simulate({
        mfa_coverage: mfaCoverage,
        edr_coverage: edrCoverage,
        patch_cadence_score: patchScore,
        network_segmentation: segmentation
      });
      setSliderResult(res);
    } catch (e) {
      console.error('Slider simulation error:', e);
    }
  };

  const handleSelectIntervention = (intItem: Intervention) => {
    setSelectedIntervention(intItem.id);
    setCustomCost(intItem.default_cost);
  };

  const resetSliders = () => {
    setMfaCoverage(72);
    setEdrCoverage(85);
    setPatchScore(70);
    setSegmentation(60);
  };

  const formatINR = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} Lakh`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const sim = simulationResult;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Scenario Analysis & What-If Simulator
            </h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono">
              FAIR Risk Engine Integration
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Simulate real enterprise security controls and interventions. Evaluate mathematically rigorous before-and-after financial risk reduction, LEF, SLE, and EAL changes.
          </p>
          <DataSourceBadge showModeledLabel={true} lastCalculated={sim?.timestamp || baselineTimestamp} className="mt-2" />
        </div>

        {/* Tab Toggle */}
        <div className="flex items-center bg-[#0C0E1A] p-1 rounded-lg border border-[#2A2F5A]">
          <button
            onClick={() => setActiveTab('presets')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition flex items-center space-x-1.5 ${
              activeTab === 'presets'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Targeted Controls (7 Interventions)</span>
          </button>
          <button
            onClick={() => setActiveTab('sliders')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition flex items-center space-x-1.5 ${
              activeTab === 'sliders'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Digital Twin Sliders</span>
          </button>
        </div>
      </div>

      {activeTab === 'presets' ? (
        <div className="space-y-6">
          {/* Intervention Selection Cards Grid */}
          <div>
            <div className="text-xs uppercase font-mono font-bold text-slate-400 tracking-wider mb-3 flex items-center justify-between">
              <span>SELECT SECURITY CONTROL / INTERVENTION</span>
              <span className="text-[11px] text-cyan-400 normal-case font-sans">
                Centralized FAIR Model: No Hardcoded Financial Outputs
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {interventions.map((item) => {
                const isSelected = selectedIntervention === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleSelectIntervention(item)}
                    className={`p-3.5 rounded-xl text-left transition border ${
                      isSelected
                        ? 'bg-[#141A33] border-cyan-500 shadow-lg shadow-cyan-950/40 ring-1 ring-cyan-500/50'
                        : 'bg-[#0E1122] border-[#1C2042] hover:border-slate-700 hover:bg-[#12152A]'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">
                        {item.category}
                      </span>
                      <span className="text-xs font-mono font-bold text-cyan-400">
                        {item.default_cost_label}
                      </span>
                    </div>
                    <div className="font-semibold text-xs text-white line-clamp-1">
                      {item.name}
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                      {item.description}
                    </p>
                    <div className="flex items-center space-x-2 mt-2 pt-2 border-t border-slate-800/60 text-[10px] font-mono">
                      <span className={item.parameter_effect.lef_affected ? 'text-emerald-400' : 'text-slate-500'}>
                        {item.parameter_effect.lef_affected ? '✓ Affects LEF' : '— LEF Unchanged'}
                      </span>
                      <span className="text-slate-600">|</span>
                      <span className={item.parameter_effect.sle_affected ? 'text-amber-400' : 'text-slate-500'}>
                        {item.parameter_effect.sle_affected ? '✓ Affects SLE' : '— SLE Unchanged'}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Before -> Control -> After Comparison Section */}
          {sim && (
            <div className="enterprise-card p-6 border-[#1C2042] space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center space-x-2">
                    <span>What-If Comparative Analysis:</span>
                    <span className="text-cyan-400 font-mono">{sim.control.control_name}</span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Data Provenance: {sim.data_provenance}
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-xs text-slate-400 font-medium">Investment Budget:</span>
                  <div className="flex items-center space-x-1.5 bg-[#0C0E1A] px-3 py-1 rounded-lg border border-slate-700">
                    <span className="text-xs text-slate-400 font-mono">₹</span>
                    <input
                      type="number"
                      value={customCost}
                      onChange={(e) => setCustomCost(Math.max(0, parseFloat(e.target.value) || 0))}
                      step={100000}
                      className="bg-transparent text-xs font-mono font-bold text-white w-28 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Three-Column Before -> Control -> After Flow */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* BEFORE COLUMN */}
                <div className="rounded-xl bg-[#0E1122] border border-rose-900/40 p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-rose-900/40 pb-2.5">
                    <span className="text-xs uppercase font-mono font-bold text-rose-400 tracking-wider flex items-center space-x-1.5">
                      <ShieldAlert className="w-4 h-4" />
                      <span>BEFORE INTERVENTION</span>
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">Baseline State</span>
                  </div>

                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-[#12152A] border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase font-mono font-semibold block">
                        Modeled Expected Annual Loss (EAL)
                      </span>
                      <div className="text-2xl font-black text-rose-400 font-mono mt-0.5">
                        {sim.before.expected_annual_loss_label}
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono">Formula: SLE × LEF</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2.5 rounded-lg bg-[#12152A] border border-slate-800">
                        <span className="text-[10px] text-slate-400 uppercase font-mono block">
                          Loss Event Frequency (LEF)
                        </span>
                        <div className="text-sm font-bold text-white font-mono mt-0.5">
                          {sim.before.loss_event_frequency} / yr
                        </div>
                        <span className="text-[9px] text-slate-500">
                          Annual Prob: {sim.before.annual_incident_probability_label}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-[#12152A] border border-slate-800">
                        <span className="text-[10px] text-slate-400 uppercase font-mono block">
                          Single Loss (SLE)
                        </span>
                        <div className="text-sm font-bold text-white font-mono mt-0.5">
                          {sim.before.single_loss_expectancy_label}
                        </div>
                        <span className="text-[9px] text-slate-500">Per breach incident</span>
                      </div>
                    </div>

                    {/* Loss Breakdown Summary */}
                    <div className="p-3 rounded-lg bg-[#12152A]/60 border border-slate-800/80 space-y-1.5 text-[11px]">
                      <span className="text-[10px] uppercase font-mono font-bold text-slate-400 block">
                        Baseline Loss Components
                      </span>
                      <div className="flex justify-between text-slate-300">
                        <span>Direct Financial / Theft:</span>
                        <span className="font-mono font-medium">{formatINR(sim.before.loss_components.direct_theft_loss)}</span>
                      </div>
                      <div className="flex justify-between text-slate-300">
                        <span>Incident Response & Forensics:</span>
                        <span className="font-mono font-medium">{formatINR(sim.before.loss_components.incident_response_cost)}</span>
                      </div>
                      <div className="flex justify-between text-slate-300">
                        <span>Regulatory Sanction / Fines:</span>
                        <span className="font-mono font-medium">{formatINR(sim.before.loss_components.regulatory_sanction_fine)}</span>
                      </div>
                      <div className="flex justify-between text-slate-300">
                        <span>Business Interruption:</span>
                        <span className="font-mono font-medium">{formatINR(sim.before.loss_components.business_interruption_loss)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* CONTROL COLUMN */}
                <div className="rounded-xl bg-[#0E1122] border border-cyan-800/50 p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-cyan-800/40 pb-2.5">
                    <span className="text-xs uppercase font-mono font-bold text-cyan-400 tracking-wider flex items-center space-x-1.5">
                      <Layers className="w-4 h-4" />
                      <span>CONTROL INTERVENTION</span>
                    </span>
                    <span className="text-[10px] font-mono text-cyan-300">{sim.control.category}</span>
                  </div>

                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-[#12152A] border border-cyan-900/60">
                      <span className="text-[10px] text-slate-400 uppercase font-mono font-semibold block">
                        Intervention Investment Cost
                      </span>
                      <div className="text-2xl font-black text-cyan-300 font-mono mt-0.5">
                        {sim.control.investment_cost_label}
                      </div>
                      <span className="text-[10px] text-cyan-400 font-mono">Capex + 1-Yr Opex Allocation</span>
                    </div>

                    <div className="p-3 rounded-lg bg-[#12152A] border border-slate-800 space-y-2">
                      <span className="text-[10px] uppercase font-mono font-bold text-slate-400 block">
                        Affected Assets
                      </span>
                      <div className="space-y-1">
                        {sim.control.affected_assets.map((asset: string, idx: number) => (
                          <div key={idx} className="flex items-center space-x-1.5 text-xs text-slate-300 font-mono">
                            <Server className="w-3 h-3 text-cyan-400 shrink-0" />
                            <span className="truncate">{asset}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-[#12152A] border border-slate-800 space-y-2">
                      <span className="text-[10px] uppercase font-mono font-bold text-slate-400 block">
                        Affected Attack Paths
                      </span>
                      <div className="space-y-1">
                        {sim.control.affected_attack_paths.map((path: string, idx: number) => (
                          <div key={idx} className="flex items-center space-x-1.5 text-xs text-amber-300 font-mono">
                            <Network className="w-3 h-3 text-amber-400 shrink-0" />
                            <span className="truncate">{path}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-[#12152A]/80 border border-slate-800 text-[11px] text-slate-300 leading-relaxed">
                      <span className="text-[10px] uppercase font-mono font-bold text-slate-400 block mb-1">
                        Control-Effectiveness Model Rationale
                      </span>
                      {sim.control.parameter_effect_model}
                    </div>
                  </div>
                </div>

                {/* AFTER COLUMN */}
                <div className="rounded-xl bg-[#0E1122] border border-emerald-800/50 p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-emerald-800/40 pb-2.5">
                    <span className="text-xs uppercase font-mono font-bold text-emerald-400 tracking-wider flex items-center space-x-1.5">
                      <ShieldCheck className="w-4 h-4" />
                      <span>AFTER INTERVENTION</span>
                    </span>
                    <span className="text-[10px] font-mono text-emerald-300">Modeled Target State</span>
                  </div>

                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-[#12152A] border border-emerald-900/70">
                      <span className="text-[10px] text-slate-400 uppercase font-mono font-semibold block">
                        Updated Modeled EAL (Expected Annual Loss)
                      </span>
                      <div className="text-2xl font-black text-emerald-400 font-mono mt-0.5">
                        {sim.after.updated_expected_annual_loss_label}
                      </div>
                      <span className="text-[10px] text-emerald-300 font-mono">
                        Modeled Reduction: {sim.after.modeled_risk_reduction_label} / yr
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2.5 rounded-lg bg-[#12152A] border border-slate-800">
                        <span className="text-[10px] text-slate-400 uppercase font-mono block">
                          Updated LEF
                        </span>
                        <div className="text-sm font-bold text-emerald-300 font-mono mt-0.5">
                          {sim.after.updated_loss_event_frequency} / yr
                        </div>
                        <span className="text-[9px] text-slate-500">
                          Prob: {sim.after.updated_annual_incident_probability_label}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-[#12152A] border border-slate-800">
                        <span className="text-[10px] text-slate-400 uppercase font-mono block">
                          Updated SLE
                        </span>
                        <div className="text-sm font-bold text-slate-200 font-mono mt-0.5">
                          {sim.after.updated_single_loss_expectancy_label}
                        </div>
                        <span className="text-[9px] text-slate-500">
                          {sim.control.variables_changed.sle_changed ? '✓ Mitigated' : '— Unaltered'}
                        </span>
                      </div>
                    </div>

                    {/* Return on Security Investment (ROSI) */}
                    <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/60 text-[11px] space-y-1">
                      <div className="flex items-center justify-between text-xs font-bold text-emerald-300 font-mono">
                        <span>Return on Investment (ROSI):</span>
                        <span>{sim.after.return_on_security_investment_percentage}%</span>
                      </div>
                      <p className="text-[10px] text-slate-400">
                        Formula: (Modeled Risk Reduction - Investment Cost) / Cost
                      </p>
                    </div>

                    {/* Updated Loss Breakdown */}
                    <div className="p-3 rounded-lg bg-[#12152A]/60 border border-slate-800/80 space-y-1.5 text-[11px]">
                      <span className="text-[10px] uppercase font-mono font-bold text-slate-400 block">
                        Updated Loss Components
                      </span>
                      <div className="flex justify-between text-slate-300">
                        <span>Direct Financial / Theft:</span>
                        <span className="font-mono font-medium">{formatINR(sim.after.loss_components.direct_theft_loss)}</span>
                      </div>
                      <div className="flex justify-between text-slate-300">
                        <span>Incident Response & Forensics:</span>
                        <span className="font-mono font-medium">{formatINR(sim.after.loss_components.incident_response_cost)}</span>
                      </div>
                      <div className="flex justify-between text-slate-300">
                        <span>Regulatory Sanction / Fines:</span>
                        <span className="font-mono font-medium">{formatINR(sim.after.loss_components.regulatory_sanction_fine)}</span>
                      </div>
                      <div className="flex justify-between text-slate-300">
                        <span>Business Interruption:</span>
                        <span className="font-mono font-medium">{formatINR(sim.after.loss_components.business_interruption_loss)}</span>
                      </div>
                    </div>
                  </div>
                </div>

              </div>

              {/* Mathematical Consistency Audit Box */}
              <div className="p-4 rounded-xl bg-[#080B17] border border-slate-800 font-mono text-xs space-y-1 text-slate-300">
                <div className="text-[10px] uppercase font-bold text-cyan-400 mb-1">
                  FAIR MODEL MATHEMATICAL AUDIT TRACE
                </div>
                <div className="text-slate-400">{sim.mathematical_audit.formula_before}</div>
                <div className="text-slate-400">{sim.mathematical_audit.formula_after}</div>
                <div className="text-emerald-400 font-bold">{sim.mathematical_audit.delta_reduction}</div>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* DIGITAL TWIN SLIDERS VIEW */
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-[#0E1122] border border-violet-900/60 shadow-card">
            <div className="text-[10px] uppercase font-mono font-bold text-slate-400 tracking-wider mb-2 text-center">
              VIRTUAL DIGITAL TWIN SIMULATION DIVERGENCE
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-center text-center">
              <div className="p-3.5 rounded-lg bg-[#12152A] border border-red-900/60">
                <span className="text-[11px] text-slate-400 block font-medium">BASELINE MODELED EAL</span>
                <div className="text-2xl font-black text-rose-400 font-mono mt-0.5">
                  {sliderResult?.baseline_label || '₹4.60 Cr'}
                </div>
                <span className="text-[10px] text-slate-400 font-mono">Current Posture</span>
              </div>

              <div className="p-3.5 rounded-lg bg-[#12152A] border border-cyan-800/80">
                <span className="text-[11px] text-slate-400 block font-medium">SIMULATED MODELED EAL</span>
                <div className="text-2xl font-black text-cyan-400 font-mono mt-0.5">
                  {sliderResult?.simulated_label || 'Calculating...'}
                </div>
                <span className="text-[10px] text-cyan-300 font-mono">Under Virtual Controls</span>
              </div>

              <div className="p-3.5 rounded-lg bg-[#12152A] border border-emerald-800/80">
                <span className="text-[11px] text-slate-400 block font-medium">MODELED RISK REDUCTION</span>
                <div className="text-2xl font-black text-emerald-400 font-mono mt-0.5">
                  {sliderResult?.modeled_reduction_label || 'Calculating...'}
                </div>
                <span className="text-[10px] text-emerald-300 font-mono">Real-Time Calculated Delta</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* MFA Slider */}
            <div className="enterprise-card p-5 border-[#1C2042] space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-white">Privileged MFA Coverage</span>
                <span className="font-mono text-base font-bold text-cyan-400">{mfaCoverage}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={mfaCoverage}
                onChange={(e) => setMfaCoverage(parseFloat(e.target.value))}
                className="w-full h-2 bg-[#181C36] rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
              <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>0% (Disabled)</span>
                <span>Baseline: 72%</span>
                <span>100% (Enforced)</span>
              </div>
            </div>

            {/* EDR Slider */}
            <div className="enterprise-card p-5 border-[#1C2042] space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-white">Next-Gen EDR / XDR Coverage</span>
                <span className="font-mono text-base font-bold text-emerald-400">{edrCoverage}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={edrCoverage}
                onChange={(e) => setEdrCoverage(parseFloat(e.target.value))}
                className="w-full h-2 bg-[#181C36] rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>0% (Disabled)</span>
                <span>Baseline: 85%</span>
                <span>100% (Full Autonomous)</span>
              </div>
            </div>

            {/* Patch Cadence */}
            <div className="enterprise-card p-5 border-[#1C2042] space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-white">Automated Patching Cadence</span>
                <span className="font-mono text-base font-bold text-amber-400">{patchScore}%</span>
              </div>
              <input
                type="range"
                min={10}
                max={100}
                value={patchScore}
                onChange={(e) => setPatchScore(parseFloat(e.target.value))}
                className="w-full h-2 bg-[#181C36] rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
              <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>Slow (&gt;30d SLA)</span>
                <span>Baseline: 70%</span>
                <span>Zero-Day SLA (100%)</span>
              </div>
            </div>

            {/* Microsegmentation */}
            <div className="enterprise-card p-5 border-[#1C2042] space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-white">Network Micro-segmentation</span>
                <span className="font-mono text-base font-bold text-purple-400">{segmentation}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={segmentation}
                onChange={(e) => setSegmentation(parseFloat(e.target.value))}
                className="w-full h-2 bg-[#181C36] rounded-lg appearance-none cursor-pointer accent-purple-500"
              />
              <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>Flat Subnet (0%)</span>
                <span>Baseline: 60%</span>
                <span>Isolated Enclave (100%)</span>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={resetSliders}
              className="px-4 py-2 rounded-lg bg-[#0C0E1A] hover:bg-[#181C36] border border-[#2A2F5A] text-slate-300 text-xs font-semibold transition flex items-center space-x-1.5 shadow-sm"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Sliders to Baseline</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
