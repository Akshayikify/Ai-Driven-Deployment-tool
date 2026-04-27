import { motion } from "framer-motion";
import { Bot, Layers, BarChart3, ShieldCheck, Zap, Repeat } from "lucide-react";

export default function FeaturesSection() {
  const features = [
    {
      icon: <Bot className="w-6 h-6" />,
      title: "AI-Powered Deployment",
      description: "Predicts configurations, automates rollbacks, and optimizes deployment strategies using advanced machine learning.",
      color: "blue",
    },
    {
      icon: <Layers className="w-6 h-6" />,
      title: "One-Click K8s Orchestration",
      description: "Seamless integration with Docker & Kubernetes. Deploy complex clusters with zero manual configuration.",
      color: "indigo",
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Real-time Monitoring",
      description: "Comprehensive dashboard with intelligent alerting and automated incident response for maximum uptime.",
      color: "green",
    },
    {
      icon: <ShieldCheck className="w-6 h-6" />,
      title: "Auto-Healing Architecture",
      description: "AI-driven error prediction and self-correction capabilities prevent system failures before they impact users.",
      color: "purple",
    },
    {
      icon: <Repeat className="w-6 h-6" />,
      title: "CI/CD Integration",
      description: "Works natively with GitHub Actions, Jenkins, GitLab CI, and all major DevOps toolchains.",
      color: "slate",
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Instant Scaling",
      description: "Dynamically scale resources based on traffic patterns predicted by our analysis engine.",
      color: "orange",
    },
  ];

  return (
    <section className="py-24 bg-white dark:bg-slate-950 border-b border-slate-100 dark:border-slate-900">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-sm font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-3">Platform Capabilities</h2>
          <h3 className="text-4xl md:text-5xl font-extrabold text-slate-900 dark:text-white mb-6 tracking-tight">
            Everything you need to <span className="text-blue-600">scale faster</span>
          </h3>
          <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed">
            Stop managing infrastructure and start building features. AutoDeploy handles 
            the complexity of modern cloud deployments for you.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="group p-8 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-blue-300 dark:hover:border-blue-700 transition-all shadow-sm hover:shadow-md"
            >
              <div className="w-12 h-12 rounded-xl bg-white dark:bg-slate-800 flex items-center justify-center mb-6 border border-slate-200 dark:border-slate-700 text-blue-600 dark:text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-colors shadow-sm">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-4 text-slate-900 dark:text-white">
                {feature.title}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>


      </div>
    </section>
  );
}
