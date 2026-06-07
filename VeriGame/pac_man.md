# 01_pac_man - Pac-Man (1980 Namco Arcade)

## 1. Product Definition
- **Prototype Anchor**: Pac-Man (1980, Namco / Midway)
- **Genre Family**: Arcade / Maze Chase
- **Core Fantasy**: Navigate a maze as a yellow, circular character, eating all dots while evading four uniquely-programmed ghosts whose combined AI creates emergent pursuit pressure.
- **Camera / Presentation**: Top-down 2D single-screen maze rendered on a vertically-oriented CRT monitor.
- **Target Session Length**: 1-5 minutes per credit for beginners; 4-6 hours for a perfect game (255 levels + kill screen).
- **Target Skill Curve**: Immediately intuitive controls; deep mastery through pattern memorization, cornering technique, and ghost AI exploitation.

## 2. Win/Lose Contract
- **Primary Win Condition**: Eat all 240 dots and 4 power pellets on the current level to advance.
- **Primary Lose Condition**: Contact with a ghost in normal (chase/scatter) mode consumes one life. Losing all lives ends the game.
- **Board Definition**: Single static maze, 28 tiles wide x 36 tiles tall (playable area 28 x 31 tiles), reused for every level.
- **Game Termination**: The game has no programmed ending. Level 256 triggers a kill screen due to an 8-bit integer overflow, rendering the right half of the maze unplayable.
- **Extra Lives**: One extra life awarded at 10,000 points (configurable via DIP switch to 10,000, 15,000, 20,000, or none). Player starts with 3 lives. Maximum displayed lives: 5 (additional lives are earned but not shown).

## 3. Technical Foundation

### 3.1 Original Hardware
| Parameter | Value |
|---|---|
| CPU | Zilog Z80A @ 3.072 MHz |
| Display Resolution | 224 x 288 pixels (portrait orientation) |
| Tile Size | 8 x 8 pixels |
| Tile Grid | 28 columns x 36 rows |
| Playable Maze Area | 28 columns x 31 rows (rows 3-33) |
| Frame Rate | 60.606060 Hz (NTSC-derived) |
| ROM | 16 KB |
| RAM | 2 KB video RAM + 1 KB color RAM + 1 KB general RAM |
| Sprite Size | 16 x 16 pixels (2 x 2 tiles) |
| Max Sprites On Screen | 6 (Pac-Man + 4 ghosts + 1 bonus fruit) |
| Sound | 3-channel WSG (Waveform Sound Generator) |
| Color Palette | 16 colors available; 13 unique colors used in-game |

### 3.2 Base Speed Reference
All speed values in this document are expressed as percentages of a "base speed" of approximately **75.7576 pixels/second** (exactly 80 pixels per second at 100%). One tile = 8 pixels, so 100% speed = 10 tiles/second. Movement is sub-pixel; the game tracks positions at pixel granularity within each frame.

### 3.3 Simulation Tick
- Fixed update at ~60.61 FPS (one tick per VBLANK interrupt).
- All movement, collision, and AI decisions are evaluated once per frame.
- Speeds below 100% are implemented via a frame-skip pattern: e.g., 80% speed moves 1 pixel on 4 out of every 5 frames.

## 4. Core Loop (Implementation Sequence)
1. Read joystick input (4-directional) and buffer desired direction.
2. Evaluate Pac-Man movement: apply cornering, attempt buffered turn, or continue current direction.
3. Evaluate ghost AI: for each ghost, determine mode (scatter/chase/frightened/eaten), select target tile, choose direction at next intersection.
4. Move all entities by their speed-determined pixel count for this frame.
5. Check Pac-Man's current tile: consume dot/pellet/fruit if present.
6. Evaluate collisions between Pac-Man and each ghost.
7. Update ghost mode timers (scatter/chase cycling, frightened countdown).
8. Update ghost house release counters and timers.
9. Check level completion (all 244 edibles consumed).
10. Emit rendering, sound, and score update events.

## 5. Input Specification
| Action | Input | Technical Constraint |
|---|---|---|
| Move Up | Joystick Up | Buffered; executes when Pac-Man reaches a tile where upward movement is possible |
| Move Down | Joystick Down | Same buffering rules |
| Move Left | Joystick Left | Same buffering rules |
| Move Right | Joystick Right | Same buffering rules |
| Start (1P) | 1P Start Button | Requires credit; begins game |
| Start (2P) | 2P Start Button | Requires 2 credits; alternating turns |
| Insert Coin | Coin Switch | Increments credit counter |

### 5.1 Input Buffering and Cornering
- The player's desired direction is stored and continuously attempted each frame.
- If Pac-Man reaches a tile center where a wall blocks the desired direction, he continues in his current direction (or stops if also blocked).
- **Cornering**: Pac-Man can begin a turn up to several pixels before reaching the exact center of an intersection tile. When approaching a turn, holding the desired direction early causes Pac-Man to "cut the corner," effectively covering less distance than ghosts do on the same turn. This gives Pac-Man a subtle but critical speed advantage around corners that ghosts cannot exploit.

## 6. Top-Level State Machines

