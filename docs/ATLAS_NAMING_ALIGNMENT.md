# ATLAS Naming Alignment

This document keeps ATLAS naming consistent across older code, current documentation, and future systems.

## Official User-Facing Names

The official ATLAS AI names are:

- **Ajani**
- **Minerva**
- **Hermes**
- **Council**

These are the names that should appear in user-facing documentation, HUD labels, prompts, project planning, and future ATLAS workflows.

## Legacy / Internal Names

Some older ATLAS Core files use earlier implementation names:

| Legacy Name | Official Name | Preferred Role |
| --- | --- | --- |
| Titan | Ajani | strategy, execution, risk, operations, practical decision-making |
| Gaia | Minerva | research, science, environment, botany, education, culture, storytelling |
| Mercury | Hermes | engineering, software, robotics, manufacturing, architecture, validation |

These legacy names should not be treated as separate AIs. They are early code aliases that should gradually be renamed or wrapped with official names.

## Migration Rule

Do not break working code just to rename files quickly.

Use this safer order:

1. Document the mapping.
2. Add official-name wrappers where needed.
3. Update comments and docs first.
4. Rename modules only after tests pass.
5. Remove legacy names only when no active imports depend on them.

## Folder Naming Preference

New files should use official names:

```text
ajani
minerva
hermes
council
```

Avoid creating new user-facing files with:

```text
titan
gaia
mercury
```

unless maintaining compatibility with existing code.

## Tool Ownership Alignment

Future tool integrations should follow this ownership model:

### Hermes

- Blender
- CAD/Fusion
- KiCad
- ROS 2
- Isaac Sim
- manufacturing tools
- blueprint validation
- simulation and engineering checks

### Minerva

- research ingestion
- source catalogs
- knowledge-bank systems
- graph memory / Neo4j planning
- science, botany, environment, culture, education

### Ajani

- project strategy
- risk review
- business planning
- operations
- priorities
- roadmap decisions

### Council

- final synthesis
- disagreement resolution
- major decision review
- cross-role recommendations

## Final Rule

When in doubt, write for the future ATLAS identity first and preserve legacy compatibility second.

The user should see Ajani, Minerva, Hermes, and Council. Internal code can keep old names temporarily only when needed for stability.
