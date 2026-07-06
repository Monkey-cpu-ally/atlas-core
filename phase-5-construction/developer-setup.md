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
Starts first in-memory ATLAS services
Registers them in the Core Runtime registry
Creates demo event/task/memory/source/knowledge records
Collects health reports
Calls the first API route registry demo
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

This is still an in-memory foundation. Data does not persist across runs yet.

Next major implementation step:

```text
Add persistence adapters for memory, knowledge, tasks, events, and agents.
```
