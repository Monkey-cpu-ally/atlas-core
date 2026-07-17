/**
 * ATLAS Vision Console — HUD panel.
 *
 * Consumes:
 *   - GET /api/vision/health         (capability chips, driver kinds, counts)
 *   - GET /api/vision/inspections    (verdict feed)
 *   - GET /api/vision/devices/drivers (advertised hardware surface)
 *
 * Mirrors the KnowledgeBankPanel visual language. Hidden by default —
 * toggle with Ctrl+Shift+V from HUDInterface.
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  X, RefreshCw, Loader2, Camera, Radar, Cpu, ShieldCheck,
  AlertTriangle, Thermometer, Radio, Activity, Boxes, Layers,
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const VERDICT = {
  pass: { color: '#20B2AA', border: 'rgba(32,178,170,0.45)', icon: ShieldCheck },
  warn: { color: '#FFB020', border: 'rgba(255,176,32,0.55)', icon: AlertTriangle },
  fail: { color: '#DC143C', border: 'rgba(220,20,60,0.55)', icon: AlertTriangle },
};

const KIND_ICON = {
  camera: Camera,
  thermal: Thermometer,
  event_camera: Activity,
  multispectral: Layers,
  depth: Boxes,
  lidar: Radar,
  radar: Radar,
  sonar: Radio,
  imu: Activity,
  force: Cpu,
  torque: Cpu,
  nir_bridge: Layers,
};

function Chip({ children, tone = 'neutral' }) {
  const tones = {
    neutral: { color: '#8fa3b4', border: 'rgba(143,163,180,0.35)' },
    good: { color: '#20B2AA', border: 'rgba(32,178,170,0.45)' },
    warn: { color: '#FFB020', border: 'rgba(255,176,32,0.55)' },
    fail: { color: '#DC143C', border: 'rgba(220,20,60,0.55)' },
  };
  const t = tones[tone] || tones.neutral;
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] uppercase tracking-wider"
      style={{ color: t.color, border: `1px solid ${t.border}`, background: 'rgba(0,0,0,0.35)' }}
    >
      {children}
    </span>
  );
}

function KindTile({ kind, capabilities }) {
  const Icon = KIND_ICON[kind] || Cpu;
  return (
    <div
      className="rounded-lg p-3 flex flex-col gap-1"
      style={{ background: 'rgba(8,20,32,0.55)', border: '1px solid rgba(255,255,255,0.06)' }}
      data-testid={`vision-driver-tile-${kind}`}
    >
      <div className="flex items-center gap-2 text-white/90 text-sm font-medium">
        <Icon size={14} style={{ color: '#7ecbff' }} />
        {kind}
      </div>
      <div className="flex flex-wrap gap-1">
        {(capabilities || []).map((c) => (
          <Chip key={c}>{c}</Chip>
        ))}
      </div>
    </div>
  );
}

function VerdictPill({ verdict }) {
  const s = VERDICT[verdict] || VERDICT.warn;
  const Icon = s.icon;
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] uppercase"
      style={{ color: s.color, border: `1px solid ${s.border}`, background: 'rgba(0,0,0,0.4)' }}
      data-testid={`vision-verdict-${verdict}`}
    >
      <Icon size={11} /> {verdict}
    </span>
  );
}

function InspectionRow({ row }) {
  return (
    <div
      className="flex items-center gap-3 rounded px-3 py-2"
      style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}
      data-testid={`vision-inspection-${row.id}`}
    >
      <VerdictPill verdict={row.verdict} />
      <div className="flex-1 min-w-0">
        <div className="text-white/85 text-xs font-mono truncate">
          {row.kind} · frame {row.frame_id?.slice(0, 10)}
        </div>
        <div className="text-white/45 text-[10px]">
          {row.defects?.length ?? 0} defect(s) · {row.inspected_at?.slice(0, 19)}
        </div>
      </div>
      <div className="text-right text-[10px] text-white/50 font-mono">
        {Object.entries(row.metrics || {})
          .slice(0, 2)
          .map(([k, v]) => (
            <div key={k}>{k}={v}</div>
          ))}
      </div>
    </div>
  );
}

export default function VisionConsole({ open, onClose }) {
  const [health, setHealth] = useState(null);
  const [drivers, setDrivers] = useState([]);
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [h, d, i] = await Promise.all([
        fetch(`${API}/api/vision/health`).then((r) => r.json()),
        fetch(`${API}/api/vision/devices/drivers`).then((r) => r.json()),
        fetch(`${API}/api/vision/inspections?limit=20`).then((r) => r.json()),
      ]);
      setHealth(h);
      setDrivers(d.drivers || []);
      setInspections(i.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open) load();
  }, [open, load]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-6"
      style={{ background: 'rgba(0,0,0,0.65)' }}
      data-testid="vision-console-overlay"
    >
      <div
        className="w-full max-w-5xl max-h-[88vh] overflow-y-auto rounded-xl backdrop-blur-md"
        style={{
          background: 'linear-gradient(160deg, rgba(4,14,26,0.92) 0%, rgba(6,20,36,0.92) 100%)',
          border: '1px solid rgba(126,203,255,0.35)',
          boxShadow: '0 0 40px rgba(126,203,255,0.15)',
        }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 py-4 border-b sticky top-0 backdrop-blur-md"
          style={{
            borderColor: 'rgba(255,255,255,0.08)',
            background: 'rgba(4,14,26,0.85)',
          }}
        >
          <div className="flex items-center gap-3">
            <Camera size={20} style={{ color: '#7ecbff' }} />
            <div>
              <div className="text-white/95 text-sm font-semibold tracking-wide">
                ATLAS Vision Console
              </div>
              <div className="text-[11px] text-white/50 font-mono">
                Perception foundation · Hermes + Weaver
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {health ? (
              <>
                <Chip tone="good" data-testid="vision-devices-chip">
                  {health.device_count ?? 0} devices
                </Chip>
                <Chip tone="good" data-testid="vision-drivers-chip">
                  {health.driver_count ?? 0} drivers
                </Chip>
              </>
            ) : null}
            <button
              type="button"
              onClick={load}
              className="p-1.5 rounded hover:bg-white/10 text-white/70"
              data-testid="vision-console-refresh"
              title="Refresh"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded hover:bg-white/10 text-white/70"
              data-testid="vision-console-close"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {error ? (
            <div
              className="text-sm rounded-lg p-3"
              style={{ color: VERDICT.fail.color, border: `1px solid ${VERDICT.fail.border}` }}
              data-testid="vision-console-error"
            >
              Vision Console Error: {error}
            </div>
          ) : null}

          {!health && loading ? (
            <div className="text-white/60 text-sm flex items-center gap-2">
              <Loader2 size={14} className="animate-spin" /> Loading Vision Console…
            </div>
          ) : null}

          {/* Capabilities strip */}
          {health?.capabilities ? (
            <section>
              <h3 className="text-xs uppercase tracking-widest text-white/50 mb-2">
                Capabilities
              </h3>
              <div className="flex flex-wrap gap-2" data-testid="vision-capabilities">
                {health.capabilities.map((c) => (
                  <Chip key={c} tone="good">{c}</Chip>
                ))}
              </div>
            </section>
          ) : null}

          {/* Drivers grid */}
          {drivers.length ? (
            <section>
              <h3 className="text-xs uppercase tracking-widest text-white/50 mb-2">
                Vision Device Drivers ({drivers.length})
              </h3>
              <div
                className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3"
                data-testid="vision-drivers-grid"
              >
                {drivers.map((d) => (
                  <KindTile key={d.kind} kind={d.kind} capabilities={d.capabilities} />
                ))}
              </div>
            </section>
          ) : null}

          {/* Inspections feed */}
          <section>
            <h3 className="text-xs uppercase tracking-widest text-white/50 mb-2">
              Recent Inspections ({inspections.length})
            </h3>
            {inspections.length ? (
              <div className="space-y-1.5" data-testid="vision-inspections-list">
                {inspections.map((row) => (
                  <InspectionRow key={row.id} row={row} />
                ))}
              </div>
            ) : (
              <div className="text-xs text-white/40" data-testid="vision-no-inspections">
                No inspections yet. Ingest a frame and POST /api/vision/inspection/industrial
                or /api/vision/inspection/pcb to populate this feed.
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
