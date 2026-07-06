# Phase 5 Developer Setup

This guide explains how to run the current ATLAS Phase 5 scaffold.

## Requirements

```text
Python 3.11+
pytest for tests
make optional but recommended
```

## Install Dev Tools

```bash
python -m pip install -e ".[dev]"
```

## Run Bootstrap Demo

```bash
make bootstrap
```

Expected behavior:

```text
Starts first ATLAS services
Registers them in the Core Runtime registry
Creates demo event, task, memory, source, and knowledge records
Collects health reports
Calls the first API route registry demo
```

## Run Bootstrap With JSON Persistence

```bash
make bootstrap-persist
```

Default data location:

```text
atlas-data/local/bootstrap-demo
```

Expected persisted collections:

```text
events.json
tasks.json
memory_records.json
source_passports.json
knowledge_entries.json
```

## Run Tests

```bash
make test
```

## Run Both

```bash
make smoke
```

## Show Phase 5 Status

```bash
make phase5-status
```

## Current Limitation

JSON persistence exists for local development, but records are not loaded back into services at startup yet.

Next major implementation step:

```text
Add persistence recovery/loading from disk and prepare SQLite adapter planning.
```
