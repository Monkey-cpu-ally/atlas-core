import React, { useRef, useCallback } from 'react';
import { Layers, FlaskConical, FolderKanban, FileCode, Network, Archive } from 'lucide-react';

const TAB_ICONS = {
  'Subjects': Layers,
  'Lab': FlaskConical,
  'Projects': FolderKanban,
  'Blueprints': FileCode,
  'Systems': Network,
  'Archive': Archive
};

export default function Ring3Knowledge({ tabs, rotation, selectedTab, onSelect, onDrag }) {
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
      className="ring ring-3"
      style={{ transform: `rotate(${rotation}deg)` }}
      onMouseDown={handleMouseDown}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      data-testid="ring-3-knowledge"
    >
      {/* Ring track with exploratory details */}
      <svg className="ring-track" viewBox="0 0 600 600">
        {/* Main track */}
        <circle 
          cx="300" 
          cy="300" 
          r="260" 
          fill="none" 
          stroke="rgba(255,255,255,0.05)" 
          strokeWidth="60"
        />
        {/* Ambient glow paths */}
        <circle 
          cx="300" 
          cy="300" 
          r="260" 
          fill="none" 
          stroke="rgba(100,200,255,0.03)" 
          strokeWidth="80"
          strokeDasharray="50 100"
          className="ambient-glow"
        />
        {/* Subtle markers */}
        {[...Array(72)].map((_, i) => (
          <line
            key={i}
            x1="300"
            y1="45"
            x2="300"
            y2={i % 12 === 0 ? "35" : "42"}
            stroke={i % 12 === 0 ? "rgba(255,255,255,0.3)" : "rgba(255,255,255,0.1)"}
            strokeWidth={i % 12 === 0 ? "2" : "1"}
            transform={`rotate(${i * 5} 300 300)`}
          />
        ))}
        {/* Inner decorative ring */}
        <circle cx="300" cy="300" r="230" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" strokeDasharray="5 10" />
        <circle cx="300" cy="300" r="290" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
      </svg>

      {/* Knowledge Tabs */}
      {tabs.map((tab, index) => {
        const angle = index * 60;
        const isSelected = selectedTab === tab;
        const Icon = TAB_ICONS[tab];

        return (
          <button
            key={tab}
            className={`ring-segment knowledge-segment ${isSelected ? 'selected expanded' : ''}`}
            style={{
              '--segment-angle': `${angle}deg`,
              transform: `rotate(${angle}deg) translateY(-260px) rotate(-${angle + rotation}deg)`
            }}
            onClick={(e) => {
              e.stopPropagation();
              onSelect(tab);
            }}
            data-testid={`knowledge-segment-${tab.toLowerCase()}`}
            aria-label={`Open ${tab}`}
          >
            <div className={`segment-content exploratory ${isSelected ? 'active' : ''}`}>
              <Icon className="segment-icon" />
              <span className="segment-label">{tab}</span>
              {isSelected && (
                <div className="node-connectors">
                  <span className="connector" />
                  <span className="connector" />
                  <span className="connector" />
                </div>
              )}
            </div>
          </button>
        );
      })}

      {/* Floating ambient particles */}
      <div className="ambient-particles">
        {[...Array(8)].map((_, i) => (
          <div 
            key={i} 
            className="particle"
            style={{
              '--delay': `${i * 0.5}s`,
              '--angle': `${i * 45}deg`
            }}
          />
        ))}
      </div>
    </div>
  );
}
