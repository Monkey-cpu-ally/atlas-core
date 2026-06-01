import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Minimize2, Maximize2, Trash2, Volume2, VolumeX, Globe } from 'lucide-react';
import { AI_PERSONAS } from '../data/atlasCore';
import { useTTS } from '../hooks/useTTS';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Native language defaults per persona — matches backend PERSONA_LANGUAGE.
const PERSONA_LANG = {
  ajani:   'zu',     // isiZulu
  minerva: 'yo',     // Yorùbá
  hermes:  'maa',    // Maa (Maasai)
  trinity: 'en',
};

const LANG_OPTIONS = [
  { code: 'en',  label: 'EN', tip: 'English' },
  { code: 'zu',  label: 'ZU', tip: 'isiZulu (Ajani)' },
  { code: 'yo',  label: 'YO', tip: 'Yorùbá (Minerva)' },
  { code: 'maa', label: 'MAA', tip: 'Maa / Maasai (Hermes)' },
];

export default function ChatPanel({ activeAI, onAISwitch }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [speakingMsgId, setSpeakingMsgId] = useState(null);
  const [voiceLang, setVoiceLang] = useState('en');  // user-selectable TTS language
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const abortRef = useRef(null);
  const tts = useTTS();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  // When the user switches the active AI, snap the TTS language to that
  // persona's native default. Architect can still override via picker.
  useEffect(() => {
    setVoiceLang(PERSONA_LANG[activeAI] || 'en');
  }, [activeAI]);

  // Abort any in-flight chat request on unmount so closing the panel
  // mid-generation does not leak an LLM call.
  useEffect(() => () => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    tts.stop();
  }, [tts]);

  const sendMessage = async () => {
    if (!inputText.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(`${API_URL}/api/chat/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          persona: activeAI,
          message: inputText,
          conversation_id: conversationId
        })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();
      if (abortRef.current !== controller) return;   // aborted mid-flight

      setConversationId(data.conversation_id);

      const aiMessage = {
        id: data.timestamp,
        role: 'assistant',
        content: data.response,
        persona: data.persona,
        timestamp: data.timestamp
      };

      setMessages(prev => [...prev, aiMessage]);

      // Speak the response in the persona's voice when voice is enabled.
      if (voiceEnabled) {
        setSpeakingMsgId(aiMessage.id);
        tts.speak(data.response, data.persona, {
          language: voiceLang,
          onEnd: () => setSpeakingMsgId(null),
        });
      }
    } catch (error) {
      if (error?.name === 'AbortError') return;     // unmounted / cancelled
      // eslint-disable-next-line no-console
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        persona: activeAI,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      if (abortRef.current === controller) abortRef.current = null;
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId(null);
  };

  const getAIColor = (persona) => {
    return AI_PERSONAS[persona]?.color || '#999';
  };

  const getAIName = (persona) => {
    return AI_PERSONAS[persona]?.name || persona;
  };

  if (!isOpen) {
    return (
      <button
        className="chat-fab"
        onClick={() => setIsOpen(true)}
        title="Chat with AI"
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  return (
    <div className={`chat-panel ${isMinimized ? 'minimized' : ''}`}>
      <div className="chat-header" style={{ borderColor: getAIColor(activeAI) }}>
        <div className="chat-header-left">
          <MessageCircle size={18} style={{ color: getAIColor(activeAI) }} />
          <div className="chat-ai-name">
            <span style={{ color: getAIColor(activeAI) }}>
              {getAIName(activeAI)}
            </span>
            <span className="chat-status">Online</span>
          </div>
        </div>
        
        <div className="chat-header-actions">
          {voiceEnabled && (
            <div className="chat-lang-picker" title="Voice language" data-testid="chat-lang-picker">
              <Globe size={14} style={{ opacity: 0.6, marginRight: 4 }} />
              {LANG_OPTIONS.map((opt) => (
                <button
                  key={opt.code}
                  className={`chat-lang-btn ${voiceLang === opt.code ? 'active' : ''}`}
                  onClick={() => setVoiceLang(opt.code)}
                  title={opt.tip}
                  data-testid={`chat-lang-${opt.code}`}
                  style={voiceLang === opt.code ? { color: getAIColor(activeAI), borderColor: getAIColor(activeAI) } : undefined}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}
          <button
            onClick={() => {
              if (voiceEnabled && speakingMsgId) {
                tts.stop();
                setSpeakingMsgId(null);
              }
              setVoiceEnabled(!voiceEnabled);
            }}
            title={voiceEnabled ? 'Mute AI voice' : 'Enable AI voice'}
            data-testid="chat-voice-toggle"
          >
            {voiceEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
          </button>
          <button onClick={clearConversation} title="Clear chat">
            <Trash2 size={16} />
          </button>
          <button onClick={() => setIsMinimized(!isMinimized)}>
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          <button onClick={() => setIsOpen(false)}>
            <X size={18} />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="chat-empty-state">
                <MessageCircle size={48} style={{ color: getAIColor(activeAI) }} />
                <p>Start a conversation with {getAIName(activeAI)}</p>
                <p className="chat-hint">Ask about {AI_PERSONAS[activeAI]?.domain || 'anything'}</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`chat-message ${msg.role === 'user' ? 'user' : 'ai'}`}
                >
                  {msg.role === 'assistant' && (
                    <div 
                      className="chat-avatar"
                      style={{ borderColor: getAIColor(msg.persona || activeAI) }}
                    >
                      {(getAIName(msg.persona || activeAI)[0] || 'A').toUpperCase()}
                    </div>
                  )}
                  <div 
                    className="chat-bubble"
                    style={{
                      borderColor: msg.role === 'assistant' ? getAIColor(msg.persona || activeAI) : undefined
                    }}
                  >
                    {msg.content}
                  </div>
                  {msg.role === 'user' && (
                    <div className="chat-avatar user-avatar">YOU</div>
                  )}
                </div>
              ))
            )}
            {loading && (
              <div className="chat-message ai">
                <div 
                  className="chat-avatar"
                  style={{ borderColor: getAIColor(activeAI) }}
                >
                  {(getAIName(activeAI)[0] || 'A').toUpperCase()}
                </div>
                <div className="chat-bubble typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <textarea
              ref={inputRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Ask ${getAIName(activeAI)} anything...`}
              rows={1}
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !inputText.trim()}
              className="chat-send-btn"
              style={{ color: getAIColor(activeAI) }}
            >
              <Send size={20} />
            </button>
          </div>
        </>
      )}
    </div>
  );
}
