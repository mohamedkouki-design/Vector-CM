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
      'LOW': 'text-green-400',
      'MEDIUM': 'text-yellow-400',
      'HIGH': 'text-orange-400',
      'CRITICAL': 'text-red-400'
    };
    return colors[risk] || 'text-slate-400';
  };
  
  const getRiskChangeIcon = (change) => {
    if (change === 'improved') return <TrendingUp className="w-5 h-5 text-green-400" />;
    if (change === 'worsened') return <TrendingDown className="w-5 h-5 text-red-400" />;
    return <Minus className="w-5 h-5 text-slate-400" />;
  };
  
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold flex items-center gap-3">
          <Sliders className="w-6 h-6 text-blue-400" />
          <span className="text-white">What-If Engine</span>
        </h3>
        <button
          onClick={resetModifications}
          className="px-4 py-2 bg-slate-700/50 hover:bg-slate-600 border border-slate-600/50 rounded-lg transition-colors text-sm text-slate-300 font-medium"
        >
          Reset
        </button>
      </div>
      
      <p className="text-slate-400 mb-8">
        Adjust the sliders to see how changes would affect the risk assessment
      </p>
      
      {/* Modification Sliders */}
      <div className="space-y-7 mb-8 bg-slate-700/20 border border-slate-600/30 rounded-lg p-6">
        {/* Debt Ratio */}
        <div>
          <div className="flex justify-between mb-3">
            <label className="font-semibold text-slate-300">Debt Ratio Change</label>
            <span className="text-blue-400 font-bold">
              {modifications.debt_ratio > 0 ? '+' : ''}
              {modifications.debt_ratio.toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="-100"
            max="100"
            step="1"
            value={modifications.debt_ratio}
            onChange={(e) => handleModification('debt_ratio', parseInt(e.target.value))}
            className="w-full h-3 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full appearance-none cursor-pointer accent-blue-500"
            style={{
              background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${((modifications.debt_ratio + 100) / 200) * 100}%, #475569 ${((modifications.debt_ratio + 100) / 200) * 100}%, #475569 100%)`
            }}
          />
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>-100%</span>
            <span>0%</span>
            <span>+100%</span>
          </div>
        </div>
        
        {/* Years Active */}
        <div>
          <div className="flex justify-between mb-3">
            <label className="font-semibold text-slate-300">Business Seniority Change</label>
            <span className="text-blue-400 font-bold">
              +{modifications.years_active.toFixed(1)} years
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={modifications.years_active}
            onChange={(e) => handleModification('years_active', parseFloat(e.target.value))}
            className="w-full h-3 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full appearance-none cursor-pointer accent-blue-500"
            style={{
              background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${(modifications.years_active / 10) * 100}%, #475569 ${(modifications.years_active / 10) * 100}%, #475569 100%)`
            }}
          />
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>0 years</span>
            <span>5 years</span>
            <span>10 years</span>
          </div>
        </div>
        
        {/* Income Stability */}
        <div>
          <div className="flex justify-between mb-3">
            <label className="font-semibold text-slate-300">Income Stability Change</label>
            <span className="text-blue-400 font-bold">
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
            onChange={(e) => handleModification('income_stability', parseFloat(e.target.value))}
            className="w-full h-3 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full appearance-none cursor-pointer accent-blue-500"
            style={{
              background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${((modifications.income_stability + 0.2) / 0.4) * 100}%, #475569 ${((modifications.income_stability + 0.2) / 0.4) * 100}%, #475569 100%)`
            }}
          />
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>-20%</span>
            <span>0%</span>
            <span>+20%</span>
          </div>
        </div>
        
        {/* Payment Regularity */}
        <div>
          <div className="flex justify-between mb-3">
            <label className="font-semibold text-slate-300">Payment Regularity Change</label>
            <span className="text-blue-400 font-bold">
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
            onChange={(e) => handleModification('payment_regularity', parseFloat(e.target.value))}
            className="w-full h-3 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full appearance-none cursor-pointer accent-blue-500"
            style={{
              background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${((modifications.payment_regularity + 0.2) / 0.4) * 100}%, #475569 ${((modifications.payment_regularity + 0.2) / 0.4) * 100}%, #475569 100%)`
            }}
          />
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>-20%</span>
            <span>0%</span>
            <span>+20%</span>
          </div>
        </div>
      </div>
      
      {/* Analyze Button */}
      <button
        onClick={runAnalysis}
        disabled={analyzing}
        className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed transition-all mb-8"
      >
        {analyzing ? 'Analyzing...' : 'Run What-If Analysis'}
      </button>
      
      {/* Results */}
      {result && (
        <div className="space-y-6 pt-8 border-t border-slate-600/50">
          {/* Risk Comparison */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-700/40 border border-slate-600/50 p-5 rounded-lg">
              <p className="text-xs text-slate-400 mb-2 font-medium">Original Risk</p>
              <p className={`text-3xl font-bold ${getRiskColor(result.original_risk)}`}>
                {result.original_risk}
              </p>
              <p className="text-xs text-slate-500 mt-2">
                {(result.confidence_before * 100).toFixed(0)}% confidence
              </p>
            </div>
            
            <div className="flex items-center justify-center">
              {getRiskChangeIcon(result.risk_change)}
            </div>
            
            <div className="bg-slate-700/40 border border-slate-600/50 p-5 rounded-lg">
              <p className="text-xs text-slate-400 mb-2 font-medium">Modified Risk</p>
              <p className={`text-3xl font-bold ${getRiskColor(result.modified_risk)}`}>
                {result.modified_risk}
              </p>
              <p className="text-xs text-slate-500 mt-2">
                {(result.confidence_after * 100).toFixed(0)}% confidence
              </p>
            </div>
          </div>
          
          {/* Improvement Path */}
          <div className="bg-gradient-to-r from-blue-600/10 to-blue-500/10 border border-blue-400/30 p-6 rounded-lg">
            <h4 className="font-semibold text-white mb-4 text-lg flex items-center gap-2">
              💡 Path to Improvement
            </h4>
            <ul className="space-y-3 text-sm">
              {result.improvement_path.map((step, i) => (
                <li key={i} className="flex items-start gap-3">
                  <span className="text-blue-400 font-bold mt-0.5">→</span>
                  <span className="text-slate-300 leading-relaxed">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}