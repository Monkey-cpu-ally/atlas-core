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

The event log gives ATLAS a traceable history for:

- debugging
- HUD activity timelines
- engineering audit trails
- project history
- future memory ingestion
- failure analysis
- approval tracking

## Current Storage

The first implementation uses an in-memory append-only log.

This is functional during one running ATLAS process, but it is not persistent across restarts yet.

A later phase should add a durable event store such as SQLite or PostgreSQL while keeping the same event contract.

## Example

```python
job_events = bus.get_job_events(job_id)
for event in job_events:
    print(event.to_dict())
```

## Safety

Event metadata should describe actions without storing secrets, access tokens, private credentials, or unnecessary sensitive payload data.
