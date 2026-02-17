import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { motion, useScroll, useTransform, useInView } from "framer-motion";
import { useRef } from "react";

export default function CTASection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], [20, -20]);
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
  const navigate = useNavigate();

  const handleStartTrial = () => {
    navigate('/dashboard');
  };

  const buttonVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const trustVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 }
  };

  return (
    <motion.section
      ref={sectionRef}
      className="py-24 bg-background relative overflow-hidden"
      style={{ y, opacity }}
    >
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-white/5 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "2s" }}
        ></div>
        <div
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "1s" }}
        ></div>
      </div>

      {/* Floating 3D Elements */}
      <div className="absolute top-20 left-10 w-16 h-16 bg-white/20 rounded-xl transform rotate-12 animate-float shadow-2xl"></div>
      <div
        className="absolute top-32 right-20 w-12 h-12 bg-white/15 rounded-full animate-float shadow-2xl"
        style={{ animationDelay: "1.5s" }}
      ></div>
      <div
        className="absolute bottom-20 left-20 w-20 h-20 bg-white/10 rounded-2xl transform -rotate-12 animate-float shadow-2xl"
        style={{ animationDelay: "0.5s" }}
      ></div>
      <div
        className="absolute bottom-32 right-10 w-14 h-14 bg-white/25 rounded-lg transform rotate-45 animate-float shadow-2xl"
        style={{ animationDelay: "2.5s" }}
      ></div>

      <div className="container mx-auto px-6 text-center relative z-10">
        <div className="max-w-4xl mx-auto">
          {/* Main CTA Heading */}
          <h2 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 text-black dark:text-white leading-tight">
            Deploy Smarter
            <br />
            <span className="bg-gradient-to-r from-yellow-300 to-orange-300 bg-clip-text text-transparent">
              with AI Today!
            </span>
          </h2>

          <p className="text-xl md:text-2xl text-black/90 dark:text-white/90 mb-12 max-w-3xl mx-auto leading-relaxed">
            Join thousands of developers and DevOps teams who have already
            transformed their deployment workflows. Experience the future of
            automated deployments with zero configuration.
          </p>

          {/* CTA Buttons */}
          <motion.div
            className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16"
            initial="hidden"
            whileInView="visible"
            variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
          >
            <motion.div variants={buttonVariants}>
              <Button
                size="lg"
                onClick={handleStartTrial}
                className="text-xl px-12 py-8 bg-white text-brand-700 hover:bg-gray-100 shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105 font-bold"
              >
                Start Free Trial
                <span className="ml-3 text-2xl">🚀</span>
              </Button>
            </motion.div>
            <motion.div variants={buttonVariants}>
              <Button
                size="lg"
                variant="outline"
                className="text-xl px-12 py-8 border-2 border-black dark:border-white text-black dark:text-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-brand-700 shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105 font-bold"
              >
                Request a Demo
                <span className="ml-3 text-2xl">📺</span>
              </Button>
            </motion.div>
          </motion.div>

          {/* Trust Indicators */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
            initial="hidden"
            whileInView="visible"
            variants={{ visible: { transition: { staggerChildren: 0.3 } } }}
          >
            <motion.div variants={trustVariants} className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <div className="text-3xl font-bold text-black dark:text-white mb-2">
                Free Forever
              </div>
              <div className="text-black/80 dark:text-white/80">No credit card required</div>
            </motion.div>
            <motion.div variants={trustVariants} className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <div className="text-3xl font-bold text-black dark:text-white mb-2">
                5-Min Setup
              </div>
              <div className="text-black/80 dark:text-white/80">Deploy in minutes, not hours</div>
            </motion.div>
            <motion.div variants={trustVariants} className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <div className="text-3xl font-bold text-black dark:text-white mb-2">
                24/7 Support
              </div>
              <div className="text-black/80 dark:text-white/80">Expert help when you need it</div>
            </motion.div>
          </motion.div>

        </div>
      </div>
    </motion.section>
  );
}
