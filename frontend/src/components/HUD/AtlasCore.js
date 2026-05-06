import React, { useEffect, useRef, useState } from 'react';

/**
 * AtlasCore — tappable lava-lamp orb (unified-consciousness viz).
 *
 *  Six plasma blobs (Ajani crimson, Minerva teal, Hermes silver, Council
 *  violet) float against a near-black glass interior. They are painted
 *  to an offscreen canvas as solid radial gradients, then re-drawn to
 *  the main canvas with `filter: blur(N) contrast(M)` — the classic 2D
 *  metaball trick — so blob edges become hard and they fuse into bigger
 *  shapes when they touch. No fog: contrast is high and inside is dark.
 *
 *  Physics:
 *   • Each blob has slow vertical convection (lava-lamp bobbing) plus
 *     lateral wobble.
 *   • Weak mutual repulsion + spring-toward-center keeps composition.
 *   • Jitter scales with `coreState`.
 *
 *  Interaction:
 *   • Tapping anywhere on the orb fires `onActivate` and triggers a
 *     "shock" — every blob picks up an outward impulse so the lava
 *     visibly thrashes for a moment, then relaxes back. This is the
 *     wake / voice-toggle gesture and also a clear "I felt that" cue.
 */

const AI_COLORS = {
  ajani:   { r: 240, g: 50,  b: 70 },  // crimson
  minerva: { r: 40,  g: 200, b: 190 }, // teal
  hermes:  { r: 240, g: 240, b: 250 },
  trinity: { r: 168, g: 120, b: 230 }, // violet
};

const STATE_RHYTHM = {
  idle:      { speed: 0.7,  jitter: 0.06, gravity: 0.85 },
  listening: { speed: 1.6,  jitter: 0.18, gravity: 1.10 },
  thinking:  { speed: 2.4,  jitter: 0.30, gravity: 1.40 },
  speaking:  { speed: 1.8,  jitter: 0.14, gravity: 1.20 },
  alert:     { speed: 3.6,  jitter: 0.42, gravity: 1.55 },
};

// Each persona contributes 1–2 blobs so all colors are alive at once.
const BLOB_RECIPE = [
  { ai: 'ajani',   weight: 1.0, phase: 0.00 },
  { ai: 'ajani',   weight: 0.65, phase: 0.55 },
  { ai: 'minerva', weight: 1.0, phase: 0.20 },
  { ai: 'minerva', weight: 0.60, phase: 0.75 },
  { ai: 'hermes',  weight: 0.75, phase: 0.40 },
  { ai: 'trinity', weight: 0.70, phase: 0.85 },
];

