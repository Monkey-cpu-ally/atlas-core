import React, { useState, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, AlertTriangle, Upload as UploadIcon } from 'lucide-react';
import AtlasCore from './HUD/AtlasCore';
import DialRing from './HUD/DialRing';
import GhostRings from './HUD/GhostRings';
import AtlasSidePanel from './HUD/AtlasSidePanel';
import FileUploadModal from './FileUploadModal';
import FileBrowserPanel from './FileBrowserPanel';
import ChatPanel from './ChatPanel';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';
import { useAudioFeedback } from '../hooks/useAudioFeedback';
import { AI_PERSONAS } from '../data/atlasCore';
import { INNER_RING, MIDDLE_RING, OUTER_RING } from '../data/ringStructure';

// Core states: idle, listening, thinking, speaking, alert
const CORE_STATES = {
  IDLE: 'idle',
  LISTENING: 'listening',
  THINKING: 'thinking',
  SPEAKING: 'speaking',
  ALERT: 'alert',
};

// File-browser sections — open the FileBrowserPanel instead of side panel.
const FILE_SECTIONS = new Set(['memory', 'archive']);

export default function HUDInterface() {
  const [activeAI, setActiveAI] = useState('ajani');
  const [coreState, setCoreState] = useState(CORE_STATES.IDLE);
  const [selectedMiddle, setSelectedMiddle] = useState(null);
  const [selectedOuter, setSelectedOuter] = useState(null);
  const [panelContent, setPanelContent] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [showLimits, setShowLimits] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showFileBrowser, setShowFileBrowser] = useState(false);
  const [coreTapPulse, setCoreTapPulse] = useState(false);

  const { playClick, playTone, playSnap, playGlide } = useAudioFeedback(soundEnabled);

  // --- Core actions -------------------------------------------------------
  const selectAI = useCallback((aiKey) => {
    const color = AI_PERSONAS[aiKey]?.color;
    if (color) playTone(color);
    setActiveAI(aiKey);
    setCoreState(CORE_STATES.SPEAKING);
    setPanelContent({ type: 'ai-info', ai: aiKey });
    setTimeout(() => setCoreState(CORE_STATES.IDLE), 2000);
  }, [playTone]);

  const openSection = useCallback((sectionId, ringSource) => {
    if (FILE_SECTIONS.has(sectionId)) {
      playClick();
      setShowFileBrowser(true);
      setPanelContent(null);
      return;
    }
    if (ringSource === 'outer') {
      playGlide();
      setSelectedOuter(sectionId);
    } else {
      playSnap();
      setSelectedMiddle(sectionId);
    }
    setPanelContent({ type: 'operation', operation: sectionId, ai: activeAI });
  }, [activeAI, playClick, playGlide, playSnap]);

  const closePanel = useCallback(() => {
    setPanelContent(null);
    setSelectedMiddle(null);
    setSelectedOuter(null);
  }, []);

  // --- Voice command flow -------------------------------------------------
  // Example: "Minerva, open Projects"
  const handleVoiceCommand = useCallback((command) => {
    const lower = command.toLowerCase();
    setCoreState(CORE_STATES.THINKING);

    setTimeout(() => {
      let aiKey = null;
      let outerOp = null;
      let middleOp = null;

      if (lower.includes('ajani')) aiKey = 'ajani';
      else if (lower.includes('minerva')) aiKey = 'minerva';
      else if (lower.includes('hermes')) aiKey = 'hermes';
      else if (lower.includes('council') || lower.includes('trinity')) aiKey = 'trinity';

      // Outer ring (knowledge & creation)
      if (lower.includes('subject')) outerOp = 'subjects';
      else if (lower.includes('lab')) outerOp = 'lab';
      else if (lower.includes('project')) outerOp = 'projects';
      else if (lower.includes('blueprint')) outerOp = 'blueprints';
      else if (lower.includes('archive')) outerOp = 'archive';

      // Middle ring (ops)
      if (!outerOp) {
        if (lower.includes('manual')) middleOp = 'manual';
        else if (lower.includes('encyclopedia')) middleOp = 'encyclopedia';
        else if (lower.includes('memory')) middleOp = 'memory';
        else if (lower.includes('system monitor') || lower.includes('monitor')) middleOp = 'system_monitor';
        else if (lower.includes('customization') || lower.includes('customize')) middleOp = 'customization';
        else if (lower.includes('explore')) middleOp = 'explore';
        else if (lower.includes('system')) middleOp = 'systems'; // falls to outer
      }

      if (aiKey) {
        selectAI(aiKey);
      }
      // Sequence: Ring 1 rotates first (~300ms), then Ring 3/2 rotates.
      if (outerOp) {
        setTimeout(() => openSection(outerOp, 'outer'), aiKey ? 400 : 0);
      } else if (middleOp) {
        setTimeout(() => openSection(middleOp, 'middle'), aiKey ? 400 : 0);
      }

      setCoreState(CORE_STATES.SPEAKING);
      setTimeout(() => setCoreState(CORE_STATES.IDLE), 2200);
    }, 400);
  }, [selectAI, openSection]);

  const { startListening, stopListening, isSupported } = useVoiceRecognition({
    onResult: (text, isFinal) => {
      setTranscript(text);
      if (isFinal) handleVoiceCommand(text);
    },
    onListeningChange: (listening) => {
      setIsListening(listening);
      setCoreState(listening ? CORE_STATES.LISTENING : CORE_STATES.IDLE);
    },
    onError: (errorCode) => {
      const msg =
        errorCode === 'not-allowed' || errorCode === 'service-not-allowed'
          ? 'Microphone permission denied'
          : errorCode === 'no-speech'
            ? 'No speech detected — try again'
            : errorCode === 'audio-capture'
              ? 'No microphone found'
              : errorCode === 'network'
                ? 'Network error during voice recognition'
                : errorCode === 'aborted'
                  ? ''
                  : `Voice error: ${errorCode}`;
      if (msg) {
        setTranscript(msg);
        setTimeout(() => setTranscript(''), 3000);
      }
    },
  });

  const toggleListening = () => {
    if (!isSupported) {
      alert('Voice recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }
    if (isListening) {
      stopListening();
      setTranscript('');
    } else {
      setTranscript('Listening…');
      startListening();
      playClick();
    }
  };

  // Core tap — wakes the system, ripples the rings outward, plays a deep
  // hum, and toggles voice listening when supported. Spec: "rings react
  // outward, glow intensifies, energy pulse expands, UI tiles subtly
  // shift, audio hum deepens."
  const handleCoreTap = useCallback(() => {
    if (soundEnabled) playTone('#220066');  // low frequency hum
    setCoreTapPulse(true);
    setTimeout(() => setCoreTapPulse(false), 700);
    if (isSupported) toggleListening();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [soundEnabled, playTone, isSupported]);

  const currentAI = AI_PERSONAS[activeAI];

  // --- Ring handlers ------------------------------------------------------
  const onInnerSelect = (item) => {
    selectAI(item.id);
  };
  const onMiddleSelect = (item) => {
    openSection(item.id, 'middle');
  };
  const onOuterSelect = (item) => {
    openSection(item.id, 'outer');
  };

  return (
    <div className="atlas-container">
      <div className="atlas-background" />

      {/* Top Controls */}
      <div className="atlas-controls">
        <button
          className={`ctrl-btn ${showLimits ? 'active warning' : ''}`}
          onClick={() => setShowLimits(!showLimits)}
          data-testid="btn-hard-limits"
          title="Hard Limits"
        >
          <AlertTriangle size={18} />
        </button>
        {isSupported ? (
          <button
            className={`ctrl-btn ${isListening ? 'active listening' : ''}`}
            onClick={toggleListening}
            data-testid="btn-mic"
            title={isListening ? 'Stop Listening' : 'Start Voice Commands'}
          >
            {isListening ? <Mic size={18} /> : <MicOff size={18} />}
          </button>
        ) : (
          <button
            className="ctrl-btn"
            disabled
            data-testid="btn-mic-disabled"
            title="Voice not supported. Use Chrome/Edge."
            style={{ opacity: 0.3, cursor: 'not-allowed' }}
          >
            <MicOff size={18} />
          </button>
        )}
        <button
          className={`ctrl-btn ${soundEnabled ? 'active' : ''}`}
          onClick={() => setSoundEnabled(!soundEnabled)}
          data-testid="btn-sound"
          title={soundEnabled ? 'Mute Sound' : 'Enable Sound'}
        >
          {soundEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
        </button>
        <button
          className="ctrl-btn"
          onClick={() => setShowUploadModal(true)}
          data-testid="btn-upload"
          title="Upload Files"
        >
          <UploadIcon size={18} />
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
        <div className="voice-display" data-testid="voice-transcript">
          <span className="voice-label">VOICE</span>
          <span className="voice-text">{transcript}</span>
        </div>
      )}

      {/* Main HUD — 3 concentric radial dials + ghost background + core */}
      <div
        className={`atlas-hud ${coreTapPulse ? 'tap-pulse' : ''}`}
        data-ring-motion={coreState}
      >
        {/* Layer 0: ghost / parallax background rings */}
        <GhostRings />

        <div className="ring-stage ring-stage-outer" data-ring="outer">
          <DialRing
            items={OUTER_RING.items}
            slotAngle={OUTER_RING.slotAngle}
            radiusPct={43}
            selectedId={selectedOuter}
            onSelect={onOuterSelect}
            ringTestId="ring-outer"
          />
        </div>
        <div className="ring-stage ring-stage-middle" data-ring="middle">
          <DialRing
            items={MIDDLE_RING.items}
            slotAngle={MIDDLE_RING.slotAngle}
            radiusPct={43}
            selectedId={selectedMiddle}
            onSelect={onMiddleSelect}
            ringTestId="ring-middle"
          />
        </div>
        <div className="ring-stage ring-stage-inner" data-ring="inner">
          <DialRing
            items={INNER_RING.items}
            slotAngle={INNER_RING.slotAngle}
            radiusPct={43}
            selectedId={activeAI}
            onSelect={onInnerSelect}
            ringTestId="ring-inner"
            activeAI={activeAI}
          />
        </div>

        {/* Containment ring — decorative reactor cradle, 1.3× orb */}
        <div
          className="core-ring"
          aria-hidden="true"
          style={{
            '--core-bloom': (
              activeAI === 'minerva' ? '40, 200, 190' :
              activeAI === 'hermes'  ? '240, 240, 250' :
              activeAI === 'trinity' ? '168, 120, 230' :
              '240, 50, 70'
            ),
          }}
        />

        {/* Central Core — tappable lava-lamp orb (wake / state / activation) */}
        <div className="core-wrap">
          <AtlasCore
            activeAI={activeAI}
            coreState={coreState}
            onActivate={handleCoreTap}
          />
        </div>
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

      {/* Date Display */}
      <div className="date-display">
        <div className="date-day">{new Date().toLocaleDateString('en-US', { weekday: 'short' })}</div>
        <div className="date-num">
          {new Date().getDate()} {new Date().toLocaleDateString('en-US', { month: 'short' })}
        </div>
      </div>
      <div className="year-display">{new Date().getFullYear()}</div>

      {/* Modals */}
      <FileUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUploadSuccess={() => { playTone(currentAI.color); }}
      />
      <FileBrowserPanel
        isOpen={showFileBrowser}
        onClose={() => setShowFileBrowser(false)}
      />
      <ChatPanel activeAI={activeAI} onAISwitch={setActiveAI} />
    </div>
  );
}
