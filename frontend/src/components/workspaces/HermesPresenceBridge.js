import { useEffect } from 'react';
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

function readStoredStatus() {
  try {
    const saved = JSON.parse(window.localStorage?.getItem(SESSION_KEY) || '{}');
    return saved.hermesStatus || 'ready';
  } catch (_) {
    return 'ready';
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
    const applyInitial = () => applyHermesPresence({ status: readStoredStatus() });
    const onStatus = (event) => {
      if (event.detail?.ai !== 'hermes') return;
      applyHermesPresence(event.detail);
    };

    const timer = window.setTimeout(applyInitial, 0);
    window.addEventListener(STATUS_EVENT, onStatus);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener(STATUS_EVENT, onStatus);
    };
  }, []);

  return null;
}
