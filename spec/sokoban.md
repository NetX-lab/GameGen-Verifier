# Sokoban — Complete Game Specification

## 1. Game Overview

**Title:** Sokoban
**Genre:** Grid-based box-pushing puzzle
**Platform:** Single-player, keyboard-controlled
**Original Release:** 1982 (Thinking Rabbit / Hiroyuki Imabayashi)
**Objective:** Push all boxes onto designated goal positions within a warehouse. The player can push boxes but cannot pull them. Each level is a self-contained puzzle that must be solved with a minimum of moves.

---

## 2. Technical Foundation

### 2.1 Display

| Parameter            | Value                    |
|----------------------|--------------------------|
| Tile size            | 48 x 48 pixels           |
| Max level size       | 20 x 20 tiles (960 x 960 pixels) |
| Typical level size   | 7-15 tiles wide, 7-12 tiles tall |
| Total canvas         | 960 x 720 pixels         |
| Frame rate           | 60 FPS                   |
| Level centered       | Yes, centered in viewport|

### 2.2 Coordinate System

- Origin (0, 0) at top-left of the level grid.
- X increases rightward, Y increases downward.

---

## 3. Tile Types

### 3.1 Tile Definitions

| Tile          | Character | Color / Visual            | Description                      |
|---------------|-----------|---------------------------|----------------------------------|
| Floor         | ` ` (space) | Light gray (#D4C8A8)    | Walkable empty space             |
| Wall          | `#`       | Dark brown (#5A3A1A)      | Impassable obstacle              |
| Player        | `@`       | Blue character (#4488FF)  | Player position on floor         |
| Player on Goal| `+`       | Blue on green              | Player standing on a goal        |
| Box           | `$`       | Brown/tan box (#C8A050)   | Pushable box on floor            |
| Box on Goal   | `*`       | Dark green box (#44AA44)  | Box correctly placed on goal     |
| Goal          | `.`       | Green diamond (#66CC66)   | Target position for a box        |
| Void          | (outside) | Black (#000000)          | Area outside the level walls     |

### 3.2 Standard Level Format (XSB)

Sokoban levels use the standard XSB text format:

```
    #####
    #   #
    #$  #
  ###  $##
  #  $ $ #
### # ## #   ######
#   # ## #####  ..#
# $  $          ..#
##### ### #@##  ..#
    #     #########
    #######
```

Character encoding:
- `#` = Wall
- ` ` = Floor (also represents empty space outside walls)
- `$` = Box
- `.` = Goal
- `@` = Player
- `+` = Player on goal
- `*` = Box on goal
- `-` or `_` = Floor (alternative)

---

## 4. Core Mechanics

### 4.1 Movement Rules

1. The player can move one tile in four directions: Up, Down, Left, Right.
2. The player cannot move into a wall.
3. The player cannot move into a box if the cell behind the box (in the movement direction) is occupied by a wall or another box.
4. If the player moves into a box and the cell behind the box is empty floor (or a goal), the box is pushed one tile in the movement direction.
5. The player can only push one box at a time (cannot push two boxes in a row).
6. The player cannot pull boxes.

### 4.2 Push Rules

```python
def try_move(player, direction, board):
    target = player.pos + direction

    if board[target] == WALL:
        return False  # blocked by wall

    if board[target] in (BOX, BOX_ON_GOAL):
        beyond = target + direction
        if board[beyond] in (WALL, BOX, BOX_ON_GOAL):
            return False  # cannot push, blocked
        # Push the box
        board.move_box(target, beyond)
        board.move_player(player.pos, target)
        return True

    # Empty floor or goal
    board.move_player(player.pos, target)
    return True
```

### 4.3 Win Condition

The level is solved when ALL boxes are on ALL goal positions simultaneously.

```python
def is_level_complete(board):
    for goal in board.goals:
        if board[goal] != BOX_ON_GOAL:
            return False
    return True
```

Note: The number of boxes always equals the number of goals in a valid level.

---

## 5. Deadlock Detection (Optional but Recommended)

### 5.1 Simple Deadlocks

A box is in a "dead" position if it can never reach any goal. Common deadlock patterns:

**Corner deadlock:** Box pushed into a corner (two adjacent walls) where no goal exists.
```
##
#$   <- dead if no goal at $ position
```

**Wall deadlock:** Box pushed against a wall where no goals exist along that wall segment.
```
######
 $        <- dead if no goals along this wall
######
```

### 5.2 Freeze Deadlock

A group of boxes that are mutually immovable and not all on goals.
```
##
$$ <- both boxes frozen against wall and each other
##
```

### 5.3 Deadlock Visualization (Optional)

- Boxes in detected deadlock positions can be highlighted with a red tint (#FF000040 overlay).
- This helps the player recognize mistakes early.

---

## 6. Level Collections

### 6.1 Classic Sokoban Levels

The original Sokoban contains 90 levels. Standard level packs:

| Pack Name           | Levels | Difficulty      | Source           |
|--------------------|--------|-----------------|------------------|
| Original           | 90     | Easy to Hard    | Thinking Rabbit  |
| Microban           | 155    | Easy            | David W. Skinner |
| Microban II        | 135    | Easy-Medium     | David W. Skinner |
| Sasquatch          | 50     | Medium          | David W. Skinner |
| Yoshio             | 45     | Medium-Hard     | Yoshio Murase    |
| Thinking Rabbit Extra | 10  | Hard            | Thinking Rabbit  |

### 6.2 Example Levels

**Level 1 (Easy):**
```
  ####
###  ####
#     $ #
# #  #$ #
# . .#@ #
#########
```
Size: 9x6, Boxes: 2, Goals: 2

**Level 5 (Medium):**
```
########
#  ....#
# #######
# $ $ $ #
#   $   #
## ### ##
 # @ # #
 #   # #
 #######
```
Size: 9x9, Boxes: 4, Goals: 4

**Level 10 (Hard):**
```
  ####
  #  ###
  #    #
  # $# #
###  # ####
# $  #    #
# ## #$$# #
#  ..#  # #
# #..   # #
#   ######
#####@ #
   ####
```
Size: 11x12, Boxes: 5, Goals: 4

---

## 7. Scoring and Statistics

### 7.1 Metrics Per Level

| Metric          | Description                            |
|-----------------|----------------------------------------|
| Moves           | Total player movements (including pushes) |
| Pushes          | Total box pushes                       |
| Time            | Time elapsed from first move           |

### 7.2 Optimal Solutions

For each level, track:
- Best (fewest) moves solution.
- Best (fewest) pushes solution.
- These may be different solutions.

### 7.3 Rating System

| Rating     | Criteria                              |
|------------|---------------------------------------|
| Bronze     | Level solved                          |
| Silver     | Solved within 2x optimal moves       |
| Gold       | Solved within 1.5x optimal moves     |
| Platinum   | Solved at or below optimal moves     |

---

## 8. Undo and Redo System

### 8.1 Full Undo/Redo

- Every move is stored in an undo stack.
- Undo key: Z or Ctrl+Z.
- Redo key: Y or Ctrl+Y.
- Unlimited undo depth (back to initial state).
- Undo/redo is instantaneous.

### 8.2 State Storage

```python
class MoveRecord:
    player_from: Position
    player_to: Position
    box_from: Position | None  # None if no push
    box_to: Position | None

undo_stack: list[MoveRecord] = []
redo_stack: list[MoveRecord] = []
```

---

## 9. Input Handling

### 9.1 Controls

| Action      | Key                    |
|-------------|------------------------|
| Move Up     | Up Arrow / W           |
| Move Down   | Down Arrow / S         |
| Move Left   | Left Arrow / A         |
| Move Right  | Right Arrow / D        |
| Undo        | Z / Ctrl+Z             |
| Redo        | Y / Ctrl+Y             |
| Restart     | R                      |
| Next Level  | N (after solving)      |
| Prev Level  | P (in level select)    |
| Pause/Menu  | Escape                 |

### 9.2 Auto-Repeat

- DAS delay: 200ms.
- ARR: 80ms.
- Allows holding a direction key for continuous movement.

### 9.3 Mouse Input (Optional)

- Click on an empty floor tile adjacent to the player: Move to that tile.
- Click on a floor tile further away: Pathfind to that tile (if possible without pushing boxes).
- Click-drag in a direction from the player: Move in that direction.

---

## 10. Animations

### 10.1 Movement Animation

| Animation              | Duration | Easing          |
|------------------------|----------|-----------------|
| Player move (1 tile)   | 100 ms   | Ease-out        |
| Box push (1 tile)      | 100 ms   | Ease-out        |
| Box placed on goal     | 200 ms   | Pulse (scale 1.0->1.1->1.0) |
| Box removed from goal  | 100 ms   | Color transition|
| Level complete         | 1500 ms  | Sequence below  |
| Undo                   | 50 ms    | Instant/fast    |
| Restart                | 300 ms   | Fade out, fade in |

### 10.2 Level Complete Sequence

1. All boxes on goals pulse green simultaneously (300ms).
2. "LEVEL COMPLETE!" text appears center screen (fade in 300ms).
3. Statistics display: Moves, Pushes, Time (count up animation, 500ms).
4. Rating badge appears (Bronze/Silver/Gold/Platinum) (300ms, bounce).
5. "Press N for next level" text appears (fade in 200ms).

### 10.3 Player Animation

- Idle: Player faces the last move direction. Slight breathing animation (2-frame cycle, 1000ms).
- Walking: 4-frame walk cycle per direction (100ms per frame).
- Pushing: Player leans forward slightly during box push.

### 10.4 Box Visual

- Normal box: Brown/tan with a slight 3D effect (lighter top, darker sides).
- Box on goal: Changes to green, with a checkmark overlay or green glow.
- Dead box (optional): Red tint overlay when deadlock is detected.

---

## 11. UI Layout

```
+--------------------------------------------------+
|  SOKOBAN         Level: 01/90     Pack: Original  |
+--------------------------------------------------+
|                                                    |
|  Moves: 0023    Pushes: 0012    Time: 01:45       |
|                                                    |
|  +--------------------------------------------+   |
|  |                                            |   |
|  |           ####                             |   |
|  |         ###  ####                          |   |
|  |         #     $ #                          |   |
|  |         # #  #$ #                          |   |
|  |         # . .#@ #                          |   |
|  |         #########                          |   |
|  |                                            |   |
|  +--------------------------------------------+   |
|                                                    |
|  [Undo] [Redo] [Restart] [Menu]                   |
+--------------------------------------------------+
```

### 11.1 Header

- Level name/number: Left-aligned, 20px font.
- Pack name: Right-aligned, 16px font.

### 11.2 Statistics Bar

- Moves, Pushes, Time: Displayed in a row below the header.
- Fixed-width font (monospace) for alignment.
- Updates in real-time.

### 11.3 Game Area

- Level centered within the game area.
- Background: Black or dark gray for void areas.
- Floor tiles have subtle texture or pattern.

### 11.4 Button Bar

- Bottom of screen: Undo, Redo, Restart, Menu buttons.
- Button size: 80x40px.
- Style: Rounded rectangles, dark background (#333), light text (#EEE).

---

## 12. Level Select Screen

```
+--------------------------------------------------+
|  SOKOBAN — Level Select        Pack: [Original v] |
+--------------------------------------------------+
|                                                    |
|  +---+  +---+  +---+  +---+  +---+  +---+        |
|  | 1 |  | 2 |  | 3 |  | 4 |  | 5 |  | 6 |        |
|  | G |  | S |  | G |  |   |  |   |  |   |        |
|  +---+  +---+  +---+  +---+  +---+  +---+        |
|                                                    |
|  +---+  +---+  +---+  +---+  +---+  +---+        |
|  | 7 |  | 8 |  | 9 |  | 10|  | 11|  | 12|        |
|  |   |  |   |  |   |  |   |  |   |  |   |        |
|  +---+  +---+  +---+  +---+  +---+  +---+        |
|                                                    |
|  ...                                               |
|                                                    |
|  G = Gold   S = Silver   B = Bronze   (empty)=unsolved |
|                                                    |
|  Total: 3/90 solved    [Back]                     |
+--------------------------------------------------+
```

---

## 13. Audio Design

### 13.1 Sound Effects

| Event                | Description                          | Duration |
|----------------------|--------------------------------------|----------|
| Player step          | Soft footstep on floor               | 80 ms    |
| Box push             | Scraping/sliding on floor            | 150 ms   |
| Box on goal          | Satisfying click/lock                | 200 ms   |
| Box off goal         | Unlocking click                      | 100 ms   |
| Wall bump (blocked)  | Soft thud                            | 80 ms    |
| Undo                 | Quick reverse whoosh                 | 80 ms    |
| Restart              | Reset sweep sound                    | 300 ms   |
| Level complete       | Triumphant jingle                    | 1500 ms  |
| Medal earned         | Achievement chime                    | 500 ms   |
| Menu navigate        | UI click                             | 50 ms    |
| Level select         | UI confirm                           | 100 ms   |
| Cannot push (2 boxes)| Dull thud (heavier than wall bump)   | 100 ms   |
| Deadlock detected    | Subtle warning tone (optional)       | 200 ms   |

### 13.2 Music

- Calm, contemplative background music.
- Genre: Ambient/light jazz/lo-fi.
- Tempo: ~80 BPM.
- Loops seamlessly every 2-3 minutes.
- Music does not change with difficulty or level.
- Volume: Adjustable, default 40%.
- Separate Music and SFX volume controls.

---

## 14. Menus

### 14.1 Main Menu

```
+----------------------------------+
|                                  |
|        S O K O B A N             |
|                                  |
|      [ PLAY       ]             |
|      [ LEVEL SELECT ]           |
|      [ SETTINGS   ]             |
|      [ CREDITS    ]             |
|                                  |
+----------------------------------+
```

### 14.2 Settings

| Setting              | Options                    | Default |
|----------------------|----------------------------|---------|
| Music Volume         | 0-100%                     | 40%     |
| SFX Volume           | 0-100%                     | 70%     |
| Tile Size            | Small / Medium / Large     | Medium  |
| Show Deadlocks       | On / Off                   | Off     |
| Animation Speed      | Slow / Normal / Fast       | Normal  |
| Control Scheme       | Arrows / WASD / Both       | Both    |
| Auto-Repeat Delay    | 100-400ms                  | 200ms   |
| Auto-Repeat Rate     | 40-200ms                   | 80ms    |
| Colorblind Markers   | On / Off                   | Off     |

### 14.3 Pause Menu

```
+----------------------------------+
|                                  |
|  PAUSED                          |
|                                  |
|  [ RESUME      ]                |
|  [ RESTART     ]                |
|  [ LEVEL SELECT]                |
|  [ SETTINGS    ]                |
|  [ MAIN MENU   ]                |
|                                  |
+----------------------------------+
```

---

## 15. State Machine

```
[MAIN_MENU]
    --> [LEVEL_SELECT]
        --> [LEVEL_LOADING]
            --> [PLAYING]
    --> [SETTINGS]
    --> [CREDITS]

[PLAYING]
    --> [IDLE] (waiting for input)
        --> [MOVING] (valid move)
            --> [CHECK_WIN]
                --> [LEVEL_COMPLETE]
                    --> [STATS_DISPLAY]
                        --> [NEXT_LEVEL] or [LEVEL_SELECT]
                --> [IDLE] (not complete)
        --> [BLOCKED] (invalid move, wall/blocked box)
            --> [IDLE]
        --> [UNDO] --> [IDLE]
        --> [RESTART] --> [IDLE] (initial state)
    --> [PAUSED]
        --> [PLAYING] (resume)
        --> [LEVEL_SELECT]
        --> [MAIN_MENU]
```

---

## 16. Pathfinding (Optional Player Convenience)

### 16.1 Click-to-Move

When the player clicks on a reachable floor tile:
1. Calculate shortest path from player to target using BFS.
2. Path must not push any boxes (pathfinding avoids box tiles).
3. Player walks the path automatically (100ms per step).
4. Path is shown as subtle dotted line during walk.
5. If the player clicks during auto-walk, cancel and stop.

### 16.2 Click-to-Push (Optional)

When the player clicks on a box:
1. Determine which side of the box the player should approach.
2. Calculate path to that position.
3. Walk to position, then push the box one tile in the click direction.
4. This is a convenience feature for mouse users.

---

## 17. Visual Design

### 17.1 Tile Rendering

```
Wall Tile (48x48):
+--------------------------------------------------+
|  Dark brown fill (#5A3A1A)                       |
|  Brick pattern: 2 rows of bricks                |
|  Light mortar lines (#8B7355)                    |
|  Darker shadow on bottom edge (4px)              |
+--------------------------------------------------+

Floor Tile (48x48):
+--------------------------------------------------+
|  Light tan fill (#D4C8A8)                        |
|  Subtle square pattern (low contrast)            |
|  No border                                       |
+--------------------------------------------------+

Goal Tile (48x48):
+--------------------------------------------------+
|  Same as floor, with centered diamond (#66CC66)  |
|  Diamond: 16x16px, rotated 45 degrees            |
|  Slight glow effect (4px, #66CC6640)             |
+--------------------------------------------------+

Box (48x48):
+--------------------------------------------------+
|  Main fill: #C8A050                              |
|  Top face: lighter (#D8B868, 4px)                |
|  Side shadow: darker (#A88030, 4px on right/bottom)|
|  Cross mark in center (darker lines)             |
+--------------------------------------------------+

Box on Goal (48x48):
+--------------------------------------------------+
|  Main fill: #44AA44 (green)                      |
|  Same 3D effect as normal box                    |
|  Checkmark in center (white, 2px line)           |
+--------------------------------------------------+

Player (48x48):
+--------------------------------------------------+
|  Circle body: 32px diameter, #4488FF             |
|  Two white dot eyes (6px each)                   |
|  Direction indicator: eyes shift in facing dir   |
+--------------------------------------------------+
```

---

## 18. Data Persistence

### 18.1 Level Progress

```json
{
  "current_pack": "original",
  "packs": {
    "original": {
      "levels_solved": 3,
      "total_levels": 90,
      "levels": {
        "1": {
          "solved": true,
          "best_moves": 23,
          "best_pushes": 12,
          "best_time": 105,
          "rating": "gold"
        },
        "2": {"solved": true, "best_moves": 45, "best_pushes": 30, "best_time": 230, "rating": "silver"},
        "3": {"solved": true, "best_moves": 18, "best_pushes": 8, "best_time": 60, "rating": "gold"},
        "4": {"solved": false}
      }
    }
  },
  "settings": {
    "music_volume": 40,
    "sfx_volume": 70,
    "tile_size": "medium",
    "show_deadlocks": false
  }
}
```

### 18.2 Auto-Save

- Current level state (including undo history) is saved automatically.
- On app restart, the player can resume from where they left off.
- Save format: Board state + undo stack serialized.

---

## 19. Accessibility

- Colorblind mode: Goals marked with a distinct pattern (crosshatch or outline) in addition to color. Boxes on goals marked with a checkmark.
- High contrast mode: Increased border width, brighter colors.
- Screen reader: Announce player position, adjacent objects, and move results.
- Keyboard-only: Full functionality without mouse.
- Move count display in large font.
- Optional gridlines overlay for visual clarity.

---

## 20. Performance Requirements

| Metric               | Target           |
|-----------------------|------------------|
| Input latency         | < 16ms           |
| Move animation        | Completes in 100ms |
| Deadlock detection    | < 10ms per move  |
| Memory usage          | < 20 MB          |
| Level load time       | < 200ms          |
| Save/load state       | < 50ms           |

---

## 21. Level Parser

```python
def parse_xsb(text: str) -> Level:
    lines = text.strip().split('\n')
    height = len(lines)
    width = max(len(line) for line in lines)

    board = [[VOID] * width for _ in range(height)]
    player_pos = None
    boxes = []
    goals = []

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '#':
                board[y][x] = WALL
            elif char == ' ' or char == '-' or char == '_':
                board[y][x] = FLOOR
            elif char == '$':
                board[y][x] = FLOOR
                boxes.append((x, y))
            elif char == '.':
                board[y][x] = FLOOR
                goals.append((x, y))
            elif char == '@':
                board[y][x] = FLOOR
                player_pos = (x, y)
            elif char == '+':
                board[y][x] = FLOOR
                goals.append((x, y))
                player_pos = (x, y)
            elif char == '*':
                board[y][x] = FLOOR
                goals.append((x, y))
                boxes.append((x, y))

    # Fill unreachable spaces as VOID
    flood_fill_exterior(board)

    return Level(board, player_pos, boxes, goals)
```

---

## 22. Testing Checklist

1. Player moves in all 4 directions correctly.
2. Player cannot move into walls.
3. Player can push a single box into empty space.
4. Player can push a box onto a goal.
5. Player cannot push a box into a wall.
6. Player cannot push a box into another box.
7. Player cannot push two boxes at once.
8. Win condition triggers when all boxes are on goals.
9. Box color changes when placed on and removed from goals.
10. Undo correctly reverses one move (including box pushes).
11. Redo correctly replays one undone move.
12. Restart returns level to initial state and clears undo history.
13. Move counter increments correctly.
14. Push counter increments only on box push moves.
15. Timer starts on first move and pauses on pause.
16. Level parser correctly reads XSB format.
17. All levels in a pack are loadable and solvable.
18. Level select shows correct solve status and ratings.
19. Deadlock detection correctly identifies corner and wall deadlocks (if enabled).
20. Auto-save and restore works correctly.
21. Click-to-move pathfinding avoids boxes (if implemented).
22. Auto-repeat works correctly at configured rates.
