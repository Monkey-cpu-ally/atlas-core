import { routeVoiceCommand } from "./voiceCommandRouter";

export function buildVoiceCommandResponse(transcript, { projects = [], mission = null } = {}) {
  const command = routeVoiceCommand(transcript, { projects });

  switch (command.type) {
    case "project":
      return { command, message: `Opening ${command.project?.title || "the project"}.` };
    case "current-project":
      return { command, message: command.project ? `Continuing ${command.project.title}.` : "There is no current project to continue." };
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
