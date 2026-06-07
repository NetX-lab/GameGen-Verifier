# Baba Is You — Complete Game Specification

## 1. Game Overview

**Title:** Baba Is You
**Genre:** Rule-based puzzle
**Platform:** Single-player, keyboard-controlled
**Original Release:** March 2019 (Hempuli Oy / Arvi Teikari)
**Objective:** Manipulate the rules of each puzzle level by pushing word blocks to form new sentences. The rules of the game (what you control, what is the goal, what stops you) are physically present in the level as pushable text objects. Reach the goal (or satisfy the win condition) to complete each level.

---

## 2. Technical Foundation

### 2.1 Display

| Parameter            | Value                    |
|----------------------|--------------------------|
| Grid size            | Variable per level (typical: 15-25 wide, 10-18 tall) |
| Cell size            | 24 x 24 pixels           |
| Typical level size   | 360 x 240 to 600 x 432 pixels |
| Total canvas         | 640 x 480 pixels         |
| Frame rate           | 60 FPS                   |
| Art style            | Pixel art, wobbly animation |

### 2.2 Coordinate System

- Origin (0, 0) at top-left cell.
- X increases rightward, Y increases downward.
- Grid is bounded by the level edges (objects cannot leave the grid).

---

## 3. Core Concept: Rules as Objects

### 3.1 Sentence Structure

Rules in the game are formed by three types of word blocks arranged in a horizontal or vertical line:

```
[SUBJECT] [VERB] [COMPLEMENT]
```

Example sentences:
- BABA IS YOU → The player controls Baba.
- WALL IS STOP → Walls block movement.
- FLAG IS WIN → Touching the flag wins the level.
- ROCK IS PUSH → Rocks can be pushed.
- BABA IS ROCK → Baba becomes a rock (transformation).
- ROCK HAS KEY → Destroying a rock spawns a key.

### 3.2 Word Types

| Type        | Role                    | Examples                            |
|-------------|-------------------------|-------------------------------------|
| Noun        | Subject or Object       | BABA, WALL, FLAG, ROCK, KEY, DOOR, WATER, LAVA, KEKE, SKULL, BOX, GRASS, TILE, HEDGE, ICE, JELLY, STAR, LOVE, TREE, FUNGUS, GHOST, CRAB, BEE, PILLAR, BOLT |
| Verb        | Connector               | IS, HAS, MAKE                       |
| Property    | Complement (adjective)  | YOU, WIN, STOP, PUSH, PULL, DEFEAT, SINK, HOT, MELT, OPEN, SHUT, MOVE, TELE, FLOAT, WEAK, WORD, SWAP, SHIFT, BONUS |
| Operator    | Logic                   | AND, NOT                            |
| Conditional | Condition prefix        | LONELY, IDLE, ON, NEAR, FACING     |

### 3.3 Rule Parsing

Rules are parsed by scanning the grid:

1. **Horizontal scan:** For each row, scan left-to-right for valid sentence patterns.
2. **Vertical scan:** For each column, scan top-to-bottom for valid sentence patterns.
3. A valid sentence requires:
   - At least one Noun
   - Followed by a Verb (IS, HAS, MAKE)
   - Followed by at least one Property or Noun

**AND chaining:**
- "BABA AND KEKE IS YOU" → Both Baba and Keke are YOU.
- "BABA IS WIN AND PUSH" → Baba is both WIN and PUSH.
- AND can appear in any segment.

**NOT negation:**
- "BABA IS NOT STOP" → Baba explicitly is NOT stop (overrides a parallel rule "BABA IS STOP").
- NOT inverts the following word.

---

## 4. Properties

### 4.1 Property Definitions

| Property | Effect                                                        |
|----------|---------------------------------------------------------------|
| YOU      | The player controls this object. Multiple objects can be YOU. |
| WIN      | Touching this object (as YOU) wins the level.                 |
| STOP     | This object blocks movement. Cannot be walked through.        |
| PUSH     | This object can be pushed by the player or other PUSH objects.|
| PULL     | This object is pulled when an adjacent PUSH/YOU moves away.   |
| DEFEAT   | Touching this object (as YOU) destroys the YOU object.        |
| SINK     | When any object overlaps with SINK, both are destroyed.       |
| HOT      | This object destroys any MELT object that touches it.         |
| MELT     | This object is destroyed by HOT objects.                      |
| OPEN     | This object is destroyed when it touches a SHUT object (and vice versa). |
| SHUT     | This object is destroyed when it touches an OPEN object.      |
| MOVE     | This object moves automatically in a direction each turn.     |
| TELE     | Objects entering this object teleport to another TELE object. |
| FLOAT    | This object exists on a higher layer; does not interact with non-FLOAT objects (except YOU). |
| WEAK     | If any other object occupies the same cell, WEAK object is destroyed. |
| WORD     | Text objects become regular objects (cannot form rules).       |
| SWAP     | When YOU touches SWAP, the two objects swap positions.        |
| SHIFT    | Objects moving onto SHIFT are pushed one cell further.         |
| BONUS    | (Optional) Collecting BONUS objects earns completion bonus.   |

