import React from 'react';
import { BookOpen, FlaskConical, FolderOpen, Database, Settings, Layout, Compass, Archive } from 'lucide-react';
import { ORIGINAL_RING_STRUCTURE, getCompassPosition } from '../../data/originalRingStructure';

const ICONS = {
  subjects: BookOpen,
  lab: FlaskConical,
  projects: FolderOpen,
  memory: Database,
  customization: Settings,
  systems: Layout,
  explore: Compass,
  archive: Archive,
};

// Ring 1 - Outer Ring (8 items)
export default function OriginalRing1({ selected, onSelect }) {
  const items = ORIGINAL_RING_STRUCTURE.ring1;
  const radius = 42; // Percentage from center

  return (
    <div className="ring ring-1-original">
      {/* Visible ring circle */}
      <svg className="ring-track" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={radius} />
      </svg>

      {/* Ring items at compass points */}
      {items.map((item) => {
        const Icon = ICONS[item.id];
        const pos = getCompassPosition(item.angle, radius);
        const isSelected = selected === item.id;

        return (
          <button
            key={item.id}
            className={`original-card ${isSelected ? 'selected' : ''}`}
            style={{
              left: `${pos.x}%`,
              top: `${pos.y}%`,
            }}
            onClick={() => onSelect(item.id)}
            data-testid={`ring1-${item.id}`}
          >
            <div className="card-icon">
              {Icon && <Icon size={28} />}
            </div>
            <div className="card-label">{item.label}</div>
          </button>
        );
      })}
    </div>
  );
}
