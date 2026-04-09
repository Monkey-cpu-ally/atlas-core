import React, { useRef, useState, useCallback } from 'react';
import { Book, BookOpen, Database, Activity, Settings, Compass } from 'lucide-react';

const SECTION_ICONS = {
  'Manual': Book,
  'Encyclopedia': BookOpen,
  'Memory': Database,
  'System Monitor': Activity,
  'Customization': Settings,
  'Explore Mode': Compass
};

export default function Ring2Operations({ sections, rotation, selectedSection, onSelect, onDrag }) {
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
      data-testid="ring-2-operations"
    >
      {/* Ring track with mechanical details */}
      <svg className="ring-track" viewBox="0 0 500 500">
        <circle 
          cx="250" 
          cy="250" 
          r="200" 
          fill="none" 
          stroke="rgba(255,255,255,0.08)" 
          strokeWidth="50"
        />
        {/* Outer tick marks */}
        {[...Array(60)].map((_, i) => (
          <line
            key={`outer-${i}`}
            x1="250"
            y1="55"
            x2="250"
            y2={i % 10 === 0 ? "45" : i % 5 === 0 ? "50" : "52"}
            stroke={i % 10 === 0 ? "rgba(255,255,255,0.5)" : "rgba(255,255,255,0.2)"}
            strokeWidth={i % 10 === 0 ? "2" : "1"}
            transform={`rotate(${i * 6} 250 250)`}
          />
        ))}
        {/* Inner tick marks */}
        {[...Array(36)].map((_, i) => (
          <line
            key={`inner-${i}`}
            x1="250"
            y1="245"
            x2="250"
            y2="250"
            stroke="rgba(255,255,255,0.15)"
            strokeWidth="1"
            transform={`rotate(${i * 10} 250 250)`}
          />
        ))}
        {/* Decorative circles */}
        <circle cx="250" cy="250" r="175" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
        <circle cx="250" cy="250" r="225" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
      </svg>

      {/* Operation Segments */}
      {sections.map((section, index) => {
        const angle = index * 60;
        const isSelected = selectedSection === section;
        const Icon = SECTION_ICONS[section];

        return (
          <button
            key={section}
            className={`ring-segment operation-segment ${isSelected ? 'selected' : ''}`}
            style={{
              '--segment-angle': `${angle}deg`,
              transform: `rotate(${angle}deg) translateY(-200px) rotate(-${angle + rotation}deg)`
            }}
            onClick={(e) => {
              e.stopPropagation();
              onSelect(section);
            }}
            data-testid={`operation-segment-${section.toLowerCase().replace(' ', '-')}`}
            aria-label={`Open ${section}`}
          >
            <div className={`segment-content mechanical ${isSelected ? 'active' : ''}`}>
              <Icon className="segment-icon" />
              <span className="segment-label">{section}</span>
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
