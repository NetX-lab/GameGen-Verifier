# Space Invaders — Complete Game Specification

> A comprehensive specification for faithfully recreating Space Invaders (Taito, 1978 Arcade). This document covers every system, mechanic, entity, and interaction required for a full clone of the pioneering fixed-shooter arcade game.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Player Cannon Mechanics](#3-player-cannon-mechanics)
4. [Invader System](#4-invader-system)
5. [UFO (Mystery Ship)](#5-ufo-mystery-ship)
6. [Shield System](#6-shield-system)
7. [Scoring System](#7-scoring-system)
8. [Difficulty Progression](#8-difficulty-progression)
9. [UI Layout & HUD](#9-ui-layout--hud)
10. [Audio Design](#10-audio-design)
11. [Animation & Visual Effects](#11-animation--visual-effects)
12. [Lives & Game Over](#12-lives--game-over)
13. [Wave Progression Details](#13-wave-progression-details)

---

## 1. Game Overview

- **Genre**: Fixed shooter
- **Perspective**: 2D top-down (vertical screen)
- **Players**: 1-2 players (alternating turns)
- **Input**: 2-way joystick (left/right) + 1 button (Fire)
- **Objective**: Destroy all 55 invaders in the wave before they reach the bottom of the screen. Survive as many waves as possible.
- **Lose Condition**: All lives lost, OR invaders reach the player's level (bottom of screen).

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Original resolution | 224 x 256 pixels (rotated 90 degrees — hardware is 256x224) |
| Recommended implementation | 448 x 512 or 672 x 768 |
| Orientation | Vertical (portrait) |
| Frame rate | 60 FPS |
| Color | Original was monochrome with colored cellophane overlay |

### Color Overlay Zones (Original Cabinet)

| Screen Zone | Color | Purpose |
|-------------|-------|---------|
| Top strip (UFO area) | Red | Mystery ship area |
| Upper area (invader rows 1-3) | White | Upper invaders |
| Middle area (invader rows 4-5) | Green | Lower invaders |
| Bottom strip (player/shields) | Green | Player and shields |
| Very bottom (score/lives) | White | HUD area |

### Coordinate System

- Origin (0, 0) at top-left.
- Player moves along the bottom.
- Invaders start near the top and descend.

### Game Loop

```
1. Process input (left/right movement, fire button)
2. Move player cannon
3. Update player bullet (only one on screen at a time)
4. Move invaders (one invader moves per frame in sequence)
5. Check invader boundary (hit edge = reverse direction + drop)
6. Update invader bullets (up to 3 on screen)
7. Check player bullet vs invader collisions
8. Check player bullet vs UFO collision
9. Check player bullet vs shield collision
10. Check invader bullet vs player collision
11. Check invader bullet vs shield collision
12. Check invader position vs bottom threshold (game over check)
13. Update UFO movement
14. Update explosions
15. Check wave clear condition
16. Render (background → shields → invaders → UFO → player → bullets → UI)
```

### Critical Implementation Detail: Frame-Based Movement

The original Space Invaders moves **one invader per frame** (not all invaders simultaneously). This means:
- With 55 invaders: the full formation takes 55 frames (~0.92 seconds) to complete one movement step.
- With 10 invaders remaining: takes only 10 frames (~0.17 seconds) per step.
- **This is why invaders speed up as you destroy them** — fewer invaders = fewer frames per full step = faster apparent movement.

---

## 3. Player Cannon Mechanics

### Cannon Properties

| Property | Value |
|----------|-------|
| Hitbox | 13 x 8 pixels |
| Movement speed | 1 px/frame (60 px/s) |
| Movement range | x = 16 to x = 200 |
| Fixed Y position | y = 216 |
| Fire rate | One bullet on screen at a time |
| Bullet speed | 4 px/frame upward |
| Bullet size | 1 x 4 pixels |
| Max bullets on screen | 1 (must wait for current to hit or leave screen) |

### Player Death

| Property | Value |
|----------|-------|
| Death trigger | Invader bullet or invader body contacts cannon |
| Death animation | Cannon explodes (expanding pixel pattern), 2 seconds |
| Respawn delay | 2 seconds after death animation |
| Respawn position | Far left of movement range |
| Invincibility | ~1 second after respawn (cannon flashes) |
| Game state during death | All invaders and bullets freeze during death animation |

---

## 4. Invader System

### 4.1 Invader Types

| Type | Row | Appearance | HP | Score |
|------|-----|-----------|-----|-------|
| Small (Squid) | Row 1 (top) | Squid-like, 8x8 px | 1 | 30 |
| Medium (Crab) | Rows 2-3 | Crab-like, 11x8 px | 1 | 20 |
| Large (Octopus) | Rows 4-5 (bottom) | Octopus-like, 12x8 px | 1 | 10 |

### 4.2 Formation Layout

```
Row 1:  S  S  S  S  S  S  S  S  S  S  S   (11 Small/Squid, 30 pts each)
Row 2:  M  M  M  M  M  M  M  M  M  M  M   (11 Medium/Crab, 20 pts each)
Row 3:  M  M  M  M  M  M  M  M  M  M  M   (11 Medium/Crab, 20 pts each)
Row 4:  L  L  L  L  L  L  L  L  L  L  L   (11 Large/Octopus, 10 pts each)
Row 5:  L  L  L  L  L  L  L  L  L  L  L   (11 Large/Octopus, 10 pts each)

Total: 55 invaders (5 rows x 11 columns)
```

### 4.3 Formation Dimensions

| Property | Value |
|----------|-------|
| Invader width | 12 pixels (largest) |
| Invader height | 8 pixels |
| Horizontal spacing | 16 pixels (center-to-center) |
| Vertical spacing | 16 pixels (center-to-center) |
| Formation width | ~176 pixels (11 invaders x 16 px spacing) |
| Formation height | ~80 pixels (5 rows x 16 px spacing) |
| Starting Y position | Row 1 starts at y = 64 |

### 4.4 Movement System

**The movement system is the core of Space Invaders' design.**

Each frame, exactly ONE invader moves. The game cycles through all living invaders sequentially (left-to-right, bottom-to-top within each row).

| Property | Value |
|----------|-------|
| Step size (horizontal) | 2 pixels per step |
| Step size (vertical drop) | 8 pixels per drop |
| Direction change | When ANY invader in the formation hits the screen edge |
| Edge boundaries | x = 10 (left edge) and x = 202 (right edge) |

### Movement Sequence

```
For each frame:
  1. Select next invader in sequence (wrapping around after the last)
  2. Skip if dead
  3. Move invader 2 pixels in current direction (left or right)
  4. If this invader has reached the screen edge:
     a. Set flag: "reverse direction after this full sweep"
  5. After all living invaders have moved once (one full sweep):
     a. If edge was hit during sweep:
        - Reverse direction (left ↔ right)
        - Move ALL invaders down 8 pixels
```

### Speed Increase Effect

| Living Invaders | Frames Per Full Sweep | Effective Speed |
|----------------|----------------------|-----------------|
| 55 | 55 frames (0.92s) | Slowest |
| 40 | 40 frames (0.67s) | Slow |
| 30 | 30 frames (0.50s) | Medium |
| 20 | 20 frames (0.33s) | Fast |
| 10 | 10 frames (0.17s) | Very Fast |
| 5 | 5 frames (0.08s) | Extremely Fast |
| 1 | 1 frame (0.017s) | Maximum Speed |

### 4.5 Invader Shooting

| Property | Value |
|----------|-------|
| Max bullets on screen | 3 |
| Bullet speed | 2-3 px/frame (varies by type) |
| Bullet types | 3 different visual types (rolling, plunger, squiggly) |
| Shooter selection | Weighted toward columns above the player |
| Fire rate | ~1 bullet per 30-60 frames |

#### Bullet Type Details

| Bullet Type | Speed | Visual | Behavior |
|-------------|-------|--------|----------|
| Rolling | 2 px/frame | Alternating plus/cross shape | Standard |
| Plunger | 2 px/frame | Thin vertical with hat | Aimed at player column |
| Squiggly | 3 px/frame | Zigzag pattern | Faster, random column |

### 4.6 Invader Column Targeting

The game selects which column fires based on the player's position:
- **Plunger bullet**: Fired from the column directly above the player.
- **Rolling/Squiggly**: Fired from random columns.
- Priority: Bottom-most invader in the selected column fires.

---

## 5. UFO (Mystery Ship)

### UFO Properties

| Property | Value |
|----------|-------|
| Appearance | Classic flying saucer shape, 16 x 7 pixels |
| Speed | 1 px/frame |
| Direction | Alternates (first appearance: left-to-right; next: right-to-left) |
| Spawn trigger | Appears when the player has fired a specific number of shots |
| Spawn interval | Every 25th shot (approximately) |
| Y position | y = 32 (top of screen, below score) |
| Score | 50, 100, 150, or 300 (see scoring table) |

### UFO Scoring (Not Random!)

The UFO score is determined by the player's shot count:

| Player Shot Count (mod 15) | UFO Score |
|---------------------------|-----------|
| 1 | 100 |
| 2 | 50 |
| 3 | 100 |
| 4 | 150 |
| 5 | 100 |
| 6 | 100 |
| 7 | 50 |
| 8 | 300 |
| 9 | 100 |
| 10 | 100 |
| 11 | 100 |
| 12 | 50 |
| 13 | 150 |
| 14 | 100 |
| 15 | 100 |

To consistently get 300 points: fire exactly on the 23rd shot count pattern.

### UFO Sound

- Distinctive oscillating "woo-woo-woo" sound while on screen.
- Sound stops when UFO is destroyed or exits screen.

---

## 6. Shield System

### Shield Properties

| Property | Value |
|----------|-------|
| Number of shields | 4 |
| Shield width | 22 pixels |
| Shield height | 16 pixels |
| Shield shape | Inverted U / bunker shape |
| Positions | Evenly spaced across the screen width |
| Shield 1 center X | ~50 |
| Shield 2 center X | ~88 |
| Shield 3 center X | ~128 |
| Shield 4 center X | ~166 |
| Shield Y position | y = 192 (above player cannon) |

### Shield Damage System

Shields are pixel-based destructible objects. Each pixel of the shield can be individually destroyed.

| Property | Value |
|----------|-------|
| Destruction by player bullet | ~3x3 pixel area removed at impact point |
| Destruction by invader bullet | ~3x3 pixel area removed at impact point |
| Destruction by invader contact | Large chunk removed (invader-sized hole) |
| Reconstruction | Shields are rebuilt at the start of each new wave |

### Shield Shape (Pixel Map, 22x16)

```
      ██████████████████
    ██████████████████████
   ████████████████████████
  ██████████████████████████
  ██████████████████████████
  ██████████████████████████
  ██████████████████████████
  ██████████████████████████
  ██████████████████████████
  ██████████████████████████
  ██████████████████████████
  ██████████████████████████
  ██████████████████████████
  ████████        ████████
  ██████            ██████
  ██████            ██████
```

The bottom has a notch (opening) so players can shoot from partially behind cover.

### Shield Interaction Rules

- Player bullets pass through holes in the shield.
- Invader bullets pass through holes in the shield.
- Both create new holes where they impact.
- Shields provide gradually diminishing cover as they take damage.
- When invaders descend to shield level, they destroy any remaining shield pixels on contact.

---

## 7. Scoring System

### Kill Scores

| Target | Points |
|--------|--------|
| Large Invader (Octopus) — bottom 2 rows | 10 |
| Medium Invader (Crab) — middle 2 rows | 20 |
| Small Invader (Squid) — top row | 30 |
| UFO (Mystery Ship) | 50, 100, 150, or 300 (see table) |

### Score Per Full Wave

| Row(s) | Count | Points Each | Subtotal |
|--------|-------|-------------|----------|
| Bottom 2 rows (Octopus) | 22 | 10 | 220 |
| Middle 2 rows (Crab) | 22 | 20 | 440 |
| Top row (Squid) | 11 | 30 | 330 |
| **Total per wave** | **55** | — | **990** |

Maximum score per wave (excluding UFO): 990 points.

### Score Display

- 4-digit display (maximum 9,999 displayed, wraps at 10,000).
- Score is stored as a higher value internally but display wraps.
- High score is displayed separately.

### Extra Lives

| Score | Effect |
|-------|--------|
| 1,500 | 1 extra life (default DIP switch setting) |
| DIP options | 1,000 or 1,500 for first extra life |
| No further score-based lives | Only 1 extra life from score |

---

## 8. Difficulty Progression

### Wave-Based Difficulty

| Wave | Starting Y | Invader Bullet Speed | Bullet Frequency | UFO Frequency |
|------|-----------|---------------------|------------------|---------------|
| 1 | y = 64 | 2 px/frame | Every 48 frames | Normal |
| 2 | y = 72 (8px lower) | 2 px/frame | Every 44 frames | Normal |
| 3 | y = 80 | 2 px/frame | Every 40 frames | Normal |
| 4 | y = 88 | 2.5 px/frame | Every 36 frames | Normal |
| 5 | y = 96 | 2.5 px/frame | Every 34 frames | Increased |
| 6 | y = 104 | 3 px/frame | Every 32 frames | Increased |
| 7 | y = 112 | 3 px/frame | Every 30 frames | Increased |
| 8 | y = 120 | 3 px/frame | Every 28 frames | Increased |
| 9+ | y = 120 (capped) | 3 px/frame | Every 26 frames | Maximum |

### Starting Position Progression

Each new wave, the invaders start 8 pixels lower (closer to the player). This continues up to a cap, after which invaders start at the lowest initial position for all subsequent waves.

### Game Over by Invasion

If ANY invader reaches y = 216 (player's Y level), the game ends immediately, regardless of remaining lives.

---

## 9. UI Layout & HUD

### 9.1 Screen Layout

```
┌────────────────────────┐
│ SCORE<1>  HI-SCORE  SCORE<2> │
│  0480      1250      0000    │
│                              │
│        [UFO area]            │
│                              │
│ SSSSSSSSSSSS  (Row 1, 30pt)  │
│ MMMMMMMMMMMM (Row 2, 20pt)  │
│ MMMMMMMMMMMM (Row 3, 20pt)  │
│ LLLLLLLLLLLL  (Row 4, 10pt)  │
│ LLLLLLLLLLLL  (Row 5, 10pt)  │
│                              │
│                              │
│  [Shield] [Shield] [Shield] [Shield] │
│                              │
│        [Player Cannon]       │
│                              │
│ ♦♦♦ (lives)     CREDIT 01   │
└────────────────────────────┘
```

### HUD Elements

| Element | Position | Description |
|---------|----------|-------------|
| SCORE<1> | Top-left | Player 1 score |
| HI-SCORE | Top-center | Session high score |
| SCORE<2> | Top-right | Player 2 score (2P mode) |
| Lives | Bottom-left | Ship icons (remaining lives, not counting current) |
| CREDIT | Bottom-right | Credits inserted |

---

## 10. Audio Design

### 10.1 Music / Rhythm

Space Invaders has no traditional music. Instead, it uses a **4-note heartbeat bass line** that serves as the game's tempo:

| Note Sequence | Pitch | Tempo Change |
|--------------|-------|-------------|
| Note 1 | Low C | Base tempo matches invader movement speed |
| Note 2 | Low B | |
| Note 3 | Low A | |
| Note 4 | Low G# | |

**Tempo**: The 4-note sequence loops continuously. The tempo increases as invaders are destroyed (matching the frame-speed increase). This creates the iconic escalating tension.

| Invaders Remaining | Approximate BPM |
|-------------------|-----------------|
| 55 | ~60 BPM |
| 40 | ~80 BPM |
| 30 | ~100 BPM |
| 20 | ~130 BPM |
| 10 | ~180 BPM |
| 5 | ~240 BPM |
| 1 | ~400+ BPM |

### 10.2 Sound Effects

| Event | Description |
|-------|-------------|
| Player shoot | Sharp "pew" (high-pitched) |
| Invader death | White noise burst (~0.2s) |
| Player death | Long descending tone sequence (~2s) |
| UFO flying | Oscillating "woo-woo-woo" (continuous while on screen) |
| UFO destroyed | Brief explosion tone |
| Invader bullet | Quiet pulsing tone |
| Shield impact | Short impact sound |
| Extra life | Brief ascending jingle |
| Wave clear | Brief silence before next wave |

---

## 11. Animation & Visual Effects

### 11.1 Invader Animations

Each invader type has exactly 2 animation frames, alternating with each movement step:

| Type | Frame 1 | Frame 2 | Description |
|------|---------|---------|-------------|
| Small (Squid) | Arms up | Arms down | Squid-like tentacles alternate |
| Medium (Crab) | Claws out | Claws in | Crab pincer animation |
| Large (Octopus) | Legs spread | Legs together | Octopus tentacles wave |

The frame toggles each time the invader takes a movement step (every time it's the invader's turn to move).

### 11.2 Explosion Animations

| Explosion Type | Frames | Duration | Description |
|---------------|--------|----------|-------------|
| Invader death | 1 (splash) | 6 frames | Single frame "splat" sprite shown at death position |
| Player death | 2 (alternating) | 120 frames | Expanding pixel pattern, alternating between two explosion sprites |
| UFO death | 1 + score display | 60 frames | Score value shown at UFO position |

### 11.3 Bullet Animations

| Bullet Type | Frames | Animation |
|-------------|--------|-----------|
| Player bullet | 1 | Static thin line moving upward |
| Rolling bullet | 4 | Plus/cross shape rotating |
| Plunger bullet | 2 | Thin shape alternating |
| Squiggly bullet | 4 | Zigzag shape shifting |

---

## 12. Lives & Game Over

### Lives System

| Property | Value |
|----------|-------|
| Starting lives | 3 (DIP switch: 3, 4, 5, or 6) |
| Maximum lives | No cap (extra lives from score rare — only 1) |
| Extra life | At 1,500 points (or 1,000, configurable) |
| Lives display | Small cannon icons at bottom-left |

### Game Over Conditions

| Condition | Result |
|-----------|--------|
| All lives lost | "GAME OVER" displayed |
| Invaders reach player level | Instant game over regardless of lives |
| Invader contacts shield at bottom | Shield destroyed but no instant game over |

### Two-Player Mode

- Players alternate turns.
- Each player has their own score, lives, and wave progress.
- When one player loses a life, the other player takes their turn.
- Each player's game state (invader positions, shield damage) is preserved between turns.
- The game ends when both players are out of lives.

---

## 13. Wave Progression Details

### Between Waves

| Property | Value |
|----------|-------|
| Pause duration | ~2 seconds |
| Shield reconstruction | All 4 shields rebuilt to full |
| Invader formation | Full 55 invaders respawn |
| Starting Y | 8 pixels lower than previous wave (up to cap) |
| Score | Carries over |
| Lives | Carry over |

### Endless Play

The game has no final stage. Waves continue with increasing difficulty until the player runs out of lives. After wave 8-9, difficulty caps at maximum settings.

### Edge Cases

| Scenario | Behavior |
|----------|----------|
| Last invader alive | Moves extremely fast (1 frame per movement step) |
| Invader at edge with 1 remaining | Bounces rapidly left-right while descending |
| All shields destroyed | No reconstruction until new wave |
| Player shoots through own shield | Bullet removes shield pixels as it passes |
| Invader on same row as shield | Shield pixels under invader are destroyed |

---

## Appendix A: Quick Reference — Key Values

| Property | Value |
|----------|-------|
| Screen size | 224 x 256 pixels |
| Total invaders per wave | 55 (5 rows x 11 columns) |
| Max player bullets | 1 |
| Max invader bullets | 3 |
| Player speed | 1 px/frame |
| Invader step size | 2 px horizontal, 8 px drop |
| Shield count | 4 |
| UFO score range | 50-300 |
| Extra life | At 1,500 points |
| Starting lives | 3 |

## Appendix B: Quick Reference — Invader Speed by Count

```
Speed
  ^
  |*
  | *
  |  *
  |   **
  |     ***
  |        ****
  |            *******
  |                   **************
  +--+--+--+--+--+--+--+--+--+--+--> Invaders Remaining
  1  5  10 15 20 25 30 35 40 45 50 55
```

## Appendix C: Shield Pixel Map (Detailed)

Each shield is a 22x16 pixel bitmap. Damage is tracked per-pixel.

```
Column:  0123456789012345678901
Row 0:   ....██████████████....
Row 1:   ..████████████████████..
Row 2:   .██████████████████████.
Row 3:   ████████████████████████
Row 4:   ████████████████████████
Row 5:   ████████████████████████
Row 6:   ████████████████████████
Row 7:   ████████████████████████
Row 8:   ████████████████████████
Row 9:   ████████████████████████
Row 10:  ████████████████████████
Row 11:  ████████████████████████
Row 12:  ████████████████████████
Row 13:  ████████....████████
Row 14:  ██████........██████
Row 15:  ██████........██████
```

Each `█` is a destructible pixel. `.` is empty space.

---

*This specification is based on Space Invaders (1978) by Taito/Midway for arcade. Values are sourced from hardware analysis, ROM examination, and community documentation. Home console ports (Atari 2600, NES, etc.) have significant differences.*
