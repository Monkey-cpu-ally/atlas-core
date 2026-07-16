import React, { useMemo, useRef, useState } from "react";
import { buildAiActivities } from "../activity/aiActivityEngine";
import "./minimal-home.css";

const HOLD_THRESHOLD_MS = 320;

export default function MinimalHome({
  mission,
  projects = [],
  pulseItems = [],
  awarenessItems = [],
  bridgeStatus = "offline",
  onOpenObservatory,
  onOpenMission,
  onOpenProject,
  onSelectPersona,
}) {
  const [holding, setHolding] = useState(false);
  const pointerStartedAt = useRef(0);
  const holdTimer = useRef(null);
  const activities = useMemo(
    () => buildAiActivities({ projects, pulseItems, awarenessItems, bridgeStatus }),
    [projects, pulseItems, awarenessItems, bridgeStatus],
  );
  const currentProject = useMemo(
    () => [...projects].sort((a, b) => (b.progress || 0) - (a.progress || 0))[0] || null,
    [projects],
  );
  const attentionCount = awarenessItems.length + pulseItems.filter((item) => item.urgency === "high").length;

  function clearHoldTimer() {
    if (holdTimer.current) {
      window.clearTimeout(holdTimer.current);
      holdTimer.current = null;
    }
  }

  function handlePointerDown(event) {
    pointerStartedAt.current = performance.now();
    event.currentTarget.setPointerCapture?.(event.pointerId);
    clearHoldTimer();
    holdTimer.current = window.setTimeout(() => setHolding(true), HOLD_THRESHOLD_MS);
  }

  function handlePointerEnd(event) {
    const duration = performance.now() - pointerStartedAt.current;
    clearHoldTimer();
    setHolding(false);
    event.currentTarget.releasePointerCapture?.(event.pointerId);
    if (duration < HOLD_THRESHOLD_MS) onOpenObservatory?.();
  }

  function handlePointerCancel() {
    clearHoldTimer();
    setHolding(false);
  }

  return (
    <section className="minimal-home" aria-label="GENESIS minimal home">
      <div className="minimal-home__portraits" aria-label="AI team">
        {activities.map((activity) => (
          <button
            type="button"
            key={activity.id}
            data-persona={activity.id}
            data-state={activity.state}
            onClick={() => onSelectPersona?.(activity.id)}
            aria-label={`Open ${activity.name}`}
          >
            <span className="minimal-home__portrait-mark" aria-hidden="true">{activity.name.slice(0, 1)}</span>
            <strong>{activity.name}</strong>
            <small>{activity.state}</small>
          </button>
        ))}
      </div>

      <button
        type="button"
        className="minimal-home__voice-core"
        data-listening={holding ? "true" : "false"}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerEnd}
        onPointerCancel={handlePointerCancel}
        onLostPointerCapture={handlePointerCancel}
        aria-label="Hold to speak to ATLAS. Tap for status."
      >
        <span className="minimal-home__voice-ring" aria-hidden="true" />
        <strong>ATLAS</strong>
        <small>{holding ? "Listening…" : "Hold to speak · Tap for status"}</small>
      </button>

      <div className="minimal-home__focus">
        <button type="button" onClick={onOpenMission}>
          <span>Current Mission</span>
          <strong>{mission?.title || "No active mission"}</strong>
          <small>{mission?.nextStep || "Choose the next mission."}</small>
        </button>
        <button type="button" onClick={() => currentProject && onOpenProject?.(currentProject)} disabled={!currentProject}>
          <span>Current Project</span>
          <strong>{currentProject?.title || "No active project"}</strong>
          <small>{currentProject?.next || currentProject?.updated || "Select a project."}</small>
        </button>
      </div>

      <div className="minimal-home__quiet-status" data-attention={attentionCount > 0 ? "true" : "false"}>
        <span aria-hidden="true" />
        <strong>{attentionCount > 0 ? `${attentionCount} item${attentionCount === 1 ? "" : "s"} need attention` : "Systems quiet"}</strong>
      </div>
    </section>
  );
}
