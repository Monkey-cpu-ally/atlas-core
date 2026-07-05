# ATLAS Prototype Manager — Architecture

## Purpose
The Prototype Manager controls how ATLAS moves from idea to safe testing.

It connects:
- Innovation Lab project intake
- Council decisions
- Digital Twin reports
- Risk reviews
- Bill of materials
- Test plans
- Failure logs

---

# Core Responsibilities

## 1. Prototype Readiness
Tracks whether a project is ready for physical testing.

Required gates:
- Intake complete
- Evidence review complete
- Digital twin handoff complete when needed
- Risk review complete
- Prototype level assigned
- Safety controls defined
- Stop conditions defined

## 2. Bill of Materials
Tracks parts, tools, materials, and estimated cost.

## 3. Test Planning
Defines what the prototype will prove and what it will not prove.

## 4. Safety Management
Tracks hazards, controls, PPE, environment, and emergency stop conditions.

## 5. Failure Logging
Records what failed, why it failed, and how to improve.

## 6. Feedback to Digital Twin
Sends real test data back to the Digital Twin Engine.

---

# Prototype Record Schema

```json
{
  "prototype_id": "string",
  "project_id": "string",
  "prototype_level": 0,
  "purpose": "string",
  "status": "planned | approved | testing | passed | failed | paused | archived",
  "required_parts": [],
  "required_tools": [],
  "required_skills": [],
  "safety_risks": [],
  "safety_controls": [],
  "stop_conditions": [],
  "test_environment": "string",
  "pass_criteria": [],
  "fail_criteria": [],
  "data_to_record": [],
  "council_decision": "string"
}
```

---

# Prototype Levels

- Level 0: Paper prototype
- Level 1: Digital prototype
- Level 2: Bench prototype
- Level 3: Functional prototype
- Level 4: Field prototype
- Level 5: Production prototype

---

# Rule
The first prototype should usually be the smallest safe test that teaches the most.

Do not build the dream version first. Build the proof.
