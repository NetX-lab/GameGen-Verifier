# Galaga — Complete Game Specification

> A comprehensive specification for faithfully recreating Galaga (Namco, 1981 Arcade). This document covers every system, mechanic, entity, and interaction required for a full clone of this classic fixed-shooter arcade game.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Player Ship Mechanics](#3-player-ship-mechanics)
4. [Enemy System](#4-enemy-system)
5. [Stage Structure & Formations](#5-stage-structure--formations)
6. [Challenging Stages](#6-challenging-stages)
7. [Capture & Dual Fighter Mechanic](#7-capture--dual-fighter-mechanic)
8. [Scoring System](#8-scoring-system)
9. [Difficulty Progression](#9-difficulty-progression)
10. [UI Layout & HUD](#10-ui-layout--hud)
11. [Audio Design](#11-audio-design)
12. [Animation & Visual Effects](#12-animation--visual-effects)
13. [Lives & Continue System](#13-lives--continue-system)

---

## 1. Game Overview

- **Genre**: Fixed shooter (shoot 'em up)
- **Perspective**: 2D top-down (vertical orientation)
- **Players**: 1-2 players (alternating turns)
- **Input**: 2-way joystick (left/right only) + 1 button (Fire)
- **Objective**: Destroy waves of alien insect formations. Survive as long as possible and achieve the highest score.
- **Lose Condition**: All lives lost.
- **Key feature**: Enemy capture beam — the boss Galaga can capture the player's ship with a tractor beam. Destroying that boss releases the captured ship, giving the player a powerful Dual Fighter (two ships firing simultaneously).

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Arcade resolution | 224 x 288 pixels (vertical orientation) |
| Recommended implementation | 448 x 576 or 672 x 864 |
| Orientation | Vertical (portrait) |
| Frame rate | 60 FPS |
| Background | Pure black (starfield) |

### Coordinate System

- Origin (0, 0) at top-left.
- Player ship moves along the bottom of the screen.
- Enemies form at the top and dive downward.
- Player Y position is fixed at approximately y = 256 (near bottom).

### Game Loop

```
1. Process input (left/right, fire button)
2. Move player ship
3. Update player projectiles
4. Update enemy formation position (breathing animation)
5. Update diving enemies (AI patterns)
6. Update enemy projectiles
7. Check player bullet vs enemy collisions
8. Check enemy/projectile vs player collisions
9. Check capture beam interactions
10. Update explosions and effects
11. Check stage clear condition
12. Update score display
13. Render (starfield → enemies → player → projectiles → UI)
```

### Starfield Background

- Scrolling star pattern (downward at ~0.5 px/frame).
- Stars are single-pixel white dots at varying brightness levels (3 levels).
- Approximately 30-40 visible stars on screen at any time.
- Creates the illusion of forward movement through space.

---

## 3. Player Ship Mechanics

### Fighter Properties

| Property | Value |
|----------|-------|
| Hitbox | 14 x 14 pixels |
| Movement speed | 2 px/frame (120 px/s) |
| Movement range | 8 pixels from left edge to 8 pixels from right edge |
| Vertical position | Fixed at y = 256 |
| Fire rate | ~6 shots/second (max 2 bullets on screen) |
| Bullet speed | 5 px/frame (300 px/s) upward |
| Bullet size | 2 x 6 pixels |
| Max bullets on screen | 2 (single fighter) / 4 (dual fighter) |

### Dual Fighter

| Property | Value |
|----------|-------|
| Width | 30 pixels (two ships side-by-side with small gap) |
| Hitbox | 30 x 14 pixels (wider target) |
| Bullets per shot | 2 (one from each ship) |
| Max bullets on screen | 4 (2 per ship) |
| Movement speed | Same as single fighter (2 px/frame) |
| Benefit | Double firepower, wider coverage |
| Risk | Larger hitbox makes dodging harder |

---

## 4. Enemy System

### 4.1 Enemy Types

#### Bee (Zako)

| Property | Value |
|----------|-------|
| HP | 1 |
| Formation position | Lower rows (rows 4-5 of formation) |
| Color | Blue/cyan |
| Dive behavior | Peels off formation, dives in looping pattern |
| Dive speed | 3 px/frame |
| Shots while diving | 0-1 bullets |
| Score (formation) | 50 |
| Score (diving) | 100 |

#### Butterfly (Goei)

| Property | Value |
|----------|-------|
| HP | 1 |
| Formation position | Middle rows (rows 2-3 of formation) |
| Color | Red/pink |
| Dive behavior | Dives in swooping arc patterns |
| Dive speed | 3 px/frame |
| Shots while diving | 1-2 bullets |
| Score (formation) | 80 |
| Score (diving) | 160 |

#### Boss Galaga (Galboss)

| Property | Value |
|----------|-------|
| HP | 2 (first hit changes color from green to blue; second hit destroys) |
| Formation position | Top row (row 1 of formation) |
| Color | Green (full HP) → Blue (damaged) |
| Dive behavior | Dives with 2 escort Butterflies, can use capture beam |
| Dive speed | 2.5 px/frame |
| Shots while diving | 1-3 bullets |
| Capture beam | Tractor beam that captures player's ship |
| Score (formation) | 150 |
| Score (diving, no escorts) | 400 |
| Score (diving, with 1+ escort) | 800 (if escort survived during dive) |
| Score (captured ship killed) | 1,000 (shoot captured ship while in formation) |

### 4.2 Enemy Projectiles

| Property | Value |
|----------|-------|
| Speed | 4 px/frame downward |
| Size | 2 x 4 pixels |
| Color | White/yellow |
| Max on screen | 3 (per enemy type — effectively ~8-10 total) |
| Aiming | Aimed at player's current X position at time of firing |
| Fire chance (dive) | Each frame during dive: ~2% chance to fire |

### 4.3 Enemy Formation

The formation consists of 40 enemies arranged in 5 rows:

```
Formation Layout (top of screen):
Row 1: [B1] [B2] [B3] [B4]                    ← 4 Boss Galaga
Row 2: [F1] [F2] [F3] [F4] [F5] [F6] [F7] [F8]  ← 8 Butterflies
Row 3: [F9] [F10][F11][F12][F13][F14][F15][F16]   ← 8 Butterflies
Row 4: [Z1] [Z2] [Z3] [Z4] [Z5] [Z6] [Z7] [Z8] [Z9] [Z10] ← 10 Bees
Row 5: [Z11][Z12][Z13][Z14][Z15][Z16][Z17][Z18][Z19][Z20] ← 10 Bees
```

### Formation Behavior

| Property | Value |
|----------|-------|
| Total enemies | 40 per stage |
| Formation width | ~160 pixels |
| Formation height | ~80 pixels |
| Formation Y position | ~60 pixels from top |
| Breathing animation | Formation expands and contracts horizontally (±16 pixels) at ~0.5 Hz |
| Breathing speed | Smooth sinusoidal movement |

### 4.4 Entry Patterns

At the start of each stage, enemies fly onto screen in predefined patterns before settling into formation.

| Entry Wave | Count | Pattern |
|------------|-------|---------|
| Wave 1 | 8 (4 Bees + 4 mix) | Enter from top-right, loop, settle in formation |
| Wave 2 | 8 | Enter from top-left, loop, settle |
| Wave 3 | 8 | Enter from bottom-left, loop upward, settle |
| Wave 4 | 8 | Enter from bottom-right, loop upward, settle |
| Wave 5 | 8 (includes Boss Galagas) | Enter from top, complex loop, settle |

Entry speed: 3 px/frame along the path.
Entry pattern: Smooth curved paths (Bezier-like curves).

### 4.5 Dive Attack System

Once all enemies are in formation, they begin diving at the player:

| Property | Value |
|----------|-------|
| Dive initiation | Random selection from formation |
| Dive priority | Boss Galaga > Butterfly > Bee |
| Dive frequency | Increases with stage number |
| Dive pattern | Looping downward path, curving toward player |
| Missed dive | Enemy loops back up and returns to formation |
| Escort dives | Boss Galaga brings 2 Butterfly escorts when diving |

### Dive Path Algorithm

```
1. Enemy leaves formation position
2. Follows a predefined curved path (one of ~8 patterns)
3. Path curves toward player's current X position
4. At bottom of screen, loops back upward
5. Returns to formation position (or a gap if formation shifted)
6. While diving: fires 0-3 bullets (random)
```

---

## 5. Stage Structure & Formations

### Stage Progression

| Stage | Speed Modifier | Dive Frequency | Bullets Per Dive | Notes |
|-------|---------------|----------------|-----------------|-------|
| 1 | 1.0x | Low (1 diver per 3s) | 0-1 | Introductory |
| 2 | 1.0x | Low-Medium | 0-1 | |
| 3 | 1.0x | Medium | 1 | Challenging Stage 1 |
| 4-5 | 1.1x | Medium | 1 | |
| 6-7 | 1.1x | Medium-High | 1-2 | Challenging Stage 2 |
| 8-10 | 1.2x | High | 1-2 | |
| 11-14 | 1.2x | High | 2 | Challenging Stage 3 |
| 15-18 | 1.3x | Very High | 2 | |
| 19-22 | 1.3x | Very High | 2-3 | |
| 23-30 | 1.4x | Maximum | 3 | |
| 31+ | 1.5x | Maximum | 3 | Maximum difficulty reached |

### Stage Clear Condition

- All 40 enemies destroyed.
- Brief pause (~2 seconds).
- Stage number increments.
- New wave of 40 enemies enters.

### Stage Counter Display

- Bottom-right: stage counter shown as flag/badge icons.
- Small flags = 1 stage each.
- Large flag = 5 stages.
- Displayed up to ~50 stages (wraps display).

---

## 6. Challenging Stages

Every 3rd stage (stages 3, 7, 11, 15, 19, 23, 27, 30, ...) is a Challenging Stage (bonus round).

### Challenging Stage Rules

| Property | Value |
|----------|-------|
| Player vulnerability | Invincible (cannot be hit) |
| Enemy behavior | Enemies fly through in preset patterns, do NOT shoot |
| Enemies per wave | 8 per wave, 5 waves = 40 total |
| Time limit | ~30 seconds per challenging stage |
| Scoring | Each hit = 100-160 points (varies by enemy type) |
| Perfect bonus | All 40 hit = 10,000 bonus points |
| Near-perfect | 36-39 hit = special bonus amounts |
| Miss penalty | None (just missed score opportunity) |

### Challenging Stage Patterns

| Wave | Entry Direction | Pattern Description |
|------|---------------|-------------------|
| 1 | Top-center | Fly down in 2 columns, split and exit sides |
| 2 | Left side | Swooping arc left-to-right |
| 3 | Right side | Swooping arc right-to-left |
| 4 | Bottom corners | Loop up from bottom, cross, exit top |
| 5 | Top, complex | Figure-8 pattern across screen |

### Results Display

```
┌──────────────────────┐
│ CHALLENGING STAGE     │
│                       │
│ NUMBER OF HITS  38    │
│                       │
│ BONUS    8000         │
│                       │
│ (PERFECT = 10000)     │
└──────────────────────┘
```

---

## 7. Capture & Dual Fighter Mechanic

### Capture Beam

| Property | Value |
|----------|-------|
| Trigger | Boss Galaga dives and positions above player |
| Beam visual | Wide blue/white tractor beam, ~24 pixels wide, extends downward |
| Beam duration | ~3 seconds |
| Beam range | Full vertical screen height |
| Capture condition | Player ship overlaps with beam for ~1 second |
| Player control during beam | Can still move left/right, but beam pulls upward |
| Pull speed | 2 px/frame upward |

### Capture Sequence

```
1. Boss Galaga dives to position directly above player (±32 pixels).
2. Boss Galaga stops and hovers.
3. Tractor beam extends downward (takes ~0.5 seconds to fully extend).
4. If player is within beam: player ship is frozen, pulled upward.
5. Captured ship attaches to Boss Galaga.
6. Boss Galaga flies back to formation with captured ship.
7. Player loses a life. Next ship spawns at bottom.
8. Captured ship sits in formation next to the Boss Galaga (visible).
```

### Rescue Sequence

```
1. Player must destroy the Boss Galaga that captured their ship.
2. IMPORTANT: Must hit the Boss Galaga, NOT the captured ship.
3. If Boss Galaga is destroyed:
   a. Captured ship detaches.
   b. Ship flies down and joins player's current ship.
   c. Player now has DUAL FIGHTER (two ships side by side).
4. If captured ship is shot by player:
   a. Captured ship is destroyed.
   b. Score: 1,000 points but ship is lost.
   c. Boss Galaga continues without the ship.
```

### Dual Fighter Details

| Property | Value |
|----------|-------|
| Formation | Two ships side-by-side with ~2 pixel gap |
| Combined width | ~30 pixels |
| Fire | Both ships fire simultaneously (2 bullets per press) |
| Max bullets | 4 on screen (2 per ship) |
| Hit vulnerability | If either ship is hit, only that ship is destroyed |
| Remaining ship | Continues as single fighter |
| Score benefit | Double firepower = faster kills = higher scores |
| Risk | Wider hitbox = harder to dodge enemy fire |

---

## 8. Scoring System

### Kill Scores

| Enemy | In Formation | While Diving |
|-------|-------------|-------------|
| Bee (Zako) | 50 | 100 |
| Butterfly (Goei) | 80 | 160 |
| Boss Galaga (undamaged) | 150 | 400 |
| Boss Galaga (with escorts) | 150 | 800 (1 escort), 1,600 (2 escorts) |
| Captured ship (shot) | 1,000 | — |
| Challenging Stage hit | 100-160 | — |
| Perfect Challenging Stage | 10,000 bonus | — |

### Score Multiplier (Dive Kills)

Killing enemies while they are diving awards double the formation score. This encourages risk-taking.

### Extra Lives

| Score | Effect |
|-------|--------|
| 20,000 | 1 extra life |
| 70,000 | 1 extra life |
| DIP switch options | Can be set to 20K/60K, 20K/70K, or 30K/80K |

### End-of-Game Statistics

When the game ends, a summary screen shows:

```
┌──────────────────────┐
│    -RESULTS-          │
│                       │
│ SHOTS FIRED    247    │
│ NUMBER OF HITS  189   │
│                       │
│ HIT-MISS RATIO        │
│       76.5 %          │
└──────────────────────┘
```

---

## 9. Difficulty Progression

### Enemy Behavior Scaling

| Stage Range | Dive Speed | Dive Frequency | Bullets/Dive | Capture Beam Frequency |
|------------|-----------|----------------|-------------|----------------------|
| 1-3 | 3.0 px/frame | Every 3 seconds | 0-1 | Rare |
| 4-7 | 3.2 px/frame | Every 2.5 seconds | 1 | Occasional |
| 8-14 | 3.5 px/frame | Every 2 seconds | 1-2 | Regular |
| 15-22 | 3.8 px/frame | Every 1.5 seconds | 2 | Frequent |
| 23-30 | 4.0 px/frame | Every 1 second | 2-3 | Very Frequent |
| 31+ | 4.5 px/frame | Every 0.8 seconds | 3 | Constant |

### Formation Entry Speed

| Stage Range | Entry Speed |
|-------------|------------|
| 1-10 | 3 px/frame |
| 11-20 | 3.5 px/frame |
| 21-30 | 4 px/frame |
| 31+ | 4.5 px/frame |

---

## 10. UI Layout & HUD

### 10.1 In-Game HUD (Vertical Orientation)

```
┌────────────────────────┐
│ 1UP     HIGH SCORE     │
│ 12450    78900         │
│                        │
│                        │
│  [Enemy Formation]     │
│                        │
│                        │
│                        │
│                        │
│       [Diving enemy]   │
│             ↓          │
│                        │
│                        │
│     [Player Ship]      │
│                        │
│ ♦♦ [lives]  [stage flags] │
└────────────────────────┘
```

### HUD Elements

| Element | Position | Description |
|---------|----------|-------------|
| 1UP score | Top-left | Player 1 current score |
| HIGH SCORE | Top-center | All-time high score |
| 2UP score | Top-right (2P mode) | Player 2 score |
| Lives | Bottom-left | Remaining ships as small icons |
| Stage counter | Bottom-right | Flag/badge icons indicating current stage |

---

## 11. Audio Design

### 11.1 Music & Jingles

| Track | Context | Description |
|-------|---------|-------------|
| Stage start jingle | Beginning of each stage | Brief ascending fanfare (~2 seconds) |
| Challenging Stage music | During bonus rounds | Upbeat, encouraging |
| Game Over | When all lives lost | Descending, somber |
| Coin insert jingle | Credit inserted | Brief chime |
| High score entry | New high score | Celebratory tune |

### 11.2 Sound Effects

| Event | Description |
|-------|-------------|
| Player shot | Sharp "pew" |
| Enemy hit | Explosion "pop" |
| Boss Galaga first hit | Different tone (lower) |
| Boss Galaga second hit (death) | Full explosion |
| Player death | Deep explosion + siren |
| Capture beam | Warbling "wee-woo-wee-woo" oscillating tone |
| Ship captured | Rising tone + ship disappears |
| Ship rescued | Descending tone + ship joins |
| Enemy dive | Whooshing sound (varies by enemy type) |
| Enemy bullet fire | Short "pewpew" |
| Challenging Stage complete | Results jingle |
| Perfect bonus | Special triumphant sound |
| Extra life | 1-UP jingle |
| Formation breathing | Subtle pulsing hum |
| Stage transition | Brief silence then new stage jingle |

---

## 12. Animation & Visual Effects

### 12.1 Player Ship

| State | Frames | Description |
|-------|--------|-------------|
| Idle | 1 | Static ship sprite |
| Firing | 1 (flash) | Muzzle flash at barrel |
| Death | 8 | Ship explodes in expanding firework pattern |
| Captured | 4 | Ship rises, rotates, attaches to Boss Galaga |
| Dual join | 4 | Rescued ship descends and aligns with current ship |

### 12.2 Enemy Animations

| Enemy | Frames | Description |
|-------|--------|-------------|
| Bee (formation) | 2 | Wing flap animation |
| Bee (diving) | 4 | Full rotation/flip while diving |
| Butterfly (formation) | 2 | Wing flutter |
| Butterfly (diving) | 4 | Rotation during dive |
| Boss Galaga (formation) | 2 | Pulsing glow |
| Boss Galaga (diving) | 4 | Wings spread, intimidating |
| Boss Galaga (beam) | 4 | Beam extension animation |
| Boss Galaga (damaged) | 2 | Color change (green → blue), faster pulse |

### 12.3 Explosion Effects

| Type | Frames | Size | Color |
|------|--------|------|-------|
| Small (Bee/Butterfly) | 4 | 16x16 | White/yellow flash → orange → fade |
| Medium (Boss Galaga) | 6 | 24x24 | Blue/white flash → orange → red → fade |
| Large (Player) | 8 | 32x32 | White starburst → orange spray → fade |

### 12.4 Capture Beam Visual

- Beam extends from Boss Galaga downward.
- Visual: blue/white oscillating column of light.
- Width: ~24 pixels.
- Length: extends to bottom of screen over 0.5 seconds.
- Animation: 4-frame shimmer loop while active.
- Retraction: collapses back upward over 0.3 seconds.

---

## 13. Lives & Continue System

### Lives

| Property | Value |
|----------|-------|
| Starting lives | 3 (configurable via DIP switches: 2, 3, or 5) |
| Maximum lives display | 7 (capped display, can accumulate more) |
| Extra life 1 | 20,000 points |
| Extra life 2 | 70,000 points |
| No further score-based lives | — |

### Death & Respawn

| Property | Value |
|----------|-------|
| Death trigger | Enemy bullet or enemy sprite contacts player ship hitbox |
| Death animation | 8-frame explosion (~0.5 seconds) |
| Respawn delay | ~2 seconds after death animation |
| Respawn position | Center-bottom of screen |
| Invincibility after spawn | ~2 seconds (ship flashes) |
| Game state on death | Remaining enemies continue in formation; stage is NOT reset |

### Game Over

| Property | Value |
|----------|-------|
| Trigger | Last life lost |
| Display | "GAME OVER" text center-screen for 3 seconds |
| Statistics | Hit-miss ratio displayed |
| High score entry | If qualifying, initials entry screen |
| Continue | Depends on arcade settings (typically no continue) |

---

## Appendix A: Quick Reference — Enemy Scores

| Enemy | Formation | Diving | Diving w/ Escort |
|-------|-----------|--------|-----------------|
| Bee | 50 | 100 | — |
| Butterfly | 80 | 160 | — |
| Boss Galaga | 150 | 400 | 800-1,600 |
| Captured Ship | 1,000 | — | — |

## Appendix B: Quick Reference — Key Mechanics

| Mechanic | Key Detail |
|----------|-----------|
| Max bullets (single) | 2 on screen |
| Max bullets (dual) | 4 on screen |
| Challenging Stage interval | Every 3 stages (3, 7, 11, ...) |
| Perfect bonus | 10,000 points |
| Capture beam width | ~24 pixels |
| Boss Galaga HP | 2 hits |
| Formation size | 40 enemies (4+8+8+10+10) |

## Appendix C: Formation Map

```
Row 1 (Boss):       B1   B2   B3   B4
Row 2 (Butterfly):  F1  F2  F3  F4  F5  F6  F7  F8
Row 3 (Butterfly):  F9  F10 F11 F12 F13 F14 F15 F16
Row 4 (Bee):        Z1 Z2 Z3 Z4 Z5 Z6 Z7 Z8 Z9 Z10
Row 5 (Bee):        Z11 Z12 Z13 Z14 Z15 Z16 Z17 Z18 Z19 Z20

Total: 4 + 8 + 8 + 10 + 10 = 40 enemies
```

---

*This specification is based on Galaga (1981) by Namco. Values are sourced from arcade board analysis, gameplay documentation, and community resources. Minor variations exist between different arcade board revisions and home console ports.*
