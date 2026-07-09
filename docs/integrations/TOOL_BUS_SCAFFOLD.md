# ATLAS Tool Bus Scaffold

This document describes the first scaffold for the ATLAS Tool Bus.

## Branch

```text
atlas/tool-bus-scaffold
```

## Scope

This branch creates the first safe implementation scaffold for routing ATLAS work to external tools.

It does not connect live services.

## Added Systems

```text
src/atlas/tool_bus/
```

Main files:

- `contracts.py` — shared dataclasses, status enums, safety levels, and adapter protocol.
- `bus.py` — Tool Bus registry and dispatcher.
- `registry.py` — default scaffold registry.
- `adapters/base.py` — safe placeholder adapter base.
- `adapters/blender.py` — Blender scaffold.
- `adapters/neo4j.py` — Neo4j scaffold.
- `adapters/ollama.py` — Ollama scaffold.
- `adapters/kicad.py` — KiCad scaffold.
- `adapters/ros2.py` — ROS 2 scaffold.
- `adapters/isaac_sim.py` — Isaac Sim scaffold.

## Safety

All adapters are placeholders.

They expose capabilities, but they do not perform live actions yet.

No API keys, local machine paths, credentials, secrets, or external service calls are included.

## Agent Ownership

### Hermes

- Blender
- KiCad
- ROS 2
- Isaac Sim
- future CAD/Fusion adapter

### Minerva

- Neo4j
- research systems
- knowledge-bank systems

### Ajani

- future planning/risk/project-management adapters

### Council

- future review and approval routing

## Next Steps

1. Add tests for the Tool Bus contracts and registry.
2. Add a safety gate layer.
3. Add a job event log.
4. Add a local-only Blender script generator.
5. Add an Ollama read-only status check.
6. Add Neo4j connection config only after secrets handling is defined.

## Rule

The Tool Bus must stay modular. No ATLAS agent should depend directly on Blender, Neo4j, Ollama, KiCad, ROS 2, or Isaac Sim.
