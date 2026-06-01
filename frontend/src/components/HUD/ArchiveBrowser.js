import React, { useEffect, useState } from 'react';
import { Loader2, Archive, FileText } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

/**
 * ArchiveBrowser — embedded inline browser for the ARCHIVE outer-ring tile.
 * Reads both the uploaded-files list (/api/files/list) and the Atlas
 * cognitive archive (/api/atlas/archive/list). Tabbed so the architect
 * can switch between raw uploads and classified Atlas entries.
 */
export default function ArchiveBrowser({ aiColor }) {
  const [tab, setTab] = useState('atlas');
  const [files, setFiles] = useState([]);
  const [archive, setArchive] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    (async () => {
      try {
        if (tab === 'files') {
          const r = await fetch(`${BACKEND}/api/files/list?limit=80`);
          const data = await r.json();
          if (!cancelled) setFiles(Array.isArray(data) ? data : (data.files || []));
        } else {
          const r = await fetch(`${BACKEND}/api/atlas/archive/list`);
          const data = await r.json();
          if (!cancelled) setArchive(data.entries || []);
        }
      } catch (_) { /* network */ }
      if (!cancelled) setLoading(false);
    })();
    return () => { cancelled = true; };
  }, [tab]);

  return (
    <div className="bp-workbench" data-testid="archive-browser">
      <h3 className="bp-title" style={{ color: aiColor }}><Archive size={14} /> Archive</h3>
      <div className="bp-actions">
        <button
          className={`bp-btn ${tab === 'atlas' ? 'primary' : ''}`}
          onClick={() => setTab('atlas')}
          data-testid="archive-tab-atlas"
          style={tab === 'atlas' ? { borderColor: aiColor, color: aiColor } : undefined}
        >
          Atlas memory
        </button>
        <button
          className={`bp-btn ${tab === 'files' ? 'primary' : ''}`}
          onClick={() => setTab('files')}
          data-testid="archive-tab-files"
          style={tab === 'files' ? { borderColor: aiColor, color: aiColor } : undefined}
        >
          Uploaded files
        </button>
      </div>

      {loading && <div className="bp-section"><Loader2 size={14} className="spin" /> Loading…</div>}

      {!loading && tab === 'atlas' && (
        <div className="archive-list" data-testid="archive-list-atlas">
          {archive.length === 0 && <div className="bp-section">No archive entries yet. Upload an artefact or run an intake.</div>}
          {archive.map((e, i) => (
            <div key={e.id || i} className="archive-row" style={{ borderLeftColor: aiColor }}>
              <div className="archive-row-head">
                <FileText size={11} />
                <span className="archive-row-title">{e.filename || e.topic || e.id || 'untitled'}</span>
                <span className="archive-row-tag">{e.classification?.routed_core || e.routed_to || e.kind || ''}</span>
              </div>
              {e.summary && <div className="bp-voice-body">{e.summary}</div>}
              {e.lesson?.summary && <div className="bp-voice-body">{e.lesson.summary.slice(0, 220)}…</div>}
            </div>
          ))}
        </div>
      )}

      {!loading && tab === 'files' && (
        <div className="archive-list" data-testid="archive-list-files">
          {files.length === 0 && <div className="bp-section">No files uploaded. Use the upload button in the HUD top-bar.</div>}
          {files.map((f) => (
            <div key={f.id} className="archive-row" style={{ borderLeftColor: aiColor }}>
              <div className="archive-row-head">
                <FileText size={11} />
                <span className="archive-row-title">{f.filename}</span>
                <span className="archive-row-tag">{f.section || f.ai_persona || ''}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
