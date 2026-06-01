import React, { useEffect, useState } from 'react';
import { Loader2, Search, BookMarked } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function CyclopediaPanel({ aiColor }) {
  const [subjects, setSubjects] = useState([]);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchHits, setSearchHits] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${BACKEND}/api/knowledge/subjects`);
        const data = await res.json();
        setSubjects(data.subjects || []);
      } catch (_) { /* network */ }
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    if (!selected) { setDetail(null); return; }
    (async () => {
      try {
        const res = await fetch(`${BACKEND}/api/knowledge/subjects/${selected}`);
        if (res.ok) setDetail(await res.json());
      } catch (_) { /* network */ }
    })();
  }, [selected]);

  const filtered = query.trim()
    ? subjects.filter((s) => (typeof s === 'string' ? s : s.name).toLowerCase().includes(query.toLowerCase()))
    : subjects;

  const runSearch = async () => {
    if (!query.trim()) { setSearchHits(null); return; }
    try {
      const res = await fetch(`${BACKEND}/api/knowledge/search?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        const data = await res.json();
        setSearchHits(data.results || data.hits || []);
      }
    } catch (_) { /* network */ }
  };

  return (
    <div className="bp-workbench" data-testid="cyclopedia-panel">
      <h3 className="bp-title" style={{ color: aiColor }}><BookMarked size={14} /> Cyclopedia</h3>
      <p className="bp-help">Atlas knowledge index — browse subjects, search the corpus.</p>

      <div className="cyclo-search">
        <Search size={12} style={{ opacity: 0.5 }} />
        <input
          className="bp-textarea cyclo-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') runSearch(); }}
          placeholder="Search or filter subjects…"
          data-testid="cyclo-search-input"
        />
      </div>

      {loading && <div className="bp-section"><Loader2 size={14} className="spin" /> Loading subjects…</div>}

      {!loading && (
        <div className="cyclo-grid" data-testid="cyclo-grid">
          {filtered.slice(0, 30).map((s, i) => {
            const name = typeof s === 'string' ? s : (s.name || s.title || `subject-${i}`);
            return (
              <button
                key={`${name}-${i}`}
                className={`cyclo-chip ${selected === name ? 'active' : ''}`}
                onClick={() => setSelected(name)}
                style={selected === name ? { borderColor: aiColor, color: aiColor } : undefined}
                data-testid={`cyclo-chip-${name.replace(/\s+/g,'-').toLowerCase()}`}
              >
                {name}
              </button>
            );
          })}
        </div>
      )}

      {detail && (
        <div className="bp-section" data-testid="cyclo-detail">
          <h4 style={{ color: aiColor }}>{detail.name || selected}</h4>
          {detail.description && <div className="bp-voice-body">{detail.description}</div>}
          {Array.isArray(detail.topics) && detail.topics.length > 0 && (
            <ul style={{ marginTop: 6 }}>
              {detail.topics.map((t, i) => <li key={`${t}-${i}`}>{t}</li>)}
            </ul>
          )}
        </div>
      )}

      {searchHits && searchHits.length > 0 && (
        <div className="bp-section" data-testid="cyclo-search-results">
          <h4 style={{ color: aiColor }}>Search results · {searchHits.length}</h4>
          {searchHits.slice(0, 10).map((hit, i) => (
            <div key={`hit-${i}`} className="cyclo-hit">{hit.title || hit.name || JSON.stringify(hit)}</div>
          ))}
        </div>
      )}
    </div>
  );
}
