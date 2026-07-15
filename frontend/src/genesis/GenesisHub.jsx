import React, { useCallback, useEffect, useMemo, useReducer, useState } from "react";
import AwarenessAlert from "./AwarenessAlert";
import ConstellationWheel from "./ConstellationWheel";
import PortraitController from "./PortraitController";
import PulsePanel from "./PulsePanel";
import { getCapabilities } from "./capabilityRegistry";
import { createGenesisKernel } from "./core/genesisKernel";
import { SCENES } from "./core/sceneManager";
import DeveloperMode from "./developer/DeveloperMode";
import { initialHubState, reduceHubState, HUB_MODES } from "./hubState";
import MissionDock from "./mission/MissionDock";
import ProjectWall from "./mission/ProjectWall";
import { getMission } from "./mission/missionRegistry";
import { getProjects } from "./mission/projectRegistry";
import { personaTokens } from "./designTokens";
import useAdaptiveQuality from "./useAdaptiveQuality";
import RoboticsWorkspace from "./workspaces/RoboticsWorkspace";
import "./genesis.css";
import "./performance.css";
import "./portrait.css";

const previewModes = [
  { label: "Idle", event: { event: "hud.returned.idle", payload: {} } },
  { label: "Ajani", event: { event: "ai.presence.requested", payload: { persona: "ajani" } } },
  { label: "Minerva", event: { event: "ai.presence.requested", payload: { persona: "minerva" } } },
  { label: "Hermes", event: { event: "ai.presence.requested", payload: { persona: "hermes" } } },
  { label: "Council", event: { event: "council.started", payload: { persona: "council" } } },
  { label: "Pulse", event: { event: "pulse.opened", payload: { persona: "atlas" } } },
];

function withEnvelope(event) {
  return {
    version: "1.0",
    timestamp: new Date().toISOString(),
    source: "genesis-preview",
    ...event,
  };
}

function sceneForHubMode(mode) {
  if (mode === HUB_MODES.PULSE) return SCENES.PULSE;
  if (mode === HUB_MODES.COUNCIL) return SCENES.COUNCIL;
  if (mode === HUB_MODES.ALERT) return SCENES.ALERT;
  if ([HUB_MODES.ACTIVE_AI, HUB_MODES.WHEEL, HUB_MODES.PROJECT].includes(mode)) return SCENES.AI;
  return SCENES.IDLE;
}

