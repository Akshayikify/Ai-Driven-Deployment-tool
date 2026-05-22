import React, { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import DeploymentsTable from "@/components/DeploymentsTable";
import ProgressTimeline from "@/components/ProgressTimeline";
import LogMonitoringCard from "@/components/LogMonitoringCard";
import AIAgent from "@/components/AIAgent";
import SecurityReportCard from "@/components/SecurityReportCard";
import { Card } from "@/components/ui/card";
import { Activity, Clock, Server, ShieldAlert, ShieldX, Github as GithubIcon, X } from "lucide-react";

import { useDeployment } from "@/context/DeploymentContext";
import { useUser } from "@clerk/clerk-react";
import { Github, ExternalLink, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function Dashboard() {
  const { steps, estimatedDuration, securityReport, awaitingPushConfirmation, confirmPush, cancelPush } = useDeployment();
  const { user, isLoaded } = useUser();

  const hasGitHub = user?.externalAccounts?.some(account => account.provider === 'github');

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

  const handleConfirmPush = async () => {
    await confirmPush();
    toast.success("Push confirmed! Deployment pipeline is resuming.", {
      description: "Your changes are being pushed to GitHub now.",
    });
  };

  const handleCancelPush = async () => {
    await cancelPush();
    toast.warning("Push cancelled.", {
      description: "Resolve the security findings and re-deploy to proceed.",
    });
  };

  return (
    <DashboardLayout>
      {/* ── Security Push Confirmation Modal ── */}
      {awaitingPushConfirmation && securityReport && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="sec-confirm-title"
        >
          <div className="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-amber-200 dark:border-amber-800/50 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            {/* Header */}
            <div className="flex items-start gap-4 bg-amber-50 dark:bg-amber-900/20 px-6 py-5 border-b border-amber-100 dark:border-amber-800/40">
              <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center flex-shrink-0">
                <ShieldAlert className="w-5 h-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h2 id="sec-confirm-title" className="text-base font-extrabold text-amber-800 dark:text-amber-300">
                  Security Findings Detected
                </h2>
                <p className="text-xs text-amber-700/80 dark:text-amber-400/80 mt-0.5 leading-relaxed">
                  The security scanner found <strong>{securityReport.findings?.length ?? 0} issue(s)</strong> in your
                  repository. Do you still want to push the deployment files to GitHub?
                </p>
              </div>
              <button
                onClick={handleCancelPush}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors flex-shrink-0 mt-0.5"
                aria-label="Cancel push"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Findings preview (top 3) */}
            {securityReport.findings && securityReport.findings.length > 0 && (
              <div className="px-6 py-4 space-y-2 border-b border-slate-100 dark:border-slate-800 max-h-52 overflow-y-auto">
                <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-2">
                  Top findings
                </p>
                {securityReport.findings.slice(0, 3).map((f: any, i: number) => (
                  <div
                    key={i}
                    className={`flex items-start gap-2 px-3 py-2 rounded-lg border text-xs ${
                      f.severity === "CRITICAL"
                        ? "bg-red-50 border-red-200 dark:bg-red-900/10 dark:border-red-800/40"
                        : f.severity === "HIGH"
                          ? "bg-orange-50 border-orange-200 dark:bg-orange-900/10 dark:border-orange-800/40"
                          : "bg-amber-50 border-amber-200 dark:bg-amber-900/10 dark:border-amber-800/40"
                    }`}
                  >
                    <ShieldX
                      className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${
                        f.severity === "CRITICAL" ? "text-red-500" : f.severity === "HIGH" ? "text-orange-500" : "text-amber-500"
                      }`}
                    />
                    <div className="min-w-0">
                      <span
                        className={`inline-block text-[9px] font-black uppercase tracking-wider px-1.5 py-0 rounded border mr-1.5 ${
                          f.severity === "CRITICAL"
                            ? "bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400"
                            : f.severity === "HIGH"
                              ? "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400"
                              : "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400"
                        }`}
                      >
                        {f.severity}
                      </span>
                      <span className="font-semibold text-slate-700 dark:text-slate-300">{f.description}</span>
                      <p className="text-[10px] font-mono text-slate-500 dark:text-slate-400 truncate mt-0.5">
                        {f.file_path}{f.line_number > 0 ? ` : line ${f.line_number}` : ""}
                      </p>
                    </div>
                  </div>
                ))}
                {securityReport.findings.length > 3 && (
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 text-center pt-1">
                    + {securityReport.findings.length - 3} more issue(s) — see the Security Report below
                  </p>
                )}
              </div>
            )}

            {/* Action buttons */}
            <div className="flex items-center justify-end gap-3 px-6 py-4 bg-slate-50 dark:bg-slate-900/60">
              <Button
                id="cancel-push-btn"
                variant="outline"
                onClick={handleCancelPush}
                className="border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                Cancel Push
              </Button>
              <Button
                id="confirm-push-btn"
                onClick={handleConfirmPush}
                className="bg-amber-500 hover:bg-amber-600 text-white flex items-center gap-2 shadow-sm"
              >
                <GithubIcon className="w-4 h-4" />
                Proceed with Push
              </Button>
            </div>
          </div>
        </div>
      )}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 max-w-7xl">
        {/* Welcome Section */}
        <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-4 sm:p-6 mb-6 shadow-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start sm:items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0 border border-blue-100 dark:border-blue-800">
                <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="min-w-0 flex-1">
                <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  Welcome, {user?.firstName || "Developer"}
                </h1>
                <p className="text-slate-500 dark:text-slate-400 text-sm sm:text-base">Deploy your applications with AI-powered automation</p>
              </div>
            </div>

            {isLoaded && !hasGitHub && (
              <Button 
                onClick={connectGitHub}
                className="bg-[#24292F] hover:bg-[#24292F]/90 text-white flex items-center gap-2 transition-all shadow-sm"
              >
                <Github className="w-4 h-4" />
                <span>Connect GitHub</span>
                <ExternalLink className="w-3 h-3 opacity-50" />
              </Button>
            )}

            {isLoaded && hasGitHub && (
              <div className="flex items-center gap-2 bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800 px-3 py-1.5 rounded-full">
                <Github className="w-4 h-4 text-green-600 dark:text-green-400" />
                <span className="text-xs font-semibold text-green-600 dark:text-green-400">GitHub Linked</span>
              </div>
            )}
          </div>
        </Card>

        {!hasGitHub && isLoaded && (
          <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800 rounded-xl flex items-center gap-3 shadow-sm">
            <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-500 flex-shrink-0" />
            <p className="text-sm text-amber-800 dark:text-amber-200">
              <span className="font-bold text-amber-700 dark:text-amber-400">Note:</span> Please connect your GitHub account to enable automated deployment and repository discovery.
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
            <Card className="lg:col-span-1 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-4 sm:p-6 flex flex-col h-[500px] shadow-sm">
              <div className="flex items-center justify-between mb-6 border-b border-slate-100 dark:border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">Deployment Status</h3>
                </div>
                {estimatedDuration && (
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Est. Time</span>
                    <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">{estimatedDuration}</span>
                  </div>
                )}
              </div>
              <div className="flex-1 overflow-y-auto">
                <ProgressTimeline steps={steps} />
              </div>
            </Card>
          </div>

          {/* 2b. Security Report Card — visible whenever a scan result arrives */}
          {securityReport && (
            <SecurityReportCard report={securityReport} />
          )}

          {/* 3. Recent Deployments Table */}
          <div className="pt-4">
            <DeploymentsTable />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
