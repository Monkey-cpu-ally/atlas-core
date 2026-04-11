# Atlas Core HUD Interface - PRD

## Original Problem Statement
Build a futuristic HUD interface for Atlas Core educational system matching the elegant light-themed reference design with:
- Living Core (glowing sphere with state-based animations)
- Ring 1: AI Presence (Ajani, Minerva, Hermes, Trinity Counsel)
- Ring 2: System/Manual (Settings, Skins, Voice, Devices, Memory, Health)
- Ring 3: Learning/Projects (Subjects, Lab, Blueprints, Weaver, Hyper Axel, Worlds, Archives, Projects)

## Core Behavior States
- **Idle**: Soft breathing glow, slow pulse
- **Listening**: Light expands outward in waves
- **Thinking**: Inner rings spin faster, particles swirl
- **Speaking**: Pulses sync to voice rhythm
- **Alert**: Sharper flashes and tighter rotations

## AI Identity Colors
- **Ajani**: Deep crimson — grounded, powerful (Elemental Kinetics)
- **Minerva**: Teal-blue — calm, wise (Bio-Genesis)
- **Hermes**: Soft white/silver — fast, precise (Nano-Synthesis)
- **Trinity Counsel**: Layered purple aura (Collaborative)

## Architecture

### Frontend (React)
```
/app/frontend/src/
├── components/
│   ├── HUDInterface.js          # Main orchestrator with state management
│   └── HUD/
│       ├── AtlasCore.js         # Canvas-based living core visualization
│       ├── Ring1AIPresence.js   # AI ring with arc segments
│       ├── Ring2System.js       # System ring with drag rotation
│       ├── Ring3Learning.js     # Learning ring with expansion nodes
│       └── AtlasSidePanel.js    # Contextual panels
├── data/
│   └── atlasCore.js             # AI personas, 30 projects, 22 fields
└── hooks/
    ├── useVoiceRecognition.js   # Web Speech API
    └── useAudioFeedback.js      # Web Audio API
```

## What's Implemented (Jan 2026)

### Visual Design
- [x] Light elegant theme (cream/beige gradients)
- [x] Glass-like core with AI-specific energy visualization
- [x] Clean white node buttons with subtle shadows
- [x] Date display (left) and year (right) like reference
- [x] Responsive layout for mobile

### Core System
- [x] 5 core states with distinct animations
- [x] AI color theming throughout
- [x] Particles, rings, pulses, ripples

### Ring 1 - AI Presence
- [x] 4 AI nodes hugging the core
- [x] Arc segment highlights
- [x] Active state glow animation
- [x] Speaking state pulse

### Ring 2 - System/Manual
- [x] 6 system nodes: Settings, UI Skins, Voice Modes, Devices, Memory, Health
- [x] Drag to rotate
- [x] Technical tick marks
- [x] Scanner line animation

### Ring 3 - Learning/Projects
- [x] 8 learning nodes: Subjects, Lab, Blueprints, Weaver, Hyper Axel, Worlds, Archives, Projects
- [x] Expansion dots on selection
- [x] Ambient particle effects
- [x] Drag to rotate

### Interactions
- [x] Voice recognition for AI selection
- [x] Audio feedback (clicks, tones, snaps, glides)
- [x] Side panels with contextual content
- [x] Hard Limits warning overlay

## 30 Projects Data
- Ajani: 13 projects (INSERT-CELL, HYDRA-CORE, RESONANCE, etc.)
- Minerva: 12 projects (PHOENIX-STRAND, ANANSI-WEAVE, EDEN-PROTOCOL, etc.)
- Hermes: 5 projects (SCARAB-FLEET, TERRABOT-BLOOM, DAEDALUS-FORGE, etc.)

## 22 Teaching Fields
Aerospace, Architecture, AI, Biology, Business, Chemistry, Creative Writing, Economics, Electronics, Environmental Science, Film Studies, Game Design, History, Mathematics, Music Theory, Nanotechnology, Philosophy, Physics, Psychology, Robotics, Software Engineering, Visual Arts

## Hard Limits (All AIs)
- No self-directed real-world action
- No unsupervised autonomy
- No illegal guidance
- No medical diagnosis
- No weapons
- You are always the architect-in-chief

## Backlog

### P1 (High)
- [ ] Connect to Atlas Core FastAPI backend
- [ ] Real AI chat integration (text-to-speech)
- [ ] Persistent user progress

### P2 (Medium)
- [ ] Hidden/Advanced rings (diagnostics, build mode)
- [ ] Teaching mode activation flows
- [ ] Haptic feedback on mobile

### P3 (Nice to Have)
- [ ] 3D WebGL core upgrade
- [ ] Multi-language voice support
- [ ] Custom AI voice profiles
