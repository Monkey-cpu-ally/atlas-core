import React, { useRef, useCallback, useState } from 'react';
import { Settings, Palette, Mic2, Smartphone, Database, Activity } from 'lucide-react';
import { AI_PERSONAS } from '../../data/atlasCore';

// Ring 2 - System/Manual Ring
// Motion: Mechanical, precise, tight snap (150-220ms)
const SYSTEM_ITEMS = [
  { id: 'settings', label: 'Settings', icon: Settings, angle: 0 },
  { id: 'skins', label: 'UI Skins', icon: Palette, angle: 60 },
  { id: 'voice', label: 'Voice Modes', icon: Mic2, angle: 120 },
  { id: 'devices', label: 'Devices', icon: Smartphone, angle: 180 },
  { id: 'memory', label: 'Memory', icon: Database, angle: 240 },
  { id: 'health', label: 'Health', icon: Activity, angle: 300 },
];

const SNAP_THRESHOLD = 15; // degrees - snap to nearest node

export default function Ring2System({ rotation, onRotate, selected, onSelect, activeAI }) {
  const ringRef = useRef(null);
  const isDragging = useRef(false);
  const lastX = useRef(0);
  const dragOffset = useRef(0);
  const [snappedRotation, setSnappedRotation] = useState(0);

  const handleMouseDown = useCallback((e) => {
    isDragging.current = true;
    lastX.current = e.clientX;
    dragOffset.current = snappedRotation;
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [snappedRotation]);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging.current) return;
    const delta = e.clientX - lastX.current;
    dragOffset.current += delta * 0.4; // Slight resistance feel
    lastX.current = e.clientX;
  }, []);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
    
    // Snap to nearest node (mechanical feel)
    const currentRotation = dragOffset.current % 360;
    const nearestAngle = SYSTEM_ITEMS.reduce((nearest, item) => {
      const diff = Math.abs((currentRotation - item.angle + 540) % 360 - 180);
      const nearestDiff = Math.abs((currentRotation - nearest + 540) % 360 - 180);
      return diff < nearestDiff ? item.angle : nearest;
    }, 0);
    
    setSnappedRotation(nearestAngle);
    
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }, [handleMouseMove]);

  // Use snapped rotation when not dragging, drag offset while dragging
  const totalRotation = isDragging.current ? dragOffset.current : snappedRotation;

  const getPosition = (angle, radius) => {
    const rad = (angle + totalRotation - 90) * (Math.PI / 180);
    return {
      x: 50 + radius * Math.cos(rad),
      y: 50 + radius * Math.sin(rad)
    };
  };

  const aiColor = AI_PERSONAS[activeAI].color;

  return (
    <div 
      ref={ringRef}
      className="ring ring-2"
      onMouseDown={handleMouseDown}
      style={{ 
        cursor: isDragging.current ? 'grabbing' : 'grab' 
      }}
    >
      {/* Ring track with technical details and mechanical snap transition */}
      <svg 
        className="ring-track" 
        viewBox="0 0 100 100"
        style={{
          transform: `rotate(${totalRotation}deg)`,
          transition: isDragging.current ? 'none' : 'transform 180ms cubic-bezier(0.4, 0.0, 0.2, 1)' // Tight mechanical snap (150-220ms)
        }}
      >
        {/* Outer border */}
        <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="0.3" />
        <circle cx="50" cy="50" r="38" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="0.3" />
        
        {/* Tick marks */}
        {[...Array(36)].map((_, i) => {
          const angle = i * 10;
          const rad = angle * Math.PI / 180;
          const isMajor = i % 6 === 0;
          const r1 = isMajor ? 41 : 40.5;
          const r2 = isMajor ? 43 : 42;
          return (
            <line
              key={i}
              x1={50 + r1 * Math.cos(rad)}
              y1={50 + r1 * Math.sin(rad)}
              x2={50 + r2 * Math.cos(rad)}
              y2={50 + r2 * Math.sin(rad)}
              stroke={isMajor ? 'rgba(255,255,255,0.3)' : 'rgba(255,255,255,0.15)'}
              strokeWidth={isMajor ? '0.5' : '0.3'}
            />
          );
        })}

        {/* Section highlights */}
        {SYSTEM_ITEMS.map((item, i) => {
          const isSelected = selected === item.id;
          const startAngle = item.angle + totalRotation - 25;
          const endAngle = item.angle + totalRotation + 25;
          
          return (
            <path
              key={item.id}
              d={describeArc(50, 50, 39, startAngle - 90, endAngle - 90)}
              fill="none"
              stroke={isSelected ? aiColor : 'rgba(255,255,255,0.1)'}
              strokeWidth={isSelected ? '1.5' : '0.8'}
              strokeLinecap="round"
              opacity={isSelected ? 1 : 0.6}
            />
          );
        })}
      </svg>

      {/* System nodes */}
      {SYSTEM_ITEMS.map((item) => {
        const Icon = item.icon;
        const pos = getPosition(item.angle, 39);
        const isSelected = selected === item.id;

        return (
          <button
            key={item.id}
            className={`system-node ${isSelected ? 'selected' : ''}`}
            style={{
              left: `${pos.x}%`,
              top: `${pos.y}%`,
              transform: `translate(-50%, -50%) rotate(${-totalRotation}deg)`
            }}
            onClick={(e) => { e.stopPropagation(); onSelect(item.id); }}
            data-testid={`system-${item.id}`}
          >
            <Icon className="node-icon" />
            <span className="node-label">{item.label}</span>
          </button>
        );
      })}

      {/* Scanner indicator */}
      <div 
        className="scanner-line"
        style={{ transform: `rotate(${totalRotation * 0.5}deg)` }}
      />
    </div>
  );
}

function describeArc(x, y, radius, startAngle, endAngle) {
  const start = polarToCartesian(x, y, radius, endAngle);
  const end = polarToCartesian(x, y, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return ["M", start.x, start.y, "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y].join(" ");
}

function polarToCartesian(cx, cy, radius, angle) {
  const rad = angle * Math.PI / 180;
  return { x: cx + radius * Math.cos(rad), y: cy + radius * Math.sin(rad) };
}
