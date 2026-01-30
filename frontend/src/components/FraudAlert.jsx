import { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import axios from 'axios';

export default function FraudAlert({ clientData }) {
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState(null);
  
  const checkFraud = async () => {
    setChecking(true);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/fraud/check', {
        client_data: clientData
      });
      setResult(response.data);
    } catch (error) {
      console.error('Fraud check failed:', error);
      alert('Fraud check failed. Make sure backend is running.');
    } finally {
      setChecking(false);
    }
  };
  
  const getAlertStyle = (level) => {
    const styles = {
      'critical': 'bg-red-600/10 border-red-400/50',
      'high': 'bg-orange-600/10 border-orange-400/50',
      'medium': 'bg-yellow-600/10 border-yellow-400/50',
      'low': 'bg-green-600/10 border-green-400/50',
      'none': 'bg-slate-700/30 border-slate-600/50'
    };
    return styles[level] || styles['none'];
  };
  
  const getIcon = (level) => {
    if (level === 'critical' || level === 'high') {
      return <AlertTriangle className="w-6 h-6 text-red-400" />;
    } else if (level === 'medium') {
      return <AlertTriangle className="w-6 h-6 text-yellow-400" />;
    } else {
      return <CheckCircle className="w-6 h-6 text-green-400" />;
    }
  };
  
  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-6 h-6 text-blue-400" />
        <h3 className="text-2xl font-bold text-white">Fraud Detection</h3>
      </div>
      
      <p className="text-slate-400 mb-8">
        Check if this profile matches known fraud patterns using vector fingerprinting
      </p>
      
      <button
        onClick={checkFraud}
        disabled={checking}
        className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed transition-all mb-8"
      >
        {checking ? 'Checking...' : 'Run Fraud Check'}
      </button>
      
      {result && (
        <div className={`p-6 rounded-lg border-2 ${getAlertStyle(result.alert_level)}`}>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 mt-1">
              {getIcon(result.alert_level)}
            </div>
            
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <h4 className="text-lg font-bold text-white">
                  {result.is_suspicious ? 'Suspicious Activity Detected' : 'No Fraud Detected'}
                </h4>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  result.alert_level === 'critical' ? 'bg-red-500 text-white' :
                  result.alert_level === 'high' ? 'bg-orange-500 text-white' :
                  result.alert_level === 'medium' ? 'bg-yellow-500 text-black' :
                  'bg-green-500 text-white'
                }`}>
                  {result.alert_level.toUpperCase()}
                </span>
              </div>

              
              <p className="text-sm text-slate-300 mb-6">{result.recommendation}</p>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-slate-700/30 border border-slate-600/50 p-4 rounded-lg">
                  <p className="text-xs text-slate-400 font-medium mb-1">Fraud Score</p>
                  <p className="text-3xl font-bold text-blue-400">{(result.fraud_score * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-slate-700/30 border border-slate-600/50 p-4 rounded-lg">
                  <p className="text-xs text-slate-400 font-medium mb-1">Similar Frauds Found</p>
                  <p className="text-3xl font-bold text-blue-400">{result.similar_frauds.length}</p>
                </div>
              </div>
              {/* Oracle Narrative */}
              {result.oracle_narrative && (
                <div className="mt-4 p-4 bg-blue-600/10 rounded-lg border-l-4 border-blue-400">
                  <p className="text-sm text-slate-300 italic">
                    "{result.oracle_narrative}"
                  </p>
                </div>
              )}
              {result.similar_frauds.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-white mb-3">Similar Fraud Patterns:</p>
                  <div className="space-y-2">
                    {result.similar_frauds.map((fraud, i) => (
                      <div key={i} className="bg-slate-700/20 border border-slate-600/30 p-3 rounded text-sm">
                        <div className="flex justify-between mb-2">
                          <span className="font-medium text-slate-300">{fraud.fraud_id}</span>
                          <span className="text-blue-400 font-semibold">
                            {(fraud.similarity * 100).toFixed(1)}% match
                          </span>
                        </div>
                        <p className="text-xs text-slate-400">Type: {fraud.fraud_type}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}