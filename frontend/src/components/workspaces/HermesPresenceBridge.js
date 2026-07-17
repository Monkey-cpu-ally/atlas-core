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

const VALID_SECTIONS = new Set([
  'dashboard',
  'projects',
  'blueprints',
  'notebook',
  'simulation',
  'tasks',
]);

function cleanText(value, maxLength = 120) {
  return typeof value === 'string' ? value.trim().slice(0, maxLength) : '';
}

function sanitizePresence(detail = {}) {
  const status = Object.prototype.hasOwnProperty.call(STATUS_LABELS, detail.status)
    ? detail.status
    : 'ready';

  return {
    status,
    project: cleanText(detail.project),
    section: VALID_SECTIONS.has(detail.section) ? detail.section : '',
  };
}

function readStoredPresence() {
  try {
    const saved = JSON.parse(window.localStorage?.getItem(SESSION_KEY) || '{}');
    const project = getAllProjects().find((item) => item.id === saved.activeProjectId);
    return sanitizePresence({
      status: saved.hermesStatus,
      project: project?.name || '',
      section: saved.section,
    });
  } catch (_) {
    return sanitizePresence();
  }
}

function applyHermesPresence(detail = {}) {
  const card = document.querySelector('[data-testid="ai-face-hermes"]');
  if (!card) return false;

  const { status, project, section } = sanitizePresence(detail);
  const label = STATUS_LABELS[status];

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
  return true;
}

export default function HermesPresenceBridge() {
  useEffect(() => {
    let lastSignature = '';

    const syncStoredPresence = () => {
      const presence = readStoredPresence();
      const signature = JSON.stringify(presence);
      if (signature === lastSignature) return;

      // Only mark the state as applied after the Hermes card actually exists.
      // This lets later interval ticks retry during HUD startup or remounts.
      if (applyHermesPresence(presence)) {
        lastSignature = signature;
      }
    };

    const onStatus = (event) => {
      if (event.detail?.ai !== 'hermes') return;
      const presence = sanitizePresence(event.detail);
      if (applyHermesPresence(presence)) {
        lastSignature = JSON.stringify(presence);
      } else {
        lastSignature = '';
      }
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
