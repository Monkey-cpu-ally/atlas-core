import { createSceneManager, SCENES } from "./sceneManager";

export function createGenesisKernel() {
  const sceneManager = createSceneManager();
  const listeners = new Set();
  let snapshot = {
    scene: SCENES.IDLE,
    activePersona: null,
    selectedCapability: null,
    activeMissionId: "genesis-alpha",
    activeProjectId: null,
  };

  function publish() {
    listeners.forEach((listener) => listener(snapshot));
  }

  sceneManager.subscribe(({ next, meta }) => {
    snapshot = { ...snapshot, scene: next, ...meta };
    publish();
  });

  return {
    sceneManager,
    getSnapshot() {
      return snapshot;
    },
    setState(patch) {
      snapshot = { ...snapshot, ...patch };
      publish();
    },
    openPersona(persona) {
      sceneManager.transition(SCENES.AI, { activePersona: persona });
    },
    openMission(missionId = snapshot.activeMissionId) {
      sceneManager.transition(SCENES.MISSION, { activeMissionId: missionId });
    },
    openProjects() {
      sceneManager.transition(SCENES.PROJECTS);
    },
    openPulse() {
      sceneManager.transition(SCENES.PULSE);
    },
    returnIdle() {
      sceneManager.transition(SCENES.IDLE, {
        activePersona: null,
        selectedCapability: null,
        activeProjectId: null,
      });
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}
