/* eslint-disable */
import React, { useEffect, useRef } from 'react';

/**
 * AtlasCore — unified-consciousness orb.
 *
 *  Stacked layers (back → front):
 *   1. Outer glow shell           — bloom radiating into the rings
 *   2. Transparent lens           — soft top-left specular highlight
 *   3. Energy containment ring    — bright inner rim
 *   4. Floating plasma sphere     — lava-lamp metaballs (5 personas + 1 ambient magenta)
 *   5. Inner particle system      — drifting bright sparks
 *   6. Central pulse nucleus      — slow breathing white-hot center
 *
 *  Depth illusion: the orb feels both recessed inward AND protruding outward
 *  by combining a deep inner-bottom shadow (recess) with a bright top-left
 *  specular highlight (protrude). Subtle slow rotation + wobble of the whole
 *  composition keeps the holographic feel without ever feeling animated.
 *
 *  Motion is intentionally slow — calm, intelligent, ancient, powerful.
 *  Internal physics: spring-pulled metaballs + mutual repulsion + per-blob
 *  bobbing + jitter scaled by `coreState`. On tap, every blob and particle
 *  picks up an outward radial impulse and a white ripple ring expands.
 */

const AI_COLORS = {
  ajani:   { r: 240, g: 50,  b: 70  }, // crimson
  minerva: { r: 40,  g: 200, b: 190 }, // teal / cyan
  hermes:  { r: 240, g: 240, b: 250 }, // silver-white
  trinity: { r: 168, g: 120, b: 230 }, // soft purple
};
const STATE_RHYTHM = {
  // Motion is slow on purpose. Nothing fast.
  idle:      { speed: 0.45, jitter: 0.05, gravity: 0.85, partAlpha: 0.55 },
  listening: { speed: 1.10, jitter: 0.16, gravity: 1.10, partAlpha: 0.85 },
  thinking:  { speed: 1.70, jitter: 0.26, gravity: 1.40, partAlpha: 0.95 },
  speaking:  { speed: 1.30, jitter: 0.12, gravity: 1.20, partAlpha: 0.80 },
  alert:     { speed: 2.50, jitter: 0.36, gravity: 1.55, partAlpha: 1.00 },
};

// Multiple blobs create sticky lava-lamp motion, but ATLAS displays one AI color at a time.
// Color handoffs are slow and living, never instant UI state changes.
const BLOB_RECIPE = [
  { ai: 'ajani',   weight: 1.00, phase: 0.00 },
  { ai: 'ajani',   weight: 0.65, phase: 0.55 },
  { ai: 'ajani',   weight: 0.45, phase: 0.30 },
  { ai: 'minerva', weight: 1.00, phase: 0.20 },
  { ai: 'minerva', weight: 0.60, phase: 0.75 },
  { ai: 'minerva', weight: 0.45, phase: 0.10 },
  { ai: 'hermes',  weight: 0.70, phase: 0.40 },
  { ai: 'hermes',  weight: 0.40, phase: 0.65 },
  { ai: 'trinity', weight: 0.70, phase: 0.85 },
  { ai: '__magenta__', weight: 0.55, phase: 0.30 },
  { ai: '__magenta__', weight: 0.40, phase: 0.95 },
];

const PARTICLE_COUNT = 22;

// Pre-built lookup so we don't allocate during draw.
const BLOB_SEGMENTS = 22;

