import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { atlasTokens } from "./designTokens";
import "./wheel.css";

const ART_MARKS = {
  robotics: "RB",
  software: "SW",
  electronics: "EL",
  cad: "CAD",
  manufacturing: "MF",
  "power-systems": "PW",
  "digital-twin": "DT",
  weaver: "WV",
  biology: "BIO",
  botany: "BOT",
  chemistry: "CH",
  genetics: "DNA",
  environment: "ENV",
  learning: "LRN",
  research: "RS",
  "knowledge-bank": "KB",
  strategy: "ST",
  business: "BZ",
  negotiation: "NG",
  risk: "RK",
  projects: "PR",
  operations: "OP",
  finance: "FN",
  security: "SC",
};

function positionFor(index, total, selectedIndex) {
  const centerAngle = 0;
  const step = Math.min(38, atlasTokens.wheel.visibleArcDegrees / Math.max(total - 1, 1));
  const degrees = centerAngle + (index - selectedIndex) * step;
  const radians = (degrees * Math.PI) / 180;
  const distance = Math.abs(index - selectedIndex);
  const depth = Math.max(0, 1 - distance * 0.14);

  return {
    x: Math.cos(radians) * atlasTokens.wheel.radius,
    y: Math.sin(radians) * atlasTokens.wheel.radius,
    scale: Math.max(0.72, depth),
    opacity: Math.max(0.34, 1 - distance * 0.18),
    zIndex: Math.max(1, 20 - distance),
  };
}

export default function ConstellationWheel({ nodes = [], selectedId, onSelect, accent }) {
  const wheelRef = useRef(null);
  const selectedIndex = Math.max(0, nodes.findIndex((node) => node.id === selectedId));
  const activeNode = nodes[selectedIndex] || nodes[0];

  const decoratedNodes = useMemo(
    () => nodes.map((node) => ({ ...node, art: node.art || ART_MARKS[node.id] || node.label.slice(0, 2).toUpperCase() })),
    [nodes],
  );

  const selectByIndex = useCallback((index) => {
    if (!decoratedNodes.length) return;
    const wrapped = (index + decoratedNodes.length) % decoratedNodes.length;
    onSelect?.(decoratedNodes[wrapped]);
  }, [decoratedNodes, onSelect]);

  useEffect(() => {
    const element = wheelRef.current;
    if (!element) return undefined;

    function onKeyDown(event) {
      if (event.key === "ArrowDown" || event.key === "ArrowRight") {
        event.preventDefault();
        selectByIndex(selectedIndex + 1);
      }
      if (event.key === "ArrowUp" || event.key === "ArrowLeft") {
        event.preventDefault();
        selectByIndex(selectedIndex - 1);
      }
      if (event.key === "Home") {
        event.preventDefault();
        selectByIndex(0);
      }
      if (event.key === "End") {
        event.preventDefault();
        selectByIndex(decoratedNodes.length - 1);
      }
    }

    element.addEventListener("keydown", onKeyDown);
    return () => element.removeEventListener("keydown", onKeyDown);
  }, [decoratedNodes.length, selectByIndex, selectedIndex]);

  if (!decoratedNodes.length) return null;

  return (
    <section className="atlas-wheel-shell" aria-label="Constellation Wheel navigation">
      <div
        ref={wheelRef}
        className="atlas-wheel"
        role="listbox"
        tabIndex={0}
        aria-activedescendant={activeNode ? `atlas-node-${activeNode.id}` : undefined}
      >
        <div className="atlas-wheel__arc" style={{ borderColor: accent }} />
        <div className="atlas-wheel__rail" aria-hidden="true" />
        {decoratedNodes.map((node, index) => {
          const selected = index === selectedIndex;
          const position = positionFor(index, decoratedNodes.length, selectedIndex);
          return (
            <button
              id={`atlas-node-${node.id}`}
              key={node.id}
              type="button"
              role="option"
              className={`atlas-wheel__node${selected ? " is-selected" : ""}`}
              style={{
                "--node-x": `${position.x}px`,
                "--node-y": `${position.y}px`,
                "--node-scale": position.scale,
                "--node-opacity": position.opacity,
                zIndex: position.zIndex,
                borderColor: selected ? accent : undefined,
              }}
              onClick={() => onSelect?.(node)}
              aria-selected={selected}
            >
              <span className="atlas-wheel__art" data-art-key={node.artKey} aria-hidden="true">
                {node.art}
              </span>
              <span className="atlas-wheel__label">{node.label}</span>
              {node.projectIds?.length ? <small>{node.projectIds.length} projects</small> : null}
            </button>
          );
        })}
      </div>

      <div className="atlas-wheel__selection" aria-live="polite">
        <p>Constellation Wheel</p>
        <strong>{activeNode?.label}</strong>
        <span>{activeNode?.summary}</span>
        <div className="atlas-wheel__controls">
          <button type="button" onClick={() => selectByIndex(selectedIndex - 1)} aria-label="Previous capability">↑</button>
          <button type="button" onClick={() => selectByIndex(selectedIndex + 1)} aria-label="Next capability">↓</button>
        </div>
      </div>
    </section>
  );
}
