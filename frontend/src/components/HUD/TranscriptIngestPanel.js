/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState, useCallback } from 'react';
import {
  X, ExternalLink, Loader2, Check, AlertCircle, Youtube,
  GraduationCap, Network, Database,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AGENT_OPTIONS = ['minerva', 'ajani', 'hermes', 'council'];

/**
 * TranscriptIngestPanel — paste a YouTube transcript, walk the full
 * KB → MB → Graph → Lesson chain via /api/youtube/ingest-transcript.
 *
 * Two-pane layout in one right-docked panel:
 *   - LEFT pane: paste form (video_url, title, channel, agent, transcript)
 *   - RIGHT pane: most recent ingest result (IDs + lesson preview) + the
 *                 dashboard verdict updated live every time the user submits.
 *
 * Storage rule reminder shown to the user: full transcript stays only in
 * the private youtube_transcripts_private collection; the public KB stores
 * the distillation summary only.
 */
export default function TranscriptIngestPanel({ open, onClose }) {
  const [form, setForm] = useState({
    video_url: '',
    video_title: '',
    channel_name: '',
    channel_url: '',
    transcript_text: '',
    force_agent: 'minerva',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [verdict, setVerdict] = useState(null);

  const refreshVerdict = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/api/youtube/dashboard`);
      if (!r.ok) return;
      const j = await r.json();
      setVerdict({
        verdict: j.verdict,
        knowledge_total: j.youtube_knowledge_total,
        manual_provided: (j.youtube_knowledge_by_status || {}).MANUAL_PROVIDED || 0,
        unavailable: (j.youtube_knowledge_by_status || {}).TRANSCRIPT_UNAVAILABLE || 0,
        lessons: j.lessons_from_youtube_count,
        graph_edges: j.graph_edges_youtube_related,
      });
    } catch (e) { /* ignore */ }
  }, []);

  useEffect(() => {
    if (open) refreshVerdict();
  }, [open, refreshVerdict]);

  if (!open) return null;

  const update = (k, v) => setForm((prev) => ({ ...prev, [k]: v }));

  const canSubmit =
    form.video_url.trim().length > 8 &&
    form.transcript_text.trim().length >= 40;

  async function submit() {
    if (!canSubmit) return;
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const body = {
        video_url: form.video_url.trim(),
        transcript_text: form.transcript_text.trim(),
        video_title: form.video_title.trim() || null,
        channel_name: form.channel_name.trim() || null,
        channel_url: form.channel_url.trim() || null,
        generate_lesson: true,
        force_agent: form.force_agent,
      };
      const r = await fetch(`${API_URL}/api/youtube/ingest-transcript`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const j = await r.json();
      if (!r.ok || j.ok === false) {
        throw new Error(j.detail || j.error || `HTTP ${r.status}`);
      }
      setResult(j);
      refreshVerdict();
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setSubmitting(false);
    }
  }

  async function resolveLatest() {
    if (!form.channel_url.trim()) return;
    setError(null);
    try {
      const r = await fetch(
        `${API_URL}/api/youtube/resolve-channel?url=${encodeURIComponent(form.channel_url.trim())}&n=3`,
      );
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      if (j.videos && j.videos.length > 0) {
        const v = j.videos[0];
        setForm((prev) => ({
          ...prev,
          video_url: v.url,
          video_title: v.title,
          channel_name: j.channel_title || prev.channel_name,
        }));
      } else {
        setError('Channel resolver returned 0 videos');
      }
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  return (
    <div className="transcript-panel-shell" data-testid="transcript-ingest-panel">
      <div className="transcript-panel">
        <header className="transcript-panel-head">
          <div className="transcript-title">
            <Youtube size={16} />
            <span>YouTube Transcript Ingest</span>
          </div>
          <button
            type="button"
            className="transcript-close"
            onClick={onClose}
            aria-label="Close"
            data-testid="transcript-ingest-close"
          >
            <X size={16} />
          </button>
        </header>

        {verdict && (
          <div className="transcript-verdict" data-testid="transcript-verdict">
            <span className="transcript-verdict-line">{verdict.verdict}</span>
            <div className="transcript-verdict-counts">
              <span title="MANUAL_PROVIDED knowledge entries">
                <Check size={11} /> {verdict.manual_provided} real
              </span>
              <span title="TRANSCRIPT_UNAVAILABLE stubs">
                <AlertCircle size={11} /> {verdict.unavailable} stub
              </span>
              <span title="Lessons sourced from YouTube">
                <GraduationCap size={11} /> {verdict.lessons} lesson{verdict.lessons === 1 ? '' : 's'}
              </span>
              <span title="Graph edges touching YouTube">
                <Network size={11} /> {verdict.graph_edges} edges
              </span>
            </div>
          </div>
        )}

        <div className="transcript-body">
          {/* form pane */}
          <section className="transcript-form">
            <label className="t-row">
              <span>Channel URL <em>(optional · click resolve to autofill latest video)</em></span>
              <div className="t-row-inline">
                <input
                  type="url"
                  placeholder="https://www.youtube.com/c/SebastianLague/videos"
                  value={form.channel_url}
                  onChange={(e) => update('channel_url', e.target.value)}
                  data-testid="transcript-channel-url"
                />
                <button
                  type="button"
                  className="t-resolve-btn"
                  onClick={resolveLatest}
                  disabled={!form.channel_url.trim() || submitting}
                  title="Fetch latest video via channel RSS feed"
                  data-testid="transcript-resolve-btn"
                >
                  <ExternalLink size={12} /> resolve
                </button>
              </div>
            </label>

            <label className="t-row">
              <span>Video URL <em>(required)</em></span>
              <input
                type="url"
                placeholder="https://www.youtube.com/watch?v=…"
                value={form.video_url}
                onChange={(e) => update('video_url', e.target.value)}
                data-testid="transcript-video-url"
              />
            </label>

            <div className="t-row-grid">
              <label className="t-row">
                <span>Video title</span>
                <input
                  type="text"
                  placeholder="optional"
                  value={form.video_title}
                  onChange={(e) => update('video_title', e.target.value)}
                  data-testid="transcript-video-title"
                />
              </label>
              <label className="t-row">
                <span>Channel name</span>
                <input
                  type="text"
                  placeholder="optional"
                  value={form.channel_name}
                  onChange={(e) => update('channel_name', e.target.value)}
                  data-testid="transcript-channel-name"
                />
              </label>
            </div>

            <label className="t-row">
              <span>Route to ATLAS persona</span>
              <select
                value={form.force_agent}
                onChange={(e) => update('force_agent', e.target.value)}
                data-testid="transcript-agent-select"
              >
                {AGENT_OPTIONS.map((a) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </label>

            <label className="t-row">
              <span>Transcript text <em>(≥ 40 chars · stored privately, distilled summary only goes to Knowledge Bank)</em></span>
              <textarea
                rows={10}
                placeholder="Paste the YouTube transcript here — from the video's captions panel or your own captioning."
                value={form.transcript_text}
                onChange={(e) => update('transcript_text', e.target.value)}
                data-testid="transcript-text"
              />
              <span className="t-row-counter">
                {form.transcript_text.length.toLocaleString()} chars
                {form.transcript_text.length < 40 && form.transcript_text.length > 0 && (
                  <em className="t-row-warn"> · need ≥ 40</em>
                )}
              </span>
            </label>

            <div className="t-actions">
              <button
                type="button"
                className="t-submit"
                disabled={!canSubmit || submitting}
                onClick={submit}
                data-testid="transcript-submit-btn"
              >
                {submitting ? <Loader2 size={14} className="t-spin" /> : <Database size={14} />}
                <span>{submitting ? 'Distilling…' : 'Ingest transcript'}</span>
              </button>
              {error && <span className="t-err" data-testid="transcript-error">{error}</span>}
            </div>
          </section>

          {/* result pane */}
          <section className="transcript-result" aria-live="polite">
            {!result && !submitting && (
              <div className="t-result-empty">
                Paste a transcript and hit <strong>Ingest</strong>.
                The result will appear here with knowledge / lesson / graph IDs.
              </div>
            )}
            {result && (
              <div data-testid="transcript-result">
                <div className="t-result-line t-ok">
                  <Check size={13} /> ingested · agent: <strong>{result.agent}</strong> · confidence: {result.confidence_score?.toFixed(2)}
                </div>
                <h4>{result.title}</h4>
                <dl className="t-ids">
                  <dt>knowledge_id</dt><dd>{result.knowledge_id}</dd>
                  <dt>memory_bank_id</dt><dd>{result.memory_bank_id}</dd>
                  <dt>lesson_id</dt><dd>{result.lesson_id || '—'}</dd>
                  <dt>private transcript</dt><dd>{result.transcript_private_id}</dd>
                  <dt>concepts</dt><dd>{(result.concepts || []).join(' · ') || '—'}</dd>
                  <dt>graph edges (lesson)</dt><dd>+{result.lesson_graph_edges_added}</dd>
                </dl>
                {result.lesson_title && (
                  <div className="t-lesson-preview">
                    <GraduationCap size={13} />
                    <span><strong>Lesson generated:</strong> {result.lesson_title}</span>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