### 6.1 Application State Machine
- `AttractMode`: Demo gameplay loop with ghost name/nickname display. Cycles until coin inserted.
- `CreditWait`: "PUSH START BUTTON" displayed. Waiting for 1P or 2P start.
- `Ready`: "READY!" text displayed. Intro music plays (~4.5 seconds). Entities at start positions.
- `Playing`: Active maze gameplay. Contains sub-states for normal play, frightened mode, ghost-eaten pause, and death sequence.
- `LevelComplete`: Maze flashes white/blue 4 times (~2 seconds). Transition to next level.
- `Intermission`: Cutscene plays after specific levels (see Section 14).
- `GameOver`: "GAME OVER" text displayed (~2 seconds). Returns to AttractMode or CreditWait.

### 6.2 Playing Sub-States
- `Normal`: Scatter/Chase mode cycling active. Standard ghost AI and speeds.
- `Frightened`: Power pellet consumed. Ghosts turn blue, reverse direction, move slowly, and are edible.
- `GhostEatenPause`: Screen freezes ~1 second to display point value (200/400/800/1600) when a ghost is eaten.
- `PacManDeath`: All entities freeze ~1 second, then Pac-Man plays 11-frame death animation (~1.5 seconds). If lives remain, reset to Ready state. Otherwise, GameOver.

### 6.3 Ghost State Machine
- `InHouse`: Bouncing up and down inside the ghost house. Waiting for release condition.
- `LeavingHouse`: Moving upward through the ghost house exit.
- `Scatter`: Targeting assigned home corner tile.
- `Chase`: Targeting tile determined by individual ghost personality AI.
- `Frightened`: Moving pseudo-randomly at intersections. Vulnerable to being eaten.
- `Eaten`: Eyes only, returning to ghost house at high speed (~2x normal). Target: ghost house entrance.
- `EnteringHouse`: Moving down into the ghost house to regenerate.
- `Regenerated`: Brief pause inside house, then exits and resumes current global mode.

## 7. Maze Layout

### 7.1 Maze Dimensions
- Total display grid: 28 x 36 tiles (224 x 288 pixels).
- Top 3 rows: Score display area.
- Rows 3-33: Playable maze area (28 x 31 tiles).
- Bottom 2 rows: Lives remaining and fruit level indicators.

### 7.2 Maze Contents
| Element | Count | Tile Positions |
|---|---|---|
| Regular Dots | 240 | Distributed throughout corridors |
| Power Pellets | 4 | Near the four corners of the maze |
| Ghost House | 1 | Center of maze, rows 15-19, columns 10-17 |
| Warp Tunnels | 2 | Row 17, columns 0-5 (left) and 22-27 (right) |
| Fruit Spawn Point | 1 | Below ghost house, tile (14, 20) |
| Pac-Man Start | 1 | Tile (14, 26), below ghost house |

### 7.3 Maze Structure (Symbolic)
The maze is horizontally symmetrical. Key structural features:
```
############################
#............##............#
#.####.#####.##.#####.####.#
#o####.#####.##.#####.####o#
#.####.#####.##.#####.####.#
#..........................#
#.####.##.########.##.####.#
#.####.##.########.##.####.#
#......##....##....##......#
######.##### ## #####.######
     #.##### ## #####.#
     #.##          ##.#
     #.## ###--### ##.#
######.## # HOUSE# ##.######
      .   # GHOST#   .
######.## # AREA # ##.######
     #.## ######## ##.#
     #.##          ##.#
     #.## ######## ##.#
######.## ######## ##.######
#............##............#
#.####.#####.##.#####.####.#
#.####.#####.##.#####.####.#
#o..##.......  .......##..o#
###.##.##.########.##.##.###
###.##.##.########.##.##.###
#......##....##....##......#
#.##########.##.##########.#
#.##########.##.##########.#
#..........................#
############################
```
Legend: `#` = wall, `.` = dot, `o` = power pellet, `-` = ghost house gate, spaces inside maze = open corridor.

### 7.4 Ghost House
- Enclosed rectangular area in the center of the maze.
- Single one-way exit gate at the top center (the "door" made of a horizontal line).
- Only ghosts can pass through the gate. Pac-Man cannot enter.
- Ghosts inside the house bob up and down vertically while waiting to be released.

### 7.5 Warp Tunnels
- Located at row 17 on both the left and right edges of the maze.
- When any entity exits one side, it wraps to the opposite side.
- Pac-Man travels through at normal speed.
- Ghosts travel through at significantly reduced speed (see speed tables).
- The tunnel slow zone extends several tiles inward from each edge (approximately columns 0-5 and 22-27).

### 7.6 No-Upward-Turn Restriction Zones
Four specific intersection tiles prevent ghosts from choosing to turn upward during scatter and chase modes. These tiles are located:
- Two tiles directly above the ghost house, at (12, 14) and (15, 14).
- Two tiles in the lower third of the maze, at (12, 26) and (15, 26).

This restriction does NOT apply during frightened mode. Ghosts entering these tiles from above can still reverse upward if a mode switch forces a direction reversal at that exact moment.

## 8. Entity Specification

### 8.1 Pac-Man
| Property | Value |
|---|---|
| Sprite Size | 16 x 16 pixels |
| Animation Frames | 3 per direction (mouth closed, partially open, fully open) + 1 full circle frame |
| Animation Cycle | Mouth opens and closes continuously while moving |
| Start Position | Tile (14, 26), facing left |
| Death Animation | 11 frames: Pac-Man opens mouth progressively wider in all directions, then shrinks to nothing |
| Death Animation Duration | ~1.5 seconds |

