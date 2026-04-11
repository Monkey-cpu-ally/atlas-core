import React, { useState, useEffect } from 'react';
import { Folder, File, Download, Trash2, X, RefreshCw } from 'lucide-react';
import { AI_PERSONAS } from '../data/atlasCore';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function FileBrowserPanel({ isOpen, onClose, filterAI, filterSection }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAI, setSelectedAI] = useState(filterAI || 'all');
  const [selectedSection, setSelectedSection] = useState(filterSection || 'all');

  useEffect(() => {
    if (isOpen) {
      fetchFiles();
    }
  }, [isOpen, selectedAI, selectedSection]);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/api/files/list?limit=100`;
      if (selectedAI && selectedAI !== 'all') {
        url += `&ai_persona=${selectedAI}`;
      }
      if (selectedSection && selectedSection !== 'all') {
        url += `&section=${selectedSection}`;
      }

      const response = await fetch(url);
      const data = await response.json();
      setFiles(data);
    } catch (error) {
      console.error('Failed to fetch files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (file) => {
    try {
      const response = await fetch(`${API_URL}/api/files/download/${file.id}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) return;

    try {
      await fetch(`${API_URL}/api/files/${fileId}`, {
        method: 'DELETE',
      });
      fetchFiles(); // Refresh list
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getAIColor = (aiPersona) => {
    return AI_PERSONAS[aiPersona]?.color || '#999';
  };

  if (!isOpen) return null;

  return (
    <div className="side-panel file-browser-panel visible">
      <div className="panel-header">
        <div className="panel-title">
          <Folder size={16} />
          <h2>File Manager</h2>
        </div>
        <button className="close-btn" onClick={onClose}>
          <X size={18} />
        </button>
      </div>

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
        {loading ? (
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
                    {file.tags.map((tag, i) => (
                      <span key={i} className="file-tag">#{tag}</span>
                    ))}
                  </div>
                )}
                <div className="file-date">{formatDate(file.uploaded_at)}</div>
              </div>
              <div className="file-actions">
                <button
                  className="file-action-btn"
                  onClick={() => handleDownload(file)}
                  title="Download"
                >
                  <Download size={16} />
                </button>
                <button
                  className="file-action-btn delete"
                  onClick={() => handleDelete(file.id)}
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {files.length > 0 && (
        <div className="panel-footer">
          <p>{files.length} file{files.length !== 1 ? 's' : ''} found</p>
        </div>
      )}
    </div>
  );
}
