export const SCENES = Object.freeze({
  IDLE: "idle",
  AI: "ai",
  WHEEL: "wheel",
  PROJECTS: "projects",
  MISSION: "mission",
  WORKSPACE: "workspace",
  PULSE: "pulse",
  COUNCIL: "council",
  ALERT: "alert",
});

export function createSceneManager(initialScene = SCENES.IDLE) {
  let current = initialScene;
  const listeners = new Set();

  function emit(previous, next, meta) {
    listeners.forEach((listener) => listener({ previous, next, meta }));
  }

  return {
    getCurrent() {
      return current;
    },
    transition(next, meta = {}) {
      if (!Object.values(SCENES).includes(next) || next === current) return current;
      const previous = current;
      current = next;
      emit(previous, next, meta);
      return current;
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}
