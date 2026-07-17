import { buildConversationCommand } from "./conversationIntent";
import {
  clearPendingClarification,
  getPendingClarification,
  requestProjectClarification,
  resolvePendingClarification,
} from "./voiceClarification";

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

const EMPTY_CONTEXT = Object.freeze({ type: null, id: null, value: null });
let voiceContext = { ...EMPTY_CONTEXT };

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

function scoreProjectMatch(text, project) {
  const terms = projectSearchTerms(project);
  let bestScore = 0;

  terms.forEach((term) => {
    if (text === term) bestScore = Math.max(bestScore, 100 + term.length);
    else if (text.includes(term)) bestScore = Math.max(bestScore, 60 + term.length);
    else if (term.includes(text) && text.length >= 3) bestScore = Math.max(bestScore, 30 + text.length);
  });

  return bestScore;
}

function resolveCurrentProject(currentProject, projects) {
  if (currentProject?.id) return currentProject;
  return [...projects]
    .filter((project) => project?.id)
    .sort((a, b) => (b.progress || 0) - (a.progress || 0))[0] || null;
}

function findExplicitPersona(text) {
  for (const [persona, aliases] of Object.entries(PERSONA_ALIASES)) {
    if (includesAny(text, aliases)) return persona;
  }
  return null;
}

function looksConversational(text, project, explicitPersona) {
  if (project || explicitPersona) return true;
  return includesAny(text, [
    "i'm thinking",
    "im thinking",
    "i want",
    "we should",
    "let's",
    "lets",
    "could we",
    "can we",
    "what if",
    "help me",
    "explain",
    "teach me",
    "review",
    "redesign",
    "research",
    "brainstorm",
  ]);
}

export function getVoiceContext() {
  return { ...voiceContext };
}

export function resetVoiceContext() {
  voiceContext = { ...EMPTY_CONTEXT };
  clearPendingClarification();
}

export function rememberVoiceContext(command) {
  if ((command?.type === "project" || command?.type === "conversation") && command.project?.id) {
    voiceContext = { type: "project", id: command.project.id, value: command.project };
  } else if ((command?.type === "persona" || command?.type === "conversation") && command.persona) {
    voiceContext = { type: "persona", id: command.persona, value: command.persona };
  }
  return getVoiceContext();
}

function rememberAndReturn(command) {
  rememberVoiceContext(command);
  return command;
}

export function findVoiceProjectCandidates(transcript, projects = []) {
  const text = normalizeProjectName(transcript);
  if (!text) return [];

  return projects
    .map((project) => ({ project, score: scoreProjectMatch(text, project) }))
    .filter((match) => match.project?.id && match.score > 0)
    .sort((a, b) => b.score - a.score);
}

export function findVoiceProject(transcript, projects = []) {
  return findVoiceProjectCandidates(transcript, projects)[0]?.project || null;
}

function hasAmbiguousProjectMatch(matches) {
  if (matches.length < 2) return false;
  const [first, second] = matches;
  return first.score < 100 && first.score - second.score <= 5;
}

function contextualReferenceCommand(text, originalTranscript, projects) {
  const referencesPriorTarget = includesAny(text, [
    "open it",
    "continue it",
    "resume it",
    "show it",
    "open that",
    "continue that",
    "resume that",
    "show that",
    "go to it",
    "what is next for it",
    "what's next for it",
    "show me the next step",
  ]);
  if (!referencesPriorTarget || !voiceContext.type) return null;

  if (voiceContext.type === "project") {
    const project = projects.find((item) => item.id === voiceContext.id) || voiceContext.value;
    if (project?.id) {
      return {
        type: "project",
        projectId: project.id,
        project,
        transcript: originalTranscript,
        contextual: true,
        resolvedFromMemory: true,
        intent: includesAny(text, ["next", "next step"]) ? "next-step" : "open",
      };
    }
  }

  if (voiceContext.type === "persona" && voiceContext.id) {
    return {
      type: "persona",
      persona: voiceContext.id,
      transcript: originalTranscript,
      contextual: true,
      resolvedFromMemory: true,
    };
  }

  return null;
}

