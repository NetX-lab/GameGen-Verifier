# Fruit Ninja Classic - Complete Game Specification

> A comprehensive specification for recreating Fruit Ninja Classic (Halfbrick, 2010), the single-player touch slicing arcade game. This spec covers fruit spawning, slice gestures, bombs, combos, modes, scoring, and mobile responsiveness.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Fruit Ninja Classic |
| Developer | Halfbrick |
| Initial Release | April 21, 2010 |
| Source Store | App Store |
| Genre | Casual action / arcade |
| Perspective | 2D front-facing playfield |
| Input | Touch swipe; mouse drag for desktop |
| Session Length | 30 seconds to 3 minutes per round |
| Primary Objective | Slice fruit thrown into the air while avoiding bombs and maximizing combos |
| Lose Condition | Depends on mode: miss 3 fruits in Classic, hit bomb in Classic, or timer expires |
| Win Condition | Score attack; no fixed win state |
| Online Requirement | None |

## 2. AI-Generation Scope

Minimum viable clone:

- Swipe trail collision with fruit, fruit physics arcs, bombs, score, combos, critical hits, Classic, Zen, and Arcade modes.
- Local high scores and short post-round summary.

High-fidelity target:

- Blade effects, dojo backgrounds, power bananas, missions, starfruit currency, achievements, and multiple fruit types with juice splatter.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | 2D sprites with particles and swipe trail |
| Physics | Simple projectile arcs with gravity and rotation |
| Input | Continuous touch path sampled into line segments |
| Collision | Swipe segment vs fruit circle or polygon |
| Spawn Manager | Timed fruit waves from bottom/sides |
| Save | High scores, unlocked blades/backgrounds, settings |

Frame loop:

```text
1. Sample active touch/mouse path and create swipe segments
2. Spawn fruit or bombs according to mode wave schedule
3. Update fruit physics, rotation, and offscreen detection
4. Test swipe segments against sliceable objects
5. Split sliced fruit, create juice particles, and award score
6. Resolve bomb hits, missed fruit, combo windows, and timers
7. Check mode-specific end condition
8. Render background, fruit, bombs, juice, swipe trail, and HUD
```

## 4. Fruit System

Fruit fields:

```text
id, type, position, velocity, angular_velocity, radius,
score_value, sliced, critical_chance, juice_color
```

Fruit behavior:

- Spawn below visible screen or side edges.
- Travel in an arc under gravity.
- Rotate while airborne.
- If sliced, split into two halves and emit juice.
- If unsliced and falls below bottom in Classic, count as missed.

Fruit types:

- Apple.
- Banana.
- Watermelon.
- Pineapple.
- Orange.
- Strawberry.
- Coconut.
- Dragon fruit rare bonus.

## 5. Swipe Slicing

Swipe rules:

- A slice is a fast enough touch movement crossing a fruit collider.
- Stationary touch should not slice.
- Each fruit can be sliced once.
- Multiple fruits sliced within a short window count as a combo.
- Swipe trail fades quickly and follows finger/mouse precisely.

Collision:

- Store recent points in a trail buffer.
- Convert consecutive points into line segments.
- Intersect each segment with active fruit circles.
- Apply minimum segment length or velocity threshold to prevent accidental taps.

## 6. Bombs

Bomb rules:

- Bombs use similar arc physics to fruit.
- Bombs are not sliceable.
- In Classic, slicing a bomb ends the round immediately.
- In Arcade, slicing a bomb deducts points and creates a screen blast but does not necessarily end the round.
- Bombs should be visually distinct from dark fruit silhouettes.

Bomb hit feedback:

- Flash screen.
- Explosion sound.
- Brief slow motion.
- Mode-specific penalty.

## 7. Scoring And Combos

Base score:

- +1 per normal fruit sliced.
- Critical slice may grant bonus points.
- Combo bonus when 3 or more fruits are sliced in one continuous gesture or short time window.

Combo table:

| Fruits In Combo | Bonus |
|-----------------|-------|
| 3 | +3 |
| 4 | +4 |
| 5 | +5 |
| 6+ | +10 or larger celebratory bonus |

Critical:

- Random or precision-based bonus.
- Show "Critical +10" style text sparingly.

## 8. Game Modes

### Classic

- No timer.
- Player has 3 miss marks.
- Missing a fruit costs one mark.
- Slicing a bomb ends game instantly.
- Every 100 points can restore one miss mark if desired.

### Zen

- 90-second timer.
- No bombs.
- Missing fruit does not matter.
- Focus on flow and score.

### Arcade

- 60-second timer.
- Bombs deduct score but do not always end game.
- Special bananas create temporary modifiers.
- End bonus awards points for remaining effects or no bombs hit.

## 9. Power Bananas

Optional Arcade powerups:

| Banana | Effect |
|--------|--------|
| Frenzy | Many fruit spawn rapidly from sides |
| Freeze | Slows fruit and timer briefly |
| Double Points | Doubles scoring during effect |

Effects can overlap. UI should show remaining duration.

## 10. Spawn Design

Wave definition:

```text
time, fruit_count, bomb_count, launch_positions,
velocity_range, spread, special_chance
```

Spawn principles:

- Early waves use few fruit with high arcs.
- Later waves mix low fast fruit, side throws, and bombs.
- Bombs should be avoidable and never hidden inside dense juice effects.
- Fruit should not spawn so fast that touch tracking cannot keep up.

## 11. UI Layout

- Top left: score.
- Top right: miss marks or timer depending on mode.
- Center popups: combo and critical text.
- Pause button in corner.
- End screen: score, best score, combos, mode, retry.

## 12. Visual And Audio Direction

- Fruit halves should fly apart along slice direction.
- Juice splatter color should match fruit.
- Swipe trail can use selected blade color.
- Sounds: slice, combo chime, bomb fuse, explosion, fruit miss, timer warning.

## 13. Validation Checklist

- Slow taps do not slice fruit.
- A single fast swipe can slice multiple fruit.
- Classic mode ends on bomb hit.
- Classic mode subtracts miss mark only when fruit exits unsliced.
- Zen mode has no bombs and ends by timer.
- Combo bonus triggers for 3+ fruit in one gesture.

