# ATLAS · Knowledge Bank Roadmap
_Generated 2026-06-21 · derived from architecture audit_

## Principle
> Connect real functioning systems only.
> Every collection, route, and worker referenced here must persist real data into MongoDB.
> No mock data, no placeholders, no fake endpoints.

## Status of the 8 KB items the architect requested

| # | Item | Current state | Action |
|---|---|---|---|
| 1 | Research Sources table | 🟡 3 split registries | **Build unified `research_sources` collection + view endpoint** |
| 2 | YouTube Sources table | 🟡 per-video only | **Promote channel-aware schema in `youtube_transcripts_private` + add `youtube_channels`** |
| 3 | Channel Watchlists | 🔴 missing | **Build `youtube_channels` + poll route** |
| 4 | Subject Categories (22) | 🟡 5 hardcoded | **Seed `subjects` collection with the full 22-subject taxonomy** |
| 5 | Knowledge Embeddings storage | 🟢 already running | No change |
| 6 | Agent-specific memory partitions | 🟡 field exists, no API | **Add `/api/membank/agents/{persona}/*` view endpoints + stats** |
| 7 | Shared Atlas Memory Bank | 🟢 IS the `memory_bank` collection | No change |
| 8 | Council recommendation pipeline | 🟢 already running | No change |

## Prioritized build order (this session)

### P0 — schema + seed (must-have, no mocks)
1. Create `subjects` collection — seed 22 canonical subjects (with description, persona-affinity, parent-tag, color).
2. Create `research_sources` view — unified read-only aggregator that maps `worldwatch_feeds` + `watchers` + `youtube_channels` to a single shape.
3. Create `youtube_channels` collection + REST CRUD (`/api/youtube/channels`).
4. Add `/api/youtube/channels/{id}/resolve` — uses existing `youtube_resolver.resolve_channel` to confirm the channel exists and capture upload-RSS URL.
5. Add per-agent memory partition endpoints — `/api/membank/agents/{persona}/list`, `/agents/{persona}/stats`.

### P1 — workers (autonomous loops)
6. Add channel-poll worker — fetches the YT uploads RSS feed for each enabled channel; surfaces new video URLs (not transcripts) into `worldwatch_updates` with `source_type=youtube_channel`. Transcript auto-fetch remains blocked but the architect-driven manual ingest is now connected to a real channel record.
7. Auto-link `youtube_transcripts_private` rows to `youtube_channels` when channel URL matches.

### P2 — pipeline wiring (none mocked, all hits real systems)
8. Subject-category tagging — when content is ingested (intake/youtube/worldwatch), best-effort tag it with a subject id via the existing `ai_categorizer`.
9. Memory-bank → subject join — extend `/api/membank/list` with optional `?subject=` filter.

### Already done in earlier phases (no rebuild)
- Knowledge embeddings (P0 item 5): ST `all-MiniLM-L6-v2` already running on `memory_bank.embedding`.
- Shared Memory Bank (P0 item 7): `memory_bank` collection with persona partitioning by field.
- Council pipeline (P0 item 8): 4-voice auto-invoke in `services/council.py` + research orchestrator.

## 8 ATLAS goals → roadmap mapping

| Goal | Status | What still needs to happen |
|---|---|---|
| Autonomous YouTube learning | 🟡 manual ingest works; channel-watch missing | P0 #3-4 + P1 #6-7 (this session) |
| Autonomous research pipeline | 🟢 single + multi-cycle running | None — already operational |
| Shared Memory Bank | 🟢 production | None |
| Agent-specific memories | 🟡 field exists, no API | P0 #5 (this session) |
| Graph database relationships | 🟢 2753 triples | None — BFS-traversed by Council |
| Project improvement recommendations | 🟢 28 self-improvements pending | None — `SelfImprovementPanel` surfaces them |
| Blueprint generation pipeline | 🟢 BlueprintForge wired | None — runs end-to-end |
| Council decision workflow | 🟢 4-voice auto-invoke | None |

## Out-of-scope (per "no mock data" rule)

- ❌ A "research source quality score" UI without a real scoring algorithm
- ❌ YouTube transcript auto-fetch (Google cloud-IP block — known external limit)
- ❌ Speculative future modules (Pantheon Prime, Hyperaxel, Neo-Terra) — kept hidden

## Deliverables this session

- `services/subjects.py` + `routes/subjects.py` + 22-subject seed (real DB rows)
- `services/research_sources.py` + `routes/research_sources.py` (read-only unified view)
- `services/youtube_channels.py` (CRUD + resolver + poll worker) + routes extension in `routes/youtube.py`
- 3 new agent-partition endpoints on `routes/memory.py`
- Tests: `tests/test_iter24_knowledge_bank.py`
- Audit doc (this file) + `/app/memory/ATLAS_ARCHITECTURE_AUDIT.md`
