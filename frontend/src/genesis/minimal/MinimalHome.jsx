import React, { useCallback, useMemo, useRef, useState } from "react";
import { buildAiActivities } from "../activity/aiActivityEngine";
import useAtlasSpeech from "../voice/useAtlasSpeech";
import useAtlasVoice from "../voice/useAtlasVoice";
import { buildVoiceCommandResponse } from "../voice/voiceCommandResponse";
import "./minimal-home.css";

const HOLD_THRESHOLD_MS = 320;

function navigationTranscriptFor(command, originalTranscript) {
  if (command?.type !== "conversation") return originalTranscript;
  if (command.project?.title) return `open ${command.project.title}`;
  if (command.persona && command.persona !== "atlas") return command.persona;
  return null;
}

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
  onVoiceCommand,
}) {
  const pointerStartedAt = useRef(0);
  const holdTimer = useRef(null);
  const holdActivated = useRef(false);
  const lastCompletedResponse = useRef("");
  const [lastResponse, setLastResponse] = useState("");
  const speech = useAtlasSpeech();
  const currentProject = useMemo(
    () => [...projects].sort((a, b) => (b.progress || 0) - (a.progress || 0))[0] || null,
    [projects],
  );

  const handleTranscript = useCallback((transcript) => {
    const response = buildVoiceCommandResponse(transcript, {
      projects,
      mission,
      currentProject,
      lastResponse: lastCompletedResponse.current,
    });

    if (response.command.type === "cancel") {
      speech.cancel();
      setLastResponse(response.message);
      lastCompletedResponse.current = response.message;
      return;
    }

    if (response.command.type === "repeat" || response.command.type === "wake") {
      setLastResponse(response.message);
      speech.speak(response.message);
      return;
    }

    setLastResponse(response.message);
    lastCompletedResponse.current = response.message;
    const navigationTranscript = navigationTranscriptFor(response.command, transcript);
    if (navigationTranscript) onVoiceCommand?.(navigationTranscript);
    speech.speak(response.message);
  }, [currentProject, mission, onVoiceCommand, projects, speech]);

  const voice = useAtlasVoice({ onTranscript: handleTranscript });
  const activities = useMemo(
    () => buildAiActivities({ projects, pulseItems, awarenessItems, bridgeStatus }),
    [projects, pulseItems, awarenessItems, bridgeStatus],
  );
  const attentionCount = awarenessItems.length + pulseItems.filter((item) => item.urgency === "high").length;
  const listening = voice.state === "listening";

  function clearHoldTimer() {
    if (holdTimer.current) {
      window.clearTimeout(holdTimer.current);
      holdTimer.current = null;
    }
  }

  function handlePointerDown(event) {
    pointerStartedAt.current = performance.now();
    holdActivated.current = false;
    speech.cancel();
    setLastResponse("");
    event.currentTarget.setPointerCapture?.(event.pointerId);
    clearHoldTimer();
    holdTimer.current = window.setTimeout(() => {
      holdActivated.current = true;
      voice.start();
    }, HOLD_THRESHOLD_MS);
  }

  function handlePointerEnd(event) {
    const duration = performance.now() - pointerStartedAt.current;
    clearHoldTimer();
    event.currentTarget.releasePointerCapture?.(event.pointerId);
    if (holdActivated.current || duration >= HOLD_THRESHOLD_MS) {
      voice.stop();
      return;
    }
    onOpenObservatory?.();
  }

  function handlePointerCancel() {
    clearHoldTimer();
    holdActivated.current = false;
    voice.stop();
  }

  const voiceMessage = voice.state === "listening"
    ? (voice.transcript || "Listening…")
    : voice.state === "processing"
      ? "Understanding command…"
      : speech.state === "speaking"
        ? (lastResponse || "Responding…")
        : voice.state === "permission-denied"
          ? "Microphone permission needed"
          : voice.state === "unsupported"
            ? "Voice unavailable · Tap for status"
            : lastResponse || "Hold to speak · Tap for status";

  const combinedVoiceState = speech.state === "speaking" ? "speaking" : voice.state;

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
        data-listening={listening ? "true" : "false"}
        data-voice-state={combinedVoiceState}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerEnd}
        onPointerCancel={handlePointerCancel}
        onLostPointerCapture={handlePointerCancel}
        aria-label="Hold to speak to ATLAS. Tap for status."
        aria-live="polite"
      >
        <span className="minimal-home__voice-ring" aria-hidden="true" />
        <strong>ATLAS</strong>
        <small>{voiceMessage}</small>
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

export { navigationTranscriptFor };
