# 06 — BIO STUDY MODELS SPEC

## Document Control
- Subsystem: **Bio Study Models**
- Status: Draft v1
- Last Updated: 2026-02-17
- Scope: Safe educational modeling for biology-adjacent study

---

## 1. Purpose

Define how biology-related learning is supported in Polymath Forge while maintaining strict safety boundaries.

This specification supports:
- conceptual understanding
- safe simulation
- ethical reasoning

It does **not** support operational wet-lab execution guidance.

---

## 2. Allowed Model Classes

1. **Concept Models**
   - systems diagrams
   - pathway overviews
   - measurement limitations

2. **Mathematical Models**
   - abstract equations and parameter sensitivity
   - non-operational simulation exercises

3. **Data Interpretation Models**
   - reading and critiquing published results
   - uncertainty and bias analysis

4. **Ethics and Policy Models**
   - governance scenarios
   - risk-benefit assessment frameworks

---

## 3. Prohibited Content Classes

- Step-by-step biological manipulation procedures
- Optimization guidance for harmful outcomes
- Acquisition or handling instructions for dangerous agents
- Any content that materially increases operational misuse capability

Hermes must block these at request time.

---

## 4. Simulation-Only Enforcement

When bio-sensitive intent is detected:
- mode switches to simulation-only constraints
- outputs remain high-level and defensive
- practical execution details are omitted
- safer alternative learning path is provided

---

## 5. Standard Output Shape for Bio Study

Each response should include:
1. scope and assumptions
2. conceptual model
3. measurable variables
4. known limitations
5. ethical and safety considerations
6. safe next-study recommendation

---

## 6. Review and Validation

- **Ajani**: ensures structural coherence of model
- **Minerva**: ensures learner clarity and contextual understanding
- **Hermes**: enforces safety and policy constraints

No bio model output is final without Hermes compliance pass.

---

## 7. Evidence Requirements

- Claims must be linked to reliable sources where possible.
- Uncertain claims must be labeled as uncertain.
- Contradictory sources must be acknowledged.

---

## 8. Risk Classification

- **R0**: low-risk conceptual biology
- **R1**: moderate-risk interpretation topics
- **R2**: sensitive topics requiring strict simulation mode
- **R3**: prohibited operational risk content (blocked)

---

## 9. Learning Outcomes

Bio study in Polymath Forge should improve:
- systems thinking in life sciences
- statistical interpretation of biological data
- ethical reasoning under uncertainty

without increasing misuse capability.

---

## 10. Non-Goals

- No procedural lab playbooks
- No optimization for real-world bio intervention
- No bypasses around policy gates
