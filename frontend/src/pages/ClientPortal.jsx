import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Upload, ArrowLeft, CheckCircle, Clock } from 'lucide-react';
import axios from 'axios';
import VoiceAssistedForm from '../components/VoiceAssistedForm';
import ErrorBoundary from '../components/ErrorBoundary';

export default function ClientPortal() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    archetype: 'market_vendor',
    years_active: 5,
    monthly_income: 1500,
    debt_ratio: 0.45,
    income_stability: 0.85,
    payment_regularity: 0.88
  });
  const [documents, setDocuments] = useState([]);
  const [applicationResult, setApplicationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setDocuments(files);
  };
  
  const submitApplication = async () => {
    setLoading(true);
    try {
      // Submit application to backend which will create a T0 point in temporal_risk_memory
      const body = {
        applicant: formData,
        documents: documents.map(d => d.name || d)
      };

      const res = await axios.post('http://localhost:8000/api/v1/applications/submit', body);
      setApplicationResult(res.data);
      setStep(4);
    } catch (error) {
      console.error('Application failed:', error);
    } finally {
      setLoading(false);
    }
  };
  const [useVoiceInput, setUseVoiceInput] = useState(false);
  
  return (
    <ErrorBoundary>
    <div className="min-h-screen p-8">
      <div className="max-w-3xl mx-auto">
        {/* Back button */}
        <Link to="/" className="btn-ghost mb-8 inline-flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>
        
        {/* Header */}
        <div className="text-center mb-12 animate-slide-down">
          <h1 className="text-4xl font-bold mb-2 neon-text">Client Portal</h1>
          <p className="text-gray-400">
            Apply for credit in just a few simple steps
          </p>
        </div>
        
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                step >= s 
                  ? 'bg-accent-cyan text-white' 
                  : 'bg-space-light text-gray-500'
              }`}>
                {s}
              </div>
              {s < 4 && (
                <div className={`w-20 h-1 ${
                  step > s ? 'bg-accent-cyan' : 'bg-space-light'
                }`} />
              )}
            </div>
          ))}
        </div>
        {/* Voice/Manual Toggle */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-space-dark rounded-lg p-1">
            <button
              onClick={() => setUseVoiceInput(false)}
              className={`px-6 py-2 rounded-lg transition-all ${
                !useVoiceInput ? 'bg-accent-cyan text-white' : 'text-gray-400'
              }`}
            >
              📝 Manual Entry
            </button>
            <button
              onClick={() => setUseVoiceInput(true)}
              className={`px-6 py-2 rounded-lg transition-all ${
                useVoiceInput ? 'bg-accent-cyan text-white' : 'text-gray-400'
              }`}
            >
              🎤 Voice Input
            </button>
          </div>
        </div>

        {/* Voice Mode */}
        {useVoiceInput && step === 1 && (
          <VoiceAssistedForm 
            onSubmit={(data) => {
              setFormData({
                ...formData,
                name: data.name || formData.name,
                archetype: data.archetype,
                years_active: data.years_active,
                monthly_income: data.monthly_income
              });
              setStep(2);
            }}
          />
        )}
        
        {/* Step 1: Basic Info */}
        {step === 1 && (
          <div className="glass-card animate-slide-up">
            <h2 className="text-2xl font-bold mb-6">Step 1: Basic Information</h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="Enter your full name"
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">
                  Type of Business
                </label>
                <select
                  value={formData.archetype}
                  onChange={(e) => setFormData({...formData, archetype: e.target.value})}
                  className="w-full"
                >
                  <option value="market_vendor">Market Vendor</option>
                  <option value="craftsman">Craftsman</option>
                  <option value="gig_worker">Gig Worker (Taxi/Delivery)</option>
                  <option value="home_business">Home Business</option>
                  <option value="shop_owner">Shop Owner</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">
                  Years in Business: {formData.years_active} years
                </label>
                <input
                  type="range"
                  min="1"
                  max="30"
                  value={formData.years_active}
                  onChange={(e) => setFormData({...formData, years_active: parseInt(e.target.value)})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">
                  Debt Ratio: {(formData.debt_ratio * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.debt_ratio}
                  onChange={(e) => setFormData({...formData, debt_ratio: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Income Stability: {(formData.income_stability * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.income_stability}
                  onChange={(e) => setFormData({...formData, income_stability: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Payment Regularity: {(formData.payment_regularity * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.payment_regularity}
                  onChange={(e) => setFormData({...formData, payment_regularity: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Average Monthly Income (TND)
                </label>
                <input
                  type="number"
                  value={formData.monthly_income}
                  onChange={(e) => setFormData({...formData, monthly_income: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>
              
              <button
                onClick={() => setStep(2)}
                disabled={!formData.name}
                className="btn-primary w-full"
              >
                Continue to Documents →
              </button>
            </div>
          </div>
        )}
        
        {/* Step 2: Documents */}
        {step === 2 && (
          <div className="glass-card animate-slide-up">
            <h2 className="text-2xl font-bold mb-6">Step 2: Upload Documents</h2>
            
            <p className="text-gray-400 mb-6">
              Upload invoices, receipts, or any proof of income. Mobile photos are fine!
            </p>
            
            <div className="border-2 border-dashed border-space-light rounded-lg p-8 text-center mb-6 hover:border-accent-cyan transition-colors">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-300 mb-2">
                Drag and drop files here, or click to browse
              </p>
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="btn-secondary cursor-pointer inline-block">
                Choose Files
              </label>
            </div>
            
            {documents.length > 0 && (
              <div className="mb-6">
                <p className="text-sm text-gray-400 mb-2">
                  {documents.length} file(s) selected:
                </p>
                <ul className="space-y-2">
                  {documents.map((file, i) => (
                    <li key={i} className="text-sm text-gray-300 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-accent-cyan" />
                      {file.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="flex gap-4">
              <button
                onClick={() => setStep(1)}
                className="btn-secondary flex-1"
              >
                ← Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="btn-primary flex-1"
              >
                Continue to Review →
              </button>
            </div>
          </div>
        )}
        
        {/* Step 3: Review */}
        {step === 3 && (
          <div className="glass-card animate-slide-up">
            <h2 className="text-2xl font-bold mb-6">Step 3: Review & Submit</h2>
            
            <div className="space-y-4 mb-8">
              <div className="flex justify-between py-2 border-b border-space-light">
                <span className="text-gray-400">Name:</span>
                <span className="font-semibold">{formData.name}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-space-light">
                <span className="text-gray-400">Business Type:</span>
                <span className="font-semibold">{formData.archetype.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-space-light">
                <span className="text-gray-400">Years Active:</span>
                <span className="font-semibold">{formData.years_active} years</span>
              </div>
              <div className="flex justify-between py-2 border-b border-space-light">
                <span className="text-gray-400">Monthly Income:</span>
                <span className="font-semibold">{formData.monthly_income} TND</span>
              </div>
              <div className="flex justify-between py-2 border-b border-space-light">
                <span className="text-gray-400">Documents:</span>
                <span className="font-semibold">{documents.length} uploaded</span>
              </div>
            </div>
            
            <div className="bg-accent-cyan/10 border border-accent-cyan/30 rounded-lg p-4 mb-8">
              <p className="text-sm text-gray-300">
                ✓ By submitting, you confirm that all information provided is accurate 
                and that you authorize us to verify your details.
              </p>
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={() => setStep(2)}
                className="btn-secondary flex-1"
                disabled={loading}
              >
                ← Back
              </button>
              <button
                onClick={submitApplication}
                disabled={loading}
                className="btn-primary flex-1"
              >
                {loading ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </div>
        )}
        
        {/* Step 4: Result */}
        {step === 4 && applicationResult && (
          applicationResult.created_point ? (
            <div className="glass-card animate-scale-in">
              <h2 className="text-2xl font-semibold mb-4">Application Submitted</h2>
              <p className="text-gray-400 mb-4">Your application has been recorded. An admin will review your documents and the initial risk snapshot.</p>

              <div className="mb-4">
                <h4 className="font-semibold mb-2">Client ID</h4>
                <div className="p-3 bg-space-dark rounded">{applicationResult.client_id}</div>
              </div>

              <div className="mb-4">
                <h4 className="font-semibold mb-2">T0 Snapshot</h4>
                <pre className="bg-space-dark p-3 rounded text-sm overflow-auto">{JSON.stringify(applicationResult.created_point, null, 2)}</pre>
              </div>

              <div className="mt-6">
                <Link to="/" className="btn-primary">Return to Home</Link>
              </div>
            </div>
          ) : (
            <div className="glass-card animate-scale-in text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-risk-safe to-accent-cyan rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse-glow">
                <CheckCircle className="w-10 h-10 text-white" />
              </div>

              <h2 className="text-3xl font-bold mb-4 text-risk-safe">
                Application {applicationResult.status === 'approved' ? 'Approved!' : 'Received'}
              </h2>

              <p className="text-gray-300 mb-8 max-w-md mx-auto">
                {applicationResult.message}
              </p>

              <div className="bg-space-dark rounded-lg p-6 mb-8 text-left">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-accent-cyan" />
                  Next Steps:
                </h3>
                <ul className="space-y-3">
                  {applicationResult.next_steps.map((step, i) => (
                    <li key={i} className="flex items-start gap-2 text-gray-300">
                      <span className="text-accent-cyan mt-1">{i + 1}.</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <Link to="/" className="btn-primary">
                Return to Home
              </Link>
            </div>
          )
        )}
      </div>
    </div>
    </ErrorBoundary>
  );
}