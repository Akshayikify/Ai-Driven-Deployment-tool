import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function DashboardSection() {
  const [activeTab, setActiveTab] = useState(0);

  const dashboardViews = [
    {
      title: "Deployment Pipeline",
      description:
        "Visualize your entire deployment process with real-time status updates",
      features: [
        "Live status tracking",
        "Automated rollbacks",
        "Multi-environment support",
      ],
    },
    {
      title: "Logs Monitoring",
      description:
        "Intelligent log aggregation with AI-powered error detection and filtering",
      features: [
        "Real-time log streaming",
        "Smart filtering",
        "Error highlighting",
      ],
    },
    {
      title: "AI Insights",
      description:
        "Predictive analytics and intelligent recommendations for optimal performance",
      features: [
        "Performance predictions",
        "Config suggestions",
        "Resource optimization",
      ],
    },
  ];

  return (
    <section className="py-24 bg-background relative overflow-hidden">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-brand-600 to-purple-600 bg-clip-text text-transparent">
              Dashboard Preview
            </span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-white max-w-3xl mx-auto">
            Experience the power of AI-driven deployment management through our
            intuitive dashboard
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap justify-center mb-12 gap-4">
          {dashboardViews.map((view, index) => (
            <Button
              key={index}
              variant={activeTab === index ? "default" : "outline"}
              onClick={() => setActiveTab(index)}
              className={`text-lg px-6 py-3 transition-all duration-300 ${
                activeTab === index
                  ? "bg-gradient-to-r from-brand-500 to-brand-700 text-white shadow-lg"
                  : "border-brand-200 text-brand-600 hover:bg-brand-50"
              }`}
            >
              {view.title}
            </Button>
          ))}
        </div>

        {/* Dashboard Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Side - Info */}
          <div className="space-y-6">
            <h3 className="text-4xl font-bold text-gray-900 dark:text-white">
              {dashboardViews[activeTab].title}
            </h3>
            <p className="text-xl text-gray-600 dark:text-white leading-relaxed">
              {dashboardViews[activeTab].description}
            </p>

            <ul className="space-y-3">
              {dashboardViews[activeTab].features.map((feature, index) => (
                <li key={index} className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-gradient-to-r from-brand-500 to-brand-700 rounded-full"></div>
                  <span className="text-gray-700 dark:text-white">{feature}</span>
                </li>
              ))}
            </ul>

          </div>

          {/* Right Side - Dashboard Mockup */}
          <div className="relative">
            {/* Browser Window Frame */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden transform hover:scale-105 transition-transform duration-500">
              {/* Browser Header */}
              <div className="bg-gray-100 dark:bg-gray-700 px-4 py-3 flex items-center space-x-2 border-b border-gray-200 dark:border-gray-600">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <div className="flex-1 bg-white dark:bg-gray-200 rounded px-3 py-1 text-sm text-gray-600 dark:text-gray-800 ml-4">
                  autodeploy.ai/dashboard
                </div>
              </div>

              {/* Dashboard Content */}
              <div className="p-6 h-80 bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-800 dark:to-gray-700">
                {activeTab === 0 && (
                  // Deployment Pipeline View
                  <div className="space-y-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold text-gray-800">
                        Current Deployments
                      </h4>
                      <div className="flex space-x-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-gray-600 dark:text-white">3 Active</span>
                      </div>
                    </div>

                    {/* Pipeline Steps */}
                    <div className="space-y-3">
                      <div className="bg-white rounded-lg p-3 shadow-sm border-l-4 border-green-500">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-sm dark:text-white">
                            Frontend App
                          </span>
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                            Deployed
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div className="bg-green-500 h-2 rounded-full w-full"></div>
                        </div>
                      </div>

                      <div className="bg-white rounded-lg p-3 shadow-sm border-l-4 border-blue-500">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-sm dark:text-white">
                            API Service
                          </span>
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            Deploying
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div className="bg-blue-500 h-2 rounded-full w-3/4 animate-pulse"></div>
                        </div>
                      </div>

                      <div className="bg-white rounded-lg p-3 shadow-sm border-l-4 border-yellow-500">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-sm dark:text-white">
                            Database Migration
                          </span>
                          <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                            Queued
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div className="bg-yellow-500 h-2 rounded-full w-1/4"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 1 && (
                  // Logs Monitoring View
                  <div className="space-y-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold text-gray-800">Live Logs</h4>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-gray-600 dark:text-white">Live</span>
                      </div>
                    </div>

                    <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-green-400 h-56 overflow-y-auto">
                      <div className="space-y-1">
                        <div className="text-gray-500">
                          [2024-01-15 14:32:15] INFO: Starting deployment
                          process...
                        </div>
                        <div className="text-blue-400">
                          [2024-01-15 14:32:16] DEBUG: Loading configuration...
                        </div>
                        <div className="text-green-400">
                          [2024-01-15 14:32:17] SUCCESS: Container built
                          successfully
                        </div>
                        <div className="text-yellow-400">
                          [2024-01-15 14:32:18] WARN: High memory usage detected
                        </div>
                        <div className="text-green-400">
                          [2024-01-15 14:32:19] INFO: Deploying to production...
                        </div>
                        <div className="text-red-400">
                          [2024-01-15 14:32:20] ERROR: Connection timeout
                        </div>
                        <div className="text-blue-400">
                          [2024-01-15 14:32:21] INFO: Retrying connection...
                        </div>
                        <div className="text-green-400 animate-pulse">
                          [2024-01-15 14:32:22] SUCCESS: Deployment completed ✓
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 2 && (
                  // AI Insights View
                  <div className="space-y-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold text-gray-800">
                        AI Recommendations
                      </h4>
                      <div className="w-6 h-6 bg-gradient-to-r from-brand-500 to-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs">🤖</span>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4 border-l-4 border-blue-500">
                        <div className="flex items-start space-x-3">
                          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-white text-xs">💡</span>
                          </div>
                          <div>
                            <h5 className="font-medium text-blue-900 mb-1">
                              Scaling Recommendation
                            </h5>
                            <p className="text-sm text-blue-700">
                              Predicted config update needed for scaling.
                              Consider increasing memory allocation by 25%.
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4 border-l-4 border-green-500">
                        <div className="flex items-start space-x-3">
                          <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-white text-xs">⚡</span>
                          </div>
                          <div>
                            <h5 className="font-medium text-green-900 mb-1">
                              Performance Optimization
                            </h5>
                            <p className="text-sm text-green-700">
                              Database queries can be optimized. Implementing
                              caching could improve response time by 40%.
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4 border-l-4 border-purple-500">
                        <div className="flex items-start space-x-3">
                          <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-white text-xs">🔒</span>
                          </div>
                          <div>
                            <h5 className="font-medium text-purple-900 mb-1">
                              Security Alert
                            </h5>
                            <p className="text-sm text-purple-700">
                              Outdated dependency detected. Update recommended
                              for security patch.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Floating Elements */}
            <div className="absolute -top-4 -right-4 w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-700 rounded-full animate-float"></div>
            <div
              className="absolute -bottom-4 -left-4 w-6 h-6 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full animate-float"
              style={{ animationDelay: "1s" }}
            ></div>
          </div>
        </div>
      </div>
    </section>
  );
}
