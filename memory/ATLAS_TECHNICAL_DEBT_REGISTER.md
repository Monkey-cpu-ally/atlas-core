# ATLAS Technical Debt Register

Purpose: keep rough edges visible, prioritized, and connected to Headquarters review instead of letting them hide inside the codebase.

## Rule

Technical debt is not shame. Hidden technical debt is the problem.

Every debt item should answer:

- What is the issue?
- What subsystem owns it?
- What risk does it create?
- What quality gate does it affect?
- What is the next safe action?

## Severity Scale

| Severity | Meaning |
|---|---|
| `critical` | Can break core ATLAS behavior, safety, data integrity, or deployment. |
| `high` | Blocks roadmap progress or creates major reliability risk. |
| `medium` | Creates maintenance drag or confusing architecture. |
| `low` | Polish, naming, docs, or cleanup that should not block execution. |

## Quality Gates

- Architecture
- Engineering
- Testing
- Documentation
- Security
- Performance
- Luxury Review

## Active Register

| ID | Subsystem | Severity | Quality Gate | Issue | Next Safe Action | Status |
|---|---|---|---|---|---|---|
| `DEBT-HUD-001` | HUD | medium | Luxury Review | Some HUD docs still used older dashboard/ring wording instead of Headquarters language. | Refresh HUD docs and design-bank contract. | completed |
| `DEBT-HQ-001` | Headquarters | medium | Engineering | Headquarters command surfaces exist, but integration tests must prove they stay mapped to developer APIs. | Add route/engine tests for command-surface mapping. | open |
| `DEBT-PERSIST-001` | Startup Persistence | high | Engineering | Discovery Approval, External Access, and Project Intelligence need persistence wiring coverage. | Add tests confirming startup hydrates/persists required collections. | open |
| `DEBT-KNOW-001` | Knowledge Division | medium | Architecture | World Knowledge Graph exists as a core service but still needs final server mounting verification. | Confirm route registration and add route tests if missing. | open |
| `DEBT-DOC-001` | Documentation | low | Documentation | Some roadmap docs lag behind completed command-surface work. | Update refinement plan after every subsystem sprint. | active |
| `DEBT-TWIN-001` | Digital Twin | high | Engineering | Digital Twin registry exists, but no real solver layer is confirmed. | Begin D2 engineering stack after Headquarters hardening. | queued |
| `DEBT-HW-001` | Hardware Bridge | high | Security | ESP32/hardware bridge must stay sim-first until safety boundaries and device permissions are clear. | Add simulation contract before any device-control work. | queued |

## Completion Policy

A debt item can move to `completed` only when:

1. The repository contains the fix or the documented decision.
2. Tests or docs prove the change.
3. Headquarters review can explain why the debt is closed.

## Headquarters Connection

The Refinement Office should eventually expose this register through a live route so the HUD can show:

- active debt count
- highest severity
- affected quality gates
- next safe action
- recently completed cleanup

This keeps ATLAS honest, disciplined, and professional.
