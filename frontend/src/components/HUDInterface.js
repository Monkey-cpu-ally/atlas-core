import React, { useState, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, AlertTriangle } from 'lucide-react';
import HUDCore from './HUD/HUDCore';
import AtlasSidePanel from './HUD/AtlasSidePanel';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';
import { useAudioFeedback } from '../hooks/useAudioFeedback';
import { AI_PERSONAS, TEACHING_MODES } from '../data/atlasCore';
import { User, Brain, Zap, Users, Layers, FlaskConical, FolderKanban, FileCode, Network, Archive, Book, Database, Activity, Settings, Compass } from 'lucide-react';

const AI_ICONS = { ajani: User, minerva: Brain, hermes: Zap, trinity: Users };

// Ring 1 - AI (innermost) - 4 segments at 0°, 90°, 180°, 270°
const AI_SEGMENTS = [
  { key: 'ajani', angle: 0 },      // top (12 o'clock)
  { key: 'minerva', angle: 90 },   // right (3 o'clock)
  { key: 'hermes', angle: 180 },   // bottom (6 o'clock)
  { key: 'trinity', angle: 270 },  // left (9 o'clock)
];

// Ring 2 - Operations (middle) - 6 segments evenly distributed
const OP_SEGMENTS = [
  { id: 'Subjects', icon: Layers, angle: 0 },
  { id: 'Manual', icon: Book, angle: 30 },
  { id: 'Encyclopedia', icon: Database, angle: 90 },
  { id: 'Lab', icon: FlaskConical, angle: 120 },
  { id: 'Projects', icon: FolderKanban, angle: 150 },
  { id: 'Memory', icon: Database, angle: 210 },
  { id: 'Blueprints', icon: FileCode, angle: 180 },
  { id: 'System Monitor', icon: Activity, angle: 240 },
  { id: 'Systems', icon: Network, angle: 270 },
  { id: 'Customization', icon: Settings, angle: 300 },
  { id: 'Archive', icon: Archive, angle: 330 },
  { id: 'Explore Mode', icon: Compass, angle: 60 },
];

