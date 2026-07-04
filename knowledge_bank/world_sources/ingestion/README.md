# World Sources Ingestion

## Purpose
This folder documents how ATLAS should ingest source updates from the World Knowledge Network.

## Ingestion Flow
1. Check approved source registry.
2. Pull metadata only: title, author, date, source URL, abstract/snippet/transcript where permitted.
3. Route to the correct AI owner.
4. Summarize in ATLAS's own words.
5. Compare with existing knowledge.
6. Assign confidence score.
7. Store clean knowledge record with citations.
8. Preserve version history.

## Copyright Rule
ATLAS should store summaries, key findings, metadata, citations, and links. It should not store full copyrighted books, articles, papers, transcripts, or images unless the user owns them or has permission.

## Future Automation
Create scheduled jobs for daily, weekly, monthly, and manual source checks. Important source changes should create Council review tasks.
