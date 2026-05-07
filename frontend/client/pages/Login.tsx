import { SignIn } from "@clerk/clerk-react";
import { Github, ShieldCheck, Zap, ArrowRight, Lock } from "lucide-react";
import { motion } from "framer-motion";

export default function Login() {
  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-slate-950 text-white overflow-hidden">
      {/* Informational Side */}
      <div className="relative flex lg:w-1/2 p-8 lg:p-16 flex-col justify-center bg-slate-900 border-b lg:border-b-0 lg:border-r border-slate-800">
        <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-neon-cyan rounded-full blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-500 rounded-full blur-[120px]" />
        </div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="relative z-10"
        >
          <div className="flex items-center gap-3 mb-8">
            <div className="p-2 bg-gradient-to-br from-neon-cyan to-indigo-600 rounded-xl shadow-lg shadow-neon-cyan/20">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">Autodeploy <span className="text-neon-cyan text-sm font-medium uppercase tracking-widest">Auto-Deploy</span></span>
          </div>

          <h1 className="text-3xl lg:text-5xl font-extrabold leading-tight mb-6">
            Begin Your <br />
            <span className="bg-gradient-to-r from-cyan-400 via-white to-indigo-400 bg-clip-text text-transparent">
              DevOps Journey
            </span>
          </h1>

          <p className="text-slate-400 text-lg mb-10 max-w-md">
            Before proceeding, please ensure you follow these steps to grant the necessary permissions for automated deployment.
          </p>

          <div className="space-y-8">
            <AuthStep 
              icon={<Github className="w-5 h-5" />}
              title="Select 'Continue with GitHub'"
              description="For the tool to access your repositories, you must authenticate through your GitHub account."
            />
            <AuthStep 
              icon={<ShieldCheck className="w-5 h-5" />}
              title="Grant 'repo' Permissions"
              description="Ensure you authorize written access so our agent can create Dockerfiles and CI/CD pipelines for you."
            />
            <AuthStep 
              icon={<Lock className="w-5 h-5" />}
              title="Secure Token Management"
              description="Your tokens are handled server-side via Clerk and never exposed to the client-side environment."
            />
          </div>
        </motion.div>
      </div>

      {/* Auth Side */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 bg-slate-900/50">
          <SignIn 
            signUpUrl="/signup"
          />
      </div>
    </div>
  );
}

function AuthStep({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-neon-cyan">
        {icon}
      </div>
      <div>
        <h4 className="text-white font-semibold mb-1 flex items-center gap-2">
          {title}
          <ArrowRight className="w-3 h-3 text-slate-500" />
        </h4>
        <p className="text-slate-400 text-sm leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
}