import React, { useState } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  ShieldAlert, 
  HelpCircle, 
  ArrowRight,
  RefreshCw,
  Cpu,
  Layers,
  Terminal
} from 'lucide-react';
import { assistantService } from '../services/api';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const PRESET_QUESTIONS = [
  "Why is enterprise Expected Annual Loss currently at ₹4.60 Crore?",
  "Explain the 5-hop attack path leading to the Core Payment Database cluster.",
  "How does Google OR-Tools allocate the ₹1.00 Crore budget to reduce risk?",
  "What is the quantitative impact of mitigating Log4j (CVE-2021-44228)?",
  "Summarize our compliance gaps against the RBI Cyber Security Framework."
];

export const AIAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'msg-01',
      sender: 'assistant',
      content: "Hello, I am the Quantum Risk AI Decision Assistant. I provide continuous quantitative cyber risk explanations, attack path breakdowns, and investment optimization rationale directly from live platform telemetry. How may I assist you today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSend = async (questionText?: string) => {
    const textToSend = questionText || input.trim();
    if (!textToSend || isLoading) return;

    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await assistantService.query(textToSend);
      const assistantMsg: Message = {
        id: `ai-${Date.now()}`,
        sender: 'assistant',
        content: res.answer || res.response || "Analysis completed based on current telemetry models.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (e: any) {
      // Offline fallback explanation if API unavailable
      const fallbackReply = generateFallbackReply(textToSend);
      const assistantMsg: Message = {
        id: `ai-${Date.now()}`,
        sender: 'assistant',
        content: fallbackReply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, assistantMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateFallbackReply = (query: string): string => {
    const q = query.toLowerCase();
    if (q.includes('4.6') || q.includes('eal') || q.includes('loss')) {
      return "Enterprise Modeled Expected Annual Loss is currently ₹4.60 Crore, aggregated across 6 key banking scenarios. The primary loss driver is the Core Payment Database (SLE: ₹87.3 Lakh, ARO: 0.52/yr = ₹45.4 Lakh EAL) coupled with active Log4j exploitation and perimeter ingress vulnerability.";
    }
    if (q.includes('attack') || q.includes('path') || q.includes('hop')) {
      return "The critical 5-hop attack path traversed by adversaries: (1) Public Internet -> (2) Edge WAF (Bypass) -> (3) Online Banking API Gateway (Log4j CVE-2021-44228) -> (4) Domain Controller (Privileged Escalation) -> (5) Core Payment Database Cluster. Google OR-Tools recommends Privileged MFA and Micro-segmentation to sever this chain.";
    }
    if (q.includes('budget') || q.includes('optimizer') || q.includes('1.00') || q.includes('crore')) {
      return "For a ₹1.00 Crore allocation, the Google OR-Tools SCIP solver reserves a 15% (₹15 Lakh) regulatory contingency and selects 5 flagship controls costing ₹85.0 Lakh: Automated Vulnerability Patching (₹15L), Privileged MFA (₹12L), EDR/XDR (₹25L), Network Micro-segmentation (₹18L), and Immutable Backup (₹15L). This achieves a ₹2.60 Crore risk reduction with a 3.06x ROI efficiency ratio.";
    }
    if (q.includes('log4j')) {
      return "Log4j (CVE-2021-44228, CVSS 10.0) is actively weaponized and listed in CISA KEV. Remediation through Automated Patching directly reduces the perimeter Threat Event Frequency by 78%, severing the ingress vector into our internal network.";
    }
    if (q.includes('rbi') || q.includes('compliance')) {
      return "Under the RBI Cyber Security Framework for Scheduled Commercial Banks, our modeled control coverage is 81.5% across 65 controls. The primary gap is in Privileged Access Management (PAM) session recording, which is addressed by the recommended Privileged MFA control.";
    }
    return "Based on continuous FAIR quantitative modeling, enterprise risk stands at 82/100 (CRITICAL) with an Expected Annual Loss of ₹4.60 Crore. Google OR-Tools optimization demonstrates that deploying ₹85 Lakh in prioritized controls will reduce annual risk to ₹2.00 Crore.";
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto text-slate-100 h-[calc(100vh-140px)] flex flex-col">
      
      {/* Header */}
      <div className="flex items-center justify-between enterprise-card p-4 border-[#1C2042]">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-gradient-to-br from-violet-600 to-cyan-500 text-white shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
              <span>AI Decision Assistant</span>
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-violet-950 text-violet-300 border border-violet-800 font-mono">
                Model: Tree-SHAP + LLM Reasoner
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Interactive conversational risk intelligence, attack path debriefs, and investment justification
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Telemetry Synchronized</span>
        </div>
      </div>

      {/* Main Grid: Chat + Context Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        
        {/* Left: Chat Stream & Input */}
        <div className="lg:col-span-3 flex flex-col enterprise-card border-[#1C2042] overflow-hidden">
          
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m) => {
              const isUser = m.sender === 'user';
              return (
                <div 
                  key={m.id} 
                  className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[85%] rounded-2xl p-4 space-y-1.5 ${
                    isUser 
                      ? 'bg-gradient-to-r from-violet-600 to-cyan-600 text-white rounded-tr-none shadow-md' 
                      : 'bg-[#0E1122] border border-[#1C2042] text-slate-200 rounded-tl-none'
                  }`}>
                    <div className="flex items-center justify-between text-[10px] opacity-70 font-mono">
                      <span>{isUser ? 'You (CISO / Risk Team)' : 'Quantum Risk AI Assistant'}</span>
                      <span>{m.timestamp}</span>
                    </div>
                    <p className="text-xs leading-relaxed whitespace-pre-line">
                      {m.content}
                    </p>
                  </div>
                </div>
              );
            })}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-[#0E1122] border border-[#1C2042] text-slate-400 rounded-2xl rounded-tl-none p-4 flex items-center space-x-2 text-xs">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                  <span>Synthesizing continuous risk telemetry & running tree explainer...</span>
                </div>
              </div>
            )}
          </div>

          {/* Quick Prompts Bar */}
          <div className="p-3 border-t border-[#1C2042] bg-[#0A0B16] space-y-2">
            <div className="text-[10px] text-slate-400 uppercase font-mono font-bold flex items-center space-x-1.5">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              <span>Recommended Inquiries:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {PRESET_QUESTIONS.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  disabled={isLoading}
                  className="text-[11px] px-2.5 py-1 rounded-lg bg-[#12152A] hover:bg-[#1A1E3A] border border-[#242A54] text-slate-300 hover:text-cyan-300 transition text-left truncate max-w-xs"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input Form */}
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(); }} 
            className="p-3 border-t border-[#1C2042] bg-[#080914] flex items-center space-x-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything regarding enterprise cyber risk, attack graphs, FAIR formulas, or investments..."
              className="flex-1 bg-[#12152A] border border-[#1C2042] focus:border-cyan-500 focus:outline-none px-4 py-2 rounded-xl text-xs text-white placeholder-slate-500 font-sans"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="p-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white transition disabled:opacity-40"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

        </div>

        {/* Right Sidebar: Telemetry Snapshot Panel */}
        <div className="space-y-4">
          
          <div className="enterprise-card p-4 border-[#1C2042] space-y-3 text-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono block">
              Active Context
            </span>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center py-1 border-b border-[#1C2042]">
                <span className="text-slate-400">Enterprise Score:</span>
                <span className="font-mono font-bold text-rose-400">82.0 / 100</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-[#1C2042]">
                <span className="text-slate-400">Modeled EAL:</span>
                <span className="font-mono font-bold text-amber-300">₹4.60 Cr</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-[#1C2042]">
                <span className="text-slate-400">Target Budget:</span>
                <span className="font-mono font-bold text-white">₹1.00 Cr</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-[#1C2042]">
                <span className="text-slate-400">Optimal Investment:</span>
                <span className="font-mono font-bold text-cyan-300">₹85.0 Lakh</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400">Risk Reduction:</span>
                <span className="font-mono font-bold text-emerald-400">₹2.60 Cr (3.06x)</span>
              </div>
            </div>
          </div>

          <div className="enterprise-card p-4 border-[#1C2042] space-y-2 text-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono block">
              Top Active Threat
            </span>
            <div className="p-2.5 rounded-lg bg-rose-950/30 border border-rose-800/60 text-rose-200">
              <div className="font-bold">Log4j (CVE-2021-44228)</div>
              <div className="text-[10px] text-rose-300 mt-1">CVSS 10.0 • Active CISA KEV • Internet Ingress Target</div>
            </div>
          </div>

          <div className="enterprise-card p-4 border-[#1C2042] space-y-2 text-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono block">
              Governing Authority
            </span>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              &quot;AI Recommends, CISO Decides.&quot; Decisions require human authorization by Vikram Malhotra (CISO) and are notarized on the cryptographic audit ledger.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
};
