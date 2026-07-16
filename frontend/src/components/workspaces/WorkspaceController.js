import React, { useEffect, useState } from 'react';
import HermesWorkspace from './HermesWorkspace';

const FOCUS_EVENT = 'atlas-ai-focus-mode';
const BRANCH_EVENT = 'atlas-ai-focus-branch';
const PROJECT_EVENT = 'atlas-project-selected';

export default function WorkspaceController() {
  const [workspaceAI, setWorkspaceAI] = useState(null);

  useEffect(() => {
    const onFocus = (event) => {
      const ai = event.detail?.ai || null;
      setWorkspaceAI(ai === 'hermes' ? 'hermes' : null);
    };

    const onBranch = (event) => {
      if (event.detail?.ai === 'hermes') setWorkspaceAI('hermes');
    };

    window.addEventListener(FOCUS_EVENT, onFocus);
    window.addEventListener(BRANCH_EVENT, onBranch);
    return () => {
      window.removeEventListener(FOCUS_EVENT, onFocus);
      window.removeEventListener(BRANCH_EVENT, onBranch);
    };
  }, []);

  const closeWorkspace = () => {
    setWorkspaceAI(null);
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
      open={workspaceAI === 'hermes'}
      onClose={closeWorkspace}
      onOpenChat={openHermesChat}
      onOpenProject={openProject}
    />
  );
}
