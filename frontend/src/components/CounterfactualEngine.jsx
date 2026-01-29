import { useState } from 'react';
import { Sliders, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import axios from 'axios';

export default function CounterfactualEngine({ clientData }) {
  const [modifications, setModifications] = useState({
    debt_ratio: 0,
    years_active: 0,
    income_stability: 0,
    payment_regularity: 0
  });
  
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  
  const handleModification = (field, value) => {
    setModifications(prev => ({
      ...prev,
      [field]: parseFloat(value)
    }));
  };
  
  const runAnalysis = async () => {
  setAnalyzing(true);
  try {
    // Backend expects: { original_client: {...}, modifications: {...} }
    const response = await axios.post('http://localhost:8000/api/v1/counterfactual/analyze', {
      original_client: {
        archetype: clientData.archetype || 'market_vendor',
        debt_ratio: parseFloat(clientData.debt_ratio) || 0.45,
        years_active: parseFloat(clientData.years_active) || 15,
        income_stability: parseFloat(clientData.income_stability) || 0.85,
        payment_regularity: parseFloat(clientData.payment_regularity) || 0.88,
        monthly_income: parseFloat(clientData.monthly_income) || 2500
      },
      modifications: {
        debt_ratio: parseFloat(modifications.debt_ratio) || 0,
        years_active: parseFloat(modifications.years_active) || 0,
        income_stability: parseFloat(modifications.income_stability) || 0,
        payment_regularity: parseFloat(modifications.payment_regularity) || 0
      }
    });
    setResult(response.data);
  } catch (error) {
    console.error('Counterfactual analysis failed:', error);
    // Log the full error for debugging
    if (error.response) {
      console.error('Error details:', error.response.data);
    }
    alert('Analysis failed. Check console for details.');
  } finally {
    setAnalyzing(false);
  }
};
  
  const resetModifications = () => {
    setModifications({
      debt_ratio: 0,
      years_active: 0,
      income_stability: 0,
      payment_regularity: 0
    });
    setResult(null);
  };
  
  const getRiskColor = (risk) => {
    const colors = {
      'LOW': 'text-risk-safe',
      'MEDIUM': 'text-risk-medium',
      'HIGH': 'text-risk-high',
      'CRITICAL': 'text-risk-critical'
    };
    return colors[risk] || 'text-gray-400';
  };
  
  const getRiskChangeIcon = (change) => {
    if (change === 'improved') return <TrendingUp className="w-5 h-5 text-risk-safe" />;
    if (change === 'worsened') return <TrendingDown className="w-5 h-5 text-risk-critical" />;
    return <Minus className="w-5 h-5 text-gray-400" />;
  };
  
  return (
    <div className="glass-card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold flex items-center gap-2">
          <Sliders className="w-6 h-6 text-accent-cyan" />
          What-If Engine
        </h3>
        <button
          onClick={resetModifications}
          className="px-4 py-2 bg-space-dark hover:bg-space-light rounded-lg transition-colors text-sm"
        >
          Reset
        </button>
      </div>
      
      <p className="text-gray-400 mb-6">
        Adjust the sliders to see how changes would affect the risk assessment
      </p>
      
      {/* Modification Sliders */}
      <div className="space-y-6 mb-6">
        {/* Debt Ratio */}
        <div>
          <div className="flex justify-between mb-2">
            <label className="font-medium">Debt Ratio Change</label>
            <span className="text-accent-cyan">
              {modifications.debt_ratio > 0 ? '+' : ''}
              {(modifications.debt_ratio * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="-0.3"
            max="0.3"
            step="0.01"
            value={modifications.debt_ratio}
            onChange={(e) => handleModification('debt_ratio', e.target.value)}
            className="w-full h-2 bg-space-dark rounded-lg appearance-none cursor-pointer accent-accent-cyan"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>-30%</span>
            <span>0%</span>
            <span>+30%</span>
          </div>
        </div>
        
        {/* Years Active */}
        <div>
          <div className="flex justify-between mb-2">
            <label className="font-medium">Business Seniority Change</label>
            <span className="text-accent-cyan">
              {modifications.years_active > 0 ? '+' : ''}
              {modifications.years_active.toFixed(1)} years
            </span>
          </div>
          <input
            type="range"
            min="-5"
            max="10"
            step="0.5"
            value={modifications.years_active}
            onChange={(e) => handleModification('years_active', e.target.value)}
            className="w-full h-2 bg-space-dark rounded-lg appearance-none cursor-pointer accent-accent-cyan"
          />
        </div>
        
        {/* Income Stability */}
        <div>
          <div className="flex justify-between mb-2">
            <label className="font-medium">Income Stability Change</label>
            <span className="text-accent-cyan">
              {modifications.income_stability > 0 ? '+' : ''}
              {(modifications.income_stability * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="-0.2"
            max="0.2"
            step="0.01"
            value={modifications.income_stability}
            onChange={(e) => handleModification('income_stability', e.target.value)}
            className="w-full h-2 bg-space-dark rounded-lg appearance-none cursor-pointer accent-accent-cyan"
          />
        </div>
        
        {/* Payment Regularity */}
        <div>
          <div className="flex justify-between mb-2">
            <label className="font-medium">Payment Regularity Change</label>
            <span className="text-accent-cyan">
              {modifications.payment_regularity > 0 ? '+' : ''}
              {(modifications.payment_regularity * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="-0.2"
            max="0.2"
            step="0.01"
            value={modifications.payment_regularity}
            onChange={(e) => handleModification('payment_regularity', e.target.value)}
            className="w-full h-2 bg-space-dark rounded-lg appearance-none cursor-pointer accent-accent-cyan"
          />
        </div>
      </div>
      
      {/* Analyze Button */}
      <button
        onClick={runAnalysis}
        disabled={analyzing}
        className="btn-primary w-full mb-6"
      >
        {analyzing ? 'Analyzing...' : 'Run What-If Analysis'}
      </button>
      
      {/* Results */}
      {result && (
        <div className="space-y-4 pt-6 border-t border-space-light">
          {/* Risk Comparison */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-space-dark p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Original Risk</p>
              <p className={`text-2xl font-bold ${getRiskColor(result.original_risk)}`}>
                {result.original_risk}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {(result.confidence_before * 100).toFixed(0)}% confidence
              </p>
            </div>
            
            <div className="flex items-center justify-center">
              {getRiskChangeIcon(result.risk_change)}
            </div>
            
            <div className="bg-space-dark p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Modified Risk</p>
              <p className={`text-2xl font-bold ${getRiskColor(result.modified_risk)}`}>
                {result.modified_risk}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {(result.confidence_after * 100).toFixed(0)}% confidence
              </p>
            </div>
          </div>
          
          {/* Improvement Path */}
          <div className="bg-space-dark p-4 rounded-lg">
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              Path to Acceptance
            </h4>
            <ul className="space-y-2 text-sm">
              {result.improvement_path.map((step, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-accent-cyan mt-1"></span>
                  <span className="text-gray-300">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}