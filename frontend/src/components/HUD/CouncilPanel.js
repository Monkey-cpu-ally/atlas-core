import React, { useState } from 'react';
import { Loader2, Users, Sparkles } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function CouncilPanel({ aiColor }) {
  const [topic, setTopic] = useState('');
  const [routeInfo, setRouteInfo] = useState(null);
  const [voices, setVoices] = useState(null);
  const [busy, setBusy] = useState(null);   // 'route' | 'deliberate' | null
  const [error, setError] = useState(null);

  const callRoute = async () => {
    if (!topic.trim()) return;
    setBusy('route'); setError(null); setVoices(null);
    try {
      const res = await fetch(`${BACKEND}/api/council/route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });
      const data = await res.json();
      setRouteInfo(data);
    } catch (e) { setError(String(e)); }
    setBusy(null);
  };

  const callDeliberate = async () => {
    if (!topic.trim()) return;
    setBusy('deliberate'); setError(null); setVoices(null);
    try {
      const res = await fetch(`${BACKEND}/api/council/deliberate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setVoices(data.voices || []);
      setRouteInfo({ routed_to: data.lead, matched_keyword: data.matched_keyword, display: null });
    } catch (e) { setError(String(e.message || e)); }
    setBusy(null);
  };

  return (
    <div className="bp-workbench" data-testid="council-panel">
      <h3 className="bp-title" style={{ color: aiColor }}><Users size={14} /> Council</h3>
      <p className="bp-help">
        Drop any topic. Council picks the lead AI from keyword routing
        (engineering → Ajani, biology → Minerva, code → Hermes). For
        cross-domain questions, all three deliberate.
      </p>

      <textarea
        className="bp-textarea"
        rows={2}
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="e.g. Should we deploy nano-medic swarms in public water?"
        data-testid="council-topic"
      />

      <div className="bp-actions">
        <button className="bp-btn" onClick={callRoute} disabled={!topic.trim() || busy}
                data-testid="council-route-btn"
                style={{ borderColor: aiColor, color: aiColor }}>
          {busy === 'route' ? <Loader2 size={13} className="spin" /> : '⇢'}
          Route only
        </button>
        <button className="bp-btn primary" onClick={callDeliberate} disabled={!topic.trim() || busy}
                data-testid="council-deliberate-btn"
                style={{ borderColor: aiColor, color: aiColor }}>
          {busy === 'deliberate' ? <Loader2 size={13} className="spin" /> : <Sparkles size={13} />}
          Deliberate · all 3
        </button>
      </div>

      {error && <div className="bp-error">{error}</div>}

      {routeInfo && routeInfo.routed_to && (
        <div className="bp-section" data-testid="council-route-result">
          <div className="council-route-line">
            Routed to <strong style={{ color: routeInfo.display?.color || aiColor }}>{routeInfo.routed_to.toUpperCase()}</strong>
            {routeInfo.matched_keyword
              ? <> · matched keyword <em>“{routeInfo.matched_keyword}”</em></>
              : <> · no direct match — falls to Council</>}
          </div>
          {routeInfo.display?.domain && <div className="bp-voice-body">{routeInfo.display.domain}</div>}
        </div>
      )}

      {voices && voices.length > 0 && (
        <div className="council-voices" data-testid="council-voices">
          {voices.map((v) => (
            <div
              key={v.persona}
              className={`council-voice ${v.is_lead ? 'lead' : ''}`}
              style={{ borderColor: v.display.color }}
              data-testid={`council-voice-${v.persona}`}
            >
              <div className="council-voice-head" style={{ color: v.display.color }}>
                {v.display.name}{v.is_lead ? ' · LEAD' : ''}
              </div>
              <div className="bp-voice-body">{v.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
