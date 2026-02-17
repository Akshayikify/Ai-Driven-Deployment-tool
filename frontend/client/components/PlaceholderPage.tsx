import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";

interface PlaceholderPageProps {
  title: string;
  description: string;
}

export default function PlaceholderPage({
  title,
  description,
}: PlaceholderPageProps) {
  return (
    <Layout>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="text-center max-w-2xl mx-auto px-6">
          <div className="w-24 h-24 bg-gradient-to-br from-brand-500 to-brand-700 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-xl animate-float">
            <span className="text-4xl">🚧</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-brand-600 to-purple-600 bg-clip-text text-transparent">
              {title}
            </span>
          </h1>

          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            {description}
          </p>

          <div className="bg-white/60 backdrop-blur-md rounded-2xl p-8 shadow-lg border border-white/20 mb-8">
            <p className="text-gray-700 mb-4">
              This page is currently under construction. In the meantime, you
              can:
            </p>
            <ul className="text-left space-y-2 text-gray-600">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-brand-500 rounded-full"></div>
                <span>Explore our main features on the homepage</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-brand-500 rounded-full"></div>
                <span>Try our interactive demo</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-brand-500 rounded-full"></div>
                <span>Contact us for more information</span>
              </li>
            </ul>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              className="bg-gradient-to-r from-brand-500 to-brand-700 text-white hover:from-brand-600 hover:to-brand-800 shadow-lg hover:shadow-xl transition-all duration-300"
              onClick={() => (window.location.href = "/")}
            >
              Return Home
              <span className="ml-2">🏠</span>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-brand-200 text-brand-600 hover:bg-brand-50 shadow-lg hover:shadow-xl transition-all duration-300"
            >
              Contact Us
              <span className="ml-2">📧</span>
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
