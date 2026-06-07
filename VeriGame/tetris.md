# tetris - Tetris (Guideline-Standard Faithful Recreation)

## 1. Game Overview

- **Reference**: Tetris, originally designed by Alexey Pajitnov (1984); this specification targets the modern Tetris Guideline standard (2009 revision) with visual homage to the 1989 Game Boy release.
- **Genre**: Puzzle / Falling-Block
- **Core Fantasy**: Guide falling tetrominoes to form complete horizontal lines across a 10-wide matrix, managing ever-increasing gravity while exploiting rotations, wall kicks, T-spins, and hold strategies to maximize score.
- **Presentation**: 2D fixed-camera side view of a vertical playfield. Monochrome-friendly palette with optional Guideline colors.
- **Target Session**: Marathon mode 6-20 minutes; Endless mode unlimited.
- **Skill Curve**: Approachable within 30 seconds, mastery depth through advanced rotation techniques (T-spins, perfect clears, combos).

---

## 2. Technical Foundation

| Parameter | Value |
|---|---|
| Simulation tick rate | 60 Hz fixed (`dt = 1/60 s = 16.67 ms`) |
| Coordinate system | Integer grid, origin (0,0) at bottom-left of playfield |
| Playfield width | 10 columns (indexed 0-9) |
| Playfield total height | 40 rows (indexed 0-39) |
| Playfield visible height | 20 rows (rows 0-19) |
| Playfield buffer zone | 20 rows above visible area (rows 20-39) used for spawning and rotation |
| Spawn rows | Rows 21-22 (pieces materialize above visible ceiling) |
| Gravity direction | Positive Y is up; gravity moves pieces in -Y direction |
| RNG | Seeded PRNG; 7-bag randomizer (see Section 12) |
| Frame reference | All frame counts assume 60 FPS. 1 frame = 16.67 ms. |

---

## 3. Win / Lose Contract

| Condition | Description |
|---|---|
| **Win (Marathon)** | Clear 150 lines (15 levels x 10 lines each) before top-out |
| **Win (Endless)** | No win state; play continues until top-out |
| **Lose (Top-Out)** | A newly spawned piece overlaps an occupied cell, OR a piece locks entirely above row 19 (the visible ceiling). Game over is triggered immediately. |
| **Lock-Out** | The entire piece locks above the visible playfield (above row 19) |
| **Block-Out** | A new piece cannot spawn because occupied cells block its spawn position |

---

## 4. Core Mechanics

### 4.1 Piece Movement

| Action | Behavior |
|---|---|
| Move Left | Translate active piece 1 cell left; blocked if collision with wall or stack |
| Move Right | Translate active piece 1 cell right; blocked if collision with wall or stack |
| Soft Drop | Increase downward speed to 1 cell per frame (1G); awards 1 point per cell descended |
| Hard Drop | Instantly drop piece to lowest valid position and lock immediately; awards 2 points per cell descended |

### 4.2 Delayed Auto Shift (DAS)

| Parameter | Value |
|---|---|
| Initial delay (DAS) | 10 frames (167 ms) |
| Auto-repeat rate (ARR) | 2 frames (33 ms) |
| Behavior | On key press, piece moves 1 cell immediately. If key is held, after DAS delay, piece auto-repeats at ARR rate. DAS charges during ARE (entry delay). |

### 4.3 Rotation

- Rotation system: **Super Rotation System (SRS)**
- Two rotation directions: Clockwise (CW) and Counter-Clockwise (CCW)
- Four rotation states per piece: **0** (spawn), **R** (clockwise from spawn), **2** (180 from spawn), **L** (counter-clockwise from spawn)
- On rotation request, the game first tests the basic rotation. If it collides, it attempts up to 4 wall kick offsets in order. The first non-colliding offset is used. If all 5 tests fail, rotation is denied.
- See Section 9 for complete wall kick tables.

### 4.4 Lock Delay

| Parameter | Value |
|---|---|
| Lock delay timer | 30 frames (500 ms) |
| Lock delay type | Move-reset (Extended placement) |
| Maximum resets | 15 moves or rotations per piece |
| Behavior | Timer starts when piece first contacts the stack or floor. Each successful move or rotation resets the timer (up to 15 times). After 15 resets, the piece locks on next contact. If the piece rises off the surface (e.g., via wall kick), the timer pauses until contact resumes. |
| Force-lock | If lock delay expires or 15 resets are exhausted while piece is on a surface, piece locks immediately on next frame. |

### 4.5 Entry Delay (ARE)

