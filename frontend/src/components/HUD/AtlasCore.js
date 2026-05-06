import React, { useEffect, useRef } from 'react';

/**
 * AtlasCore — unified-consciousness lava-lamp orb.
 *
 *  Functional role: wake area, AI listening indicator, state monitor,
 *  personality transition hub, navigation anchor, audio-reactive viz.
 *
 *  Visual approach:
 *   • Plasma blobs rendered to an OFFSCREEN canvas as solid colored
 *     circles.
 *   • That offscreen layer is then drawn onto the main canvas with a
 *     "blur(N) contrast(M)" filter — the classic 2D metaball trick.
 *     Soft circle edges + heavy contrast clamp the alpha so blobs gain
 *     hard organic edges and visibly fuse into bigger lava-lamp shapes
 *     when they touch.
 *   • A glass shell, specular highlight, soft inner shadow and an outer
 *     bloom finish the "liquid plasma trapped in glass" look.
 *
 *  Physics:
 *   • Each blob has a slow vertical oscillation (lava-lamp convection).
 *   • Weak mutual repulsion keeps them from collapsing into one mass.
 *   • Damped jitter scaled by `coreState` produces alert / listening
 *     bursts of activity.
 *
 *  Interaction:
 *   • A small central disc (`.core-wake`) is the click target so the
 *     surrounding inner ring stays draggable.
 */

const AI_COLORS = {
  ajani:   { r: 240, g: 50,  b: 70,  hex: '#F03246' }, // crimson
  minerva: { r: 40,  g: 200, b: 190, hex: '#28C8BE' }, // teal
  hermes:  { r: 240, g: 240, b: 250, hex: '#F0F0FA' }, // silver
  trinity: { r: 168, g: 120, b: 230, hex: '#A878E6' }, // violet
};

const STATE_RHYTHM = {
  idle:      { speed: 0.6,  jitter: 0.06, gravity: 0.85 },
  listening: { speed: 1.4,  jitter: 0.18, gravity: 1.10 },
  thinking:  { speed: 2.2,  jitter: 0.30, gravity: 1.40 },
  speaking:  { speed: 1.7,  jitter: 0.14, gravity: 1.20 },
  alert:     { speed: 3.5,  jitter: 0.40, gravity: 1.55 },
};

// Each persona contributes 1-2 blobs so all four colors are always alive
// inside the orb (red AND teal floating, even when one AI dominates).
const BLOB_RECIPE = [
  { ai: 'ajani',   weight: 1.0, phase: 0.00 },
  { ai: 'ajani',   weight: 0.7, phase: 0.55 },
  { ai: 'minerva', weight: 1.0, phase: 0.20 },
  { ai: 'minerva', weight: 0.6, phase: 0.75 },
  { ai: 'hermes',  weight: 0.8, phase: 0.40 },
  { ai: 'trinity', weight: 0.7, phase: 0.85 },
];

