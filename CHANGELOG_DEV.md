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
  - iOS: ATS exception `NSAllowsLocalNetworking` + `NSAllowsArbitraryLoadsInLocalNetworking` + `NSLocalNetworkUsageDescription`
  - Atlas Console now defaults base URL to `10.0.2.2` on Android emulator, `127.0.0.1` on iOS simulator
- Risk: Medium (cleartext + ATS exceptions are dev-friendly; tighten before App Store/Play release).
- Rollback: Revert the commit that modifies AndroidManifest/Info.plist and console defaults.
- Summary (UX): Updated the Atlas Console base URL hint to explicitly include physical-device LAN IP usage.
- Summary (UX): Added quick presets + persisted base URL + /health connectivity check for emulator/simulator/USB reverse/LAN IP workflows.

## 2026-02-19

### Area: Skin System (Free Selection Model)
- Summary: Updated architecture specs to enforce user-driven skin selection:
  - skins are manually selected at any time (no auto-switch by mode)
  - apply uses a smooth 400–600 ms crossfade
  - selection persists across restart/mode/AI/council changes
  - skins must remain compatible with center-only identity accents (Ajani/Minerva/Hermes + Ghost Purple council)
  - baseline skin set updated to: Lumen Core, Archive Grid, Circuit Veil, Module Array
- Risk: Low (documentation-only; implementation to follow UI layer).
- Rollback: Revert the commit introducing the spec updates.

### Area: Dial Modular Visual System
- Summary: Added `docs/architecture/DIAL_MODULAR_VISUAL_SYSTEM.md` defining optional, independently configurable visual layers (panels/frame/rings/background), canonical layer stack order, and persistence rules.
- Risk: Low (documentation-only; implementation staged in UI layer).
- Rollback: Revert the commit that adds the modular visual system doc.

### Area: Skin System (Flutter Implementation Seed)
- Summary: Added a minimal free-selection skin system implementation:
  - `flutter_atlas_scaffold`: `AtlasSkins` tokens + `AtlasSkinId` for the initial 4 skins
  - `VoiceCoreLayer` now accepts ring style parameters so skins can affect ring feel without touching identity accents
  - `flutterflow_app`: persisted skin picker + 400–600ms crossfade (default 500ms) applied to the Atlas Console
- Risk: Medium (FlutterFlow exports can overwrite generated files; keep custom code isolated and re-apply after export updates).
- Rollback: Revert the commits introducing the skin tokens and UI wiring.

### Area: Dial Modular Visual System (Flutter Implementation Seed)
- Summary: Implemented modular visual layers in the scaffold `VoiceCoreLayer` and exposed basic toggles in the FlutterFlow app:
  - optional background renderer (solid/gradient/noise/cosmic)
  - optional frame plate under the dial
  - sigil/rings/core layer order aligned to the modular visual stack
  - council dim overlay can be toggled on/off
- Summary (panel system): Added panel tilt/shadow/material support and persisted modular visual prefs to app state.
- Risk: Medium (early implementation; gyro and per-ring materials are staged next).
- Rollback: Revert the commit(s) introducing `dial_visual_prefs.dart`, background/frame widgets, and console toggles.

### Area: Appearance Lab (Calibration Mode)
- Summary: Implemented "Appearance Lab" manual calibration mode per final behavior spec:
  - Hermes governs calibration (Ivory core rim accent while active)
  - background dims subtly (5–8%) and fades out on exit (~400ms)
  - council mode disabled while Appearance Lab is active (guarded in `VoiceCoreController`)
  - live controls for panel tilt degrees, frame type/opacity, ring material + transparency + line weight, background type
  - no save button; changes persist immediately; exit auto-saves; reset restores skin-provided defaults
- Summary (refinement): Matched exit + layout details to spec:
  - exit button is top-minimal on narrow and wide layouts
  - exit sequence dissolves controls + fades dim overlay without fading the full dial
  - core rim color animates (Ivory -> neutral) on exit
- Summary (interaction refinement): Appearance Lab sliders are silent and continuous:
  - removed discrete divisions/labels to avoid snapping
  - no haptic or sound feedback during drag or on release
  - 200–300 ms visual blend for dial response to slider adjustments
- Summary (scaffold): Added skin-level visual defaults (`AtlasSkins.visualDefaults`) used by reset-to-default behavior.
- Risk: Medium (UI layout changes; new persisted pref fields may require one-time migration for old JSON values).
- Rollback: Revert the commit(s) introducing Appearance Lab + the new dial visual preference fields.

