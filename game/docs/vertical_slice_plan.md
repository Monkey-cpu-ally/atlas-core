# Vertical Slice Plan - Godot Step 2

## Scope Delivered
- Playable prototype lane with modular systems wired to consistent style rules:
  - Axel movement tuned for responsive platforming feel.
  - Ground combo, air swat, and downward smash behavior.
  - Sticker-based health chips (light chip, heavy full-sticker removal).
  - Scrap meter that charges from combat + pickups and spends on systems.
  - Six one-at-a-time timed powers (15s each) with distinct icon/color/behavior.
  - Enemy category pass: Root Crawler, Gear Bug, Flicker Unit, Heavy Chassis.
  - Breakable wall/floor interactions (Buffalo + smash gate examples).
  - Scrap-themed HUD + Flight Log feed with practical cryptic entries.

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
  - `root_crawler.gd`, `gear_bug.gd`, `flicker_enemy.gd`, `heavy_enemy.gd`: category tuning.
  - `pickup_item.gd`: reusable pickup logic for coin/scrap/food/power.
- `scripts/ui/`
  - `hud.gd`: sticker readout, scrap meter, power icon/timer, pickup text, log summary.

## Immediate Next Steps
1. Add animation player/state machine and true hitbox timing per attack frame.
2. Add boss skeleton (Rootbound Siege Tank) with attack/vulnerable/recover loop.
3. Add Fox Spirit post-boss guide event and hidden alcove reveal.
4. Add dedicated Flight Log panel with scroll and category filters.
5. Add authored icon sprites + polish pass for Scrap-themed HUD framing.
