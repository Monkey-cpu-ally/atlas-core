# Axel: Wrenchbound - Identity Bible (v0.2)

## Core Design Language
- 80% soft, rounded, readable shape language (SMW2 influence).
- 20% impact punctuation through hit reactions, color flashes, and timing snaps (Metal Slug influence).
- Priorities in order: readability -> feel -> feedback -> complexity.
- Environment/level background lock (approved second reference):
  - overgrown urban-mechanical ruins with large rooted tree forms merging into concrete/metal architecture
  - painterly pixel treatment for background masses with clear shape reads (no noisy over-detail in play-critical space)
  - saturated greens/teals and warm concrete tones as primary world palette anchors
  - signage/prop accents used as visual rhythm markers (supports navigation without cluttering gameplay layer)
  - background depth should remain softer and less contrast-heavy than interactive foreground objects.

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
- Background treatment target based on references:
  - softer, slightly desaturated workshop zones for close character reads
  - overgrown city ruins palette and composition for outdoor/world route spaces
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
- Required family taxonomy (locked from provided references):
  - Element Family:
    - elemental bodies (fire/water/air/stone/ice motifs)
    - round/chunky reads first, high-clarity element accent second
  - Dinosaur Family:
    - creature-forward silhouettes, playful but dangerous posture
    - strong profile readability with bright species accents
  - Machine Family:
    - mechanical shells, bolts/plates/wheels, heavy shape weight
    - high-contrast warning accents for weak points and attack tells
- Prototype mapping used in current slice:
  - Root Crawlers -> Dinosaur Family (small crawler branch)
  - Gear Bugs -> Machine Family (light machine branch)
  - Flicker enemies -> Element Family (energy/flicker branch)
  - Heavy enemies -> Machine Family (heavy chassis branch)

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
