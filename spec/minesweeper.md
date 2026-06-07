# Minesweeper — Complete Game Specification

## 1. Game Overview

**Title:** Minesweeper
**Genre:** Logic / deduction puzzle
**Platform:** Single-player, mouse-controlled
**Original Release:** 1990 (Microsoft, Robert Donner & Curt Johnson)
**Objective:** Reveal all cells on a grid that do NOT contain mines. Each revealed cell shows the count of adjacent mines. Use logic to determine which cells are safe and flag the mines. The game is won when all non-mine cells are revealed; the game is lost when a mine is revealed.

---

## 2. Technical Foundation

### 2.1 Display

| Parameter            | Value                    |
|----------------------|--------------------------|
| Cell size            | 24 x 24 pixels (classic) or 30 x 30 (modern) |
| Border               | 3D-style beveled edges (classic) or flat (modern) |
| Frame rate           | 30-60 FPS (low resource usage) |
| Timer resolution     | 1 second                  |

### 2.2 Difficulty Presets

| Difficulty   | Grid Width | Grid Height | Mines | Mine Density |
|-------------|-----------|-------------|-------|-------------|
| Beginner    | 9         | 9           | 10    | 12.3%       |
| Intermediate| 16        | 16          | 40    | 15.6%       |
| Expert      | 30        | 16          | 99    | 20.6%       |
| Custom      | 8-50      | 8-50        | 1-999 | Variable    |

### 2.3 Custom Difficulty Constraints

- Minimum grid: 8 x 8
- Maximum grid: 50 x 50
- Minimum mines: 1
- Maximum mines: (width * height) - 9 (must leave at least 9 cells mine-free for the first click safe zone)

---

## 3. Cell States

### 3.1 Cell Data Model

```python
class Cell:
    has_mine: bool          # True if cell contains a mine
    state: CellState        # HIDDEN, REVEALED, FLAGGED, QUESTION
    adjacent_mines: int     # 0-8 count of mines in 8 neighbors

class CellState(Enum):
    HIDDEN = 0      # Default, covered cell
    REVEALED = 1    # Uncovered, showing number or blank
    FLAGGED = 2     # Player placed a flag (thinks mine is here)
    QUESTION = 3    # Player placed a question mark (uncertain)
```

### 3.2 Visual States

