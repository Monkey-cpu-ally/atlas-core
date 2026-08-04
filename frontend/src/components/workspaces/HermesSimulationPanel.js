import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Play, Pause, RotateCcw, CheckCircle2, AlertCircle } from 'lucide-react';

function storageKey(projectId) {
  return `atlas.workspace.hermes.simulation.${projectId || 'general'}`;
}

const INITIAL = {
  status: 'idle',
  progress: 0,
  runName: 'Engineering validation run',
  objective: '',
  startedAt: null,
  completedAt: null,
};

const VALID_STATUSES = new Set(['idle', 'running', 'paused', 'complete']);

function cleanText(value, fallback = '', maxLength = 2000) {
  return typeof value === 'string' ? value.slice(0, maxLength) : fallback;
}

function cleanTimestamp(value) {
  if (value === null || value === undefined) return null;
  const timestamp = Number(value);
  return Number.isFinite(timestamp) && timestamp > 0 ? timestamp : null;
}

function sanitizeState(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return { ...INITIAL };
  }

  const progress = Number(value.progress);
  return {
    status: VALID_STATUSES.has(value.status) ? value.status : INITIAL.status,
    progress: Number.isFinite(progress) ? Math.min(100, Math.max(0, progress)) : INITIAL.progress,
    runName: cleanText(value.runName, INITIAL.runName, 160),
    objective: cleanText(value.objective, INITIAL.objective, 4000),
    startedAt: cleanTimestamp(value.startedAt),
    completedAt: cleanTimestamp(value.completedAt),
  };
}

function loadState(projectId) {
  try {
    const stored = window.localStorage?.getItem(storageKey(projectId));
    if (!stored) return { ...INITIAL };
    return sanitizeState(JSON.parse(stored));
  } catch (_) {
    try { window.localStorage?.removeItem(storageKey(projectId)); } catch (_) {}
    return { ...INITIAL };
  }
}

/**
 * HermesSimulationPanel tracks a simulation workflow locally. It does not claim
 * to be a physics solver: the panel prepares, times, pauses and records a run so
 * a real simulation backend can be attached without changing the workspace UI.
 */
export default function HermesSimulationPanel({ project, onStatusChange, onActivity }) {
  const projectId = project?.id || 'general';
  const saved = useMemo(() => loadState(projectId), [projectId]);
  const [run, setRun] = useState(saved);
  const reportedCompletionRef = useRef(saved.completedAt);
  const hydratingProjectRef = useRef(false);

  useEffect(() => {
    const restored = loadState(projectId);
    hydratingProjectRef.current = true;
    reportedCompletionRef.current = restored.completedAt;
    setRun(restored);
  }, [projectId]);

  useEffect(() => {
    // When the selected project changes, this effect first sees the previous
    // project's in-memory run. Skip that write so one project's simulation
    // can never overwrite another project's storage during hydration.
    if (hydratingProjectRef.current) {
      hydratingProjectRef.current = false;
      return;
    }

    try {
      window.localStorage?.setItem(storageKey(projectId), JSON.stringify(run));
    } catch (_) {}
  }, [projectId, run]);

  useEffect(() => {
    onStatusChange?.(run.status === 'running' ? 'simulating' : run.status === 'paused' ? 'paused' : 'ready');
  }, [run.status, onStatusChange]);

  useEffect(() => {
    if (run.status !== 'complete' || !run.completedAt) return;
    if (reportedCompletionRef.current === run.completedAt) return;

    reportedCompletionRef.current = run.completedAt;
    onActivity?.('Simulation workflow completed');
  }, [run.status, run.completedAt, onActivity]);

  useEffect(() => {
    if (run.status !== 'running') return undefined;
    const timer = window.setInterval(() => {
      setRun((current) => {
        const nextProgress = Math.min(100, current.progress + 2);
        if (nextProgress >= 100) {
          return { ...current, status: 'complete', progress: 100, completedAt: Date.now() };
        }
        return { ...current, progress: nextProgress };
      });
    }, 700);
    return () => window.clearInterval(timer);
  }, [run.status]);

  const startOrResume = () => {
    setRun((current) => ({
      ...current,
      status: 'running',
      startedAt: current.startedAt || Date.now(),
      completedAt: null,
    }));
    onActivity?.(run.progress > 0 ? 'Simulation workflow resumed' : 'Simulation workflow started');
  };

  const pause = () => {
    setRun((current) => ({ ...current, status: 'paused' }));
    onActivity?.('Simulation workflow paused');
  };

  const reset = () => {
    setRun({ ...INITIAL, runName: run.runName, objective: run.objective });
    onActivity?.('Simulation workflow reset');
  };

  const etaSeconds = run.status === 'running' ? Math.ceil((100 - run.progress) * 0.35) : null;

  return (
    <section className="hermes-simulation" aria-label="Hermes simulation run manager">
      <div className="hermes-tool-heading">
        <div>
          <span className="hermes-kicker">Simulation workspace</span>
          <h2>{project?.name || 'General engineering run'}</h2>
        </div>
        <span className={`hermes-sim-state is-${run.status}`}>{run.status}</span>
      </div>

      <div className="hermes-sim-disclaimer">
        <AlertCircle size={15} />
        <span>This manages the run workflow and history. A numerical physics solver is not connected yet.</span>
      </div>

      <div className="hermes-sim-fields">
        <label>
          Run name
          <input value={run.runName} onChange={(event) => setRun((current) => ({ ...current, runName: event.target.value }))} />
        </label>
        <label>
          Objective and expected result
          <textarea value={run.objective} onChange={(event) => setRun((current) => ({ ...current, objective: event.target.value }))} placeholder="Describe what Hermes should validate, compare, or measure..." />
        </label>
      </div>

      <div className="hermes-sim-progress" aria-label={`Simulation workflow ${run.progress}% complete`}>
        <div className="hermes-sim-progress-head">
          <strong>{run.progress}%</strong>
          <span>{etaSeconds !== null ? `Estimated ${etaSeconds}s` : run.status === 'complete' ? 'Run recorded' : 'Ready'}</span>
        </div>
        <div className="hermes-sim-track"><span style={{ width: `${run.progress}%` }} /></div>
      </div>

      <div className="hermes-sim-actions">
        {run.status === 'running' ? (
          <button type="button" onClick={pause}><Pause size={15} /> Pause</button>
        ) : (
          <button type="button" onClick={startOrResume} disabled={run.status === 'complete'}><Play size={15} /> {run.progress > 0 ? 'Resume' : 'Start run'}</button>
        )}
        <button type="button" className="secondary" onClick={reset}><RotateCcw size={15} /> Reset</button>
      </div>

      {run.status === 'complete' && (
        <div className="hermes-sim-complete"><CheckCircle2 size={17} /> Workflow complete and saved for this project.</div>
      )}
    </section>
  );
}
