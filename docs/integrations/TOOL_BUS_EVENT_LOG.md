# ATLAS Tool Bus Event Log

The Tool Bus event log records the lifecycle of every routed tool job.

## Recorded Events

- job received
- safety allowed
- approval required
- safety denied
- adapter verification failed
- job started
- job succeeded
- job failed
- job cancelled

## Why It Matters

The log gives ATLAS traceable history for debugging, HUD timelines, project records, failure analysis, approval tracking, and future memory ingestion.

## Current Storage

The first version uses an in-memory append-only log. It works during one running ATLAS process but is not persistent across restarts.

A future phase should add a durable event store such as SQLite or PostgreSQL while preserving the same event contract.

## Safety

Event metadata should describe actions without storing secrets, access tokens, credentials, or unnecessary sensitive payload data.
