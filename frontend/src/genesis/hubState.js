export const HUB_MODES = Object.freeze({
  IDLE: "idle",
  CONVERSATION: "conversation",
  ACTIVE_AI: "active-ai",
  WHEEL: "constellation-wheel",
  PROJECT: "project-workspace",
  COUNCIL: "council",
  ALERT: "awareness-alert",
});

export const initialHubState = Object.freeze({
  mode: HUB_MODES.IDLE,
  activePersona: null,
  visiblePersonas: [],
  selectedNodeId: null,
  activeProjectId: null,
  alert: null,
});

function oneFace(persona) {
  return persona && persona !== "atlas" ? [persona] : [];
}

export function reduceHubState(state, envelope) {
  if (!envelope?.event) return state;
  const payload = envelope.payload || {};
  const persona = payload.persona || state.activePersona;

  switch (envelope.event) {
    case "system.ready":
      return { ...initialHubState };
    case "ai.speech.started":
      return {
        ...state,
        mode: state.mode === HUB_MODES.IDLE ? HUB_MODES.CONVERSATION : state.mode,
        activePersona: persona,
        visiblePersonas: state.mode === HUB_MODES.IDLE ? [] : oneFace(persona),
      };
    case "ai.presence.requested":
      return {
        ...state,
        mode: HUB_MODES.ACTIVE_AI,
        activePersona: persona,
        visiblePersonas: oneFace(persona),
      };
    case "wheel.opened":
      return {
        ...state,
        mode: HUB_MODES.WHEEL,
        activePersona: persona,
        visiblePersonas: oneFace(persona),
        selectedNodeId: payload.node_id || state.selectedNodeId,
      };
    case "wheel.selection.changed":
      return { ...state, selectedNodeId: payload.node_id || null };
    case "project.opened":
      return {
        ...state,
        mode: HUB_MODES.PROJECT,
        activePersona: persona,
        visiblePersonas: oneFace(persona),
        activeProjectId: payload.project_id || null,
      };
    case "council.started":
      return {
        ...state,
        mode: HUB_MODES.COUNCIL,
        activePersona: "council",
        visiblePersonas: ["ajani", "minerva", "hermes"],
      };
    case "council.completed":
      return { ...initialHubState };
    case "awareness.alert.raised":
      return { ...state, mode: HUB_MODES.ALERT, alert: payload };
    case "hud.returned.idle":
      return { ...initialHubState };
    default:
      return state;
  }
}
