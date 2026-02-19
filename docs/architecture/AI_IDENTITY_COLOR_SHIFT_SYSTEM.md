# AI Center Ripple + Color Activation System (Voice Core + Council + Ethereal Sigil Ring)

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Dial HUD + 3D Core + Voice UI
- Version: v1.4 (Draft)
- Last Updated: 2026-02-19
- Owner: Identity and Visual Systems

---

## 1. Purpose

Define a speaker-driven center-core identity system where only the **3D center core** carries AI accent and ripple behavior.

Design intent:
- preserve a clean, premium interface,
- express AI identity with precision,
- avoid full-UI color flooding.

Note:
- Modular visual preferences may change background/ring/frame/panel atmosphere (see Dial Modular Visual System).
- Identity overlays remain center-only and must remain readable across all configurations.

Voice-first rule:
- `TALK` is removed from the command ring.
- Voice is always available through center hold and wake word.

Council rule:
- Saying `Council` activates sequenced multi-AI response mode with shared council identity.

---

## 2. Scope

In scope:
- center-core accent activation by active AI speaker
- ripple/wave surface behavior during listening/speaking
- haptic and audio micro-feedback cues
- hold + wake-word activation paths
- council sequencing visuals and state flow

Out of scope:
- ring recolor behavior (rings remain neutral)
- skin replacement behavior
- command routing semantics
- policy/safety logic

---

## 3. Core Concept (Non-Negotiable)

Default state:
- center core is neutral
- subtle idle motion only
- no accent color and no ripple

Active speaker state:
- center core applies speaker accent rim light
- surface ripple effect activates
- speaking-end fades back to neutral

Hard rule:
- rings and outer UI do not change identity color.

---

## 4. Identity Color Profiles

## 4.1 Ajani
- Accent family: deep crimson (non-neon)
- Identity intent: strategic strength and structural decisiveness
- Motion character: sharper pulse and clearer ripple edges

## 4.2 Minerva
- Accent family: balanced teal-blue (non-electric)
- Identity intent: reflective guidance and calm depth
- Motion character: softer ripple edges and smoother transitions

## 4.3 Hermes
- Accent family: warm ivory (light neutral with slight warmth)
- Identity intent: precision, logic, and controlled execution
- Motion character: minimal distortion and cleaner light band

## 4.4 Council Baseline
- Accent family: Ghost Purple (soft translucent violet with slight blue undertone, non-neon)
- Identity intent: collective reasoning and unified council presence
- Motion character: restrained ambient energy band, steady baseline glow

---

## 5. Trigger Model

Activate identity flow when any of the following begins:
1. AI voice playback starts
2. AI text response starts typing
3. voice waveform enters active state
4. hold-flow name detection resolves (`ajani|minerva|hermes`)
5. wake-word detection resolves (`ajani|minerva|hermes`)
6. council detection resolves (`council`)

Deactivate identity flow when:
- speaking and typing indicators are complete, and
- response playback ends.

---

## 6. Micro Feedback System

On successful name detection (`ajani|minerva|hermes`):
1. Haptic pulse
   - duration: 10–20 ms
   - intent: subtle confirmation
2. AI-specific tone
   - duration: 200–300 ms
   - low volume, center-localized
3. Sync requirement
   - tone onset must align with accent activation start

AI cue personality:
- Ajani: low harmonic with subtle metallic resonance
- Minerva: soft layered chime, airy profile
- Hermes: clean high-frequency pulse, minimal tail

Council cue:
- haptic pulse slightly stronger than single-AI cue
- subtle low ambient council pad begins on activation

---

## 7. Spiritual Feel Enhancement Layer

Additive center-only visual atmosphere:
- low-density particle dust near core
- active halo ring
- energy-wave style ripple (not hard water ripple mimic)
- subtle inner glow swirl in listening states

Motion rules:
- smooth easing
- no harsh mechanical snaps
- inhale-like activation expansion
- exhale-like neutral return

Center expansion bounds:
- scale range: 1.05x–1.08x

---

## 8. Hold-to-Activate Flow (Touch)

## 8.1 Press Down
Trigger: `onLongPressStart`

Center animation (150–250 ms):
- scale to 1.05x–1.08x
- neutral glow increases slightly
- thin listening band appears

State transition:
- `IDLE -> LISTENING_PENDING_NAME`

## 8.2 Name Detected
Accepted names:
- Ajani
- Minerva
- Hermes

On detection:
- set `activeSpeaker`
- apply speaker accent rim light
- tint listening band to speaker accent
- start ripple effect

Transition:
- ~300 ms fade

State transition:
- `LISTENING_PENDING_NAME -> LISTENING_TO_AI`

## 8.3 Release
Trigger: `onLongPressEnd`

If speaker detected:
- continue into processing/speaking flow

If speaker not detected:
- fade to neutral (200–300 ms)
- scale returns to 1.0
- listening band disappears

---

## 9. Wake Word Flow (Hands-Free)

Trigger:
- `wakeWordDetected("Ajani" | "Minerva" | "Hermes")`
- `wakeWordDetected("Council")`

