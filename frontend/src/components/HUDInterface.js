import React, { useState, useCallback } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import AtlasCore from './HUD/AtlasCore';
import DialRing from './HUD/DialRing';
import GhostRings from './HUD/GhostRings';
import AtlasSidePanel from './HUD/AtlasSidePanel';
import { useAudioFeedback } from '../hooks/useAudioFeedback';
import { useAudioReactive } from '../hooks/useAudioReactive';
import { AI_PERSONAS } from '../data/atlasCore';
import { INNER_RING, MIDDLE_RING, OUTER_RING } from '../data/ringStructure';
import ajaniLogo from '../assets/logos/ajani-logo.jpg';
import minervaLogo from '../assets/logos/minerva-logo.jpg';
import hermesLogo from '../assets/logos/hermes-logo.jpg';
import councilLogo from '../assets/logos/atlas-council-logo.jpg';

// Clean HUD mode: ATLAS face only.
// No chat box, no type-to-speak, no upload controls, no transcript overlay.
// The screen is limited to the AIs, rings, core, and selected section panels.

const AI_LOGOS = {
  ajani: ajaniLogo,
  minerva: minervaLogo,
  hermes: hermesLogo,
  trinity: councilLogo,
};

function AIFaceDock({ activeAI, aiPersonas, onSelect }) {
  const aiOrder = ['ajani', 'minerva', 'hermes'];
  return (
    <div className="ai-face-dock" aria-label="AI face HUDs">
      {aiOrder.map((aiKey) => {
        const ai = aiPersonas[aiKey];
        const active = activeAI === aiKey;
        return (
          <button
            key={aiKey}
            type="button"
            className={`ai-face-card ${active ? 'active' : ''}`}
            style={{ '--ai-color': ai.color }}
            onClick={() => onSelect(aiKey)}
          >
            <span className="ai-face-window">
              <img src={AI_LOGOS[aiKey]} alt="" />
            </span>
            <span className="ai-face-name">{ai.name}</span>
            <span className="ai-presence-dot" />
          </button>
        );
      })}
      <button
        type="button"
        className={`ai-face-card council-card ${activeAI === 'trinity' ? 'active' : ''}`}
        style={{ '--ai-color': AI_PERSONAS.trinity.color }}
        onClick={() => onSelect('trinity')}
      >
        <span className="ai-face-window">
          <img src={AI_LOGOS.trinity} alt="" />
        </span>
        <span className="ai-face-name">Council</span>
        <span className="ai-presence-dot" />
      </button>
    </div>
  );
}

const CORE_STATES = {
  IDLE: 'idle',
  THINKING: 'thinking',
  SPEAKING: 'speaking',
};

export default function HUDInterface() {
  const [activeAI, setActiveAI] = useState('ajani');
  const [coreState, setCoreState] = useState(CORE_STATES.IDLE);
  const [selectedMiddle, setSelectedMiddle] = useState(null);
  const [selectedOuter, setSelectedOuter] = useState(null);
  const [panelContent, setPanelContent] = useState(null);
  const [coreTapPulse, setCoreTapPulse] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);

  const { playTone, playSnap, playGlide } = useAudioFeedback(soundEnabled);
  const audioReactive = useAudioReactive();

  const selectAI = useCallback((aiKey) => {
    const color = AI_PERSONAS[aiKey]?.color;
    if (color) playTone(color);

    setActiveAI(aiKey);
    setCoreState(CORE_STATES.SPEAKING);
    setPanelContent({ type: 'ai-info', ai: aiKey });
    setTimeout(() => setCoreState(CORE_STATES.IDLE), 1400);
  }, [playTone]);

  const openSection = useCallback((sectionId, ringSource) => {
    if (ringSource === 'outer') {
      playGlide();
      setSelectedOuter(sectionId);
    } else {
      playSnap();
      setSelectedMiddle(sectionId);
    }

    setCoreState(CORE_STATES.THINKING);
    setPanelContent({ type: 'operation', operation: sectionId, ai: activeAI });
    setTimeout(() => setCoreState(CORE_STATES.IDLE), 1000);
  }, [activeAI, playGlide, playSnap]);

  const closePanel = useCallback(() => {
    setPanelContent(null);
    setSelectedMiddle(null);
    setSelectedOuter(null);
  }, []);

  const handleCoreTap = useCallback(() => {
    playTone('#220066');
    setCoreTapPulse(true);
    setCoreState(CORE_STATES.THINKING);
    setTimeout(() => {
      setCoreTapPulse(false);
      setCoreState(CORE_STATES.IDLE);
    }, 700);
  }, [playTone]);

  return (
    <div className="atlas-container clean-hud-mode">
      <div className="atlas-background" />

      <div
        className={`atlas-hud ${coreTapPulse ? 'tap-pulse' : ''}`}
        data-ring-motion={coreState}
      >
        <GhostRings />

        <div className="ring-stage ring-stage-outer" data-ring="outer">
          <DialRing
            items={OUTER_RING.items}
            slotAngle={OUTER_RING.slotAngle}
            radiusPct={43}
            selectedId={selectedOuter}
            onSelect={(item) => openSection(item.id, 'outer')}
            ringTestId="ring-outer"
          />
        </div>

        <div className="ring-stage ring-stage-middle" data-ring="middle">
          <DialRing
            items={MIDDLE_RING.items}
            slotAngle={MIDDLE_RING.slotAngle}
            radiusPct={43}
            selectedId={selectedMiddle}
            onSelect={(item) => openSection(item.id, 'middle')}
            ringTestId="ring-middle"
          />
        </div>

        <div className="ring-stage ring-stage-inner" data-ring="inner">
          <DialRing
            items={INNER_RING.items}
            slotAngle={INNER_RING.slotAngle}
            radiusPct={43}
            selectedId={activeAI}
            onSelect={(item) => selectAI(item.id)}
            ringTestId="ring-inner"
            activeAI={activeAI}
          />
        </div>

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

        <div className="core-wrap">
          <AtlasCore
            activeAI={activeAI}
            coreState={coreState}
            onActivate={handleCoreTap}
            audioLevelRef={audioReactive.levelRef}
          />
        </div>
      </div>

      <AIFaceDock activeAI={activeAI} aiPersonas={AI_PERSONAS} onSelect={selectAI} />

      <AtlasSidePanel
        content={panelContent}
        activeAI={activeAI}
        aiPersonas={AI_PERSONAS}
        onClose={closePanel}
      />

      <div className="atlas-startup-mark" aria-hidden="true">
        <img src={councilLogo} alt="" />
      </div>

      <button
        type="button"
        className={`atlas-sound-toggle ${soundEnabled ? 'on' : 'off'}`}
        onClick={() => setSoundEnabled((s) => !s)}
        title={soundEnabled ? 'Mute HUD chimes' : 'Enable HUD chimes'}
        aria-label={soundEnabled ? 'Mute HUD chimes' : 'Enable HUD chimes'}
        data-testid="sound-toggle"
      >
        {soundEnabled ? <Volume2 size={13} /> : <VolumeX size={13} />}
      </button>
    </div>
  );
}
