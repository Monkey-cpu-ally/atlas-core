# Performance and QA Test Plan

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Dial UI + 3D Core + Skin System
- Version: v1.2 (Draft)
- Last Updated: 2026-02-17
- Owner: Validation and Reliability

---

## 1. Purpose

Define measurable quality gates for:
- interaction smoothness
- runtime stability
- visual integrity across skins
- state/event correctness across Flutter and Unity layers

---

## 2. Quality Objectives

1. Preserve deterministic interaction behavior.
2. Sustain responsive frame pacing under typical usage.
3. Prevent skin changes from altering system logic.
4. Catch bridge desync and recover cleanly.
5. Maintain accessibility and readability across themes.

---

## 3. Performance Budgets (Target)

| Metric | Target | Alert Threshold | Fail Threshold |
|---|---:|---:|---:|
| Render frame rate | 60 fps | < 55 fps sustained | < 45 fps sustained |
| Input-to-response latency | <= 50 ms | > 60 ms | > 90 ms |
| Ring snap settle duration | 180–260 ms | > 300 ms | > 400 ms |
| Skin preview apply latency | <= 120 ms | > 160 ms | > 220 ms |
| Mode switch visual settle | <= 300 ms | > 400 ms | > 550 ms |
| Bridge round-trip (critical events) | <= 80 ms | > 120 ms | > 200 ms |
| Hold-start -> listening band visible | <= 200 ms | > 260 ms | > 350 ms |
| Wake-word detect -> center activation | <= 300 ms | > 420 ms | > 600 ms |
| Accent activation -> haptic cue sync delta | <= 30 ms | > 50 ms | > 80 ms |
| Accent activation -> tone cue sync delta | <= 30 ms | > 50 ms | > 80 ms |
| Council activation -> core full-stop rotation | <= 700 ms | > 900 ms | > 1200 ms |
| Council Ghost Purple baseline -> sigil visible | 300 ms (+/- 60 ms) | > +/- 90 ms drift | > +/- 140 ms drift |
| Council sigil opacity while visible | 8-15% | outside 7-16% | outside 6-18% |
| Council sigil fade-out duration | 400-600 ms | < 320 ms or > 700 ms | < 250 ms or > 850 ms |
| Council completion -> rotation resume start | <= 500 ms | > 700 ms | > 1000 ms |

---

## 4. Device Test Tiers

Define at least three hardware tiers:
- **Tier A (high)**: flagship devices
- **Tier B (mid)**: mainstream devices
- **Tier C (low)**: constrained devices

All critical workflows must pass on Tier B.  
Tier C may use reduced visual effect budgets but cannot fail core interactions.

---

## 5. Test Suites

## 5.1 Interaction Suite
- Ring drag ownership correctness
- Ring snap index correctness
- Multi-ring conflict handling
- Center core gesture isolation (orbit/zoom/tap)
- Reduced-motion behavior equivalence
- Long-press center activation timing and cancellation behavior
- Ring neutrality verification during center identity activation

## 5.2 3D Core Suite
- Core ready handshake timing
- Mode-driven visual response checks
- Hotspot event correctness
- Animation completion signaling
- Speaker-accent center activation correctness (Ajani/Minerva/Hermes)
- Ripple fade timing on response end
- Council Ghost Purple baseline activation correctness
- Council phase overlay behavior correctness (Ajani/Minerva/Hermes overlays)
- Council stillness enforcement correctness (no idle rotation drift)
- Council sigil behavior correctness:
  - appears only in `COUNCIL_ACTIVE` path
  - delayed appearance after Ghost Purple baseline activation
  - stays Ghost Purple across all council speaker turns
  - remains behind core and within low-opacity range
- Council completion fade duration correctness (500–800 ms target)
- Council completion shutdown order correctness (sigil fade -> Ghost Purple fade -> rotation resume -> background dim fade)

## 5.3 Skin Suite
- Apply/cancel preview behavior
- Persistence after app restart
- No logic drift across skin swaps
- Accessibility checks per skin (contrast/focus/readability)

## 5.4 Bridge Contract Suite
- Valid event acceptance
- Invalid payload rejection format
- Timeout and retry behavior
- Duplicate event idempotency
- Desync recovery workflow
- Wake-word detection flow integrity
- Hold-start/hold-end event ordering integrity
- Council phase event ordering integrity
- Identity feedback cue timing integrity
- Council idle-glow pause duration integrity (1 second target between speakers)
- Council sigil payload integrity (`sigilVisible`, `sigilOpacityPercent`, `sigilRotationMode`, bounds validation)

## 5.5 Stability Suite
- Long session memory stability
- Background/foreground transition recovery
- Thermal stress handling with effect degradation
- Network intermittency impact on state consistency

---

## 6. Functional Acceptance Matrix

| Area | Must Pass Before Release |
|---|---|
| Ring commit behavior | 100% deterministic on tested devices |
| Event schema compliance | 100% for canonical v1 events |
| Skin application | 100% non-destructive to state |
| Core readiness and recovery | no blocking startup failures in release profile |
| Accessibility checks | all critical flows pass |
| Council sequence correctness | strict Ajani -> Minerva -> Hermes order with neutral return |
| Council sigil integrity | delayed council-only visibility, speaker-invariant Ghost Purple behavior |

---

## 7. Regression Cadence

- Per pull request: targeted suite (changed components)
- Nightly: full interaction + bridge + skin suite
- Pre-release: full matrix across device tiers and all baseline skins

Any fail in fail-threshold metrics blocks release candidate promotion.

---

## 8. Defect Severity Model

- **P0:** crash, data corruption, unsafe state drift
- **P1:** core interaction or bridge contract break
- **P2:** major visual or performance degradation without logic break
- **P3:** minor polish issues

Release policy:
- P0/P1 must be zero
- P2 limited and explicitly waived
- P3 tracked to maintenance queue

---

## 9. Observability Requirements

Runtime telemetry should capture:
- frame pacing samples
- input latency samples
- snap duration distribution
- event error rates by name/version
- skin apply failures

Observability data must support root-cause analysis, not only dashboard reporting.

---

## 10. Exit Criteria for v1

v1 is accepted when:
1. all critical suites pass on Tier A/B devices
2. Tier C passes with reduced effect profile
3. no P0/P1 defects remain
4. bridge event contract is stable under reconnection tests
5. all baseline skins pass logic-invariance checks

---

## 11. Glossary

- **Fail Threshold:** Metric level that blocks release progression.
- **Idempotency:** Safe repeated processing with same final outcome.
- **Logic Invariance:** Guarantee that visual skin changes do not alter system behavior.
- **Reduced Effect Profile:** Lower visual complexity mode to protect performance.
- **Regression Suite:** Repeated test set run to detect new breakage after changes.
- **Round-Trip Time:** Duration from event send to response receive across the bridge.
