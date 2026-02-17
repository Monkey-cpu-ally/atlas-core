# 04 — TOOL SYSTEM SPEC

## Document Control
- System: **Polymath Forge Tool Layer**
- Status: Draft v1
- Last Updated: 2026-02-17
- Scope: Tool architecture, governance, and execution contract

---

## 1. Purpose

The tool system provides controlled capabilities to Atlas and its personas without breaking doctrine constraints.

Goals:
- Expand useful capability safely
- Keep tool usage auditable
- Prevent uncontrolled execution or privilege drift

---

## 2. Tool Categories

1. **Knowledge Tools**: retrieval, indexing, citation
2. **Planning Tools**: task decomposition, dependency mapping
3. **Build Tools**: artifact generation support, checklists
4. **Validation Tools**: policy checks, consistency checks, test checks
5. **Simulation Tools**: model-based exploration under safety boundaries

---

## 3. Tool Registry Contract

Each tool requires metadata:
- Tool ID (stable, unique)
- Name and description
- Category
- Input schema
- Output schema
- Permission level
- Safety classification
- Owner and version

No unregistered tool may execute.

---

## 4. Invocation Lifecycle

1. Request context established
2. Candidate tool selected
3. Hermes policy pre-check
4. Execution with scoped permissions
5. Output validation
6. Trace logging (input hash, output hash, timing)
7. Response assembly

---

## 5. Permission Model

- **P0 (Read-only)**: retrieval and inspection
- **P1 (Constrained write)**: project-scoped artifact updates
- **P2 (Privileged)**: restricted operations requiring explicit gate

Default permission is lowest-privilege.

---

## 6. Safety and Policy Rules

- Tool calls inherit doctrine restrictions.
- Bio/security-sensitive requests force simulation-only restrictions.
- Any policy violation aborts execution and emits a structured refusal.
- Unsafe tool chains are blocked at planning time, not after execution.

---

## 7. Error Handling Contract

Tool failures must return:
- error class
- concise explanation
- retryable/non-retryable status
- safe fallback suggestion (if available)

Raw stack traces should not be surfaced to end-user layers.

---

## 8. Performance and Reliability Guardrails

- Timeouts required for all tool calls
- Concurrency limits by category
- Rate limiting on expensive tools
- Idempotency where applicable
- Deterministic behavior preferred for evaluation flows

---

## 9. Auditability Requirements

Every call records:
- who requested
- what tool/version executed
- policy decision
- key parameters (sanitized)
- result status
- timestamp and duration

Logs must support replay and incident review.

---

## 10. Versioning and Deprecation

- Tools are semantically versioned.
- Breaking changes require a migration note.
- Deprecated tools remain available only for bounded compatibility windows.
- Removed tools are archived with rationale.