### 4.2 IS (Transformation)

When "A IS B" (both nouns):
- All instances of A transform into B.
- Happens immediately when the rule forms.
- Example: "BABA IS ROCK" turns all Baba objects into Rock objects.
- If this removes all YOU objects, the player loses control.

### 4.3 HAS

When "A HAS B":
- When an A object is destroyed, a B object spawns in its place.
- Example: "BOX HAS KEY" — destroying a box leaves a key behind.

### 4.4 MAKE

When "A MAKE B":
- Each turn, every A object spawns a B object in an adjacent empty cell.
- Spawning direction cycles or is random.

---

## 5. Object Types

### 5.1 Standard Objects

| Object  | Default Sprite         | Default Color   | Common Rules       |
|---------|------------------------|-----------------|-------------------|
| BABA    | White creature         | #FFFFFF          | YOU               |
| KEKE    | Red creature           | #FF4444          | (varies)          |
| WALL    | Gray brick             | #888888          | STOP              |
| ROCK    | Brown boulder          | #AA7744          | PUSH              |
| FLAG    | Yellow flag            | #FFDD00          | WIN               |
| KEY     | Golden key             | #FFD700          | (varies)          |
| DOOR    | Brown door             | #884400          | SHUT, STOP        |
| WATER   | Blue waves             | #4488FF          | SINK              |
| LAVA    | Red/orange glow        | #FF4400          | HOT               |
| SKULL   | White skull            | #FFFFFF          | DEFEAT            |
| BOX     | Brown box              | #AA8855          | (varies)          |
| GRASS   | Green tuft             | #44AA44          | (varies)          |
| TILE    | Gray tile              | #999999          | (varies)          |
| HEDGE   | Dark green bush        | #226622          | STOP              |
| ICE     | Light blue block       | #AADDFF          | (varies)          |
| JELLY   | Pink blob              | #FF88AA          | (varies)          |
| STAR    | Yellow star            | #FFFF44          | (varies)          |
| LOVE    | Pink heart             | #FF4488          | (varies)          |
| TREE    | Green tree             | #228822          | (varies)          |
| CRAB    | Red crab               | #CC4444          | (varies)          |

### 5.2 Word Objects (Text Blocks)

- Each word is also a physical object on the grid.
- Word objects are PUSH by default (always pushable unless "WORD IS NOT PUSH" or "WORD IS STOP").
- Word objects are rendered as white text on a dark background tile.
- Each word object occupies exactly 1 cell.

---

## 6. Turn System

### 6.1 Turn Flow

Baba Is You is turn-based. Each player input constitutes one turn:

1. Player presses a direction key (or waits with space).
2. **Phase 1 — Movement:**
   a. All YOU objects attempt to move in the input direction.
   b. Push chains resolve (PUSH objects pushed by YOU or other PUSH objects).
   c. PULL objects are pulled.
   d. MOVE objects move in their facing direction.
3. **Phase 2 — Interaction:**
   a. Check for overlaps. Apply SINK, HOT+MELT, OPEN+SHUT, DEFEAT, WIN, TELE, WEAK, SWAP, SHIFT.
4. **Phase 3 — Rule Parsing:**
   a. Re-scan the entire grid for valid sentences.
   b. Apply transformation rules (IS noun).
   c. Apply HAS/MAKE rules.
5. **Phase 4 — Check State:**
   a. If any YOU object overlaps a WIN object: level complete.
   b. If no YOU objects remain on the grid: level reset (undo to start or undo stack).

### 6.2 Push Chain Resolution

When a YOU or PUSH object attempts to move:
1. Check the target cell.
2. If the target cell is empty: move.
3. If the target cell has a STOP object: blocked. Do not move.
4. If the target cell has a PUSH object: attempt to push it.
   - Recursively check the next cell in line.
   - If the chain reaches an empty cell: all objects in the chain slide.
   - If the chain reaches a STOP object or level edge: entire push is blocked.
5. Multiple YOU objects move simultaneously. If one is blocked, it stays; others still move if possible.

