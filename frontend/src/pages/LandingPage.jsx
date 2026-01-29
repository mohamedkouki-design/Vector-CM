import { Link } from 'react-router-dom';
import { Sparkles, Shield, TrendingUp } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-6xl w-full">
        {/* Hero Section */}
        <div className="text-center mb-16 animate-slide-down">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 neon-text">
            Vector CM
          </h1>
          <p className="text-2xl md:text-3xl text-gray-300 mb-4">
            Self-Evolving Multimodal Credit Intelligence
          </p>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Transforming credit scoring for the informal economy through 
            vector similarity and AI-powered insights
          </p>
        </div>
        
        {/* Role Selection Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Client Portal */}
          <Link to="/client" className="group">
            <div className="glass-card h-full hover:scale-105 transform transition-all duration-300 cursor-pointer glow-border">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-accent-cyan to-accent-purple rounded-full flex items-center justify-center mx-auto mb-6 group-hover:animate-pulse-glow">
                  <Sparkles className="w-10 h-10 text-white" />
                </div>
                
                <h2 className="text-3xl font-bold mb-4 text-gradient">
                  Client Portal
                </h2>
                
                <p className="text-gray-300 mb-6">
                  Simple, friendly interface for informal workers to apply 
                  for credit and track their applications
                </p>
                
                <ul className="text-left space-y-3 text-gray-400 mb-8">
                  <li className="flex items-start gap-2">
                    <span className="text-accent-cyan mt-1">✓</span>
                    <span>Easy application process</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent-cyan mt-1">✓</span>
                    <span>Upload documents via mobile</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent-cyan mt-1">✓</span>
                    <span>Track application status</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent-cyan mt-1">✓</span>
                    <span>Get improvement advice</span>
                  </li>
                </ul>
                
                <div className="btn-primary w-full">
                  Enter as Client →
                </div>
              </div>
            </div>
          </Link>
          
          {/* Admin Dashboard */}
          <Link to="/admin" className="group">
            <div className="glass-card h-full hover:scale-105 transform transition-all duration-300 cursor-pointer glow-border">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-accent-purple to-accent-pink rounded-full flex items-center justify-center mx-auto mb-6 group-hover:animate-pulse-glow">
                  <Shield className="w-10 h-10 text-white" />
                </div>
                
                <h2 className="text-3xl font-bold mb-4 text-gradient">
                  Admin Command Center
                </h2>
                
                <p className="text-gray-300 mb-6">
                  Powerful analytics and decision tools for credit officers 
                  and risk analysts
                </p>
                
                <ul className="text-left space-y-3 text-gray-400 mb-8">
                  <li className="flex items-start gap-2">
                    <span className="text-accent-purple mt-1">✓</span>
                    <span>3D Galaxy View visualization</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent-purple mt-1">✓</span>
                    <span>AI-powered fraud detection</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent-purple mt-1">✓</span>
                    <span>Counterfactual analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent-purple mt-1">✓</span>
                    <span>Temporal evolution tracking</span>
                  </li>
                </ul>
                
                <div className="btn-primary w-full">
                  Enter as Admin →
                </div>
              </div>
            </div>
          </Link>
        </div>
        
        {/* Features Grid */}
        <div className="mt-20 grid md:grid-cols-3 gap-6 animate-slide-up">
          <div className="glass-card text-center">
            <TrendingUp className="w-10 h-10 text-accent-cyan mx-auto mb-4" />
            <h3 className="font-semibold text-lg mb-2">Evidence-Based</h3>
            <p className="text-gray-400 text-sm">
              50 similar cases, not black-box predictions
            </p>
          </div>
          
          <div className="glass-card text-center">
            <Sparkles className="w-10 h-10 text-accent-purple mx-auto mb-4" />
            <h3 className="font-semibold text-lg mb-2">AI-Powered</h3>
            <p className="text-gray-400 text-sm">
              LLM-generated explanations for every decision
            </p>
          </div>
          
          <div className="glass-card text-center">
            <Shield className="w-10 h-10 text-accent-pink mx-auto mb-4" />
            <h3 className="font-semibold text-lg mb-2">Fraud-Resistant</h3>
            <p className="text-gray-400 text-sm">
              Vector fingerprinting detects synthetic identities
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}