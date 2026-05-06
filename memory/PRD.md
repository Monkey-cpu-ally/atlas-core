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

## Ring Layout (matches reference screenshot)

### Inner ring (radius 14.2% of HUD, 4 slots @ 90°)
- N: AJANI — E: MINERVA — S: HERMES — W: COUNCIL

### Middle ring (radius 29.2% of HUD, 6 of 8 slots @ 45°)
- N: MANUAL — E: ENCYCLOPEDIA — S: SYSTEM MONITOR — W: EXPLORE MODE
- SE: MEMORY — SW: CUSTOMIZATION
- (NE, NW intentionally empty)

### Outer ring (radius 43% of HUD, 6 of 8 slots @ 45°)
- N: SUBJECTS — E: LAB — S: BLUEPRINTS — W: ARCHIVE
- SE: PROJECTS — SW: SYSTEMS
- (NE, NW intentionally empty)

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
- [x] Layout matches user reference image exactly (inner/middle/outer)
- [x] Click-vs-drag detection with > 4° threshold
- [x] Selected tile snaps to top, glows in AI color (inner) or blue (others)
- [x] Per-ring motion personality (timings + easing)
- [x] Voice command bug fixed:
      - removed undefined `setSelectedSystem` / `setSelectedLearning` setters
        that crashed the app on voice result
      - hook now uses callback refs so recognition isn't recreated each render
      - added explicit `getUserMedia` permission request and `onError` callback
- [x] FileUploadModal + FileBrowserPanel: data-testid for testability
- [x] Backend `.env` fix: EMERGENT_LLM_KEY moved onto its own line (was being
      silently dropped by python-dotenv → `/api/chat/send` returned 503)
- [x] Dead code removed: old OriginalRing1/2/3, Ring1AIPresence, Ring2System,
      Ring3Learning, originalRingStructure data file

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
