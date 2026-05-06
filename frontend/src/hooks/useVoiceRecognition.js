import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Web Speech API wrapper. Uses refs so callbacks can change without
 * re-initializing the recognition instance (which was the root cause
 * of voice commands silently dying after the first render).
 */
export function useVoiceRecognition({ onResult, onListeningChange, onError }) {
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef(null);
  const listeningRef = useRef(false);

  // Keep the latest callbacks in refs so we don't recreate recognition.
  const onResultRef = useRef(onResult);
  const onListeningChangeRef = useRef(onListeningChange);
  const onErrorRef = useRef(onError);
  useEffect(() => { onResultRef.current = onResult; }, [onResult]);
  useEffect(() => { onListeningChangeRef.current = onListeningChange; }, [onListeningChange]);
  useEffect(() => { onErrorRef.current = onError; }, [onError]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }
    setIsSupported(true);

    const rec = new SpeechRecognition();
    rec.continuous = false;      // one utterance per click — clearer UX
    rec.interimResults = true;
    rec.lang = 'en-US';
    rec.maxAlternatives = 1;

    rec.onresult = (event) => {
      const results = Array.from(event.results);
      const transcript = results.map(r => r[0].transcript).join('');
      const last = results[results.length - 1];
      // Stream interim to UI, but only commit final result.
      if (onResultRef.current) {
        onResultRef.current(transcript, !!last?.isFinal);
      }
    };

    rec.onerror = (event) => {
      // Common errors: 'not-allowed', 'service-not-allowed', 'no-speech',
      // 'audio-capture', 'network', 'aborted'
      // eslint-disable-next-line no-console
      console.warn('[voice] error:', event.error);
      if (onErrorRef.current) onErrorRef.current(event.error);
      listeningRef.current = false;
      if (onListeningChangeRef.current) onListeningChangeRef.current(false);
    };

    rec.onend = () => {
      listeningRef.current = false;
      if (onListeningChangeRef.current) onListeningChangeRef.current(false);
    };

    rec.onstart = () => {
      listeningRef.current = true;
      if (onListeningChangeRef.current) onListeningChangeRef.current(true);
    };

    recognitionRef.current = rec;

    return () => {
      try { rec.abort(); } catch (_) { /* no-op */ }
      recognitionRef.current = null;
    };
  }, []); // initialize once

  const startListening = useCallback(async () => {
    if (!recognitionRef.current) return;
    if (listeningRef.current) return; // already active

    // Proactively request mic permission so we can surface failures clearly.
    try {
      if (navigator.mediaDevices?.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // We only needed the permission gate — release the mic immediately.
        stream.getTracks().forEach(t => t.stop());
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn('[voice] mic permission denied:', err);
      if (onErrorRef.current) onErrorRef.current('not-allowed');
      return;
    }

    try {
      recognitionRef.current.start();
    } catch (e) {
      // Calling start() twice throws InvalidStateError — ignore.
      // eslint-disable-next-line no-console
      console.warn('[voice] start failed:', e?.message || e);
    }
  }, []);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return;
    try {
      recognitionRef.current.stop();
    } catch (_) { /* no-op */ }
  }, []);

  return {
    isSupported,
    startListening,
    stopListening,
  };
}
