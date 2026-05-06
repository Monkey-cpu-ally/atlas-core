import React, { useState } from 'react';
import { Loader2, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * BlueprintWorkbench — interactive surface for the four AI services:
 *   • Blueprint Engine   POST /api/ai/blueprint/generate
 *   • Minerva approval   POST /api/ai/minerva/approve
 *   • Hermes validation  POST /api/ai/hermes/validate
 *
 * Renders inside AtlasSidePanel when the user opens the BLUEPRINTS tile.
 */
export default function BlueprintWorkbench({ aiColor }) {
  const [concept, setConcept] = useState('');
  const [loading, setLoading] = useState(null); // null | 'blueprint' | 'minerva' | 'hermes'
  const [blueprint, setBlueprint] = useState(null);
  const [minerva, setMinerva] = useState(null);
  const [hermes, setHermes] = useState(null);
  const [error, setError] = useState(null);

  const callJson = async (path, body) => {
    const res = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`${path} → ${res.status}`);
    return res.json();
  };

  const generate = async () => {
    if (!concept.trim()) return;
    setLoading('blueprint'); setError(null); setBlueprint(null); setMinerva(null); setHermes(null);
    try {
      const data = await callJson('/api/ai/blueprint/generate', { concept });
      setBlueprint(data.blueprint);
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(null); }
  };

  const review = async (which) => {
    if (!concept.trim()) return;
    setLoading(which); setError(null);
    try {
      const path = which === 'minerva' ? '/api/ai/minerva/approve' : '/api/ai/hermes/validate';
      const data = await callJson(path, { proposal: concept });
      if (which === 'minerva') setMinerva(data.review);
      else setHermes(data.review);
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(null); }
  };

  const verdictIcon = (v) => {
    if (!v) return null;
    if (v.startsWith('approve') && !v.includes('reject')) return <CheckCircle2 size={16} color="#28C8BE" />;
    if (v.startsWith('valid') && !v.includes('invalid')) return <CheckCircle2 size={16} color="#28C8BE" />;
    if (v.includes('conditions') || v.includes('constraints')) return <AlertTriangle size={16} color="#E8B845" />;
    return <XCircle size={16} color="#E63946" />;
  };

  return (
    <div className="bp-workbench" data-testid="blueprint-workbench">
      <h3 className="bp-title">Blueprint Engine</h3>
      <p className="bp-help">Describe a concept. Generate a 5-phase blueprint, then route it through Minerva (ethics) and Hermes (technical).</p>

      <textarea
        className="bp-textarea"
        value={concept}
        onChange={(e) => setConcept(e.target.value)}
        placeholder="e.g. A solar-powered water purification rig for off-grid villages…"
        rows={4}
        data-testid="bp-concept-input"
      />

      <div className="bp-actions">
        <button
          className="bp-btn primary"
          style={{ borderColor: aiColor, color: aiColor }}
          onClick={generate}
          disabled={!concept.trim() || loading !== null}
          data-testid="bp-generate-btn"
        >
          {loading === 'blueprint' ? <Loader2 size={14} className="spin" /> : null}
          Generate Blueprint
        </button>
        <button
          className="bp-btn"
          onClick={() => review('minerva')}
          disabled={!concept.trim() || loading !== null}
          data-testid="bp-minerva-btn"
        >
          {loading === 'minerva' ? <Loader2 size={14} className="spin" /> : null}
          Minerva Review
        </button>
        <button
          className="bp-btn"
          onClick={() => review('hermes')}
          disabled={!concept.trim() || loading !== null}
          data-testid="bp-hermes-btn"
        >
          {loading === 'hermes' ? <Loader2 size={14} className="spin" /> : null}
          Hermes Validate
        </button>
      </div>

      {error && <div className="bp-error">{error}</div>}

      {blueprint && (
        <div className="bp-section" data-testid="bp-blueprint-output">
          <h4>Blueprint · {blueprint.domain || 'general'}</h4>
          {Object.entries(blueprint.phases || {}).map(([phase, body]) => (
            <details key={phase} className="bp-phase">
              <summary>{phase.toUpperCase()}</summary>
              <ul>
                {Object.entries(body).map(([k, v]) => (
                  <li key={k}>
                    <span className="bp-key">{k.replace(/_/g, ' ')}:</span>{' '}
                    {Array.isArray(v) ? v.join(' · ') : String(v)}
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </div>
      )}

      {minerva && (
        <div className="bp-section" data-testid="bp-minerva-output">
          <h4>{verdictIcon(minerva.verdict)} Minerva — {minerva.verdict}</h4>
          <p className="bp-summary">{minerva.summary}</p>
          {minerva.ancestral_wisdom && (
            <p className="bp-quote">“{minerva.ancestral_wisdom}”</p>
          )}
          {minerva.concerns?.length > 0 && (
            <details><summary>Concerns ({minerva.concerns.length})</summary>
              <ul>{minerva.concerns.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </details>
          )}
          {minerva.conditions?.length > 0 && (
            <details><summary>Conditions ({minerva.conditions.length})</summary>
              <ul>{minerva.conditions.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </details>
          )}
        </div>
      )}

      {hermes && (
        <div className="bp-section" data-testid="bp-hermes-output">
          <h4>{verdictIcon(hermes.verdict)} Hermes — {hermes.verdict}</h4>
          <p className="bp-summary">{hermes.summary}</p>
          <div className="bp-scores">
            <span>Feasibility {hermes.feasibility_score}/100</span>
            <span>Safety {hermes.safety_score}/100</span>
          </div>
          {hermes.failure_modes?.length > 0 && (
            <details><summary>Failure modes ({hermes.failure_modes.length})</summary>
              <ul>{hermes.failure_modes.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </details>
          )}
          {hermes.next_steps?.length > 0 && (
            <details><summary>Next steps</summary>
              <ul>{hermes.next_steps.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
