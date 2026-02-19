import React, { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import DeploymentStepper from "@/components/DeploymentStepper";
import FileUploader from "@/components/FileUploader";
import DeploymentsTable from "@/components/DeploymentsTable";
import ProgressTimeline from "@/components/ProgressTimeline";
import LogMonitoringCard from "@/components/LogMonitoringCard";
import AIAgent from "@/components/AIAgent";
import { Card } from "@/components/ui/card";
import { Activity, Upload, Clock, Server } from "lucide-react";

const timelineSteps = [
  {
    id: "upload",
    title: "Code Uploaded",
    description: "Project files successfully uploaded to the platform",
    status: "completed" as const,
    timestamp: "2 minutes ago",
  },
  {
    id: "analyze",
    title: "AI Analysis",
    description: "Analyzing project structure and dependencies",
    status: "active" as const,
    timestamp: "1 minute ago",
  },
  {
    id: "build",
    title: "Build Process",
    description: "Building application for deployment",
    status: "pending" as const,
  },
  {
    id: "deploy",
    title: "Deployment",
    description: "Deploying to production environment",
    status: "pending" as const,
  },
  {
    id: "monitor",
    title: "Monitoring",
    description: "Setting up monitoring and alerts",
    status: "pending" as const,
  },
];

export default function Dashboard() {
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
              <p className="text-slate-400 text-sm sm:text-base">Deploy your applications with AI-powered automation</p>
            </div>
          </div>
        </Card>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-6">
          {/* Main Content Area - Left Column */}
          <div className="xl:col-span-2 space-y-6">
            {/* AI Agent - Expanded */}
            <AIAgent className="h-[600px] w-full" />

            {/* Deployments Table */}
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

          {/* Right Column */}
          <div className="xl:col-span-1 space-y-6">
            {/* Deployment Timeline */}
            <Card className="bg-slate-800/50 border-slate-700 p-4 sm:p-6">
              <div className="flex items-center gap-3 mb-4">
                <Clock className="w-5 h-5 text-neon-cyan flex-shrink-0" />
                <h3 className="text-base sm:text-lg font-semibold text-white">Deployment Timeline</h3>
              </div>
              <ProgressTimeline steps={timelineSteps} />
            </Card>

            {/* Log Monitoring */}
            <LogMonitoringCard />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
