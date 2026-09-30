import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DatasetProvider } from './context/DatasetContext';
import { Navbar } from './components/Navbar';
import { DatasetSelectorBar } from './components/DatasetSelectorBar';
import { Sidebar } from './components/Sidebar';
import { DemoWalkthroughBar } from './components/DemoWalkthroughBar';
import { AIAssistantModal } from './components/AIAssistantModal';
import { TamperSandboxModal } from './components/TamperSandboxModal';
import { ErrorBoundary } from './components/ErrorBoundary';

// Existing Pages
import { LoginPage } from './pages/LoginPage';
import { ExecutiveDashboard } from './pages/ExecutiveDashboard';
import { CISODashboard } from './pages/CISODashboard';
import { SecurityAnalystDashboard } from './pages/SecurityAnalystDashboard';
import { AuditorDashboard } from './pages/AuditorDashboard';
import { AssetInventory } from './pages/AssetInventory';
import { VulnerabilityManagement } from './pages/VulnerabilityManagement';
import { ThreatIntelligence } from './pages/ThreatIntelligence';
import { SecurityControls } from './pages/SecurityControls';
import { RiskHeatmap } from './pages/RiskHeatmap';
import { FinancialExposure } from './pages/FinancialExposure';
import { AIPredictions } from './pages/AIPredictions';
import { InvestmentOptimizer } from './pages/InvestmentOptimizer';
import { WhatIfSimulator } from './pages/WhatIfSimulator';
import { AttackPaths } from './pages/AttackPaths';
import { ComplianceMatrix } from './pages/ComplianceMatrix';
import { BlockchainAudit } from './pages/BlockchainAudit';
import { ExecutiveReports } from './pages/ExecutiveReports';
import { SystemIntegrations } from './pages/SystemIntegrations';
import { SystemStatusPage } from './pages/SystemStatusPage';
import { AIAssistantPage } from './pages/AIAssistantPage';
import { RealWorldScenarioLab } from './pages/RealWorldScenarioLab';
import { IncidentLossIntelligence } from './pages/IncidentLossIntelligence';
import { DataManagement } from './pages/DataManagement';
import { ExecutiveBoardView } from './pages/ExecutiveBoardView';

// Dedicated Focused Workflow Pages
import { MonteCarloPage } from './pages/MonteCarloPage';
import { ExplainableAIPage } from './pages/ExplainableAIPage';
import { FutureRiskPage } from './pages/FutureRiskPage';
import { BudgetStressTestPage } from './pages/BudgetStressTestPage';
import { CISODecisionsPage } from './pages/CISODecisionsPage';
import { RiskHistoryPage } from './pages/RiskHistoryPage';
import { RiskAppetitePage } from './pages/RiskAppetitePage';
import { SIHFinalDemoPage } from './pages/SIHFinalDemoPage';

