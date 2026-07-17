import { routeVoiceCommand } from "./voiceCommandRouter";

const PERSONA_OPENERS = Object.freeze({
  atlas: "I understand.",
  hermes: "Hermes here.",
  minerva: "Minerva is ready.",
  ajani: "Ajani is with you.",
  council: "The Council will examine it together.",
});

const INTENT_RESPONSES = Object.freeze({
  design: "I will open the engineering context and help shape the design.",
  research: "I will organize the research questions and evidence we need.",
  review: "I will review the current work, risks, and weak points.",
  plan: "I will turn this into clear milestones and a next action.",
  explain: "I will explain it step by step and connect it to the project.",
  brainstorm: "I will explore several genuinely different directions before narrowing them down.",
  discuss: "Let us develop the idea and identify the best next step.",
});

function buildConversationResponse(command) {
  const opener = PERSONA_OPENERS[command.persona] || PERSONA_OPENERS.atlas;
  const action = INTENT_RESPONSES[command.intent] || INTENT_RESPONSES.discuss;
  const topic = command.project?.title || command.topic;
  return `${opener} About ${topic}: ${action}`;
}

function buildClarificationResponse(command) {
  const names = (command.options || []).map((option) => option.title || option.id).filter(Boolean);
  if (!names.length) return "Which project did you mean?";
  if (names.length === 1) return `Did you mean ${names[0]}?`;
  if (names.length === 2) return `Which project did you mean: ${names[0]} or ${names[1]}?`;
  return `Which project did you mean: ${names[0]}, ${names[1]}, or ${names[2]}?`;
}

export function buildVoiceCommandResponse(
  transcript,
  { projects = [], mission = null, currentProject = null, lastResponse = "" } = {},
) {
  const command = routeVoiceCommand(transcript, { projects, currentProject });

  switch (command.type) {
    case "wake":
      return { command, message: "Yes?" };
    case "repeat":
      return { command, message: lastResponse || "There is no previous response to repeat." };
    case "cancel":
      return { command, message: command.clarificationCancelled ? "Clarification cancelled." : "Cancelled." };
    case "clarification":
      return { command, message: buildClarificationResponse(command) };
    case "project":
      return { command, message: command.contextual ? `Continuing ${command.project?.title || "the project"}.` : `Opening ${command.project?.title || "the project"}.` };
    case "persona":
      return { command, message: command.persona === "council" ? "Assembling the Council." : `${command.persona} is ready.` };
    case "conversation":
      return { command, message: buildConversationResponse(command) };
    case "observatory":
      return { command, message: "Opening system status." };
    case "projects":
      return { command, message: "Opening your projects." };
    case "mission":
      return { command, message: mission?.title ? `Opening ${mission.title}.` : "Opening the current mission." };
    case "pulse":
      return { command, message: "Opening Pulse." };
    case "awareness":
      return { command, message: "Opening Awareness." };
    case "home":
      return { command, message: "Returning home." };
    default:
      return { command, message: "I did not recognize that command." };
  }
}

export { buildConversationResponse, buildClarificationResponse };
