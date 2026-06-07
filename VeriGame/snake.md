# Snake (Nokia 6110) — Complete Game Specification

> A comprehensive specification for faithfully recreating the original Snake game, first released on the Nokia 6110 in 1997/1998, programmed by Taneli Armanto. This document covers every system, mechanic, and interaction required for a faithful clone of the classic Nokia Snake I experience.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Grid System](#3-grid-system)
4. [Core Mechanics — Movement](#4-core-mechanics--movement)
5. [Core Mechanics — Growth & Collision](#5-core-mechanics--growth--collision)
6. [Food System](#6-food-system)
7. [Speed & Difficulty Progression](#7-speed--difficulty-progression)
8. [Scoring System](#8-scoring-system)
9. [Game States](#9-game-states)
10. [Controls & Input Handling](#10-controls--input-handling)
11. [UI Layout](#11-ui-layout)
12. [Audio Design](#12-audio-design)
13. [Technical Requirements](#13-technical-requirements)
14. [QA Acceptance Matrix](#14-qa-acceptance-matrix)

---

## 1. Game Overview

- **Title**: Snake (also known as Snake I)
- **Original Platform**: Nokia 6110 (released December 1997, game included from early 1998)
- **Developer**: Taneli Armanto (Nokia, Helsinki)
- **Genre**: Arcade / Casual
- **Perspective**: 2D top-down, single-screen, static camera
- **Input**: 4-directional discrete (numpad keys 2/4/6/8 on original; arrow keys or WASD in modern recreation)
- **Objective**: Guide a continuously moving snake to eat food pellets, growing longer with each pellet consumed, while avoiding collision with walls and the snake's own body.
- **Lose Condition**: The snake's head collides with a wall boundary or any segment of its own body.
- **Win Condition**: The snake fills the entire grid (all 300 cells occupied). This is the theoretical maximum; in practice, the game is an endless high-score chase.
- **Target Session Length**: 1--10 minutes (varies by skill and speed setting)
- **Historical Note**: Snake was one of three games bundled with the Nokia 6110 (alongside Memory and Logic). It was shipped on over 400 million Nokia devices between 1997 and 2007, making it one of the most widely distributed games in history. The graphics were directly programmed in machine code due to extreme memory constraints (the entire phone OS fit in approximately 1 MB).

---

## 2. Technical Foundation

### Original Hardware Reference

| Property | Value |
|----------|-------|
| Phone model | Nokia 6110 |
| Display type | Monochrome LCD |
| Display resolution | 84 x 48 pixels |
| Display colors | 2 (black pixels on greenish-gray background) |
| Audio hardware | Piezo buzzer (single-channel, square wave) |
| Input device | Physical 12-key numpad |
| CPU | Texas Instruments MAD2WD1 (ARM-based) |
| Total system memory | ~1 MB (shared with phone OS) |

### Recreation Target Specifications

| Property | Value |
|----------|-------|
| Logical resolution (game area) | 320 x 240 pixels (recommended minimum) |
| Render style | Pixel-perfect monochrome or Nokia LCD-green palette |
| LCD foreground color | `#43523D` (dark olive / Nokia pixel ON) |
| LCD background color | `#C7D6A3` (pale green-gray / Nokia pixel OFF) |
| Frame rate target | 60 FPS (rendering); game logic runs on a separate tick timer |
| Game loop architecture | Fixed-timestep logic tick decoupled from render |
| Determinism | All game logic must be deterministic given the same seed and input sequence |

### Color Palette (Nokia LCD Faithful)

| Element | Color (Hex) | Description |
|---------|-------------|-------------|
| Background | `#C7D6A3` | LCD inactive pixel, pale green-gray |
| Foreground (snake, walls, food, text) | `#43523D` | LCD active pixel, dark olive |
| Optional: pixel shadow | `#9EAD86` | Slight sub-pixel ghosting effect for authenticity |

### Game Loop (Per Tick)

```
1. Read input buffer; resolve queued direction change
2. Move snake head one cell in current direction
3. Check head collision with walls
4. Check head collision with snake body
5. If collision -> trigger Game Over state
6. Check head collision with food
7. If food eaten -> increment score, grow snake, spawn new food, play eat sound
8. If no food eaten -> remove tail segment (snake moves forward without growing)
9. Update display
10. Check win condition (snake length == grid total cells)
```

---

## 3. Grid System

### Grid Dimensions

| Property | Value |
|----------|-------|
| Grid width (columns) | 20 |
| Grid height (rows) | 15 |
| Total cells | 300 |
| Cell size (original hardware) | ~4 x 3 pixels (non-square due to 84x48 resolution) |
| Cell size (recreation, recommended) | 16 x 16 pixels (square cells for modern displays) |
| Playfield pixel size (at 16px cells) | 320 x 240 pixels |

### Coordinate System

- **Origin**: Top-left corner of the playfield is (0, 0).
- **X-axis**: Increases rightward, range [0, 19].
- **Y-axis**: Increases downward, range [0, 14].
- **Cell addressing**: Each cell is identified by integer coordinates (x, y).
- **No sub-cell positions**: All positions are discrete integer grid coordinates.

### Boundary Model

| Property | Value |
|----------|-------|
| Boundary type | Solid walls (Snake I) |
| Wall collision | Fatal — immediately triggers Game Over |
| Wrapping / toroidal | **Not present** in Snake I (introduced in Snake II, Nokia 3310, 2000) |

The playfield is fully enclosed. The valid movement area is columns 0--19 and rows 0--14. Any head position at x < 0, x > 19, y < 0, or y > 14 constitutes a wall collision.

### Grid Rendering

- **Walls**: Drawn as a 1-cell-thick border around the playfield. In the original, the border was implicit (screen edge). In a recreation, draw a visible border rectangle.
- **Snake body**: Each occupied cell is rendered as a filled square.
- **Food**: Rendered as a filled square in the same foreground color, but smaller or with a distinct pattern (e.g., a single centered dot or a 2x2 pixel dot within the cell) to distinguish it from the snake body.
- **Empty cells**: Rendered in the background color.

---

## 4. Core Mechanics — Movement

### Discrete Grid Movement

The snake moves exactly **one cell per game tick**. There is no sub-cell interpolation, acceleration, or deceleration. The snake advances in its current direction by one grid unit each tick.

| Property | Value |
|----------|-------|
| Movement type | Discrete, grid-aligned |
| Movement unit | 1 cell per tick |
| Movement directions | 4 cardinal: UP, DOWN, LEFT, RIGHT |
| Diagonal movement | Not allowed |
| Stopping | Not allowed — the snake is always moving |
| Reversal | Not allowed — the snake cannot turn 180 degrees |

### Direction State

The snake has a **current direction** that persists between ticks. Valid direction changes are 90-degree turns only:

| Current Direction | Valid Next Directions | Invalid (Reversal) |
|-------------------|----------------------|---------------------|
| UP | LEFT, RIGHT | DOWN |
| DOWN | LEFT, RIGHT | UP |
| LEFT | UP, DOWN | RIGHT |
| RIGHT | UP, DOWN | LEFT |

If the player inputs the current direction again (e.g., pressing RIGHT while already moving RIGHT), the input is accepted but has no effect. If the player inputs the reverse direction, it is **silently ignored**.

### Head Movement Algorithm

Each tick:
1. Read the next direction from the input queue (if any valid input is buffered).
2. Compute the new head position: `new_head = current_head + direction_vector`.
3. Direction vectors:
   - UP: (0, -1)
   - DOWN: (0, +1)
   - LEFT: (-1, 0)
   - RIGHT: (+1, 0)

### Body Movement

The snake body is stored as an **ordered list of cell coordinates**, with the head at index 0 and the tail at the last index.

Each tick (when not growing):
1. Prepend the new head position to the front of the list.
2. Remove the last element (tail) from the list.

When growing (food was eaten on this tick):
1. Prepend the new head position to the front of the list.
2. **Do not** remove the tail — the snake is now one cell longer.

### Starting Position and Direction

| Property | Value |
|----------|-------|
| Starting length | 3 segments |
| Starting head position | Approximately center of grid: (10, 7) |
| Starting body layout | Horizontal, extending left from head: head at (10, 7), body at (9, 7), tail at (8, 7) |
| Starting direction | RIGHT (+1, 0) |

The snake begins in the center of the 20x15 grid, facing right, with a length of 3 cells laid out horizontally.

### Grace Period (Armanto's Leniency Feature)

Taneli Armanto implemented a subtle grace mechanic: the game provides **a few extra milliseconds of input acceptance right before a fatal collision**, during which the player can still change direction. This prevents frustrating deaths where the player reacted in time but the input was processed too late.

| Property | Value |
|----------|-------|
| Grace window | ~50 ms before collision would resolve |
| Behavior | If a valid direction change is received during the grace window, process it before evaluating the collision |
| Scope | Applies to both wall and self-collision |

Implementation: Before evaluating collision on a new head position, check if a buffered input would redirect the snake to a non-fatal position. If so, apply the direction change first.

---

## 5. Core Mechanics — Growth & Collision

### Growth Mechanics

| Property | Value |
|----------|-------|
| Growth per food pellet | 1 segment |
| Growth timing | Immediate — on the tick the food is eaten |
| Growth method | Tail retention (skip tail removal for one tick) |
| Maximum snake length | 300 segments (entire grid) |

When the snake eats food:
1. The new head position is prepended to the body list.
2. The tail is **not** removed this tick.
3. Net effect: snake length increases by 1.

### Collision Detection

Collision is checked **after** the new head position is computed but **before** the display is updated.

#### Wall Collision

```
if new_head.x < 0 OR new_head.x >= 20 OR new_head.y < 0 OR new_head.y >= 15:
    trigger GAME_OVER (reason: "wall")
```

#### Self-Collision

```
if new_head position exists in current snake body list (excluding the tail*):
    trigger GAME_OVER (reason: "self")
```

*Note on tail exclusion: On a non-growth tick, the tail will be removed after the head moves. Therefore, the cell currently occupied by the tail tip will be vacated. The collision check should account for this: if the snake is not growing, the tail position is safe. If the snake **is** growing (just ate food), the tail is not removed, so the tail position **is** checked for collision.

#### Collision Priority

| Priority | Check | Result |
|----------|-------|--------|
| 1 | Wall boundary check | Game Over (wall) |
| 2 | Self-body overlap check | Game Over (self) |
| 3 | Food overlap check | Eat food, grow, spawn new food |
| 4 | No collision | Normal movement (remove tail) |

---

## 6. Food System

### Food Properties

| Property | Value |
|----------|-------|
| Food items on screen | Exactly 1 at all times |
| Food appearance | Single filled cell (same foreground color as snake) |
| Food size | 1 cell |
| Food persistence | Remains until eaten (no timeout in Snake I) |
| Food types | 1 (standard pellet; no bonus items in Snake I) |

### Food Spawning Algorithm

When food needs to be spawned (at game start and after each food is eaten):

```
1. Build list of all unoccupied cells:
   free_cells = all grid cells NOT occupied by any snake segment
2. If free_cells is empty:
   trigger WIN condition (snake fills entire board)
3. Select one cell uniformly at random from free_cells
4. Place food at the selected cell
```

| Property | Value |
|----------|-------|
| Spawn timing | Immediately after previous food is eaten (same tick) |
| Spawn location | Uniformly random among all unoccupied cells |
| Minimum distance from snake head | None (can spawn adjacent to head) |
| Spawn on snake body | Never — explicitly excluded |
| RNG | Seeded pseudo-random number generator for determinism |

### Food Spawning Edge Cases

- **Near-full board**: When the snake occupies 299 of 300 cells, exactly one cell remains for food. The food spawns there. When eaten, the snake fills all 300 cells and the game is won.
- **Single free cell**: The algorithm degenerates to placing food in the only available cell. No retry logic needed.
- **Game start**: The initial food is spawned after the snake is placed, ensuring it does not overlap with the starting 3-segment body.

---

## 7. Speed & Difficulty Progression

### Speed Model

The original Nokia 6110 Snake had a **selectable starting speed** level and **progressive acceleration** as the snake grows longer. Taneli Armanto stated that the hardest level runs "as fast as the snake can possibly go" with "no delay" between position calculations.

### Starting Speed Levels

The player selects a speed level before the game begins. The original game offered multiple speed levels (commonly referenced as levels 1 through 9).

| Speed Level | Base Tick Interval (ms) | Approximate Moves/Second | Description |
|-------------|------------------------|--------------------------|-------------|
| 1 | 400 | 2.5 | Very slow — beginner pace |
| 2 | 350 | 2.9 | Slow |
| 3 | 300 | 3.3 | Comfortable |
| 4 | 250 | 4.0 | Moderate |
| 5 | 200 | 5.0 | Default / medium |
| 6 | 167 | 6.0 | Brisk |
| 7 | 133 | 7.5 | Fast |
| 8 | 100 | 10.0 | Very fast |
| 9 | 70 | 14.3 | Maximum — expert only |

### Progressive Speed Increase

As the snake eats food and grows, the tick interval decreases (speed increases). This creates a natural difficulty curve.

| Property | Value |
|----------|-------|
| Speed increase trigger | Every 5 food pellets eaten |
| Tick interval reduction per step | 8 ms |
| Minimum tick interval (speed floor) | 50 ms (~20 moves/second) at level 9; scales by starting level |
| Speed increase formula | `current_interval = base_interval - (floor(foods_eaten / 5) * 8)` |
| Speed floor formula | `min_interval = max(50, base_interval * 0.2)` |

### Speed Progression Example (Level 5, Base = 200ms)

| Foods Eaten | Tick Interval (ms) | Moves/Second |
|-------------|-------------------|--------------|
| 0--4 | 200 | 5.0 |
| 5--9 | 192 | 5.2 |
| 10--14 | 184 | 5.4 |
| 15--19 | 176 | 5.7 |
| 20--24 | 168 | 6.0 |
| 25--29 | 160 | 6.3 |
| 30--34 | 152 | 6.6 |
| 35--39 | 144 | 6.9 |
| 40--44 | 136 | 7.4 |
| 45--49 | 128 | 7.8 |
| 50--54 | 120 | 8.3 |
| 75--79 | 80 | 12.5 |
| 100+ | 40 (floor) | 25.0 |

### Speed Progression Example (Level 1, Base = 400ms)

| Foods Eaten | Tick Interval (ms) | Moves/Second |
|-------------|-------------------|--------------|
| 0--4 | 400 | 2.5 |
| 5--9 | 392 | 2.6 |
| 10--14 | 384 | 2.6 |
| 50--54 | 320 | 3.1 |
| 100--104 | 240 | 4.2 |
| 200--204 | 80 (floor) | 12.5 |

---

## 8. Scoring System

### Basic Scoring (Snake I Faithful)

In the original Nokia 6110 Snake I, the scoring is simple: **1 point per food pellet eaten**.

| Property | Value |
|----------|-------|
| Points per food pellet (base) | 1 |
| Maximum possible score | 297 (300 cells - 3 starting segments) |
| Score display | Integer, top of screen |
| High score persistence | Saved to device memory |

### Extended Scoring (Speed-Weighted Variant)

Some Nokia Snake versions awarded more points at higher speed levels. For a recreation that supports speed-level selection, the following weighted scoring model is recommended:

| Speed Level | Points Per Food |
|-------------|-----------------|
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |
| 6 | 6 |
| 7 | 7 |
| 8 | 8 |
| 9 | 9 |

With this model:
- **Maximum score at Level 1**: 297 x 1 = 297
- **Maximum score at Level 5**: 297 x 5 = 1,485
- **Maximum score at Level 9**: 297 x 9 = 2,673

### Score Events

| Event | Score Change |
|-------|-------------|
| Food pellet eaten | +N (where N = speed level, or +1 in simple mode) |
| Wall collision | 0 (game ends) |
| Self collision | 0 (game ends) |
| Time survival | 0 (no time-based scoring in Snake I) |

---

## 9. Game States

### Application State Machine

```
BOOT -> TITLE_SCREEN -> SPEED_SELECT -> GAMEPLAY -> GAME_OVER -> TITLE_SCREEN
                                            |
                                          PAUSED
```

### State Definitions

#### BOOT
- Initialize display, load high score from persistent storage, seed RNG.
- Transition: automatic to TITLE_SCREEN.

#### TITLE_SCREEN
- Display game title "SNAKE" and prompt to start.
- Show current high score.
- Input: Press START/ENTER to proceed to SPEED_SELECT.
- Input: No other actions available.

#### SPEED_SELECT
- Display speed level selector (1--9).
- Default selection: Level 5 (or last-used level).
- Input: UP/DOWN to change level; ENTER to confirm.
- Transition: on confirm, proceed to GAMEPLAY.

#### GAMEPLAY
- Active game simulation running.
- Snake moves, food is active, collisions are checked.
- Input: Directional controls change snake direction.
- Input: PAUSE key pauses the game.
- Transition: on collision -> GAME_OVER; on pause -> PAUSED.

##### GAMEPLAY Sub-States

| Sub-State | Description |
|-----------|-------------|
| COUNTDOWN | Optional 3-2-1 countdown before snake starts moving (recreation feature) |
| ACTIVE | Full simulation running; snake is moving |
| EATING | Transient state on the tick food is consumed (triggers growth + new food spawn) |

#### PAUSED
- All timers frozen. Display "PAUSED" text overlay.
- Snake position, score, and all state preserved.
- Input: Press PAUSE again or ENTER to resume.
- Transition: on resume -> GAMEPLAY (ACTIVE).

#### GAME_OVER
- Display "GAME OVER" text.
- Display final score.
- If final score > high score, update high score and display "NEW HIGH SCORE!" message.
- Input: Press ENTER/START to return to TITLE_SCREEN.
- Input: Press R (in recreation) for quick restart.

### State Transition Table

| From | Event | To |
|------|-------|----|
| BOOT | Init complete | TITLE_SCREEN |
| TITLE_SCREEN | Start pressed | SPEED_SELECT |
| SPEED_SELECT | Level confirmed | GAMEPLAY |
| GAMEPLAY | Wall/self collision | GAME_OVER |
| GAMEPLAY | Snake fills grid | GAME_OVER (with win flag) |
| GAMEPLAY | Pause pressed | PAUSED |
| PAUSED | Unpause pressed | GAMEPLAY |
| GAME_OVER | Start/Enter pressed | TITLE_SCREEN |

---

## 10. Controls & Input Handling

### Original Nokia 6110 Controls

| Action | Key | Numpad Position |
|--------|-----|-----------------|
| Move UP | 2 | Top-center |
| Move LEFT | 4 | Middle-left |
| Move RIGHT | 6 | Middle-right |
| Move DOWN | 8 | Bottom-center |
| Pause/Menu | 5 (or dedicated key) | Center |

### Modern Recreation Controls

| Action | Primary Input | Alternative Input |
|--------|---------------|-------------------|
| Move UP | Arrow UP | W |
| Move DOWN | Arrow DOWN | S |
| Move LEFT | Arrow LEFT | A |
| Move RIGHT | Arrow RIGHT | D |
| Pause | Space | Escape |
| Start / Confirm | Enter | Space (on menus) |
| Quick Restart | R | -- |

### Input Handling Model

The game uses a **single-slot input buffer** (direction queue depth of 1). This prevents jitter from rapid key presses while allowing responsive direction changes.

| Property | Value |
|----------|-------|
| Input buffer depth | 1 direction (single next-direction slot) |
| Input timing | Polled between ticks; most recent valid input wins |
| Invalid input rejection | Silent — 180-degree reversals are dropped |
| Same-direction input | Accepted but no-op |
| Input during pause | Direction inputs ignored; only unpause accepted |
| Input during game over | Only restart/menu inputs accepted |

### Direction Queue Algorithm

```
on_key_press(new_direction):
    // Determine the "effective current direction" for validation
    if queued_direction is not empty:
        effective = queued_direction
    else:
        effective = current_snake_direction

    // Reject 180-degree reversals
    if new_direction is opposite of effective:
        return  // silently ignore

    // Accept the input
    queued_direction = new_direction

on_game_tick():
    if queued_direction is not empty:
        current_snake_direction = queued_direction
        clear queued_direction
    move_snake(current_snake_direction)
```

### Two-Input Quick Turn

The single-slot buffer design allows for a critical advanced technique: **the two-input quick turn**. In a single tick window, the player can input two sequential 90-degree turns (e.g., UP then LEFT) to effectively make a U-turn across two ticks. Because the buffer only holds the most recent valid input and validates against the queued (not yet applied) direction:

1. Snake is moving RIGHT.
2. Player presses UP (valid 90-degree turn from RIGHT). Queued = UP.
3. Player presses LEFT (valid 90-degree turn from UP). Queued = LEFT.
4. On the next tick, the snake moves LEFT (apparent reversal over two inputs).

This is **intentional behavior** and a skill-expressive mechanic. Implementations that use a deeper input queue (2 slots) can preserve both inputs and execute them over consecutive ticks for even more precise control.

### Extended Input Queue (Recommended for Recreation)

For smoother play at high speeds, a 2-deep input queue is recommended:

| Property | Value |
|----------|-------|
| Queue depth | 2 directions |
| Validation | Each queued direction validated against the previous queued direction |
| Consumption | One direction consumed per tick |
| Overflow | Oldest queued input is discarded when queue is full and new valid input arrives |

---

## 11. UI Layout

### Screen Layout (Original Nokia 6110)

The original 84x48 pixel display dedicated nearly the entire screen to the game field. The score was displayed at the top in a small font, leaving the remainder for the play area.

```
+------------------------------------------+
|  SCORE: 042                              |  <- Status bar (~6px tall)
+------------------------------------------+
|                                          |
|                                          |
|           [GAME FIELD]                   |  <- Play area (~42px tall)
|          20 x 15 grid                    |
|                                          |
|                                          |
+------------------------------------------+
```

### Screen Layout (Modern Recreation)

```
+--------------------------------------------------+
|  SCORE: 042          HI: 153         SPEED: 5    |  <- Header bar
+--------------------------------------------------+
|##################################################|
|#                                                #|
|#                                                #|
|#                                                #|
|#              [20 x 15 GAME GRID]               #|  <- Bordered play area
|#                                                #|
|#                                                #|
|#                                                #|
|#                                                #|
|##################################################|
+--------------------------------------------------+
|  LENGTH: 15          FOODS: 12                   |  <- Footer (optional)
+--------------------------------------------------+
```

### UI Elements

| Element | Position | Content | Update Frequency |
|---------|----------|---------|------------------|
| Score display | Top-left | Current score integer | Every food eaten |
| High score display | Top-right | All-time high score | On game start and new high score |
| Speed level indicator | Top-center or top-right | Current speed level (1-9) | On game start |
| Snake length | Bottom-left (optional) | Current segment count | Every food eaten |
| Foods eaten counter | Bottom-right (optional) | Total foods consumed | Every food eaten |
| Game field border | Around play area | Solid line (wall indicator) | Static |
| Pause overlay | Center of field | "PAUSED" text | On pause toggle |
| Game Over overlay | Center of field | "GAME OVER" + final score | On death |

### Title Screen Layout

```
+--------------------------------------------------+
|                                                  |
|                                                  |
|                   S N A K E                      |
|                                                  |
|              HIGH SCORE: 153                     |
|                                                  |
|            PRESS ENTER TO START                  |
|                                                  |
|                                                  |
+--------------------------------------------------+
```

### Speed Select Screen Layout

```
+--------------------------------------------------+
|                                                  |
|                SELECT SPEED                      |
|                                                  |
|           1  2  3  4 [5] 6  7  8  9             |
|                       ^                          |
|               (current selection)                |
|                                                  |
|             PRESS ENTER TO START                 |
|                                                  |
+--------------------------------------------------+
```

### Game Over Screen Layout

```
+--------------------------------------------------+
|                                                  |
|                GAME OVER                         |
|                                                  |
|              SCORE:    042                       |
|              BEST:     153                       |
|              LENGTH:    45                       |
|                                                  |
|          PRESS ENTER TO CONTINUE                 |
|                                                  |
+--------------------------------------------------+
```

---

## 12. Audio Design

### Original Hardware

The Nokia 6110 used a **piezo buzzer** capable of producing single-channel square-wave tones. Snake was notably one of the first mobile games released with sound effects on a cellular phone.

### Sound Events

| Event | Sound Type | Frequency | Duration | Description |
|-------|-----------|-----------|----------|-------------|
| Food eaten | Short beep | ~880 Hz (A5) | 50 ms | Quick high-pitched chirp on food consumption |
| Game over (wall) | Descending tone | 440 Hz -> 220 Hz | 300 ms | Falling pitch indicating failure |
| Game over (self) | Descending tone | 440 Hz -> 220 Hz | 300 ms | Same as wall collision |
| Game start | Rising tone | 330 Hz -> 660 Hz | 200 ms | Ascending chirp indicating game begin |
| Level up (speed increase) | Double beep | 660 Hz, 880 Hz | 50 ms + 50 ms | Two quick ascending tones |
| Pause | Single beep | 440 Hz (A4) | 80 ms | Neutral mid-pitch tone |
| Unpause | Single beep | 660 Hz (E5) | 80 ms | Slightly higher pitch than pause |
| Menu navigation | Click | 1000 Hz | 20 ms | Very short tick sound |
| New high score | Celebratory sequence | 440, 554, 659, 880 Hz | 100 ms each | Ascending arpeggio (A4, C#5, E5, A5) |

### Audio Implementation

| Property | Value |
|----------|-------|
| Audio channels | 1 (monophonic) |
| Waveform | Square wave (authentic) or sine wave (softer alternative) |
| Volume levels | 3: Off, Quiet, Normal |
| Audio priority | Game Over sound preempts all other sounds |
| Sound overlap | No overlap — new sound cuts off previous sound |
| Audio latency target | < 16 ms from event trigger to audible output |

### Sound Generation (Square Wave Synthesis)

For authentic recreation, generate sounds programmatically using square wave synthesis:

```
function generate_beep(frequency_hz, duration_ms, sample_rate=44100):
    samples = duration_ms / 1000 * sample_rate
    for i in 0..samples:
        t = i / sample_rate
        value = sign(sin(2 * PI * frequency_hz * t))  // square wave
        output(value * volume)
```

### Music

The original Nokia Snake I had **no background music**. The game was played in silence, punctuated only by sound effects. Background music should **not** be added for a faithful recreation.

---

## 13. Technical Requirements

### Simulation & Timing

| Property | Value |
|----------|-------|
| Logic update | Fixed-timestep tick (interval varies by speed level) |
| Render update | 60 FPS independent of logic tick |
| Tick timer precision | Millisecond accuracy minimum |
| Update order | Input -> Move -> Collision -> Score -> Spawn -> Render |
| Determinism | Same seed + same input sequence = identical game outcome |

### Random Number Generation

| Property | Value |
|----------|-------|
| RNG type | Seeded PRNG (e.g., linear congruential, Mersenne Twister, or xorshift) |
| Seed source | System time at game start (or user-provided for replays) |
| RNG consumers | Food spawn position only |
| RNG calls per food spawn | 1 (index into free cell list) |

### Data Structures

#### Snake Body

- **Representation**: Ordered deque (double-ended queue) of (x, y) coordinate pairs.
- **Head**: Front of deque (index 0).
- **Tail**: Back of deque (last index).
- **Operations**: Push front (new head), pop back (remove tail), iterate (collision check).

#### Grid Occupancy (Optional Optimization)

- **Representation**: 2D boolean array [20][15] marking occupied cells.
- **Purpose**: O(1) collision check and O(n) free cell enumeration for food spawning.
- **Update**: Set cell true on snake head entry; set cell false on tail removal.

#### Input Queue

- **Representation**: Fixed-size circular buffer of capacity 1 or 2.
- **Element type**: Direction enum {UP, DOWN, LEFT, RIGHT}.

### Memory Budget

| Structure | Size |
|-----------|------|
| Snake body (max 300 cells, 2 bytes each) | 600 bytes |
| Grid occupancy (300 booleans) | 300 bytes |
| Food position (2 bytes) | 2 bytes |
| Score, high score, speed, state variables | ~32 bytes |
| Input queue (2 directions) | 2 bytes |
| **Total game state** | **< 1 KB** |

### Persistence

| Data | Storage | Format |
|------|---------|--------|
| High score | Local storage / file | Integer |
| Last speed level used | Local storage / file | Integer (1-9) |
| Sound preference | Local storage / file | Enum (off/quiet/normal) |

---

## 14. QA Acceptance Matrix

### Functional Tests

| # | Test | Expected Result |
|---|------|-----------------|
| 1 | Snake moves one cell per tick in current direction | Position updates by exactly (dx, dy) of direction vector |
| 2 | Snake cannot reverse direction (180-degree turn) | Reverse input is silently ignored; snake continues in current direction |
| 3 | Snake grows by exactly 1 cell when eating food | Body list length increases by 1; tail is not removed on eating tick |
| 4 | Wall collision triggers Game Over | Head at x<0, x>=20, y<0, or y>=15 immediately ends game |
| 5 | Self-collision triggers Game Over | Head overlapping any body segment (accounting for tail removal) ends game |
| 6 | Food never spawns on snake body | After 1000 food spawns, zero overlap with snake body |
| 7 | Exactly one food exists at all times during gameplay | Food count is always 1 between spawn events |
| 8 | Score increments correctly on food eaten | Score increases by speed-level multiplier per food |
| 9 | Speed increases every 5 foods eaten | Tick interval decreases by 8ms at food counts 5, 10, 15, ... |
| 10 | Speed never exceeds minimum tick interval | Tick interval is clamped to floor value |
| 11 | Game Over screen shows correct final score | Displayed score matches internal score counter |
| 12 | High score updates when beaten | New high score saved and displayed on Game Over and Title screens |
| 13 | Pause freezes all game state | Snake position, tick timer, and food position unchanged while paused |
| 14 | Resume from pause continues correctly | Game resumes from exact pre-pause state with no skipped ticks |
| 15 | Game win at 300 segments | Snake filling entire grid triggers win condition |

### Edge Case Tests

| # | Test | Expected Result |
|---|------|-----------------|
| 16 | Food spawn with only 1 free cell | Food spawns in the single remaining cell without error |
| 17 | Rapid direction changes within one tick | Only the last valid input in the queue is used (or queue processes in order) |
| 18 | Direction input during Game Over | Input is ignored; no state changes |
| 19 | Pause/unpause rapid toggling | Game state remains consistent; no duplicate tick processing |
| 20 | Snake moving along wall (parallel) | No collision; snake continues along the wall edge |
| 21 | Snake head meets tail tip (non-growth tick) | No collision (tail vacates the cell on the same tick) |
| 22 | Snake head meets tail tip (growth tick) | Collision occurs (tail does not vacate during growth) |
| 23 | Start game at speed level 9 | Game begins at 70ms tick interval without errors |
| 24 | Deterministic replay: same seed + inputs | Identical game outcome across multiple replays |

### Performance Tests

| # | Test | Expected Result |
|---|------|-----------------|
| 25 | Render at 60 FPS with 300-segment snake | Frame time < 16.67 ms |
| 26 | Logic tick at minimum interval (50ms) | Tick processing completes in < 5 ms |
| 27 | Food spawn with 299 occupied cells | Spawn completes in < 1 ms |
| 28 | No memory leaks over 1000 game sessions | Memory usage remains constant |

---

## Appendix A: Snake I vs. Snake II Feature Comparison

For reference and to clarify scope boundaries, the following features belong to Snake II (Nokia 3310, 2000) and are **excluded** from a faithful Snake I recreation:

| Feature | Snake I (1997/98) | Snake II (2000) |
|---------|-------------------|-----------------|
| Grid size | 20 x 15 | 35 x 28 (larger screen) |
| Wall collision | Fatal | Optional (wrapping mode) |
| Screen wrapping | No | Yes (toroidal) |
| Mazes / obstacles | No | Yes (5 maze layouts + no-maze) |
| Bonus food items | No | Yes (bug/animal shapes, ~100 pts) |
| Bonus food timing | N/A | Every 5 foods eaten, time-limited |
| Two-player mode | No (planned but not shipped) | No |
| Speed levels | Progressive acceleration | 9 selectable levels |
| Score multiplier | 1x (simple) | Speed-level dependent |
| Snake appearance | Simple filled cells | Patterned segments |

---

## Appendix B: Implementation Pseudocode

### Complete Game Tick

```
function game_tick():
    // 1. Process input
    if input_queue is not empty:
        next_dir = input_queue.dequeue()
        if not is_opposite(next_dir, snake.direction):
            snake.direction = next_dir

    // 2. Calculate new head position
    new_head = snake.head + direction_to_vector(snake.direction)

    // 3. Check wall collision
    if new_head.x < 0 or new_head.x >= GRID_WIDTH
       or new_head.y < 0 or new_head.y >= GRID_HEIGHT:
        trigger_game_over("wall")
        return

    // 4. Check food collision
    ate_food = (new_head == food.position)

    // 5. Check self collision
    // If not eating, tail will be removed, so exclude it from check
    body_to_check = snake.body
    if not ate_food:
        body_to_check = snake.body[0 .. length-2]  // exclude tail tip

    if new_head in body_to_check:
        trigger_game_over("self")
        return

    // 6. Move snake
    snake.body.prepend(new_head)
    if ate_food:
        score += points_per_food
        foods_eaten += 1
        update_speed()
        spawn_food()
        play_sound(EAT_SOUND)
    else:
        freed_cell = snake.body.pop_back()

    // 7. Check win
    if snake.body.length == GRID_WIDTH * GRID_HEIGHT:
        trigger_win()
        return

    // 8. Render
    render_game_state()
```

### Food Spawn

```
function spawn_food():
    free_cells = []
    for x in 0..GRID_WIDTH:
        for y in 0..GRID_HEIGHT:
            if (x, y) not in snake.body:
                free_cells.append((x, y))

    if free_cells is empty:
        trigger_win()
        return

    index = rng.next_int(0, free_cells.length - 1)
    food.position = free_cells[index]
```

### Speed Update

```
function update_speed():
    speed_steps = floor(foods_eaten / 5)
    new_interval = base_interval - (speed_steps * 8)
    tick_interval = max(new_interval, min_interval)
```
