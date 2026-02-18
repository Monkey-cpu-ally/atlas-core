# Unity Bridge Event Contract

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Flutter HUD + Unity 3D Core
- Version: v1.0 (Draft)
- Last Updated: 2026-02-17
- Owner: Platform Integration

---

## 1. Purpose

Define a stable event contract between UI runtime and 3D runtime so state changes are deterministic, traceable, and version-safe.

---

## 2. Scope

In scope:
- Event envelope standard
- Event names and direction
- Required payload fields per event
- Ack/error behavior
- Timeout and retry policy

Out of scope:
- Ring motion internals (Dial Interaction Spec)
- Skin token internals (Skin Token Schema)
- Device performance gates (Performance and QA Test Plan)

---

## 3. Transport Assumptions

- Bridge is asynchronous.
- Event ordering is preserved per sender stream.
- Receivers may process events with finite delay.
- Duplicate delivery is possible under retry paths; idempotency is required.

---

## 4. Event Envelope (Required Fields)

Every event must include:
- `eventName` (string)
- `schemaVersion` (string, e.g., `v1`)
- `requestId` (unique id)
- `timestampUtc` (ISO format)
- `source` (`flutter` or `unity`)
- `target` (`flutter`, `unity`, or `both`)
- `payload` (object)

Optional:
- `correlationId` (ties response to originating request)
- `priority` (`normal`, `high`)

---

## 5. Canonical Event Set (v1)

## 5.1 Flutter -> Unity

1. `v1.modeChanged`
- Trigger: Command Ring commit
- Required payload:
  - `modeId`
  - `previousModeId`
  - `transitionStyle` (optional hint)

2. `v1.domainChanged`
- Trigger: Domain Ring commit
- Required payload:
  - `domainId`
  - `previousDomainId`

3. `v1.moduleChanged`
- Trigger: Module Ring commit
- Required payload:
  - `moduleId`
  - `domainId`

4. `v1.skinChanged`
- Trigger: Skin picker apply
- Required payload:
  - `skinId`
  - `motionProfileId`
  - `materialProfileId`

5. `v1.coreCommand`
- Trigger: direct center action (future hotspot bindings)
- Required payload:
  - `commandId`
  - `commandArgs` (object)

## 5.2 Unity -> Flutter

1. `v1.coreReady`
- Trigger: 3D core initialized and interactive
- Required payload:
  - `coreVersion`
  - `capabilities` (list)

2. `v1.hotspotTapped`
- Trigger: user taps registered hotspot in 3D core
- Required payload:
  - `hotspotId`
  - `coreStateId`

3. `v1.animationDone`
- Trigger: requested core animation/state transition ends
- Required payload:
  - `animationId`
  - `finalStateId`

4. `v1.coreError`
- Trigger: recoverable 3D runtime issue
- Required payload:
  - `errorCode`
  - `message`
  - `recoverable` (boolean)

5. `v1.performanceStateChanged`
- Trigger: thermal/fps tier shift
- Required payload:
  - `performanceTier`
  - `reason`

---

## 6. Ack and Timeout Policy

- Command events expecting confirmation must receive ack (`accepted` or `rejected`).
- Standard timeout window must be defined per event class.
- Retry policy:
  - retry only idempotent events
  - bounded retries
  - preserve original `requestId` with retry attempt metadata in payload

If timeout budget is exhausted:
- sender logs bridge timeout
- UI surfaces non-blocking status where possible

---

## 7. Error Model

Error classes:
- `validation_error` (payload invalid)
- `unsupported_event` (unknown event name/version)
- `state_conflict` (event not valid in current state)
- `runtime_error` (receiver internal issue)

Error response must include:
- original `requestId`
- error class
- human-readable summary
- retryable flag

---

## 8. State Consistency Rules

- Source of truth for ring selection state is Flutter.
- Source of truth for 3D local animation progress is Unity.
- On reconnect/desync, Flutter sends a full state snapshot event (v1) to rehydrate Unity.
- Unity must not silently remap mode/domain/module identifiers.

---

## 9. Versioning Rules

- Event names are version-prefixed (`v1.*`).
- Breaking payload changes require version bump.
- New optional fields do not require version bump if older receivers can ignore them.

---

## 10. Security and Privacy Baseline

- Do not transmit secret tokens in bridge payloads.
- Payload should carry identifiers and state references, not sensitive raw content.
- Error messages must avoid leaking internal runtime details beyond debugging scope.

---

## 11. Test Requirements

Minimum contract tests:
- valid payload acceptance for all canonical events
- invalid payload rejection with structured error
- retry behavior for timeout paths
- ordering preservation for sequential mode/domain/module changes
- duplicate event idempotency validation

---

## 12. Glossary

- **Ack:** Confirmation message that an event was accepted or rejected.
- **Correlation ID:** Link between a response event and the original request.
- **Event Envelope:** Standard wrapper metadata around each payload.
- **Idempotent:** Safe to process more than once without changing final outcome.
- **Schema Version:** Version tag that defines event shape and semantics.
- **State Conflict:** Event rejected because current runtime state cannot apply it safely.
