import React, { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Terminal, Maximize2, RefreshCw, Circle, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useDeployment } from "@/context/DeploymentContext";
import { useAuth } from "@clerk/clerk-react";

interface LogEntry {
    id: string;
    timestamp: string;
    level: "info" | "success" | "warning" | "error";
    message: string;
    autoFix?: {
        diagnosis: string;
        actions: any[];
    };
}

export default function LogMonitoringCard({ className }: { className?: string }) {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [isFixing, setIsFixing] = useState(false);

    const { repoUrl } = useDeployment();
    const { userId } = useAuth();

    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    useEffect(() => {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
        const eventSource = new EventSource(`${baseUrl}/api/v1/logs/stream`);

        eventSource.onmessage = (event) => {
            const logText = event.data;
            const parts = logText.split(" | ");
            if (parts.length >= 3) {
                let actualMessage = parts.slice(2).join(" | ");
                let autoFixInfo = undefined;

                if (actualMessage.includes("[AUTO_FIX_PAYLOAD]")) {
                    try {
                        const jsonStr = actualMessage.replace("[AUTO_FIX_PAYLOAD]", "").trim();
                        autoFixInfo = JSON.parse(jsonStr);
                        actualMessage = "[AI DevOps Agent] 💡 Diagnosis: " + autoFixInfo.diagnosis;
                    } catch (e) {
                        console.error("Failed to parse autofix payload", e);
                    }
                }

                const newLog: LogEntry = {
                    id: Math.random().toString(36).substr(2, 9),
                    timestamp: parts[0],
                    level: parts[1].toLowerCase() as any,
                    message: actualMessage,
                    autoFix: autoFixInfo
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

    const applyAutoFix = async (actions: any[]) => {
        if (!repoUrl || !userId) return;
        setIsFixing(true);
        try {
            const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
            const res = await fetch(`${baseUrl}/api/v1/analyze/auto-fix`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ repo_url: repoUrl, user_id: userId, actions })
            });
            if (res.ok) {
                setLogs(prev => [...prev, {
                    id: Math.random().toString(36).substr(2, 9),
                    timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
                    level: "success",
                    message: "[System] Auto-Fix applied! A new GitHub Action pipeline should trigger momentarily."
                }]);
            } else {
                setLogs(prev => [...prev, {
                    id: Math.random().toString(36).substr(2, 9),
                    timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
                    level: "error",
                    message: "[System] Failed to apply Auto-Fix to the repository."
                }]);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setIsFixing(false);
        }
    };

    return (
        <Card className={cn("bg-slate-950 border-slate-800 flex flex-col overflow-hidden shadow-sm rounded-xl", className)}>
            {/* Terminal Header */}
            <div className="bg-slate-900 border-b border-slate-800 px-4 py-2.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Terminal className="w-4 h-4 text-slate-400" />
                    <span className="text-xs font-bold font-mono tracking-tight text-slate-200">System Logs</span>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <span className="relative flex h-1.5 w-1.5">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
                        </span>
                        <span className="text-[10px] font-bold font-mono text-green-500 uppercase tracking-widest">Live</span>
                    </div>
                    <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-slate-800" />
                        <div className="w-2.5 h-2.5 rounded-full bg-slate-800" />
                        <div className="w-2.5 h-2.5 rounded-full bg-slate-800" />
                    </div>
                </div>
            </div>

            {/* Terminal Content */}
            <div
                ref={scrollRef}
                className="flex-1 p-5 font-mono text-[11px] sm:text-xs overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent space-y-2.5 leading-relaxed"
            >
                {logs.map((log) => (
                    <div key={log.id} className="flex flex-col gap-2 group">
                        <div className="flex gap-4">
                            <span className="text-slate-600 flex-shrink-0 font-medium">[{log.timestamp}]</span>
                            <span className={cn(
                                "font-black flex-shrink-0 uppercase tracking-tighter w-12",
                                log.level === "info" && "text-blue-500",
                                log.level === "success" && "text-green-500",
                                log.level === "warning" && "text-amber-500",
                                log.level === "error" && "text-red-500",
                            )}>
                                {log.level}
                            </span>
                            <span className="text-slate-300 break-all font-medium">{log.message}</span>
                        </div>
                        {log.autoFix && log.autoFix.actions && log.autoFix.actions.length > 0 && (
                            <div className="ml-16 mt-1 mb-2 flex flex-col gap-2">
                                <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/20 max-w-lg">
                                    <p className="text-[10px] text-blue-400 font-bold uppercase mb-2">AI-Driven Solution Available</p>
                                    <Button
                                        size="sm"
                                        onClick={() => applyAutoFix(log.autoFix!.actions)}
                                        disabled={isFixing}
                                        className="bg-blue-600 hover:bg-blue-700 text-white text-[10px] h-8 px-4 font-bold shadow-sm"
                                    >
                                        <Zap className="w-3.5 h-3.5 mr-2" />
                                        {isFixing ? "Processing..." : "Deploy Automatic Fix"}
                                    </Button>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
                {logs.length === 0 && (
                    <div className="flex items-center justify-center h-full text-slate-600 font-mono text-xs">
                        Waiting for log stream...
                    </div>
                )}
                <div className="flex gap-2 items-center text-slate-700 pt-2">
                    <span className="font-black">&gt;</span>
                    <div className="w-1.5 h-4 bg-blue-600/40 animate-pulse" />
                </div>
            </div>

            {/* Terminal Footer */}
            <div className="px-4 py-2 bg-slate-900/50 border-t border-slate-800 flex items-center justify-between">
                <span className="text-[10px] text-slate-600 font-mono font-bold tracking-tight uppercase">Session Active</span>
                <div className="flex gap-4">
                    <button
                        onClick={() => setLogs([])}
                        className="text-slate-600 hover:text-slate-300 transition-colors"
                        title="Clear Logs"
                    >
                        <RefreshCw className="w-3.5 h-3.5" />
                    </button>
                    <button className="text-slate-600 hover:text-slate-300 transition-colors">
                        <Maximize2 className="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>
        </Card>
    );
}
