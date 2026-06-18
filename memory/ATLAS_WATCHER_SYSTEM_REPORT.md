# ATLAS · Watcher System Report

> **Status as of 2026-06-18.** End-to-end test run executed against
> `https://github.com/PrejudiceNeutrino/YouTube_Channels` with real IDs and
> on-disk Mongo evidence.

---

## What was built

### Part 1 — GitHub + YouTube Knowledge Watcher

| Component | File | Lines |
| --------- | ---- | ----: |
| Service | `/app/backend/services/knowledge_watcher.py` | 308 |
| Lesson generator | `/app/backend/services/lesson_generator.py` | 196 |
| Routes (8) | `/app/backend/routes/watchers.py` | 79 |
| Lesson routes (3) | `/app/backend/routes/lessons.py` | 28 |

**Pipeline.** `register_github_source` → `_fetch_github` (existing kbase
infra) → `_extract_links` (URL regex with markdown-heading category lookup)
→ for each link `ki.ingest_url(...)` → graph triples auto-wired by
`knowledge_ingestion._wire_graph` → if generate_lesson: `_generate_lesson`
via gpt-5.2 → persist `watcher_runs` document.

### Part 2 — ATLAS Self-Improvement Watcher

| Component | File | Lines |
| --------- | ---- | ----: |
| Service | `/app/backend/services/self_improvement.py` | 154 |
| Routes (6) | `/app/backend/routes/self_improve.py` | 87 |

**Contract.** Proposals always start `status=pending`. Approval is required
for `risk_level in {medium,high}` OR `category in {code_architecture,
agent_personality}`. The agent never silently applies a change — every
status transition goes through `/api/self-improve/approve/{id}` or
`/reject/{id}`. Weekly report is **computed live** from the last 7 days of
records; no background thread.

### Mongo collections introduced
- `watchers` — registry, 1 row after test
- `watcher_runs` — proof-of-execution, **3 rows** after test
- `lessons` — generated lesson plans, **7 rows** after test
- `self_improvements` — proposals, **1 row** after test

### Endpoints introduced (11 total)
```
GET   /api/watchers/sources
POST  /api/watchers/github/register
POST  /api/watchers/github/run
GET   /api/watchers/github/status
GET   /api/watchers/proof/{source_id}
GET   /api/kbase/sources/github
GET   /api/lessons/generated
GET   /api/lessons/by-source
GET   /api/lessons/{lesson_id}
GET   /api/self-improve/proposals
POST  /api/self-improve/propose
POST  /api/self-improve/approve/{id}
POST  /api/self-improve/reject/{id}
GET   /api/self-improve/history
GET   /api/self-improve/weekly-report
```

---

## Live test against the user's URL

**Source.** `https://github.com/PrejudiceNeutrino/YouTube_Channels`

**Registered source ID.** `a2f334e53c8f49a3bbbdb4e1e3b28611`
**Source hash.** `4218d71a2ac9c0142ac72366`
**Registered at.** `2026-06-18T11:35:39.374011+00:00`

### Run #3 (the run shown to the user)
**run_id.** `705e6a1c30cd45adbbebaf3f41009680`
**Status.** `ok` · **Errors.** `0`

| Metric | Value | User requirement |
| ------ | ----: | ---------------- |
| GitHub source registered | ✅ id `a2f334e5…` | yes |
| README scanned | ✅ 57,799 chars | yes |
| Links extracted | **15** | ≥ 5 ✅ |
| Sources categorised (with markdown heading) | **15** under categories like *“Personal Favorites:”*, *“YouTube Channels & Other Resources”*, *“Educational - Math, Logic, Programming, Coding”* | ≥ 5 ✅ |
| Knowledge entries created | **15** (1 real Google-Doc ingest reused across runs + 14 TRANSCRIPT_UNAVAILABLE stubs) | ≥ 3 ✅ |
| Memory entries created | **15** | ≥ 3 ✅ |
| Graph edges created in this run | **24** | ≥ 3 ✅ |
| Lesson plans created | **1** (lesson_id `671582b765b04d9e8f37191d720eb0c5`) | ≥ 1 ✅ |
| Transcripts found | 0 | — |
| Transcripts unavailable | 14 (channel URLs — see below) | — |

**Total ATLAS Mongo state after test:**
`graph_triples=1316 · knowledge_records=21 · transcript_unavailable_records=14 · watchers=1 · watcher_runs=3 · lessons=7 · self_improvements=1`

