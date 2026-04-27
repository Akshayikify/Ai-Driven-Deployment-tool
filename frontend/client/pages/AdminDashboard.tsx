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
  Loader2,
  ShieldCheck,
  LayoutDashboard
} from "lucide-react";
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip, 
  Legend
} from "recharts";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

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
    document.title = "Admin Console | AutoDeploy.ai";
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    toast.success("Logged out successfully");
    navigate("/admin/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
          <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">Loading Console...</p>
        </div>
      </div>
    );
  }

  const chartData = [
    { name: "Successful", value: Number(stats?.success_rate) || 0, color: "#10b981" }, // Green
    { name: "Failed", value: Number(stats?.failed_rate) || 0, color: "#ef4444" },    // Red
    { name: "Running", value: Number(stats?.running_deployments) || 0, color: "#3b82f6" }, // Blue
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Sidebar/Header */}
      <nav className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 p-4 sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-md">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-black text-slate-900 dark:text-white tracking-tight">Admin Console</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Infrastructure Control</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 font-bold text-xs uppercase tracking-wider transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-10 max-w-7xl">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <StatCard title="Total Platform Users" value={stats?.total_users ?? 0} icon={<Users className="w-5 h-5 text-blue-600" />} />
          <StatCard title="Global Deployments" value={stats?.total_deployments ?? 0} icon={<Server className="w-5 h-5 text-indigo-600" />} />
          <StatCard title="Overall Success" value={`${stats?.success_rate ?? 0}%`} icon={<CheckCircle className="w-5 h-5 text-green-600" />} />
          <StatCard title="Active Jobs" value={stats?.running_deployments ?? 0} icon={<Activity className="w-5 h-5 text-orange-600" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
          {/* Distribution Chart */}
          <Card className="lg:col-span-2 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-8 shadow-sm">
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest flex items-center gap-3">
                <LayoutDashboard className="w-4 h-4 text-blue-600" />
                Performance Distribution
              </h3>
            </div>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={85}
                    outerRadius={110}
                    paddingAngle={5}
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
                      padding: '12px',
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                    }}
                    itemStyle={{ color: '#1e293b', fontSize: '12px', fontWeight: 'bold' }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    iconType="circle"
                    formatter={(value) => <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider ml-1">{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* User Overview */}
          <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-8 shadow-sm">
            <h3 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest mb-8 flex items-center justify-between">
              Recent Signups
              <Users className="w-4 h-4 text-slate-400" />
            </h3>
            <div className="space-y-5 max-h-[320px] overflow-y-auto pr-2">
              {Array.isArray(users) && users.slice(0, 5).map((user) => (
                <div key={user.clerk_id || Math.random().toString()} className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 transition-colors">
                  <img src={user.profile_image_url || "/placeholder-avatar.png"} alt="" className="w-10 h-10 rounded-full border-2 border-white dark:border-slate-700 shadow-sm" />
                  <div className="min-w-0">
                    <p className="text-sm font-bold text-slate-900 dark:text-white truncate">{(user.first_name || "") + " " + (user.last_name || "")}</p>
                    <p className="text-[11px] text-slate-500 truncate font-medium">{user.email || "No email"}</p>
                  </div>
                </div>
              ))}
              {(!Array.isArray(users) || users.length === 0) && (
                <div className="flex flex-col items-center justify-center py-12">
                   <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">No users found</p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Global Deployments Table */}
        <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          <div className="p-8 border-b border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
            <div>
              <h3 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest flex items-center gap-3">
                <Activity className="w-4 h-4 text-blue-600" />
                Live Deployment Stream
              </h3>
            </div>
            <div className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search across all projects..." 
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
              />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/50">
                  <th className="px-8 py-4 font-bold text-slate-500 dark:text-slate-400 text-[11px] uppercase tracking-wider">User Identifier</th>
                  <th className="px-8 py-4 font-bold text-slate-500 dark:text-slate-400 text-[11px] uppercase tracking-wider">Repository / Project</th>
                  <th className="px-8 py-4 font-bold text-slate-500 dark:text-slate-400 text-[11px] uppercase tracking-wider text-center">Stack</th>
                  <th className="px-8 py-4 font-bold text-slate-500 dark:text-slate-400 text-[11px] uppercase tracking-wider">Status</th>
                  <th className="px-8 py-4 font-bold text-slate-500 dark:text-slate-400 text-[11px] uppercase tracking-wider text-right">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {Array.isArray(deployments) && deployments.map((dep) => (
                  <tr key={dep.id} className="group hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-8 py-5 text-xs font-bold text-slate-500 dark:text-slate-400 font-mono">{(dep.user_id || "unknown").slice(0, 12)}...</td>
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-bold text-slate-900 dark:text-white truncate max-w-[200px]">{dep.repo_url ? dep.repo_url.split('/').pop() : "unknown"}</span>
                        <ExternalLink className="w-3.5 h-3.5 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </td>
                    <td className="px-8 py-5 text-center">
                      {dep.language ? (
                        <span className="px-2.5 py-1 rounded-md bg-blue-50 dark:bg-blue-900/20 text-[10px] font-black text-blue-700 dark:text-blue-400 border border-blue-100 dark:border-blue-900/30 uppercase">
                          {dep.language}
                        </span>
                      ) : dep.status === "running" ? (
                        <div className="flex items-center justify-center gap-2 text-blue-600 animate-pulse">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          <span className="text-[10px] font-black uppercase">Analyzing</span>
                        </div>
                      ) : (
                        <span className="text-[10px] font-bold text-slate-400 uppercase">N/A</span>
                      )}
                    </td>
                    <td className="px-8 py-5">
                      <StatusBadge status={dep.status || "unknown"} />
                    </td>
                    <td className="px-8 py-5 text-xs font-bold text-slate-500 dark:text-slate-400 text-right">
                      {dep.start_time ? new Date(dep.start_time).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : "N/A"}
                    </td>
                  </tr>
                ))}
                {(!Array.isArray(deployments) || deployments.length === 0) && (
                  <tr>
                    <td colSpan={5} className="px-8 py-16 text-center text-slate-400 text-xs font-bold uppercase tracking-widest">No deployment activity found</td>
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
    <Card className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 p-6 shadow-sm group hover:border-blue-200 dark:hover:border-blue-900 transition-all">
      <div className="flex items-center justify-between mb-6">
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 group-hover:bg-blue-600 group-hover:border-blue-600 transition-all group-hover:scale-110">
          <div className="group-hover:text-white transition-colors">
            {icon}
          </div>
        </div>
        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{title}</p>
      </div>
      <p className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">{value}</p>
    </Card>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: any = {
    success: "bg-green-50 text-green-700 border-green-100 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30",
    failed: "bg-red-50 text-red-700 border-red-100 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30",
    running: "bg-blue-50 text-blue-700 border-blue-100 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-900/30 animate-pulse",
  };

  return (
    <span className={cn(
      "px-2.5 py-1 rounded-full text-[10px] font-black uppercase border shadow-sm",
      styles[status] || "bg-slate-100 text-slate-500 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-800"
    )}>
      {status}
    </span>
  );
}
