import { useCallback, useEffect, useRef } from 'react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

/**
 * useTTS — synthesizes speech via the backend `/api/ai/tts` endpoint and
 * plays it back through an in-memory <audio> element.
 *
 * Per-call options:
 *   speak(text, persona, {
 *     onStart, onEnd,
 *     provider,   // 'elevenlabs' | 'openai' (omit = backend chooses)
 *     language,   // 'en' | 'zu' | 'yo' | 'maa' | …
 *     voice,      // explicit voice id override
 *     model,      // 'eleven_multilingual_v2' | 'tts-1' | …
 *   })
 *
 * Calling speak() again interrupts the previous utterance, and the
 * in-flight fetch is aborted via AbortController. The hook also aborts
 * everything on unmount so navigating away from a panel mid-generation
 * does not leak network requests.
 */
export function useTTS() {
  const audioRef = useRef(null);
  const isSpeakingRef = useRef(false);
  const objectUrlRef = useRef(null);
  const abortRef = useRef(null);

  const stop = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
      audioRef.current = null;
    }
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
    isSpeakingRef.current = false;
  }, []);

  // Abort any in-flight TTS request when the consuming component unmounts.
  useEffect(() => () => stop(), [stop]);

  const speak = useCallback(async (text, persona = 'ajani', opts = {}) => {
    const { onStart, onEnd, provider, language, voice, model } = opts;
    if (!text || !text.trim()) return;
    // Cancel any previous playback / fetch.
    stop();

    const controller = new AbortController();
    abortRef.current = controller;

    let response;
    try {
      response = await fetch(`${BACKEND}/api/ai/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          text: text.slice(0, 4096),
          persona,
          ...(provider ? { provider } : {}),
          ...(language ? { language } : {}),
          ...(voice ? { voice } : {}),
          ...(model ? { model } : {}),
        }),
      });
    } catch (err) {
      if (err?.name !== 'AbortError') {
        // eslint-disable-next-line no-console
        console.warn('[tts] network error:', err);
      }
      return;
    }
    if (abortRef.current !== controller) return;   // superseded by stop()
    if (!response.ok) {
      // eslint-disable-next-line no-console
      console.warn('[tts] backend error:', response.status);
      return;
    }
    const blob = await response.blob();
    if (abortRef.current !== controller) return;   // user aborted mid-stream
    const url = URL.createObjectURL(blob);
    objectUrlRef.current = url;

    const audio = new Audio(url);
    audioRef.current = audio;
    isSpeakingRef.current = true;
    if (onStart) onStart();

    return new Promise((resolve) => {
      audio.onended = () => {
        isSpeakingRef.current = false;
        if (objectUrlRef.current === url) {
          URL.revokeObjectURL(url);
          objectUrlRef.current = null;
        }
        if (onEnd) onEnd();
        resolve();
      };
      audio.onerror = () => {
        isSpeakingRef.current = false;
        if (onEnd) onEnd();
        resolve();
      };
      audio.play().catch(() => {
        // autoplay blocked — surface a clean failure
        isSpeakingRef.current = false;
        if (onEnd) onEnd();
        resolve();
      });
    });
  }, [stop]);

  return { speak, stop, isSpeakingRef };
}
