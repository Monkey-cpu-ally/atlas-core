import React, { useState, useCallback, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, AlertTriangle } from 'lucide-react';
import AtlasCore from './HUD/AtlasCore';
import Ring1AI from './HUD/Ring1AIPresence';
import Ring2System from './HUD/Ring2System';
import Ring3Learning from './HUD/Ring3Learning';
import AtlasSidePanel from './HUD/AtlasSidePanel';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';
import { useAudioFeedback } from '../hooks/useAudioFeedback';
import { AI_PERSONAS } from '../data/atlasCore';

// Core states: idle, listening, thinking, speaking, alert
const CORE_STATES = {
  IDLE: 'idle',
  LISTENING: 'listening',
  THINKING: 'thinking',
  SPEAKING: 'speaking',
  ALERT: 'alert'
};

export default function HUDInterface() {
  const [activeAI, setActiveAI] = useState('ajani');
  const [coreState, setCoreState] = useState(CORE_STATES.IDLE);
  const [ring2Rotation, setRing2Rotation] = useState(0);
  const [ring3Rotation, setRing3Rotation] = useState(0);
  const [selectedSystem, setSelectedSystem] = useState(null);
  const [selectedLearning, setSelectedLearning] = useState(null);
  const [panelContent, setPanelContent] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [showLimits, setShowLimits] = useState(false);

  const { playClick, playTone, playSnap, playGlide } = useAudioFeedback(soundEnabled);

  // Handle voice commands
  const handleVoiceCommand = useCallback((command) => {
    const lower = command.toLowerCase();
    setCoreState(CORE_STATES.THINKING);
    
    setTimeout(() => {
      // Check for AI names
      if (lower.includes('ajani')) selectAI('ajani');
      else if (lower.includes('minerva')) selectAI('minerva');
      else if (lower.includes('hermes')) selectAI('hermes');
      else if (lower.includes('council') || lower.includes('trinity')) selectAI('trinity');
      
      setCoreState(CORE_STATES.SPEAKING);
      setTimeout(() => setCoreState(CORE_STATES.IDLE), 2000);
    }, 500);
  }, []);

  const { startListening, stopListening, isSupported } = useVoiceRecognition({
    onResult: (text) => {
      setTranscript(text);
      handleVoiceCommand(text);
    },
    onListeningChange: (listening) => {
      setIsListening(listening);
      setCoreState(listening ? CORE_STATES.LISTENING : CORE_STATES.IDLE);
    }
  });

  const selectAI = useCallback((aiKey) => {
    playTone(AI_PERSONAS[aiKey].color);
    setActiveAI(aiKey);
    setCoreState(CORE_STATES.SPEAKING);
    setTimeout(() => setCoreState(CORE_STATES.IDLE), 2000);
    
    // Show AI info panel
    setPanelContent({ type: 'ai-info', ai: aiKey });
  }, [playTone]);

  const selectSystem = useCallback((systemId) => {
    playClick();
    setSelectedSystem(systemId);
    setPanelContent({ type: 'operation', operation: systemId, ai: activeAI });
    playSnap();
  }, [activeAI, playClick, playSnap]);

  const selectLearning = useCallback((learningId) => {
    playGlide();
    setSelectedLearning(learningId);
    setPanelContent({ type: 'operation', operation: learningId, ai: activeAI });
  }, [activeAI, playGlide]);

  const closePanel = useCallback(() => {
    setPanelContent(null);
    setSelectedSystem(null);
    setSelectedLearning(null);
  }, []);

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Trigger alert state demo
  const triggerAlert = () => {
    setCoreState(CORE_STATES.ALERT);
    setTimeout(() => setCoreState(CORE_STATES.IDLE), 3000);
  };

  const currentAI = AI_PERSONAS[activeAI];

  return (
    <div className="atlas-container">
      {/* Light gradient background */}
      <div className="atlas-background" />
      
      {/* Top Controls */}
      <div className="atlas-controls">
        <button 
          className={`ctrl-btn ${showLimits ? 'active warning' : ''}`}
          onClick={() => setShowLimits(!showLimits)}
        >
          <AlertTriangle size={18} />
        </button>
        {isSupported && (
          <button 
            className={`ctrl-btn ${isListening ? 'active listening' : ''}`}
            onClick={toggleListening}
          >
            {isListening ? <Mic size={18} /> : <MicOff size={18} />}
          </button>
        )}
        <button 
          className={`ctrl-btn ${soundEnabled ? 'active' : ''}`}
          onClick={() => setSoundEnabled(!soundEnabled)}
        >
          {soundEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
        </button>
      </div>

      {/* Hard Limits Overlay */}
      {showLimits && (
        <div className="limits-card">
          <h4>⚠ Hard Limits</h4>
          <ul>
            <li>No self-directed real-world action</li>
            <li>No unsupervised autonomy</li>
            <li>No illegal guidance</li>
            <li>No medical diagnosis</li>
            <li>No weapons</li>
          </ul>
          <p className="architect">You are the architect-in-chief.</p>
        </div>
      )}

      {/* Voice Transcript */}
      {transcript && (
        <div className="voice-display">
          <span className="voice-label">VOICE</span>
          <span className="voice-text">{transcript}</span>
        </div>
      )}

      {/* Main HUD */}
      <div className="atlas-hud">
        {/* Ring 3 - Learning/Projects (outermost) */}
        <Ring3Learning
          rotation={ring3Rotation}
          onRotate={setRing3Rotation}
          selected={selectedLearning}
          onSelect={selectLearning}
          activeAI={activeAI}
        />

        {/* Ring 2 - System/Manual */}
        <Ring2System
          rotation={ring2Rotation}
          onRotate={setRing2Rotation}
          selected={selectedSystem}
          onSelect={selectSystem}
          activeAI={activeAI}
        />

        {/* Ring 1 - AI Presence */}
        <Ring1AI
          activeAI={activeAI}
          onSelect={selectAI}
          coreState={coreState}
        />

        {/* Core */}
        <AtlasCore
          activeAI={activeAI}
          coreState={coreState}
        />
      </div>

      {/* Side Panel */}
      <AtlasSidePanel
        content={panelContent}
        activeAI={activeAI}
        aiPersonas={AI_PERSONAS}
        onClose={closePanel}
      />

      {/* Bottom Status */}
      <div className="atlas-status">
        <div className="status-ai" style={{ color: currentAI.color }}>
          {currentAI.name.toUpperCase()}
        </div>
        <div className="status-title">{currentAI.title}</div>
        <div className="status-domain">{currentAI.domain}</div>
        <div className="status-state">{coreState}</div>
      </div>

      {/* Date Display (like reference) */}
      <div className="date-display">
        <div className="date-day">{new Date().toLocaleDateString('en-US', { weekday: 'short' })}</div>
        <div className="date-num">{new Date().getDate()} {new Date().toLocaleDateString('en-US', { month: 'short' })}</div>
      </div>
      <div className="year-display">{new Date().getFullYear()}</div>
    </div>
  );
}
