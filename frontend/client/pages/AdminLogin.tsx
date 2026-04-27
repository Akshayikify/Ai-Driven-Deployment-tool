import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Lock, User, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

export default function AdminLogin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch("http://127.0.0.1:8000/api/v1/admin/login", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Invalid credentials");
      }

      const data = await response.json();
      localStorage.setItem("admin_token", data.access_token);
      toast.success("Admin login successful");
      navigate("/admin/dashboard");
    } catch (error) {
      toast.error("Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-neon-blue/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-neon-purple/10 rounded-full blur-[120px]" />
      </div>

      <Card className="w-full max-w-md bg-slate-900/50 border-slate-700 backdrop-blur-xl p-8 relative z-10 shadow-2xl">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-neon-blue to-neon-purple rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-neon-blue/20">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Admin Portal</h1>
          <p className="text-slate-400">Secure access for administrators only</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 ml-1">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <Input
                type="text"
                placeholder="Enter admin username"
                className="pl-10 bg-slate-800/50 border-slate-700 text-white focus:border-neon-blue transition-all"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <Input
                type="password"
                placeholder="Enter admin password"
                className="pl-10 bg-slate-800/50 border-slate-700 text-white focus:border-neon-blue transition-all"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full h-12 bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-blue/90 hover:to-neon-purple/90 text-white font-bold rounded-xl shadow-lg shadow-neon-blue/20 transition-all transform hover:scale-[1.02] active:scale-[0.98]"
          >
            {loading ? "Authenticating..." : "Login to Dashboard"}
          </Button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-800 text-center">
          <button 
            onClick={() => navigate("/")}
            className="text-slate-500 hover:text-slate-300 text-sm transition-colors"
          >
            &larr; Back to User Portal
          </button>
        </div>
      </Card>
    </div>
  );
}
