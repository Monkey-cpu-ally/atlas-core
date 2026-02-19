# CHANGELOG_DEV

Development change log for cleanup/performance/UI passes.

Format:
- Date
- Area
- Summary
- Risk
- Rollback

---

## 2026-02-17

### Area: Safety Net / Process
- Summary: Initialized `CHANGELOG_DEV.md` for reversible staged changes (cleanup, performance, UI polish) with risk and rollback notes per change.
- Risk: None (documentation only).
- Rollback: Revert commit that introduces this file.

### Area: Branching
- Summary: Repository is operating on managed branch `cursor/three-js-library-import-ed42`; staged pass commits are recorded on this branch.
- Risk: Low (process note only).
- Rollback: N/A.
- TODO: If you want a dedicated `cleanup-perf-ui` branch in this environment, confirm branch-policy override so commits can be moved safely.

### Area: Pass 1 Audit
- Summary: Added cleanup audit report at `docs/pass1_cleanup_audit.md` documenting dead-weight scan outcomes and no-behavior-change constraints.
- Risk: None (documentation only).
- Rollback: Revert commit that adds the pass-1 audit doc.

### Area: Pass 2 Performance (Backend)
- Summary: Optimized registry lookups in `atlas_orchestrator/knowledge.py` with precomputed normalized indexes and cached regex compilation for keyword matching.
- Risk: Low (lookup and matching internals refactor with same function signatures and outputs).
- Rollback: Revert the pass-2 backend optimization commit.

### Area: Pass 2 Performance (Frontend)
- Summary: Refactored `frontend/src/client/atlasClient.ts` to use shared JSON fetch helpers and in-flight GET request coalescing to reduce duplicate concurrent requests.
- Risk: Low (same endpoint URLs, methods, and error message patterns; no schema changes).
- Rollback: Revert the pass-2 frontend optimization commit.

### Area: Pass 3 Visual Polish
- Summary: Applied CSS-only visual consistency polish in `atlas_core_new/static/css/main.css` (spacing rhythm, hierarchy, card/button/input consistency, reduced glow/noise, maintained focus visibility and contrast).
- Risk: Low to medium (visual-only overrides may require tuning per theme).
- Rollback: Revert the pass-3 UI polish commit.

### Area: Specification Authoring
- Summary: Added 10 structured markdown specifications for Polymath Forge and Atlas hybrid system:
  - `docs/00_MASTER_DOCTRINE.md`
  - `docs/01_ACADEMY_STRUCTURE_22_SUBJECTS.md`
  - `docs/02_TEACHING_STANDARD_IVY_SIMPLE.md`
  - `docs/03_TOME_UI_BOOK_LAYOUT_SPEC.md`
  - `docs/04_TOOL_SYSTEM_SPEC.md`
  - `docs/05_MATERIAL_VAULT_SPEC.md`
  - `docs/06_BIO_STUDY_MODELS_SPEC.md`
  - `docs/07_PROJECT_ARTIFACT_VAULT_SPEC.md`
  - `docs/08_UNLOCKS_TESTS_RETEST_ENGINE_SPEC.md`
  - `docs/09_BUILDER_ROADMAP.md`
- Risk: Low (documentation-only; no application code changes).
- Rollback: Revert the documentation commit for these files.

### Area: Specification Gap Closure
- Summary: Updated spec set to explicitly include:
  - minimum 2+ anchor projects for each of 22 subjects (`docs/01_ACADEMY_STRUCTURE_22_SUBJECTS.md`)
  - the exact rule "PhD backbone / 6th-grade clarity" (`docs/02_TEACHING_STANDARD_IVY_SIMPLE.md`)
  - explicit book/tome tab system with red bookmark behavior (`docs/03_TOME_UI_BOOK_LAYOUT_SPEC.md`)
- Risk: Low (documentation-only refinements).
- Rollback: Revert the documentation gap-closure commit.

### Area: Defensive Program Clarification
- Summary: Added explicit doctrine/roadmap coverage for approved defensive programs:
  - protective gear innovation concepts
  - physical/digital security hardening tracks
  (while preserving the no-harm/no-weaponization policy rule)
- Risk: Low (documentation-only clarification).
- Rollback: Revert the defensive-program clarification commit.

