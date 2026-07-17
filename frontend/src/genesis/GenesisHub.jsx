import React, { useCallback, useEffect, useMemo, useReducer, useState } from "react";
import AwarenessAlert from "./AwarenessAlert";
import ConstellationWheel from "./ConstellationWheel";
import PortraitController from "./PortraitController";
import PulsePanel from "./PulsePanel";
import AwarenessCenter from "./awareness/AwarenessCenter";
import { getCapabilities } from "./capabilityRegistry";
import { createGenesisKernel } from "./core/genesisKernel";
import { SCENES } from "./core/sceneManager";
import DeveloperMode from "./developer/DeveloperMode";
import { initialHubState, reduceHubState, HUB_MODES } from "./hubState";
import MinimalHome from "./minimal/MinimalHome";
import ProjectWall from "./mission/ProjectWall";
import { getMission } from "./mission/missionRegistry";
import { getProjects } from "./mission/projectRegistry";
import Observatory from "./observatory/Observatory";
import { githubPulseItemFromEnvelope } from "./pulse/githubPulse";
import useGithubPulseFeed from "./pulse/useGithubPulseFeed";
import { personaTokens } from "./designTokens";
import useAdaptiveQuality from "./useAdaptiveQuality";
import { routeVoiceCommand } from "./voice/voiceCommandRouter";
import AdaptiveWorkspace from "./workspaces/AdaptiveWorkspace";
import "./genesis.css";
import "./performance.css";
import "./portrait.css";
import "./utility-dock.css";

const previewModes = [
  { label: "Idle", event: { event: "hud.returned.idle", payload: {} } },
  { label: "Ajani", event: { event: "ai.presence.requested", payload: { persona: "ajani" } } },
  { label: "Minerva", event: { event: "ai.presence.requested", payload: { persona: "minerva" } } },
  { label: "Hermes", event: { event: "ai.presence.requested", payload: { persona: "hermes" } } },
  { label: "Council", event: { event: "council.started", payload: { persona: "council" } } },
];

function withEnvelope(event) {
  return { version: "1.0", timestamp: new Date().toISOString(), source: "genesis-preview", ...event };
}

