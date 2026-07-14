export const missions = Object.freeze([
  {
    id: "genesis-alpha",
    title: "GENESIS Alpha",
    owner: "Council",
    progress: 58,
    health: "active",
    nextStep: "Finish the Robotics workspace shell and live project data bindings.",
    deadline: null,
    projectIds: ["atlas-core", "robotics-workspace", "knowledge-bank"],
  },
  {
    id: "robotics-foundation",
    title: "Robotics Foundation",
    owner: "Hermes",
    progress: 34,
    health: "planning",
    nextStep: "Connect blueprint, electronics, manufacturing, and simulation panels.",
    deadline: null,
    projectIds: ["weaver", "greenbots", "nir-scanner"],
  },
  {
    id: "knowledge-bank",
    title: "Knowledge Bank",
    owner: "Minerva",
    progress: 31,
    health: "active",
    nextStep: "Define source ingestion, citation, and memory-linking rules.",
    deadline: null,
    projectIds: ["knowledge-bank", "research", "learning"],
  },
]);

export const projectWall = Object.freeze([
  { id: "genesis-hud", title: "Genesis HUD", ai: "hermes", health: "good", progress: 62, lastUpdate: "Today", next: "Complete mission and workspace navigation" },
  { id: "atlas-core", title: "ATLAS Core", ai: "ajani", health: "watch", progress: 48, lastUpdate: "Today", next: "Connect real AI events" },
  { id: "weaver", title: "Weaver", ai: "hermes", health: "research", progress: 24, lastUpdate: "This week", next: "Validate mechanical layout" },
  { id: "knowledge-bank", title: "Knowledge Bank", ai: "minerva", health: "good", progress: 31, lastUpdate: "This week", next: "Build ingestion rules" },
  { id: "power-cell", title: "Power Cell", ai: "hermes", health: "watch", progress: 18, lastUpdate: "12 days ago", next: "Review chemistry and test plan" },
  { id: "greenbots", title: "GreenBots", ai: "minerva", health: "research", progress: 16, lastUpdate: "18 days ago", next: "Prioritize environmental use cases" },
]);

export function getMission(id) {
  return missions.find((mission) => mission.id === id) || missions[0];
}
