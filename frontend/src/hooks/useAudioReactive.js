/* eslint-disable */
import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * useAudioReactive — opens the user's mic, runs an AnalyserNode against it,
 * and exposes a smoothed RMS audio level (0..1) that other components can
 * subscribe to via an external `levelRef` instead of triggering React renders
 * (animation frames read it directly so the lava reacts instantly without
 * causing 60 setState calls per second).
 *
 * Usage:
 *   const { start, stop, isActive, levelRef } = useAudioReactive();
 *   // levelRef.current ∈ [0, 1] — read inside requestAnimationFrame loops.
 */
export function useAudioReactive() {
  const [isActive, setIsActive] = useState(false);
  const ctxRef = useRef(null);
  const analyserRef = useRef(null);
  const streamRef = useRef(null);
  const rafRef = useRef(null);
  const levelRef = useRef(0);
  const dataRef = useRef(null);

  const tick = useCallback(() => {
    const analyser = analyserRef.current;
    const buf = dataRef.current;
    if (!analyser || !buf) return;
    analyser.getByteTimeDomainData(buf);
    // Compute RMS deviation from 128 (silence baseline).
    let sum = 0;
    for (let i = 0; i < buf.length; i++) {
      const v = (buf[i] - 128) / 128;
      sum += v * v;
    }
    const rms = Math.sqrt(sum / buf.length); // 0..~1
    // Smooth toward target so visuals don't jitter on tiny spikes.
    const target = Math.min(1, rms * 3.5);   // amplify quiet speech
    levelRef.current = levelRef.current * 0.75 + target * 0.25;
    rafRef.current = requestAnimationFrame(tick);
  }, []);

  const start = useCallback(async () => {
    if (isActive) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const Ctx = window.AudioContext || window.webkitAudioContext;
      const ctx = new Ctx();
      ctxRef.current = ctx;
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      source.connect(analyser);
      analyserRef.current = analyser;
      dataRef.current = new Uint8Array(analyser.fftSize);
      setIsActive(true);
      rafRef.current = requestAnimationFrame(tick);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn('[audio-reactive] mic access failed:', err);
    }
  }, [isActive, tick]);

  const stop = useCallback(() => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (ctxRef.current) {
      try { ctxRef.current.close(); } catch (_) { /* no-op */ }
      ctxRef.current = null;
    }
    analyserRef.current = null;
    dataRef.current = null;
    levelRef.current = 0;
    setIsActive(false);
  }, []);

  useEffect(() => () => stop(), [stop]);

  return { start, stop, isActive, levelRef };
}
