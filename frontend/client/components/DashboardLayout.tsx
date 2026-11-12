import React from "react";
import DashboardHeader from "@/components/DashboardHeader";
import Footer from "@/components/Footer";
import { useDeployment } from "@/context/DeploymentContext";
import { ExternalLink } from "lucide-react";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const { deploymentUrl } = useDeployment();

  return (
    <div className="min-h-screen bg-black">
      {/* Dashboard Header */}
      <div className="relative flex-shrink-0">
        <DashboardHeader />
        {/* Dashboard Title Bar */}
        <div
          className="h-16 border-b border-slate-800/50 bg-slate-900/50 backdrop-blur-xl flex items-center px-4 sm:px-6"
          style={{ marginTop: "80px" }}
        >
          <div className="flex items-center justify-between w-full">
            <h1 className="text-lg sm:text-xl font-semibold text-white truncate">
              AI-Powered Dashboard
            </h1>
            <div className="flex items-center gap-2 sm:gap-3">
              {deploymentUrl && (
                <a
                  href={deploymentUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-3 py-1 bg-green-500/20 text-green-400 border border-green-500/40 hover:bg-green-500/30 rounded-full text-xs font-semibold transition-all hover:scale-105"
                  title="Open live deployed application in new tab"
                >
                  <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                  <span className="hidden sm:inline">Live App:</span>
                  <span className="font-mono text-[11px] underline truncate max-w-[150px] sm:max-w-[200px]">{deploymentUrl}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              <div className="px-2 sm:px-3 py-1 bg-neon-blue/20 text-neon-cyan border border-neon-blue/30 rounded-full text-xs font-semibold">
                Live Mode
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto min-h-0">
        {children}
        <Footer />
      </main>
    </div>
  );
}
