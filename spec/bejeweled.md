# Bejeweled (Classic) — Complete Game Specification

## 1. Game Overview

**Title:** Bejeweled (Original / Bejeweled Classic)
**Genre:** Match-three puzzle
**Platform:** Single-player, mouse/touch-controlled
**Original Release:** 2001 (PopCap Games)
**Objective:** Swap adjacent gems on an 8x8 grid to create matches of three or more identical gems in a row or column. Score points, trigger cascades, and survive as long as possible.

---

## 2. Technical Foundation

### 2.1 Display

| Parameter            | Value                |
|----------------------|----------------------|
| Grid size            | 8 columns x 8 rows  |
| Cell size            | 64 x 64 pixels      |
| Grid pixel size      | 512 x 512 pixels     |
| Total canvas         | ~640 x 700 pixels    |
| Frame rate           | 60 FPS               |

### 2.2 Coordinate System

- Origin (0, 0) at top-left cell.
- X increases rightward (0..7).
- Y increases downward (0..7).

---

## 3. Gem Types

### 3.1 Standard Gems

| Gem ID | Color     | Shape      | Hex Color  |
|--------|-----------|------------|------------|
| 1      | Red       | Ruby       | #FF0000    |
| 2      | Orange    | Topaz      | #FF8C00    |
| 3      | Yellow    | Citrine    | #FFD700    |
| 4      | Green     | Emerald    | #00CC00    |
| 5      | Blue      | Sapphire   | #0066FF    |
| 6      | Purple    | Amethyst   | #9900CC    |
| 7      | White     | Diamond    | #FFFFFF    |

Total: 7 gem types.

### 3.2 Special Gems (Bejeweled 2+ / Classic variant)

In classic Bejeweled, special gems are not present. However, most modern re-releases include:

| Special Gem       | Created By                 | Effect                              |
|-------------------|----------------------------|-------------------------------------|
| Flame Gem         | Match of 4 in a row        | Explodes in a 3x3 area when matched |
| Hypercube         | Match of 5 in a row        | Destroys all gems of the color it's swapped with |
| Star Gem          | Match of 5 in T/L shape    | Destroys entire row and column      |

For this specification, we include the Classic (no specials) mode and the Enhanced mode.

---

## 4. Game Modes

### 4.1 Classic Mode (Untimed)

- No time pressure.
- Game ends when no valid moves remain on the board.
- Focus on strategy and high scores.

### 4.2 Timed Mode (Zen / Lightning)

- A time bar counts down.
- Making matches adds time to the bar.
- Game ends when the time bar empties.

For this specification, **Classic Mode** is the primary focus.

---

## 5. Core Mechanics

### 5.1 Gem Swapping

1. Player selects a gem by clicking on it (gem highlights with a border/glow).
2. Player clicks an adjacent gem (up, down, left, right — not diagonal).
3. If the swap creates a match (3+ in a row/column), the swap is performed.
4. If the swap does NOT create a match, the gems swap and then swap back (invalid move animation).
5. Only orthogonally adjacent swaps are allowed.

### 5.2 Match Detection

After every swap and cascade drop:

1. Scan all rows left-to-right for groups of 3+ consecutive same-type gems.
2. Scan all columns top-to-bottom for groups of 3+ consecutive same-type gems.
3. Mark all matched gems for removal.
4. A gem can be part of both a horizontal and vertical match simultaneously (T-shape, L-shape, cross).

```
Match detection algorithm (pseudocode):

for each row y:
    run_start = 0
    for x from 1 to 8:
        if grid[y][x] != grid[y][run_start] or x == 8:
            run_length = x - run_start
            if run_length >= 3:
                mark cells (run_start..x-1, y) as matched
            run_start = x

for each column x:
    run_start = 0
    for y from 1 to 8:
        if grid[y][x] != grid[run_start][x] or y == 8:
            run_length = y - run_start
            if run_length >= 3:
                mark cells (x, run_start..y-1) as matched
            run_start = y
```

### 5.3 Match Clearing and Gravity

1. All matched gems are removed simultaneously (with animation).
2. Gems above empty cells fall downward to fill gaps (gravity).
3. New random gems spawn at the top of each column to fill remaining empty cells.
4. After gems settle, scan for new matches (cascade).
5. Repeat until no new matches are found.

### 5.4 Cascade System

