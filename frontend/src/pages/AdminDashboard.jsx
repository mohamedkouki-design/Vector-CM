import GalaxyView from '../components/Galaxyview'; 
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Search, Users, TrendingUp } from 'lucide-react';
import { searchSimilar, getStats } from '../services/api';
import CounterfactualEngine from '../components/CounterfactualEngine';
import FraudAlert from '../components/FraudAlert';
import TemporalEvolution from '../components/TemporalEvolution';
import TrustRings from '../components/TrustRings';

export default function Dashboard() {
  const [clientData, setClientData] = useState({
    archetype: 'market_vendor',
    debt_ratio: 0.45,
    years_active: 15,
    income_stability: 0.85,
    payment_regularity: 0.88,
    monthly_income: 2500
  });
  
  const [searchTriggered, setSearchTriggered] = useState(false);
  
  // Search query
  const { data: searchResults, isLoading, refetch } = useQuery({
    queryKey: ['search', clientData],
    queryFn: () => searchSimilar(clientData, 50),
    enabled: searchTriggered
  });
  
  // Stats query
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats
  });
  
  const handleSearch = () => {
    setSearchTriggered(true);
    refetch();
  };
  const [selectedClientId, setSelectedClientId] = useState(null);
  
  return (
    <div className="min-h-screen p-8 animate-fade-in">
      <Link to="/" className="btn-ghost mb-8 inline-flex items-center gap-2">
        <ArrowLeft className="w-4 h-4" />
        Back to Home
      </Link>
      <div className="max-w-7xl mx-auto">
        
        {/* Enhanced Header with Gradient */}
        <div className="mb-8 animate-slide-down">
          <h1 className="text-5xl font-bold mb-2 bg-gradient-to-r from-accent-cyan via-accent-purple to-accent-pink bg-clip-text text-transparent">
            Admin Command Center
          </h1>
          <p className="text-gray-400 text-lg">
            Self-Evolving Multimodal Credit Intelligence
          </p>
        </div>
        
        {/* Stats Cards with Staggered Animation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {[
            { icon: '👥', label: 'Total Clients', value: stats?.total_clients },
            { icon: '📊', label: 'Vector Size', value: stats?.vector_size },
            { icon: '🔍', label: 'Distance Metric', value: stats?.distance_metric }
          ].map((stat, i) => (
            <div 
              key={i}
              className="stat-card animate-in"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{stat.icon}</span>
                <h3 className="font-semibold text-gray-300">{stat.label}</h3>
              </div>
              <p className="text-3xl font-bold neon-text">
                {stat.value || '---'}
              </p>
            </div>
          ))}
        </div>
        
        {/* Search Form */}
        <div className="glass-card mb-8">
          <h2 className="text-2xl font-bold mb-6">Client Profile</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                Business Type
              </label>
              <select
                value={clientData.archetype}
                onChange={(e) => setClientData({...clientData, archetype: e.target.value})}
                className="w-full bg-space-dark border border-space-light rounded-lg px-4 py-2"
              >
                <option value="market_vendor">Market Vendor</option>
                <option value="craftsman">Craftsman</option>
                <option value="gig_worker">Gig Worker</option>
                <option value="home_business">Home Business</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Years Active: {clientData.years_active}
              </label>
              <input
                type="range"
                min="1"
                max="30"
                step="0.5"
                value={clientData.years_active}
                onChange={(e) => setClientData({...clientData, years_active: parseFloat(e.target.value)})}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Debt Ratio: {(clientData.debt_ratio * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={clientData.debt_ratio}
                onChange={(e) => setClientData({...clientData, debt_ratio: parseFloat(e.target.value)})}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Income Stability: {(clientData.income_stability * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={clientData.income_stability}
                onChange={(e) => setClientData({...clientData, income_stability: parseFloat(e.target.value)})}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Payment Regularity: {(clientData.payment_regularity * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={clientData.payment_regularity}
                onChange={(e) => setClientData({...clientData, payment_regularity: parseFloat(e.target.value)})}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Monthly Income (TND)
              </label>
              <input
                type="number"
                value={clientData.monthly_income}
                onChange={(e) => setClientData({...clientData, monthly_income: parseFloat(e.target.value)})}
                className="w-full bg-space-dark border border-space-light rounded-lg px-4 py-2"
              />
            </div>
          </div>
          
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="btn-primary w-full mt-6"
          >
            {isLoading ? 'Searching...' : 'Search Similar Clients'}
          </button>
        </div>
        
        {/* Loading State */}
        {isLoading && (
          <div className="glass-card mb-8 animate-pulse-glow">
            <div className="flex items-center justify-center gap-3 py-8">
              <div className="w-4 h-4 bg-accent-cyan rounded-full animate-bounce" 
                   style={{ animationDelay: '0ms' }} />
              <div className="w-4 h-4 bg-accent-purple rounded-full animate-bounce" 
                   style={{ animationDelay: '150ms' }} />
              <div className="w-4 h-4 bg-accent-pink rounded-full animate-bounce" 
                   style={{ animationDelay: '300ms' }} />
              <span className="ml-2 text-gray-400">Searching vector space...</span>
            </div>
          </div>
        )}
        
        {/* Galaxy View */}
        {searchResults && searchResults.similar_clients.length > 0 && (
          <div className="glass-card mb-8">
            <h2 className="text-2xl font-bold mb-4">Galaxy View - Vector Space</h2>
            <div style={{ height: '600px' }}>
              <GalaxyView
                clients={searchResults.similar_clients}
                onSelectClient={(client) => console.log('Selected:', client)}
                selectedClientId={null}
              />
            </div>
          </div>
        )}
        {/* Temporal Evolution */}
        {searchResults && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Select Client for Temporal Analysis</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
              {searchResults.similar_clients.slice(0, 8).map((client, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedClientId(client.client_id)}
                  className={`p-3 rounded-lg text-sm transition-all ${
                    selectedClientId === client.client_id
                      ? 'bg-accent-cyan text-white'
                      : 'bg-space-dark hover:bg-space-light text-gray-300'
                  }`}
                >
                  {client.client_id}
                  <div className={`text-xs mt-1 ${
                    client.outcome === 'repaid' ? 'text-risk-safe' : 'text-risk-critical'
                  }`}>
                    {client.outcome}
                  </div>
                </button>
              ))}
            </div>
            
            <TemporalEvolution clientId={selectedClientId} />
          </div>
        )}
        {/* Trust Rings Network */}
        {searchResults && (
          <TrustRings 
            clientId={selectedClientId || searchResults.similar_clients[0]?.client_id}
            similarClients={searchResults.similar_clients}
          />
        )}

        {/* Counterfactual Engine */}
        {searchResults && (
          <div className="mb-8">
            <CounterfactualEngine clientData={clientData} />
          </div>
        )}
        {/* Fraud Detection */}
        {searchResults && (
          <div className="mb-8">
            <FraudAlert clientData={clientData} />
          </div>
        )}
        
        {/* Results */}
        {searchResults && (
          <>
            {/* Risk Assessment */}
            <div className="glass-card mb-8">
              <h2 className="text-2xl font-bold mb-4">Risk Assessment</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Risk Level</p>
                  <p className={`text-3xl font-bold ${
                    searchResults.risk_level === 'LOW' ? 'text-risk-safe' :
                    searchResults.risk_level === 'MEDIUM' ? 'text-risk-medium' :
                    searchResults.risk_level === 'HIGH' ? 'text-risk-high' :
                    'text-risk-critical'
                  }`}>
                    {searchResults.risk_level}
                  </p>
                </div>
                {/* Oracle Explanation */}
                {searchResults.oracle_explanation && (
                  <div className="mt-6 p-4 bg-gradient-to-r from-accent-cyan/10 to-accent-purple/10 rounded-lg border border-accent-cyan/30">
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">✨</div>
                      <div>
                        <h4 className="font-semibold text-accent-cyan mb-1">Credit Oracle Insight</h4>
                        <p className="text-gray-300 leading-relaxed">
                          {searchResults.oracle_explanation}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
                
                <div>
                  <p className="text-sm text-gray-400 mb-1">Confidence</p>
                  <p className="text-3xl font-bold">
                    {(searchResults.confidence * 100).toFixed(0)}%
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-400 mb-1">Repayment Rate</p>
                  <p className="text-3xl font-bold">
                    {searchResults.repaid_count}/{searchResults.total_count}
                  </p>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-space-dark rounded-lg">
                <p className="font-semibold mb-2">Recommendation:</p>
                <p className="text-gray-300">{searchResults.recommendation}</p>
              </div>
            </div>
            
            {/* Similar Clients */}
            <div className="glass-card">
              <h2 className="text-2xl font-bold mb-4">
                Similar Clients (Top 10)
              </h2>
              
              <div className="space-y-3">
                {searchResults.similar_clients.slice(0, 10).map((client, i) => (
                  <div
                    key={i}
                    className="bg-space-dark p-4 rounded-lg border border-space-light hover:border-accent-cyan transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">{client.client_id}</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        client.outcome === 'repaid' 
                          ? 'bg-risk-safe/20 text-risk-safe'
                          : 'bg-risk-critical/20 text-risk-critical'
                      }`}>
                        {client.outcome.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <p className="text-gray-400">Similarity</p>
                        <p className="font-semibold">{(client.similarity * 100).toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Loan Source</p>
                        <p className="font-semibold text-accent-cyan">{client.loan_source}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Debt Ratio</p>
                        <p className="font-semibold">{(client.debt_ratio * 100).toFixed(0)}%</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Experience</p>
                        <p className="font-semibold">{client.years_active} years</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}