### Area: Dial Core UI Implementation Pack (Flutter-first architecture)
- Summary: Added a full implementation scaffold under `frontend/flutter_atlas_scaffold/` matching the requested folder map:
  - `lib/app`, `lib/core`, `lib/domain`, `lib/ui` trees with explicit state slices, services, controllers, themes, painters, and screen/widget composition
  - new interaction/state controllers (`CoreController`, `VoiceController`, `CouncilController`, `RingController`, `AppearanceLabController`) covering idle/hold/listen/process/speaking/council/appearance-lab flows
  - new `DialScreen` stack composition with background/frame/sigil/rings/core + overlays (tooltip, mic assist, appearance lab)
  - skin token resolver + built-in skins + asset-backed skin JSON contracts
  - asset structure for skins/textures/audio/sigil recipes plus pubspec asset wiring
  - package exports updated in `atlas_voice_core.dart` for the new architecture surface
- Risk: Medium to high (large additive scaffold; real sensor/audio/ASR implementations are still mocked and placeholder media files must be replaced before production use).
- Rollback: Revert commits that introduce the `lib/app|core|domain|ui` architecture pack and `assets/*` scaffold additions.

### Area: Skin Schema Integration (Ajani v1)
- Summary: Integrated support for `$schema: "ajani.skin.schema.v1"` in the Flutter scaffold skin resolver and made the provided Lumen Core schema file canonical:
  - replaced `assets/skins/lumen_core.json` with the full Ajani v1 schema payload
  - added resolver support to parse `meta/colors/background/panel/frame/rings/motion/core/council/power/audio` sections
  - mapped schema fields into runtime `SkinTokens` and `UiPrefs` defaults
  - added `SkinLoadResult` (`tokens + prefs`) and wired `DialScreen` to load both
  - reset-to-default now restores skin-derived defaults, not hardcoded generic defaults
  - panel shape/shadow and council dim strength now honor skin schema values
- Risk: Medium (schema parsing is additive but now expects consistent field names for advanced overrides).
- Rollback: Revert the schema-integration commit and restore legacy `lumen_core.json`.

### Area: Skin Schema Integration (Ajani v1) — Archive Grid profile
- Summary: Replaced `assets/skins/archive_grid.json` with the full Ajani v1 schema payload provided by user.
- Summary (compatibility): Added `hex_plate` -> `hexagonalPlate` alias mapping in `skin_resolver.dart` so frame type resolves correctly under the new schema variant.
- Risk: Low (additive schema profile update + alias mapping).
- Rollback: Restore prior `archive_grid.json` and remove the `hex_plate` alias mapping.

### Area: Skin Schema Integration (Ajani v1) — Circuit Veil profile
- Summary: Replaced `assets/skins/circuit_veil.json` with the full Ajani v1 schema payload provided by user.
- Summary (compatibility): Added schema alias mappings:
  - `frame.type: "angular_tech"` -> `angularTechFrame`
  - `background.type: "texture"` -> gradient-backed textured presentation path
- Risk: Low (additive profile and parser aliases only).
- Rollback: Restore prior `circuit_veil.json` and remove newly added resolver aliases.

### Area: Skin Schema Integration (Ajani v1) — Module Array profile
- Summary: Replaced `assets/skins/module_array.json` with the full Ajani v1 schema payload provided by user.
- Summary (compatibility): Added `frame.type: "modular_plate"` alias mapping to the existing runtime frame family (`angularTechFrame`) to preserve rendering without introducing a breaking enum change.
- Risk: Low (profile replacement + additive alias mapping).
- Rollback: Restore prior `module_array.json` and remove `modular_plate` resolver alias.

### Area: UI Prefs Schema Integration (Ajani v1)
- Summary: Added canonical UI prefs asset + resolver support for `$schema: "ajani.ui_prefs.schema.v1"`:
  - added `assets/prefs/ui_prefs_default.json` (user-provided default profile)
  - added `UiPrefsResolver` and `UiPrefsProfile` model for parsing selected skin, onboarding, failure, voice, haptics, council, and power defaults
  - expanded `UiPrefs` model to carry panel/frame/ring/core/gyro/launch pref fields from schema
  - wired `DialScreen` bootstrap to load UI prefs first, pick selected skin, and apply defaults
  - wired onboarding hint text/timing/show-once (process-level) from schema
  - wired failure thresholds + hint text/duration into `VoiceController` and `MicAssistOverlay`
  - updated ring label rendering to respect partial-label opacity/scale preferences and per-ring material/transparency fields
  - added `assets/prefs/` in pubspec and exported the new resolver/model in `atlas_voice_core.dart`
- Risk: Medium (larger config surface; some advanced prefs are stored and partially applied while deeper runtime hooks remain TODO).
- Rollback: Revert the UI-prefs schema integration commit and remove `assets/prefs/ui_prefs_default.json`.

