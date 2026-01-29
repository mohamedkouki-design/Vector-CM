import { useState } from 'react';
import VoiceInput from './VoiceInput';
import { Bot, Sparkles } from 'lucide-react';
import axios from 'axios';

export default function VoiceAssistedForm({ onSubmit }) {
  const [transcript, setTranscript] = useState('');
  const [extractedData, setExtractedData] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [language, setLanguage] = useState('ar-TN');
  
  const handleTranscriptComplete = async (text) => {
    setTranscript(text);
    await extractDataFromSpeech(text);
  };
  
  const extractDataFromSpeech = async (text) => {
    setProcessing(true);
    try {
      // Call backend to extract structured data from speech
      const response = await axios.post('http://localhost:8000/api/v1/voice/extract', {
        transcript: text,
        language: language
      });
      
      setExtractedData(response.data);
    } catch (error) {
      console.error('Failed to extract data:', error);
      
      // Fallback to simple extraction
      const mockExtraction = extractDataSimple(text);
      setExtractedData(mockExtraction);
    } finally {
      setProcessing(false);
    }
  };
  
  const extractDataSimple = (text) => {
    // Simple keyword-based extraction (fallback)
    const lowerText = text.toLowerCase();
    
    let archetype = 'market_vendor';
    if (lowerText.includes('artisan') || lowerText.includes('craftsman')) archetype = 'craftsman';
    if (lowerText.includes('taxi') || lowerText.includes('driver')) archetype = 'gig_worker';
    if (lowerText.includes('shop') || lowerText.includes('store')) archetype = 'shop_owner';
    
    // Extract numbers (very basic)
    const numbers = text.match(/\d+/g);
    const years = numbers && numbers[0] ? parseInt(numbers[0]) : 5;
    const income = numbers && numbers[1] ? parseInt(numbers[1]) : 1500;
    
    return {
      archetype,
      years_active: Math.min(years, 30),
      monthly_income: income,
      confidence: 0.6,
      raw_transcript: text
    };
  };
  
  const handleSubmitExtracted = () => {
    if (extractedData && onSubmit) {
      onSubmit(extractedData);
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Language Selection */}
      <div className="glass-card p-4">
        <label className="block text-sm font-medium mb-2">
          Select Language / اختر اللغة
        </label>
        <div className="grid grid-cols-3 gap-3">
          <button
            onClick={() => setLanguage('ar-TN')}
            className={`p-3 rounded-lg text-center transition-all ${
              language === 'ar-TN' 
                ? 'bg-accent-cyan text-white' 
                : 'bg-space-dark hover:bg-space-light'
            }`}
          >
            🇹🇳 العربية
          </button>
          <button
            onClick={() => setLanguage('fr-FR')}
            className={`p-3 rounded-lg text-center transition-all ${
              language === 'fr-FR' 
                ? 'bg-accent-cyan text-white' 
                : 'bg-space-dark hover:bg-space-light'
            }`}
          >
            🇫🇷 Français
          </button>
          <button
            onClick={() => setLanguage('en-US')}
            className={`p-3 rounded-lg text-center transition-all ${
              language === 'en-US' 
                ? 'bg-accent-cyan text-white' 
                : 'bg-space-dark hover:bg-space-light'
            }`}
          >
            🇬🇧 English
          </button>
        </div>
      </div>
      
      {/* Voice Input */}
      <VoiceInput 
        onTranscriptComplete={handleTranscriptComplete}
        language={language}
      />
      
      {/* Processing Indicator */}
      {processing && (
        <div className="glass-card p-6 text-center animate-pulse-glow">
          <Bot className="w-12 h-12 text-accent-purple mx-auto mb-3 animate-bounce" />
          <p className="text-gray-300">Extracting information from your speech...</p>
        </div>
      )}
      
      {/* Extracted Data Display */}
      {extractedData && !processing && (
        <div className="glass-card p-6 animate-slide-up">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-6 h-6 text-accent-cyan" />
            <h3 className="text-xl font-bold">Extracted Information</h3>
          </div>
          
          <div className="space-y-4 mb-6">
            <div className="flex justify-between items-center p-3 bg-space-dark rounded-lg">
              <span className="text-gray-400">Business Type:</span>
              <span className="font-semibold text-gray-200">
                {extractedData.archetype?.replace('_', ' ')}
              </span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-space-dark rounded-lg">
              <span className="text-gray-400">Years Active:</span>
              <span className="font-semibold text-gray-200">
                {extractedData.years_active} years
              </span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-space-dark rounded-lg">
              <span className="text-gray-400">Monthly Income:</span>
              <span className="font-semibold text-gray-200">
                {extractedData.monthly_income} TND
              </span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-space-dark rounded-lg">
              <span className="text-gray-400">Extraction Confidence:</span>
              <span className={`font-semibold ${
                extractedData.confidence > 0.8 ? 'text-risk-safe' :
                extractedData.confidence > 0.6 ? 'text-risk-medium' :
                'text-risk-high'
              }`}>
                {(extractedData.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          
          {extractedData.confidence < 0.7 && (
            <div className="bg-risk-medium/20 border border-risk-medium/30 rounded-lg p-4 mb-6">
              <p className="text-sm text-risk-medium">
                ⚠️ Low confidence extraction. Please verify the information above.
              </p>
            </div>
          )}
          
          <button
            onClick={handleSubmitExtracted}
            className="btn-primary w-full"
          >
            Use This Information →
          </button>
        </div>
      )}
    </div>
  );
}