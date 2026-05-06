# Atlas Core HUD — PRD

## Original Problem Statement
A 2.5D AI HUD interface for Atlas Core. Three concentric, drag-to-rotate radial
dial rings around a central animated core. Built to match the user's exact
reference screenshot (rectangular tiles on glowing blue circular tracks inside a
blue rectangular HUD frame, tiles snap to the top slot when selected, selected
tile glows in the AI's identity color).

## Identity Colors
- **Ajani**:   crimson #DC143C — Builder / Strategist / Engineer
- **Minerva**: teal    #20B2AA — Guide / Teacher / Healer
- **Hermes**:  silver  #C0C0C0 — Messenger / Protector / Validator
- **Council**: purple  #9370DB — Trinity Counsel

## Architecture

### Frontend
```
/app/frontend/src/
├── components/
│   ├── HUDInterface.js          # Main orchestrator
│   ├── HUD/
│   │   ├── DialRing.js          # Single radial drag-to-rotate dial
│   │   ├── AtlasCore.js         # Canvas-based central orb
│   │   └── AtlasSidePanel.js    # Right-side context panel
│   ├── ChatPanel.js
│   ├── FileUploadModal.js
│   └── FileBrowserPanel.js
├── data/
│   ├── ringStructure.js         # INNER/MIDDLE/OUTER ring tile definitions
│   └── atlasCore.js             # AI personas, projects, phases
├── hooks/
│   ├── useVoiceRecognition.js   # Web Speech API wrapper
│   └── useAudioFeedback.js      # WebAudio click/tone/snap/glide
└── App.css                      # Theme + radial dial CSS
```

### Backend
```
/app/backend/
├── server.py                    # FastAPI entrypoint
├── routes/
│   ├── chat.py                  # POST /api/chat/send (Emergent LLM Key)
│   ├── files.py                 # /api/files/{upload,list,download,delete,stats}
│   └── knowledge.py             # /api/knowledge/{subjects,teach}
└── services/
    ├── ai_categorizer.py
    └── knowledge_core.py        # 22 educational subjects (in-memory)
```

## Ring Layout (matches reference screenshot + 6-layer spec)

### Layer hierarchy (inside → outside, all centered on orb)
1. **Core orb** ≈ 18% of HUD — tappable lava-lamp visualization
2. **Core containment ring** ≈ 22% (1.3× orb) — decorative reactor cradle
3. **Inner orbit** ≈ 38% (2.5× orb) — AI personas (4 slots @ 90°, compass)
4. **Mid system ring** ≈ 60% (4× orb) — operating-system shell
5. **Outer world ring** ≈ 88% (6× orb) — knowledge / exploration
6. **Ghost / parallax rings** — 7 faded background circles drifting at
   different speeds (75–320 s per revolution) for "living machine" depth.
   Opacity 5–15%, extend beyond the rectangular HUD frame.

### Inner ring (4 slots @ 90°)
- N: AJANI — E: MINERVA — S: HERMES — W: COUNCIL

### Mid System ring (5 slots, 8-slot grid)
- N: MANUAL — E: ENCYCLOPEDIA — SE: MEMORY — S: SYSTEMS — SW: CUSTOMIZATION

### Outer World ring (6 slots, 8-slot grid)
- N: SUBJECTS — E: LAB — SE: PROJECTS — S: BLUEPRINTS — SW: ARCHIVE — W: EXPLORE MODE

## Motion Spec (per ring)
| Ring   | Snap duration | Easing                        | Personality |
|--------|---------------|-------------------------------|-------------|
| Inner  | 300 ms        | cubic-bezier(.33, 1, .68, 1)  | Identity / soft |
| Middle | 180 ms        | cubic-bezier(.4, 0, .2, 1)    | Mechanical / precise |
| Outer  | 400 ms        | cubic-bezier(.25, .8, .3, 1)  | Exploratory / graceful |

Stillness rule: rings only move on drag, click, voice, or panel open. After
movement they snap to the nearest slot and stop. No auto-spin.

## Interactions
- **Click a tile** → select it (inner = activate AI; middle/outer = open panel)
- **Drag the ring** → rotates all tiles around center; on release, snaps to
  nearest slot and the new top tile is selected
- **Memory / Archive tiles** → open File Browser (not side panel)
- **Voice mic button** (top-right) → "Minerva, open projects" rotates ring 1 to
  Minerva, ring 3 to Projects, opens panel
- **Hard Limits / Sound / Upload** → top-right control buttons

## What's Implemented (this session, Feb 2026)
- [x] Radial dial rebuild with polar-coord tile placement and pointer-driven
      drag-to-rotate (DialRing.js)
- [x] Layout matches user reference image exactly with interleaved middle
      ring (offset 22.5° from outer to avoid radial collisions)
- [x] Premium glass tiles with neon rim, gradient bg, hover lift
- [x] 6-layer ring hierarchy: orb (18%) → core ring (22%) → inner (38%) →
      mid (60%) → outer (88%) → 7 ghost parallax rings
- [x] Differentiated ring track thicknesses (containment > inner > outer > mid)
- [x] **Fluid liquid lava-lamp core** — 11 organic deformed blobs (red,
      teal, silver, violet, magenta) with velocity squash/stretch, particle
      system, central pulse nucleus, multi-layer depth, tap-to-shock ripple
- [x] Tap reaction: rings flare, tiles shift, containment ring brightens,
      deep machine hum
- [x] Voice command flow fixed (callback-ref hook, getUserMedia, onError)
- [x] FileUploadModal + FileBrowserPanel: data-testid for testability
- [x] Backend `.env` fix: EMERGENT_LLM_KEY on its own line

### AI Services (NEW this iteration)
- [x] **OpenAI TTS** — POST /api/ai/tts with per-AI voice mapping
      (Ajani→onyx, Minerva→nova, Hermes→echo, Trinity→shimmer)
- [x] **Minerva approval API** — POST /api/ai/minerva/approve returns
      verdict + ethical_score + concerns + conditions + alternatives +
      ancestral_wisdom
- [x] **Hermes validation API** — POST /api/ai/hermes/validate returns
      verdict + feasibility/safety scores + failure_modes + constraints +
      next_steps
- [x] **Blueprint Engine** — POST /api/ai/blueprint/generate returns
      5-phase structured spec (Philosophy, Research, Blueprint, Simulation,
      Physical)
- [x] **Audio-reactive core** — useAudioReactive hook pipes mic
      AnalyserNode RMS into AtlasCore via levelRef. When listening, blob
      jitter + speed scale with voice volume.
- [x] **TTS playback in ChatPanel** — chat-voice-toggle button, AI
      responses spoken aloud in the persona's voice
- [x] **BlueprintWorkbench** — interactive UI (opens via outer-blueprints
      tile) for Generate Blueprint + Minerva Review + Hermes Validate
- [x] All 11 backend AI tests passed (test_ai_services.py); frontend
      flows verified end-to-end

## Backlog

### P1
- [ ] Minerva approval API + Hermes validation API (parity with user's GitHub repo)
- [ ] Blueprint Engine + Design Tools (from user's GitHub repo)

### P2
- [ ] Real-time TTS for AI personas (per-AI voice rhythm)
- [ ] Offline AI fallback (Ollama local LLM or hybrid cache)
- [ ] Hidden / advanced rings (diagnostics, build mode)

### P3
- [ ] Persistent PostgreSQL/MongoDB Knowledge Core (currently in-memory)
- [ ] 3D WebGL upgrade for the central core
- [ ] Multi-language voice support
- [ ] Custom AI voice profiles
