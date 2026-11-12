import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an unhandled error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[300px] p-6 flex flex-col items-center justify-center text-center bg-white dark:bg-slate-900 rounded-2xl border border-red-200 dark:border-red-900/40 m-4 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-4 text-red-600 dark:text-red-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
            Something went wrong displaying this section
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mb-6">
            An unexpected error occurred while rendering the dashboard. Your background deployment and backend services remain safe and operational.
          </p>
          {this.state.error && (
            <p className="text-xs font-mono bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 px-3 py-1.5 rounded-lg border border-red-200 dark:border-red-900/30 mb-6 max-w-lg truncate">
              {this.state.error.message}
            </p>
          )}
          <Button
            onClick={this.handleReset}
            className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Reload View
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

