/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState, useCallback } from 'react';
import {
  X, Check, AlertTriangle, ShieldAlert, Code2,
  RefreshCw, Filter, Loader2,
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const STATUSES = ['pending', 'approved', 'rejected', 'applied'];

const RISK_ICONS = {
  high:   <ShieldAlert size={11} color="#FF6B6B" />,
  medium: <AlertTriangle size={11} color="#F0B663" />,
  low:    <Check size={11} color="#66E2A0" />,
};

export default function SelfImprovementPanel({ open, onClose }) {
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('pending');
  const [filterSource, setFilterSource] = useState('all'); // all | self-code-scanner | manual
  const [acting, setActing] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const url = `${API}/api/self-improve/proposals?status=${filterStatus}&limit=300`;
      const r = await fetch(url);
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      let items = j.items || [];
      if (filterSource !== 'all') {
        items = items.filter((p) =>
          filterSource === 'self-code-scanner'
            ? p.source === 'self-code-scanner'
            : p.source !== 'self-code-scanner');
      }
      setProposals(items);
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(false); }
  }, [filterStatus, filterSource]);

  useEffect(() => { if (open) refresh(); }, [open, refresh]);

  if (!open) return null;

  async function decide(id, kind) {
    setActing(id);
    try {
      const url = `${API}/api/self-improve/${kind}/${id}`;
      const r = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ note: `${kind} via HUD` }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      refresh();
    } catch (e) { setError(String(e.message || e)); }
    finally { setActing(null); }
  }

  const grouped = proposals.reduce((acc, p) => {
    const k = p.category || 'workflow';
    if (!acc[k]) acc[k] = [];
    acc[k].push(p);
    return acc;
  }, {});

  return (
    <div className="si-shell" data-testid="self-improvement-panel">
      <div className="si-panel">
        <header className="si-head">
          <div className="si-title">
            <Code2 size={16} />
            <span>ATLAS Self-Improvement</span>
          </div>
          <button className="si-close" onClick={onClose} data-testid="si-close">
            <X size={16} />
          </button>
        </header>

        <div className="si-toolbar">
          <div className="si-filters">
            <Filter size={11} />
            {STATUSES.map((s) => (
              <button
                key={s}
                className={`si-chip ${filterStatus === s ? 'active' : ''}`}
                onClick={() => setFilterStatus(s)}
                data-testid={`si-filter-${s}`}
              >{s}</button>
            ))}
          </div>
          <div className="si-filters">
            <span className="si-sub">source:</span>
            {['all', 'self-code-scanner', 'manual'].map((s) => (
              <button
                key={s}
                className={`si-chip ${filterSource === s ? 'active' : ''}`}
                onClick={() => setFilterSource(s)}
                data-testid={`si-source-${s}`}
              >{s}</button>
            ))}
          </div>
          <button className="si-refresh" onClick={refresh} disabled={loading} data-testid="si-refresh">
            {loading ? <Loader2 size={12} className="t-spin" /> : <RefreshCw size={12} />}
            <span>{proposals.length} shown</span>
          </button>
        </div>

        {error && <div className="si-err">{error}</div>}

        <div className="si-body">
          {Object.keys(grouped).length === 0 && !loading && (
            <div className="si-empty">No proposals match the current filter.</div>
          )}
          {Object.entries(grouped).map(([cat, items]) => (
            <section key={cat} className="si-cat-block">
              <h4 className="si-cat-title">{cat.replace(/_/g, ' ')} · {items.length}</h4>
              <ul className="si-list">
                {items.map((p) => (
                  <li key={p.id} className="si-card" data-testid={`si-card-${p.id}`}>
                    <div className="si-card-head">
                      <span className="si-risk">{RISK_ICONS[p.risk_level] || RISK_ICONS.low} {p.risk_level}</span>
                      <span className="si-conf">confidence {(p.confidence_score || 0).toFixed(2)}</span>
                      <span className="si-source">· {p.source || 'manual'}</span>
                    </div>
                    <div className="si-card-pattern">{p.observed_pattern}</div>
                    <div className="si-card-system">in <code>{p.affected_system}</code></div>
                    <div className="si-card-change">{p.proposed_change}</div>
                    {p.evidence && p.evidence.length > 0 && (
                      <details className="si-evidence">
                        <summary>evidence ({p.evidence.length})</summary>
                        <pre>{JSON.stringify(p.evidence, null, 2)}</pre>
                      </details>
                    )}
                    {p.status === 'pending' ? (
                      <div className="si-card-actions">
                        <button
                          className="si-btn si-btn-ok"
                          disabled={acting === p.id}
                          onClick={() => decide(p.id, 'approve')}
                          data-testid={`si-approve-${p.id}`}
                        >approve</button>
                        <button
                          className="si-btn si-btn-no"
                          disabled={acting === p.id}
                          onClick={() => decide(p.id, 'reject')}
                          data-testid={`si-reject-${p.id}`}
                        >reject</button>
                        {p.approval_required && (
                          <span className="si-required">approval required</span>
                        )}
                      </div>
                    ) : (
                      <div className="si-card-status">
                        status: <strong>{p.status}</strong>
                        {p.decision_note && <em> — {p.decision_note}</em>}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
