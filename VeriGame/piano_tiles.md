# Piano Tiles (Don't Tap the White Tile) — Complete Game Specification

## 1. Game Overview

**Title:** Piano Tiles / Don't Tap the White Tile
**Genre:** Casual / Rhythm / Reflex
**Platform:** Mobile (portrait), desktop
**Original Creator:** Hu Wen Zeng (Clean Master Games / Umoni Studio)
**Release Year:** 2014
**Core Loop:** Black and white tiles scroll upward on a 4-column grid. Tap only the black tiles. Tapping a white tile, missing a black tile that scrolls past, or running out of time ends the game. Play as fast as possible to score high.

Piano Tiles is a minimalist reflex game where rows of tiles scroll from the bottom to the top of the screen. Each row has one black tile and three white tiles (in the basic mode). The player must tap every black tile before it exits the top of the screen. The game tests speed and accuracy.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Portrait
- **Logical Resolution:** 320 x 568 pixels
- **Coordinate Origin:** Top-left (0, 0)
- **Frame Rate:** 60 FPS
- **Art Style:** High contrast black and white, clean geometric

### 2.2 Grid Layout
| Parameter          | Value                         |
|--------------------|-------------------------------|
| Columns            | 4                             |
| Column width       | 80 px each (320 / 4)         |
| Row height         | 142 px (568 / 4 visible rows)|
| Visible rows       | 4 (plus partial row at edges) |
| Column divider     | 1 px gray line                |

### 2.3 Rendering Layers
```
Layer 0: White background
Layer 1: Column divider lines
Layer 2: Black tiles
Layer 3: Tap effects (gray flash)
Layer 4: Score overlay
Layer 5: Game over panel
```

---

## 3. Game Modes

### 3.1 Classic Mode
- Tiles are static (no scrolling)
- Tap black tiles from bottom to top
- Each tap advances the grid by one row
- Score = number of tiles tapped
- Miss = tap white tile = game over
- No time limit

### 3.2 Arcade Mode (Rush)
- Tiles scroll upward continuously
- Speed increases over time
- Tap black tiles before they scroll off the top
- Missing a tile that exits the screen = game over
- Tapping white tile = game over
- Score = number of tiles tapped

### 3.3 Zen Mode
- 30-second time limit
- Tiles scroll at player speed (tap to advance)
- Score = tiles tapped in 30 seconds
- No penalty for tapping white (except wasted time)

### 3.4 Relay Mode
- Tiles scroll at increasing speeds
- Every 50 tiles, speed increases by a level
- Score = total tiles tapped before failure

---

## 4. Tile System

### 4.1 Tile Properties

| Parameter          | Value                         |
|--------------------|-------------------------------|
| Black tile color   | #1A1A1A                       |
| White tile color   | #FFFFFF                       |
| Tapped tile color  | #808080 (gray, briefly)       |
| Miss indicator     | #FF0000 (red flash)           |
| Tile gap           | 0 px (tiles are edge-to-edge) |
| Border lines       | 1 px, #CCCCCC                 |

### 4.2 Row Generation

Each row has exactly 1 black tile in one of 4 columns.

```
function generateRow():
    black_column = random(0, 3)  // 0, 1, 2, or 3
    return Row(black_column)

// Rule: black tile should not be in the same column
// for more than 2 consecutive rows (optional fairness rule)
// In original: no such restriction, purely random
```

### 4.3 Double Tile Rows (Advanced Mode)
In harder modes, rows can have 2 black tiles:
```
function generateHardRow():
    if difficulty > HARD and random() < 0.3:
        columns = random_2_unique(0, 3)
        return Row(black_columns=columns)
    else:
        return generateRow()  // single black tile
```

### 4.4 Long Tiles (Piano Mode)
For piano/song mode, some tiles are longer (held notes):
```
Long tile:
    height: 2-3 rows
    Require: tap AND hold until tile fully passes
    Release early = fail
    Column: spans single column across multiple rows
```

---

## 5. Core Mechanics

### 5.1 Classic Mode Mechanics

