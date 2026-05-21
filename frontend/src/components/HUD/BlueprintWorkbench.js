import React, { useState } from 'react';
import { Loader2, CheckCircle2, AlertTriangle, XCircle, Sparkles } from 'lucide-react';
import { useAtlasJob } from '../../hooks/useAtlasJob';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Lens metadata keyed by core. Matches the backend TRI_FRAMINGS.
const VOICES = {
  ajani:   { label: 'AJANI · STRUCTURAL',  color: '#F03246' },
  minerva: { label: 'MINERVA · HUMAN',     color: '#28C8BE' },
  hermes:  { label: 'HERMES · INVENTIVE',  color: '#E0E0EA' },
};

/**
 * BlueprintWorkbench — Generate runs the Atlas tri-council job. Because
 * the backend job takes 90–200s and the K8s ingress times out at 60s, we
 * use useAtlasJob to submit + poll a background job.
 */
export default function BlueprintWorkbench({ aiColor }) {
  const [concept, setConcept] = useState('');
  const [loading, setLoading] = useState(null); // null | 'minerva' | 'hermes'  (single-core paths only)
  const [minerva, setMinerva] = useState(null);
  const [hermes, setHermes] = useState(null);
  const [reviewError, setReviewError] = useState(null);

  const council = useAtlasJob();
  const councilBusy = council.status === 'pending' || council.status === 'running';
  const councilResult = council.status === 'done' ? council.result : null;

  const callJson = async (path, body) => {
    const res = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`${path} → ${res.status}`);
    return res.json();
  };

  const generate = () => {
    if (!concept.trim()) return;
    setMinerva(null); setHermes(null); setReviewError(null);
    council.run('/api/atlas/blueprint/council', { concept });
  };

  const review = async (which) => {
    if (!concept.trim()) return;
    setLoading(which); setReviewError(null);
    try {
      const path = which === 'minerva' ? '/api/ai/minerva/approve' : '/api/ai/hermes/validate';
      const data = await callJson(path, { proposal: concept });
      if (which === 'minerva') setMinerva(data.review);
      else setHermes(data.review);
    } catch (e) { setReviewError(String(e.message || e)); }
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
      <p className="bp-help">
        Three voices, one synthesis. Generate fires the Atlas tri-council:
        Ajani reasons structurally, Minerva reasons through humans &amp;
        ecosystems, Hermes reasons inventively, then the cores merge into
        one blueprint.
      </p>

      <textarea
        className="bp-textarea"
        value={concept}
        onChange={(e) => setConcept(e.target.value)}
        placeholder="e.g. A solar-powered rainwater harvesting kit for a village school…"
        rows={4}
        data-testid="bp-concept-input"
      />

      <div className="bp-actions">
        <button
          className="bp-btn primary"
          style={{ borderColor: aiColor, color: aiColor }}
          onClick={generate}
          disabled={!concept.trim() || councilBusy || loading !== null}
          data-testid="bp-generate-btn"
        >
          {councilBusy ? <Loader2 size={14} className="spin" /> : <Sparkles size={14} />}
          Generate Tri-Council Blueprint
        </button>
        <button
          className="bp-btn"
          onClick={() => review('minerva')}
          disabled={!concept.trim() || councilBusy || loading !== null}
          data-testid="bp-minerva-btn"
        >
          {loading === 'minerva' ? <Loader2 size={14} className="spin" /> : null}
          Minerva Approval
        </button>
        <button
          className="bp-btn"
          onClick={() => review('hermes')}
          disabled={!concept.trim() || councilBusy || loading !== null}
          data-testid="bp-hermes-btn"
        >
          {loading === 'hermes' ? <Loader2 size={14} className="spin" /> : null}
          Hermes Validation
        </button>
      </div>

      {councilBusy && (
        <div className="bp-section bp-loading" data-testid="bp-council-loading">
          {council.status === 'pending'
            ? 'Submitting job…'
            : 'Three cores thinking in parallel · this takes 60–180 seconds.'}
        </div>
      )}

      {council.status === 'failed' && (
        <div className="bp-error">Council job failed: {council.error}</div>
      )}
      {reviewError && <div className="bp-error">{reviewError}</div>}

      {/* --- Tri-council output --- */}
      {councilResult && !councilResult.error && (
        <div className="bp-section bp-council" data-testid="bp-council-output">
          <h4>Three Voices</h4>
          {['ajani', 'minerva', 'hermes'].map((k) => {
            const v = councilResult.voices?.[k];
            if (!v) return null;
            return (
              <details key={k} className="bp-voice" open>
                <summary style={{ color: VOICES[k].color }}>
                  {VOICES[k].label}
                </summary>
                <div className="bp-voice-body">{v.reasoning}</div>
              </details>
            );
          })}

          <h4 className="bp-synth-title">Synthesis Blueprint</h4>
          {councilResult.synthesis?.error ? (
            <div className="bp-error">
              Synthesis failed: {councilResult.synthesis.error}
            </div>
          ) : (
            <div className="bp-synth">
              {councilResult.synthesis?.headline && (
                <p className="bp-summary">{councilResult.synthesis.headline}</p>
              )}
              {[
                ['structural_pillar', 'Structural pillar', '#F03246'],
                ['human_pillar',      'Human pillar',      '#28C8BE'],
                ['inventive_pillar',  'Inventive pillar',  '#E0E0EA'],
                ['tensions',          'Tensions',          '#E8B845'],
                ['first_actions',     'First actions',     '#9CD3FF'],
                ['open_questions',    'Open questions',    '#B388FF'],
              ].map(([key, label, color]) => {
                const items = councilResult.synthesis?.[key];
                if (!Array.isArray(items) || items.length === 0) return null;
                return (
                  <div key={key} className="bp-synth-block">
                    <h5 style={{ color }}>{label}</h5>
                    <ul>{items.map((it, i) => <li key={i}>{it}</li>)}</ul>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* --- Legacy single-core reviews --- */}
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
