/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import { X, Network, Search, RefreshCw, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * GraphMemoryPanel — lightweight SVG force-directed visualizer for the
 * /api/membank/graph/expand endpoint. No external graph library — we use
 * a small Fruchterman-Reingold-style relaxation in-process.
 */
export default function GraphMemoryPanel({ open, onClose }) {
  const [root, setRoot] = useState('');
  const [depth, setDepth] = useState(2);
  const [data, setData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hovered, setHovered] = useState(null);
  const svgRef = useRef(null);

  const load = useCallback(async (term) => {
    if (!term) return;
    setLoading(true); setError(null);
    try {
      const r = await fetch(
        `${API}/api/membank/graph/expand?subject=${encodeURIComponent(term)}&depth=${depth}&min_weight=0`,
      );
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      const nodes = (j.nodes || []).map((n, i) => ({
        id: n,
        x: 50 + 40 * Math.cos((i / Math.max(1, j.nodes.length)) * Math.PI * 2),
        y: 50 + 40 * Math.sin((i / Math.max(1, j.nodes.length)) * Math.PI * 2),
        vx: 0, vy: 0,
      }));
      const edges = (j.edges || []).map((e) => ({
        from: e.from_node ?? e.from,
        to:   e.to_node ?? e.to,
        relation: e.relation,
        weight: e.weight || 1,
      }));
      // 220 steps of cheap force layout
      const idx = Object.fromEntries(nodes.map((n) => [n.id, n]));
      for (let step = 0; step < 220; step++) {
        for (const n of nodes) { n.fx = 0; n.fy = 0; }
        for (let i = 0; i < nodes.length; i++) {
          for (let j2 = i + 1; j2 < nodes.length; j2++) {
            const a = nodes[i]; const b = nodes[j2];
            const dx = a.x - b.x, dy = a.y - b.y;
            const d = Math.sqrt(dx*dx + dy*dy) || 0.1;
            const repulse = 60 / (d * d);
            a.fx += (dx/d) * repulse; a.fy += (dy/d) * repulse;
            b.fx -= (dx/d) * repulse; b.fy -= (dy/d) * repulse;
          }
        }
        for (const e of edges) {
          const a = idx[e.from], b = idx[e.to];
          if (!a || !b) continue;
          const dx = b.x - a.x, dy = b.y - a.y;
          const d = Math.sqrt(dx*dx + dy*dy) || 0.1;
          const spring = (d - 16) * 0.06;
          a.fx += (dx/d) * spring; a.fy += (dy/d) * spring;
          b.fx -= (dx/d) * spring; b.fy -= (dy/d) * spring;
        }
        for (const n of nodes) {
          n.vx = (n.vx + n.fx) * 0.55;
          n.vy = (n.vy + n.fy) * 0.55;
          n.x += n.vx; n.y += n.vy;
          n.x = Math.max(6, Math.min(94, n.x));
          n.y = Math.max(6, Math.min(94, n.y));
        }
      }
      setData({
        nodes: nodes.map(({ id, x, y }) => ({ id, x, y })),
        edges,
        root: j.subject,
        stats: { nodes: nodes.length, edges: edges.length },
      });
    } catch (e) { setError(String(e.message || e)); }
    finally { setLoading(false); }
  }, [depth]);

  useEffect(() => {
    if (!open) return;
    // auto-load a known root from worldwatch run if none chosen
    if (!root) setRoot('agent:ajani');
  }, [open]);

  useEffect(() => { if (open && root) load(root); }, [open, root, depth]);

  if (!open) return null;

  return (
    <div className="gv-shell" data-testid="graph-memory-panel">
      <div className="gv-panel">
        <header className="gv-head">
          <div className="gv-title"><Network size={16} /><span>Graph Memory</span></div>
          <button className="gv-close" onClick={onClose} data-testid="gv-close"><X size={16} /></button>
        </header>

        <div className="gv-toolbar">
          <div className="gv-search">
            <Search size={11} />
            <input
              type="text"
              placeholder="root node (e.g. agent:ajani · domain:AI · ida* search · concept name)"
              value={root}
              onChange={(e) => setRoot(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') load(root); }}
              data-testid="gv-root-input"
            />
            <label className="gv-depth">
              depth
              <select value={depth} onChange={(e) => setDepth(Number(e.target.value))} data-testid="gv-depth">
                {[1, 2, 3, 4].map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            </label>
            <button className="gv-go" onClick={() => load(root)} disabled={loading} data-testid="gv-go">
              {loading ? <Loader2 size={11} className="t-spin" /> : <RefreshCw size={11} />}
              <span>load</span>
            </button>
          </div>
          {data.stats && (
            <div className="gv-stats" data-testid="gv-stats">
              <span>{data.stats.nodes} nodes</span>
              <span>{data.stats.edges} edges</span>
            </div>
          )}
        </div>

        {error && <div className="gv-err">{error}</div>}

        <div className="gv-canvas" ref={svgRef}>
          {data.nodes.length === 0 && !loading && (
            <div className="gv-empty">enter a node and press load</div>
          )}
          {data.nodes.length > 0 && (
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" width="100%" height="100%">
              {data.edges.map((e, i) => {
                const a = data.nodes.find((n) => n.id === e.from);
                const b = data.nodes.find((n) => n.id === e.to);
                if (!a || !b) return null;
                return (
                  <g key={`e${i}`}>
                    <line x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                          stroke="rgba(244,239,228,0.22)" strokeWidth="0.18" />
                  </g>
                );
              })}
              {data.nodes.map((n) => {
                const isRoot = n.id === data.root;
                const fill = isRoot ? '#9B6BD8' :
                  n.id.startsWith('agent:') ? '#E63946' :
                  n.id.startsWith('domain:') ? '#2EC4B6' :
                  n.id.startsWith('lesson:') ? '#F0B663' :
                  n.id.startsWith('channel:') ? '#88C8FF' :
                  'rgba(244,239,228,0.85)';
                return (
                  <g key={n.id}
                     onMouseEnter={() => setHovered(n.id)}
                     onMouseLeave={() => setHovered(null)}
                     data-testid={`gv-node-${n.id}`}
                  >
                    <circle cx={n.x} cy={n.y}
                            r={isRoot ? 1.7 : 1.1}
                            fill={fill}
                            stroke="rgba(0,0,0,0.6)" strokeWidth="0.12" />
                    <text x={n.x + 1.6} y={n.y + 0.6}
                          fontSize="1.2" fill="rgba(244,239,228,0.85)"
                          style={{ pointerEvents: 'none' }}>
                      {n.id.length > 22 ? n.id.slice(0, 20) + '…' : n.id}
                    </text>
                  </g>
                );
              })}
            </svg>
          )}
        </div>

        {hovered && (
          <div className="gv-hover" data-testid="gv-hover">
            <strong>{hovered}</strong>
            <span>
              { (data.edges || []).filter((e) => e.from === hovered || e.to === hovered).length }
              {' '}
              connections
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
