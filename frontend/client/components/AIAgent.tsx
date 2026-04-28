import React, { useState, useRef, useEffect } from "react";
import { useDeployment } from "@/context/DeploymentContext";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Bot, MessageCircle, Zap, Brain, Sparkles, Send, User, RefreshCw } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import { useAuth, useUser } from "@clerk/clerk-react";
import { cn } from "@/lib/utils";

interface AIAgentProps {
  className?: string;
}

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
}

export default function AIAgent({ className }: AIAgentProps) {
  const { userId } = useAuth();
  const { user } = useUser();
  const hasGitHub = user?.externalAccounts?.some(account => account.provider === 'github');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "agent",
      content: "Hello! I'm your AI Deployment Assistant. Paste a GitHub repository link or ask me anything about your deployment process!",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [currentTask, setCurrentTask] = useState("Ready to assist with your deployment...");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { setActiveTaskId, setRepoUrl } = useDeployment();

  const agentCapabilities = [
    { icon: Brain, label: "Code Analysis", status: "active" },
    { icon: Zap, label: "Optimization", status: "ready" },
    { icon: Sparkles, label: "AI Insights", status: "ready" },
  ];

  const clearChat = () => {
    setMessages([
      {
        id: Date.now().toString(),
        type: "agent",
        content: "Hello! I'm your AI Deployment Assistant. Paste a GitHub repository link or ask me anything about your deployment process!",
        timestamp: new Date(),
      },
    ]);
    setInputValue("");
    setCurrentTask("Ready to assist with your deployment...");
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleRepositoryAnalysis = async (url: string) => {
    setIsTyping(true);
    setCurrentTask("Analyzing repository structure...");

    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
    try {
      const response = await fetch(`${baseUrl}/api/v1/analyze/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: url,
          branch: "main",
          user_id: userId || null
        }),
      });

      const data = await response.json();

      // Update the global active task ID and repo URL to trigger timeline and auto-fix capabilities
      if (data.task_id) {
        setActiveTaskId(data.task_id);
        setRepoUrl(url);
      }

      const agentResponse: Message = {
        id: Date.now().toString(),
        type: 'agent',
        content: `### Repository Analysis Initiated\n\nI've detected a GitHub repository and started the automated analysis process.\n\n**Task Details:**\n- **ID:** \`${data.task_id}\`\n- **Status:** ⏳ Queued\n\n**Authentication Status:**\n${hasGitHub ? "✅ **GitHub Linked:** I have access to your repository and can push automated deployment files." : "⚠️ **GitHub Not Linked:** I will perform a local analysis, but I won't be able to push changes or trigger CI/CD pipelines. Please connect your GitHub account in the dashboard for full automation."}\n\n---\n*You can monitor the progress in real-time using the **Deployment Logs** and **Timeline** cards below.*`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, agentResponse]);
    } catch (error) {
      console.error("Analysis failed:", error);
    } finally {
      setIsTyping(false);
      setCurrentTask("Ready to assist with your deployment...");
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Check for GitHub URL
    const githubRegex = /https:\/\/github\.com\/[\w.-]+\/[\w.-]+/;
    const match = inputValue.match(githubRegex);

    if (match) {
      const url = match[0];

      await handleRepositoryAnalysis(url);
      return;
    }

    setIsTyping(true);
    setCurrentTask("Thinking...");

    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
    try {
      const response = await fetch(`${baseUrl}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: inputValue }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();

      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, agentResponse]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
      setCurrentTask("Ready to assist with your deployment...");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card className={cn("bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 flex flex-col h-full shadow-sm", className)}>
      <div className="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center border border-blue-200 dark:border-blue-800">
              <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Deployment Assistant</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Powered by AutoDeploy AI</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className={cn(
                "text-[10px] font-bold uppercase tracking-wider",
                isActive
                  ? "border-green-200 text-green-700 bg-green-50 dark:border-green-900/30 dark:text-green-400 dark:bg-green-900/20"
                  : "border-slate-200 text-slate-500 bg-slate-50 dark:border-slate-800 dark:text-slate-400 dark:bg-slate-800/50",
              )}
            >
              {isActive ? "Connected" : "Standby"}
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              onClick={clearChat}
              className="w-8 h-8 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              title="Reset Conversation"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/20 dark:bg-slate-950/20 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-4",
              message.type === 'user' ? "justify-end" : "justify-start"
            )}
          >
            {message.type === 'agent' && (
              <div className="w-9 h-9 rounded-xl bg-white dark:bg-slate-800 flex items-center justify-center flex-shrink-0 border border-slate-200 dark:border-slate-700 shadow-sm">
                <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
            )}
            <div
              className={cn(
                "max-w-[80%] p-5 rounded-2xl text-sm leading-relaxed shadow-sm",
                message.type === 'user'
                  ? "bg-blue-600 text-white rounded-tr-none font-medium"
                  : "bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-800 rounded-tl-none"
              )}
            >
              {message.type === 'agent' ? (
                <div className="prose prose-sm dark:prose-invert max-w-none prose-slate prose-p:leading-relaxed prose-p:font-medium">
                  <ReactMarkdown>
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <span className="whitespace-pre-wrap">{message.content}</span>
              )}
            </div>
            {message.type === 'user' && (
              <div className="w-9 h-9 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 border border-slate-200 dark:border-slate-700 shadow-sm">
                <User className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              </div>
            )}
          </div>
        ))}
        {isTyping && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
              <Bot className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            </div>
            <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl rounded-tl-none border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="flex gap-1.5">
                <div className="w-1.5 h-1.5 bg-slate-300 dark:bg-slate-600 rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-slate-300 dark:bg-slate-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-1.5 h-1.5 bg-slate-300 dark:bg-slate-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
        <div className="relative group">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your deployment or paste a repo URL..."
            className="w-full bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white placeholder:text-slate-400 resize-none pr-14 focus-visible:ring-blue-500 rounded-xl min-h-[100px] transition-all"
            rows={3}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="absolute right-3 bottom-3 bg-blue-600 hover:bg-blue-700 text-white w-10 h-10 p-0 rounded-lg shadow-sm transition-all"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 mt-4">
          <Button
            variant="outline"
            size="sm"
            className="text-xs font-semibold border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            onClick={() => setInputValue("Analyze my project structure")}
          >
            Analyze Project
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs font-semibold border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            onClick={() => setInputValue("Optimize my CI/CD workflow")}
          >
            Optimize Workflow
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs font-semibold border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            onClick={() => setInputValue("Check deployment security")}
          >
            Security Audit
          </Button>
        </div>
      </div>
    </Card>
  );
}
