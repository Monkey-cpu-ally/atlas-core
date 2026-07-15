import React from "react";
import usePerformanceTelemetry from "./usePerformanceTelemetry";
import "./developer.css";

export default function DeveloperMode({ enabled, onToggle, scene, persona, quality, bridgeStatus, activeProjectId }) {
  const telemetry = usePerformanceTelemetry(enabled);

  return (
    <>
      <button
        type="button"
        className="developer-mode__toggle"
        onClick={onToggle}
        aria-pressed={enabled}
        aria-label="Toggle ATLAS Developer Mode"
      >
        DEV
      </button>

      {enabled ? (
        <aside className="developer-mode" aria-label="ATLAS Developer Mode">
          <header>
            <div>
              <p>Hermes Engineering Mode</p>
              <h2>System telemetry</h2>
            </div>
            <button type="button" onClick={onToggle} aria-label="Close Developer Mode">×</button>
          </header>

          <div className="developer-mode__grid">
            <Metric label="FPS" value={telemetry.fps || "—"} status={telemetry.fps >= 55 ? "good" : "watch"} />
            <Metric label="Frame" value={telemetry.frameTime ? `${telemetry.frameTime} ms` : "—"} />
            <Metric label="Memory" value={telemetry.memoryMb ? `${telemetry.memoryMb} MB` : "Unavailable"} />
            <Metric label="Quality" value={quality} />
            <Metric label="Scene" value={scene} />
            <Metric label="Persona" value={persona || "atlas"} />
            <Metric label="Project" value={activeProjectId || "none"} />
            <Metric label="Bridge" value={bridgeStatus || "offline"} status={bridgeStatus === "connected" ? "good" : "watch"} />
          </div>

          <footer>
            <span>Hidden in production unless deliberately enabled.</span>
          </footer>
        </aside>
      ) : null}
    </>
  );
}

function Metric({ label, value, status = "normal" }) {
  return (
    <div className="developer-mode__metric" data-status={status}>
      <span>{label}</span>
      <strong>{String(value)}</strong>
    </div>
  );
}