function sceneForHubMode(mode) {
  if (mode === HUB_MODES.PULSE) return SCENES.PULSE;
  if (mode === HUB_MODES.AWARENESS) return SCENES.AWARENESS;
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
  const [observatoryOpen, setObservatoryOpen] = useState(false);
  const kernel = useMemo(() => createGenesisKernel(), []);
  const quality = useAdaptiveQuality();
  const githubFeed = useGithubPulseFeed();

  useEffect(() => kernel.subscribe(setKernelSnapshot), [kernel]);
  useEffect(() => setKernelSnapshot(kernel.getSnapshot()), [kernel]);

  useEffect(() => {
    const envelope = visualBridge?.lastEvent;
    if (!envelope) return;
    dispatch(envelope);
    const githubItem = githubPulseItemFromEnvelope(envelope);
    if (githubItem) {
      dispatch({
        event: "pulse.item.received",
        timestamp: envelope.timestamp || new Date().toISOString(),
        payload: { item: githubItem },
      });
    }
  }, [visualBridge?.lastEvent]);

  useEffect(() => {
    if (!githubFeed.updatedAt || !githubFeed.items.length) return;
    githubFeed.items.forEach((item) => dispatch({
      event: "pulse.item.received",
      timestamp: item.occurredAt || githubFeed.updatedAt,
      source: "github-live-provider",
      payload: { item },
    }));
  }, [githubFeed.items, githubFeed.updatedAt]);

  useEffect(() => {
    if ([SCENES.MISSION, SCENES.PROJECTS, SCENES.WORKSPACE, SCENES.AWARENESS].includes(kernelSnapshot?.scene)) return;
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
      if (event.key === "Escape") {
        setObservatoryOpen(false);
        kernel.returnIdle();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [kernel]);

  const persona = kernelSnapshot?.activePersona || state.activePersona || "atlas";
  const tokens = personaTokens[persona] || personaTokens.atlas;
  const nodes = useMemo(() => getCapabilities(persona), [persona]);
  const allProjects = useMemo(() => getProjects(), []);
  const mission = useMemo(() => getMission(kernelSnapshot?.activeMissionId), [kernelSnapshot?.activeMissionId]);
  const missionProjects = useMemo(() => getProjects(mission?.projectIds), [mission?.projectIds]);
  const activeProject = useMemo(
    () => getProjects(kernelSnapshot?.activeProjectId ? [kernelSnapshot.activeProjectId] : [])[0] || null,
    [kernelSnapshot?.activeProjectId],
  );

  const showWheel = [HUB_MODES.WHEEL, HUB_MODES.PROJECT, HUB_MODES.ACTIVE_AI, HUB_MODES.COUNCIL].includes(state.mode);
  const scene = kernelSnapshot?.scene || SCENES.IDLE;
  const showPulse = scene === SCENES.PULSE;
  const showAwareness = scene === SCENES.AWARENESS;
  const showMission = scene === SCENES.MISSION;
  const showProjects = scene === SCENES.PROJECTS;
  const showWorkspace = scene === SCENES.WORKSPACE;
  const standardScene = !showPulse && !showAwareness && !showMission && !showProjects && !showWorkspace;
  const showMinimalHome = standardScene && !showWheel && persona === "atlas" && state.mode === HUB_MODES.IDLE && !observatoryOpen;
  const showObservatory = standardScene && !showWheel && persona === "atlas" && state.mode === HUB_MODES.IDLE && observatoryOpen;

  useEffect(() => setSelectedNode(null), [persona]);
  useEffect(() => {
    if (!selectedNode && nodes.length) setSelectedNode(nodes[0]);
  }, [nodes, selectedNode]);

  const selectNode = useCallback((node) => {
    setSelectedNode(node);
    kernel.setState({ selectedCapability: node.id });
    dispatch(withEnvelope({ event: "wheel.selection.changed", payload: { persona, node_id: node.id } }));
  }, [kernel, persona]);

  const selectProject = useCallback((project) => {
    if (!project?.id) return;
    setObservatoryOpen(false);
    kernel.openWorkspace(project.id, project.persona);
    dispatch(withEnvelope({ event: "project.opened", payload: { persona: project.persona, project_id: project.id } }));
  }, [kernel]);

  const selectPersona = useCallback((personaId) => {
    setObservatoryOpen(false);
    if (personaId === "council") {
      dispatch(withEnvelope({ event: "council.started", payload: { persona: "council" } }));
      return;
    }
    dispatch(withEnvelope({ event: "ai.presence.requested", payload: { persona: personaId } }));
  }, []);

  const dismissAlert = useCallback((id) => {
    dispatch(withEnvelope({ event: "awareness.alert.dismissed", payload: id ? { id } : {} }));
  }, []);

  const handleVoiceCommand = useCallback((commandOrTranscript) => {
    const command = typeof commandOrTranscript === "string"
      ? routeVoiceCommand(commandOrTranscript, { projects: allProjects, currentProject: activeProject })
      : commandOrTranscript;
    if (!command?.type) return;

    dispatch(withEnvelope({
      event: "hud.mode.changed",
      payload: { mode: "voice-command", message: command.transcript, data: command },
    }));

    switch (command.type) {
      case "project":
        selectProject(command.project);
        break;
      case "conversation":
        if (command.project?.id) selectProject(command.project);
        else if (command.persona && command.persona !== "atlas") selectPersona(command.persona);
        break;
      case "persona":
        selectPersona(command.persona);
        break;
      case "observatory":
        kernel.returnIdle();
        setObservatoryOpen(true);
        break;
      case "projects":
        setObservatoryOpen(false);
        kernel.openProjects();
        break;
      case "mission":
        setObservatoryOpen(false);
        kernel.openMission(mission.id);
        break;
      case "pulse":
        setObservatoryOpen(false);
        kernel.openPulse();
        break;
      case "awareness":
        setObservatoryOpen(false);
        kernel.openAwareness();
        break;
      case "home":
        setObservatoryOpen(false);
        kernel.returnIdle();
        dispatch(withEnvelope({ event: "hud.returned.idle", payload: {} }));
        break;
      default:
        dispatch(withEnvelope({
          event: "awareness.alert.raised",
          payload: {
            persona: "atlas",
            title: "Command not recognized",
            reason: command.transcript || "Unknown voice command",
            action: "Try a project name, status, projects, mission, Pulse, Awareness, Ajani, Minerva, Hermes, or Council.",
            urgency: "normal",
          },
        }));
    }
  }, [activeProject, allProjects, kernel, mission.id, selectPersona, selectProject]);

  return (
    <main
      className={`genesis-hub genesis-hub--${state.mode}`}
      data-persona={persona}
      data-quality={quality.profile}
      data-scene={scene}
      data-minimal-home={showMinimalHome ? "true" : "false"}
      style={{ "--atlas-accent": tokens.accent }}
    >
      {!quality.reducedEffects ? <div className="genesis-hub__ambient" aria-hidden="true" /> : null}

      {showMinimalHome ? (
        <MinimalHome
          mission={mission}
          projects={allProjects}
          pulseItems={state.pulseItems}
          awarenessItems={state.awarenessItems}
          bridgeStatus={visualBridge?.status || "offline"}
          onOpenObservatory={() => setObservatoryOpen(true)}
          onOpenMission={() => kernel.openMission(mission.id)}
          onOpenProject={selectProject}
          onSelectPersona={selectPersona}
          onVoiceCommand={handleVoiceCommand}
        />
      ) : (
        <button className="genesis-hub__core" type="button" aria-label="Return ATLAS to idle" onClick={() => { setObservatoryOpen(false); kernel.returnIdle(); }}>
          <span>ATLAS</span>
        </button>
      )}

      {showWheel && standardScene ? (
        <ConstellationWheel nodes={nodes} selectedId={selectedNode?.id || state.selectedNodeId} onSelect={selectNode} accent={tokens.accent} />
      ) : null}

      {showObservatory ? (
        <Observatory
          mission={mission}
          projects={allProjects}
          pulseItems={state.pulseItems}
          awarenessItems={state.awarenessItems}
          bridgeStatus={visualBridge?.status || "offline"}
          onOpenMission={() => kernel.openMission(mission.id)}
          onOpenProjects={() => kernel.openProjects()}
          onOpenPulse={() => kernel.openPulse()}
          onOpenAwareness={() => kernel.openAwareness()}
          onOpenProject={selectProject}
        />
      ) : null}

      {standardScene && !showWheel && !showObservatory && !showMinimalHome ? (
        <section className="genesis-hub__workspace" aria-live="polite">
          <p className="genesis-hub__mode">{state.mode}</p>
          <h1>{persona === "council" ? "Council assembled" : `${persona} workspace`}</h1>
          <p>{persona === "council" ? "Ajani, Minerva, and Hermes are present together. Agreements and dissent remain visible." : "Voice stays primary. The Hub expands only when the work needs it."}</p>
        </section>
      ) : null}

      {showPulse ? <PulsePanel items={state.pulseItems} updatedAt={state.pulseUpdatedAt} /> : null}
      {showAwareness ? <AwarenessCenter alerts={state.awarenessItems} onDismiss={dismissAlert} onSelect={(alert) => dispatch(withEnvelope({ event: "awareness.alert.raised", payload: alert }))} onClose={() => kernel.returnIdle()} /> : null}
      {showMission ? <ProjectWall projects={missionProjects} onSelect={selectProject} /> : null}
      {showProjects ? <ProjectWall projects={allProjects} onSelect={selectProject} /> : null}
      {showWorkspace ? <AdaptiveWorkspace project={activeProject} onBack={() => kernel.openProjects()} /> : null}

      {standardScene && !showObservatory && !showMinimalHome ? <PortraitController visiblePersonas={state.visiblePersonas} activePersona={state.activePersona} state={state.speechState} /> : null}
      {!showAwareness && !showMinimalHome ? <AwarenessAlert alert={state.alert} onDismiss={() => dismissAlert()} /> : null}

      {!showMinimalHome ? (
        <nav className="genesis-utility-dock" aria-label="ATLAS intelligence centers">
          <button type="button" className={showPulse ? "is-active" : ""} onClick={() => kernel.openPulse()}><span>Pulse</span><small>{state.pulseItems.length}</small></button>
          <button type="button" className={showAwareness ? "is-active" : ""} onClick={() => kernel.openAwareness()}><span>Awareness</span><small>{state.awarenessItems.length}</small></button>
        </nav>
      ) : null}

      <DeveloperMode enabled={developerMode} onToggle={() => setDeveloperMode((current) => !current)} scene={scene} />

      {process.env.NODE_ENV !== "production" && developerMode ? (
        <nav className="genesis-preview" aria-label="Genesis development preview controls">
          {previewModes.map((item) => <button type="button" key={item.label} onClick={() => dispatch(withEnvelope(item.event))}>{item.label}</button>)}
          <button type="button" onClick={() => kernel.openProjects()}>Projects</button>
          <button type="button" onClick={() => kernel.openMission()}>Mission</button>
        </nav>
      ) : null}

      {developerMode ? <div className="genesis-hub__connection">Visual bridge: {visualBridge?.status || "offline"} · GitHub: {githubFeed.status} · {quality.profile} · {scene}</div> : null}
    </main>
  );
}
