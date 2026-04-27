import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import Layout from "@/components/Layout";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import WorkflowSection from "@/components/WorkflowSection";
import DashboardSection from "@/components/DashboardSection";
import BenefitsSection from "@/components/BenefitsSection";
import CTASection from "@/components/CTASection";
import ContactSection from "@/components/ContactSection";

export default function Index() {
  const { hash } = useLocation();

  useEffect(() => {
    if (hash === '#contact') {
      const contactSection = document.getElementById('contact');
      if (contactSection) {
        contactSection.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [hash]);

  return (
    <Layout>
      <HeroSection />
      <FeaturesSection />
      <WorkflowSection />
      <DashboardSection />
      <BenefitsSection />
      <CTASection />
      <ContactSection />
    </Layout>
  );
}
