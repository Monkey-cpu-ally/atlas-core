import React, { useRef, useCallback, useState, useEffect } from 'react';
import { BookOpen, FlaskConical, FileCode, Sparkles, Globe, FolderOpen } from 'lucide-react';
import { AI_PERSONAS } from '../../data/atlasCore';

// Ring 3 - Learning/Projects Ring (outermost, most expansive)
// Motion: Exploratory, graceful, slower (300-450ms rotate, 180-250ms expansion)
const LEARNING_ITEMS = [
  { id: 'subjects', label: 'Subjects', icon: BookOpen, angle: 0 },
  { id: 'lab', label: 'Lab', icon: FlaskConical, angle: 51.4 },
  { id: 'blueprints', label: 'Blueprints', icon: FileCode, angle: 102.8 },
  { id: 'weaver', label: 'Weaver', icon: Sparkles, angle: 154.2 },
  { id: 'worlds', label: 'Worlds', icon: Globe, angle: 205.6 },
  { id: 'archives', label: 'Archives', icon: FolderOpen, angle: 257 },
  { id: 'projects', label: 'Projects', icon: FileCode, angle: 308.4 },
];

export default function Ring3Learning({ rotation, onRotate, selected, onSelect, activeAI }) {
  const ringRef = useRef(null);
  const isDragging = useRef(false);
  const lastX = useRef(0);
  const dragOffset = useRef(0);
  const [smartRotation, setSmartRotation] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  // Smart rotation: When item is selected, rotate to bring it to top center
  useEffect(() => {
    if (!selected) return;
    
    const selectedItem = LEARNING_ITEMS.find(item => item.id === selected);
    if (!selectedItem) return;
    
    // Calculate rotation needed to bring selected item to top (-90°)
    const targetAngle = -90;
    const rotationNeeded = targetAngle - selectedItem.angle;
    
    setSmartRotation(rotationNeeded);
    setIsAnimating(true);
    
    // Animation completes in 380ms (per spec: 300-450ms)
    const timer = setTimeout(() => setIsAnimating(false), 380);
    return () => clearTimeout(timer);
  }, [selected]);

  const handleMouseDown = useCallback((e) => {
    if (isAnimating) return; // Don't allow drag during smart rotation
    isDragging.current = true;
    lastX.current = e.clientX;
    dragOffset.current = 0;
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAnimating]);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging.current) return;
    const delta = e.clientX - lastX.current;
    dragOffset.current += delta * 0.3;
    lastX.current = e.clientX;
  }, []);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }, [handleMouseMove]);

  // Combine smart rotation with manual drag offset
  const totalRotation = smartRotation + dragOffset.current;

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
      className="ring ring-3"
      onMouseDown={handleMouseDown}
      style={{ 
        cursor: isAnimating ? 'default' : 'grab'
      }}
    >
      {/* Outer ring track - exploratory feel with graceful rotation */}
      <svg 
        className="ring-track" 
        viewBox="0 0 100 100"
        style={{
          transition: isAnimating ? 'transform 380ms cubic-bezier(0.25, 0.46, 0.45, 0.94)' : 'none'
        }}
      >
        {/* Multiple concentric guides */}
        <circle cx="50" cy="50" r="48" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="0.3" />
        <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="0.3" strokeDasharray="2 4" />
        <circle cx="50" cy="50" r="44" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="0.3" />

        {/* Ambient glow segments */}
        {LEARNING_ITEMS.map((item, i) => {
          const isSelected = selected === item.id;
          const startAngle = item.angle + totalRotation - 20;
          const endAngle = item.angle + totalRotation + 20;
          
          return (
            <g key={item.id}>
              {/* Background arc */}
              <path
                d={describeArc(50, 50, 46, startAngle - 90, endAngle - 90)}
                fill="none"
                stroke={isSelected ? aiColor : 'rgba(100,150,255,0.1)'}
                strokeWidth={isSelected ? '3' : '1'}
                strokeLinecap="round"
                opacity={isSelected ? 0.8 : 0.4}
                style={{
                  filter: isSelected ? `drop-shadow(0 0 10px ${aiColor})` : 'none',
                  transition: 'all 0.3s ease'
                }}
              />
              {/* Connector line to node */}
              {isSelected && (
                <line
                  x1={50 + 44 * Math.cos((item.angle + totalRotation - 90) * Math.PI / 180)}
                  y1={50 + 44 * Math.sin((item.angle + totalRotation - 90) * Math.PI / 180)}
                  x2={50 + 48 * Math.cos((item.angle + totalRotation - 90) * Math.PI / 180)}
                  y2={50 + 48 * Math.sin((item.angle + totalRotation - 90) * Math.PI / 180)}
                  stroke={aiColor}
                  strokeWidth="1"
                  opacity="0.6"
                />
              )}
            </g>
          );
        })}

        {/* Subtle particle dots around ring */}
        {[...Array(24)].map((_, i) => {
          const angle = i * 15 + totalRotation * 0.1;
          const rad = angle * Math.PI / 180;
          const r = 47 + Math.sin(i * 0.5) * 1;
          return (
            <circle
              key={i}
              cx={50 + r * Math.cos(rad)}
              cy={50 + r * Math.sin(rad)}
              r="0.4"
              fill="rgba(100,200,255,0.3)"
            />
          );
        })}
      </svg>

      {/* Learning nodes with expansion on selection */}
      {LEARNING_ITEMS.map((item) => {
        const Icon = item.icon;
        const pos = getPosition(item.angle, 46);
        const isSelected = selected === item.id;

        return (
          <button
            key={item.id}
            className={`learning-node ${isSelected ? 'selected expanded' : ''}`}
            style={{
              left: `${pos.x}%`,
              top: `${pos.y}%`,
              transform: `translate(-50%, -50%) rotate(${-totalRotation}deg) ${isSelected ? 'scale(1.15)' : 'scale(1)'}`,
              transition: isAnimating 
                ? 'all 380ms cubic-bezier(0.25, 0.46, 0.45, 0.94)' 
                : isSelected 
                  ? 'all 220ms cubic-bezier(0.34, 1.56, 0.64, 1)' // Expansion easing (180-250ms spec)
                  : 'all 0.3s ease'
            }}
            onClick={(e) => { 
              e.stopPropagation(); 
              onSelect(item.id); 
            }}
            data-testid={`learning-${item.id}`}
          >
            <Icon className="node-icon" />
            <span className="node-label">{item.label}</span>
            {isSelected && (
              <div className="node-expansion">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            )}
          </button>
        );
      })}
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
