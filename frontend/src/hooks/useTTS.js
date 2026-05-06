import { useCallback, useRef } from 'react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

/**
 * useTTS — synthesizes speech via the backend `/api/ai/tts` endpoint and
 * plays it back through an in-memory <audio> element. Tracks the current
 * playback so calling `speak()` again interrupts the previous utterance
 * instead of stacking voices on top of each other.
 *
 *   const { speak, stop, isSpeakingRef } = useTTS();
 *   await speak('Hello world', 'minerva');   // resolves when audio ends
 */
export function useTTS() {
  const audioRef = useRef(null);
  const isSpeakingRef = useRef(false);
  const objectUrlRef = useRef(null);

  const stop = useCallback(() => {
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

  const speak = useCallback(async (text, persona = 'ajani', { onStart, onEnd } = {}) => {
    if (!text || !text.trim()) return;
    // Cancel any previous playback.
    stop();

    let response;
    try {
      response = await fetch(`${BACKEND}/api/ai/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.slice(0, 4096), persona }),
      });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn('[tts] network error:', err);
      return;
    }
    if (!response.ok) {
      // eslint-disable-next-line no-console
      console.warn('[tts] backend error:', response.status);
      return;
    }
    const blob = await response.blob();
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