```
// Grid starts with 4 visible rows
// Bottom row is the active row (player must tap here)
// Tap black tile in bottom row: advance grid

on_tap(x, y):
    column = floor(x / column_width)  // 0-3
    row = bottom_visible_row

    if tiles[row][column] == BLACK:
        // Correct!
        tiles[row][column] = TAPPED (gray)
        score += 1
        advanceGrid()  // scroll down, new row appears at top
    elif tiles[row][column] == WHITE:
        // Wrong!
        tiles[row][column] = MISS (red)
        gameOver()

function advanceGrid():
    // Move all rows down by 1 row height
    // Remove bottom row (now off-screen)
    // Generate new row at top
    new_row = generateRow()
    grid.insert(0, new_row)
    grid.remove_last()

    // Animation: smooth scroll down over 50ms
```

### 5.2 Arcade Mode Mechanics

```
// Tiles scroll upward continuously
scroll_speed = base_speed  // pixels per frame

each_frame:
    for row in grid:
        row.y -= scroll_speed

    // Check if top row has exited screen
    if grid[0].y + row_height < 0:
        if grid[0].has_untapped_black_tile:
            gameOver()  // missed a tile
        grid.remove(0)

    // Generate new rows at bottom as needed
    while grid.last.y < screen_height:
        new_row = generateRow()
        new_row.y = grid.last.y + row_height
        grid.append(new_row)

on_tap(x, y):
    column = floor(x / column_width)

    // Find which row was tapped (by Y position)
    for row in grid:
        if y >= row.y and y < row.y + row_height:
            if row.tiles[column] == BLACK:
                row.tiles[column] = TAPPED
                score += 1
                playPianoNote(score)
            elif row.tiles[column] == WHITE:
                row.tiles[column] = MISS
                gameOver()
            break
```

### 5.3 Speed Scaling (Arcade Mode)

| Score Range | Speed (px/frame) | Tiles per second |
|-------------|-------------------|-----------------|
| 0 - 10     | 2.0               | ~0.85           |
| 10 - 25    | 3.0               | ~1.27           |
| 25 - 50    | 4.0               | ~1.69           |
| 50 - 100   | 5.0               | ~2.11           |
| 100 - 200  | 6.0               | ~2.54           |
| 200 - 500  | 7.0               | ~2.96           |
| 500+       | 8.0 (max)         | ~3.38           |

```
scroll_speed = min(2.0 + score * 0.03, 8.0)
```

---

## 6. Scoring

### 6.1 Score Calculation

| Mode     | Score Definition                          |
|----------|-------------------------------------------|
| Classic  | Total black tiles tapped                  |
| Arcade   | Total black tiles tapped before miss/fail |
| Zen      | Tiles tapped in 30 seconds               |
| Relay    | Total tiles tapped across speed levels    |

### 6.2 Score Display
- **During play:** Top-center of screen
- **Font:** Large, bold, black on white
- **Size:** ~36 px
- **Animation:** Scale pulse on increment (1.0 to 1.15 over 50ms, back to 1.0)

### 6.3 High Score
- Separate high score per game mode
- "NEW BEST!" indicator when beaten
- Stored in local storage

---

## 7. Piano Notes

### 7.1 Note Sequence
Each tap plays a piano note, creating a melody:

```
// Notes follow a musical scale or preset song
// For basic mode: ascending scale
notes = [C4, D4, E4, F4, G4, A4, B4, C5, D5, E5, F5, G5, A5, B5, C6...]
current_note = notes[score % notes.length]

// For song mode: predetermined note sequence matching the song
```

### 7.2 Note Frequencies (Hz)

| Note | Frequency |
|------|-----------|
| C4   | 261.6     |
| D4   | 293.7     |
| E4   | 329.6     |
| F4   | 349.2     |
| G4   | 392.0     |
| A4   | 440.0     |
| B4   | 493.9     |
| C5   | 523.3     |

### 7.3 Song Mode
Pre-programmed songs where tiles match the melody:

| Song                    | Difficulty | Notes | BPM |
|-------------------------|------------|-------|-----|
| Twinkle Twinkle        | Easy       | 42    | 100 |
| Fur Elise              | Medium     | 120   | 120 |
| Turkish March           | Hard       | 200   | 140 |
| Flight of the Bumblebee| Expert     | 350   | 180 |
| Canon in D              | Medium     | 160   | 110 |
| Moonlight Sonata        | Hard       | 180   | 80  |

