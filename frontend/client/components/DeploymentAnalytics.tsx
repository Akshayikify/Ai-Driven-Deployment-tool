import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { Activity, CheckCircle, XCircle, Clock, TrendingUp } from "lucide-react";
import { useAuth } from "@clerk/clerk-react";
import { cn } from "@/lib/utils";

interface Stats {
  success: number;
  failed: number;
  running: number;
  total: number;
}

export default function DeploymentAnalytics() {
  const { userId } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const fetchStats = async () => {
    if (!userId) return;
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${baseUrl}/api/v1/analyze/stats?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Failed to fetch deployment stats:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, [userId]);

  if (loading && !stats) {
    return (
      <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-8 h-[300px] flex items-center justify-center shadow-sm">
        <div className="flex flex-col items-center gap-3">
          <Activity className="w-8 h-8 text-blue-600 animate-pulse" />
          <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-widest">Loading Analytics...</p>
        </div>
      </Card>
    );
  }

  const chartData = [
    { name: "Successful", value: stats?.success || 0, color: "#10b981" }, // Emerald-500
    { name: "Failed", value: stats?.failed || 0, color: "#ef4444" },     // Red-500
    { name: "Running", value: stats?.running || 0, color: "#3b82f6" },    // Blue-500
  ];

  const successRate = stats?.total 
    ? Math.round((stats.success / stats.total) * 100) 
    : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      {/* 1. Quick Stats */}
      <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-8 flex flex-col justify-between shadow-sm">
        <div>
          <h3 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest mb-8 flex items-center gap-3">
            <TrendingUp className="w-4 h-4 text-blue-600" />
            Performance
          </h3>
          <div className="space-y-4">
            <StatRow 
              icon={<CheckCircle className="w-4 h-4 text-green-500" />} 
              label="Success Rate" 
              value={`${successRate}%`} 
            />
            <StatRow 
              icon={<XCircle className="w-4 h-4 text-red-500" />} 
              label="Failures" 
              value={stats?.failed || 0} 
            />
            <StatRow 
              icon={<Clock className="w-4 h-4 text-blue-500" />} 
              label="Active Tasks" 
              value={stats?.running || 0} 
            />
          </div>
        </div>
        <div className="mt-8 pt-4 border-t border-slate-100 dark:border-slate-800">
           <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest text-center">
             Infrastructure Sync Active
           </p>
        </div>
      </Card>

      {/* 2. Success Ratio Donut Chart */}
      <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-8 lg:col-span-2 shadow-sm">
        <h3 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest mb-8">
          Deployment Distribution
        </h3>
        <div className="h-[240px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={90}
                paddingAngle={8}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #e2e8f0', 
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
                itemStyle={{ color: '#1e293b', fontSize: '12px', fontWeight: 'bold' }}
              />
              <Legend 
                verticalAlign="middle" 
                align="right" 
                layout="vertical"
                iconType="circle"
                formatter={(value) => <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider ml-2">{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}

function StatRow({ icon, label, value }: { icon: React.ReactNode, label: string, value: any }) {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
      <div className="flex items-center gap-3">
        {icon}
        <span className="text-slate-600 dark:text-slate-400 text-xs font-bold uppercase tracking-wide">{label}</span>
      </div>
      <span className="text-lg font-black text-slate-900 dark:text-white tracking-tight">{value}</span>
    </div>
  );
}
