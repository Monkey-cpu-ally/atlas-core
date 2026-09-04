# ATLAS HUD Intelligence Loop V1 Implementation Plan

**Status:** Approved — Phase 1 contract spine started 2026-09-04
**Companion specification:** `docs/HUD_INTELLIGENCE_LOOP_V1_SPECIFICATION.md`  
**Scope boundary:** HUD-only unless the Architect explicitly expands it

## 1. Outcome and delivery rule

Deliver one production-ready vertical slice from HUD intent through grounded
persona response, evidence, memory, and next-step suggestion. Build it behind a
feature flag, prove it on one surface, then migrate the remaining V1 HUD entry
surfaces. Do not redesign the core, rings, face dock, or Focus Mode.

No production-code phase starts until the specification and this plan are
approved.

## 2. Milestones

| Milestone | Exit outcome | Production code? |
|---|---|---:|
| M0 — Contract approval | Scope, requirements, drift decisions, API envelope approved | No |
| M1 — Contract spine | Versioned models, orchestrator boundary, idempotency, events, test fixtures | Yes, behind flag |
| M2 — One complete HUD slice | Persona Chat works end-to-end on canonical loop | Yes, behind flag |
| M3 — Learning convergence | Bookshelf and Teaching use the same loop and teaching contract | Yes, behind flag |
| M4 — Council convergence | Council route/deliberation use one orchestrator | Yes, behind flag |
| M5 — HUD production gate | Accessibility, failure, security, performance, visual, and rollback gates pass | Yes, flag rollout |

## 3. Phase 0 — review and lock decisions

### Deliverables

- Approved V1 specification and requirement IDs.
- API examples for success, partial, failure, retry, and Council responses.
- Locked persona registry: slugs, domains, colors, teaching lenses, hard rules.
- Decision on chat-memory retention after session deletion.
- Decision on one canonical endpoint family and compatibility adapters.
- Feature-flag and rollback strategy.

### Decisions required from the Architect

| ID | Decision | Recommended choice | Why |
|---|---|---|---|
| D-01 | Canonical HUD intelligence surface | Versioned `/api/v1/hud/intelligence/*` facade over existing services | Keeps HUD contract stable while internals evolve |
| D-02 | Bookshelf behavior | Resolve selected resource by stable ID server-side | Prevents prompt-built context from masquerading as evidence |
| D-03 | Session deletion | Delete transcript; retain derived persona memory only with explicit disclosure and separate delete control | Preserves learning without hiding retention |
| D-04 | Confidence display | `high / medium / low / unknown` plus basis | Honest and digestible; avoids fake precision |
| D-05 | Council | One fan-out+synthesis implementation; route-only remains a mode | Prevents split personalities and output contracts |
| D-06 | Persona colors | Ajani crimson, Minerva teal, Hermes ivory, Council purple | Matches the locked HUD identity |
| D-07 | First vertical slice | Persona Chat | It already has the strongest grounded backend path |

### Exit gate

All decisions recorded in the specification or an Architecture Decision Record.
No unresolved decision may be silently chosen in code.

## 4. Phase 1 — contract spine

### Backend work

1. Add versioned request, response, evidence, confidence, event, and error
   models.
2. Add a thin HUD orchestration facade that delegates to existing persona,
   knowledge, memory, teaching, and job services.
3. Centralize persona identity and teaching rules; remove prompt duplication by
   importing one server-owned contract.
4. Add idempotent `request_id` handling with a unique persistence constraint.
5. Add typed provenance so generated conversation memory cannot be confused
   with verified knowledge.
6. Add correlated run events and redacted operational logging.
7. Return truthful retrieval and provider fallback modes.

### Test-first fixtures

- One verified shared knowledge record.
- One private memory record for each persona.
- One provisional source.
- One missing resource ID.
- One provider failure and one retrieval failure.
- One Council disagreement case.
- All seven learning levels.

### Exit gate

- HIL-002 through HIL-010, HIL-013, and HIL-014 pass at service/contract level.
- Existing persona, memory, and teaching tests remain green.
- The feature flag defaults off outside test environments.

## 5. Phase 2 — first complete vertical slice: Persona Chat

### Frontend work

1. Introduce `useHudIntelligence()` as the sole client adapter for the new
   contract.
2. Replace DOM-dispatched core double-click behavior with an explicit HUD state
   action while preserving the same visible interaction.
3. Migrate `PersonaChatPanel` to the adapter.
4. Render status with accessible live text and existing restrained motion.
5. Render evidence, confidence basis, retrieval mode, and provider fallback in
   a collapsed details area.
6. Preserve draft text on failure and provide idempotent Retry.
7. Distinguish Stop Watching from confirmed Cancel.

### Exit gate

- A user can select each AI, click the unchanged core, send a prompt, receive a
  grounded answer, inspect evidence, close/reopen the session, and retry safely.
- Council displays three labeled sub-voices plus synthesis.
- Keyboard-only, screen-reader, reduced-motion, and responsive checks pass.
- No permanent hidden-system control appears.