export function routeVoiceCommand(transcript, { projects = [], currentProject = null } = {}) {
  const originalTranscript = normalizeTranscript(transcript);
  const text = stripWakeWord(originalTranscript);
  if (!text) return { type: "wake", transcript: originalTranscript };

  const clarificationResult = resolvePendingClarification(text);
  if (clarificationResult) return rememberAndReturn(clarificationResult);

  if (includesAny(text, ["repeat that", "say that again", "repeat response", "what did you say"])) {
    return { type: "repeat", transcript: originalTranscript, contextual: true };
  }

  if (includesAny(text, ["cancel", "never mind", "nevermind", "stop speaking", "be quiet"])) {
    clearPendingClarification();
    return { type: "cancel", transcript: originalTranscript, contextual: true };
  }

  const pendingClarification = getPendingClarification();
  if (pendingClarification.kind === "project" && pendingClarification.options.length) {
    return {
      type: "clarification",
      clarificationKind: "project",
      options: pendingClarification.options,
      originalCommand: pendingClarification.originalCommand,
      transcript: originalTranscript,
      contextual: true,
      retry: true,
    };
  }

  const memoryCommand = contextualReferenceCommand(text, originalTranscript, projects);
  if (memoryCommand) return rememberAndReturn(memoryCommand);

  if (includesAny(text, ["continue current project", "resume current project", "open current project", "continue where i left off"])) {
    const resolvedProject = resolveCurrentProject(currentProject, projects);
    const command = resolvedProject
      ? { type: "project", projectId: resolvedProject.id, project: resolvedProject, transcript: originalTranscript, contextual: true }
      : { type: "projects", transcript: originalTranscript, contextual: true };
    return rememberAndReturn(command);
  }

  if (includesAny(text, ["what's next", "what is next", "next step", "what should i do next"])) {
    return { type: "mission", transcript: originalTranscript, contextual: true };
  }

  if (includesAny(text, ["go back", "back", "previous screen", "return"])) {
    return { type: "home", transcript: originalTranscript, contextual: true };
  }

  const projectMatches = findVoiceProjectCandidates(text, projects);
  const project = projectMatches[0]?.project || null;
  const explicitPersona = findExplicitPersona(text);
  const projectAction = project && includesAny(text, ["open", "continue", "resume", "show", "workspace", project.title?.toLowerCase() || project.id]);

  if (projectAction && hasAmbiguousProjectMatch(projectMatches)) {
    return requestProjectClarification(
      projectMatches.slice(0, 3).map((match) => match.project),
      { type: "project", transcript: originalTranscript },
    );
  }

  if (projectAction) {
    return rememberAndReturn({
      type: "project",
      projectId: project.id,
      project,
      transcript: originalTranscript,
    });
  }

  const isPersonaOnly = explicitPersona && PERSONA_ALIASES[explicitPersona].some((alias) => text === alias);
  if (isPersonaOnly) {
    return rememberAndReturn({ type: "persona", persona: explicitPersona, transcript: originalTranscript });
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

  if (looksConversational(text, project, explicitPersona)) {
    const conversationCommand = buildConversationCommand({
      text,
      originalTranscript,
      project,
      persona: explicitPersona,
    });

    if (project && hasAmbiguousProjectMatch(projectMatches)) {
      return requestProjectClarification(
        projectMatches.slice(0, 3).map((match) => match.project),
        conversationCommand,
      );
    }

    return rememberAndReturn(conversationCommand);
  }

  return { type: "unknown", transcript: originalTranscript };
}

export {
  normalizeTranscript,
  normalizeProjectName,
  resolveCurrentProject,
  stripWakeWord,
  findExplicitPersona,
  hasAmbiguousProjectMatch,
};
