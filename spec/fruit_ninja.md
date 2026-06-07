# Fruit Ninja — Complete Game Specification

> A comprehensive specification for faithfully recreating Fruit Ninja (Halfbrick Studios, 2010). This document covers every system, mechanic, entity, and interaction required for a full clone across all three core modes: Classic, Zen, and Arcade.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Slicing Mechanics](#3-core-slicing-mechanics)
4. [Fruit System](#4-fruit-system)
5. [Bomb System](#5-bomb-system)
6. [Classic Mode](#6-classic-mode)
7. [Zen Mode](#7-zen-mode)
8. [Arcade Mode](#8-arcade-mode)
9. [Combo System](#9-combo-system)
10. [Critical Hit System](#10-critical-hit-system)
11. [Power-Ups & Boosts](#11-power-ups--boosts)
12. [Scoring System](#12-scoring-system)
13. [Blade Effects & Unlockables](#13-blade-effects--unlockables)
14. [Background & Dojo System](#14-background--dojo-system)
15. [UI Layout & Screen Flow](#15-ui-layout--screen-flow)
16. [Fruit Throw Patterns](#16-fruit-throw-patterns)
17. [Progression & Achievements](#17-progression--achievements)
18. [Audio Design](#18-audio-design)
19. [Animation & Visual Effects](#19-animation--visual-effects)
20. [Starfruit & Special Events](#20-starfruit--special-events)

---

## 1. Game Overview

- **Genre**: Action / Casual
- **Perspective**: 2D front-facing
- **Input**: Touch/swipe (mouse drag for PC). Single finger primary; multitouch supported for simultaneous slices.
- **Objective**: Slice fruit launched into the air by swiping across the screen. Avoid bombs. Maximize score.
- **Core Loop**: Fruit is tossed upward from below the screen. Player swipes to slice fruit. Sliced fruit splits into two halves with juice splash. Missed fruit or hit bombs end the game (Classic) or reduce score (Arcade).

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Original resolution | 480 x 320 (iPhone), scales to device |
| Recommended implementation | 960 x 640 or 1920 x 1080 |
| Orientation | Landscape |
| Frame rate target | 60 FPS |
| Physics update | 60 Hz |

### Coordinate System

- Origin (0, 0) at bottom-left of screen.
- Fruit is launched from below the bottom edge (y < 0) with upward velocity.
- Gravity pulls fruit back down after reaching apex.

### Game Loop

```
1. Process input (touch/swipe detection, blade trail update)
2. Update fruit physics (position, velocity, gravity)
3. Update bomb physics (same as fruit)
4. Check slice collisions (blade trail vs fruit/bomb hitboxes)
5. Update particle effects (juice splashes, slice trails)
6. Check miss conditions (fruit falling below screen unsliced)
7. Update score display
8. Update game state (lives, timer, combos)
9. Render (background → fruit → bombs → blade trail → UI → particles)
```

### Physics Constants

| Constant | Value |
|----------|-------|
| Gravity | 980 pixels/second^2 (at 960x640 reference) |
| Fruit launch velocity (Y) | 800-1400 pixels/second upward (varies by difficulty) |
| Fruit launch velocity (X) | -300 to +300 pixels/second (horizontal drift) |
| Fruit rotation speed | -360 to +360 degrees/second (random per fruit) |
| Screen bottom threshold | y = -100 (fruit considered "missed" below this) |

---

## 3. Core Slicing Mechanics

### Blade Trail

- The blade is rendered as a trail following the player's swipe gesture.
- Trail length: last 12-16 touch points, fading from opaque to transparent.
- Trail width: 8-12 pixels at the tip, tapering to 2 pixels at the tail.
- Minimum swipe velocity to register a slice: 100 pixels/second.
- Blade trail persists for ~0.3 seconds after touch release, then fades.

### Slice Detection

- Each fruit has a circular hitbox with radius proportional to its visual size.
- A slice is detected when the blade trail segment intersects the fruit's hitbox.
- The slice angle is calculated from the swipe direction at the point of intersection.
- Fruit splits along the slice angle into two halves.

### Slice Geometry

| Property | Value |
|----------|-------|
| Fruit hitbox radius (standard) | 40-55 pixels (at 960x640) |
| Fruit hitbox radius (small, e.g., starfruit) | 30 pixels |
| Fruit hitbox radius (large, e.g., watermelon) | 65 pixels |
| Minimum swipe length for valid slice | 20 pixels |
| Slice registration delay | 0 frames (instant) |

### Fruit Halves After Slicing

- Two halves separate along the slice line.
- Each half inherits the fruit's current velocity plus a perpendicular separation force.
- Separation velocity: 80-150 pixels/second perpendicular to the slice direction.
- Each half continues to be affected by gravity.
- Halves fall off-screen and are then despawned.
- Juice splash effect spawns at the slice point (color matches fruit).

---

## 4. Fruit System

### Fruit Types

| Fruit | Point Value | Hitbox Radius | Juice Color | Frequency Weight |
|-------|------------|---------------|-------------|-----------------|
| Apple (red) | 1 | 45 px | Red (#CC0000) | 15% |
| Apple (green) | 1 | 45 px | Green (#33CC00) | 10% |
| Orange | 1 | 48 px | Orange (#FF8800) | 15% |
| Watermelon | 1 | 65 px | Red-pink (#FF3366) | 10% |
| Pineapple | 1 | 50 px | Yellow (#FFCC00) | 10% |
| Kiwi | 1 | 40 px | Green (#66CC33) | 10% |
| Coconut | 1 | 50 px | White (#FFFFFF) | 8% |
| Banana | 1 | 42 px | Yellow (#FFE033) | 10% |
| Peach | 1 | 43 px | Pink-orange (#FFAA66) | 7% |
| Strawberry | 1 | 35 px | Red (#EE0033) | 5% |

### Fruit Physics Properties

All fruits share the same physics behavior:
- Subject to gravity after launch.
- Rotate continuously while airborne.
- No air resistance (simplified physics).
- Despawn when center falls 100 pixels below screen bottom.

### Fruit Launch Parameters

| Difficulty Phase | Launch Speed (Y) | Fruits Per Wave | Wave Interval |
|-----------------|-------------------|-----------------|---------------|
| Early (0-30s) | 800-1000 px/s | 1-3 | 1.5-2.5s |
| Mid (30-60s) | 900-1200 px/s | 2-5 | 1.0-2.0s |
| Late (60-90s) | 1000-1300 px/s | 3-6 | 0.7-1.5s |
| Very Late (90s+) | 1100-1400 px/s | 4-8 | 0.5-1.2s |

### Launch Positions

- Fruits launch from the bottom of the screen.
- Horizontal launch positions are distributed across the screen width.
- Launch zones: left third, center third, right third (weighted toward center).
- Fruits can launch from left/right edges with horizontal velocity pointing inward.

---

## 5. Bomb System

### Bomb Types

#### Standard Bomb

| Property | Value |
|----------|-------|
| Appearance | Black sphere with lit fuse, sparking |
| Hitbox radius | 45 px |
| Effect (Classic) | Instant game over |
| Effect (Arcade) | -10 points penalty |
| Effect (Zen) | Not present |
| Launch frequency | Increases with difficulty; starts at ~5% of throws |
| Behavior | Same physics as fruit |

#### Bomb Appearance Scaling

| Time Elapsed | Bomb Frequency |
|-------------|----------------|
| 0-20s | ~3% of throws |
| 20-40s | ~5% of throws |
| 40-60s | ~8% of throws |
| 60-80s | ~10% of throws |
| 80s+ | ~12% of throws |

### Bomb Visual Effects

- On slice: screen flashes white, then fades to sepia/dark.
- Explosion particle effect radiates outward.
- All airborne fruit is destroyed by the explosion.
- A "X" marker appears at the bomb location.
- In Classic mode: slow-motion "Game Over" sequence plays.

---

## 6. Classic Mode

### Rules

- **Starting lives**: 3 (displayed as crossed-out X marks at top-right).
- **Lose a life**: When any fruit falls off the bottom of the screen without being sliced.
- **Game Over**: All 3 lives lost OR a bomb is sliced.
- **No timer**: Game continues indefinitely until game over.
- **Bombs**: Present. Slicing a bomb = instant game over regardless of remaining lives.

### Difficulty Progression

The game progressively increases difficulty based on elapsed time and score:

| Score Threshold | Fruit Speed | Max Fruits/Wave | Bomb Rate | Wave Interval |
|----------------|-------------|-----------------|-----------|---------------|
| 0-25 | Slow | 3 | 3% | 2.0-2.5s |
| 25-75 | Medium | 4 | 5% | 1.5-2.0s |
| 75-150 | Fast | 5 | 8% | 1.2-1.8s |
| 150-250 | Very Fast | 6 | 10% | 0.8-1.5s |
| 250+ | Maximum | 7 | 12% | 0.5-1.2s |

### Life Display

- 3 "X" icons in the top-right corner.
- When a fruit is missed, one X turns red and animates (grows and fades).
- A "whoosh" warning sound plays on each miss.
- On the third miss, all X marks flash and game over sequence begins.

### Special Waves

- **Fruit Frenzy**: Occasionally, a large burst of 10-15 fruits launches simultaneously with no bombs. Signaled by a brief visual cue (screen edges glow).
- Frequency: every 30-60 seconds.
- All fruits in a frenzy wave have slightly higher launch velocity.

---

## 7. Zen Mode

### Rules

- **No lives**: Fruit can fall without penalty.
- **No bombs**: No bombs appear at all.
- **Timer**: 90 seconds (1 minute 30 seconds).
- **Objective**: Score as many points as possible within the time limit.
- **Fruit density**: Higher than Classic mode. Frequent multi-fruit waves.

### Zen Mode Specific Mechanics

| Property | Value |
|----------|-------|
| Duration | 90 seconds |
| Starting fruit rate | 3-4 fruits per wave |
| Peak fruit rate | 6-8 fruits per wave |
| Wave interval | 0.8-1.5 seconds |
| Combo bonus | Standard combo multipliers apply |
| Special fruit | Pomegranate appears (bonus fruit, worth 3 points) |

### Timer Display

- Circular countdown timer in the top-right corner.
- Timer bar decreases smoothly.
- At 10 seconds remaining, timer flashes red.
- At 0 seconds, "Time's Up!" appears and final score is shown.

---

## 8. Arcade Mode

### Rules

- **Timer**: 60 seconds.
- **No lives**: Missing fruit does not end the game.
- **Bombs**: Present. Slicing a bomb deducts 10 points (score cannot go below 0).
- **Special bananas**: Bonus bananas appear that are worth extra points.
- **Power-up fruits**: Freeze, Frenzy, and Double Score bananas appear periodically.

### Arcade Mode Power-Up Bananas

| Power-Up | Appearance | Effect | Duration |
|----------|-----------|--------|----------|
| Freeze | Blue-glowing banana | Freezes all fruit in mid-air for easy slicing | 5 seconds |
| Frenzy | Pink/red-glowing banana | Launches a massive wave of fruit with no bombs | 4 seconds |
| Double Score | Yellow-glowing banana with "x2" | All points earned are doubled | 8 seconds |

### Arcade Scoring

| Action | Points |
|--------|--------|
| Slice a fruit | 1 |
| Slice a fruit during Double Score | 2 |
| 3-fruit combo | 3 bonus (6 during Double Score) |
| 4-fruit combo | 6 bonus |
| 5-fruit combo | 10 bonus |
| 6+ fruit combo | 15+ bonus |
| Bomb hit | -10 |
| Critical hit (pomegranate) | 3 |

### Arcade Difficulty Scaling

| Time Remaining | Fruit Speed | Wave Size | Power-Up Frequency |
|---------------|-------------|-----------|-------------------|
| 60-40s | Medium | 3-5 | Every 15s |
| 40-20s | Fast | 4-6 | Every 12s |
| 20-0s | Very Fast | 5-8 | Every 10s |

---

## 9. Combo System

### Combo Definition

A combo occurs when the player slices 3 or more fruits in a single continuous swipe (within a short time window).

### Combo Timing

| Property | Value |
|----------|-------|
| Combo time window | 0.5 seconds between successive fruit slices |
| Minimum combo size | 3 fruits |
| Maximum theoretical combo | Unlimited (limited by available fruit) |

### Combo Bonuses

| Combo Size | Bonus Points | Visual |
|-----------|-------------|--------|
| 3 fruits | +3 | "Combo x3!" popup |
| 4 fruits | +6 | "Combo x4!" popup |
| 5 fruits | +10 | "Combo x5!" popup |
| 6 fruits | +15 | "Combo x6!" popup |
| 7 fruits | +21 | "Combo x7!" popup |
| 8+ fruits | +n*(n-1)/2 | "Combo x{n}!" popup |

### Combo Visual Feedback

- Combo text appears at the location of the last sliced fruit in the combo.
- Text color escalates: white (3) -> yellow (4) -> orange (5) -> red (6+).
- Font size increases with combo count.
- A brief "whoosh" sound plays for combos of 3+.
- Screen edges flash with the juice color of the combo fruits.

---

## 10. Critical Hit System

### Critical Hit Definition

A critical hit occurs when the player slices a fruit exactly through its center (within a tolerance zone).

| Property | Value |
|----------|-------|
| Critical hit zone radius | 8 pixels from fruit center |
| Critical hit bonus | +1 additional point |
| Visual feedback | Extra large juice splash + "Critical!" text |
| Sound feedback | Higher-pitched slice sound |

---

## 11. Power-Ups & Boosts

### Pre-Game Boosts (Purchasable/Equippable)

| Boost | Effect | Cost (Starfruit) | Duration |
|-------|--------|-------------------|----------|
| Extra Life | Start with 4 lives in Classic | 200 | One game |
| Score x2 Start | Double score for first 15 seconds | 300 | One game |
| Bomb Deflect | First bomb sliced has no penalty | 400 | One game |
| Freeze Start | Begin with 5 seconds of freeze | 250 | One game |
| Peachy Time | +10 seconds in Arcade mode | 350 | One game |

### In-Game Power-Ups (Arcade Mode Only)

Described in Section 8. These appear as special glowing bananas within the fruit stream.

---

## 12. Scoring System

### Base Scoring

| Action | Points |
|--------|--------|
| Slice any fruit | 1 |
| Critical hit bonus | +1 |
| Combo (3+) | See combo table |
| Pomegranate slice | 3 |
| Bomb slice (Arcade) | -10 |
| Bomb slice (Classic) | Game Over |

### High Score System

- Separate high scores for each mode: Classic, Zen, Arcade.
- Top 10 scores stored locally.
- Online leaderboard integration (Game Center / Google Play).
- High score displayed on mode selection screen.

### Score Display

- Current score shown in top-left corner.
- Large, bold, white font with slight shadow.
- Score increments animate (number rolls up).
- New high score announcement at end of game if beaten.

---

## 13. Blade Effects & Unlockables

### Blade Types

| Blade | Trail Color | Trail Effect | Unlock Condition |
|-------|-----------|-------------|-----------------|
| Classic | White | Simple fade trail | Default |
| Flame Blade | Orange-red | Fire particle trail | Score 200+ in Classic |
| Ice Blade | Blue-white | Frost particle trail | Score 200+ in Zen |
| Lightning Blade | Yellow-purple | Electric spark trail | Score 200+ in Arcade |
| Disco Blade | Rainbow | Color-cycling trail | 100 total games played |
| Shadow Blade | Dark purple | Smoke particle trail | Slice 2000 total fruit |
| Starfruit Blade | Gold | Star particle trail | Collect 500 starfruit |
| Bamboo Blade | Green | Leaf particle trail | Achieve 8-combo |
| Butterfly Blade | Pink | Butterfly particle trail | Play 50 Zen games |

### Blade Trail Rendering

```
For each frame:
  1. Record current touch position
  2. Add to trail point buffer (max 16 points)
  3. Remove points older than 0.3 seconds
  4. Render quad strip connecting trail points
  5. Apply blade-specific particle emitters along trail
  6. Alpha: 1.0 at newest point, 0.0 at oldest point
  7. Width: 10px at newest point, 2px at oldest point
```

---

## 14. Background & Dojo System

### Backgrounds

| Background | Appearance | Unlock Condition |
|-----------|-----------|-----------------|
| Classic Dojo | Wooden wall with fruit stains | Default |
| Great Wave | Japanese wave painting backdrop | 500 starfruit |
| Cherry Blossom | Pink blossoms, gentle petal fall | 1000 starfruit |
| Sensei's Swamp | Dark green, misty swamp | 2000 starfruit |
| Gutsu's Cart | Market cart background | 3000 starfruit |

### Background Details

- Backgrounds are static images with subtle animated elements (floating particles, swaying elements).
- Juice stains from sliced fruit persist on the background for the duration of the game.
- Stain positions correspond to where fruits were sliced.
- Stains fade slowly over 10 seconds (alpha from 0.5 to 0.0).
- Background does not affect gameplay.

---

## 15. UI Layout & Screen Flow

### 15.1 Main Menu

```
┌──────────────────────────────────────────────────────┐
│                   FRUIT NINJA                         │
│                   [Logo/Sword]                        │
│                                                       │
│              ┌──────────────┐                        │
│              │   CLASSIC    │                        │
│              └──────────────┘                        │
│              ┌──────────────┐                        │
│              │     ZEN      │                        │
│              └──────────────┘                        │
│              ┌──────────────┐                        │
│              │   ARCADE     │                        │
│              └──────────────┘                        │
│                                                       │
│  [Dojo]  [Blades]  [Boosts]            [Leaderboard] │
│                                          [Starfruit: 520] │
└──────────────────────────────────────────────────────┘
```

### 15.2 In-Game HUD (Classic Mode)

```
┌──────────────────────────────────────────────────────┐
│ Score: 47                              [X] [X] [X]   │
│                                                       │
│                                                       │
│                                                       │
│          [Fruit flying area - full screen]            │
│                                                       │
│                                                       │
│                                                       │
│                            Best: 156                  │
└──────────────────────────────────────────────────────┘
```

### 15.3 In-Game HUD (Zen Mode)

```
┌──────────────────────────────────────────────────────┐
│ Score: 83                          [Timer: 1:12]     │
│                                                       │
│                                                       │
│                                                       │
│          [Fruit flying area - full screen]            │
│                                                       │
│                                                       │
│                                                       │
│                            Best: 230                  │
└──────────────────────────────────────────────────────┘
```

### 15.4 In-Game HUD (Arcade Mode)

```
┌──────────────────────────────────────────────────────┐
│ Score: 112                         [Timer: 0:38]     │
│ [x2 ACTIVE]                                          │
│                                                       │
│                                                       │
│          [Fruit flying area - full screen]            │
│                                                       │
│                                                       │
│                                                       │
│                            Best: 342                  │
└──────────────────────────────────────────────────────┘
```

### 15.5 Game Over Screen

```
┌──────────────────────────────────────────────────────┐
│                                                       │
│                    GAME OVER                          │
│                                                       │
│                   Score: 156                           │
│                 Best: 156 (NEW!)                       │
│                                                       │
│            Fruit Sliced: 142                          │
│            Best Combo: 6                              │
│            Bombs Hit: 0                               │
│                                                       │
│         [Retry]     [Menu]     [Share]                │
│                                                       │
│              Starfruit Earned: +23                    │
└──────────────────────────────────────────────────────┘
```

### 15.6 Screen Flow

```
Splash Screen → Main Menu → Mode Select → Pre-Game (Boosts) → Gameplay → Game Over → Results
                    ↓                                                           ↓
                  Dojo/Blades/Settings                                    Retry (loops)
```

---

## 16. Fruit Throw Patterns

### Pattern Types

The game uses predefined throw patterns mixed with randomized throws:

#### Pattern 1: Single Fruit
- 1 fruit launched from random X position.
- Frequency: Common in early game.

#### Pattern 2: Pair
- 2 fruits launched simultaneously, spread horizontally.
- Gap: 200-300 pixels between launch X positions.

#### Pattern 3: Triple Arc
- 3 fruits launched in quick succession (0.15s apart).
- Forms an arc pattern left-to-right or right-to-left.

#### Pattern 4: Cluster
- 4-6 fruits launched nearly simultaneously.
- All from similar X position, with slight velocity variation.
- Prime combo opportunity.

#### Pattern 5: V-Shape
- 5 fruits in a V formation.
- Two outside fruits launch first, center fruit last.
- Time between first and last: 0.3 seconds.

#### Pattern 6: Frenzy Wave
- 10-15 fruits launched over 1 second.
- No bombs included.
- Occurs every 30-60 seconds in Classic mode.

#### Pattern 7: Bomb Trap
- 3-4 fruits surrounding 1 bomb, launched simultaneously.
- Tests precision slicing.
- Only appears after score > 50 in Classic mode.

### Throw Sequencing Algorithm

```
1. Determine current difficulty tier based on score/time.
2. Select a pattern from weighted random table:
   - Single: 30% (decreases with difficulty)
   - Pair: 25%
   - Triple: 15%
   - Cluster: 10% (increases with difficulty)
   - V-Shape: 5%
   - Frenzy: 5%
   - Bomb Trap: 10% (increases with difficulty)
3. Apply difficulty modifiers to launch parameters.
4. Wait wave interval (decreases with difficulty).
5. Repeat.
```

---

## 17. Progression & Achievements

### Starfruit Currency

- Starfruit is the premium/soft currency.
- Earned by: slicing starfruit (appears rarely in-game, worth 1 starfruit each), completing challenges, achieving high scores.
- Used to: purchase blades, backgrounds, boosts.

### Challenges (Daily/Cumulative)

| Challenge | Requirement | Reward |
|-----------|------------|--------|
| Slice 50 fruit in Classic | 50 fruit sliced | 10 starfruit |
| Get a 5-combo | Single combo of 5+ | 20 starfruit |
| Score 100 in Zen | Zen score >= 100 | 15 starfruit |
| No bombs in Arcade | Complete Arcade with 0 bomb hits | 30 starfruit |
| Play 5 games today | Play any 5 games | 25 starfruit |
| Slice 1000 total fruit | Cumulative 1000 fruit | 50 starfruit |
| Slice 10000 total fruit | Cumulative 10000 fruit | 200 starfruit |

### Achievements

| Achievement | Condition | Points |
|------------|-----------|--------|
| Apprentice | Score 50 in Classic | 10 |
| Ninja | Score 100 in Classic | 25 |
| Master | Score 200 in Classic | 50 |
| Grandmaster | Score 300 in Classic | 100 |
| Zen Master | Score 200 in Zen | 50 |
| Arcade King | Score 300 in Arcade | 50 |
| Combo Starter | Get a 3-combo | 10 |
| Combo Artist | Get a 5-combo | 25 |
| Combo Maniac | Get a 7-combo | 50 |
| Combo Legend | Get a 10-combo | 100 |
| Bomb Dodger | Score 100 in Classic, 0 bombs | 50 |
| Fruit Lover | Slice 5000 total fruit | 50 |
| Sharpshooter | 10 critical hits in one game | 50 |

---

## 18. Audio Design

### 18.1 Music

| Track | Context | Style |
|-------|---------|-------|
| Menu Theme | Main menu | Upbeat Japanese-inspired, taiko drums |
| Classic Theme | Classic mode gameplay | Energetic, building tempo |
| Zen Theme | Zen mode gameplay | Calm, ambient, koto and flute |
| Arcade Theme | Arcade mode gameplay | Fast-paced, electronic |
| Game Over Jingle | Game over screen | Short, descending tone |
| New High Score | New high score achieved | Triumphant fanfare |

### 18.2 Sound Effects

| Event | Sound Description |
|-------|-------------------|
| Fruit slice | Crisp "schwick" with wet fruit squish |
| Bomb slice | Deep "boom" explosion |
| Fruit miss (Classic) | Splatting thud + warning whoosh |
| Combo (3) | Rising chime "ding-ding-ding" |
| Combo (5+) | Escalating chime sequence + crowd cheer |
| Critical hit | Sharp metallic "shing" |
| Power-up collected | Magical chime with echo |
| Freeze activate | Crystalline ice sound + time-slow effect |
| Frenzy activate | Rapid drum roll |
| Double Score activate | Cash register "cha-ching" |
| Timer warning (10s) | Ticking clock, increasing tempo |
| Menu button press | Soft click |
| Blade swipe (idle) | Light whoosh (proportional to swipe speed) |
| Starfruit collected | Sparkling chime |
| Life lost | Low-pitched "dun" |
| Game start | Gong strike |

### 18.3 Audio Layering

- Slice sounds are pitch-shifted slightly with each successive slice in a combo.
- Pitch starts at 1.0x and increases by 0.05x per combo fruit (up to 1.5x).
- Background music volume reduces to 60% during power-up activation.

---

## 19. Animation & Visual Effects

### 19.1 Fruit Animation

| State | Description |
|-------|-------------|
| **Airborne** | Fruit rotates continuously. Rotation speed: -360 to +360 deg/s (random). Slight shadow beneath. |
| **Sliced** | Two halves separate along slice line. Each half has exposed fruit interior texture. Halves continue rotating and falling. |
| **Juice Splash** | Particle burst at slice point. 15-25 droplet particles. Colors match fruit type. Droplets spray in a cone perpendicular to the blade direction. |
| **Stain** | Circular juice stain on background at slice point. Radius: 40-80px. Fades over 10 seconds. |

### 19.2 Bomb Animation

| State | Description |
|-------|-------------|
| **Airborne** | Black sphere with sparking fuse. Fuse sparks emit small orange particles. |
| **Sliced** | White screen flash (0.2s). Explosion particle effect (red-orange-yellow). Screen shake (amplitude: 10px, duration: 0.5s). Smoke dissipation over 1 second. |

### 19.3 Blade Trail Rendering

- Trail is rendered as a series of connected quads.
- Each quad is textured with the current blade's trail texture.
- Additive blending for glowing blade effects.
- Particle emitters attached to the trail tip for special blades.

### 19.4 Screen Effects

| Effect | Trigger | Description |
|--------|---------|-------------|
| Screen shake | Bomb explosion | 10px amplitude, 0.5s duration, sinusoidal decay |
| Flash | Bomb explosion | White overlay, 0.2s fade-out |
| Slow motion | Game over (bomb) | Time scale reduces to 0.3x for 1 second |
| Score popup | Any score event | Float upward from event location, fade over 1 second |
| Combo popup | 3+ combo | Large text at combo center, scale up then fade, 1.5 seconds |
| Freeze effect | Freeze power-up | Blue tint overlay, frost particles at screen edges |
| Frenzy effect | Frenzy power-up | Screen edge glow (golden), fruit rain from all directions |

---

## 20. Starfruit & Special Events

### Starfruit Spawning

| Property | Value |
|----------|-------|
| Appearance | Golden star-shaped fruit, glowing |
| Spawn chance | 1% per fruit throw |
| Value | 1 starfruit (premium currency) |
| Point value | 3 (like pomegranate) |
| Hitbox | 30 px radius |
| Behavior | Same physics as normal fruit |

### Pomegranate (Zen Mode Exclusive)

| Property | Value |
|----------|-------|
| Appearance | Red-purple, slightly larger than standard fruit |
| Spawn chance | 5% per fruit throw in Zen |
| Point value | 3 points |
| Hitbox | 50 px radius |

### Special Event: Dragon Fruit (Rare)

| Property | Value |
|----------|-------|
| Appearance | Pink-white exotic fruit, trailing sparkle particles |
| Spawn chance | 0.5% per fruit throw |
| Effect | Slicing triggers a "fruit tornado" — 20 fruits launch simultaneously |
| Point value | 5 points |

---

## Appendix A: Quick Reference — Timing Values

| Mechanic | Time |
|----------|------|
| Classic mode game length | Variable (until game over) |
| Zen mode duration | 90 seconds |
| Arcade mode duration | 60 seconds |
| Combo time window | 0.5 seconds between slices |
| Blade trail persistence | 0.3 seconds |
| Freeze power-up duration | 5 seconds |
| Frenzy power-up duration | 4 seconds |
| Double Score duration | 8 seconds |
| Juice stain fade time | 10 seconds |
| Bomb explosion duration | 0.5 seconds |
| Slow-motion on game over | 1 second at 0.3x speed |
| Score popup float duration | 1 second |
| Combo popup duration | 1.5 seconds |

## Appendix B: Quick Reference — Score Targets

| Mode | Average Score | Good Score | Expert Score |
|------|-------------|-----------|-------------|
| Classic | 50-100 | 150-200 | 300+ |
| Zen | 100-150 | 200-300 | 400+ |
| Arcade | 100-200 | 300-400 | 500+ |

## Appendix C: Difficulty Curves

### Classic Mode Difficulty Curve

```
Difficulty
    ^
    |                                    ___________
    |                              _____/
    |                        _____/
    |                  _____/
    |            _____/
    |      _____/
    |_____/
    +----+----+----+----+----+----+----+-----> Score
    0   25   50   75  100  150  200  250+
```

### Fruit Density Over Time (Zen Mode)

```
Fruits/Wave
    ^
  8 |                              ___________
  7 |                        _____/
  6 |                  _____/
  5 |            _____/
  4 |      _____/
  3 |_____/
    +----+----+----+----+----+----+-----> Time (s)
    0   15   30   45   60   75   90
```

---

*This specification is based on Fruit Ninja (2010) by Halfbrick Studios, primarily the iOS/Android version. Values are sourced from gameplay analysis and community documentation. Minor variations may exist between platform versions.*
