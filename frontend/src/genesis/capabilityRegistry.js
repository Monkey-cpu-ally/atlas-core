export const capabilityRegistry = Object.freeze({
  hermes: [
    { id: "robotics", label: "Robotics", summary: "Robots, automation, control, and machine design.", artKey: "robotics", projectIds: ["weaver", "greenbots"] },
    { id: "software", label: "Software", summary: "Applications, services, APIs, and system architecture.", artKey: "software", projectIds: ["atlas-core", "hyper-axel"] },
    { id: "electronics", label: "Electronics", summary: "Circuits, PCBs, sensors, embedded systems, and hardware integration.", artKey: "electronics", projectIds: ["nir-scanner", "resonance-scanner"] },
    { id: "cad", label: "CAD", summary: "Mechanical design, assemblies, dimensions, and fabrication-ready models.", artKey: "cad", projectIds: ["weaver", "mother-box"] },
    { id: "manufacturing", label: "Manufacturing", summary: "Processes, materials, tooling, assembly, and quality control.", artKey: "manufacturing", projectIds: ["weaver", "power-cell"] },
    { id: "power-systems", label: "Power Systems", summary: "Energy storage, delivery, efficiency, and thermal control.", artKey: "power", projectIds: ["power-cell"] },
    { id: "digital-twin", label: "Digital Twin", summary: "Simulation, telemetry, prediction, and virtual testing.", artKey: "digital-twin", projectIds: ["weaver", "atlas-core"] },
    { id: "weaver", label: "Weaver", summary: "The multi-arm suspended fabrication and research platform.", artKey: "weaver", projectIds: ["weaver"] },
  ],
  minerva: [
    { id: "biology", label: "Biology", summary: "Living systems, physiology, cellular processes, and biomimicry.", artKey: "biology", projectIds: ["greenbots", "augmentation-framework"] },
    { id: "botany", label: "Botany", summary: "Plants, growth systems, medicinal species, and ecological design.", artKey: "botany", projectIds: ["greenbots", "realm-forge"] },
    { id: "chemistry", label: "Chemistry", summary: "Materials, reactions, compounds, and laboratory reasoning.", artKey: "chemistry", projectIds: ["power-cell"] },
    { id: "genetics", label: "Genetics", summary: "Genomics, CRISPR, inheritance, and responsible biotechnology.", artKey: "genetics", projectIds: ["crispr-precision"] },
    { id: "environment", label: "Environment", summary: "Climate, ecosystems, restoration, pollution, and sustainability.", artKey: "environment", projectIds: ["greenbots", "realm-forge"] },
    { id: "learning", label: "Learning", summary: "Teaching, study plans, explanations, testing, and skill growth.", artKey: "learning", projectIds: ["knowledge-bank"] },
    { id: "research", label: "Research", summary: "Evidence review, source quality, synthesis, and discovery.", artKey: "research", projectIds: ["knowledge-bank"] },
    { id: "knowledge-bank", label: "Knowledge Bank", summary: "ATLAS shared research memory across all disciplines.", artKey: "knowledge", projectIds: ["knowledge-bank"] },
  ],
  ajani: [
    { id: "strategy", label: "Strategy", summary: "Objectives, sequencing, leverage, tradeoffs, and long-range planning.", artKey: "strategy", projectIds: ["atlas-core"] },
    { id: "business", label: "Business", summary: "Models, pricing, competition, revenue, and execution.", artKey: "business", projectIds: ["banking-system"] },
    { id: "negotiation", label: "Negotiation", summary: "Offers, leverage, concessions, contradictions, and deal structure.", artKey: "negotiation", projectIds: [] },
    { id: "risk", label: "Risk", summary: "Technical, financial, operational, and legal exposure.", artKey: "risk", projectIds: ["atlas-core"] },
    { id: "projects", label: "Projects", summary: "Milestones, priorities, dependencies, and completion plans.", artKey: "projects", projectIds: ["atlas-core", "weaver", "power-cell"] },
    { id: "operations", label: "Operations", summary: "Daily execution, resources, schedules, and coordination.", artKey: "operations", projectIds: ["atlas-core"] },
    { id: "finance", label: "Finance", summary: "Budgets, markets, investment analysis, and financial planning.", artKey: "finance", projectIds: ["banking-system"] },
    { id: "security", label: "Security", summary: "Privacy, access, resilience, and defensive system planning.", artKey: "security", projectIds: ["atlas-core"] },
  ],
});

export const councilCapabilities = Object.freeze([
  { id: "council-review", label: "Council Review", summary: "All three AIs examine one decision from their specialties.", artKey: "council" },
  { id: "conflict-map", label: "Conflict Map", summary: "Shows agreements, disagreements, unknowns, and unresolved risks.", artKey: "conflict" },
  { id: "final-recommendation", label: "Recommendation", summary: "Combines evidence while preserving important dissent.", artKey: "recommendation" },
]);

export function getCapabilities(persona) {
  if (persona === "council") return councilCapabilities;
  return capabilityRegistry[persona] || [];
}
