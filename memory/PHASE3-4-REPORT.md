# Phases 3 & 4 — Completion Report

> Status: ✅ **COMPLETE** · Feb 2026 · iteration_12.json (16/16 backend + voice frontend GREEN)

---

## Phase 3 — Research Pipeline

### Surface
| Method | Path | Returns |
|--------|------|---------|
| POST | `/api/research/web`   | `{kind:'web', query, count, sources:[{title,url,host,text,summary,word_count,fetched_at,snippet,skipped?}]}` |
| POST | `/api/research/patent`| `{kind:'patent', query, count, deep, patents:[{id,title,abstract,assignee,inventor,filed,url, claims?, description_excerpt?, engineer_take?, error?}]}` |
| POST | `/api/research/pdf`   | multipart `file=<.pdf>` → `{kind:'pdf', filename, page_count, extracted_pages, chunk_count, metadata, summary, parent_memory_id}` |
| GET  | `/api/research/recent`| `?source_type=web|pdf|patent&limit=20` → research memory list |

### Internals
```
routes/research.py
└── services/research_pipeline.py
    ├── research_web(query)
    │   ├── web_scraper.search_web()    DuckDuckGo HTML
    │   ├── web_scraper.fetch_page()    httpx + selectolax
    │   ├── _summarise() via Hermes
    │   └── memory_bank.auto_store(category='research', source_type='web')
    ├── research_pdf(blob, filename)
    │   ├── pdf_reader.extract_pdf_text()
    │   ├── pdf_reader.chunk_text()     paragraph-aware, 1800c + 200c overlap
    │   ├── _summarise() via Hermes
    │   └── memory_bank.auto_store() parent + N chunks
    └── research_patents(query, deep)
        ├── patent_client.search_patents()           public Google Patents XHR
        ├── patent_client.fetch_patent_detail()      HTML
        ├── _summarise() via Ajani (engineer-take)
        └── memory_bank.auto_store(category='research', source_type='patent')
```

### Failure modes (handled)
* `ResearchUnreachable` raised for cloud-IP blocks / 5xx / non-HTML responses → routes return 503.
* Per-page fetch errors are recorded as `{...,'skipped': reason}` so the rest of the batch can complete.
* `PatentUnreachable` raised for Google Patents rate-limit / blocks → routes return 503.
* PDF: empty file → 400, >12 MB → 413, password-protected → 400 with clean message.
* Memory writes wrapped in `auto_store` (try/except) — never abort the research call.

### Dependencies
* `selectolax==0.4.10` (added to `backend/requirements.txt`)
* `pypdf==6.11.0` (already present)
* `httpx==0.28.1` (already present)
* `reportlab` (test-only, for synthesising PDFs in pytest)

---

## Phase 4 — Voice System restored on Luxury HUD

### Modes (mic button cycles through these)
| Mode | Icon | Title | Behaviour |
|------|------|-------|-----------|
| `off`  | `MicOff` | "Voice off — click to enable push-to-talk" | recognition stopped |
| `push` | `Mic`    | "Push-to-talk active — click for wake-word mode" | one utterance, stops on silence |
| `wake` | `Radio`  | "Wake-word listening — click to stop" | continuous; auto-restarts; transcripts that don't start with a wake phrase ("hey atlas", "atlas", "ok atlas", "atlas core") are silently ignored |

### Files
| File | Role |
|------|------|
| `hooks/useVoiceRecognition.js` | Web Speech API wrapper; callbacks held in refs so the SpeechRecognition instance survives re-renders without re-creating; `getUserMedia` permission pre-flight; lazy isSupported flag. |
| `utils/voiceCommands.js` | `parseVoiceCommand(transcript, {requireWake})` → `{type, ai?, ring?, id?, body?}`. Recognises 4 persona aliases + 11 tile aliases. Greedy longest-match on aliases. |
| `components/HUDInterface.js` | Renders the mic toggle + transcript chip in top-right (`atlas-voice-toggle`, `atlas-voice-transcript`). Wires recognised intents into the existing `setActiveAI`/`setSelectedMiddle`/`setSelectedOuter`/`setPanelContent` orchestrators — i.e. voice exercises the exact same code paths as click. |
| `App.css` lines 3225-3309 | New CSS only — no existing rule modified. Adds `.atlas-voice-toggle` (off/push/wake state colours), pulsing `atlas-voice-pulse` keyframes, and the `.atlas-voice-transcript` chip with `.atlas-voice-dot` blink. |

### Recognised vocabulary
* **Personas**: Ajani / Minerva / Hermes / Council (+ "trinity", "the council")
* **Outer ring**: subjects · lab · projects · blueprints · archive · explore (+ aliases: "teach me", "sandbox", "intake", "youtube", "design"…)
* **Middle ring**: manual · encyclopedia · memory · systems · customization
* **Global**: "stop", "cancel", "close", "never mind" → close current panel

### Wake-phrase examples
> "Hey atlas, open projects"
> "Atlas, lab"
> "OK atlas, minerva let's talk"
> "Atlas core, recall"

In **push-to-talk** mode the wake phrase is optional. In **wake-word** mode it's required.

### HUD visual integrity
* Geometry untouched — three concentric rings + AJANI/MINERVA/HERMES/COUNCIL face dock all present.
* New controls slot beside the existing sound-toggle in the top-right corner; same glass-chip aesthetic, same border treatment, same backdrop-blur.
* When listening in wake mode the mic chip pulses with a violet accent (rgba(168,120,230,*)) — only ambient signal, no panel intrusion.

---

## Verification

### Phase 3 backend
* 16/16 pytest cases in `/app/backend/tests/test_research_phase3.py` — 24 seconds
* Covers: contract shapes, validation (422/400/413), memory auto-write, recent filtering, regression of all Phase 2 endpoints.

### Phase 4 frontend
* Playwright cycle test: voice-toggle present exactly once, icon transitions MicOff → Mic → Radio → MicOff, title updates accordingly.
* DOM contract test: `voice-transcript` absent when transcript empty.
* HUD geometry test: 3 rings + 4 face-dock tiles present.

### Combined report
`/app/test_reports/iteration_12.json` · `success_rate.backend = 100% (16/16)` · `success_rate.frontend = 100%`

---

## Recommended next iteration

Phase 5 (Digital Twin) requires the architect's spec — see PRD.md backlog.
Phase 6 (Weaver) requires the architect's spec.
Phase 7 (Robot Control) requires target hardware.

Until those specs land, suggested polish work (all optional):
1. **Memory Bank inside the MEMORY HUD tile** — replace the placeholder with a live "Recall" search box that hits `/api/membank/search`. Surfaces every lesson/council/blueprint/research row the architect has accumulated. (~1 hour, no aesthetic change.)
2. **Research workbench tab inside IntakePanel** — Web/PDF/Patent tabs that drive the Phase 3 endpoints from the HUD. (~2 hours.)
3. **Voice → Research** — `"Hey atlas, research <topic>"` shortcut firing `POST /api/research/web`. Already partially wired in voiceCommands.js (just needs an `intent.type === 'run-research'` branch). (~30 min.)
4. **Parallelise per-source memory writes** in `research_pipeline` — `asyncio.gather` instead of sequential. Will cut a 5-source web research call from ~30s to ~8s.
