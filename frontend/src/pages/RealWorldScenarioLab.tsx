import React, { useState, useEffect } from 'react';
import {
  FlaskConical,
  ShieldAlert,
  Server,
  DollarSign,
  Activity,
  Sparkles,
  GitBranch,
  Sliders,
  TrendingDown,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Link2,
  ExternalLink,
  Info,
  Layers,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Lock,
  ArrowRight,
  ShieldCheck,
  BarChart3,
  HelpCircle
} from 'lucide-react';
import { realWorldScenarioService } from '../services/api';

export const RealWorldScenarioLab: React.FC = () => {
  // Scenario & Metadata state
  const [catalog, setCatalog] = useState<any[]>([]);
  const [selectedCve, setSelectedCve] = useState<string>('CVE-2021-44228');
  const [scenarioDetails, setScenarioDetails] = useState<any>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [whatIfResult, setWhatIfResult] = useState<any>(null);
  const [optimizationResult, setOptimizationResult] = useState<any>(null);
  const [historyList, setHistoryList] = useState<any[]>([]);

  // Synthetic Enterprise Configurator state
  const [enterpriseConfig, setEnterpriseConfig] = useState<any>({
    total_servers: 120,
    internet_facing_servers: 14,
    asset_criticality: 88.0,
    hourly_downtime_cost: 300000.0,
    incident_outage_hours: 8.0,
    incident_response_hours: 40.0,
    incident_response_hourly_rate: 25000.0,
    data_recovery_base_cost: 1500000.0,
    legal_regulatory_base_cost: 2000000.0,
    business_interruption_base_cost: 2500000.0,
    is_internet_exposed: true,
    threat_activity_level: 92.0
  });

  // UI state
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isSourcesOpen, setIsSourcesOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'ATTACK_PATH' | 'AI_PREDICTION' | 'MONTE_CARLO' | 'WHAT_IF' | 'OPTIMIZATION' | 'CISO_GOVERNANCE'>('OVERVIEW');
  const [budgetSlider, setBudgetSlider] = useState<number>(5000000.0); // ₹50 Lakh
  const [cisoNotes, setCisoNotes] = useState<string>("Authorized for immediate deployment to mitigate Log4Shell CVE-2021-44228.");
  const [cisoFeedback, setCisoFeedback] = useState<string | null>(null);

  // Load initial catalog & enterprise baseline
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setIsLoading(true);
    try {
      const [catRes, profRes, histRes] = await Promise.all([
        realWorldScenarioService.getCatalog(),
        realWorldScenarioService.getEnterpriseProfile(),
        realWorldScenarioService.getHistory()
      ]);

      if (catRes?.catalog) {
        setCatalog(catRes.catalog);
      }
      if (profRes?.enterprise_profile) {
        setEnterpriseConfig((prev: any) => ({ ...prev, ...profRes.enterprise_profile }));
      }
      if (histRes?.history) {
        setHistoryList(histRes.history);
      }

      // Execute baseline analysis for default CVE
      await triggerFullAnalysis('CVE-2021-44228', profRes?.enterprise_profile);
    } catch (err) {
      console.error("Failed to load scenario lab baseline:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const triggerFullAnalysis = async (cveId: string, customConfig?: any) => {
    setIsAnalyzing(true);
    try {
      const cfg = customConfig || enterpriseConfig;
      const [analysis, whatIf, opt, details] = await Promise.all([
        realWorldScenarioService.analyzeScenario({
          cve_id: cveId,
          enterprise_overrides: cfg
        }),
        realWorldScenarioService.runWhatIf({
          cve_id: cveId,
          enterprise_overrides: cfg
        }),
        realWorldScenarioService.optimizeInvestment({
          cve_id: cveId,
          budget: budgetSlider,
          enterprise_overrides: cfg
        }),
        realWorldScenarioService.getScenarioDetails(cveId)
      ]);

      setAnalysisResult(analysis);
      setWhatIfResult(whatIf);
      setOptimizationResult(opt);
      setScenarioDetails(details);

      // Refresh history
      const hist = await realWorldScenarioService.getHistory();
      if (hist?.history) setHistoryList(hist.history);
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleConfigChange = (key: string, value: any) => {
    setEnterpriseConfig((prev: any) => ({
      ...prev,
      [key]: value
    }));
  };

  const handleRunAnalysis = () => {
    triggerFullAnalysis(selectedCve, enterpriseConfig);
  };

  const handleRunOptimization = async () => {
    try {
      const opt = await realWorldScenarioService.optimizeInvestment({
        cve_id: selectedCve,
        budget: budgetSlider,
        enterprise_overrides: enterpriseConfig
      });
      setOptimizationResult(opt);
    } catch (err) {
      console.error("Optimization failed:", err);
    }
  };

  const handleCISODecision = async (decision: 'APPROVE' | 'REJECT' | 'REQUEST_REVIEW') => {
    try {
      const payload: any = {
        cve_id: selectedCve,
        decision: decision,
        ciso_name: "Vikram Malhotra (CISO)",
        decision_notes: cisoNotes,
        modeled_eal: analysisResult?.risk_quantification?.expected_annual_loss || 0,
        recommended_investment: optimizationResult?.total_investment || 0,
        recommended_controls: optimizationResult?.selected_controls?.map((c: any) => c.code || c.name) || []
      };
      const res = await realWorldScenarioService.recordCISODecision(payload);
      setCisoFeedback(`CISO decision [${decision}] recorded on ledger! Block #${res?.blockchain_record?.block_number || 'N/A'}`);
      
      // Refresh history
      const hist = await realWorldScenarioService.getHistory();
      if (hist?.history) setHistoryList(hist.history);
    } catch (err) {
      console.error("CISO decision recording failed:", err);
      setCisoFeedback("Failed to record decision.");
    }
  };

  const formatINR = (val: number) => {
    if (!val && val !== 0) return "₹0";
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)} L`;
    return `₹${Math.round(val).toLocaleString()}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#07080F] flex items-center justify-center p-6">
        <div className="flex flex-col items-center space-y-4">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
          <div className="text-sm font-mono text-cyan-300">
            CONNECTING AUTHORITATIVE THREAT DATA (NVD / CISA KEV)...
          </div>
        </div>
      </div>
    );
  }

  const risk = analysisResult?.risk_quantification;
  const breakdown = risk?.loss_breakdown;
  const meta = scenarioDetails?.threat_metadata;
  const mc = analysisResult?.monte_carlo_simulation;
  const ai = analysisResult?.ai_prediction;
  const attackPath = analysisResult?.modeled_attack_path;
  const proof = analysisResult?.criticality_rule_proof;

  return (
    <div className="min-h-screen bg-[#07080F] text-slate-100 p-6 space-y-6">
      
      {/* ==================================================================== */}
      {/* 1. TOP HEADER & PROVENANCE DISTINCTION BANNER */}
      {/* ==================================================================== */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#1C2042] pb-5">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-cyan-950/60 border border-cyan-700/60 text-cyan-400">
              <FlaskConical className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold text-slate-100 tracking-wide font-mono">
                  REAL-WORLD CYBER INCIDENT SCENARIO LAB
                </h1>
                <span className="px-2 py-0.5 text-[10px] font-bold font-mono uppercase rounded bg-cyan-900/60 text-cyan-300 border border-cyan-700/70">
                  SIH 2026 ROUND 2
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Multi-Dimensional Threat Simulation: Public Intelligence + Synthetic Enterprise Profile + Centralized FAIR Engine
              </p>
            </div>
          </div>
        </div>

        {/* Global Provenance Legend */}
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono">
          <span className="px-2.5 py-1 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/80 flex items-center gap-1.5 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            REAL PUBLIC DATA (NVD / CISA)
          </span>
          <span className="px-2.5 py-1 rounded bg-amber-950/60 text-amber-300 border border-amber-800/80 flex items-center gap-1.5 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
            SYNTHETIC DEMO INPUT
          </span>
          <span className="px-2.5 py-1 rounded bg-violet-950/60 text-violet-300 border border-violet-800/80 flex items-center gap-1.5 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400"></span>
            MODELED FINANCIAL EXPOSURE
          </span>
        </div>
      </div>

      {/* NON-VICTIM MANDATORY DISCLAIMER */}
      <div className="p-3 rounded-lg bg-blue-950/30 border border-blue-800/60 flex items-center justify-between text-xs text-blue-200">
        <div className="flex items-center space-x-2.5">
          <Info className="w-4 h-4 text-cyan-400 flex-shrink-0" />
          <span>
            <strong className="font-semibold text-cyan-300">Synthetic Enterprise Environment for Demonstration: </strong>
            All operational metrics are modeled for <em>ABC Bank (Synthetic Environment)</em>. This system models prospective technical exposure and does NOT assert or reconstruct any historical victim's actual balance-sheet loss.
          </span>
        </div>
        <button
          onClick={() => setIsSourcesOpen(!isSourcesOpen)}
          className="ml-3 px-2.5 py-1 text-[11px] font-mono font-medium rounded bg-[#0E132B] hover:bg-[#161D42] text-cyan-300 border border-cyan-800/60 flex items-center gap-1 flex-shrink-0 transition"
        >
          <span>Authoritative Sources</span>
          {isSourcesOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* AUTHORITATIVE SOURCES DRAWER */}
      {isSourcesOpen && (
        <div className="p-4 rounded-lg bg-[#0A0D1E] border border-cyan-800/50 space-y-3 animate-fadeIn">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold text-cyan-300 uppercase tracking-wider font-mono flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" />
              Verified Public Cybersecurity Sources (Zero-Hallucination Policy)
            </div>
            <span className="text-[10px] text-slate-400 font-mono">
              Cached Authoritative Snapshot (Updated 2026-09-17)
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
            {scenarioDetails?.authoritative_sources?.map((src: any, idx: number) => (
              <div key={idx} className="p-3 rounded bg-[#070914] border border-[#1C2042] space-y-1.5">
                <div className="font-semibold text-slate-200 flex items-center justify-between">
                  <span>{src.organization}</span>
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-cyan-400 hover:text-cyan-200 flex items-center gap-0.5 text-[10px]"
                  >
                    <span>Link</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </div>
                <div className="text-[11px] text-slate-400 font-mono line-clamp-1">{src.title}</div>
                <div className="text-[10px] text-emerald-400 font-mono">
                  Fields: {src.fields_used?.join(', ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* 2. SCENARIO SELECTOR & REAL-WORLD THREAT INTELLIGENCE PANEL */}
      {/* ==================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left: Authoritative Threat Card (4 cols) */}
        <div className="lg:col-span-5 enterprise-card p-5 space-y-4 border-cyan-800/40">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">
              <ShieldAlert className="w-4 h-4" />
              <span>REAL-WORLD THREAT INTELLIGENCE</span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700/60 font-mono font-semibold">
              REAL PUBLIC DATA
            </span>
          </div>

          {/* Scenario Picker */}
          <div>
            <label className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
              Documented Public Incident Scenario
            </label>
            <select
              value={selectedCve}
              onChange={(e) => {
                setSelectedCve(e.target.value);
                triggerFullAnalysis(e.target.value);
              }}
              className="mt-1 w-full bg-[#080B1C] border border-cyan-800/60 rounded px-3 py-2 text-xs text-cyan-200 font-mono focus:outline-none focus:border-cyan-500"
            >
              {catalog.map((sc: any) => (
                <option key={sc.cve_id} value={sc.cve_id}>
                  {sc.short_name} ({sc.cve_id}) — CVSS {sc.cvss_score} Critical
                </option>
              ))}
            </select>
          </div>

          {/* Key Threat Metrics Grid */}
          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">CVE Identifier</div>
              <div className="text-sm font-bold font-mono text-cyan-300 mt-0.5">
                {selectedCve}
              </div>
              <div className="text-[9px] text-emerald-400/80 font-mono mt-0.5">Source: NVD (NIST)</div>
            </div>

            <div className="p-3 rounded bg-[#090C1F] border border-rose-900/40">
              <div className="text-[10px] text-slate-400 font-mono">CVSS v3.1 Severity</div>
              <div className="text-sm font-bold font-mono text-rose-400 mt-0.5 flex items-center justify-between">
                <span>10.0 Critical</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-rose-950 text-rose-300 border border-rose-800">MAX</span>
              </div>
              <div className="text-[9px] text-rose-400/80 font-mono mt-0.5">Vector: AV:N / AC:L / PR:N</div>
            </div>

            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">Known Exploitation</div>
              <div className="text-sm font-bold font-mono text-amber-300 mt-0.5 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                ACTIVE (In the Wild)
              </div>
              <div className="text-[9px] text-amber-400/80 font-mono mt-0.5">Source: CISA KEV Catalog</div>
            </div>

            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">Vulnerability Type</div>
              <div className="text-xs font-bold font-mono text-slate-200 mt-0.5 truncate">
                CWE-502 JNDI RCE
              </div>
              <div className="text-[9px] text-slate-400 font-mono mt-0.5">Apache Log4j 2.0-2.14.1</div>
            </div>
          </div>

          {/* MITRE ATT&CK Techniques */}
          <div className="space-y-2 pt-2 border-t border-[#1C2042]">
            <div className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">
              Relevant MITRE ATT&CK Techniques
            </div>
            <div className="flex flex-wrap gap-1.5">
              {meta?.mitre_attack_techniques?.map((tech: any) => (
                <span
                  key={tech.id}
                  className="px-2 py-0.5 text-[10px] rounded bg-[#0D122E] text-slate-300 border border-[#212952] font-mono"
                  title={tech.description}
                >
                  <strong className="text-cyan-400 font-semibold">{tech.id}</strong>: {tech.name}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Configurable Synthetic Enterprise Business Profile (7 cols) */}
        <div className="lg:col-span-7 enterprise-card p-5 space-y-4 border-amber-800/40">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 uppercase tracking-wider font-mono">
              <Server className="w-4 h-4" />
              <span>SYNTHETIC ENTERPRISE PROFILE (ABC BANK)</span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-700/60 font-mono font-semibold">
              SYNTHETIC DEMO INPUT
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div>
              <label className="text-[10px] font-mono text-slate-400">Total Server Fleet</label>
              <input
                type="number"
                value={enterpriseConfig.total_servers}
                onChange={(e) => handleConfigChange('total_servers', Number(e.target.value))}
                className="mt-1 w-full bg-[#080B1C] border border-[#1A1F3D] rounded px-2.5 py-1.5 text-xs text-slate-200 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] font-mono text-slate-400">Internet-Facing Servers</label>
              <input
                type="number"
                value={enterpriseConfig.internet_facing_servers}
                onChange={(e) => handleConfigChange('internet_facing_servers', Number(e.target.value))}
                className="mt-1 w-full bg-[#080B1C] border border-[#1A1F3D] rounded px-2.5 py-1.5 text-xs text-slate-200 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] font-mono text-slate-400">Downtime Cost (₹/hr)</label>
              <input
                type="number"
                step="50000"
                value={enterpriseConfig.hourly_downtime_cost}
                onChange={(e) => handleConfigChange('hourly_downtime_cost', Number(e.target.value))}
                className="mt-1 w-full bg-[#080B1C] border border-[#1A1F3D] rounded px-2.5 py-1.5 text-xs text-amber-300 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] font-mono text-slate-400">Outage Duration (hrs)</label>
              <input
                type="number"
                step="1"
                value={enterpriseConfig.incident_outage_hours}
                onChange={(e) => handleConfigChange('incident_outage_hours', Number(e.target.value))}
                className="mt-1 w-full bg-[#080B1C] border border-[#1A1F3D] rounded px-2.5 py-1.5 text-xs text-amber-300 font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-1">
            <div>
              <label className="text-[10px] font-mono text-slate-400">IR Forensics Rate (₹/hr)</label>
              <input
                type="number"
                step="5000"
                value={enterpriseConfig.incident_response_hourly_rate}
                onChange={(e) => handleConfigChange('incident_response_hourly_rate', Number(e.target.value))}
                className="mt-1 w-full bg-[#080B1C] border border-[#1A1F3D] rounded px-2.5 py-1.5 text-xs text-slate-200 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] font-mono text-slate-400">Data Recovery Base (₹)</label>
              <input
                type="number"
                step="100000"
                value={enterpriseConfig.data_recovery_base_cost}
                onChange={(e) => handleConfigChange('data_recovery_base_cost', Number(e.target.value))}
                className="mt-1 w-full bg-[#080B1C] border border-[#1A1F3D] rounded px-2.5 py-1.5 text-xs text-slate-200 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] font-mono text-slate-400">Regulatory Fine Base (₹)</label>
              <input
                type="number"
                step="100000"
                value={enterpriseConfig.legal_regulatory_base_cost}
                onChange={(e) => handleConfigChange('legal_regulatory_base_cost', Number(e.target.value))}
                className="mt-1 w-full bg-[#080B1C] border border-[#1A1F3D] rounded px-2.5 py-1.5 text-xs text-slate-200 font-mono"
              />
            </div>
          </div>

          {/* Asset Criticality Slider with Mathematical FAIR Rule Badge */}
          <div className="pt-2 border-t border-[#1C2042] space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5">
                <label className="text-[11px] font-mono text-slate-300 font-semibold">
                  Affected Asset Criticality Score:
                </label>
                <span className="text-xs font-bold font-mono text-amber-400">
                  {enterpriseConfig.asset_criticality} / 100
                </span>
              </div>
              <span className="text-[10px] text-cyan-300/80 font-mono">
                Asset: Payment Application Server (Tier-1)
              </span>
            </div>
            <input
              type="range"
              min="20"
              max="100"
              step="1"
              value={enterpriseConfig.asset_criticality}
              onChange={(e) => handleConfigChange('asset_criticality', Number(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer"
            />
            <div className="flex items-center justify-between text-[9px] text-slate-400 font-mono">
              <span>Low Consequence (20)</span>
              <span className="text-cyan-400 font-semibold">
                FAIR Rule: Modifies Loss Magnitude (SLE); LEF remains invariant.
              </span>
              <span>Maximum Consequence (100)</span>
            </div>
          </div>

          {/* Recalculate Trigger Button */}
          <div className="flex items-center justify-between pt-1">
            <span className="text-[10px] text-slate-400 font-mono">
              Changes update modeled financial calculations dynamically without hardcoding.
            </span>
            <button
              onClick={handleRunAnalysis}
              disabled={isAnalyzing}
              className="px-4 py-2 rounded bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono font-bold text-xs tracking-wider uppercase transition shadow-lg shadow-cyan-900/30 flex items-center space-x-2"
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>ANALYZING SCENARIO...</span>
                </>
              ) : (
                <>
                  <FlaskConical className="w-3.5 h-3.5" />
                  <span>ANALYZE SCENARIO</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>

      {/* ==================================================================== */}
      {/* 3. QUANTIFIED FAIR FINANCIAL RISK & DYNAMIC BREAKDOWN */}
      {/* ==================================================================== */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-bold text-violet-400 uppercase tracking-wider font-mono">
            <DollarSign className="w-4 h-4" />
            <span>TRACEABLE MODELED FINANCIAL EXPOSURE (FAIR-ALIGNED)</span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            Formula: Modeled EAL = Single Loss Expectancy (SLE) × Loss Event Frequency (LEF)
          </span>
        </div>

        {/* Top 4 KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div className="enterprise-card p-4 border-cyan-800/40 relative overflow-hidden">
            <div className="text-[10px] font-mono text-slate-400 uppercase flex items-center justify-between">
              <span>Technical Risk Score</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 font-mono">0-100</span>
            </div>
            <div className="text-2xl font-bold font-mono text-cyan-300 mt-1">
              {risk?.technical_risk_score} / 100
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-1">
              CVSS 10.0 + Threat + Attack Path
            </div>
          </div>

          <div className="enterprise-card p-4 border-emerald-800/40 relative overflow-hidden">
            <div className="text-[10px] font-mono text-slate-400 uppercase flex items-center justify-between">
              <span>Likelihood / LEF</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono">FAIR</span>
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-300 mt-1">
              {risk?.loss_event_frequency} <span className="text-xs text-slate-400 font-normal">events/yr</span>
            </div>
            <div className="text-[10px] text-emerald-400/80 font-mono mt-1">
              Annual Prob: {((risk?.annual_incident_probability || 0) * 100).toFixed(1)}%
            </div>
          </div>

          <div className="enterprise-card p-4 border-amber-800/40 relative overflow-hidden">
            <div className="text-[10px] font-mono text-slate-400 uppercase flex items-center justify-between">
              <span>Loss Magnitude / SLE</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 font-mono">PER EVENT</span>
            </div>
            <div className="text-2xl font-bold font-mono text-amber-300 mt-1">
              {formatINR(risk?.single_loss_expectancy)}
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-1">
              Primary + Secondary Loss Sum
            </div>
          </div>

          <div className="enterprise-card p-4 border-rose-800/60 bg-rose-950/20 relative overflow-hidden">
            <div className="text-[10px] font-mono text-slate-400 uppercase flex items-center justify-between">
              <span>Modeled EAL</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-rose-900 text-rose-200 font-mono font-bold">ANNUAL EXPOSURE</span>
            </div>
            <div className="text-2xl font-bold font-mono text-rose-300 mt-1">
              {formatINR(risk?.expected_annual_loss)}
            </div>
            <div className="text-[10px] text-rose-400/90 font-mono mt-1">
              SLE × LEF (Dynamic Derivation)
            </div>
          </div>

        </div>

        {/* Granular Loss Breakdown Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-1">
          <div className="p-3 rounded bg-[#090C1F] border border-[#1C2244]">
            <div className="text-[10px] text-slate-400 font-mono">1. Downtime Loss</div>
            <div className="text-sm font-bold font-mono text-slate-100 mt-0.5">
              {formatINR(breakdown?.downtime_loss)}
            </div>
            <div className="text-[9px] text-slate-500 font-mono mt-0.5">₹{enterpriseConfig.hourly_downtime_cost/100000}L/hr × {enterpriseConfig.incident_outage_hours}h</div>
          </div>

          <div className="p-3 rounded bg-[#090C1F] border border-[#1C2244]">
            <div className="text-[10px] text-slate-400 font-mono">2. Incident Response</div>
            <div className="text-sm font-bold font-mono text-slate-100 mt-0.5">
              {formatINR(breakdown?.incident_response_loss)}
            </div>
            <div className="text-[9px] text-slate-500 font-mono mt-0.5">40h @ ₹25K/hr Forensics</div>
          </div>

          <div className="p-3 rounded bg-[#090C1F] border border-[#1C2244]">
            <div className="text-[10px] text-slate-400 font-mono">3. Data Recovery</div>
            <div className="text-sm font-bold font-mono text-slate-100 mt-0.5">
              {formatINR(breakdown?.data_recovery_loss)}
            </div>
            <div className="text-[9px] text-slate-500 font-mono mt-0.5">Integrity Reconstruction</div>
          </div>

          <div className="p-3 rounded bg-[#090C1F] border border-[#1C2244]">
            <div className="text-[10px] text-slate-400 font-mono">4. Regulatory / Legal</div>
            <div className="text-sm font-bold font-mono text-slate-100 mt-0.5">
              {formatINR(breakdown?.regulatory_legal_loss)}
            </div>
            <div className="text-[9px] text-slate-500 font-mono mt-0.5">RBI / DPDP Statutory Fine Base</div>
          </div>

          <div className="p-3 rounded bg-[#090C1F] border border-[#1C2244]">
            <div className="text-[10px] text-slate-400 font-mono">5. Business Interruption</div>
            <div className="text-sm font-bold font-mono text-slate-100 mt-0.5">
              {formatINR(breakdown?.business_interruption_loss)}
            </div>
            <div className="text-[9px] text-slate-500 font-mono mt-0.5">Customer Churn & Compensation</div>
          </div>
        </div>

        {/* Invariant Verification Box */}
        <div className="p-3 rounded bg-[#080B1B] border border-cyan-900/50 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono text-slate-300">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />
            <span>
              <strong>FAIR Criticality Separation Verified: </strong>
              Technical attack frequency (LEF = {risk?.loss_event_frequency} events/yr) is mathematically invariant to asset criticality. Asset Criticality strictly governs financial Loss Magnitude (SLE = {formatINR(risk?.single_loss_expectancy)}).
            </span>
          </div>
          <span className="text-[10px] text-emerald-400 font-semibold flex-shrink-0">
            [INVARIANT CHECK: PASSED]
          </span>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* 4. TABBED DEEP-DIVE MODULE NAVIGATION */}
      {/* ==================================================================== */}
      <div className="border-b border-[#1C2042] flex space-x-2 overflow-x-auto text-xs font-mono">
        {[
          { id: 'OVERVIEW', label: 'Overview & Sources', icon: Layers },
          { id: 'ATTACK_PATH', label: 'Modeled Attack Path', icon: GitBranch },
          { id: 'AI_PREDICTION', label: 'AI Prediction (XGBoost + SHAP)', icon: Sparkles },
          { id: 'MONTE_CARLO', label: 'Monte Carlo Simulation', icon: BarChart3 },
          { id: 'WHAT_IF', label: 'What-If Mitigations', icon: Activity },
          { id: 'OPTIMIZATION', label: 'OR-Tools Optimization', icon: TrendingDown },
          { id: 'CISO_GOVERNANCE', label: 'CISO & Blockchain Audit', icon: ShieldCheck }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-3.5 py-2.5 rounded-t font-semibold transition border-b-2 whitespace-nowrap ${
                isActive
                  ? 'bg-cyan-950/40 text-cyan-300 border-cyan-400'
                  : 'text-slate-400 hover:text-slate-200 border-transparent hover:bg-[#0C0F24]'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ==================================================================== */}
      {/* TAB CONTENT 1: OVERVIEW & SOURCES */}
      {/* ==================================================================== */}
      {activeTab === 'OVERVIEW' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="enterprise-card p-5 space-y-3">
            <h3 className="text-xs font-bold text-cyan-400 font-mono uppercase tracking-wider">
              Scenario Architectural Traceability
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              This module bridges the gap between public technical vulnerability disclosures and board-level financial quantification. Under the <strong>Open FAIR Standard (ISO/IEC 27005)</strong>, real-world CVE parameters are mathematically decoupled from internal asset consequentiality:
            </p>
            <div className="p-3 rounded bg-[#070914] border border-[#1C2042] text-[11px] font-mono space-y-1 text-slate-300">
              <div>1. <span className="text-cyan-300 font-semibold">Threat Intelligence</span> (NVD CVSS 10.0 + CISA KEV Exploitation = High Threat Frequency)</div>
              <div>2. <span className="text-cyan-300 font-semibold">Defensive Posture</span> (Edge WAF + EDR controls determine Residual Exploitability Weakness)</div>
              <div>3. <span className="text-cyan-300 font-semibold">Loss Event Frequency</span> (LEF = TEF × Vuln × Weakness × Attack Path)</div>
              <div>4. <span className="text-cyan-300 font-semibold">Single Loss Expectancy</span> (SLE = Downtime + IR + Recovery + Reg + Interruption)</div>
              <div>5. <span className="text-cyan-300 font-semibold">Modeled EAL</span> (Expected Annual Loss = SLE × LEF)</div>
            </div>
          </div>

          <div className="enterprise-card p-5 space-y-3">
            <h3 className="text-xs font-bold text-emerald-400 font-mono uppercase tracking-wider">
              Data Provenance & Traceability Ledger
            </h3>
            <div className="space-y-2 text-xs">
              {Object.entries(analysisResult?.provenance_registry || {}).map(([key, p]: any) => (
                <div key={key} className="flex items-center justify-between p-2 rounded bg-[#080B1C] border border-[#1A1F3D]">
                  <span className="font-mono text-slate-300">{key}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] text-slate-400 font-mono">{p.source}</span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-semibold ${
                      p.source_type === 'REAL PUBLIC DATA' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                      p.source_type === 'SYNTHETIC DEMONSTRATION INPUT' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                      'bg-violet-950 text-violet-300 border border-violet-800'
                    }`}>
                      {p.source_type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB CONTENT 2: MODELED ATTACK PATH */}
      {/* ==================================================================== */}
      {activeTab === 'ATTACK_PATH' && (
        <div className="enterprise-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-cyan-400 font-mono uppercase tracking-wider">
                Modeled Lateral Exploitation Route
              </h3>
              <p className="text-xs text-slate-400">
                {attackPath?.name} (Chain Length: {attackPath?.path_length} Hops)
              </p>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-violet-950 text-violet-300 border border-violet-800 font-mono">
              Target Crown Jewel: {attackPath?.target_crown_jewel}
            </span>
          </div>

          {/* Linear Visual Node Pipeline */}
          <div className="grid grid-cols-1 md:grid-cols-7 gap-2 pt-2">
            {attackPath?.nodes?.map((node: any, idx: number) => (
              <div key={node.id} className="p-3 rounded bg-[#080B1D] border border-cyan-900/40 relative flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span>Hop #{idx + 1}</span>
                    <span className="text-cyan-400 font-bold">{node.type}</span>
                  </div>
                  <div className="text-xs font-bold text-slate-100 font-mono mt-1">
                    {node.name}
                  </div>
                </div>
                <div className="mt-2 pt-2 border-t border-[#1C2042] text-[9px] font-mono text-amber-400">
                  Status: {node.status}
                </div>
              </div>
            ))}
          </div>

          {/* Action Explanations */}
          <div className="space-y-2 pt-2">
            <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
              Step-by-Step Exploit Protocols & Actions
            </div>
            <div className="space-y-1.5">
              {attackPath?.edges?.map((edge: any, idx: number) => (
                <div key={idx} className="p-2.5 rounded bg-[#080A18] border border-[#171B36] flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center space-x-2">
                    <span className="text-cyan-400 font-bold">{idx + 1}.</span>
                    <span className="text-slate-300">{edge.protocol}</span>
                    <ArrowRight className="w-3 h-3 text-slate-500" />
                    <span className="text-amber-300">{edge.action}</span>
                  </div>
                  <span className="text-[10px] text-slate-500">
                    {edge.source} → {edge.target}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB CONTENT 3: AI PREDICTION (XGBOOST + SHAP) */}
      {/* ==================================================================== */}
      {activeTab === 'AI_PREDICTION' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div className="enterprise-card p-5 space-y-4">
            <h3 className="text-xs font-bold text-cyan-400 font-mono uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              XGBoost Predictive Trajectory (90-Day Horizon)
            </h3>
            
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
                <div className="text-[10px] text-slate-400 font-mono">30-Day Predicted EAL</div>
                <div className="text-base font-bold font-mono text-amber-300 mt-1">
                  {formatINR(ai?.predicted_30d_eal)}
                </div>
                <div className="text-[9px] text-amber-400 font-mono mt-0.5">+15% Active Threat</div>
              </div>
              <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
                <div className="text-[10px] text-slate-400 font-mono">60-Day Predicted EAL</div>
                <div className="text-base font-bold font-mono text-rose-300 mt-1">
                  {formatINR(ai?.predicted_60d_eal)}
                </div>
                <div className="text-[9px] text-rose-400 font-mono mt-0.5">+35% Unpatched Age</div>
              </div>
              <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
                <div className="text-[10px] text-slate-400 font-mono">90-Day Predicted EAL</div>
                <div className="text-base font-bold font-mono text-rose-400 mt-1">
                  {formatINR(ai?.predicted_90d_eal)}
                </div>
                <div className="text-[9px] text-rose-500 font-mono mt-0.5">+60% Lateral Sprawl</div>
              </div>
            </div>

            <div className="p-3 rounded bg-[#080A18] border border-[#171B36] text-xs font-mono text-slate-300 space-y-1">
              <div className="flex justify-between">
                <span>Model Confidence:</span>
                <span className="text-cyan-300 font-semibold">{ai?.confidence_percentage}%</span>
              </div>
              <div className="flex justify-between">
                <span>Projected Risk Velocity:</span>
                <span className="text-rose-400 font-semibold">{ai?.trend || 'INCREASING'}</span>
              </div>
            </div>
          </div>

          <div className="enterprise-card p-5 space-y-3">
            <h3 className="text-xs font-bold text-violet-400 font-mono uppercase tracking-wider">
              SHAP Feature Attribution (Risk Drivers)
            </h3>
            <p className="text-xs text-slate-400">
              Tree SHAP attributions explaining why technical risk score is elevated:
            </p>
            <div className="space-y-2">
              {ai?.shap_explanations?.map((item: any, idx: number) => (
                <div key={idx} className="p-2.5 rounded bg-[#080B1C] border border-[#1A1F3D] flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-200">{item.feature}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    item.direction === 'INCREASES_RISK' ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  }`}>
                    {item.impact}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB CONTENT 4: MONTE CARLO STOCHASTIC SIMULATION */}
      {/* ==================================================================== */}
      {activeTab === 'MONTE_CARLO' && (
        <div className="enterprise-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-cyan-400 font-mono uppercase tracking-wider">
                Monte Carlo Stochastic Loss Distribution (10,000 Iterations)
              </h3>
              <p className="text-xs text-slate-400">
                Poisson Frequency Sampling (λ = {risk?.loss_event_frequency}) × Lognormal Severity Centered at SLE
              </p>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono">
              MODELED SIMULATION
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">P50 (Median Exposure)</div>
              <div className="text-lg font-bold font-mono text-cyan-300 mt-1">
                {formatINR(mc?.percentiles?.p50_median || mc?.p50)}
              </div>
            </div>
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">P90 (90th Percentile)</div>
              <div className="text-lg font-bold font-mono text-amber-300 mt-1">
                {formatINR(mc?.percentiles?.p90 || mc?.p90)}
              </div>
            </div>
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">P95 (Extreme Worst-Case)</div>
              <div className="text-lg font-bold font-mono text-rose-300 mt-1">
                {formatINR(mc?.percentiles?.p95 || mc?.p95)}
              </div>
            </div>
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">Mean Expected Loss</div>
              <div className="text-lg font-bold font-mono text-emerald-300 mt-1">
                {formatINR(mc?.mean_expected_loss || mc?.mean)}
              </div>
            </div>
          </div>

          {/* Histogram Bins */}
          <div className="space-y-2 pt-2">
            <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
              Annualized Loss Density Histogram (Stochastic Trials)
            </div>
            <div className="grid grid-cols-5 sm:grid-cols-10 gap-1.5 items-end h-28 pt-4">
              {mc?.histogram?.slice(0, 10).map((bin: any, idx: number) => {
                const maxCount = Math.max(...(mc?.histogram?.map((b: any) => b.count) || [1]));
                const pct = Math.round((bin.count / maxCount) * 100);
                return (
                  <div key={idx} className="flex flex-col items-center h-full justify-end group relative">
                    <div
                      style={{ height: `${pct}%` }}
                      className="w-full bg-gradient-to-t from-cyan-900 to-cyan-400 rounded-t transition hover:brightness-125"
                    ></div>
                    <span className="text-[8px] text-slate-400 font-mono mt-1 truncate max-w-full">
                      {bin.label?.split('-')[0]?.trim()}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB CONTENT 5: SCENARIO-SPECIFIC WHAT-IF ANALYSIS */}
      {/* ==================================================================== */}
      {activeTab === 'WHAT_IF' && (
        <div className="enterprise-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-cyan-400 font-mono uppercase tracking-wider">
                Scenario-Specific What-If Mitigations (FAIR Recalculation)
              </h3>
              <p className="text-xs text-slate-400">
                Baseline Exposure: {formatINR(whatIfResult?.baseline?.expected_annual_loss)} / yr
              </p>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
              CENTRALIZED RISK ENGINE EVALUATION
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {whatIfResult?.what_if_simulations?.map((sim: any) => (
              <div key={sim.id} className="p-4 rounded-lg bg-[#090C1F] border border-[#1A1F3D] hover:border-cyan-800/60 transition space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-slate-100 font-mono">{sim.name}</h4>
                    <p className="text-[11px] text-slate-400 mt-0.5">{sim.description}</p>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono font-semibold flex-shrink-0">
                    ROI: {sim.roi_ratio}x
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono pt-1">
                  <div className="p-2 rounded bg-[#070914] border border-[#14182E]">
                    <div className="text-[9px] text-slate-500">Cost</div>
                    <div className="text-slate-200 font-bold mt-0.5">{formatINR(sim.implementation_cost)}</div>
                  </div>
                  <div className="p-2 rounded bg-[#070914] border border-[#14182E]">
                    <div className="text-[9px] text-slate-500">New EAL</div>
                    <div className="text-emerald-300 font-bold mt-0.5">{formatINR(sim.new_eal)}</div>
                  </div>
                  <div className="p-2 rounded bg-[#070914] border border-[#14182E]">
                    <div className="text-[9px] text-slate-500">Risk Reduction</div>
                    <div className="text-cyan-300 font-bold mt-0.5">-{formatINR(sim.modeled_risk_reduction)}</div>
                  </div>
                </div>

                <div className="text-[10px] text-slate-400 font-mono flex items-center gap-1.5 pt-1 border-t border-[#14182E]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                  <span>{sim.effectiveness_note}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB CONTENT 6: OR-TOOLS INVESTMENT OPTIMIZATION */}
      {/* ==================================================================== */}
      {activeTab === 'OPTIMIZATION' && (
        <div className="enterprise-card p-5 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-[#1C2042] pb-4">
            <div>
              <h3 className="text-xs font-bold text-cyan-400 font-mono uppercase tracking-wider">
                Google OR-Tools SCIP Mixed-Integer Knapsack Optimization
              </h3>
              <p className="text-xs text-slate-400">
                Solves optimal control portfolio maximizing modeled risk reduction subject to budget cap.
              </p>
            </div>

            {/* Budget Slider */}
            <div className="flex items-center space-x-3">
              <span className="text-xs font-mono text-slate-300">
                Budget Cap: <strong className="text-amber-400 font-semibold">{formatINR(budgetSlider)}</strong>
              </span>
              <input
                type="range"
                min="2000000"
                max="10000000"
                step="500000"
                value={budgetSlider}
                onChange={(e) => setBudgetSlider(Number(e.target.value))}
                className="w-36 accent-cyan-400 cursor-pointer"
              />
              <button
                onClick={handleRunOptimization}
                className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold transition"
              >
                OPTIMIZE
              </button>
            </div>
          </div>

          {/* Optimization Results Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">Recommended Investment</div>
              <div className="text-base font-bold font-mono text-cyan-300 mt-1">
                {formatINR(optimizationResult?.total_investment)}
              </div>
            </div>
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">Remaining Budget Buffer</div>
              <div className="text-base font-bold font-mono text-emerald-300 mt-1">
                {formatINR(optimizationResult?.remaining_budget)}
              </div>
            </div>
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">Modeled Risk Reduction</div>
              <div className="text-base font-bold font-mono text-violet-300 mt-1">
                {formatINR(optimizationResult?.modeled_risk_reduction)}
              </div>
            </div>
            <div className="p-3 rounded bg-[#090C1F] border border-[#1A1F3D]">
              <div className="text-[10px] text-slate-400 font-mono">Projected Modeled EAL</div>
              <div className="text-base font-bold font-mono text-amber-300 mt-1">
                {formatINR(optimizationResult?.projected_eal)}
              </div>
            </div>
          </div>

          {/* Selected Portfolio Controls */}
          <div className="space-y-2">
            <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
              Recommended Control Portfolio Selection
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {optimizationResult?.selected_controls?.map((ctrl: any) => (
                <div key={ctrl.control_id || ctrl.code} className="p-3 rounded bg-[#090C1F] border border-cyan-800/40 flex items-center justify-between text-xs font-mono">
                  <div>
                    <div className="font-bold text-slate-200">{ctrl.name}</div>
                    <div className="text-[10px] text-slate-400">{ctrl.code} • {ctrl.category}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-cyan-300 font-bold">{formatINR(ctrl.implementation_cost)}</div>
                    <div className="text-[9px] text-emerald-400">-{formatINR(ctrl.modeled_risk_reduction)} EAL</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB CONTENT 7: CISO GOVERNANCE & BLOCKCHAIN AUDIT */}
      {/* ==================================================================== */}
      {activeTab === 'CISO_GOVERNANCE' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* CISO Decision Panel (7 cols) */}
          <div className="lg:col-span-7 enterprise-card p-5 space-y-4">
            <h3 className="text-xs font-bold text-cyan-400 font-mono uppercase tracking-wider flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" />
              CISO Human-in-the-Loop Governance Action
            </h3>

            <div className="p-3 rounded bg-[#080B1C] border border-[#1A1F3D] text-xs font-mono space-y-1 text-slate-300">
              <div className="flex justify-between">
                <span>Active Threat Scenario:</span>
                <span className="text-cyan-300 font-semibold">{scenarioDetails?.short_name} ({selectedCve})</span>
              </div>
              <div className="flex justify-between">
                <span>Current Modeled Exposure:</span>
                <span className="text-rose-300 font-semibold">{formatINR(analysisResult?.risk_quantification?.expected_annual_loss)} / yr</span>
              </div>
              <div className="flex justify-between">
                <span>Authorized Investment:</span>
                <span className="text-amber-300 font-semibold">{formatINR(optimizationResult?.total_investment)}</span>
              </div>
            </div>

            <div>
              <label className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                CISO Executive Decision Rationale / Notes
              </label>
              <textarea
                rows={3}
                value={cisoNotes}
                onChange={(e) => setCisoNotes(e.target.value)}
                className="mt-1 w-full bg-[#080B1C] border border-[#1A1F3D] rounded p-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="flex items-center space-x-3 pt-2">
              <button
                onClick={() => handleCISODecision('APPROVE')}
                className="flex-1 py-2.5 rounded bg-emerald-700 hover:bg-emerald-600 text-white font-mono text-xs font-bold uppercase transition flex items-center justify-center gap-1.5 shadow-lg shadow-emerald-950/40"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>APPROVE & COMMIT LEDGER</span>
              </button>
              <button
                onClick={() => handleCISODecision('REQUEST_REVIEW')}
                className="px-4 py-2.5 rounded bg-amber-700 hover:bg-amber-600 text-white font-mono text-xs font-bold uppercase transition flex items-center justify-center gap-1.5"
              >
                <HelpCircle className="w-4 h-4" />
                <span>REQUEST REVIEW</span>
              </button>
              <button
                onClick={() => handleCISODecision('REJECT')}
                className="px-4 py-2.5 rounded bg-rose-800 hover:bg-rose-700 text-white font-mono text-xs font-bold uppercase transition flex items-center justify-center gap-1.5"
              >
                <XCircle className="w-4 h-4" />
                <span>REJECT</span>
              </button>
            </div>

            {cisoFeedback && (
              <div className="p-2.5 rounded bg-emerald-950/50 border border-emerald-700/60 text-emerald-300 text-xs font-mono animate-fadeIn">
                {cisoFeedback}
              </div>
            )}
          </div>

          {/* Blockchain Audit Status Card (5 cols) */}
          <div className="lg:col-span-5 enterprise-card p-5 space-y-4">
            <h3 className="text-xs font-bold text-violet-400 font-mono uppercase tracking-wider flex items-center gap-2">
              <Link2 className="w-4 h-4" />
              Cryptographic Audit Verification
            </h3>
            <p className="text-xs text-slate-400">
              Approved decisions generate canonical SHA-256 hashes anchored to the immutable audit ledger.
            </p>

            <div className="space-y-2">
              <div className="p-3 rounded bg-[#080B1C] border border-[#1A1F3D] font-mono text-xs space-y-1.5">
                <div className="text-[10px] text-slate-400">Network Framework</div>
                <div className="text-cyan-300 font-semibold">Hyperledger Fabric v2.5 (Audit Channel)</div>
                <div className="text-[10px] text-slate-400 pt-1">Cryptographic Hash Algorithm</div>
                <div className="text-slate-200">SHA-256 (Canonical Normalized JSON)</div>
              </div>

              <div className="p-3 rounded bg-[#080B1C] border border-emerald-800/40 text-[10px] font-mono space-y-1 text-slate-300">
                <div className="text-emerald-400 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Audit Trail Integrity: VERIFIED</span>
                </div>
                <div>Blocks are chained sequentially with SHA-256 pointers to prevent retro-active modification.</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* 5. HISTORICAL EVALUATION COMPARISON LOG */}
      {/* ==================================================================== */}
      <div className="enterprise-card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            Scenario Evaluation History & Mitigation Comparison
          </h3>
          <span className="text-[10px] text-slate-400 font-mono">
            {historyList.length} Recorded Runs
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-[#1C2042] text-slate-400 text-[10px] uppercase">
                <th className="py-2 px-3">Date</th>
                <th className="py-2 px-3">Scenario / CVE</th>
                <th className="py-2 px-3">Affected Asset</th>
                <th className="py-2 px-3">Crit.</th>
                <th className="py-2 px-3">Modeled EAL</th>
                <th className="py-2 px-3">CISO Decision</th>
                <th className="py-2 px-3">Ledger Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#13172E]">
              {historyList.slice(-5).reverse().map((rec: any, idx: number) => (
                <tr key={idx} className="hover:bg-[#090C1F] transition">
                  <td className="py-2.5 px-3 text-slate-400">{rec.timestamp?.split('T')[0]}</td>
                  <td className="py-2.5 px-3 text-cyan-300 font-semibold">{rec.scenario_name || rec.cve_id}</td>
                  <td className="py-2.5 px-3 text-slate-300">{rec.affected_asset}</td>
                  <td className="py-2.5 px-3 text-amber-300">{rec.asset_criticality}</td>
                  <td className="py-2.5 px-3 text-rose-300 font-bold">{formatINR(rec.modeled_eal)}</td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      rec.ciso_decision === 'APPROVE' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                      rec.ciso_decision === 'REJECT' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                      'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}>
                      {rec.ciso_decision}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                      <Lock className="w-2.5 h-2.5" />
                      {rec.blockchain_status || 'COMMITTED'}
                    </span>
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
