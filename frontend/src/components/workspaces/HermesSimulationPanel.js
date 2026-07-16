import React, { useEffect, useMemo, useState } from 'react';
import { Play, Pause, RotateCcw, CheckCircle2, AlertCircle } from 'lucide-react';

function storageKey(projectId) {
  return `atlas.workspace.hermes.simulation.${projectId || 'general'}`;
}

function loadState(projectId) {
  try {
    const stored = window.localStorage?.getItem(storageKey(projectId));
    return stored ? JSON.parse(stored) : null;
  } catch (_) {
    return null;
  }
}

const INITIAL = {
  status: 'idle',
  progress: 0,
  runName: 'Engineering validation run',
  objective: '',
  startedAt: null,
  completedAt: null,
};

/**
 * HermesSimulationPanel tracks a simulation workflow locally. It does not claim
 * to be a physics solver: the panel prepares, times, pauses and records a run so
 * a real simulation backend can be attached without changing the workspace UI.
 */
export default function HermesSimulationPanel({ project, onStatusChange, onActivity }) {
  const projectId = project?.id || 'general';
  const saved = useMemo(() => loadState(projectId), [projectId]);
  const [run, setRun] = useState(saved || INITIAL);

  useEffect(() => {
    setRun(loadState(projectId) || INITIAL);
  }, [projectId]);

  useEffect(() => {
    try {
      window.localStorage?.setItem(storageKey(projectId), JSON.stringify(run));
    } catch (_) {}
  }, [projectId, run]);

  useEffect(() => {
    onStatusChange?.(run.status === 'running' ? 'simulating' : run.status === 'paused' ? 'paused' : 'ready');
  }, [run.status, onStatusChange]);

  useEffect(() => {
    if (run.status !== 'running') return undefined;
    const timer = window.setInterval(() => {
      setRun((current) => {
        const nextProgress = Math.min(100, current.progress + 2);
        if (nextProgress >= 100) {
          const completed = { ...current, status: 'complete', progress: 100, completedAt: Date.now() };
          onActivity?.('Simulation workflow completed');
          return completed;
        }
        return { ...current, progress: nextProgress };
      });
    }, 700);
    return () => window.clearInterval(timer);
  }, [run.status, onActivity]);

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
