import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, Clock, AlertCircle, RefreshCw } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface Deployment {
  id: string;
  repo_url: string;
  status: "success" | "failed" | "pending" | "running";
  created_at: string;
  duration: string;
  commit: string;
  environment: string;
  current_message?: string;
}

const getStatusConfig = (status: string) => {
  switch (status) {
    case "success":
      return {
        icon: CheckCircle,
        label: "Success",
        className: "bg-green-500/20 text-green-400 border-green-500/30",
      };
    case "failed":
      return {
        icon: XCircle,
        label: "Failed",
        className: "bg-red-500/20 text-red-400 border-red-500/30",
      };
    case "running":
      return {
        icon: Clock,
        label: "Running",
        className: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      };
    case "pending":
    default:
      return {
        icon: AlertCircle,
        label: "Pending",
        className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
      };
  }
};

const getRepoName = (url: string) => {
  if (!url) return "Unknown";
  const cleanUrl = url.replace(".git", "");
  const parts = cleanUrl.split("/");
  return parts[parts.length - 1] || url;
};

interface DeploymentsTableProps {
  className?: string;
}

export default function DeploymentsTable({ className }: DeploymentsTableProps) {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDeployments = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/analyze/tasks");
      if (response.ok) {
        const data = await response.json();
        setDeployments(data);
      }
    } catch (error) {
      console.error("Failed to fetch deployments:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeployments();
    
    // Poll for updates intelligently
    // Every 60 seconds if everything is finished, every 10 seconds if something is running
    const hasActiveTasks = deployments.some(d => d.status === "running" || d.status === "pending");
    const intervalTime = hasActiveTasks ? 10000 : 60000;
    
    const interval = setInterval(fetchDeployments, intervalTime);
    return () => clearInterval(interval);
  }, [deployments.length, deployments.some(d => d.status === "running" || d.status === "pending")]);

  if (loading && deployments.length === 0) {
    return (
      <Card className="bg-slate-800/50 border-slate-700 p-8 flex items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <RefreshCw className="w-8 h-8 text-neon-cyan animate-spin" />
          <p className="text-slate-400 text-sm">Loading deployments...</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">
            Recent Deployments
          </h3>
          <button 
            onClick={fetchDeployments}
            className="p-2 hover:bg-slate-700 rounded-full transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 text-slate-400 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-700 hover:bg-slate-800/50">
                <TableHead className="text-slate-300">Deployment</TableHead>
                <TableHead className="text-slate-300">Status</TableHead>
                <TableHead className="text-slate-300">Environment</TableHead>
                <TableHead className="text-slate-300">Duration</TableHead>
                <TableHead className="text-slate-300">Commit</TableHead>
                <TableHead className="text-slate-300">Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {deployments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-slate-500">
                    No recent deployments found.
                  </TableCell>
                </TableRow>
              ) : (
                deployments.map((deployment) => {
                  const statusConfig = getStatusConfig(deployment.status);
                  const StatusIcon = statusConfig.icon;

                  return (
                    <TableRow
                      key={deployment.id}
                      className="border-slate-700 hover:bg-slate-800/30"
                    >
                      <TableCell className="text-white font-medium">
                        <div className="flex flex-col">
                          <span>{getRepoName(deployment.repo_url)}</span>
                          {deployment.current_message && (
                            <span className="text-[10px] text-slate-400 font-normal truncate max-w-[200px]">
                              {deployment.current_message}
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <StatusIcon className="w-4 h-4" />
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${statusConfig.className}`}
                          >
                            {statusConfig.label}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-slate-300 text-sm">
                          {deployment.environment}
                        </span>
                      </TableCell>
                      <TableCell className="text-slate-300 text-sm">
                        {deployment.duration}
                      </TableCell>
                      <TableCell>
                        {deployment.commit !== "N/A" ? (
                           <code className="text-[10px] text-slate-400 bg-slate-900/50 px-2 py-1 rounded">
                             {deployment.commit}
                           </code>
                        ) : (
                          <span className="text-slate-500 text-xs">N/A</span>
                        )}
                      </TableCell>
                      <TableCell className="text-slate-400 text-sm">
                        {deployment.created_at ? formatDistanceToNow(new Date(deployment.created_at), { addSuffix: true }) : "-"}
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </Card>
  );
}
