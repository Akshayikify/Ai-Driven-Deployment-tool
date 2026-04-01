import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { Activity, CheckCircle, XCircle, Clock, TrendingUp } from "lucide-react";

interface Stats {
  success: number;
  failed: number;
  running: number;
  total: number;
}

export default function DeploymentAnalytics() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/analyze/stats");
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
  }, []);

  if (loading && !stats) {
    return (
      <Card className="bg-slate-800/50 border-slate-700 p-8 h-[300px] flex items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <Activity className="w-8 h-8 text-neon-cyan animate-pulse" />
          <p className="text-slate-400 text-sm">Loading analytics...</p>
        </div>
      </Card>
    );
  }

  const chartData = [
    { name: "Successful", value: stats?.success || 0, color: "#10b981" },
    { name: "Failed", value: stats?.failed || 0, color: "#ef4444" },
    { name: "Running", value: stats?.running || 0, color: "#3b82f6" },
  ];

  const successRate = stats?.total 
    ? Math.round((stats.success / stats.total) * 100) 
    : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      {/* 1. Quick Stats */}
      <Card className="bg-slate-800/50 border-slate-700 p-6 flex flex-col justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-neon-cyan" />
            Performance Overview
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-slate-300 text-sm">Success Rate</span>
              </div>
              <span className="text-xl font-bold text-white">{successRate}%</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50">
              <div className="flex items-center gap-3">
                <XCircle className="w-4 h-4 text-red-400" />
                <span className="text-slate-300 text-sm">Failure Count</span>
              </div>
              <span className="text-xl font-bold text-white">{stats?.failed}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50">
              <div className="flex items-center gap-3">
                <Clock className="w-4 h-4 text-blue-400" />
                <span className="text-slate-300 text-sm">Active Now</span>
              </div>
              <span className="text-xl font-bold text-white">{stats?.running}</span>
            </div>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-slate-700">
           <p className="text-[10px] text-slate-500 uppercase tracking-widest text-center">
             Synced with MongoDB Atlas
           </p>
        </div>
      </Card>

      {/* 2. Success Ratio Donut Chart */}
      <Card className="bg-slate-800/50 border-slate-700 p-6 lg:col-span-2">
        <h3 className="text-lg font-semibold text-white mb-4">Deployment Distribution</h3>
        <div className="h-[200px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#fff' }}
                itemStyle={{ color: '#fff' }}
              />
              <Legend verticalAlign="middle" align="right" layout="vertical" />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
