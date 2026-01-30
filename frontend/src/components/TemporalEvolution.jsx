import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import axios from 'axios';

export default function TemporalEvolution({ clientId }) {
  const [evolutionData, setEvolutionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState('risk_score');
  
  const fetchTemporalData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/temporal/${clientId}`);
      const { client_id, snapshots } = response.data;
      
      // Determine outcome from latest risk score
      const latestSnapshot = snapshots[snapshots.length - 1];
      const final_outcome = latestSnapshot.status === 'good' ? 'repaid' : 'defaulted';
      
      // Generate narrative based on trend
      const firstRisk = snapshots[0].risk_score;
      const lastRisk = snapshots[snapshots.length - 1].risk_score;
      const riskChange = lastRisk - firstRisk;
      
      let narrative;
      if (riskChange < -0.1) {
        narrative = `Client ${client_id} demonstrated improving financial health over 6 months, with decreasing risk score from ${(firstRisk * 100).toFixed(0)}% to ${(lastRisk * 100).toFixed(0)}%. This positive trajectory indicates reliable repayment capacity.`;
      } else if (riskChange > 0.1) {
        narrative = `Client ${client_id}'s financial situation deteriorated over 6 months with increasing risk from ${(firstRisk * 100).toFixed(0)}% to ${(lastRisk * 100).toFixed(0)}%. Monitoring required.`;
      } else {
        narrative = `Client ${client_id} maintained stable financial metrics over the 6-month period, with risk score hovering around ${(lastRisk * 100).toFixed(0)}%. Status remains ${latestSnapshot.status}.`;
      }
      
      setEvolutionData({
        client_id,
        snapshots,
        final_outcome,
        narrative
      });
    } catch (error) {
      console.error('Failed to fetch temporal data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    if (clientId) {
      fetchTemporalData();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clientId]);
  
 /* const generateMockTemporalData = (id) => {
    // Generate realistic temporal progression
    const isGoodClient = Math.random() > 0.3;
    
    const t0 = {
      timestamp: 'T0: Application',
      date: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toLocaleDateString(),
      risk_score: isGoodClient ? 0.45 : 0.65,
      debt_ratio: isGoodClient ? 0.45 : 0.72,
      income_stability: isGoodClient ? 0.75 : 0.55,
      payment_regularity: isGoodClient ? 0.78 : 0.58,
      status: 'pending'
    };
    
    const t1 = {
      timestamp: 'T1: 3 Months',
      date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toLocaleDateString(),
      risk_score: isGoodClient ? 0.35 : 0.70,
      debt_ratio: isGoodClient ? 0.38 : 0.78,
      income_stability: isGoodClient ? 0.82 : 0.48,
      payment_regularity: isGoodClient ? 0.85 : 0.52,
      status: isGoodClient ? 'improving' : 'warning'
    };
    
    const t2 = {
      timestamp: 'T2: 6 Months',
      date: new Date().toLocaleDateString(),
      risk_score: isGoodClient ? 0.25 : 0.78,
      debt_ratio: isGoodClient ? 0.30 : 0.85,
      income_stability: isGoodClient ? 0.88 : 0.42,
      payment_regularity: isGoodClient ? 0.92 : 0.45,
      status: isGoodClient ? 'good' : 'default'
    };
    
    return {
      client_id: id,
      final_outcome: isGoodClient ? 'repaid' : 'defaulted',
      snapshots: [t0, t1, t2],
      narrative: isGoodClient 
        ? "Client demonstrated strong financial discipline over 6 months, reducing debt by 33% while improving income stability. This positive trajectory indicates reliable repayment capacity."
        : "Client's financial situation deteriorated over 6 months with increasing debt and declining payment regularity. Early warning signs were evident at T1 but accelerated by T2."
    };
  };*/
  
  if (!clientId) {
    return (
      <div className="glass-card">
        <div className="text-center py-12">
          <Clock className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">Select a client to view temporal evolution</p>
        </div>
      </div>
    );
  }
  
  if (loading) {
    return (
      <div className="glass-card">
        <div className="text-center py-12">
          <div className="w-12 h-12 border-4 border-accent-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading temporal data...</p>
        </div>
      </div>
    );
  }
  
  if (!evolutionData) {
    return null;
  }
  
  const { snapshots, final_outcome, narrative } = evolutionData;
  
  // Calculate trend
  const firstRisk = snapshots[0].risk_score;
  const lastRisk = snapshots[snapshots.length - 1].risk_score;
  const riskChange = lastRisk - firstRisk;
  
  let trendIcon;
  let trendColor;
  let trendText;
  
  if (riskChange < -0.1) {
    trendIcon = <TrendingDown className="w-5 h-5" />;
    trendColor = 'text-risk-safe';
    trendText = 'Improving';
  } else if (riskChange > 0.1) {
    trendIcon = <TrendingUp className="w-5 h-5" />;
    trendColor = 'text-risk-critical';
    trendText = 'Declining';
  } else {
    trendIcon = <Minus className="w-5 h-5" />;
    trendColor = 'text-risk-medium';
    trendText = 'Stable';
  }
  
  // Prepare chart data
  const chartData = snapshots.map((s) => {
    const timestampLabel = s.timestamp === 'T0_application' ? 'T0: App' :
                          s.timestamp === 'T1_3months' ? 'T1: 3mo' :
                          'T2: 6mo';
    return {
      name: timestampLabel,
      'Risk Score': (s.risk_score * 100).toFixed(1),
      'Debt Ratio': (s.debt_ratio * 100).toFixed(1),
      'Income Stability': (s.income_stability * 100).toFixed(1),
      'Payment Regularity': (s.payment_regularity * 100).toFixed(1),
    };
  });
  
  const metrics = [
    { key: 'Risk Score', color: '#ef4444', label: 'Risk Score' },
    { key: 'Debt Ratio', color: '#f97316', label: 'Debt Ratio' },
    { key: 'Income Stability', color: '#10b981', label: 'Income Stability' },
    { key: 'Payment Regularity', color: '#06b6d4', label: 'Payment Regularity' }
  ];
  
  return (
    <div className="glass-card animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold flex items-center gap-3">
            <Clock className="w-8 h-8 text-accent-cyan" />
            Temporal Evolution
          </h3>
          <p className="text-gray-400 mt-1">6-month risk trajectory analysis</p>
        </div>
        
        <div className={`flex items-center gap-2 ${trendColor} font-semibold`}>
          {trendIcon}
          <span>{trendText}</span>
        </div>
      </div>
      
      {/* Timeline Status */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {snapshots.map((snapshot, i) => {
          // Format timestamp labels
          const timestampLabel = snapshot.timestamp === 'T0_application' ? 'T0: Application' :
                                snapshot.timestamp === 'T1_3months' ? 'T1: 3 Months' :
                                'T2: 6 Months';
          
          // Status color mapping
          const statusStyles = {
            'pending': 'border-gray-500 bg-space-dark',
            'good': 'border-risk-safe bg-risk-safe/10',
            'improving': 'border-accent-cyan bg-accent-cyan/10',
            'warning': 'border-risk-medium bg-risk-medium/10',
            'default': 'border-risk-critical bg-risk-critical/10'
          };
          
          const statusTextColors = {
            'pending': 'text-gray-400',
            'good': 'text-risk-safe',
            'improving': 'text-accent-cyan',
            'warning': 'text-risk-medium',
            'default': 'text-risk-critical'
          };
          
          return (
          <div 
            key={i}
            className={`p-4 rounded-lg border-2 ${statusStyles[snapshot.status] || statusStyles['pending']}`}
          >
            <div className="text-sm text-gray-400 mb-1">{timestampLabel}</div>
            <div className="text-xs text-gray-500 mb-2">{snapshot.date}</div>
            <div className="text-2xl font-bold mb-1">
              {(snapshot.risk_score * 100).toFixed(0)}%
            </div>
            <div className={`text-xs font-semibold uppercase ${statusTextColors[snapshot.status] || statusTextColors['pending']}`}>
              {snapshot.status}
            </div>
          </div>
        );
        })}
      </div>
      
      {/* Metric Selector */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {metrics.map(metric => (
          <button
            key={metric.key}
            onClick={() => setSelectedMetric(metric.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
              selectedMetric === metric.key
                ? 'bg-accent-cyan text-white'
                : 'bg-space-dark text-gray-400 hover:bg-space-light'
            }`}
          >
            {metric.label}
          </button>
        ))}
      </div>
      
      {/* Chart */}
      <div className="mb-8" style={{ height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorDebt" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorStability" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorPayment" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3562" />
            <XAxis 
              dataKey="name" 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e2749',
                border: '1px solid #2a3562',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Area
              type="monotone"
              dataKey={selectedMetric}
              stroke={metrics.find(m => m.key === selectedMetric)?.color}
              strokeWidth={3}
              fill={`url(#color${selectedMetric.replace(' ', '')})`}
              animationDuration={1000}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      
      {/* AI Narrative */}
      <div className="bg-gradient-to-r from-accent-cyan/10 to-accent-purple/10 border border-accent-cyan/30 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <div className="text-2xl">🔮</div>
          <div>
            <h4 className="font-semibold text-accent-cyan mb-2">Temporal Analysis</h4>
            <p className="text-gray-300 leading-relaxed">{narrative}</p>
          </div>
        </div>
      </div>
      
      {/* Final Outcome */}
      <div className={`mt-6 p-4 rounded-lg text-center font-semibold ${
        final_outcome === 'repaid' 
          ? 'bg-risk-safe/20 text-risk-safe border border-risk-safe/30'
          : 'bg-risk-critical/20 text-risk-critical border border-risk-critical/30'
      }`}>
        Final Outcome: {final_outcome.toUpperCase()}
      </div>
    </div>
  );
}