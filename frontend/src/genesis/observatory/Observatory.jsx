import React, { useMemo } from "react";
import "./observatory.css";

function projectHealthSummary(projects) {
  return projects.reduce(
    (summary, project) => {
      const health = String(project.health || "planning").toLowerCase();
      if (["stable", "good", "active"].includes(health)) summary.healthy += 1;
      else if (["watch", "blocked", "risk"].includes(health)) summary.watch += 1;
      else summary.building += 1;
      return summary;
    },
    { healthy: 0, building: 0, watch: 0 },
  );
}

export default function Observatory({
  mission,
  projects = [],
  pulseItems = [],
  awarenessItems = [],
  bridgeStatus = "offline",
  onOpenMission,
  onOpenProjects,
  onOpenPulse,
  onOpenAwareness,
  onOpenProject,
}) {
  const health = useMemo(() => projectHealthSummary(projects), [projects]);
  const activeProjects = projects.slice(0, 4);
  const importantPulse = pulseItems
    .filter((item) => item.status !== "disconnected")
    .slice(0, 3);
  const importantAlerts = awarenessItems.slice(0, 3);

  return (
    <section className="observatory" aria-label="ATLAS Observatory">
      <header className="observatory__header">
        <div>
          <p>GENESIS Observatory</p>
          <h1>Everything that matters, in one view.</h1>
          <span>ATLAS stays quiet when there is nothing useful to surface.</span>
        </div>
        <div className="observatory__system" data-status={bridgeStatus}>
          <span>Visual Bridge</span>
          <strong>{bridgeStatus}</strong>
        </div>
      </header>

      <div className="observatory__grid">
        <button className="observatory-card observatory-card--mission" type="button" onClick={onOpenMission}>
          <div className="observatory-card__topline">
            <span>Current Mission</span>
            <b>{mission?.progress ?? 0}%</b>
          </div>
          <h2>{mission?.title || "No active mission"}</h2>
          <p>{mission?.nextStep || "Choose the next mission."}</p>
          <div className="observatory__progress"><span style={{ width: `${mission?.progress ?? 0}%` }} /></div>
          <small>{mission?.owner || "ATLAS"}</small>
        </button>

        <section className="observatory-card observatory-card--ai" aria-label="AI status">
          <div className="observatory-card__topline">
            <span>AI Council</span>
            <b>Ready</b>
          </div>
          <div className="observatory__ai-list">
            <div data-persona="ajani"><strong>Ajani</strong><span>Strategy and risk</span></div>
            <div data-persona="minerva"><strong>Minerva</strong><span>Research and guidance</span></div>
            <div data-persona="hermes"><strong>Hermes</strong><span>Engineering and systems</span></div>
          </div>
        </section>

        <button className="observatory-card observatory-card--projects" type="button" onClick={onOpenProjects}>
          <div className="observatory-card__topline">
            <span>Project Health</span>
            <b>{projects.length}</b>
          </div>
          <div className="observatory__health">
            <div><strong>{health.healthy}</strong><span>Healthy</span></div>
            <div><strong>{health.building}</strong><span>Building</span></div>
            <div><strong>{health.watch}</strong><span>Watch</span></div>
          </div>
        </button>

        <button className="observatory-card observatory-card--pulse" type="button" onClick={onOpenPulse}>
          <div className="observatory-card__topline">
            <span>Pulse</span>
            <b>{importantPulse.length}</b>
          </div>
          {importantPulse.length ? (
            <div className="observatory__brief-list">
              {importantPulse.map((item) => (
                <div key={item.id}>
                  <strong>{item.category}</strong>
                  <span>{item.title}</span>
                </div>
              ))}
            </div>
          ) : (
            <p>No verified live updates yet.</p>
          )}
        </button>

        <button className="observatory-card observatory-card--awareness" type="button" onClick={onOpenAwareness}>
          <div className="observatory-card__topline">
            <span>Awareness</span>
            <b>{awarenessItems.length}</b>
          </div>
          {importantAlerts.length ? (
            <div className="observatory__brief-list">
              {importantAlerts.map((alert) => (
                <div key={alert.id}>
                  <strong>{alert.persona || "ATLAS"}</strong>
                  <span>{alert.title || alert.message}</span>
                </div>
              ))}
            </div>
          ) : (
            <p>Nothing urgent. ATLAS is watching quietly.</p>
          )}
        </button>

        <section className="observatory-card observatory-card--active-projects" aria-label="Active projects">
          <div className="observatory-card__topline">
            <span>Active Projects</span>
            <b>{activeProjects.length}</b>
          </div>
          <div className="observatory__project-list">
            {activeProjects.map((project) => (
              <button type="button" key={project.id} onClick={() => onOpenProject?.(project)}>
                <div>
                  <strong>{project.title}</strong>
                  <span>{project.updated}</span>
                </div>
                <b>{project.progress}%</b>
              </button>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
