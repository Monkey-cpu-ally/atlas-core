import React, { useMemo, useState } from "react";
import { resolveWorkspace } from "./workspaceRegistry";
import "./adaptive-workspace.css";

export default function AdaptiveWorkspace({ project, onBack }) {
  const workspace = useMemo(() => resolveWorkspace(project), [project]);
  const [activeToolId, setActiveToolId] = useState(workspace.tools[0]?.[0]);
  const activeTool = workspace.tools.find(([id]) => id === activeToolId) || workspace.tools[0];

  return (
    <section className="adaptive-workspace" data-workspace={workspace.id} data-persona={workspace.persona} aria-label={workspace.title}>
      <header className="adaptive-workspace__header">
        <div>
          <p>{workspace.persona} workspace</p>
          <h2>{project?.title || workspace.title}</h2>
          <span>{workspace.tagline}</span>
        </div>
        <button type="button" onClick={onBack}>Back</button>
      </header>

      <div className="adaptive-workspace__body">
        <aside className="adaptive-workspace__rail" aria-label="Workspace tools">
          {workspace.tools.map(([id, label]) => (
            <button
              type="button"
              key={id}
              className={id === activeToolId ? "is-active" : ""}
              onClick={() => setActiveToolId(id)}
            >
              <span>{label.slice(0, 2).toUpperCase()}</span>
              <small>{label}</small>
            </button>
          ))}
        </aside>

        <main className="adaptive-workspace__canvas">
          <div className="adaptive-workspace__mark" aria-hidden="true">{workspace.mark}</div>
          <div className="adaptive-workspace__focus">
            <p>Active Tool</p>
            <h3>{activeTool?.[1]}</h3>
            <span>{activeTool?.[2]}</span>
            <div className="adaptive-workspace__status">
              <strong>{project?.progress ?? 0}% project progress</strong>
              <div><span style={{ width: `${project?.progress ?? 0}%` }} /></div>
              <small>{project?.updated || "Workspace ready"}</small>
            </div>
          </div>
        </main>

        <aside className="adaptive-workspace__context">
          <section>
            <p>Mission Objective</p>
            <strong>{project?.next || "Define the next verified step."}</strong>
          </section>
          <section>
            <p>Project Health</p>
            <strong>{project?.health || "planning"}</strong>
          </section>
          <section>
            <p>Responsible AI</p>
            <strong>{workspace.persona}</strong>
          </section>
          <section>
            <p>Quick Actions</p>
            <div className="adaptive-workspace__actions">
              <button type="button">Add note</button>
              <button type="button">Open files</button>
              <button type="button">Run review</button>
            </div>
          </section>
        </aside>
      </div>
    </section>
  );
}