Behavior:
- no touch required
- core expands to ~1.05x
- corresponding accent or council baseline activates
- ripple/listening waveform begins

State transition:
- single speaker: `IDLE -> LISTENING_TO_AI`
- council: `IDLE -> COUNCIL_ACTIVE`

---

## 10. Processing and Speaking Flow

## 10.1 Processing
Trigger:
- user input complete while listening

Behavior:
- keep active accent
- ripple slows
- soft inner pulse remains

State:
- `PROCESSING`

## 10.2 Speaking
Trigger:
- `aiResponseStart`

Behavior:
- ripple lightly synced to output waveform
- accent glow moderately strengthened
- optional subtle rotation lift

State:
- `SPEAKING` or council speaking phase

## 10.3 Done Speaking
Trigger:
- `aiResponseEnd`

Behavior (~400 ms):
- ripple fades out
- accent fades to neutral
- scale returns to 1.0
- listening band disappears

State transition:
- `SPEAKING -> IDLE` (single speaker)

---

## 11. Council Mode

Trigger:
- user says `Council` (hold flow or wake-word flow)

Council activation behavior:
1. background dim layer fades in to 5-10%
2. stronger micro haptic confirmation
3. center expands slowly to max 1.08x
4. core rotation decelerates to complete stop
5. Ghost Purple rim light activates
6. after a 300 ms delay, ethereal sigil ring fades in behind the core
7. low ambient harmonic tone begins
8. subtle halo ring appears around core

State:
- `COUNCIL_ACTIVE`

Council stillness rule:
- core must be visually still while council is active
- no idle rotation
- no mechanical motion cues
- stillness = authority

## 11.1 Ethereal Sigil Ring (Council-Only)

Purpose:
- represent collective wisdom and ancestral intelligence
- reinforce presence without theatrical effects

Visual characteristics:
- thin circular geometric pattern, behind the 3D core
- Ghost Purple tint with slight translucency
- very low opacity: 8-15%
- no hard lines and no aggressive glow
- sacred-geometry-inspired structure:
  - concentric line system
  - subtle radial glyph markers
  - minimal complexity

Motion behavior:
- recommended mode: static
- optional mode: ultra-slow rotation only
  - approximately 1 full rotation every 30-60 seconds
- if motion is enabled, it must be almost imperceptible

---

## 12. Council Response Flow

Fixed order:
1. Ajani speaks first
2. Minerva responds second
3. Hermes concludes third

Visual behavior:
- base council identity remains Ghost Purple between speakers:
  - Ghost Purple rim baseline
  - council halo
  - ethereal sigil ring
- active speaker overlays temporary identity accent on the core only:
  - Ajani overlay: crimson
  - Minerva overlay: teal
  - Hermes overlay: ivory
- Ajani segment: subtle ripple + deep harmonic layer
- Minerva segment: softer ripple + gentle chime layer
- Hermes segment: minimal ripple + clean tone layer
- after each speaker segment, fade back to Ghost Purple baseline and hold `COUNCIL_IDLE_GLOW` for 1 second

Completion:
1. sigil ring fades out over 400-600 ms
2. Ghost Purple fades out
3. halo dissolves
4. core rotation resumes slowly
5. center scale returns to 1.0
6. ambient council tone fades out
7. background dim layer fades out
8. core returns to neutral idle

---

## 13. Council Sound Design

Base council ambience:
- low ambient harmonic pad
- subtle, almost subconscious

Between speaker transitions:
- soft rising swell

Speaker tone layers:
- Ajani: deeper harmonic emphasis
- Minerva: lighter chime emphasis
- Hermes: clean high-band precision layer

Constraint:
- no dramatic cinematic stingers
- keep spiritual, restrained, and controlled

---

## 14. Ripple and Glow Constraints

Ripple:
- radial distortion
- low speed, low intensity
- no high-frequency flicker
- no aggressive ripple spikes

Glow:
- emission/rim-light layer only
- no full-UI tint
- no dramatic pulse bursts

Halo:
- thin circular band around core
- opacity breathing cycle: 4–6 seconds

Council sigil ring:
- council-only surface rendered behind core
- opacity must remain in 8-15% range
- tint remains Ghost Purple across all council speakers
- default motion mode is `static`
- optional rotation mode is ultra-slow only (30-60 sec per full turn)

Particles:
- very low density, almost invisible
- no visible particle swarms

Performance:
- target 60 fps
- avoid heavy particle spam

---

## 15. Non-Affected Surfaces Rule

The following remain neutral during identity activation:
- Command Ring
- Domain Ring
- Module Ring
- Status/Utility Ring
- outer HUD chrome/panels

Only center-core identity surfaces and waveform accent may shift.

---

## 16. State Contract

