import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function BenefitsSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], [30, -30]);
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
  const benefits = [
    {
      title: "For Developers",
      subtitle: "Code with Confidence",
      icon: "👨‍💻",
      primaryBenefit: "Saves Time",
      secondaryBenefit: "Reduces Errors",
      features: [
        "Focus on coding, not deployment complexity",
        "Automatic error detection and prevention",
        "Instant feedback on code quality",
        "Seamless integration with existing tools",
      ],
      gradient: "from-blue-500 to-cyan-600",
      bgGradient: "from-blue-50 to-cyan-50",
    },
    {
      title: "For DevOps Teams",
      subtitle: "Scale with Ease",
      icon: "⚙️",
      primaryBenefit: "Faster Rollouts",
      secondaryBenefit: "Enhanced Scalability",
      features: [
        "Automated deployment orchestration",
        "Intelligent resource management",
        "Zero-downtime deployments",
        "Advanced monitoring and alerting",
      ],
      gradient: "from-brand-500 to-purple-600",
      bgGradient: "from-brand-50 to-purple-50",
    },
    {
      title: "For Companies",
      subtitle: "Maximize ROI",
      icon: "🏢",
      primaryBenefit: "Reduced Costs",
      secondaryBenefit: "High Availability",
      features: [
        "Lower operational overhead",
        "Minimize downtime and outages",
        "Faster time-to-market",
        "Improved customer satisfaction",
      ],
      gradient: "from-green-500 to-emerald-600",
      bgGradient: "from-green-50 to-emerald-50",
    },
  ];

  return (
    <motion.section
      ref={sectionRef}
      className="py-24 bg-background relative overflow-hidden"
      style={{ y, opacity }}
    >
      {/* Background decorations */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/6 w-64 h-64 bg-gradient-to-br from-brand-200/20 to-brand-400/20 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute bottom-1/4 right-1/6 w-80 h-80 bg-gradient-to-br from-purple-200/20 to-pink-400/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "2s" }}
        ></div>
        <div
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-gradient-to-br from-green-200/20 to-emerald-400/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "1s" }}
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
              Why Choose AutoDeploy.AI?
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transforming deployment workflows for teams of all sizes across the
            technology stack
          </p>
        </motion.div>

        {/* 3-Column Benefits */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
          {benefits.map((benefit, index) => (
            <div
              key={index}
              className={`group relative bg-gradient-to-br ${benefit.bgGradient} rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 border border-white/50`}
              style={{
                animationDelay: `${index * 0.2}s`,
              }}
            >
              {/* Floating Icon */}
              <div className="relative mb-6">
                <div
                  className={`w-24 h-24 bg-gradient-to-br ${benefit.gradient} rounded-2xl flex items-center justify-center shadow-xl group-hover:shadow-2xl transition-all duration-500 transform group-hover:scale-110 group-hover:rotate-3 mx-auto`}
                >
                  <span className="text-4xl filter drop-shadow-sm">
                    {benefit.icon}
                  </span>
                </div>

                {/* Glow effect */}
                <div
                  className={`absolute top-0 left-1/2 transform -translate-x-1/2 w-24 h-24 bg-gradient-to-br ${benefit.gradient} rounded-2xl opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500`}
                ></div>
              </div>

              {/* Content */}
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {benefit.title}
                </h3>
                <p className="text-lg text-gray-600 mb-4">{benefit.subtitle}</p>

                {/* Primary Benefits */}
                <div className="flex flex-col sm:flex-row gap-2 justify-center mb-6">
                  <div
                    className={`bg-gradient-to-r ${benefit.gradient} text-white px-4 py-2 rounded-full text-sm font-medium shadow-md`}
                  >
                    ✓ {benefit.primaryBenefit}
                  </div>
                  <div
                    className={`bg-white text-gray-700 px-4 py-2 rounded-full text-sm font-medium shadow-md border-2 border-transparent group-hover:border-current transition-colors duration-300`}
                  >
                    ✓ {benefit.secondaryBenefit}
                  </div>
                </div>
              </div>

              {/* Features List */}
              <ul className="space-y-3">
                {benefit.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start space-x-3">
                    <div
                      className={`w-2 h-2 bg-gradient-to-r ${benefit.gradient} rounded-full mt-2 flex-shrink-0`}
                    ></div>
                    <span className="text-gray-700 text-sm leading-relaxed">
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              {/* Hover Effect Border */}
              <div
                className={`absolute inset-0 rounded-3xl border-2 border-transparent group-hover:border-current transition-colors duration-500 opacity-0 group-hover:opacity-20`}
              ></div>

              {/* Corner Accents */}
              <div
                className={`absolute top-4 right-4 w-3 h-3 bg-gradient-to-br ${benefit.gradient} rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
              ></div>
              <div
                className={`absolute bottom-4 left-4 w-2 h-2 bg-gradient-to-br ${benefit.gradient} rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
              ></div>
            </div>
          ))}
        </div>


        {/* Call to Action */}
        <div className="text-center mt-12">
          <p className="text-lg text-gray-600 mb-6">
            Join thousands of teams already deploying smarter with AI
          </p>
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-brand-500 to-brand-700 rounded-full px-8 py-4 border border-brand-600 shadow-lg">
            <span className="text-white font-medium">
              🚀 Start your AI-powered deployment journey today
            </span>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