---

## 8. UI Layout

### 8.1 Title Screen / Mode Select
```
+---------------------------+
|                           |
|     PIANO TILES           |  Y = 60
|     Don't Tap the         |  Y = 100
|     White Tile            |  Y = 130
|                           |
|   +---+---+---+---+      |
|   |   | B |   |   |      |  Decorative tiles
|   +---+---+---+---+      |
|   |   |   | B |   |      |
|   +---+---+---+---+      |
|                           |
|   [  CLASSIC  ]           |  Y = 320
|   [  ARCADE   ]           |  Y = 370
|   [    ZEN    ]           |  Y = 420
|   [   RELAY   ]           |  Y = 470
|                           |
|   Best: Classic: 234      |  Y = 520
+---------------------------+
```

### 8.2 Classic Mode Screen
```
+-----|-----|-----|-----+
|     |     | *** |     |  Top row (upcoming)
|     |     | *** |     |
+-----|-----|-----|-----+
|     | *** |     |     |  Second row
|     | *** |     |     |
+-----|-----|-----|-----+
| *** |     |     |     |  Third row
| *** |     |     |     |
+-----|-----|-----|-----+
|     |     |     | *** |  Bottom row (active - tap here)
|     |     |     | *** |  *** = black tile
+-----|-----|-----|-----+
         Score: 17

(| = column dividers, *** = black tile)
```

### 8.3 Arcade Mode Screen
```
+-----|-----|-----|-----+
|     23                |  Score at top
+-----|-----|-----|-----+
|     |     | BBB |     |  Scrolling rows
|     |     | BBB |     |
+-----|-----|-----|-----+
| BBB |     |     |     |
| BBB |     |     |     |
+-----|-----|-----|-----+
|     | BBB |     |     |
|     | BBB |     |     |
+-----|-----|-----|-----+
|     |     |     | BBB |
|     |     |     | BBB |
+-----|-----|-----|-----+  <- new rows appear here
```

### 8.4 Game Over Screen
```
+---------------------------+
|                           |
|       GAME OVER           |
|                           |
|   [red tile flashes at    |
|    point of failure]      |
|                           |
|       Score: 47           |
|       Best:  89           |
|                           |
|   [  RETRY  ]             |
|   [  MENU   ]             |
|   [  SHARE  ]             |
|                           |
+---------------------------+
```

---

## 9. Visual Effects

### 9.1 Tap Feedback
```
on_correct_tap(tile):
    // Tile changes from black to gray over 100ms
    tile.color = animate(BLACK, GRAY, 100ms)

    // Brief white flash at tap point
    flash = Circle(tap_x, tap_y, radius=30, color=WHITE, alpha=0.5)
    animate flash.alpha from 0.5 to 0 over 100ms
    animate flash.radius from 30 to 50 over 100ms
```

### 9.2 Wrong Tap Feedback
```
on_wrong_tap(tile):
    // Tile flashes red
    tile.color = RED
    // X mark appears at tap point
    draw_x(tap_x, tap_y, size=30, color=RED)

    // Screen flash: red overlay, 50ms
    // Optional: screen shake (2px, 100ms)

    // Freeze game for 500ms to show the mistake
    // Then show game over screen
```

### 9.3 Missed Tile (Arcade)
```
on_tile_missed:
    // Tile highlights red at the top of screen
    missed_tile.color = RED
    // Arrow or indicator pointing at the missed tile
    // Freeze + game over
```

---

## 10. Sound Effects

| Sound          | Trigger                  | Description                    |
|----------------|--------------------------|-------------------------------|
| piano_note     | Correct tap              | Piano note (varies by score)  |
| wrong_tap      | Tap white tile           | Harsh buzzer / error tone     |
| miss           | Black tile exits screen  | Descending error tone         |
| game_over      | Game ends                | Short sad melody              |
| timer_tick     | Zen mode last 5 seconds  | Ticking clock sound           |
| new_record     | Beat high score          | Triumphant chime              |

