import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Terminal, Shield, Zap } from "lucide-react";
import { useUser } from "@clerk/clerk-react";

export default function HeroSection() {
  const navigate = useNavigate();
  const { isSignedIn } = useUser();

  return (
    <section className="relative min-h-[90vh] flex items-center justify-center py-20 bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800">
      <div className="container mx-auto px-6 relative z-10 max-w-6xl">
        <div className="text-center space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >

            
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-6">
              Automate Your Deployments <br />
              <span className="text-blue-600 dark:text-blue-400">with Intelligence</span>
            </h1>

            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Streamline your CI/CD pipelines and let AI handle deployments across
              Docker, Kubernetes, and Cloud with zero manual overhead.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                size="lg"
                onClick={() => navigate(isSignedIn ? "/dashboard" : "/signup")}
                className="text-base px-8 h-12 bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition-all"
              >
                Get Started Free
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => navigate("/workflow")}
                className="text-base px-8 h-12 border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
              >
                View Workflow
              </Button>
            </div>
          </motion.div>

          {/* Simplified Workflow Visualization */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="pt-16"
          >
            <div className="bg-white dark:bg-slate-900 rounded-xl p-8 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-8 items-center">
                <div className="flex flex-col items-center space-y-3">
                  <div className="w-14 h-14 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center border border-slate-200 dark:border-slate-700">
                    <Terminal className="w-6 h-6 text-slate-700 dark:text-slate-300" />
                  </div>
                  <span className="text-sm font-semibold text-slate-900 dark:text-white">Commit Code</span>
                </div>

                <div className="hidden md:flex justify-center text-slate-300 dark:text-slate-700">
                  <ArrowRight className="w-6 h-6" />
                </div>

                <div className="flex flex-col items-center space-y-3">
                  <div className="w-14 h-14 bg-blue-50 dark:bg-blue-900/30 rounded-lg flex items-center justify-center border border-blue-100 dark:border-blue-800">
                    <Shield className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <span className="text-sm font-semibold text-slate-900 dark:text-white">AI Analysis</span>
                </div>

                <div className="hidden md:flex justify-center text-slate-300 dark:text-slate-700">
                  <ArrowRight className="w-6 h-6" />
                </div>

                <div className="flex flex-col items-center space-y-3">
                  <div className="w-14 h-14 bg-green-50 dark:bg-green-900/30 rounded-lg flex items-center justify-center border border-green-100 dark:border-green-800">
                    <Zap className="w-6 h-6 text-green-600 dark:text-green-400" />
                  </div>
                  <span className="text-sm font-semibold text-slate-900 dark:text-white">Cloud Deploy</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

