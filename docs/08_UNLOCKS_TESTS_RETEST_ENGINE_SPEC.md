# 08 — UNLOCKS, TESTS, AND RETEST ENGINE SPEC

## Document Control
- Subsystem: **Progression Engine**
- Status: Draft v1
- Last Updated: 2026-02-17
- Scope: Mastery gates, assessments, unlock logic, and retest policy

---

## 1. Purpose

Ensure progression in Polymath Forge is earned through evidence, not time spent.

The engine governs:
- unlock conditions
- test pass criteria
- retest scheduling
- confidence tracking

---

## 2. Progression Objects

- **Unit**: smallest teachable block
- **Checkpoint Test**: validates unit mastery
- **Unlock Gate**: controls access to next unit/subject
- **Retest Plan**: structured recovery path after failure

---

## 3. Unlock Criteria

A unit unlocks only when:
1. prerequisite units are passed
2. required artifact is submitted
3. checkpoint score meets threshold
4. Hermes compliance checks pass

Optional acceleration unlocks require strong confidence history.

---

## 4. Assessment Types

- Objective checks (short answer / multiple choice / numeric)
- Applied tasks (design, reasoning, analysis)
- Teach-back responses (clarity and transfer)
- Error diagnosis tasks (find and fix flawed logic)

Assessments should mix recall, application, and synthesis.

---

## 5. Scoring Model

Each assessment reports:
- accuracy score
- reasoning quality score
- confidence estimate
- safety/compliance score (where relevant)

Pass threshold is configurable by subject difficulty tier.

---

## 6. Retest Policy

On failure:
1. provide targeted gap diagnosis
2. assign focused remediation set
3. enforce cooldown interval (anti-guessing)
4. retest with variant questions

Retests should measure corrected understanding, not memorized answers.

---

## 7. Confidence and Stability Rules

- Single-pass success does not always imply mastery.
- Stability checks require repeated correct performance over time.
- High variance in performance triggers reinforcement loops.

---

## 8. Anti-Gaming Controls

- variant question pools
- limited immediate retries
- explanation-required items
- artifact-based checkpoints

Progress cannot be advanced by answer-pattern exploitation.

---

## 9. Persona Roles in Testing

- **Ajani**: technical validity of applied tasks
- **Minerva**: explanation quality and comprehension checks
- **Hermes**: policy/safety compliance and test integrity
- **Atlas**: gate orchestration and progression state updates

---

## 10. Reporting and Transparency

Learner dashboard should show:
- mastered units
- blocked gates
- reason for block
- next required action
- retest eligibility window

---

## 11. Non-Goals

- Not a generic gamified quiz system
- Not a one-shot grading tool
- Not a substitute for artifact-based evidence