### Area: Unified Builder Spec Expansion
- Summary: Added and populated four new markdown specifications:
  - `docs/10_UNIFIED_SYSTEM_PLATFORM.md`
  - `docs/11_BUILDER_SCALE_LADDER.md`
  - `docs/12_FLAGSHIP_PROJECT_TRACK.md`
  - `docs/13_CROSS_DOMAIN_INTEGRATION_MAP.md`
- Risk: Low (documentation-only additions; no application code).
- Rollback: Revert the commit introducing docs 10-13.

### Area: Spec Quality Tightening (Docs 10-13)
- Summary: Refined docs 10-13 for cross-file consistency and precision:
  - aligned wording around "one platform, five expressions"
  - removed ambiguous subject naming drift
  - strengthened definition language
  - added plain-language Glossary sections to each document
- TODO: Need exact filenames/content list for the requested `/docs/phase1` and `/docs/architecture` additions before creating those files.
- Risk: Low (documentation-only edits).
- Rollback: Revert the spec-quality tightening commit.

### Area: Architecture Spec Pack (Dial + Bridge + Skin + QA)
- Summary: Added implementation-grade markdown specs in `docs/architecture/`:
  - `DIAL_INTERACTION_SPEC.md`
  - `UNITY_BRIDGE_EVENT_CONTRACT.md`
  - `SKIN_TOKEN_SCHEMA.md`
  - `PERFORMANCE_QA_TEST_PLAN.md`
- Risk: Low (documentation-only additions; no application code).
- Rollback: Revert the architecture spec pack commit.

### Area: AI Identity Color-Shift Spec
- Summary: Added `docs/architecture/AI_IDENTITY_COLOR_SHIFT_SYSTEM.md` defining speaker-linked accent behavior for Ajani/Minerva/Hermes, transition timing, visual bounds, integration rules, and acceptance checklist.
- Risk: Low (documentation-only addition; no application code).
- Rollback: Revert the AI identity color-shift spec commit.

### Area: AI Center-Only Identity Refinement
- Summary: Refined `docs/architecture/AI_IDENTITY_COLOR_SHIFT_SYSTEM.md` to center-only activation behavior:
  - center core + waveform respond to active speaker
  - rings and outer HUD remain neutral
  - ripple/pulse transitions tightened with explicit timing and bounds
- Risk: Low (documentation-only refinement).
- Rollback: Revert the center-only identity refinement commit.

### Area: Voice-First Center Core Finalization
- Summary: Updated architecture specs to lock voice-first behavior:
  - removed `TALK` from command ring (`DIAL_INTERACTION_SPEC.md`)
  - added hold + wake-word center-state flows
  - expanded bridge events for hold/wake/listening/speaking states
  - added QA metrics/tests for voice-first activation timing and neutrality rules
- Risk: Low (documentation-only refinement).
- Rollback: Revert the voice-first center core refinement commit.

### Area: Spiritual Mode + Council System Expansion
- Summary: Expanded voice-core architecture with:
  - micro haptic/tone feedback at name recognition
  - center-only spiritual visual layer (halo/particles/energy ripple)
  - council mode (`council`) with Ghost Purple baseline and sequenced Ajani->Minerva->Hermes flow
  - bridge and QA updates for council and cue-timing validation
- Summary (final refinement): Council mode now enforces stillness-first behavior:
  - core decelerates to full stop during council activation
  - 1-second pause cadence between council speakers
  - controlled council completion fade and gradual rotation resume
- Summary (language lock): Added explicit doctrine phrasing in council identity spec:
  - "stillness = authority"
  - "Just deeper."
- Summary (ethereal sigil ring): Added a council-only sigil layer contract across architecture docs:
  - delayed sigil reveal (~300 ms after Ghost Purple activation)
  - low-opacity Ghost Purple sigil behind core (8-15%, speaker-invariant)
  - static-first motion rule (ultra-slow optional)
  - explicit completion shutdown order including sigil fade and background dim fade
  - bridge payload fields and QA checks for sigil state correctness
- Risk: Low (documentation-only refinement).
- Rollback: Revert the spiritual mode + council refinement commit.

### Area: Flutter Scaffold (Voice Core + Council + Sigil)
- Summary: Added `frontend/flutter_atlas_scaffold/` starter package with:
  - canonical state model (`VoiceCoreVisualState`, council enums, sigil state)
  - `VoiceCoreController` for council activation timeline, speaker phases, pause, and completion return
  - bridge payload helpers for `v1.councilPhaseChanged` including sigil/dim fields
  - composable widgets (`VoiceCoreLayer`, `EtherealSigilRing`, `NeutralRingShell`)
  - baseline Flutter tests for council delay, sigil invariance, completion reset, and bridge payload shape
