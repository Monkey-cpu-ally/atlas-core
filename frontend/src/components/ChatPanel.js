import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Minimize2, Maximize2, Trash2 } from 'lucide-react';
import { AI_PERSONAS } from '../data/atlasCore';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ChatPanel({ activeAI, onAISwitch }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

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

    try {
      const response = await fetch(`${API_URL}/api/chat/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona: activeAI,
          message: inputText,
          conversation_id: conversationId
        })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();
      
      setConversationId(data.conversation_id);
      
      const aiMessage = {
        role: 'assistant',
        content: data.response,
        persona: data.persona,
        timestamp: data.timestamp
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        persona: activeAI,
        timestamp: new Date().toISOString()
      }]);
    } finally {
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
