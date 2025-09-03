import React, { useState } from "react";
import { DarkModeToggle } from "@/components/DarkModeToggle";
import { Menu, X } from "lucide-react";

export default function DashboardHeader() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-black/95 backdrop-blur-xl border-b border-slate-800/50 transition-all duration-300">
      <div className="container mx-auto px-4 sm:px-6 py-4">
        <nav className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-neon-blue to-neon-purple rounded-xl flex items-center justify-center transform rotate-3 shadow-lg">
              <span className="text-white font-bold text-lg filter drop-shadow-sm">
                🚀
              </span>
            </div>
            <span className="text-xl sm:text-2xl font-bold gradient-text-neon font-mono tracking-tight">
              AutoDeploy.AI
            </span>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6 lg:space-x-8">
            <a
              href="/"
              className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Home
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </a>
            <a
              href="/features"
              className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Features
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </a>
            <a
              href="/workflow"
              className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Workflow
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </a>
            <a
              href="/pricing"
              className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Pricing
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </a>
            <a
              href="/docs"
              className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Docs
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </a>
            <a
              href="/contact"
              className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Contact
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </a>
          </div>

          {/* Right Side Buttons */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <DarkModeToggle />
            <button className="hidden sm:inline-flex text-slate-300 hover:text-neon-blue border border-transparent hover:border-neon-blue/30 transition-all duration-300 rounded-xl px-3 sm:px-4 py-2 text-sm">
              Login
            </button>
            <button className="bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-cyan hover:to-neon-pink text-white font-semibold shadow-lg hover:shadow-neon-blue/30 transition-all duration-300 transform hover:scale-105 rounded-xl px-3 sm:px-6 py-2 border border-neon-blue/20 text-sm">
              Signup
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={toggleMobileMenu}
              className="md:hidden p-2 text-slate-300 hover:text-neon-blue transition-colors"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </nav>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-slate-800/50">
            <div className="flex flex-col space-y-3 pt-4">
              <a
                href="/"
                className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-slate-800/50"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Home
              </a>
              <a
                href="/features"
                className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-slate-800/50"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Features
              </a>
              <a
                href="/workflow"
                className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-slate-800/50"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Workflow
              </a>
              <a
                href="/pricing"
                className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-slate-800/50"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Pricing
              </a>
              <a
                href="/docs"
                className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-slate-800/50"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Docs
              </a>
              <a
                href="/contact"
                className="text-slate-300 hover:text-neon-blue transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-slate-800/50"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Contact
              </a>
              <div className="pt-2 border-t border-slate-800/50">
                <button className="w-full text-left text-slate-300 hover:text-neon-blue border border-transparent hover:border-neon-blue/30 transition-all duration-300 rounded-xl px-3 py-2">
                  Login
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
