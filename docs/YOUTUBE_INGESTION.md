# ATLAS YouTube Ingestion Pipeline

## Current capability

ATLAS now has the core logic for a transcript-first YouTube ingestion pipeline. It can validate common YouTube URLs, normalize authorized transcript segments, create a stable transcript hash for duplicate detection, and produce a review-pending Knowledge Bank record with source attribution.

This foundation does **not** yet fetch captions from YouTube by itself. Network access is intentionally handled through replaceable providers so ATLAS can use an approved YouTube API, authorized caption service, user-supplied transcript, or a future local speech-to-text service.

## Pipeline

1. Accept a YouTube video URL.
2. Validate the host and extract the video ID.
3. Convert it to a canonical YouTube URL.
4. Retrieve metadata through an approved metadata provider.
5. Retrieve authorized captions/transcript through a transcript provider.
6. Normalize the transcript and calculate its SHA-256 hash.
7. Tag the record by ATLAS subject and assigned AI.
8. Store it with `review_status: pending`.
9. Verify important claims using primary or authoritative sources.
10. Promote approved notes into the Knowledge Bank.

## Safety and accuracy rules

- A transcript is evidence of what a video said, not proof that it is correct.
- Do not silently ingest unavailable, private, age-restricted, or unauthorized content.
- Store links, metadata, notes, citations, and authorized transcripts rather than copied video files.
- Detect duplicates using the YouTube video ID and transcript hash.
- Keep provenance when notes are derived from the PrejudiceNeutrino channel directory.
- Medical, legal, financial, chemistry, biological, electrical, and engineering claims require stronger review.

## Next implementation stages

### Stage 2 — Providers

Add an approved metadata provider and transcript provider. Configuration and credentials must use environment variables and must never be committed to GitHub.

### Stage 3 — Knowledge processing

Add transcript chunking, subject classification, difficulty scoring, claim extraction, summaries, quizzes, and citations linked to timestamps.

### Stage 4 — Multimodal review

Sample key frames only when visuals are necessary, such as diagrams, equations, demonstrations, circuit layouts, fabrication steps, or software interfaces. Frame analysis should supplement—not replace—the transcript and source verification.

### Stage 5 — Scheduling

Add a queue that limits channel ingestion, retries temporary failures, records audit events, and avoids repeatedly processing the same video.

## Main code

`atlas-knowledge-engine/src/atlas_knowledge_engine/youtube_ingestion.py`

## Tests

`atlas-tests/tests/test_youtube_ingestion.py`
