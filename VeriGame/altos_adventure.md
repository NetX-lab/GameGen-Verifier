# Alto's Adventure - Complete Game Specification

> A comprehensive specification for recreating Alto's Adventure (Snowman, 2015), the single-player endless snowboarding game. This spec covers one-button physics, terrain generation, tricks, combos, goals, coins, llamas, elders, and zen-like presentation.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Alto's Adventure |
| Developer | Snowman |
| Initial Release | February 19, 2015 |
| Source Store | App Store |
| Genre | Casual endless runner / snowboarding |
| Perspective | Side-view 2D |
| Input | Tap to jump, hold to backflip; optional wingsuit control |
| Session Length | 1-10 minutes per run |
| Primary Objective | Snowboard downhill, collect coins, rescue llamas, perform tricks, and complete goals |
| Lose Condition | Crash into obstacle, land badly, fall into chasm, or get caught by elder |
| Win Condition | Endless score attack plus goal progression |
| Online Requirement | None |

## 2. AI-Generation Scope

Minimum viable clone:

- Procedural downhill terrain, one-button jump/backflip control, coins, llamas, rocks, chasms, bunting/grind lines, trick scoring, combo multiplier, goals, and character unlocks.
- Day-night and weather transitions as visual atmosphere.

High-fidelity target:

- Wingsuit, elders, multiple characters with physics differences, workshop upgrades, photo mode, zen mode, and dynamic music layers.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | 2D side-scrolling parallax |
| Physics | Continuous slope-following character body with jump and rotation |
| Terrain | Procedural spline hills and authored obstacle chunks |
| Camera | Smooth follow with forward look-ahead |
| Save | Goals, coins, unlocks, best distance, best combo |
| Input | Single touch/button is enough for core gameplay |

Frame loop:

```text
1. Read tap/hold input
2. Apply gravity, slope acceleration, jump impulse, and rotation torque
3. Scroll terrain and spawn upcoming chunks
4. Resolve ground contact, landing angle, grinds, pickups, and obstacles
5. Update trick detection, combo timer, speed boost, and score
6. Update elder chase, weather, time-of-day, and music layers
7. Check crash and end run
8. Render terrain, character, pickups, VFX, foreground, and HUD
```

## 4. Player Physics

Controls:

- Tap while grounded: jump.
- Hold while airborne: rotate backward for backflip.
- Release: stop active rotation torque.
- Landing requires board angle close to terrain slope.

Physics stats:

| Stat | Meaning |
|------|---------|
| Speed | Horizontal downhill velocity |
| Jump Strength | Initial upward impulse |
| Rotation Speed | Backflip torque while held |
| Landing Tolerance | Max safe angle difference |
| Grind Balance | Forgiveness on rails/lines |

Landing:

- Clean landing continues run.
- Trick landing grants score and speed boost.
- Bad angle causes crash.

## 5. Terrain Generation

Terrain chunks:

```text
id, length, slope_curve, obstacle_slots, coin_paths,
llama_slots, grind_lines, chasms, difficulty_value
```

Generation rules:

- Terrain scrolls left as player moves right.
- Early terrain has gentle slopes and few obstacles.
- Difficulty increases by distance and goal tier.
- Chasms and rocks require enough warning distance.
- Coin arcs indicate safe jump paths.
- Grind lines are positioned above terrain with entry/exit safety.

## 6. Obstacles And Pickups

| Element | Behavior |
|---------|----------|
| Coin | Adds currency and score |
| Llama | Runs away; collect by passing through |
| Rock | Crash on contact |
| Campfire | Crash on contact |
| Chasm | Crash if player falls in |
| Bunting Line | Grindable line, adds trick score |
| Roof/Temple Line | Grindable structure |
| Magnet | Temporarily attracts coins |
| Feather | Optional hover/protection pickup |

## 7. Tricks And Combo System

Tricks:

- Backflip: complete 360-degree rotation and land safely.
- Double/triple backflip: multiple rotations before landing.
- Grind: ride line or roof.
- Llama horn/collection sequence: collect multiple llamas.
- Gap jump: clear chasm.
- Wingsuit flight if implemented.

Combo:

1. Start combo when trick begins.
2. Add trick points to pending combo.
3. Continue combo if another trick starts before timeout.
4. Bank combo only after safe landing.
5. Crash loses unbanked combo.

Speed boost:

- Successful trick grants scarf extension and temporary speed.
- Longer combos produce stronger boost.

## 8. Goals And Progression

Each level tier gives three goals. Completing all three advances tier.

Goal examples:

- Collect 50 coins in one run.
- Rescue 10 llamas.
- Perform a double backflip.
- Grind 200 meters.
- Land 3 backflips in one run.
- Escape elder.
- Travel 5,000 meters.

Progression:

- Coins buy upgrades such as magnet timer, hover timer, wingsuit, and coin doubler.
- Characters unlock at goal tiers.
- Later characters may have different rotation, speed, or landing tolerance.

## 9. Elders And Chase Pressure

Elders:

- Appear after player disturbs a camp or reaches distance threshold.
- Chase from behind at high speed.
- Player escapes by maintaining speed, tricks, and clean terrain.
- If elder catches player, run ends.

The chase should be tense but readable, with warning sound and visible pursuer distance.

## 10. Modes

| Mode | Rules |
|------|-------|
| Standard | Goals, coins, crashes, progression |
| Zen | No score pressure or goals; relaxed endless ride |
| Tutorial | Teaches jump, backflip, grind, and llamas |

Zen mode can remove fail state or restart softly after crash.

## 11. UI Layout

- Top left: score or distance.
- Top right: coins and current goals.
- During combo: center text showing trick chain and multiplier.
- End screen: distance, score, coins, goals completed, retry.
- Workshop: upgrades and characters.

## 12. Visual And Audio Direction

- Minimal landscape silhouettes with changing sky colors.
- Snow particles, scarf trail, and smooth parallax are central.
- Music should be calm and adaptive.
- Trick sounds should be light: jump, flip wind, grind, coin, llama, crash.

## 13. Validation Checklist

- Holding input rotates player; tapping only jumps.
- Bad landing angle crashes the run.
- Tricks score only after safe landing.
- Combo chains across grinds and flips.
- Terrain generator creates reachable obstacle spacing.
- Goals persist across runs and unlock new tiers.

