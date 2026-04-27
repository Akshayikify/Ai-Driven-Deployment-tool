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
            Connect Your <br />
            <span className="bg-gradient-to-r from-neon-cyan to-indigo-500 bg-clip-text text-transparent">
              GitHub Ecosystem
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
      <div className="flex-1 flex flex-col items-center justify-center p-6 relative">
        <motion.div
           initial={{ opacity: 0, scale: 0.95 }}
           animate={{ opacity: 1, scale: 1 }}
           transition={{ duration: 0.5, delay: 0.2 }}
           className="w-full max-w-md"
        >
          <SignIn 
            appearance={{
              variables: {
                colorPrimary: "#00E5FF",
                colorText: "white",
                colorBackground: "#0f172a",
                colorInputBackground: "#1e293b",
                colorInputText: "white",
                colorTextOnPrimaryBackground: "white",
              },
              elements: {
                formButtonPrimary: "bg-gradient-to-r from-neon-cyan to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-sm normal-case shadow-lg shadow-neon-cyan/20",
                card: "bg-slate-900 border border-slate-800 shadow-2xl",
                headerTitle: "text-white text-2xl font-bold",
                headerSubtitle: "text-slate-400 text-sm",
                socialButtonsBlockButton: "bg-slate-800 border-slate-700 hover:bg-slate-700 text-white",
                socialButtonsBlockButtonText: "text-white font-medium",
                dividerLine: "bg-slate-800",
                dividerText: "text-slate-500",
                formFieldLabel: "text-slate-200 font-semibold mb-1",
                formFieldInput: "bg-slate-800 border border-slate-700 text-white focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 transition-all duration-200 hover:border-slate-600 py-2 px-4 h-11",
                otpCodeFieldInput: "bg-slate-800 border border-slate-700 text-white text-xl font-bold focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 transition-all duration-200 h-12",
                formResendCodeActionText: "text-neon-cyan hover:text-cyan-300 font-medium",
                footerActionText: "text-slate-300",
                footerActionLink: "text-neon-cyan hover:text-cyan-300 font-bold",
                identityPreviewText: "text-white font-medium",
                identityPreviewEditButtonIcon: "text-neon-cyan",
              }
            }}
            signUpUrl="/signup"
          />
        </motion.div>
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