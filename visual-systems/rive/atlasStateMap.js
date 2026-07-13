export const RIVE_PERSONA_STATE_MAP = Object.freeze({
  ajani: {
    machine: "AjaniStateMachine",
    color: "crimson",
  },
  minerva: {
    machine: "MinervaStateMachine",
    color: "teal",
  },
  hermes: {
    machine: "HermesStateMachine",
    color: "warm-white",
  },
  council: {
    machine: "CouncilStateMachine",
    color: "purple",
  },
  atlas: {
    machine: "AtlasStateMachine",
    color: "blue-white",
  },
});

export const RIVE_STATE_INPUTS = Object.freeze({
  idle: { listening: false, thinking: false, speaking: false, warning: false },
  listening: { listening: true, thinking: false, speaking: false, warning: false },
  thinking: { listening: false, thinking: true, speaking: false, warning: false },
  speaking: { listening: false, thinking: false, speaking: true, warning: false },
  working: { listening: false, thinking: true, speaking: false, warning: false },
  warning: { listening: false, thinking: false, speaking: false, warning: true },
  error: { listening: false, thinking: false, speaking: false, warning: true },
  offline: { listening: false, thinking: false, speaking: false, warning: false },
});

export function applyAtlasEventToRive(riveInstance, envelope) {
  const persona = envelope?.payload?.persona || "atlas";
  const state = envelope?.payload?.state || "idle";
  const config = RIVE_PERSONA_STATE_MAP[persona] || RIVE_PERSONA_STATE_MAP.atlas;
  const values = RIVE_STATE_INPUTS[state] || RIVE_STATE_INPUTS.idle;

  const inputs = riveInstance?.stateMachineInputs?.(config.machine) || [];
  for (const input of inputs) {
    if (Object.prototype.hasOwnProperty.call(values, input.name)) {
      input.value = values[input.name];
    }
    if (input.name === "intensity") {
      input.value = envelope?.payload?.intensity ?? 0.5;
    }
  }

  return { persona, state, machine: config.machine };
}
