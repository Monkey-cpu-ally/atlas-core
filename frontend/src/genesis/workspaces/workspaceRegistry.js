export const workspaceRegistry = Object.freeze({
  robotics: {
    id: "robotics",
    title: "Robotics Lab",
    persona: "hermes",
    tagline: "Design, simulate, build, and test intelligent machines.",
    mark: "RB",
    tools: [
      ["blueprints", "Blueprints", "Drawings, dimensions, assemblies, and revision history."],
      ["cad", "CAD", "Mechanical models, part relationships, and fabrication geometry."],
      ["electronics", "Electronics", "Sensors, boards, wiring, power, and embedded controls."],
      ["materials", "Materials", "Strength, weight, cost, durability, and environmental fit."],
      ["manufacturing", "Manufacturing", "Processes, tooling, assembly, and quality control."],
      ["ai-control", "AI Control", "Behavior, planning, perception, and safe operating limits."],
      ["testing", "Testing", "Test plans, failures, tolerances, and validation evidence."],
      ["simulation", "Simulation", "Digital-twin runs, telemetry, predicted stress, and performance."],
    ],
  },
  software: {
    id: "software",
    title: "Software Engineering",
    persona: "hermes",
    tagline: "Plan, build, test, review, and ship dependable software.",
    mark: "SW",
    tools: [
      ["code", "Code", "Source files, modules, services, and application logic."],
      ["architecture", "Architecture", "System boundaries, contracts, dependencies, and scale."],
      ["github", "GitHub", "Branches, commits, pull requests, reviews, and build status."],
      ["tests", "Tests", "Unit, integration, regression, and end-to-end verification."],
      ["debug", "Debugger", "Errors, traces, logs, breakpoints, and failure analysis."],
      ["terminal", "Terminal", "Commands, scripts, package tools, and deployment workflows."],
      ["docs", "Documentation", "Technical notes, API contracts, onboarding, and decisions."],
      ["release", "Release", "Versions, changelogs, deployment checks, and rollback plans."],
    ],
  },
  research: {
    id: "research",
    title: "Research Observatory",
    persona: "minerva",
    tagline: "Turn reliable evidence into knowledge, decisions, and experiments.",
    mark: "RS",
    tools: [
      ["questions", "Questions", "Research questions, hypotheses, unknowns, and assumptions."],
      ["sources", "Sources", "Papers, books, reports, datasets, and source-quality notes."],
      ["evidence", "Evidence", "Claims, supporting findings, contradictions, and confidence."],
      ["experiments", "Experiments", "Methods, controls, observations, and repeatable tests."],
      ["citations", "Citations", "Traceable references and quote-safe source management."],
      ["synthesis", "Synthesis", "Patterns, explanations, tradeoffs, and conclusions."],
      ["knowledge", "Knowledge Bank", "Reusable findings connected to ATLAS projects."],
      ["review", "Peer Review", "Criticism, uncertainty, bias checks, and revision history."],
    ],
  },
  business: {
    id: "business",
    title: "Strategy Room",
    persona: "ajani",
    tagline: "Convert vision into leverage, execution, and durable value.",
    mark: "BZ",
    tools: [
      ["strategy", "Strategy", "Objectives, sequencing, leverage, and long-range direction."],
      ["market", "Market", "Customers, competitors, demand, pricing, and positioning."],
      ["finance", "Finance", "Budgets, costs, revenue, cash flow, and capital needs."],
      ["negotiation", "Negotiation", "Offers, floors, concessions, leverage, and deal terms."],
      ["risk", "Risk", "Legal, operational, financial, technical, and reputation exposure."],
      ["operations", "Operations", "People, schedules, resources, processes, and delivery."],
      ["roadmap", "Roadmap", "Milestones, dependencies, priorities, and decision gates."],
      ["investors", "Investors", "Pitches, evidence, updates, diligence, and follow-through."],
    ],
  },
  writing: {
    id: "writing",
    title: "Writing Studio",
    persona: "minerva",
    tagline: "Build stories with memory, emotion, structure, and a distinct voice.",
    mark: "WR",
    tools: [
      ["story", "Story Bible", "World rules, tone, themes, canon, and locked decisions."],
      ["characters", "Characters", "Goals, flaws, relationships, arcs, and voice."],
      ["timeline", "Timeline", "Events, chronology, reveals, and continuity checks."],
      ["plot", "Plot", "Acts, turning points, tension, mysteries, and resolutions."],
      ["scenes", "Scenes", "Purpose, conflict, environment, pacing, and transitions."],
      ["dialogue", "Dialogue", "Character voice, subtext, rhythm, and emotional truth."],
      ["research", "Research", "Cultural, historical, scientific, and location grounding."],
      ["drafts", "Drafts", "Versions, notes, revisions, feedback, and final polish."],
    ],
  },
  architecture: {
    id: "architecture",
    title: "Architecture Atelier",
    persona: "hermes",
    tagline: "Shape spaces that are beautiful, buildable, efficient, and alive.",
    mark: "AR",
    tools: [
      ["site", "Site", "Context, climate, access, terrain, and surrounding systems."],
      ["program", "Program", "Purpose, occupants, spaces, capacity, and relationships."],
      ["plans", "Plans", "Floor plans, circulation, dimensions, and accessibility."],
      ["structure", "Structure", "Loads, spans, materials, stability, and build sequence."],
      ["systems", "Building Systems", "Power, water, HVAC, controls, and safety."],
      ["materials", "Materials", "Durability, texture, sourcing, cost, and maintenance."],
      ["environment", "Environment", "Daylight, airflow, energy, ecology, and comfort."],
      ["visualization", "Visualization", "Models, renderings, walkthroughs, and presentations."],
    ],
  },
});

export function resolveWorkspace(project) {
  const id = project?.id || "robotics-workspace";
  if (id.includes("software") || id === "atlas-core" || id === "genesis-hud") return workspaceRegistry.software;
  if (id.includes("knowledge") || id.includes("research")) return workspaceRegistry.research;
  if (id.includes("business") || id.includes("banking")) return workspaceRegistry.business;
  if (id.includes("writing") || id.includes("story")) return workspaceRegistry.writing;
  if (id.includes("architecture") || id.includes("realm-forge")) return workspaceRegistry.architecture;
  return workspaceRegistry.robotics;
}
