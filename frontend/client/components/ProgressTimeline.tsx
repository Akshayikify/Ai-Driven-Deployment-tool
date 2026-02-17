import React from "react";
import { cn } from "@/lib/utils";
import { CheckCircle, Clock, Loader2 } from "lucide-react";

interface TimelineStep {
  id: string;
  title: string;
  description: string;
  status: "pending" | "active" | "completed";
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
                    "bg-green-500 border-green-500 text-white",
                  step.status === "active" &&
                    "bg-neon-blue border-neon-cyan text-white shadow-lg shadow-neon-blue/30",
                  step.status === "pending" &&
                    "bg-slate-700 border-slate-600 text-slate-400",
                )}
              >
                {step.status === "completed" && (
                  <CheckCircle className="w-4 h-4" />
                )}
                {step.status === "active" && (
                  <Loader2 className="w-4 h-4 animate-spin" />
                )}
                {step.status === "pending" && <Clock className="w-4 h-4" />}
              </div>

              {/* Vertical line */}
              {!isLast && (
                <div
                  className={cn(
                    "w-0.5 h-12 mt-2 transition-colors duration-300",
                    step.status === "completed"
                      ? "bg-green-500"
                      : "bg-slate-600",
                  )}
                />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 pb-8">
              <div className="flex items-center justify-between">
                <h4
                  className={cn(
                    "font-semibold transition-colors duration-300",
                    step.status === "completed" && "text-green-400",
                    step.status === "active" && "text-neon-cyan",
                    step.status === "pending" && "text-slate-300",
                  )}
                >
                  {step.title}
                </h4>
                {step.timestamp && (
                  <span className="text-xs text-slate-500">
                    {step.timestamp}
                  </span>
                )}
              </div>

              <p
                className={cn(
                  "text-sm mt-1 transition-colors duration-300",
                  step.status === "completed" && "text-green-300/70",
                  step.status === "active" && "text-neon-cyan/70",
                  step.status === "pending" && "text-slate-400",
                )}
              >
                {step.description}
              </p>

              {/* Progress bar for active step */}
              {step.status === "active" && (
                <div className="mt-3">
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-neon-blue h-2 rounded-full animate-pulse"
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