```python
def can_move(obj, direction, board):
    target = obj.pos + direction
    if not in_bounds(target):
        return False
    occupants = board.get_objects_at(target)
    for occ in occupants:
        if has_property(occ, STOP) and not has_property(occ, PUSH):
            return False
        if has_property(occ, PUSH):
            if not can_move(occ, direction, board):
                return False
    return True
```

---

## 7. Level Structure

### 7.1 World Map

The game is organized into worlds on an overworld map:

| World | Name         | Levels | Theme                        |
|-------|-------------|--------|------------------------------|
| 0     | Overworld    | ~15    | Tutorial, basic rules        |
| 1     | The Lake     | ~12    | WATER, SINK                  |
| 2     | Solitary Isle| ~10    | FLOAT, layers                |
| 3     | Temple Ruins | ~12    | OPEN, SHUT, KEY, DOOR        |
| 4     | Forest of Fall| ~10   | MOVE, SHIFT                  |
| 5     | Deep Forest  | ~10    | TELE, complex chains         |
| 6     | Rocket Trip  | ~10    | HOT, MELT, multi-rule        |
| 7     | Flower Garden| ~10    | AND, NOT, complex logic      |
| 8     | Volcanic Cavern| ~10  | All mechanics combined       |
| 9     | ???          | ~8     | Meta-puzzles                 |
| Extra | Bonus levels | ~20    | Expert difficulty             |

### 7.2 Level Data Format

```json
{
  "level_id": "01-03",
  "name": "Still Still Still",
  "width": 18,
  "height": 12,
  "objects": [
    {"type": "baba", "x": 3, "y": 5},
    {"type": "wall", "x": 5, "y": 3},
    {"type": "word_baba", "x": 1, "y": 1},
    {"type": "word_is", "x": 2, "y": 1},
    {"type": "word_you", "x": 3, "y": 1},
    {"type": "word_wall", "x": 1, "y": 9},
    {"type": "word_is", "x": 2, "y": 9},
    {"type": "word_stop", "x": 3, "y": 9},
    {"type": "word_flag", "x": 14, "y": 1},
    {"type": "word_is", "x": 15, "y": 1},
    {"type": "word_win", "x": 16, "y": 1},
    {"type": "flag", "x": 15, "y": 6}
  ]
}
```

---

## 8. Undo System

### 8.1 Full Undo Stack

- Every turn's state is saved to an undo stack.
- Player can undo unlimited times back to the initial state.
- Undo key: Z (or Ctrl+Z).
- Undo restores the exact board state (all objects, all positions).
- Undo is instantaneous (no animation).
- The undo stack is cleared when the level is restarted.

### 8.2 State Representation

```python
class BoardState:
    objects: list[Object]  # each with type, position, direction, properties
    active_rules: list[Rule]  # parsed from current word positions
    turn_number: int
```

---

## 9. Input Handling

### 9.1 Controls

| Action       | Key                    |
|--------------|------------------------|
| Move Up      | Up Arrow / W           |
| Move Down    | Down Arrow / S         |
| Move Left    | Left Arrow / A         |
| Move Right   | Right Arrow / D        |
| Wait (skip)  | Space                  |
| Undo         | Z                      |
| Restart      | R                      |
| Pause/Menu   | Escape                 |

### 9.2 Input Timing

- Hold-to-repeat: If a direction key is held, repeat the move every 150ms after an initial 250ms delay.
- Undo repeat: Same timing as movement.

---

## 10. Visual Design

### 10.1 Art Style