### 8.2 Ghosts (General)
| Property | Value |
|---|---|
| Sprite Size | 16 x 16 pixels |
| Animation Frames | 2 per direction (body wobble), 2 for frightened (blue), 2 for flashing (blue/white alternation), 4 for eyes-only (one per direction) |
| Body Shape | Rounded top, wavy bottom edge (3 "tentacles") |

### 8.3 Individual Ghost Profiles

#### Blinky (Red) -- "Shadow"
| Property | Value |
|---|---|
| Character | "Oikake" (JP) / "Shadow" (EN) |
| Personality | Aggressive chaser |
| Start Position | Directly above ghost house, outside, at tile (14, 14) |
| Start Direction | Left |
| Scatter Target Tile | (25, 0) -- top-right corner |
| Chase Target | Pac-Man's exact current tile |
| Special Mechanic | Cruise Elroy (see Section 8.4) |

#### Pinky (Pink) -- "Speedy"
| Property | Value |
|---|---|
| Character | "Machibuse" (JP) / "Speedy" (EN) |
| Personality | Ambusher |
| Start Position | Inside ghost house, center |
| Start Direction | Down (bouncing) |
| Scatter Target Tile | (2, 0) -- top-left corner |
| Chase Target | 4 tiles ahead of Pac-Man in Pac-Man's current facing direction |
| Overflow Bug | When Pac-Man faces UP, the target is calculated as 4 tiles up AND 4 tiles left due to an arithmetic overflow in the original Z80 code |

#### Inky (Cyan) -- "Bashful"
| Property | Value |
|---|---|
| Character | "Kimagure" (JP) / "Bashful" (EN) |
| Personality | Unpredictable flanker |
| Start Position | Inside ghost house, left of center |
| Start Direction | Up (bouncing) |
| Scatter Target Tile | (27, 35) -- bottom-right corner |
| Chase Target | Complex two-step: (1) Find tile 2 tiles ahead of Pac-Man's current direction. (2) Draw vector from Blinky's position to that tile. (3) Double the vector length. The endpoint is Inky's target. |
| Overflow Bug | Same as Pinky: when Pac-Man faces UP, the "2 tiles ahead" reference point is actually 2 tiles up and 2 tiles left |

