import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { 
  Users, 
  Server, 
  TrendingUp, 
  Activity, 
  LogOut, 
  CheckCircle, 
  XCircle, 
  Clock,
  ExternalLink,
  Search,
  Loader2
} from "lucide-react";
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
  CartesianGrid
} from "recharts";
import { toast } from "sonner";

interface AdminStats {
  total_users: number;
  total_deployments: number;
  success_rate: number;
  failed_rate: number;
  running_deployments: number;
}

interface UserData {
  clerk_id: string;
  email: string;
  first_name: string;
  last_name: string;
  profile_image_url: string;
  created_at: string;
  last_active_at: string;
}

interface DeploymentData {
  id: string;
  user_id: string;
  status: string;
  repo_url: string;
  language: string;
  start_time: string;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<UserData[]>([]);
  const [deployments, setDeployments] = useState<DeploymentData[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      navigate("/admin/login");
      return;
    }

    const fetchData = async () => {
      try {
        const headers = { Authorization: `Bearer ${token}` };
        
        const [statsRes, usersRes, depsRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/v1/admin/stats", { headers }),
          fetch("http://127.0.0.1:8000/api/v1/admin/users", { headers }),
          fetch("http://127.0.0.1:8000/api/v1/admin/deployments", { headers })
        ]);

        if (statsRes.status === 401) {
          localStorage.removeItem("admin_token");
          navigate("/admin/login");
          return;
        }

        const statsData = await statsRes.json();
        const usersData = await usersRes.json();
        const depsData = await depsRes.json();

        setStats(statsData);
        setUsers(usersData);
        setDeployments(depsData);
      } catch (error) {
        console.error("Failed to fetch admin data:", error);
        toast.error("Error loading dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    document.title = "Admin Dashboard | Auto Deploy.AI";
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    toast.success("Logged out successfully");
    navigate("/admin/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Activity className="w-12 h-12 text-neon-blue animate-spin" />
          <p className="text-slate-400 font-mono">Initializing Admin Console...</p>
        </div>
      </div>
    );
  }

  const chartData = [
    { name: "Successful", value: Number(stats?.success_rate) || 0, color: "#0ea5e9" }, // Sky Blue
    { name: "Failed", value: Number(stats?.failed_rate) || 0, color: "#f43f5e" },    // Rose
    { name: "Running", value: Number(stats?.running_deployments) || 0, color: "#a855f7" }, // Purple
  ];

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200">
      {/* Sidebar/Header */}
      <nav className="bg-slate-900/50 border-b border-slate-800 p-4 sticky top-0 z-50 backdrop-blur-md">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-neon-blue to-neon-purple rounded-lg flex items-center justify-center shadow-lg shadow-neon-blue/20">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">Admin Dashboard</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Auto Deploy Control Center</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-red-500/10 hover:text-red-400 border border-slate-700 hover:border-red-500/50 rounded-lg transition-all text-sm font-medium"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard title="Total Users" value={stats?.total_users ?? 0} icon={<Users className="text-neon-blue" />} />
          <StatCard title="Total Deployments" value={stats?.total_deployments ?? 0} icon={<Server className="text-neon-purple" />} />
          <StatCard title="Success Rate" value={`${stats?.success_rate ?? 0}%`} icon={<CheckCircle className="text-green-400" />} />
          <StatCard title="Active Processes" value={stats?.running_deployments ?? 0} icon={<Clock className="text-blue-400" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Distribution Chart */}
          <Card className="lg:col-span-2 bg-slate-900/50 border-slate-800 p-6">
            <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
              <Activity className="w-5 h-5 text-neon-blue" />
              Global Deployment Distribution (%)
            </h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={100}
                    paddingAngle={8}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                      border: '1px solid rgba(51, 65, 85, 0.5)', 
                      borderRadius: '12px',
                      backdropFilter: 'blur(8px)',
                      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
                      padding: '12px'
                    }}
                    itemStyle={{ color: '#e2e8f0', fontSize: '14px', fontWeight: '500' }}
                    labelStyle={{ color: '#94a3b8', marginBottom: '4px', fontSize: '12px', fontWeight: '600', textTransform: 'uppercase' }}
                    cursor={{ stroke: '#334155', strokeWidth: 2 }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    iconType="circle"
                    formatter={(value) => <span className="text-slate-400 text-xs font-medium ml-1">{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* User Overview */}
          <Card className="bg-slate-900/50 border-slate-800 p-6">
            <h3 className="text-lg font-semibold text-white mb-6 flex items-center justify-between">
              Recent Users
              <Users className="w-5 h-5 text-slate-500" />
            </h3>
            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
              {Array.isArray(users) && users.slice(0, 5).map((user) => (
                <div key={user.clerk_id || Math.random().toString()} className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/30 border border-slate-800/50 hover:border-slate-700 transition-colors">
                  <img src={user.profile_image_url || "/placeholder-avatar.png"} alt="" className="w-10 h-10 rounded-full border border-slate-700" />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-white truncate">{(user.first_name || "") + " " + (user.last_name || "")}</p>
                    <p className="text-xs text-slate-500 truncate">{user.email || "No email"}</p>
                  </div>
                </div>
              ))}
              {(!Array.isArray(users) || users.length === 0) && (
                <p className="text-center text-slate-500 text-sm py-8">No users found</p>
              )}
            </div>
          </Card>
        </div>

        {/* Global Deployments Table */}
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Server className="w-5 h-5 text-neon-purple" />
              Global Deployment Activity
            </h3>
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
              <input 
                type="text" 
                placeholder="Search deployments..." 
                className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm focus:border-neon-blue outline-none transition-all"
              />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="pb-4 font-semibold text-slate-400 text-sm">USER ID</th>
                  <th className="pb-4 font-semibold text-slate-400 text-sm">PROJECT / REPO</th>
                  <th className="pb-4 font-semibold text-slate-400 text-sm">LANGUAGE</th>
                  <th className="pb-4 font-semibold text-slate-400 text-sm">STATUS</th>
                  <th className="pb-4 font-semibold text-slate-400 text-sm">DATE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {Array.isArray(deployments) && deployments.map((dep) => (
                  <tr key={dep.id} className="group hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 text-xs font-mono text-slate-500">{(dep.user_id || "unknown").slice(0, 8)}...</td>
                    <td className="py-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-white truncate max-w-[200px]">{dep.repo_url ? dep.repo_url.split('/').pop() : "unknown"}</span>
                        <ExternalLink className="w-3 h-3 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </td>
                    <td className="py-4">
                      {dep.language ? (
                        <span className="px-2 py-1 rounded bg-slate-800 text-[10px] font-bold text-slate-400 uppercase">
                          {dep.language}
                        </span>
                      ) : dep.status === "running" ? (
                        <div className="flex items-center gap-1.5 text-neon-cyan animate-pulse">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          <span className="text-[10px] font-bold uppercase tracking-tight">Detecting...</span>
                        </div>
                      ) : (
                        <span className="text-[10px] font-bold text-slate-600 uppercase">N/A</span>
                      )}
                    </td>
                    <td className="py-4">
                      <StatusBadge status={dep.status || "unknown"} />
                    </td>
                    <td className="py-4 text-sm text-slate-500">
                      {dep.start_time ? new Date(dep.start_time).toLocaleDateString() : "N/A"}
                    </td>
                  </tr>
                ))}
                {(!Array.isArray(deployments) || deployments.length === 0) && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-500 text-sm">No deployments found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </main>
    </div>
  );
}

function StatCard({ title, value, icon }: { title: string, value: any, icon: React.ReactNode }) {
  return (
    <Card className="bg-slate-900/50 border-slate-800 p-6 group hover:border-slate-700 transition-all">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-medium text-slate-400">{title}</p>
        <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center group-hover:scale-110 transition-transform">
          {icon}
        </div>
      </div>
      <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
    </Card>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: any = {
    success: "bg-green-500/10 text-green-400 border-green-500/20",
    failed: "bg-red-500/10 text-red-400 border-red-500/20",
    running: "bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse",
  };

  return (
    <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase border ${styles[status] || "bg-slate-800 text-slate-400"}`}>
      {status}
    </span>
  );
}
