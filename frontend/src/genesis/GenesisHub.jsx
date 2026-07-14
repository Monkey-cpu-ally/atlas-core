import React, { useCallback, useEffect, useMemo, useReducer, useState } from "react";
import AwarenessAlert from "./AwarenessAlert";
import ConstellationWheel from "./ConstellationWheel";
import PortraitController from "./PortraitController";
import PulsePanel from "./PulsePanel";
import { getCapabilities } from "./capabilityRegistry";
import { initialHubState, reduceHubState, HUB_MODES } from "./hubState";
import { personaTokens } from "./designTokens";
import useAdaptiveQuality from "./useAdaptiveQuality";
import "./genesis.css";

const previewModes = [
  { label: "Idle", event: { event: "hud.returned.idle", payload: {} } },
  { label: "Ajani", event: { event: "ai.presence.requested", payload: { persona: "ajani" } } },
  { label: "Minerva", event: { event: "ai.presence.requested", payload: { persona: "minerva" } } },
  { label: "Hermes", event: { event: "ai.presence.requested", payload: { persona: "hermes" } } },
  { label: "Council", event: { event: "council.started", payload: { persona: "council" } } },
  { label: "Pulse", event: { event: "pulse.opened", payload: { persona: "atlas" } } },
];

function withEnvelope(event) {
  return {
    version: "1.0",
    timestamp: new Date().toISOString(),
    source: "genesis-preview",
    ...event,
  };
}

export default function GenesisHub({ visualBridge }) {
  const [state, dispatch] = useReducer(reduceHubState, initialHubState);
  const [selectedNode, setSelectedNode] = useState(null);
  const quality = useAdaptiveQuality();

  useEffect(() => {
    if (visualBridge?.lastEvent) dispatch(visualBridge.lastEvent);
  }, [visualBridge?.lastEvent]);

  const persona = state.activePersona || "atlas";
  const tokens = personaTokens[persona] || personaTokens.atlas;
  const nodes = useMemo(
    () => getCapabilities(persona).map((node) => ({ ...node, art: node.label.slice(0, 1) })),
    [persona],
  );
  const showWheel = [HUB_MODES.WHEEL, HUB_MODES.PROJECT, HUB_MODES.ACTIVE_AI, HUB_MODES.COUNCIL].includes(state.mode);
  const showPulse = state.mode === HUB_MODES.PULSE;

  useEffect(() => {
    setSelectedNode(null);
  }, [persona]);

  const selectNode = useCallback((node) => {
    setSelectedNode(node);
    dispatch(withEnvelope({ event: "wheel.selection.changed", payload: { persona, node_id: node.id } }));
  }, [persona]);

  const dismissAlert = useCallback(() => {
    dispatch(withEnvelope({ event: "awareness.alert.dismissed", payload: {} }));
  }, []);

  return (
    <main
      className={`genesis-hub genesis-hub--${state.mode}`}
      data-persona={persona}
      data-quality={quality.profile}
      style={{ "--atlas-accent": tokens.accent }}
    >
      {!quality.reducedEffects ? <div className="genesis-hub__ambient" aria-hidden="true" /> : null}
      <div className="genesis-hub__core" aria-label="ATLAS core">
        <span>ATLAS</span>
      </div>

      {showWheel && (
        <ConstellationWheel
          nodes={nodes}
          selectedId={selectedNode?.id || state.selectedNodeId}
          onSelect={selectNode}
          accent={tokens.accent}
        />
      )}

      {!showPulse && (
        <section className="genesis-hub__workspace" aria-live="polite">
          <p className="genesis-hub__mode">{state.mode}</p>
          <h1>
            {selectedNode?.label ||
              (persona === "atlas"
                ? "Quiet and ready"
                : persona === "council"
                  ? "Council assembled"
                  : `${persona} workspace`)}
          </h1>
          <p>
            {selectedNode?.summary ||
              (persona === "council"
                ? "Ajani, Minerva, and Hermes are present together. Agreements and dissent remain visible."
                : "Voice stays primary. The Hub expands only when the work needs it.")}
          </p>
          {selectedNode?.projectIds?.length ? (
            <div className="genesis-hub__project-links">
              {selectedNode.projectIds.map((projectId) => <span key={projectId}>{projectId}</span>)}
            </div>
          ) : null}
        </section>
      )}

      {showPulse ? <PulsePanel items={state.pulseItems} updatedAt={state.pulseUpdatedAt} /> : null}

      <PortraitController
        visiblePersonas={state.visiblePersonas}
        activePersona={state.activePersona}
        state={state.speechState}
      />

      <AwarenessAlert alert={state.alert} onDismiss={dismissAlert} />

      {process.env.NODE_ENV !== "production" ? (
        <nav className="genesis-preview" aria-label="Genesis development preview controls">
          {previewModes.map((item) => (
            <button type="button" key={item.label} onClick={() => dispatch(withEnvelope(item.event))}>
              {item.label}
            </button>
          ))}
          <button
            type="button"
            onClick={() => dispatch(withEnvelope({
              event: "awareness.alert.raised",
              payload: {
                persona: "ajani",
                title: "The offer is below your stated floor.",
                reason: "The proposed amount is 18% under your minimum target.",
                action: "Do not accept yet. Ask them to justify the reduction.",
                urgency: "high",
              },
            }))}
          >
            Alert
          </button>
        </nav>
      ) : null}

      <div className="genesis-hub__connection">
        Visual bridge: {visualBridge?.status || "offline"} · {quality.profile}
      </div>
    </main>
  );
}
