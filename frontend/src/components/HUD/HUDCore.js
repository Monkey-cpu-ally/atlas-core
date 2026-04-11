import React, { useRef, useEffect } from 'react';

export default function HUDCore({ activeAI, aiPersonas, speakingAI }) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const size = 120;
    const center = size / 2;

    const drawCore = (time) => {
      ctx.clearRect(0, 0, size, size);
      
      const ai = aiPersonas[activeAI];
      const aiColor = ai.color;

      // Outer glow
      const outerGlow = ctx.createRadialGradient(center, center, center * 0.5, center, center, center);
      outerGlow.addColorStop(0, `${aiColor}30`);
      outerGlow.addColorStop(0.7, `${aiColor}10`);
      outerGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = outerGlow;
      ctx.fillRect(0, 0, size, size);

      // Main sphere
      ctx.save();
      ctx.beginPath();
      ctx.arc(center, center, center * 0.65, 0, Math.PI * 2);
      ctx.clip();

      // Background gradient
      const bgGradient = ctx.createRadialGradient(center, center * 0.7, 0, center, center, center * 0.7);
      bgGradient.addColorStop(0, '#1a1a2e');
      bgGradient.addColorStop(0.5, '#0f0f1a');
      bgGradient.addColorStop(1, '#050510');
      ctx.fillStyle = bgGradient;
      ctx.fillRect(0, 0, size, size);

      // Colored atmosphere based on AI
      const atmosGradient = ctx.createRadialGradient(center, center, center * 0.2, center, center, center * 0.65);
      atmosGradient.addColorStop(0, `${aiColor}40`);
      atmosGradient.addColorStop(0.4, `${aiColor}20`);
      atmosGradient.addColorStop(1, 'transparent');
      ctx.fillStyle = atmosGradient;
      ctx.fillRect(0, 0, size, size);

      // Floating elements
      ctx.fillStyle = `${aiColor}60`;
      for (let i = 0; i < 5; i++) {
        const angle = (i / 5) * Math.PI * 2 + time * 0.001;
        const radius = center * 0.3 + Math.sin(time * 0.002 + i) * 10;
        const x = center + Math.cos(angle) * radius;
        const y = center + Math.sin(angle) * radius * 0.6;
        const dotSize = 4 + Math.sin(time * 0.003 + i * 2) * 2;
        ctx.beginPath();
        ctx.arc(x, y, dotSize, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();

      // Edge highlight
      const edgeGradient = ctx.createRadialGradient(center, center, center * 0.55, center, center, center * 0.68);
      edgeGradient.addColorStop(0, 'transparent');
      edgeGradient.addColorStop(0.5, `${aiColor}20`);
      edgeGradient.addColorStop(1, `${aiColor}50`);
      ctx.fillStyle = edgeGradient;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.68, 0, Math.PI * 2);
      ctx.fill();

      // Speaking pulse
      if (speakingAI) {
        const pulseSize = center * 0.72 + Math.sin(time * 0.01) * 4;
        const pulseAlpha = Math.sin(time * 0.012) * 0.3 + 0.5;
        ctx.strokeStyle = `${aiColor}${Math.floor(pulseAlpha * 255).toString(16).padStart(2, '0')}`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(center, center, pulseSize, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Center glow
      const centerGlow = ctx.createRadialGradient(center, center, 0, center, center, center * 0.15);
      centerGlow.addColorStop(0, `${aiColor}80`);
      centerGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = centerGlow;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.15, 0, Math.PI * 2);
      ctx.fill();
    };

    const animate = () => {
      timeRef.current += 16;
      drawCore(timeRef.current);
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [activeAI, aiPersonas, speakingAI]);

  return (
    <div className="hud-core" data-testid="hud-core">
      <canvas ref={canvasRef} width={120} height={120} className="core-canvas" />
      <div className="core-glow" style={{ boxShadow: `0 0 40px ${aiPersonas[activeAI].color}30` }} />
    </div>
  );
}
