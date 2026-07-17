const EMPTY_CLARIFICATION = Object.freeze({
  active: false,
  originalTranscript: "",
  intent: null,
  persona: null,
  candidates: [],
});

let pendingClarification = { ...EMPTY_CLARIFICATION };

export function getPendingClarification() {
  return {
    ...pendingClarification,
    candidates: [...pendingClarification.candidates],
  };
}

export function setPendingClarification(value = {}) {
  pendingClarification = {
    active: true,
    originalTranscript: value.originalTranscript || "",
    intent: value.intent || null,
    persona: value.persona || null,
    candidates: [...(value.candidates || [])].filter((candidate) => candidate?.id),
  };
  return getPendingClarification();
}

export function clearPendingClarification() {
  pendingClarification = { ...EMPTY_CLARIFICATION };
  return getPendingClarification();
}

export function resolvePendingClarification(transcript, findProject) {
  if (!pendingClarification.active || typeof findProject !== "function") return null;

  const project = findProject(transcript, pendingClarification.candidates);
  if (!project?.id) return null;

  const resolved = {
    project,
    projectId: project.id,
    originalTranscript: pendingClarification.originalTranscript,
    intent: pendingClarification.intent,
    persona: pendingClarification.persona,
  };
  clearPendingClarification();
  return resolved;
}

export { EMPTY_CLARIFICATION };
