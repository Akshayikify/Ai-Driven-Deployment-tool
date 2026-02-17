import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function WorkflowSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], [50, -50]);
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
  const workflowSteps = [
    {
      id: 1,
      title: "Code Commit",
      description: "Push your code to any Git repository",
      icon: "💻",
      color: "from-green-500 to-emerald-600",
      delay: "0s",
    },
    {
      id: 2,
      title: "AI Analyzer",
      description: "Config + security check with AI intelligence",
      icon: "🤖",
      color: "from-brand-500 to-brand-700",
      delay: "0.5s",
    },
    {
      id: 3,
      title: "Containerization & Testing",
      description: "Automated Docker builds and comprehensive testing",
      icon: "🧪",
      color: "from-blue-500 to-cyan-600",
      delay: "1s",
    },
    {
      id: 4,
      title: "Deployment to Cloud/K8s",
      description: "Zero-downtime deployment across environments",
      icon: "🚀",
      color: "from-purple-500 to-pink-600",
      delay: "1.5s",
    },
    {
      id: 5,
      title: "Monitoring & Feedback",
      description: "Continuous monitoring with intelligent feedback loops",
      icon: "📊",
      color: "from-orange-500 to-red-600",
      delay: "2s",
    },
  ];

  return (
    <motion.section
      ref={sectionRef}
      id="workflow"
      className="py-24 bg-background relative overflow-hidden"
      style={{ y, opacity }}
    >
      {/* Animated background */}
      <div className="absolute inset-0">
        <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-gradient-to-br from-brand-200/20 to-brand-400/20 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute bottom-1/3 right-1/4 w-80 h-80 bg-gradient-to-br from-purple-200/20 to-pink-400/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "3s" }}
        ></div>
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
              How It Works
            </span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-white max-w-3xl mx-auto">
            See your deployment workflow transform from complex to effortless in
            5 simple steps
          </p>
        </motion.div>

        {/* Desktop Workflow - Horizontal */}
        <div className="hidden lg:block">
          <div className="relative">
            {/* Connection Lines */}
            <div className="absolute top-1/2 left-0 w-full h-1 bg-gradient-to-r from-brand-200 via-purple-200 to-orange-200 rounded-full transform -translate-y-1/2"></div>

            {/* Animated flow */}
            <div className="absolute top-1/2 left-0 w-full h-1 transform -translate-y-1/2">
              <div
                className="w-16 h-1 bg-gradient-to-r from-brand-500 to-purple-500 rounded-full"
                style={{ animation: "flow 8s ease-in-out infinite" }}
              ></div>
            </div>

            <div className="grid grid-cols-5 gap-8">
              {workflowSteps.map((step, index) => (
                <div
                  key={step.id}
                  className="flex flex-col items-center relative group"
                  style={{ animationDelay: step.delay }}
                >
                  {/* Step Circle */}
                  <div
                    className={`relative w-24 h-24 bg-gradient-to-br ${step.color} rounded-full flex items-center justify-center shadow-xl group-hover:shadow-2xl transition-all duration-1000 transform group-hover:scale-110`}
                    style={{
                      animationDelay: step.delay,
                      animation: 'float 8s ease-in-out infinite'
                    }}
                  >
                    <span className="text-3xl filter drop-shadow-sm">
                      {step.icon}
                    </span>

                    {/* Glow effect */}
                    <div
                      className={`absolute inset-0 bg-gradient-to-br ${step.color} rounded-full opacity-0 group-hover:opacity-30 blur-xl transition-opacity duration-500`}
                    ></div>
                  </div>

                  {/* Step Number */}
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-white dark:bg-gray-800 rounded-full border-2 border-gray-200 dark:border-gray-600 flex items-center justify-center text-sm font-bold text-gray-600 dark:text-gray-300 shadow-md">
                    {step.id}
                  </div>

                  {/* Content */}
                  <div className="mt-6 text-center">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 group-hover:text-brand-700 dark:group-hover:text-brand-700 transition-colors duration-300">
                      {step.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-white max-w-xs group-hover:text-gray-700 dark:group-hover:text-gray-700 transition-colors duration-300">
                      {step.description}
                    </p>
                  </div>

                  {/* Animated connector */}
                  {index < workflowSteps.length - 1 && (
                    <div className="absolute top-12 -right-4 w-8 h-1">
                      <div
                        className={`w-full h-full bg-gradient-to-r ${step.color} opacity-50 rounded-full`}
                        style={{ animation: "pulse 6s ease-in-out infinite" }}
                      ></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Mobile/Tablet Workflow - Vertical */}
        <div className="lg:hidden">
          <div className="space-y-8">
            {workflowSteps.map((step, index) => (
              <div key={step.id} className="flex items-start space-x-6 group">
                {/* Step Circle */}
                <div
                  className={`relative w-20 h-20 bg-gradient-to-br ${step.color} rounded-full flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-1000 transform group-hover:scale-110 flex-shrink-0`}
                  style={{
                    animation: 'float 8s ease-in-out infinite',
                    animationDelay: step.delay
                  }}
                >
                  <span className="text-2xl filter drop-shadow-sm">
                    {step.icon}
                  </span>

                  {/* Step Number */}
                  <div className="absolute -top-2 -right-2 w-7 h-7 bg-white dark:bg-gray-800 rounded-full border-2 border-gray-200 dark:border-gray-600 flex items-center justify-center text-sm font-bold text-gray-600 dark:text-gray-300 shadow-md">
                    {step.id}
                  </div>

                  {/* Glow effect */}
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${step.color} rounded-full opacity-0 group-hover:opacity-30 blur-xl transition-opacity duration-500`}
                  ></div>
                </div>

                {/* Content */}
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 group-hover:text-brand-700 dark:group-hover:text-brand-700 transition-colors duration-300">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 dark:text-white group-hover:text-gray-700 dark:group-hover:text-gray-700 transition-colors duration-300">
                    {step.description}
                  </p>
                </div>

                {/* Vertical connector */}
                {index < workflowSteps.length - 1 && (
                  <div className="absolute left-10 mt-20 w-1 h-8 bg-gradient-to-b from-gray-200 dark:from-gray-600 to-transparent rounded-full"></div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Stats */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-md rounded-2xl p-6 shadow-lg border border-white/20 dark:border-gray-600/20">
            <div className="text-3xl font-bold text-brand-600 mb-2">90%</div>
            <div className="text-gray-600 dark:text-white">Faster Deployments</div>
          </div>
          <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-md rounded-2xl p-6 shadow-lg border border-white/20 dark:border-gray-600/20">
            <div className="text-3xl font-bold text-purple-600 mb-2">99.9%</div>
            <div className="text-gray-600 dark:text-white">Success Rate</div>
          </div>
          <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-md rounded-2xl p-6 shadow-lg border border-white/20 dark:border-gray-600/20">
            <div className="text-3xl font-bold text-green-600 mb-2">0</div>
            <div className="text-gray-600 dark:text-white">Downtime Required</div>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
