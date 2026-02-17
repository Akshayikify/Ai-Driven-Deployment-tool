import Layout from "@/components/Layout";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import WorkflowSection from "@/components/WorkflowSection";
import DashboardSection from "@/components/DashboardSection";
import BenefitsSection from "@/components/BenefitsSection";
import CTASection from "@/components/CTASection";

export default function Index() {
  return (
    <Layout>
      <HeroSection />
      <FeaturesSection />
      <WorkflowSection />
      <DashboardSection />
      <BenefitsSection />
      <CTASection />
    </Layout>
  );
}