### 10.1 Piano Note Generation
```
// Option 1: Synthesize using Web Audio API
function playNote(frequency, duration=200ms):
    oscillator = createOscillator(type="sine")
    oscillator.frequency = frequency
    gain = createGain()
    gain.value = 0.5
    // ADSR envelope:
    // Attack: 10ms ramp to full
    // Decay: 50ms to 80%
    // Sustain: hold for duration
    // Release: 100ms fade to 0

// Option 2: Pre-recorded piano samples (preferred for quality)
```

---

## 11. Difficulty Analysis

### 11.1 Classic Mode
- No time pressure, purely accuracy
- Difficulty is self-imposed (play faster = higher risk)
- Average game length: 50-200 taps for beginners, 1000+ for experts

### 11.2 Arcade Mode
- Time pressure increases continuously
- At maximum speed (8 px/frame): ~3.38 tiles per second required
- Human reaction time: ~200ms average
- At max speed, tile visible for: 142px / 8px = 17.75 frames = ~296ms
- This is barely above reaction time -- extremely challenging

### 11.3 Zen Mode
- Strategy: balance speed vs accuracy
- 30 seconds = theoretically up to 150 taps (5 per second) for expert
- Average player: 40-80 taps

---

## 12. Touch / Input Handling

### 12.1 Multi-Touch Support
```
// The game must support rapid sequential taps
// Input events should be processed immediately (no buffering)

on_touch_begin(finger_id, x, y):
    column = floor(x / column_width)
    processTouch(column, y)

// Each finger is independent
// Multiple fingers can tap different columns simultaneously
// This is crucial for fast play (alternating thumbs)
```

### 12.2 Input Precision
- Column detection: purely based on X coordinate
- Row detection: based on Y coordinate relative to grid position
- No gesture detection needed (tap only)
- Touch up events are not used (action on touch down only)
- Exception: long tiles require touch-and-hold (touch down to touch up)

---

## 13. Long Tile Mechanics (Piano Mode)

