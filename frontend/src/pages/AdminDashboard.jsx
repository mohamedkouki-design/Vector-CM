import GalaxyView from '../components/Galaxyview'; 
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Search, Users, TrendingUp } from 'lucide-react';
import { searchSimilar, getStats } from '../services/api';
import { useEffect } from 'react';
import axios from 'axios';
import CounterfactualEngine from '../components/CounterfactualEngine';
import FraudAlert from '../components/FraudAlert';
import TemporalEvolution from '../components/TemporalEvolution';
import TrustRings from '../components/TrustRings';

export default function Dashboard() {
  const [selectedClientId, setSelectedClientId] = useState(null);
  const [selectedSimilarClientId, setSelectedSimilarClientId] = useState(null);
  const [applications, setApplications] = useState([]);
  
  const [searchTriggered, setSearchTriggered] = useState(false);
  
  // Search query
  const { data: searchResults, isLoading, refetch, error: searchError } = useQuery({
    queryKey: ['search', selectedClientId],
    queryFn: () => {
      const appToSearch = applications.find(app => app.client_id === selectedClientId);
      if (!appToSearch) {
        console.warn('No application found for client:', selectedClientId);
        return null;
      }
      return searchSimilar({
        archetype: 'market_vendor',
        debt_ratio: appToSearch.debt_ratio || 0.45,
        years_active: 15,
        income_stability: appToSearch.income_stability || 0.85,
        payment_regularity: appToSearch.payment_regularity || 0.88,
        monthly_income: 2500
      }, 50);
    },
    enabled: searchTriggered && !!selectedClientId,
    retry: 1
  });
  
  // Stats query
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats
  });
  
  const handleSearch = () => {
    if (!selectedClientId) {
      console.warn('No client selected');
      return;
    }
    setSearchTriggered(true);
    refetch();
  };
  
  // Fetch applications on component mount
  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/applications?limit=50');
        if (response.data && response.data.applications) {
          setApplications(response.data.applications);
          if (response.data.applications.length > 0 && !selectedClientId) {
            setSelectedClientId(response.data.applications[0].client_id);
          }
        }
      } catch (error) {
        console.error('Failed to fetch applications:', error);
      }
    };
    fetchApplications();
  }, []);
  
  return (
    <div className="min-h-screen p-8 animate-fade-in">
      <Link to="/" className="btn-ghost mb-8 inline-flex items-center gap-2">
        <ArrowLeft className="w-4 h-4" />
        Back to Home
      </Link>
      
      {/* Error message if search failed */}
      {searchError && (
        <div className="mb-8 p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
          <p className="text-red-300">Search error: {searchError.message}</p>
        </div>
      )}
      
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
        
        {/* Applications List */}
        <div className="glass-card mb-8">
          <h2 className="text-2xl font-bold mb-6">Applications Board</h2>
          
          <div className="space-y-3 mb-6 max-h-96 overflow-y-auto">
            {applications.length > 0 ? (
              applications.map((app) => (
                <button
                  key={app.id}
                  onClick={() => setSelectedClientId(app.client_id)}
                  className={`w-full p-4 rounded-lg text-left transition-all border ${
                    selectedClientId === app.client_id
                      ? 'bg-accent-cyan/30 border-accent-cyan'
                      : 'bg-space-dark/50 border-space-light hover:border-accent-cyan'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-accent-cyan">{app.client_id}</span>
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      app.status === 'pending' ? 'bg-yellow-500/20 text-yellow-300' :
                      app.status === 'approved' ? 'bg-green-500/20 text-green-300' :
                      'bg-red-500/20 text-red-300'
                    }`}>
                      {app.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-400">
                    <div>
                      <p className="text-xs">Timestamp</p>
                      <p className="font-semibold">{app.timestamp || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-xs">Risk Score</p>
                      <p className="font-semibold">{(app.risk_score || 0).toFixed(3)}</p>
                    </div>
                    <div>
                      <p className="text-xs">Debt Ratio</p>
                      <p className="font-semibold">{((app.debt_ratio || 0) * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-xs">Date</p>
                      <p className="font-semibold text-xs">{app.date ? new Date(app.date).toLocaleDateString() : 'N/A'}</p>
                    </div>
                  </div>
                </button>
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                <p>No applications found</p>
              </div>
            )}
          </div>
          
          <button
            onClick={handleSearch}
            disabled={isLoading || !selectedClientId}
            className="btn-primary w-full"
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
            <p className="text-gray-400 text-sm mb-4">Click on any node to view client details</p>
            <div style={{ height: '600px' }}>
              <GalaxyView
                clients={searchResults.similar_clients}
                onSelectClient={(client) => setSelectedSimilarClientId(client.client_id)}
                selectedClientId={selectedSimilarClientId}
              />
            </div>
            {selectedSimilarClientId && (
              <div className="mt-4 p-3 bg-accent-cyan/20 border border-accent-cyan/50 rounded-lg">
                <p className="text-sm text-gray-300">Viewing Similar Client: <span className="font-bold text-accent-cyan">{selectedSimilarClientId}</span></p>
              </div>
            )}
          </div>
        )}
        {/* Temporal Evolution */}
        {searchResults && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Top 10 Most Similar Clients</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
              {searchResults.similar_clients.slice(0, 10).map((client, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedSimilarClientId(client.client_id)}
                  className={`p-3 rounded-lg text-sm transition-all relative ${
                    selectedSimilarClientId === client.client_id
                      ? 'bg-accent-cyan text-white'
                      : 'bg-gradient-to-br from-space-dark to-space-light hover:from-accent-cyan/20 hover:to-accent-purple/20 text-gray-300 border border-accent-cyan/30'
                  }`}
                >
                  <span className="absolute top-1 right-1 bg-gradient-to-r from-accent-cyan to-accent-purple text-white text-xs font-bold px-2 py-0.5 rounded-full">
                    #{i + 1}
                  </span>
                  <div className="mt-3">{client.client_id}</div>
                  <div className={`text-xs mt-1 ${
                    client.outcome === 'repaid' ? 'text-risk-safe' : 'text-risk-critical'
                  }`}>
                    {client.outcome}
                  </div>
                </button>
              ))}
            </div>
            
            <TemporalEvolution clientId={selectedSimilarClientId} />
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
        {searchResults && selectedClientId && (
          <div className="mb-8">
            <CounterfactualEngine clientData={{
              archetype: 'market_vendor',
              debt_ratio: applications.find(app => app.client_id === selectedClientId)?.debt_ratio || 0.45,
              years_active: 15,
              income_stability: applications.find(app => app.client_id === selectedClientId)?.income_stability || 0.85,
              payment_regularity: applications.find(app => app.client_id === selectedClientId)?.payment_regularity || 0.88,
              monthly_income: 2500
            }} />
          </div>
        )}
        {/* Fraud Detection */}
        {searchResults && selectedClientId && (
          <div className="mb-8">
            <FraudAlert clientData={{
              archetype: 'market_vendor',
              debt_ratio: applications.find(app => app.client_id === selectedClientId)?.debt_ratio || 0.45,
              years_active: 15,
              income_stability: applications.find(app => app.client_id === selectedClientId)?.income_stability || 0.85,
              payment_regularity: applications.find(app => app.client_id === selectedClientId)?.payment_regularity || 0.88,
              monthly_income: 2500
            }} />
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
                  <div className="mt-6 p-4 bg-gradient-to-r from-accent-cyan/10 to-accent-purple/10 rounded-lg border border-accent-cyan/30 col-span-1 md:col-span-3">
                    <div className="flex items-start gap-3">
                      <div className="text-2xl flex-shrink-0">✨</div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-accent-cyan mb-1">Credit Oracle Insight</h4>
                        <p className="text-gray-300 leading-relaxed break-words whitespace-pre-wrap">
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
                    className="bg-gradient-to-r from-accent-cyan/10 to-accent-purple/10 p-4 rounded-lg border border-accent-cyan/40 hover:border-accent-cyan transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="bg-gradient-to-r from-accent-cyan to-accent-purple text-white font-bold px-2 py-1 rounded text-xs">
                          TOP #{i + 1}
                        </span>
                        <span className="font-semibold">{client.client_id}</span>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        client.outcome === 'repaid' 
                          ? 'bg-risk-safe/20 text-risk-safe'
                          : 'bg-risk-critical/20 text-risk-critical'
                      }`}>
                        {client.outcome ? client.outcome.toUpperCase() : 'UNKNOWN'}
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