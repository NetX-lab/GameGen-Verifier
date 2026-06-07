# Threes! — Complete Game Specification

## 1. Game Overview

**Title:** Threes!
**Genre:** Sliding number puzzle
**Platform:** Single-player, swipe/keyboard-controlled
**Original Release:** February 2014 (Sirvo LLC / Asher Vollmer)
**Objective:** Slide numbered tiles on a 4x4 grid to combine matching numbers. Unlike 2048, the base values are 1, 2, and 3. Ones and twos combine to make 3; threes and higher combine only with their own value. Maximize your score when no moves remain.

---

## 2. Technical Foundation

### 2.1 Display

| Parameter            | Value                |
|----------------------|----------------------|
| Grid size            | 4 x 4 cells          |
| Cell size            | 80 x 80 pixels       |
| Cell spacing         | 10 pixels             |
| Board size           | 350 x 350 pixels     |
| Total canvas         | 400 x 600 pixels     |
| Border radius (cells)| 8 pixels              |
| Frame rate           | 60 FPS               |

### 2.2 Coordinate System

- Origin (0, 0) at top-left.
- Column 0-3 left-to-right, Row 0-3 top-to-bottom.

---

## 3. Tile Types and Colors

### 3.1 Tile Values and Appearance

| Value  | Background   | Text Color | Category      |
|--------|-------------|------------|---------------|
| 1      | #66CCFF     | #FFFFFF    | Blue tile     |
| 2      | #FF6680     | #FFFFFF    | Red/pink tile |
| 3      | #FFFFFF     | #333333    | White tile    |
| 6      | #FFFFFF     | #333333    | White tile    |
| 12     | #FFFFFF     | #333333    | White tile    |
| 24     | #FFFFFF     | #333333    | White tile    |
| 48     | #FFFFFF     | #333333    | White tile    |
| 96     | #FFD700     | #FFFFFF    | Gold tile     |
| 192    | #FFB800     | #FFFFFF    | Gold tile     |
| 384    | #FF9900     | #FFFFFF    | Orange tile   |
| 768    | #FF6600     | #FFFFFF    | Orange tile   |
| 1536   | #FF3300     | #FFFFFF    | Red tile      |
| 3072   | #CC0000     | #FFFFFF    | Deep red tile |
| 6144   | #990066     | #FFFFFF    | Purple tile   |
| 12288  | #660099     | #FFFFFF    | Dark purple   |

### 3.2 Tile Faces

Each tile >= 3 has a simple face illustration:
- Two dots for eyes (positioned at 30% and 70% horizontal, 35% vertical).
- A small curved line for a mouth (centered, 60% vertical).
- Face expression changes: tiles < 48 = happy, 48-192 = excited, 384+ = determined/fierce.
- Tiles 1 and 2 have NO face (they are "incomplete" tiles).

---

## 4. Core Mechanics

### 4.1 Sliding Rules — Key Differences from 2048

1. **Tiles move only ONE cell per swipe** (not all the way to the wall).
2. **Three combination types:**
   - 1 + 2 = 3
   - N + N = 2N (only when N >= 3)
   - 1 + 1 does NOT combine
   - 2 + 2 does NOT combine
3. **One tile enters from the side** after each valid move.
4. **Tiles stack against walls and each other** — a tile blocked by another tile or a wall does not move.

### 4.2 Movement Rules (Detailed)

When the player swipes in a direction:

1. Process each row/column in the direction of movement.
2. For each tile (starting from the side closest to the swipe direction):
   a. If the cell in front is empty: slide the tile one cell.
   b. If the cell in front contains a compatible tile: merge them.
   c. If the cell in front is occupied by an incompatible tile or is a wall: the tile does not move.
3. Each tile can move at most 1 cell.
4. Merges happen during the slide (not after).

### 4.3 Merge Compatibility Table

