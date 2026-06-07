# Celeste — Complete Game Specification

> A comprehensive specification for faithfully recreating Celeste (Matt Makes Games / Extremely OK Games, 2018). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics — Movement](#3-core-mechanics--movement)
4. [Player Character — Madeline](#4-player-character--madeline)
5. [Hazards & Objects](#5-hazards--objects)
6. [Chapter Progression](#6-chapter-progression)
7. [All Chapters — Room-by-Room Design](#7-all-chapters)
8. [Collectibles](#8-collectibles)
9. [B-Side & C-Side Chapters](#9-b-side--c-side-chapters)
10. [UI Layout & Screens](#10-ui-layout--screens)
11. [Audio Design](#11-audio-design)
12. [Visual Effects](#12-visual-effects)
13. [Assist Mode](#13-assist-mode)

---

## 1. Game Overview

- **Genre**: Precision platformer
- **Perspective**: 2D side-scrolling
- **Input**: D-pad/analog stick (8-directional), Jump, Dash, Grab/Climb
- **Objective**: Help Madeline climb Celeste Mountain across 7 main chapters (+1 epilogue, +B-sides, +C-sides).
- **Lose Condition**: Touching any hazard (spikes, pits) = instant death. Respawn at room start.
- **Win Condition**: Complete all rooms in a chapter to advance. Complete Chapter 7 for main story ending.
- **Death counter**: Tracked per chapter and total. No penalty for dying.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 320 x 180 pixels (internal) |
| Display resolution | Scaled to window/fullscreen (typically 1920x1080 = 6x) |
| Tile size | 8 x 8 pixels |
| Frame rate | 60 FPS |
| Physics updates | Fixed timestep at 60Hz |
| Engine | Monocle (C#/FNA), originally XNA |

### Coordinate System

- Origin (0, 0) at top-left of current room.
- Sub-pixel positions tracked as floats.
- Each room is a fixed size (varies per room, typically 40x23 tiles = 320x184 pixels).
- Rooms connect seamlessly — transitioning to next room when Madeline exits a boundary.

### Game Loop

```
1. Process input (buffer system for jump/dash)
2. Update scene (current chapter state)
3. Update player (movement, dash, climb, state machine)
4. Update all entities (moving platforms, springs, etc.)
5. Update particles and effects
6. Check collisions (player vs tiles, player vs hazards, player vs entities)
7. Camera update (follow player with dead zone, room transitions)
8. Render background layers (parallax, up to 4 layers)
9. Render tilemap (foreground + background)
10. Render entities
11. Render player + hair
12. Render particles/effects
13. Render HUD (death counter, strawberry counter, timer)
```

---

## 3. Core Mechanics — Movement

### Input Buffering

| Buffer | Duration | Description |
|--------|----------|-------------|
| Jump buffer | 5 frames | If jump pressed within 5 frames before landing, jump executes on landing |
| Dash buffer | 4 frames | If dash pressed within 4 frames of available dash, executes when possible |
| Grab buffer | 0 frames | Immediate; hold to grab walls |
| Coyote time | 6 frames | Can jump within 6 frames after walking off a ledge |

### Walking / Running

| Parameter | Value |
|-----------|-------|
| Max run speed | 90 px/sec (1.5 px/frame) |
| Run acceleration | 1000 px/sec² (0.278 px/frame²) |
| Run deceleration (friction) | 400 px/sec² (ground), 200 px/sec² (air) |
| Turn multiplier | 1.6x (acceleration multiplied when changing direction) |
| Ducking speed | 30 px/sec (0.5 px/frame) while holding down |

### Jumping

| Parameter | Value |
|-----------|-------|
| Jump velocity | -105 px/sec (-1.75 px/frame upward) |
| Short hop (release early) | Vertical velocity halved when button released and ascending |
| Gravity (normal) | 900 px/sec² (0.25 px/frame²) |
| Gravity (holding jump, ascending) | 450 px/sec² (half normal) |
| Max fall speed | 160 px/sec (2.67 px/frame) |
| Fast fall speed (holding down) | 240 px/sec (4.0 px/frame) |
| Wall jump horizontal velocity | 130 px/sec (2.17 px/frame) away from wall |
| Wall jump vertical velocity | -105 px/sec (same as ground jump) |
| Wall slide speed | 40 px/sec (0.67 px/frame) downward |
| Wall slide gravity | 450 px/sec² |

### Dashing

| Parameter | Value |
|-----------|-------|
| Dash speed | 240 px/sec (4.0 px/frame) |
| Dash duration | 15 frames (0.25 seconds) |
| Dash freeze frames | 4 frames (time freezes briefly at dash start) |
| Dash cooldown | 0 frames (but must land/touch ground to regain dash) |
| Dash directions | 8-directional (cardinal + diagonal) |
| Diagonal dash speed | Same magnitude (240 px/sec total, ~170 px/sec per axis) |
| Dashes available | 1 (default). Regained on landing or touching refill crystal. 2 dashes in Chapter 8. |
| Post-dash speed retention | After dash ends, retain 70% of dash speed if holding direction |
| Updash end velocity | Vertical velocity set to -60 px/sec after upward dash ends |

### Dash States

```
1. Dash Start (Frame 0): Freeze frame. Direction locked. Trail effect begins.
2. Freeze (Frames 0-3): Game time paused for player. Other entities may or may not freeze depending on type.
3. Dash Active (Frames 4-18): Player moves at dash speed in locked direction.
   - No gravity applied during dash.
   - Player can cancel into wall grab.
   - Player can cancel into jump (super/hyper jumps).
4. Dash End (Frame 19): Speed retained partially.
   - Gravity resumes.
   - Hair color changes from white (dashing) back to red (if no dash available) or blue (dash available).
```

### Climbing / Grabbing

| Parameter | Value |
|-----------|-------|
| Climb speed (up) | 45 px/sec (0.75 px/frame) |
| Climb speed (down) | 80 px/sec (1.33 px/frame) |
| Stamina (max) | 110 units |
| Stamina drain (holding still) | 10 units/sec |
| Stamina drain (climbing up) | 45.36 units/sec |
| Stamina drain (climbing down) | 0 units/sec |
| Wall jump stamina cost | 27.5 units |
| Climb jump stamina cost | 27.5 units |
| Stamina recovery | Full refill on touching ground |
| Stamina warning | At 20 units, Madeline sweats (particle effect) and flashes red |
| Stamina exhaustion | At 0, Madeline loses grip and falls. Cannot grab again for 20 frames. |

### Advanced Techniques (Intended by Designers)

#### Wavedash
- Dash diagonally downward while on ground.
- Immediately jump at end of dash.
- Result: Long, fast horizontal jump preserving dash momentum.
- Speed: ~200 px/sec horizontal.

#### Hyper Dash
- Dash horizontally on ground.
- Jump during dash.
- Result: Long horizontal jump with boosted speed.
- Speed: ~180 px/sec horizontal + full jump height.

#### Super Jump
- Dash horizontally.
- Jump at end of dash.
- Retain vertical velocity bonus.
- Speed: ~160 px/sec horizontal.

#### Wall Bounce
- Wall jump + immediately dash diagonally up-away from wall.
- Result: Maximum height gain.

#### Corner Correction
- If Madeline's head clips a corner by up to **4 pixels**, she is pushed horizontally to clear it.
- Enables smoother platforming near tight openings.

---

## 4. Player Character — Madeline

### Visual Design

- **Sprite size**: 16 x 16 pixels (standing), additional frames for crouching (16x12).
- **Hair**: 5 trailing nodes that follow Madeline's head with spring physics.
  - Each node trails the previous with a delay of 3 frames.
  - Hair color indicates dash state:
    - **Red**: No dash available (used, not recovered).
    - **Blue**: Dash available (normal state).
    - **White**: Currently dashing.
    - **Pink**: Two dashes available (Chapter 8).
  - Node distance: 3 pixels between each node.
- **Animation frames**:
  - Idle: 1 frame (+ hair animation)
  - Run: 12 frames, 5 FPS
  - Jump/fall: 1 frame (different for ascending/descending)
  - Dash: 1 frame with trail effect
  - Climb: 4 frames, 8 FPS
  - Wall slide: 1 frame
  - Death: Burst into particles (no frame, particle effect)
  - Respawn: Emerge from bubble, 12 frames at 12 FPS

### Hitbox

| State | Size (pixels) | Offset from sprite center |
|-------|--------------|---------------------------|
| Standing/Running | 8 x 11 | Center-bottom aligned |
| Crouching | 8 x 6 | Center-bottom |
| Climbing | 8 x 11 | Shifted toward wall by 2px |
| Dashing | 8 x 11 | Same as standing |

### Death & Respawn

- **Death trigger**: Any frame where Madeline's hitbox overlaps a hazard hitbox.
- **Death effect**: Madeline bursts into colored particles (hair color). Screen freezes for 6 frames. Screen flashes white for 2 frames.
- **Respawn**: Screen wipes/fades (10 frames). Madeline appears at room's spawn point inside a bubble that pops (15 frames). Player regains control.
- **Total death-to-control time**: ~0.5 seconds (31 frames).
- **Death counter**: Incremented per death. Displayed on chapter complete screen. No gameplay penalty.

---

## 5. Hazards & Objects

### Spikes

| Spike Type | Hitbox | Placement |
|-----------|--------|-----------|
| Up-facing | 8 x 3, bottom of tile | Floor spikes |
| Down-facing | 8 x 3, top of tile | Ceiling spikes |
| Left-facing | 3 x 8, left of tile | Right-wall spikes |
| Right-facing | 3 x 8, right of tile | Left-wall spikes |

- Instant kill on contact with Madeline's hitbox.
- Can be placed on any solid surface.
- Spikes on moving platforms move with the platform.

### Moving Platforms

| Type | Behavior |
|------|----------|
| Static platform | Solid block, does not move |
| Moving platform (linear) | Moves between 2 points. Speed: 60 px/sec. Pauses 30 frames at each end. |
| Moving platform (triggered) | Stationary until Madeline stands on it. Then moves in set direction. Speed: 90 px/sec. |
| Crumbling platform | Madeline stands on it → shakes for 20 frames → falls. Respawns after 120 frames. |
| Cloud platform | Moves slowly in one direction (30 px/sec). Madeline can stand on top. One-way (jump through from below). |
| Zipper | Moves in dash direction when Madeline dashes while touching. Speed: 180 px/sec. Stops at wall. Respawns after 120 frames. |

### Springs

| Type | Effect |
|------|--------|
| Spring (up) | Launches Madeline upward. Velocity: -180 px/sec. Refills dash. |
| Spring (side) | Launches Madeline horizontally. Velocity: 180 px/sec. Refills dash. |
| Spring (down) | Pushes Madeline down. Velocity: 180 px/sec. Used in specific puzzles. |
| Super spring | Launches with extra force: -240 px/sec. |

### Dash Refill Crystal

- Small floating crystal (8x8 sprite, animated wobble).
- Touching it refills Madeline's dash (returns to 1 available dash).
- After collection, turns grey and respawns after 150 frames (2.5 seconds).
- Hitbox: 12 x 12 pixels (slightly larger than sprite for generous collection).
- In some chapters, **double refill crystals** (green) give 2 dashes.

### Bubbles

- Floating bubbles that Madeline can enter.
- Inside bubble: Madeline moves in all 8 directions at 90 px/sec.
- Dash inside bubble = launch out of bubble in dash direction at dash speed. Bubble pops.
- Bubble duration: 5 seconds (300 frames) before auto-pop.
- After pop: Madeline retains dash speed momentum. Dash refilled.

### Dream Blocks (Chapter 2)

- Translucent jelly-like blocks.
- Madeline dashes into them to enter "dream state."
- Inside dream block: Madeline floats through the block in dash direction.
- Speed inside: Same as dash speed (240 px/sec).
- Exits when reaching block edge.
- Dash is refilled upon entering a dream block.
- Can chain through multiple dream blocks.

### Feathers (Chapter 2)

- Collectible that allows free flight for a limited time.
- Duration: 4 seconds (240 frames).
- Flight speed: 90 px/sec in all directions (analog control).
- Madeline turns golden during flight.
- Stamina-like meter depletes; not using analog stick slows depletion.
- At end: Madeline retains one dash.

### Kevin Blocks (Chapter 5)

- Large blocks with a face (red or blue).
- Activated when Madeline dashes toward them.
- Move in the dash direction at 240 px/sec until hitting a wall.
- After stopping: Pause 90 frames, then return to original position over 180 frames.
- Can carry Madeline (if standing on top).
- Red Kevins: Move in direction Madeline is facing.
- Blue Kevins: Move in direction Madeline dashes.

### Seekers (Chapter 5)

- Dark starfish-like enemies.
- Move toward Madeline at 60 px/sec when she's within 8 tiles.
- Contact = death.
- Can be destroyed by dashing through them.
- Respawn after 300 frames.
- Destroyed seekers leave a dash refill.

### Oshiro Ghosts (Chapter 3)

- Chase Madeline at increasing speed during chase sequences.
- Contact = death.
- Cannot be destroyed.
- Speed: Starts at 60 px/sec, increases by 10 px/sec every 5 seconds.
- Triggered at specific room boundaries.

### Badeline Orbs (Chapter 6)

- Badeline appears at fixed positions.
- Launches a seeking projectile at Madeline.
- Projectile speed: 90 px/sec, homing.
- Projectile lifetime: 10 seconds.
- On hit: Death.
- Can be dodged; destroyed by touching refill crystal or leaving room.

### Dust Bunnies (Chapter 3)

- Dark creatures that move along walls.
- Contact = death.
- Pattern: Fixed paths on walls/ceilings. Speed: 60 px/sec.
- Cannot be destroyed.

### Wind (Chapter 4)

| Wind Type | Speed | Effect |
|-----------|-------|--------|
| Wind Left | 40 px/sec | Pushes Madeline left |
| Wind Right | 40 px/sec | Pushes Madeline right |
| Wind Up | 40 px/sec | Pushes Madeline up, slows falling |
| Wind Down | 40 px/sec | Pushes Madeline down, accelerates falling |
| Snowstorm (strong) | 80 px/sec | Double push force |

### Bumpers (Chapter 4)

- Circular bouncing objects (16x16 sprite).
- On contact: Madeline is launched away from bumper center.
- Launch speed: 180 px/sec.
- Dash is refilled.
- Hitbox: Circular, radius 8 pixels.

### Swap Blocks (Chapter 6)

- Two-state blocks (red/blue).
- Dashing swaps which color is solid.
- Red solid = Blue passable, and vice versa.
- State is toggled every time Madeline dashes.

### Lava / Rising Lava (Chapter 9 / Core)

- Slowly rising from bottom of room.
- Speed: 20-40 px/sec (varies by room).
- Contact = death.
- Ice variant: Can toggle between fire (rising from bottom) and ice (falling from top).

---

## 6. Chapter Progression

### Main Chapters

| Chapter | Name | Rooms (approx) | New Mechanic | Theme | Target Time |
|---------|------|-----------------|-------------|-------|-------------|
| Prologue | Forsaken City (intro) | 5 | Basic movement | City ruins | 2 min |
| 1 | Forsaken City | 31 | Dash, climb | City ruins, twilight | 10 min |
| 2 | Old Site | 40 | Dream blocks, feather | Hotel ruins, darkness | 15 min |
| 3 | Celestial Resort | 38 | Dust bunnies, moving platforms | Haunted hotel | 20 min |
| 4 | Golden Ridge | 29 | Wind, clouds, bumpers | Mountain ridge, snow | 15 min |
| 5 | Mirror Temple | 32 | Seekers, Kevin blocks | Dark temple | 20 min |
| 6 | Reflection | 34 | Badeline orbs, feather | Underwater/mirror world | 20 min |
| 7 | The Summit | 46 | All mechanics combined | Peak of mountain, ice/snow | 25 min |
| 8 (Epilogue) | Core | 22 | Fire/ice toggle, lava | Volcanic core, hot/cold | 15 min |

### Chapter Structure

Each chapter consists of:
1. **Checkpoint rooms**: Main progression path. Each room is a self-contained puzzle.
2. **Secret rooms**: Hidden paths leading to strawberries or crystal hearts.
3. **Boss/chase sequences**: Scripted sections with auto-scrolling or pursuing enemies.
4. **Cutscene triggers**: Dialog and story moments at specific rooms.

### Chapter Unlock

| Chapter | Requirement |
|---------|------------|
| 1 | Start of game |
| 2 | Complete Chapter 1 |
| 3 | Complete Chapter 2 |
| 4 | Complete Chapter 3 |
| 5 | Complete Chapter 4 |
| 6 | Complete Chapter 5 |
| 7 | Complete Chapter 6 |
| 8 | Collect 4+ Crystal Hearts (from B-sides/secrets) |
| B-sides | Find B-side cassette tape in each chapter's A-side |
| C-sides | Complete all B-sides |

---

## 7. All Chapters — Key Room Designs

### Chapter 1: Forsaken City

**Theme**: Crumbling urban environment. Twilight/dusk palette.

**Room 1-1 (Tutorial: Movement)**
```
████████████████████████████████████████
█                                      █
█                                      █
█  M-->                         [EXIT] █
█  ████   ████   ████   ██████████████ █
█                                      █
████████████████████████████████████████
M = Madeline spawn. Arrow = direction to go.
Flat ground with small gaps to jump over.
```

**Room 1-5 (Tutorial: Dash)**
```
████████████████████████████████████████
█                           ████       █
█                           █  █       █
█  M                  ▲▲▲▲  █  █ [EXIT]█
█  ████               ████  █  █████████
█                                      █
████████████████████████████████████████
▲ = spikes. Must dash right over spikes to reach exit.
```

**Room 1-15 (Vertical climb)**
```
████                    ████
█  █                    █  █
█  █  ■                 █  █  <- Crumbling platforms
█  █  ■  ◇             █  █  <- ◇ = dash refill crystal
█  █     █████          █  █
█  █              ■     █  █
█  █              ■     █  █
█  ████████████████     █  █
█  M                    █  █
████████████████████████████
```

### Chapter 2: Old Site (Dream Blocks)

**Key mechanic introduction**: Dream blocks (turquoise jelly).

Room structure alternates between normal platforming and dream-block sequences requiring dashes into/through dream blocks to cross large gaps.

**Dream block chain example**:
```
█████████████████████████████████████
█                                   █
█  M        [DB1]    [DB2]    EXIT  █
█  ████                        ████ █
█       ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲       █
█████████████████████████████████████
DB = Dream Block (4x4 tiles).
Dash into DB1, float through, exit into DB2, float to exit.
```

### Chapter 3: Celestial Resort

**Chase sequence rooms**: Mr. Oshiro ghost chases Madeline. Auto-advancing camera.
- Camera moves right at 90 px/sec.
- Madeline must keep ahead of camera boundary (left edge = death).
- Rooms are long horizontal runs (80+ tiles wide).

### Chapter 5: Mirror Temple

**Seeker puzzle rooms**: Navigate past seekers in dark rooms.
- Seekers illuminate small radius (4 tiles) of darkness.
- Some rooms are completely dark except for seeker glow.
- Key: Dash through seekers to destroy them and create path.

### Chapter 7: The Summit

**Multi-section vertical climb**:
- 3000m of vertical climbing (approximately 200 tile-heights).
- Altitude counter displayed (0m to 3000m).
- Checkpoint flags every ~100m.
- Wind sections, moving platforms, crumbling blocks, and all previous mechanics.

**Flag checkpoint rooms** (every ~5 rooms): Touch flag to set respawn. Small celebrations (confetti particles).

---

## 8. Collectibles

### Strawberries

| Type | Count | Effect |
|------|-------|--------|
| Red Strawberry | 175 total across A-sides | Cosmetic. Counted per chapter. |
| Winged Strawberry | 4 total | Must reach without dashing. Flies away if dash is used. |
| Golden Strawberry | 8 (+1 per chapter) | Earned by deathless chapter runs. Ultra-hard. |
| Moon Berry | 1 | Chapter 9 (Farewell). Extremely hidden. |

**Strawberry collection**: Touch the strawberry, then land on solid ground. If you die before landing, strawberry is NOT collected (returns to position).

**Strawberry positions**: Usually in off-path rooms requiring optional challenging platforming to reach. Each berry has an invisible "seed" that makes it visible; entering the room triggers it.

### Crystal Hearts

| Location | Requirement |
|----------|-------------|
| Chapter 1 | Hidden room: Dash in specific pattern revealed by poem on sign |
| Chapter 2 | Hidden room: Complete falling block puzzle |
| Chapter 3 | Hidden room: Find behind bookshelf |
| Chapter 4 | Hidden room: Wind puzzle sequence |
| Chapter 5 | Hidden room: Mirror puzzle (match real and reflected Madeline positions) |
| Chapter 6 | Hidden room: Complete without touching ground |
| Chapter 7 | Hidden room: Reach secret area at summit |
| Chapter 8 | Complete the chapter |
| B-side Hearts | Complete each B-side chapter (8 total) |
| C-side Hearts | Complete each C-side chapter (8 total) |

### B-Side Cassette Tapes

- Hidden in each A-side chapter.
- Floating cassette with music notes animation.
- Must be reached via hidden path or difficult platforming.
- Collection unlocks B-side variant of that chapter.

---

## 9. B-Side & C-Side Chapters

### B-Sides

| Chapter B-Side | Rooms | Difficulty | New Twists |
|----------------|-------|------------|------------|
| 1B | 20 | Hard | Complex dash chains, tight spike gaps |
| 2B | 22 | Hard | Dream block mazes, feather precision |
| 3B | 18 | Hard | Timed platform sequences |
| 4B | 15 | Very Hard | Wind + precision climbing |
| 5B | 20 | Very Hard | Multi-seeker rooms |
| 6B | 18 | Very Hard | Badeline + swap block combos |
| 7B | 25 | Extreme | Everything combined at extreme difficulty |
| 8B | 12 | Extreme | Fire/ice rapid switching |

B-sides feature remixed music (more intense versions of A-side tracks).

### C-Sides

- 3 rooms each (extremely short but brutally difficult).
- Each room is a single, incredibly precise challenge.
- Must complete all B-sides to unlock.
- C-side rooms require pixel-perfect execution and advanced technique mastery.

---

## 10. UI Layout & Screens

### In-Game HUD

```
+------------------------------------------------------------------+
| [Strawberry count: X/Y]                          [Timer: MM:SS]  |
|                                                                   |
|                                                                   |
|                     (GAMEPLAY - 320x180)                          |
|                                                                   |
|                                                                   |
|                                                   [Deaths: NNN]  |
+------------------------------------------------------------------+
```

HUD elements are minimal and semi-transparent:
- **Strawberry counter**: Top-left. Shows "X" collected. Fades to 0 opacity after 3 seconds of no collection.
- **Timer**: Top-right (if speedrun timer enabled). MM:SS.mmm format.
- **Death counter**: Bottom-right (appears briefly on death, otherwise hidden).

### Title Screen

```
+----------------------------------+
|                                  |
|        [Mountain artwork]        |
|                                  |
|          CELESTE                 |
|                                  |
|      [Madeline climbing art]    |
|                                  |
|        PRESS ANY BUTTON          |
|                                  |
|   © 2018 Extremely OK Games     |
+----------------------------------+
```

### Chapter Select (Overworld Map)

```
+--------------------------------------------------+
|  Mountain map with path/nodes                     |
|                                                    |
|  [1]----[2]----[3]----[4]                         |
|                  \                                  |
|                  [5]----[6]----[7]                 |
|                                  \                 |
|                                  [8]               |
|                                                    |
|  Chapter 3: Celestial Resort                       |
|  Strawberries: 15/25  Deaths: 342  Time: 1:23:45 |
|  [A-Side] [B-Side] [C-Side]                       |
+--------------------------------------------------+
```

### Pause Menu

```
+----------------------------------+
|         PAUSED                   |
|                                  |
|    > Resume                      |
|      Restart Chapter             |
|      Variants (B/C-sides)       |
|      Options                     |
|      Save & Quit                 |
|                                  |
+----------------------------------+
```

### Chapter Complete Screen

```
+------------------------------------------+
|    CHAPTER 3 COMPLETE                     |
|    Celestial Resort                       |
|                                           |
|    Strawberries:  15 / 25                 |
|    Deaths:        342                      |
|    Time:          00:23:45                |
|                                           |
|    [Strawberry images in a grid]          |
|                                           |
|    Total Strawberries: 45 / 175           |
|                                           |
|    PRESS CONFIRM TO CONTINUE              |
+------------------------------------------+
```

---

## 11. Audio Design

### Music Tracks

| Track | Chapter/Context | Composer | BPM | Style |
|-------|----------------|----------|-----|-------|
| "First Steps" | Chapter 1 (A-side) | Lena Raine | 140 | Atmospheric electronic, piano |
| "Resurrections" | Chapter 2 (A-side) | Lena Raine | 120 | Ambient, ethereal |
| "Checking In" | Chapter 3 (A-side) | Lena Raine | 130 | Spooky, building tension |
| "Golden Ridge" | Chapter 4 (A-side) | Lena Raine | 110 | Orchestral, windy |
| "Mirror Magic" | Chapter 5 (A-side) | Lena Raine | 100 | Dark, mysterious |
| "Reflection" | Chapter 6 (A-side) | Lena Raine | 90 | Emotional, piano-driven |
| "Reach for the Summit" | Chapter 7 (A-side) | Lena Raine | 160 | Epic, driving, climactic |
| "Heart of the Mountain" | Chapter 8 (A-side) | Lena Raine | 140 | Intense, dual-nature |
| "Prologue" | Prologue/Title | Lena Raine | 100 | Gentle, inviting |
| "Awake" | Overworld Map | Lena Raine | 90 | Calm, contemplative |
| "In the Mirror" | Chapter 2 (B-side) | Lena Raine | 140 | Intense remix |

Each chapter has A-side and B-side music variants. B-side tracks are more intense/electronic remixes.

### Sound Effects

| Sound | Trigger | Description |
|-------|---------|-------------|
| Jump | Leave ground via jump | Soft "woosh" with pitch variation |
| Land | Touch ground | Light impact thud |
| Dash | Dash initiated | Sharp whoosh, stereo panned in dash direction |
| Dash refill | Touch crystal | Bright chime, ascending |
| Wall grab | Grab wall | Soft grip sound |
| Climb | Moving on wall | Quiet scraping per 8 pixels |
| Stamina warning | Stamina < 20 | Rapid heartbeat-like pulses |
| Stamina out | Stamina = 0 | Exhaustion breath |
| Death | Die | Soft pop/burst (deliberately non-harsh) |
| Respawn | Reappear | Bubble pop + sparkle |
| Strawberry collect | Land with strawberry | Musical jingle (ascending notes, unique per berry count) |
| Strawberry float | Touch strawberry | High-pitched chime |
| Crystal heart | Collect crystal heart | Long, beautiful chime sequence (3 seconds) |
| Cassette collect | Touch B-side tape | Music note jingle |
| Spring | Hit spring | Boing/spring sound |
| Crumble | Step on crumbling platform | Cracking/crumbling |
| Dream enter | Enter dream block | Underwater/dreamy whoosh |
| Dream exit | Exit dream block | Pop back to reality |
| Feather collect | Touch feather | Angelic chime |
| Wind | In wind zone | Sustained wind ambiance |
| Bumper | Hit bumper | Bouncy pop |
| Kevin activate | Kevin block starts moving | Heavy grinding |
| Seeker death | Dash through seeker | Dark burst |
| Checkpoint flag | Touch flag | Flapping cloth + chime |

---

## 12. Visual Effects

### Hair Physics

Madeline's hair consists of 5 trailing nodes:
```
Node 0 (head): Position = Madeline's head position
Node 1: Follows Node 0 with spring constant k=0.3, damping=0.8, distance=3px
Node 2: Follows Node 1, same parameters
Node 3: Follows Node 2
Node 4: Follows Node 3 (tail end)
```

Hair rendered as circles: Node 0 = 5px radius, decreasing to Node 4 = 2px radius.

### Particle Systems

| Effect | Trigger | Particles | Duration | Description |
|--------|---------|-----------|----------|-------------|
| Death burst | Death | 12 | 30 frames | Colored particles (hair color) fly outward |
| Dash trail | During dash | Continuous | Dash duration | Afterimages of Madeline, fading over 10 frames |
| Landing dust | Landing | 4 | 15 frames | Small dust clouds at feet |
| Wall dust | Wall grab/slide | 2/frame | Continuous | Dust from wall contact |
| Strawberry sparkle | Near strawberry | 6 | Continuous | Twinkling stars around berry |
| Feather glow | During flight | 8/frame | Flight duration | Golden particles trailing |
| Checkpoint confetti | Flag touch | 20 | 60 frames | Colored confetti explosion |
| Summit snow | Chapter 7 | Continuous | Level duration | Snow particles, wind-affected |

### Screen Shake

| Trigger | Intensity (pixels) | Duration (frames) |
|---------|--------------------|--------------------|
| Death | 2 | 6 |
| Boss attack | 3 | 10 |
| Kevin block impact | 4 | 8 |
| Ground pound/landing | 1 | 4 |
| Explosion | 5 | 12 |

### Camera System

- Camera follows Madeline with a dead zone of 16x16 pixels.
- Camera snaps to room boundaries (no camera past room edges).
- Smooth lerp to new position: `camera += (target - camera) * 0.15` per frame.
- During room transitions: Camera pans smoothly over 15 frames.
- Look-ahead: Camera leads Madeline slightly in movement direction (8 pixels).

---

## 13. Assist Mode

Accessible from options menu. Provides adjustable difficulty modifiers:

| Setting | Options | Default |
|---------|---------|---------|
| Game Speed | 50%, 60%, 70%, 80%, 90%, 100% | 100% |
| Invincible | On/Off | Off |
| Infinite Stamina | On/Off | Off |
| Infinite Dashes | On/Off | Off |
| Dash Assist | On/Off (auto-completes dash direction) | Off |

When Assist Mode is active:
- A small icon appears on HUD.
- Strawberries collected are marked with assist mode indicator.
- No restrictions on progression; all content accessible.
- Can be toggled at any time during gameplay from pause menu.

---

## Appendix A: Timing Constants

| Constant | Value | Notes |
|----------|-------|-------|
| Frames per second | 60 | |
| Input buffer (jump) | 5 frames | 83ms |
| Input buffer (dash) | 4 frames | 67ms |
| Coyote time | 6 frames | 100ms |
| Dash freeze frames | 4 frames | 67ms |
| Dash active frames | 11 frames | 183ms |
| Total dash duration | 15 frames | 250ms |
| Crumble platform warn | 20 frames | 333ms |
| Crumble platform respawn | 120 frames | 2 seconds |
| Dash refill respawn | 150 frames | 2.5 seconds |
| Death-to-control | 31 frames | ~517ms |
| Room transition camera | 15 frames | 250ms |
| Seeker respawn | 300 frames | 5 seconds |
| Kevin block return delay | 90 frames | 1.5 seconds |
| Kevin block return time | 180 frames | 3 seconds |
| Bubble duration | 300 frames | 5 seconds |
| Feather duration | 240 frames | 4 seconds |
| Stamina drain (hold) | 10/sec | Takes 11 seconds to empty |
| Stamina drain (climb up) | 45.36/sec | Takes ~2.4 seconds to empty |
| Strawberry sparkle range | 32 pixels | Distance to trigger sparkle |

## Appendix B: Speedrun Mechanics

The game includes a built-in speedrun timer:
- Starts when entering Chapter 1.
- Pauses during menus and cutscenes.
- Displayed as MM:SS.mmm in top-right.
- Per-chapter splits shown on chapter complete screen.
- Total time shown on file select.
- Timer can be enabled/disabled in options.

Key speedrun strats the physics support:
- **Demodash**: Dash into a corner at the exact frame to clip through 1-tile gaps.
- **Extended super/hyper**: Chain wavedashes for sustained speed.
- **Neutral jump**: Jump without direction input to gain height with minimal horizontal movement.
- All advanced techniques are intentional design — the physics engine supports them without bugs.