| Parameter | Value |
|---|---|
| ARE duration | 6 frames (100 ms) |
| Behavior | After a piece locks, there is a brief delay before the next piece spawns. During ARE, the player can charge DAS and buffer a hold input. Line clear animation occurs during or overlaps with ARE. |

### 4.6 Hold System

| Rule | Description |
|---|---|
| Hold action | Swaps current active piece with the held piece. If no piece is held, current piece goes to hold and next piece from queue spawns. |
| Reset on hold | Held piece returns to spawn orientation (state 0) and spawn position |
| Usage limit | One hold per piece placement. After holding, cannot hold again until the next piece locks. |
| Visual | Hold box displayed on left side of playfield |

### 4.7 Ghost Piece

| Rule | Description |
|---|---|
| Display | A translucent silhouette of the active piece shown at its hard-drop destination |
| Update | Recalculated every frame to reflect current piece position and rotation |
| Collision | Ghost piece has no collision; it is purely visual |
| Toggle | Optionally hideable in settings |

---

## 5. Tetromino Definitions

All 7 tetrominoes are defined on a bounding box grid. Cell positions are given as (column, row) offsets within the bounding box, where (0,0) is the bottom-left corner of the bounding box.

### 5.1 Piece Colors (Guideline Standard)

| Piece | Color | Hex Code |
|---|---|---|
| I | Cyan | `#00FFFF` |
| O | Yellow | `#FFFF00` |
| T | Purple | `#800080` |
| S | Green | `#00FF00` |
| Z | Red | `#FF0000` |
| J | Blue | `#0000FF` |
| L | Orange | `#FFA500` |

### 5.2 Spawn Positions

All pieces spawn horizontally in state 0 (spawn orientation). Pieces appear in rows 21-22 (above the visible playfield), centered horizontally:
- **I and O**: spawn centered (columns 3-6 for I, columns 4-5 for O)
- **J, L, S, T, Z**: spawn left-of-center (columns 3-5), rounded left

### 5.3 Rotation States (Cell Positions in Bounding Box)

Convention: Each piece is defined by 4 cells within its bounding box. States: **0** = spawn, **R** = CW, **2** = 180, **L** = CCW.

#### I-Piece (4x4 bounding box)

```
State 0:          State R:          State 2:          State L:
. . . .           . . I .           . . . .           . I . .
I I I I           . . I .           . . . .           . I . .
. . . .           . . I .           I I I I           . I . .
. . . .           . . I .           . . . .           . I . .
```

| State | Cells (col, row) |
|---|---|
| 0 | (0,2), (1,2), (2,2), (3,2) |
| R | (2,3), (2,2), (2,1), (2,0) |
| 2 | (0,1), (1,1), (2,1), (3,1) |
| L | (1,3), (1,2), (1,1), (1,0) |

#### O-Piece (3x3 bounding box, no rotation)

```
State 0/R/2/L:
. O O
. O O
. . .
```

| State | Cells (col, row) |
|---|---|
| 0 | (1,2), (2,2), (1,1), (2,1) |
| R | (1,2), (2,2), (1,1), (2,1) |
| 2 | (1,2), (2,2), (1,1), (2,1) |
| L | (1,2), (2,2), (1,1), (2,1) |

Note: O-piece does not change shape on rotation in standard SRS, but wall kick offsets cause position shifts that cancel out, resulting in no net movement.

#### T-Piece (3x3 bounding box)

```
State 0:       State R:       State 2:       State L:
. T .          . T .          . . .          . T .
T T T          . T T          T T T          T T .
. . .          . T .          . T .          . T .
```

| State | Cells (col, row) |
|---|---|
| 0 | (1,2), (0,1), (1,1), (2,1) |
| R | (1,2), (1,1), (2,1), (1,0) |
| 2 | (0,1), (1,1), (2,1), (1,0) |
| L | (1,2), (0,1), (1,1), (1,0) |

#### S-Piece (3x3 bounding box)

```
State 0:       State R:       State 2:       State L:
. S S          . S .          . . .          S . .
S S .          . S S          . S S          S S .
. . .          . . S          S S .          . S .
```

| State | Cells (col, row) |
|---|---|
| 0 | (1,2), (2,2), (0,1), (1,1) |
| R | (1,2), (1,1), (2,1), (2,0) |
| 2 | (1,1), (2,1), (0,0), (1,0) |
| L | (0,2), (0,1), (1,1), (1,0) |

#### Z-Piece (3x3 bounding box)

```
State 0:       State R:       State 2:       State L:
Z Z .          . . Z          . . .          . Z .
. Z Z          . Z Z          Z Z .          Z Z .
. . .          . Z .          . Z Z          Z . .
```