Identity renderer consumes:
- `currentSpeaker` (`ajani` | `minerva` | `hermes` | `null`)
- `currentState` (`IDLE` | `LISTENING_PENDING_NAME` | `LISTENING_TO_AI` | `PROCESSING` | `SPEAKING` | `COUNCIL_ACTIVE` | `COUNCIL_IDLE_GLOW` | `SPEAKING_AJANI` | `SPEAKING_MINERVA` | `SPEAKING_HERMES`)
- `voiceMode` (`single` | `council`)
- `councilPhase` (`COUNCIL_ACTIVE` | `SPEAKING_AJANI` | `COUNCIL_IDLE_GLOW` | `SPEAKING_MINERVA` | `SPEAKING_HERMES` | `null`)
- `accentColor`
- `glowIntensity`
- `rippleProfileId`
- `motionProfileModifier` (optional)
- `coreRotationState` (`rotating` | `stopped` | `resume_ramp`)
- `backgroundDimPercent` (0-10)
- `councilSigilVisible` (boolean)
- `councilSigilOpacityPercent` (8-15 when visible)
- `councilSigilRotationMode` (`static` | `ultra_slow`)
- `councilSigilRotationPeriodSec` (optional; 30-60 when `ultra_slow`)

State consumers:
- Unity 3D core renderer (primary)
- waveform renderer

`currentSpeaker = null` maps to neutral core state.

---

## 17. State Machine (Canonical)

Single-speaker path:
- `IDLE -> LISTENING_PENDING_NAME` (hold start)
- `LISTENING_PENDING_NAME -> LISTENING_TO_AI` (name detected)
- `LISTENING_TO_AI -> PROCESSING` (input complete)
- `PROCESSING -> SPEAKING` (response start)
- `SPEAKING -> IDLE` (response end)

Council path:
- `IDLE -> COUNCIL_ACTIVE` (council detected)
- `COUNCIL_ACTIVE -> SPEAKING_AJANI`
- `SPEAKING_AJANI -> COUNCIL_IDLE_GLOW` (1 second pause)
- `COUNCIL_IDLE_GLOW -> SPEAKING_MINERVA`
- `SPEAKING_MINERVA -> COUNCIL_IDLE_GLOW` (1 second pause)
- `COUNCIL_IDLE_GLOW -> SPEAKING_HERMES`
- `SPEAKING_HERMES -> IDLE`

---

## 18. Integration Rules

- Identity activation overlays center core on top of current skin baseline.
- Skin controls baseline look; identity controls temporary speaker behavior.
- Skins must not override or remap identity accent colors:
  - AI accents and Ghost Purple must remain consistent across all skins
  - if a skin cannot render identity overlays cleanly, the skin is invalid
- Identity behavior must not modify:
  - command semantics
  - mode/domain/module state
  - policy/safety behavior

---

## 19. Validation Checklist

Accept only when:
- each AI profile triggers correct center accent and ripple
- micro haptic + tone cues align with accent activation
- rings remain neutral in all active states
- hold and wake-word paths produce equivalent state correctness
- council sequence always executes Ajani -> Minerva -> Hermes
- council baseline glow persists between speakers
- all flows return to neutral deterministically
- active pulses preserve readability/contrast
- council core remains still during active council mode
- council pause windows between speakers hold for 1 second (+/- tolerance)
- council sigil appears only in council mode and only after Ghost Purple activation with ~300 ms delay
- council sigil remains Ghost Purple across Ajani/Minerva/Hermes speaker turns
- council sigil opacity remains within 8-15% while visible
- council completion fades sigil before full neutral return and removes background dim

---

## 20. Design Philosophy

Single AI = energy.  
Council = stillness.

Council mode should feel deeper, calmer, and more authoritative, not louder or more dramatic.
The sigil is not decoration. It is presence.

---

## 14. Appearance Lab (Calibration Mode)

Purpose:
- manual visual customization mode
- system-level calibration environment

Activation:
- user selects "Appearance Lab" from the Status/Utility ring

Behavior (non-negotiable):
1. background dims slightly (5–8%)
2. core rotation slows but does **not** fully stop
3. Hermes becomes active AI identity
4. center rim shifts to soft Ivory accent
5. ripple effects disabled
6. council mode disabled
7. minimal system tone plays (clean, short)

Visual constraints:
- no sigil
- no spiritual halo
- no particles
- no dramatic glow

Philosophy:
- Council Mode = ritual
- Appearance Lab = calibration
- Hermes governs calibration
It should feel like entering a chamber of higher deliberation: still, focused, intentional.
Never flashy.
Just deeper.

---

## 21. Glossary

- **Accent Rim Light:** Colored edge highlight around center core.
- **Council Idle Glow:** Ghost Purple baseline between council speaker turns.
- **Council Mode:** Sequenced tri-AI speaking mode with shared baseline identity.
- **Ghost Purple:** Council accent color (soft violet-blue, non-neon).
- **Council Stillness Rule:** Requirement that center core holds visual stillness during council activation.
- **Listening Pending Name:** Hold-start state before AI name resolution.
- **Neutral State:** Default center-core state with no active accent.
- **Ripple Profile:** Persona-specific wave behavior (speed, softness, edge definition).
- **Wave Envelope:** Smoothed voice intensity signal used for pulse modulation.
