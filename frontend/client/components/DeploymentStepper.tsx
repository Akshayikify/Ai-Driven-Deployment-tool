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
    title: "Upload",
    description: "Source code ready",
    icon: Upload,
    status: "pending",
  },
  {
    id: "analyze",
    title: "Analyze",
    description: "Deep AI check",
    icon: Search,
    status: "pending",
  },
  {
    id: "build",
    title: "Build",
    description: "Asset compilation",
    icon: Cog,
    status: "pending",
  },
  {
    id: "deploy",
    title: "Deploy",
    description: "Live environment",
    icon: Rocket,
    status: "pending",
  },
  {
    id: "monitor",
    title: "Monitor",
    description: "Stability check",
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
        ? ("completed" as const)
        : index === currentStep
          ? ("active" as const)
          : ("pending" as const),
  }));

  return (
    <div className={cn("w-full", className)}>
      {/* Mobile Layout */}
      <div className="block sm:hidden space-y-6 mb-12">
        {updatedSteps.map((step) => {
          const Icon = step.icon;

          return (
            <div key={step.id} className="flex items-center gap-5">
              {/* Step Circle */}
              <div
                className={cn(
                  "relative w-12 h-12 rounded-2xl flex items-center justify-center border-2 transition-all duration-500 flex-shrink-0 shadow-sm",
                  step.status === "completed" &&
                    "bg-green-600 border-green-600 text-white",
                  step.status === "active" &&
                    "bg-blue-600 border-blue-600 text-white animate-pulse",
                  step.status === "pending" &&
                    "bg-white dark:bg-slate-900 text-slate-300 border-slate-100 dark:border-slate-800",
                )}
              >
                {step.status === "completed" ? (
                  <Check className="w-6 h-6" />
                ) : (
                  <Icon className="w-6 h-6" />
                )}
              </div>

              {/* Step Content */}
              <div className="flex-1 min-w-0">
                <h3
                  className={cn(
                    "text-xs font-black uppercase tracking-widest transition-colors duration-500",
                    step.status === "completed" && "text-green-600",
                    step.status === "active" && "text-blue-600",
                    step.status === "pending" && "text-slate-400",
                  )}
                >
                  {step.title}
                </h3>
                <p
                  className={cn(
                    "text-[10px] font-bold uppercase tracking-widest mt-1 opacity-60",
                    step.status === "pending" ? "text-slate-500" : "text-slate-900 dark:text-slate-100",
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
      <div className="hidden sm:flex items-center justify-between mb-12 bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm">
        {updatedSteps.map((step, index) => {
          const Icon = step.icon;
          const isLast = index === updatedSteps.length - 1;

          return (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center flex-1">
                {/* Step Circle */}
                <div
                  className={cn(
                    "relative w-14 h-14 rounded-2xl flex items-center justify-center border-2 transition-all duration-500 shadow-md",
                    step.status === "completed" &&
                      "bg-green-600 border-green-600 text-white",
                    step.status === "active" &&
                      "bg-blue-600 border-blue-600 text-white animate-pulse",
                    step.status === "pending" &&
                      "bg-slate-50 dark:bg-slate-800 text-slate-300 border-slate-100 dark:border-slate-800",
                  )}
                >
                  {step.status === "completed" ? (
                    <Check className="w-7 h-7" />
                  ) : (
                    <Icon className="w-7 h-7" />
                  )}
                </div>

                {/* Step Title */}
                <div className="mt-4 text-center">
                  <h3
                    className={cn(
                      "text-[10px] font-black uppercase tracking-widest transition-colors duration-500",
                      step.status === "completed" && "text-green-600",
                      step.status === "active" && "text-blue-600",
                      step.status === "pending" && "text-slate-400",
                    )}
                  >
                    {step.title}
                  </h3>
                  <p className="text-[9px] font-bold uppercase tracking-tighter text-slate-400 mt-1">
                    {step.description}
                  </p>
                </div>
              </div>

              {/* Connector Line */}
              {!isLast && (
                <div className="flex-[0.5] mx-2">
                  <div
                    className={cn(
                      "h-0.5 rounded-full transition-all duration-1000",
                      index < currentStep ? "bg-green-600" : "bg-slate-100 dark:bg-slate-800",
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
