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
import { useAuth } from "@clerk/clerk-react";
import { cn } from "@/lib/utils";

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
        className: "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30",
        iconColor: "text-green-600 dark:text-green-500",
      };
    case "failed":
      return {
        icon: XCircle,
        label: "Failed",
        className: "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30",
        iconColor: "text-red-600 dark:text-red-500",
      };
    case "running":
      return {
        icon: Clock,
        label: "Running",
        className: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-900/30",
        iconColor: "text-blue-600 dark:text-blue-500",
      };
    case "pending":
    default:
      return {
        icon: AlertCircle,
        label: "Pending",
        className: "bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-800/50 dark:text-slate-400 dark:border-slate-800",
        iconColor: "text-slate-500 dark:text-slate-400",
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
  const { userId } = useAuth();
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDeployments = async () => {
    if (!userId) return;
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/analyze/tasks?user_id=${userId}`);
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
    
    const hasActiveTasks = deployments.some(d => d.status === "running" || d.status === "pending");
    const intervalTime = hasActiveTasks ? 10000 : 60000;
    
    const interval = setInterval(fetchDeployments, intervalTime);
    return () => clearInterval(interval);
  }, [userId, deployments.length, deployments.some(d => d.status === "running" || d.status === "pending")]);

  if (loading && deployments.length === 0) {
    return (
      <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-12 flex items-center justify-center shadow-sm">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
          <p className="text-slate-500 dark:text-slate-400 text-sm font-bold uppercase tracking-wider">Syncing Deployments...</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-extrabold text-slate-900 dark:text-white tracking-tight">
              Recent Deployments
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Tracking your latest repository activities</p>
          </div>
          <button 
            onClick={fetchDeployments}
            className="p-2.5 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-700 transition-all group"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 text-slate-500 group-hover:text-blue-600 transition-colors ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-100 dark:border-slate-800 hover:bg-transparent">
                <TableHead className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Deployment</TableHead>
                <TableHead className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Status</TableHead>
                <TableHead className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Environment</TableHead>
                <TableHead className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Duration</TableHead>
                <TableHead className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Commit</TableHead>
                <TableHead className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right">Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {deployments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12 text-slate-400 font-medium">
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
                      className="border-slate-50 dark:border-slate-800 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
                    >
                      <TableCell className="py-4">
                        <div className="flex flex-col">
                          <span className="text-sm font-bold text-slate-900 dark:text-white">
                            {getRepoName(deployment.repo_url)}
                          </span>
                          {deployment.current_message && (
                            <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium truncate max-w-[180px] mt-0.5">
                              {deployment.current_message}
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className={cn(
                          "inline-flex items-center gap-2 px-2.5 py-1 rounded-full border text-[10px] font-black uppercase tracking-tighter shadow-sm",
                          statusConfig.className
                        )}>
                          <StatusIcon className={cn("w-3.5 h-3.5", statusConfig.iconColor)} />
                          {statusConfig.label}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-xs font-bold text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded-md border border-slate-100 dark:border-slate-700">
                          {deployment.environment}
                        </span>
                      </TableCell>
                      <TableCell className="text-slate-600 dark:text-slate-400 text-xs font-bold">
                        {deployment.duration}
                      </TableCell>
                      <TableCell>
                        {deployment.commit !== "N/A" ? (
                           <code className="text-[10px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded border border-blue-100 dark:border-blue-900/30">
                             {deployment.commit}
                           </code>
                        ) : (
                          <span className="text-slate-400 text-[10px] font-bold">N/A</span>
                        )}
                      </TableCell>
                      <TableCell className="text-slate-500 dark:text-slate-400 text-xs font-medium text-right">
                        {(() => {
                          if (!deployment.created_at) return "-";
                          try {
                            const date = new Date(deployment.created_at);
                            if (isNaN(date.getTime())) return "Recent";
                            return formatDistanceToNow(date, { addSuffix: true });
                          } catch (e) {
                            return "Recent";
                          }
                        })()}
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
