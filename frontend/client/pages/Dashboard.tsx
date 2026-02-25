import React, { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import DeploymentStepper from "@/components/DeploymentStepper";
import FileUploader from "@/components/FileUploader";
import DeploymentsTable from "@/components/DeploymentsTable";
import ProgressTimeline from "@/components/ProgressTimeline";
import LogMonitoringCard from "@/components/LogMonitoringCard";
import AIAgent from "@/components/AIAgent";
import { Card } from "@/components/ui/card";
import { Activity, Upload, Clock, Server } from "lucide-react";

import { useDeployment } from "@/context/DeploymentContext";

export default function Dashboard() {
  const [backendStatus, setBackendStatus] = useState<{ status: string, database: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const { steps } = useDeployment();

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

  const handleFileSelect = (files: FileList) => {
    console.log("Files selected:", files);
  };

  const handleContinue = () => {
    console.log("Continue to next step");
  };

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 max-w-7xl">
        {/* Welcome Section */}
        <Card className="bg-gradient-to-r from-slate-800/50 to-slate-900/50 border-slate-700 p-4 sm:p-6 mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple flex items-center justify-center flex-shrink-0">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-xl sm:text-2xl font-bold text-white">Welcome to Auto Deploy.AI</h1>
              <p className="text-slate-400 text-sm sm:text-base mb-2">Deploy your applications with AI-powered automation</p>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${loading ? 'bg-yellow-500 animate-pulse' : backendStatus ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs font-mono text-slate-300">
                  Backend: {loading ? "Connecting..." : backendStatus ? `ONLINE (DB: ${backendStatus.database})` : "OFFLINE"}
                </span>
              </div>
            </div>
          </div>
        </Card>

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
              <div className="flex items-center gap-3 mb-4">
                <Clock className="w-5 h-5 text-neon-cyan flex-shrink-0" />
                <h3 className="text-base sm:text-lg font-semibold text-white">Deployment Status</h3>
              </div>
              <div className="flex-1 overflow-y-auto">
                <ProgressTimeline steps={steps} />
              </div>
            </Card>
          </div>

          {/* 3. Recent Deployments - Full Width */}
          <Card className="bg-slate-800/50 border-slate-700 p-4 sm:p-6">
            <div className="flex items-center gap-3 mb-4">
              <Server className="w-5 h-5 text-neon-cyan flex-shrink-0" />
              <h3 className="text-base sm:text-lg font-semibold text-white">Recent Deployments</h3>
            </div>
            <div className="overflow-x-auto">
              <DeploymentsTable />
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
