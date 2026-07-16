const PERSONA_ALIASES = Object.freeze({
  ajani: ["ajani", "strategy"],
  minerva: ["minerva", "research"],
  hermes: ["hermes", "engineering"],
  council: ["council", "team review"],
});

function normalizeTranscript(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[.,!?;:]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function includesAny(text, phrases) {
  return phrases.some((phrase) => text.includes(phrase));
}

export function routeVoiceCommand(transcript) {
  const text = normalizeTranscript(transcript);
  if (!text) return { type: "unknown", transcript: text };

  for (const [persona, aliases] of Object.entries(PERSONA_ALIASES)) {
    if (includesAny(text, aliases)) return { type: "persona", persona, transcript: text };
  }

  if (includesAny(text, ["status", "observatory", "system status", "show status"])) {
    return { type: "observatory", transcript: text };
  }
  if (includesAny(text, ["show projects", "open projects", "project wall", "all projects"])) {
    return { type: "projects", transcript: text };
  }
  if (includesAny(text, ["show mission", "open mission", "current mission"])) {
    return { type: "mission", transcript: text };
  }
  if (includesAny(text, ["show pulse", "open pulse", "github activity", "latest updates"])) {
    return { type: "pulse", transcript: text };
  }
  if (includesAny(text, ["show awareness", "open awareness", "show alerts", "what needs attention"])) {
    return { type: "awareness", transcript: text };
  }
  if (includesAny(text, ["go home", "return home", "close", "quiet mode", "idle"])) {
    return { type: "home", transcript: text };
  }

  return { type: "unknown", transcript: text };
}

export { normalizeTranscript };
