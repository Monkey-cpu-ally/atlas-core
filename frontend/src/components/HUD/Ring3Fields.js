import React, { useRef, useCallback, useState } from 'react';
import * as Icons from 'lucide-react';

export default function Ring3Fields({ fields, rotation, selectedField, onSelect, onDrag, activeAI }) {
  const ringRef = useRef(null);
  const isDragging = useRef(false);
  const lastX = useRef(0);
  const [visibleFields, setVisibleFields] = useState(fields.slice(0, 12));
  const [fieldOffset, setFieldOffset] = useState(0);

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
    
    // Update visible fields based on rotation
    const newOffset = Math.floor(Math.abs(rotation) / 30) % fields.length;
    if (newOffset !== fieldOffset) {
      setFieldOffset(newOffset);
      const start = newOffset;
      const visible = [];
      for (let i = 0; i < 12; i++) {
        visible.push(fields[(start + i) % fields.length]);
      }
      setVisibleFields(visible);
    }
  }, [onDrag, rotation, fields, fieldOffset]);

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

  const getIcon = (iconName) => {
    const IconComponent = Icons[iconName];
    return IconComponent || Icons.BookOpen;
  };

  return (
    <div 
      ref={ringRef}
      className="ring ring-3"
      style={{ transform: `rotate(${rotation}deg)` }}
      onMouseDown={handleMouseDown}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      data-testid="ring-3-fields"
    >
      {/* Ring track */}
      <svg className="ring-track" viewBox="0 0 600 600">
        <circle 
          cx="300" 
          cy="300" 
          r="260" 
          fill="none" 
          stroke="rgba(255,255,255,0.05)" 
          strokeWidth="60"
        />
        <circle 
          cx="300" 
          cy="300" 
          r="260" 
          fill="none" 
          stroke="rgba(100,200,255,0.03)" 
          strokeWidth="80"
          strokeDasharray="30 60"
          className="ambient-glow"
        />
        {/* Field count indicator */}
        <text x="300" y="580" textAnchor="middle" fill="rgba(255,255,255,0.3)" fontSize="10">
          22 FIELDS
        </text>
      </svg>

      {/* Field Segments - show 12 at a time */}
      {visibleFields.map((field, index) => {
        const angle = index * 30; // 360/12 = 30 degrees per field
        const isSelected = selectedField === field.id;
        const Icon = getIcon(field.icon);

        return (
          <button
            key={field.id}
            className={`ring-segment field-segment ${isSelected ? 'selected expanded' : ''}`}
            style={{
              '--segment-angle': `${angle}deg`,
              transform: `rotate(${angle}deg) translateY(-260px) rotate(-${angle + rotation}deg)`
            }}
            onClick={(e) => {
              e.stopPropagation();
              onSelect(field.id);
            }}
            data-testid={`field-segment-${field.id}`}
            aria-label={`Select ${field.name}`}
          >
            <div className={`segment-content exploratory ${isSelected ? 'active' : ''}`}>
              <Icon className="segment-icon" />
              <span className="segment-label">{field.name.split(' ')[0]}</span>
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

      {/* Category indicators */}
      <div className="field-categories">
        <span className="category science">Science</span>
        <span className="category tech">Technology</span>
        <span className="category arts">Arts</span>
        <span className="category humanities">Humanities</span>
      </div>

      {/* Ambient particles */}
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
