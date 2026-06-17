/* eslint-disable */
import React, { useEffect, useState, useCallback } from 'react';
import { Bot, Wifi, AlertOctagon, Send, Loader2, RefreshCw, ShieldAlert } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ROLES = ['owner', 'council', 'ajani', 'minerva', 'hermes', 'guest'];

const STATUS_COLOR = {
  registered:  '#9CD3FF',
  online:      '#28C8BE',
  offline:     '#A0AEC0',
  safe_state:  '#E63946',
  quarantined: '#E8B845',
};

const CMD_STATUS_COLOR = {
  executed:   '#28C8BE',
  rejected:   '#E63946',
  validated:  '#9CD3FF',
  simulated:  '#B388FF',
  queued:     '#A0AEC0',
  failed:     '#E8B845',
};

/**
 * Phase 7 — Robot Control Panel.
 * Embedded inside the SYSTEMS tile (DiagnosticsPanel). Surfaces:
 *  - device registry with live status
 *  - telemetry history for the selected device
 *  - PING / EMERGENCY_STOP from any role (panel respects the owner-gate)
 *  - command log with sim_score + rejection_reason
 *
 * Role is sent on every write via the X-Atlas-Role header (matches backend
 * routes/robot.py). No ring geometry changes — purely panel content.
 */
