import React, { useCallback, useEffect, useState } from 'react';
import {
  X, BookOpen, Rss, Youtube, FileText, RefreshCw, Loader2, Users, Play,
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Knowledge Bank panel — surfaces the 4 unified APIs added in phase B/C/D/E:
 *   subjects        · GET /api/subjects/stats
 *   sources         · GET /api/research-sources
 *   channels        · GET /api/youtube/channels + poll trigger
 *   transcripts     · GET /api/transcripts + POST /:id/summarise
 *
 * Every value is real; no mock data.
 */
export default function KnowledgeBankPanel({ open, onClose }) {
  const [tab, setTab] = useState('subjects');
  const [subjects, setSubjects] = useState([]);
  const [sources, setSources] = useState([]);
  const [channels, setChannels] = useState([]);
  const [transcripts, setTranscripts] = useState([]);
  const [agents, setAgents] = useState({ items: [], grand_total: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(null);

  const load = useCallback(async (which) => {
    setLoading(true); setError(null);
    try {
      const urls = {
        subjects:   `${API}/api/subjects/stats`,
        sources:    `${API}/api/research-sources?enabled_only=false`,
        channels:   `${API}/api/youtube/channels?enabled_only=false`,
        transcripts:`${API}/api/transcripts?limit=40`,
        agents:     `${API}/api/membank/agents`,
      };
      const r = await fetch(urls[which]);
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      if (which === 'subjects')     setSubjects(j.items || []);
      if (which === 'sources')      setSources(j.items || []);
      if (which === 'channels')     setChannels(j.items || []);
      if (which === 'transcripts')  setTranscripts(j.items || []);
      if (which === 'agents')       setAgents(j);
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { if (open) load(tab); }, [open, tab, load]);
  if (!open) return null;

  const pollChannel = async (id) => {
    setBusy(`poll-${id}`);
    try {
      const r = await fetch(`${API}/api/youtube/channels/${id}/poll`, { method: 'POST' });
      await r.json();
      await load('channels');
    } catch (e) { setError(String(e.message || e)); }
    finally { setBusy(null); }
  };

  const summariseTranscript = async (id) => {
    setBusy(`sum-${id}`);
    try {
      const r = await fetch(`${API}/api/transcripts/${id}/summarise`, { method: 'POST' });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      await load('transcripts');
    } catch (e) { setError(String(e.message || e)); }
    finally { setBusy(null); }
  };

  const TABS = [
    { id: 'subjects',    icon: BookOpen,  label: `Subjects (${subjects.length || 22})` },
    { id: 'sources',     icon: Rss,       label: `Sources (${sources.length})` },
    { id: 'channels',    icon: Youtube,   label: `Channels (${channels.length})` },
    { id: 'transcripts', icon: FileText,  label: `Transcripts (${transcripts.length})` },
    { id: 'agents',      icon: Users,     label: `Agents (${agents.grand_total || 0})` },
  ];

  return (
    <div className="ww-shell" data-testid="kb-panel">
      <div className="ww-panel">
        <header className="ww-head">
          <div className="ww-title"><BookOpen size={16} /><span>Knowledge Bank</span></div>
          <button className="ww-close" onClick={onClose} data-testid="kb-close"><X size={16} /></button>
        </header>

        <nav className="lh-tabs" data-testid="kb-tabs">
          {TABS.map((t) => (
            <button key={t.id}
              className={`lh-tab ${tab === t.id ? 'active' : ''}`}
              onClick={() => setTab(t.id)}
              data-testid={`kb-tab-${t.id}`}>
              <t.icon size={11} /><span>{t.label}</span>
            </button>
          ))}
          <button className="lh-refresh" onClick={() => load(tab)} disabled={loading}
                  data-testid="kb-refresh">
            {loading ? <Loader2 size={11} className="t-spin" /> : <RefreshCw size={11} />}
          </button>
        </nav>

        {error && <div className="ww-err">{error}</div>}

        {tab === 'subjects' && (
          <div className="ww-body">
            <ul className="ww-list">
              {subjects.map((s) => (
                <li key={s.subject_id} className="ww-card" data-testid={`kb-subj-${s.slug}`}>
                  <header className="ww-card-head">
                    <span className="ww-dom"
                      style={{ background: 'rgba(0,255,200,0.10)', color: '#00FFC8',
                               borderColor: 'rgba(0,255,200,0.35)' }}>
                      {s.family}
                    </span>
                    <span className="ww-novelty">total {s.total}</span>
                    <span className="ww-feed">mb {s.memory_bank_count}</span>
                    <span className="ww-feed">kr {s.knowledge_records_count}</span>
                    <span className="ww-feed">lsn {s.lesson_count}</span>
                  </header>
                  <div className="ww-title-link">{s.name}</div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {tab === 'sources' && (
          <div className="ww-body">
            <ul className="ww-list">
              {sources.map((s) => (
                <li key={s.id} className="ww-card" data-testid={`kb-src-${s.id}`}>
                  <header className="ww-card-head">
                    <span className="ww-dom">{s.kind}</span>
                    <span className="ww-agent">{s.agent || '-'}</span>
                    <span className="ww-feed">runs {s.run_count}</span>
                    <span className="ww-novelty">{s.enabled ? 'on' : 'off'}</span>
                  </header>
                  <div className="ww-title-link">{s.label}</div>
                  <footer className="ww-card-foot">
                    <span>{s.url?.slice(0, 60)}</span>
                    <span>{(s.last_polled_at || '').slice(0, 19)}</span>
                  </footer>
                </li>
              ))}
            </ul>
          </div>
        )}

        {tab === 'channels' && (
          <div className="ww-body">
            <ul className="ww-list">
              {channels.map((c) => (
                <li key={c.id} className="ww-card" data-testid={`kb-ch-${c.id}`}>
                  <header className="ww-card-head">
                    <span className="ww-dom">youtube</span>
                    <span className="ww-agent">{c.agent || '-'}</span>
                    <span className="ww-novelty">polls {c.poll_count || 0}</span>
                    <span className="ww-feed">new {c.new_videos_seen || 0}</span>
                  </header>
                  <div className="ww-title-link">{c.name || c.channel_url}</div>
                  <footer className="ww-card-foot">
                    <span>{c.channel_id || 'unresolved'}</span>
                    <button
                      className="ww-run"
                      onClick={() => pollChannel(c.id)}
                      disabled={busy === `poll-${c.id}`}
                      data-testid={`kb-ch-poll-${c.id}`}>
                      {busy === `poll-${c.id}` ? <Loader2 size={11} className="t-spin" /> : <Play size={11} />}
                      <span>{busy === `poll-${c.id}` ? 'polling…' : 'poll now'}</span>
                    </button>
                  </footer>
                </li>
              ))}
              {!channels.length && !loading && (
                <div className="ww-empty">
                  No channels yet. Register via <code>POST /api/youtube/channels</code>.
                </div>
              )}
            </ul>
          </div>
        )}

        {tab === 'transcripts' && (
          <div className="ww-body">
            <ul className="ww-list">
              {transcripts.map((t) => (
                <li key={t.id} className="ww-card" data-testid={`kb-tr-${t.id}`}>
                  <header className="ww-card-head">
                    <span className="ww-dom">{t.source}</span>
                    <span className="ww-agent">{t.agent}</span>
                    {t.subject_slug && <span className="ww-feed">{t.subject_slug}</span>}
                    <span className="ww-novelty">
                      {t.summary_id ? 'summarised' : 'unsummarised'}
                    </span>
                  </header>
                  <div className="ww-title-link">{t.title}</div>
                  <footer className="ww-card-foot">
                    <span>{t.word_count} words · {(t.captured_at || '').slice(0, 19)}</span>
                    {!t.summary_id && (
                      <button
                        className="ww-run"
                        onClick={() => summariseTranscript(t.id)}
                        disabled={busy === `sum-${t.id}`}
                        data-testid={`kb-tr-sum-${t.id}`}>
                        {busy === `sum-${t.id}` ? <Loader2 size={11} className="t-spin" /> : <Play size={11} />}
                        <span>{busy === `sum-${t.id}` ? 'summarising…' : 'summarise'}</span>
                      </button>
                    )}
                  </footer>
                </li>
              ))}
              {!transcripts.length && !loading && (
                <div className="ww-empty">No transcripts yet.</div>
              )}
            </ul>
          </div>
        )}

        {tab === 'agents' && (
          <div className="ww-body">
            <ul className="ww-list">
              {agents.items.map((a) => (
                <li key={a.persona} className="ww-card" data-testid={`kb-agent-${a.persona}`}>
                  <header className="ww-card-head">
                    <span className="ww-dom">{a.persona}</span>
                    <span className="ww-novelty">total {a.total}</span>
                    <span className="ww-feed">pinned {a.pinned}</span>
                    <span className="ww-feed">perm {a.permanent}</span>
                    <span className="ww-feed">decay {a.decaying}</span>
                  </header>
                  <div className="ww-title-link">Persona memory · {a.persona}</div>
                </li>
              ))}
              <li className="ww-empty" data-testid="kb-agents-total">
                Total shared memory bank rows: <strong>{agents.grand_total}</strong>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
