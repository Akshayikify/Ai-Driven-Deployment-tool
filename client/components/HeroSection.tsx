import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useTheme } from "next-themes";
import { ArrowRight } from "lucide-react";

export default function HeroSection() {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const isDark = theme === "dark";
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
      {/* Spline 3D Background */}
      <iframe
        src="https://my.spline.design/abstractnirvana-aeRHGpYfyL8nblk2tKDK1Pop/"
        frameBorder="0"
        width="100%"
        height="100%"
        className="absolute inset-0 z-0"
        title="Spline 3D Background"
      ></iframe>
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-br from-brand-400/20 to-brand-600/20 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute top-3/4 right-1/4 w-80 h-80 bg-gradient-to-br from-purple-400/20 to-pink-600/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "2s" }}
        ></div>
        <div
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-br from-cyan-400/20 to-blue-600/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "1s" }}
        ></div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        {/* 3D Floating Elements */}
        <div className="absolute -top-20 left-10 w-20 h-20 bg-gradient-to-br from-brand-500 to-brand-700 rounded-xl transform rotate-12 animate-float shadow-2xl"></div>
        <div
          className="absolute -top-10 right-20 w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full animate-float shadow-2xl"
          style={{ animationDelay: "1.5s" }}
        ></div>
        <div
          className="absolute top-32 -left-10 w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg transform -rotate-12 animate-float shadow-2xl"
          style={{ animationDelay: "0.5s" }}
        ></div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 gap-12 items-center">
          {/* Centered Text Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-[#60a5fa] to-[#ec4899] bg-clip-text text-transparent">
                Automate Your
              </span>
              <br />
              <span className="bg-gradient-to-r from-[#60a5fa] to-[#ec4899] bg-clip-text text-transparent">
                Deployments
              </span>
              <br />
              <span className="bg-gradient-to-r from-[#60a5fa] to-[#ec4899] bg-clip-text text-transparent">
                with AI
              </span>
            </h1>

            <p className="text-xl md:text-2xl bg-gradient-to-r from-[#b429f9] to-[#26c5f3] bg-clip-text text-transparent mb-8 leading-relaxed">
              <strong>Faster, Smarter, Error-Free</strong>
              <br />
              Streamline CI/CD pipelines and let AI handle deployments across
              Docker, Kubernetes, and Cloud.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Button
                size="lg"
                onClick={() => navigate("/dashboard")}
                className="text-lg px-8 py-6 bg-gradient-to-r from-[#caefd7]/30 via-[#f5bfd7]/30 to-[#abc9e9]/30 backdrop-blur-md border border-white/20 text-black hover:bg-white/50 hover:text-black shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105"
              >
                Analyze
                <span className="ml-2"></span>
              </Button>
              <Button
                size="lg"
                onClick={() => navigate("/workflow")}
                className="text-lg px-8 py-6 bg-gradient-to-r from-[#caefd7]/30 via-[#f5bfd7]/30 to-[#abc9e9]/30 backdrop-blur-md border border-white/20 text-black hover:bg-white/50 hover:text-black shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
              >
                View Workflow
                <span className="ml-2"></span>
              </Button>
            </div>

            {/* 3D Workflow Visualization */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="relative"
            >
              <div className="bg-card rounded-3xl p-8 shadow-2xl transition-colors mt-32 dark:border dark:border-white/10">
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center bg-card/80 rounded-2xl p-4 transition-colors dark:bg-card/50">
                  {/* Code Commit */}
                  <div className="flex flex-col items-center space-y-2 group">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-110 group-hover:rotate-3 dark:from-lime-400 dark:to-lime-500">
                      <span className="text-2xl">💻</span>
                    </div>
                    <span className="text-sm font-medium text-card-foreground dark:text-white">
                      Code Commit
                    </span>
                  </div>

                  {/* Arrow */}
                  <div className="flex justify-center">
                    <div className="w-8 h-8 bg-gradient-to-r from-brand-400 to-brand-600 rounded-full animate-pulse flex items-center justify-center dark:from-cyan-400 dark:to-cyan-600">
                      <ArrowRight className="w-4 h-4 text-white" />
                    </div>
                  </div>

                  {/* AI Analyzer */}
                  <div className="flex flex-col items-center space-y-2 group">
                    <div className="w-16 h-16 bg-gradient-to-br from-brand-500 to-brand-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-110 group-hover:rotate-3 dark:from-blue-400 dark:to-blue-500">
                      <span className="text-2xl">🤖</span>
                    </div>
                    <span className="text-sm font-medium text-card-foreground dark:text-white">
                      AI Analyzer
                    </span>
                  </div>

                  {/* Arrow */}
                  <div className="flex justify-center">
                    <div className="w-8 h-8 bg-gradient-to-r from-brand-400 to-brand-600 rounded-full animate-pulse flex items-center justify-center dark:from-cyan-400 dark:to-cyan-600">
                      <ArrowRight className="w-4 h-4 text-white" />
                    </div>
                  </div>

                  {/* Deployment */}
                  <div className="flex flex-col items-center space-y-2 group">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-110 group-hover:rotate-3 dark:from-violet-400 dark:to-violet-500">
                      <span className="text-2xl">☁️</span>
                    </div>
                    <span className="text-sm font-medium text-card-foreground dark:text-white">
                      Deploy to Cloud
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}

