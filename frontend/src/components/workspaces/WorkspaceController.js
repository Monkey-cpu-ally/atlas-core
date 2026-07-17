import React, { useEffect, useState } from 'react';
import HermesWorkspace from './HermesWorkspace';
import './WorkspaceDock.css';

const FOCUS_EVENT = 'atlas-ai-focus-mode';
const BRANCH_EVENT = 'atlas-ai-focus-branch';
const PROJECT_EVENT = 'atlas-project-selected';

const HERMES_BRANCH_ROUTES = {
  engineering: 'dashboard',
  robotics: 'projects',
  software: 'tasks',
  manufacturing: 'projects',
  architecture: 'blueprints',
  systems: 'simulation',
};

export default function WorkspaceController() {
  const [workspaceAI, setWorkspaceAI] = useState(null);
  const [workspaceRequest, setWorkspaceRequest] = useState(null);
  const hermesOpen = workspaceAI === 'hermes';

  useEffect(() => {
    const onFocus = (event) => {
      const ai = event.detail?.ai || null;
      if (ai === 'hermes') {
        // A normal Hermes focus request should open the saved/default workspace,
        // not replay a stale specialized branch request from an earlier session.
        setWorkspaceRequest(null);
        setWorkspaceAI('hermes');
        return;
      }
      setWorkspaceAI(null);
      setWorkspaceRequest(null);
    };

    const onBranch = (event) => {
      if (event.detail?.ai !== 'hermes') return;
      const branch = event.detail?.branch || 'engineering';
      setWorkspaceAI('hermes');
      setWorkspaceRequest({
        branch,
        section: HERMES_BRANCH_ROUTES[branch] || 'dashboard',
        requestId: Date.now(),
      });
    };

    window.addEventListener(FOCUS_EVENT, onFocus);
    window.addEventListener(BRANCH_EVENT, onBranch);
    return () => {
      window.removeEventListener(FOCUS_EVENT, onFocus);
      window.removeEventListener(BRANCH_EVENT, onBranch);
    };
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    const hud = document.querySelector('.atlas-container');

    root.classList.toggle('atlas-workspace-docked', hermesOpen);
    hud?.classList.toggle('workspace-docked', hermesOpen);

    return () => {
      root.classList.remove('atlas-workspace-docked');
      hud?.classList.remove('workspace-docked');
    };
  }, [hermesOpen]);

  const closeWorkspace = () => {
    setWorkspaceAI(null);
    setWorkspaceRequest(null);
    window.dispatchEvent(new CustomEvent(FOCUS_EVENT, { detail: { ai: null } }));
  };

  const openHermesChat = () => {
    const card = document.querySelector('[data-testid="ai-face-hermes"]');
    card?.dispatchEvent(new MouseEvent('dblclick', {
      bubbles: true,
      cancelable: true,
      view: window,
    }));
  };

  const openProject = (project) => {
    window.dispatchEvent(new CustomEvent(PROJECT_EVENT, {
      detail: { project: { id: project.id, label: project.name } },
    }));
  };

  return (
    <HermesWorkspace
      open={hermesOpen}
      requestedSection={workspaceRequest?.section || null}
      requestedBranch={workspaceRequest?.branch || null}
      requestId={workspaceRequest?.requestId || 0}
      onClose={closeWorkspace}
      onOpenChat={openHermesChat}
      onOpenProject={openProject}
    />
  );
}
