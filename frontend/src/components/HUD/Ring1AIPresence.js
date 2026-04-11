import React, { useState, useEffect } from 'react';
import { User, Brain, Zap, Users } from 'lucide-react';
import { AI_PERSONAS } from '../../data/atlasCore';

const AI_ICONS = { ajani: User, minerva: Brain, hermes: Zap, trinity: Users };

// Ring 1 hugs the core - AI Presence
// Motion: Smooth, identity-driven, soft snap (250-350ms)
export default function Ring1AIPresence({ activeAI, onSelect, coreState, rotation = 0 }) {
  const aiKeys = ['ajani', 'minerva', 'hermes', 'trinity'];
  const [targetRotation, setTargetRotation] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  
  // Base positions around the core (close ring)
  const basePositions = [
    { key: 'ajani', angle: -60 },    // Top-left
    { key: 'minerva', angle: 60 },    // Top-right  
    { key: 'hermes', angle: 180 },    // Bottom
    { key: 'trinity', angle: -120 },  // Left
  ];

  // When AI changes, rotate to bring it to top center (-90°)
  useEffect(() => {
    const aiIndex = aiKeys.indexOf(activeAI);
    if (aiIndex === -1) return;
    
    const currentAngle = basePositions[aiIndex].angle;
    const targetAngle = -90; // Top center position
    const rotationNeeded = targetAngle - currentAngle;
    
    setTargetRotation(rotationNeeded);
    setIsAnimating(true);
    
    // Animation completes in 300ms (per spec: 250-350ms)
    const timer = setTimeout(() => setIsAnimating(false), 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeAI]);

  const getPosition = (angle, radius) => {
    const rad = (angle + targetRotation) * (Math.PI / 180);
    return {
      x: 50 + radius * Math.cos(rad),
      y: 50 + radius * Math.sin(rad)
    };
  };

  return (
    <div className={`ring ring-1 ${coreState === 'speaking' ? 'speaking' : ''}`}>
      {/* Ring track with smooth rotation and soft snap easing */}
      <svg 
        className="ring-track" 
        viewBox="0 0 100 100" 
        style={{ 
          transform: `rotate(${targetRotation}deg)`,
          transition: isAnimating ? 'transform 300ms cubic-bezier(0.34, 1.56, 0.64, 1)' : 'none'
        }}
      >
        <circle 
          cx="50" cy="50" r="28"
          fill="none" 
          stroke={AI_PERSONAS[activeAI].color}
          strokeWidth="0.5"
          strokeOpacity="0.3"
        />
        {/* Segment arcs */}
        {aiKeys.map((key, i) => {
          const isActive = activeAI === key;
          const ai = AI_PERSONAS[key];
          const startAngle = basePositions[i].angle - 30;
          const endAngle = basePositions[i].angle + 30;
          
          return (
            <path
              key={key}
              d={describeArc(50, 50, 28, startAngle, endAngle)}
              fill="none"
              stroke={isActive ? ai.color : 'rgba(255,255,255,0.1)'}
              strokeWidth={isActive ? '2' : '1'}
              strokeLinecap="round"
              style={{
                filter: isActive ? `drop-shadow(0 0 8px ${ai.color})` : 'none',
                transition: 'all 0.3s ease'
              }}
            />
          );
        })}
      </svg>

      {/* AI Segments */}
      {aiKeys.map((key, i) => {
        const ai = AI_PERSONAS[key];
        const Icon = AI_ICONS[key];
        const isActive = activeAI === key;
        const pos = getPosition(basePositions[i].angle, 28);

        return (
          <button
            key={key}
            className={`ai-node ${isActive ? 'active' : ''}`}
            style={{
              left: `${pos.x}%`,
              top: `${pos.y}%`,
              '--ai-color': ai.color,
              transform: `translate(-50%, -50%) rotate(${-targetRotation}deg)`,
              transition: isAnimating ? 'all 300ms cubic-bezier(0.34, 1.56, 0.64, 1)' : 'all 0.3s ease'
            }}
            onClick={() => onSelect(key)}
            data-testid={`ai-${key}`}
          >
            <div className="node-inner">
              <Icon className="node-icon" />
            </div>
            <span className="node-label">{ai.name}</span>
            {isActive && <div className="node-glow" />}
          </button>
        );
      })}
    </div>
  );
}

// Helper to draw arc paths
function describeArc(x, y, radius, startAngle, endAngle) {
  const start = polarToCartesian(x, y, radius, endAngle);
  const end = polarToCartesian(x, y, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return [
    "M", start.x, start.y,
    "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y
  ].join(" ");
}

function polarToCartesian(cx, cy, radius, angle) {
  const rad = angle * Math.PI / 180;
  return {
    x: cx + radius * Math.cos(rad),
    y: cy + radius * Math.sin(rad)
  };
}
