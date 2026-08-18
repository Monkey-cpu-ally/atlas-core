/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import { Clapperboard, BookOpen, Palette, Scale, RefreshCw, ShieldCheck, Loader2 } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const STAGES = [
  { id: 'brief', label: 'Brief', icon: BookOpen },
  { id: 'references', label: 'References', icon: Clapperboard },
  { id: 'create', label: 'Create', icon: Palette },
  { id: 'critique', label: 'Critic Council', icon: Scale },
  { id: 'revision', label: 'Revisions', icon: RefreshCw },
  { id: 'master', label: 'Master Gate', icon: ShieldCheck },
];

export default function CreativeStudioPanel({ aiColor, project, onBack }) {
  const [stage, setStage] = useState('brief');
  const [references, setReferences] = useState([]);
  const [critics, setCritics] = useState([]);
  const [rubrics, setRubrics] = useState(null);
  const [qualityContract, setQualityContract] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const title = project?.title || project?.name || 'Untitled Creative Project';
  const summary = project?.summary || project?.description || 'Define the creative brief before production begins.';
  const projectId = String(project?.id || project?._id || title);

  const loadJobs = async () => {
    try {
      const res = await fetch(`${BACKEND}/api/creative-studio/jobs?project_id=${encodeURIComponent(projectId)}`);
      if (!res.ok) throw new Error('jobs');
      const data = await res.json();
      setJobs(data.items || []);
    } catch (_) {}
  };

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch(`${BACKEND}/api/creative-studio/references`).then((r) => { if (!r.ok) throw new Error('references'); return r.json(); }),
      fetch(`${BACKEND}/api/creative-studio/critic-council`).then((r) => { if (!r.ok) throw new Error('critics'); return r.json(); }),
      fetch(`${BACKEND}/api/creative-studio/rubrics`).then((r) => { if (!r.ok) throw new Error('rubrics'); return r.json(); }),
      fetch(`${BACKEND}/api/creative-studio/quality-contract`).then((r) => { if (!r.ok) throw new Error('quality'); return r.json(); }),
      fetch(`${BACKEND}/api/creative-studio/jobs?project_id=${encodeURIComponent(projectId)}`).then((r) => { if (!r.ok) throw new Error('jobs'); return r.json(); }),
    ]).then(([refs, council, quality, contract, jobData]) => {
      if (!active) return;
      setReferences(refs.items || []);
      setCritics(council.critics || []);
      setRubrics(quality);
      setQualityContract(contract);
      setJobs(jobData.items || []);
      setLoading(false);
    }).catch(() => {
      if (!active) return;
      setError('Creative Intelligence API is unavailable.');
      setLoading(false);
    });
    return () => { active = false; };
  }, [projectId]);

  const queueJob = async (jobStage) => {
    try {
      const res = await fetch(`${BACKEND}/api/creative-studio/jobs`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, stage: jobStage }),
      });
      if (!res.ok) throw new Error('queue');
      await loadJobs();
    } catch (_) { setError('Could not queue Creative Studio job.'); }
  };

  const stageData = useMemo(() => STAGES.find((item) => item.id === stage) || STAGES[0], [stage]);
  const StageIcon = stageData.icon;
  const capabilities = qualityContract?.executor_capabilities || {};

  return (
    <div className="bp-workbench" data-testid="creative-studio-panel">
      <div className="bp-actions">{onBack && <button className="bp-btn" onClick={onBack}>← Projects</button>}</div>
      <h3 className="bp-title" style={{ color: aiColor }}><Clapperboard size={15} /> Creative Studio</h3>
      <p className="bp-help">References inform craft; originality, Critic Council review, revisions, and production gates determine whether an asset becomes a master.</p>
      <div className="bp-section"><div className="project-card-label">Project</div><div className="project-card-title">{title}</div><div className="bp-voice-body">{summary}</div></div>
      {loading && <div className="bp-section"><Loader2 size={14} className="spin" /> Loading Creative Intelligence…</div>}
      {error && <div className="bp-section">{error}</div>}

      <div className="bp-actions">
        {STAGES.map(({ id, label, icon: Icon }) => <button key={id} className={`bp-btn ${stage === id ? 'primary' : ''}`} onClick={() => setStage(id)} style={stage === id ? { borderColor: aiColor, color: aiColor } : undefined}><Icon size={12} /> {label}</button>)}
      </div>

      <div className="bp-section">
        <h4 style={{ color: aiColor, display: 'flex', gap: 8 }}><StageIcon size={14} /> {stageData.label}</h4>
        {stage === 'brief' && <p>Lock premise, audience, medium, tone, constraints, story/art bible, and intended emotional effect.</p>}
        {stage === 'references' && <div>{references.slice(0, 20).map((ref) => <div className="project-card" key={ref.id}><div className="project-card-title">{ref.title}</div><div className="project-card-meta">{ref.kind} · {ref.category}</div><div className="bp-voice-body">{(ref.study || []).join(' · ')}</div></div>)}</div>}
        {stage === 'create' && <div><p>Create executor: {capabilities.create ? 'LIVE' : 'LOCKED'}.</p><button className="bp-btn" onClick={() => queueJob('create')}>Queue Create Job</button></div>}
        {stage === 'critique' && <div>{critics.map((critic) => <div className="project-card" key={critic.id}><div className="project-card-title">{critic.id.toUpperCase()}</div><div className="bp-voice-body">{critic.focus}</div></div>)}<button className="bp-btn" onClick={() => queueJob('critique')}>Queue Critique Job</button></div>}
        {stage === 'revision' && <div><p>Revision executor: {capabilities.revision ? 'LIVE' : 'LOCKED'}.</p><button className="bp-btn" onClick={() => queueJob('revision')}>Queue Revision Job</button></div>}
        {stage === 'master' && <div><p>Final master approval requires every applicable quality gate.</p>{rubrics?.quality_principles?.map((p, i) => <div className="bp-voice-body" key={i}>• {p}</div>)}<button className="bp-btn" onClick={() => queueJob('master')}>Queue Master Job</button></div>}
      </div>

      <div className="bp-section" data-testid="creative-job-history">
        <div className="project-card-label">Production Job History</div>
        {jobs.length === 0 && <div className="bp-voice-body">No production jobs recorded for this project.</div>}
        {jobs.map((job) => <div className="project-card" key={job.id}><div className="project-card-title">{job.stage.toUpperCase()} · {job.status.toUpperCase()}</div><div className="project-card-meta">{job.id}</div>{job.blockers?.length > 0 && <div className="bp-voice-body">Blocked: {job.blockers.join(' · ')}</div>}</div>)}
      </div>

      <div className="bp-section"><div className="project-card-label">Integration status</div><div className="bp-voice-body">Job API: {qualityContract?.job_api_enabled ? 'LIVE' : 'LOCKED'} · Create: {capabilities.create ? 'LIVE' : 'LOCKED'} · Critique: {capabilities.critique ? 'LIVE' : 'LOCKED'} · Revision: {capabilities.revision ? 'LIVE' : 'LOCKED'} · Master: {capabilities.master ? 'LIVE' : 'LOCKED'}</div></div>
    </div>
  );
}
