# World Sources Sync History

## Purpose
This folder documents how ATLAS should track source checks over time.

## Sync Event Fields
Future sync records should include:
- sync_id
- source_id
- started_at
- completed_at
- status
- items_found
- items_processed
- new_knowledge_records
- updated_knowledge_records
- errors
- next_sync

## Knowledge Evolution Rule
When a source changes ATLAS's understanding, the old knowledge record should not be deleted. ATLAS should create a new version and explain what changed, why it changed, and which sources caused the update.