| State | Cells (col, row) |
|---|---|
| 0 | (0,2), (1,2), (1,1), (2,1) |
| R | (2,2), (1,1), (2,1), (1,0) |
| 2 | (0,1), (1,1), (1,0), (2,0) |
| L | (1,2), (0,1), (1,1), (0,0) |

#### J-Piece (3x3 bounding box)

```
State 0:       State R:       State 2:       State L:
J . .          . J J          . . .          . J .
J J J          . J .          J J J          . J .
. . .          . J .          . . J          J J .
```

| State | Cells (col, row) |
|---|---|
| 0 | (0,2), (0,1), (1,1), (2,1) |
| R | (1,2), (2,2), (1,1), (1,0) |
| 2 | (0,1), (1,1), (2,1), (2,0) |
| L | (1,2), (1,1), (0,0), (1,0) |

#### L-Piece (3x3 bounding box)

```
State 0:       State R:       State 2:       State L:
. . L          . L .          . . .          L L .
L L L          . L .          L L L          . L .
. . .          . L L          L . .          . L .
```

| State | Cells (col, row) |
|---|---|
| 0 | (2,2), (0,1), (1,1), (2,1) |
| R | (1,2), (1,1), (1,0), (2,0) |
| 2 | (0,1), (1,1), (2,1), (0,0) |
| L | (0,2), (1,2), (1,1), (1,0) |

---

## 6. Gravity and Speed System

### 6.1 Gravity Formula (Tetris Worlds / Guideline Standard)

The time for a piece to fall one row is calculated as:

```
seconds_per_row = (0.8 - ((level - 1) * 0.007)) ^ (level - 1)
```

Where `level` starts at 1. Gravity in G (cells per frame at 60 FPS):

```
G = 1 / (seconds_per_row * 60)
```

### 6.2 Gravity Table (Marathon Mode, 60 FPS)

| Level | Seconds/Row | Approx. Frames/Row | Gravity (G) |
|---|---|---|---|
| 1 | 1.0000 | 60.00 | 0.01667 |
| 2 | 0.7930 | 47.58 | 0.02102 |
| 3 | 0.6178 | 37.07 | 0.02698 |
| 4 | 0.4726 | 28.36 | 0.03527 |
| 5 | 0.3541 | 21.24 | 0.04706 |
| 6 | 0.2598 | 15.59 | 0.06415 |
| 7 | 0.1862 | 11.17 | 0.08953 |
| 8 | 0.1302 | 7.81 | 0.12802 |
| 9 | 0.0887 | 5.32 | 0.18797 |
| 10 | 0.0585 | 3.51 | 0.28490 |
| 11 | 0.0373 | 2.24 | 0.44692 |
| 12 | 0.0229 | 1.37 | 0.72854 |
| 13 | 0.0135 | 0.81 | 1.23457 |
| 14 | 0.0076 | 0.46 | 2.19298 |
| 15 | 0.0041 | 0.24 | 4.10256 |

At level 13+, gravity exceeds 1G (more than 1 cell per frame), requiring sub-frame accumulation. At level 15 the piece effectively moves ~4 cells per frame. Implementations should clamp to 20G maximum (instant drop to stack).

### 6.3 NES Classic Reference (Alternate / Retro Mode)

For implementations targeting NES-style feel (NTSC, 60.0988 FPS):

| Level | Frames/Row |
|---|---|
| 0 | 48 |
| 1 | 43 |
| 2 | 38 |
| 3 | 33 |
| 4 | 28 |
| 5 | 23 |
| 6 | 18 |
| 7 | 13 |
| 8 | 8 |
| 9 | 6 |
| 10-12 | 5 |
| 13-15 | 4 |
| 16-18 | 3 |
| 19-28 | 2 |
| 29+ | 1 |

### 6.4 Soft Drop Speed

| Mode | Speed |
|---|---|
| Soft drop | 1G (1 cell per frame, i.e., 60 cells/second) or 20x current gravity, whichever is faster |
| Hard drop | Instantaneous (teleport to lowest valid row, lock immediately) |

### 6.5 Gravity Accumulation

Gravity is applied as a fractional accumulator:
1. Each frame, add the current gravity G to `drop_accumulator`.
2. While `drop_accumulator >= 1.0`, move piece down 1 row and subtract 1.0.
3. If piece cannot move down, begin lock delay.

---

## 7. Scoring System

All scores use the modern Guideline scoring system. Base values are listed below; the level multiplier is applied as shown.

