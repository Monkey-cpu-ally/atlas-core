/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState, useCallback } from 'react';
import {
  X, GraduationCap, ListTodo, Hammer, FolderKanban, Award, Users, RefreshCw, Loader2,
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const TABS = [
  { id: 'lessons',        label: 'Lessons',       icon: GraduationCap },
  { id: 'queue',          label: 'Research Queue', icon: ListTodo },
  { id: 'blueprints',     label: 'Blueprints',     icon: Hammer },
  { id: 'projects',       label: 'Projects',       icon: FolderKanban },
  { id: 'recommendations',label: 'Council Recs',   icon: Users },
  { id: 'certifications', label: 'Certifications', icon: Award },
];

const STATE_ORDER = [
  'discovered','queued','investigating','analyzed','verified','stored',
  'linked','lesson_generated','blueprint_generated','project_created',
];

export default function LearningHubPanel({ open, onClose }) {
  const [tab, setTab] = useState('lessons');
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async (k) => {
    setLoading(true); setError(null);
    try {
      let url;
      if (k === 'lessons') url = `${API}/api/lessons/generated?limit=40`;
      else if (k === 'queue') url = `${API}/api/research-orch/queue?limit=80`;
      else if (k === 'blueprints') url = `${API}/api/research-orch/blueprints?limit=40`;
      else if (k === 'projects') url = `${API}/api/research-orch/projects?limit=40`;
      else if (k === 'recommendations') url = `${API}/api/research-orch/project-recommendations?limit=40`;
      else if (k === 'certifications') {
        setData((d) => ({ ...d, certifications: { count: 0, items: [], note: 'no certifications collection yet' } }));
        setLoading(false); return;
      }
      const r = await fetch(url);
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      setData((d) => ({ ...d, [k]: j }));
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { if (open) load(tab); }, [open, tab, load]);
  if (!open) return null;

  const block = data[tab] || { items: [] };

  return (
    <div className="lh-shell" data-testid="learning-hub-panel">
      <div className="lh-panel">
        <header className="lh-head">
          <div className="lh-title"><GraduationCap size={16} /><span>Learning Hub · Minerva</span></div>
          <button className="lh-close" onClick={onClose} data-testid="lh-close"><X size={16} /></button>
        </header>

        <nav className="lh-tabs">
          {TABS.map((t) => {
            const Icon = t.icon;
            return (
              <button key={t.id}
                className={`lh-tab ${tab === t.id ? 'active' : ''}`}
                onClick={() => setTab(t.id)}
                data-testid={`lh-tab-${t.id}`}>
                <Icon size={11} /><span>{t.label}</span>
                {data[t.id] && <em>{data[t.id].count}</em>}
              </button>
            );
          })}
          <button className="lh-refresh" onClick={() => load(tab)} disabled={loading} data-testid="lh-refresh">
            {loading ? <Loader2 size={11} className="t-spin" /> : <RefreshCw size={11} />}
          </button>
        </nav>

        {error && <div className="lh-err">{error}</div>}

        <div className="lh-body" data-testid={`lh-body-${tab}`}>
          {block.note && <div className="lh-empty">{block.note}</div>}
          {(block.items || []).length === 0 && !block.note && !loading && (
            <div className="lh-empty">no items in this tab yet</div>
          )}

          {tab === 'lessons' && (block.items || []).map((l) => (
            <article key={l.id} className="lh-card" data-testid={`lh-lesson-${l.id}`}>
              <h4>{l.title}</h4>
              <div className="lh-meta">
                <span>{l.subject || '—'}</span>
                <span>level: {l.skill_level}</span>
                <span>agent: {l.agent}</span>
                {l.profile_bias?.mode && <span>mode: {l.profile_bias.mode}</span>}
              </div>
            </article>
          ))}

          {tab === 'queue' && (block.items || []).map((q) => (
            <article key={q.id} className="lh-card" data-testid={`lh-queue-${q.id}`}>
              <header className="lh-card-head">
                <span className={`lh-state lh-state-${q.state}`}>{q.state}</span>
                <span>{q.domain}</span>
                <span>· {q.agent}</span>
                <span>· conf {(q.evidence?.confidence || 0).toFixed(2)}</span>
                <span>· {q.evidence?.verification_status}</span>
              </header>
              <h4>{q.title}</h4>
              {q.evidence?.evidence_refs?.length > 0 && (
                <details className="lh-evidence"><summary>evidence ({q.evidence.evidence_refs.length})</summary>
                  <pre>{JSON.stringify(q.evidence, null, 2)}</pre></details>
              )}
            </article>
          ))}

          {tab === 'blueprints' && (block.items || []).map((b) => (
            <article key={b.id} className="lh-card" data-testid={`lh-blueprint-${b.id}`}>
              <h4>{b.prototype_suggestion?.name || 'untitled blueprint'}</h4>
              <div className="lh-meta">
                <span>parts: {b.parts_count}</span>
                <span>steps: {b.steps_count}</span>
                <span>risks: {b.risks_count}</span>
                <span>cost: ${b.total_cost_usd || 0}</span>
                <span>agent: {b.agent}</span>
              </div>
            </article>
          ))}

          {tab === 'projects' && (block.items || []).map((p) => (
            <article key={p.id} className="lh-card" data-testid={`lh-project-${p.id}`}>
              <header className="lh-card-head">
                <span className={`lh-state lh-state-${p.status}`}>{p.status}</span>
                <span>{p.agent}</span>
              </header>
              <h4>{p.title}</h4>
              <div className="lh-meta">
                {p.knowledge_id && <span>kb {p.knowledge_id.slice(0,8)}</span>}
                {p.blueprint_id && <span>blueprint {p.blueprint_id.slice(0,8)}</span>}
                {p.lesson_id && <span>lesson {p.lesson_id.slice(0,8)}</span>}
              </div>
            </article>
          ))}

          {tab === 'recommendations' && (block.items || []).map((r) => (
            <article key={r.project_id + r.council_message_id} className="lh-card">
              <h4>Project: {r.project_title}</h4>
              <p>{r.council_reply_excerpt || '(no excerpt)'}</p>
              <div className="lh-meta">
                <span>{r.considered_queue_items?.length || 0} findings considered</span>
                <span>· conf {(r.evidence?.confidence || 0).toFixed(2)}</span>
              </div>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
