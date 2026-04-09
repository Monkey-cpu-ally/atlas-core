import React, { useRef, useEffect } from 'react';

export default function HUDCore({ activeAI, aiConfig, speakingAI }) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const size = canvas.width;
    const center = size / 2;

    const drawPlanet = (time) => {
      ctx.clearRect(0, 0, size, size);
      
      // Background glow
      const aiColor = aiConfig[activeAI].color;
      const gradient = ctx.createRadialGradient(center, center, 0, center, center, center);
      gradient.addColorStop(0, `${aiColor}40`);
      gradient.addColorStop(0.5, `${aiColor}20`);
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, size, size);

      // Planet base
      ctx.save();
      ctx.beginPath();
      ctx.arc(center, center, center * 0.7, 0, Math.PI * 2);
      ctx.clip();

      // Terrain layers with movement
      const terrainGradient = ctx.createLinearGradient(
        center + Math.sin(time * 0.001) * 20,
        0,
        center + Math.cos(time * 0.001) * 20,
        size
      );
      terrainGradient.addColorStop(0, '#1a1a2e');
      terrainGradient.addColorStop(0.3, '#16213e');
      terrainGradient.addColorStop(0.5, '#0f3460');
      terrainGradient.addColorStop(0.7, '#e94560');
      terrainGradient.addColorStop(1, '#ff6b35');
      ctx.fillStyle = terrainGradient;
      ctx.fillRect(0, 0, size, size);

      // Water layer
      ctx.fillStyle = 'rgba(32, 178, 170, 0.6)';
      ctx.beginPath();
      for (let i = 0; i < 5; i++) {
        const x = center + Math.sin(time * 0.002 + i) * (center * 0.4);
        const y = center + Math.cos(time * 0.0015 + i * 0.5) * (center * 0.3);
        ctx.moveTo(x + center * 0.2, y);
        ctx.arc(x, y, center * 0.2 + Math.sin(time * 0.003 + i) * 10, 0, Math.PI * 2);
      }
      ctx.fill();

      // Land masses
      ctx.fillStyle = 'rgba(233, 69, 96, 0.7)';
      ctx.beginPath();
      for (let i = 0; i < 3; i++) {
        const x = center + Math.cos(time * 0.001 + i * 2) * (center * 0.3);
        const y = center + Math.sin(time * 0.0012 + i * 2) * (center * 0.25);
        ctx.moveTo(x + center * 0.15, y);
        ctx.arc(x, y, center * 0.15 + Math.cos(time * 0.002 + i) * 5, 0, Math.PI * 2);
      }
      ctx.fill();

      ctx.restore();

      // Planet edge glow
      const edgeGradient = ctx.createRadialGradient(center, center, center * 0.6, center, center, center * 0.75);
      edgeGradient.addColorStop(0, 'transparent');
      edgeGradient.addColorStop(0.7, `${aiColor}30`);
      edgeGradient.addColorStop(1, `${aiColor}60`);
      ctx.fillStyle = edgeGradient;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.75, 0, Math.PI * 2);
      ctx.fill();

      // Speaking pulse effect
      if (speakingAI) {
        const pulseIntensity = Math.sin(time * 0.01) * 0.3 + 0.7;
        ctx.strokeStyle = `${aiColor}${Math.floor(pulseIntensity * 255).toString(16).padStart(2, '0')}`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(center, center, center * 0.72 + Math.sin(time * 0.008) * 5, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Inner ring detail
      ctx.strokeStyle = `${aiColor}40`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.5, 0, Math.PI * 2);
      ctx.stroke();

      // Core indicator
      const indicatorGlow = ctx.createRadialGradient(center, center, 0, center, center, center * 0.15);
      indicatorGlow.addColorStop(0, `${aiColor}80`);
      indicatorGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = indicatorGlow;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.15, 0, Math.PI * 2);
      ctx.fill();
    };

    const animate = () => {
      timeRef.current += 16;
      drawPlanet(timeRef.current);
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [activeAI, aiConfig, speakingAI]);

  return (
    <div className="hud-core" data-testid="hud-core">
      <canvas
        ref={canvasRef}
        width={200}
        height={200}
        className="core-canvas"
      />
      <div 
        className="core-glow"
        style={{ 
          boxShadow: `0 0 60px ${aiConfig[activeAI].color}40, inset 0 0 30px ${aiConfig[activeAI].color}20`
        }}
      />
    </div>
  );
}
