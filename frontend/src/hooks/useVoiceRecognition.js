import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Web Speech API wrapper — Phase 4 voice system.
 *
 * Modes:
 *   'off'     → recognition off
 *   'push'    → push-to-talk: one utterance, stops on silence
 *   'wake'    → continuous wake-word: listens forever, restarts on end;
 *               every final transcript is delivered raw and the consumer
 *               decides whether it starts with the wake phrase.
 *
 * Callbacks are held in refs so they can change without re-creating the
 * SpeechRecognition instance (which was the root cause of voice dying
 * after the first render in the legacy hook).
 */
export function useVoiceRecognition({
  onResult,           // (transcript, isFinal) => void
  onListeningChange,  // (isListening) => void
  onError,            // (errorCode) => void
} = {}) {
  // Lazy initial — checked once at mount, never re-runs.
  const [isSupported] = useState(() =>
    typeof window !== 'undefined'
    && !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  );
  const [mode, setMode] = useState('off');
  const recognitionRef = useRef(null);
  const listeningRef = useRef(false);
  const modeRef = useRef('off');
  useEffect(() => { modeRef.current = mode; }, [mode]);

  const onResultRef = useRef(onResult);
  const onListeningChangeRef = useRef(onListeningChange);
  const onErrorRef = useRef(onError);
  useEffect(() => { onResultRef.current = onResult; }, [onResult]);
  useEffect(() => { onListeningChangeRef.current = onListeningChange; }, [onListeningChange]);
  useEffect(() => { onErrorRef.current = onError; }, [onError]);

  useEffect(() => {
    if (!isSupported) return undefined;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = true;
    rec.lang = 'en-US';
    rec.maxAlternatives = 1;

    rec.onresult = (event) => {
      const results = Array.from(event.results);
      const transcript = results.map((r) => r[0].transcript).join('');
      const last = results[results.length - 1];
      if (onResultRef.current) {
        onResultRef.current(transcript, !!last?.isFinal);
      }
    };

    rec.onerror = (event) => {
      // eslint-disable-next-line no-console
      console.warn('[voice] error:', event.error);
      if (onErrorRef.current) onErrorRef.current(event.error);
      listeningRef.current = false;
      if (onListeningChangeRef.current) onListeningChangeRef.current(false);
    };

    rec.onend = () => {
      listeningRef.current = false;
      if (onListeningChangeRef.current) onListeningChangeRef.current(false);
      // In wake-word mode the browser stops the engine every ~60s — auto-restart.
      if (modeRef.current === 'wake') {
        try {
          rec.start();
        } catch (_) { /* InvalidStateError on rapid restart — ignore */ }
      }
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
  }, []);

  const _ensureMic = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) return true;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((t) => t.stop());
      return true;
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn('[voice] mic permission denied:', err);
      if (onErrorRef.current) onErrorRef.current('not-allowed');
      return false;
    }
  }, []);

  const startPushToTalk = useCallback(async () => {
    if (!recognitionRef.current) return;
    if (!(await _ensureMic())) return;
    recognitionRef.current.continuous = false;
    setMode('push');
    try {
      recognitionRef.current.start();
    } catch (e) {
      // eslint-disable-next-line no-console
      console.warn('[voice] start failed:', e?.message || e);
    }
  }, [_ensureMic]);

  const startWakeWord = useCallback(async () => {
    if (!recognitionRef.current) return;
    if (!(await _ensureMic())) return;
    recognitionRef.current.continuous = true;
    setMode('wake');
    try {
      recognitionRef.current.start();
    } catch (e) {
      // eslint-disable-next-line no-console
      console.warn('[voice] wake start failed:', e?.message || e);
    }
  }, [_ensureMic]);

  const stop = useCallback(() => {
    setMode('off');
    if (!recognitionRef.current) return;
    try { recognitionRef.current.stop(); } catch (_) { /* no-op */ }
  }, []);

  return {
    isSupported,
    mode,
    startPushToTalk,
    startWakeWord,
    stop,
  };
}