- Risk: Low to medium (new isolated scaffold code; integration still required in a production app).
- Rollback: Revert the commit introducing `frontend/flutter_atlas_scaffold/`.
- Summary (packaging fix): Added `.gitignore` exception for `frontend/flutter_atlas_scaffold/lib/**` so Dart source files are tracked (repo had a global `lib/` ignore).
- Risk: Low (scoped ignore exception for one path).
- Rollback: Revert the `.gitignore` exception commit.
- Summary (state machine + bridge hardening): Tightened the scaffold to be implementation-grade:
  - strict council speaker order enforcement (Ajani -> Minerva -> Hermes)
  - rejection of invalid transitions (pause/complete guards)
  - cancellable timing tokens to prevent stale delayed callbacks from re-opening sigil
  - centralized `VoiceCoreTiming` config shared by controller/widgets/tests (delay + fade + bounds)
  - inbound bridge handler with payload validation and enum parsing (`UnityBridgeInboundHandler`)
  - expanded test coverage for delay/opacity/order rules + widget timing wiring
- Risk: Low to medium (API surface expanded inside scaffold; still isolated from app runtime).
- Rollback: Revert the follow-up scaffold hardening commit(s).

### Area: Architecture Mockup (SVG)
- Summary: Added `docs/architecture/COUNCIL_SIGIL_RING_MOCKUP.svg` showing a side-by-side idle vs council visual mockup (Ghost Purple baseline + background dim + ethereal sigil ring behind core; rings remain neutral).
- Risk: None (documentation-only asset).
- Rollback: Revert the commit adding the SVG mockup.

### Area: Architecture Mockup (SVG) — Council Speaker Sequence
- Summary: Added `docs/architecture/COUNCIL_SPEAKER_SEQUENCE_MOCKUP.svg` showing the council speaker sequence (Ajani -> Minerva -> Hermes) where only the core overlay changes per speaker and the sigil remains Ghost Purple.
- Risk: None (documentation-only asset).
- Rollback: Revert the commit adding the speaker-sequence SVG mockup.

### Area: FlutterFlow Integration (Monorepo Sync)
- Summary: Imported the FlutterFlow-exported Flutter project from branch `flutterflow` into `frontend/flutterflow_app/` so the monorepo branch can include Flutter code without replacing backend/docs at repo root.
- Summary (fix): Replaced `frontend/flutterflow_app/.gitignore` with Flutter/Dart ignores to ensure `lib/` is tracked (FlutterFlow branch previously ignored `lib/`, causing missing Dart sources).
- Risk: Medium (adds mobile/web platform folders and assets to repo; may increase repo size).
- Rollback: Revert the commit that adds `frontend/flutterflow_app/`.

### Area: FlutterFlow Integration (Monorepo Sync) — Source Added
- Summary: Re-imported the latest FlutterFlow export after it pushed the missing Dart sources (`lib/` and `lib/main.dart`) and restored the monorepo sync notes file.
- Risk: Medium (large import delta; requires Flutter tooling locally to validate build).
- Rollback: Revert the commit that updates `frontend/flutterflow_app/` with the new export.

### Area: FlutterFlow App (Backend + Council Demo Wiring)
- Summary: Added a minimal “Atlas Console” screen inside the FlutterFlow app mirror:
  - calls FastAPI `POST /route` and displays Ajani/Minerva/Hermes summaries
  - embeds the `flutter_atlas_scaffold` voice core layer with a council/sigil visual demo (placeholder core for now)
  - adds a simple Home -> Atlas navigation button
- Risk: Medium (FlutterFlow exports may overwrite page files; treat as a starting integration).
- Rollback: Revert the commit adding the console widget and route wiring.

### Area: Mobile Networking (Android + iOS)
- Summary: Enabled local-dev HTTP connectivity to the FastAPI backend from mobile builds:
  - Android: `android:usesCleartextTraffic="true"` for HTTP base URLs
  - iOS: ATS exception `NSAllowsLocalNetworking` + `NSLocalNetworkUsageDescription`
  - Atlas Console now defaults base URL to `10.0.2.2` on Android emulator, `127.0.0.1` on iOS simulator
- Risk: Medium (cleartext + ATS exceptions are dev-friendly; tighten before App Store/Play release).
- Rollback: Revert the commit that modifies AndroidManifest/Info.plist and console defaults.
