import React, { useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Terminal, Circle } from "lucide-react";

interface LogEntry {
    timestamp: string;
    level: "INFO" | "DEBUG" | "SUCCESS" | "WARN" | "ERROR";
    message: string;
}

const mockLogs: LogEntry[] = [
    {
        timestamp: "2024-01-15 14:32:15",
        level: "INFO",
        message: "Starting deployment process...",
    },
    {
        timestamp: "2024-01-15 14:32:16",
        level: "DEBUG",
        message: "Loading configuration...",
    },
    {
        timestamp: "2024-01-15 14:32:17",
        level: "SUCCESS",
        message: "Container built successfully",
    },
    {
        timestamp: "2024-01-15 14:32:18",
        level: "WARN",
        message: "High memory usage detected",
    },
    {
        timestamp: "2024-01-15 14:32:19",
        level: "INFO",
        message: "Deploying to production...",
    },
    {
        timestamp: "2024-01-15 14:32:20",
        level: "ERROR",
        message: "Connection timeout",
    },
    {
        timestamp: "2024-01-15 14:32:21",
        level: "INFO",
        message: "Retrying connection...",
    },
    {
        timestamp: "2024-01-15 14:32:22",
        level: "SUCCESS",
        message: "Deployment completed ✓",
    },
];

const getLevelColor = (level: LogEntry["level"]) => {
    switch (level) {
        case "INFO":
            return "text-gray-400";
        case "DEBUG":
            return "text-blue-400";
        case "SUCCESS":
            return "text-green-400";
        case "WARN":
            return "text-yellow-400";
        case "ERROR":
            return "text-red-400";
        default:
            return "text-gray-400";
    }
};

export default function LogMonitoringCard({ className }: { className?: string }) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, []);

    return (
        <Card className={`bg-slate-800/50 border-slate-700 p-4 sm:p-6 ${className}`}>
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <Terminal className="w-5 h-5 text-neon-cyan flex-shrink-0" />
                    <h3 className="text-base sm:text-lg font-semibold text-white">
                        Live Logs
                    </h3>
                </div>
                <div className="flex items-center gap-2">
                    <div className="relative flex h-2.5 w-2.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                    </div>
                    <span className="text-xs font-medium text-green-500">Live</span>
                </div>
            </div>

            <div className="bg-gray-950 rounded-lg border border-slate-800 shadow-inner overflow-hidden">
                {/* Terminal Header */}
                <div className="bg-gray-900 px-4 py-2 flex items-center gap-2 border-b border-slate-800">
                    <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
                        <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
                        <div className="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
                    </div>
                    <div className="flex-1 text-center">
                        <span className="text-xs text-gray-500 font-mono">
                            autodeploy.ai/dashboard
                        </span>
                    </div>
                </div>

                {/* Logs Content */}
                <div
                    ref={scrollRef}
                    className="p-4 h-[300px] overflow-y-auto font-mono text-xs sm:text-sm space-y-1.5 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent"
                >
                    {mockLogs.map((log, index) => (
                        <div key={index} className="flex gap-2 hover:bg-white/5 p-0.5 rounded transition-colors">
                            <span className="text-slate-500 flex-shrink-0">[{log.timestamp}]</span>
                            <span className={`font-semibold ${getLevelColor(log.level)} w-16 flex-shrink-0`}>
                                {log.level}:
                            </span>
                            <span className="text-slate-300 break-all">{log.message}</span>
                        </div>
                    ))}
                    {/* Typing cursor effect */}
                    <div className="flex items-center gap-2 text-neon-cyan animate-pulse">
                        <span>_</span>
                    </div>
                </div>
            </div>
        </Card>
    );
}