### 7.1 Line Clear Scoring

| Action | Base Points | Formula |
|---|---|---|
| Single (1 line) | 100 | 100 x level |
| Double (2 lines) | 300 | 300 x level |
| Triple (3 lines) | 500 | 500 x level |
| Tetris (4 lines) | 800 | 800 x level |

### 7.2 T-Spin Scoring

| Action | Base Points | Formula |
|---|---|---|
| T-Spin (no lines) | 400 | 400 x level |
| T-Spin Mini (no lines) | 100 | 100 x level |
| T-Spin Mini Single | 200 | 200 x level |
| T-Spin Mini Double | 400 | 400 x level |
| T-Spin Single | 800 | 800 x level |
| T-Spin Double | 1200 | 1200 x level |
| T-Spin Triple | 1600 | 1600 x level |

### 7.3 Back-to-Back Bonus

| Condition | Bonus |
|---|---|
| Consecutive "difficult" clears | +50% of base score |
| Difficult clears | Tetris, T-Spin Mini Single, T-Spin Single, T-Spin Double, T-Spin Triple |
| Chain break | Any Single, Double, or Triple (non-T-Spin) breaks the B2B chain |
| T-Spin with 0 lines | Does NOT break B2B chain |

Example: A back-to-back Tetris at level 5 scores `800 * 5 * 1.5 = 6000`.

### 7.4 Combo Scoring

The combo counter starts at -1 (no combo active). Each consecutive piece placement that clears at least one line increments the counter by 1. A piece that clears no lines resets the counter to -1.

| Combo Count | Bonus Points |
|---|---|
| 0 | 0 (first line clear, no combo) |
| 1 | 50 x level |
| 2 | 50 x level |
| 3 | 100 x level |
| 4 | 100 x level |
| 5 | 150 x level |
| 6 | 150 x level |
| 7 | 200 x level |
| 8 | 200 x level |
| 9 | 250 x level |
| 10 | 250 x level |
| 11+ | 350 x level |

Total score for a line clear = `(base_clear_score [x 1.5 if B2B] + combo_bonus) x level`.

### 7.5 Drop Scoring

| Action | Points |
|---|---|
| Soft drop | 1 point per cell descended (not multiplied by level) |
| Hard drop | 2 points per cell descended (not multiplied by level) |

### 7.6 Perfect Clear (All Clear) Bonus

Awarded when a line clear leaves the entire playfield empty:

| Clear Type | Bonus Points |
|---|---|
| Single Perfect Clear | 800 x level |
| Double Perfect Clear | 1200 x level |
| Triple Perfect Clear | 1800 x level |
| Tetris Perfect Clear | 2000 x level |
| B2B Tetris Perfect Clear | 3200 x level |

---

## 8. Level Progression

### 8.1 Fixed-Goal System (Modern Standard)

| Parameter | Value |
|---|---|
| Lines per level | 10 |
| Total levels (Marathon) | 15 |
| Total lines to complete Marathon | 150 |
| Level-up trigger | Clearing 10 lines advances to next level |
| Excess lines | NOT carried over to next level goal |
| Starting level | Player may select starting level (1-15) |

### 8.2 Goal Credit per Action

In the variable-goal system (alternative mode), each action contributes goal points equal to `base_score / 100` (rounded down):

| Action | Goal Credit |
|---|---|
| Single | 1 |
| Double | 3 |
| Triple | 5 |
| Tetris | 8 |
| T-Spin Mini Single | 2 |
| T-Spin Single | 8 |
| T-Spin Double | 12 |
| T-Spin Triple | 16 |
| Perfect Clear (any) | +10 bonus |

Each level requires `5 x level` goal points. Excess is NOT carried over.

---

## 9. Wall Kick System (SRS)

When a rotation would cause the piece to overlap the playfield boundary or existing blocks, the game tests a series of offset translations (wall kicks). Five tests are performed in order; the first that results in a valid position is accepted. If all 5 fail, the rotation is denied.

Convention: Offsets are `(x, y)` where `+x` = right, `+y` = up.

### 9.1 J, L, S, T, Z Wall Kick Data

