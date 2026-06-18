/* eslint-disable */
import React, { useEffect, useRef, useState } from 'react';
import { X, Send, Loader2, Trash2, MessagesSquare, Bot } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// AI face dock uses 'trinity' as the slug for the Council card; persona-chat
// API expects 'council'. Map at the boundary so the rest of the HUD doesn't
// have to change.
function _normalizePersona(slug) {
  return slug === 'trinity' ? 'council' : slug;
}

// localStorage key — one sticky session per persona so closing + reopening
// the panel resumes the conversation. Cleared when the user hits "new chat".
function _sessionKey(persona) {
  return `atlas.persona.session.${persona}`;
}

/**
 * PersonaChatPanel — Phase 8e.
 *
 * Dedicated chat panel for one persona at a time. Pulls the persona's
 * registry entry from /api/persona/list, holds a sticky session-id in
 * localStorage, and posts to /api/persona/{persona}/chat.
 *
 * The architect's contract:
 *   - Each persona pulls persona-specific memories ✅ (server-side)
 *   - Each persona pulls relevant Knowledge Bank entries ✅ (server-side)
 *   - Uses its own prompt / personality ✅ (server-side voice_prompt)
 *   - Saves conversations back into Memory Bank ✅ (server-side mirror)
 *   - Supports future voice integration ✅ (transcript bar already shows the
 *     last reply; could be wired to TTS in a follow-up)
 *   - Supports future HUD panels ✅ (this IS the HUD panel)
 *
 * UI: docked on the right side, full-height. Council panel (when persona
 * === 'council') additionally renders the 3 sub-voices in collapsed cards
 * above the synthesised reply.
 */
