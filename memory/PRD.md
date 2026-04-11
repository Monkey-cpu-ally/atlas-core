# Atlas Core HUD Interface - PRD

## Original Problem Statement
Build a futuristic HUD (Heads-Up Display) interface for Atlas Core educational system with:
- 3 AI personas: Ajani (Elemental Kinetics), Minerva (Bio-Genesis), Hermes (Nano-Synthesis) + Trinity Counsel mode
- 30 research projects across all AIs with phases (Philosophy → Research → Blueprint → Simulation → Physical Proposal)
- 22 teaching fields shared by all AIs
- 4 teaching modes: Teach, Build, Analyze, Story
- Voice activation, audio feedback, visual core, side panels

## Architecture

### Frontend (React)
```
/app/frontend/src/
├── App.js, App.css
├── components/
│   ├── HUDInterface.js        # Main circular HUD
│   └── HUD/
│       ├── HUDCore.js         # Canvas planet visualization
│       └── AtlasSidePanel.js  # Contextual panels
├── data/
│   └── atlasCore.js           # AI personas, projects, fields data
└── hooks/
    ├── useVoiceRecognition.js # Web Speech API
    └── useAudioFeedback.js    # Web Audio API
```

## What's Implemented (Jan 2026)

### Circular HUD Layout
- [x] Concentric circular rings matching reference design
- [x] Inner ring: 4 AI personas at cardinal positions
- [x] Outer ring: 12 operation/knowledge segments evenly distributed
- [x] Central animated core with AI-specific visualizations
- [x] Ring visual guides (elliptical borders)

### AI System
- [x] Ajani (crimson) - Elemental Kinetics - 13 projects
- [x] Minerva (teal) - Bio-Genesis - 12 projects  
- [x] Hermes (silver) - Nano-Synthesis - 5 projects
- [x] Trinity Counsel (purple) - Collaborative mode

### Interactions
- [x] Click AI to select and see info panel
- [x] Click operation segments for context panels
- [x] Voice recognition for AI names
- [x] Audio feedback (clicks, tones, snaps)
- [x] Drag to rotate outer ring
- [x] Hard Limits warning overlay

### Content
- [x] All 30 projects with phases and progress
- [x] Operation panels: Manual, Encyclopedia, Lab, Projects, Memory, Blueprints, Systems, Archive, etc.
- [x] AI profiles with domain, core belief, hard rule

## Data Model

### AI Personas
```js
{
  ajani: { name, title, domain, color, coreBelief, hardRule, projects[] },
  minerva: { ... },
  hermes: { ... },
  trinity: { ... }
}
```

### Project Phases
```
Philosophy (20%) → Research (40%) → Blueprint (60%) → Simulation (80%) → Physical Proposal (100%)
```

## Backlog

### P1 (High)
- [ ] Connect to Atlas Core backend API
- [ ] Real-time AI chat integration
- [ ] Text-to-speech for AI responses

### P2 (Medium)
- [ ] Persistent user progress
- [ ] Teaching mode activation
- [ ] Field selection → learning flow

### P3 (Nice to Have)
- [ ] 3D WebGL core visualization
- [ ] Haptic feedback on mobile
- [ ] Multi-language voice support

## Hard Limits (All AIs)
- No self-directed real-world action
- No unsupervised autonomy
- No illegal guidance
- No medical diagnosis
- No weapons
- No overriding user decisions
- User is always the architect-in-chief
