import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import HUDCore from './HUD/HUDCore';
import Ring1AI from './HUD/Ring1AI';
import Ring2Operations from './HUD/Ring2Operations';
import Ring3Knowledge from './HUD/Ring3Knowledge';
import SidePanel from './HUD/SidePanel';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';
import { useAudioFeedback } from '../hooks/useAudioFeedback';

const AI_CONFIG = {
  ajani: { color: '#DC143C', name: 'Ajani', pulseStyle: 'steady' },
  minerva: { color: '#20B2AA', name: 'Minerva', pulseStyle: 'flowing' },
  hermes: { color: '#F5F5F5', name: 'Hermes', pulseStyle: 'precise' },
  council: { color: '#9370DB', name: 'Council', pulseStyle: 'flash' }
};

const RING2_SECTIONS = ['Manual', 'Encyclopedia', 'Memory', 'System Monitor', 'Customization', 'Explore Mode'];
const RING3_TABS = ['Subjects', 'Lab', 'Projects', 'Blueprints', 'Systems', 'Archive'];

export default function HUDInterface() {
  const [activeAI, setActiveAI] = useState('ajani');
  const [speakingAI, setSpeakingAI] = useState(null);
  const [ring1Rotation, setRing1Rotation] = useState(0);
  const [ring2Rotation, setRing2Rotation] = useState(0);
  const [ring3Rotation, setRing3Rotation] = useState(0);
  const [selectedOperation, setSelectedOperation] = useState(null);
  const [selectedKnowledge, setSelectedKnowledge] = useState(null);
  const [panelContent, setPanelContent] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');

  const { playClick, playTone, playSnap, playGlide } = useAudioFeedback(soundEnabled);
  
  const handleVoiceCommand = useCallback((command) => {
    const lowerCommand = command.toLowerCase();
    
    // Check for AI names
    for (const [key, ai] of Object.entries(AI_CONFIG)) {
      if (lowerCommand.includes(key) || lowerCommand.includes(ai.name.toLowerCase())) {
        selectAI(key);
        break;
      }
    }
    
    // Check for Ring 3 tabs
    for (const tab of RING3_TABS) {
      if (lowerCommand.includes(tab.toLowerCase())) {
        selectKnowledge(tab);
        break;
      }
    }
    
    // Check for Ring 2 operations
    for (const op of RING2_SECTIONS) {
      if (lowerCommand.includes(op.toLowerCase())) {
        selectOperation(op);
        break;
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
    if (aiKey === activeAI) return;
    
    playTone(AI_CONFIG[aiKey].color);
    
    const aiIndex = Object.keys(AI_CONFIG).indexOf(aiKey);
    const targetRotation = -aiIndex * 90;
    setRing1Rotation(targetRotation);
    
    setTimeout(() => {
      setActiveAI(aiKey);
      playSnap();
      
      // Simulate speaking
      setSpeakingAI(aiKey);
      setTimeout(() => setSpeakingAI(null), 2000);
    }, 300);
  }, [activeAI, playTone, playSnap]);

  const selectOperation = useCallback((operation) => {
    playClick();
    
    const opIndex = RING2_SECTIONS.indexOf(operation);
    const targetRotation = -opIndex * 60;
    setRing2Rotation(targetRotation);
    
    setTimeout(() => {
      setSelectedOperation(operation);
      setPanelContent({ type: 'operation', content: operation });
      playSnap();
    }, 180);
  }, [playClick, playSnap]);

  const selectKnowledge = useCallback((tab) => {
    playGlide();
    
    const tabIndex = RING3_TABS.indexOf(tab);
    const targetRotation = -tabIndex * 60;
    setRing3Rotation(targetRotation);
    
    setTimeout(() => {
      setSelectedKnowledge(tab);
      setPanelContent({ type: 'knowledge', content: tab });
    }, 350);
  }, [playGlide]);

  const handleRing2Drag = useCallback((delta) => {
    setRing2Rotation(prev => prev + delta * 0.5);
    playClick();
  }, [playClick]);

  const handleRing3Drag = useCallback((delta) => {
    setRing3Rotation(prev => prev + delta * 0.3);
  }, []);

  const closePanel = useCallback(() => {
    setPanelContent(null);
    setSelectedOperation(null);
    setSelectedKnowledge(null);
  }, []);

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="hud-container" data-testid="hud-container">
      {/* Background */}
      <div className="hud-background" />
      
      {/* Controls */}
      <div className="hud-controls" data-testid="hud-controls">
        {isSupported && (
          <button 
            className={`control-btn ${isListening ? 'active' : ''}`}
            onClick={toggleListening}
            data-testid="voice-toggle-btn"
            aria-label={isListening ? 'Stop listening' : 'Start listening'}
          >
            {isListening ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
          </button>
        )}
        <button 
          className={`control-btn ${soundEnabled ? 'active' : ''}`}
          onClick={() => setSoundEnabled(!soundEnabled)}
          data-testid="sound-toggle-btn"
          aria-label={soundEnabled ? 'Mute sounds' : 'Enable sounds'}
        >
          {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
        </button>
      </div>

      {/* Voice Transcript */}
      {transcript && (
        <div className="voice-transcript" data-testid="voice-transcript">
          <span className="transcript-label">Voice:</span>
          <span className="transcript-text">{transcript}</span>
        </div>
      )}

      {/* Main HUD */}
      <div className="hud-wrapper" data-testid="hud-wrapper">
        {/* Ring 3 - Knowledge (outermost) */}
        <Ring3Knowledge
          tabs={RING3_TABS}
          rotation={ring3Rotation}
          selectedTab={selectedKnowledge}
          onSelect={selectKnowledge}
          onDrag={handleRing3Drag}
        />

        {/* Ring 2 - Operations */}
        <Ring2Operations
          sections={RING2_SECTIONS}
          rotation={ring2Rotation}
          selectedSection={selectedOperation}
          onSelect={selectOperation}
          onDrag={handleRing2Drag}
        />

        {/* Ring 1 - AI Identity */}
        <Ring1AI
          aiConfig={AI_CONFIG}
          rotation={ring1Rotation}
          activeAI={activeAI}
          speakingAI={speakingAI}
          onSelect={selectAI}
        />

        {/* Core */}
        <HUDCore
          activeAI={activeAI}
          aiConfig={AI_CONFIG}
          speakingAI={speakingAI}
        />
      </div>

      {/* Side Panel */}
      <SidePanel
        content={panelContent}
        activeAI={activeAI}
        aiConfig={AI_CONFIG}
        onClose={closePanel}
      />

      {/* AI Status Display */}
      <div className="ai-status" data-testid="ai-status">
        <div className="ai-name" style={{ color: AI_CONFIG[activeAI].color }}>
          {AI_CONFIG[activeAI].name}
        </div>
        <div className="ai-state">
          {speakingAI ? 'Speaking...' : 'Ready'}
        </div>
      </div>

      {/* Instructions */}
      <div className="hud-instructions" data-testid="hud-instructions">
        <p>Voice commands: Say AI name (Ajani, Minerva, Hermes, Council) or tab names</p>
        <p>Click segments to select • Drag outer rings to rotate</p>
      </div>
    </div>
  );
}
