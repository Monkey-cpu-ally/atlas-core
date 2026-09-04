# ATLAS Production-Readiness Audit

**Audit ID:** ATLAS-PRA-001
**Baseline:** `integration/knowledge-bookshelf-v1` at `a003cd6`
**Audit date:** 2026-09-04
**Decision:** Prototype foundation accepted; production promotion blocked pending the gates below.

## Executive finding

ATLAS is no longer a concept-only prototype. It has working backend services, a functioning HUD, persona chat, model routing, memory retrieval, Knowledge Bank integration, Council fan-out, CI workflows, digital-twin planning, and guarded robotics surfaces. The repository is large enough to prove breadth, but breadth is now its chief risk: multiple overlapping runtimes, duplicated contracts, identity drift, direct database access, and weak deployment boundaries make system-wide behavior difficult to guarantee.

The next release must not add another broad feature layer. It must establish one production-quality vertical slice:

> HUD command → authenticated session → canonical persona → grounded retrieval → model response → cited result → durable audit event.

That slice is defined by `docs/HUD_INTELLIGENCE_LOOP_V1_SPECIFICATION.md` and
sequenced by `docs/HUD_INTELLIGENCE_LOOP_V1_IMPLEMENTATION_PLAN.md`.

## Verified baseline

### Evidence observed

- Repository default branch: `main`.
- Integration baseline: `integration/knowledge-bookshelf-v1` at `a003cd6`.
- Latest integration checks at the audited SHA were green:
  - ATLAS Backend CI #550
  - ATLAS Frontend HUD CI #133
  - Frontend HUD Check #369
  - Visual Ecosystem #570
  - Creative Intelligence CI #138
  - Knowledge Bank Coverage Audit #230
- Static repository inventory:
  - 50 backend route modules
  - 78 backend service modules
  - 64 backend test modules
  - 30 HUD component modules
  - 11 root-level creative-system test modules
- The current persona pipeline performs session lookup, persona memory retrieval, Knowledge Bank retrieval, short-context retrieval, model invocation, response persistence, and Memory Bank mirroring.
- The current model gateway supports hosted inference, Ollama, and LM Studio with fallback behavior.
- The Memory Bank supports persona routing, vector search, graph triples, permanence/decay categories, and multiple embedding providers.

### Evidence not yet sufficient

- There is no single release manifest proving which runtime is authoritative.
- There is no end-to-end test proving the complete HUD Intelligence Loop contract.
- There is no production authentication boundary for ordinary HUD/persona routes.
- There is no formal API versioning or error-envelope standard across the HUD surface.
- The default memory path still uses lexical feature hashing rather than guaranteed semantic embeddings.
- Frontend automated coverage is materially thinner than backend coverage.
- Deployment, rollback, backup restoration, and disaster-recovery proof are not release gates.

## Readiness scorecard

| Area | State | Gate | Evidence / blocker |
| --- | --- | --- | --- |
| Backend correctness | Conditional pass | G-01 | Integration backend suite is green, but runtime ownership is fragmented. |
| HUD build | Conditional pass | G-02 | Integration HUD checks are green; complete user-journey coverage is absent. |
| Persona orchestration | Blocked | G-03 | Working pipeline exists, but canonical role/color definitions drift between repository documents, backend registry, and HUD data. |
| Memory and grounding | Blocked | G-04 | Retrieval exists; default hash embeddings, coarse Knowledge Bank search, and permanent storage of assistant replies weaken truth guarantees. |
| Security | Blocked | G-05 | Persona routes explicitly rely on a single-operator assumption; robotics uses a soft header role gate. |
| Observability | Blocked | G-06 | Logs and Sentinel exist, but there is no universal request/trace ID or immutable intelligence-loop audit envelope. |
| Reliability | Blocked | G-07 | Provider fallback exists, but time budgets, circuit breaking, idempotency, and degraded-mode UX are not governed end to end. |
| Deployment | Blocked | G-08 | Tracked environment files and fixed `/app` paths remain; no release/rollback contract is enforced. |
| Hardware safety | Conditional pass | G-09 | Safety intent exists; all Weaver/robot execution must remain planning-only or human-approved. |
| Documentation | In progress | G-10 | Architecture documents exist; this audit begins the production contract set. |

## Critical findings

### PRA-001 — Canonical identity drift

**Severity:** P0
**Finding:** Persona ownership, descriptions, and colors are inconsistent. The repository README defines Ajani as strategy/operations, Hermes as engineering/software/robotics, and Minerva as research/science/education. The current backend persona registry assigns Ajani to engineering, Hermes to logic/software, and uses colors that do not match the established HUD identity system.

**Required correction:** Create one versioned persona registry consumed by backend and frontend. Canonical presentation is:

| Persona | Primary responsibility | HUD identity |
| --- | --- | --- |
| Ajani | Strategy, execution, risk, operations, and practical decisions | Crimson; disciplined warrior-strategist |
| Minerva | Research, science, education, culture, nature, and knowledge organization | Teal; flowing scholar-storyteller |
| Hermes | Engineering, software, robotics, manufacturing, architecture, materials, and validation | Ivory/linen; inventive architect |
| Council | Weighted synthesis, conflict disclosure, and major review | Purple |

No production loop ships until identity contract tests prove backend/frontend agreement.

### PRA-002 — No production identity boundary

**Severity:** P0
**Finding:** Normal persona and memory surfaces have no production authentication requirement. Robotics describes its role header as a soft gate. Single-user intent does not remove the need for identity, session integrity, request authorization, or child/profile separation.

**Required correction:** Add an authenticated operator identity, server-issued session, capability-based authorization, and deny-by-default policy. Hardware commands require explicit human approval tokens with expiry and replay protection.

### PRA-003 — Fragmented runtime ownership

**Severity:** P0
**Finding:** `backend/`, `atlas_core/`, `atlas-*-runtime`, and root services contain overlapping responsibilities. `backend/server.py` registers roughly fifty route modules directly and performs many startup wiring actions.

**Required correction:** Declare the production control plane and module ownership. Introduce a composition root and service interfaces before moving code. Do not perform a big-bang rewrite.

### PRA-004 — Grounding can look stronger than it is

**Severity:** P0
**Finding:** Memory defaults to feature hashing, Knowledge Bank lookup is keyword/regex based, and retrieved record IDs are returned as citations without a universal evidence envelope. Assistant replies are mirrored into permanent `agent` memory, allowing model-generated content to become durable before verification.

**Required correction:** Separate conversation history from verified memory. Require semantic retrieval in production, provenance metadata, evidence snippets, confidence, freshness, and a promotion workflow before model output becomes permanent knowledge.

### PRA-005 — Client integration is duplicated

**Severity:** P1
**Finding:** HUD components issue direct `fetch` calls and repeat base-URL, parsing, and failure logic. There is no shared typed client, cancellation contract, retry policy, or standard error envelope.

**Required correction:** Introduce one HUD API client and one Intelligence Loop state controller. Migrate only the vertical slice first.

### PRA-006 — Release configuration is development-shaped

**Severity:** P1
**Finding:** Environment files are tracked; fixed `/app/...` export paths and localhost defaults are embedded in runtime/test code; server startup requires environment variables at import time; the root route returns `Hello World` rather than release metadata.

**Required correction:** Add validated configuration profiles, `.env.example` templates, secret scanning, runtime data directories, a versioned health/readiness response, and environment-independent paths.

### PRA-007 — Frontend regression proof is insufficient

**Severity:** P1
**Finding:** The HUD contains many feature components but very few component/unit tests. Build success does not prove persona selection, session restoration, citations, cancellation, degraded mode, accessibility, or safety confirmations.

**Required correction:** Add contract tests, reducer/state-machine tests, component interaction tests, and one browser-level vertical-slice test.

### PRA-008 — Availability behavior is implicit

**Severity:** P1
**Finding:** Model and embedding fallback behavior exists, but the user is not guaranteed to see provider degradation, retrieval degradation, or partial Council failure in a consistent way.

**Required correction:** Every response includes a machine-readable quality state: `grounded`, `degraded`, `partial`, or `failed`, plus safe user-facing recovery actions.

## Production gates

| Gate | Pass condition |
| --- | --- |
| G-01 Build integrity | Backend compile, unit, integration, migration, and dependency checks pass from a clean checkout. |
| G-02 HUD integrity | Lint, unit, component, production build, and vertical-slice browser tests pass. |
| G-03 Identity integrity | One persona registry passes schema and backend/frontend snapshot tests. |
| G-04 Grounding integrity | Every grounded claim maps to retrievable evidence; unverified assistant text cannot silently become verified memory. |
| G-05 Security integrity | Authentication, authorization, session expiry, input limits, secret scanning, and hardware approval tests pass. |
| G-06 Observability integrity | One trace ID follows command, retrieval, inference, persistence, and response; sensitive content is redacted. |
| G-07 Reliability integrity | Timeout, cancellation, duplicate request, provider outage, database outage, and partial Council tests pass. |
| G-08 Release integrity | Staging deploy, smoke test, backup, restore, rollback, and version reporting are demonstrated. |
| G-09 Safety integrity | Hardware execution is deny-by-default and requires explicit, scoped, expiring human approval. |
| G-10 Documentation integrity | Architecture, API, operations, threat model, and acceptance requirements match the release. |

## Promotion decision

ATLAS may continue development on the audited integration baseline. It must not be labeled production-ready until G-01 through G-10 pass. The first implementation target is the Intelligence Loop V1 vertical slice; unrelated feature expansion is deferred until that slice is proven.
