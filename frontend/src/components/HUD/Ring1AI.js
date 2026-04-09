import React, { useRef } from 'react';
import { User, Brain, Zap, Users } from 'lucide-react';

const AI_ICONS = {
  ajani: User,
  minerva: Brain,
  hermes: Zap,
  council: Users
};

export default function Ring1AI({ aiConfig, rotation, activeAI, speakingAI, onSelect }) {
  const aiKeys = Object.keys(aiConfig);

  return (
    <div 
      className="ring ring-1"
      style={{ transform: `rotate(${rotation}deg)` }}
      data-testid="ring-1-ai"
    >
      {/* Ring track */}
      <svg className="ring-track" viewBox="0 0 400 400">
        <circle 
          cx="200" 
          cy="200" 
          r="140" 
          fill="none" 
          stroke="rgba(255,255,255,0.1)" 
          strokeWidth="40"
        />
        {/* Tick marks */}
        {[...Array(24)].map((_, i) => (
          <line
            key={i}
            x1="200"
            y1="70"
            x2="200"
            y2={i % 6 === 0 ? "60" : "65"}
            stroke="rgba(255,255,255,0.3)"
            strokeWidth={i % 6 === 0 ? "2" : "1"}
            transform={`rotate(${i * 15} 200 200)`}
          />
        ))}
      </svg>

      {/* AI Segments */}
      {aiKeys.map((aiKey, index) => {
        const angle = index * 90;
        const isActive = activeAI === aiKey;
        const isSpeaking = speakingAI === aiKey;
        const Icon = AI_ICONS[aiKey];
        const ai = aiConfig[aiKey];

        return (
          <button
            key={aiKey}
            className={`ring-segment ai-segment ${isActive ? 'active' : ''} ${isSpeaking ? 'speaking' : ''}`}
            style={{
              '--segment-angle': `${angle}deg`,
              '--segment-color': ai.color,
              transform: `rotate(${angle}deg) translateY(-140px) rotate(-${angle + rotation}deg)`
            }}
            onClick={() => onSelect(aiKey)}
            data-testid={`ai-segment-${aiKey}`}
            aria-label={`Select ${ai.name}`}
          >
            <div 
              className="segment-content"
              style={{
                borderColor: isActive ? ai.color : 'rgba(255,255,255,0.2)',
                background: isActive ? `${ai.color}20` : 'rgba(0,0,0,0.6)'
              }}
            >
              <Icon 
                className="segment-icon"
                style={{ color: isActive ? ai.color : 'rgba(255,255,255,0.6)' }}
              />
              <span 
                className="segment-label"
                style={{ color: isActive ? ai.color : 'rgba(255,255,255,0.8)' }}
              >
                {ai.name}
              </span>
              {isSpeaking && (
                <div 
                  className="speaking-indicator"
                  style={{ background: ai.color }}
                />
              )}
            </div>
            {isActive && (
              <div 
                className="segment-glow"
                style={{ 
                  boxShadow: `0 0 20px ${ai.color}60, 0 0 40px ${ai.color}30`
                }}
              />
            )}
          </button>
        );
      })}

      {/* Active indicator arc */}
      <svg className="active-arc" viewBox="0 0 400 400">
        <defs>
          <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={aiConfig[activeAI].color} stopOpacity="0" />
            <stop offset="50%" stopColor={aiConfig[activeAI].color} stopOpacity="0.8" />
            <stop offset="100%" stopColor={aiConfig[activeAI].color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d="M 200 60 A 140 140 0 0 1 340 200"
          fill="none"
          stroke="url(#arcGradient)"
          strokeWidth="3"
          strokeLinecap="round"
          style={{
            transform: `rotate(${-45}deg)`,
            transformOrigin: 'center'
          }}
        />
      </svg>
    </div>
  );
}
