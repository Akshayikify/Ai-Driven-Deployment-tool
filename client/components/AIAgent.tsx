import React, { useState, useRef, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Bot, MessageCircle, Zap, Brain, Sparkles, Send, User } from "lucide-react";
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
  const [isActive, setIsActive] = useState(true);
  const [currentTask, setCurrentTask] = useState(
    "Ready to assist with your deployment...",
  );
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'agent',
      content: "Hello! I'm your AI deployment assistant. How can I help you today?",
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const agentCapabilities = [
    { icon: Brain, label: "Code Analysis", status: "active" },
    { icon: Zap, label: "Optimization", status: "ready" },
    { icon: Sparkles, label: "AI Insights", status: "ready" },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    setIsTyping(true);
    setCurrentTask("Processing your request...");

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "I understand your request. Let me analyze that for you.",
        "Great question! Here's what I found...",
        "I've processed your input. Here's my recommendation:",
        "Based on your deployment needs, I suggest...",
        "Let me help you optimize that configuration."
      ];

      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, agentResponse]);
      setIsTyping(false);
      setCurrentTask("Ready to assist with your deployment...");
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card className={cn("bg-slate-800/50 border-slate-700 flex flex-col h-full", className)}>
      <div className="p-4 border-b border-slate-700/50">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">AI Assistant</h3>
              <p className="text-xs text-slate-400">Spark Intelligence</p>
            </div>
          </div>
          <Badge
            variant="outline"
            className={cn(
              "text-xs border",
              isActive
                ? "border-green-500/30 text-green-400 bg-green-500/10"
                : "border-slate-600 text-slate-400 bg-slate-700/50",
            )}
          >
            {isActive ? "Active" : "Standby"}
          </Badge>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-2",
              message.type === 'user' ? "justify-end" : "justify-start"
            )}
          >
            {message.type === 'agent' && (
              <div className="w-6 h-6 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple flex items-center justify-center flex-shrink-0">
                <Bot className="w-3 h-3 text-white" />
              </div>
            )}
            <div
              className={cn(
                "max-w-[80%] p-3 rounded-lg text-sm",
                message.type === 'user'
                  ? "bg-neon-blue text-white"
                  : "bg-slate-700/50 text-slate-300 border border-slate-600/50"
              )}
            >
              {message.content}
            </div>
            {message.type === 'user' && (
              <div className="w-6 h-6 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0">
                <User className="w-3 h-3 text-white" />
              </div>
            )}
          </div>
        ))}
        {isTyping && (
          <div className="flex gap-2 justify-start">
            <div className="w-6 h-6 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple flex items-center justify-center">
              <Bot className="w-3 h-3 text-white" />
            </div>
            <div className="bg-slate-700/50 p-3 rounded-lg border border-slate-600/50">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-700/50">
        <div className="flex gap-2">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your deployment..."
            className="flex-1 bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 resize-none"
            rows={2}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="bg-neon-blue hover:bg-neon-blue/80 text-white px-3"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-2 mt-3">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 text-xs border-slate-600 text-slate-300 hover:bg-slate-700/50"
            onClick={() => setInputValue("Analyze my project structure")}
          >
            Analyze Project
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1 text-xs border-slate-600 text-slate-300 hover:bg-slate-700/50"
            onClick={() => setInputValue("Optimize deployment")}
          >
            Optimize
          </Button>
        </div>
      </div>
    </Card>
  );
}
