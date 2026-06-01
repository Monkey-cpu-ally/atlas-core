import React, { useEffect, useState } from 'react';
import { Loader2, Database } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

const FRIENDLY_TYPE = {
  archive_upload: 'archive',
  teach_request:  'teaching',
  council_vote:   'council',
  blueprint_run:  'blueprint',
};

export default function MemoryPanel({ aiColor }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const res = await fetch(`${BACKEND}/api/memory/feed?limit=30`);
        const data = await res.json();
        if (!cancelled) {
          setEvents(data.events || []);
          setLoading(false);
        }
      } catch (_) { /* network */ }
    };
    tick();
    const id = setInterval(tick, 8000);    // gentle live refresh
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  return (
    <div className="bp-workbench" data-testid="memory-panel">
      <h3 className="bp-title" style={{ color: aiColor }}><Database size={14} /> Live Memory Feed</h3>
      <p className="bp-help">
        Every uploaded artefact, council vote, teaching run, and shield event is
        recorded here. Auto-refreshes every 8 seconds.
      </p>
      {loading && <div className="bp-section"><Loader2 size={14} className="spin" /> Listening…</div>}
      {!loading && events.length === 0 && (
        <div className="bp-section" data-testid="memory-empty">No events yet. Upload an artefact or run a council deliberation to seed the memory.</div>
      )}
      <div className="memory-feed">
        {events.map((e, i) => (
          <div key={`${e.id || i}-${e.timestamp || ''}`} className="memory-row">
            <div className="memory-row-head">
              <span className="memory-row-type" style={{ color: aiColor }}>
                {FRIENDLY_TYPE[e.event_type] || e.event_type || 'event'}
              </span>
              <span className="memory-row-time">
                {e.timestamp ? new Date(e.timestamp).toLocaleString() : ''}
              </span>
            </div>
            <pre className="memory-row-body">
              {typeof e.details === 'string'
                ? e.details
                : JSON.stringify(e.details ?? {}, null, 0)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
