/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState, useCallback } from 'react';
import { X, Globe2, RefreshCw, Loader2, ExternalLink } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const DOMAINS = [
  'all', 'AI', 'robotics', 'software_engineering', 'electronics',
  'batteries', 'green_tech', 'manufacturing', 'design', 'architecture',
  'medicine', 'agriculture', 'aerospace',
];

const NOVELTY_TINT = {
  breakthrough: '#FF6B6B',
  notable: '#F0B663',
  incremental: '#88C8FF',
};

const AGENT_COLOR = {
  ajani: '#E63946', minerva: '#2EC4B6', hermes: '#F4EFE4', council: '#9B6BD8',
};

export default function WorldWatchPanel({ open, onClose }) {
  const [updates, setUpdates] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [domain, setDomain] = useState('all');
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const q = domain === 'all' ? '' : `?domain=${encodeURIComponent(domain)}&limit=80`;
      const [u, s] = await Promise.all([
        fetch(`${API}/api/worldwatch/updates${q || '?limit=80'}`).then((r) => r.json()),
        fetch(`${API}/api/worldwatch/status`).then((r) => r.json()),
      ]);
      setUpdates(u.items || []);
      setStatus(s);
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(false); }
  }, [domain]);

  useEffect(() => { if (open) refresh(); }, [open, refresh]);
  if (!open) return null;

  async function runNow() {
    setRunning(true); setError(null);
    try {
      const r = await fetch(`${API}/api/worldwatch/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_per_feed: 1 }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      await refresh();
    } catch (e) { setError(String(e.message || e)); }
    finally { setRunning(false); }
  }

  return (
    <div className="ww-shell" data-testid="world-watch-panel">
      <div className="ww-panel">
        <header className="ww-head">
          <div className="ww-title"><Globe2 size={16} /><span>World Watch</span></div>
          <button className="ww-close" onClick={onClose} data-testid="ww-close"><X size={16} /></button>
        </header>

        <div className="ww-toolbar">
          <div className="ww-domains" data-testid="ww-domains">
            {DOMAINS.map((d) => (
              <button key={d}
                className={`ww-chip ${domain === d ? 'active' : ''}`}
                onClick={() => setDomain(d)}
                data-testid={`ww-chip-${d}`}
              >{d.replace(/_/g, ' ')}</button>
            ))}
          </div>
          <button className="ww-run" onClick={runNow} disabled={running} data-testid="ww-run-btn">
            {running ? <Loader2 size={11} className="t-spin" /> : <RefreshCw size={11} />}
            <span>{running ? 'running…' : 'run now'}</span>
          </button>
        </div>

        {status && (
          <div className="ww-stats" data-testid="ww-stats">
            <span>{status.feeds_count} feeds</span>
            <span>{status.updates_total} updates total</span>
            <span>{updates.length} shown</span>
            <span>last run: {status.last_run ? (status.last_run.ended_at || '').slice(0, 19) : 'never'}</span>
          </div>
        )}

        {error && <div className="ww-err">{error}</div>}

        <div className="ww-body">
          {updates.length === 0 && !loading && (
            <div className="ww-empty">No updates for this filter. Try "run now" or pick a different domain.</div>
          )}
          <ul className="ww-list">
            {updates.map((u) => {
              const wc = u.what_changed || {};
              const tint = NOVELTY_TINT[wc.novelty] || '#88C8FF';
              const agentColor = AGENT_COLOR[u.agent] || '#FFFFFF';
              return (
                <li key={u.id} className="ww-card" data-testid={`ww-card-${u.id}`}>
                  <header className="ww-card-head">
                    <span className="ww-dom" style={{ background: `${tint}22`, color: tint, borderColor: `${tint}55` }}>
                      {u.domain.replace(/_/g, ' ')}
                    </span>
                    <span className="ww-agent" style={{ color: agentColor }}>
                      {u.agent}
                    </span>
                    <span className="ww-novelty">{wc.novelty || 'incremental'}</span>
                    {u.source_type === 'patent' && (
                      <span className="ww-novelty"
                            style={{ background: 'rgba(255,200,80,0.12)', color: '#FFC850',
                                     borderColor: 'rgba(255,200,80,0.4)' }}
                            data-testid="ww-badge-patent">patent</span>
                    )}
                    <span className="ww-feed">{u.feed_label}</span>
                  </header>
                  <a href={u.url} target="_blank" rel="noreferrer" className="ww-title-link">
                    {u.title} <ExternalLink size={10} />
                  </a>
                  {wc.one_line && <p className="ww-one">{wc.one_line}</p>}
                  {(wc.bullets || []).length > 0 && (
                    <ul className="ww-bullets">
                      {wc.bullets.slice(0, 3).map((b, i) => b && <li key={i}>{b}</li>)}
                    </ul>
                  )}
                  <footer className="ww-card-foot">
                    {u.knowledge_id && <span>kb {u.knowledge_id.slice(0, 8)}</span>}
                    {u.memory_bank_id && <span>mb {u.memory_bank_id.slice(0, 8)}</span>}
                    {u.published && <span>{u.published.slice(0, 10)}</span>}
                  </footer>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
}
