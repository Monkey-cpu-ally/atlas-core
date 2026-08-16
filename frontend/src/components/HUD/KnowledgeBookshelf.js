/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import { BookOpen, Search, Loader2, RefreshCw, ExternalLink, GraduationCap, MessageCircle, Sparkles } from 'lucide-react';
import './KnowledgeBookshelf.css';

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const SUBJECT_COLORS = ['#b23a48','#386641','#31587a','#7b2cbf','#bc6c25','#2a9d8f','#9b2226','#5f6f52','#3a5a40','#6d597a','#457b9d','#8d6e63'];
const PERSONAS = [
  { id: 'ajani', label: 'Ask Ajani', color: '#F03246' },
  { id: 'minerva', label: 'Ask Minerva', color: '#28C8BE' },
  { id: 'hermes', label: 'Ask Hermes', color: '#F4EFE4' },
];

const normalizeList = (data, keys = []) => {
  if (Array.isArray(data)) return data;
  for (const key of keys) if (Array.isArray(data?.[key])) return data[key];
  return [];
};

export default function KnowledgeBookshelf({ aiColor }) {
  const [subjects, setSubjects] = useState([]);
  const [resources, setResources] = useState([]);
  const [subject, setSubject] = useState('all');
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true); setError('');
    Promise.all([
      fetch(`${BACKEND}/api/kbase/subjects`).then(async r => { if (!r.ok) throw new Error(`subjects ${r.status}`); return r.json(); }),
      fetch(`${BACKEND}/api/kbase/resources`).then(async r => { if (!r.ok) throw new Error(`resources ${r.status}`); return r.json(); }),
    ]).then(([subjectData, resourceData]) => {
      if (cancelled) return;
      setSubjects(normalizeList(subjectData, ['subjects','items','data']));
      setResources(normalizeList(resourceData, ['resources','items','data']));
    }).catch(e => { if (!cancelled) setError(e.message || 'Knowledge Bank unavailable'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [reloadKey]);

  const subjectId = s => String(s?.id || s?.slug || s?.name || s || '').toLowerCase();
  const subjectName = s => s?.name || s?.label || s?.title || s;
  const colorForSubject = value => {
    const key = String(value || 'atlas').toLowerCase();
    let hash = 0; for (let i = 0; i < key.length; i += 1) hash = ((hash << 5) - hash) + key.charCodeAt(i);
    return SUBJECT_COLORS[Math.abs(hash) % SUBJECT_COLORS.length];
  };
  const resourceSubject = r => String(r.subject || r.subject_id || r.domain || 'General');

  const filtered = useMemo(() => resources.filter(r => {
    const rSubject = resourceSubject(r).toLowerCase();
    const haystack = `${r.title || ''} ${r.author || ''} ${r.summary || ''} ${r.source || ''}`.toLowerCase();
    return (subject === 'all' || rSubject === subject) && (!query.trim() || haystack.includes(query.trim().toLowerCase()));
  }), [resources, subject, query]);

  const personaAction = (persona) => {
    window.dispatchEvent(new CustomEvent('atlas-knowledge-question', { detail: { persona, resource: selected } }));
  };
  const teachAction = () => {
    window.dispatchEvent(new CustomEvent('atlas-teach-resource', { detail: { resource: selected } }));
  };

  if (selected) {
    const accent = colorForSubject(resourceSubject(selected));
    return <div className="knowledge-bookshelf kb-reading-room" data-testid="knowledge-resource-detail">
      <button className="bp-btn" onClick={() => setSelected(null)}>← Return to bookshelf</button>
      <article className="kb-open-book" style={{ '--subject-accent': accent }}>
        <section className="kb-page kb-page-left">
          <div className="kb-bookmark" />
          <div className="kb-kicker">{resourceSubject(selected)}</div>
          <div className="kb-detail-type">{selected.type || selected.resource_type || 'KNOWLEDGE RESOURCE'}</div>
          <h2>{selected.title || 'Untitled resource'}</h2>
          {selected.author && <div className="kb-byline">by {selected.author}</div>}
          <div className="kb-source-seal">ATLAS VERIFIED SOURCE</div>
        </section>
        <section className="kb-page kb-page-right">
          <h3>Research Notes</h3>
          <p>{selected.summary || selected.description || 'No summary is available yet. ATLAS can research this resource further.'}</p>
          <div className="kb-meta">Source: {selected.source || selected.provider || 'ATLAS Knowledge Bank'}</div>
          <div className="kb-reader-actions">
            <button className="kb-action primary" onClick={teachAction} style={{ borderColor: aiColor }}><GraduationCap size={13}/> Teach Me</button>
            {PERSONAS.map(p => <button key={p.id} className="kb-action" onClick={() => personaAction(p.id)} style={{ borderColor: p.color, color: p.color }}><MessageCircle size={12}/> {p.label}</button>)}
            {selected.url && <a className="kb-action" href={selected.url} target="_blank" rel="noreferrer"><ExternalLink size={12}/> Open source</a>}
          </div>
          <div className="kb-action-note"><Sparkles size={11}/> AI actions are emitted through the HUD event bus for workspace integration.</div>
        </section>
      </article>
    </div>;
  }

  return <div className="knowledge-bookshelf" data-testid="knowledge-bookshelf">
    <div className="kb-header"><div><div className="kb-kicker">ATLAS RESEARCH ARCHIVE</div><h3 style={{ color: aiColor }}><BookOpen size={15}/> Knowledge Bookshelf</h3><p>Twenty-two disciplines organized as a living engineering library.</p></div><button className="bp-btn" onClick={() => setReloadKey(n => n + 1)} title="Refresh bookshelf"><RefreshCw size={12}/></button></div>
    <label className="kb-search"><Search size={13}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search books, papers, topics, inventors, authors…"/></label>
    <div className="kb-subject-tabs" aria-label="Knowledge subjects">
      <button className={`kb-tab ${subject === 'all' ? 'active' : ''}`} onClick={() => setSubject('all')} style={subject === 'all' ? { borderColor: aiColor, color: aiColor } : undefined}>ALL SHELVES</button>
      {subjects.map(s => { const id = subjectId(s); const c = colorForSubject(id); return <button key={id} className={`kb-tab ${subject === id ? 'active' : ''}`} onClick={() => setSubject(id)} style={{ '--tab-color': c, ...(subject === id ? { borderColor: c, color: c } : {}) }}><span className="kb-tab-mark"/>{subjectName(s)}</button>; })}
    </div>
    {loading && <div className="kb-state"><Loader2 size={15} className="spin"/> Loading Knowledge Bank…</div>}
    {!loading && error && <div className="kb-state kb-error">Knowledge Bank unavailable: {error}</div>}
    {!loading && !error && filtered.length === 0 && <div className="kb-state">No resources match this shelf yet.</div>}
    {!loading && !error && filtered.length > 0 && <div className="kb-library-wall">{filtered.map((r,i) => { const c = colorForSubject(resourceSubject(r)); return <button key={r.id || r.resource_id || `${r.title}-${i}`} className="kb-volume" onClick={() => setSelected(r)} style={{ '--book-accent': c }} title={`Open ${r.title || 'resource'}`}><span className="kb-volume-band"/><span className="kb-volume-type">{r.type || r.resource_type || 'REFERENCE'}</span><strong>{r.title || 'Untitled resource'}</strong><span className="kb-volume-author">{r.author || r.provider || resourceSubject(r)}</span><span className="kb-volume-subject">{resourceSubject(r)}</span></button>; })}</div>}
    <div className="kb-footer">{filtered.length} volume{filtered.length === 1 ? '' : 's'} · {subject === 'all' ? 'all disciplines' : subject}</div>
  </div>;
}
