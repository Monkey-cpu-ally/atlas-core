import React, { useState } from 'react';
import { Loader2, BookOpen } from 'lucide-react';
import { useAtlasJob } from '../../hooks/useAtlasJob';

const BAND_META = {
  simple:      { label: 'Simple understanding',      color: '#9CD3FF' },
  systems:     { label: 'Systems understanding',     color: '#28C8BE' },
  advanced:    { label: 'Advanced understanding',    color: '#F03246' },
  speculative: { label: 'Speculative / Research',    color: '#B388FF' },
};

// Crude split of a markdown lesson into per-band sections by H3 heading.
function splitLesson(markdown) {
  if (!markdown) return {};
  const sections = {};
  const re = /^###\s+(SIMPLE|SYSTEMS|ADVANCED|SPECULATIVE)\b\s*$/gim;
  const indices = [];
  let match;
  while ((match = re.exec(markdown)) !== null) {
    indices.push({ name: match[1].toLowerCase(), start: match.index, headerLen: match[0].length });
  }
  for (let i = 0; i < indices.length; i++) {
    const cur = indices[i];
    const next = indices[i + 1];
    const bodyStart = cur.start + cur.headerLen;
    const bodyEnd = next ? next.start : markdown.length;
    sections[cur.name] = markdown.slice(bodyStart, bodyEnd).trim();
  }
  return sections;
}

/**
 * TeachingWorkbench — drives /api/atlas/teach. Submits a background job
 * and polls until the 4-band lesson is ready.
 */
export default function TeachingWorkbench({ aiColor }) {
  const [topic, setTopic] = useState('');
  const job = useAtlasJob();
  const busy = job.status === 'pending' || job.status === 'running';
  const lesson = job.status === 'done' ? job.result : null;

  const onTeach = () => {
    if (!topic.trim()) return;
    job.run('/api/atlas/teach', { topic });
  };

  const sections = lesson?.lesson ? splitLesson(lesson.lesson) : {};

  return (
    <div className="bp-workbench" data-testid="teaching-workbench">
      <h3 className="bp-title">Teaching Engine</h3>
      <p className="bp-help">
        Type any subject. The council picks the right lead core, applies
        the ATLAS teaching law, and returns four nested depths.
      </p>

      <textarea
        className="bp-textarea"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="e.g. How do enzymes work? · What is entropy? · Why do bridges resonate?"
        rows={3}
        data-testid="teach-topic-input"
      />

      <div className="bp-actions">
        <button
          className="bp-btn primary"
          style={{ borderColor: aiColor, color: aiColor }}
          onClick={onTeach}
          disabled={!topic.trim() || busy}
          data-testid="teach-btn"
        >
          {busy ? <Loader2 size={14} className="spin" /> : <BookOpen size={14} />}
          Teach Me
        </button>
      </div>

      {busy && (
        <div className="bp-section bp-loading">
          {job.status === 'pending'
            ? 'Submitting job…'
            : 'The teaching engine is working · 30–90 seconds.'}
        </div>
      )}

      {job.status === 'failed' && (
        <div className="bp-error">Teaching job failed: {job.error}</div>
      )}

      {lesson && !lesson.error && (
        <div className="bp-section" data-testid="teach-output">
          <h4>
            Taught by {lesson.teacher?.toUpperCase()}
            {lesson.lead_via_council ? ' · selected by council' : ''}
          </h4>
          {Object.keys(BAND_META).map((band) => {
            const body = sections[band];
            if (!body) return null;
            const meta = BAND_META[band];
            return (
              <details key={band} className="bp-phase" open={band === 'simple'}>
                <summary style={{ color: meta.color }}>{meta.label}</summary>
                <div className="bp-voice-body">{body}</div>
              </details>
            );
          })}
          {Object.keys(sections).length === 0 && (
            <div className="bp-voice-body">{lesson.lesson}</div>
          )}
        </div>
      )}
      {lesson?.error && (
        <div className="bp-error">{lesson.error}</div>
      )}
    </div>
  );
}
