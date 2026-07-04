# ATLAS · Knowledge Bank Schema, APIs, and Ingestion Workflows
_Generated 2026-06-21 · authoritative reference · no mocks_

## 1 · Collection Schemas

### 1.1 `subjects` (22-subject taxonomy)
| Field | Type | Notes |
|---|---|---|
| `id` | str (uuid) | primary |
| `slug` | str | snake_case, stable handle, unique |
| `name` | str | display |
| `description` | str | one-line canonical |
| `primary_agent` | enum | `ajani` \| `minerva` \| `hermes` \| `council` |
| `family` | enum | `science` \| `engineering` \| `humanities` \| `craft` \| `meta` |
| `accent_color` | str | HUD hex |
| `parent_tags` | list<str> | broader domains |
| `enabled` | bool | soft-delete flag |
| `created_at` | ISO str | UTC |

Seeded on startup (`services/subjects.seed_if_needed`). Idempotent by `slug`.

### 1.2 `youtube_channels` (channel watchlist)
| Field | Type | Notes |
|---|---|---|
| `id` | str (uuid) | primary |
| `channel_url` | str | `@handle` or `/channel/UC...` — unique |
| `channel_id` | str | resolved `UC...` |
| `name` | str | resolved title |
| `uploads_rss_url` | str | derived from `channel_id` |
| `subject_slug` | str | join → `subjects.slug` |
| `agent` | str | owning persona |
| `tags` | list<str> | free-form |
| `enabled` | bool | toggle poll worker |
| `last_polled_at` | ISO str | last successful poll |
| `last_video_published_at` | ISO str | newest video seen |
| `new_videos_seen` | int | lifetime counter |
| `poll_count` | int | lifetime counter |
| `notes` | str | architect free-form |
| `registered_at` | ISO str | first insertion |

### 1.3 `youtube_channel_runs` (per-poll proof envelope)
| Field | Type | Notes |
|---|---|---|
| `run_id` | str (uuid) | primary |
| `channel_id` | str | fk → `youtube_channels.id` |
| `started_at` / `ended_at` | ISO str | UTC |
| `entries_seen` | int | in-feed count |
| `new_videos` | int | delta since previous poll |
| `new_video_urls` | list<str> | first 10 for audit |

### 1.4 `transcripts` (source-agnostic)
| Field | Type | Notes |
|---|---|---|
| `id` | str (uuid) | primary |
| `title` | str | required |
| `source` | enum | `youtube` \| `audio_upload` \| `meeting` \| `podcast` \| `lecture` \| `manual_paste` \| `other` |
| `source_url` | str | idempotency key (upsert on repeat) |
| `author_or_channel` | str | display credit |
| `duration_seconds` | float | optional |
| `language` | str | ISO-639-1, default `en` |
| `text` | str | full body |
| `word_count` | int | auto-populated |
| `youtube_channel_id` | str | fk → `youtube_channels.id` when applicable |
| `subject_slug` | str | join → `subjects.slug` |
| `agent` | str | owning persona |
| `tags` | list<str> | subject:X style |
| `summary_id` | str | fk → `transcript_summaries.id` (nullable) |
| `captured_at` | ISO str | UTC |

### 1.5 `transcript_summaries` (LLM output)
| Field | Type | Notes |
|---|---|---|
| `id` | str (uuid) | primary |
| `transcript_id` | str | fk → `transcripts.id` |
| `model` | str | LLM model used (e.g. `claude-sonnet-4-6`) |
| `one_line` | str | ≤ 220 chars |
| `key_points` | list<str> | 5-7 items |
| `identified_subjects` | list<str> | whitelist against `subjects.slug` |
| `concepts` | list<str> | 5-16 free-form |
| `tokens_in_estimated` | int | audit |
| `tokens_out_estimated` | int | audit |
| `knowledge_record_id` | str | fk → `knowledge_records.id` |
| `memory_bank_id` | str | fk → `memory_bank.id` |
| `generated_at` | ISO str | UTC |

