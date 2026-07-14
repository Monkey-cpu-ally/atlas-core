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
]);

export function getMission(id) {
  return missions.find((mission) => mission.id === id) || missions[0];
}
