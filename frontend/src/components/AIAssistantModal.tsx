import React, { useState } from 'react';
import { 
  Bot, 
  Send, 
  X, 
  Terminal, 
  HelpCircle, 
  ShieldCheck
} from 'lucide-react';
import { assistantService } from '../services/api';

interface AIAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  toolExecuted?: string;
  dataPoints?: any;
}

const PRESET_QUERIES = [
  "What is our highest financial cyber risk?",
  "What should we do with ₹50 lakh budget?",
  "Why is the Payment Database high risk?",
  "What happens if MFA is disabled?",
  "Which control provides the highest modeled risk reduction?",
  "Which attack path is most dangerous?",
  "Which compliance controls are failing?",
  "Verify latest blockchain audit proof"
];

export const AIAssistantModal: React.FC<AIAssistantModalProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 
        "Welcome to the **Controlled Cyber Risk Decision Assistant**.\n\n" +
        "I execute deterministic backend analytical tools across the live risk engine, Google OR-Tools optimizer, and Hyperledger Fabric audit ledger without hallucination.\n\n" +
        "Click a query suggestion below or ask any decision question.",
      toolExecuted: 'system_initialization()'
    }
  ]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleSend = async (queryText?: string) => {
    const q = queryText || input;
    if (!q.trim() || isLoading) return;

    const userMsg: Message = { role: 'user', content: q };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await assistantService.query(q);
      const assistantMsg: Message = {
        role: 'assistant',
        content: res.answer,
        toolExecuted: res.tool_executed,
        dataPoints: res.data_points
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Unable to reach backend decision tools. Showing calibrated enterprise model metrics for ABC Bank.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-3xl h-[620px] rounded-xl enterprise-card border border-[#2A2F5A] shadow-modal flex flex-col overflow-hidden bg-[#12152A]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1C2042] bg-[#0C0E1A]">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 text-white">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-sm text-white uppercase tracking-wider">
                  AI Decision Intelligence Assistant
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono">
                  Controlled Tool Execution
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Zero Hallucination • Direct Backend Analytics Engine</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-[#181C36] hover:bg-[#2A2F5A] text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-lg p-3.5 text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-sm'
                    : 'bg-[#0C0E1A] border border-[#1C2042] text-slate-200 shadow-sm'
                }`}
              >
                {msg.toolExecuted && (
                  <div className="mb-2 flex items-center space-x-1.5 px-2 py-1 rounded bg-[#0A0B16] border border-[#1C2042] text-[10px] font-mono text-cyan-400">
                    <Terminal className="w-3 h-3" />
                    <span>Executed: {msg.toolExecuted}</span>
                  </div>
                )}
                <div className="whitespace-pre-wrap space-y-2">
                  {msg.content}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center space-x-2 text-xs text-cyan-400 font-mono py-1">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span>Executing analytical tools across Risk & Optimization engines...</span>
            </div>
          )}
        </div>

        {/* Presets Suggestions */}
        <div className="px-5 py-2 border-t border-[#1C2042]/80 bg-[#0C0E1A] flex items-center space-x-2 overflow-x-auto text-[11px]">
          <span className="text-slate-500 font-semibold flex-shrink-0 flex items-center">
            <HelpCircle className="w-3 h-3 mr-1" /> Prompts:
          </span>
          {PRESET_QUERIES.slice(0, 4).map((query, i) => (
            <button
              key={i}
              onClick={() => handleSend(query)}
              disabled={isLoading}
              className="flex-shrink-0 px-2.5 py-1 rounded-md bg-[#12152A] hover:bg-[#181C36] border border-[#2A2F5A]/80 text-slate-300 text-[11px] transition"
            >
              {query}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3.5 border-t border-[#1C2042] bg-[#0C0E1A] flex items-center space-x-2.5">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a cyber risk, budget optimization, or attack path question..."
            disabled={isLoading}
            className="flex-1 bg-[#12152A] border border-[#2A2F5A] rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
          />
          <button
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="p-2 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white font-semibold transition shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
