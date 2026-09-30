import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an unhandled error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 max-w-3xl mx-auto my-12 enterprise-card border-rose-800/80 bg-[#120B16] text-rose-200 shadow-2xl rounded-xl">
          <div className="flex items-center space-x-3 mb-4 border-b border-rose-900/50 pb-3">
            <div className="p-2 rounded-lg bg-rose-950/80 border border-rose-700 text-rose-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-wide">
                {this.props.fallbackTitle || 'Component Render Error'}
              </h2>
              <span className="text-[11px] font-mono text-rose-400">
                A frontend error was intercepted by the Quantum Risk AI Error Boundary
              </span>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-[#0A060E] border border-rose-900/40 text-xs font-mono text-rose-300 space-y-1 mb-5 overflow-x-auto">
            <div className="font-bold text-rose-200">
              {this.state.error?.name}: {this.state.error?.message || 'Unknown component rendering error'}
            </div>
            {this.state.errorInfo?.componentStack && (
              <pre className="text-[10px] text-slate-400 mt-2 leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
                {this.state.errorInfo.componentStack}
              </pre>
            )}
          </div>

          <div className="flex items-center space-x-3 text-xs font-semibold">
            <button
              onClick={this.handleReset}
              className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white transition flex items-center space-x-2 shadow-sm"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Component</span>
            </button>
            <a
              href="/"
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center space-x-2"
            >
              <Home className="w-3.5 h-3.5" />
              <span>Return to Overview</span>
            </a>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
export default ErrorBoundary;
