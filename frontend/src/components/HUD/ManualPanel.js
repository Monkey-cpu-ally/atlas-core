import React, { useEffect, useState } from 'react';
import { Loader2, BookOpen } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

/** Lightweight markdown renderer for the manual — bold + line breaks only. */
function fmt(text) {
  return text.split('\n').map((line, i) => {
    const parts = line.split(/(\*\*[^*]+\*\*)/g).map((p, j) =>
      p.startsWith('**') && p.endsWith('**')
        ? <strong key={j}>{p.slice(2, -2)}</strong>
        : p
    );
    return <div key={i} className="manual-line">{parts}</div>;
  });
}

export default function ManualPanel({ aiColor }) {
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState('hard-rules');

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${BACKEND}/api/manual/sections`);
        const data = await res.json();
        setSections(data.sections || []);
      } catch (_) { /* network */ }
      setLoading(false);
    })();
  }, []);

  return (
    <div className="bp-workbench" data-testid="manual-panel">
      <h3 className="bp-title" style={{ color: aiColor }}><BookOpen size={14} /> Operator Manual</h3>
      <p className="bp-help">How Atlas Core works. The rules each AI lives by, the rings, the labs, and the voice stack.</p>
      {loading && <div className="bp-section"><Loader2 size={14} className="spin" /> Loading manual…</div>}
      {!loading && sections.map((s) => (
        <details
          key={s.id}
          className="bp-phase"
          open={openId === s.id}
          onToggle={(e) => e.target.open && setOpenId(s.id)}
          data-testid={`manual-section-${s.id}`}
        >
          <summary style={{ color: aiColor }}>{s.title}</summary>
          <div className="bp-voice-body manual-body">{fmt(s.body)}</div>
        </details>
      ))}
    </div>
  );
}
