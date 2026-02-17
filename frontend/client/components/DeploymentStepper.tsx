import React from "react";
import { cn } from "@/lib/utils";
import { Check, Upload, Search, Cog, Rocket, Monitor } from "lucide-react";

interface Step {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  status: "pending" | "active" | "completed";
}

interface DeploymentStepperProps {
  currentStep?: number;
  className?: string;
}

const steps: Step[] = [
  {
    id: "upload",
    title: "Upload Code",
    description: "Upload your project files",
    icon: Upload,
    status: "pending",
  },
  {
    id: "analyze",
    title: "AI Analysis",
    description: "Analyzing dependencies",
    icon: Search,
    status: "pending",
  },
  {
    id: "build",
    title: "Build",
    description: "Building your application",
    icon: Cog,
    status: "pending",
  },
  {
    id: "deploy",
    title: "Deploy",
    description: "Deploying to production",
    icon: Rocket,
    status: "pending",
  },
  {
    id: "monitor",
    title: "Monitor",
    description: "Monitoring deployment",
    icon: Monitor,
    status: "pending",
  },
];

export default function DeploymentStepper({
  currentStep = 0,
  className,
}: DeploymentStepperProps) {
  const updatedSteps = steps.map((step, index) => ({
    ...step,
    status:
      index < currentStep
        ? "completed"
        : index === currentStep
          ? "active"
          : "pending",
  }));

  return (
    <div className={cn("w-full", className)}>
      {/* Mobile Layout */}
      <div className="block sm:hidden space-y-4 mb-8">
        {updatedSteps.map((step, index) => {
          const Icon = step.icon;

          return (
            <div key={step.id} className="flex items-center gap-4">
              {/* Step Circle */}
              <div
                className={cn(
                  "relative w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 flex-shrink-0",
                  step.status === "completed" &&
                    "bg-green-500 text-white shadow-lg shadow-green-500/30",
                  step.status === "active" &&
                    "bg-neon-blue text-white shadow-lg shadow-neon-blue/50 animate-pulse",
                  step.status === "pending" &&
                    "bg-slate-700 text-slate-400 border-2 border-slate-600",
                )}
              >
                {step.status === "completed" ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <Icon className="w-5 h-5" />
                )}

                {/* Glowing effect for active step */}
                {step.status === "active" && (
                  <div className="absolute inset-0 rounded-full bg-neon-blue animate-ping opacity-20" />
                )}
              </div>

              {/* Step Content */}
              <div className="flex-1 min-w-0">
                <h3
                  className={cn(
                    "text-sm font-semibold transition-colors duration-300 truncate",
                    step.status === "completed" && "text-green-400",
                    step.status === "active" && "text-neon-cyan",
                    step.status === "pending" && "text-slate-400",
                  )}
                >
                  {step.title}
                </h3>
                <p
                  className={cn(
                    "text-xs mt-1 transition-colors duration-300",
                    step.status === "completed" && "text-green-300/70",
                    step.status === "active" && "text-neon-cyan/70",
                    step.status === "pending" && "text-slate-500",
                  )}
                >
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Desktop Layout */}
      <div className="hidden sm:flex items-center justify-between mb-8">
        {updatedSteps.map((step, index) => {
          const Icon = step.icon;
          const isLast = index === updatedSteps.length - 1;

          return (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center flex-1">
                {/* Step Circle */}
                <div
                  className={cn(
                    "relative w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300",
                    step.status === "completed" &&
                      "bg-green-500 text-white shadow-lg shadow-green-500/30",
                    step.status === "active" &&
                      "bg-neon-blue text-white shadow-lg shadow-neon-blue/50 animate-pulse",
                    step.status === "pending" &&
                      "bg-slate-700 text-slate-400 border-2 border-slate-600",
                  )}
                >
                  {step.status === "completed" ? (
                    <Check className="w-6 h-6" />
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}

                  {/* Glowing effect for active step */}
                  {step.status === "active" && (
                    <div className="absolute inset-0 rounded-full bg-neon-blue animate-ping opacity-20" />
                  )}
                </div>

                {/* Step Title */}
                <div className="mt-3 text-center">
                  <h3
                    className={cn(
                      "text-sm font-semibold transition-colors duration-300",
                      step.status === "completed" && "text-green-400",
                      step.status === "active" && "text-neon-cyan",
                      step.status === "pending" && "text-slate-400",
                    )}
                  >
                    {step.title}
                  </h3>
                  <p
                    className={cn(
                      "text-xs mt-1 transition-colors duration-300",
                      step.status === "completed" && "text-green-300/70",
                      step.status === "active" && "text-neon-cyan/70",
                      step.status === "pending" && "text-slate-500",
                    )}
                  >
                    {step.description}
                  </p>
                </div>
              </div>

              {/* Connector Line */}
              {!isLast && (
                <div className="flex-1 mx-4">
                  <div
                    className={cn(
                      "h-0.5 transition-colors duration-300",
                      index < currentStep ? "bg-green-500" : "bg-slate-600",
                    )}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
