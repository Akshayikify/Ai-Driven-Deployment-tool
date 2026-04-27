import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Rocket, Calendar, Shield, Zap, Heart } from "lucide-react";

export default function CTASection() {
  const navigate = useNavigate();

  const handleStartTrial = () => {
    navigate('/signup');
  };

  return (
    <section className="py-24 bg-slate-900 relative overflow-hidden">
      {/* Subtle Pattern Background */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
      </div>

      <div className="container mx-auto px-6 text-center relative z-10 max-w-7xl">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-6xl font-extrabold mb-8 text-white leading-tight tracking-tight">
              Ready to ship <span className="text-blue-400">faster?</span>
            </h2>

            <p className="text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
              Join the growing number of teams who use AutoDeploy.ai to automate their 
              infrastructure and focus on what matters most—their code.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-20">
              <Button
                size="lg"
                onClick={handleStartTrial}
                className="w-full sm:w-auto h-14 px-10 bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg rounded-xl shadow-xl shadow-blue-600/20 transition-all"
              >
                Get Started for Free
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={handleStartTrial}
                className="w-full sm:w-auto h-14 px-10 border-slate-700 text-white hover:bg-slate-800 font-bold text-lg rounded-xl transition-all"
              >
                Schedule a Demo
              </Button>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: <Shield className="w-5 h-5" />, title: "Enterprise Grade", desc: "SOC2 Type II Compliant" },
              { icon: <Zap className="w-5 h-5" />, title: "Instant Setup", desc: "No configuration needed" },
              { icon: <Heart className="w-5 h-5" />, title: "Dev Centric", desc: "Built by engineers, for engineers" },
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center p-6 rounded-2xl bg-slate-800/50 border border-slate-700/50">
                <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-blue-400 mb-4">
                  {item.icon}
                </div>
                <h4 className="text-sm font-bold text-white mb-1 uppercase tracking-widest">{item.title}</h4>
                <p className="text-xs text-slate-500 font-medium">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
