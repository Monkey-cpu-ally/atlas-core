import React from "react";
import { atlasTokens } from "./designTokens";

function positionFor(index, total) {
  const start = -110;
  const span = atlasTokens.wheel.visibleArcDegrees;
  const degrees = total <= 1 ? 0 : start + (span * index) / (total - 1);
  const radians = (degrees * Math.PI) / 180;
  return {
    x: Math.cos(radians) * atlasTokens.wheel.radius,
    y: Math.sin(radians) * atlasTokens.wheel.radius,
  };
}

export default function ConstellationWheel({ nodes = [], selectedId, onSelect, accent }) {
  return (
    <div className="atlas-wheel" aria-label="Constellation Wheel">
      <div className="atlas-wheel__arc" style={{ borderColor: accent }} />
      {nodes.map((node, index) => {
        const selected = node.id === selectedId;
        const { x, y } = positionFor(index, nodes.length);
        return (
          <button
            key={node.id}
            type="button"
            className={`atlas-wheel__node${selected ? " is-selected" : ""}`}
            style={{
              transform: `translate(${x}px, ${y}px)`,
              borderColor: selected ? accent : undefined,
            }}
            onClick={() => onSelect?.(node)}
            aria-pressed={selected}
          >
            <span className="atlas-wheel__art" aria-hidden="true">
              {node.art || node.label.slice(0, 1)}
            </span>
            <span className="atlas-wheel__label">{node.label}</span>
          </button>
        );
      })}
    </div>
  );
}
