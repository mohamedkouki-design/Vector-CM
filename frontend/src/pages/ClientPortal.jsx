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
      let documentPaths = [];
      
      // Step 1: Upload documents if any
      if (documents.length > 0) {
        const formDataToUpload = new FormData();
        documents.forEach(file => {
          formDataToUpload.append('files', file);
        });
        
        const uploadRes = await axios.post(
          'http://localhost:8000/api/v1/applications/upload-documents',
          formDataToUpload,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        );
        
        // Extract paths from response
        documentPaths = uploadRes.data.files.map(f => f.path);
        console.log('Documents uploaded:', documentPaths);
      }
      
      // Step 2: Submit application with document paths
      const body = {
        applicant: formData,
        documents: documentPaths  // Use full paths from upload
      };

      const res = await axios.post('http://localhost:8000/api/v1/applications/submit', body);
      setApplicationResult(res.data);
      setStep(4);
      
      // Also create credit history point with same client_id from the submission
      try {
        const creditHistoryRes = await axios.post('http://localhost:8000/api/v1/applications/add-to-credit-history', {
          client_id: res.data.client_id,  // Use the same client_id from submission
          name: formData.name,
          archetype: formData.archetype,
          years_active: formData.years_active,
          monthly_income: formData.monthly_income,
          debt_ratio: formData.debt_ratio,
          income_stability: formData.income_stability,
          payment_regularity: formData.payment_regularity
        });
        console.log('Credit history point created:', creditHistoryRes.data);
      } catch (creditError) {
        console.warn('Failed to create credit history point:', creditError);
      }
    } catch (error) {
      console.error('Application failed:', error);
    } finally {
      setLoading(false);
    }
  };
  const [useVoiceInput, setUseVoiceInput] = useState(false);
  
  return (
    <ErrorBoundary>
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header Navigation */}
        <Link to="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-blue-300 transition-colors mb-8 font-medium">
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>
        
        {/* Professional Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-400/30 mb-6">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
            <span className="text-sm font-semibold text-blue-300">Credit Application</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
            Apply for Credit
          </h1>
          <p className="text-slate-400 text-lg">
            Complete your application in just a few simple steps
          </p>
        </div>
        
        {/* Professional Progress Steps */}
        <div className="flex items-center justify-center mb-12 gap-2">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                step >= s 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-slate-700 text-slate-400'
              }`}>
                {s}
              </div>
              {s < 4 && (
                <div className={`w-16 h-1 rounded-full transition-all ${
                  step > s ? 'bg-blue-600' : 'bg-slate-700'
                }`} />
              )}
            </div>
          ))}
        </div>
        {/* Voice/Manual Toggle */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-slate-800 border border-slate-700 rounded-lg p-1">
            <button
              onClick={() => setUseVoiceInput(false)}
              className={`px-6 py-3 rounded-md font-semibold transition-all ${
                !useVoiceInput ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              📝 Manual Entry
            </button>
            <button
              onClick={() => setUseVoiceInput(true)}
              className={`px-6 py-3 rounded-md font-semibold transition-all ${
                useVoiceInput ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-slate-400 hover:text-slate-200'
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
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 animate-slide-up">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-white">Step 1: Basic Information</h2>
              <p className="text-slate-400 mt-2">Tell us about yourself and your business</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-white mb-3">
                  Full Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="Enter your full name"
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-400 focus:ring-1 focus:ring-blue-400/50 transition-all"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-white mb-3">
                  Type of Business
                </label>
                <select
                  value={formData.archetype}
                  onChange={(e) => setFormData({...formData, archetype: e.target.value})}
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:border-blue-400 focus:ring-1 focus:ring-blue-400/50 transition-all"
                >
                  <option value="market_vendor">Market Vendor</option>
                  <option value="craftsman">Craftsman</option>
                  <option value="gig_worker">Gig Worker (Taxi/Delivery)</option>
                  <option value="home_business">Home Business</option>
                  <option value="shop_owner">Shop Owner</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-3 text-slate-300">
                  Years in Business: <span className="text-blue-400 font-bold">{formData.years_active} years</span>
                </label>
                <input
                  type="range"
                  min="1"
                  max="30"
                  value={formData.years_active}
                  onChange={(e) => setFormData({...formData, years_active: parseInt(e.target.value)})}
                  className="w-full h-3 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full appearance-none cursor-pointer accent-blue-500"
                  style={{
                    background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${((formData.years_active - 1) / 29) * 100}%, #475569 ${((formData.years_active - 1) / 29) * 100}%, #475569 100%)`
                  }}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-3 text-slate-300">
                  Debt Ratio: <span className="text-blue-400 font-bold">{(formData.debt_ratio * 100).toFixed(0)}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={formData.debt_ratio * 100}
                  onChange={(e) => setFormData({...formData, debt_ratio: parseInt(e.target.value) / 100})}
                  className="w-full h-3 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full appearance-none cursor-pointer accent-blue-500"
                  style={{
                    background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${formData.debt_ratio * 100}%, #475569 ${formData.debt_ratio * 100}%, #475569 100%)`
                  }}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-3 text-slate-300">
                  Income Stability: <span className="text-blue-400 font-bold">{(formData.income_stability * 100).toFixed(0)}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={formData.income_stability * 100}
                  onChange={(e) => setFormData({...formData, income_stability: parseInt(e.target.value) / 100})}
                  className="w-full h-3 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full appearance-none cursor-pointer accent-blue-500"
                  style={{
                    background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${formData.income_stability * 100}%, #475569 ${formData.income_stability * 100}%, #475569 100%)`
                  }}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-3 text-slate-300">
                  Payment Regularity: <span className="text-blue-400 font-bold">{(formData.payment_regularity * 100).toFixed(0)}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={formData.payment_regularity * 100}
                  onChange={(e) => setFormData({...formData, payment_regularity: parseInt(e.target.value) / 100})}
                  className="w-full h-3 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full appearance-none cursor-pointer accent-blue-500"
                  style={{
                    background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${formData.payment_regularity * 100}%, #475569 ${formData.payment_regularity * 100}%, #475569 100%)`
                  }}
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
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed transition-all"
              >
                Continue to Documents →
              </button>
            </div>
          </div>
        )}
        
        {/* Step 2: Documents */}
        {step === 2 && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 animate-slide-up">
            <h2 className="text-2xl font-bold mb-2 text-white">Step 2: Upload Documents</h2>
            <p className="text-slate-400 mb-8">Upload invoices, receipts, or any proof of income. Mobile photos are fine!</p>
            
            <div className="border-2 border-dashed border-slate-600 rounded-lg p-12 text-center mb-8 hover:border-blue-400 transition-colors bg-slate-700/20">
              <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <p className="text-slate-300 mb-3 font-medium">
                Drag and drop files here, or click to browse
              </p>
              <p className="text-slate-500 text-sm mb-4">Supports images and PDFs</p>
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 cursor-pointer inline-block transition-all">
                Choose Files
              </label>
            </div>
            
            {documents.length > 0 && (
              <div className="mb-8 bg-slate-700/30 border border-slate-600/50 rounded-lg p-6">
                <p className="text-sm text-slate-400 mb-4 font-medium">
                  {documents.length} file(s) selected:
                </p>
                <ul className="space-y-2">
                  {documents.map((file, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-center gap-3">
                      <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span className="truncate">{file.name}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="flex gap-4">
              <button
                onClick={() => setStep(1)}
                className="flex-1 px-6 py-3 bg-slate-700/50 text-slate-300 font-semibold rounded-lg hover:bg-slate-600 border border-slate-600/50 transition-all"
              >
                ← Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all"
              >
                Continue to Review →
              </button>
            </div>
          </div>
        )}
        
        {/* Step 3: Review */}
        {step === 3 && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 animate-slide-up">
            <h2 className="text-2xl font-bold mb-2 text-white">Step 3: Review & Submit</h2>
            <p className="text-slate-400 mb-8">Please verify that all information is correct before submitting</p>
            
            <div className="space-y-4 mb-8 bg-slate-700/20 border border-slate-600/30 rounded-lg p-6">
              <div className="flex justify-between py-3 border-b border-slate-600/50">
                <span className="text-slate-400 font-medium">Name:</span>
                <span className="font-semibold text-white">{formData.name}</span>
              </div>
              <div className="flex justify-between py-3 border-b border-slate-600/50">
                <span className="text-slate-400 font-medium">Business Type:</span>
                <span className="font-semibold text-white">{formData.archetype.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between py-3 border-b border-slate-600/50">
                <span className="text-slate-400 font-medium">Years Active:</span>
                <span className="font-semibold text-white">{formData.years_active} years</span>
              </div>
              <div className="flex justify-between py-3 border-b border-slate-600/50">
                <span className="text-slate-400 font-medium">Monthly Income:</span>
                <span className="font-semibold text-blue-400">{formData.monthly_income} TND</span>
              </div>
              <div className="flex justify-between py-3">
                <span className="text-slate-400 font-medium">Documents:</span>
                <span className="font-semibold text-green-400">{documents.length} uploaded</span>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-blue-600/10 to-blue-500/10 border border-blue-400/30 rounded-lg p-6 mb-8">
              <p className="text-sm text-slate-300 flex items-start gap-3">
                <span className="text-lg">✓</span>
                <span>By submitting, you confirm that all information provided is accurate and that you authorize us to verify your details.</span>
              </p>
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={() => setStep(2)}
                className="flex-1 px-6 py-3 bg-slate-700/50 text-slate-300 font-semibold rounded-lg hover:bg-slate-600 border border-slate-600/50 transition-all disabled:opacity-50"
                disabled={loading}
              >
                ← Back
              </button>
              <button
                onClick={submitApplication}
                disabled={loading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed transition-all"
              >
                {loading ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </div>
        )}
        
        {/* Step 4: Result */}
        {step === 4 && applicationResult && (
          applicationResult.created_point ? (
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 animate-scale-in">
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 border border-green-400/50 mb-4">
                  <CheckCircle className="w-8 h-8 text-green-400" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-2">Application Submitted</h2>
                <p className="text-slate-400">Your application has been recorded and is being processed</p>
              </div>

              <div className="bg-slate-700/20 border border-slate-600/30 rounded-lg p-6 mb-8 space-y-6">
                <div>
                  <h4 className="font-semibold text-white mb-3 text-sm uppercase tracking-wider">Client ID</h4>
                  <div className="p-4 bg-slate-700/50 border border-slate-600/50 rounded font-mono text-blue-400">{applicationResult.client_id}</div>
                </div>

                <div>
                  <h4 className="font-semibold text-white mb-3 text-sm uppercase tracking-wider">Initial Risk Snapshot</h4>
                  <pre className="bg-slate-700/50 border border-slate-600/50 p-4 rounded text-sm overflow-auto text-slate-300 max-h-48">{JSON.stringify(applicationResult.created_point, null, 2)}</pre>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-600/10 to-green-500/10 border border-green-400/30 rounded-lg p-6 mb-8">
                <p className="text-sm text-slate-300">
                  An admin will now review your documents and initial risk profile. You can check back here for updates on your application status.
                </p>
              </div>

              <Link to="/" className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all text-center block">
                Return to Home
              </Link>
            </div>
          ) : (
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-xl p-8 animate-scale-in text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-green-500/20 border border-green-400/50 rounded-full mb-6">
                <CheckCircle className="w-10 h-10 text-green-400" />
              </div>

              <h2 className="text-3xl font-bold mb-4 text-green-400">
                Application {applicationResult.status === 'approved' ? 'Approved!' : 'Received'}
              </h2>

              <p className="text-slate-300 mb-8 max-w-md mx-auto leading-relaxed">
                {applicationResult.message}
              </p>

              <div className="bg-slate-700/20 border border-slate-600/30 rounded-lg p-6 mb-8 text-left">
                <h3 className="font-semibold mb-4 flex items-center gap-2 text-white">
                  <Clock className="w-5 h-5 text-blue-400" />
                  Next Steps:
                </h3>
                <ul className="space-y-3">
                  {applicationResult.next_steps.map((step, i) => (
                    <li key={i} className="flex items-start gap-3 text-slate-300">
                      <span className="text-blue-400 font-semibold mt-0.5">{i + 1}.</span>
                      <span className="leading-relaxed">{step}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <Link to="/" className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all text-center block">
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