## 6. Phase 3 — learning convergence

### Bookshelf

- Replace legacy `/api/chat/send` use with `explain_resource` through the shared
  adapter.
- Send stable `resource_ids` and explicit `learning_level`.
- Require the response to identify whether the selected record was used.
- Offer one persona-specific next step; never auto-start research or a project.

### Teaching Workbench

- Route `teach` through the same envelope while allowing background execution.
- Preserve all seven depth values and the shared ADHD-friendly delivery law.
- Replace the fixed four-band assumption with a response structure that
  preserves the requested depth; optional supporting layers may remain when
  clearly subordinate.
- Store explicit understanding checks/progress separately from verified
  knowledge.

### Exit gate

- HIL-001, HIL-003, and HIL-005 pass across Persona Chat, Bookshelf, and
  Teaching.
- Contract tests prove that Research depth retains frontier methods,
  uncertainty, and open questions while using clear delivery.
- No Bookshelf prompt manually impersonates evidence.

## 7. Phase 4 — Council convergence

- Move `route`, `deliberate`, Persona Chat Council, and teaching lead selection
  behind one Council service.
- Preserve three separate persona contexts and hard rules.
- Return structured agreement, disagreement, synthesis, and recommended lead.
- Keep “route only” fast and non-generative when possible.
- Deprecate old routes through compatibility adapters; do not remove them in
  the same release.

### Exit gate

- Identical Council intent produces the same persona routing and envelope from
  every V1 HUD surface.
- Partial sub-voice failure is labeled; successful voices remain visible.
- No consequential recommendation executes automatically.

## 8. Phase 5 — production gate and rollout

### Required evidence

| Gate | Required proof |
|---|---|
| Functional | End-to-end tests for all five entry surfaces and four personas |
| Contract | Schema snapshots and backward-compatibility tests |
| Safety | Hard-rule prompt tests, harmful-instruction tests, no actuator payloads |
| Privacy | Log/redaction tests and session/project authorization review |
| Accessibility | Keyboard, focus, screen reader, contrast, reduced-motion checks |
| Visual | Orb, rings, face dock, Focus Mode, panel bounds, and motion regression |
| Performance | Measured UI frame rate and latency percentiles; no estimated claims |
| Reliability | Retrieval/provider/job fault injection and idempotent retry tests |
| Persistence | Restart test for sessions, evidence links, memory typing, and events |
| Rollback | Demonstrated flag-off restoration of current HUD paths |

### Rollout

1. Developer environment with synthetic fixtures.
2. Architect-only canary with the flag on.
3. Review real run events and failure cases.
4. Migrate one surface at a time in this order: Persona Chat, Bookshelf,
   Teaching, Council, Core bridge cleanup.
5. Remove compatibility paths only in a later, separately approved change.

## 9. Work packages and likely file boundaries

These are planning targets, not authorization to modify them yet.

| Package | Likely existing files | New boundary |
|---|---|---|
| Contract models | `backend/models/persona_models.py` | Versioned HUD intelligence models |
| Orchestration | `backend/services/persona_chat.py`, teaching/job services | HUD intelligence coordinator |
| Routes | `backend/routes/persona.py`, `chat.py`, `council.py`, Atlas job routes | Versioned HUD facade + adapters |
| Persona/teaching law | Persona prompts and teaching-contract module | One canonical prompt assembler |
| Client state | `frontend/src/hooks/useAtlasJob.js` | `useHudIntelligence()` |
| HUD surfaces | Persona Chat, Bookshelf, Teaching, Council, Core bridge | Shared response renderer/status model |
| Verification | Existing persona, teaching, HUD, memory suites | Contract, fault, a11y, visual, E2E suites |

## 10. Blockers and dependencies

- Phase 0 decisions are not yet approved.
- Persona definitions and colors conflict across current server and HUD docs.
- Semantic retrieval quality is limited while hashed embeddings/lexical search
  remain fallbacks.
- Current persona routes assume a single architect and lack a future multi-user
  authorization model.
- Server-side cancellation semantics for accepted background jobs are not yet
  proven.
- A production performance baseline must be measured; repository prose is not
  evidence of 60 FPS or latency.

None blocks contract documentation. D-01 through D-07 block production code.

## 11. Progress reporting contract

The weekly HUD report must compare repository evidence against this plan and
the authorities named in the specification. It reports:

- completed GitHub deliverables;
- blockers;
- decisions needed;
- next milestone;
- specification drift before any production-code recommendation;
- measured, estimated, and unknown values as separate categories.

Automatic bug fixes under the weekly permission remain HUD-only. A fix may be
applied automatically only when it is reversible, covered by tests, within an
approved milestone, and does not choose an unresolved product/design decision.
Security, destructive, layout, data-retention, or scope-expanding changes still
require explicit review.

## 12. Immediate next milestone

**M1 — Contract spine.** Phase 0 was approved on 2026-09-04. Phase 1 begins
with the canonical persona registry and its backend/HUD drift tests, followed by
the versioned request and response models behind a default-off feature flag.
