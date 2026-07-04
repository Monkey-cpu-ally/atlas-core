/**
 * ATLAS Engineering Console — hidden developer overlay.
 *
 * Toggled from HUDInterface via Ctrl+Shift+E. Pulls live status from
 * `/api/dev/pipeline/status` and renders a status grid, active tasks,
 * and recommended next actions. No mock data.
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  X, RefreshCw, Loader2, GitBranch, ShieldCheck, Cpu, Database,
  BookOpen, ClipboardList, Rocket, Terminal, AlertTriangle, HelpCircle,
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_STYLES = {
  healthy:             { color: '#20B2AA', border: 'rgba(32,178,170,0.45)', icon: ShieldCheck },
  degraded:            { color: '#FFB020', border: 'rgba(255,176,32,0.55)',  icon: AlertTriangle },
  missing:             { color: '#DC143C', border: 'rgba(220,20,60,0.55)',   icon: AlertTriangle },
  under_construction:  { color: '#9370DB', border: 'rgba(147,112,219,0.55)', icon: Rocket },
  unknown:             { color: '#C0C0C0', border: 'rgba(192,192,192,0.35)', icon: HelpCircle },
};

const SYSTEM_ICONS = {
  'MongoDB':           Database,
  'Memory Bank':       Database,
  'Knowledge Network': BookOpen,
  'Research Queue':    ClipboardList,
  'AI Routing':        Cpu,
  'Teaching Engine':   BookOpen,
  'Research Engine':   ClipboardList,
  'GitHub':            GitBranch,
  'Test Suite':        Terminal,
};

function StatusPill({ status }) {
  const s = STATUS_STYLES[status] || STATUS_STYLES.unknown;
  const Icon = s.icon;
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs uppercase tracking-wider"
      style={{
        color: s.color,
        border: `1px solid ${s.border}`,
        background: 'rgba(0,0,0,0.35)',
      }}
      data-testid={`eng-status-pill-${status}`}
    >
      <Icon size={12} />
      {status.replace(/_/g, ' ')}
    </span>
  );
}

function SystemCard({ system }) {
  const Icon = SYSTEM_ICONS[system.name] || Cpu;
  const s = STATUS_STYLES[system.status] || STATUS_STYLES.unknown;
  return (
    <div
      className="rounded-lg p-3 flex flex-col gap-2 backdrop-blur-sm"
      style={{
        background: 'rgba(8,20,32,0.55)',
        border: `1px solid ${s.border}`,
      }}
      data-testid={`eng-system-card-${system.name.replace(/\s+/g, '-').toLowerCase()}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon size={16} style={{ color: s.color }} />
          <span className="text-white/90 font-medium text-sm">{system.name}</span>
        </div>
        <StatusPill status={system.status} />
      </div>
      {system.details ? (
        <div className="text-xs text-white/60 leading-snug">{system.details}</div>
      ) : null}
      {system.endpoint ? (
        <div className="text-[10px] text-white/40 font-mono truncate">{system.endpoint}</div>
      ) : null}
    </div>
  );
}

export default function EngineeringConsole({ open, onClose }) {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API}/api/dev/pipeline/status`);
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      setStatus(j);
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

  const overall = status?.overall_status || 'unknown';
  const overallStyle = STATUS_STYLES[overall] || STATUS_STYLES.unknown;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-6"
      style={{ background: 'rgba(0,0,0,0.65)' }}
      data-testid="engineering-console-overlay"
    >
      <div
        className="w-full max-w-5xl max-h-[88vh] overflow-y-auto rounded-xl backdrop-blur-md"
        style={{
          background: 'linear-gradient(160deg, rgba(4,14,26,0.92) 0%, rgba(6,20,36,0.92) 100%)',
          border: `1px solid ${overallStyle.border}`,
          boxShadow: `0 0 40px ${overallStyle.color}22`,
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
            <Terminal size={20} style={{ color: overallStyle.color }} />
            <div>
              <div className="text-white/95 text-sm font-semibold tracking-wide">
                ATLAS Engineering Console
              </div>
              <div className="text-[11px] text-white/50 font-mono">
                {status?.current_release?.name} · {status?.current_release?.phase}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <StatusPill status={overall} />
            <button
              type="button"
              onClick={load}
              className="p-1.5 rounded hover:bg-white/10 text-white/70"
              data-testid="engineering-console-refresh"
              title="Refresh"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded hover:bg-white/10 text-white/70"
              data-testid="engineering-console-close"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Release + branch strip */}
          {status?.current_release ? (
            <div
              className="rounded-lg p-3 text-xs text-white/70 flex flex-wrap gap-x-6 gap-y-1 font-mono"
              style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(255,255,255,0.06)' }}
              data-testid="engineering-console-release"
            >
              <span>branch: <span className="text-white/90">{status.current_release.branch}</span></span>
              <span>next: <span className="text-white/90">{status.current_release.next_target}</span></span>
              <span>generated: <span className="text-white/50">{status.generated_at}</span></span>
            </div>
          ) : null}

          {error ? (
            <div
              className="text-sm rounded-lg p-3"
              style={{
                color: STATUS_STYLES.missing.color,
                border: `1px solid ${STATUS_STYLES.missing.border}`,
              }}
              data-testid="engineering-console-error"
            >
              Engineering Console Error: {error}
            </div>
          ) : null}

          {!status && loading ? (
            <div className="text-white/60 text-sm flex items-center gap-2">
              <Loader2 size={14} className="animate-spin" /> Loading ATLAS Engineering Console…
            </div>
          ) : null}

          {/* Systems grid */}
          {status?.systems ? (
            <section>
              <h3 className="text-xs uppercase tracking-widest text-white/50 mb-2">
                System Health
              </h3>
              <div
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"
                data-testid="engineering-console-systems"
              >
                {status.systems.map((sys) => (
                  <SystemCard key={sys.name} system={sys} />
                ))}
              </div>
            </section>
          ) : null}

          {/* Active tasks */}
          <section>
            <h3 className="text-xs uppercase tracking-widest text-white/50 mb-2">
              Active Tasks
            </h3>
            {status?.active_tasks?.length ? (
              <ul
                className="space-y-1 text-sm text-white/85"
                data-testid="engineering-console-active-tasks"
              >
                {status.active_tasks.map((t, i) => (
                  <li
                    key={t.id || i}
                    className="rounded px-3 py-1.5"
                    style={{ background: 'rgba(255,255,255,0.04)' }}
                  >
                    <span className="text-white/60 mr-2">·</span>
                    {t.content || t.title || t.summary || JSON.stringify(t).slice(0, 100)}
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-xs text-white/40" data-testid="engineering-console-no-tasks">
                No active engineering tasks tracked in memory bank.
              </div>
            )}
          </section>

          {/* Recommended actions */}
          {status?.recommended_next_actions?.length ? (
            <section>
              <h3 className="text-xs uppercase tracking-widest text-white/50 mb-2">
                Recommended Next Actions
              </h3>
              <ul
                className="space-y-1 text-sm text-white/85"
                data-testid="engineering-console-next-actions"
              >
                {status.recommended_next_actions.map((a) => (
                  <li key={a}>· {a}</li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      </div>
    </div>
  );
}