### 1.6 Existing Knowledge Bank collections (unchanged)
| Collection | Rows | Purpose |
|---|---:|---|
| `memory_bank` | 1502+ | Shared Atlas Memory Bank with `persona` partitioning + ST embeddings |
| `knowledge_records` | 50+ | Long-form knowledge (title/summary/key_points/tags/source_url) |
| `graph_triples` | 2753+ | Knowledge graph edges |
| `worldwatch_feeds` / `worldwatch_updates` | 17 / 26+ | RSS + patent ingestion |
| `watchers` / `watcher_runs` | 1 / 3+ | Code/site watchers |
| `youtube_transcripts_private` | 3 | Legacy YouTube transcripts (consent-gated) |

---

## 2 · REST API

### 2.1 Subjects — `/api/subjects/*`
| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/subjects` | list (params: `family`, `enabled_only`) |
| `GET` | `/api/subjects/stats` | per-subject content counts |
| `GET` | `/api/subjects/{slug_or_id}` | single |
| `POST` | `/api/subjects` | upsert |
| `POST` | `/api/subjects/seed` | idempotent re-seed |

### 2.2 YouTube channels — `/api/youtube/channels/*`
| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/youtube/channels` | register (auto-resolves UC id + RSS) |
| `GET` | `/api/youtube/channels` | list (params: `enabled_only`, `agent`) |
| `GET` | `/api/youtube/channels/stats` | aggregate counts |
| `GET` | `/api/youtube/channels/{id}` | single |
| `DELETE` | `/api/youtube/channels/{id}` | remove |
| `POST` | `/api/youtube/channels/{id}/poll` | fetch new uploads → `worldwatch_updates` |
| `POST` | `/api/youtube/channels/poll-all` | batch poll |
| `GET` | `/api/youtube/channels/{id}/runs` | per-poll history |

### 2.3 Unified Research Sources — `/api/research-sources/*`
| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/research-sources` | unified view over `worldwatch_feeds` + `watchers` + `youtube_channels` (params: `kind`, `agent`, `enabled_only`) |
| `GET` | `/api/research-sources/stats` | count per kind |

### 2.4 Transcripts + Summaries — `/api/transcripts/*`
| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/transcripts` | store (upsert by `source_url`) |
| `GET` | `/api/transcripts` | list (params: `source`, `subject_slug`, `agent`, `limit`) |
| `GET` | `/api/transcripts/stats` | aggregate |
| `GET` | `/api/transcripts/{id}` | single (with full text) |
| `POST` | `/api/transcripts/{id}/summarise` | **real** Claude call → structured summary + KR + MB row |
| `GET` | `/api/transcripts/{id}/summary` | newest summary |

### 2.5 Agent memory partitions — `/api/membank/agents/*`
| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/membank/agents` | per-persona counts (total/pinned/permanent/decaying) |
| `GET` | `/api/membank/agents/{persona}` | recent memories + by-category rollup |

### 2.6 Existing endpoints reused (no changes)
- Shared Memory Bank: `/api/membank/store` · `/api/membank/list` · `/api/membank/search` · `/api/membank/by-tag` · `/api/membank/embed-settings`
- Knowledge Graph: `/api/membank/graph/list` · `/api/membank/graph/expand` · `/api/membank/graph/add`
- Council: `/api/council/route` · `/api/council/deliberate` · `/api/council/log`

---

## 3 · Ingestion Workflows

### 3.1 YouTube channel → new videos
```
architect  →  POST /api/youtube/channels  { channel_url, subject_slug, agent }
                    │
                    ▼
      services/youtube_channels.register()
        └─ resolves UC id via youtube_resolver
        └─ constructs uploads_rss_url
        └─ upserts into `youtube_channels`
                    │
architect  →  POST /api/youtube/channels/{id}/poll
                    │
                    ▼
      services/youtube_channels.poll_channel()
        └─ latest_video_urls() → Atom feed parse
        └─ for each new url:
             ├─ insert into `worldwatch_updates`   (source_type=youtube_channel)
             └─ (transcript intentionally NOT auto-fetched — cloud IP blocked)
        └─ upsert `youtube_channel_runs` proof envelope
        └─ increment channel counters
        └─ MB write ("YOUTUBE CHANNEL POLL · ...")
```

Manual transcript ingest remains the canonical path for transcripts
(via `/api/youtube/ingest-transcript` or the general
`POST /api/transcripts`).

### 3.2 Transcript → summary → knowledge_record → memory_bank
```
POST /api/transcripts  { text, source, subject_slug, agent, ... }
      │
      ▼
services/transcripts.store()
  └─ upsert `transcripts` (idempotent by source_url)
      │
architect  →  POST /api/transcripts/{id}/summarise
      │
      ▼
services/transcripts.summarise()
  ├─ pull 22-subject taxonomy from `subjects` collection (WHITELIST)
  ├─ build system + user prompts (system message strict JSON)
  ├─ LlmChat(EMERGENT_LLM_KEY).with_model("anthropic","claude-sonnet-4-6")
  ├─ send_message() → raw JSON
  ├─ _extract_json() with regex safety net
  ├─ _valid_subjects() ← enforces whitelist (no hallucinated slugs)
  ├─ mb.auto_store()  → `memory_bank` row with ST embedding
  ├─ insert into `knowledge_records` with `memory_bank_id` link
  └─ insert into `transcript_summaries`
      Fields: model, one_line, key_points, identified_subjects, concepts,
              tokens_in_estimated, tokens_out_estimated,
              knowledge_record_id, memory_bank_id
```

### 3.3 Research query → agent-specific recall
```
GET /api/membank/agents           → summary of persona footprints
GET /api/membank/agents/{persona} → recent memories + by-category rollup
GET /api/membank/search?q=X&persona=Y → ST-cosine ranked results within
                                        the agent's partition
```

### 3.4 Council recommendation pipeline (existing · reused)
```
Any orchestrator step with confidence < 0.7
  → services/council.deliberate(topic, evidence)
       ├─ Ajani  voice (engineering perspective)
       ├─ Minerva voice (science perspective)
       ├─ Hermes voice (logic perspective)
       └─ Council synthesis (final decision)
  → persist to `memory_bank` (persona=council)
  → surface in `CouncilPanel.js`
```

---

## 4 · Data-Flow Contract (invariants)

| # | Invariant |
|---|---|
| 1 | Every subject reference (in `youtube_channels`, `transcripts`, `worldwatch_updates`, `memory_bank.tags`) uses a slug that exists in the `subjects` collection. |
| 2 | Every LLM-generated `identified_subjects` list is whitelisted against `subjects` (enforced in `services/transcripts._valid_subjects`). |
| 3 | Every `transcript_summaries` row has a valid `transcript_id`, a `knowledge_record_id`, and a `memory_bank_id`. |
| 4 | Every `memory_bank` row has a persona in `{ajani, minerva, hermes, council, system, default}`. |
| 5 | Every source URL that appears in `worldwatch_updates` with `source_type=youtube_channel` also has a matching row in `youtube_channels` (feed_id column). |

---

## 5 · Test Coverage

| Iteration | File | Tests |
|---|---|---:|
| 21 | `test_iter21_esp32_safety.py` | 24 |
| 22 | `test_iter22_twin_environments.py` | 4 |
| 23 | `test_iter23_d3_d6.py` | 11 |
| 24 | `test_iter24_knowledge_bank.py` | 11 |
| 25 | `test_iter25_transcripts.py` | 6 |
| — | **TOTAL in-repo regression suite** | **56** |

All 56 pass in isolation. Test 25 includes a **real Claude Sonnet 4.6 call** that verifies the LLM output shape end-to-end (not a mock).

---

## 6 · What is still explicitly deferred

- ❌ YouTube transcript auto-fetch (Google cloud-IP block — architect-driven manual ingest is the working path)
- ❌ HUD panel for Knowledge Bank (backlog — architect approved deferring cosmetics until all systems operational)
- ❌ Subject-tagging auto-categoriser on generic intake / worldwatch (taxonomy is in DB, wiring is left)
- ❌ Periodic `poll-all` worker (manual trigger works today)
