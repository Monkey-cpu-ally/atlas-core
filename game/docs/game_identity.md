# Axel: Wrenchbound - Identity Bible (v0.2)

## Core Design Language
- 80% soft, rounded, readable shape language (SMW2 influence).
- 20% impact punctuation through hit reactions, color flashes, and timing snaps (Metal Slug influence).
- Priorities in order: readability -> feel -> feedback -> complexity.

## Character Identity
### Axel
- Black/brown girl mechanic with red cap, puff balls, nose bandage, red gloves, pockets, and wrench weapon.
- Tone: confident, grounded, skilled.
- Approved visual reference lock:
  - chibi-proportioned pixel character with strong, clean silhouette readability
  - chunky pixel clusters and clear contour separation (readable at gameplay distance)
  - warm skin tones, worn denim/mechanic blues, and red cap/glove accents as primary identity colors
  - expression-first face design (large eyes, simple mouth/readability over micro detail)
  - "worked-in" outfit wear (patches/scuffs) without muddying silhouette
- Background treatment target based on the reference:
  - softer, slightly desaturated workshop backdrop
  - foreground character contrast must remain clearly higher than environment contrast
  - detail density should be highest on Axel and lower in distant scenery
- Combat verbs:
  - 3-hit ground swat chain
  - 1 air swat
  - downward smash

### Scrap (Assist System, not world follower)
- Scrap is an interface presence, analyzer voice, and meter identity.
- Visual motif in UI/logs:
  - thin scarecrow-like mech silhouette
  - one damaged eye
  - pilot goggles + flight helmet
  - worn white gloves
  - blue/white backpack
  - mismatched parts
- Implementation rule: Scrap should not be a physical follower in normal gameplay.

## Combat + Health + Resource Rules
- Health uses sticker chips, not a standard HP bar.
  - light hits chip the current sticker
  - heavy hits can remove a full sticker
- Scrap meter is mechanical charge.
  - fills from combat and scrap pickups
  - powers/systems can spend it

## Power Rules
- Exactly one active power at a time.
- Duration: 15 seconds.
- New power overrides existing one.
- Required set:
  1. Burning Buffalo
  2. Shadow Tag
  3. Golden Gloves
  4. Super Mode
  5. Specter Mode
  6. Fighter Plane
- Every power must have distinct icon, color signal, and behavior.

## Enemy Rules
- Clear silhouettes and simple readable patterns.
- Readability-first body language with punchy hit reactions.
- Required categories:
  - Root Crawlers
  - Gear Bugs
  - Flicker enemies
  - Heavy enemies

## Flight Log Tone
- Mechanical explorer journal.
- Practical, short, slightly cryptic entries.
- Never fantasy/gothic voice.

## UI Rules
- Mechanical but clean.
- Required HUD pieces:
  - sticker health
  - coins
  - scrap meter
  - power icon + timer
  - pickup text
- Scrap branding should be visible in HUD/log language.
