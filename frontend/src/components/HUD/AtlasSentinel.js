/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import { Activity, CircleDot, FolderKanban, RotateCcw, Wifi, WifiOff, X } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const FOCUS_EVENT = 'atlas-ai-focus-mode';
const BRANCH_EVENT = 'atlas-ai-focus-branch';
const PROJECT_EVENT = 'atlas-project-selected';

const PROJECTS = [
  { id: 'weaver', label: 'WEAVER' },
  { id: 'power-cell', label: 'POWER CELL' },
  { id: 'green-bots', label: 'GREEN BOTS' },
  { id: 'hyper-axel', label: 'HYPER AXEL' },
];

function titleCase(value) {
  return String(value || '')
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

/**
 * AtlasSentinel is the small daily-use status ribbon.
 *
 * It stays intentionally quiet: connection, selected AI workspace, active
 * branch, and active project. Knowledge banks and infrastructure remain hidden.
 */
export default function AtlasSentinel() {
  const [enabled, setEnabled] = useState(() => {
    if (typeof window === 'undefined') return true;
    return window.localStorage?.getItem('atlas.status.enabled') !== '0';
  });
  const [connection, setConnection] = useState('checking');
  const [focusAI, setFocusAI] = useState(null);
  const [branch, setBranch] = useState(null);
  const [projectIndex, setProjectIndex] = useState(() => {
    if (typeof window === 'undefined') return 0;
    const saved = Number(window.localStorage?.getItem('atlas.activeProjectIndex'));
    return Number.isInteger(saved) && saved >= 0 && saved < PROJECTS.length ? saved : 0;
  });

  const activeProject = PROJECTS[projectIndex];

  useEffect(() => {
    let cancelled = false;
    let timer;

    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/api/system/health`, {
          headers: { Accept: 'application/json' },
        });
        if (!cancelled) setConnection(response.ok ? 'online' : 'degraded');
      } catch (_) {
        if (!cancelled) setConnection('offline');
      }
    };

    checkHealth();
    timer = window.setInterval(checkHealth, 15000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    const onFocus = (event) => {
      const ai = event.detail?.ai || null;
      setFocusAI(ai);
      if (!ai) setBranch(null);
    };
    const onBranch = (event) => {
      setFocusAI(event.detail?.ai || null);
      setBranch(event.detail?.branch || null);
    };
    window.addEventListener(FOCUS_EVENT, onFocus);
    window.addEventListener(BRANCH_EVENT, onBranch);
    return () => {
      window.removeEventListener(FOCUS_EVENT, onFocus);
      window.removeEventListener(BRANCH_EVENT, onBranch);
    };
  }, []);

  const connectionLabel = useMemo(() => {
    if (connection === 'online') return 'ATLAS ONLINE';
    if (connection === 'degraded') return 'ATLAS DEGRADED';
    if (connection === 'offline') return 'BACKEND OFFLINE';
    return 'CHECKING SYSTEM';
  }, [connection]);

  const persistEnabled = (next) => {
    setEnabled(next);
    try { window.localStorage?.setItem('atlas.status.enabled', next ? '1' : '0'); } catch (_) {}
  };

  const cycleProject = () => {
    const next = (projectIndex + 1) % PROJECTS.length;
    setProjectIndex(next);
    try { window.localStorage?.setItem('atlas.activeProjectIndex', String(next)); } catch (_) {}
    window.dispatchEvent(new CustomEvent(PROJECT_EVENT, { detail: { project: PROJECTS[next] } }));
  };

  if (!enabled) {
    return (
      <button
        type="button"
        className="atlas-sentinel-toggle off"
        onClick={() => persistEnabled(true)}
        title="Show ATLAS status"
        aria-label="Show ATLAS status"
        data-testid="sentinel-toggle"
      >
        STATUS
      </button>
    );
  }

  const statusColor = connection === 'online'
    ? '#6EE7B7'
    : connection === 'degraded'
      ? '#FBBF24'
      : connection === 'offline'
        ? '#F87171'
        : '#94A3B8';

  return (
    <div
      className="atlas-sentinel"
      data-testid="atlas-sentinel"
      aria-label="ATLAS daily status"
      style={{ display: 'flex', alignItems: 'center', gap: 10 }}
    >
      <button
        type="button"
        className="atlas-sentinel-toggle on"
        onClick={() => persistEnabled(false)}
        title="Hide ATLAS status"
        aria-label="Hide ATLAS status"
        data-testid="sentinel-hide"
      >
        <X size={11} />
      </button>

      <span className="atlas-sentinel-label">ATLAS</span>

      <span
        className="atlas-sentinel-chip"
        style={{ '--chip-hue': statusColor, cursor: 'default' }}
        data-testid="atlas-connection-status"
      >
        {connection === 'offline' ? <WifiOff size={11} /> : <Wifi size={11} />}
        <span className="atlas-sentinel-name">{connectionLabel}</span>
      </span>

      <span
        className="atlas-sentinel-chip"
        style={{ '--chip-hue': '#A78BFA', cursor: 'default' }}
        data-testid="atlas-focus-status"
      >
        <CircleDot size={11} />
        <span className="atlas-sentinel-name">
          {focusAI ? titleCase(focusAI === 'trinity' ? 'Council' : focusAI) : 'HOME'}
        </span>
        <span className="atlas-sentinel-readings">
          {branch ? titleCase(branch) : (focusAI ? 'Focus Mode' : 'Three-ring HUD')}
        </span>
      </span>

      <button
        type="button"
        className="atlas-sentinel-chip"
        style={{ '--chip-hue': '#60A5FA' }}
        onClick={cycleProject}
        title="Switch active project"
        data-testid="active-project-switch"
      >
        <FolderKanban size={11} />
        <span className="atlas-sentinel-name">PROJECT</span>
        <span className="atlas-sentinel-readings">{activeProject.label}</span>
        <RotateCcw size={9} />
      </button>

      <span
        className="atlas-sentinel-chip"
        style={{ '--chip-hue': '#67E8F9', cursor: 'default' }}
        title="HUD session is active"
      >
        <Activity size={11} />
        <span className="atlas-sentinel-name">READY</span>
      </span>
    </div>
  );
}
