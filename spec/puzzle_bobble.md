# Puzzle Bobble / Bust-a-Move -- Complete Game Specification

> A comprehensive specification for faithfully recreating the original Puzzle Bobble (Taito, 1994 arcade version). Also known internationally as Bust-a-Move. This document covers every system, mechanic, entity, and interaction required for a full clone based on the Neo Geo MVS release.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics](#3-core-mechanics)
4. [Bubble Grid System](#4-bubble-grid-system)
5. [Aiming & Launching](#5-aiming--launching)
6. [Wall Bounce Physics](#6-wall-bounce-physics)
7. [Color Matching & Popping Rules](#7-color-matching--popping-rules)
8. [Orphaned Bubble Physics](#8-orphaned-bubble-physics)
9. [Ceiling Descent System](#9-ceiling-descent-system)
10. [All Bubble Types](#10-all-bubble-types)
11. [Scoring System](#11-scoring-system)
12. [Level Design -- All 30 Rounds](#12-level-design--all-30-rounds)
13. [Two-Player Competitive Mode](#13-two-player-competitive-mode)
14. [Danger Line & Game Over](#14-danger-line--game-over)
15. [Game States & Flow](#15-game-states--flow)
16. [UI Layout](#16-ui-layout)
17. [Audio Design](#17-audio-design)
18. [Animation System](#18-animation-system)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title (Japan) | Puzzle Bobble (paused as "Bubble Buster" during early development) |
| Title (International) | Bust-a-Move |
| Developer | Taito Corporation |
| Publisher | Taito (Japan); SNK (Neo Geo international) |
| Genre | Tile-matching / action puzzle |
| Players | 1--2 (competitive) |
| Platform (original) | Taito B System (Japan, June 1994) |
| Platform (international) | Neo Geo MVS (December 21, 1994) |
| Perspective | 2D, fixed-screen, bottom-up shooting |
| Input | 2-way joystick (left/right) + 1 fire button |
| Objective | Clear all bubbles from the playfield before they cross the danger line |
| Designers | Kazuhiro Kinoshita, Seiichi Nakakuki |
| Programmer | Yasuo Tsumori |
| Music | Kazuko Umino (tracks 1--2, 4--7), Yasuko Yamada (track 3) |
| Sound team | ZUNTATA (Taito in-house) |
| Rounds (1P) | 30 |
| Characters | Bub (green dinosaur, Player 1) and Bob (blue dinosaur, Player 2) |

### Connection to Bubble Bobble

Puzzle Bobble is a puzzle spin-off of the 1986 platformer Bubble Bobble. Bub and Bob, the twin bubble dragons, appear as the operators of the bubble launcher. Each colored bubble visually contains a trapped enemy from the original Bubble Bobble game (see Section 10).

---

## 2. Technical Foundation

### Hardware -- Taito B System (Original Japan Release)

| Property | Value |
|----------|-------|
| Main CPU | Motorola MC68000 @ 12 MHz |
| Sound CPU | Zilog Z80 @ 4 MHz |
| Sound chip | Yamaha YM2610 |
| Custom chips | TC0220IOC, TC0260DAR, TC0180VCU, TC0140SYT |
| Video resolution | 320 x 224 pixels |
| Color palette | 4096 colors |
| Sprite layers | 4 separate planned layers with sprites |
| Audio output | Mono |
| Refresh rate | ~60 Hz (59.185606 Hz) |

### Hardware -- Neo Geo MVS (International Release)

| Property | Value |
|----------|-------|
| Main CPU | Motorola 68000 @ 12 MHz |
| Sound CPU | Zilog Z80 @ 4 MHz |
| Sound chip | Yamaha YM2610 |
| Video resolution | 320 x 224 pixels (active area 304 x 224 in-game) |
| ROM size | 32 Mbit |
| Audio output | Stereo (upgraded from B System mono) |
| PROG board | PROGBK1 |
| CHA board | CHA256 |
| MAME romset | pbobblen |

### Coordinate System

- Origin (0, 0) at top-left of screen.
- Active playfield is horizontally centered within the 320-pixel width.
- Playfield interior width accommodates 8 bubble columns.
- Each bubble occupies approximately 16 pixels in diameter (radius = 8 pixels) at the native grid scale.

### Timing

| Property | Value |
|----------|-------|
| Frame rate | ~60 FPS (tied to hardware refresh) |
| Game tick | 1 tick per frame (~16.67 ms) |
| Bubble travel speed | ~8 pixels per frame |
| Shot timer | ~10 seconds before auto-fire |
| Hurry-up warning | Appears at ~5 seconds remaining |

### Game Loop

```
1. Process input (joystick left/right, fire button)
2. Update aim angle of launcher
3. If bubble in flight: update bubble position, check wall collisions, check grid collisions
4. If bubble snapped to grid: check color matches (3+ connected), pop matching bubbles
5. Check for orphaned bubbles (disconnected from ceiling), drop them
6. Update shot counter; check ceiling descent trigger
7. Check danger line (game over condition)
8. Check win condition (all bubbles cleared)
9. If round cleared: calculate time bonus, advance to next round
10. Render (background -> grid bubbles -> flying bubble -> launcher -> UI -> particles)
```

---

## 3. Core Mechanics

### Launcher (Catapult / Pointer)

The launcher sits at the bottom center of the playfield. It is operated by Bub (Player 1) or Bob (Player 2). The launcher consists of:

1. **Arrow indicator**: A visible arrow/pointer extending from the launcher pivot that shows the current aim direction. The arrow has a fixed length and rotates smoothly.
2. **Current bubble**: The bubble loaded in the launcher, displayed at the pivot point. Its color is visible to the player.
3. **Next bubble**: A smaller preview bubble shown beside the launcher indicating the next color that will be loaded after firing. This allows one-step-ahead planning.
4. **Pivot point**: Located at the horizontal center of the playfield, near the bottom edge, just above the danger line area.

### Bubble Selection

- The color of each bubble provided to the player is **randomly selected** from the set of colors currently present on the playfield.
- As colors are eliminated from the field, they are also removed from the random pool.
- This ensures the player always receives usable colors.

### Auto-Fire

- If the player does not fire within approximately **10 seconds**, the game displays a "HURRY UP!" warning.
- The warning appears at the **5-second mark** (5 seconds remaining).
- If the timer expires, the bubble is launched automatically in the current aim direction.
- The auto-fired bubble follows normal physics (bouncing, snapping, matching).

### Continuation

- Upon game over, the player may insert a credit to continue.
- Continuing **resets the score to zero** but resumes at the current round.

---

## 4. Bubble Grid System

### Hexagonal Staggered Grid

The playfield uses a **hexagonal close-packed (honeycomb) grid** where every other row is offset by half a bubble width. This creates a staggered arrangement where each bubble can be adjacent to up to 6 neighbors.

#### Grid Dimensions

| Property | Value |
|----------|-------|
| Columns (even rows, 0-indexed) | 8 |
| Columns (odd rows, 0-indexed) | 7 |
| Maximum visible rows | ~13 (varies with ceiling descent) |
| Bubble diameter | ~16 pixels (at native 320x224 resolution) |
| Bubble radius | ~8 pixels |
| Horizontal spacing | Equal to bubble diameter (16 px) |
| Vertical spacing | Bubble diameter x cos(30 deg) = ~13.86 px (approximately 14 px) |
| Row offset (odd rows) | Half bubble diameter = 8 px to the right |

#### Neighbor Relationships

Each bubble in the grid has up to 6 neighbors depending on whether it is in an even or odd row:

**Even row (8 bubbles) -- bubble at column c:**
| Neighbor | Row delta | Column delta |
|----------|-----------|--------------|
| Upper-left | -1 | -1 |
| Upper-right | -1 | 0 |
| Left | 0 | -1 |
| Right | 0 | +1 |
| Lower-left | +1 | -1 |
| Lower-right | +1 | 0 |

**Odd row (7 bubbles) -- bubble at column c:**
| Neighbor | Row delta | Column delta |
|----------|-----------|--------------|
| Upper-left | -1 | 0 |
| Upper-right | -1 | +1 |
| Left | 0 | -1 |
| Right | 0 | +1 |
| Lower-left | +1 | 0 |
| Lower-right | +1 | +1 |

Bubbles at the edges of the playfield have fewer than 6 neighbors.

### Snapping to Grid

When a fired bubble comes to rest (by contacting another bubble or the ceiling), it **snaps** to the nearest valid empty grid cell. The snapping algorithm:

1. Determine the center position of the bubble at the moment of collision.
2. Calculate the nearest grid cell center to that position.
3. Place the bubble in that cell.
4. The bubble visually teleports to the exact grid-aligned position (no smooth interpolation).

### Ceiling Attachment

- The top row of the grid (row 0) is implicitly attached to the ceiling.
- All bubbles must maintain a connected path to at least one bubble in row 0 (or to the ceiling itself) to remain on the field.
- Any bubble not connected to the ceiling (directly or through a chain of adjacent bubbles) is considered **orphaned** and will fall (see Section 8).

---

## 5. Aiming & Launching

### Aim Mechanics

| Property | Value |
|----------|-------|
| Aim control | Joystick left/right rotates the launcher arrow |
| Rotation speed | ~2 degrees per frame (~120 degrees/second) |
| Minimum angle | ~20 degrees from horizontal-left (~160 deg from right) |
| Maximum angle | ~20 degrees from horizontal-right (~20 deg from right) |
| Effective range | Approximately 140-degree arc centered on vertical |
| Dead zone | Cannot fire horizontally or below horizontal |
| Center reset | Pressing Up on joystick centers the launcher to vertical (90 degrees) |

The arrow indicator is drawn as a line or elongated triangle extending from the launcher pivot in the direction of aim. It shows the initial trajectory but does **not** extend to show wall bounces (unlike some later versions). Players must mentally calculate bank shots.

### Launch Mechanics

| Property | Value |
|----------|-------|
| Trigger | Fire button (A button on Neo Geo) |
| Bubble speed | ~8 pixels per frame (constant velocity) |
| Trajectory | Straight line in the aimed direction |
| Gravity | None (bubbles travel in straight lines) |
| Acceleration | None (constant speed from launch to rest) |
| Multiple bounces | Unlimited wall bounces until the bubble contacts another bubble or the ceiling |

### Launch Sequence

1. Player presses fire button.
2. Current bubble launches from the pivot point at the aimed angle.
3. The "next bubble" moves into the current position.
4. A new random "next bubble" is generated (color from remaining field colors).
5. The shot counter increments by 1 (used for ceiling descent calculation).
6. The shot timer resets to ~10 seconds.

---

## 6. Wall Bounce Physics

### Reflection Rules

Bubbles bounce off the left and right walls of the playfield using **perfect reflection** (angle of incidence equals angle of reflection):

- If a bubble traveling at angle theta hits the left or right wall, its horizontal velocity component (dx) is negated: `dx = -dx`.
- The vertical velocity component (dy) is unchanged.
- This produces a mirror-image trajectory.
- There is no energy loss -- the bubble speed remains constant after bouncing.

### Wall Boundaries

| Property | Value |
|----------|-------|
| Left wall | Left edge of the playfield interior |
| Right wall | Right edge of the playfield interior |
| Collision point | When bubble center reaches within one radius of the wall |
| Bounce count limit | No limit; bubbles can bounce multiple times |

### Ceiling Collision

- If a bubble reaches the ceiling (top of the playfield) without contacting another bubble, it snaps to the nearest available cell in the top row.
- The ceiling acts as a solid boundary, not a reflective one.

### No Floor Collision

- Bubbles only travel upward (the launch angle is always above horizontal).
- There is no floor bounce mechanic.

### Bank Shot Strategy

Bank shots (bouncing off walls) are a core skill in Puzzle Bobble. They allow players to:

- Reach bubble clusters hidden behind other bubbles.
- Thread shots through narrow gaps between bubbles.
- Access the far side of asymmetric formations.
- Achieve precise placements at shallow angles.

---

## 7. Color Matching & Popping Rules

### Match Detection

After a bubble snaps to a grid cell, the game checks for color matches:

1. Starting from the newly placed bubble, perform a **flood fill** (breadth-first or depth-first search) to find all connected bubbles of the **same color**.
2. "Connected" means adjacent in the hexagonal grid (sharing one of the 6 neighbor positions).
3. If the connected group contains **3 or more bubbles** (including the newly placed one), all bubbles in the group **pop**.

### Popping Behavior

| Property | Value |
|----------|-------|
| Minimum match size | 3 bubbles of the same color |
| Maximum match size | No upper limit |
| Pop animation | Bubbles burst simultaneously with a brief particle/flash effect |
| Pop timing | Instantaneous from game logic perspective |
| Chain reactions | Not present in standard rules -- only one match check per shot |

### What Does NOT Count

- Two bubbles of the same color touching each other do **not** pop (minimum is 3).
- Diagonal adjacency beyond the hexagonal neighbor set does not count.
- Bubbles in flight do not participate in match checks.

### Color Elimination

- When all bubbles of a particular color are removed from the field (through popping or dropping), that color is removed from the random selection pool.
- The "current" and "next" bubbles in the launcher are also re-evaluated -- if their color no longer exists on the field, they may be rerolled (implementation varies; typically the color is locked once assigned).

---

## 8. Orphaned Bubble Physics

### Disconnection Check

After popping occurs, the game checks which remaining bubbles are still connected to the ceiling:

1. Start from every bubble in the **top row** (row 0, attached to ceiling).
2. Perform a flood fill to mark all bubbles reachable from the top row through any color adjacency.
3. Any bubble **not** marked is considered **orphaned** (disconnected from the ceiling).

### Falling Behavior

| Property | Value |
|----------|-------|
| Trigger | Immediately after pop animation completes |
| Fall direction | Straight down with gravity acceleration |
| Gravity | Applied per frame; bubbles accelerate downward |
| Horizontal motion | None (fall straight down from their grid position) |
| Fall animation | Bubbles tumble/fall off-screen below the playfield |
| Removal | Bubbles are removed from game state when they exit the screen |

### Strategic Importance

Orphaned bubbles are the primary source of high scores. The exponential scoring system for dropped bubbles (see Section 11) means that creating a single connection point ("stem" or "bridge") and then popping it causes many bubbles to fall simultaneously, yielding massive point multipliers.

Key strategies:

- **Stem building**: Create a narrow connection (1--2 bubbles wide) supporting a large mass of bubbles.
- **Bridge cutting**: Identify and target the critical bubbles connecting a large group to the ceiling.
- **Color pairing**: Place bubbles strategically so that popping a small match severs a large group.

---

## 9. Ceiling Descent System

### Descent Trigger

The ceiling (and all attached bubbles) periodically descends by one row, compressing the playfield and pushing bubbles closer to the danger line. The descent rate is determined by the **number of distinct colors remaining** on the field.

#### Descent Interval Table

| Colors Remaining | Shots Before Descent |
|------------------|---------------------|
| 8 (all colors) | ~12 shots |
| 7 | ~11 shots |
| 6 | ~10 shots |
| 5 | ~9 shots |
| 4 | ~8 shots |
| 3 | ~7 shots |
| 2 | ~6 shots |
| 1 | ~5 shots |

The general formula: with B as the base interval (approximately 12 for 8 colors), the ceiling drops every `B - (8 - colors_remaining)` shots. As the player eliminates colors, the ceiling descends more frequently, creating urgency even when the field is nearly clear.

### Descent Behavior

| Property | Value |
|----------|-------|
| Descent amount | 1 bubble row height (~14 pixels) |
| Animation | Smooth downward slide over several frames |
| Effect on grid | All bubble row indices effectively shift down by 1 |
| New top row | Filled with the ceiling border (no new bubbles added) |
| Music change | Tempo increases as bubbles approach the danger line |

### Visual Indicator

- The ceiling border is drawn as a solid bar or mechanical compressor at the top of the playfield.
- When the ceiling descends, the bar visibly moves downward, pushing all bubbles with it.
- A metal/mechanical pressing animation accompanies the descent.

---

## 10. All Bubble Types

### Standard Colored Bubbles

The original 1994 Puzzle Bobble features **8 standard bubble colors**, each visually containing a trapped enemy from Bubble Bobble:

| Color | Trapped Enemy | Enemy Description |
|-------|--------------|-------------------|
| Red | Invader | Space Invader-like alien |
| Blue | Zen-Chan | Round bubble enemy |
| Green | Drunk | Bottle-carrying monster |
| Yellow | Pulpul | Wind-up robot toy |
| Orange | Banebou | Spring-coiled creature |
| Purple | Monsta | Ghost-like monster |
| Black | Hidegons | Dragon-like fire breather |
| White | Mighta | Boulder creature |

### Bubble Properties

| Property | Value |
|----------|-------|
| Diameter | ~16 pixels |
| Shape | Circular / spherical |
| Visual | Semi-transparent with enemy character visible inside |
| Behavior | Standard -- participates in color matching |
| All 8 colors present | Levels 1--8 (approx); later levels use fewer |

### Color Distribution Across Rounds

Not all 30 rounds use all 8 colors. Later rounds may use as few as 3--4 colors. Fewer colors means:
- Easier to create matches (fewer distinct types).
- Faster ceiling descent (see Section 9).
- The random bubble generator only provides colors present on the field.

### Special Note: No Special Bubble Types in Original

The original 1994 arcade Puzzle Bobble does **not** include special/power-up bubbles. Features such as star bubbles, metal bubbles, rainbow bubbles, and bomb bubbles were introduced in later sequels (Puzzle Bobble 2, 3, and beyond). The original game uses only the 8 standard colored bubbles.

---

## 11. Scoring System

Puzzle Bobble features an **exponential scoring system** that enables extremely high scores through strategic play. Scoring is divided into three categories.

### Popped Bubbles (Direct Matches)

Each bubble removed through color matching (3+ connected same-color bubbles) awards a flat 10 points:

| Bubbles Popped | Points |
|----------------|--------|
| 3 (minimum match) | 30 |
| 4 | 40 |
| 5 | 50 |
| 6 | 60 |
| 7 | 70 |
| N | N x 10 |

### Dropped Bubbles (Orphaned/Fallen)

Dropped bubbles use an **exponential doubling** system. The first dropped bubble scores 20 points, and each subsequent bubble doubles the previous value:

| Bubbles Dropped | Points per Drop | Cumulative Total |
|-----------------|----------------|------------------|
| 1 | 20 | 20 |
| 2 | 40 | 60 |
| 3 | 80 | 140 |
| 4 | 160 | 300 |
| 5 | 320 | 620 |
| 6 | 640 | 1,260 |
| 7 | 1,280 | 2,540 |
| 8 | 2,560 | 5,100 |
| 9 | 5,120 | 10,220 |
| 10 | 10,240 | 20,460 |
| 11 | 20,480 | 40,940 |
| 12 | 40,960 | 81,900 |
| 13 | 81,920 | 163,820 |
| 14 | 163,840 | 327,660 |
| 15 | 327,680 | 655,340 |
| 16 | 655,360 | 1,310,700 |
| 17+ | 1,310,720 | 2,621,420+ |

The maximum value per bubble is capped at **1,310,720 points** (reached at 17 dropped bubbles). Dropping all 17 bubbles in a single cascade yields over **2.6 million cumulative points**.

### Time Bonus (Round Completion)

Upon clearing all bubbles from a round, a time bonus is awarded based on completion speed:

| Completion Time | Bonus Points |
|-----------------|-------------|
| 0--5 seconds | 50,000 |
| 6 seconds | 49,160 |
| 7 seconds | 48,320 |
| 8 seconds | 47,480 |
| 9 seconds | 46,640 |
| 10 seconds | 45,800 |
| 15 seconds | 41,600 |
| 20 seconds | 37,400 |
| 25 seconds | 33,200 |
| 30 seconds | 29,000 |
| 35 seconds | 24,800 |
| 40 seconds | 20,600 |
| 45 seconds | 16,400 |
| 50 seconds | 12,200 |
| 55 seconds | 8,000 |
| 60 seconds | 3,800 |
| 64 seconds | 440 |
| 65+ seconds | 0 (no bonus) |

The bonus decreases approximately **840 points per second** from the 50,000-point maximum. The timer starts when the round begins (first bubble becomes available) and stops when the last bubble is cleared.

### Score Display

- Score is displayed as a running total at the top of the screen.
- High score table is maintained across sessions (battery-backed SRAM on arcade hardware).
- Continuing after game over **resets the score to zero**.

### Million-Point Opportunities

Certain rounds are specifically designed to allow million-point scoring through large cascade drops. Notable rounds include:

| Round | Potential | Difficulty |
|-------|-----------|-----------|
| Round 9 | 1x million | Moderate |
| Round 10 | 3x million | Moderate |
| Round 13 | 2x million | Hard |
| Round 22 | 3x million | Moderate |
| Round 27 | 1x million | Risky |
| Round 29 | 1x million | Risky |

---

## 12. Level Design -- All 30 Rounds

The single-player game consists of 30 rounds with increasing complexity. Each round starts with a pre-arranged pattern of colored bubbles. Rounds are designed to test different skills: some reward precision, some reward strategic stem-building, and some are pure survival challenges.

### Round Summary Table

| Round | Colors Used | Approx. Bubble Count | Shape/Pattern Description | Strategy Type | Score Potential |
|-------|------------|---------------------|---------------------------|---------------|----------------|
| 1 | 4 | ~16 | Simple scattered rows | Tutorial / Easy clear | Low |
| 2 | 4 | ~20 | Two-row spread | Basic matching | Low |
| 3 | 5 | ~24 | Three rows, mild stagger | Introduction to bank shots | Low |
| 4 | 5 | ~28 | Diamond/rhombus pattern | Color grouping practice | Low |
| 5 | 6 | ~30 | Inverted triangle | Cascade introduction | Medium |
| 6 | 6 | ~32 | Dual columns | Side-access bank shots | Medium |
| 7 | 6 | ~34 | Zigzag rows | Precision aiming | Medium |
| 8 | 7 | ~36 | Wide spread, mixed | Survival focus | Medium |
| 9 | 5 | ~38 | "Orange Road" -- long color stems | 1x Million opportunity | High |
| 10 | 6 | ~40 | Multi-stem cluster | 3x Million opportunity | Very High |
| 11 | 6 | ~36 | Hourglass / narrow center | Guide shots required | Medium |
| 12 | 5 | ~42 | "Christmas Tree" shape | Center-line attack | Medium |
| 13 | 3 | ~30 | V-shape cluster (blue) | 2x Million (fast ceiling!) | Very High |
| 14 | 6 | ~38 | Arrow pointing down | Side erosion | Medium |
| 15 | 5 | ~40 | Stalks / columns with caps | Deflection shots | Medium |
| 16 | 7 | ~44 | Dense rectangular block | Systematic clearing | Medium |
| 17 | 4 | ~36 | Solid mass, 4 colors | Hollow-out sides, mass drop | High |
| 18 | 6 | ~42 | Cross / plus shape | Center targeting | Medium |
| 19 | 7 | ~46 | Scattered clusters | Multi-front clearing | Medium |
| 20 | 6 | ~40 | Checkerboard pattern | Precision placement | Medium |
| 21 | 5 | ~38 | Pyramid | Base-first approach | Medium |
| 22 | 6 | ~44 | Multi-mass hanging | 3x Million opportunity | Very High |
| 23 | 7 | ~48 | Dense fill, many colors | Survival under pressure | Medium |
| 24 | 5 | ~40 | Single mass | Erode bottom, deflection | High |
| 25 | 6 | ~42 | Symmetric wings | Simultaneous side clears | Medium |
| 26 | 4 | ~36 | Compact 4-color block | Strategic pairing | High |
| 27 | 6 | ~44 | Complex multi-stem | 1x Million (risky) | High |
| 28 | 7 | ~48 | Near-full field | Survival, fast clearing | Medium |
| 29 | 5 | ~42 | Intricate pattern | 1x Million (risky) | High |
| 30 | 8 | ~50 | Final challenge, all colors | Boss-level difficulty | Variable |

### Level Design Principles

1. **Early rounds (1--5)**: Introduce core mechanics; few colors; simple patterns; gentle ceiling timer.
2. **Mid rounds (6--15)**: Introduce bank shots, stem strategies, and the first million-point opportunities. Round 13 is notable for using only 3 colors (very fast ceiling descent).
3. **Late rounds (16--25)**: Dense patterns, many colors, require advanced techniques.
4. **Final rounds (26--30)**: Maximum difficulty; the final round uses all 8 colors and a near-full playfield.

### Round Transition

- After clearing all bubbles, a brief "ROUND CLEAR" animation plays.
- Time bonus is calculated and added to the score.
- The next round loads with its pre-arranged bubble pattern.
- A "ROUND X" splash screen displays briefly before play begins.

---

## 13. Two-Player Competitive Mode

### Overview

Two players compete simultaneously on a **split screen**, each with their own playfield. The objective is to force the opponent's bubbles past their danger line.

### Screen Layout

| Property | Value |
|----------|-------|
| Screen division | Vertical split -- left half (Player 1) and right half (Player 2) |
| Playfield size | Each player has a narrower playfield (half-width screen) |
| Bubble stack indicator | Center of screen between the two playfields |
| Player 1 character | Bub (green dinosaur) |
| Player 2 character | Bob (blue dinosaur) |

### Competitive Mechanics

#### Bubble Transfer System

When a player pops 4 or more bubbles (not counting dropped bubbles), the excess is transferred to the opponent:

1. Pop 3 bubbles: **No transfer** (minimum match, no penalty to opponent).
2. Pop 4 bubbles: **1 bubble** added to the transfer stack.
3. Pop 5 bubbles: **2 bubbles** added to the transfer stack.
4. Pop N bubbles (N >= 4): **(N - 3) bubbles** added to the transfer stack.

#### Drop Transfer

When bubbles are **dropped** (orphaned and fallen), ALL dropped bubbles plus any existing stacked bubbles are transferred to the opponent's field:

- Dropped bubbles + stacked bubbles = total added to opponent's playfield.
- Transferred bubbles appear at the **top** of the opponent's field in the next available rows.
- The colors of transferred bubbles are chosen to **not match** the colors currently on the opponent's field, maximizing disruption.

#### Stack Indicator

The transfer stack between the playfields uses color-coded bubble icons:

| Icon Color | Value |
|------------|-------|
| Yellow bubble | 1 pending bubble |
| Red bubble | 5 pending bubbles |

The stack accumulates until a drop triggers the transfer, at which point all pending bubbles are sent to the opponent.

### Victory Conditions

| Condition | Result |
|-----------|--------|
| Opponent's bubbles cross danger line | Current player wins the round |
| Player clears all bubbles first | Current player wins the round (opponent continues until loss or clear) |
| Winner display | Blue "WON" text flashes on winner's side |
| Loser display | Red "LOST" text; all remaining bubbles turn black |

### Match Format

| Setting | Options |
|---------|---------|
| Match type | Best-of-3 or Best-of-5 (DIP switch configurable) |
| Round indicator | Diamond symbols show wins per player |
| After match | Game returns to versus select or title screen |
| Score reset | Loser's score resets to zero on loss |

### Two-Player Level Selection

In versus mode, both players receive **identical** starting patterns and bubble sequences, ensuring a fair contest of skill rather than luck.

---

## 14. Danger Line & Game Over

### Danger Line

| Property | Value |
|----------|-------|
| Position | A horizontal line near the bottom of the playfield, above the launcher |
| Visual | A dashed or solid line across the playfield width |
| Visibility | Always visible as a warning boundary |
| Trigger zone | When any bubble in the grid extends below this line |

### Approaching Danger

As bubbles approach the danger line, several warnings escalate:

| Warning Level | Condition | Effect |
|---------------|-----------|--------|
| Safe | Bubbles well above line | Normal music tempo |
| Caution | Bubbles within ~4 rows of line | Music tempo increases slightly |
| Warning | Bubbles within ~2 rows of line | Music tempo increases significantly |
| Critical | Bubbles at or touching line | Maximum music tempo; imminent game over |

### Game Over Trigger

- Game over occurs when any bubble in the grid is positioned at or below the danger line after a ceiling descent or after a new bubble snaps to a position below the line.
- The game does **not** end during a bubble's flight -- only after it comes to rest.
- Upon game over, the playfield freezes and all bubbles drop/dissolve in a cascade animation.

### Continue System

| Property | Value |
|----------|-------|
| Continue prompt | "CONTINUE?" with countdown timer |
| Continue timer | ~10 seconds |
| Cost | 1 credit |
| Effect | Resume at current round with same bubble layout |
| Score penalty | Score resets to 0 |
| Round progress | Maintained (do not restart from round 1) |

---

## 15. Game States & Flow

### State Machine

```
[ATTRACT MODE] -> [TITLE SCREEN] -> [MODE SELECT] -> [GAMEPLAY]
                                          |                |
                                     [1P / 2P VS]    [ROUND START]
                                                          |
                                                     [ACTIVE PLAY]
                                                      /        \
                                               [ROUND CLEAR]  [GAME OVER]
                                                    |              |
                                              [NEXT ROUND]   [CONTINUE?]
                                                    |           /     \
                                              [ROUND 30]   [YES]    [NO]
                                                    |         |        |
                                               [ENDING]  [RESUME]  [HIGH SCORE ENTRY]
                                                    |                      |
                                             [CREDITS]             [ATTRACT MODE]
```

### Attract Mode

- Plays automatically when no credits are inserted and the machine is idle.
- Shows: title logo, brief gameplay demo, high score table, credit/copyright text.
- Loops continuously until a credit is inserted.

### Title Screen

- Displays the Puzzle Bobble / Bust-a-Move logo.
- "INSERT COIN" flashes at the bottom.
- After credit insertion: "PUSH START BUTTON" appears.
- Pressing Start advances to Mode Select.

### Mode Select

- **1 PLAYER**: Single-player 30-round campaign.
- **VS 2 PLAYER**: Competitive two-player mode (requires 2 credits).
- Selection made with joystick up/down and confirmed with Start or Fire.

### Round Start

- Brief splash: "ROUND X" (where X is the round number, 1--30).
- The pre-arranged bubble pattern loads into the grid.
- Bub/Bob appear at the launcher.
- The first bubble is loaded; play begins.

### Ending (After Round 30)

- Upon clearing Round 30, a victory sequence plays.
- Bub and Bob depart with the catapult, leaving behind the defeated enemies.
- Credits roll showing the development team.
- The player's final score is eligible for the high score table.

---

## 16. UI Layout

### Single-Player Screen Layout

```
+------------------------------------------+
|  SCORE: 0000000    HI-SCORE: 0000000     |
|  ROUND: XX                                |
+------------------------------------------+
|          [Ceiling / Top Border]           |
|  |  O O O O O O O O  |                   |
|  |   O O O O O O O   |   <- Staggered    |
|  |  O O O O O O O O  |      rows         |
|  |   O O O O O O O   |                   |
|  |  O O O O O O O O  |                   |
|  |                    |                   |
|  |                    |   <- Open play    |
|  |                    |      area         |
|  |                    |                   |
|  |- - - - - - - - - -|   <- Danger line  |
|  |        /|\         |                   |
|  |       / | \        |   <- Aim arrow    |
|  |      [BUBBLE]      |   <- Current      |
|  |     [next]         |   <- Next preview |
|  |      [BUB]         |   <- Character    |
+------------------------------------------+
```

### UI Elements

| Element | Position | Description |
|---------|----------|-------------|
| Score | Top-left | Current player score, 7 digits |
| High Score | Top-right | Session high score, 7 digits |
| Round number | Top area | "ROUND XX" display |
| Playfield walls | Left and right borders | Solid walls for bubble bouncing |
| Ceiling bar | Top of playfield | Mechanical press indicator |
| Bubble grid | Upper playfield | Pre-arranged and player-placed bubbles |
| Danger line | Lower playfield | Horizontal warning boundary |
| Launcher arrow | Bottom-center | Rotating aim indicator |
| Current bubble | Launcher pivot | The bubble about to be fired |
| Next bubble | Beside launcher | Preview of upcoming bubble color |
| Character sprite | Below launcher | Bub (1P) or Bob (2P) operating the launcher |
| Shot timer warning | Center screen | "HURRY UP!" text when time is running out |

### Two-Player Screen Layout

```
+------------------------------------------+
| P1 SCORE    [STACK]     P2 SCORE         |
+------------------------------------------+
| [Ceiling]   |Y|R|Y|   [Ceiling]          |
| |O O O O |  | | | |   |O O O O |        |
| | O O O  |  | | | |   | O O O  |        |
| |O O O O |  |stack|   |O O O O |        |
| |        |  |     |   |        |         |
| |--------|  |     |   |--------|         |
| |  /|\   |  |     |   |  /|\   |        |
| | [BUB]  |  |     |   | [BOB]  |        |
+------------------------------------------+
```

---

## 17. Audio Design

### Music Tracks

The soundtrack was composed by Kazuko Umino and Yasuko Yamada of ZUNTATA (Taito's in-house sound team).

| Track | Name | Duration | Usage | Composer |
|-------|------|----------|-------|----------|
| 1 | Title Demo | 0:07 | Attract mode / title screen intro | Kazuko Umino |
| 2 | "Let's Go to Pao Pao Island!" (BGM1) | 1:49 | Main gameplay theme -- plays during most rounds | Kazuko Umino |
| 3 | "April Forest" (BGM2) | 1:13 | Alternate gameplay theme -- later rounds | Yasuko Yamada |
| 4 | Clear | 0:03 | Round completion jingle | Kazuko Umino |
| 5 | Continue | 0:47 | Continue screen music | Kazuko Umino |
| 6 | Game Over | 0:05 | Game over jingle | Kazuko Umino |
| 7 | Ending | 0:52 | End credits music after clearing Round 30 | Kazuko Umino |
| 8 | Title (Bust-a-Move) | 0:04 | International title screen variant | Kazuko Umino |

### Music Behavior

| Condition | Effect |
|-----------|--------|
| Normal play | BGM1 or BGM2 plays at standard tempo |
| Bubbles approaching danger line | Music tempo gradually increases |
| Very close to danger line | Music plays at maximum speed (frantic feel) |
| Round cleared | Music stops; Clear jingle plays |
| Game over | Music stops; Game Over jingle plays |
| Continue screen | Continue music plays during countdown |

### Sound Effects

| Sound Event | Description |
|-------------|-------------|
| Bubble launch | Short "pop" / "whoosh" sound when bubble fires from launcher |
| Wall bounce | Brief "tick" or "click" on each wall reflection |
| Bubble snap | Soft "thud" when bubble attaches to grid |
| Match pop (3+) | Bubbly "pop-pop-pop" cascade sound |
| Bubble drop (orphaned) | Descending "whoooosh" as bubbles fall |
| Large cascade | Extended falling sound with increasing urgency |
| Ceiling descent | Mechanical grinding/pressing sound |
| Hurry Up | Warning chime / alarm; "HURRY UP!" voice or sound cue |
| Auto-fire | Same as bubble launch (no distinct sound) |
| Round start | Brief fanfare or chime |
| Danger zone entry | Tension sting / warning tone |
| 2P -- bubble transfer | Distinctive "delivery" sound when stack transfers |
| Victory (2P) | Celebratory jingle |
| Defeat (2P) | Deflating / sad jingle |
| Score tally | Rapid counting sound during time bonus calculation |
| Coin insert | Standard arcade credit sound |

### Audio Hardware Differences

| Version | Audio Chip | Output |
|---------|-----------|--------|
| Taito B System (Japan) | YM2610 | Mono |
| Neo Geo MVS (International) | YM2610 | Stereo |

The Neo Geo version features slightly different sound effects from the B System original due to the different sound driver, but the music compositions are the same.

---

## 18. Animation System

### Bubble Animations

| Animation | Frames | Duration | Trigger |
|-----------|--------|----------|---------|
| Idle bubble in grid | 1 (static) | N/A | Always (bubbles do not animate while stationary) |
| Bubble in flight | 1 (static, moving) | Until rest | Launch |
| Bubble pop | 3--4 | ~200 ms | Match of 3+ |
| Bubble fall (orphaned) | Continuous | Until off-screen | Disconnection from ceiling |
| Bubble snap to grid | 1 (instant) | 1 frame | Collision with grid |

### Character Animations

| Animation | Character | Trigger |
|-----------|-----------|---------|
| Idle | Bub/Bob | Default state, waiting for input |
| Aiming | Bub/Bob | Joystick held left or right |
| Fire | Bub/Bob | Fire button pressed -- brief launch animation |
| Celebration | Bub/Bob | Round cleared |
| Panic | Bub/Bob | Bubbles near danger line |
| Victory pose | Bub/Bob | Win in 2P mode |
| Defeat | Bub/Bob | Lose in 2P mode or game over |

### Launcher Animations

| Animation | Description |
|-----------|-------------|
| Arrow rotation | Smooth rotation following joystick input |
| Bubble loading | Next bubble slides into current position after fire |
| Recoil | Brief kickback animation on the launcher when firing |

### Screen Transition Animations

| Transition | Animation |
|------------|-----------|
| Round start | "ROUND X" text slides or fades in, brief hold, fades out |
| Round clear | All remaining grid positions flash; "ROUND CLEAR" text |
| Game over | Bubbles darken and drop one by one from top |
| Continue countdown | Numbers count down from 10 with pulsing animation |
| Ending sequence | Bub and Bob ride away on the catapult; enemies float free; credits scroll |

### Particle Effects

| Effect | Trigger | Description |
|--------|---------|-------------|
| Pop sparkles | Bubble match pop | Small star/sparkle particles emanate from popped positions |
| Drop trail | Orphaned bubbles falling | Brief trailing particle behind falling bubbles |
| Score popup | Points awarded | Numeric score value briefly floats up from the action point |
| Ceiling dust | Ceiling descent | Small dust/debris particles from the pressing ceiling bar |

---

## Appendix A: Key Formulas

### Bubble Grid Position to Screen Position

```
screen_x = playfield_left + (col * bubble_diameter) + (row % 2 == 1 ? bubble_radius : 0)
screen_y = playfield_top + (row * vertical_spacing)

where:
  bubble_diameter = 16 pixels
  bubble_radius = 8 pixels
  vertical_spacing = bubble_diameter * cos(30 degrees) = approximately 14 pixels
```

### Aim Direction to Velocity

```
dx = bubble_speed * cos(angle)
dy = -bubble_speed * sin(angle)    // negative because y-axis points down

where:
  bubble_speed = 8 pixels/frame
  angle = launcher angle in radians (0 = right, PI/2 = straight up, PI = left)
  valid range: approximately 20 degrees to 160 degrees
```

### Wall Bounce

```
if (bubble_center_x - bubble_radius <= left_wall) or
   (bubble_center_x + bubble_radius >= right_wall):
    dx = -dx   // reverse horizontal component
    // dy unchanged
```

### Grid Snap (Nearest Cell)

```
// Approximate row from y position
row = round((bubble_y - playfield_top) / vertical_spacing)

// Approximate column from x position (accounting for odd-row offset)
if row % 2 == 1:
    col = round((bubble_x - playfield_left - bubble_radius) / bubble_diameter)
else:
    col = round((bubble_x - playfield_left) / bubble_diameter)

// Clamp to valid range
col = clamp(col, 0, max_col_for_row)
```

### Dropped Bubble Score

```
points_for_nth_drop = 20 * (2 ^ (min(n, 17) - 1))

// or equivalently:
// drop 1 = 20, drop 2 = 40, drop 3 = 80, ..., drop 17+ = 1,310,720

total_drop_score = sum of points_for_nth_drop for n = 1 to num_drops
```

### Time Bonus

```
if completion_seconds <= 5:
    bonus = 50000
elif completion_seconds <= 64:
    bonus = 50000 - ((completion_seconds - 5) * 840)
    bonus = max(bonus, 440)
else:
    bonus = 0
```

### Ceiling Descent Interval

```
base_interval = 12   // shots when all 8 colors present
colors_missing = 8 - colors_remaining
descent_every_n_shots = base_interval - colors_missing

// minimum is approximately 5 shots (when only 1 color remains)
```

---

## Appendix B: DIP Switch / Operator Settings

The arcade hardware supports operator-configurable settings via DIP switches or the test menu:

| Setting | Options | Default |
|---------|---------|---------|
| Difficulty | Easy / Normal / Hard / Very Hard | Normal |
| Coinage | Various (1C/1P, 2C/1P, etc.) | 1 Coin / 1 Play |
| Lives / Continues | 1--9 continues, or Free Play | 3 continues |
| Versus match format | Best of 3 / Best of 5 | Best of 3 |
| Demo sound | On / Off | On |
| Service mode | On / Off | Off |
| Flip screen | On / Off (for cocktail cabinets) | Off |

### Difficulty Effects

| Difficulty | Ceiling Speed | Shot Timer | Bubble Colors |
|------------|--------------|------------|---------------|
| Easy | Slower descent | ~12 seconds | Fewer colors per round |
| Normal | Standard | ~10 seconds | Standard |
| Hard | Faster descent | ~8 seconds | More colors per round |
| Very Hard | Very fast descent | ~6 seconds | Maximum colors |

---

## Appendix C: Known Quirks and Edge Cases

1. **Color re-roll on elimination**: When a color is completely eliminated from the field, any "next bubble" preview of that color should be re-rolled to a valid color. Some implementations keep the existing color until it is fired, then ensure subsequent bubbles are valid.

2. **Simultaneous snap and pop**: If a bubble snaps to a position that completes a 3+ match, the pop occurs immediately in the same game tick. There is no delay between snap and match check.

3. **Multiple orphan groups**: When a pop disconnects multiple separate groups of bubbles from the ceiling, all groups fall simultaneously. The drop scoring counts ALL orphaned bubbles from a single pop event, not per group.

4. **Wall hugging**: At very shallow angles (near horizontal), a bubble can bounce many times between the walls while slowly ascending. This is legal and sometimes strategically useful.

5. **Ceiling snap priority**: When a bubble reaches the ceiling between two valid cells, it snaps to whichever cell center is closer to the bubble's center at the moment of contact.

6. **Shot counter persistence**: The shot counter for ceiling descent does NOT reset between pops. It only resets when the ceiling actually descends.

7. **2P stack overflow**: In versus mode, if the transfer stack accumulates a very large number of bubbles, they are all dumped at once, potentially instantly overwhelming the opponent.
