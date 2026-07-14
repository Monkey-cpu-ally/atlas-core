export const atlasTokens = Object.freeze({
  color: {
    background: "#070b10",
    surface: "rgba(18, 27, 36, 0.58)",
    line: "rgba(213, 232, 239, 0.28)",
    text: "#e7f0f2",
    muted: "#8b9aa3",
    idle: "#d58a35",
    ajani: "#8d2638",
    minerva: "#2d9a8c",
    hermes: "#ddd2b2",
    council: "#7650b5",
    warning: "#d9a441",
    danger: "#d04a4a",
  },
  motion: {
    fast: 180,
    normal: 420,
    slow: 900,
    portraitHold: 2200,
    idleBreath: 6000,
  },
  glass: {
    blur: 18,
    border: "1px solid rgba(220, 238, 244, 0.18)",
    shadow: "0 24px 80px rgba(0, 0, 0, 0.42)",
  },
  wheel: {
    radius: 230,
    nodeSize: 68,
    selectedNodeSize: 112,
    visibleArcDegrees: 220,
  },
});

export const personaTokens = Object.freeze({
  ajani: {
    accent: atlasTokens.color.ajani,
    branchClass: "atlas-branch--tactical",
  },
  minerva: {
    accent: atlasTokens.color.minerva,
    branchClass: "atlas-branch--organic",
  },
  hermes: {
    accent: atlasTokens.color.hermes,
    branchClass: "atlas-branch--circuit",
  },
  council: {
    accent: atlasTokens.color.council,
    branchClass: "atlas-branch--council",
  },
  atlas: {
    accent: atlasTokens.color.idle,
    branchClass: "atlas-branch--idle",
  },
});
