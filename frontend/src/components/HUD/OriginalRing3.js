import React from 'react';
import { User } from 'lucide-react';
import { ORIGINAL_RING_STRUCTURE, getCompassPosition, AI_LIST } from '../../data/originalRingStructure';

// Ring 3 - Inner Ring (Active AI only)
export default function OriginalRing3({ activeAI, onSelect }) {
  const item = ORIGINAL_RING_STRUCTURE.ring3[0];
  const radius = 12; // Close to center
  const pos = getCompassPosition(item.angle, radius);
  const aiData = AI_LIST[activeAI];

  return (
    <div className="ring ring-3-original">
      {/* Active AI card */}
      <button
        className="original-card ai-card active-ai large"
        style={{
          left: `${pos.x}%`,
          top: `${pos.y}%`,
          '--ai-color': aiData?.color,
        }}
        onClick={() => onSelect(activeAI)}
        data-testid={`ring3-${activeAI}`}
      >
        <div className="card-icon">
          <User size={36} />
        </div>
        <div className="card-label">{aiData?.name || activeAI.toUpperCase()}</div>
      </button>
    </div>
  );
}