const ProtectedAppLayout: React.FC = () => {
  const { user, token } = useAuth();
  const [isAssistantOpen, setIsAssistantOpen] = useState<boolean>(false);
  const [isTamperModalOpen, setIsTamperModalOpen] = useState<boolean>(false);
  const [isRecalculating, setIsRecalculating] = useState<boolean>(false);

  // If unauthenticated, redirect to /login
  if (!user && !token) {
    return <Navigate to="/login" replace />;
  }

  const handleTriggerRecalculate = () => {
    setIsRecalculating(true);
    setTimeout(() => {
      setIsRecalculating(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-enterprise-bg text-enterprise-textPrimary flex flex-col antialiased selection:bg-enterprise-blue selection:text-white">
      
      {/* Top Main Navbar with User Profile & Logout */}
      <Navbar 
        onOpenAssistant={() => setIsAssistantOpen(true)}
        onOpenTamperSandbox={() => setIsTamperModalOpen(true)}
        onTriggerRecalculate={handleTriggerRecalculate}
        isRecalculating={isRecalculating}
      />

      {/* Dataset Selector Bar & Data Origin Banner */}
      <DatasetSelectorBar />

      {/* 18-Step Master SIH Demonstration Controller Bar */}
      <DemoWalkthroughBar 
        onOpenAssistant={() => setIsAssistantOpen(true)}
        onOpenTamperSandbox={() => setIsTamperModalOpen(true)}
      />

      {/* Main Content Area with Sidebar */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar onOpenAssistant={() => setIsAssistantOpen(true)} />
        
        <main className="flex-1 overflow-y-auto bg-[#07080F]">
          <ErrorBoundary fallbackTitle="View Rendering Error">
            <Routes>
              {/* OVERVIEW */}
              <Route path="/" element={<ExecutiveDashboard />} />
              <Route path="/dashboard" element={<ExecutiveDashboard />} />
              <Route path="/ciso" element={<CISODashboard />} />
              <Route path="/ciso-command-center" element={<CISODashboard />} />
              <Route path="/executive-board" element={<ExecutiveBoardView />} />
              <Route path="/board" element={<ExecutiveBoardView />} />
              
              {/* RISK INTELLIGENCE */}
              <Route path="/risk" element={<RiskHeatmap />} />
              <Route path="/risk-dashboard" element={<RiskHeatmap />} />
              <Route path="/risk-heatmap" element={<RiskHeatmap />} />
              <Route path="/risk-history" element={<RiskHistoryPage />} />
              <Route path="/attack-paths" element={<AttackPaths />} />
              <Route path="/scenario-lab" element={<RealWorldScenarioLab />} />
              <Route path="/real-world-scenarios" element={<RealWorldScenarioLab />} />
              <Route path="/incidents" element={<IncidentLossIntelligence />} />
              <Route path="/incident-intelligence" element={<IncidentLossIntelligence />} />
              <Route path="/loss-intelligence" element={<IncidentLossIntelligence />} />
              
              {/* ENTERPRISE DATA */}
              <Route path="/data-management" element={<DataManagement />} />
              <Route path="/assets" element={<AssetInventory />} />
              <Route path="/vulnerabilities" element={<VulnerabilityManagement />} />
              <Route path="/threats" element={<ThreatIntelligence />} />
              <Route path="/threat-intelligence" element={<ThreatIntelligence />} />
              <Route path="/controls" element={<SecurityControls />} />
              <Route path="/security-controls" element={<SecurityControls />} />
              
              {/* FINANCIAL RISK */}
              <Route path="/financial-risk" element={<FinancialExposure />} />
              <Route path="/financial-exposure" element={<FinancialExposure />} />
              <Route path="/monte-carlo" element={<MonteCarloPage />} />
              <Route path="/risk-appetite" element={<RiskAppetitePage />} />
              
              {/* AI & ANALYTICS */}
              <Route path="/future-risk" element={<FutureRiskPage />} />
              <Route path="/explainable-ai" element={<ExplainableAIPage />} />
              <Route path="/ai-predictions" element={<ExplainableAIPage />} />
              <Route path="/scenario-analysis" element={<WhatIfSimulator />} />
              <Route path="/what-if" element={<WhatIfSimulator />} />
              <Route path="/ai-assistant" element={<AIAssistantPage />} />
              
              {/* INVESTMENT */}
              <Route path="/investment-optimizer" element={<InvestmentOptimizer />} />
              <Route path="/optimizer" element={<InvestmentOptimizer />} />
              <Route path="/budget-stress-test" element={<BudgetStressTestPage />} />
              
              {/* GOVERNANCE */}
              <Route path="/ciso-decisions" element={<CISODecisionsPage />} />
              <Route path="/ciso-approval" element={<CISODecisionsPage />} />
              <Route path="/audit-trail" element={<AuditorDashboard onOpenTamperSandbox={() => setIsTamperModalOpen(true)} />} />
              <Route path="/blockchain" element={<BlockchainAudit />} />
              <Route path="/blockchain-audit" element={<BlockchainAudit />} />
              <Route path="/compliance" element={<ComplianceMatrix />} />
              <Route path="/reports" element={<ExecutiveReports />} />
              
              {/* SIH FINAL DEMO */}
              <Route path="/sih-demo" element={<SIHFinalDemoPage />} />
              <Route path="/demo" element={<SIHFinalDemoPage />} />

              {/* SYSTEM */}
              <Route path="/system-status" element={<SystemStatusPage />} />
              <Route path="/system-health" element={<SystemStatusPage />} />
              
              {/* ADDITIONAL ROLES & CONNECTORS */}
              <Route path="/analyst" element={<SecurityAnalystDashboard />} />
              <Route path="/auditor" element={<AuditorDashboard onOpenTamperSandbox={() => setIsTamperModalOpen(true)} />} />
              <Route path="/integrations" element={<SystemIntegrations />} />

              {/* Fallback to Overview */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </ErrorBoundary>
        </main>
      </div>

      {/* Interactive Global AI Decision Assistant Modal */}
      <AIAssistantModal 
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
      />

      {/* Subtle Project Version Footer */}
      <footer className="border-t border-[#141834] bg-[#05060C] px-6 py-2 flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-slate-500 z-10">
        <div className="flex items-center space-x-2">
          <span className="text-slate-400 font-semibold">Quantum Risk AI</span>
          <span>•</span>
          <span className="text-cyan-400 font-medium">SIH 2026 Final</span>
          <span>•</span>
          <span className="text-slate-400 font-bold">Version 1.0</span>
        </div>
        <div className="text-[10px] text-slate-600 mt-1 sm:mt-0 font-sans">
          Continuous Cyber Risk Quantification &amp; Knapsack Investment Optimizer
        </div>
      </footer>

    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <DatasetProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/*" element={<ProtectedAppLayout />} />
          </Routes>
        </Router>
      </DatasetProvider>
    </AuthProvider>
  );
}

export default App;
