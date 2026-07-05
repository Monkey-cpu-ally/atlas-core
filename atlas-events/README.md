# ATLAS Event System

## Mission

Allow ATLAS divisions and services to communicate through structured events.

## Example Events

```text
knowledge.source.discovered
knowledge.source.verified
memory.record.created
project.created
project.status.changed
agent.task.assigned
agent.task.completed
council.review.requested
council.review.completed
system.health.warning
```

## Event Contract

Every event should include:

```text
event_id
event_type
timestamp
source_service
actor
payload
priority
correlation_id
```

## Status

Scaffold created. Implementation pending.
