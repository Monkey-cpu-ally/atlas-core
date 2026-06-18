/* eslint-disable */
import React, { useEffect, useState, useRef } from 'react';
import { Waves, Cloud, Sprout, AlertOctagon, AlertTriangle, MessagesSquare, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Visual mapping per device family. The icons + colours stay subtle so the
// strip reads as a status ribbon, not a primary HUD element.
const SENTINEL_VISUAL = {
  'POSEIDON-BUOY':   { Icon: Waves,  hue: '#28C8BE', label: 'WATER'  },
  'AETHER-STATION':  { Icon: Cloud,  hue: '#9CD3FF', label: 'AIR'    },
  'SOIL-WATCH':      { Icon: Sprout, hue: '#A0E66E', label: 'SOIL'   },
};

// Pretty-print the three primary readings per device (everything else falls
// through as raw key=value).
function formatReadings(payload, deviceName) {
  if (!payload || typeof payload !== 'object') return '—';
  const entries = Object.entries(payload).slice(0, 3);
  if (!entries.length) return '—';
  return entries
    .map(([k, v]) => {
      const val = typeof v === 'number' ? v.toFixed(2).replace(/\.00$/, '') : String(v);
      return `${k}=${val}`;
    })
    .join(' · ');
}

/**
 * Phase 7 add-on — Atlas Sentinel.
 *
 * Optional environmental ribbon at the bottom of the HUD. Pulls the latest
 * telemetry burst per seed device every 12s, falls back to a friendly
 * "no telemetry yet" message when the device hasn't reported. Click a chip
 * → opens a small details popover.
 *
 * Visibility is gated on the local-storage flag `atlas.sentinel.enabled`
 * (default ON) so the architect can collapse it without touching code.
 */
export default function AtlasSentinel() {
  const [items, setItems] = useState([]);
  const [enabled, setEnabled] = useState(() => {
    if (typeof window === 'undefined') return true;
    const v = window.localStorage?.getItem('atlas.sentinel.enabled');
    return v == null ? true : v === '1';
  });
  const [openId, setOpenId] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!enabled) return undefined;

    const tick = async () => {
      try {
        const dRes = await fetch(`${API_URL}/api/robot/devices`);
        const dData = await dRes.json();
        const seeds = (dData.items || []).filter((d) => SENTINEL_VISUAL[d.name]);
        const enriched = await Promise.all(
          seeds.map(async (d) => {
            try {
              const tRes = await fetch(`${API_URL}/api/robot/devices/${d.id}/telemetry?limit=1`);
              const tData = await tRes.json();
              const latest = (tData.items || [])[0] || null;
              return { device: d, latest };
            } catch (_) {
              return { device: d, latest: null };
            }
          }),
        );
        setItems(enriched);
      } catch (_) {
        // Silent — strip stays in its last good state.
      }
    };

    tick();
    timerRef.current = setInterval(tick, 12000);
    return () => clearInterval(timerRef.current);
  }, [enabled]);

  const persist = (next) => {
    setEnabled(next);
    try { window.localStorage?.setItem('atlas.sentinel.enabled', next ? '1' : '0'); } catch (_) {}
    if (!next) setOpenId(null);
  };

  if (!enabled) {
    return (
      <button
        type="button"
        className="atlas-sentinel-toggle off"
        onClick={() => persist(true)}
        title="Show Atlas Sentinel"
        aria-label="Show Atlas Sentinel"
        data-testid="sentinel-toggle"
      >
        SENTINEL
      </button>
    );
  }

  return (
    <div className="atlas-sentinel" data-testid="atlas-sentinel" aria-label="Atlas Sentinel — environmental telemetry">
      <button
        type="button"
        className="atlas-sentinel-toggle on"
        onClick={() => persist(false)}
        title="Hide Atlas Sentinel"
        aria-label="Hide Atlas Sentinel"
        data-testid="sentinel-hide"
      >
        ×
      </button>
      <span className="atlas-sentinel-label">SENTINEL</span>
      {items.length === 0 && (
        <span className="atlas-sentinel-empty">…awaiting first telemetry burst…</span>
      )}
      {items.map(({ device, latest }) => {
        const v = SENTINEL_VISUAL[device.name];
        const Icon = v.Icon;
        const isSafe = device.status === 'safe_state';
        const anomaly = (device.state && device.state.anomaly) || null;
        const isAnomaly = !!anomaly && !isSafe;
        const isOpen = openId === device.id;
        const stateLabel = isSafe
          ? 'SAFE STATE'
          : isAnomaly
            ? `ANOMALY · ${(anomaly.drifting_keys || []).slice(0, 2).join(', ')}`
            : (latest ? formatReadings(latest.payload, device.name) : 'no data yet');
        const StatusIcon = isSafe ? AlertOctagon : isAnomaly ? AlertTriangle : Icon;
        const chipClass = [
          'atlas-sentinel-chip',
          isSafe && 'is-safe',
          isAnomaly && 'is-anomaly',
          isOpen && 'is-open',
        ].filter(Boolean).join(' ');
        return (
          <div
            key={device.id}
            className={chipClass}
            data-testid={`sentinel-chip-${device.name}`}
            data-anomaly={isAnomaly ? 'true' : 'false'}
            style={{ '--chip-hue': v.hue }}
            onClick={() => setOpenId(isOpen ? null : device.id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') setOpenId(isOpen ? null : device.id);
            }}
          >
            <StatusIcon size={11} />
            <span className="atlas-sentinel-name">{v.label}</span>
            <span className="atlas-sentinel-readings">{stateLabel}</span>
            {isOpen && (
              <SentinelPopover
                device={device}
                latest={latest}
                anomaly={anomaly}
                visual={v}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}


function SentinelPopover({ device, latest, anomaly, visual }) {
  const [askLoading, setAskLoading] = useState(false);
  const [council, setCouncil] = useState(null);
  const [askError, setAskError] = useState(null);

  const askCouncil = async (e) => {
    e.stopPropagation();
    setAskLoading(true); setAskError(null); setCouncil(null);
    try {
      const r = await fetch(`${API_URL}/api/robot/devices/${device.id}/ask-council`, {
        method: 'POST',
      });
      const body = await r.json();
      if (!r.ok) throw new Error(body.detail || 'council call failed');
      setCouncil(body);
    } catch (err) {
      setAskError(String(err.message || err));
    } finally {
      setAskLoading(false);
    }
  };

  const isSafe = device.status === 'safe_state';
  const headColor = isSafe ? '#E63946' : (anomaly ? '#E8B845' : visual.hue);

  return (
    <div
      className="atlas-sentinel-popover"
      data-testid={`sentinel-popover-${device.name}`}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="atlas-sentinel-popover-head">
        <strong>{device.name}</strong>
        <span style={{ color: headColor }}>{anomaly ? 'anomaly' : device.status}</span>
      </div>
      {anomaly && (
        <div className="atlas-sentinel-anomaly-block" data-testid={`sentinel-anomaly-${device.name}`}>
          <div className="atlas-sentinel-anomaly-head">
            <AlertTriangle size={10} /> drifting: {(anomaly.drifting_keys || []).join(', ')}
          </div>
          {Object.entries(anomaly.z_scores || {}).map(([k, z]) => (
            <div key={k} className="atlas-sentinel-anomaly-row">
              <span className="bp-key">{k}</span>: z = {Number(z).toFixed(2)}
            </div>
          ))}
          <button
            type="button"
            className="atlas-sentinel-ask"
            onClick={askCouncil}
            disabled={askLoading}
            data-testid={`sentinel-ask-council-${device.name}`}
          >
            {askLoading
              ? <><Loader2 size={10} className="spin" /> asking council…</>
              : <><MessagesSquare size={10} /> ask the council</>}
          </button>
          {askError && <div className="bp-error" style={{ fontSize: 10 }}>{askError}</div>}
          {council && (
            <div className="atlas-sentinel-council" data-testid={`sentinel-council-reply-${device.name}`}>
              <div className="atlas-sentinel-council-head">
                COUNCIL · {council.council?.model_used || 'reply'}
              </div>
              <div className="atlas-sentinel-council-body">
                {council.council?.reply || '(no reply)'}
              </div>
            </div>
          )}
        </div>
      )}
      <div className="atlas-sentinel-popover-body">
        {latest ? (
          <>
            <div>last seen · {new Date(latest.received_at).toLocaleString()}</div>
            {Object.entries(latest.payload).map(([k, val]) => (
              <div key={k}><span className="bp-key">{k}</span>: {String(val)}</div>
            ))}
          </>
        ) : (
          <div className="atlas-help-muted">
            No telemetry yet. POST a reading to <code>/api/robot/devices/{device.id}/telemetry</code> from the device firmware.
          </div>
        )}
        {!anomaly && !isSafe && (
          <button
            type="button"
            className="atlas-sentinel-ask"
            onClick={askCouncil}
            disabled={askLoading}
            data-testid={`sentinel-ask-council-${device.name}`}
            style={{ marginTop: 6 }}
          >
            {askLoading
              ? <><Loader2 size={10} className="spin" /> asking council…</>
              : <><MessagesSquare size={10} /> ask the council</>}
          </button>
        )}
        {!anomaly && council && (
          <div className="atlas-sentinel-council" data-testid={`sentinel-council-reply-${device.name}`}>
            <div className="atlas-sentinel-council-head">
              COUNCIL · {council.council?.model_used || 'reply'}
            </div>
            <div className="atlas-sentinel-council-body">
              {council.council?.reply || '(no reply)'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
