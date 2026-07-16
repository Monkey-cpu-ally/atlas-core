const PERSONA_ALIASES = Object.freeze({
  ajani: ["ajani", "strategy"],
  minerva: ["minerva", "research"],
  hermes: ["hermes", "engineering"],
  council: ["council", "team review"],
});

const WAKE_WORDS = Object.freeze([
  "hey atlas",
  "okay atlas",
  "ok atlas",
  "atlas",
]);

function normalizeTranscript(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[.,!?;:]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function stripWakeWord(value) {
  const text = normalizeTranscript(value);
  const wakeWord = WAKE_WORDS.find((phrase) => text === phrase || text.startsWith(`${phrase} `));
  return wakeWord ? text.slice(wakeWord.length).trim() : text;
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

function resolveCurrentProject(currentProject, projects) {
  if (currentProject?.id) return currentProject;
  return [...projects]
    .filter((project) => project?.id)
    .sort((a, b) => (b.progress || 0) - (a.progress || 0))[0] || null;
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

export function routeVoiceCommand(transcript, { projects = [], currentProject = null } = {}) {
  const originalTranscript = normalizeTranscript(transcript);
  const text = stripWakeWord(originalTranscript);
  if (!text) return { type: "wake", transcript: originalTranscript };

  if (includesAny(text, ["repeat that", "say that again", "repeat response", "what did you say"])) {
    return { type: "repeat", transcript: originalTranscript, contextual: true };
  }

  if (includesAny(text, ["cancel", "never mind", "nevermind", "stop speaking", "be quiet"])) {
    return { type: "cancel", transcript: originalTranscript, contextual: true };
  }

  if (includesAny(text, ["open it", "continue it", "resume it", "show it"])) {
    const resolvedProject = resolveCurrentProject(currentProject, projects);
    return resolvedProject
      ? { type: "project", projectId: resolvedProject.id, project: resolvedProject, transcript: originalTranscript, contextual: true }
      : { type: "projects", transcript: originalTranscript, contextual: true };
  }

  if (includesAny(text, ["continue current project", "resume current project", "open current project", "continue where i left off"])) {
    const resolvedProject = resolveCurrentProject(currentProject, projects);
    return resolvedProject
      ? { type: "project", projectId: resolvedProject.id, project: resolvedProject, transcript: originalTranscript, contextual: true }
      : { type: "projects", transcript: originalTranscript, contextual: true };
  }

  if (includesAny(text, ["what's next", "what is next", "next step", "what should i do next"])) {
    return { type: "mission", transcript: originalTranscript, contextual: true };
  }

  if (includesAny(text, ["go back", "back", "previous screen", "return"])) {
    return { type: "home", transcript: originalTranscript, contextual: true };
  }

  const project = findVoiceProject(text, projects);
  if (project && includesAny(text, ["open", "continue", "resume", "show", "workspace", project.title?.toLowerCase() || project.id])) {
    return {
      type: "project",
      projectId: project.id,
      project,
      transcript: originalTranscript,
    };
  }

  for (const [persona, aliases] of Object.entries(PERSONA_ALIASES)) {
    if (includesAny(text, aliases)) return { type: "persona", persona, transcript: originalTranscript };
  }

  if (includesAny(text, ["status", "observatory", "system status", "show status"])) {
    return { type: "observatory", transcript: originalTranscript };
  }
  if (includesAny(text, ["show projects", "open projects", "project wall", "all projects"])) {
    return { type: "projects", transcript: originalTranscript };
  }
  if (includesAny(text, ["show mission", "open mission", "current mission"])) {
    return { type: "mission", transcript: originalTranscript };
  }
  if (includesAny(text, ["show pulse", "open pulse", "github activity", "latest updates"])) {
    return { type: "pulse", transcript: originalTranscript };
  }
  if (includesAny(text, ["show awareness", "open awareness", "show alerts", "what needs attention"])) {
    return { type: "awareness", transcript: originalTranscript };
  }
  if (includesAny(text, ["go home", "return home", "close", "quiet mode", "idle"])) {
    return { type: "home", transcript: originalTranscript };
  }

  return { type: "unknown", transcript: originalTranscript };
}

export { normalizeTranscript, normalizeProjectName, resolveCurrentProject, stripWakeWord };
