# Atlas Core — HUD Headquarters Frontend Architecture

The complete React/CSS layer that renders the radial AI operating system. The HUD is the visual command layer for **ATLAS Headquarters**, not a generic dashboard.

## Visual layout

```
                    ┌──────────────────────────────────────┐
                    │   Date · Year · Status · Persona     │
                    │                                      │
                    │      ╭──── Mission Departments ───╮  │
                    │     ╱ Knowledge · Lab · Projects   ╲ │
                    │    │ Blueprints · Archive · Sources │ │
                    │    │ ─ Headquarters Systems ──────  │ │
                    │    │ Standard · Memory · Status     │ │
                    │    │ ─ Council Chamber ───────────  │ │
                    │    │ Ajani · Minerva · Hermes       │ │
                    │     ╲      ⟡ ATLAS Core ⟡          ╱ │
                    │      ╰────────────────────────────╯  │
                    │                                      │
                    │   FAB · Chat · Upload · Voice        │
                    └──────────────────────────────────────┘
```

The three rings drag-rotate independently with snap angles. The central core is a touch-reactive Canvas2D lava-lamp simulation. Side panels slide in from the right and should feel like command surfaces inside a headquarters, not separate app pages.

## Headquarters language map

| Legacy UI idea | ATLAS Headquarters language | Purpose |
|---|---|---|
| AI persona ring | Council Chamber | Ajani, Minerva, Hermes, and Council decision work |
| System ring | Headquarters Systems | status, memory, manual, customization, diagnostics |
| World ring | Mission Departments | knowledge, lab, projects, blueprints, archive, source intake |
| Generic diagnostics | Headquarters Status / Quality Gates | product-facing system confidence |
| Generic project view | Project Briefing | risks, recommendations, reuse signals |
| Generic import/intake | Source Clearance | permission-first source handling |
| Generic self-improvement | Refinement Office | cleanup, polish, technical debt, ATLAS standard checks |

## Layout

```
frontend/src/
├── App.js                       Entry — renders <HUDInterface/>
├── App.css                      Single CSS file for HUD styling
│
├── components/
│   ├── HUDInterface.js          Main orchestrator — state, voice, FAB, panels
│   ├── ChatPanel.js             Floating chat with language picker
│   ├── FileUploadModal.js       Chunked upload + AI categorisation
│   ├── FileBrowserPanel.js      Legacy popover; ARCHIVE uses inline panel
│   │
│   └── HUD/
│       ├── AtlasCore.js              Central lava-lamp core
│       ├── DialRing.js               Drag-to-rotate ring renderer
│       ├── GhostRings.js             Holographic parallax background rings
│       ├── AtlasSidePanel.js         Command-surface router for every tile
│       │
│       ├── BlueprintWorkbench.js     Council-reviewed blueprint generator UI
│       ├── TeachingWorkbench.js      Knowledge Division teach surface
│       ├── DiagnosticsPanel.js       Headquarters status / quality posture
│       ├── InteractiveSandbox.js     Engineering Lab simulator
│       ├── ManualPanel.js            ATLAS Standard / operator manual
│       ├── CyclopediaPanel.js        Knowledge Gate index
│       ├── MemoryPanel.js            Memory Bank live feed
│       ├── CustomizationPanel.js     HUD identity, voice, theme controls
│       ├── CouncilPanel.js           Council Chamber deliberation UI
│       ├── IntakePanel.js            Source Clearance intake
│       ├── ArchiveBrowser.js         Memory Bank archive and uploaded files
│       ├── ProjectsPanel.js          Project Briefing / roadmap execution
│       └── QuizTaker.js              Mastery check
│
├── hooks/
│   ├── useVoiceRecognition.js   Web Speech API → wake-word & command parsing
│   ├── useTTS.js                Backend TTS with provider + abort-on-unmount
│   ├── useAudioReactive.js      Mic level → ring pulse + core hum
│   ├── useAudioFeedback.js      Hover / click / select chimes
│   └── useAtlasJob.js           Non-blocking job-polling for long LLM tasks
│
├── data/
│   ├── ringStructure.js         Council/Systems/Missions tile definitions
│   └── atlasCore.js             AI personas, phases, teaching modes
│
└── components/ui/               shadcn primitives
```

## Key technical patterns

### 1. Strict radial layout
The HUD geometry is calibrated to exact pixel positions. `ringStructure.js` holds snap angles, `DialRing.js` renders one ring, and `AtlasSidePanel.js` maps `(ring, tile-id)` to the right command surface. Redesign only through the design-bank contract.

### 2. Headquarters first, developer APIs underneath
Product-facing language should say Headquarters, Council Chamber, Mission Control, Knowledge Gate, Source Clearance, Project Briefing, and Refinement Office. Stable developer APIs should remain underneath until migration is safe.

### 3. Job polling for long LLM tasks
The ingress may kill HTTP requests after 60 s. Long tasks submit a job, receive a `job_id`, poll `/api/atlas/jobs/{id}`, and auto-cancel on unmount.

### 4. Abort-on-close everywhere
TTS, job polling, and chat fetches must abort on panel close so hidden panels never leak LLM calls.

### 5. Lava-lamp Canvas2D core
`AtlasCore.js` runs a 60 fps Canvas2D simulation. Audio-reactive pulse comes from `useAudioReactive`. Canvas2D remains the default for reliability on iPad/laptop.

### 6. Multi-AI persona styling
Every workbench panel accepts an `aiColor` prop.

- **Ajani** `#F03246` crimson
- **Minerva** `#28C8BE` teal
- **Hermes** `#E0E0EA` silver
- **Council** `#A878E6` violet

### 7. Premium motion, not noisy neon
The scan-sweep, ring shadows, persona pulse, tile hover stroke, and core saturation bump should decorate existing geometry without turning ATLAS into a random sci-fi skin.

## Required environment

```
REACT_APP_BACKEND_URL=https://...   # base URL for all /api/* calls
```

## Conventions

- All interactive elements have `data-testid` for Playwright drive.
- Hooks return named objects, not ambiguous arrays.
- Panels render inside `.bp-workbench` shell for consistent spacing.
- Command surfaces use ATLAS-facing names while preserving stable backend APIs.
