export const portraitRegistry = Object.freeze({
  ajani: {
    label: "Ajani",
    role: "Strategist · Warrior Mind",
    reference: "/assets/ai-faces/atlas-ai-face-reference.jpg",
    states: {
      idle: "/assets/ai-faces/ajani/neutral.webp",
      listening: "/assets/ai-faces/ajani/neutral.webp",
      thinking: "/assets/ai-faces/ajani/thinking.webp",
      speaking: "/assets/ai-faces/ajani/speaking.webp",
      working: "/assets/ai-faces/ajani/serious.webp",
      warning: "/assets/ai-faces/ajani/serious.webp",
      approval: "/assets/ai-faces/ajani/approval.webp",
    },
  },
  hermes: {
    label: "Hermes",
    role: "Architect · System Genius",
    reference: "/assets/ai-faces/atlas-ai-face-reference.jpg",
    states: {
      idle: "/assets/ai-faces/hermes/neutral.webp",
      listening: "/assets/ai-faces/hermes/neutral.webp",
      thinking: "/assets/ai-faces/hermes/thinking.webp",
      speaking: "/assets/ai-faces/hermes/speaking.webp",
      working: "/assets/ai-faces/hermes/serious.webp",
      warning: "/assets/ai-faces/hermes/serious.webp",
      scheming: "/assets/ai-faces/hermes/scheming.webp",
    },
  },
  minerva: {
    label: "Minerva",
    role: "Scholar · Guardian Mind",
    reference: "/assets/ai-faces/atlas-ai-face-reference.jpg",
    states: {
      idle: "/assets/ai-faces/minerva/neutral.webp",
      listening: "/assets/ai-faces/minerva/neutral.webp",
      thinking: "/assets/ai-faces/minerva/thinking.webp",
      speaking: "/assets/ai-faces/minerva/speaking.webp",
      working: "/assets/ai-faces/minerva/guidance.webp",
      warning: "/assets/ai-faces/minerva/concern.webp",
      concern: "/assets/ai-faces/minerva/concern.webp",
      guidance: "/assets/ai-faces/minerva/guidance.webp",
    },
  },
});

export function getPortrait(persona, state = "idle") {
  const entry = portraitRegistry[persona];
  if (!entry) return null;
  return {
    ...entry,
    src: entry.states[state] || entry.states.idle,
    state,
  };
}
