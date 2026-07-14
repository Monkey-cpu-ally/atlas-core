import React from "react";

const sections = [
  { id: "blueprints", label: "Blueprints", detail: "Drawings, dimensions, assemblies, and revision history." },
  { id: "cad", label: "CAD", detail: "Mechanical models, part relationships, and fabrication geometry." },
  { id: "electronics", label: "Electronics", detail: "Sensors, boards, wiring, power, and embedded controls." },
  { id: "materials", label: "Materials", detail: "Strength, weight, cost, durability, and environmental fit." },
  { id: "manufacturing", label: "Manufacturing", detail: "Processes, tooling, assembly, and quality control." },
  { id: "ai-control", label: "AI Control", detail: "Behavior, planning, perception, and safe operating limits." },
  { id: "testing", label: "Testing", detail: "Test plans, failures, tolerances, and validation evidence." },
  { id: "simulation", label: "Simulation", detail: "Digital-twin runs, telemetry, predicted stress, and performance." },
];

export default function RoboticsWorkspace({ project, onBack }) {
  return (
    <section className="robotics-workspace" aria-label="Robotics workspace">
      <header className="robotics-workspace__header">
        <div>
          <p>Hermes Workspace</p>
          <h2>{project?.title || "Robotics"}</h2>
          <span>{project?.updated || "Engineering workspace"}</span>
        </div>
        <button type="button" onClick={onBack}>Back</button>
      </header>

      <div className="robotics-workspace__hero">
        <div className="robotics-workspace__art" aria-hidden="true">R</div>
        <div>
          <strong>{project?.progress ?? 0}% complete</strong>
          <div className="robotics-workspace__progress"><span style={{ width: `${project?.progress ?? 0}%` }} /></div>
          <p>One place for the mechanical, electronic, software, manufacturing, and testing sides of the robot.</p>
        </div>
      </div>

      <div className="robotics-workspace__grid">
        {sections.map((section) => (
          <button className="robotics-tool" type="button" key={section.id}>
            <span>{section.label}</span>
            <small>{section.detail}</small>
          </button>
        ))}
      </div>
    </section>
  );
}
