import { useState, useCallback, useRef, useEffect } from 'react';

export function useVoiceRecognition({ onResult, onListeningChange }) {
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setIsSupported(true);
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const results = Array.from(event.results);
        const transcript = results
          .map(result => result[0].transcript)
          .join('');
        
        if (results[results.length - 1]?.isFinal) {
          onResult(transcript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'not-allowed') {
          onListeningChange(false);
        }
      };

      recognitionRef.current.onend = () => {
        onListeningChange(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [onResult, onListeningChange]);

  const startListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
        onListeningChange(true);
      } catch (e) {
        console.error('Failed to start recognition:', e);
      }
    }
  }, [onListeningChange]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      onListeningChange(false);
    }
  }, [onListeningChange]);

  return {
    isSupported,
    startListening,
    stopListening
  };
}
