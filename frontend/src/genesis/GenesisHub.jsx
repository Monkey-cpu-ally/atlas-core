import React, { useEffect, useMemo, useReducer, useState } from "react";
import ConstellationWheel from "./ConstellationWheel";
import { initialHubState, reduceHubState, HUB_MODES } from "./hubState";
import { personaTokens } from "./designTokens";
import "./genesis.css";

const demoNodes = {
  hermes: [
    { id: "robotics", label: "Robotics", art: "R" },
    { id: "software", label: "Software", art: "S" },
    { id: "electronics", label: "Electronics", art: "E" },
    { id: "cad", label: "CAD", art: "C" },
    { id: "weaver", label: "Weaver", art: "W" },
  ],
  minerva: [
    { id: "biology", label: "Biology", art: "B" },
    { id: "botany", label: "Botany", art: "N" },
    { id: "research", label: "Research", art: "R" },
    { id: "learning", label: "Learning", art: "L" },
    { id: "knowledge", label: "Knowledge Bank", art: "K" },
  ],
  ajani: [
    { id: "strategy", label: "Strategy", art: "S" },
    { id: "projects", label: "Projects", art: "P" },
    { id: "risk", label: "Risk", art: "R" },
    { id: "business", label: "Business", art: "B" },
    { id: "missions", label: "Missions", art: "M" },
  ],
};

export default function GenesisHub({ visualBridge }) {
  const [state, dispatch] = useReducer(reduceHubState, initialHubState);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (visualBridge?.lastEvent) dispatch(visualBridge.lastEvent);
  }, [visualBridge?.lastEvent]);

  const persona = state.activePersona || "atlas";
  const tokens = personaTokens[persona] || personaTokens.atlas;
  const nodes = useMemo(() => demoNodes[persona] || [], [persona]);

  const showWheel = [HUB_MODES.WHEEL, HUB_MODES.PROJECT, HUB_MODES.ACTIVE_AI].includes(state.mode);
  const visibleFaces = state.visiblePersonas;

  return (
    <main className="genesis-hub" style={{ "--atlas-accent": tokens.accent }}>
      <div className="genesis-hub__core" aria-label="ATLAS core">
        <span>ATLAS</span>
      </div>

      {showWheel && (
        <ConstellationWheel
          nodes={nodes}
          selectedId={selectedNode?.id || state.selectedNodeId}
          onSelect={setSelectedNode}
          accent={tokens.accent}
        />
      )}

      <section className="genesis-hub__workspace" aria-live="polite">
        <p className="genesis-hub__mode">{state.mode}</p>
        <h1>{selectedNode?.label || (persona === "atlas" ? "Quiet and ready" : `${persona} workspace`)}</h1>
        <p>
          {selectedNode
            ? "This is the first functional shell. Original project artwork and real tools will replace this placeholder."
            : "Voice stays primary. The Hub expands only when the work needs it."}
        </p>
      </section>

      <aside className="genesis-hub__portraits" aria-label="Active AI presence">
        {visibleFaces.map((name) => (
          <div className="genesis-hub__portrait" key={name}>
            <div className="genesis-hub__portrait-placeholder">{name.slice(0, 1).toUpperCase()}</div>
            <span>{name}</span>
          </div>
        ))}
      </aside>

      <div className="genesis-hub__connection">
        Visual bridge: {visualBridge?.status || "offline"}
      </div>
    </main>
  );
}
