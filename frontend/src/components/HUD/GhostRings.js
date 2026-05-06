import React from 'react';

/**
 * GhostRings — faded background concentric rings that drift slowly at
 * different speeds for a parallax / "living machine" depth effect.
 *
 * Per spec: 5–15% opacity, never overpower the interface, extend nearly
 * edge-to-edge across the HUD bounding frame. Each ring rotates around
 * the core at its own pace so the scene has subtle parallax motion that
 * the eye reads as depth, not animation.
 */

const RINGS = [
  // Inside-out. radiusPct is in viewBox units (svg viewBox 0..100).
  // dur is the rotation period in seconds; alternating directions add subtle layering.
  { r: 38, dur: 90,  reverse: false, opacity: 0.10, dashed: false },
  { r: 47, dur: 140, reverse: true,  opacity: 0.07, dashed: true  },
  { r: 56, dur: 200, reverse: false, opacity: 0.10, dashed: false },
  { r: 64, dur: 75,  reverse: true,  opacity: 0.06, dashed: true  },
  { r: 72, dur: 260, reverse: false, opacity: 0.08, dashed: false },
  { r: 80, dur: 110, reverse: true,  opacity: 0.05, dashed: true  },
  { r: 90, dur: 320, reverse: false, opacity: 0.07, dashed: false },
];

const TICK_COUNT = 48;

export default function GhostRings() {
  return (
    <div className="ghost-rings" aria-hidden="true">
      {RINGS.map((ring, i) => (
        <svg
          key={i}
          className={`ghost-ring ${ring.reverse ? 'reverse' : ''}`}
          viewBox="0 0 100 100"
          preserveAspectRatio="xMidYMid meet"
          style={{
            '--dur': `${ring.dur}s`,
            '--opacity': ring.opacity,
          }}
        >
          <circle
            cx="50" cy="50" r={ring.r}
            fill="none"
            stroke="rgba(120, 170, 240, 0.95)"
            strokeWidth="0.18"
            strokeDasharray={ring.dashed ? '0.6 1.2' : 'none'}
            vectorEffect="non-scaling-stroke"
          />
          {/* Sparse tick markers riding along the ring for engineered detail */}
          {i % 2 === 0 && Array.from({ length: TICK_COUNT }).map((_, k) => {
            const a = (k / TICK_COUNT) * Math.PI * 2;
            const inner = ring.r - 0.6;
            const outer = ring.r + 0.6;
            return (
              <line
                key={k}
                x1={50 + inner * Math.cos(a)}
                y1={50 + inner * Math.sin(a)}
                x2={50 + outer * Math.cos(a)}
                y2={50 + outer * Math.sin(a)}
                stroke="rgba(120, 170, 240, 0.85)"
                strokeWidth={k % 6 === 0 ? 0.25 : 0.12}
                vectorEffect="non-scaling-stroke"
              />
            );
          })}
        </svg>
      ))}
    </div>
  );
}