export default function HUDInterface() {
  const [activeAI, setActiveAI] = useState('ajani');
  const [speakingAI, setSpeakingAI] = useState(null);
  const [ring2Rotation, setRing2Rotation] = useState(0);
  const [selectedOp, setSelectedOp] = useState(null);
  const [panelContent, setPanelContent] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [showHardLimits, setShowHardLimits] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const lastXRef = React.useRef(0);

  const { playClick, playTone, playSnap } = useAudioFeedback(soundEnabled);
  
  const handleVoiceCommand = useCallback((command) => {
    const lowerCommand = command.toLowerCase();
    const aiKeys = ['ajani', 'minerva', 'hermes', 'trinity'];
    for (const key of aiKeys) {
      if (lowerCommand.includes(key)) {
        selectAI(key);
        return;
      }
    }
  }, []);

  const { startListening, stopListening, isSupported } = useVoiceRecognition({
    onResult: (text) => {
      setTranscript(text);
      handleVoiceCommand(text);
    },
    onListeningChange: setIsListening
  });

  const selectAI = useCallback((aiKey) => {
    if (aiKey === activeAI) {
      setPanelContent({ type: 'ai-info', ai: aiKey });
      return;
    }
    playTone(AI_PERSONAS[aiKey].color);
    setActiveAI(aiKey);
    playSnap();
    setSpeakingAI(aiKey);
    setTimeout(() => setSpeakingAI(null), 2000);
  }, [activeAI, playTone, playSnap]);

  const selectOp = useCallback((opId) => {
    playClick();
    setSelectedOp(opId);
    setPanelContent({ type: 'operation', operation: opId, ai: activeAI });
    playSnap();
  }, [activeAI, playClick, playSnap]);

  const closePanel = useCallback(() => {
    setPanelContent(null);
    setSelectedOp(null);
  }, []);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    lastXRef.current = e.clientX;
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    const delta = e.clientX - lastXRef.current;
    setRing2Rotation(prev => prev + delta * 0.3);
    lastXRef.current = e.clientX;
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  React.useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const currentAI = AI_PERSONAS[activeAI];

  // Helper to calculate position on a circle
  const getPosition = (angle, radius) => {
    const rad = (angle - 90) * (Math.PI / 180); // -90 to start from top
    return {
      x: 50 + radius * Math.cos(rad),
      y: 50 + radius * Math.sin(rad)
    };
  };

  return (
    <div className="hud-container" data-testid="hud-container">
      <div className="hud-background" />
      
      {/* Controls */}
      <div className="hud-controls">
        <button 
          className={`control-btn warning ${showHardLimits ? 'active' : ''}`}
          onClick={() => setShowHardLimits(!showHardLimits)}
          data-testid="limits-toggle-btn"
        >
          <AlertTriangle className="w-5 h-5" />
        </button>
        {isSupported && (
          <button 
            className={`control-btn ${isListening ? 'active' : ''}`}
            onClick={() => isListening ? stopListening() : startListening()}
            data-testid="voice-toggle-btn"
          >
            {isListening ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
          </button>
        )}
        <button 
          className={`control-btn ${soundEnabled ? 'active' : ''}`}
          onClick={() => setSoundEnabled(!soundEnabled)}
          data-testid="sound-toggle-btn"
        >
          {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
        </button>
      </div>

      {/* Hard Limits */}
      {showHardLimits && (
        <div className="hard-limits-overlay">
          <div className="hard-limits-card">
            <h3><AlertTriangle className="inline w-4 h-4 mr-2" />Hard Limits</h3>
            <ul>
              <li>No self-directed real-world action</li>
              <li>No unsupervised autonomy</li>
              <li>No illegal guidance</li>
              <li>No medical diagnosis</li>
              <li>No weapons</li>
            </ul>
            <p className="architect-note">You are the architect-in-chief.</p>
          </div>
        </div>
      )}

      {/* Voice Transcript */}
      {transcript && (
        <div className="voice-transcript">
          <span className="transcript-label">Voice:</span>
          <span className="transcript-text">{transcript}</span>
        </div>
      )}

      {/* Main HUD - Circular Layout */}
      <div 
        className="hud-wrapper"
        onMouseDown={handleMouseDown}
      >
        {/* Circular ring visuals */}
        <div className="ring-circle ring-circle-1" style={{ borderColor: `${currentAI.color}40` }} />
        <div className="ring-circle ring-circle-2" />
        <div className="ring-circle ring-circle-3" />

        {/* Ring 2 - Operations (outer ring) */}
        <div className="ring-layer" style={{ transform: `rotate(${ring2Rotation}deg)` }}>
          {OP_SEGMENTS.map(({ id, icon: Icon, angle }) => {
            const pos = getPosition(angle, 42);
            const isSelected = selectedOp === id;
            return (
              <button
                key={id}
                className={`segment op-segment ${isSelected ? 'selected' : ''}`}
                style={{ 
                  left: `${pos.x}%`, 
                  top: `${pos.y}%`,
                  transform: `translate(-50%, -50%) rotate(${-ring2Rotation}deg)`
                }}
                onClick={(e) => { e.stopPropagation(); selectOp(id); }}
                data-testid={`op-${id.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className="segment-icon" />
                <span className="segment-label">{id}</span>
              </button>
            );
          })}
        </div>

        {/* Ring 1 - AI (inner ring) */}
        <div className="ring-layer">
          {AI_SEGMENTS.map(({ key, angle }) => {
            const ai = AI_PERSONAS[key];
            const Icon = AI_ICONS[key];
            const isActive = activeAI === key;
            const isSpeaking = speakingAI === key;
            const pos = getPosition(angle, 24);
            return (
              <button
                key={key}
                className={`segment ai-segment ${isActive ? 'active' : ''} ${isSpeaking ? 'speaking' : ''}`}
                style={{ 
                  left: `${pos.x}%`, 
                  top: `${pos.y}%`,
                  '--ai-color': ai.color 
                }}
                onClick={(e) => { e.stopPropagation(); selectAI(key); }}
                data-testid={`ai-segment-${key}`}
              >
                <Icon className="segment-icon" style={{ color: isActive ? ai.color : undefined }} />
                <span className="segment-label" style={{ color: isActive ? ai.color : undefined }}>{ai.name}</span>
                {isSpeaking && <div className="speaking-dot" style={{ background: ai.color }} />}
              </button>
            );
          })}
        </div>

        {/* Core */}
        <HUDCore activeAI={activeAI} aiPersonas={AI_PERSONAS} speakingAI={speakingAI} />
      </div>

      {/* Side Panel */}
      <AtlasSidePanel
        content={panelContent}
        activeAI={activeAI}
        aiPersonas={AI_PERSONAS}
        onClose={closePanel}
        onSelectProject={(project) => setPanelContent({ type: 'project-detail', project, ai: activeAI })}
      />

      {/* AI Status */}
      <div className="ai-status">
        <div className="ai-name" style={{ color: currentAI.color }}>{currentAI.name}</div>
        <div className="ai-subtitle">{currentAI.title}</div>
        <div className="ai-domain">{currentAI.domain}</div>
      </div>

      {/* Instructions */}
      <div className="hud-instructions">
        <p>Voice: Say AI name • Click segments to select • Drag to rotate</p>
      </div>
    </div>
  );
}