| Rotation | Test 1 | Test 2 | Test 3 | Test 4 | Test 5 |
|---|---|---|---|---|---|
| 0 -> R | (0, 0) | (-1, 0) | (-1,+1) | (0,-2) | (-1,-2) |
| R -> 0 | (0, 0) | (+1, 0) | (+1,-1) | (0,+2) | (+1,+2) |
| R -> 2 | (0, 0) | (+1, 0) | (+1,-1) | (0,+2) | (+1,+2) |
| 2 -> R | (0, 0) | (-1, 0) | (-1,+1) | (0,-2) | (-1,-2) |
| 2 -> L | (0, 0) | (+1, 0) | (+1,+1) | (0,-2) | (+1,-2) |
| L -> 2 | (0, 0) | (-1, 0) | (-1,-1) | (0,+2) | (-1,+2) |
| L -> 0 | (0, 0) | (-1, 0) | (-1,-1) | (0,+2) | (-1,+2) |
| 0 -> L | (0, 0) | (+1, 0) | (+1,+1) | (0,-2) | (+1,-2) |

### 9.2 I-Piece Wall Kick Data

| Rotation | Test 1 | Test 2 | Test 3 | Test 4 | Test 5 |
|---|---|---|---|---|---|
| 0 -> R | (0, 0) | (-2, 0) | (+1, 0) | (-2,-1) | (+1,+2) |
| R -> 0 | (0, 0) | (+2, 0) | (-1, 0) | (+2,+1) | (-1,-2) |
| R -> 2 | (0, 0) | (-1, 0) | (+2, 0) | (-1,+2) | (+2,-1) |
| 2 -> R | (0, 0) | (+1, 0) | (-2, 0) | (+1,-2) | (-2,+1) |
| 2 -> L | (0, 0) | (+2, 0) | (-1, 0) | (+2,+1) | (-1,-2) |
| L -> 2 | (0, 0) | (-2, 0) | (+1, 0) | (-2,-1) | (+1,+2) |
| L -> 0 | (0, 0) | (+1, 0) | (-2, 0) | (+1,-2) | (-2,+1) |
| 0 -> L | (0, 0) | (-1, 0) | (+2, 0) | (-1,+2) | (+2,-1) |

### 9.3 O-Piece Wall Kick Data

The O-piece does not kick. All rotation states are identical, so rotation has no effect.

---

## 10. T-Spin Detection

### 10.1 Three-Corner Rule

A T-Spin is recognized when ALL of the following conditions are met:
1. The last successful movement of the T-piece was a rotation (not a translation).
2. At least 3 of the 4 diagonal corners adjacent to the T-piece's center cell are occupied (by wall, floor, or stack blocks).

### 10.2 T-Spin vs T-Spin Mini

After confirming the 3-corner rule:

| Classification | Condition |
|---|---|
| **T-Spin (proper)** | 2 of the 3 occupied corners are in the "front" of the T (the two corners adjacent to the pointing/protruding mino), AND at least 1 corner is in the "back" |
| **T-Spin Mini** | Only 1 of the 2 front corners is occupied, and both back corners are occupied |
| **Override to proper** | If the last rotation used a wall kick offset that moved the piece by (1,2) or (2,1) cells (the 5th kick test), it is always classified as a proper T-Spin regardless of corner configuration |

### 10.3 Front/Back Corner Definition by State

| T-State | Front Corners (relative to center) | Back Corners |
|---|---|---|
| 0 (pointing up) | (-1,+1), (+1,+1) | (-1,-1), (+1,-1) |
| R (pointing right) | (+1,+1), (+1,-1) | (-1,+1), (-1,-1) |
| 2 (pointing down) | (-1,-1), (+1,-1) | (-1,+1), (+1,+1) |
| L (pointing left) | (-1,+1), (-1,-1) | (+1,+1), (+1,-1) |

---

## 11. Line Clear Mechanics

### 11.1 Detection

After a piece locks, scan all rows from bottom to top. Any row where all 10 cells are occupied is marked for clearing.

### 11.2 Clear Process

1. **Mark**: Identify all complete rows (1-4 rows possible per lock).
2. **Animate**: Play line clear animation (duration: 20 frames / 333 ms).
3. **Remove**: Delete all cells in marked rows.
4. **Collapse**: All rows above cleared rows shift down by the number of cleared rows below them (naive gravity; no cascade/split gravity).
5. **Score**: Award points based on clear type, T-spin status, B2B, combo, and perfect clear.
6. **Level check**: Increment line counter; check level-up condition.

### 11.3 Line Clear Animation Timing

| Phase | Duration |
|---|---|
| Flash/highlight | 10 frames (167 ms) |
| Collapse | 10 frames (167 ms) |
| Total clear delay | ~20 frames (333 ms) |
| ARE overlap | Line clear delay may overlap with ARE |

---

## 12. Random Generation (7-Bag System)

### 12.1 Algorithm

