export const HUB_MODES = Object.freeze({
  IDLE: "idle",
  CONVERSATION: "conversation",
  ACTIVE_AI: "active-ai",
  WHEEL: "constellation-wheel",
  PROJECT: "project-workspace",
  COUNCIL: "council",
  PULSE: "pulse",
  AWARENESS: "awareness-center",
  ALERT: "awareness-alert",
});

export const initialHubState = Object.freeze({
  mode: HUB_MODES.IDLE,
  activePersona: null,
  visiblePersonas: [],
  selectedNodeId: null,
  activeProjectId: null,
  speechState: "idle",
  pulseItems: [],
  pulseUpdatedAt: null,
  alert: null,
  awarenessItems: [],
});

function oneFace(persona) {
  return persona && !["atlas", "council"].includes(persona) ? [persona] : [];
}

function normalizeAlert(payload, envelope) {
  return {
    id: payload.id || `alert-${envelope.timestamp || Date.now()}`,
    createdAt: envelope.timestamp || new Date().toISOString(),
    ...payload,
  };
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
        speechState: "speaking",
        visiblePersonas: state.mode === HUB_MODES.IDLE ? [] : oneFace(persona),
      };
    case "ai.speech.ended":
      return { ...state, speechState: "idle" };
    case "ai.state.changed":
      return { ...state, speechState: payload.state || state.speechState };
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
    case "pulse.opened":
      return {
        ...state,
        mode: HUB_MODES.PULSE,
        activePersona: persona || "atlas",
        visiblePersonas: oneFace(persona),
      };
    case "pulse.updated":
      return {
        ...state,
        pulseItems: Array.isArray(payload.items) ? payload.items : state.pulseItems,
        pulseUpdatedAt: envelope.timestamp || payload.updated_at || new Date().toISOString(),
      };
    case "awareness.opened":
      return { ...state, mode: HUB_MODES.AWARENESS };
    case "council.started":
      return {
        ...state,
        mode: HUB_MODES.COUNCIL,
        activePersona: "council",
        visiblePersonas: ["ajani", "minerva", "hermes"],
      };
    case "council.completed":
      return { ...initialHubState };
    case "awareness.alert.raised": {
      const alert = normalizeAlert(payload, envelope);
      return {
        ...state,
        mode: HUB_MODES.ALERT,
        alert,
        awarenessItems: [alert, ...state.awarenessItems.filter((item) => item.id !== alert.id)].slice(0, 50),
      };
    }
    case "awareness.alert.dismissed": {
      const dismissedId = payload.id || state.alert?.id;
      return {
        ...state,
        mode: state.mode === HUB_MODES.AWARENESS ? HUB_MODES.AWARENESS : state.activePersona ? HUB_MODES.ACTIVE_AI : HUB_MODES.IDLE,
        alert: state.alert?.id === dismissedId ? null : state.alert,
        awarenessItems: dismissedId ? state.awarenessItems.filter((item) => item.id !== dismissedId) : state.awarenessItems,
      };
    }
    case "hud.returned.idle":
      return { ...initialHubState, pulseItems: state.pulseItems, pulseUpdatedAt: state.pulseUpdatedAt, awarenessItems: state.awarenessItems };
    default:
      return state;
  }
}
