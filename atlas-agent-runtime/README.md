# ATLAS Agent Runtime

## Mission

Run Hermes, Minerva, Ajani, and the Council as coordinated ATLAS agents.

## Agent Types

```text
specialist_agent
review_agent
council_agent
teaching_agent
research_agent
knowledge_agent
operations_agent
```

## Core Agents

```text
Hermes — engineering, software, robotics, manufacturing
Minerva — science, botany, medicine, environment, design, storytelling
Ajani — strategy, business, risk, operations, planning
Council — final review and synthesis
```

## Agent Contract

Every agent should include:

```text
agent_id
name
role
primary_domains
permissions
available_tools
memory_scope
task_queue
response_format
review_rules
```

## Council Workflow

```text
Task submitted
↓
Hermes review
↓
Minerva review
↓
Ajani review
↓
Council synthesis
↓
Final recommendation
↓
Memory record created
```

## Status

Scaffold created. Implementation pending.
