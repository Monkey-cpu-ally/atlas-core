/* eslint-disable */
import React, { useState } from 'react';
import { Loader2, ClipboardCheck, X, Award } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

/**
 * QuizTaker — inline 5-question quiz UI. Submits free-text answers to the
 * LLM grader on the backend, which returns per-question scores + an
 * aggregated mastery rank that's persisted in the `mastery` collection.
 */
export default function QuizTaker({ lessonId, quiz, persona, accent, onClose }) {
  const [answers, setAnswers] = useState(() => quiz.map((q) => ({ question: q.question, answer: '' })));
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const update = (i, v) => setAnswers((prev) => prev.map((a, idx) => idx === i ? { ...a, answer: v } : a));

  const submit = async () => {
    setBusy(true); setError(null);
    try {
      const res = await fetch(`${BACKEND}/api/learning/lessons/${lessonId}/quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (e) { setError(String(e.message || e)); }
    setBusy(false);
  };

  return (
    <div className="quiz-modal" data-testid="quiz-taker">
      <div className="quiz-modal-head">
        <h3 style={{ color: accent }}><ClipboardCheck size={14} /> Quiz · {persona?.toUpperCase()}</h3>
        <button className="quiz-close" onClick={onClose} data-testid="quiz-close"><X size={14} /></button>
      </div>

      {!result && (
        <>
          {answers.map((a, i) => (
            <div key={i} className="quiz-q" data-testid={`quiz-q-${i}`}>
              <div className="quiz-q-label">Q{i + 1}. {a.question}</div>
              <textarea
                className="bp-textarea"
                rows={2}
                value={a.answer}
                onChange={(e) => update(i, e.target.value)}
                placeholder="Your answer…"
                data-testid={`quiz-answer-${i}`}
              />
            </div>
          ))}
          <div className="bp-actions">
            <button
              className="bp-btn primary"
              onClick={submit}
              disabled={busy || answers.every((a) => !a.answer.trim())}
              style={{ borderColor: accent, color: accent }}
              data-testid="quiz-submit"
            >
              {busy ? <Loader2 size={12} className="spin" /> : <ClipboardCheck size={12} />}
              Submit for grading
            </button>
          </div>
          {error && <div className="bp-error">{error}</div>}
        </>
      )}

      {result && (
        <div className="quiz-result" data-testid="quiz-result">
          <div className="quiz-score" style={{ color: accent }}>
            <Award size={18} />
            <div>
              <div className="quiz-score-num">{result.overall_score}</div>
              <div className="quiz-score-rank">{result.rank}</div>
            </div>
          </div>
          {result.per_question.map((q, i) => (
            <div key={i} className="quiz-feedback" data-testid={`quiz-feedback-${i}`}>
              <div className="quiz-feedback-head">
                <span>Q{i + 1}</span>
                <span style={{ color: accent }}>{q.score}/100</span>
              </div>
              <div className="quiz-feedback-text">{q.feedback}</div>
            </div>
          ))}
          <div className="bp-actions">
            <button className="bp-btn" onClick={onClose} data-testid="quiz-done">Done</button>
          </div>
        </div>
      )}
    </div>
  );
}