| State           | Visual (Classic)                        | Visual (Modern)              |
|-----------------|-----------------------------------------|------------------------------|
| Hidden          | Raised 3D button, gray (#C0C0C0)       | Rounded square, #B8B8B8     |
| Revealed (0)    | Flat, sunken, empty, light gray         | White/cream, no number      |
| Revealed (1)    | Blue number "1" (#0000FF)               | Blue "1"                    |
| Revealed (2)    | Green number "2" (#008000)              | Green "2"                   |
| Revealed (3)    | Red number "3" (#FF0000)                | Red "3"                     |
| Revealed (4)    | Dark blue number "4" (#000080)          | Dark blue "4"               |
| Revealed (5)    | Dark red number "5" (#800000)           | Maroon "5"                  |
| Revealed (6)    | Cyan number "6" (#008080)               | Teal "6"                    |
| Revealed (7)    | Black number "7" (#000000)              | Black "7"                   |
| Revealed (8)    | Gray number "8" (#808080)               | Gray "8"                    |
| Flagged         | Red flag icon on hidden cell            | Flag emoji or red marker    |
| Question        | Blue "?" on hidden cell                 | "?" marker                  |
| Mine (revealed) | Black circle/bomb on white background   | Bomb icon, red background   |
| Mine (death)    | Red background behind the clicked mine  | Red explosion               |
| Wrong flag      | Flag with X through it (on game over)   | Red X over flag             |

### 3.3 Number Colors (Exact)

| Number | Classic Color | Modern Color  |
|--------|-------------|---------------|
| 1      | #0000FF     | #1565C0       |
| 2      | #008000     | #2E7D32       |
| 3      | #FF0000     | #C62828       |
| 4      | #000080     | #283593       |
| 5      | #800000     | #6A1B29       |
| 6      | #008080     | #00838F       |
| 7      | #000000     | #424242       |
| 8      | #808080     | #9E9E9E       |

---

## 4. Core Mechanics

### 4.1 Mine Placement

Mines are placed AFTER the first click. This ensures the first click is always safe.

1. Player clicks a cell.
2. Generate mine positions randomly, excluding:
   - The clicked cell.
   - All 8 neighbors of the clicked cell (guarantees a 3x3 safe zone around the first click).
3. Calculate adjacent_mines for every cell.

```python
def place_mines(width, height, mine_count, first_click_x, first_click_y):
    excluded = set()
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = first_click_x + dx, first_click_y + dy
            if 0 <= nx < width and 0 <= ny < height:
                excluded.add((nx, ny))

    available = [(x, y) for x in range(width) for y in range(height)
                 if (x, y) not in excluded]

    mine_positions = random.sample(available, mine_count)

    board = [[Cell() for _ in range(width)] for _ in range(height)]
    for (mx, my) in mine_positions:
        board[my][mx].has_mine = True

    # Calculate adjacency counts
    for y in range(height):
        for x in range(width):
            if not board[y][x].has_mine:
                count = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if board[ny][nx].has_mine:
                                count += 1
                board[y][x].adjacent_mines = count

    return board
```

### 4.2 Cell Reveal (Left Click)

1. If the cell is FLAGGED or QUESTION: Ignore the click (do nothing).
2. If the cell has a mine: Game Over (loss).
3. If the cell has adjacent_mines > 0: Reveal this cell, show the number.
4. If the cell has adjacent_mines == 0: Reveal this cell AND automatically reveal all adjacent cells (flood fill / chord reveal).

### 4.3 Flood Fill (Auto-Reveal)

When a cell with 0 adjacent mines is revealed:

```python
def flood_reveal(board, x, y):
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if board[cy][cx].state == REVEALED:
            continue
        board[cy][cx].state = REVEALED
        if board[cy][cx].adjacent_mines == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if board[ny][nx].state == HIDDEN:
                            stack.append((nx, ny))
```

### 4.4 Flagging (Right Click)

Right-clicking a hidden cell cycles through states:
1. HIDDEN -> FLAGGED (place flag)
2. FLAGGED -> QUESTION (place question mark)
3. QUESTION -> HIDDEN (remove marker)

Optional setting: Skip question marks (HIDDEN -> FLAGGED -> HIDDEN).

### 4.5 Chord Reveal (Double Click / Middle Click)

When a revealed number cell is clicked (left+right simultaneously, or middle click):
1. Count the number of flagged cells adjacent to this cell.
2. If the flag count equals the cell's number:
   - Reveal all non-flagged, non-revealed adjacent cells.
   - If any of those cells have mines: Game Over (the player flagged incorrectly).
3. If the flag count does not equal the number: Do nothing (or briefly highlight the adjacent cells).

```python
def chord_reveal(board, x, y):
    cell = board[y][x]
    if cell.state != REVEALED or cell.adjacent_mines == 0:
        return

    flag_count = 0
    hidden_neighbors = []
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if board[ny][nx].state == FLAGGED:
                    flag_count += 1
                elif board[ny][nx].state == HIDDEN:
                    hidden_neighbors.append((nx, ny))

    if flag_count == cell.adjacent_mines:
        for (nx, ny) in hidden_neighbors:
            if board[ny][nx].has_mine:
                game_over(loss=True, clicked=(nx, ny))
                return
            reveal(board, nx, ny)
```

---

## 5. Win and Loss Conditions

### 5.1 Win

The game is won when all non-mine cells are revealed.

```python
def check_win(board):
    for y in range(height):
        for x in range(width):
            if not board[y][x].has_mine and board[y][x].state != REVEALED:
                return False
    return True
```

On win:
1. All remaining mines are automatically flagged.
2. Timer stops.
3. Smiley face changes to sunglasses face.
4. "You Win!" overlay or message.
5. If the time is a new best for this difficulty, display "New Record!".

### 5.2 Loss

The game is lost when a mine cell is revealed.

On loss:
1. The clicked mine is shown with a red background.
2. All other mines are revealed (shown as mine icons).
3. Any incorrectly placed flags (flagged cells without mines) are shown with an X.
4. Timer stops.
5. Smiley face changes to dead face (X eyes).
6. All input is disabled until the player starts a new game.

---

## 6. Timer

### 6.1 Timer Rules

- Timer starts on the first click (not on game load).
- Timer counts up in whole seconds (000 to 999).
- Timer stops on win or loss.
- Timer does not run during paused state.
- Timer wraps at 999 (stays at 999 if exceeded).
- Display: 3-digit LED-style number display.

### 6.2 Timer Display

```
Classic LED style:
+-----+-----+-----+
| 0   | 4   | 2   |  = 042 seconds
+-----+-----+-----+
```

Each digit rendered as a 7-segment display:
- Segment color (active): #FF0000 (red)
- Segment color (inactive): #400000 (dark red, barely visible)
- Background: #000000 (black)
- Digit size: 13 x 23 pixels (classic) or 20 x 36 pixels (modern)

---

## 7. Mine Counter

### 7.1 Mine Counter Rules

- Displays: total_mines - flags_placed.
- Can go negative (if more flags than mines are placed).
- Range: -99 to 999.
- Updated immediately when a flag is placed or removed.

### 7.2 Mine Counter Display

Same LED style as timer, positioned on the left side of the header.

---

## 8. Smiley Face Button

### 8.1 Smiley States

| State            | Face        | When                              |
|------------------|-------------|-----------------------------------|
| Default          | :)          | Normal gameplay                   |
| Pressed cell     | :O          | While mouse button is held down   |
| Win              | B)          | Game won (sunglasses)             |
| Loss             | X(          | Game lost (dead)                  |

### 8.2 Behavior

- Clicking the smiley face starts a new game with the same difficulty settings.
- The smiley face is always clickable (even during game over).
- Size: 26 x 26 pixels (classic) or 36 x 36 pixels (modern).
- Position: Centered in the header bar.

---

## 9. UI Layout

```
+----------------------------------------------------+
|                                                    |
|  +------+        +------+         +------+         |
|  | 0 1 0 |       | :)   |        | 0 0 0 |         |
|  +------+        +------+         +------+         |
|  Mine Counter    Smiley            Timer            |
|                                                    |
+----------------------------------------------------+
|                                                    |
|  +--+--+--+--+--+--+--+--+--+                     |
|  |##|##|##|##|##|##|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|  |##|##|##| 1| 1|##|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|  |##| 1|  |  |  | 1|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|  |##| 1|  |  |  | 2|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|  | 1| 1|  | 1| 1| 2|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|  |  |  |  | 1|FL|##|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|  |  |  |  | 1| 2|##|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|  |  |  |  |  | 1|##|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|  | 1| 1|  |  | 1|##|##|##|##|                     |
|  +--+--+--+--+--+--+--+--+--+                     |
|                                                    |
|  ## = hidden   FL = flag   (blank) = revealed 0   |
+----------------------------------------------------+
```

### 9.1 Classic Layout (Windows Style)

- Outer border: 3D raised border (3px).
- Header area: Contains mine counter, smiley, timer.
- Header border: 3D sunken border (2px).
- Grid area: 3D sunken border (3px).
- Background color: #C0C0C0 (classic gray).

### 9.2 Modern Layout

- Flat design, no 3D borders.
- Rounded corners (4px border radius).
- Background: #F5F5F5 or theme color.
- Header: Clean bar with centered elements.

---

## 10. Animations

### 10.1 Cell Reveal Animation

| Animation              | Duration | Effect                           |
|------------------------|----------|----------------------------------|
| Single cell reveal     | 50 ms    | Button depression (3D: instant)  |
| Flood fill cascade     | Staggered | 20ms delay per wave from origin |
| Mine explosion (loss)  | 300 ms   | Red flash, slight shake          |
| Mine reveal (all)      | 500 ms   | Staggered reveal, 30ms per mine  |
| Win celebration        | 1000 ms  | Flag animations on remaining mines|
| Chord highlight        | 200 ms   | Adjacent cells briefly depress   |

### 10.2 Flood Fill Visual

- Cells are revealed in waves radiating outward from the clicked cell.
- Each wave adds ~20ms delay.
- Effect: Ripple-like spread of revealed cells.
- Performance: For large reveals (50+ cells), batch the rendering.

### 10.3 Game Over Shake (Optional)

- On mine hit: Screen shakes horizontally (4px amplitude, 100ms, 3 cycles).
- Mine cell flashes red (200ms pulse).

---

## 11. Audio Design

### 11.1 Sound Effects

| Event                    | Description                          | Duration |
|--------------------------|--------------------------------------|----------|
| Cell reveal (single)     | Light click                          | 50 ms    |
| Cell reveal (flood fill) | Multiple rapid clicks                | Variable |
| Flag place               | Metal click / stamp                  | 100 ms   |
| Flag remove              | Reverse click                        | 80 ms    |
| Question mark            | Short blip                           | 60 ms    |
| Chord reveal             | Multiple clicks                      | 200 ms   |
| Mine hit (game over)     | Explosion                            | 500 ms   |
| Win                      | Fanfare / victory chime              | 1500 ms  |
| New record               | Extra celebratory jingle             | 1000 ms  |
| Smiley click (new game)  | Reset / shuffle sound                | 200 ms   |
| Invalid action           | Subtle buzz (optional)               | 50 ms    |
| Timer tick (optional)    | Soft tick every second               | 50 ms    |

### 11.2 Music

- Minesweeper is traditionally silent (no background music).
- Optional: Very subtle ambient background.
- Volume: Adjustable, default 0% (off).

---

## 12. Menus

### 12.1 Menu Bar (Classic Style)

```
[Game] [Help]

Game:
  - New Game (F2)
  - Beginner
  - Intermediate
  - Expert
  - Custom...
  - -----------
  - Best Times
  - -----------
  - Exit

Help:
  - How to Play
  - About
```

### 12.2 Custom Difficulty Dialog

```
+----------------------------------+
|  Custom Field                    |
|                                  |
|  Width:  [  16  ]  (8-50)       |
|  Height: [  16  ]  (8-50)       |
|  Mines:  [  40  ]  (1-max)      |
|                                  |
|  [  OK  ]  [ Cancel ]           |
+----------------------------------+
```

### 12.3 Best Times Screen

```
+----------------------------------+
|  Best Times                      |
|                                  |
|  Beginner:     042 sec  (Name)  |
|  Intermediate: 120 sec  (Name)  |
|  Expert:       350 sec  (Name)  |
|                                  |
|  [ Reset ]  [ OK ]              |
+----------------------------------+
```

---

## 13. Settings

| Setting              | Options                    | Default       |
|----------------------|----------------------------|---------------|
| Question Marks       | On / Off                   | On            |
| Sound Effects        | On / Off                   | On            |
| Color Theme          | Classic / Modern / Dark    | Classic       |
| Cell Size            | Small / Medium / Large     | Medium        |
| First Click Safe     | On / Off                   | On (always)   |
| Safe Zone Size       | 1 (cell only) / 9 (3x3)   | 9 (3x3)      |
| Animation Speed      | Off / Normal / Slow        | Normal        |
| Show Timer           | On / Off                   | On            |

---

## 14. State Machine

```
[MAIN_MENU / GAME_READY]
    --> (click on cell)
        --> [FIRST_CLICK]
            --> Generate mines (avoiding clicked area)
            --> Reveal clicked cell
            --> Start timer
            --> [PLAYING]

[PLAYING]
    --> (left click on hidden cell)
        --> [REVEAL_CELL]
            --> (mine) --> [GAME_OVER_LOSS]
            --> (number > 0) --> Show number --> [PLAYING]
            --> (number = 0) --> [FLOOD_FILL] --> [CHECK_WIN]
    --> (right click on hidden cell)
        --> Cycle flag state --> [PLAYING]
    --> (chord click on revealed number)
        --> [CHORD_REVEAL]
            --> (mine found) --> [GAME_OVER_LOSS]
            --> (safe) --> [CHECK_WIN]
    --> (smiley click)
        --> [NEW_GAME]

[CHECK_WIN]
    --> (all non-mines revealed) --> [GAME_OVER_WIN]
    --> (not complete) --> [PLAYING]

[GAME_OVER_WIN]
    --> Flag remaining mines
    --> Stop timer
    --> Check for new record
    --> (smiley click or menu) --> [NEW_GAME]

[GAME_OVER_LOSS]
    --> Reveal all mines
    --> Show incorrect flags
    --> Stop timer
    --> (smiley click or menu) --> [NEW_GAME]

[NEW_GAME]
    --> Reset board
    --> Reset timer to 000
    --> Reset mine counter
    --> [GAME_READY]
```

---

## 15. Mouse Interaction Details

### 15.1 Left Button

| Target          | Action                                |
|-----------------|---------------------------------------|
| Hidden cell     | Reveal the cell                       |
| Flagged cell    | No action                             |
| Question cell   | Reveal the cell                       |
| Revealed cell   | No action (unless chord with right)   |
| Smiley          | New game                              |

### 15.2 Right Button

| Target          | Action                                |
|-----------------|---------------------------------------|
| Hidden cell     | Place flag                            |
| Flagged cell    | Place question mark (or unflag)       |
| Question cell   | Remove question mark (back to hidden) |
| Revealed cell   | No action                             |

### 15.3 Both Buttons / Middle Button (Chord)

| Target          | Action                                |
|-----------------|---------------------------------------|
| Revealed number | Chord reveal if flags match number    |
| Other           | No action                             |

### 15.4 Visual Feedback on Mouse Down

- When left button is held on a hidden cell: Cell appears depressed (sunken).
- When both buttons are held on a number: All hidden adjacent cells appear depressed.
- Smiley shows :O face while any cell is pressed.

---

## 16. Data Persistence

```json
{
  "best_times": {
    "beginner": {"time": 42, "name": "Anonymous", "date": "2024-03-15"},
    "intermediate": {"time": 120, "name": "Anonymous", "date": "2024-03-10"},
    "expert": {"time": 350, "name": "Anonymous", "date": "2024-02-28"}
  },
  "settings": {
    "question_marks": true,
    "sound": true,
    "theme": "classic",
    "cell_size": "medium"
  },
  "statistics": {
    "beginner": {"played": 150, "won": 95, "win_rate": 0.633, "streak": 3},
    "intermediate": {"played": 80, "won": 30, "win_rate": 0.375, "streak": 1},
    "expert": {"played": 45, "won": 5, "win_rate": 0.111, "streak": 0}
  }
}
```

---

## 17. Accessibility

- **Keyboard controls:** Arrow keys to navigate cells, Space to reveal, F to flag, Enter for chord.
- **Cursor highlight:** Current cell has a visible border/highlight.
- **Screen reader:** Announce cell position, state, and adjacent mine count.
- **High contrast mode:** Brighter number colors, thicker borders.
- **Colorblind mode:** Numbers include shape indicators (1=circle, 2=square, etc.) in addition to colors.
- **Large cell option:** Cell size up to 48x48 pixels for accessibility.

---

## 18. Edge Cases

1. **First click on corner:** The 3x3 safe zone is clipped to board bounds. Only 4 cells are excluded (corner + 3 neighbors).
2. **Too many mines for safe zone:** If mines > (width*height - 9), reduce the safe zone to just the clicked cell.
3. **Negative mine counter:** If more flags than mines are placed, counter shows negative (e.g., -03).
4. **Timer at 999:** Timer stops incrementing at 999 but game continues.
5. **Single-cell board:** 1x1 with 0 mines = instant win. Not practically useful but should not crash.
6. **All cells are mines (except 1):** Edge case for custom mode. First click is safe, game won immediately after revealing the only non-mine cell.
7. **Right-click during game over:** No effect.
8. **Rapid clicking:** All clicks should be processed in order. No double-reveal bugs.

---

## 19. Performance Requirements

| Metric               | Target           |
|-----------------------|------------------|
| Input latency         | < 16ms           |
| Flood fill (50x50)    | < 50ms           |
| Mine generation       | < 10ms           |
| Memory usage          | < 10 MB          |
| Initial load          | < 500ms          |

---

## 20. Testing Checklist

1. First click is always safe (no mine at or adjacent to first click).
2. Mine count matches the specified difficulty.
3. Adjacent mine counts are correct for all cells.
4. Flood fill reveals correct set of cells.
5. Flagging cycles correctly (hidden -> flag -> question -> hidden).
6. Mine counter updates correctly with flag placement/removal.
7. Timer starts on first click, not before.
8. Timer stops on win and loss.
9. Chord reveal works correctly when flag count matches number.
10. Chord reveal triggers game over when incorrect flags are present.
11. Win condition detected correctly.
12. Loss reveals all mines and marks incorrect flags.
13. Smiley face states change correctly.
14. Custom difficulty validates input ranges.
15. Best times save and display correctly.
16. All three difficulty presets have correct grid/mine counts.
17. Right-click on revealed cells has no effect.
18. Question marks can be disabled in settings.
19. Game works correctly at maximum board size (50x50).
20. Performance is acceptable for expert-level flood fills.
