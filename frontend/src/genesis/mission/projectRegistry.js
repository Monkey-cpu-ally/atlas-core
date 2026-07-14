export const projects = Object.freeze([
  { id: "atlas-core", title: "ATLAS Core", persona: "hermes", progress: 61, health: "stable", updated: "Visual event and Genesis HUD development" },
  { id: "robotics-workspace", title: "Robotics Workspace", persona: "hermes", progress: 28, health: "building", updated: "Workspace framework queued" },
  { id: "knowledge-bank", title: "Knowledge Bank", persona: "minerva", progress: 42, health: "planning", updated: "Shared research structure" },
  { id: "weaver", title: "The Weaver", persona: "hermes", progress: 19, health: "research", updated: "Suspended multi-arm platform" },
  { id: "power-cell", title: "Power Cell", persona: "hermes", progress: 23, health: "research", updated: "Energy-storage concept development" },
  { id: "greenbots", title: "GreenBots", persona: "minerva", progress: 17, health: "concept", updated: "Environmental restoration robotics" },
]);

export function getProjects(ids) {
  if (!ids?.length) return projects;
  const wanted = new Set(ids);
  return projects.filter((project) => wanted.has(project.id));
}