export default function AtlasCore({
  activeAI = 'ajani',
  coreState = 'idle',
  onActivate,
  audioLevelRef,    // optional: { current: 0..1 } from useAudioReactive
}) {
  const canvasRef = useRef(null);
  const offscreenRef = useRef(null);
  const blobsRef = useRef(null);
  const particlesRef = useRef(null);
  const rafRef = useRef(null);
  const startRef = useRef(performance.now());
  const shockRef = useRef(0); // 0..1 fades after a tap
  const fluidColorRef = useRef({ r: 240, g: 50, b: 70 }); // slow 2.5D color handoff

  // Initialize blobs + particles once — lazy useRef pattern wrapped in an
  // effect so the linter's "no impure render" rule is satisfied (Math.random
  // is impure but acceptable inside useEffect).
  useEffect(() => {
    if (blobsRef.current == null) {
      blobsRef.current = BLOB_RECIPE.map((recipe, i) => {
        const a = (i / BLOB_RECIPE.length) * Math.PI * 2;
        return {
          ...recipe,
          x: 0.30 * Math.cos(a),
          y: 0.30 * Math.sin(a),
          vx: 0,
          vy: 0,
          bobAmp: 0.34 + Math.random() * 0.22,
          bobFreq: 0.14 + Math.random() * 0.16,
          wobAmp: 0.22 + Math.random() * 0.18,
          wobFreq: 0.10 + Math.random() * 0.16,
        };
      });
    }
    if (particlesRef.current == null) {
      particlesRef.current = Array.from({ length: PARTICLE_COUNT }).map(() => {
        const a = Math.random() * Math.PI * 2;
        const r = 0.15 + Math.random() * 0.45;
        return {
          x: r * Math.cos(a),
          y: r * Math.sin(a),
          vx: (Math.random() - 0.5) * 0.0008,
          vy: (Math.random() - 0.5) * 0.0008,
          life: Math.random(),
          size: 0.6 + Math.random() * 1.4,
        };
      });
    }
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const cssSize = canvas.getBoundingClientRect().width || 320;
    canvas.width = cssSize * dpr;
    canvas.height = cssSize * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    if (!offscreenRef.current) offscreenRef.current = document.createElement('canvas');
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
      const targetAI = AI_COLORS[activeAI] || AI_COLORS.ajani;
      const fluid = fluidColorRef.current;
      const lerpAmount = Math.min(1, dt / 2600); // slow color transition, never a snap
      fluid.r += (targetAI.r - fluid.r) * lerpAmount;
      fluid.g += (targetAI.g - fluid.g) * lerpAmount;
      fluid.b += (targetAI.b - fluid.b) * lerpAmount;
      const ai = fluid;

      // Audio-reactive boost — when the user is talking during listening,
      // the lava physically reacts to the mic level. Falls back to 0 when
      // no audio is being captured.
      const audioLevel = audioLevelRef?.current ?? 0;
      const audioBoost = 1 + audioLevel * 1.6;
      const liveJitter = rhythm.jitter * audioBoost;
      const liveSpeed  = rhythm.speed  * (1 + audioLevel * 0.6);

      shockRef.current *= 0.92;
      if (shockRef.current < 0.001) shockRef.current = 0;

      // Slow global wobble + rotation of the whole composition.
      const wobbleX = Math.sin(t * 0.18) * 0.012;
      const wobbleY = Math.cos(t * 0.14) * 0.012;
      const slowRot = t * 0.04; // ~157s per revolution

      // ─── physics: blobs ─────────────────────────────────────────────
      const blobs = blobsRef.current;
      for (let i = 0; i < blobs.length; i++) {
        const b = blobs[i];
        const bobSpeed = b.bobFreq * liveSpeed;
        const wobSpeed = b.wobFreq * liveSpeed;
        const targetY = b.bobAmp * Math.sin(t * bobSpeed * Math.PI + b.phase * Math.PI * 2);
        const targetX = b.wobAmp * Math.cos(t * wobSpeed * Math.PI + b.phase * Math.PI * 2);
        b.vx += (targetX - b.x) * 0.0017;
        b.vy += (targetY - b.y) * 0.0017;
        b.vx += -b.x * 0.0003 * rhythm.gravity;
        b.vy += -b.y * 0.0003 * rhythm.gravity;
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
        if (shockRef.current > 0) {
          const r = Math.hypot(b.x, b.y) + 0.001;
          b.vx += (b.x / r) * shockRef.current * 0.012;
          b.vy += (b.y / r) * shockRef.current * 0.012;
        }
        b.vx += (Math.random() - 0.5) * 0.00012 * liveJitter;
        b.vy += (Math.random() - 0.5) * 0.00012 * liveJitter;
        b.vx *= 0.93;
        b.vy *= 0.93;
        b.x += b.vx * dt;
        b.y += b.vy * dt;
        const r = Math.hypot(b.x, b.y);
        if (r > 0.62) { b.x *= 0.62 / r; b.y *= 0.62 / r; }
      }

      // ─── physics: particles ─────────────────────────────────────────
      const particles = particlesRef.current;
      for (const p of particles) {
        // Soft drift toward nearest plasma blob — particles cluster near color masses.
        let nearest = null;
        let minD = Infinity;
        for (const b of blobs) {
          const dx = b.x - p.x;
          const dy = b.y - p.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < minD) { minD = d2; nearest = b; }
        }
        if (nearest) {
          p.vx += (nearest.x - p.x) * 0.00009;
          p.vy += (nearest.y - p.y) * 0.00009;
        }
        p.vx += (Math.random() - 0.5) * 0.00006 * liveJitter;
        p.vy += (Math.random() - 0.5) * 0.00006 * liveJitter;
        if (shockRef.current > 0) {
          const r = Math.hypot(p.x, p.y) + 0.001;
          p.vx += (p.x / r) * shockRef.current * 0.018;
          p.vy += (p.y / r) * shockRef.current * 0.018;
        }
        p.vx *= 0.96;
        p.vy *= 0.96;
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        const pr = Math.hypot(p.x, p.y);
        if (pr > 0.65) { p.x *= 0.65 / pr; p.y *= 0.65 / pr; }
        p.life += 0.0008 * dt;
      }

      // ─── offscreen blob layer (for metaball blur+contrast) ──────────
      offCtx.save();
      offCtx.clearRect(0, 0, cssSize, cssSize);
      offCtx.fillStyle = '#000000';
      offCtx.fillRect(0, 0, cssSize, cssSize);
      offCtx.globalCompositeOperation = 'destination-out';
      offCtx.beginPath();
      offCtx.arc(C, C, CORE_R, 0, Math.PI * 2);
      offCtx.fill();
      offCtx.globalCompositeOperation = 'source-over';

      offCtx.translate(C, C);
      offCtx.rotate(slowRot);
      offCtx.translate(-C, -C);

      for (const b of blobs) {
        // One-color-at-a-time rule: all internal lava uses the active AI fluid color.
        // Individual blobs still have different size/phase so the core feels sticky and alive.
        const isActive = b.ai === activeAI;
        const col = ai;
        const blobR = CORE_R * 0.34 * b.weight * (isActive ? 1.16 : 0.96);
        const cx = C + (b.x + wobbleX) * CORE_R;
        const cy = C + (b.y + wobbleY) * CORE_R;

        // Velocity-based squash/stretch: blob elongates in direction of motion.
        const speed = Math.hypot(b.vx, b.vy);
        const stretch = Math.min(1.4, 1 + speed * 35);
        const angle = Math.atan2(b.vy, b.vx);

        // Build a deformed organic path so blobs aren't perfect circles.
        // Each angular sample is perturbed by two sine waves running at
        // different speeds — natural-looking ink-in-water deformation.
        offCtx.save();
        offCtx.translate(cx, cy);
        offCtx.rotate(angle);
        offCtx.scale(stretch, 1 / Math.sqrt(stretch));
        offCtx.beginPath();
        for (let s = 0; s <= BLOB_SEGMENTS; s++) {
          const a = (s / BLOB_SEGMENTS) * Math.PI * 2;
          const wob =
            0.10 * Math.sin(a * 3 + t * 0.9 + b.phase * 6) +
            0.06 * Math.sin(a * 5 - t * 1.4 + b.phase * 9) +
            0.04 * Math.cos(a * 2 + t * 0.6);
          const r = blobR * (1 + wob);
          const px = r * Math.cos(a);
          const py = r * Math.sin(a);
          if (s === 0) offCtx.moveTo(px, py);
          else offCtx.lineTo(px, py);
        }
        offCtx.closePath();
        const g = offCtx.createRadialGradient(0, 0, 0, 0, 0, blobR);
        g.addColorStop(0,    `rgba(${col.r}, ${col.g}, ${col.b}, 1)`);
        g.addColorStop(0.55, `rgba(${col.r}, ${col.g}, ${col.b}, 0.92)`);
        g.addColorStop(1,    `rgba(${col.r}, ${col.g}, ${col.b}, 0)`);
        offCtx.fillStyle = g;
        offCtx.fill();
        offCtx.restore();
      }
      offCtx.restore();

      // ─── main canvas ────────────────────────────────────────────────
      ctx.clearRect(0, 0, cssSize, cssSize);

      // Layer 1 — outer glow shell, fades softly into darkness.
      const bloom = ctx.createRadialGradient(C, C, CORE_R * 0.85, C, C, CORE_R * 1.7);
      bloom.addColorStop(0,   `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.32)`);
      bloom.addColorStop(0.5, `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.10)`);
      bloom.addColorStop(1,   'rgba(0,0,0,0)');
      ctx.fillStyle = bloom;
      ctx.beginPath();
      ctx.arc(C, C, CORE_R * 1.7, 0, Math.PI * 2);
      ctx.fill();

      // Clip everything inside the orb.
      ctx.save();
      ctx.beginPath();
      ctx.arc(C, C, CORE_R, 0, Math.PI * 2);
      ctx.clip();

      // Glass interior — deep dark gradient with subtle convex shape.
      const interior = ctx.createRadialGradient(
        C - CORE_R * 0.15, C - CORE_R * 0.15, 0,
        C, C, CORE_R
      );
      interior.addColorStop(0,    '#100618');
      interior.addColorStop(0.55, '#06030c');
      interior.addColorStop(1,    '#000000');
      ctx.fillStyle = interior;
      ctx.fillRect(0, 0, cssSize, cssSize);

      // Layer 4 — lava-lamp metaballs. Lower contrast + slightly larger
      // blur than before = soft fluid edges that flow into each other,
      // closer to ink-in-water than glass marbles.
      ctx.save();
      ctx.filter = `blur(${BLUR_PX * 1.15}px) contrast(14) saturate(1.4)`;
      ctx.drawImage(off, 0, 0, cssSize, cssSize);
      ctx.restore();

      // Soft inner glow following the same blob silhouettes — adds the
      // "wet" sheen of liquid plasma.
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      ctx.globalAlpha = 0.55;
      ctx.filter = `blur(${BLUR_PX * 0.6}px)`;
      ctx.drawImage(off, 0, 0, cssSize, cssSize);
      ctx.restore();

      // Layer 5 — particle system. Drift bright sparks above the plasma.
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      for (const p of particles) {
        const px = C + (p.x + wobbleX) * CORE_R;
        const py = C + (p.y + wobbleY) * CORE_R;
        const tw = (Math.sin(t * 2 + p.life) + 1) * 0.5;
        const a = (0.4 + tw * 0.6) * rhythm.partAlpha;
        const sz = p.size * (0.8 + tw * 0.4);
        const g2 = ctx.createRadialGradient(px, py, 0, px, py, sz * 4);
        g2.addColorStop(0, `rgba(255, 230, 250, ${a})`);
        g2.addColorStop(1, 'rgba(255, 230, 250, 0)');
        ctx.fillStyle = g2;
        ctx.beginPath();
        ctx.arc(px, py, sz * 4, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      // Layer 6 — central pulse nucleus. Slow breathing white-hot core.
      const nuclePulse = 0.5 + 0.5 * Math.sin(t * 0.9);
      const nucleR = CORE_R * (0.06 + nuclePulse * 0.025);
      const nucleGrad = ctx.createRadialGradient(C, C, 0, C, C, nucleR * 2.5);
      nucleGrad.addColorStop(0,   `rgba(255, 255, 255, ${0.85 + nuclePulse * 0.1})`);
      nucleGrad.addColorStop(0.4, `rgba(${ai.r}, ${ai.g}, ${ai.b}, ${0.55 + nuclePulse * 0.25})`);
      nucleGrad.addColorStop(1,   'rgba(0,0,0,0)');
      ctx.fillStyle = nucleGrad;
      ctx.beginPath();
      ctx.arc(C, C, nucleR * 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Listening overlay
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
      // Speaking overlay
      if (coreState === 'speaking') {
        const p = 0.5 + 0.5 * Math.sin(t * 5);
        ctx.strokeStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, ${0.35 + p * 0.4})`;
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(C, C, CORE_R * (0.93 + p * 0.04), 0, Math.PI * 2);
        ctx.stroke();
      }
      // Tap ripple
      if (shockRef.current > 0.05) {
        const ringR = CORE_R * (0.30 + (1 - shockRef.current) * 0.7);
        ctx.strokeStyle = `rgba(255, 255, 255, ${shockRef.current * 0.7})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(C, C, ringR, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Layer 3 — energy containment ring (inner rim glow)
      ctx.strokeStyle = `rgba(${ai.r}, ${ai.g}, ${ai.b}, 0.35)`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(C, C, CORE_R * 0.94, 0, Math.PI * 2);
      ctx.stroke();

      // Inner-bottom shadow — recess illusion.
      const innerShadow = ctx.createRadialGradient(
        C, C + CORE_R * 0.45, 0,
        C, C + CORE_R * 0.45, CORE_R * 0.85
      );
      innerShadow.addColorStop(0, 'rgba(0,0,0,0.55)');
      innerShadow.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = innerShadow;
      ctx.fillRect(0, 0, cssSize, cssSize);

      ctx.restore(); // end clip

      // Layer 2 — transparent lens specular (top-left highlight = protrude).
      const spec = ctx.createRadialGradient(
        C - CORE_R * 0.35, C - CORE_R * 0.42, 0,
        C - CORE_R * 0.35, C - CORE_R * 0.42, CORE_R * 0.55
      );
      spec.addColorStop(0,    'rgba(255, 255, 255, 0.30)');
      spec.addColorStop(0.45, 'rgba(255, 255, 255, 0.07)');
      spec.addColorStop(1,    'rgba(255, 255, 255, 0)');
      ctx.save();
      ctx.beginPath();
      ctx.arc(C, C, CORE_R, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = spec;
      ctx.fillRect(0, 0, cssSize, cssSize);
      ctx.restore();

      // Outer rim — bright AI-tinted edge.
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
  }, [activeAI, coreState, audioLevelRef]);

  const handleTap = () => {
    shockRef.current = 1;
    if (onActivate) onActivate();
  };

  return (
    <button
      type="button"
      className={`atlas-core core-state-${coreState} core-ai-${activeAI}`}
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
