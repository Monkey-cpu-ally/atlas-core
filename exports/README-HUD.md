# Atlas Core — HUD Frontend Architecture

The complete React/CSS layer that renders the radial AI operating system.

## Visual layout

```
                    ┌──────────────────────────────────────┐
                    │   Date · Year · Status · Persona     │
                    │                                      │
                    │      ╭─────── Outer Ring ───────╮    │
                    │     ╱   Subjects · Manual ·      ╲   │
                    │    │  Memory · Projects · Lab     │  │
                    │    │  ──── Middle Ring ────       │  │
                    │    │  Cyclopedia · Customization  │  │
                    │    │   ──── Inner Ring ────       │  │
                    │    │   Ajani · Minerva · Hermes   │  │
                    │     ╲   ⟡ Lava Lamp Core ⟡       ╱   │
                    │      ╰──────────────────────────╯    │
                    │                                      │
                    │   FAB · Chat · Upload · Voice        │
                    └──────────────────────────────────────┘
```

The three rings drag-rotate independently with snap angles. The central core
is a touch-reactive Canvas2D lava-lamp simulation (particles + blobs +
audio-reactive pulse). Side panels slide in from the right.

## Layout

```
frontend/src/
├── App.js                       Entry — renders <HUDInterface/>
├── App.css                      Single CSS file (2.9 K LOC) for ALL HUD styling
│                                including rings, panels, sandbox, vibrancy
│
├── components/
│   ├── HUDInterface.js          Main orchestrator — state, voice, FAB, panels
│   ├── ChatPanel.js             Floating chat with EN/ZU/YO/MAA language picker
│   ├── FileUploadModal.js       Chunked upload + AI categorisation
│   ├── FileBrowserPanel.js      Legacy popover (kept; ARCHIVE now uses inline panel)
│   │
│   └── HUD/
│       ├── AtlasCore.js              Central lava-lamp core (Canvas2D + particles)
│       ├── DialRing.js               Drag-to-rotate ring renderer
│       ├── GhostRings.js             Holographic parallax background rings
│       ├── AtlasSidePanel.js         Side-panel router for every tile
│       │
│       ├── BlueprintWorkbench.js     Tri-council blueprint generator UI
│       ├── TeachingWorkbench.js      4-band teach + hands-on sandbox toggle
│       ├── DiagnosticsPanel.js       Core status · events · shield stats
│       │
│       ├── InteractiveSandbox.js     6-lab hands-on simulator
│       │                             (Power/Bridge/Code/Ecosystem/Nanoswarm/Resonance)
│       │
│       ├── ManualPanel.js            Operator manual (collapsible sections)
│       ├── CyclopediaPanel.js        Knowledge index + search
│       ├── MemoryPanel.js            Live event feed (8-second auto refresh)
│       ├── CustomizationPanel.js     Real persisted settings (TTS / lang / theme)
│       ├── CouncilPanel.js           Topic routing + tri-AI deliberation UI
│       ├── IntakePanel.js            YouTube / paste-transcript intake
│       ├── ArchiveBrowser.js         Atlas memory + uploaded files (tabbed)
│       ├── ProjectsPanel.js          Auto-generated projects with status cycle
│       └── QuizTaker.js              Inline quiz with LLM-graded mastery
│
├── hooks/
│   ├── useVoiceRecognition.js   Web Speech API → wake-word & command parsing
│   ├── useTTS.js                Backend TTS with provider + language + abort-on-unmount
│   ├── useAudioReactive.js      Mic level → ring pulse + core hum
│   ├── useAudioFeedback.js      Hover / click / select chimes
│   └── useAtlasJob.js           Non-blocking job-polling for >60s LLM tasks
│
├── data/
│   ├── ringStructure.js         Inner/middle/outer ring tile definitions
│   └── atlasCore.js             AI personas, phases, teaching modes
│
└── components/ui/               shadcn primitives (slider, button, dialog, …)
```

## Key technical patterns

### 1. Strict radial layout (locked)
The HUD geometry is calibrated to exact pixel positions. `ringStructure.js`
holds the snap angles; `DialRing.js` renders one ring; `AtlasSidePanel.js`
maps `(ring, tile-id)` → the right workbench component. **Do not redesign.**

### 2. Job polling for long LLM tasks
The Kubernetes ingress kills HTTP requests after 60 s. The teaching engine
(4-band lesson), the tri-council blueprint, and the council deliberation all
exceed that. `useAtlasJob.js` submits a job, gets a `job_id`, polls
`/api/atlas/jobs/{id}` every 2 s, and auto-cancels on unmount so closing
a panel mid-generation never leaks LLM calls.

### 3. Abort-on-close everywhere
Both `useTTS.js` and `useAtlasJob.js` keep an `AbortController` in a ref
and `.abort()` it in the cleanup effect. ChatPanel does the same with its
`/api/chat/send` fetch. Closing a panel ⇒ all in-flight LLM calls cancel.

### 4. Lava-lamp Canvas2D core
`AtlasCore.js` runs a 60 fps simulation of N particles + M metaballs in a
single `<canvas>` element. Audio-reactive pulse comes from `useAudioReactive`.
Three.js / WebGL was deferred — Canvas2D performs beautifully on iPad/laptop.

### 5. Multi-AI persona styling
Every workbench panel accepts an `aiColor` prop. Persona colours:
- **Ajani** `#F03246` (crimson)
- **Minerva** `#28C8BE` (teal)
- **Hermes** `#E0E0EA` (silver)
- **Council** `#A878E6` (violet)

The sandbox lead-mentor card gets a `.lead` glow ring in its colour.

### 6. Vibrancy additive layer
The scan-sweep, brighter ring drop-shadows, persona pulse, tile hover-stroke,
and core saturation bump are added in App.css ONLY — they decorate the
existing geometry without redrawing it.

## Required environment

```
REACT_APP_BACKEND_URL=https://...   # base URL for all /api/* calls
```

## Conventions

- All interactive elements have `data-testid` for Playwright drive
- Hooks return `{ ref, fn1, fn2 }` not arrays
- Panels render inside `.bp-workbench` shell for consistent spacing
- shadcn primitives imported from `../components/ui/...`
