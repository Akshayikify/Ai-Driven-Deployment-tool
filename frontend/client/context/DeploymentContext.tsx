import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface TimelineStep {
    id: string;
    title: string;
    description: string;
    status: "pending" | "active" | "completed";
    timestamp?: string;
}

interface DeploymentContextType {
    activeTaskId: string | null;
    setActiveTaskId: (id: string | null) => void;
    steps: TimelineStep[];
    currentMessage: string;
}

const defaultSteps: TimelineStep[] = [
    {
        id: "upload",
        title: "Code Uploaded",
        description: "Project files successfully uploaded to the platform",
        status: "pending",
    },
    {
        id: "analyze",
        title: "AI Analysis",
        description: "Analyzing project structure and dependencies",
        status: "pending",
    },
    {
        id: "build",
        title: "Build Process",
        description: "Building application for deployment",
        status: "pending",
    },
    {
        id: "deploy",
        title: "Deployment",
        description: "Deploying to production environment",
        status: "pending",
    },
    {
        id: "monitor",
        title: "Monitoring",
        description: "Setting up monitoring and alerts",
        status: "pending",
    },
];

const DeploymentContext = createContext<DeploymentContextType | undefined>(undefined);

export const DeploymentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
    const [steps, setSteps] = useState<TimelineStep[]>(defaultSteps);
    const [currentMessage, setCurrentMessage] = useState<string>("Ready for deployment");

    useEffect(() => {
        let intervalId: NodeJS.Timeout;

        if (activeTaskId) {
            const pollStatus = async () => {
                try {
                    const response = await fetch(`http://127.0.0.1:8000/api/v1/analyze/status/${activeTaskId}`);
                    if (response.ok) {
                        const data = await response.json();
                        setSteps(data.steps);
                        setCurrentMessage(data.current_message);

                        // Stop polling if the task is in a terminal state
                        if (data.current_message.toLowerCase().includes("complete") ||
                            data.current_message.toLowerCase().includes("failed")) {
                            if (intervalId) clearInterval(intervalId);
                        }
                    }
                } catch (error) {
                    console.error("Failed to poll task status:", error);
                }
            };

            // Poll every 2 seconds
            pollStatus();
            intervalId = setInterval(pollStatus, 2000);
        } else {
            setSteps(defaultSteps);
            setCurrentMessage("Ready for deployment");
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [activeTaskId]);

    return (
        <DeploymentContext.Provider value={{ activeTaskId, setActiveTaskId, steps, currentMessage }}>
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
