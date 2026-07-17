const APPROVAL_REQUIRED_INTENTS = new Set(["design", "review", "plan"]);

function normalizeObjective(command) {
  return String(command?.transcript || command?.topic || "")
    .replace(/\s+/g, " ")
    .trim();
}

export function taskStatusForIntent(intent) {
  return APPROVAL_REQUIRED_INTENTS.has(intent) ? "proposed" : "ready";
}

export function buildConversationTask(command) {
  if (command?.type !== "conversation") return null;

  const project = command.project || null;
  const intent = command.intent || "discuss";
  const status = taskStatusForIntent(intent);

  return {
    id: `voice-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    source: "voice",
    projectId: project?.id || null,
    projectTitle: project?.title || null,
    owner: command.persona || project?.persona || "atlas",
    intent,
    objective: normalizeObjective(command),
    topic: command.topic || project?.title || "this idea",
    status,
    approvalRequired: status === "proposed",
    createdAt: new Date().toISOString(),
    context: {
      resolvedFromConversationMemory: Boolean(command.resolvedFromConversationMemory),
      resolvedFromClarification: Boolean(command.resolvedFromClarification),
      conversational: true,
    },
  };
}

export function attachConversationTask(command) {
  const task = buildConversationTask(command);
  return task ? { ...command, task } : command;
}

export { APPROVAL_REQUIRED_INTENTS };