| Tile A | Tile B | Result | Valid? |
|--------|--------|--------|--------|
| 1      | 1      | N/A    | NO     |
| 1      | 2      | 3      | YES    |
| 2      | 1      | 3      | YES    |
| 2      | 2      | N/A    | NO     |
| 1      | 3+     | N/A    | NO     |
| 2      | 3+     | N/A    | NO     |
| 3      | 3      | 6      | YES    |
| 6      | 6      | 12     | YES    |
| 12     | 12     | 24     | YES    |
| N      | N      | 2N     | YES (N>=3) |
| N      | M      | N/A    | NO (N!=M, unless 1+2) |

### 4.4 Slide Algorithm

```python
def slide_row_left(row):
    """Slide a row of 4 tiles to the left. Each tile moves at most 1 cell."""
    result = list(row)  # copy
    for i in range(1, 4):  # process positions 1, 2, 3
        if result[i] == 0:
            continue  # no tile to move
        if result[i-1] == 0:
            # Empty cell in front: slide into it
            result[i-1] = result[i]
            result[i] = 0
        elif can_merge(result[i-1], result[i]):
            # Compatible tile: merge
            result[i-1] = merge(result[i-1], result[i])
            result[i] = 0
        # else: blocked, do nothing
    return result

def can_merge(a, b):
    if a == 1 and b == 2: return True
    if a == 2 and b == 1: return True
    if a >= 3 and a == b: return True
    return False

def merge(a, b):
    if (a == 1 and b == 2) or (a == 2 and b == 1):
        return 3
    return a + b  # same values, a == b
```

### 4.5 Processing Order

- Swipe Left: Process columns 1, 2, 3 (left to right, merging into left).
- Swipe Right: Process columns 2, 1, 0 (right to left, merging into right).
- Swipe Up: Process rows 1, 2, 3 (top to bottom, merging upward).
- Swipe Down: Process rows 2, 1, 0 (bottom to top, merging downward).

---

## 5. New Tile Spawning

### 5.1 Spawn Position

After each valid move, a new tile enters from the **opposite edge** of the swipe direction:
- Swipe Left → new tile enters from the right edge.
- Swipe Right → new tile enters from the left edge.
- Swipe Up → new tile enters from the bottom edge.
- Swipe Down → new tile enters from the top edge.

