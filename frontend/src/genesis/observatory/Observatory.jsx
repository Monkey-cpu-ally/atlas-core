import React, { useMemo } from "react";
import { buildAiActivities } from "../activity/aiActivityEngine";
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

function connectionLabel(status) {
  if (status === "connected") return "Connected";
  if (status === "connecting") return "Connecting";
  return "Offline";
}

function latestTimestamp(items) {
  const timestamps = items
    .map((item) => item.occurredAt || item.timestamp || item.updatedAt)
    .filter(Boolean)
    .map((value) => new Date(value).getTime())
    .filter(Number.isFinite);
  return timestamps.length ? new Date(Math.max(...timestamps)) : null;
}

function formatUpdatedAt(date) {
  if (!date) return "No verified update yet";
  return `Updated ${date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
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
  const activeProjects = useMemo(
    () => [...projects].sort((a, b) => (b.progress || 0) - (a.progress || 0)).slice(0, 4),
    [projects],
  );
  const importantPulse = useMemo(
    () => pulseItems.filter((item) => item.status !== "disconnected").slice(0, 3),
    [pulseItems],
  );
  const aiActivities = useMemo(
    () => buildAiActivities({ projects, pulseItems, awarenessItems, bridgeStatus }),
    [projects, pulseItems, awarenessItems, bridgeStatus],
  );
  const importantAlerts = awarenessItems.slice(0, 3);
  const knowledgeProject = projects.find((project) => project.id === "knowledge-bank");
  const githubItems = pulseItems.filter((item) => item.sourceId === "github");
  const githubStatus = githubItems.some((item) => item.status === "connected" || item.status === "attention")
    ? "connected"
    : "offline";
  const lastUpdate = latestTimestamp([...pulseItems, ...awarenessItems]);
  const systemReady = bridgeStatus === "connected" && health.watch === 0;

  return (
    <section className="observatory" aria-label="ATLAS Observatory">
      <header className="observatory__header">
        <div>
          <p>GENESIS Observatory</p>
          <h1>Command the whole system from one view.</h1>
          <span>{formatUpdatedAt(lastUpdate)}</span>
        </div>
        <div className="observatory__system-stack" aria-label="System connections">
          <div className="observatory__system" data-status={bridgeStatus}>
            <span>Visual Bridge</span>
            <strong>{connectionLabel(bridgeStatus)}</strong>
          </div>
          <div className="observatory__system" data-status={githubStatus}>
            <span>GitHub Pulse</span>
            <strong>{connectionLabel(githubStatus)}</strong>
          </div>
        </div>
      </header>

      <div className="observatory__status-strip" aria-label="ATLAS readiness">
        <div data-state={systemReady ? "good" : "watch"}><span>System</span><strong>{systemReady ? "Ready" : "Review"}</strong></div>
        <div data-state={health.watch ? "watch" : "good"}><span>Projects at risk</span><strong>{health.watch}</strong></div>
        <div data-state={awarenessItems.length ? "watch" : "good"}><span>Active alerts</span><strong>{awarenessItems.length}</strong></div>
        <div data-state={githubStatus === "connected" ? "good" : "muted"}><span>Verified GitHub events</span><strong>{githubItems.length}</strong></div>
      </div>

      <div className="observatory__grid">
        <button className="observatory-card observatory-card--mission" type="button" onClick={onOpenMission}>
          <div className="observatory-card__topline"><span>Current Mission</span><b>{mission?.progress ?? 0}%</b></div>
          <h2>{mission?.title || "No active mission"}</h2>
          <p>{mission?.nextStep || "Choose the next mission."}</p>
          <div className="observatory__timeline" aria-label="Mission timeline">
            <div className="is-complete"><span>01</span><strong>Mission selected</strong></div>
            <div className="is-current"><span>02</span><strong>{mission?.nextStep || "Define next step"}</strong></div>
            <div><span>03</span><strong>Verification</strong></div>
          </div>
          <div className="observatory__progress"><span style={{ width: `${mission?.progress ?? 0}%` }} /></div>
          <small>{mission?.owner || "ATLAS"}</small>
        </button>

        <section className="observatory-card observatory-card--ai" aria-label="AI activity">
          <div className="observatory-card__topline"><span>AI Activity Engine</span><b>{aiActivities.filter((item) => item.state === "active").length} active</b></div>
          <div className="observatory__ai-list">
            {aiActivities.map((activity) => (
              <div key={activity.id} data-persona={activity.id} data-state={activity.state}>
                <span className="observatory__presence" aria-hidden="true" />
                <div>
                  <strong>{activity.name}</strong>
                  <span>{activity.task}</span>
                  <div className="observatory__ai-progress"><span style={{ width: `${activity.progress}%` }} /></div>
                </div>
                <small>{activity.state}</small>
              </div>
            ))}
          </div>
        </section>

        <button className="observatory-card observatory-card--projects" type="button" onClick={onOpenProjects}>
          <div className="observatory-card__topline"><span>Project Health</span><b>{projects.length}</b></div>
          <div className="observatory__health">
            <div><strong>{health.healthy}</strong><span>Healthy</span></div>
            <div><strong>{health.building}</strong><span>Building</span></div>
            <div><strong>{health.watch}</strong><span>Watch</span></div>
          </div>
        </button>

        <section className="observatory-card observatory-card--knowledge" aria-label="Knowledge Bank status">
          <div className="observatory-card__topline"><span>Knowledge Bank</span><b>{knowledgeProject ? `${knowledgeProject.progress}%` : "Not linked"}</b></div>
          <h3>{knowledgeProject?.title || "Knowledge Bank"}</h3>
          <p>{knowledgeProject?.updated || "No verified Knowledge Bank project data is connected."}</p>
          <div className="observatory__progress"><span style={{ width: `${knowledgeProject?.progress || 0}%` }} /></div>
          <small>{knowledgeProject?.next || "Connect a verified source workflow."}</small>
        </section>

        <button className="observatory-card observatory-card--pulse" type="button" onClick={onOpenPulse}>
          <div className="observatory-card__topline"><span>Pulse</span><b>{importantPulse.length}</b></div>
          {importantPulse.length ? <div className="observatory__brief-list">{importantPulse.map((item) => <div key={item.id}><strong>{item.category}</strong><span>{item.title}</span></div>)}</div> : <p>No verified live updates yet.</p>}
        </button>

        <button className="observatory-card observatory-card--awareness" type="button" onClick={onOpenAwareness}>
          <div className="observatory-card__topline"><span>Awareness</span><b>{awarenessItems.length}</b></div>
          {importantAlerts.length ? <div className="observatory__brief-list">{importantAlerts.map((alert) => <div key={alert.id}><strong>{alert.persona || "ATLAS"}</strong><span>{alert.title || alert.message}</span></div>)}</div> : <p>Nothing urgent. ATLAS is watching quietly.</p>}
        </button>

        <section className="observatory-card observatory-card--active-projects" aria-label="Active projects">
          <div className="observatory-card__topline"><span>Active Projects</span><b>{activeProjects.length}</b></div>
          <div className="observatory__project-list">
            {activeProjects.map((project) => <button type="button" key={project.id} onClick={() => onOpenProject?.(project)}><div><strong>{project.title}</strong><span>{project.updated}</span></div><b>{project.progress}%</b></button>)}
          </div>
        </section>
      </div>
    </section>
  );
}