1. Place all 7 tetromino types (I, O, T, S, Z, J, L) into a "bag."
2. Shuffle the bag using a seeded Fisher-Yates shuffle.
3. Deal pieces one at a time from the shuffled bag.
4. When the bag is empty, generate a new bag and repeat.

### 12.2 Properties

| Property | Value |
|---|---|
| Maximum gap between same piece | 12 pieces (worst case: piece is last in bag N, first in bag N+2) |
| Minimum duplicates in 14 pieces | Each piece appears exactly 2 times in any 2 consecutive bags |
| Drought protection | By design, no piece can be absent for more than 12 consecutive pieces |
| Seed | Must be stored for replay determinism |

### 12.3 Next Queue

| Parameter | Value |
|---|---|
| Preview pieces shown | 5 (minimum 1 required by Guideline; 5 is standard) |
| Display position | Right side of playfield |

---

## 13. Game States

### 13.1 Application State Machine

```
Boot -> MainMenu -> Loading -> Run -> Result
                                 ^      |
                                 |      v
                                 +------+
```

| State | Description |
|---|---|
| `Boot` | Load config, input bindings, seed RNG, initialize audio |
| `MainMenu` | Mode selection (Marathon / Endless), starting level, options |
| `Loading` | Asset preload, initialize playfield, generate first 2 bags |
| `Run` | Active gameplay (substates below) |
| `Result` | Final score display, statistics, replay option, restart |

### 13.2 Run Substates

| Substate | Description |
|---|---|
| `Countdown` | 3-2-1-Go countdown before gameplay begins (180 frames / 3 seconds) |
| `Active` | Normal gameplay; gravity, input, and timers running |
| `LineClear` | Rows being cleared; piece input paused during animation |
| `ARE` | Entry delay between piece lock and next piece spawn |
| `Paused` | All timers frozen; pause menu shown. DAS state preserved. |
| `TopOut` | Game over sequence; board state frozen, death animation plays |

### 13.3 Per-Piece Lifecycle

```
Spawn -> Falling -> [Soft/Hard Drop] -> Landed -> Lock Delay -> Locked
                         ^                             |
                         |                             v
                         +--- (move/rotate resets) ----+
```

1. **Spawn**: Piece appears at spawn position in state 0. If spawn position is blocked, trigger Block-Out (game over).
2. **Falling**: Piece descends at current gravity rate. Player can move, rotate, soft drop, hard drop, or hold.
3. **Landed**: Piece contacts surface. Lock delay timer starts (or resumes if previously started).
4. **Lock Delay**: 500 ms timer. Moves/rotations reset timer (up to 15 times). If piece lifts off surface, timer pauses.
5. **Locked**: Piece integrates into stack. Check for line clears. Trigger ARE. Spawn next piece.

---

## 14. UI Layout

### 14.1 Screen Composition

```
+--------------------------------------------------+
|                                                  |
|   +------+   +--------------------+   +-------+  |
|   | HOLD |   |                    |   | NEXT  |  |
|   |      |   |                    |   |  [1]  |  |
|   | [  ] |   |     PLAYFIELD     |   |  [2]  |  |
|   +------+   |     10 x 20       |   |  [3]  |  |
|              |                    |   |  [4]  |  |
|   SCORE:    |  (ghost piece at   |   |  [5]  |  |
|   000000    |   drop position)   |   +-------+  |
|              |                    |              |
|   LEVEL:    |                    |              |
|   01        |                    |              |
|              |                    |              |
|   LINES:    +--------------------+              |
|   000                                           |
|                                                  |
|   COMBO:                                        |
|   --                                            |
|                                                  |
+--------------------------------------------------+
```

### 14.2 HUD Elements

| Element | Position | Update Rate |
|---|---|---|
| Hold box | Left of playfield | On hold action |
| Next queue (5 pieces) | Right of playfield | On piece spawn |
| Score | Left panel | On score change |
| Level | Left panel | On level change |
| Lines cleared | Left panel | On line clear |
| Combo counter | Left panel | On combo change |
| Back-to-back indicator | Near score | On B2B status change |
| Time elapsed | Bottom or top | Every second |

### 14.3 Playfield Rendering

| Element | Visual |
|---|---|
| Grid lines | Subtle grid overlay on empty cells |
| Active piece | Full color, Guideline color per piece type |
| Ghost piece | Same shape as active piece, 30% opacity, at hard-drop destination |
| Locked stack | Same colors as piece type that placed them; slightly dimmer than active |
| Line clear | Flash white (10 frames), then collapse animation (10 frames) |
| Danger zone | Row 17+ stack height triggers danger visual (red tint or pulsing border) |

