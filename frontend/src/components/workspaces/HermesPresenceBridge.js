import { useEffect } from 'react';
import { getAllProjects } from '../../data/atlasCore';
import './HermesPresenceBridge.css';

const STATUS_EVENT = 'atlas-ai-status';
const SESSION_KEY = 'atlas.workspace.hermes.v1';

const STATUS_LABELS = {
  ready: 'Ready',
  simulating: 'Simulating',
  paused: 'Paused',
  noting: 'Writing notes',
  blueprinting: 'Blueprinting',
  reviewing: 'Reviewing',
};

function readStoredPresence() {
  try {
    const saved = JSON.parse(window.localStorage?.getItem(SESSION_KEY) || '{}');
    const project = getAllProjects().find((item) => item.id === saved.activeProjectId);
    return {
      status: saved.hermesStatus || 'ready',
      project: project?.name || '',
      section: saved.section || '',
    };
  } catch (_) {
    return { status: 'ready', project: '', section: '' };
  }
}

function applyHermesPresence(detail = {}) {
  const card = document.querySelector('[data-testid="ai-face-hermes"]');
  if (!card) return;

  const status = detail.status || 'ready';
  const label = STATUS_LABELS[status] || status;
  const project = detail.project || '';
  const section = detail.section || '';

  card.dataset.aiStatus = status;
  card.dataset.workspaceSection = section;
  card.setAttribute('aria-label', `Hermes: ${label}${project ? ` on ${project}` : ''}`);
  card.title = `Hermes · ${label}${project ? ` · ${project}` : ''}${section ? ` · ${section}` : ''}`;

  const dot = card.querySelector('.ai-presence-dot');
  if (dot) dot.dataset.aiStatus = status;

  let statusText = card.querySelector('.ai-face-status');
  if (!statusText) {
    statusText = document.createElement('span');
    statusText.className = 'ai-face-status';
    card.appendChild(statusText);
  }
  statusText.textContent = label;
}

export default function HermesPresenceBridge() {
  useEffect(() => {
    let lastSignature = '';

    const syncStoredPresence = () => {
      const presence = readStoredPresence();
      const signature = JSON.stringify(presence);
      if (signature === lastSignature) return;
      lastSignature = signature;
      applyHermesPresence(presence);
    };

    const onStatus = (event) => {
      if (event.detail?.ai !== 'hermes') return;
      lastSignature = '';
      applyHermesPresence(event.detail);
    };

    const timer = window.setTimeout(syncStoredPresence, 0);
    const interval = window.setInterval(syncStoredPresence, 500);
    window.addEventListener(STATUS_EVENT, onStatus);
    window.addEventListener('storage', syncStoredPresence);

    return () => {
      window.clearTimeout(timer);
      window.clearInterval(interval);
      window.removeEventListener(STATUS_EVENT, onStatus);
      window.removeEventListener('storage', syncStoredPresence);
    };
  }, []);

  return null;
}
