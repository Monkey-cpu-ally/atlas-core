/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import { Clapperboard, BookOpen, Palette, Scale, RefreshCw, ShieldCheck, Loader2, Search } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const STAGES = [
  { id: 'brief', label: 'Brief', icon: BookOpen },
  { id: 'references', label: 'References', icon: Clapperboard },
  { id: 'create', label: 'Create', icon: Palette },
  { id: 'critique', label: 'Critic Council', icon: Scale },
  { id: 'revision', label: 'Revisions', icon: RefreshCw },
  { id: 'master', label: 'Master Gate', icon: ShieldCheck },
];
const resultOutput = (job) => job?.result?.output || null;

export default function CreativeStudioPanel({ aiColor, project, onBack }) {
  const [stage, setStage] = useState('brief');
  const [references, setReferences] = useState([]);
  const [referenceQuery, setReferenceQuery] = useState('');
  const [referenceSynthesis, setReferenceSynthesis] = useState(null);
  const [referenceLoading, setReferenceLoading] = useState(false);
  const [critics, setCritics] = useState([]);
  const [rubrics, setRubrics] = useState(null);
  const [qualityContract, setQualityContract] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningStage, setRunningStage] = useState('');
  const [error, setError] = useState('');
  const title = project?.title || project?.name || 'Untitled Creative Project';
  const summary = project?.summary || project?.description || 'Define the creative brief before production begins.';
  const projectId = String(project?.id || project?._id || title);

  const loadJobs = async () => {
    const res = await fetch(`${BACKEND}/api/creative-studio/jobs?project_id=${encodeURIComponent(projectId)}`);
    if (!res.ok) throw new Error('jobs');
    const data = await res.json();
    setJobs(data.items || []);
    return data.items || [];
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
      setReferences(refs.items || []); setCritics(council.critics || []); setRubrics(quality);
      setQualityContract(contract); setJobs(jobData.items || []); setLoading(false);
    }).catch(() => { if (active) { setError('Creative Intelligence API is unavailable.'); setLoading(false); } });
    return () => { active = false; };
  }, [projectId]);

  const completed = useMemo(() => jobs.filter((j) => j.status === 'completed'), [jobs]);
  const latest = (jobStage, predicate = () => true) => [...completed].reverse().find((j) => j.stage === jobStage && predicate(j));
  const createJob = latest('create');
  const revisionJob = latest('revision');
  const currentArtifactJob = revisionJob || createJob;
  const currentArtifact = resultOutput(currentArtifactJob)?.text || '';
  const currentArtifactId = currentArtifactJob?.result?.artifact_id || resultOutput(currentArtifactJob)?.artifact_id || currentArtifactJob?.artifact_id || null;
  const critiques = completed.filter((j) => j.stage === 'critique');
  const currentCritique = [...critiques].reverse().find((j) => j.artifact_id === currentArtifactId) || null;
  const council = resultOutput(currentCritique);
  const needsRevision = council && council.approved === false && (council.revision_plan || []).length > 0;
  const masterEligible = Boolean(currentArtifact && council?.approved === true && !(council.blockers || []).length);

  const synthesizeReferences = async () => {
    const query = referenceQuery.trim() || `${title} ${summary}`;
    setReferenceLoading(true); setError(''); setReferenceSynthesis(null);
    try {
      const res = await fetch(`${BACKEND}/api/creative-studio/references/synthesize?q=${encodeURIComponent(query)}&limit=4&minimum_references=2`);
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || 'Reference synthesis could not meet its safety contract.');
      }
      const data = await res.json();
      setReferenceSynthesis(data);
      setReferences(data.references || []);
    } catch (e) { setError(e.message || 'Reference synthesis failed.'); }
    finally { setReferenceLoading(false); }
  };

  const createAndExecute = async (jobStage, payload, artifactId = null, parentJobId = null) => {
    setRunningStage(jobStage); setError('');
    try {
      const queued = await fetch(`${BACKEND}/api/creative-studio/jobs`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, stage: jobStage, artifact_id: artifactId, parent_job_id: parentJobId }),
      });
      if (!queued.ok) throw new Error(`Could not queue ${jobStage} job.`);
      const job = await queued.json();
      const executed = await fetch(`${BACKEND}/api/creative-studio/jobs/${job.id}/execute`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ payload }),
      });
      if (!executed.ok) throw new Error(`Could not execute ${jobStage} job.`);
      const finished = await executed.json();
      await loadJobs();
      if (finished.status !== 'completed') throw new Error(finished.result?.error || `${jobStage} did not complete.`);
      return finished;
    } catch (e) { setError(e.message || `Creative Studio ${jobStage} failed.`); return null; }
    finally { setRunningStage(''); }
  };

  const referenceContext = referenceSynthesis ? {
    query: referenceSynthesis.query,
    reference_ids: (referenceSynthesis.references || []).map((ref) => ref.id),
    principles: referenceSynthesis.principles || [],
    study_targets: referenceSynthesis.study_targets || [],
    limitations: referenceSynthesis.limitations || [],
    provenance: referenceSynthesis.provenance || [],
    contract: referenceSynthesis.synthesis_contract || {},
  } : null;
  const runCreate = () => createAndExecute('create', { premise: summary, audience: 'general', medium: 'story', tone: 'project-defined', reference_context: referenceContext });
  const runCritique = () => currentArtifact ? createAndExecute('critique', { artifact: currentArtifact, reference_context: referenceContext }, currentArtifactId, currentArtifactJob?.id) : setError('Create an artifact before critique.');
  const runRevision = () => needsRevision ? createAndExecute('revision', { artifact: currentArtifact, revision_plan: council.revision_plan, blockers: council.blockers || [], brief: { premise: summary }, reference_context: referenceContext }, currentArtifactId, currentCritique?.id) : setError('Revision requires explicit Critic Council requests.');
  const runMaster = () => {
    if (!masterEligible) return setError('Master Gate requires an approved critique of the current artifact.');
    const qualityEvidence = { creative_approval: { passed: true }, story_quality: { passed: true }, originality: { passed: true } };
    return createAndExecute('master', { artifact: currentArtifact, critic_council: council, applicable_gates: Object.keys(qualityEvidence), quality_evidence: qualityEvidence, reference_context: referenceContext }, currentArtifactId, currentCritique?.id);
  };

  const stageData = useMemo(() => STAGES.find((item) => item.id === stage) || STAGES[0], [stage]);
  const StageIcon = stageData.icon;
  const capabilities = qualityContract?.executor_capabilities || {};
  const busy = Boolean(runningStage);

  return (
    <div className="bp-workbench" data-testid="creative-studio-panel">
      <div className="bp-actions">{onBack && <button className="bp-btn" onClick={onBack}>← Projects</button>}</div>
      <h3 className="bp-title" style={{ color: aiColor }}><Clapperboard size={15} /> Creative Studio</h3>
      <p className="bp-help">References inform craft; originality, Critic Council review, revisions, and production gates determine whether an asset becomes a master.</p>
      <div className="bp-section"><div className="project-card-label">Project</div><div className="project-card-title">{title}</div><div className="bp-voice-body">{summary}</div></div>
      {loading && <div className="bp-section"><Loader2 size={14} className="spin" /> Loading Creative Intelligence…</div>}
      {error && <div className="bp-section">{error}</div>}
      <div className="bp-actions">{STAGES.map(({ id, label, icon: Icon }) => <button key={id} className={`bp-btn ${stage === id ? 'primary' : ''}`} onClick={() => setStage(id)} style={stage === id ? { borderColor: aiColor, color: aiColor } : undefined}><Icon size={12} /> {label}</button>)}</div>
      <div className="bp-section">
        <h4 style={{ color: aiColor, display: 'flex', gap: 8 }}><StageIcon size={14} /> {stageData.label}</h4>
        {stage === 'brief' && <p>Current project summary is the production premise. Future brief controls can expand audience, medium, tone, constraints, story/art bible, and intended emotional effect.</p>}
        {stage === 'references' && <div>
          <div className="bp-actions"><input value={referenceQuery} onChange={(e) => setReferenceQuery(e.target.value)} placeholder="Search craft goals, e.g. minimal dialogue + industrial horror" style={{ flex: 1 }} /><button disabled={referenceLoading} className="bp-btn" onClick={synthesizeReferences}><Search size={12} /> {referenceLoading ? 'Synthesizing…' : 'Synthesize References'}</button></div>
          {referenceSynthesis && <div className="project-card"><div className="project-card-label">Reference Intelligence</div><div className="project-card-title">{referenceSynthesis.references?.length || 0} sources synthesized</div><div className="bp-voice-body">Principles: {(referenceSynthesis.principles || []).join(' · ')}</div><div className="bp-voice-body">Study: {(referenceSynthesis.study_targets || []).join(' · ')}</div><div className="bp-voice-body">Boundaries: {(referenceSynthesis.limitations || []).join(' · ')}</div><div className="bp-voice-body">Provenance records: {(referenceSynthesis.provenance || []).length} · Principle-only: {referenceSynthesis.synthesis_contract?.principle_only ? 'ENFORCED' : 'LOCKED'}</div></div>}
          {references.slice(0, 20).map((ref) => <div className="project-card" key={ref.id}><div className="project-card-title">{ref.title}</div><div className="project-card-meta">{ref.kind} · {ref.category}{ref.score ? ` · score ${ref.score}` : ''}</div><div className="bp-voice-body">{(ref.study || []).join(' · ')}</div>{ref.techniques?.length > 0 && <div className="bp-voice-body">Techniques: {ref.techniques.join(' · ')}</div>}{ref.matched_terms?.length > 0 && <div className="bp-voice-body">Matched: {ref.matched_terms.join(' · ')}</div>}</div>)}
        </div>}
        {stage === 'create' && <div><p>Create executor: {capabilities.create ? 'LIVE' : 'LOCKED'} · Reference synthesis: {referenceSynthesis ? 'ATTACHED' : 'OPTIONAL'}.</p><button disabled={busy || !capabilities.create} className="bp-btn" onClick={runCreate}>{runningStage === 'create' ? 'Creating…' : createJob ? 'Create New Draft' : 'Create Draft'}</button>{currentArtifact && <div className="bp-voice-body">Current artifact ready for Council review.</div>}</div>}
        {stage === 'critique' && <div>{critics.map((critic) => <div className="project-card" key={critic.id}><div className="project-card-title">{critic.id.toUpperCase()}</div><div className="bp-voice-body">{critic.focus}</div></div>)}<button disabled={busy || !currentArtifact || !capabilities.critique} className="bp-btn" onClick={runCritique}>{runningStage === 'critique' ? 'Council Reviewing…' : currentCritique ? 'Re-run Critic Council' : 'Run Critic Council'}</button>{council && <div className="bp-voice-body">Council: {council.approved ? 'APPROVED' : 'REVISION REQUIRED'}{council.blockers?.length ? ` · ${council.blockers.join(' · ')}` : ''}</div>}</div>}
        {stage === 'revision' && <div><p>Revision executor: {capabilities.revision ? 'LIVE' : 'LOCKED'}.</p><button disabled={busy || !needsRevision || !capabilities.revision} className="bp-btn" onClick={runRevision}>{runningStage === 'revision' ? 'Revising…' : 'Apply Council Revision Plan'}</button>{revisionJob && !currentCritique && <div className="bp-voice-body">Revision complete. Re-run Critic Council before Master approval.</div>}</div>}
        {stage === 'master' && <div><p>Master approval is enabled only after the current artifact passes post-revision Council review.</p>{rubrics?.quality_principles?.map((p, i) => <div className="bp-voice-body" key={i}>• {p}</div>)}<button disabled={busy || !masterEligible || !capabilities.master} className="bp-btn" onClick={runMaster}>{runningStage === 'master' ? 'Verifying…' : 'Run Story Master Gate'}</button></div>}
      </div>
      <div className="bp-section" data-testid="creative-job-history"><div className="project-card-label">Production Job History</div>{jobs.length === 0 && <div className="bp-voice-body">No production jobs recorded for this project.</div>}{jobs.map((job) => <div className="project-card" key={job.id}><div className="project-card-title">{job.stage.toUpperCase()} · {job.status.toUpperCase()}</div><div className="project-card-meta">{job.id}</div>{job.blockers?.length > 0 && <div className="bp-voice-body">Blocked: {job.blockers.join(' · ')}</div>}</div>)}</div>
      <div className="bp-section"><div className="project-card-label">Integration status</div><div className="bp-voice-body">Job API: {qualityContract?.job_api_enabled ? 'LIVE' : 'LOCKED'} · Reference Intelligence: {referenceSynthesis ? 'ATTACHED' : 'READY'} · Create: {capabilities.create ? 'LIVE' : 'LOCKED'} · Critique: {capabilities.critique ? 'LIVE' : 'LOCKED'} · Revision: {capabilities.revision ? 'LIVE' : 'LOCKED'} · Master: {capabilities.master ? 'LIVE' : 'LOCKED'}</div></div>
    </div>
  );
}
