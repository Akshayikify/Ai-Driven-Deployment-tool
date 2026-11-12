import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { toast } from 'sonner';

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
    deploymentUrl: string | null;
    setDeploymentUrl: (url: string | null) => void;
    openDeploymentUrl: () => void;
}

const defaultSteps: TimelineStep[] = [
    { id: "upload",   title: "Code Uploaded",  description: "Project files successfully uploaded to the platform", status: "pending" },
    { id: "analyze",  title: "AI Analysis",    description: "Analyzing project structure and dependencies",       status: "pending" },
    { id: "security", title: "Security Scan",  description: "Scanning for hardcoded secrets and API keys",        status: "pending" },
    { id: "build",    title: "Build Process",  description: "Building application for deployment",                status: "pending" },
    { id: "minikube_deploy", title: "Deploying To Minikube", description: "Preparing Kubernetes manifests",       status: "pending" },
    { id: "minikube_deployment", title: "Creating Deployment", description: "Applying deployment manifest to cluster", status: "pending" },
    { id: "minikube_service", title: "Creating Service", description: "Applying service manifest to cluster",       status: "pending" },
    { id: "minikube_pods", title: "Waiting For Pods", description: "Waiting for pods to be in Running state",    status: "pending" },
    { id: "minikube_live", title: "Application Live", description: "Deployment is live on local Minikube cluster", status: "pending" },
];

const DeploymentContext = createContext<DeploymentContextType | undefined>(undefined);

export const DeploymentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    // Session-persistent state initialization
    const [activeTaskId, setActiveTaskId] = useState<string | null>(() => {
        try {
            return sessionStorage.getItem("autodeploy_activeTaskId");
        } catch {
            return null;
        }
    });

    const [repoUrl, setRepoUrl] = useState<string | null>(() => {
        try {
            return sessionStorage.getItem("autodeploy_repoUrl");
        } catch {
            return null;
        }
    });

    const [steps, setSteps] = useState<TimelineStep[]>(defaultSteps);
    const [currentMessage, setCurrentMessage] = useState<string>("Ready for deployment");
    const [estimatedDuration, setEstimatedDuration] = useState<string | null>(null);
    const [securityReport, setSecurityReport] = useState<any | null>(null);
    const [awaitingPushConfirmation, setAwaitingPushConfirmation] = useState<boolean>(false);
    const [sessionKey, setSessionKey] = useState<number>(0);
    const [autoFix, setAutoFix] = useState<any | null>(null);

    const [deploymentUrl, setDeploymentUrl] = useState<string | null>(() => {
        try {
            return sessionStorage.getItem("autodeploy_deploymentUrl");
        } catch {
            return null;
        }
    });

    // Reference to prevent duplicate toasts for the same deployment URL
    const lastNotifiedUrlRef = useRef<string | null>(null);

    // Sync activeTaskId to sessionStorage
    useEffect(() => {
        try {
            if (activeTaskId) {
                sessionStorage.setItem("autodeploy_activeTaskId", activeTaskId);
            } else {
                sessionStorage.removeItem("autodeploy_activeTaskId");
            }
        } catch {}
    }, [activeTaskId]);

    // Sync repoUrl to sessionStorage
    useEffect(() => {
        try {
            if (repoUrl) {
                sessionStorage.setItem("autodeploy_repoUrl", repoUrl);
            } else {
                sessionStorage.removeItem("autodeploy_repoUrl");
            }
        } catch {}
    }, [repoUrl]);

    // Sync deploymentUrl to sessionStorage
    useEffect(() => {
        try {
            if (deploymentUrl) {
                sessionStorage.setItem("autodeploy_deploymentUrl", deploymentUrl);
            } else {
                sessionStorage.removeItem("autodeploy_deploymentUrl");
            }
        } catch {}
    }, [deploymentUrl]);

    const resetSession = () => {
        setActiveTaskId(null);
        setRepoUrl(null);
        setSteps(defaultSteps);
        setCurrentMessage("Ready for deployment");
        setEstimatedDuration(null);
        setSecurityReport(null);
        setAwaitingPushConfirmation(false);
        setAutoFix(null);
        setDeploymentUrl(null);
        lastNotifiedUrlRef.current = null;
        try {
            sessionStorage.removeItem("autodeploy_activeTaskId");
            sessionStorage.removeItem("autodeploy_repoUrl");
            sessionStorage.removeItem("autodeploy_deploymentUrl");
        } catch {}
        setSessionKey(k => k + 1); // signal all subscribers to reset
    };

    const openDeploymentUrl = () => {
        if (deploymentUrl) {
            window.open(deploymentUrl, "_blank", "noopener,noreferrer");
        }
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
                        setSteps(data.steps || defaultSteps);
                        setCurrentMessage(data.current_message || "");
                        if (data.estimated_duration) {
                            setEstimatedDuration(data.estimated_duration);
                        }
                        if (data.security_report) {
                            setSecurityReport(data.security_report);
                        }
                        if (data.auto_fix) {
                            setAutoFix(data.auto_fix);
                        }
                        
                        const detectedUrl = data.deployment_url || data.application_url;
                        if (detectedUrl) {
                            setDeploymentUrl(detectedUrl);

                            // Notify the user if this URL hasn't been notified yet
                            if (lastNotifiedUrlRef.current !== detectedUrl) {
                                lastNotifiedUrlRef.current = detectedUrl;
                                toast.success("Application Successfully Deployed! 🚀", {
                                    description: `Your application is live and accessible at ${detectedUrl}`,
                                    action: {
                                        label: "Visit App",
                                        onClick: () => window.open(detectedUrl, "_blank", "noopener,noreferrer"),
                                    },
                                    duration: 15000,
                                });
                            }
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
            // Note: We deliberately preserve deploymentUrl from sessionStorage if one exists from the session
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
        <DeploymentContext.Provider value={{
            activeTaskId,
            setActiveTaskId,
            repoUrl,
            setRepoUrl,
            steps,
            currentMessage,
            estimatedDuration,
            securityReport,
            awaitingPushConfirmation,
            confirmPush,
            cancelPush,
            sessionKey,
            resetSession,
            autoFix,
            deploymentUrl,
            setDeploymentUrl,
            openDeploymentUrl
        }}>
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
