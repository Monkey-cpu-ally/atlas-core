# Atlas Core — AI Cognitive Architecture

A complete bundle of the cognition, routing, and learning-pipeline code that powers Atlas Core.

## Pipeline at a glance

```
Video / Transcript / Upload
        ↓
Hermes Reads     (pattern extraction, transcript fetch)
        ↓
Topic Router     route_topic() → Ajani | Minerva | Hermes | Council
        ↓
Ajani Studies    (Titan / Gaia / Mercury cognitive cores)
        ↓
Ajani Creates    Lesson · Blueprint · Project · Quiz
        ↓
Council          tri-AI deliberation on ambiguous topics
        ↓
Mastery          quiz grading + per-topic curve
```

## Layout

```
atlas_core/
├── cores/                  Titan (engineering), Gaia (life), Mercury (patterns)
├── council/                Council router & deliberation
├── teaching_engine/        4-band lesson builder
├── blueprint_engine/       Tri-council blueprint generator
├── archive_engine/         Classified file storage
├── shield_core/            Hard-rule enforcement
└── memory/                 MongoDB-backed persistent memory

backend/
├── routing/
│   └── topic_router.py     AJANI / MINERVA / HERMES keyword map + route_topic()
└── routes/
    ├── ai_services.py      TTS (OpenAI + ElevenLabs multilingual)
    ├── chat.py             Per-persona chat
    ├── council.py          /api/council/route + /deliberate
    ├── intake.py           YouTube transcript intake → lesson + quiz
    ├── learning.py         Full learning pipeline (knowledge/lessons/projects/quiz/mastery/journal)
    ├── sandbox.py          AI Suggest + save/load + mastery curve
    └── hud_surfaces.py     Manual / Memory feed / Settings
```

## Data model (MongoDB collections)

| Collection | Purpose |
|---|---|
| `knowledge` | Ingested videos/transcripts: title, topic, source, transcript, summary, ai_owner |
| `lessons` | Per-knowledge lesson body + reflection + nature_connection + flashcards + next_topic |
| `projects` | Auto-suggested hands-on project per lesson, with status |
| `mastery` | Quiz attempts, per-question scores, aggregate rank |
| `study_journal` | Free-form architect notes per lesson |
| `sandbox_runs` | Auto-recorded sandbox runs (top-3 per lab per day) |
| `sandbox_saved` | Named saved configurations |
| `atlas_archive` | File uploads + classified artefacts |
| `atlas_events` | Live event feed |
| `atlas_settings` | TTS provider, default language, accent theme |

## AI personas

- **Ajani** — Zulu warrior-engineer · #F03246 · Hard rule: no energy system you cannot safely shut down.
- **Minerva** — Yoruba wisdom keeper · #28C8BE · Hard rule: no irreversible harm in the name of optimisation.
- **Hermes** — Maasai pattern hunter · #E0E0EA · Hard rule: never design nanobots capable of self-replication.
- **Council** — All three deliberate when no domain match.

## Required environment

```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
EMERGENT_LLM_KEY=...   # Universal key for OpenAI / Anthropic / Gemini
ELEVENLABS_API_KEY=... # Optional — falls back to OpenAI TTS if absent
```

## Models in use

- `claude-sonnet-4-5-20250929` — sandbox AI Suggest (persona-flavoured slider tweaks)
- `gpt-5.2` — chat, council deliberation, learning pipeline (lesson/project/quiz grading)
- `tts-1` (OpenAI) — fallback TTS
- `eleven_multilingual_v2` — primary TTS when ElevenLabs key configured
