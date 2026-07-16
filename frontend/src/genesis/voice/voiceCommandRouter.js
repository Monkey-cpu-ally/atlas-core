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

function normalizeProjectName(value) {
  return normalizeTranscript(value)
    .replace(/\b(project|the|open|continue|resume|show|workspace)\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function projectSearchTerms(project) {
  const terms = new Set([
    normalizeProjectName(project?.id),
    normalizeProjectName(project?.title),
    ...(project?.aliases || []).map(normalizeProjectName),
  ]);
  return [...terms].filter(Boolean).sort((a, b) => b.length - a.length);
}

export function findVoiceProject(transcript, projects = []) {
  const text = normalizeProjectName(transcript);
  if (!text) return null;

  const matches = projects
    .map((project) => {
      const terms = projectSearchTerms(project);
      const matchedTerm = terms.find((term) => text.includes(term) || term.includes(text));
      return matchedTerm ? { project, score: matchedTerm.length } : null;
    })
    .filter(Boolean)
    .sort((a, b) => b.score - a.score);

  return matches[0]?.project || null;
}

export function routeVoiceCommand(transcript, { projects = [] } = {}) {
  const text = normalizeTranscript(transcript);
  if (!text) return { type: "unknown", transcript: text };

  const project = findVoiceProject(text, projects);
  if (project && includesAny(text, ["open", "continue", "resume", "show", "workspace", project.title?.toLowerCase() || project.id])) {
    return {
      type: "project",
      projectId: project.id,
      project,
      transcript: text,
    };
  }

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

export { normalizeTranscript, normalizeProjectName };