---

## 15. Audio Design

### 15.1 Music

| Track | Context |
|---|---|
| Type-A (Korobeiniki) | Main gameplay BGM. Tempo increases with level. |
| Type-B (optional) | Alternate BGM selection |
| Type-C (optional) | Alternate BGM selection |
| Menu theme | Main menu / title screen |
| Results fanfare | Score display screen |

### 15.2 Sound Effects

| Event | SFX Description |
|---|---|
| Piece move (left/right) | Short click/tap |
| Piece rotate | Slightly higher-pitched click |
| Soft drop (per cell) | Soft thud per row |
| Hard drop | Sharp impact/slam |
| Piece lock | Solid thunk/snap |
| Single line clear | Short chime |
| Double line clear | Ascending two-note chime |
| Triple line clear | Ascending three-note chime |
| Tetris (4 lines) | Triumphant jingle (distinct, rewarding) |
| T-Spin | Unique spinning/whoosh effect |
| T-Spin + lines | T-Spin SFX layered with line clear SFX |
| Back-to-back | Additional sparkle/accent on top of clear SFX |
| Combo (increasing) | Rising pitch per consecutive combo count |
| Perfect Clear | Grand fanfare / explosion SFX |
| Hold | Swap/whoosh sound |
| Level up | Ascending scale or bell tone |
| Danger (high stack) | Warning beep or heartbeat pulse (looping) |
| Top-out (game over) | Descending tone / crash |
| Countdown (3-2-1) | Beep per count; different tone on "Go" |

### 15.3 Music Tempo Scaling

| Level Range | Tempo Multiplier |
|---|---|
| 1-5 | 1.0x (base tempo) |
| 6-10 | 1.15x |
| 11-13 | 1.3x |
| 14-15 | 1.5x |
| Danger active | Additional +10% tempo on top of level tempo |

---

## 16. Controls

### 16.1 Default Key Bindings

| Action | Keyboard Primary | Keyboard Alt | Gamepad |
|---|---|---|---|
| Move Left | Left Arrow | A | D-Pad Left |
| Move Right | Right Arrow | D | D-Pad Right |
| Soft Drop | Down Arrow | S | D-Pad Down |
| Hard Drop | Space | W / Up Arrow | D-Pad Up / A Button |
| Rotate CW | X / Up Arrow | Numpad 1 | B Button |
| Rotate CCW | Z | Numpad 2 | Y Button |
| Hold | C / Shift | Numpad 0 | L / R Bumper |
| Pause | Escape / P | F1 | Start |
| Restart | (from pause menu) | - | (from pause menu) |

### 16.2 Input Handling Rules

| Rule | Description |
|---|---|
| Input buffering | Buffer the most recent input during ARE/line clear delay; execute on first active frame |
| DAS preservation | DAS charge is maintained across piece spawns and hold swaps |
| Simultaneous L+R | Cancel out (no movement) OR last-pressed wins (configurable) |
| Rotation priority | If both CW and CCW are pressed simultaneously, CW takes priority |
| Input during ARE | DAS charges; hold input is buffered; rotation input may be buffered |

---

## 17. Data Contracts

### 17.1 Config Schema

```json
{
  "game": {
    "version": "1.0.0",
    "mode": "marathon",
    "starting_level": 1,
    "marathon_target_lines": 150,
    "seed": null
  },
  "timing": {
    "logic_fps": 60,
    "das_frames": 10,
    "arr_frames": 2,
    "lock_delay_frames": 30,
    "max_lock_resets": 15,
    "are_frames": 6,
    "line_clear_frames": 20
  },
  "display": {
    "ghost_piece_enabled": true,
    "ghost_opacity": 0.3,
    "next_preview_count": 5,
    "grid_lines_visible": true
  },
  "audio": {
    "master_volume": 1.0,
    "bgm_volume": 0.7,
    "sfx_volume": 0.9,
    "music_track": "type_a"
  },
  "scoring": {
    "system": "guideline_modern",
    "soft_drop_per_cell": 1,
    "hard_drop_per_cell": 2,
    "back_to_back_multiplier": 1.5
  }
}
```

### 17.2 Runtime State Snapshot

