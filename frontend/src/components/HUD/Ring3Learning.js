import React, { useRef, useCallback } from 'react';
import { BookOpen, FlaskConical, FileCode, Sparkles, Rocket, Globe, FolderOpen } from 'lucide-react';
import { AI_PERSONAS } from '../../data/atlasCore';

// Ring 3 - Learning/Projects Ring (outermost, most expansive)
// AI subjects, Lab, Blueprints, Weaver, Hyper Axel, Creative worlds, Notes/archives
const LEARNING_ITEMS = [
  { id: 'subjects', label: 'Subjects', icon: BookOpen, angle: 0 },
  { id: 'lab', label: 'Lab', icon: FlaskConical, angle: 45 },
  { id: 'blueprints', label: 'Blueprints', icon: FileCode, angle: 90 },
  { id: 'weaver', label: 'Weaver', icon: Sparkles, angle: 135 },
  { id: 'hyperaxel', label: 'Hyper Axel', icon: Rocket, angle: 180 },
  { id: 'worlds', label: 'Worlds', icon: Globe, angle: 225 },
  { id: 'archives', label: 'Archives', icon: FolderOpen, angle: 270 },
  { id: 'projects', label: 'Projects', icon: FileCode, angle: 315 },
];

export default function Ring3Learning({ rotation, onRotate, selected, onSelect, activeAI }) {
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
    onRotate(prev => prev + delta * 0.2);
    lastX.current = e.clientX;
  }, [onRotate]);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }, [handleMouseMove]);

  const getPosition = (angle, radius) => {
    const rad = (angle + rotation - 90) * (Math.PI / 180);
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
    >
      {/* Outer ring track - expansive feel */}
      <svg className="ring-track" viewBox="0 0 100 100">
        {/* Multiple concentric guides */}
        <circle cx="50" cy="50" r="48" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="0.3" />
        <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="0.3" strokeDasharray="2 4" />
        <circle cx="50" cy="50" r="44" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="0.3" />

        {/* Ambient glow segments */}
        {LEARNING_ITEMS.map((item, i) => {
          const isSelected = selected === item.id;
          const startAngle = item.angle + rotation - 20;
          const endAngle = item.angle + rotation + 20;
          
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
                  x1={50 + 44 * Math.cos((item.angle + rotation - 90) * Math.PI / 180)}
                  y1={50 + 44 * Math.sin((item.angle + rotation - 90) * Math.PI / 180)}
                  x2={50 + 48 * Math.cos((item.angle + rotation - 90) * Math.PI / 180)}
                  y2={50 + 48 * Math.sin((item.angle + rotation - 90) * Math.PI / 180)}
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
          const angle = i * 15 + rotation * 0.1;
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

      {/* Learning nodes */}
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
              transform: `translate(-50%, -50%) rotate(${-rotation}deg)`
            }}
            onClick={(e) => { e.stopPropagation(); onSelect(item.id); }}
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
