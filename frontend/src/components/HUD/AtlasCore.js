import React, { useRef, useEffect } from 'react';
import { AI_PERSONAS } from '../../data/atlasCore';

// Core states determine animation behavior
const STATE_CONFIG = {
  idle: { pulseSpeed: 0.002, spinSpeed: 0.0005, particleSpeed: 0.001, intensity: 0.6 },
  listening: { pulseSpeed: 0.004, spinSpeed: 0.001, particleSpeed: 0.003, intensity: 0.9 },
  thinking: { pulseSpeed: 0.008, spinSpeed: 0.003, particleSpeed: 0.005, intensity: 1.0 },
  speaking: { pulseSpeed: 0.006, spinSpeed: 0.002, particleSpeed: 0.002, intensity: 0.85 },
  alert: { pulseSpeed: 0.015, spinSpeed: 0.005, particleSpeed: 0.008, intensity: 1.2 }
};

export default function AtlasCore({ activeAI, coreState }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const size = canvas.width;
    const center = size / 2;
    const ai = AI_PERSONAS[activeAI];
    const config = STATE_CONFIG[coreState] || STATE_CONFIG.idle;

    const draw = (time) => {
      ctx.clearRect(0, 0, size, size);
      
      // Parse AI color
      const aiColor = ai.color;
      
      // Outer glass shell glow
      const shellGlow = ctx.createRadialGradient(center, center, center * 0.4, center, center, center * 0.85);
      shellGlow.addColorStop(0, 'transparent');
      shellGlow.addColorStop(0.6, `${aiColor}15`);
      shellGlow.addColorStop(0.8, `${aiColor}30`);
      shellGlow.addColorStop(1, `${aiColor}10`);
      ctx.fillStyle = shellGlow;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.85, 0, Math.PI * 2);
      ctx.fill();

      // Glass shell border
      ctx.strokeStyle = `${aiColor}40`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.78, 0, Math.PI * 2);
      ctx.stroke();

      // Inner energy sphere
      const pulseScale = 1 + Math.sin(time * config.pulseSpeed) * 0.08 * config.intensity;
      const energyGradient = ctx.createRadialGradient(
        center, center * 0.9, 0,
        center, center, center * 0.65 * pulseScale
      );
      
      // AI-specific core colors
      if (activeAI === 'ajani') {
        energyGradient.addColorStop(0, '#ff6b4a');
        energyGradient.addColorStop(0.3, '#dc143c');
        energyGradient.addColorStop(0.6, '#8b0000');
        energyGradient.addColorStop(1, '#2d0a0a');
      } else if (activeAI === 'minerva') {
        energyGradient.addColorStop(0, '#5fe7e0');
        energyGradient.addColorStop(0.3, '#20b2aa');
        energyGradient.addColorStop(0.6, '#0d6b66');
        energyGradient.addColorStop(1, '#0a2020');
      } else if (activeAI === 'hermes') {
        energyGradient.addColorStop(0, '#ffffff');
        energyGradient.addColorStop(0.3, '#d0d0d8');
        energyGradient.addColorStop(0.6, '#808088');
        energyGradient.addColorStop(1, '#1a1a1f');
      } else {
        // Trinity/Council - layered purple
        energyGradient.addColorStop(0, '#c9a0dc');
        energyGradient.addColorStop(0.3, '#9370db');
        energyGradient.addColorStop(0.6, '#5a3d7a');
        energyGradient.addColorStop(1, '#1a0d1f');
      }

      ctx.fillStyle = energyGradient;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.65 * pulseScale, 0, Math.PI * 2);
      ctx.fill();

      // Inner spinning rings
      ctx.save();
      ctx.translate(center, center);
      ctx.rotate(time * config.spinSpeed);
      
      for (let i = 0; i < 3; i++) {
        const ringRadius = center * (0.25 + i * 0.12);
        ctx.strokeStyle = `${aiColor}${Math.floor((0.3 - i * 0.08) * 255).toString(16).padStart(2, '0')}`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(0, 0, ringRadius, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();

      // Swirling particles
      ctx.save();
      ctx.translate(center, center);
      const particleCount = coreState === 'thinking' ? 20 : coreState === 'alert' ? 25 : 12;
      
      for (let i = 0; i < particleCount; i++) {
        const angle = (i / particleCount) * Math.PI * 2 + time * config.particleSpeed * (i % 2 === 0 ? 1 : -1);
        const radius = center * (0.3 + Math.sin(time * 0.002 + i) * 0.15);
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius * 0.7; // Elliptical for depth
        const particleSize = 2 + Math.sin(time * 0.003 + i * 0.5) * 1;
        
        ctx.fillStyle = `${aiColor}${Math.floor((0.5 + Math.sin(time * 0.004 + i) * 0.3) * 255).toString(16).padStart(2, '0')}`;
        ctx.beginPath();
        ctx.arc(x, y, particleSize, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      // Listening state - expanding waves
      if (coreState === 'listening') {
        const waveCount = 3;
        for (let i = 0; i < waveCount; i++) {
          const waveProgress = ((time * 0.002 + i / waveCount) % 1);
          const waveRadius = center * 0.5 + waveProgress * center * 0.4;
          const waveAlpha = (1 - waveProgress) * 0.3;
          
          ctx.strokeStyle = `${aiColor}${Math.floor(waveAlpha * 255).toString(16).padStart(2, '0')}`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(center, center, waveRadius, 0, Math.PI * 2);
          ctx.stroke();
        }
      }

      // Speaking state - sync pulses
      if (coreState === 'speaking') {
        const pulsePhase = Math.sin(time * 0.01) * 0.5 + 0.5;
        ctx.strokeStyle = `${aiColor}${Math.floor(pulsePhase * 0.5 * 255).toString(16).padStart(2, '0')}`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(center, center, center * 0.7 + pulsePhase * 5, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Alert state - sharp flashes
      if (coreState === 'alert') {
        const flashIntensity = Math.abs(Math.sin(time * 0.02));
        ctx.fillStyle = `${aiColor}${Math.floor(flashIntensity * 0.2 * 255).toString(16).padStart(2, '0')}`;
        ctx.beginPath();
        ctx.arc(center, center, center * 0.85, 0, Math.PI * 2);
        ctx.fill();
      }

      // Center bright point
      const centerGlow = ctx.createRadialGradient(center, center * 0.95, 0, center, center, center * 0.15);
      centerGlow.addColorStop(0, '#ffffff');
      centerGlow.addColorStop(0.5, `${aiColor}80`);
      centerGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = centerGlow;
      ctx.beginPath();
      ctx.arc(center, center, center * 0.15, 0, Math.PI * 2);
      ctx.fill();

      // Light ripples on surface
      const rippleCount = 5;
      for (let i = 0; i < rippleCount; i++) {
        const rippleAngle = (i / rippleCount) * Math.PI * 2 + time * 0.001;
        const rippleX = center + Math.cos(rippleAngle) * center * 0.45;
        const rippleY = center + Math.sin(rippleAngle) * center * 0.35;
        const rippleSize = 8 + Math.sin(time * 0.005 + i) * 4;
        
        const rippleGrad = ctx.createRadialGradient(rippleX, rippleY, 0, rippleX, rippleY, rippleSize);
        rippleGrad.addColorStop(0, 'rgba(255,255,255,0.3)');
        rippleGrad.addColorStop(1, 'transparent');
        ctx.fillStyle = rippleGrad;
        ctx.beginPath();
        ctx.arc(rippleX, rippleY, rippleSize, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    const animate = () => {
      timeRef.current += 16;
      draw(timeRef.current);
      animRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [activeAI, coreState]);

  return (
    <div className="atlas-core">
      <canvas ref={canvasRef} width={200} height={200} />
      <div className="core-reflection" />
    </div>
  );
}