- Pixel art, 24x24 per cell.
- Objects have a "wobbly" idle animation (2-3 frame cycle, organic feel).
- Dark background (#0A0A2A — near-black blue).
- Bright, saturated object colors.
- Word blocks: White text on a darker background, slight glow effect.
- Grid lines: Not visible (clean look).

### 10.2 Animation

| Animation          | Frames | Duration per frame | Style                |
|--------------------|--------|--------------------|----------------------|
| Object idle        | 3      | 200 ms             | Wobbly/breathing     |
| Object move        | 1      | 100 ms             | Slide to target      |
| Object destroy     | 3      | 100 ms             | Shrink + particles   |
| Object transform   | 4      | 80 ms              | Morph shape          |
| Object spawn       | 3      | 100 ms             | Grow from center     |
| Rule formation     | N/A    | Immediate          | Words glow briefly   |
| Level complete     | N/A    | 1000 ms            | Screen flash + fanfare|
| Undo               | N/A    | Immediate          | No animation         |

### 10.3 Rule Highlight

When a valid rule is formed:
- The participating word objects glow with a white outline (2px).
- The glow pulses subtly at 1Hz.
- Broken rules (words that were part of a rule but are no longer) lose their glow immediately.

### 10.4 Particle Effects

| Event              | Particles | Color            | Duration |
|--------------------|-----------|------------------|----------|
| Object destroyed   | 6-10      | Object color     | 300 ms   |
| SINK interaction   | 8-12      | Blue (#4488FF)   | 400 ms   |
| HOT+MELT           | 10-15     | Orange (#FF6600) | 400 ms   |
| WIN reached        | 20-30     | Gold (#FFD700)   | 1000 ms  |
| Transformation     | 8-12      | White (#FFFFFF)  | 300 ms   |

---

## 11. Scoring and Completion

### 11.1 No Score

Baba Is You does not have a traditional score. Progress is tracked by:
- Levels completed (checkmark on overworld map).
- Bonus collectibles found (flowers/stars within levels).
- Percentage completion displayed on the world map.

### 11.2 Level Completion

- A level is complete when any YOU object overlaps any WIN object.
- Multiple solutions may exist for a single level.
- Completion is permanent (once solved, always marked as solved).

### 11.3 Bonus Objectives

Some levels contain bonus flowers/orbs:
- Optional collectible that requires a harder or alternate solution.
- Tracked separately from level completion.
- Displayed as a small icon on the level node in the overworld.

---

## 12. UI Layout

### 12.1 In-Game

```
+------------------------------------------+
|                                          |
|  Level: 01-03 "Still Still Still"        |
|                                          |
|  +--+--+--+--+--+--+--+--+--+--+--+--+  |
|  |  |BA|IS|YO|  |  |  |  |  |  |  |  |  |
|  +--+--+--+--+--+--+--+--+--+--+--+--+  |
|  |  |  |  |  |##|##|##|  |  |  |  |  |  |
|  +--+--+--+--+--+--+--+--+--+--+--+--+  |
|  |  |  |  |  |##|  |##|  |  |FL|IS|WI|  |
|  +--+--+--+--+--+--+--+--+--+--+--+--+  |
|  |  |  |@B|  |##|  |##|  |  |  |  |  |  |
|  +--+--+--+--+--+--+--+--+--+--+--+--+  |
|  |  |  |  |  |##|  |##|  |>F|  |  |  |  |
|  +--+--+--+--+--+--+--+--+--+--+--+--+  |
|  |  |  |  |  |##|##|##|  |  |  |  |  |  |
|  +--+--+--+--+--+--+--+--+--+--+--+--+  |
|  |  |WA|IS|ST|  |  |  |  |  |  |  |  |  |
|  +--+--+--+--+--+--+--+--+--+--+--+--+  |
|                                          |
|  BA=BABA  IS=IS  YO=YOU  ##=WALL         |
|  WA=WALL  ST=STOP  FL=FLAG  WI=WIN       |
|  @B=Baba(object)  >F=Flag(object)        |
+------------------------------------------+
```

### 12.2 Overworld Map

```
+------------------------------------------+
|  BABA IS YOU                             |
|                                          |
|       [1]---[2]---[3]                    |
|        |           |                      |
|       [4]   [5]---[6]---[7]              |
|        |    |                             |
|       [8]---[9]--[10]                    |
|              |                            |
|             [E]  (exit to next world)     |
|                                          |
|  [1] = level node                        |
|  Completed = bright, Locked = dim        |
|  Lines = paths between levels            |
+------------------------------------------+
```

### 12.3 Pause Menu

```
+----------------------------------+
|                                  |
|  PAUSED                          |
|                                  |
|  [ RESUME    ]                   |
|  [ RESTART   ]                   |
|  [ LEVEL MAP ]                   |
|  [ SETTINGS  ]                   |
|                                  |
+----------------------------------+
```

---

## 13. Audio Design

### 13.1 Sound Effects

| Event                    | Description                          | Duration |
|--------------------------|--------------------------------------|----------|
| Move (step)              | Soft footstep / slide                | 80 ms    |
| Push object              | Scraping / pushing sound             | 100 ms   |
| Rule formed              | Musical chime (major chord)          | 300 ms   |
| Rule broken              | Dissonant tone                       | 200 ms   |
| Object destroyed         | Pop / crumble                        | 150 ms   |
| SINK interaction         | Splash                               | 300 ms   |
| HOT+MELT                 | Sizzle                               | 300 ms   |
| OPEN+SHUT                | Click / unlock                       | 200 ms   |
| Transformation           | Magical shimmer                      | 400 ms   |
| Level complete           | Triumphant fanfare                   | 1500 ms  |
| Undo                     | Reverse whoosh                       | 100 ms   |
| Restart                  | Quick reset sound                    | 200 ms   |
| Cannot move              | Soft bump                            | 80 ms    |
| DEFEAT (death)           | Sad tone                             | 300 ms   |
| TELE (teleport)          | Warp / zap                           | 200 ms   |
| Menu navigate            | UI blip                              | 50 ms    |

### 13.2 Music

- Atmospheric, ambient electronic music.
- Each world has a unique background track.
- Tempo: Slow, contemplative (~70-90 BPM).
- Style: Minimalist synth pads, light melodies.
- Music continues through level attempts (no restart on undo).
- Volume: Adjustable, default 50%.

---

## 14. Edge Cases and Complex Rules

### 14.1 Infinite Loops

- If "A IS B" and "B IS A" (mutual transformation): All A become B and all B become A. This swaps the types each time the rule is re-evaluated. To prevent infinite loops, transformations only apply once per turn.

### 14.2 No YOU Objects

- If no rule defines anything as YOU, the player cannot act.
- The game enters a "stuck" state. The player must undo or restart.
- No explicit game over screen — just undo/restart.

### 14.3 Multiple YOU Types

- If "BABA IS YOU" and "ROCK IS YOU", the player controls both.
- All YOU objects move simultaneously in the same direction.
- If one is blocked and another is not, only the unblocked one moves.

### 14.4 Self-Referential Rules

- "WORD IS PUSH" — All word objects are pushable (default behavior).
- "WORD IS STOP" — Word objects become immovable walls.
- "WORD IS YOU" — The player controls the word objects themselves.
- "WORD IS WIN" — Touching any word object wins the level.
- "TEXT IS NOT PUSH" — Word objects can no longer be pushed.

### 14.5 "IS" Chains

- "BABA IS BABA" — No effect (Baba stays Baba, but this is a valid rule).
- "BABA IS FLAG IS WIN" — NOT valid. "IS" cannot chain. Parsed as "BABA IS FLAG" and leftover "IS WIN".

### 14.6 Stacking

- Multiple objects can occupy the same cell.
- All interactions (DEFEAT, SINK, HOT+MELT, etc.) apply to all overlapping objects.
- FLOAT objects exist on a separate layer and don't interact with non-FLOAT objects (except YOU entering the cell).

---

## 15. Rule Priority and Conflict Resolution

1. NOT takes precedence: "BABA IS STOP" + "BABA IS NOT STOP" → Baba is NOT stop.
2. Transformations apply after all rules are parsed.
3. If an object gains and loses a property in the same turn (via NOT), the NOT wins.
4. If two conflicting transformations apply ("BABA IS ROCK" and "BABA IS FLAG"), both apply: Baba objects transform into both Rock and Flag (one copy becomes Rock, another becomes Flag — or the later-parsed rule wins, depending on implementation).

---

## 16. Data Persistence

```json
{
  "current_world": 2,
  "levels_completed": ["00-01", "00-02", "00-03", "01-01", "01-02"],
  "bonuses_collected": ["00-01", "01-02"],
  "settings": {
    "music_volume": 50,
    "sfx_volume": 70,
    "move_repeat_delay": 250,
    "move_repeat_interval": 150
  }
}
```

---

## 17. Performance Requirements

| Metric               | Target           |
|-----------------------|------------------|
| Input latency         | < 16ms           |
| Rule parsing          | < 5ms            |
| Push chain resolution | < 5ms            |
| Animation frame time  | < 16.67ms        |
| Undo operation        | < 1ms            |
| Memory per undo state | < 10 KB          |
| Max undo depth        | 1000 turns       |
| Level load time       | < 500ms          |

---

## 18. Testing Checklist

1. Basic sentence parsing: NOUN IS PROPERTY works in both horizontal and vertical.
2. AND correctly chains subjects and properties.
3. NOT correctly negates properties.
4. PUSH chains resolve correctly (multi-object chains).
5. STOP blocks movement correctly.
6. YOU transfers control to the correct object(s).
7. WIN triggers level completion.
8. DEFEAT destroys YOU objects.
9. SINK destroys both objects.
10. HOT + MELT interaction works.
11. OPEN + SHUT interaction works.
12. IS (transformation) converts all instances correctly.
13. HAS spawns correct object on destruction.
14. MOVE objects move automatically each turn.
15. TELE teleports objects correctly.
16. FLOAT objects exist on separate layer.
17. WEAK objects are destroyed when overlapped.
18. Undo restores exact previous state.
19. Unlimited undo works correctly.
20. No YOU = player cannot act (undo/restart only).
21. Word objects are pushable by default.
22. Breaking a rule removes its effect immediately.
23. Multiple YOU types all move simultaneously.
24. Level map shows correct completion status.
25. All worlds are accessible after completing prerequisites.
