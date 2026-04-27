import { Button } from "@/components/ui/button";
import { Menu, X, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  SignedIn,
  SignedOut,
  UserButton,
  useClerk
} from "@clerk/clerk-react";

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { signOut } = useClerk();
  const navigate = useNavigate();

  const handleNavClick = (section: string) => {
    if (section === 'contact') {
      navigate('/contact');
    } else if (section === 'features') {
      navigate('/features');
    } else if (section === 'workflow') {
      navigate('/workflow');
    } else {
      navigate('/');
    }
    setIsMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-all duration-300">
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
          <div className="hidden md:flex items-center space-x-8">
            {['Home', 'Features', 'Workflow', 'Contact'].map((item) => (
              <button
                key={item}
                onClick={() => handleNavClick(item.toLowerCase())}
                className="text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                {item}
              </button>
            ))}
          </div>

          {/* Right Side Buttons */}
          <div className="flex items-center space-x-4">
            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>

            <SignedOut>
              <div className="hidden sm:flex items-center space-x-3">
                <Button
                  variant="ghost"
                  className="text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-blue-600"
                  asChild
                >
                  <Link to="/login">Sign in</Link>
                </Button>
                <Button
                  className="bg-blue-600 text-white hover:bg-blue-700 font-semibold px-5 shadow-sm rounded-lg"
                  asChild
                >
                  <Link to="/signup">Get Started</Link>
                </Button>
              </div>
            </SignedOut>

            {/* Mobile Menu Button */}
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
          <div className="md:hidden mt-4 pb-6 border-t border-slate-100 dark:border-slate-800 animate-in slide-in-from-top-2 duration-200">
            <div className="flex flex-col space-y-4 pt-6">
              {['Home', 'Features', 'Workflow', 'Contact'].map((item) => (
                <button
                  key={item}
                  onClick={() => handleNavClick(item.toLowerCase())}
                  className="text-base font-semibold text-slate-600 dark:text-slate-400 hover:text-blue-600 text-left px-2"
                >
                  {item}
                </button>
              ))}
              <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                <SignedIn>
                  <div className="px-2">
                    <UserButton afterSignOutUrl="/" showName />
                  </div>
                </SignedIn>
                <SignedOut>
                  <div className="space-y-3 px-2">
                    <Button
                      variant="outline"
                      className="w-full justify-start font-semibold"
                      onClick={() => {
                        navigate("/login");
                        setIsMobileMenuOpen(false);
                      }}
                    >
                      Sign in
                    </Button>
                    <Button
                      className="w-full justify-start bg-blue-600 text-white font-semibold"
                      onClick={() => {
                        navigate("/signup");
                        setIsMobileMenuOpen(false);
                      }}
                    >
                      Get Started
                    </Button>
                  </div>
                </SignedOut>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