export default function GenesisHub({ visualBridge }) {
  const [state, dispatch] = useReducer(reduceHubState, initialHubState);
  const [selectedNode, setSelectedNode] = useState(null);
  const [kernelSnapshot, setKernelSnapshot] = useState(null);
  const [developerMode, setDeveloperMode] = useState(false);
  const kernel = useMemo(() => createGenesisKernel(), []);
  const quality = useAdaptiveQuality();

  useEffect(() => kernel.subscribe(setKernelSnapshot), [kernel]);
  useEffect(() => setKernelSnapshot(kernel.getSnapshot()), [kernel]);

  useEffect(() => {
    if (visualBridge?.lastEvent) dispatch(visualBridge.lastEvent);
  }, [visualBridge?.lastEvent]);

  useEffect(() => {
    if ([SCENES.MISSION, SCENES.PROJECTS, SCENES.WORKSPACE].includes(kernelSnapshot?.scene)) return;
    kernel.sceneManager.transition(sceneForHubMode(state.mode), {
      activePersona: state.activePersona,
      activeProjectId: state.activeProjectId,
    });
  }, [kernel, kernelSnapshot?.scene, state.activePersona, state.activeProjectId, state.mode]);

  useEffect(() => {
    function onKeyDown(event) {
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === "d") {
        event.preventDefault();
        setDeveloperMode((current) => !current);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const persona = kernelSnapshot?.activePersona || state.activePersona || "atlas";
  const tokens = personaTokens[persona] || personaTokens.atlas;
  const nodes = useMemo(() => getCapabilities(persona), [persona]);
  const mission = useMemo(() => getMission(kernelSnapshot?.activeMissionId), [kernelSnapshot?.activeMissionId]);
  const missionProjects = useMemo(() => getProjects(mission?.projectIds), [mission?.projectIds]);
  const activeProject = useMemo(
    () => getProjects(kernelSnapshot?.activeProjectId ? [kernelSnapshot.activeProjectId] : [])[0] || null,
    [kernelSnapshot?.activeProjectId],
  );
  const showWheel = [HUB_MODES.WHEEL, HUB_MODES.PROJECT, HUB_MODES.ACTIVE_AI, HUB_MODES.COUNCIL].includes(state.mode);
  const scene = kernelSnapshot?.scene || SCENES.IDLE;
  const showPulse = scene === SCENES.PULSE;
  const showMission = scene === SCENES.MISSION;
  const showProjects = scene === SCENES.PROJECTS;
  const showWorkspace = scene === SCENES.WORKSPACE;

  useEffect(() => {
    setSelectedNode(null);
  }, [persona]);

  useEffect(() => {
    if (!selectedNode && nodes.length) setSelectedNode(nodes[0]);
  }, [nodes, selectedNode]);

  const selectNode = useCallback((node) => {
    setSelectedNode(node);
    kernel.setState({ selectedCapability: node.id });
    dispatch(withEnvelope({ event: "wheel.selection.changed", payload: { persona, node_id: node.id } }));
  }, [kernel, persona]);

  const selectProject = useCallback((project) => {
    kernel.openWorkspace(project.id, project.persona);
    dispatch(withEnvelope({ event: "project.opened", payload: { persona: project.persona, project_id: project.id } }));
  }, [kernel]);

  const dismissAlert = useCallback(() => {
    dispatch(withEnvelope({ event: "awareness.alert.dismissed", payload: {} }));
  }, []);

  const standardScene = !showPulse && !showMission && !showProjects && !showWorkspace;

  return (
    <main
      className={`genesis-hub genesis-hub--${state.mode}`}
      data-persona={persona}
      data-quality={quality.profile}
      data-scene={scene}
      style={{ "--atlas-accent": tokens.accent }}
    >
      {!quality.reducedEffects ? <div className="genesis-hub__ambient" aria-hidden="true" /> : null}
      <button className="genesis-hub__core" type="button" aria-label="Return ATLAS to idle" onClick={() => kernel.returnIdle()}>
        <span>ATLAS</span>
      </button>

      {showWheel && standardScene && (
        <ConstellationWheel
          nodes={nodes}
          selectedId={selectedNode?.id || state.selectedNodeId}
          onSelect={selectNode}
          accent={tokens.accent}
        />
      )}

      {standardScene && !showWheel && (
        <section className="genesis-hub__workspace" aria-live="polite">
          <p className="genesis-hub__mode">{state.mode}</p>
          <h1>
            {persona === "atlas"
              ? "Quiet and ready"
              : persona === "council"
                ? "Council assembled"
                : `${persona} workspace`}
          </h1>
          <p>
            {persona === "council"
              ? "Ajani, Minerva, and Hermes are present together. Agreements and dissent remain visible."
              : "Voice stays primary. The Hub expands only when the work needs it."}
          </p>
        </section>
      )}

      {showPulse ? <PulsePanel items={state.pulseItems} updatedAt={state.pulseUpdatedAt} /> : null}
      {showMission ? <ProjectWall projects={missionProjects} onSelect={selectProject} /> : null}
      {showProjects ? <ProjectWall projects={getProjects()} onSelect={selectProject} /> : null}
      {showWorkspace ? (
        <RoboticsWorkspace
          project={activeProject}
          onBack={() => kernel.openProjects()}
        />
      ) : null}

      {standardScene ? (
        <PortraitController
          visiblePersonas={state.visiblePersonas}
          activePersona={state.activePersona}
          state={state.speechState}
        />
      ) : null}

      {!showWorkspace ? <MissionDock mission={mission} onOpen={() => kernel.openMission(mission.id)} /> : null}
      <AwarenessAlert alert={state.alert} onDismiss={dismissAlert} />

      <DeveloperMode
        enabled={developerMode}
        onToggle={() => setDeveloperMode((current) => !current)}
        scene={scene}
        persona={persona}
        quality={quality.profile}
        bridgeStatus={visualBridge?.status}
        activeProjectId={kernelSnapshot?.activeProjectId}
      />

      {process.env.NODE_ENV !== "production" ? (
        <nav className="genesis-preview" aria-label="Genesis development preview controls">
          {previewModes.map((item) => (
            <button type="button" key={item.label} onClick={() => dispatch(withEnvelope(item.event))}>
              {item.label}
            </button>
          ))}
          <button type="button" onClick={() => kernel.openProjects()}>Projects</button>
          <button type="button" onClick={() => kernel.openMission()}>Mission</button>
          <button
            type="button"
            onClick={() => dispatch(withEnvelope({
              event: "awareness.alert.raised",
              payload: {
                persona: "ajani",
                title: "The offer is below your stated floor.",
                reason: "The proposed amount is 18% under your minimum target.",
                action: "Do not accept yet. Ask them to justify the reduction.",
                urgency: "high",
              },
            }))}
          >
            Alert
          </button>
        </nav>
      ) : null}

      <div className="genesis-hub__connection">
        Visual bridge: {visualBridge?.status || "offline"} · {quality.profile} · {scene}
      </div>
    </main>
  );
}
