import React from "react";
import { cn } from "@/lib/utils";
import { CheckCircle, Clock, Loader2, XCircle } from "lucide-react";

interface TimelineStep {
  id: string;
  title: string;
  description: string;
  status: "pending" | "active" | "completed" | "failed";
  timestamp?: string;
}

interface ProgressTimelineProps {
  steps: TimelineStep[];
  className?: string;
}

export default function ProgressTimeline({
  steps,
  className,
}: ProgressTimelineProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {steps.map((step, index) => {
        const isLast = index === steps.length - 1;

        return (
          <div key={step.id} className="flex items-start gap-4">
            {/* Timeline connector */}
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-300",
                  step.status === "completed" &&
                    "bg-green-600 border-green-600 text-white shadow-sm",
                  step.status === "active" &&
                    "bg-blue-600 border-blue-600 text-white shadow-md shadow-blue-500/20",
                  step.status === "failed" &&
                    "bg-red-600 border-red-600 text-white shadow-sm",
                  step.status === "pending" &&
                    "bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-400",
                )}
              >
                {step.status === "completed" && (
                  <CheckCircle className="w-4 h-4" />
                )}
                {step.status === "active" && (
                  <Loader2 className="w-4 h-4 animate-spin" />
                )}
                {step.status === "failed" && (
                  <XCircle className="w-4 h-4" />
                )}
                {step.status === "pending" && <Clock className="w-4 h-4" />}
              </div>

              {/* Vertical line */}
              {!isLast && (
                <div
                  className={cn(
                    "w-0.5 h-12 mt-2 transition-colors duration-300",
                    step.status === "completed"
                      ? "bg-green-600"
                      : "bg-slate-200 dark:bg-slate-800",
                  )}
                />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 pb-8">
              <div className="flex items-center justify-between">
                <h4
                  className={cn(
                    "text-sm font-bold transition-colors duration-300 uppercase tracking-tight",
                    step.status === "completed" && "text-green-700 dark:text-green-500",
                    step.status === "active" && "text-blue-700 dark:text-blue-400",
                    step.status === "failed" && "text-red-700 dark:text-red-400",
                    step.status === "pending" && "text-slate-500 dark:text-slate-400",
                  )}
                >
                  {step.title}
                </h4>
                {step.timestamp && (
                  <span className="text-[10px] font-bold text-slate-400 uppercase">
                    {step.timestamp}
                  </span>
                )}
              </div>

              <p
                className={cn(
                  "text-xs mt-1 transition-colors duration-300 font-medium",
                  step.status === "completed" && "text-slate-500 dark:text-slate-400",
                  step.status === "active" && "text-slate-700 dark:text-slate-300",
                  step.status === "pending" && "text-slate-400 dark:text-slate-500",
                )}
              >
                {step.description}
              </p>

              {/* Progress bar for active step */}
              {step.status === "active" && (
                <div className="mt-3">
                  <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden border border-slate-200 dark:border-slate-700">
                    <div
                      className="bg-blue-600 h-full rounded-full animate-pulse"
                      style={{ width: "60%" }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
