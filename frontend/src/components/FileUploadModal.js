import React, { useState, useRef } from 'react';
import { Upload, X, Check, AlertCircle, Loader } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function FileUploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await uploadFile(files[0]);
    }
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      await uploadFile(files[0]);
    }
  };

  const uploadFile = async (file) => {
    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/files/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      setUploadResult(result);
      
      // Call success callback after a delay
      setTimeout(() => {
        onUploadSuccess(result);
        handleClose();
      }, 2000);

    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setUploadResult(null);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="upload-modal-overlay" onClick={handleClose} data-testid="file-upload-modal">
      <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
        <div className="upload-modal-header">
          <h3>📁 Upload File</h3>
          <button className="close-btn-upload" onClick={handleClose} data-testid="file-upload-close">
            <X size={18} />
          </button>
        </div>

        <div className="upload-modal-content">
          {!uploadResult && !error && (
            <>
              <div
                className={`upload-dropzone ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                {uploading ? (
                  <div className="upload-status">
                    <Loader className="spinner" size={48} />
                    <p>Uploading and analyzing...</p>
                  </div>
                ) : (
                  <>
                    <Upload size={48} />
                    <p className="upload-text-primary">Drop file here or click to browse</p>
                    <p className="upload-text-secondary">
                      Documents, Images, Projects, Archives
                    </p>
                    <p className="upload-text-limit">Max 50MB</p>
                  </>
                )}
              </div>
              <input
                ref={fileInputRef}
                type="file"
                style={{ display: 'none' }}
                onChange={handleFileSelect}
                accept="*/*"
              />
            </>
          )}

          {uploadResult && (
            <div className="upload-success">
              <Check size={48} className="success-icon" />
              <h4>Upload Successful!</h4>
              <p className="filename">{uploadResult.filename}</p>
              
              <div className="ai-suggestion">
                <p className="suggestion-label">AI Categorization:</p>
                <div className="suggestion-details">
                  <div className="suggestion-row">
                    <span className="label">AI Persona:</span>
                    <span className="value ai-name">{uploadResult.ai_suggestion.ai_persona.toUpperCase()}</span>
                  </div>
                  <div className="suggestion-row">
                    <span className="label">Section:</span>
                    <span className="value">{uploadResult.ai_suggestion.section}</span>
                  </div>
                  {uploadResult.ai_suggestion.tags.length > 0 && (
                    <div className="suggestion-row">
                      <span className="label">Tags:</span>
                      <div className="tags">
                        {uploadResult.ai_suggestion.tags.map((tag, i) => (
                          <span key={i} className="tag">{tag}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <p className="success-message">✓ File added to {uploadResult.ai_suggestion.ai_persona}'s {uploadResult.ai_suggestion.section}</p>
            </div>
          )}

          {error && (
            <div className="upload-error">
              <AlertCircle size={48} className="error-icon" />
              <h4>Upload Failed</h4>
              <p>{error}</p>
              <button className="retry-btn" onClick={() => setError(null)}>
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
