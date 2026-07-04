# ATLAS World Knowledge Connector Engine

## Purpose
The Connector Engine is the backend layer that turns approved World Knowledge Network sources into scheduled research jobs and clean Knowledge Bank records.

This does not mean ATLAS copies websites, papers, videos, or books. It means ATLAS checks approved sources, extracts permitted metadata and snippets, summarizes in its own words, preserves citations, and stores traceable understanding.

## Status
Foundation/specification layer. Backend implementation should be added after tests are reviewed in Emergent/Cursor.

## Core Pipeline
1. Load approved sources from `knowledge_bank/world_sources/source_registry.json`.
2. Choose connector by `access_method` and `source_type`.
3. Create a source sync job.
4. Pull metadata only.
5. Route item to AI owner.
6. Produce summary in ATLAS's own words.
7. Compare against existing Knowledge Bank entries.
8. Assign confidence and verification state.
9. Store a Knowledge Record with original source links.
10. Write sync history and next review time.

## Connector Types
- rss_connector
- api_connector
- web_metadata_connector
- github_connector
- youtube_connector
- patent_connector
- paper_connector
- book_archive_connector
- museum_archive_connector
- personal_notes_connector

## Safety Rules
- Only approved sources may be auto-synced.
- Private sources require explicit user permission.
- Store summaries and citations, not copyrighted works wholesale.
- Medical, legal, financial, biological, and engineering safety claims require stronger verification.
- Low-trust sources can inspire research but cannot establish facts alone.

## Future Backend Targets
Recommended backend files:
- `backend/services/world_knowledge_connector.py`
- `backend/routes/knowledge_network.py`
- `backend/services/knowledge_records.py`
- `backend/tests/test_world_knowledge_connector.py`

## Future API Targets
- `GET /api/knowledge-network/sources`
- `GET /api/knowledge-network/stats`
- `POST /api/knowledge-network/sync/{source_id}`
- `GET /api/knowledge-network/jobs`
- `GET /api/knowledge-network/records`
