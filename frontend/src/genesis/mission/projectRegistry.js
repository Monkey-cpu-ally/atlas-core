export const projects = Object.freeze([
  { id: "atlas-core", title: "ATLAS Core", persona: "hermes", progress: 61, health: "stable", updated: "Visual event and Genesis HUD development", next: "Connect live AI events and service health" },
  { id: "robotics-workspace", title: "Robotics Workspace", persona: "hermes", progress: 38, health: "building", updated: "Shared workspace engine connected", next: "Connect blueprint and simulation data" },
  { id: "knowledge-bank", title: "Knowledge Bank", persona: "minerva", progress: 42, health: "planning", updated: "Shared research structure", next: "Build ingestion and citation workflows" },
  { id: "weaver", title: "The Weaver", persona: "hermes", progress: 19, health: "research", updated: "Suspended multi-arm platform", next: "Validate arm geometry and camera coverage" },
  { id: "power-cell", title: "Power Cell", persona: "hermes", progress: 23, health: "research", updated: "Energy-storage concept development", next: "Review chemistry and safe test design" },
  { id: "greenbots", title: "GreenBots", persona: "minerva", progress: 17, health: "concept", updated: "Environmental restoration robotics", next: "Prioritize first environmental deployment" },
  { id: "software-workspace", title: "Software Engineering", persona: "hermes", progress: 46, health: "building", updated: "Code, tests, GitHub, and releases", next: "Connect repository and CI activity" },
  { id: "research-workspace", title: "Research Observatory", persona: "minerva", progress: 29, health: "planning", updated: "Evidence and source-quality workflow", next: "Connect Knowledge Bank sources" },
  { id: "business-workspace", title: "Strategy Room", persona: "ajani", progress: 21, health: "planning", updated: "Business, risk, negotiation, and finance", next: "Define operating targets and decision gates" },
  { id: "writing-workspace", title: "Writing Studio", persona: "minerva", progress: 33, health: "active", updated: "Story bibles, character arcs, and timelines", next: "Connect current story projects" },
  { id: "architecture-workspace", title: "Architecture Atelier", persona: "hermes", progress: 14, health: "concept", updated: "Site, plans, systems, and visualization", next: "Define first building project" },
]);

export function getProjects(ids) {
  if (!ids?.length) return projects;
  const wanted = new Set(ids);
  return projects.filter((project) => wanted.has(project.id));
}
