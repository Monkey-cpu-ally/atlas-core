import { useEffect, useRef, useState } from "react";

export default function usePerformanceTelemetry(enabled) {
  const [telemetry, setTelemetry] = useState({
    fps: 0,
    frameTime: 0,
    memoryMb: null,
  });
  const lastUpdate = useRef(0);

  useEffect(() => {
    if (!enabled || typeof window === "undefined") return undefined;

    let frameId;
    let frameCount = 0;
    let sampleStart = performance.now();
    let previousFrame = sampleStart;
    let frameTimeTotal = 0;

    function sample(now) {
      frameCount += 1;
      frameTimeTotal += now - previousFrame;
      previousFrame = now;

      if (now - sampleStart >= 1000) {
        const elapsed = now - sampleStart;
        const fps = Math.round((frameCount * 1000) / elapsed);
        const frameTime = Number((frameTimeTotal / Math.max(frameCount, 1)).toFixed(2));
        const memoryBytes = performance.memory?.usedJSHeapSize;
        const memoryMb = memoryBytes ? Math.round(memoryBytes / 1024 / 1024) : null;

        if (now - lastUpdate.current >= 900) {
          setTelemetry({ fps, frameTime, memoryMb });
          lastUpdate.current = now;
        }

        frameCount = 0;
        frameTimeTotal = 0;
        sampleStart = now;
      }

      frameId = requestAnimationFrame(sample);
    }

    frameId = requestAnimationFrame(sample);
    return () => cancelAnimationFrame(frameId);
  }, [enabled]);

  return telemetry;
}
