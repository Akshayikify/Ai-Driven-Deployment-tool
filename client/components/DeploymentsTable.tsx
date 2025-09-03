import React from "react";
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
import { CheckCircle, XCircle, Clock, AlertCircle } from "lucide-react";

interface Deployment {
  id: string;
  name: string;
  status: "success" | "failed" | "pending" | "running";
  timestamp: string;
  duration: string;
  commit: string;
  environment: string;
}

const mockDeployments: Deployment[] = [
  {
    id: "1",
    name: "frontend-v2.1.0",
    status: "success",
    timestamp: "2024-01-15 14:30:00",
    duration: "2m 34s",
    commit: "a1b2c3d",
    environment: "production",
  },
  {
    id: "2",
    name: "api-hotfix-urgent",
    status: "failed",
    timestamp: "2024-01-15 12:15:00",
    duration: "1m 12s",
    commit: "e4f5g6h",
    environment: "staging",
  },
  {
    id: "3",
    name: "backend-v1.8.2",
    status: "running",
    timestamp: "2024-01-15 10:45:00",
    duration: "45s",
    commit: "i7j8k9l",
    environment: "production",
  },
  {
    id: "4",
    name: "mobile-app-v3.0.0",
    status: "pending",
    timestamp: "2024-01-15 09:20:00",
    duration: "-",
    commit: "m0n1o2p",
    environment: "development",
  },
  {
    id: "5",
    name: "docs-update",
    status: "success",
    timestamp: "2024-01-14 16:00:00",
    duration: "1m 8s",
    commit: "q3r4s5t",
    environment: "production",
  },
];

const getStatusConfig = (status: Deployment["status"]) => {
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
      return {
        icon: AlertCircle,
        label: "Pending",
        className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
      };
  }
};

interface DeploymentsTableProps {
  className?: string;
}

export default function DeploymentsTable({ className }: DeploymentsTableProps) {
  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Recent Deployments
        </h3>

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
              {mockDeployments.map((deployment) => {
                const statusConfig = getStatusConfig(deployment.status);
                const StatusIcon = statusConfig.icon;

                return (
                  <TableRow
                    key={deployment.id}
                    className="border-slate-700 hover:bg-slate-800/30"
                  >
                    <TableCell className="text-white font-medium">
                      {deployment.name}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <StatusIcon className="w-4 h-4" />
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium border ${statusConfig.className}`}
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
                      <code className="text-xs text-slate-400 bg-slate-900/50 px-2 py-1 rounded">
                        {deployment.commit}
                      </code>
                    </TableCell>
                    <TableCell className="text-slate-400 text-sm">
                      {deployment.timestamp}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </div>
    </Card>
  );
}
