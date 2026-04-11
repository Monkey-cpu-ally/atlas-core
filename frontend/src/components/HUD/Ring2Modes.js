import React, { useRef, useCallback } from 'react';
import { GraduationCap, Hammer, Search, BookOpen } from 'lucide-react';

const MODE_ICONS = {
  'teach': GraduationCap,
  'build': Hammer,
  'analyze': Search,
  'story': BookOpen
};

export default function Ring2Modes({ modes, rotation, selectedMode, onSelect, onDrag, activeAI }) {
  const ringRef = useRef(null);
  const isDragging = useRef(false);
  const lastX = useRef(0);

  const handleMouseDown = useCallback((e) => {
    isDragging.current = true;
    lastX.current = e.clientX;
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging.current) return;
    const delta = e.clientX - lastX.current;
    onDrag(delta);
    lastX.current = e.clientX;
  }, [onDrag]);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }, [handleMouseMove]);

  const handleTouchStart = useCallback((e) => {
    isDragging.current = true;
    lastX.current = e.touches[0].clientX;
  }, []);

  const handleTouchMove = useCallback((e) => {
    if (!isDragging.current) return;
    const delta = e.touches[0].clientX - lastX.current;
    onDrag(delta);
    lastX.current = e.touches[0].clientX;
  }, [onDrag]);

  const handleTouchEnd = useCallback(() => {
    isDragging.current = false;
  }, []);

  return (
    <div 
      ref={ringRef}
      className="ring ring-2"
      style={{ transform: `rotate(${rotation}deg)` }}
      onMouseDown={handleMouseDown}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      data-testid="ring-2-modes"
    >
      {/* Ring track */}
      <svg className="ring-track" viewBox="0 0 500 500">
        <circle 
          cx="250" 
          cy="250" 
          r="200" 
          fill="none" 
          stroke="rgba(255,255,255,0.08)" 
          strokeWidth="50"
        />
        {/* Tick marks */}
        {[...Array(48)].map((_, i) => (
          <line
            key={`tick-${i}`}
            x1="250"
            y1="55"
            x2="250"
            y2={i % 12 === 0 ? "45" : i % 6 === 0 ? "50" : "52"}
            stroke={i % 12 === 0 ? "rgba(255,255,255,0.5)" : "rgba(255,255,255,0.2)"}
            strokeWidth={i % 12 === 0 ? "2" : "1"}
            transform={`rotate(${i * 7.5} 250 250)`}
          />
        ))}
        <circle cx="250" cy="250" r="175" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
        <circle cx="250" cy="250" r="225" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
      </svg>

      {/* Mode Segments */}
      {modes.map((mode, index) => {
        const angle = index * 90;
        const isSelected = selectedMode === mode.id;
        const Icon = MODE_ICONS[mode.id];

        return (
          <button
            key={mode.id}
            className={`ring-segment mode-segment ${isSelected ? 'selected' : ''}`}
            style={{
              '--segment-angle': `${angle}deg`,
              transform: `rotate(${angle}deg) translateY(-200px) rotate(-${angle + rotation}deg)`
            }}
            onClick={(e) => {
              e.stopPropagation();
              onSelect(mode.id);
            }}
            data-testid={`mode-segment-${mode.id}`}
            aria-label={`Select ${mode.name}`}
          >
            <div className={`segment-content mechanical ${isSelected ? 'active' : ''}`}>
              <Icon className="segment-icon" />
              <span className="segment-label">{mode.name.replace(' Mode', '')}</span>
              <div className="segment-indicator" />
            </div>
          </button>
        );
      })}

      {/* Scanner line effect */}
      <div className="scanner-line" />
    </div>
  );
}