### The generated lesson (real artefact, not a stub)
```
lesson_id:       671582b765b04d9e8f37191d720eb0c5
title:           Build a YouTube Channel Directory from a Google Doc
                 (and Make It Actually Useful)
subject:         Digital literacy + information organization
                 (Google Docs + YouTube research)
skill_level:     beginner
agent:           council
model_used:      gpt-5.2
learning_objectives:
  - Explain what a "content list/channel directory" is and why it's useful
  - Turn a messy list of YouTube channels into a clean, searchable directory
    in Google Docs
  - Check source visibility and share settings so other people can access
    the directory
hands_on_project: Make a 'Council Picks' YouTube Channel Directory (1-page version)
hands_on_steps_count:  3
quiz_questions_count:  4
vocabulary_count:      5
related_sources:       https://docs.google.com/document/d/1M5kvDldTCDCNgrlNx6fcDF1h81fnKX6Ovvm20L06Jtk/edit
next_lesson_suggestion: Upgrade your directory into a searchable spreadsheet...
```

### First 8 extracted links (raw, with category headings)
```
1. https://docs.google.com/document/d/1M5kvDld.../edit            kind=web              category=YouTube Channels & Other Resources
2. https://www.youtube.com/user/Top10Memes/videos                 kind=youtube_channel  category=Personal Favorites:
3. https://www.youtube.com/user/melodysheep/videos                kind=youtube_channel  category=Personal Favorites:
4. https://www.youtube.com/c/zefrank/videos                       kind=youtube_channel  category=Personal Favorites:
5. https://www.youtube.com/channel/UCAL3JXZSzSm8AlZyD3nQdBA/videos kind=youtube_channel category=Personal Favorites:
6. https://www.youtube.com/c/CasuallyExplained/videos             kind=youtube_channel  category=Personal Favorites:
7. https://www.youtube.com/user/bkraz333/videos                   kind=youtube_channel  category=Personal Favorites:
8. https://www.youtube.com/c/SebastianLague/videos                kind=youtube_channel  category=Personal Favorites:
```

### Self-Improvement proposal created in the same session
```
id:                 410a020f53e34e3997c96e70664eda24
observed_pattern:   YouTube channel URLs (not video URLs) cannot be transcript-
                    fetched — system marks 14/15 watcher links TRANSCRIPT_UNAVAILABLE
affected_system:    services/knowledge_watcher.py + services/source_fetchers.py
proposed_change:    Add a channel-resolver step: when encountering a YouTube
                    channel URL, fetch its uploads RSS feed and queue the most
                    recent 3 video URLs for transcript ingestion instead.
category:           research_source
risk_level:         low
confidence_score:   0.85
status:             approved
decision_note:      approved — channel-resolver is a sensible upgrade
```

---

## What is REAL

| Surface | Evidence |
| ------- | -------- |
| GitHub README fetch via `api.github.com` (60 KB cap) | `proof.files_scanned[0] = {filename: 'README', chars: 57799}` |
| URL extraction + markdown-heading categorisation | 15 distinct URLs with 4 distinct category headings |
| Idempotent source registration (sha256-keyed) | second `register` call returned the same `source_id` with `run_count: 3` |
| Knowledge-Memory-Graph triple write per ingest | `knowledge_records=21 · memory_bank.tag=watcher:* exists · graph_triples=1316 (+24 in last run)` |
| TRANSCRIPT_UNAVAILABLE stub recording (URL + category only) | 14 rows in `knowledge_records` with `transcript_status=TRANSCRIPT_UNAVAILABLE`, **no copyrighted body text stored** |
| Lesson generation via gpt-5.2 (real LLM) | `lesson.model_used=gpt-5.2 · provider_used=emergent` |
| Self-improvement proposal lifecycle (pending → approved/rejected, audit trail) | proposal `410a020f…` transitioned `pending → approved` with `decision_note` persisted |
| Weekly self-improvement roll-up | `/api/self-improve/weekly-report` returned `total_proposals=1 · by_status={approved:1}` |
| Proof endpoint with raw IDs | `/api/watchers/proof/{source_id}` returns the full run record verbatim |

## What is SIMULATED (LLM-produced, not a real-world process)

| Surface | Why simulated |
| ------- | ------------- |
| Lesson "skill_level" classification | gpt-5.2 picks the level from concepts — no learner-model behind it |
| Lesson `learning_objectives`, `hands_on_project`, `quiz_questions` | All generated by the LLM per-call; not pulled from a curated pedagogy database |
| Knowledge "confidence_score" | LLM self-reports its confidence — not validated against an oracle |
| Self-improvement `confidence_score` | Set by the caller (ATLAS itself or a human); no calibration |
| Persona "voice" inside lessons | Prompt-driven; same caveat as Phase-8 personas — `gpt-5.2` plays along |

## What requires API keys

