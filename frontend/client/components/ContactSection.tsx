import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { motion } from "framer-motion";

export default function ContactSection() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const subject = `Contact from ${name} (AutoDeploy.ai)`;
    const body = `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`;
    const mailtoLink = `mailto:sumams758@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.location.href = mailtoLink;
  };

  return (
    <section id="contact" className="py-24 bg-white dark:bg-slate-950 border-t border-slate-100 dark:border-slate-900">
      <div className="container mx-auto px-6 max-w-4xl">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-extrabold text-slate-900 dark:text-white mb-4 tracking-tight">
            Contact Us
          </h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          viewport={{ once: true }}
        >
          <form onSubmit={handleSubmit} className="space-y-8 bg-slate-50 dark:bg-slate-900/50 p-8 md:p-12 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-3">
                <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-widest ml-1">
                  Name
                </label>
                <Input
                  placeholder="Your full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="h-12 bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 rounded-xl transition-all"
                  required
                />
              </div>
              <div className="space-y-3">
                <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-widest ml-1">
                  Email Address
                </label>
                <Input
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-12 bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 rounded-xl transition-all"
                  required
                />
              </div>
            </div>
            <div className="space-y-3">
              <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-widest ml-1">
                Your Message
              </label>
              <Textarea
                placeholder="How can we help your team scale?"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 rounded-xl min-h-[160px] transition-all resize-none"
                required
              />
            </div>
            <div className="text-center pt-4">
              <Button
                type="submit"
                className="px-12 py-7 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-xl shadow-blue-500/20 transition-all hover:-translate-y-1 active:translate-y-0"
              >
                Send Message
              </Button>
            </div>
          </form>
        </motion.div>
      </div>
    </section>
  );
}
