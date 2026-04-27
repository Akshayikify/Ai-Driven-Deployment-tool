import { useState } from "react";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Terminal, BrainCircuit, CheckCircle2, AlertCircle, Zap } from "lucide-react";

export default function DashboardSection() {
  const [activeTab, setActiveTab] = useState(0);

  const dashboardViews = [
    {
      title: "Pipeline Overview",
      description: "Manage and monitor your entire deployment lifecycle from a single, unified interface.",
      icon: <Activity className="w-5 h-5" />,
      features: [
        "Real-time deployment tracking",
        "Automated failure rollbacks",
        "Multi-environment synchronization",
      ],
    },
    {
      title: "Intelligent Logs",
      description: "Smart log aggregation with AI-powered error surfacing and contextual analysis.",
      icon: <Terminal className="w-5 h-5" />,
      features: [
        "Live streaming at scale",
        "Predictive error highlighting",
        "Contextual search & filtering",
      ],
    },
    {
      title: "AI Optimization",
      description: "Receive proactive recommendations to improve performance and reduce costs.",
      icon: <BrainCircuit className="w-5 h-5" />,
      features: [
        "Auto-scaling predictions",
        "Resource allocation optimization",
        "Security vulnerability audits",
      ],
    },
  ];

  return (
    <section className="py-24 bg-white dark:bg-slate-950 border-b border-slate-100 dark:border-slate-900 overflow-hidden">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-sm font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-3">Intuitive Interface</h2>
          <h3 className="text-4xl md:text-5xl font-extrabold text-slate-900 dark:text-white mb-6 tracking-tight">
            Control center for your <span className="text-blue-600">infrastructure</span>
          </h3>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            A professional workspace designed for clarity, speed, and absolute control over 
            your production environments.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap justify-center mb-16 p-1.5 bg-slate-100 dark:bg-slate-900 rounded-2xl w-fit mx-auto border border-slate-200 dark:border-slate-800">
          {dashboardViews.map((view, index) => (
            <button
              key={index}
              onClick={() => setActiveTab(index)}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold transition-all ${
                activeTab === index
                  ? "bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 shadow-sm border border-slate-200 dark:border-slate-700"
                  : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
              }`}
            >
              {view.icon}
              {view.title}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Info Side */}
          <div className="order-2 lg:order-1">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <h3 className="text-3xl font-extrabold text-slate-900 dark:text-white mb-6">
                  {dashboardViews[activeTab].title}
                </h3>
                <p className="text-xl text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
                  {dashboardViews[activeTab].description}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {dashboardViews[activeTab].features.map((feature, i) => (
                    <div key={i} className="flex items-center gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800">
                      <CheckCircle2 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      <span className="text-sm font-bold text-slate-700 dark:text-slate-300">{feature}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Browser Mockup Side */}
          <div className="order-1 lg:order-2">
            <div className="bg-slate-200 dark:bg-slate-800 p-2 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-700">
              <div className="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden border border-slate-100 dark:border-slate-800 shadow-inner h-[400px]">
                {/* Browser Header */}
                <div className="bg-slate-50 dark:bg-slate-800 px-4 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center gap-4">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
                    <div className="w-3 h-3 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
                    <div className="w-3 h-3 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
                  </div>
                  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1 text-[10px] text-slate-400 font-mono w-full max-w-[200px]">
                    app.autodeploy.ai/dashboard
                  </div>
                </div>

                {/* Content View */}
                <div className="p-6 h-full overflow-y-auto">
                  {activeTab === 0 && (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">Active Deployments</h4>
                        <span className="px-2 py-1 rounded-full bg-green-100 text-green-700 text-[10px] font-bold">LIVE STATUS</span>
                      </div>
                      {[
                        { name: "Frontend Cluster", status: "Active", progress: 100, color: "bg-blue-600" },
                        { name: "Payments API", status: "Deploying", progress: 75, color: "bg-blue-500", animated: true },
                        { name: "Worker Service", status: "Queued", progress: 0, color: "bg-slate-200" },
                      ].map((item, i) => (
                        <div key={i} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700">
                          <div className="flex justify-between items-center mb-3">
                            <span className="text-xs font-bold text-slate-700 dark:text-slate-300">{item.name}</span>
                            <span className={`text-[10px] font-black uppercase ${item.status === 'Active' ? 'text-green-600' : 'text-blue-600'}`}>{item.status}</span>
                          </div>
                          <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                            <motion.div 
                              initial={{ width: 0 }}
                              animate={{ width: `${item.progress}%` }}
                              className={`h-full ${item.color} ${item.animated ? 'animate-pulse' : ''}`}
                            ></motion.div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {activeTab === 1 && (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">Stream Monitor</h4>
                        <div className="flex items-center gap-1.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping"></div>
                          <span className="text-[10px] font-black text-red-500 uppercase">LIVE</span>
                        </div>
                      </div>
                      <div className="bg-slate-950 rounded-xl p-4 font-mono text-[11px] leading-relaxed h-[250px] overflow-hidden border border-slate-800">
                        <p className="text-slate-500 mb-1">{"[09:42:12] INFO: Connecting to K8s cluster..."}</p>
                        <p className="text-blue-400 mb-1">{"[09:42:13] DEBUG: Pulling image version v2.4.1"}</p>
                        <p className="text-slate-500 mb-1">{"[09:42:15] INFO: Validating configuration maps"}</p>
                        <p className="text-green-400 mb-1">{"[09:42:16] SUCCESS: Service mesh integration verified"}</p>
                        <p className="text-amber-400 mb-1">{"[09:42:18] WARNING: Memory pressure high in node-02"}</p>
                        <p className="text-blue-400 mb-1">{"[09:42:19] DEBUG: Auto-healing triggered"}</p>
                        <p className="text-slate-500 mb-1 italic">{"[09:42:20] AI_AGENT: Optimized memory limits for pod..."}</p>
                        <p className="text-green-400 animate-pulse">{"[09:42:21] SUCCESS: New deployment healthy ✓"}</p>
                      </div>
                    </div>
                  )}

                  {activeTab === 2 && (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">AI Insight Engine</h4>
                        <Zap className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="space-y-3">
                        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800/30">
                          <div className="flex gap-3">
                            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                            <div>
                              <p className="text-xs font-bold text-blue-900 dark:text-blue-200 mb-1">Scaling Alert</p>
                              <p className="text-[11px] text-blue-700 dark:text-blue-400">Traffic predicted to spike by 300% in next hour. Increased cluster size by 2 nodes.</p>
                            </div>
                          </div>
                        </div>
                        <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700">
                          <div className="flex gap-3">
                            <BrainCircuit className="w-5 h-5 text-slate-400 mt-0.5" />
                            <div>
                              <p className="text-xs font-bold text-slate-900 dark:text-white mb-1">Cost Optimization</p>
                              <p className="text-[11px] text-slate-500 dark:text-slate-400">Identified 3 underutilized instances. Consolidating workloads could save $420/month.</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
