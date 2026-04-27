import { motion } from "framer-motion";
import { GitCommit, Search, Box, Cloud, LineChart, ArrowRight } from "lucide-react";

export default function WorkflowSection() {
  const workflowSteps = [
    {
      id: 1,
      title: "Commit Code",
      description: "Push your code to any Git repository including GitHub, GitLab, or Bitbucket.",
      icon: <GitCommit className="w-6 h-6" />,
      color: "bg-slate-100 text-slate-700",
    },
    {
      id: 2,
      title: "AI Analysis",
      description: "AI-powered checks for configuration errors, security vulnerabilities, and optimizations.",
      icon: <Search className="w-6 h-6" />,
      color: "bg-blue-100 text-blue-700",
    },
    {
      id: 3,
      title: "Build Image",
      description: "Automated Docker containerization and comprehensive testing of your application.",
      icon: <Box className="w-6 h-6" />,
      color: "bg-indigo-100 text-indigo-700",
    },
    {
      id: 4,
      title: "Cloud Deploy",
      description: "Zero-downtime deployment across AWS, GCP, Azure, or private Kubernetes clusters.",
      icon: <Cloud className="w-6 h-6" />,
      color: "bg-green-100 text-green-700",
    },
    {
      id: 5,
      title: "Monitor",
      description: "Continuous health monitoring with intelligent feedback and automated rollbacks.",
      icon: <LineChart className="w-6 h-6" />,
      color: "bg-orange-100 text-orange-700",
    },
  ];

  return (
    <section id="workflow" className="py-24 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 dark:text-white mb-6 tracking-tight">
            Streamlined <span className="text-blue-600">to Perfection</span>
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            Our optimized pipeline handles the heavy lifting, allowing your team to focus 
            on writing code while we handle the distribution.
          </p>
        </div>

        {/* Desktop Workflow */}
        <div className="hidden lg:block">
          <div className="relative">
            {/* Connection Line */}
            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-slate-200 dark:bg-slate-800 -translate-y-1/2 z-0"></div>

            <div className="grid grid-cols-5 gap-4 relative z-10">
              {workflowSteps.map((step, index) => (
                <div key={step.id} className="flex flex-col items-center">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className={`w-16 h-16 rounded-full ${step.color} flex items-center justify-center border-4 border-white dark:border-slate-900 shadow-sm mb-6`}
                  >
                    {step.icon}
                  </motion.div>
                  <div className="text-center px-4">
                    <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">{step.title}</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
                      {step.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Mobile Workflow */}
        <div className="lg:hidden space-y-12">
          {workflowSteps.map((step, index) => (
            <div key={step.id} className="flex gap-6 items-start">
              <div className={`w-12 h-12 rounded-lg ${step.color} flex items-center justify-center flex-shrink-0 shadow-sm border border-slate-200 dark:border-slate-800`}>
                {step.icon}
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                  <span className="text-blue-600 mr-2">{step.id}.</span>
                  {step.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Stats */}
        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { label: "Deployment Speed", value: "90%", desc: "Faster compared to manual pipelines", color: "blue" },
            { label: "Deployment Success", value: "99.9%", desc: "Reliability you can depend on", color: "green" },
            { label: "Infrastructure Cost", value: "30%", desc: "Average savings via AI optimization", color: "indigo" },
          ].map((stat, i) => (
            <div key={i} className="p-8 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm text-center">
              <div className="text-4xl font-black text-slate-900 dark:text-white mb-2">{stat.value}</div>
              <div className="text-sm font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-3">{stat.label}</div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">{stat.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
