import React, { useCallback, useEffect, useState } from 'react';
import { X, Scan, Sparkles, Database, Loader2, RefreshCw, FlaskConical } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const SYNTH_MATERIALS = [
  'PET (polyethylene terephthalate)',
  'HDPE (high-density polyethylene)',
  'PP (polypropylene)',
  'PVC (polyvinyl chloride)',
  'PLA (polylactic acid)',
  'Plant leaf — healthy',
  'Plant leaf — drought stress',
  'Soil — high organic matter',
  'NPK fertiliser',
  'Water (free)',
  'Ethanol',
  'Cotton / cellulose',
];

/**
 * D4 — NIR Scanner HUD panel.
 *
 * Three tabs:
 *   scans      — recent ingestions + analysis results
 *   library    — the 12-entry seed library, filterable by category
 *   synthetic  — one-click generator that runs through the full pipeline
 */
export default function NIRScannerPanel({ open, onClose }) {
  const [tab, setTab] = useState('scans');
  const [results, setResults] = useState([]);
  const [library, setLibrary] = useState([]);
  const [libCategory, setLibCategory] = useState('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(false);
  const [pickMaterial, setPickMaterial] = useState(SYNTH_MATERIALS[0]);
  const [lastSynth, setLastSynth] = useState(null);

  const load = useCallback(async (which) => {
    setLoading(true); setError(null);
    try {
      if (which === 'scans') {
        const r = await fetch(`${API}/api/nir/results?limit=40`);
        const j = await r.json();
        if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
        setResults(j.items || []);
      } else if (which === 'library') {
        const r = await fetch(`${API}/api/nir/library`);
        const j = await r.json();
        if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
        setLibrary(j.items || []);
      }
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { if (open && tab !== 'synthetic') load(tab); }, [open, tab, load]);
  if (!open) return null;

  const runSynth = async () => {
    setRunning(true); setError(null); setLastSynth(null);
    try {
      const r = await fetch(`${API}/api/nir/scan/synthetic`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ material_name: pickMaterial,
                               label: `manual · ${pickMaterial}` }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail?.errors?.join('; ') || j.detail || `HTTP ${r.status}`);
      setLastSynth(j.result);
    } catch (e) { setError(String(e.message || e)); }
    finally { setRunning(false); }
  };

  const libCategories = ['all', ...Array.from(new Set(library.map((x) => x.category))).sort()];
  const libFiltered = libCategory === 'all'
    ? library
    : library.filter((x) => x.category === libCategory);

  const renderResult = (r) => {
    const best = r.best_match || null;
    const conf = r.confidence || 0;
    const confColor = conf >= 0.85 ? '#00FFC8'
                    : conf >= 0.55 ? '#FFC850'
                    : '#FF6B6B';
    return (
      <li key={r.id} className="ww-card" data-testid={`nir-result-${r.id}`}>
        <header className="ww-card-head">
          <span className="ww-dom"
                style={{ background: `${confColor}22`, color: confColor,
                         borderColor: `${confColor}55` }}>
            conf {conf.toFixed(2)}
          </span>
          {best && (
            <span className="ww-agent" style={{ color: confColor }}>
              {best.library_name.slice(0, 28)}
            </span>
          )}
          <span className="ww-novelty">{(r.detected_peaks_nm || []).length} peaks</span>
          <span className="ww-feed">snr {Number(r.snr || 0).toFixed(1)}</span>
        </header>
        <div className="ww-title-link">{r.interpretation}</div>
        {(r.top_matches || []).length > 0 && (
          <ul className="ww-bullets">
            {r.top_matches.slice(0, 3).map((m, i) => (
              <li key={i}>{m.library_name} · {m.cosine_score.toFixed(3)} · peaks {m.peaks_matched_count}</li>
            ))}
          </ul>
        )}
        <footer className="ww-card-foot">
          <span>peaks: {(r.detected_peaks_nm || []).slice(0, 5).map((p) => `${Math.round(p)}nm`).join(' · ')}</span>
          <span>{(r.captured_at || '').slice(0, 19)}</span>
        </footer>
      </li>
    );
  };

  return (
    <div className="ww-shell" data-testid="nir-scanner-panel">
      <div className="ww-panel">
        <header className="ww-head">
          <div className="ww-title"><Scan size={16} /><span>NIR Scanner</span></div>
          <button className="ww-close" onClick={onClose} data-testid="nir-close"><X size={16} /></button>
        </header>

        <nav className="lh-tabs" data-testid="nir-tabs">
          {[
            { id: 'scans',     icon: Sparkles,    label: `Scans (${results.length})` },
            { id: 'library',   icon: Database,    label: `Library (${library.length})` },
            { id: 'synthetic', icon: FlaskConical, label: 'Synthesise' },
          ].map((t) => (
            <button key={t.id}
              className={`lh-tab ${tab === t.id ? 'active' : ''}`}
              onClick={() => setTab(t.id)}
              data-testid={`nir-tab-${t.id}`}>
              <t.icon size={11} /><span>{t.label}</span>
            </button>
          ))}
          {tab !== 'synthetic' && (
            <button className="lh-refresh" onClick={() => load(tab)} disabled={loading}
                    data-testid="nir-refresh">
              {loading ? <Loader2 size={11} className="t-spin" /> : <RefreshCw size={11} />}
            </button>
          )}
        </nav>

        {error && <div className="ww-err">{error}</div>}

        {tab === 'scans' && (
          <div className="ww-body">
            {results.length === 0 && !loading && (
              <div className="ww-empty">No NIR scans yet. Try the Synthesise tab.</div>
            )}
            <ul className="ww-list">{results.map(renderResult)}</ul>
          </div>
        )}

        {tab === 'library' && (
          <div className="ww-body">
            <div className="ww-domains" style={{ margin: '0 12px 8px' }} data-testid="nir-lib-cats">
              {libCategories.map((c) => (
                <button key={c}
                  className={`ww-chip ${libCategory === c ? 'active' : ''}`}
                  onClick={() => setLibCategory(c)}
                  data-testid={`nir-lib-cat-${c}`}>{c}</button>
              ))}
            </div>
            <ul className="ww-list">
              {libFiltered.map((e) => (
                <li key={e.id} className="ww-card" data-testid={`nir-lib-${e.id}`}>
                  <header className="ww-card-head">
                    <span className="ww-dom"
                          style={{ background: 'rgba(0,255,200,0.10)', color: '#00FFC8',
                                   borderColor: 'rgba(0,255,200,0.35)' }}>
                      {e.category}
                    </span>
                    <span className="ww-novelty">{(e.characteristic_peaks_nm || []).length} peaks</span>
                  </header>
                  <div className="ww-title-link">{e.name}</div>
                  {e.notes && <p className="ww-one">{e.notes}</p>}
                  <footer className="ww-card-foot">
                    <span>peaks: {(e.characteristic_peaks_nm || []).map((p) => `${p}nm`).join(' · ')}</span>
                  </footer>
                </li>
              ))}
            </ul>
          </div>
        )}

        {tab === 'synthetic' && (
          <div className="ww-body" style={{ padding: 12 }}>
            <div style={{ fontSize: 11, color: 'var(--hud-text-dim)', marginBottom: 8 }}>
              Generate a synthetic NIR scan for one of the library materials. Runs
              through the full peak-detection + library-match pipeline.
            </div>
            <select
              value={pickMaterial}
              onChange={(e) => setPickMaterial(e.target.value)}
              data-testid="nir-synth-select"
              style={{
                width: '100%', padding: 8, fontSize: 11,
                background: 'rgba(255,255,255,0.04)', color: 'var(--hud-text)',
                border: '1px solid rgba(0,255,200,0.3)', borderRadius: 6,
                marginBottom: 8,
              }}>
              {SYNTH_MATERIALS.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
            <button
              className="ww-run"
              onClick={runSynth}
              disabled={running}
              data-testid="nir-synth-run"
              style={{ width: '100%' }}>
              {running ? <Loader2 size={11} className="t-spin" /> : <FlaskConical size={11} />}
              <span>{running ? 'analysing…' : 'Generate + Analyse'}</span>
            </button>

            {lastSynth && (
              <ul className="ww-list" style={{ marginTop: 12 }} data-testid="nir-synth-result">
                {renderResult(lastSynth)}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
