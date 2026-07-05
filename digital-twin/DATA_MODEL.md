# ATLAS Digital Twin Engine — Data Model

## Purpose
This file defines the first data structure for ATLAS digital twins.

The goal is to make every invention readable by humans, usable by AI, and ready for future simulation.

---

# Core Objects

## Project

```json
{
  "project_id": "string",
  "name": "string",
  "category": "robotics | energy | ai | materials | biology | transportation | ux | manufacturing | education",
  "lead_ai": "Ajani | Minerva | Hermes | Council",
  "status": "intake | discovery | concept | digital_twin | prototype | paused | archived",
  "purpose": "string",
  "intended_user": "string",
  "operating_environment": "string",
  "council_decision": "string"
}
```

## Subsystem

```json
{
  "subsystem_id": "string",
  "project_id": "string",
  "name": "string",
  "function": "string",
  "components": []
}
```

## Component

```json
{
  "component_id": "string",
  "subsystem_id": "string",
  "name": "string",
  "type": "structure | sensor | actuator | controller | power | material | software | interface",
  "function": "string",
  "material": "string",
  "estimated_mass_g": 0,
  "estimated_cost_usd": 0,
  "power_draw_watts": 0,
  "failure_modes": []
}
```

## Material

```json
{
  "material_id": "string",
  "name": "string",
  "type": "metal | polymer | ceramic | composite | biological | electronic | unknown",
  "properties_known": [],
  "properties_unknown": [],
  "risks": [],
  "sustainability_notes": "string"
}
```

## Sensor

```json
{
  "sensor_id": "string",
  "name": "string",
  "measures": "string",
  "range": "string",
  "accuracy": "string",
  "sample_rate": "string",
  "data_output": "string",
  "failure_modes": []
}
```

## Risk

```json
{
  "risk_id": "string",
  "project_id": "string",
  "risk_type": "safety | technical | cost | legal | environmental | manufacturing | ethical",
  "description": "string",
  "severity": "low | medium | high | critical",
  "likelihood": "low | medium | high",
  "mitigation": "string",
  "stop_condition": "string"
}
```

## SimulationQuestion

```json
{
  "question_id": "string",
  "project_id": "string",
  "question": "string",
  "simulation_type": "mass | power | heat | load | motion | electrical | control | fluid | manufacturing",
  "required_data": [],
  "confidence": "low | medium | high"
}
```

## TestRecord

```json
{
  "test_id": "string",
  "project_id": "string",
  "test_name": "string",
  "purpose": "string",
  "prototype_level": 0,
  "data_recorded": {},
  "result": "pass | fail | inconclusive",
  "lessons_learned": "string",
  "model_updates_needed": []
}
```

---

# Confidence Levels

## Low
Mostly assumptions. Use only for planning.

## Medium
Based on formulas, datasheets, or known engineering references.

## High
Validated against real test data.

---

# Rule
Every digital twin must clearly mark what is estimated, measured, assumed, and unknown.
