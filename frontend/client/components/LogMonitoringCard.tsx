import React, { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Terminal, Maximize2, RefreshCw, Circle } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogEntry {
    id: string;
    timestamp: string;
    level: "info" | "success" | "warning" | "error";
    message: string;
}

export default function LogMonitoringCard() {
    const [logs, setLogs] = useState<LogEntry[]>([
        {
            id: "1",
            timestamp: new Date().toLocaleTimeString(),
            level: "info",
            message: "Initializing deployment sequence...",
        },
        {
            id: "2",
            timestamp: new Date().toLocaleTimeString(),
            level: "success",
            message: "Build environment ready.",
        },
        {
            id: "3",
            timestamp: new Date().toLocaleTimeString(),
            level: "info",
            message: "Fetching dependencies from package.json",
        },
    ]);

    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Auto-scroll to bottom of logs
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    // Simulate incoming logs for demonstration
    useEffect(() => {
        const timer = setInterval(() => {
            const newLog: LogEntry = {
                id: Math.random().toString(36).substr(2, 9),
                timestamp: new Date().toLocaleTimeString(),
                level: Math.random() > 0.8 ? "warning" : "info",
                message: `Deployment progress: ${Math.floor(Math.random() * 100)}% complete...`,
            };
            setLogs((prev) => [...prev.slice(-49), newLog]);
        }, 5000);

        return () => clearInterval(timer);
    }, []);

    return (
        <Card className="bg-slate-900 border-slate-700 flex flex-col h-[400px] overflow-hidden shadow-2xl">
            {/* Terminal Header */}
            <div className="bg-slate-800/80 border-b border-slate-700 px-4 py-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-neon-cyan" />
                    <span className="text-xs font-mono font-medium text-slate-300">Live Deployment Logs</span>
                </div>
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                        <span className="text-[10px] font-mono text-green-400">CONNECTED</span>
                    </div>
                    <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                        <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                        <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                    </div>
                </div>
            </div>

            {/* Terminal Content */}
            <div
                ref={scrollRef}
                className="flex-1 p-4 font-mono text-[11px] sm:text-xs overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent space-y-1.5"
            >
                {logs.map((log) => (
                    <div key={log.id} className="flex gap-3 animate-in fade-in slide-in-from-left-2 duration-300">
                        <span className="text-slate-500 flex-shrink-0">[{log.timestamp}]</span>
                        <span className={cn(
                            "font-semibold flex-shrink-0 uppercase",
                            log.level === "info" && "text-blue-400",
                            log.level === "success" && "text-green-400",
                            log.level === "warning" && "text-yellow-400",
                            log.level === "error" && "text-red-400",
                        )}>
                            {log.level}:
                        </span>
                        <span className="text-slate-300 break-all">{log.message}</span>
                    </div>
                ))}
                <div className="flex gap-2 items-center text-slate-400 animate-pulse">
                    <span>&gt;</span>
                    <div className="w-2 h-4 bg-slate-400" />
                </div>
            </div>

            {/* Terminal Footer */}
            <div className="px-4 py-2 bg-slate-800/40 border-t border-slate-700/50 flex items-center justify-between">
                <span className="text-[10px] text-slate-500 font-mono">Process-ID: 8842</span>
                <div className="flex gap-3">
                    <button className="text-slate-500 hover:text-white transition-colors">
                        <RefreshCw className="w-3 h-3" />
                    </button>
                    <button className="text-slate-500 hover:text-white transition-colors">
                        <Maximize2 className="w-3 h-3" />
                    </button>
                </div>
            </div>
        </Card>
    );
}
