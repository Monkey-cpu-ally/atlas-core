/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import { BookOpen, Search, Loader2, RefreshCw, ExternalLink } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

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
    setLoading(true);
    setError('');
    Promise.all([
      fetch(`${BACKEND}/api/kbase/subjects`).then(async (r) => {
        if (!r.ok) throw new Error(`subjects ${r.status}`);
        return r.json();
      }),
      fetch(`${BACKEND}/api/kbase/resources`).then(async (r) => {
        if (!r.ok) throw new Error(`resources ${r.status}`);
        return r.json();
      }),
    ])
      .then(([subjectData, resourceData]) => {
        if (cancelled) return;
        setSubjects(normalizeList(subjectData, ['subjects', 'items', 'data']));
        setResources(normalizeList(resourceData, ['resources', 'items', 'data']));
      })
      .catch((e) => { if (!cancelled) setError(e.message || 'Knowledge Bank unavailable'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [reloadKey]);

  const subjectId = (s) => String(s?.id || s?.slug || s?.name || s || '').toLowerCase();
  const subjectName = (s) => s?.name || s?.label || s?.title || s;

  const filtered = useMemo(() => resources.filter((r) => {
    const rSubject = String(r.subject || r.subject_id || r.domain || '').toLowerCase();
    const haystack = `${r.title || ''} ${r.author || ''} ${r.summary || ''} ${r.source || ''}`.toLowerCase();
    return (subject === 'all' || rSubject === subject) && (!query.trim() || haystack.includes(query.trim().toLowerCase()));
  }), [resources, subject, query]);

  if (selected) {
    return (
      <div className="knowledge-bookshelf" data-testid="knowledge-resource-detail">
        <button className="bp-btn" onClick={() => setSelected(null)}>← Back to shelf</button>
        <div className="kb-detail" style={{ borderColor: aiColor }}>
          <div className="kb-kicker">{selected.subject || selected.domain || selected.type || 'Knowledge resource'}</div>
          <h3 style={{ color: aiColor }}>{selected.title || 'Untitled resource'}</h3>
          {selected.author && <div className="kb-meta">{selected.author}</div>}
          <p>{selected.summary || selected.description || 'No summary is available yet.'}</p>
          <div className="kb-meta">Source: {selected.source || selected.provider || selected.url || 'ATLAS Knowledge Bank'}</div>
          {selected.url && <a className="bp-btn" href={selected.url} target="_blank" rel="noreferrer"><ExternalLink size={12} /> Open source</a>}
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-bookshelf" data-testid="knowledge-bookshelf">
      <div className="kb-header">
        <div>
          <div className="kb-kicker">ATLAS KNOWLEDGE BANK</div>
          <h3 style={{ color: aiColor }}><BookOpen size={15} /> Knowledge Bookshelf</h3>
          <p>Browse verified learning resources across the canonical ATLAS subjects.</p>
        </div>
        <button className="bp-btn" onClick={() => setReloadKey((n) => n + 1)} title="Refresh bookshelf"><RefreshCw size={12} /></button>
      </div>

      <label className="kb-search">
        <Search size={13} />
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search books, papers, topics, authors…" />
      </label>

      <div className="kb-subject-tabs" aria-label="Knowledge subjects">
        <button className={`kb-tab ${subject === 'all' ? 'active' : ''}`} onClick={() => setSubject('all')} style={subject === 'all' ? { borderColor: aiColor, color: aiColor } : undefined}>All</button>
        {subjects.map((s) => {
          const id = subjectId(s);
          return <button key={id} className={`kb-tab ${subject === id ? 'active' : ''}`} onClick={() => setSubject(id)} style={subject === id ? { borderColor: aiColor, color: aiColor } : undefined}>{subjectName(s)}</button>;
        })}
      </div>

      {loading && <div className="kb-state"><Loader2 size={15} className="spin" /> Loading Knowledge Bank…</div>}
      {!loading && error && <div className="kb-state kb-error">Knowledge Bank unavailable: {error}</div>}
      {!loading && !error && filtered.length === 0 && <div className="kb-state">No resources match this shelf yet.</div>}

      {!loading && !error && filtered.length > 0 && (
        <div className="kb-shelf-grid">
          {filtered.map((r, i) => (
            <button key={r.id || r.resource_id || `${r.title}-${i}`} className="kb-book" onClick={() => setSelected(r)} style={{ '--book-accent': aiColor }}>
              <span className="kb-book-spine" />
              <span className="kb-book-type">{r.type || r.resource_type || r.source || 'RESOURCE'}</span>
              <strong>{r.title || 'Untitled resource'}</strong>
              <span className="kb-book-author">{r.author || r.provider || r.subject || 'ATLAS'}</span>
            </button>
          ))}
        </div>
      )}
      <div className="kb-footer">{filtered.length} resource{filtered.length === 1 ? '' : 's'} on this shelf</div>
    </div>
  );
}
