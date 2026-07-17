const INTENT_PATTERNS = Object.freeze([
  { intent: "design", phrases: ["design", "redesign", "build", "make", "create", "change", "smaller", "larger", "lighter", "stronger"] },
  { intent: "research", phrases: ["research", "study", "find out", "look into", "compare", "evidence", "papers"] },
  { intent: "review", phrases: ["review", "check", "inspect", "evaluate", "analyze", "analyse", "what is wrong", "problems"] },
  { intent: "plan", phrases: ["plan", "roadmap", "schedule", "milestone", "next steps", "how do we start", "what should we do"] },
  { intent: "explain", phrases: ["explain", "teach me", "how does", "how do", "why does", "what is"] },
  { intent: "brainstorm", phrases: ["idea", "ideas", "brainstorm", "what if", "could we", "can we"] },
]);

const PERSONA_BY_INTENT = Object.freeze({
  design: "hermes",
  research: "minerva",
  review: "council",
  plan: "ajani",
  explain: "minerva",
  brainstorm: "council",
});

function includesPhrase(text, phrase) {
  return text === phrase || text.includes(phrase);
}

export function detectConversationIntent(text) {
  for (const entry of INTENT_PATTERNS) {
    if (entry.phrases.some((phrase) => includesPhrase(text, phrase))) return entry.intent;
  }
  return "discuss";
}

export function inferConversationPersona(intent, explicitPersona = null, project = null) {
  if (explicitPersona) return explicitPersona;
  if (project?.persona) return project.persona;
  return PERSONA_BY_INTENT[intent] || "atlas";
}

export function extractConversationTopic(text, project = null) {
  if (project?.title) return project.title;

  const cleaned = String(text || "")
    .replace(/\b(hey|okay|ok|atlas|ajani|minerva|hermes|council)\b/g, " ")
    .replace(/\b(i am|i'm|im|we are|we're|were|let us|let's|lets|thinking about|want to|need to|could we|can we)\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  return cleaned || "this idea";
}

export function buildConversationCommand({ text, originalTranscript, project = null, persona = null }) {
  const intent = detectConversationIntent(text);
  const resolvedPersona = inferConversationPersona(intent, persona, project);

  return {
    type: "conversation",
    intent,
    topic: extractConversationTopic(text, project),
    project,
    projectId: project?.id || null,
    persona: resolvedPersona,
    transcript: originalTranscript,
    conversational: true,
  };
}

export { INTENT_PATTERNS, PERSONA_BY_INTENT };