export default function PersonaChatPanel({ open, persona, onClose }) {
  const normalized = _normalizePersona(persona);

  const [info, setInfo] = useState(null);                // PersonaInfo from /list
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);          // {role, content, council_voices?, id}
  const [input, setInput] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(null);
  const [showVoices, setShowVoices] = useState({});      // message_id → bool
  const bodyRef = useRef(null);

  // Load persona info once.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(`${API_URL}/api/persona/list`);
        const all = await r.json();
        if (cancelled) return;
        const me = (Array.isArray(all) ? all : []).find((p) => p.slug === normalized);
        setInfo(me || null);
      } catch (e) {
        // fall back to minimal info — UI will still render
        setInfo({ slug: normalized, name: normalized, color: '#F4EFE4', domain: '', one_liner: '' });
      }
    })();
    return () => { cancelled = true; };
  }, [normalized]);

  // Hydrate the sticky session for this persona.
  useEffect(() => {
    if (!open || !normalized) return;
    setError(null);
    const stored = window.localStorage?.getItem(_sessionKey(normalized));
    if (!stored) {
      setSessionId(null); setMessages([]); return;
    }
    setSessionId(stored);
    // Pull the transcript for this session
    fetch(`${API_URL}/api/persona/sessions/${stored}`)
      .then((r) => r.json().then((j) => ({ ok: r.ok, body: j })))
      .then(({ ok, body }) => {
        if (!ok) {
          // Session may have been deleted server-side — wipe local pointer.
          window.localStorage?.removeItem(_sessionKey(normalized));
          setSessionId(null); setMessages([]); return;
        }
        setMessages((body.messages || []).map((m) => ({
          id: m.id, role: m.role, content: m.content,
          provider_used: m.provider_used, model_used: m.model_used,
        })));
      })
      .catch(() => { /* keep empty */ });
  }, [open, normalized]);

  // Scroll to bottom on new message.
  useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [messages, pending]);

  const startNewChat = () => {
    window.localStorage?.removeItem(_sessionKey(normalized));
    setSessionId(null); setMessages([]); setError(null);
  };

  const send = async () => {
    const text = (input || '').trim();
    if (!text || pending) return;
    setPending(true); setError(null);
    setMessages((prev) => [...prev, { id: `local-${Date.now()}`, role: 'user', content: text }]);
    setInput('');
    try {
      const r = await fetch(`${API_URL}/api/persona/${normalized}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId || undefined,
          memory_top_k: 3,
          knowledge_top_k: 3,
        }),
      });
      const body = await r.json();
      if (!r.ok) {
        setError(body.detail || `chat failed (${r.status})`);
        return;
      }
      if (!sessionId) {
        setSessionId(body.session_id);
        try { window.localStorage?.setItem(_sessionKey(normalized), body.session_id); } catch (_) {}
      }
      setMessages((prev) => [
        ...prev,
        {
          id: body.message_id, role: 'assistant', content: body.reply,
          provider_used: body.provider_used, model_used: body.model_used,
          council_voices: body.council_voices || [],
          cited_memory_ids: body.cited_memory_ids || [],
          cited_knowledge_ids: body.cited_knowledge_ids || [],
        },
      ]);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setPending(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  if (!open) return null;
  const accent = info?.color || '#F4EFE4';

  return (
    <div
      className="persona-chat-panel"
      data-testid={`persona-chat-${normalized}`}
      style={{ '--persona-accent': accent }}
      role="dialog"
      aria-label={`Chat with ${info?.name || normalized}`}
    >
      <header className="persona-chat-head">
        <div className="persona-chat-head-meta">
          <Bot size={14} />
          <strong>{info?.name || normalized}</strong>
          {info?.domain && <span className="persona-chat-domain">{info.domain}</span>}
        </div>
        <div className="persona-chat-head-actions">
          <button
            type="button"
            className="persona-chat-iconbtn"
            onClick={startNewChat}
            title="New conversation (current session log discarded; persona keeps its memories)"
            data-testid={`persona-chat-new-${normalized}`}
          >
            <Trash2 size={11} />
          </button>
          <button
            type="button"
            className="persona-chat-iconbtn"
            onClick={onClose}
            title="Close"
            data-testid={`persona-chat-close-${normalized}`}
          >
            <X size={13} />
          </button>
        </div>
      </header>

      {info?.one_liner && (
        <div className="persona-chat-one-liner">{info.one_liner}</div>
      )}

      <div ref={bodyRef} className="persona-chat-body" data-testid={`persona-chat-body-${normalized}`}>
        {messages.length === 0 && !pending && (
          <div className="persona-chat-empty">
            Start a conversation. {info?.name || 'The persona'} pulls from
            their tagged Memory Bank entries and recent Knowledge Bank
            sources every turn.
          </div>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`persona-chat-msg is-${m.role}`}>
            {m.role === 'user' ? (
              <div className="persona-chat-bubble user">{m.content}</div>
            ) : (
              <>
                {/* Council sub-voices (collapsed by default) */}
                {Array.isArray(m.council_voices) && m.council_voices.length > 0 && (
                  <div className="persona-chat-voices">
                    <button
                      type="button"
                      className="persona-chat-voices-toggle"
                      onClick={() => setShowVoices((s) => ({ ...s, [m.id]: !s[m.id] }))}
                    >
                      <MessagesSquare size={10} /> {showVoices[m.id] ? 'hide' : 'show'} {m.council_voices.length} sub-voices
                    </button>
                    {showVoices[m.id] && (
                      <div className="persona-chat-voices-list">
                        {m.council_voices.map((v) => (
                          <div
                            key={v.persona}
                            className="persona-chat-voice"
                            data-testid={`council-subvoice-${v.persona}`}
                          >
                            <div className="persona-chat-voice-head">
                              {v.persona} {v.model_used && <span className="muted">· {v.model_used}</span>}
                            </div>
                            <div className="persona-chat-voice-text">{v.text}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                <div className="persona-chat-bubble assistant">
                  {m.content}
                  {(m.model_used || m.provider_used) && (
                    <div className="persona-chat-bubble-meta">
                      {m.provider_used} {m.model_used && `· ${m.model_used}`}
                      {(m.cited_memory_ids?.length || m.cited_knowledge_ids?.length) ? (
                        <> · cited {m.cited_memory_ids?.length || 0}mem · {m.cited_knowledge_ids?.length || 0}kb</>
                      ) : null}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        ))}

        {pending && (
          <div className="persona-chat-msg is-pending">
            <div className="persona-chat-bubble assistant pending">
              <Loader2 size={12} className="spin" /> thinking…
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="persona-chat-error" data-testid={`persona-chat-error-${normalized}`}>{error}</div>
      )}

      <footer className="persona-chat-foot">
        <textarea
          className="persona-chat-input"
          data-testid={`persona-chat-input-${normalized}`}
          placeholder={`Message ${info?.name || normalized}… (Enter to send · Shift+Enter newline)`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={pending}
          rows={2}
        />
        <button
          type="button"
          className="persona-chat-send"
          data-testid={`persona-chat-send-${normalized}`}
          onClick={send}
          disabled={pending || !(input || '').trim()}
          title="Send (Enter)"
        >
          {pending ? <Loader2 size={13} className="spin" /> : <Send size={13} />}
        </button>
      </footer>
    </div>
  );
}
