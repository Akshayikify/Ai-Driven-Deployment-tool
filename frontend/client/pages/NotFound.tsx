import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Home, AlertCircle } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname,
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-white dark:bg-slate-950 px-6">
      <div className="text-center max-w-md w-full">
        <div className="w-20 h-20 bg-slate-50 dark:bg-slate-900 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-slate-100 dark:border-slate-800 shadow-sm">
          <AlertCircle className="w-10 h-10 text-slate-400" />
        </div>
        
        <h1 className="text-8xl font-black text-slate-900 dark:text-white tracking-tighter mb-4">404</h1>
        
        <div className="space-y-2 mb-10">
          <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200 uppercase tracking-widest">Page not found</h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">
            The link you followed may be broken, or the page may have been removed.
          </p>
        </div>

        <Button 
          asChild
          size="lg"
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 rounded-xl shadow-lg shadow-blue-600/20 transition-all"
        >
          <Link to="/" className="flex items-center gap-2">
            <Home className="w-4 h-4" />
            Return to Home
          </Link>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
