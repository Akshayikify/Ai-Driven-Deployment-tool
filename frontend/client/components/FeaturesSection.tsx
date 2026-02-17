import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function FeaturesSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
  const features = [
    {
      icon: "🤖",
      title: "AI-Powered Deployment",
      description:
        "Predicts configurations, automates rollbacks, and optimizes deployment strategies using machine learning.",
      gradient: "from-neon-blue to-neon-purple",
    },
    {
      icon: "🐳",
      title: "One-Click Docker & Kubernetes",
      description:
        "Seamless integration with containerization platforms. Deploy to K8s clusters with zero configuration.",
      gradient: "from-neon-cyan to-neon-blue",
    },
    {
      icon: "📊",
      title: "Monitoring & Alerts",
      description:
        "Real-time monitoring with intelligent alerting and automated incident response.",
      gradient: "from-neon-green to-neon-cyan",
    },
    {
      icon: "🔮",
      title: "Auto-Healing",
      description:
        "AI-driven error prediction and auto-healing capabilities prevent issues before they occur.",
      gradient: "from-neon-pink to-neon-purple",
    },
    {
      icon: "⚙️",
      title: "CI/CD Integration",
      description:
        "Works seamlessly with Jenkins, GitHub Actions, GitLab CI, and all major CI/CD platforms.",
      gradient: "from-neon-purple to-neon-blue",
    },
  ];

  return (
    <motion.section
      ref={sectionRef}
      className="py-24 bg-background relative overflow-hidden"
      style={{ y, opacity }}
    >
      {/* Background decorations */}
      <div className="absolute top-0 left-0 w-full h-full">
        <div className="absolute top-1/4 -left-32 w-64 h-64 bg-gradient-to-br from-brand-200/30 to-brand-400/30 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 -right-32 w-64 h-64 bg-gradient-to-br from-purple-200/30 to-pink-400/30 rounded-full blur-3xl"></div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-brand-600 to-purple-600 bg-clip-text text-transparent">
              Key Features
            </span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-white max-w-3xl mx-auto">
            Powerful AI-driven features designed to revolutionize your
            deployment workflow
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 border border-gray-100 hover:border-brand-200"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
            >
              {/* Card background gradient on hover */}
              <div
                className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity duration-500`}
              ></div>

              {/* Floating icon */}
              <div className="relative">
                <div
                  className={`w-20 h-20 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-all duration-500 transform group-hover:scale-110 group-hover:rotate-3`}
                >
                  <span className="text-3xl filter drop-shadow-sm">
                    {feature.icon}
                  </span>
                </div>

                {/* Glow effect */}
                <div
                  className={`absolute top-0 left-0 w-20 h-20 bg-gradient-to-br ${feature.gradient} rounded-2xl opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500`}
                ></div>
              </div>

              <h3 className="text-2xl font-bold mb-4 text-gray-900 group-hover:text-brand-700 transition-colors duration-300">
                {feature.title}
              </h3>

              <p className="text-gray-600 leading-relaxed group-hover:text-gray-700 transition-colors duration-300">
                {feature.description}
              </p>

              {/* Animated border */}
              <div className="absolute inset-0 rounded-2xl border-2 border-transparent group-hover:border-brand-200 transition-colors duration-500"></div>

              {/* Corner accent */}
              <div
                className={`absolute top-4 right-4 w-2 h-2 bg-gradient-to-br ${feature.gradient} rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
              ></div>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <p className="text-lg text-gray-600 mb-6">
            Ready to experience the future of deployment automation?
          </p>
          <div className="inline-flex items-center space-x-2 rounded-full px-6 py-3">
            <span className="text-gray-700 dark:text-gray-200 font-medium">
              ⚡ All features included in every plan
            </span>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