- Each cascade level is counted (first match = level 1, cascades = level 2, 3, ...).
- Cascade bonus increases the point multiplier.
- Cascades are entirely emergent (player doesn't control them).

---

## 6. Scoring System

### 6.1 Base Scores

| Match Type            | Base Points |
|-----------------------|-------------|
| 3-gem match           | 50          |
| 4-gem match           | 100         |
| 5-gem match           | 150         |
| 6+ gem match          | 200 + 50 per additional gem |

### 6.2 Cascade Multiplier

| Cascade Level | Multiplier |
|---------------|------------|
| 1 (initial)   | 1x         |
| 2             | 2x         |
| 3             | 3x         |
| 4             | 4x         |
| 5             | 5x         |
| 6+            | 5x (cap)   |

**Points per match = base_points x cascade_multiplier**

### 6.3 Simultaneous Matches

If a single swap/cascade creates multiple matches simultaneously, each match is scored independently at the same cascade level.

Example: An L-shaped match of 5 gems = one 3-match (horizontal) + one 3-match (vertical) = 50 + 50 = 100 points (no double-counting of the corner gem for scoring, but it contributes to both match detections).

### 6.4 Special Gem Scoring (Enhanced Mode)

| Special Gem Action    | Points          |
|-----------------------|-----------------|
| Flame Gem explosion   | 50 per gem destroyed in 3x3 area |
| Hypercube activation  | 100 per gem destroyed of that color |
| Star Gem activation   | 50 per gem destroyed in row+column |

---

## 7. Board Generation

### 7.1 Initial Board

1. Fill all 64 cells with random gem types (7 types).
2. After filling, scan for any pre-existing matches.
3. If matches exist, regenerate the offending gems until no matches are present.
4. Verify at least one valid move exists.
5. If no valid moves, regenerate the entire board.

### 7.2 New Gem Generation (During Play)

- When new gems drop from the top, they are randomly selected from the 7 types.
- No guarantee against immediate matches (matches from drops trigger cascades, which is desirable).

### 7.3 Ensuring Valid Moves

After each cascade chain resolves:
1. Check if any valid swap exists on the board.
2. A valid swap is one where swapping two adjacent gems would create a match of 3+.
3. If no valid swaps exist in Classic mode: **Game Over**.
4. If no valid swaps exist in Timed mode: Reshuffle the board (keeping the same gem distribution but rearranging positions).

```
Valid move check (pseudocode):

for each cell (x, y):
    for each neighbor (nx, ny) of (x, y):
        temp_swap(grid, (x,y), (nx,ny))
        if has_match(grid):
            return True  # at least one valid move
        undo_swap(grid, (x,y), (nx,ny))
return False
```

---

## 8. Hint System

- If the player is idle for 10 seconds, a hint is displayed.
- The hint highlights one valid swap by making the gem glow/pulse.
- Hints do not penalize the player (no score deduction).
- The hint selects any valid move (not necessarily the best one).
- Hint animation: Gem pulses (scale 1.0 to 1.1 at 2Hz) with a golden glow (#FFD700, 40% opacity).

---

## 9. Level Progression

### 9.1 Level Bar

- A progress bar fills as the player scores points.
- When the bar reaches 100%, the level increments and the bar resets.

### 9.2 Points Required Per Level

| Level | Points to Next Level |
|-------|---------------------|
| 1     | 1,000               |
| 2     | 1,500               |
| 3     | 2,000               |
| 4     | 2,500               |
| 5     | 3,000               |
| 6     | 3,500               |
| 7     | 4,000               |
| 8     | 4,500               |
| 9     | 5,000               |
| 10+   | 5,000 + 500*(level-10) |

### 9.3 Level Effects

- Background changes color/theme each level.
- Background designs cycle through preset patterns.
- No gameplay changes (gem count, speed) in Classic mode.
- In Timed mode, time drain increases slightly per level.

---

## 10. Animations and Timing

### 10.1 Animation Durations

| Animation              | Duration (ms) | Easing            |
|------------------------|---------------|-------------------|
| Gem selection highlight | Immediate    | N/A               |
| Swap animation         | 200           | Ease-in-out       |
| Invalid swap (bounce)  | 300           | Ease-out-bounce   |
| Match clear (fade/pop) | 300           | Ease-out          |
| Gem fall (per cell)    | 100           | Ease-in (gravity) |
| New gem entry          | 100           | Ease-in           |
| Level up transition    | 1000          | Fade              |
| Hint pulse             | 500 (loop)    | Sine wave         |

### 10.2 Gem Fall Physics

- Each gem falls at a constant acceleration.
- Fall speed: 100ms per cell (so a gem falling 3 cells takes 300ms).
- Slight bounce on landing (10% overshoot, 50ms settle).

### 10.3 Match Clear Effect

- Matched gems flash white (100ms).
- Then scale down to 0 while fading out (200ms).
- Particle burst: 5-8 small particles fly outward from each gem (random angles, speed 100-300px/s, lifetime 400ms, fade out).
- Particles match the color of the cleared gem.

---

## 11. Visual Design

### 11.1 Gem Rendering

Each gem is rendered as:
1. Base color fill (rounded rectangle or circle, 56x56px with 4px margin).
2. Highlight gradient (top-left to center, white at 30% opacity).
3. Shadow (bottom-right, dark at 20% opacity, 2px offset).
4. Shape icon overlay (ruby facet pattern, emerald cut, etc.) — or simple geometric shapes for simpler implementation.

### 11.2 Selected Gem

- White border (3px) around the selected gem.
- Subtle pulsing glow (white, 40% opacity, frequency 1.5Hz).

### 11.3 Board Background

- Dark panel behind the grid (#1A1A2E).
- Grid lines: subtle (#2A2A4E, 1px).
- Outer border: golden frame (#B8860B, 3px).

### 11.4 Score Display

```
+------------------------------------------+
|  BEJEWELED CLASSIC                       |
+------------------------------------------+
|  SCORE: 0,025,600    LEVEL: 5            |
|  [=========>          ] 65%              |
+------------------------------------------+
|                                          |
|  +--+--+--+--+--+--+--+--+              |
|  |RU|TO|CI|EM|SA|AM|DI|RU|              |
|  +--+--+--+--+--+--+--+--+              |
|  |SA|EM|RU|TO|CI|RU|SA|EM|              |
|  +--+--+--+--+--+--+--+--+              |
|  |CI|RU|SA|AM|DI|TO|CI|AM|              |
|  +--+--+--+--+--+--+--+--+              |
|  |TO|DI|AM|RU|SA|EM|TO|DI|              |
|  +--+--+--+--+--+--+--+--+              |
|  |AM|SA|TO|DI|RU|CI|AM|SA|              |
|  +--+--+--+--+--+--+--+--+              |
|  |EM|CI|DI|SA|TO|AM|RU|CI|              |
|  +--+--+--+--+--+--+--+--+              |
|  |DI|AM|EM|CI|AM|DI|SA|TO|              |
|  +--+--+--+--+--+--+--+--+              |
|  |RU|TO|CI|EM|SA|RU|EM|AM|              |
|  +--+--+--+--+--+--+--+--+              |
|                                          |
+------------------------------------------+
```

---

## 12. UI Layout

### 12.1 Main Game Screen

```
+--------------------------------------------------+
|  [Menu]     BEJEWELED CLASSIC        [Sound] [?]  |
+--------------------------------------------------+
|                                                    |
|  SCORE           LEVEL          HIGH SCORE         |
|  0,025,600       5              0,150,200          |
|                                                    |
|  Level Progress:                                   |
|  [=================>                    ] 65%      |
|                                                    |
|  +----+----+----+----+----+----+----+----+         |
|  | RU | TO | CI | EM | SA | AM | DI | RU |         |
|  +----+----+----+----+----+----+----+----+         |
|  | SA | EM | RU | TO | CI | RU | SA | EM |         |
|  +----+----+----+----+----+----+----+----+         |
|  | CI | RU | SA | AM | DI | TO | CI | AM |         |
|  +----+----+----+----+----+----+----+----+         |
|  | TO | DI | AM | RU | SA | EM | TO | DI |         |
|  +----+----+----+----+----+----+----+----+         |
|  | AM | SA | TO | DI | RU | CI | AM | SA |         |
|  +----+----+----+----+----+----+----+----+         |
|  | EM | CI | DI | SA | TO | AM | RU | CI |         |
|  +----+----+----+----+----+----+----+----+         |
|  | DI | AM | EM | CI | AM | DI | SA | TO |         |
|  +----+----+----+----+----+----+----+----+         |
|  | RU | TO | CI | EM | SA | RU | EM | AM |         |
|  +----+----+----+----+----+----+----+----+         |
|                                                    |
|                  MOVES: 47                         |
+--------------------------------------------------+
```

---

## 13. Audio Design

### 13.1 Sound Effects

| Event                  | Description                           | Duration |
|------------------------|---------------------------------------|----------|
| Gem select             | Light chime / click                   | 100 ms   |
| Gem swap               | Whoosh/slide                          | 200 ms   |
| Invalid swap           | Dull thud / buzz                      | 200 ms   |
| Match 3                | Bright chime (C5)                     | 300 ms   |
| Match 4                | Higher chime (E5)                     | 300 ms   |
| Match 5                | Ascending arpeggio (C5-E5-G5)         | 400 ms   |
| Cascade level 1        | Base pitch                            | 300 ms   |
| Cascade level 2        | Pitch +2 semitones                    | 300 ms   |
| Cascade level 3        | Pitch +4 semitones                    | 300 ms   |
| Cascade level 4+       | Pitch +6 semitones                    | 300 ms   |
| Flame gem create       | Fire ignition whoosh                  | 400 ms   |
| Flame gem explode      | Explosion                             | 500 ms   |
| Hypercube create       | Ethereal shimmer                      | 500 ms   |
| Hypercube activate     | Lightning zap across board            | 800 ms   |
| Level up               | Triumphant fanfare                    | 1500 ms  |
| Game over              | Descending sad tones                  | 2000 ms  |
| Hint appear            | Soft twinkle                          | 300 ms   |
| No moves warning       | Alarm chime                           | 500 ms   |

### 13.2 Music

- Background music: Calm, ambient, slightly mysterious electronic/orchestral loop.
- Tempo: ~100 BPM, does not change with level.
- Music loops seamlessly every 90-120 seconds.
- Separate volume controls for SFX and Music.

---

## 14. Special Gem Mechanics (Enhanced Mode)

### 14.1 Flame Gem

- Created when 4 gems are matched in a line.
- Appears at the position of the 4th gem (or center of the match).
- When the Flame Gem is matched in a subsequent match, it explodes.
- Explosion radius: 3x3 area centered on the Flame Gem.
- All gems in the 3x3 area are destroyed regardless of type.
- Chain reaction: If a Flame Gem explodes near another Flame Gem, the second one also explodes.

### 14.2 Hypercube

- Created when 5 gems are matched in a straight line.
- The Hypercube is a special piece that does not have a gem type.
- Rendered as a multicolored/rainbow cube with sparkle effects.
- Activation: Swap the Hypercube with any adjacent gem.
- Effect: All gems of the swapped gem's type on the entire board are destroyed.
- If swapped with another Hypercube: ALL gems on the board are destroyed (board clear).

### 14.3 Star Gem (T/L shape match)

- Created when gems match in a T-shape or L-shape (5 gems total).
- When matched, destroys the entire row AND column intersecting at its position.

### 14.4 Special Gem Interactions

| Swap Combination           | Result                                          |
|----------------------------|--------------------------------------------------|
| Flame + Flame              | 5x5 explosion                                    |
| Flame + Star               | 3 rows + 3 columns destroyed                     |
| Flame + Hypercube          | All gems of one type become Flame Gems, then explode |
| Star + Star                | All rows and columns destroyed (full board clear) |
| Star + Hypercube           | All gems of one type become Star Gems, then activate |
| Hypercube + Hypercube      | Entire board cleared                              |

---

## 15. Game Over

### 15.1 Classic Mode Game Over

1. After all cascades resolve, check for valid moves.
2. If no valid moves exist, display "NO MORE MOVES" message.
3. Animate remaining gems shattering/fading row by row from bottom to top (2 seconds total).
4. Display Game Over screen with final score.

### 15.2 Game Over Screen

```
+----------------------------------+
|                                  |
|         GAME OVER                |
|                                  |
|    Final Score:  0,150,200       |
|    Level:        12              |
|    Moves Made:   347             |
|    Cascades:     89              |
|    Best Cascade: 7 levels        |
|                                  |
|    [ PLAY AGAIN ]                |
|    [ MAIN MENU  ]                |
|                                  |
+----------------------------------+
```

---

## 16. Menus

### 16.1 Main Menu

```
+----------------------------------+
|                                  |
|      ✦ B E J E W E L E D ✦      |
|                                  |
|       [ CLASSIC MODE ]           |
|       [ TIMED MODE   ]           |
|       [ SETTINGS     ]           |
|       [ HIGH SCORES  ]           |
|                                  |
+----------------------------------+
```

### 16.2 Settings

| Setting              | Options                    | Default |
|----------------------|----------------------------|---------|
| Music Volume         | 0-100% (slider)            | 70%     |
| SFX Volume           | 0-100% (slider)            | 80%     |
| Hint Delay           | 5s / 10s / 15s / Off       | 10s     |
| Special Gems         | On / Off (Classic only)    | On      |
| Animations           | Full / Reduced / Off       | Full    |
| Colorblind Mode      | On / Off                   | Off     |
| Background Theme     | Classic / Space / Ocean    | Classic |

---

## 17. Timed Mode Specifics

### 17.1 Time Bar

- Initial time: 60 seconds.
- Time drains at 1 second per second.
- Time gained per match:

| Match Type      | Time Added (seconds) |
|-----------------|---------------------|
| 3-gem match     | +3                  |
| 4-gem match     | +5                  |
| 5-gem match     | +8                  |
| Cascade bonus   | +2 per cascade level |

### 17.2 Time Bar Visual

- Full bar: green (#00FF00).
- Below 50%: transitions to yellow (#FFFF00).
- Below 25%: transitions to red (#FF0000) and pulses.
- Below 10%: fast pulse (3Hz) with warning sound.

### 17.3 Level Advancement (Timed)

- Each level requires clearing a set number of gems:

| Level | Gems to Clear |
|-------|--------------|
| 1     | 50           |
| 2     | 75           |
| 3     | 100          |
| 4     | 125          |
| 5+    | 125 + 25*(level-5) |

- Time drain rate increases by 5% per level.

---

## 18. State Machine

```
[MAIN_MENU]
    --> [CLASSIC_MODE] or [TIMED_MODE]
        --> [BOARD_INIT] (generate valid board)
        --> [WAITING_FOR_INPUT]
            --> [GEM_SELECTED] (first gem clicked)
                --> [SWAP_ANIMATION] (second gem clicked, valid adjacent)
                    --> [MATCH_CHECK]
                        --> [MATCH_CLEAR_ANIMATION] (if matches found)
                            --> [GEM_FALL_ANIMATION]
                                --> [MATCH_CHECK] (cascade loop)
                        --> [VALID_MOVE_CHECK] (if no matches)
                            --> [WAITING_FOR_INPUT] (if valid moves exist)
                            --> [GAME_OVER]
                --> [INVALID_SWAP_ANIMATION] (no match created)
                    --> [WAITING_FOR_INPUT]
                --> [DESELECT] (same gem clicked again)
                    --> [WAITING_FOR_INPUT]
        --> [PAUSED]
            --> [WAITING_FOR_INPUT] (resume)
            --> [MAIN_MENU] (quit)
    --> [SETTINGS]
    --> [HIGH_SCORES]

[GAME_OVER]
    --> [MAIN_MENU]
    --> [BOARD_INIT] (play again)
```

---

## 19. Particle Effects

### 19.1 Match Clear Particles

- Per cleared gem: 6-10 small diamond-shaped particles.
- Size: 4x4 to 8x8 pixels.
- Color: Same as the cleared gem, with slight brightness variation.
- Velocity: Random direction, speed 100-400 px/s.
- Lifetime: 300-600 ms.
- Fade: Linear fade from 100% to 0% opacity over lifetime.
- Gravity: Slight downward pull (200 px/s^2).

### 19.2 Explosion Particles (Flame Gem)

- 20-30 particles per explosion.
- Colors: Orange (#FF6600), Yellow (#FFCC00), Red (#FF0000).
- Size: 6x6 to 12x12 pixels.
- Speed: 200-600 px/s.
- Lifetime: 400-800 ms.

### 19.3 Hypercube Lightning

- Animated lines from the Hypercube to each target gem.
- Color: White with blue (#00AAFF) glow.
- Width: 2px, with 6px glow.
- Duration: 50ms per target gem (staggered).
- Total animation: ~400ms for a full board sweep.

### 19.4 Score Popups

- When gems are cleared, a score popup appears at the match center.
- Font: Bold, 18px, white with black 2px outline.
- Animation: Float upward 40px over 800ms, fade out in last 300ms.
- Cascade level indicator: "x2", "x3", etc. appended to score popup.

---

## 20. Edge Cases

1. **Multiple simultaneous matches from one swap:** All matches at the same cascade level. Score each independently.
2. **T-shape / L-shape / Cross matches:** Counted as a single match of the total number of gems involved. Creates a Star Gem at the intersection.
3. **Board stalemate prevention:** In Timed mode, if no moves exist, shuffle the board immediately. In Classic mode, end the game.
4. **Gem fall ordering:** All gems in a column fall simultaneously. Columns are independent.
5. **Special gem in cascade:** If a special gem is created by a cascade and immediately matched in the next cascade step, it activates.
6. **Maximum cascade depth:** No artificial limit. The cascade continues until the board stabilizes.
7. **Score overflow:** Use 64-bit integer for score storage. Display up to 9,999,999 on screen (use abbreviations beyond: 10.0M, etc.).

---

## 21. Data Persistence

### 21.1 High Scores

- Store top 10 scores per game mode.
- Fields: Rank, Name, Score, Level, Date.
- Storage: localStorage or JSON file.

### 21.2 Statistics

Track and display:
- Total games played
- Total gems cleared
- Longest cascade chain
- Highest single move score
- Total play time

---

## 22. Accessibility

- **Colorblind mode:** Each gem type has a unique shape symbol rendered on top (circle, square, triangle, diamond, star, hexagon, cross).
- **Keyboard controls:** Arrow keys to move selection cursor, Space/Enter to select, Escape to deselect.
- **Screen reader:** Announce gem type and position on selection, match results.
- **Reduced motion:** Option to disable particle effects and reduce animation duration by 50%.

---

## 23. Performance Requirements

| Metric               | Target           |
|-----------------------|------------------|
| Input latency         | < 50ms           |
| Frame time            | < 16.67ms        |
| Particle count max    | 200 simultaneous |
| Memory usage          | < 30 MB          |
| Load time             | < 2 seconds      |

---

## 24. Implementation Notes

### 24.1 Board Representation

```
board[y][x] = { type: 1-7, special: null|'flame'|'hypercube'|'star' }
```

### 24.2 Match Finding

```python
def find_matches(board):
    matched = set()
    # Horizontal
    for y in range(8):
        for x in range(6):  # max start for 3-match
            if board[y][x].type == board[y][x+1].type == board[y][x+2].type:
                run = 3
                while x+run < 8 and board[y][x+run].type == board[y][x].type:
                    run += 1
                for i in range(run):
                    matched.add((x+i, y))
    # Vertical (same logic, transposed)
    for x in range(8):
        for y in range(6):
            if board[y][x].type == board[y+1][x].type == board[y+2][x].type:
                run = 3
                while y+run < 8 and board[y+run][x].type == board[y][x].type:
                    run += 1
                for i in range(run):
                    matched.add((x, y+i))
    return matched
```

### 24.3 Gravity Fill

```python
def apply_gravity(board):
    for x in range(8):
        # Collect non-empty cells from bottom to top
        column = [board[y][x] for y in range(7, -1, -1) if board[y][x] is not None]
        # Fill from bottom
        for y in range(7, -1, -1):
            idx = 7 - y
            if idx < len(column):
                board[y][x] = column[idx]
            else:
                board[y][x] = random_gem()
```

---

## 25. Testing Checklist

1. Board generation produces no initial matches and has at least one valid move.
2. All 7 gem types appear in roughly equal distribution over 1000 generated gems.
3. Match detection correctly identifies horizontal matches of 3, 4, 5, 6, 7, and 8.
4. Match detection correctly identifies vertical matches of 3, 4, 5, 6, 7, and 8.
5. T-shape, L-shape, and cross-shape matches are detected correctly.
6. Invalid swaps are rejected and animate correctly.
7. Cascade scoring applies correct multipliers at each level.
8. Flame Gem creation on 4-match, Hypercube on 5-match, Star on T/L-match.
9. Special gem chain reactions work (Flame near Flame, etc.).
10. Hypercube + Hypercube clears entire board.
11. Game over detection works when no valid moves remain.
12. Hint system activates after the configured idle time.
13. Score popups appear at correct positions with correct values.
14. Level progression bar fills and resets correctly.
15. Timed mode time bar drains and refills correctly.
16. High scores save and load correctly.
17. All animations complete without visual glitches.
18. Colorblind mode renders distinct symbols on each gem type.
