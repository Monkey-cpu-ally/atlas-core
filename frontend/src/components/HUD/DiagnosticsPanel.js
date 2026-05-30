import React, { useEffect, useState } from 'react';
import { Activity, Shield, Cpu, RefreshCw, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const KIND_COLOR = {
  identity_attack_blocked: '#E63946',
  quarantine_reject:       '#E8B845',
  blueprint_council:       '#9CD3FF',
  blueprint_council_submitted: '#9CD3FF',
  archive_upload:          '#28C8BE',
  permission_change:       '#B388FF',
  think:                   '#A0AEC0',
  council:                 '#F0F0FA',
};

/**
 * DiagnosticsPanel — surfaces /api/atlas/status + /api/atlas/events for the
 * SYSTEMS tile. Read-only health snapshot of the cognition stack: the 3
 * cores, the shield, the identity anchor, recent audit events. Refresh on
 * demand.
 */
export default function DiagnosticsPanel() {
  const [status, setStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const [s, e] = await Promise.all([
        fetch(`${API_URL}/api/atlas/status`).then((r) => r.json()),
        fetch(`${API_URL}/api/atlas/events?limit=40`).then((r) => r.json()),
      ]);
      setStatus(s);
      setEvents(e.events || []);
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="bp-workbench" data-testid="diagnostics-panel">
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'space-between' }}>
        <h3 className="bp-title" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <Activity size={14} /> Atlas Diagnostics
        </h3>
        <button
          className="bp-btn"
          onClick={load}
          disabled={loading}
          style={{ flex: 'none', minWidth: 'auto', padding: '4px 8px' }}
          data-testid="diag-refresh"
          title="Refresh"
        >
          {loading ? <Loader2 size={12} className="spin" /> : <RefreshCw size={12} />}
        </button>
      </div>
      <p className="bp-help">
        Live snapshot of ATLAS Core cognition. Read-only audit surface for
        the architect-in-chief.
      </p>

      {error && <div className="bp-error">{error}</div>}

      {status && (
        <>
          {/* --- Cores --- */}
          <div className="bp-section" data-testid="diag-cores">
            <h4><Cpu size={13} /> Cognitive Cores</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {Object.entries(status.cores || {}).map(([key, c]) => (
                <div key={key} className="bp-synth-block" style={{ marginTop: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span
                      style={{
                        width: 10, height: 10, borderRadius: 5,
                        background: c.color, display: 'inline-block',
                        boxShadow: `0 0 8px ${c.color}88`,
                      }}
                    />
                    <strong style={{ color: c.color, fontSize: 11.5, letterSpacing: 1 }}>
                      {c.code_name.toUpperCase()}
                    </strong>
                    <span style={{ fontSize: 11, color: 'rgba(220,230,245,0.7)' }}>
                      · {c.name} · {c.domain}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* --- Shield --- */}
          <div className="bp-section" data-testid="diag-shield">
            <h4><Shield size={13} /> Shield Core</h4>
            <div className="bp-scores">
              <span>Injection patterns: {status.shield.injection_patterns_loaded}</span>
              <span>Control tokens: {status.shield.control_token_patterns_loaded}</span>
            </div>
            <div className="bp-scores">
              <span>Max upload: {status.shield.max_upload_mb}MB</span>
              <span>Allowed: {(status.shield.allowed_extensions || []).join(' · ')}</span>
            </div>
            <div className="bp-scores">
              <span>Anchored cores: {(status.identity_anchor?.anchored_cores || []).join(' · ')}</span>
              <span>Anchor patterns: {status.identity_anchor?.identity_attack_patterns_loaded ?? '?'}</span>
            </div>
            <details>
              <summary>Capability permissions</summary>
              <ul>
                {Object.entries(status.shield.permissions || {}).map(([k, v]) => (
                  <li key={k}>
                    <span className="bp-key">{k}:</span>{' '}
                    <span style={{ color: v ? '#28C8BE' : '#F47C7C' }}>
                      {v ? 'allowed' : 'denied'}
                    </span>
                  </li>
                ))}
              </ul>
            </details>
          </div>
        </>
      )}

      {/* --- Recent audit events --- */}
      <div className="bp-section" data-testid="diag-events">
        <h4>Recent events ({events.length})</h4>
        {events.length === 0 ? (
          <p className="bp-help" style={{ margin: 0 }}>No events recorded yet.</p>
        ) : (
          <div style={{ maxHeight: 280, overflowY: 'auto' }}>
            {events.slice().reverse().map((evt, i) => (
              <div key={i} className="diag-event">
                <div className="diag-event-head">
                  <span
                    className="diag-event-kind"
                    style={{ color: KIND_COLOR[evt.kind] || '#A0AEC0' }}
                  >
                    {evt.kind}
                  </span>
                  <span className="diag-event-ts">
                    {evt.ts ? new Date(evt.ts).toLocaleTimeString() : ''}
                  </span>
                </div>
                <div className="diag-event-payload">
                  {Object.entries(evt.payload || {}).slice(0, 4).map(([k, v]) => (
                    <span key={k}>
                      <span className="bp-key">{k}:</span>{' '}
                      <span>{typeof v === 'object' ? JSON.stringify(v) : String(v).slice(0, 80)}</span>
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
