# Vertical Slice Plan - Godot Step 2

## Scope Delivered
- Playable prototype lane with modular systems wired to consistent style rules:
  - Axel movement tuned for responsive platforming feel.
  - Ground combo, air swat, and downward smash behavior.
  - Sticker-based health chips (light chip, heavy full-sticker removal).
  - Scrap meter that charges from combat + pickups and spends on systems.
  - Six one-at-a-time timed powers (15s each) with distinct icon/color/behavior.
  - Enemy category pass: Root Crawler, Gear Bug, Flicker Unit, Heavy Chassis.
  - Enemy family taxonomy lock: Element / Dinosaur / Machine (used as style lineage + encounter labeling).
  - Breakable wall/floor interactions (Buffalo + smash gate examples).
  - Scrap-themed HUD + Flight Log feed with practical cryptic entries.

## Art Direction Lock (Character + Background References Approved)
- Axel visual lock is now based on the provided pixel reference:
  - black/brown skin tone
  - red cap with worn marks
  - twin puff hairstyle silhouette
  - mechanic jumpsuit with grime/wear decals
  - red gloves + tool-belt utility shapes
  - compact, readable chibi-proportioned body language
- Pixel style lock:
  - soft, warm palette with grounded neutrals
  - clean silhouette readability at gameplay scale
  - high-contrast face readability (eyes/brows/mouth) for expression clarity
  - subtle texture/noise for wear without muddying forms
- Environment consistency:
  - workshop-mechanical backdrop motifs should stay lower-contrast than Axel
  - hero and interactable props must remain color-priority anchors.
- Background reference lock (overgrown urban ruins):
  - wide, readable lanes with hand-painted perspective depth
  - rooted-overgrowth through cracked concrete and architecture (nature reclaiming city)
  - chunky stylized forms over photoreal detail
  - saturated accents in signage/props, but main path readability remains clear
  - silhouettes of traversal surfaces must read quickly from gameplay camera distance
  - avoid noisy micro-detail in collision-critical foreground edges.

## Modular Architecture
- `scripts/systems/`
  - `game_state.gd`: stickers, coins, scrap parts, scrap meter, pickup text events.
  - `power_manager.gd`: power registry, one-active rule, timer and meta/icons.
  - `flight_log.gd`: structured mechanical journal entries.
  - `game_root.gd`: level-level setup and seeded world notes.
- `scripts/player/`
  - `player_controller.gd`: movement/attack/power ability/environment interactions.
- `scripts/entities/`
  - `enemy_base.gd`: shared patrol/detect/chase/contact/hit response loop.
  - `root_crawler.gd`, `gear_bug.gd`, `flicker_enemy.gd`, `heavy_enemy.gd`: category + family tuning.
  - `pickup_item.gd`: reusable pickup logic for coin/scrap/food/power.

## Enemy Family Mapping (Reference-Driven)
- **Element family**:
  - `Root Crawler` (earth/root line)
  - `Flicker Unit` (lightning/frost spectral line)
- **Dinosaur family**:
  - reserved for incoming creature variants and branch forms
- **Machine family**:
  - `Gear Bug` (small machine line)
  - `Heavy Chassis` (armored machine line)
- `scripts/ui/`
  - `hud.gd`: sticker readout, scrap meter, power icon/timer, pickup text, log summary.

## Immediate Next Steps
1. Add animation player/state machine and true hitbox timing per attack frame.
2. Add boss skeleton (Rootbound Siege Tank) with attack/vulnerable/recover loop.
3. Add Fox Spirit post-boss guide event and hidden alcove reveal.
4. Add dedicated Flight Log panel with scroll and category filters.
5. Add authored icon sprites + polish pass for Scrap-themed HUD framing.
