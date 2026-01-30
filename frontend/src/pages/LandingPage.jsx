import { Link } from 'react-router-dom';
import { Sparkles, Shield, TrendingUp } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center px-4">
      <div className="max-w-6xl w-full">
        {/* Professional Hero Section */}
        <div className="text-center mb-20 animate-slide-down">
          <div className="inline-flex items-center gap-3 mb-6 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-400/30">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
            <span className="text-sm font-semibold text-blue-300">Enterprise Credit Intelligence</span>
          </div>
          
          <h1 className="text-6xl md:text-7xl font-bold mb-6 text-white bg-gradient-to-r from-blue-200 via-slate-100 to-blue-200 bg-clip-text text-transparent">
            Vector CM
          </h1>
          <p className="text-xl md:text-2xl text-slate-300 mb-4">
            Next-Generation Credit Scoring for Emerging Markets
          </p>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
            Advanced vector similarity matching and AI-powered credit intelligence 
            for the informal economy. Evidence-based decisions, not black boxes.
          </p>
        </div>
        
        {/* Role Selection Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-20">
          {/* Client Portal */}
          <Link to="/client" className="group">
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 h-full hover:border-blue-400/50 transform transition-all duration-300 cursor-pointer hover:shadow-xl hover:shadow-blue-500/10">
              <div className="text-left">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center mb-6 group-hover:shadow-lg group-hover:shadow-blue-500/50 transition-all">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                
                <h2 className="text-3xl font-bold mb-3 text-white">
                  Client Portal
                </h2>
                
                <p className="text-slate-400 mb-8 leading-relaxed">
                  Intuitive interface for applicants to submit credit applications and track their progress in real-time
                </p>
                
                <ul className="space-y-3 text-slate-300 mb-8">
                  <li className="flex items-start gap-3">
                    <span className="text-blue-400 font-bold text-lg mt-0.5">→</span>
                    <span>Streamlined application workflow</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-blue-400 font-bold text-lg mt-0.5">→</span>
                    <span>Document upload and verification</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-blue-400 font-bold text-lg mt-0.5">→</span>
                    <span>Real-time status updates</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-blue-400 font-bold text-lg mt-0.5">→</span>
                    <span>Personalized recommendations</span>
                  </li>
                </ul>
                
                <div className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all text-center">
                  Access Client Portal →
                </div>
              </div>
            </div>
          </Link>
          
          {/* Admin Dashboard */}
          <Link to="/admin" className="group">
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 h-full hover:border-blue-400/50 transform transition-all duration-300 cursor-pointer hover:shadow-xl hover:shadow-blue-500/10">
              <div className="text-left">
                <div className="w-14 h-14 bg-gradient-to-br from-slate-600 to-slate-700 rounded-lg flex items-center justify-center mb-6 group-hover:shadow-lg group-hover:shadow-slate-500/50 transition-all">
                  <Shield className="w-7 h-7 text-blue-300" />
                </div>
                
                <h2 className="text-3xl font-bold mb-3 text-white">
                  Admin Dashboard
                </h2>
                
                <p className="text-slate-400 mb-8 leading-relaxed">
                  Comprehensive analytics platform for credit officers and risk managers. Vector-powered intelligence.
                </p>
                
                <ul className="space-y-3 text-slate-300 mb-8">
                  <li className="flex items-start gap-3">
                    <span className="text-slate-400 font-bold text-lg mt-0.5">→</span>
                    <span>3D vector space visualization</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-slate-400 font-bold text-lg mt-0.5">→</span>
                    <span>Advanced fraud detection</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-slate-400 font-bold text-lg mt-0.5">→</span>
                    <span>Counterfactual modeling</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-slate-400 font-bold text-lg mt-0.5">→</span>
                    <span>Temporal risk tracking</span>
                  </li>
                </ul>
                
                <div className="w-full px-6 py-3 bg-gradient-to-r from-slate-700 to-slate-600 text-white font-semibold rounded-lg hover:from-slate-600 hover:to-slate-500 transition-all text-center">
                  Access Admin Center →
                </div>
              </div>
            </div>
          </Link>
        </div>
        
        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 animate-slide-up">
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6 hover:border-blue-400/30 transition-all">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-blue-300" />
            </div>
            <h3 className="font-bold text-lg text-white mb-2">Evidence-Based</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Decisions backed by 50 similar cases, not opaque algorithms
            </p>
          </div>
          
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6 hover:border-blue-400/30 transition-all">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-blue-300" />
            </div>
            <h3 className="font-bold text-lg text-white mb-2">AI-Generated Insights</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              LLM-powered explanations for transparency and compliance
            </p>
          </div>
          
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6 hover:border-blue-400/30 transition-all">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-blue-300" />
            </div>
            <h3 className="font-bold text-lg text-white mb-2">Fraud Detection</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Vector fingerprinting identifies synthetic identities and patterns
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}