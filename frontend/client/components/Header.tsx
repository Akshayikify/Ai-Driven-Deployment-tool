import { Button } from "@/components/ui/button";
import { DarkModeToggle } from "@/components/DarkModeToggle";
import { Menu, X, LogOut, User } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
  useUser,
  useClerk
} from "@clerk/clerk-react";

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, isSignedIn } = useUser();
  const { signOut } = useClerk();
  const navigate = useNavigate();

  const handleNavClick = (section: string) => {
    if (section === 'contact') {
      // Scroll to footer
      const footer = document.getElementById('footer');
      if (footer) {
        footer.scrollIntoView({ behavior: 'smooth' });
      }
    } else if (section === 'features') {
      // Navigate to features page
      navigate('/features');
    } else if (section === 'workflow') {
      // Navigate to workflow page
      navigate('/workflow');
    } else {
      // Navigate to home page for other sections
      navigate('/');
    }
    setIsMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-white/10 dark:bg-black/10 backdrop-blur-lg border border-white/20 dark:border-white/10 shadow-2xl transition-all duration-300">
      <div className="container mx-auto px-4 sm:px-6 py-4">
        <nav className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <span className="text-xl sm:text-2xl font-bold gradient-text-neon font-mono tracking-tight">
              Auto Deploy.AI
            </span>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6 lg:space-x-8">
            <Link
              to="/"
              className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Home
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </Link>
            <button
              onClick={() => handleNavClick('features')}
              className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Features
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </button>
            <button
              onClick={() => handleNavClick('workflow')}
              className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Workflow
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </button>
            <button
              onClick={() => handleNavClick('contact')}
              className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-all duration-300 font-medium relative group text-sm lg:text-base"
            >
              Contact
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-blue to-neon-cyan group-hover:w-full transition-all duration-300"></span>
            </button>
          </div>

          {/* Right Side Buttons */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <DarkModeToggle />

            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>

            <SignedOut>
              <div className="hidden sm:flex space-x-2">
                <Button
                  variant="ghost"
                  className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan border border-transparent hover:border-neon-blue/30 dark:hover:border-neon-cyan/30 transition-all duration-300 rounded-xl text-sm"
                  asChild
                >
                  <Link to="/login">Login</Link>
                </Button>
                <Button
                  className="bg-neon-blue text-white hover:bg-neon-blue/90 border border-neon-blue hover:border-neon-blue/80 transition-all duration-300 rounded-xl text-sm px-3 sm:px-4 shadow-lg hover:shadow-xl"
                  asChild
                >
                  <Link to="/signup">Signup</Link>
                </Button>
              </div>
            </SignedOut>

            {/* Mobile Menu Button */}
            <button
              onClick={toggleMobileMenu}
              className="md:hidden p-2 text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-colors"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </nav>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-gray-200/30 dark:border-neon-blue/20">
            <div className="flex flex-col space-y-3 pt-4">
              <Link
                to="/"
                className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Home
              </Link>
              <button
                onClick={() => handleNavClick('features')}
                className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50 text-left"
              >
                Features
              </button>
              <button
                onClick={() => handleNavClick('workflow')}
                className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50 text-left"
              >
                Workflow
              </button>
              <button
                onClick={() => handleNavClick('contact')}
                className="text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan transition-all duration-300 font-medium px-2 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50 text-left"
              >
                Contact
              </button>
              <div className="pt-2 border-t border-gray-200/30 dark:border-neon-blue/20">
                <SignedIn>
                  <div className="px-2 py-2">
                    <UserButton afterSignOutUrl="/" showName />
                  </div>
                </SignedIn>
                <SignedOut>
                  <Button
                    variant="ghost"
                    className="w-full text-left text-gray-700 dark:text-gray-300 hover:text-neon-blue dark:hover:text-neon-cyan border border-transparent hover:border-neon-blue/30 dark:hover:border-neon-cyan/30 transition-all duration-300 rounded-xl mb-2"
                    onClick={() => {
                      navigate("/login");
                      setIsMobileMenuOpen(false);
                    }}
                  >
                    Login
                  </Button>
                  <Button
                    className="w-full text-left bg-neon-blue text-white hover:bg-neon-blue/90 border border-neon-blue hover:border-neon-blue/80 transition-all duration-300 rounded-xl"
                    onClick={() => {
                      navigate("/signup");
                      setIsMobileMenuOpen(false);
                    }}
                  >
                    Signup
                  </Button>
                </SignedOut>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
