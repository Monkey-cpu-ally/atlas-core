import { routeVoiceCommand } from "./voiceCommandRouter";

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
      return { command, message: "Cancelled." };
    case "project":
      return { command, message: command.contextual ? `Continuing ${command.project?.title || "the project"}.` : `Opening ${command.project?.title || "the project"}.` };
    case "persona":
      return { command, message: command.persona === "council" ? "Assembling the Council." : `${command.persona} is ready.` };
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