The tile spawns in a random row/column on that edge that has an empty cell. If multiple cells on that edge are empty, one is chosen at random. If no cells on that edge are empty (all 4 are occupied), the move is still valid if tiles moved, but no new tile spawns (rare edge case — in standard Threes this shouldn't happen if the move is valid).

### 5.2 Spawn Values

The game uses a deck-based system for spawning tiles:

**Deck composition:**
- 4 tiles of value 1
- 4 tiles of value 2
- 4 tiles of value 3

Total: 12 tiles per deck.

**Deck behavior:**
1. Shuffle the deck of 12 tiles.
2. Deal one tile per move from the deck.
3. When the deck is empty, create and shuffle a new deck.

**Bonus tiles:** Once the highest tile on the board reaches 48 or higher, a "bonus" tile can appear instead of a deck tile. Bonus tile rules:
- Probability: ~1 in 21 tiles is a bonus tile.
- Bonus tile value: A random power of 3, from 3 up to max_tile / 8.
  - Example: If max tile is 384, bonus tiles can be 3, 6, 12, 24, or 48.
- Bonus tiles are visually indicated in the "next tile" preview with a + symbol.

### 5.3 Next Tile Preview

- The next tile to spawn is shown at the top of the screen.
- For standard tiles (1, 2, 3): Show the tile color (blue, red, or white).
- For bonus tiles (6+): Show a white tile with a "+" or highlight.
- The preview only hints at the category, not the exact value (original game behavior).
  - Blue hint = 1
  - Red hint = 2
  - White hint = 3
  - White with + = bonus tile (exact value unknown)

---

## 6. Initial Board Setup

1. Start with 9 tiles on the 4x4 board (9 occupied, 7 empty).
2. Initial tiles are drawn from the first deck: approximately 3 ones, 3 twos, and 3 threes.
3. Placed randomly on the board with no specific pattern.

---

## 7. Scoring

### 7.1 Score Formula

Each tile's score contribution is calculated as:

```
score(value) = 3^(log2(value/3) + 1)    for value >= 3
score(1) = 0
score(2) = 0
```

Simplified lookup table:

| Tile Value | Points       |
|------------|-------------|
| 1          | 0           |
| 2          | 0           |
| 3          | 3           |
| 6          | 9           |
| 12         | 27          |
| 24         | 81          |
| 48         | 243         |
| 96         | 729         |
| 192        | 2,187       |
| 384        | 6,561       |
| 768        | 19,683      |
| 1536       | 59,049      |
| 3072       | 177,147     |
| 6144       | 531,441     |
| 12288      | 1,594,323   |

**Total score = sum of score(value) for all tiles on the board.**

Score is recalculated after each move (it's a snapshot of the board state, not cumulative).

### 7.2 Score Display

- Display the current board score prominently.
- Show best score for comparison.

---

## 8. Game Over

### 8.1 Condition

The game ends when no valid move exists in any of the 4 directions.

A move is valid if at least one tile can either:
- Slide into an adjacent empty cell, OR
- Merge with an adjacent compatible tile.

### 8.2 Game Over Sequence

1. "No more moves!" text appears.
2. Board zooms out slightly (scale 0.9 over 500ms).
3. Each tile's individual score is displayed above it briefly.
4. Total score calculated and displayed with count-up animation.
5. Highest tile is highlighted with a golden border.
6. Options: "Play Again", "Share".

### 8.3 Game Over Screen

```
+------------------------------------------+
|                                          |
|        GAME OVER                         |
|                                          |
|  +----+----+----+----+                   |
|  | 3  | 6  | 12 | 3  |                   |
|  |+3  |+9  |+27 |+3  |  (individual      |
|  +----+----+----+----+   tile scores)     |
|  | 48 | 24 | 6  | 1  |                   |
|  |+243|+81 |+9  | 0  |                   |
|  +----+----+----+----+                   |
|  | 2  | 96 | 12 | 3  |                   |
|  | 0  |+729|+27 |+3  |                   |
|  +----+----+----+----+                   |
|  | 1  | 6  | 48 | 24 |                   |
|  | 0  |+9  |+243|+81 |                   |
|  +----+----+----+----+                   |
|                                          |
|  TOTAL SCORE: 1,467                      |
|  BEST: 24,680                            |
|                                          |
|  [ PLAY AGAIN ]                          |
|                                          |
+------------------------------------------+
```

---

## 9. Input Handling

### 9.1 Controls

| Action      | Key / Gesture           |
|-------------|-------------------------|
| Slide Up    | Up Arrow / W / Swipe Up |
| Slide Down  | Down Arrow / S / Swipe Down |
| Slide Left  | Left Arrow / A / Swipe Left |
| Slide Right | Right Arrow / D / Swipe Right |
| New Game    | Button click            |

### 9.2 Swipe Detection

- Minimum distance: 20 pixels.
- Direction determined by dominant axis (same as 2048).
- Swipe must originate within the board area.

### 9.3 Input During Animation

- Inputs during the slide animation (200ms) are queued.
- Maximum queue size: 1.
- Rapid swipes are processed sequentially.

---

## 10. Animations

### 10.1 Tile Movement

| Animation              | Duration | Easing              |
|------------------------|----------|----------------------|
| Tile slide (1 cell)    | 200 ms   | Ease-out             |
| Tile merge             | 200 ms   | Scale bump 1.0->1.15->1.0 |
| New tile entrance      | 250 ms   | Slide in from edge   |
| Board settle           | 50 ms    | None                 |
| Game over zoom out     | 500 ms   | Ease-out             |
| Score count up         | 1000 ms  | Ease-out             |

### 10.2 New Tile Entrance

- Tile slides in from the edge (opposite to swipe direction).
- Starts one cell off-screen, slides into its target cell.
- Duration: 250ms, ease-out.
- Tile appears with full opacity from the start.

### 10.3 Merge Animation

- The moving tile slides into the stationary tile.
- On contact, both disappear and the merged tile pops in.
- Pop: Scale from 0.8 to 1.15 (100ms), then settle to 1.0 (100ms).
- Brief particle burst (5-8 particles, tile color, 200ms lifetime).

### 10.4 Idle Animations

- Tiles with faces blink occasionally (every 3-5 seconds, random per tile).
- Blink: Eyes close for 150ms.
- Tiles >= 96 have a subtle golden shimmer (light travels across the tile surface at 0.5Hz).

---

## 11. UI Layout

```
+------------------------------------------+
|                                          |
|  THREES!              SCORE: 1,467       |
|                       BEST:  24,680      |
|                                          |
|  Next: [Blue]    (preview of next tile)  |
|        ↓                                 |
|  +--------+--------+--------+--------+   |
|  |        |        |        |        |   |
|  |   3    |   1    |        |   6    |   |
|  |  ^_^   |        |        |  ^_^   |   |
|  +--------+--------+--------+--------+   |
|  |        |        |        |        |   |
|  |   2    |   48   |   12   |        |   |
|  |        |  >_<   |  ^_^   |        |   |
|  +--------+--------+--------+--------+   |
|  |        |        |        |        |   |
|  |        |   3    |   24   |   1    |   |
|  |        |  ^_^   |  ^_^   |        |   |
|  +--------+--------+--------+--------+   |
|  |        |        |        |        |   |
|  |   96   |   2    |   6    |   3    |   |
|  |  >_<   |        |  ^_^   |  ^_^   |   |
|  +--------+--------+--------+--------+   |
|                                          |
|  Swipe to move tiles. Match numbers!     |
|                                          |
+------------------------------------------+
```

### 11.1 Next Tile Preview

- Small tile (40x40px) shown above the edge where the next tile will enter.
- Position updates based on the last swipe direction.
- Shows the tile color/category (not exact value for bonus tiles).
- Arrow indicator pointing to the edge.

### 11.2 Background

- Background color: #50C8FF (light blue) — changes based on highest tile:

| Highest Tile | Background Color |
|-------------|------------------|
| < 48        | #50C8FF (blue)   |
| 48-96       | #FFE066 (warm yellow) |
| 192-384     | #FF9944 (orange) |
| 768+        | #FF4444 (red)    |

---

## 12. Audio Design

### 12.1 Sound Effects

| Event                | Description                          | Duration |
|----------------------|--------------------------------------|----------|
| Tile slide           | Soft slide/scrape                    | 150 ms   |
| Tile merge (1+2)     | Two-tone chime (ascending)           | 200 ms   |
| Tile merge (3+3)     | Satisfying click                     | 150 ms   |
| Tile merge (high)    | Deeper, more resonant chime          | 200 ms   |
| New tile enter       | Soft pop                             | 100 ms   |
| Invalid move         | Subtle bump/resistance               | 100 ms   |
| Game over            | Gentle descending melody             | 1500 ms  |
| New high score       | Celebratory jingle                   | 1000 ms  |
| Tile blink (subtle)  | Barely audible blip (optional)       | 50 ms    |

### 12.2 Music

- Gentle, jazzy/lo-fi background music.
- Tempo: ~90 BPM.
- Instruments: Piano, soft synth, light percussion.
- Loops every ~2 minutes.
- Volume: Adjustable, default 40%.

---

## 13. Edge Cases

1. **All edge cells occupied on spawn side:** If the player swipes left and all cells in column 3 are occupied, but tiles did move, this is an edge case. In practice, if at least one cell on the spawn edge is empty, spawn there. If none are empty, do not spawn (extremely rare).

2. **No tiles can move:** Game over. Verify by checking all 4 directions for any possible slide or merge.

3. **Board full but merges possible:** Game continues. Only game over when zero valid moves exist.

4. **Bonus tile value selection:** Never spawn a bonus tile larger than max_tile / 8. If max_tile is 48, only 3 and 6 are valid bonus values.

5. **Deck depletion timing:** A new deck is shuffled when the previous deck is exhausted. The bonus tile chance is checked independently of the deck.

6. **Multiple merges in one swipe:** Each merge in a single swipe is independent. All happen simultaneously during the one-cell slide.

---

## 14. State Machine

```
[TITLE_SCREEN]
    --> [NEW_GAME]
        --> Initialize board with 9 tiles
        --> Initialize deck
        --> [WAITING_FOR_INPUT]

[WAITING_FOR_INPUT]
    --> (swipe detected)
        --> [VALIDATE_MOVE]
            --> (valid)
                --> [ANIMATE_SLIDE] (200ms)
                --> [SPAWN_NEW_TILE] (250ms)
                --> [UPDATE_SCORE]
                --> [CHECK_GAME_OVER]
                    --> (game over) --> [GAME_OVER_SCREEN]
                    --> (continue) --> [WAITING_FOR_INPUT]
            --> (invalid)
                --> [BOUNCE_ANIMATION] (100ms)
                --> [WAITING_FOR_INPUT]
    --> (new game) --> [NEW_GAME]

[GAME_OVER_SCREEN]
    --> [SCORE_BREAKDOWN] (show individual tile scores)
    --> (play again) --> [NEW_GAME]
```

---

## 15. Data Persistence

```json
{
  "board": [[3,0,1,6],[2,48,12,0],[0,3,24,1],[96,2,6,3]],
  "score": 1467,
  "best_score": 24680,
  "deck": [2,1,3,1,2],
  "next_tile": 1,
  "highest_tile": 96,
  "moves_made": 47
}
```

---

## 16. Difficulty Analysis

Threes! is significantly harder than 2048 because:
1. Tiles move only 1 cell (less control over placement).
2. 1 and 2 tiles are asymmetric (only combine with each other, not themselves).
3. New tiles enter from the opposite edge (more constrained).
4. The deck system provides some predictability but limits control.
5. Typical high scores: Casual players reach 48-192 as highest tile; expert players reach 768-3072.

---

## 17. Accessibility

- Colorblind mode: Add number labels with high contrast on all tiles (already present).
- Shape indicators: Add unique border patterns (dotted for 1s, dashed for 2s, solid for 3+).
- Screen reader: Announce board state on each move.
- Large text option: Scale tile numbers up by 25%.
- Reduced motion: Disable face animations and particle effects.

---

## 18. Performance Requirements

| Metric               | Target           |
|-----------------------|------------------|
| Input latency         | < 16ms           |
| Animation frame time  | < 16.67ms        |
| Memory usage          | < 15 MB          |
| Save/load             | < 10ms           |
| Initial load          | < 1 second       |

---

## 19. Testing Checklist

1. Tiles slide exactly 1 cell per swipe (not more).
2. 1 + 2 = 3 merge works correctly.
3. 1 + 1 does NOT merge.
4. 2 + 2 does NOT merge.
5. Equal tiles >= 3 merge correctly (3+3=6, 6+6=12, etc.).
6. Incompatible tiles block each other correctly.
7. New tile spawns from the correct edge (opposite to swipe).
8. Deck system cycles correctly (12 tiles per deck).
9. Bonus tile appears only when max tile >= 48.
10. Bonus tile value is always <= max_tile / 8.
11. Next tile preview shows correct category hint.
12. Score calculation matches the formula for all tile values.
13. Game over detection is correct.
14. Initial board has exactly 9 tiles.
15. Face animations render correctly on tiles >= 3.
16. Background color changes based on highest tile.
17. Invalid moves show bounce animation without spawning a tile.
18. Best score persists across games.
