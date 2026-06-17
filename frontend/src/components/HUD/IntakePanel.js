/* eslint-disable */
import React, { useState } from 'react';
import { Loader2, Youtube, ClipboardPaste, ClipboardCheck, Hammer } from 'lucide-react';
import QuizTaker from './QuizTaker';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

/**
 * IntakePanel — feed a YouTube URL or pasted transcript into Atlas. The
 * backend routes the topic, builds an AI-styled lesson + quick quiz, and
 * persists into the archive so it can be revisited.
 *
 * YouTube transcript fetching is blocked by YouTube for most cloud IPs,
 * so we offer a paste-transcript fallback alongside.
 */
export default function IntakePanel({ aiColor }) {
  const [mode, setMode] = useState('youtube');    // 'youtube' | 'paste'
  const [url, setUrl] = useState('');
  const [transcript, setTranscript] = useState('');
  const [topic, setTopic] = useState('');
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [quizOpen, setQuizOpen] = useState(false);

  const run = async () => {
    setBusy(true); setError(null); setResult(null);
    try {
      const path = mode === 'youtube' ? '/api/intake/youtube' : '/api/intake/transcript';
      const body = mode === 'youtube'
        ? { url, topic, persist: true }
        : { transcript, topic, source_url: url || null, persist: true };
      const res = await fetch(`${BACKEND}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        // Cloud-IP block → suggest switching to paste mode automatically.
        if (res.status === 503 && (data.detail || '').includes('blocking requests')) {
          setError('YouTube blocks this server\'s IP. Switch to "Paste transcript" mode and drop the transcript directly.');
          setMode('paste');
        } else {
          setError(data.detail || `HTTP ${res.status}`);
        }
      } else {
        setResult(data);
      }
    } catch (e) { setError(String(e.message || e)); }
    setBusy(false);
  };

  const canRun = topic.trim() && (mode === 'youtube' ? url.trim() : transcript.trim().length >= 20);

  return (
    <div className="bp-workbench" data-testid="intake-panel">
      <h3 className="bp-title" style={{ color: aiColor }}><Youtube size={14} /> External Intake</h3>
      <p className="bp-help">
        Drop a YouTube URL or paste any transcript. Council routes the topic
        to a lead AI and produces a quick lesson + a 5-question quiz.
      </p>

      <div className="intake-mode" role="tablist">
        <button
          className={`bp-btn ${mode === 'youtube' ? 'primary' : ''}`}
          onClick={() => { setMode('youtube'); setError(null); }}
          data-testid="intake-mode-youtube"
          style={mode === 'youtube' ? { borderColor: aiColor, color: aiColor } : undefined}
        >
          <Youtube size={12} /> YouTube
        </button>
        <button
          className={`bp-btn ${mode === 'paste' ? 'primary' : ''}`}
          onClick={() => { setMode('paste'); setError(null); }}
          data-testid="intake-mode-paste"
          style={mode === 'paste' ? { borderColor: aiColor, color: aiColor } : undefined}
        >
          <ClipboardPaste size={12} /> Paste transcript
        </button>
      </div>

      <input
        className="bp-textarea"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Topic — e.g. solar cell physics"
        data-testid="intake-topic"
      />

      {mode === 'youtube' ? (
        <input
          className="bp-textarea"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://youtube.com/watch?v=…"
          data-testid="intake-url"
        />
      ) : (
        <textarea
          className="bp-textarea"
          rows={6}
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder="Paste the transcript here…"
          data-testid="intake-transcript"
        />
      )}

      <div className="bp-actions">
        <button
          className="bp-btn primary"
          onClick={run}
          disabled={!canRun || busy}
          data-testid="intake-run-btn"
          style={{ borderColor: aiColor, color: aiColor }}
        >
          {busy ? <Loader2 size={13} className="spin" /> : '⇢'} Ingest
        </button>
      </div>

      {error && <div className="bp-error" data-testid="intake-error">{error}</div>}

      {result && (
        <div className="bp-section" data-testid="intake-result">
          <div className="intake-result-head">
            <span style={{ color: result.display?.color || aiColor, fontFamily: 'Orbitron', letterSpacing: 1 }}>
              {result.assigned_to?.toUpperCase()}
            </span>
            {result.matched_keyword && <span className="intake-kw">matched <em>{result.matched_keyword}</em></span>}
          </div>
          <div className="bp-voice-body">{result.lesson?.summary}</div>
          <div className="intake-concepts">
            {(result.lesson?.key_concepts || []).map((c) => (
              <span key={c} className="cyclo-chip" style={{ borderColor: result.display?.color }}>{c}</span>
            ))}
          </div>

          {/* Full LLM-generated lesson body (if pipeline ran) */}
          {result.pipeline?.lesson?.lesson_text && (
            <details className="bp-phase" data-testid="intake-lesson-full" open>
              <summary style={{ color: aiColor }}>Full lesson · {result.pipeline.lesson.difficulty}</summary>
              <pre className="bp-voice-body intake-lesson-body">{result.pipeline.lesson.lesson_text}</pre>
            </details>
          )}

          {/* Auto-generated project card */}
          {result.pipeline?.project && (
            <details className="bp-phase" data-testid="intake-project-card" open>
              <summary style={{ color: aiColor }}><Hammer size={11} /> Suggested project</summary>
              <div className="bp-voice-body">
                <strong>{result.pipeline.project.title}</strong>
                <div style={{ marginTop: 4 }}>{result.pipeline.project.summary}</div>
                {result.pipeline.project.steps?.length > 0 && (
                  <ol className="project-card-list" style={{ marginTop: 6 }}>
                    {result.pipeline.project.steps.slice(0, 4).map((s, i) => <li key={i}>{s}</li>)}
                  </ol>
                )}
                <div className="intake-pipe-meta">Saved to PROJECTS tile · status: proposed</div>
              </div>
            </details>
          )}

          {result.quiz?.length > 0 && (
            <div className="bp-actions" data-testid="intake-quiz-row">
              <button
                className="bp-btn primary"
                onClick={() => setQuizOpen(true)}
                style={{ borderColor: aiColor, color: aiColor }}
                disabled={!result.pipeline?.lesson_id}
                data-testid="intake-take-quiz"
                title={result.pipeline?.lesson_id ? 'Take the quiz · grades into mastery' : 'Quiz requires the persisted lesson'}
              >
                <ClipboardCheck size={12} /> Take quiz · {result.quiz.length} Qs
              </button>
            </div>
          )}
        </div>
      )}

      {quizOpen && result?.pipeline?.lesson_id && (
        <QuizTaker
          lessonId={result.pipeline.lesson_id}
          quiz={result.quiz}
          persona={result.assigned_to}
          accent={result.display?.color || aiColor}
          onClose={() => setQuizOpen(false)}
        />
      )}
    </div>
  );
}