#### Clyde (Orange) -- "Pokey"
| Property | Value |
|---|---|
| Character | "Otoboke" (JP) / "Pokey" (EN) |
| Personality | Fickle, avoidant |
| Start Position | Inside ghost house, right of center |
| Start Direction | Up (bouncing) |
| Scatter Target Tile | (0, 35) -- bottom-left corner |
| Chase Target | If more than 8 tiles away from Pac-Man (Euclidean distance): same as Blinky (Pac-Man's exact tile). If within 8 tiles: switches to scatter target (bottom-left corner), effectively fleeing. |

### 8.4 Cruise Elroy (Blinky's Speed Boost)
When the number of remaining dots in the maze drops below a level-specific threshold, Blinky enters "Cruise Elroy" mode:
- **Elroy 1**: Speed increases to match or exceed Pac-Man. Blinky also ignores scatter mode, continuing to chase even when other ghosts scatter.
- **Elroy 2**: At an even lower dot threshold, Blinky speeds up further.
- If Pac-Man dies while Blinky is in Elroy mode, Blinky reverts to normal speed until the dot counter threshold is met again (he re-enters Elroy once enough dots are eaten on the new life).

| Level | Elroy 1 Dots Left | Elroy 1 Speed | Elroy 2 Dots Left | Elroy 2 Speed |
|---|---|---|---|---|
| 1 | 20 | 80% | 10 | 85% |
| 2 | 30 | 90% | 15 | 95% |
| 3-4 | 40 | 90% | 20 | 95% |
| 5-6 | 40 | 100% | 20 | 105% |
| 7-8 | 50 | 100% | 25 | 105% |
| 9-11 | 60 | 100% | 30 | 105% |
| 12-14 | 80 | 100% | 40 | 105% |
| 15-18 | 100 | 100% | 50 | 105% |
| 19+ | 120 | 100% | 60 | 105% |

## 9. Ghost AI System

### 9.1 Movement Rules
1. Ghosts move tile-by-tile. Upon entering a new tile, the ghost evaluates the NEXT tile it will enter and pre-selects a direction.
2. **No Reversal Rule**: A ghost can never voluntarily reverse its direction of travel. The only exception is a forced reversal triggered by a mode switch (scatter-to-chase, chase-to-scatter, or any-mode-to-frightened).
3. At an intersection (3+ exits excluding reversal), the ghost calculates the Euclidean distance from each candidate next-tile to its current target tile. It chooses the direction that minimizes this distance.
4. **Tie-breaking priority** when two directions yield equal distance: Up > Left > Down > Right (this is the fixed priority order).
5. Ghosts cannot stop or slow down at intersections; they always move continuously.

### 9.2 Scatter/Chase Mode Cycling
The game alternates between global Scatter and Chase modes on a fixed timer. All ghosts (except Cruise Elroy Blinky) obey the current global mode. Each mode switch forces all ghosts to immediately reverse direction.

| Phase | Level 1 | Levels 2-4 | Levels 5+ |
|---|---|---|---|
| Scatter 1 | 7 sec | 7 sec | 5 sec |
| Chase 1 | 20 sec | 20 sec | 20 sec |
| Scatter 2 | 7 sec | 7 sec | 5 sec |
| Chase 2 | 20 sec | 20 sec | 20 sec |
| Scatter 3 | 5 sec | 5 sec | 5 sec |
| Chase 3 | 20 sec | 1033 sec | 1037 sec |
| Scatter 4 | 5 sec | 1/60 sec | 1/60 sec |
| Chase 4 | Indefinite | Indefinite | Indefinite |

- The scatter/chase timer pauses during frightened mode and resumes when frightened mode ends.
- The timer resets at the start of each level and after each life loss.
- After the final scatter period, ghosts remain in chase mode permanently for the rest of the level.

### 9.3 Frightened Mode
When Pac-Man eats a power pellet:
1. All ghosts immediately reverse direction.
2. Ghosts enter frightened mode: they turn blue, slow down, and choose directions pseudo-randomly at intersections.
3. The frightened timer counts down (see table below). When it nears zero, ghosts begin flashing blue/white to warn the player.
4. When the timer expires, ghosts instantly revert to their current scatter/chase mode (no reversal on exit from frightened).
5. On levels where frightened time = 0, ghosts still reverse direction when a power pellet is eaten but do not turn blue or become edible.

### 9.4 Ghost Eaten (Eyes) State
When Pac-Man eats a frightened ghost:
1. The game pauses for ~1 second to display the point value.
2. The ghost becomes "eyes only" and targets the ghost house entrance tile at very high speed (approximately 2x normal ghost speed, unaffected by tunnel slow zones).
3. Upon reaching the ghost house, the eyes float down inside, the ghost regenerates, and then exits normally.
4. A regenerated ghost resumes the current global mode immediately upon exiting the house.

### 9.5 Ghost House Release Logic
Ghosts exit the house via three mechanisms, checked in this priority order:

**1. Personal Dot Counter** (primary mechanism at level start):
- Each ghost has an individual dot counter that increments each time Pac-Man eats a dot (only the highest-priority ghost waiting in the house has its counter active).
- Priority order: Pinky > Inky > Clyde.
- When a ghost's counter reaches its "dot limit," it exits immediately.

| Level | Pinky Limit | Inky Limit | Clyde Limit |
|---|---|---|---|
| 1 | 0 | 30 | 60 |
| 2 | 0 | 0 | 50 |
| 3+ | 0 | 0 | 0 |

**2. Global Dot Counter** (activated after a life is lost):
- After any life loss, the personal counters are abandoned and a single global counter takes over.
- The global counter increments with each dot eaten.
- Pinky exits at count 7, Inky at 17, Clyde at 32.
- If Clyde is still in the house when the counter reaches 32, the global counter deactivates and reverts to personal counters. If Clyde has already exited, the global counter stays active but no further ghosts need releasing.

**3. Inactivity Timer** (fallback):
- A timer runs continuously and resets each time Pac-Man eats a dot.
- If the timer reaches its limit without Pac-Man eating a dot, the highest-priority ghost in the house is forced to exit.
- Timer limit: 4 seconds (levels 1-4), 3 seconds (levels 5+).

### 9.6 Starting Positions and Behavior
| Ghost | Start Position | Start State | Initial Direction |
|---|---|---|---|
| Blinky | Above ghost house, tile (14, 14) | Scatter (outside house) | Left |
| Pinky | Center of ghost house | InHouse (exits immediately on level 1) | Down |
| Inky | Left of center in ghost house | InHouse | Up |
| Clyde | Right of center in ghost house | InHouse | Up |

- Pac-Man starts at tile (14, 26), facing left.
- On the "READY!" screen, all entities are visible but frozen for ~4.5 seconds while the intro jingle plays.

## 10. Level Progression

### 10.1 Speed Table (Percentage of Base Speed)

| Level | Pac-Man Normal | Pac-Man Dots | Ghost Normal | Ghost Tunnel | Pac-Man Fright | Pac-Man Fright Dots | Ghost Fright | Fright Time (sec) | Flashes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 80% | 71% | 75% | 40% | 90% | 79% | 50% | 6 | 5 |
| 2 | 90% | 79% | 85% | 45% | 95% | 83% | 55% | 5 | 5 |
| 3 | 90% | 79% | 85% | 45% | 95% | 83% | 55% | 4 | 5 |
| 4 | 90% | 79% | 85% | 45% | 95% | 83% | 55% | 3 | 5 |
| 5 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 2 | 5 |
| 6 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 5 | 5 |
| 7 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 2 | 5 |
| 8 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 2 | 5 |
| 9 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 1 | 3 |
| 10 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 5 | 5 |
| 11 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 2 | 5 |
| 12 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 1 | 3 |
| 13 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 1 | 3 |
| 14 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 3 | 5 |
| 15 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 1 | 3 |
| 16 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 1 | 3 |
| 17 | 100% | 87% | 95% | 50% | -- | -- | -- | 0 | 0 |
| 18 | 100% | 87% | 95% | 50% | 100% | 87% | 60% | 1 | 3 |
| 19 | 100% | 87% | 95% | 50% | -- | -- | -- | 0 | 0 |
| 20 | 100% | 87% | 95% | 50% | -- | -- | -- | 0 | 0 |
| 21+ | 90% | 79% | 95% | 50% | -- | -- | -- | 0 | 0 |

**Notes:**
- "Pac-Man Dots" speed is the reduced speed while actively eating a dot (Pac-Man pauses for 1 frame each time he eats a regular dot, and 3 frames for a power pellet).
- Levels marked "--" for frightened values means power pellets still cause ghosts to reverse direction, but they do NOT turn blue, do NOT slow down, and are NOT edible.
- From level 21 onward, Pac-Man slows to 90% while ghosts remain at 95%, making ghosts faster than Pac-Man in straight corridors.

### 10.2 Dot-Eating Speed Penalty
- Eating a regular dot: Pac-Man is stationary for **1 frame** (1/60 second).
- Eating a power pellet: Pac-Man is stationary for **3 frames** (3/60 second).
- This cumulative slowdown means Pac-Man moves noticeably slower along dot-filled corridors.

## 11. Scoring System

### 11.1 Point Values
| Action | Points |
|---|---|
| Eat regular dot | 10 |
| Eat power pellet | 50 |
| Eat 1st ghost (per power pellet) | 200 |
| Eat 2nd ghost (per power pellet) | 400 |
| Eat 3rd ghost (per power pellet) | 800 |
| Eat 4th ghost (per power pellet) | 1,600 |
| All 4 ghosts from one power pellet | 3,000 (total) |

### 11.2 Per-Level Base Points (Dots Only)
- 240 dots x 10 = 2,400 points
- 4 power pellets x 50 = 200 points
- Total dots/pellets per level = **2,600 points**

### 11.3 Maximum Ghost Points Per Level
- 4 power pellets x 3,000 points (all 4 ghosts each) = **12,000 points**

### 11.4 Perfect Game Score
- **3,333,360 points**: Achieved by eating every dot, power pellet, fruit, and all four ghosts per power pellet on all 255 levels, plus maximum possible points on the broken level 256.
- First achieved by Billy Mitchell on July 3, 1999.

### 11.5 Score Display
- Up to 7 digits displayed.
- No score rollover (the display can show up to 9,999,990 but a perfect game ends before that).
- High score displayed at the top center of the screen.

## 12. Bonus Items (Fruit)

### 12.1 Fruit Appearance
- The first fruit appears after Pac-Man eats **70 dots**.
- The second fruit appears after Pac-Man eats **170 dots**.
- Each fruit remains on screen for approximately **9-10 seconds** before disappearing.
- Fruit spawns at the fixed position below the ghost house at tile (14, 20).
- Fruit does not move.

### 12.2 Fruit Table
| Level | Fruit | Points |
|---|---|---|
| 1 | Cherry | 100 |
| 2 | Strawberry | 300 |
| 3-4 | Peach (Orange) | 500 |
| 5-6 | Apple | 700 |
| 7-8 | Grapes (Melon) | 1,000 |
| 9-10 | Galaxian Flagship | 2,000 |
| 11-12 | Bell | 3,000 |
| 13+ | Key | 5,000 |

### 12.3 Fruit Display
- The current level's fruit icon is shown in the bottom-right corner of the screen.
- Up to 7 fruit icons are displayed, representing the most recent 7 levels completed.

## 13. Game States and Timing

### 13.1 Game Start Sequence
1. Player inserts coin and presses Start.
2. Maze is drawn with all 240 dots and 4 power pellets.
3. "PLAYER ONE" text appears briefly, then "READY!" text appears below the ghost house.
4. Intro jingle plays (~4.5 seconds). All entities are visible at starting positions but frozen.
5. "READY!" text disappears and gameplay begins.

### 13.2 Level Complete Sequence
1. Last dot/pellet is consumed. All entities freeze.
2. Brief pause (~1 second).
3. Maze walls flash between blue and white, 4 complete cycles (~2 seconds).
4. Screen clears, new level initializes with all dots replaced.
5. "READY!" screen for ~2 seconds (shorter than initial start), then play resumes.

### 13.3 Pac-Man Death Sequence
1. Pac-Man contacts a ghost in non-frightened mode.
2. All entities freeze for ~1 second.
3. Ghosts disappear.
4. Pac-Man plays death animation: mouth opens wider and wider in a circular pattern, then collapses to nothing (11 frames over ~1.5 seconds).
5. If lives remain: brief pause, then reset entities to starting positions with "READY!" screen (~2 seconds).
6. If no lives remain: "GAME OVER" text displayed for ~2 seconds.

### 13.4 Ghost Eaten Pause
1. Game freezes for ~1 second.
2. Point value (200/400/800/1600) is displayed at the ghost's position.
3. Pac-Man is invisible during this pause.
4. After the pause, the ghost becomes eyes-only and gameplay resumes. The frightened timer continues counting during this pause.

### 13.5 Attract Mode
- Loops continuously when no credits are inserted.
- Displays the game title, a brief demo of AI-controlled Pac-Man playing the maze, and the ghost character introduction screen showing each ghost's name, nickname, and color.
- Ghost introduction displays:
  - `-SHADOW    "BLINKY"` (red)
  - `-SPEEDY    "PINKY"` (pink)
  - `-BASHFUL   "INKY"` (cyan)
  - `-POKEY     "CLYDE"` (orange)

## 14. Intermission Cutscenes

Three unique intermissions play between specific levels. Each lasts approximately 10-12 seconds.

| Intermission | Plays After Level(s) | Description |
|---|---|---|
| Act 1 | 2 | Blinky chases Pac-Man across the screen from right to left. Then a giant Pac-Man chases a frightened Blinky back from left to right. |
| Act 2 | 5 | Blinky chases Pac-Man across the screen. Blinky's ghost "sheet" catches on a nail in the ground and tears, revealing his naked form. |
| Act 3 | 9, 13, 17 | Blinky chases Pac-Man with a visibly patched sheet. After passing off-screen, Blinky returns from the left dragging his torn sheet behind him, naked and defeated. |

- Intermissions play automatically after the maze-flash sequence of the specified level.
- The player cannot skip intermissions.
- After level 17, no more intermissions play for the remainder of the game.

## 15. Level 256 Kill Screen

### 15.1 Technical Cause
- The internal level counter is stored as an unsigned 8-bit integer (0-255).
- After completing level 255 (internal counter value 255), incrementing the counter causes it to overflow to 0.
- The fruit-drawing subroutine uses this counter to determine how many fruit symbols to draw in the level indicator at the bottom of the screen. When the value is 0, the routine interprets this as 256 due to the loop structure, attempting to draw 256 fruit symbols.
- This overflows the screen memory, corrupting the right half of the maze with random tiles, characters, and colors.

### 15.2 Gameplay Impact
- The left half of the maze is normal and playable.
- The right half is an unnavigable mess of garbled graphics.
- Only 9 dots are accessible on the corrupted right side, plus 122 on the intact left side = **131 dots total** (out of the 244 normally required to clear the level).
- Since Pac-Man cannot eat enough dots to trigger level completion, the game becomes permanently stuck.
- The player can continue playing the accessible portion until all lives are lost.

## 16. Audio Design

### 16.1 Sound Hardware
- Namco WSG (Waveform Sound Generator): 3 independent sound channels.
- Channels can output custom waveforms stored in ROM.
- All sounds are synthesized, not sampled.

### 16.2 Sound Effects Inventory
| Sound | Trigger | Description |
|---|---|---|
| Game Start Jingle | Level start (first level or after coin-in) | Distinctive melodic intro (~4.5 seconds), sets tempo and mood |
| Waka-Waka (Munch) | Pac-Man eats a dot | Two alternating tones in rapid succession; pitch varies slightly between the two "waka" sounds. Approximately D+A followed by C#+G# |
| Power Pellet Siren | Power pellet eaten (frightened mode active) | Replaces the normal siren; lower, more ominous pulsing tone |
| Normal Siren | During regular gameplay | Continuous background tone that oscillates. Pitch increases with each level and when fewer dots remain |
| Siren Speed-Up | As dots are consumed | The siren gradually increases in tempo/pitch throughout the level |
| Ghost Eaten | Pac-Man eats a frightened ghost | Quick ascending electronic sound |
| Eyes Returning | Eaten ghost eyes traveling to house | Distinctive rapid pulsing sound while eyes traverse the maze |
| Fruit Eaten | Pac-Man eats a bonus fruit | Short celebratory sound |
| Extra Life | Score reaches 10,000 | Brief musical cue indicating a life was awarded |
| Death | Pac-Man is caught by a ghost | Descending spiral sound lasting ~1.5 seconds, synchronized with the death animation |
| Intermission Music | During cutscenes | Unique musical piece for each intermission act |
| Credit | Coin inserted | Short acknowledgment sound |

### 16.3 Sound Priority
- The game can produce limited simultaneous sounds due to 3 channels.
- Priority hierarchy: Death > Ghost Eaten > Waka-Waka > Siren.
- Waka-waka sound plays only while Pac-Man is actively eating dots; silence when moving through empty corridors.
- The background siren is always present during normal and frightened play, changing character based on game state.

## 17. Animation System

### 17.1 Pac-Man Animation
| State | Frames | Cycle Rate |
|---|---|---|
| Moving (any direction) | 3 frames: mouth closed, half-open, fully open | Continuous loop at ~10 cycles/sec |
| Idle (between levels) | 1 frame: mouth half-open facing current direction | Static |
| Death | 11 frames: progressive mouth opening expanding 360 degrees, then shrinking to nothing | ~7 frames/sec |
| Warp tunnel | Same as moving | Unchanged |

### 17.2 Ghost Animation
| State | Frames | Details |
|---|---|---|
| Normal (per direction) | 2 frames: body wobble (tentacles alternate) | Continuous loop |
| Frightened (blue) | 2 frames: same wobble, uniform blue color, simplified wavy mouth | Continuous loop |
| Flashing (warning) | 4 frames: alternating blue/white body wobble | Flashes accelerate as timer nears zero |
| Eyes Only (eaten) | 1 frame per direction (2 eyeballs with pupils indicating direction) | No animation cycle |
| In House | 2 frames: wobble while bobbing up/down | Continuous loop |

### 17.3 Power Pellet Animation
- Power pellets blink on/off at a fixed rate (~6 times/second) for visual emphasis.
- Regular dots do not animate.

### 17.4 Fruit Animation
- Fruit sprites do not animate; they are static images.
- Point value text (100-5000) appears briefly at the fruit's position when eaten.

### 17.5 Maze Animation
- Level complete: maze walls flash blue/white 4 times.
- All wall tiles use the same blue color during normal play (color changes between levels were not present in the original Pac-Man; maze is always blue).

## 18. UI Layout

### 18.1 Screen Layout (224 x 288 pixels)
```
+----------------------------+
|  1UP    HIGH SCORE    2UP  |  <- Row 0-2: Score area
|  00       0000        00   |
|                            |
| +------------------------+ |
| |                        | |  <- Rows 3-33: Maze area
| |      GAME MAZE         | |     (28 x 31 tiles)
| |                        | |
| |    [Ghost House]       | |
| |                        | |
| |      [Pac-Man]         | |
| +------------------------+ |
|                            |
| [Lives] [Fruit Indicators] |  <- Rows 34-35: Status bar
+----------------------------+
```

### 18.2 Score Display
- **1UP Score**: Top-left. Current player 1 score, up to 7 digits, right-aligned.
- **HIGH SCORE**: Top-center. Highest score achieved, persists across games (battery-backed RAM or cleared on power cycle depending on board revision).
- **2UP Score**: Top-right. Player 2 score in 2-player alternating mode.

### 18.3 Status Bar (Bottom)
- **Lives Remaining**: Bottom-left. Displayed as Pac-Man icons (max 5 shown even if more earned). Shows lives minus the current active life.
- **Level Fruit Indicators**: Bottom-right. Shows fruit icons for the current and up to 6 previous levels (max 7 icons). Scrolls as levels increase.

### 18.4 In-Game Text
| Text | When Displayed | Position |
|---|---|---|
| "READY!" | Before each life begins | Below ghost house, yellow text |
| "GAME OVER" | All lives lost | Center of maze, red text |
| "PLAYER ONE" | Game start | Center of maze, cyan text |
| "PLAYER TWO" | 2P game, player 2's turn | Center of maze, cyan text |
| Point values (200-1600) | Ghost eaten | At ghost's position, temporary |
| Fruit point values | Fruit eaten | At fruit's position, temporary |

## 19. Color Palette

### 19.1 Entity Colors
| Entity | Primary Color | Hex Approximation |
|---|---|---|
| Pac-Man | Yellow | #FFFF00 |
| Blinky | Red | #FF0000 |
| Pinky | Pink | #FFB8FF |
| Inky | Cyan | #00FFFF |
| Clyde | Orange | #FFB852 |
| Frightened Ghost | Dark Blue | #2121DE |
| Flashing Ghost (warning) | Alternating Blue/White | #2121DE / #FFFFFF |
| Ghost Eyes | White with blue pupils | #FFFFFF / #2121DE |
| Maze Walls | Blue | #2121DE |
| Dots | #FFB8AE (peach/cream) | |
| Power Pellets | #FFB8AE (same as dots, but larger and blinking) | |
| Text (score) | White | #FFFFFF |
| "READY!" text | Yellow | #FFFF00 |
| "GAME OVER" text | Red | #FF0000 |
| Background | Black | #000000 |

## 20. Collision System

### 20.1 Collision Detection
- Collision between Pac-Man and ghosts is checked by comparing their current tile positions.
- If Pac-Man and a ghost occupy the same tile on the same frame, a collision is triggered.
- Collision type depends on the ghost's current state:
  - **Normal/Scatter/Chase ghost**: Pac-Man dies (life lost).
  - **Frightened ghost**: Ghost is eaten (points awarded, ghost becomes eyes).
  - **Eyes/Eaten ghost**: No collision (Pac-Man passes through safely).

### 20.2 Collision Edge Cases
- It is possible for Pac-Man and a ghost to "pass through" each other between frames if both are moving at high speed in opposite directions through the same tile. This is because the game checks tile overlap per-frame, not continuous path intersection.
- When Pac-Man eats a power pellet and ghosts reverse direction, there is a brief window where a ghost that was adjacent might reverse onto Pac-Man's tile. The game handles this gracefully: the ghost is now frightened, so Pac-Man eats it.

## 21. Difficulty Scaling Summary

### 21.1 Difficulty Phases
| Phase | Levels | Characteristics |
|---|---|---|
| Learning | 1 | Slow speeds. Long frightened time (6 sec). Wide Elroy thresholds. |
| Developing | 2-4 | Moderate speed increase. Frightened time decreasing (5-3 sec). More ghost house releases. |
| Challenging | 5-8 | Full Pac-Man speed. Short frightened time (2 sec). Ghosts at 95%. |
| Expert | 9-16 | Minimal or no frightened time on some levels. Elroy thresholds widening. Long chase periods. |
| Punishing | 17-20 | Some levels have 0 frightened time (ghosts can never be eaten). |
| Endgame | 21+ | Pac-Man slows to 90%, ghosts remain at 95%. Zero frightened time. Ghosts are permanently faster. Consistent forever. |

### 21.2 Key Design Observations
- The difficulty is NOT monotonically increasing. Levels 6, 10, and 14 have unusually long frightened times as "breather" levels.
- Pac-Man's dot-eating slowdown becomes a larger handicap as ghost speeds increase.
- The cornering mechanic becomes essential for survival at higher levels.
- Level 21 establishes the "forever" difficulty: ghosts are permanently faster than Pac-Man with no frightened mode. This setting persists identically from level 21 to level 255.

## 22. Data Contracts

### 22.1 Config Schema Example
```json
{
  "game": {
    "version": "1.0.0",
    "title": "PAC-MAN",
    "mode": "arcade_maze_chase"
  },
  "display": {
    "resolution_width": 224,
    "resolution_height": 288,
    "tile_size": 8,
    "grid_columns": 28,
    "grid_rows": 36,
    "frame_rate": 60.606060,
    "orientation": "portrait"
  },
  "gameplay": {
    "starting_lives": 3,
    "extra_life_score": 10000,
    "dots_per_level": 240,
    "power_pellets_per_level": 4,
    "base_speed_pixels_per_second": 75.7576,
    "dot_eat_pause_frames": 1,
    "pellet_eat_pause_frames": 3,
    "fruit_appear_dot_1": 70,
    "fruit_appear_dot_2": 170,
    "fruit_display_seconds": 9.5
  },
  "ghost_house": {
    "inactivity_timer_limit_levels_1_4": 4.0,
    "inactivity_timer_limit_levels_5_plus": 3.0
  }
}
```

### 22.2 Runtime Snapshot Schema Example
```json
{
  "time": {
    "frame": 0,
    "elapsed_seconds": 0.0
  },
  "level": {
    "number": 1,
    "dots_remaining": 240,
    "power_pellets_remaining": 4,
    "fruit_active": false,
    "fruit_timer": 0.0
  },
  "mode": {
    "global_mode": "scatter",
    "mode_phase": 0,
    "mode_timer": 7.0,
    "frightened_active": false,
    "frightened_timer": 0.0
  },
  "pac_man": {
    "tile_x": 14,
    "tile_y": 26,
    "pixel_x": 112,
    "pixel_y": 208,
    "direction": "left",
    "buffered_direction": "left",
    "speed_percent": 80,
    "alive": true
  },
  "ghosts": [
    {
      "name": "blinky",
      "state": "scatter",
      "tile_x": 14,
      "tile_y": 14,
      "direction": "left",
      "target_tile_x": 25,
      "target_tile_y": 0,
      "speed_percent": 75,
      "elroy_level": 0,
      "frightened": false
    }
  ],
  "score": {
    "player1": 0,
    "high_score": 0,
    "lives": 3,
    "ghost_eat_multiplier": 1
  }
}
```

## 23. Technical Requirements
- Simulation tick: fixed at ~60.61 Hz (NTSC VBLANK).
- Update order: `Input -> Pac-Man Movement -> Ghost AI -> Entity Movement -> Dot/Pellet Consumption -> Collision Detection -> Mode Timers -> Ghost Release Logic -> Level Completion Check -> Rendering/Audio`.
- All movement uses integer pixel positions with frame-skip patterns for sub-100% speeds.
- Ghost AI pathfinding is evaluated one tile ahead only; no long-range pathfinding.
- The maze structure and dot positions must be identical every level (no procedural generation).
- Frightened mode pseudo-random direction selection uses a PRNG seeded by the game's frame counter.
- Ghost reversal on mode switch must be instantaneous and unconditional.
- Score counter must not overflow (max displayable is 9,999,990 with 7 digits).

### 23.1 Determinism and Replay
- Given identical input frame sequences, the game must produce identical outcomes.
- Ghost AI decisions are deterministic given: current position, current direction, target tile, and available exits.
- The only source of non-determinism is frightened mode random turns, which must use a seeded PRNG.
- Attract mode demo is a pre-recorded input sequence played back deterministically.

### 23.2 Performance Requirements
- Zero frame drops on original Z80A @ 3.072 MHz hardware.
- All AI calculations, movement, collision, and rendering complete within one frame (~16.5 ms).
- Sprite flickering should not occur (max 6 sprites is within hardware limits).

## 24. QA Acceptance Matrix
1. Pac-Man cannot move through walls.
2. Pac-Man can traverse warp tunnels at full speed; ghosts traverse them at reduced speed.
3. Eating all 244 edibles (240 dots + 4 power pellets) completes the level.
4. Ghost AI correctly implements unique targeting for each ghost (Blinky: direct, Pinky: 4-ahead with overflow bug, Inky: double-vector with overflow bug, Clyde: distance-threshold switch).
5. Scatter/Chase mode cycling matches the timing table exactly, per level group.
6. Frightened mode duration matches the per-level table, including levels with 0-second fright.
7. Ghost score chain resets to 200 for each new power pellet.
8. Cruise Elroy triggers at correct dot thresholds and speeds per level.
9. Fruit appears at 70 and 170 dots consumed, disappears after ~9-10 seconds.
10. Extra life is awarded exactly once at 10,000 points.
11. Ghost house release follows personal dot counter > global dot counter > inactivity timer priority.
12. Ghosts reverse direction on every scatter/chase mode switch and on power pellet consumption.
13. No-upward-turn restriction zones are enforced during scatter/chase but not during frightened mode.
14. Death animation plays completely before life deduction or game over.
15. Intermissions play at the correct levels (after 2, 5, 9, 13, 17).
16. Level 256 produces the kill screen with corrupted right half.
17. Score display updates immediately on every scoring event.
18. The game handles the Pac-Man/ghost "pass-through" edge case in the warp tunnel.
19. Cornering allows Pac-Man to pre-turn before reaching tile center.
20. High score persists between games within a power cycle.

## 25. Engineering Milestones
- **Milestone 1**: Tile-based maze rendering, Pac-Man movement with input buffering and cornering, dot consumption and score display.
- **Milestone 2**: Ghost movement engine (tile-based pathfinding, no-reversal rule, tunnel slowdown), scatter mode with corner targeting.
- **Milestone 3**: Individual ghost chase AI (all four personalities), scatter/chase mode cycling with direction reversal.
- **Milestone 4**: Power pellets, frightened mode, ghost eating with score chain, eyes-return-to-house behavior.
- **Milestone 5**: Ghost house release system (personal counters, global counter, inactivity timer), Cruise Elroy.
- **Milestone 6**: Level progression (speed table, frightened time table, fruit table), complete difficulty scaling through level 21+.
- **Milestone 7**: Death sequence, extra lives, game over, attract mode, intermission cutscenes.
- **Milestone 8**: Audio system (siren, waka-waka, death, all sound effects), UI polish, level 256 kill screen.
