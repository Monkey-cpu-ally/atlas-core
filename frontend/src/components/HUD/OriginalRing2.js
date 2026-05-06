import React from 'react';
import { Book, Brain, Activity, Users, Monitor } from 'lucide-react';
import { ORIGINAL_RING_STRUCTURE, getCompassPosition, AI_LIST } from '../../data/originalRingStructure';

const ICONS = {
  manual: Book,
  minerva: Brain,
  system_monitor: Monitor,
  hermes: Activity,
  council: Users,
};

// Ring 2 - Middle Ring (5 items including AIs)
export default function OriginalRing2({ selected, onSelect, activeAI }) {
  const items = ORIGINAL_RING_STRUCTURE.ring2;
  const radius = 28; // Percentage from center

  return (
    <div className="ring ring-2-original">
      {/* Visible ring circle */}
      <svg className="ring-track" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={radius} />
      </svg>

      {/* Ring items */}
      {items.map((item) => {
        const Icon = ICONS[item.id];
        const pos = getCompassPosition(item.angle, radius);
        const isSelected = selected === item.id;
        const isAI = item.type === 'ai';
        const aiColor = isAI ? AI_LIST[item.id]?.color : null;
        const isActiveAI = isAI && activeAI === item.id;

        return (
          <button
            key={item.id}
            className={`original-card ${isSelected ? 'selected' : ''} ${isAI ? 'ai-card' : ''} ${isActiveAI ? 'active-ai' : ''}`}
            style={{
              left: `${pos.x}%`,
              top: `${pos.y}%`,
              '--ai-color': aiColor,
            }}
            onClick={() => onSelect(item.id, item.type)}
            data-testid={`ring2-${item.id}`}
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
