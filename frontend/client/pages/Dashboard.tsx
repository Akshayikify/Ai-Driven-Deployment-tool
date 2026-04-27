import React, { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import DeploymentsTable from "@/components/DeploymentsTable";
import ProgressTimeline from "@/components/ProgressTimeline";
import LogMonitoringCard from "@/components/LogMonitoringCard";
import AIAgent from "@/components/AIAgent";
import { Card } from "@/components/ui/card";
import { Activity, Clock, Server } from "lucide-react";

import { useDeployment } from "@/context/DeploymentContext";
import { useUser } from "@clerk/clerk-react";
import { Github, ExternalLink, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function Dashboard() {
  const [backendStatus, setBackendStatus] = useState<{ status: string, database: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const { steps, estimatedDuration } = useDeployment();
  const { user, isLoaded } = useUser();

  const hasGitHub = user?.externalAccounts?.some(account => account.provider === 'github');

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((res) => res.json())
      .then((data) => {
        setBackendStatus(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Backend health check failed:", err);
        setLoading(false);
      });
  }, []);

  const connectGitHub = async () => {
    try {
      if (!user) return;
      
      // Clerk v5 uses 'strategy' for external accounts.
      // We also need to redirect the user to the verification URL.
      const externalAccount = await user.createExternalAccount({ 
        strategy: 'oauth_github',
        redirectUrl: window.location.origin + "/dashboard"
      });
      
      const redirectUrl = externalAccount.verification?.externalVerificationRedirectURL;
      if (redirectUrl) {
        window.location.href = redirectUrl.toString();
      }
    } catch (err: any) {
      console.error("Failed to initiate GitHub link:", err);
      toast.error(err.message || "Failed to connect GitHub account");
    }
  };

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 max-w-7xl">
        {/* Welcome Section */}
        <Card className="bg-gradient-to-r from-slate-800/50 to-slate-900/50 border-slate-700 p-4 sm:p-6 mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start sm:items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple flex items-center justify-center flex-shrink-0">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0 flex-1">
                <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
                  Welcome, {user?.firstName || "Developer"}
                </h1>
                <p className="text-slate-400 text-sm sm:text-base mb-2">Deploy your applications with AI-powered automation</p>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${loading ? 'bg-yellow-500 animate-pulse' : backendStatus ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-xs font-mono text-slate-300">
                    Backend: {loading ? "Connecting..." : backendStatus ? `ONLINE (DB: ${backendStatus.database})` : "OFFLINE"}
                  </span>
                </div>
              </div>
            </div>

            {isLoaded && !hasGitHub && (
              <Button 
                onClick={connectGitHub}
                className="bg-[#24292F] hover:bg-[#24292F]/90 text-white border border-slate-700 shadow-xl neon-glow-blue flex items-center gap-2 transition-all duration-300 transform hover:scale-105"
              >
                <Github className="w-4 h-4" />
                <span>Connect GitHub</span>
                <ExternalLink className="w-3 h-3 opacity-50" />
              </Button>
            )}

            {isLoaded && hasGitHub && (
              <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 px-3 py-1.5 rounded-full">
                <Github className="w-4 h-4 text-green-400" />
                <span className="text-xs font-medium text-green-400">GitHub Linked</span>
              </div>
            )}
          </div>
        </Card>

        {!hasGitHub && isLoaded && (
          <div className="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0" />
            <p className="text-sm text-amber-200">
              <span className="font-semibold text-amber-500">Note:</span> Please connect your GitHub account to enable automated deployment and repository discovery. This tool requires repository access to function correctly.
            </p>
          </div>
        )}

        {/* Main Content Area */}
        <div className="space-y-6">
          {/* 1. AI Agent - Full Width */}
          <AIAgent className="h-[600px] w-full" />

          {/* 2. Logs and Status - 75/25 Split */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Log Monitoring - 75% */}
            <LogMonitoringCard className="lg:col-span-3 h-[500px]" />

            {/* Deployment Status - 25% */}
            <Card className="lg:col-span-1 bg-slate-800/50 border-slate-700 p-4 sm:p-6 flex flex-col h-[500px]">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-neon-cyan flex-shrink-0" />
                  <h3 className="text-base sm:text-lg font-semibold text-white">Deployment Status</h3>
                </div>
                {estimatedDuration && (
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider">Est. Time</span>
                    <span className="text-xs font-mono text-neon-cyan">{estimatedDuration}</span>
                  </div>
                )}
              </div>
              <div className="flex-1 overflow-y-auto">
                <ProgressTimeline steps={steps} />
              </div>
            </Card>
          </div>

          {/* 3. Recent Deployments Table */}
          <div className="space-y-6">
            <DeploymentsTable />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
