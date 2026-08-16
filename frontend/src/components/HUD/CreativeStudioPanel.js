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
  const [status, setStatus] = useState(null);
  const [references, setReferences] = useState([]);
  const [critics, setCritics] = useState([]);
  const [rubrics, setRubrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const title = project?.title || project?.name || 'Untitled Creative Project';
  const summary = project?.summary || project?.description || 'Define the creative brief before production begins.';

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch(`${BACKEND}/api/creative-studio/status`).then((r) => { if (!r.ok) throw new Error('status'); return r.json(); }),
      fetch(`${BACKEND}/api/creative-studio/references?limit=80`).then((r) => { if (!r.ok) throw new Error('references'); return r.json(); }),
      fetch(`${BACKEND}/api/creative-studio/critics`).then((r) => { if (!r.ok) throw new Error('critics'); return r.json(); }),
      fetch(`${BACKEND}/api/creative-studio/rubrics`).then((r) => { if (!r.ok) throw new Error('rubrics'); return r.json(); }),
    ]).then(([s, refs, council, quality]) => {
      if (!active) return;
      setStatus(s);
      setReferences(refs.items || []);
      setCritics(council.critics || []);
      setRubrics(quality);
      setLoading(false);
    }).catch(() => {
      if (!active) return;
      setError('Creative Intelligence API is unavailable.');
      setLoading(false);
    });
    return () => { active = false; };
  }, []);

  const stageData = useMemo(() => STAGES.find((item) => item.id === stage) || STAGES[0], [stage]);
  const StageIcon = stageData.icon;
  const execution = status?.execution || {};

  return (
    <div className="bp-workbench" data-testid="creative-studio-panel">
      <div className="bp-actions">
        {onBack && <button className="bp-btn" onClick={onBack} data-testid="creative-studio-back">← Projects</button>}
      </div>
      <h3 className="bp-title" style={{ color: aiColor }}><Clapperboard size={15} /> Creative Studio</h3>
      <p className="bp-help">ATLAS production workspace. References inform craft; originality, Critic Council review, revisions, and production gates determine whether an asset becomes a master.</p>

      <div className="bp-section" data-testid="creative-project-brief">
        <div className="project-card-label">Project</div>
        <div className="project-card-title">{title}</div>
        <div className="bp-voice-body">{summary}</div>
      </div>

      {loading && <div className="bp-section"><Loader2 size={14} className="spin" /> Loading Creative Intelligence…</div>}
      {error && <div className="bp-section" data-testid="creative-studio-error">{error}</div>}

      <div className="bp-actions" data-testid="creative-stage-nav">
        {STAGES.map(({ id, label, icon: Icon }) => (
          <button key={id} className={`bp-btn ${stage === id ? 'primary' : ''}`} onClick={() => setStage(id)} data-testid={`creative-stage-${id}`} style={stage === id ? { borderColor: aiColor, color: aiColor } : undefined}>
            <Icon size={12} /> {label}
          </button>
        ))}
      </div>

      <div className="bp-section" data-testid={`creative-stage-view-${stage}`}>
        <h4 style={{ color: aiColor, display: 'flex', alignItems: 'center', gap: 8 }}><StageIcon size={14} /> {stageData.label}</h4>

        {stage === 'brief' && <p>Lock premise, audience, medium, tone, constraints, story/art bible, and intended emotional effect.</p>}

        {stage === 'references' && (
          <div data-testid="creative-live-references">
            <p>{references.length} loaded references. Select references by the craft principles ATLAS should study—not by copying protected expression.</p>
            {references.slice(0, 20).map((ref) => (
              <div className="project-card" key={ref.id}>
                <div className="project-card-title">{ref.title}</div>
                <div className="project-card-meta">{ref.kind} · {ref.category}</div>
                <div className="bp-voice-body">{(ref.study || []).join(' · ')}</div>
              </div>
            ))}
          </div>
        )}

        {stage === 'create' && <p>Production execution is {execution.generation_jobs ? 'enabled' : 'locked until a real generation job service is connected'}. The HUD will not represent placeholder output as completed creative work.</p>}

        {stage === 'critique' && (
          <div data-testid="creative-live-critics">
            {(critics || []).map((critic) => (
              <div className="project-card" key={critic.id}>
                <div className="project-card-title">{critic.id.toUpperCase()}</div>
                <div className="bp-voice-body">{critic.focus}</div>
              </div>
            ))}
          </div>
        )}

        {stage === 'revision' && <p>Revision jobs are {execution.revision_jobs ? 'enabled' : 'locked'}. When enabled, rejected work receives explicit revision requests and is re-evaluated rather than silently accepted.</p>}

        {stage === 'master' && (
          <div data-testid="creative-live-master-gate">
            <p>Final master approval requires every applicable quality gate to pass.</p>
            {rubrics?.quality_principles?.map((principle, index) => <div className="bp-voice-body" key={index}>• {principle}</div>)}
            <div className="project-card-meta">Rubrics: {status?.available_rubrics?.join(' · ') || 'loading'}</div>
          </div>
        )}
      </div>

      <div className="bp-section" data-testid="creative-studio-integration-status">
        <div className="project-card-label">Integration status</div>
        <div className="bp-voice-body">
          Reference browsing: {execution.reference_browsing ? 'LIVE' : 'LOCKED'} · Critic contract: {execution.critic_contract ? 'LIVE' : 'LOCKED'} · Generation: {execution.generation_jobs ? 'LIVE' : 'LOCKED'} · Revisions: {execution.revision_jobs ? 'LIVE' : 'LOCKED'} · Master jobs: {execution.master_jobs ? 'LIVE' : 'LOCKED'}
        </div>
      </div>
    </div>
  );
}