### 13.1 Long Tile Properties
| Parameter       | Value                          |
|-----------------|--------------------------------|
| Min length      | 2 rows (284 px)                |
| Max length      | 4 rows (568 px)                |
| Hold tolerance  | 30 px outside tile = fail      |
| Color while held| Dark gray (#404040)            |
| Progress        | Fill animation top-to-bottom   |

### 13.2 Long Tile Behavior
```
on_touch_begin on long tile:
    start_holding = true
    tile.color = DARK_GRAY
    note.start_playing()  // continuous note

while holding:
    // Check finger still within tile column (+/- tolerance)
    if finger.x < tile.left - tolerance or finger.x > tile.right + tolerance:
        fail("released too early or drifted off tile")

    // Check tile has not fully scrolled past
    // Fill meter tracks progress

on_touch_end on long tile:
    if tile has fully scrolled (progress >= 95%):
        success()
    else:
        fail("released too early")
```

---

## 14. Color Palette

| Element          | Color (Hex)  |
|------------------|--------------|
| Background       | #FFFFFF      |
| Black tile       | #1A1A1A      |
| Tapped tile      | #808080      |
| Miss tile        | #FF0000      |
| Column divider   | #CCCCCC      |
| Score text       | #333333      |
| Game over text   | #FF0000      |
| Zen timer        | #FF6600      |
| Row divider      | #E0E0E0      |

---

## 15. Game Over Conditions Summary

| Mode    | Game Over Trigger                                   |
|---------|-----------------------------------------------------|
| Classic | Tap a white tile                                    |
| Arcade  | Tap white tile OR black tile exits top of screen    |
| Zen     | 30-second timer expires (not a "fail," just ends)   |
| Relay   | Tap white tile OR miss tile                         |

---

## 16. Data Persistence

| Key                 | Type  | Description                    |
|---------------------|-------|--------------------------------|
| best_classic        | int   | High score for Classic mode    |
| best_arcade         | int   | High score for Arcade mode     |
| best_zen            | int   | High score for Zen mode        |
| best_relay          | int   | High score for Relay mode      |
| total_tiles_tapped  | int   | Lifetime tiles tapped          |
| total_games         | int   | Total games played             |
| selected_theme      | string| Current visual theme           |
| sound_enabled       | bool  | Sound on/off                   |
| songs_unlocked      | list  | Song mode songs unlocked       |

---

## 17. Theme Variants

| Theme      | Black Tile    | Background   | Dividers    |
|------------|---------------|--------------|-------------|
| Classic    | #1A1A1A       | #FFFFFF      | #CCCCCC     |
| Dark       | #FFFFFF       | #1A1A1A      | #333333     |
| Blue       | #1565C0       | #E3F2FD      | #90CAF9     |
| Red        | #C62828       | #FFEBEE      | #EF9A9A     |
| Green      | #2E7D32       | #E8F5E9      | #A5D6A7     |
| Purple     | #6A1B9A       | #F3E5F5      | #CE93D8     |
| Neon       | #00E676       | #212121      | #424242     |

---

## 18. Implementation Pseudocode

```
// Main game loop (Arcade mode)
function update():
    if state != PLAYING: return

    // Scroll tiles
    scroll_speed = min(2.0 + score * 0.03, 8.0)
    for row in rows:
        row.y -= scroll_speed

    // Check for missed tiles (top of screen)
    while rows[0].y + row_height < 0:
        if rows[0].has_black_tile and not rows[0].tapped:
            // MISSED!
            markMissed(rows[0])
            gameOver()
            return
        rows.remove(0)

    // Generate new rows at bottom
    while rows.last().y < screen_height:
        new_row = generateRow()
        new_row.y = rows.last().y + row_height
        rows.append(new_row)

function onTap(x, y):
    if state != PLAYING: return

    col = floor(x / column_width)
    // Find row at y position
    for row in rows:
        if y >= row.y and y < row.y + row_height:
            if row.tiles[col] == BLACK and not row.tapped:
                // CORRECT
                row.tapped = true
                row.tiles[col] = GRAY
                score += 1
                playPianoNote(score)
                animateTap(x, y)
            elif row.tiles[col] == WHITE:
                // WRONG
                row.tiles[col] = RED
                gameOver()
            // Already tapped rows ignored
            break

function gameOver():
    state = GAME_OVER
    if score > bestScore:
        bestScore = score
        showNewRecord()
    saveData()
    // Show game over after 500ms delay
```

---

## 19. Implementation Checklist

1. [ ] Set up portrait canvas 320x568
2. [ ] Create 4-column grid with dividers
3. [ ] Generate rows with 1 random black tile per row
4. [ ] Implement Classic mode (tap advances grid)
5. [ ] Implement tap detection (column + row lookup)
6. [ ] Add correct tap feedback (black to gray)
7. [ ] Add wrong tap detection (game over on white tap)
8. [ ] Implement Arcade mode (continuous scrolling)
9. [ ] Add scroll speed that increases with score
10. [ ] Detect missed tiles at top of screen
11. [ ] Implement Zen mode (30-second timer)
12. [ ] Implement Relay mode (speed levels)
13. [ ] Add piano note playback per tap
14. [ ] Implement scoring per mode
15. [ ] Create mode select screen
16. [ ] Create game over screen with score/best
17. [ ] Add visual effects (tap flash, miss red)
18. [ ] Add sound effects
19. [ ] Implement high score persistence per mode
20. [ ] Add theme/skin options
21. [ ] Optional: implement song mode with long tiles
22. [ ] Optional: implement multi-touch for fast play
23. [ ] Optional: add double-tile rows for hard mode
24. [ ] Polish: score animation, transitions

---

## 20. Mathematical Reference

**Arcade mode tile visibility time:**
```
At speed S px/frame:
visibility_time = row_height / S frames = (142 / S) frames
At S=2: 71 frames = 1.18 seconds
At S=5: 28.4 frames = 0.47 seconds
At S=8: 17.75 frames = 0.30 seconds
```

**Maximum theoretical score (Arcade):**
```
Human max tap rate: ~8 taps/second
At max speed, tiles arrive at: ~3.38/second
Therefore: game is scroll-limited, not tap-limited
Max score limited by attention span and consistency
World records: 1000+ in arcade mode
```

---

End of Piano Tiles specification.
