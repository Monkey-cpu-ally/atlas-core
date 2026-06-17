/* eslint-disable -- archived legacy component, see _legacy/README.md */
import React, { useState, useEffect, useCallback } from 'react';
import { Folder, File, Download, Trash2, X, RefreshCw, BookOpen, Loader2, Library } from 'lucide-react';
import { AI_PERSONAS } from '../data/atlasCore';
import { useAtlasJob } from '../hooks/useAtlasJob';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CORE_COLORS = {
  ajani:   '#F03246',
  minerva: '#28C8BE',
  hermes:  '#E0E0EA',
  trinity: '#A878E6',
};

/**
 * FileBrowserPanel
 * ----------------
 * Two tabs:
 *   • Files       — legacy uploads from /api/files/list
 *   • Atlas Archive — classified knowledge from /api/atlas/archive/list,
 *                     with a per-entry "Teach this" button that fires
 *                     /api/atlas/teach using the entry's summary as
 *                     teaching context.
 *
 * The HUD visuals are not touched; this is purely panel content.
 */
export default function FileBrowserPanel({ isOpen, onClose, filterAI, filterSection }) {
  const [tab, setTab] = useState('files');   // 'files' | 'archive'

  // --- Files tab state -----------------------------------------------------
  const [files, setFiles] = useState([]);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [selectedAI, setSelectedAI] = useState(filterAI || 'all');
  const [selectedSection, setSelectedSection] = useState(filterSection || 'all');

  // --- Archive tab state ---------------------------------------------------
  const [archive, setArchive] = useState([]);
  const [loadingArchive, setLoadingArchive] = useState(false);
  const [archiveCore, setArchiveCore] = useState('all');
  const [teachTarget, setTeachTarget] = useState(null);  // archive entry being taught
  const teachJob = useAtlasJob();

  // --- Loaders -------------------------------------------------------------
  const fetchFiles = useCallback(async () => {
    setLoadingFiles(true);
    try {
      let url = `${API_URL}/api/files/list?limit=100`;
      if (selectedAI && selectedAI !== 'all') url += `&ai_persona=${selectedAI}`;
      if (selectedSection && selectedSection !== 'all') url += `&section=${selectedSection}`;
      const r = await fetch(url);
      const data = await r.json();
      setFiles(data);
    } catch (e) { /* eslint-disable-next-line no-console */ console.error('files fetch:', e); }
    finally { setLoadingFiles(false); }
  }, [selectedAI, selectedSection]);

  const fetchArchive = useCallback(async () => {
    setLoadingArchive(true);
    try {
      const q = archiveCore !== 'all' ? `?core=${archiveCore}` : '';
      const r = await fetch(`${API_URL}/api/atlas/archive/list${q}`);
      const data = await r.json();
      setArchive(data.entries || []);
    } catch (e) { /* eslint-disable-next-line no-console */ console.error('archive fetch:', e); }
    finally { setLoadingArchive(false); }
  }, [archiveCore]);

  useEffect(() => {
    if (!isOpen) return;
    if (tab === 'files') fetchFiles();
    else fetchArchive();
  }, [isOpen, tab, fetchFiles, fetchArchive]);

  // --- Files actions -------------------------------------------------------
  const handleDownload = async (file) => {
    try {
      const r = await fetch(`${API_URL}/api/files/download/${file.id}`);
      const blob = await r.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = file.filename;
      document.body.appendChild(a); a.click();
      window.URL.revokeObjectURL(url); document.body.removeChild(a);
    } catch (e) { /* eslint-disable-next-line no-console */ console.error('download:', e); }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) return;
    try {
      await fetch(`${API_URL}/api/files/${fileId}`, { method: 'DELETE' });
      fetchFiles();
    } catch (e) { /* eslint-disable-next-line no-console */ console.error('delete:', e); }
  };

  // --- Archive actions -----------------------------------------------------
  const teachThisDoc = (entry) => {
    setTeachTarget(entry);
    teachJob.run('/api/atlas/teach', {
      topic: entry.summary || entry.filename,
      core: entry.classified_core,
      context: `From archived document "${entry.filename}":\n${entry.excerpt || ''}`,
    });
  };

  // --- Format helpers ------------------------------------------------------
  const formatFileSize = (bytes) => {
    if (!bytes && bytes !== 0) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };
  const formatDate = (iso) => {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
  };
  const getAIColor = (aiPersona) => AI_PERSONAS[aiPersona]?.color || '#999';

  if (!isOpen) return null;

  return (
    <div className="side-panel file-browser-panel visible" data-testid="file-browser-panel">
      <div className="panel-header">
        <div className="panel-title">
          <Folder size={16} />
          <h2>File Manager</h2>
        </div>
        <button className="close-btn" onClick={onClose} data-testid="file-browser-close">
          <X size={18} />
        </button>
      </div>

      {/* Tab bar */}
      <div className="fb-tabs">
        <button
          className={`fb-tab ${tab === 'files' ? 'active' : ''}`}
          onClick={() => setTab('files')}
          data-testid="fb-tab-files"
        >
          <Folder size={13} /> Files
        </button>
        <button
          className={`fb-tab ${tab === 'archive' ? 'active' : ''}`}
          onClick={() => setTab('archive')}
          data-testid="fb-tab-archive"
        >
          <Library size={13} /> Atlas Archive
        </button>
      </div>

      {/* --- Tab: Files --- */}
      {tab === 'files' && (
        <>
          <div className="panel-filters">
            <div className="filter-group">
              <label>AI Persona:</label>
              <select value={selectedAI} onChange={(e) => setSelectedAI(e.target.value)}>
                <option value="all">All AIs</option>
                <option value="ajani">Ajani</option>
                <option value="minerva">Minerva</option>
                <option value="hermes">Hermes</option>
                <option value="trinity">Trinity</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Section:</label>
              <select value={selectedSection} onChange={(e) => setSelectedSection(e.target.value)}>
                <option value="all">All Sections</option>
                <option value="projects">Projects</option>
                <option value="lab">Lab</option>
                <option value="subjects">Subjects</option>
                <option value="blueprints">Blueprints</option>
                <option value="archives">Archives</option>
              </select>
            </div>
            <button className="refresh-btn" onClick={fetchFiles} title="Refresh">
              <RefreshCw size={16} />
            </button>
          </div>

          <div className="panel-content file-list">
            {loadingFiles ? (
              <div className="loading-state">Loading files...</div>
            ) : files.length === 0 ? (
              <div className="empty-state">
                <Folder size={48} />
                <p>No files uploaded yet</p>
              </div>
            ) : (
              files.map((file) => (
                <div key={file.id} className="file-item">
                  <div className="file-icon">
                    <File size={20} style={{ color: getAIColor(file.ai_persona) }} />
                  </div>
                  <div className="file-info">
                    <div className="file-name">{file.filename}</div>
                    <div className="file-meta">
                      <span className="ai-badge" style={{ color: getAIColor(file.ai_persona) }}>
                        {file.ai_persona.toUpperCase()}
                      </span>
                      <span className="section-badge">{file.section}</span>
                      <span className="file-size">{formatFileSize(file.file_size)}</span>
                    </div>
                    {file.tags && file.tags.length > 0 && (
                      <div className="file-tags">
                        {file.tags.map((tag, i) => <span key={i} className="file-tag">#{tag}</span>)}
                      </div>
                    )}
                    <div className="file-date">{formatDate(file.uploaded_at)}</div>
                  </div>
                  <div className="file-actions">
                    <button className="file-action-btn" onClick={() => handleDownload(file)} title="Download">
                      <Download size={16} />
                    </button>
                    <button className="file-action-btn delete" onClick={() => handleDelete(file.id)} title="Delete">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}

      {/* --- Tab: Atlas Archive --- */}
      {tab === 'archive' && (
        <>
          <div className="panel-filters">
            <div className="filter-group">
              <label>Routed core:</label>
              <select
                value={archiveCore}
                onChange={(e) => setArchiveCore(e.target.value)}
                data-testid="fb-archive-core-filter"
              >
                <option value="all">All cores</option>
                <option value="ajani">Ajani</option>
                <option value="minerva">Minerva</option>
                <option value="hermes">Hermes</option>
              </select>
            </div>
            <button className="refresh-btn" onClick={fetchArchive} title="Refresh">
              <RefreshCw size={16} />
            </button>
          </div>

          <div className="panel-content file-list" data-testid="fb-archive-list">
            {loadingArchive ? (
              <div className="loading-state">Loading archive...</div>
            ) : archive.length === 0 ? (
              <div className="empty-state">
                <Library size={48} />
                <p>No documents archived yet.<br />Upload a PDF / ZIP to populate.</p>
              </div>
            ) : (
              archive.map((entry, idx) => {
                const color = CORE_COLORS[entry.classified_core] || '#999';
                const isTeachingThis =
                  teachTarget?.filename === entry.filename &&
                  (teachJob.status === 'pending' || teachJob.status === 'running');
                return (
                  <div key={idx} className="file-item archive-item" data-testid="fb-archive-item">
                    <div className="file-icon">
                      <Library size={20} style={{ color }} />
                    </div>
                    <div className="file-info">
                      <div className="file-name">{entry.filename}</div>
                      <div className="file-meta">
                        <span className="ai-badge" style={{ color }}>
                          {entry.classified_core?.toUpperCase()}
                        </span>
                        <span className="section-badge">{entry.domain}</span>
                        {entry.page_count != null && (
                          <span className="file-size">{entry.page_count}p</span>
                        )}
                        <span className="file-size">{formatFileSize(entry.bytes_size)}</span>
                      </div>
                      <div className="archive-summary">{entry.summary}</div>
                      {entry.open_questions?.length > 0 && (
                        <div className="file-tags">
                          {entry.open_questions.slice(0, 3).map((q, i) => (
                            <span key={i} className="file-tag">?{q.slice(0, 60)}</span>
                          ))}
                        </div>
                      )}
                      <div className="file-date">{formatDate(entry.ts)}</div>
                    </div>
                    <div className="file-actions">
                      <button
                        className="file-action-btn"
                        onClick={() => teachThisDoc(entry)}
                        disabled={isTeachingThis}
                        title="Teach this document"
                        data-testid="fb-teach-btn"
                      >
                        {isTeachingThis ? <Loader2 size={16} className="spin" /> : <BookOpen size={16} />}
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Inline teach result */}
          {teachTarget && (
            <div className="archive-teach-result" data-testid="fb-teach-result">
              <div className="archive-teach-head">
                <strong>Teach: {teachTarget.filename}</strong>
                <button onClick={() => { teachJob.cancel(); setTeachTarget(null); }} title="Close">
                  <X size={14} />
                </button>
              </div>
              {(teachJob.status === 'pending' || teachJob.status === 'running') && (
                <div className="bp-loading">
                  {teachJob.status === 'pending' ? 'Submitting…' : 'Teaching · 30–90s…'}
                </div>
              )}
              {teachJob.status === 'failed' && (
                <div className="bp-error">Teach failed: {teachJob.error}</div>
              )}
              {teachJob.status === 'done' && teachJob.result && (
                <div className="archive-teach-body">
                  <div className="bp-key" style={{ marginBottom: 4 }}>
                    Taught by {teachJob.result.teacher?.toUpperCase()}
                  </div>
                  <div className="bp-voice-body">{teachJob.result.lesson}</div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {(tab === 'files' ? files.length : archive.length) > 0 && (
        <div className="panel-footer">
          <p>
            {tab === 'files' ? files.length : archive.length}{' '}
            {tab === 'files' ? 'file' : 'archive entr'}
            {tab === 'files'
              ? (files.length === 1 ? '' : 's')
              : (archive.length === 1 ? 'y' : 'ies')
            } found
          </p>
        </div>
      )}
    </div>
  );
}
