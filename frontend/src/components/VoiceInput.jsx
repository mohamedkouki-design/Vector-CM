import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Check, X } from 'lucide-react';

export default function VoiceInput({ onTranscriptComplete, language = 'ar-TN' }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState(null);
  
  const recognitionRef = useRef(null);
  
  useEffect(() => {
    // Check if browser supports Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      setIsSupported(true);
      
      // Initialize recognition
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = language;  // Arabic (Tunisian)
      
      recognition.onstart = () => {
        setIsListening(true);
        setError(null);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognition.onerror = (event) => {
        setError(event.error);
        setIsListening(false);
      };
      
      recognition.onresult = (event) => {
        let interim = '';
        let final = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPart = event.results[i][0].transcript;
          
          if (event.results[i].isFinal) {
            final += transcriptPart + ' ';
          } else {
            interim += transcriptPart;
          }
        }
        
        if (final) {
          setTranscript(prev => prev + final);
        }
        setInterimTranscript(interim);
      };
      
      recognitionRef.current = recognition;
    } else {
      setIsSupported(false);
      setError('Speech recognition not supported in this browser');
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [language]);
  
  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
      } catch (err) {
        console.error('Recognition start error:', err);
      }
    }
  };
  
  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };
  
  const handleComplete = () => {
    stopListening();
    onTranscriptComplete(transcript);
  };
  
  const handleClear = () => {
    setTranscript('');
    setInterimTranscript('');
  };
  
  const speak = (text) => {
    // Text-to-speech for feedback
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language;
      window.speechSynthesis.speak(utterance);
    }
  };
  
  if (!isSupported) {
    return (
      <div className="glass-card p-6">
        <div className="text-center text-gray-400">
          <MicOff className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Voice input not supported in this browser.</p>
          <p className="text-sm mt-2">Please use Chrome or Edge for voice features.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="glass-card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold flex items-center gap-2">
            <Mic className="w-6 h-6 text-accent-cyan" />
            Voice Input
          </h3>
          <p className="text-sm text-gray-400 mt-1">
            Speak naturally about your business and financial situation
          </p>
        </div>
        
        <button
          onClick={() => speak("مرحبا. أخبرني عن عملك")}  // "Hello. Tell me about your business" in Arabic
          className="btn-ghost p-2"
          title="Hear sample prompt"
        >
          <Volume2 className="w-5 h-5" />
        </button>
      </div>
      
      {/* Microphone Button */}
      <div className="text-center mb-6">
        <button
          onClick={isListening ? stopListening : startListening}
          className={`w-24 h-24 rounded-full mx-auto flex items-center justify-center transition-all ${
            isListening 
              ? 'bg-risk-critical animate-pulse-glow shadow-lg shadow-risk-critical/50' 
              : 'bg-accent-cyan hover:bg-accent-cyan/80 shadow-lg shadow-accent-cyan/30'
          }`}
        >
          {isListening ? (
            <MicOff className="w-12 h-12 text-white" />
          ) : (
            <Mic className="w-12 h-12 text-white" />
          )}
        </button>
        
        <p className="mt-4 text-sm text-gray-400">
          {isListening ? 'Listening... Click to stop' : 'Click to start speaking'}
        </p>
      </div>
      
      {/* Transcript Display */}
      <div className="bg-space-dark rounded-lg p-4 min-h-[150px] mb-4">
        {transcript || interimTranscript ? (
          <div className="text-gray-200">
            <span>{transcript}</span>
            <span className="text-gray-500 italic">{interimTranscript}</span>
            <span className="inline-block w-1 h-5 bg-accent-cyan animate-pulse ml-1"></span>
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            Your speech will appear here...
          </div>
        )}
      </div>
      
      {/* Error Display */}
      {error && (
        <div className="bg-risk-critical/20 border border-risk-critical/30 rounded-lg p-3 mb-4">
          <p className="text-sm text-risk-critical">
            Error: {error}
          </p>
        </div>
      )}
      
      {/* Action Buttons */}
      {transcript && (
        <div className="flex gap-3">
          <button
            onClick={handleClear}
            className="btn-secondary flex-1 flex items-center justify-center gap-2"
          >
            <X className="w-4 h-4" />
            Clear
          </button>
          <button
            onClick={handleComplete}
            className="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            <Check className="w-4 h-4" />
            Use Transcript
          </button>
        </div>
      )}
      
      {/* Language Indicator */}
      <div className="mt-4 text-center text-xs text-gray-500">
        Language: {language === 'ar-TN' ? '🇹🇳 Tunisian Arabic' : 
                   language === 'fr-FR' ? '🇫🇷 French' : 
                   '🇬🇧 English'}
      </div>
    </div>
  );
}