| Surface | Key | Status |
| ------- | --- | ------ |
| Lesson LLM call | `EMERGENT_LLM_KEY` (in `/app/backend/.env`) | ✅ present, used by `services/llm_provider.send` |
| Knowledge distillation | `EMERGENT_LLM_KEY` (same key, same path) | ✅ present |
| Real OpenAI **embeddings** | `OPENAI_API_KEY` | ❌ **not set** — Memory Bank still uses the hash embedder fallback. The Emergent universal key does NOT cover the `/v1/embeddings` endpoint. |
| ElevenLabs TTS (lesson voice playback) | `ELEVENLABS_API_KEY` | ⚠️ key present but cloud-IP blocked on free tier; OpenAI TTS fallback active |
| GitHub authenticated calls | `GITHUB_TOKEN` (optional) | ❌ not set — anonymous calls hit 60 req/h rate-limit |

## What requires YouTube transcripts

| Need | Status |
| ---- | ------ |
| Transcript fetch for a single **video URL** (`youtube.com/watch?v=…`) | works via `youtube_transcript_api`, but **this preview env's cloud IP is blocked by YouTube** — verified in REALITY_CHECK_REPORT §8 |
| Transcript fetch for a **channel URL** (`/user/X/videos`, `/c/X/videos`, `/channel/UC.../videos`) | **NOT POSSIBLE** without a resolver — channels have no transcript. Self-improvement proposal `410a020f…` proposes the fix (RSS feed → latest video URLs). |
| Transcript fetch for a **playlist URL** (`?list=…`) | Same — needs a resolver to enumerate the playlist's videos first |
| Permanent storage of **full transcript text** | ❌ **Intentionally not stored.** Per the user's rule: copyrighted transcripts are never permanently stored unless explicitly marked local/private. We store only summary + concept list + source URL for citation. |

## What requires local hardware

Nothing in the Watcher Systems requires hardware. The downstream **Robot
Control / ESP32 / MQTT** layers do (still UNTESTED per
`ATLAS_TRUTH_REPORT.md`), but the Watcher Systems are pure software.

## What is not finished (and the gap)

| Gap | Severity | Path to close |
| --- | -------- | ------------- |
| YouTube channel/playlist URLs don't resolve to videos | **High** for this use case | Adopt self-improvement proposal `410a020f…` — fetch the channel's RSS feed (`https://www.youtube.com/feeds/videos.xml?channel_id=…`) and queue the latest 3 video URLs |
| Cloud-IP block on YouTube transcript API | High | Either move to a non-blocked deployment, or proxy through a residential-IP relay. **Cannot be fixed in this env.** |
| Lesson generation only fires once per run | Low | Could iterate over all real-fetched ingests and produce a lesson per concept-cluster. Currently picks the first viable ingest only. |
| No webhook on GitHub push → auto-run | Medium | Add `POST /api/watchers/github/webhook` accepting GitHub push events. Today the watcher is **on-demand only** (manual `/run`). |
| No diff-vs-last-commit (full re-scan each run) | Medium | Store the README hash; only re-process new URLs on subsequent runs. The watchers collection already has `last_commit_sha` populated as `_hash_first_line(readme_text)` placeholder — extend to a content-aware diff. |
| No PDF/website-specific extraction beyond what `kbase` already does | Low | Inherits whatever `source_fetchers` supports. PDF and web fetch work today. |

---

## Repro instructions

```bash
API=http://127.0.0.1:8001         # or REACT_APP_BACKEND_URL externally

# 1. Register the source
curl -s -X POST "$API/api/watchers/github/register" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/PrejudiceNeutrino/YouTube_Channels"}'

# 2. Run the watcher (max_links=15 is recommended for a first pass)
curl -s -X POST "$API/api/watchers/github/run" \
  -H "Content-Type: application/json" \
  -d '{"source_id":"<id_from_step_1>","generate_lesson":true,"max_links":15}'

# 3. Pull proof
curl -s "$API/api/watchers/proof/<id_from_step_1>" | jq .

# 4. Read the lesson
curl -s "$API/api/lessons/generated?limit=1" | jq .

# 5. Self-improvement
curl -s -X POST "$API/api/self-improve/propose" \
  -H "Content-Type: application/json" \
  -d '{"observed_pattern":"...","affected_system":"...",
       "proposed_change":"...","category":"workflow","risk_level":"low"}'
```

---

_Source files of record:_
- `/app/backend/services/knowledge_watcher.py`
- `/app/backend/services/lesson_generator.py`
- `/app/backend/services/self_improvement.py`
- `/app/backend/routes/watchers.py`
- `/app/backend/routes/lessons.py`
- `/app/backend/routes/self_improve.py`
- `/tmp/watcher_run3.json` (raw output of run `705e6a1c30cd45adbbebaf3f41009680`)