export default function AtlasCore({ activeAI = 'ajani', coreState = 'idle', onActivate }) {
  const canvasRef = useRef(null);
  const offscreenRef = useRef(null);
  const blobsRef = useRef(null);
  const rafRef = useRef(null);
  const startRef = useRef(performance.now());

  // Initialize blobs once.
  if (!blobsRef.current) {
    blobsRef.current = BLOB_RECIPE.map((recipe, i) => {
      const a = (i / BLOB_RECIPE.length) * Math.PI * 2;
      return {
        ...recipe,
        // normalized [-1, 1]; scaled by core radius at draw time
        x: 0.32 * Math.cos(a),
        y: 0.32 * Math.sin(a),
        vx: 0,
        vy: 0,
        // Per-blob oscillation params for varied motion.
        bobAmp: 0.35 + Math.random() * 0.25,
        bobFreq: 0.18 + Math.random() * 0.18,
        wobAmp: 0.20 + Math.random() * 0.20,
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

    // Offscreen canvas for the metaball layer.
    if (!offscreenRef.current) {
      offscreenRef.current = document.createElement('canvas');
    }
    const off = offscreenRef.current;
    off.width = cssSize * dpr;
    off.height = cssSize * dpr;
    const offCtx = off.getContext('2d');
    offCtx.scale(dpr, dpr);

    const C = cssSize / 2;
    const CORE_R = cssSize * 0.42;
    const BLUR_PX = Math.max(8, cssSize * 0.05);

    let lastT = performance.now();

    const draw = (now) => {
      const dt = Math.min(50, now - lastT);
      lastT = now;
      const t = (now - startRef.current) / 1000;
      const rhythm = STATE_RHYTHM[coreState] || STATE_RHYTHM.idle;

      // ─── Update blob physics ────────────────────────────────────────
      const blobs = blobsRef.current;
      for (let i = 0; i < blobs.length; i++) {
        const b = blobs[i];
        // Lava-lamp vertical bobbing.
        const bobSpeed = b.bobFreq * rhythm.speed;
        const wobSpeed = b.wobFreq * rhythm.speed;
        const targetY = b.bobAmp * Math.sin(t * bobSpeed * Math.PI + b.phase * Math.PI * 2);
        const targetX = b.wobAmp * Math.cos(t * wobSpeed * Math.PI + b.phase * Math.PI * 2);
        // Spring toward target trajectory.
        b.vx += (targetX - b.x) * 0.0015;
        b.vy += (targetY - b.y) * 0.0015;
        // Center pull (gravity) so blobs stay roughly centered.
        b.vx += -b.x * 0.0003 * rhythm.gravity;
        b.vy += -b.y * 0.0003 * rhythm.gravity;
        // Mutual repulsion so they don't all stack on top of each other.
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
        // Tiny turbulence for organic feel.
        b.vx += (Math.random() - 0.5) * 0.00012 * rhythm.jitter;
        b.vy += (Math.random() - 0.5) * 0.00012 * rhythm.jitter;
        // Damping.
        b.vx *= 0.94;
        b.vy *= 0.94;
        b.x += b.vx * dt;
        b.y += b.vy * dt;
        // Soft confine.
        const r = Math.hypot(b.x, b.y);
        if (r > 0.62) { b.x *= 0.62 / r; b.y *= 0.62 / r; }
      }

      // ─── Layer A: paint blobs to offscreen, ───────────────────────
      // then blur+contrast to fuse into lava-lamp metaballs.
      offCtx.save();
      offCtx.clearRect(0, 0, cssSize, cssSize);
      for (const b of blobs) {
        const isActive = b.ai === activeAI;
        const col = AI_COLORS[b.ai];
        const blobR = CORE_R * 0.32 * b.weight * (isActive ? 1.35 : 1.0);
        const cx = C + b.x * CORE_R;
        const cy = C + b.y * CORE_R;
        // Soft radial gradient — combined with blur+contrast on the
        // main canvas this becomes a hard-edged lava blob.
        const g = offCtx.createRadialGradient(cx, cy, 0, cx, cy, blobR);
        const peak = isActive ? 1 : 0.85;
        g.addColorStop(0,    `rgba(${col.r}, ${col.g}, ${col.b}, ${peak})`);
        g.addColorStop(0.55, `rgba(${col.r}, ${col.g}, ${col.b}, ${peak * 0.6})`);
        g.addColorStop(1,    `rgba(${col.r}, ${col.g}, ${col.b}, 0)`);
        offCtx.fillStyle = g;
        offCtx.beginPath();
        offCtx.arc(cx, cy, blobR, 0, Math.PI * 2);
        offCtx.fill();
      }
      offCtx.restore();

      // Clear main canvas.
      ctx.clearRect(0, 0, cssSize, cssSize);

      // ─── Layer 1: outer bloom (drawn before clip) ───────────────────
      const ai = AI_COLORS[activeAI] || AI_COLORS.ajani;
      const bloom = ctx.createRadialGradient(C, C, CORE_R * 0.85, C, C, CORE_R * 1.7);
      bloom.addColorStop(0, `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.30)`);
      bloom.addColorStop(0.5, `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.10)`);
      bloom.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = bloom;
      ctx.beginPath();
      ctx.arc(C, C, CORE_R * 1.7, 0, Math.PI * 2);
      ctx.fill();

      // ─── Clip to core circle for everything inside the glass ────────
      ctx.save();
      ctx.beginPath();
      ctx.arc(C, C, CORE_R, 0, Math.PI * 2);
      ctx.clip();

      // ─── Layer 2: glass shell back ──────────────────────────────────
      const shellBack = ctx.createRadialGradient(C, C * 0.92, 0, C, C, CORE_R);
      shellBack.addColorStop(0,    'rgba(12, 8, 18, 0.0)');
      shellBack.addColorStop(0.55, 'rgba(12, 8, 18, 0.15)');
      shellBack.addColorStop(0.92, 'rgba(8,  6, 14, 0.45)');
      shellBack.addColorStop(1,    'rgba(8,  6, 14, 0.6)');
      ctx.fillStyle = shellBack;
      ctx.fillRect(0, 0, cssSize, cssSize);

      // ─── Layer 3: lava-lamp metaballs ───────────────────────────────
      // Heavy blur + extreme contrast = blobs with hard organic edges
      // that merge into bigger shapes when they touch.
      ctx.save();
      ctx.filter = `blur(${BLUR_PX}px) contrast(18) saturate(1.25)`;
      ctx.drawImage(off, 0, 0, cssSize, cssSize);
      ctx.restore();

      // Layer 3b: subtle re-paint of the same blobs un-thresholded for
      // a soft inner glow that follows the same shapes.
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      ctx.globalAlpha = 0.35;
      ctx.filter = `blur(${BLUR_PX * 0.6}px)`;
      ctx.drawImage(off, 0, 0, cssSize, cssSize);
      ctx.restore();

      // ─── Layer 4: state-driven overlays ─────────────────────────────
      if (coreState === 'listening') {
        for (let i = 0; i < 3; i++) {
          const phase = ((t * 0.6) + i / 3) % 1;
          const r = CORE_R * (0.42 + phase * 0.55);
          ctx.strokeStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, ${(1 - phase) * 0.5})`;
          ctx.lineWidth = 1.4;
          ctx.beginPath();
          ctx.arc(C, C, r, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
      if (coreState === 'speaking') {
        const p = 0.5 + 0.5 * Math.sin(t * 5);
        ctx.strokeStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, ${0.35 + p * 0.35})`;
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(C, C, CORE_R * (0.93 + p * 0.04), 0, Math.PI * 2);
        ctx.stroke();
      }
      if (coreState === 'alert') {
        ctx.fillStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, ${0.18 * Math.abs(Math.sin(t * 9))})`;
        ctx.fillRect(0, 0, cssSize, cssSize);
      }

      ctx.restore(); // end clip

      // ─── Layer 5: glass front specular + rim ────────────────────────
      const spec = ctx.createRadialGradient(
        C - CORE_R * 0.35, C - CORE_R * 0.4, 0,
        C - CORE_R * 0.35, C - CORE_R * 0.4, CORE_R * 0.55
      );
      spec.addColorStop(0, 'rgba(255, 255, 255, 0.22)');
      spec.addColorStop(0.5, 'rgba(255, 255, 255, 0.05)');
      spec.addColorStop(1, 'rgba(255, 255, 255, 0)');
      ctx.save();
      ctx.beginPath();
      ctx.arc(C, C, CORE_R, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = spec;
      ctx.fillRect(0, 0, cssSize, cssSize);
      ctx.restore();

      // Outer rim ring
      ctx.strokeStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.55)`;
      ctx.lineWidth = 1;
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

  return (
    <div
      className={`atlas-core core-state-${coreState} core-ai-${activeAI}`}
      style={{
        '--core-bloom': (
          activeAI === 'minerva' ? '40, 200, 190' :
          activeAI === 'hermes'  ? '240, 240, 250' :
          activeAI === 'trinity' ? '168, 120, 230' :
          '240, 50, 70' // ajani default
        ),
      }}
      data-testid="core-orb"
    >
      <canvas ref={canvasRef} />
      <button
        type="button"
        className="core-wake"
        onClick={onActivate}
        data-testid="core-wake"
        aria-label="Atlas Core — wake / activate voice"
      />
    </div>
  );
}