export default function RobotPanel({ aiColor }) {
  const [role, setRole] = useState('owner');
  const [devices, setDevices] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [telemetry, setTelemetry] = useState([]);
  const [commands, setCommands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [lastCmd, setLastCmd] = useState(null);

  const loadDevices = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch(`${API_URL}/api/robot/devices`);
      const data = await r.json();
      setDevices(data.items || []);
      if (!selectedId && (data.items || []).length) {
        setSelectedId(data.items[0].id);
      }
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setLoading(false);
    }
  }, [selectedId]);

  const loadDeviceDetail = useCallback(async (id) => {
    if (!id) return;
    try {
      const [tRes, cRes] = await Promise.all([
        fetch(`${API_URL}/api/robot/devices/${id}/telemetry?limit=10`).then(r => r.json()),
        fetch(`${API_URL}/api/robot/devices/${id}/commands?limit=10`).then(r => r.json()),
      ]);
      setTelemetry(tRes.items || []);
      setCommands(cRes.items || []);
    } catch (err) {
      setError(String(err.message || err));
    }
  }, []);

  useEffect(() => { loadDevices(); }, [loadDevices]);
  useEffect(() => { loadDeviceDetail(selectedId); }, [selectedId, loadDeviceDetail]);

  const issueCommand = async (kind) => {
    if (!selectedId || busy) return;
    setBusy(true); setError(null);
    try {
      const r = await fetch(`${API_URL}/api/robot/devices/${selectedId}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Atlas-Role': role },
        body: JSON.stringify({ kind, payload: {} }),
      });
      const body = await r.json();
      setLastCmd(body);
      await loadDeviceDetail(selectedId);
      await loadDevices();
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setBusy(false);
    }
  };

  const triggerEmergencyStop = async () => {
    if (!selectedId || busy) return;
    setBusy(true); setError(null);
    try {
      const r = await fetch(`${API_URL}/api/robot/devices/${selectedId}/emergency-stop`, {
        method: 'POST',
        headers: { 'X-Atlas-Role': role },
      });
      if (r.status === 403) {
        setError('EMERGENCY_STOP is owner-only — switch role to "owner".');
      } else {
        const body = await r.json();
        setLastCmd({ status: 'executed', kind: 'emergency_stop', device_id: body.id });
        await loadDevices();
        await loadDeviceDetail(selectedId);
      }
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setBusy(false);
    }
  };

  const selected = devices.find(d => d.id === selectedId);

  return (
    <div className="bp-section" data-testid="robot-panel">
      <h4 style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <Bot size={13} /> Robot Control
        <span style={{ marginLeft: 'auto', display: 'inline-flex', gap: 6, alignItems: 'center' }}>
          <label style={{ fontSize: 10, color: 'rgba(220,230,245,0.6)' }}>role</label>
          <select
            data-testid="robot-role-select"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            style={{
              fontSize: 10, padding: '2px 6px', background: 'rgba(0,0,0,0.4)',
              color: aiColor || '#F4EFE4', border: '1px solid rgba(255,255,255,0.15)',
              borderRadius: 4, fontFamily: 'inherit',
            }}
          >
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <button
            className="bp-btn"
            onClick={loadDevices}
            disabled={loading}
            style={{ flex: 'none', minWidth: 'auto', padding: '2px 6px' }}
            data-testid="robot-refresh"
            title="Refresh devices"
          >
            {loading ? <Loader2 size={11} className="spin" /> : <RefreshCw size={11} />}
          </button>
        </span>
      </h4>

      <p className="bp-help" style={{ marginTop: 4 }}>
        Simulation-first command bridge. Every non-trivial command flows
        Twin → Sim → Validate → Execute. Owner-only: actuate · motion · bind · firmware · emergency-stop.
      </p>

      {error && <div className="bp-error" data-testid="robot-error">{error}</div>}

      {/* --- Device registry --- */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 8 }}>
        {devices.length === 0 && !loading && (
          <p className="bp-help" style={{ margin: 0 }}>No devices registered.</p>
        )}
        {devices.map((d) => {
          const active = d.id === selectedId;
          const color = STATUS_COLOR[d.status] || '#A0AEC0';
          return (
            <button
              key={d.id}
              onClick={() => setSelectedId(d.id)}
              data-testid={`robot-device-${d.name}`}
              style={{
                textAlign: 'left',
                padding: '6px 10px',
                background: active ? 'rgba(255,255,255,0.07)' : 'rgba(255,255,255,0.025)',
                border: `1px solid ${active ? (aiColor || '#9CD3FF') : 'rgba(255,255,255,0.08)'}`,
                borderRadius: 6,
                color: 'inherit',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: 8,
                fontFamily: 'inherit',
              }}
            >
              <span style={{
                width: 8, height: 8, borderRadius: 4,
                background: color, boxShadow: `0 0 6px ${color}88`,
              }} />
              <strong style={{ fontSize: 11, letterSpacing: 0.5 }}>{d.name}</strong>
              <span style={{ fontSize: 10, color: 'rgba(220,230,245,0.55)' }}>
                · {d.kind} · {d.status}
              </span>
              {d.twin_id && (
                <span style={{
                  marginLeft: 'auto', fontSize: 9, color: '#B388FF',
                  background: 'rgba(179,136,255,0.1)', padding: '1px 5px', borderRadius: 3,
                }}>
                  twin-bound
                </span>
              )}
            </button>
          );
        })}
      </div>

      {selected && (
        <>
          {/* --- Command controls --- */}
          <div style={{ display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap' }}>
            <button
              className="bp-btn"
              onClick={() => issueCommand('ping')}
              disabled={busy}
              data-testid="robot-cmd-ping"
              style={{ flex: 'none', minWidth: 'auto', padding: '4px 10px', fontSize: 11 }}
            >
              <Wifi size={11} /> ping
            </button>
            <button
              className="bp-btn"
              onClick={() => issueCommand('actuate')}
              disabled={busy}
              data-testid="robot-cmd-actuate"
              style={{ flex: 'none', minWidth: 'auto', padding: '4px 10px', fontSize: 11 }}
              title="Owner-only — twin-bound devices run a failure simulation first"
            >
              <Send size={11} /> actuate
            </button>
            <button
              className="bp-btn"
              onClick={triggerEmergencyStop}
              disabled={busy}
              data-testid="robot-cmd-estop"
              style={{
                flex: 'none', minWidth: 'auto', padding: '4px 10px', fontSize: 11,
                borderColor: '#E63946', color: '#E63946',
              }}
              title="Owner-only — flips device to SAFE_STATE"
            >
              <AlertOctagon size={11} /> e-stop
            </button>
          </div>

          {lastCmd && (
            <div
              className="bp-synth-block"
              data-testid="robot-last-cmd"
              style={{
                marginTop: 8, fontSize: 11,
                borderColor: CMD_STATUS_COLOR[lastCmd.status] || 'rgba(255,255,255,0.1)',
              }}
            >
              <strong style={{ color: CMD_STATUS_COLOR[lastCmd.status] || '#F4EFE4' }}>
                {lastCmd.kind} → {lastCmd.status}
              </strong>
              {lastCmd.sim_score != null && (
                <span style={{ marginLeft: 8, fontSize: 10, color: 'rgba(220,230,245,0.7)' }}>
                  sim_score={lastCmd.sim_score.toFixed?.(2) ?? lastCmd.sim_score}
                </span>
              )}
              {lastCmd.rejection_reason && (
                <div style={{ marginTop: 4, fontSize: 10, color: '#F47C7C', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <ShieldAlert size={10} /> {lastCmd.rejection_reason}
                </div>
              )}
            </div>
          )}

          {/* --- Telemetry --- */}
          <div style={{ marginTop: 10 }}>
            <h5 style={{ fontSize: 10, letterSpacing: 1, color: 'rgba(220,230,245,0.55)', margin: '8px 0 4px' }}>
              TELEMETRY ({telemetry.length})
            </h5>
            {telemetry.length === 0 ? (
              <p className="bp-help" style={{ margin: 0 }}>No telemetry yet — device hasn't reported.</p>
            ) : (
              <div style={{ maxHeight: 100, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 3 }}>
                {telemetry.slice(0, 5).map((t) => (
                  <div key={t.id} style={{
                    fontSize: 10, padding: '3px 6px', background: 'rgba(255,255,255,0.025)',
                    borderRadius: 4, color: 'rgba(220,230,245,0.85)',
                  }}>
                    <span style={{ color: '#9CD3FF' }}>{new Date(t.received_at).toLocaleTimeString()}</span>
                    {' · '}
                    {Object.entries(t.payload).slice(0, 3).map(([k, v]) => `${k}=${v}`).join(' · ')}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* --- Command log --- */}
          <div style={{ marginTop: 8 }}>
            <h5 style={{ fontSize: 10, letterSpacing: 1, color: 'rgba(220,230,245,0.55)', margin: '8px 0 4px' }}>
              COMMAND LOG ({commands.length})
            </h5>
            {commands.length === 0 ? (
              <p className="bp-help" style={{ margin: 0 }}>No commands issued yet.</p>
            ) : (
              <div style={{ maxHeight: 120, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 3 }}>
                {commands.slice(0, 8).map((c) => (
                  <div
                    key={c.id}
                    data-testid={`robot-cmd-row-${c.id}`}
                    style={{
                      fontSize: 10, padding: '3px 6px', background: 'rgba(255,255,255,0.025)',
                      borderRadius: 4, color: 'rgba(220,230,245,0.85)',
                      display: 'flex', alignItems: 'center', gap: 6,
                    }}
                  >
                    <span style={{
                      color: CMD_STATUS_COLOR[c.status] || '#A0AEC0',
                      minWidth: 60, fontSize: 9, letterSpacing: 0.5,
                    }}>
                      {c.status.toUpperCase()}
                    </span>
                    <span>{c.kind}</span>
                    <span style={{ color: 'rgba(220,230,245,0.5)', fontSize: 9 }}>
                      · {c.issued_by_role}
                    </span>
                    {c.sim_score != null && (
                      <span style={{ marginLeft: 'auto', color: '#B388FF', fontSize: 9 }}>
                        sim={c.sim_score.toFixed ? c.sim_score.toFixed(2) : c.sim_score}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
