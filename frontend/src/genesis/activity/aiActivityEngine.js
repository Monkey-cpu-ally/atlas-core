const PERSONA_CONFIG = Object.freeze({
  ajani: {
    name: "Ajani",
    role: "Strategy, risk, and execution",
    defaultTask: "Reviewing mission priorities",
    projectMatch: ["business", "strategy", "banking"],
  },
  minerva: {
    name: "Minerva",
    role: "Research, knowledge, and guidance",
    defaultTask: "Organizing the Knowledge Bank",
    projectMatch: ["knowledge", "research", "writing", "greenbots"],
  },
  hermes: {
    name: "Hermes",
    role: "Engineering, systems, and diagnostics",
    defaultTask: "Monitoring GENESIS systems",
    projectMatch: ["atlas", "genesis", "robotics", "weaver", "power-cell", "software", "architecture"],
  },
});

function findProjectForPersona(projects, personaId) {
  const config = PERSONA_CONFIG[personaId];
  return [...projects]
    .filter((project) => project.persona === personaId || config.projectMatch.some((token) => project.id?.includes(token)))
    .sort((a, b) => (b.progress || 0) - (a.progress || 0))[0] || null;
}

function latestPersonaEvent(items, personaId) {
  return [...items]
    .filter((item) => item.persona === personaId)
    .sort((a, b) => new Date(b.occurredAt || b.timestamp || 0) - new Date(a.occurredAt || a.timestamp || 0))[0] || null;
}

export function buildAiActivities({ projects = [], pulseItems = [], awarenessItems = [], bridgeStatus = "offline" } = {}) {
  return Object.entries(PERSONA_CONFIG).map(([id, config]) => {
    const project = findProjectForPersona(projects, id);
    const alert = latestPersonaEvent(awarenessItems, id);
    const pulse = latestPersonaEvent(pulseItems, id);
    const source = alert || pulse;
    const task = alert?.title || pulse?.title || project?.next || project?.updated || config.defaultTask;
    const progress = Number.isFinite(project?.progress) ? Math.max(0, Math.min(100, project.progress)) : 0;
    const priority = alert?.urgency === "high" ? "high" : project?.health === "risk" || project?.health === "blocked" ? "high" : "normal";
    const state = bridgeStatus === "connected" ? (source || project ? "active" : "ready") : "standby";

    return {
      id,
      name: config.name,
      role: config.role,
      task,
      progress,
      priority,
      state,
      projectTitle: project?.title || null,
      updatedAt: source?.occurredAt || source?.timestamp || null,
    };
  });
}
