const EMPTY_MEMORY = Object.freeze({
  project: null,
  projectId: null,
  persona: null,
  intent: null,
  topic: null,
  lastTranscript: "",
  turnCount: 0,
});

let conversationMemory = { ...EMPTY_MEMORY };

export function getConversationMemory() {
  return { ...conversationMemory };
}

export function resetConversationMemory() {
  conversationMemory = { ...EMPTY_MEMORY };
  return getConversationMemory();
}

export function rememberConversationTurn(command) {
  if (!command) return getConversationMemory();

  const project = command.project?.id ? command.project : conversationMemory.project;
  conversationMemory = {
    project,
    projectId: project?.id || conversationMemory.projectId || null,
    persona: command.persona || project?.persona || conversationMemory.persona || null,
    intent: command.intent || conversationMemory.intent || null,
    topic: command.topic || project?.title || conversationMemory.topic || null,
    lastTranscript: command.transcript || conversationMemory.lastTranscript,
    turnCount: conversationMemory.turnCount + 1,
  };

  return getConversationMemory();
}

export function looksLikeConversationFollowUp(text) {
  const value = String(text || "").trim();
  if (!value || !conversationMemory.projectId) return false;

  const referencesPriorSubject = /\b(it|that|this|them|those|the design|the project|same one)\b/.test(value);
  const followUpAction = /\b(make|change|redesign|research|study|review|check|explain|compare|plan|improve|lighter|smaller|larger|stronger|safer|cheaper|faster)\b/.test(value);
  const compactFollowUp = value.split(/\s+/).length <= 7 && followUpAction;
  return referencesPriorSubject || compactFollowUp;
}

export function conversationFollowUpDefaults() {
  return {
    project: conversationMemory.project,
    persona: conversationMemory.persona,
    intent: conversationMemory.intent,
    topic: conversationMemory.topic,
  };
}

export { EMPTY_MEMORY };