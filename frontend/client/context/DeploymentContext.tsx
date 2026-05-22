import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface TimelineStep {
    id: string;
    title: string;
    description: string;
    status: "pending" | "active" | "completed" | "failed";
    timestamp?: string;
}

interface DeploymentContextType {
    activeTaskId: string | null;
    setActiveTaskId: (id: string | null) => void;
    repoUrl: string | null;
    setRepoUrl: (url: string | null) => void;
    steps: TimelineStep[];
    currentMessage: string;
    estimatedDuration: string | null;
    securityReport: any | null;
    awaitingPushConfirmation: boolean;
    confirmPush: () => Promise<void>;
    cancelPush: () => Promise<void>;
    /** Increments every time the user starts a new session. Components watch this to reset local state. */
    sessionKey: number;
    /** Clears all deployment state and starts a fresh session. */
    resetSession: () => void;
    autoFix: any | null;
}

const defaultSteps: TimelineStep[] = [
    { id: "upload",   title: "Code Uploaded",  description: "Project files successfully uploaded to the platform", status: "pending" },
    { id: "analyze",  title: "AI Analysis",    description: "Analyzing project structure and dependencies",       status: "pending" },
    { id: "security", title: "Security Scan",  description: "Scanning for hardcoded secrets and API keys",        status: "pending" },
    { id: "build",    title: "Build Process",  description: "Building application for deployment",                status: "pending" },
    { id: "deploy",   title: "Deployment",     description: "Deploying to production environment",                status: "pending" },
    { id: "monitor",  title: "Monitoring",     description: "Setting up monitoring and alerts",                   status: "pending" },
];

const DeploymentContext = createContext<DeploymentContextType | undefined>(undefined);

export const DeploymentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
    const [repoUrl, setRepoUrl] = useState<string | null>(null);
    const [steps, setSteps] = useState<TimelineStep[]>(defaultSteps);
    const [currentMessage, setCurrentMessage] = useState<string>("Ready for deployment");
    const [estimatedDuration, setEstimatedDuration] = useState<string | null>(null);
    const [securityReport, setSecurityReport] = useState<any | null>(null);
    const [awaitingPushConfirmation, setAwaitingPushConfirmation] = useState<boolean>(false);
    const [sessionKey, setSessionKey] = useState<number>(0);
    const [autoFix, setAutoFix] = useState<any | null>(null);

    const resetSession = () => {
        setActiveTaskId(null);
        setRepoUrl(null);
        setSteps(defaultSteps);
        setCurrentMessage("Ready for deployment");
        setEstimatedDuration(null);
        setSecurityReport(null);
        setAwaitingPushConfirmation(false);
        setAutoFix(null);
        setSessionKey(k => k + 1); // signal all subscribers to reset
    };

    useEffect(() => {
        let intervalId: NodeJS.Timeout;

        if (activeTaskId) {
            let consecutive404s = 0;
            const MAX_404s = 5; // ~20s of 404s before giving up

            const pollStatus = async () => {
                try {
                    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
                    const response = await fetch(`${baseUrl}/api/v1/analyze/status/${activeTaskId}`);

                    if (response.status === 404) {
                        consecutive404s++;
                        console.warn(
                            `Task ${activeTaskId} returned 404 (${consecutive404s}/${MAX_404s}).`,
                            consecutive404s >= MAX_404s
                                ? "Server may have reloaded. Stopping poll."
                                : "Retrying..."
                        );
                        if (consecutive404s >= MAX_404s) {
                            if (intervalId) clearInterval(intervalId);
                        }
                        return; // don't update UI on 404
                    }

                    consecutive404s = 0; // reset on success

                    if (response.ok) {
                        const data = await response.json();
                        setSteps(data.steps);
                        setCurrentMessage(data.current_message);
                        if (data.estimated_duration) {
                            setEstimatedDuration(data.estimated_duration);
                        }
                        if (data.security_report) {
                            setSecurityReport(data.security_report);
                        }
                        if (data.auto_fix) {
                            setAutoFix(data.auto_fix);
                        }
                        // Drive the confirmation modal
                        setAwaitingPushConfirmation(
                            data.status === "awaiting_push_confirmation"
                        );

                        // Stop polling only on truly final states.
                        // NOTE: 'failed' is intentionally omitted — an auto-fix may flip the
                        // task back to 'building', and we must keep polling to catch that.
                        if (data.status === "success" || data.status === "security_warning") {
                            if (intervalId) clearInterval(intervalId);
                        }
                    }
                } catch (error) {
                    console.error("Failed to poll task status:", error);
                }
            };

            // Poll every 4 seconds for responsive UI updates
            pollStatus();
            intervalId = setInterval(pollStatus, 4000);

        } else {
            setSteps(defaultSteps);
            setCurrentMessage("Ready for deployment");
            setEstimatedDuration(null);
            setSecurityReport(null);
            setAwaitingPushConfirmation(false);
            setAutoFix(null);
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [activeTaskId]);

    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

    const confirmPush = async () => {
        if (!activeTaskId) return;
        setAwaitingPushConfirmation(false);
        await fetch(`${baseUrl}/api/v1/analyze/confirm-push/${activeTaskId}`, { method: "POST" });
    };

    const cancelPush = async () => {
        if (!activeTaskId) return;
        setAwaitingPushConfirmation(false);
        await fetch(`${baseUrl}/api/v1/analyze/cancel-push/${activeTaskId}`, { method: "POST" });
    };

    return (
        <DeploymentContext.Provider value={{ activeTaskId, setActiveTaskId, repoUrl, setRepoUrl, steps, currentMessage, estimatedDuration, securityReport, awaitingPushConfirmation, confirmPush, cancelPush, sessionKey, resetSession, autoFix }}>
            {children}
        </DeploymentContext.Provider>
    );
};

export const useDeployment = () => {
    const context = useContext(DeploymentContext);
    if (context === undefined) {
        throw new Error('useDeployment must be used within a DeploymentProvider');
    }
    return context;
};
