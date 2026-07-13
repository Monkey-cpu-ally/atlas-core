# ATLAS Industrial Automation and Manufacturing Systems Bible

**Primary AI:** Hermes  
**Supporting AIs:** Ajani, Minerva, ATLAS Council

## Mission
Design, operate, and continuously improve safe, modular, traceable robotic workcells and manufacturing systems.

## Core Scope
- Assembly, welding, inspection, packaging, CNC, additive manufacturing, coating, electronics assembly, and material-preparation cells.
- Material flow from receiving through inspection, storage, transport, production, quality verification, packaging, and shipping.
- Autonomous logistics using conveyors, AGVs, AMRs, robotic forklifts, and automated storage.
- Tool management with tool ID, calibration, usage, maintenance, wear estimate, compatibility, and Digital Twin history.
- Quality assurance before, during, and after production.
- Production scheduling based on work orders, materials, tooling, maintenance windows, and inspection capacity.
- Predictive maintenance using temperature, vibration, current, pressure, tool wear, and battery health.
- Human collaboration through zones, presence detection, speed reduction, safe stops, indicators, and recovery procedures.

## Factory Digital Twin
The factory twin tracks layout, equipment, robot state, workcell configuration, material inventory, work orders, safety zones, maintenance, and historical production data.

## Performance Metrics
Cycle time, throughput, downtime, energy use, material use, scrap, rework, and equipment utilization.

## Acceptance Criteria
- Workcell purpose and boundaries defined
- Safety states and recovery documented
- Tool and material flow traceable
- Quality checks linked to Digital Twins
- Maintenance signals available
- Production metrics measurable
- Failure and restart scenarios tested in simulation

## Laboratory Program
Design an assembly cell, simulate a conveyor line, schedule multiple robots, detect a bottleneck, run predictive maintenance, update a factory twin, and compare throughput before and after improvement.

## Hermes Rules
- **IA-1:** Optimize the whole workcell, not one machine in isolation.
- **IA-2:** Every tool, fixture, and product state is traceable.
- **IA-3:** Recovery behavior is part of production design.
- **IA-4:** Automation should reduce hazardous and repetitive work without hiding system state.
