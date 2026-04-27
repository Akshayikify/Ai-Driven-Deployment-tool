import Header from "@/components/Header";
import ContactSection from "@/components/ContactSection";
import Footer from "@/components/Footer";

export default function Contact() {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <Header />
      <main className="pt-24">
        <ContactSection />
      </main>
      <Footer />
    </div>
  );
}