```json
{
  "time": {
    "tick": 0,
    "elapsed_seconds": 0.0,
    "paused": false
  },
  "run": {
    "state": "Active",
    "substate": "Falling",
    "seed": 123456,
    "bag_index": 0,
    "bag_sequence": ["T", "I", "L", "J", "S", "Z", "O"]
  },
  "active_piece": {
    "type": "T",
    "state": "0",
    "position": { "col": 4, "row": 21 },
    "lock_delay_remaining_frames": 30,
    "lock_resets_used": 0,
    "gravity_accumulator": 0.0
  },
  "hold": {
    "piece": null,
    "available": true
  },
  "next_queue": ["I", "L", "J", "S", "Z"],
  "playfield": {
    "width": 10,
    "height": 40,
    "cells": "10x40 array of { occupied: bool, color: string | null }"
  },
  "scoring": {
    "score": 0,
    "level": 1,
    "lines_cleared": 0,
    "lines_to_next_level": 10,
    "combo_count": -1,
    "back_to_back_active": false,
    "last_clear_was_difficult": false
  },
  "statistics": {
    "pieces_placed": 0,
    "singles": 0,
    "doubles": 0,
    "triples": 0,
    "tetrises": 0,
    "t_spins": 0,
    "t_spin_singles": 0,
    "t_spin_doubles": 0,
    "t_spin_triples": 0,
    "perfect_clears": 0,
    "max_combo": 0,
    "max_b2b": 0
  }
}
```

---

## 18. Technical Requirements

| Requirement | Specification |
|---|---|
| Simulation tick | Fixed `dt = 1/60 s`; all gameplay logic runs at this rate |
| Update order | `Input -> DAS -> Gravity -> Collision -> Lock -> LineClear -> Score -> Spawn -> UI` |
| RNG | All random decisions consume from a single seeded PRNG stream |
| Determinism | Same seed + same input sequence = identical game state at every tick |
| Pause behavior | Freezes all gameplay timers, gravity, lock delay, ARE, and DAS charging |
| 2x speed | Must preserve deterministic outcomes |
| Replay support | Record format: initial seed + timestamped input events (tick, action) |
| Entity lifecycle | `spawn -> active -> locked -> merged_to_stack` |
| No gameplay in render | All rules and state changes occur in logic tick, never in render callback |

### 18.1 Performance Budget

| Metric | Target |
|---|---|
| Render frame | 16.67 ms (60 FPS) |
| Logic tick | <= 2 ms average, <= 4 ms p99 |
| Input latency | <= 1 frame (16.67 ms) from keypress to visual response |
| Audio latency | <= 2 frames (33 ms) from event to sound |

---

## 19. Accessibility

| Feature | Description |
|---|---|
| Remappable controls | All actions rebindable for keyboard and gamepad |
| Colorblind mode | Distinct piece shapes are sufficient; optionally add pattern overlays or high-contrast outlines per piece type |
| Volume sliders | Independent master, BGM, SFX controls |
| Ghost piece toggle | Can be enabled/disabled |
| Visual flash reduction | Option to reduce line clear flash intensity |
| Text scaling | Score/level/line display scalable for visibility |
| Screen reader hints | Announce game over, level up, Tetris clear events as text |

---

## 20. QA Acceptance Criteria

1. All 7 tetrominoes render correctly in all 4 rotation states.
2. SRS wall kicks match the offset tables in Section 9 exactly; all 5 tests are tried in order.
3. 7-bag randomizer never produces the same piece more than twice in any sequence of 7 pieces (within one bag).
4. Lock delay resets exactly 15 times and then forces lock on surface contact.
5. Hard drop places piece at the exact same position as the ghost piece.
6. Back-to-back bonus activates only after consecutive difficult clears and awards exactly 1.5x base score.
7. Combo counter increments correctly and resets to -1 on non-clearing placement.
8. T-Spin detection correctly distinguishes proper T-Spin from T-Spin Mini using the 3-corner rule.
9. Perfect clear is detected when all 400 playfield cells (10x40) are empty after a line clear.
10. Gravity matches the formula `(0.8 - ((level-1) * 0.007)) ^ (level-1)` within 1-frame tolerance.
11. Game over triggers on block-out (spawn overlap) and lock-out (piece locked entirely above row 19).
12. Hold correctly swaps piece, resets orientation to state 0, and prevents double-hold per placement.
13. Pause freezes all timers; resume restores exact state with no frame skip or duplication.
14. Replay with same seed and input stream produces identical score and final state.
15. DAS charges during ARE and carries across piece transitions.
16. Line clear animation completes before next piece becomes controllable.
17. Level-up occurs at exactly 10 lines per level; marathon ends at level 15 completion.
18. Score, lines, level, and combo display update within the same frame as the triggering event.
19. No piece can be moved or rotated outside the playfield boundaries (columns 0-9, rows 0-39).
20. Seeded runs are fully deterministic: identical seed + inputs = identical outputs at every tick.
