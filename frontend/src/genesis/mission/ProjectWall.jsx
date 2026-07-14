import React from "react";

export default function ProjectWall({ projects = [], onSelect }) {
  return (
    <section className="project-wall" aria-label="Living Project Wall">
      <header>
        <p>Living Project Wall</p>
        <h2>Active work</h2>
      </header>
      <div className="project-wall__grid">
        {projects.map((project) => (
          <button
            className="project-card"
            data-persona={project.persona}
            type="button"
            key={project.id}
            onClick={() => onSelect?.(project)}
          >
            <div className="project-card__topline">
              <span>{project.health}</span>
              <b>{project.progress}%</b>
            </div>
            <h3>{project.title}</h3>
            <p>{project.updated}</p>
            <div className="project-card__progress"><span style={{ width: `${project.progress}%` }} /></div>
          </button>
        ))}
      </div>
    </section>
  );
}
