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
      'critical': 'bg-risk-critical/20 border-risk-critical',
      'high': 'bg-risk-high/20 border-risk-high',
      'medium': 'bg-risk-medium/20 border-risk-medium',
      'low': 'bg-risk-safe/20 border-risk-safe',
      'none': 'bg-space-dark border-space-light'
    };
    return styles[level] || styles['none'];
  };
  
  const getIcon = (level) => {
    if (level === 'critical' || level === 'high') {
      return <AlertTriangle className="w-6 h-6 text-risk-critical" />;
    } else if (level === 'medium') {
      return <AlertTriangle className="w-6 h-6 text-risk-medium" />;
    } else {
      return <CheckCircle className="w-6 h-6 text-risk-safe" />;
    }
  };
  
  return (
    <div className="glass-card">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-6 h-6 text-accent-purple" />
        <h3 className="text-2xl font-bold">Fraud Detection</h3>
      </div>
      
      <p className="text-gray-400 mb-6">
        Check if this profile matches known fraud patterns using vector fingerprinting
      </p>
      
      <button
        onClick={checkFraud}
        disabled={checking}
        className="btn-primary w-full mb-6"
      >
        {checking ? 'Checking...' : 'Run Fraud Check'}
      </button>
      
      {result && (
        <div className={`p-6 rounded-lg border-2 ${getAlertStyle(result.alert_level)}`}>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              {getIcon(result.alert_level)}
            </div>
            
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <h4 className="text-lg font-bold">
                  {result.is_suspicious ? 'Suspicious Activity Detected' : 'No Fraud Detected'}
                </h4>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  result.alert_level === 'critical' ? 'bg-risk-critical text-white' :
                  result.alert_level === 'high' ? 'bg-risk-high text-white' :
                  result.alert_level === 'medium' ? 'bg-risk-medium text-black' :
                  'bg-risk-safe text-white'
                }`}>
                  {result.alert_level.toUpperCase()}
                </span>
              </div>

              
              <p className="text-sm mb-4">{result.recommendation}</p>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-space-dark/50 p-3 rounded">
                  <p className="text-xs text-gray-400">Fraud Score</p>
                  <p className="text-2xl font-bold">{(result.fraud_score * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-space-dark/50 p-3 rounded">
                  <p className="text-xs text-gray-400">Similar Frauds Found</p>
                  <p className="text-2xl font-bold">{result.similar_frauds.length}</p>
                </div>
              </div>
              {/* Oracle Narrative */}
              {result.oracle_narrative && (
                <div className="mt-4 p-3 bg-space-dark/50 rounded-lg border-l-4 border-accent-purple">
                  <p className="text-sm text-gray-300 italic">
                    "Note this is just a demo please disregard the previous message{result.oracle_narrative}"
                  </p>
                </div>
              )}
              {result.similar_frauds.length > 0 && (
                <div>
                  <p className="text-sm font-semibold mb-2">Similar Fraud Patterns:</p>
                  <div className="space-y-2">
                    {result.similar_frauds.map((fraud, i) => (
                      <div key={i} className="bg-space-dark/30 p-3 rounded text-sm">
                        <div className="flex justify-between mb-1">
                          <span className="font-medium">{fraud.fraud_id}</span>
                          <span className="text-accent-cyan">
                            {(fraud.similarity * 100).toFixed(1)}% match
                          </span>
                        </div>
                        <p className="text-xs text-gray-400">Type: {fraud.fraud_type}</p>
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