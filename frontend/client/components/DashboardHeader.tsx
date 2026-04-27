import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X, ShieldCheck } from "lucide-react";

export default function DashboardHeader() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-white/95 dark:bg-slate-950/95 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800 transition-all duration-300 shadow-sm">
      <div className="container mx-auto px-4 sm:px-6 py-4 max-w-7xl">
        <nav className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-md transition-transform hover:scale-105">
                <ShieldCheck className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-black text-slate-900 dark:text-white tracking-tight leading-none">
                  AutoDeploy.ai
                </h1>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-1">
                  Intelligent Infrastructure
                </p>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6 lg:space-x-8">
            {['Home', 'Features', 'Workflow', 'Contact'].map((item) => (
              <a
                key={item}
                href={item === 'Home' ? '/' : `/${item.toLowerCase()}`}
                className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-all duration-300 font-bold uppercase tracking-widest text-xs"
              >
                {item}
              </a>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center">
            <button
              onClick={toggleMobileMenu}
              className="md:hidden p-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </nav>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden mt-4 pb-6 border-t border-slate-100 dark:border-slate-800 animate-in slide-in-from-top-2">
            <div className="flex flex-col space-y-4 pt-6">
              {['Home', 'Features', 'Workflow', 'Contact'].map((item) => (
                <a
                  key={item}
                  href={item === 'Home' ? '/' : `/${item.toLowerCase()}`}
                  className="text-sm font-bold text-slate-600 dark:text-slate-400 hover:text-blue-600 uppercase tracking-widest px-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
