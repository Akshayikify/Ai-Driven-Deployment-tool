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

export default function LogMonitoringCard({ className }: { className?: string }) {
    const [logs, setLogs] = useState<LogEntry[]>([]);

    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    useEffect(() => {
        const eventSource = new EventSource("http://127.0.0.1:8000/api/v1/logs/stream");

        eventSource.onmessage = (event) => {
            const logText = event.data;
            // Parse: 09:40:15 | INFO | message
            const parts = logText.split(" | ");
            if (parts.length >= 3) {
                const newLog: LogEntry = {
                    id: Math.random().toString(36).substr(2, 9),
                    timestamp: parts[0],
                    level: parts[1].toLowerCase() as any,
                    message: parts.slice(2).join(" | "),
                };
                setLogs((prev) => [...prev.slice(-99), newLog]);
            }
        };

        eventSource.onerror = (error) => {
            console.error("EventSource failed:", error);
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, []);

    return (
        <Card className={cn("bg-slate-900 border-slate-700 flex flex-col overflow-hidden shadow-2xl", className)}>
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
                    <button
                        onClick={() => setLogs([])}
                        className="text-slate-500 hover:text-white transition-colors active:rotate-180 duration-500"
                        title="Clear Logs"
                    >
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
