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
        archetype: appToSearch.archetype || 'market_vendor',
        debt_ratio: appToSearch.debt_ratio || 0.45,
        years_active: appToSearch.years_active || 15,
        income_stability: appToSearch.income_stability || 0.85,
        payment_regularity: appToSearch.payment_regularity || 0.88,
        monthly_income: appToSearch.monthly_income || 2500
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
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 p-8 animate-fade-in">
      <div className="max-w-7xl mx-auto">
        <Link to="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-blue-300 transition-colors mb-8 font-medium">
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>
        
        {/* Error message if search failed */}
        {searchError && (
          <div className="mb-8 p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
            <p className="text-red-300">Search error: {searchError.message}</p>
          </div>
        )}
        
        {/* Professional Header */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-400/30 mb-6">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
            <span className="text-sm font-semibold text-blue-300">Risk Management</span>
          </div>
          <h1 className="text-5xl font-bold text-white mb-2">
            Credit Command Center
          </h1>
          <p className="text-slate-400 text-lg">
            Vector-powered credit intelligence and risk analysis
          </p>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {[
            { icon: '👥', label: 'Total Clients', value: stats?.total_clients, color: 'blue' },
            { icon: '📊', label: 'Vector Dimension', value: stats?.vector_size, color: 'blue' },
            { icon: '🔍', label: 'Distance Metric', value: stats?.distance_metric, color: 'slate' }
          ].map((stat, i) => (
            <div 
              key={i}
              className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-lg p-6 hover:border-blue-400/30 transition-all"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-slate-300 uppercase tracking-wider">{stat.label}</span>
                <span className="text-3xl">{stat.icon}</span>
              </div>
              <p className="text-3xl font-bold text-white">
                {stat.value || '---'}
              </p>
            </div>
          ))}
        </div>
        
        {/* Applications List */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 mb-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">Recent Applications</h2>
            <p className="text-slate-400">Select an applicant to view detailed analysis</p>
          </div>
          
          <div className="space-y-3 mb-6 max-h-96 overflow-y-auto">
            {applications.length > 0 ? (
              applications.map((app) => (
                <button
                  key={app.id}
                  onClick={() => setSelectedClientId(app.client_id)}
                  className={`w-full p-4 rounded-lg text-left transition-all border ${
                    selectedClientId === app.client_id
                      ? 'bg-blue-600/20 border-blue-400/50 shadow-lg shadow-blue-500/10'
                      : 'bg-slate-700/30 border-slate-600/50 hover:border-blue-400/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-semibold text-blue-300">{app.client_id}</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      app.status === 'pending' ? 'bg-yellow-500/20 text-yellow-300' :
                      app.status === 'approved' ? 'bg-green-500/20 text-green-300' :
                      'bg-red-500/20 text-red-300'
                    }`}>
                      {app.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm text-slate-300">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Timestamp</p>
                      <p className="font-semibold text-white">{app.timestamp || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Risk Score</p>
                      <p className="font-semibold text-white">{(app.risk_score || 0).toFixed(3)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Debt Ratio</p>
                      <p className="font-semibold text-white">{((app.debt_ratio || 0) * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Date</p>
                      <p className="font-semibold text-white text-xs">{app.date ? new Date(app.date).toLocaleDateString() : 'N/A'}</p>
                    </div>
                  </div>
                </button>
              ))
            ) : (
              <div className="text-center py-8 text-slate-400">
                <p>No applications found</p>
              </div>
            )}
          </div>
          
          <button
            onClick={handleSearch}
            disabled={isLoading || !selectedClientId}
            className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? 'Analyzing...' : 'Analyze Similar Clients'}
          </button>
        </div>
        
        {/* Loading State */}
        {isLoading && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 text-center mb-8">
            <div className="flex items-center justify-center gap-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" 
                   style={{ animationDelay: '0ms' }} />
              <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce" 
                   style={{ animationDelay: '150ms' }} />
              <div className="w-3 h-3 bg-blue-300 rounded-full animate-bounce" 
                   style={{ animationDelay: '300ms' }} />
              <span className="ml-2 text-slate-300 font-medium">Analyzing vector space...</span>
            </div>
          </div>
        )}
        
        {/* Galaxy View */}
        {searchResults && searchResults.similar_clients.length > 0 && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 mb-8">
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-3 h-3 rounded-full bg-indigo-500 animate-pulse"></div>
                <h2 className="text-2xl font-bold text-white">Galaxy View - Vector Space</h2>
              </div>
              <p className="text-slate-400 text-sm">Click on any node to view client details</p>
            </div>
            <div style={{ height: '600px' }}>
              <GalaxyView
                clients={searchResults.similar_clients}
                onSelectClient={(client) => setSelectedSimilarClientId(client.client_id)}
                selectedClientId={selectedSimilarClientId}
              />
            </div>
            {selectedSimilarClientId && (
              <div className="mt-4 p-4 bg-blue-600/10 border border-blue-400/30 rounded-lg">
                <p className="text-sm text-slate-300">Viewing Similar Client: <span className="font-bold text-blue-300">{selectedSimilarClientId}</span></p>
              </div>
            )}
          </div>
        )}
        {/* Temporal Evolution */}
        {searchResults && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-6">Top 10 Most Similar Clients</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
              {searchResults.similar_clients.slice(0, 10).map((client, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedSimilarClientId(client.client_id)}
                  className={`p-4 rounded-lg text-sm transition-all relative border ${
                    selectedSimilarClientId === client.client_id
                      ? 'bg-blue-600 border-blue-400 shadow-lg shadow-blue-500/20 text-white'
                      : 'bg-slate-700/40 border-slate-600/50 hover:border-blue-400/50 text-slate-300'
                  }`}
                >
                  <span className="absolute top-2 right-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-bold px-2.5 py-1 rounded-full">
                    #{i + 1}
                  </span>
                  <div className="mt-4 font-semibold text-white">{client.client_id}</div>
                  <div className={`text-xs mt-2 font-medium ${
                    client.outcome === 'repaid' ? 'text-green-400' : 'text-red-400'
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
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 mb-8">
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-3 h-3 rounded-full bg-purple-500 animate-pulse"></div>
                <h2 className="text-2xl font-bold text-white">Trust Network Analysis</h2>
              </div>
              <p className="text-slate-400 text-sm">Client relationships and trust connections</p>
            </div>
            <TrustRings 
              clientId={selectedClientId || searchResults.similar_clients[0]?.client_id}
              similarClients={searchResults.similar_clients}
              queryClientData={applications.find(app => app.client_id === selectedClientId)}
            />
          </div>
        )}

        {/* Counterfactual Engine */}
        {searchResults && selectedClientId && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 mb-8">
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-3 h-3 rounded-full bg-orange-500 animate-pulse"></div>
                <h2 className="text-2xl font-bold text-white">Counterfactual Analysis</h2>
              </div>
              <p className="text-slate-400 text-sm">What-if scenarios and decision drivers</p>
            </div>
            <CounterfactualEngine clientData={{
              archetype: applications.find(app => app.client_id === selectedClientId)?.archetype || 'market_vendor',
              debt_ratio: applications.find(app => app.client_id === selectedClientId)?.debt_ratio || 0.45,
              years_active: applications.find(app => app.client_id === selectedClientId)?.years_active || 15,
              income_stability: applications.find(app => app.client_id === selectedClientId)?.income_stability || 0.85,
              payment_regularity: applications.find(app => app.client_id === selectedClientId)?.payment_regularity || 0.88,
              monthly_income: applications.find(app => app.client_id === selectedClientId)?.monthly_income || 2500
            }} />
          </div>
        )}
        {/* Fraud Detection */}
        {searchResults && selectedClientId && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 mb-8">
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                <h2 className="text-2xl font-bold text-white">Fraud Detection & Risk</h2>
              </div>
              <p className="text-slate-400 text-sm">Advanced anomaly and fraud pattern analysis</p>
            </div>
            <FraudAlert clientData={{
              archetype: applications.find(app => app.client_id === selectedClientId)?.archetype || 'market_vendor',
              debt_ratio: applications.find(app => app.client_id === selectedClientId)?.debt_ratio || 0.45,
              years_active: applications.find(app => app.client_id === selectedClientId)?.years_active || 15,
              income_stability: applications.find(app => app.client_id === selectedClientId)?.income_stability || 0.85,
              payment_regularity: applications.find(app => app.client_id === selectedClientId)?.payment_regularity || 0.88,
              monthly_income: applications.find(app => app.client_id === selectedClientId)?.monthly_income || 2500
            }} />
          </div>
        )}
        
        {/* Results */}
        {searchResults && (
          <>
            {/* Risk Assessment */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 mb-8">
              <div className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse"></div>
                  <h2 className="text-2xl font-bold text-white">Risk Assessment</h2>
                </div>
                <p className="text-slate-400 text-sm">Comprehensive credit risk evaluation</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-6">
                  <p className="text-sm text-slate-400 mb-3">Risk Level</p>
                  <p className={`text-4xl font-bold ${
                    searchResults.risk_level === 'LOW' ? 'text-green-400' :
                    searchResults.risk_level === 'MEDIUM' ? 'text-yellow-400' :
                    searchResults.risk_level === 'HIGH' ? 'text-orange-400' :
                    'text-red-400'
                  }`}>
                    {searchResults.risk_level}
                  </p>
                </div>
                
                <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-6">
                  <p className="text-sm text-slate-400 mb-3">Confidence Score</p>
                  <p className="text-4xl font-bold text-blue-400">
                    {(searchResults.confidence * 100).toFixed(0)}%
                  </p>
                </div>
                
                <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-6">
                  <p className="text-sm text-slate-400 mb-3">Repayment Rate</p>
                  <p className="text-4xl font-bold text-blue-400">
                    {searchResults.repaid_count}/{searchResults.total_count}
                  </p>
                </div>
              </div>

              {/* Oracle Explanation */}
              {searchResults.oracle_explanation && (
                <div className="mb-8 p-6 bg-gradient-to-r from-blue-600/10 to-blue-500/10 rounded-lg border border-blue-400/30">
                  <div className="flex items-start gap-4">
                    <div className="text-3xl flex-shrink-0">✨</div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-blue-300 mb-2 text-lg">Credit Oracle Insight</h4>
                      <p className="text-slate-300 leading-relaxed break-words whitespace-pre-wrap">
                        {searchResults.oracle_explanation}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="p-6 bg-slate-700/40 border border-slate-600/50 rounded-lg">
                <p className="font-semibold text-white mb-3 text-lg">Recommendation:</p>
                <p className="text-slate-300 leading-relaxed">{searchResults.recommendation}</p>
              </div>
            </div>
            
            {/* Similar Clients */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8">
              <div className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                  <h2 className="text-2xl font-bold text-white">
                    Similar Clients (Top 10)
                  </h2>
                </div>
                <p className="text-slate-400 text-sm">Comparable credit profiles and outcomes</p>
              </div>
              
              <div className="space-y-3">
                {searchResults.similar_clients.slice(0, 10).map((client, i) => (
                  <div
                    key={i}
                    className="bg-slate-700/30 border border-slate-600/50 p-5 rounded-lg hover:border-blue-400/50 transition-all"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <span className="bg-gradient-to-r from-blue-500 to-blue-600 text-white font-bold px-3 py-1 rounded text-xs">
                          TOP #{i + 1}
                        </span>
                        <span className="font-semibold text-white">{client.client_id}</span>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        client.outcome === 'repaid' 
                          ? 'bg-green-500/20 text-green-300'
                          : 'bg-red-500/20 text-red-300'
                      }`}>
                        {client.outcome ? client.outcome.toUpperCase() : 'UNKNOWN'}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-slate-400 text-xs mb-1">Similarity</p>
                        <p className="font-semibold text-blue-300">{(client.similarity * 100).toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-xs mb-1">Loan Source</p>
                        <p className="font-semibold text-slate-300">{client.loan_source}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-xs mb-1">Debt Ratio</p>
                        <p className="font-semibold text-slate-300">{(client.debt_ratio * 100).toFixed(0)}%</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-xs mb-1">Experience</p>
                        <p className="font-semibold text-slate-300">{client.years_active} years</p>
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