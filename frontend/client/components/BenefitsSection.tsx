import { motion } from "framer-motion";
import { Code2, Settings2, Building2, CheckCircle2 } from "lucide-react";

export default function BenefitsSection() {
  const benefits = [
    {
      title: "For Developers",
      subtitle: "Code with Confidence",
      icon: <Code2 className="w-8 h-8" />,
      features: [
        "Focus on features, not infrastructure",
        "Automatic rollback on failure",
        "Instant preview environments",
        "Native Git integration",
      ],
      color: "blue",
    },
    {
      title: "For DevOps Teams",
      subtitle: "Scale with Ease",
      icon: <Settings2 className="w-8 h-8" />,
      features: [
        "Automated cluster management",
        "AI-driven resource optimization",
        "Zero-downtime blue-green deployments",
        "Enterprise-grade security audits",
      ],
      color: "indigo",
    },
    {
      title: "For Companies",
      subtitle: "Maximize ROI",
      icon: <Building2 className="w-8 h-8" />,
      features: [
        "Reduced cloud infrastructure costs",
        "Faster time-to-market for features",
        "Minimize expensive downtime",
        "Scalable platform for growth",
      ],
      color: "slate",
    },
  ];

  return (
    <section className="py-24 bg-white dark:bg-slate-950 border-b border-slate-100 dark:border-slate-900">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 dark:text-white mb-6 tracking-tight">
            Impact across <span className="text-blue-600">the organization</span>
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            AutoDeploy isn't just a tool—it's a multiplier for your entire engineering 
            and business operation.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="p-10 rounded-3xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm"
            >
              <div className="flex flex-col items-center text-center mb-8">
                <div className="w-16 h-16 rounded-2xl bg-white dark:bg-slate-800 flex items-center justify-center text-blue-600 dark:text-blue-400 shadow-sm border border-slate-100 dark:border-slate-700 mb-6">
                  {benefit.icon}
                </div>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">{benefit.title}</h3>
                <p className="text-blue-600 dark:text-blue-400 font-semibold text-sm uppercase tracking-wider">{benefit.subtitle}</p>
              </div>

              <div className="space-y-4">
                {benefit.features.map((feature, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-slate-700 dark:text-slate-300 text-sm font-medium leading-relaxed">
                      {feature}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>


      </div>
    </section>
  );
}