export default function AtlasCore({ activeAI = 'ajani', coreState = 'idle', onActivate }) {
  const canvasRef = useRef(null);
  const offscreenRef = useRef(null);
  const blobsRef = useRef(null);
  const rafRef = useRef(null);
  const startRef = useRef(performance.now());
  const shockRef = useRef(0); // 0..1 — fades after a tap to drive a ripple

  const [tapping, setTapping] = useState(false);

  if (!blobsRef.current) {
    blobsRef.current = BLOB_RECIPE.map((recipe, i) => {
      const a = (i / BLOB_RECIPE.length) * Math.PI * 2;
      return {
        ...recipe,
        x: 0.30 * Math.cos(a),
        y: 0.30 * Math.sin(a),
        vx: 0,
        vy: 0,
        bobAmp: 0.36 + Math.random() * 0.24,
        bobFreq: 0.18 + Math.random() * 0.18,
        wobAmp: 0.22 + Math.random() * 0.20,
        wobFreq: 0.13 + Math.random() * 0.18,
      };
    });
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const cssSize = canvas.getBoundingClientRect().width || 320;
    canvas.width = cssSize * dpr;
    canvas.height = cssSize * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    if (!offscreenRef.current) {
      offscreenRef.current = document.createElement('canvas');
    }
    const off = offscreenRef.current;
    off.width = cssSize * dpr;
    off.height = cssSize * dpr;
    const offCtx = off.getContext('2d');
    offCtx.scale(dpr, dpr);

    const C = cssSize / 2;
    const CORE_R = cssSize * 0.44;
    const BLUR_PX = Math.max(7, cssSize * 0.038);

    let lastT = performance.now();

    const draw = (now) => {
      const dt = Math.min(50, now - lastT);
      lastT = now;
      const t = (now - startRef.current) / 1000;
      const rhythm = STATE_RHYTHM[coreState] || STATE_RHYTHM.idle;
      const ai = AI_COLORS[activeAI] || AI_COLORS.ajani;

      // Decay shock impulse.
      shockRef.current *= 0.92;
      if (shockRef.current < 0.001) shockRef.current = 0;

      // ─── physics ────────────────────────────────────────────────────
      const blobs = blobsRef.current;
      for (let i = 0; i < blobs.length; i++) {
        const b = blobs[i];
        const bobSpeed = b.bobFreq * rhythm.speed;
        const wobSpeed = b.wobFreq * rhythm.speed;
        const targetY = b.bobAmp * Math.sin(t * bobSpeed * Math.PI + b.phase * Math.PI * 2);
        const targetX = b.wobAmp * Math.cos(t * wobSpeed * Math.PI + b.phase * Math.PI * 2);
        b.vx += (targetX - b.x) * 0.0017;
        b.vy += (targetY - b.y) * 0.0017;
        // Center pull.
        b.vx += -b.x * 0.0003 * rhythm.gravity;
        b.vy += -b.y * 0.0003 * rhythm.gravity;
        // Mutual repulsion.
        for (let j = 0; j < blobs.length; j++) {
          if (i === j) continue;
          const o = blobs[j];
          const dx = b.x - o.x;
          const dy = b.y - o.y;
          const d2 = dx * dx + dy * dy + 0.001;
          const force = 0.00004 / d2;
          b.vx += dx * force;
          b.vy += dy * force;
        }
        // Tap shock — push outward radially.
        if (shockRef.current > 0) {
          const r = Math.hypot(b.x, b.y) + 0.001;
          b.vx += (b.x / r) * shockRef.current * 0.012;
          b.vy += (b.y / r) * shockRef.current * 0.012;
        }
        // Turbulence.
        b.vx += (Math.random() - 0.5) * 0.00012 * rhythm.jitter;
        b.vy += (Math.random() - 0.5) * 0.00012 * rhythm.jitter;
        // Damping.
        b.vx *= 0.93;
        b.vy *= 0.93;
        b.x += b.vx * dt;
        b.y += b.vy * dt;
        const r = Math.hypot(b.x, b.y);
        if (r > 0.62) { b.x *= 0.62 / r; b.y *= 0.62 / r; }
      }

      // ─── offscreen blob layer ───────────────────────────────────────
      offCtx.save();
      offCtx.clearRect(0, 0, cssSize, cssSize);
      // Solid dark background fills the offscreen so contrast filter has
      // a clean alpha map to work with — eliminates the foggy halo.
      offCtx.fillStyle = '#000000';
      offCtx.fillRect(0, 0, cssSize, cssSize);
      // Punch out the core circle so blobs exist against transparent.
      offCtx.globalCompositeOperation = 'destination-out';
      offCtx.beginPath();
      offCtx.arc(C, C, CORE_R, 0, Math.PI * 2);
      offCtx.fill();
      offCtx.globalCompositeOperation = 'source-over';

      for (const b of blobs) {
        const isActive = b.ai === activeAI;
        const col = AI_COLORS[b.ai];
        const blobR = CORE_R * 0.34 * b.weight * (isActive ? 1.30 : 1.0);
        const cx = C + b.x * CORE_R;
        const cy = C + b.y * CORE_R;
        // Solid-edged radial gradient: full alpha at center, hard fall-off.
        const g = offCtx.createRadialGradient(cx, cy, 0, cx, cy, blobR);
        g.addColorStop(0,    `rgba(${col.r}, ${col.g}, ${col.b}, 1)`);
        g.addColorStop(0.55, `rgba(${col.r}, ${col.g}, ${col.b}, 0.90)`);
        g.addColorStop(1,    `rgba(${col.r}, ${col.g}, ${col.b}, 0)`);
        offCtx.fillStyle = g;
        offCtx.beginPath();
        offCtx.arc(cx, cy, blobR, 0, Math.PI * 2);
        offCtx.fill();
      }
      offCtx.restore();

      // ─── main canvas ────────────────────────────────────────────────
      ctx.clearRect(0, 0, cssSize, cssSize);

      // Outer bloom.
      const bloom = ctx.createRadialGradient(C, C, CORE_R * 0.85, C, C, CORE_R * 1.7);
      bloom.addColorStop(0, `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.32)`);
      bloom.addColorStop(0.5, `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.10)`);
      bloom.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = bloom;
      ctx.beginPath();
      ctx.arc(C, C, CORE_R * 1.7, 0, Math.PI * 2);
      ctx.fill();

      // Clip to core.
      ctx.save();
      ctx.beginPath();
      ctx.arc(C, C, CORE_R, 0, Math.PI * 2);
      ctx.clip();

      // Dark glass interior — the lamp's "oil".
      const interior = ctx.createRadialGradient(C, C * 0.95, 0, C, C, CORE_R);
      interior.addColorStop(0,   '#0a0410');
      interior.addColorStop(0.7, '#05030a');
      interior.addColorStop(1,   '#000000');
      ctx.fillStyle = interior;
      ctx.fillRect(0, 0, cssSize, cssSize);

      // Lava-lamp blobs: blur + extreme contrast → hard organic edges, no fog.
      ctx.save();
      ctx.filter = `blur(${BLUR_PX}px) contrast(28) saturate(1.35)`;
      ctx.drawImage(off, 0, 0, cssSize, cssSize);
      ctx.restore();

      // Soft inner glow following the same blob silhouettes.
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      ctx.globalAlpha = 0.45;
      ctx.filter = `blur(${BLUR_PX * 0.55}px)`;
      ctx.drawImage(off, 0, 0, cssSize, cssSize);
      ctx.restore();

      // State overlays.
      if (coreState === 'listening') {
        for (let i = 0; i < 3; i++) {
          const phase = ((t * 0.7) + i / 3) % 1;
          const r = CORE_R * (0.42 + phase * 0.55);
          ctx.strokeStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, ${(1 - phase) * 0.55})`;
          ctx.lineWidth = 1.4;
          ctx.beginPath();
          ctx.arc(C, C, r, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
      if (coreState === 'speaking') {
        const p = 0.5 + 0.5 * Math.sin(t * 5);
        ctx.strokeStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, ${0.35 + p * 0.4})`;
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(C, C, CORE_R * (0.93 + p * 0.04), 0, Math.PI * 2);
        ctx.stroke();
      }

      // Tap ripple — outward expanding ring on shock.
      if (shockRef.current > 0.05) {
        const ringR = CORE_R * (0.30 + (1 - shockRef.current) * 0.7);
        const alpha = shockRef.current * 0.7;
        ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(C, C, ringR, 0, Math.PI * 2);
        ctx.stroke();
      }

      ctx.restore(); // end clip

      // Specular highlight on glass surface.
      const spec = ctx.createRadialGradient(
        C - CORE_R * 0.35, C - CORE_R * 0.42, 0,
        C - CORE_R * 0.35, C - CORE_R * 0.42, CORE_R * 0.55
      );
      spec.addColorStop(0, 'rgba(255, 255, 255, 0.28)');
      spec.addColorStop(0.5, 'rgba(255, 255, 255, 0.06)');
      spec.addColorStop(1, 'rgba(255, 255, 255, 0)');
      ctx.save();
      ctx.beginPath();
      ctx.arc(C, C, CORE_R, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = spec;
      ctx.fillRect(0, 0, cssSize, cssSize);
      ctx.restore();

      // Outer rim.
      ctx.strokeStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.65)`;
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(C, C, CORE_R, 0, Math.PI * 2);
      ctx.stroke();

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [activeAI, coreState]);

  const handleTap = () => {
    shockRef.current = 1;        // visible ripple + outward blob impulse
    setTapping(true);
    setTimeout(() => setTapping(false), 200);
    if (onActivate) onActivate();
  };

  return (
    <button
      type="button"
      className={`atlas-core core-state-${coreState} core-ai-${activeAI} ${tapping ? 'tapping' : ''}`}
      style={{
        '--core-bloom': (
          activeAI === 'minerva' ? '40, 200, 190' :
          activeAI === 'hermes'  ? '240, 240, 250' :
          activeAI === 'trinity' ? '168, 120, 230' :
          '240, 50, 70'
        ),
      }}
      onClick={handleTap}
      data-testid="core-orb"
      aria-label="Atlas Core — tap to wake / activate voice"
    >
      <canvas ref={canvasRef} />
    </button>
  );
}