### Area: Rings Schema Integration (Ajani v1)
- Summary: Added canonical rings profile support for `$schema: "ajani.rings.schema.v1"`:
  - added `assets/rings/rings_default.json` with full ring hierarchy (command/domain/modules/utility), segment IDs/labels/icons, radii, and labeling rules
  - added `RingsResolver` and `RingsProfile` model graph for runtime loading/validation
  - wired `DialScreen` bootstrap to load ring schema defaults and configure `RingController` snapping behavior
  - upgraded `RingsWidget` to render rings from schema data (dynamic segment counts, per-ring radii, schema-driven labels) instead of hardcoded label arrays
  - upgraded `RingPainter` to support explicit radius per ring layer
  - added `assets/rings/` pubspec wiring and exported new resolver/model from `atlas_voice_core.dart`
- Risk: Medium (ring rendering surface changed from fixed prototype to schema-driven; interactive edge cases should be tuned on device).
- Rollback: Revert rings schema integration commit and restore fixed ring widget behavior.

### Area: Skin Schema Contract (Draft 2020-12)
- Summary: Added formal JSON Schema contract file for skin tokens:
  - `frontend/flutter_atlas_scaffold/assets/schemas/ajani.skin.schema.v1.json`
  - includes required fields, enum/range rules, and conditional background requirements (`solid` vs `gradient` vs `texture`)
- Summary (runtime guard): Hardened `SkinResolver` with a lightweight schema guard for `ajani.skin.schema.v1` payloads:
  - checks required top-level sections
  - validates required color keys + hex format
  - validates key enum families (background/panel/frame/rings)
  - fails closed to fallback skin when shape is invalid
- Summary (packaging): Added `assets/schemas/` to scaffold pubspec assets.
- Risk: Low to medium (stricter validation may reject malformed skin JSON that was previously tolerated).
- Rollback: Revert schema-contract commit and remove resolver guard path.

## 2026-02-20

### Area: FlutterFlow App (Dial Preview Workspace Entry)
- Summary: Began FlutterFlow-first integration of the new scaffold dial stack by extending `AtlasConsoleWidget` with a workspace switcher:
  - added `Console` vs `Dial Preview` mode chips
  - mounted `DialScreen` directly as a full-screen preview workspace
  - added a top-right "Open Console" return control from the dial workspace
  - ensured Appearance Lab exits cleanly before switching into Dial Preview
- Risk: Medium (switching between two large stateful workspaces may surface lifecycle edge cases on lower-memory devices).
- Rollback: Revert the commit that updates `frontend/flutterflow_app/lib/custom_code/atlas_console/atlas_console_widget.dart`.

### Area: Rings Schema Contract (Draft 2020-12)
- Summary: Added formal JSON Schema contract file for rings:
  - `frontend/flutter_atlas_scaffold/assets/schemas/ajani.rings.schema.v1.json`
- Summary (runtime guard): Hardened `RingsResolver` with lightweight schema validation for `ajani.rings.schema.v1`:
  - checks required top-level sections (`meta`, `rings`, `snapping`, `labelingDefaults`)
  - validates ring definitions, segment definitions, and labeling contract keys
  - validates range constraints for radius, segment counts, snap params, and labeling defaults
  - fails closed to `RingsProfile.fallback` when payload shape is invalid
- Summary (contract alignment): Updated `assets/rings/rings_default.json` command ring labeling to include `showFullLabelWhenCentered` for strict schema compliance.
- Risk: Low to medium (stricter validation may reject malformed or partially specified ring profile payloads that were previously tolerated).
- Rollback: Revert the commit adding the rings schema file and resolver validation guard.

### Area: FlutterFlow Dial Preview Controls (Schema Profile Switching)
- Summary: Added FlutterFlow-facing control panel for the new Dial Preview workspace in `AtlasConsoleWidget`:
  - live skin selector for all 4 Ajani skin IDs
  - rings profile selector (`rings_default.json`, `rings_precision.json`)
  - UI prefs profile selector (`ui_prefs_default.json`, `ui_prefs_calm.json`)
  - `DialScreen` now remounts with a key derived from selected skin/profile paths so changes apply immediately
- Summary (persistence): Added new app-state fields persisted in `SharedPreferences`:
  - `dialPreviewRingsProfilePath`
  - `dialPreviewUiPrefsProfilePath`
- Summary (scaffold wiring): Extended `DialScreen` constructor with:
  - `uiPrefsProfilePath`
  - `ringsProfilePath`
  and wired both through bootstrap resolvers.
- Summary (new profiles): Added additional schema-driven presets:
  - `frontend/flutter_atlas_scaffold/assets/rings/rings_precision.json`
  - `frontend/flutter_atlas_scaffold/assets/prefs/ui_prefs_calm.json`
- Risk: Medium (profile switching remounts the preview dial; malformed custom profile paths now fall back to known defaults).
- Rollback: Revert the commit that updates `atlas_console_widget.dart`, `app_state.dart`, `dial_screen.dart`, and adds the new profile JSON files.
