import React, { useCallback, useEffect, useState } from 'react';
import { X, Hammer, Package, FileText, Loader2, RefreshCw } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * D3 — Weaver HUD panel.
 *
 * Surfaces the existing `/api/weaver/plans` + `/api/weaver/parts`
 * endpoints (already populated · 2 plans, 25 parts). Two tabs:
 *
 *   plans  — recently generated build plans, expandable to show blueprint
 *   parts  — the curated parts library, filterable by category
 */
export default function WeaverPanel({ open, onClose }) {
  const [tab, setTab] = useState('plans');
  const [plans, setPlans] = useState([]);
  const [parts, setParts] = useState([]);
  const [partsCategory, setPartsCategory] = useState('all');
  const [openPlanId, setOpenPlanId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async (which) => {
    setLoading(true); setError(null);
    try {
      if (which === 'plans') {
        const r = await fetch(`${API}/api/weaver/plans?limit=40`);
        const j = await r.json();
        if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
        setPlans(j.items || []);
      } else {
        const r = await fetch(`${API}/api/weaver/parts?limit=200`);
        const j = await r.json();
        if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
        setParts(j.items || []);
      }
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { if (open) load(tab); }, [open, tab, load]);
  if (!open) return null;

  const partCategories = ['all', ...Array.from(new Set(parts.map((p) => p.category))).sort()];
  const partsFiltered = partsCategory === 'all'
    ? parts
    : parts.filter((p) => p.category === partsCategory);

  return (
    <div className="ww-shell" data-testid="weaver-panel">
      <div className="ww-panel">
        <header className="ww-head">
          <div className="ww-title"><Hammer size={16} /><span>Weaver · Build Planner</span></div>
          <button className="ww-close" onClick={onClose} data-testid="weaver-close"><X size={16} /></button>
        </header>

        <nav className="lh-tabs" data-testid="weaver-tabs">
          {[
            { id: 'plans', icon: FileText, label: `Plans (${plans.length})` },
            { id: 'parts', icon: Package,  label: `Parts (${parts.length})` },
          ].map((t) => (
            <button key={t.id}
              className={`lh-tab ${tab === t.id ? 'active' : ''}`}
              onClick={() => setTab(t.id)}
              data-testid={`weaver-tab-${t.id}`}>
              <t.icon size={11} />
              <span>{t.label}</span>
            </button>
          ))}
          <button className="lh-refresh" onClick={() => load(tab)} disabled={loading}
                  data-testid="weaver-refresh">
            {loading ? <Loader2 size={11} className="t-spin" /> : <RefreshCw size={11} />}
          </button>
        </nav>

        {error && <div className="ww-err">{error}</div>}

        {tab === 'plans' && (
          <div className="ww-body">
            {plans.length === 0 && !loading && (
              <div className="ww-empty">No plans yet. Generate one via /api/weaver/plans.</div>
            )}
            <ul className="ww-list">
              {plans.map((p) => {
                const isOpen = openPlanId === p.id;
                return (
                  <li key={p.id} className="ww-card" data-testid={`weaver-plan-${p.id}`}>
                    <header className="ww-card-head" style={{ cursor: 'pointer' }}
                            onClick={() => setOpenPlanId(isOpen ? null : p.id)}>
                      <span className="ww-dom"
                            style={{ background: 'rgba(232,184,69,0.12)', color: '#E8B845',
                                     borderColor: 'rgba(232,184,69,0.4)' }}>
                        plan
                      </span>
                      <span className="ww-agent" style={{ color: '#E8B845' }}>
                        {p.owner_agent || 'ajani'}
                      </span>
                      <span className="ww-feed">{(p.created_at || '').slice(0, 10)}</span>
                    </header>
                    <div className="ww-title-link">{p.title || '(untitled plan)'}</div>
                    {p.description && <p className="ww-one">{(p.description || '').slice(0, 280)}</p>}
                    {isOpen && p.blueprint && (
                      <pre style={{
                        marginTop: 8, padding: 10, fontSize: 10, lineHeight: 1.5,
                        background: 'rgba(255,255,255,0.03)', borderRadius: 6,
                        whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                        color: 'var(--hud-text-dim)', maxHeight: 320, overflow: 'auto',
                      }} data-testid={`weaver-plan-blueprint-${p.id}`}>
                        {typeof p.blueprint === 'string'
                          ? p.blueprint
                          : JSON.stringify(p.blueprint, null, 2)}
                      </pre>
                    )}
                    <footer className="ww-card-foot">
                      <span>{isOpen ? 'click to collapse' : 'click to expand blueprint'}</span>
                    </footer>
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {tab === 'parts' && (
          <div className="ww-body">
            <div className="ww-domains" style={{ margin: '0 12px 8px' }} data-testid="weaver-part-cats">
              {partCategories.map((c) => (
                <button key={c}
                  className={`ww-chip ${partsCategory === c ? 'active' : ''}`}
                  onClick={() => setPartsCategory(c)}
                  data-testid={`weaver-part-cat-${c}`}>{c}</button>
              ))}
            </div>
            {partsFiltered.length === 0 && !loading && (
              <div className="ww-empty">No parts for this category.</div>
            )}
            <ul className="ww-list">
              {partsFiltered.map((p) => (
                <li key={p.id} className="ww-card" data-testid={`weaver-part-${p.id}`}>
                  <header className="ww-card-head">
                    <span className="ww-dom"
                          style={{ background: 'rgba(0,255,200,0.10)', color: '#00FFC8',
                                   borderColor: 'rgba(0,255,200,0.35)' }}>
                      {p.category}
                    </span>
                    {p.cost_per_unit_usd != null && (
                      <span className="ww-novelty">${p.cost_per_unit_usd}</span>
                    )}
                    {p.mass_g != null && <span className="ww-feed">{p.mass_g} g</span>}
                  </header>
                  <div className="ww-title-link">{p.name}</div>
                  {p.notes && <p className="ww-one">{p.notes}</p>}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
