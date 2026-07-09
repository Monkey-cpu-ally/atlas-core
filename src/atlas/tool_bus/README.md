# ATLAS Tool Bus

The ATLAS Tool Bus is the standard integration layer between ATLAS agents and external tools.

It is designed so Hermes, Minerva, Ajani, Council, and future agents can request work from tools without being tightly coupled to specific software.

## Current Status

Scaffold only.

This branch does not connect live services, does not store secrets, and does not execute destructive actions.

## Purpose

The Tool Bus should eventually route jobs to:

- Blender
- CAD/Fusion
- KiCad
- ROS 2
- Isaac Sim
- Neo4j
- Ollama
- research systems
- future engineering tools

## Core Principle

Agents should not call external tools directly.

Agents should submit a job to the Tool Bus. The Tool Bus chooses the correct adapter, validates the request, runs the job, collects logs/artifacts, and returns a structured result.

## Standard Adapter Lifecycle

Every adapter should support:

```text
initialize()
connect()
verify()
get_capabilities()
get_status()
execute(job)
cancel(job_id)
disconnect()
```

## Standard Job Result

Every job should return:

```text
success
status
job_id
tool_name
started_at
finished_at
execution_time_ms
logs
artifacts
errors
warnings
metadata
```

## Safety Rules

- No hardcoded API keys.
- No machine-specific absolute paths.
- No live tool execution until adapters are explicitly enabled.
- No destructive actions without a safety gate.
- Every tool must be replaceable.
