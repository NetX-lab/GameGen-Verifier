# Candy Crush Saga -- Complete Game Specification

> A comprehensive specification for faithfully recreating Candy Crush Saga (King, 2012 mobile/Facebook match-3 puzzle game). This document covers every system, mechanic, candy type, blocker, scoring rule, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Match-3 Mechanics](#3-core-match-3-mechanics)
4. [All Candy Types](#4-all-candy-types)
5. [Special Candy Creation Rules](#5-special-candy-creation-rules)
6. [Special Candy Combination Effects](#6-special-candy-combination-effects)
7. [Level Types](#7-level-types)
8. [Blocker Types](#8-blocker-types)
9. [Cascade System](#9-cascade-system)
10. [Scoring System](#10-scoring-system)
11. [Board Generation & Layout](#11-board-generation--layout)
12. [Lives & Progression System](#12-lives--progression-system)
13. [Boosters](#13-boosters)
14. [Sugar Crush End-of-Level Bonus](#14-sugar-crush-end-of-level-bonus)
15. [UI Layout & Screen Flow](#15-ui-layout--screen-flow)
16. [Audio Design](#16-audio-design)
17. [Monetization & Premium Currency](#17-monetization--premium-currency)

---

## 1. Game Overview

- **Title**: Candy Crush Saga
- **Developer / Publisher**: King
- **Original Release**: April 12, 2012 (Facebook); November 14, 2012 (iOS / Android)
- **Genre**: Puzzle / Match-3
- **Perspective**: 2D top-down static board
- **Input**: Touch (mobile) or Mouse click/drag (desktop). Single-point interaction only.
- **Primary Objective**: Swap adjacent candies on a grid to create matches of 3 or more same-colored candies, completing level-specific objectives within a limited number of moves.
- **Core Fantasy**: Clear colorful candy from a whimsical game board through strategic swapping, triggering chain reactions and deploying powerful special candy combinations.
- **Target Session Length**: 1--5 minutes per level attempt.
- **Target Audience**: Casual players; all ages.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native board grid | 9 x 9 cells (maximum) |
| Aspect ratio | Portrait on mobile; landscape on Facebook/desktop |
| Frame rate target | 60 FPS |
| Original platform | Facebook (Flash); later HTML5 for all platforms |
| Current platforms | iOS, Android, Windows 10/11, Facebook (HTML5) |
| Rendering | 2D sprite-based with tweened animations |

### Coordinate System

- Board origin (0, 0) at the top-left cell of the grid.
- Column indices run left-to-right: 0..8.
- Row indices run top-to-bottom: 0..8.
- Gravity direction: top to bottom (candies fall downward to fill empty cells).
- Some levels use candy cannons at the top of columns that dispense new candies.

### Game Loop (per move)

```
1. Wait for player input (swap gesture)
2. Validate swap: does it create at least one match of 3+? If no, reject and bounce candies back.
3. Execute swap animation (~200ms)
4. Scan board for all matches (3+, prioritizing special candy creation patterns)
5. Mark matched candies for removal; create special candies where applicable
6. Play clear animations and award points
7. Apply gravity: drop candies to fill empty cells
8. Spawn new random candies from top / candy cannons
9. Re-scan for new matches created by gravity (cascade)
10. If new matches found, repeat from step 5
11. If no matches found, cascade ends
12. Check for blocker spread (chocolate spreads if none destroyed this turn)
13. Decrement bomb timers
14. Check win/lose conditions
15. If no valid moves remain and game not over, shuffle the board
16. Return to step 1
```

---

## 3. Core Match-3 Mechanics

### Swap Rules

- The player selects a candy and swaps it with one **orthogonally adjacent** candy (up, down, left, or right). Diagonal swaps are **not** permitted.
- A swap is only **legal** if it produces at least one match of 3 or more candies of the same color in a horizontal or vertical line.
- If the swap does not produce a match, the two candies animate swapping and then **bounce back** to their original positions. This does **not** consume a move.
- A successful swap **consumes one move** from the move counter.
- Swapping two special candies together triggers their **combination effect** regardless of whether it forms a color match.

### Match Detection

- A **match** is 3 or more candies of the same color aligned in a contiguous horizontal or vertical line.
- Matches are detected simultaneously across the entire board after each swap or gravity settle.
- If a candy participates in both a horizontal and vertical match simultaneously (T-shape or L-shape), it produces a **Wrapped Candy** rather than two separate matches.
- Match priority for special candy creation (highest first):
  1. **5 in a line** -> Color Bomb
  2. **T-shape or L-shape** (5 candies in intersecting lines) -> Wrapped Candy
  3. **4 in a line** -> Striped Candy
  4. **3 in a line** -> Normal clear (no special candy created)

### Gravity & Refill

- When candies are removed, all candies above the empty cells fall downward to fill gaps.
- New random candies spawn at the top of each column (or from designated candy cannons) to replace depleted supply.
- Gravity operates column by column, and new candies are drawn from a seeded random pool of the level's active color set.
- The gravity-refill-rescan cycle repeats until no new matches form (this is the **cascade**).

### No-Moves Shuffle

- If no valid swap exists on the board after a cascade resolves, the board **automatically shuffles** all movable candies into new random positions.
- Shuffling preserves all blockers, special candies, and objective-critical elements in place.
- The shuffle guarantees at least one valid move exists after completion.
- A text notification "No more moves! Shuffling..." is displayed.

### Hint System

- If the player is idle for approximately **5 seconds**, a hint animation plays: one valid swap pair of candies gently pulses/glows to suggest a move.
- The hint does not necessarily suggest the best move, just a legal one.

---

## 4. All Candy Types

### 4.1 Base Candies (Regular)

There are **6 base candy colors**, each with a distinct shape:

| Color | Candy Name | Shape Description |
|-------|-----------|-------------------|
| Red | Red Jelly Bean | Rounded jellybean / bean shape |
| Orange | Orange Lozenge | Diamond / lozenge shape |
| Yellow | Yellow Lemon Drop | Teardrop / lemon drop shape |
| Green | Green Gum Square | Rounded square shape |
| Blue | Blue Lollipop Head | Circular lollipop head shape |
| Purple | Purple Jujube Cluster | Cluster of small rounded shapes |

- Not all 6 colors appear in every level. Levels use between **2 and 6 colors** depending on design difficulty.
- Fewer colors make matching easier; more colors increase difficulty.

### 4.2 Special Candies

| Special Candy | Creation Method | Appearance | Effect on Activation |
|---------------|----------------|------------|----------------------|
| **Striped Candy (Horizontal)** | Match 4 in a horizontal row | Base candy with horizontal stripes | Clears entire **row** the candy occupies |
| **Striped Candy (Vertical)** | Match 4 in a vertical column | Base candy with vertical stripes | Clears entire **column** the candy occupies |
| **Wrapped Candy** | Match 5 in an L-shape or T-shape | Base candy with wrapper/bow overlay | Explodes in a **3x3 area**, then settles and explodes a second time in another 3x3 area |
| **Color Bomb** | Match 5 in a straight line | Chocolate sprinkle ball (not color-specific) | Swap with any candy to destroy **all candies of that color** on the board |
| **Jelly Fish** | Spawned by candy cannons or 2x2 match (event) | Small candy fish | Targets and destroys **3 random jelly squares** (or random candies if no jelly remains) |
| **Coconut Wheel** | Spawned on board (specific levels) | Pink/white coconut wheel shape | When swapped, rolls in the swap direction, converting the next **3 candies** into Striped Candies that immediately activate |
| **Lucky Candy** | Spawned on board (specific levels) | Candy with a question mark "?" | When matched, transforms into whichever item the level currently needs most (a required order piece, special candy, etc.) |

### 4.3 Striped Candy Orientation Rule

- The stripe direction is determined by the **direction of the player's swap**, not the direction of the match line.
- If the player swaps **horizontally** to create a 4-match, the resulting Striped Candy has **vertical** stripes (clears a column).
- If the player swaps **vertically** to create a 4-match, the resulting Striped Candy has **horizontal** stripes (clears a row).
- If a Striped Candy is created by a cascade (no player swap), the orientation is chosen **randomly**.

### 4.4 Ingredient Pieces (Non-candy Movable Items)

| Ingredient | Appearance | Behavior |
|------------|-----------|----------|
| Cherry | Red cherry with stem | Must be brought to the bottom exit point by clearing candies beneath it |
| Hazelnut | Brown hazelnut | Same behavior as cherry; must reach the exit |

- Ingredients are **not matchable**. They are moved only by gravity when candies below them are cleared.
- Ingredients pass through "exit" markers (green arrows) at the bottom of designated columns to be collected.

---

## 5. Special Candy Creation Rules

### Creation Patterns

All special candies are created by matching specific patterns of same-colored candies in a single move:

| Pattern | Count | Shape | Result |
|---------|-------|-------|--------|
| 3 in a line | 3 | Horizontal or vertical line | **Normal match** (no special created) |
| 4 in a line | 4 | Horizontal or vertical line | **Striped Candy** at the intersection/swap point |
| L-shape | 5 | 3 in one line + 3 in perpendicular (sharing corner) | **Wrapped Candy** at the corner cell |
| T-shape | 5 | 3 in one line + 3 in perpendicular (sharing center) | **Wrapped Candy** at the center cell |
| 5 in a line | 5 | Straight horizontal or vertical line | **Color Bomb** at the swap point |
| 6+ in a line | 6+ | Extended straight line | **Color Bomb** + remaining candies cleared normally |

### Placement of Created Special Candy

- The newly created special candy appears at the **position of the candy the player moved** (the swap origin) when possible.
- If created during a cascade (no player swap), it appears at the **center** of the matched pattern.
- Only **one** special candy is created per match pattern. Excess candies in the match are simply cleared.

---

## 6. Special Candy Combination Effects

When two special candies are **swapped with each other**, a powerful combination effect triggers instead of their individual effects. The two candies do **not** need to form a color match to combine.

### Combination Matrix

| Candy A | Candy B | Combined Effect |
|---------|---------|-----------------|
| **Striped** | **Striped** | Clears both the entire **row** AND entire **column** intersecting at the swap point (cross/plus pattern) |
| **Striped** | **Wrapped** | Creates a giant cross that clears **3 rows AND 3 columns** centered on the swap point (a plus sign that is 3 cells wide in each direction) |
| **Striped** | **Color Bomb** | All candies matching the Striped Candy's color transform into Striped Candies with random orientations, then all activate simultaneously |
| **Wrapped** | **Wrapped** | Produces a massive double explosion: a **5x5 area** clear centered on the swap point |
| **Wrapped** | **Color Bomb** | All candies of the Wrapped Candy's color transform into Wrapped Candies, then all explode. Effectively two Color Bomb activations. |
| **Color Bomb** | **Color Bomb** | **Clears the entire board** of all candies and removes one layer from every blocker on the board |
| **Color Bomb** | **Regular Candy** | Destroys all candies on the board matching the regular candy's color |

### Combination Detail Notes

- **Striped + Striped**: Always produces a full cross regardless of stripe orientation on either candy. The horizontal line and vertical line both fire from the point of the swap.
- **Striped + Wrapped**: The 3-wide cross effect clears a band that is 3 rows tall horizontally and 3 columns wide vertically, creating a massive plus-sign clearance across the board.
- **Color Bomb + Striped**: Each candy of the matching color that is converted to a Striped Candy also individually activates, potentially creating huge chain reactions across multiple rows and columns.
- **Color Bomb + Wrapped**: Similar to Color Bomb + Striped but converts all matching candies into Wrapped Candies that each explode in 3x3 areas.
- **Color Bomb + Color Bomb**: The rarest and most powerful combination. Clears every candy and strips one layer off every blocker on the entire board.

---

## 7. Level Types

Candy Crush Saga features several level types, each with distinct objectives. Levels are played within a limited number of moves (unless otherwise noted).

### 7.1 Moves Levels (Retired)

| Property | Value |
|----------|-------|
| Objective | Reach the target score before running out of moves |
| Fail condition | Moves reach 0 without hitting 1-star score threshold |
| Status | **Removed** from game as of August 31, 2021 |
| Indicator color | Blue banner |

### 7.2 Jelly Levels

| Property | Value |
|----------|-------|
| Objective | Clear all jelly squares on the board |
| Jelly layers | Single jelly (1 hit) or Double jelly (2 hits) |
| Clear method | Match candies on top of jelly-covered cells |
| Fail condition | Moves reach 0 with jelly remaining |
| Indicator color | Green banner |

- **Single jelly**: Translucent colored square under the candy. One match clears it.
- **Double jelly**: Thicker, more opaque jelly square. Requires **two** matches on the same cell to fully clear.
- Jelly can be hidden under blockers. Clearing the blocker first is necessary to access the jelly.
- Special candy explosions and cascades also clear jelly on affected cells.
- Jelly fish specifically target jelly squares.

### 7.3 Ingredient Drop Levels

| Property | Value |
|----------|-------|
| Objective | Bring all ingredients (cherries, hazelnuts) to the exit points |
| Exit markers | Green downward arrows at the bottom of specific columns |
| Fail condition | Moves reach 0 with ingredients still on the board |
| Indicator color | Pink/magenta banner |

- Ingredients drop due to gravity when candies below them are cleared.
- Ingredients cannot be swapped or matched directly.
- Multiple ingredients may need to be collected; the count is shown in the objective panel.

### 7.4 Timed Levels (Retired)

| Property | Value |
|----------|-------|
| Objective | Reach the target score before the timer runs out |
| Timer | Countdown clock (typically 60--120 seconds) |
| Special mechanic | +5 second candies appear on the board periodically |
| Fail condition | Timer reaches 0 without hitting 1-star score threshold |
| Status | **Removed** from the game due to negative player reception |
| Indicator color | Purple banner |

### 7.5 Candy Order Levels

| Property | Value |
|----------|-------|
| Objective | Collect specific quantities of designated candies, special candies, or blockers |
| Example orders | "Collect 20 blue candies," "Create 5 Striped Candies," "Destroy 10 chocolate" |
| Fail condition | Moves reach 0 with order incomplete |
| Indicator color | Orange banner |

- The required orders are displayed in the objective panel at the top of the screen.
- Progress is tracked in real-time as items are collected/destroyed.
- Orders can require: regular colored candies, special candies, blocker destruction, or combinations.

### 7.6 Rainbow Rapids Levels

| Property | Value |
|----------|-------|
| Objective | Connect a rainbow flow from the faucet (start) to the mold (end) by clearing blockers in the path |
| Introduced | Level 7116 |
| Indicator | Rainbow-colored banner |

- The board features a **rainbow faucet** (start point) and a **rainbow mold** (end point).
- The rainbow stream flows between them but is blocked by obstacles.
- Clearing blockers along the path allows the rainbow to progress.
- Can be mixed with other level types (jelly + rainbow rapids, etc.).

### 7.7 Mixed Mode Levels

| Property | Value |
|----------|-------|
| Objective | Combines objectives from two or more level types |
| Example | Clear all jelly AND collect 3 ingredients |
| Introduced | Early in the game |
| Percentage of all levels | ~37.5% |

- All sub-objectives must be completed to win.
- Mixed mode levels are the most common level type in the game.

---

## 8. Blocker Types

Blockers are obstacles placed on the board that impede candy movement and matching. They must be cleared (or worked around) to complete objectives.

### 8.1 Complete Blocker Table

| Blocker | Layers/Hits | First Appears | Behavior | Clear Method |
|---------|-------------|---------------|----------|--------------|
| **Icing (Frosting / Meringue)** | 1--5 layers | Level 8 | Static; occupies a cell; no candy underneath | Match adjacent candies or use special candy effects; one hit removes one layer |
| **Chocolate** | 1 layer | Level 52 | **Spreads** by one tile each turn if no chocolate is cleared that move | Match adjacent to it or hit with special candy; clears in one hit |
| **Dark Chocolate** | 1--2 layers | Later episodes | Spreads **more aggressively** than regular chocolate; generates new squares when one gains a layer | Adjacent matches or special candy hits; each hit removes one layer |
| **Chocolate Fountain** | Indestructible | Level 156 | **Spawns** new chocolate squares each turn even if all other chocolate is cleared | Cannot be destroyed; must be managed |
| **Licorice Swirl** | 1 layer | Level 81 | Occupies a cell like a regular candy but is **not matchable**; blocks the cell | Match adjacent to it or hit with special candy; clears in one hit |
| **Licorice Lock (Liquorice Lock)** | 1 layer | Level 97 | **Locks** the candy inside; the locked candy cannot move, be swapped, or be cleared by adjacent matches | Match the locked candy's color in a line touching it (the lock breaks, candy remains); or hit with special candy |
| **Marmalade** | 1 layer | Level 211 | Encases a candy (often a special candy); the encased candy cannot activate or be moved | Match adjacent to the marmalade to break the shell; the candy inside is then freed |
| **Candy Bomb** | Timed (countdown) | Level 96 | Has a **move counter** number displayed on it; decrements by 1 each player move | Must match the bomb's color adjacent to it or use special candy before counter reaches 0; if counter reaches 0, **the player loses** |
| **Cake Bomb** | 8 hits (8 slices) | Level 366 | Occupies a **2x2** area on the board; pieces break off one at a time from adjacent matches | Match adjacent to any edge; each match removes 1 slice; special candy hits can remove up to 4 slices; when all 8 slices removed, a **board-wide explosion** clears all candies and removes 1 layer from all blockers |
| **Candy Cane Fence** | Indestructible | Level 3246 | **Barrier** placed between two cells; prevents candies on either side from matching or swapping with each other | Cannot be destroyed; must be worked around |
| **Candy Cane Curl** | 1--3 layers (orange/purple/green) | Level 4086 | Similar to Candy Cane Fence but **destructible**; protects candies within its radius | Match adjacent or use special candies; each hit removes one layer |
| **Licorice Shell (formerly Popcorn)** | 3 hits | Level 1384 | Stationary blocker; when fully destroyed (3 hits), transforms into a **Color Bomb** | Match adjacent to it 3 times or hit with special candies |
| **Toffee Tornado** | Cannot be permanently cleared | Removed from standard levels (late 2015) | Moves to a **random tile** every 1--2 turns; destroys any candy on the tile it moves to; leaves a crack that blocks the tile for one additional turn | Cannot be permanently removed; hitting with special candy disables it for several moves |
| **Conveyor Belt** | N/A (board element) | Various levels | Shifts all candies on the belt one position in the indicated direction each turn | Not a blocker to destroy; a board movement mechanic |
| **Liquorice Fence** | Indestructible | Various levels | Barrier on cell edges preventing movement in one direction | Cannot be destroyed |
| **Sugar Chest** | 1--3 layers | Later episodes | Contains a candy or booster inside; opened by collecting keys (matched like colored candies) | Collect the required number of keys by matching key-colored candies adjacent to it |

### 8.2 Blocker Interaction Rules

- **Chocolate spread prevention**: Chocolate does not spread through Icing, Licorice Swirls, Marmalade, Candy Cane Fences, or board edges.
- **Chocolate clearing rule**: If the player clears at least **one** chocolate square per move, chocolate does not spread that turn. If zero chocolate is cleared in a move, **one** new chocolate square spawns adjacent to existing chocolate.
- **Chocolate Fountain**: Spawns one new chocolate tile per turn regardless of whether chocolate was cleared.
- **Jelly under blockers**: Jelly can exist beneath multi-layer icing and other blockers. The blocker layers must be removed first before the jelly can be cleared.
- **Bomb failure**: If a Candy Bomb's countdown reaches 0, the level is **instantly failed** regardless of remaining moves or objective progress.

---

## 9. Cascade System

### What is a Cascade?

A cascade (also called a chain reaction) occurs when matches formed by falling candies (after the initial player-triggered match is resolved) create additional automatic matches without further player input.

### Cascade Flow

```
Player swaps two candies
  -> Initial match(es) resolved and cleared
  -> Candies above fall down (gravity)
  -> New candies spawn from top
  -> New matches detected from settled board
  -> Those matches clear (CASCADE LEVEL 1)
  -> More candies fall
  -> More new matches detected
  -> Those matches clear (CASCADE LEVEL 2)
  -> ... continues until no new matches form
```

### Cascade Properties

- Each successive cascade level awards **increased points** (see Scoring System).
- Cascades can trigger special candy activations if special candies are involved in gravity-formed matches.
- Long cascades can dramatically increase score and are key to achieving 3-star ratings.
- Cascades count as a single "turn" for blocker mechanics (chocolate spread, bomb countdown, etc.).
- The total number of cascades in a single move is unlimited in theory.

### Cascade Voice Announcements

Based on the number of candies destroyed or cascades achieved in a single move:

| Threshold | Announcement | Trigger |
|-----------|-------------|---------|
| 12+ candies destroyed OR 4+ cascades | **"Sweet!"** | Spoken voice + on-screen text |
| 18+ candies destroyed OR 6+ cascades | **"Tasty!"** | Spoken voice + on-screen text |
| 24+ candies destroyed OR 8+ cascades | **"Delicious!"** | Spoken voice + on-screen text |
| 30+ candies destroyed OR 10+ cascades | **"Divine!"** | Spoken voice + on-screen text |

- A single move can trigger multiple announcements sequentially as cascades continue.
- The "Divine!" announcement has a rare **0.1% (1 in 1000)** chance of being spoken in an alternate voice.

---

## 10. Scoring System

### 10.1 Base Match Points

| Match Type | Points Awarded |
|------------|---------------|
| 3-candy match (normal clear) | **60 points** |
| 4-candy match (creates Striped Candy) | **120 points** |
| 5-candy L/T-shape (creates Wrapped Candy) | **200 points** |
| 5-candy line (creates Color Bomb) | **200 points** |

### 10.2 Special Candy Activation Points

| Activation | Points |
|------------|--------|
| Striped Candy clears a row/column | **60 points per candy destroyed** in the line |
| Wrapped Candy explosion | **540 points** base + **60 points per candy destroyed** in the 3x3 area |
| Color Bomb + regular candy swap | **1,200 points** base + **60 points per candy destroyed** of the matching color |
| Candy Bomb defused (matched before countdown) | **3,000 points** |

### 10.3 Jelly Level Bonus Points

| Jelly Action | Points |
|-------------|--------|
| Clearing a single jelly square | **1,000 points** |
| Clearing a double jelly square (per layer) | **1,000 points** per layer |
| 3-match on single jelly | **3,060 points** (3,000 jelly + 60 match) |
| Striped Candy on jelly | **4,120 points** (4,000 jelly bonus + 120 match) |
| Wrapped Candy on jelly | **5,200 points** (5,000 jelly bonus + 200 match) |
| Color Bomb activation on jelly | **6,120+ points** (scaling with candies destroyed) |

### 10.4 Blocker Destruction Points

| Blocker | Points per Layer |
|---------|-----------------|
| Icing (per layer cleared) | **20 points** |
| Chocolate (per square) | **20 points** |
| Licorice Swirl | **20 points** |
| Marmalade shell | **20 points** |
| Licorice Shell / Popcorn (per hit) | **20 points** (bonus Color Bomb on final hit) |

### 10.5 Cascade Scoring Multiplier

Cascades award progressively increasing bonus points:

| Cascade Level | Bonus Points (for 3-match) | Cumulative Multiplier |
|---------------|---------------------------|----------------------|
| 0 (initial match) | 60 | x1 |
| 1st cascade | 120 | x2 |
| 2nd cascade | 180 | x3 |
| 3rd cascade | 240 | x4 |
| 4th cascade | 300 | x5 |
| Nth cascade | 60 x (N+1) | x(N+1) |

- The cascade multiplier applies to the **base match value** of each match in that cascade level.
- Formula: `points_per_match = base_points x (cascade_level + 1)`
- The total score from cascades is a **quadratic function** of the cascade depth, making long chains extremely valuable.

### 10.6 Star Rating Thresholds

| Star Level | Requirement |
|------------|-------------|
| 1 Star | Reach the level's **minimum target score** (varies per level) |
| 2 Stars | Reach the **2-star threshold** (varies per level; typically ~2x the 1-star target) |
| 3 Stars | Reach the **3-star threshold** (varies per level; typically ~3-5x the 1-star target) |
| Sugar Stars | Reach **exactly 2x the 3-star threshold** score |

- Each level has unique, designer-set score thresholds for each star rating.
- Star thresholds are displayed on the pre-level info screen.
- At least 1 star is required to pass the level.
- Completing the level objective (jelly, ingredients, order) is also required -- score alone is not sufficient for non-moves levels.
- Sugar Stars were introduced as an additional challenge for completionists.

---

## 11. Board Generation & Layout

### 11.1 Grid Dimensions

| Property | Value |
|----------|-------|
| Maximum grid size | **9 columns x 9 rows** (81 cells) |
| Minimum grid size | Varies by level; some levels use irregular shapes as small as 5x5 effective area |
| Cell shape | Square |
| Board shape | Can be any subset of the 9x9 grid; irregular shapes with holes, narrow passages, and isolated sections are common |

### 11.2 Board Shape Variations

- **Full rectangle**: Standard 9x9, 9x8, 8x7, etc.
- **Irregular / custom shapes**: Cells can be removed to create diamond shapes, crosses, narrow corridors, isolated islands connected by 1-cell-wide passages, and many other custom configurations.
- **Multi-section boards**: Some levels have two or more separate areas connected only by teleporters or conveyors.
- **Teleporter portals**: Candies exiting one portal enter another, allowing non-contiguous board sections.

### 11.3 Initial Board Generation Rules

1. Randomly assign one of the level's active colors (2--6 colors) to each non-blocked, non-special cell.
2. **No pre-existing matches**: The initial board must contain **zero** matches of 3 or more. If a random assignment creates one, re-randomize those cells until no initial match exists.
3. **At least one valid move**: The generated board must have at least one legal swap that produces a match. If not, regenerate.
4. Place all pre-set elements: blockers, ingredients, special spawners, locked candies, and pre-placed special candies as defined in the level configuration.
5. Level configurations are **hand-designed** by King's level designers; the randomization is only for the candy colors filling the empty playable cells.

### 11.4 Candy Cannons / Dispensers

- Located at the top of columns (or at board edges in unusual layouts).
- Dispense new random candies to fill the column as candies are cleared below.
- Some cannons are configured to periodically dispense **special items**: Jelly Fish, Lucky Candies, or other special elements defined by the level.

### 11.5 Active Color Count by Difficulty

| Colors on Board | Typical Usage |
|-----------------|--------------|
| 3 colors | Tutorial levels only; very easy |
| 4 colors | Easy levels; increases match frequency |
| 5 colors | Standard difficulty; most common in early/mid game |
| 6 colors | Hard levels; reduces match frequency significantly |

---

## 12. Lives & Progression System

### 12.1 Lives

| Property | Value |
|----------|-------|
| Maximum lives (standard) | **5** |
| Regeneration rate | **1 life per 30 minutes** |
| Full refill time | **2 hours 30 minutes** (5 lives x 30 min) |
| Life lost on | Failing a level (running out of moves) or quitting mid-level |
| Life NOT lost on | Winning a level |
| Friend-sent lives | Up to **20 lives accepted per day**; up to **200** stored in mailbox |

- When lives reach 0, the player cannot start a new level attempt.
- Lives can be refilled instantly by spending Gold Bars (premium currency).
- Refill costs: 1 life = 4 Gold Bars; 5 lives = 12 Gold Bars; unlimited lives for 6 hours = 69 Gold Bars.

### 12.2 Map & Episode Progression

| Property | Value |
|----------|-------|
| Episode size | **15 levels** per episode (except first two episodes: 10 levels each) |
| Total levels | 22,000+ and growing (new episodes added regularly) |
| Total episodes | 1,460+ |
| Worlds | 5 episodes per world |
| Progression | Linear; must complete all levels in an episode to unlock the next |
| Episode gates | Originally required Facebook friend tickets or 72-hour wait or 9 Gold Bars; **now removed** (free progression) |

### 12.3 Map Visual Design

- The map is a winding path through themed candy landscapes.
- Each level is represented by a **numbered dot** on the path.
- Completed levels show the player's star rating (1, 2, or 3 stars).
- Each episode has a unique **theme name** (e.g., "Candy Town," "Lemonade Lake," "Chocolate Mountains").
- Story vignettes play at the start and end of each episode featuring characters like Mr. Toffee, Tiffi, and Odus the Owl.
- The player's avatar and friends' avatars are shown on the map at their current level.

### 12.4 Episode Race

- When starting a new episode, the player is entered into a race against 4 other randomly selected players.
- **1st place**: 5 Gold Bars
- **2nd place**: 3 Gold Bars
- **3rd place**: 1 Gold Bar
- The race ends when any player completes all 15 levels in the episode.

---

## 13. Boosters

Boosters are power-ups that provide advantages. They are divided into **pre-game boosters** (activated before a level starts) and **in-game boosters** (activated during gameplay).

### 13.1 Pre-Game Boosters

These are selected on the level start screen before beginning the level.

| Booster | Unlock Level | Effect |
|---------|-------------|--------|
| **Color Bomb** | Level 13 | Places **1 Color Bomb** on a random board position at level start |
| **Striped & Wrapped** | Level 9 | Places **1 Striped Candy** and **1 Wrapped Candy** on random board positions at level start |
| **Jelly Fish** | Level 39 (jelly levels) | Places **several Jelly Fish** on random board positions at level start |
| **Coconut Wheel** | Ingredient levels only | Places **1 Coconut Wheel** on the board at level start |
| **Lucky Candy** | Various | Places **1 Lucky Candy** (transforms into the most needed special for the level) on the board |

### 13.2 In-Game Boosters

These can be activated during gameplay and typically do **not** consume a move.

| Booster | Unlock Level | Effect | Consumes Move? |
|---------|-------------|--------|----------------|
| **Lollipop Hammer** | Level 7 | Tap any **single cell** to destroy whatever is on it (candy, blocker layer, ingredient) | **No** |
| **Free Switch** | Level 15 | Swap any two **adjacent** candies freely, even if it does not create a match | **No** |
| **UFO** | Level 21 | A UFO flies over the board and drops **3 Wrapped Candies** onto random positions, which immediately explode | **No** |
| **Party Popper** | Level 29 | Two party poppers appear and trigger a **board-wide explosion** (similar to Cake Bomb clearing effect); places random special candies on cleared cells | **No** |
| **Sweet Teeth** | Various | Eats a portion of chocolate blockers | **No** |
| **Bomb Cooler** | Various | Adds +5 to all Candy Bomb countdowns on the board | **No** |
| **Bubblegum Troll** | Various | Prevents chocolate from spreading for 3 turns | **No** |
| **Extra Moves (+3)** | Post-level | Adds 3 extra moves when the player fails; offered as a continue option | N/A |
| **Extra Moves (+5)** | Post-level | Adds 5 extra moves on failure; premium option | N/A |

### 13.3 Booster Acquisition

- Boosters are earned through: level rewards, daily bonuses, episode race prizes, special events, Daily Booster Wheel, and purchasing with Gold Bars.
- Each booster has a **limited quantity** in the player's inventory.
- Some boosters can be purchased with Gold Bars directly; typical cost: 9--15 Gold Bars per booster.

---

## 14. Sugar Crush End-of-Level Bonus

### 14.1 Trigger

Sugar Crush activates **automatically** when the player completes the level's objective(s). The voice announces **"Sugar Crush!"** and the text appears on-screen.

### 14.2 Remaining Moves Bonus

Each remaining (unused) move is converted into a bonus:

| Per Remaining Move | Effect |
|-------------------|--------|
| Base points | **3,000 points** per remaining move |
| Special candy spawn | Each remaining move spawns a **Jelly Fish** on a random board position |
| Activation | All spawned Jelly Fish and any existing special candies activate sequentially |
| Chain reactions | The activated specials can trigger cascades, earning even more points |

- The Sugar Crush bonus can dramatically increase the final score, often doubling or tripling it.
- Players who finish levels efficiently (with many moves remaining) get significantly higher scores.

### 14.3 Special Candy Bonus Values During Sugar Crush

| Special Candy Activated | Bonus Points |
|------------------------|-------------|
| Jelly Fish | **250 points** each |
| Lucky Candy | **250 points** each |
| Striped Candy | **500 points** each |
| Wrapped Candy | **1,000 points** each |
| Coconut Wheel | **3,000 points** each |
| Color Bomb | **5,000 points** each |
| UFO | **5,000 points** each |

- These bonus points are awarded **in addition to** the normal effect-based scoring of the special candy activating.

### 14.4 Super Sugar Crush

| Property | Value |
|----------|-------|
| Trigger | Completing the level objective on the **very last move** (0 moves remaining) |
| Effect | A **board-wide explosion** equivalent to a Cake Bomb detonation |
| Introduced | July 1, 2018 |

---

## 15. UI Layout & Screen Flow

### 15.1 Screen Flow

```
Launch -> Title Screen -> Map Screen -> Level Info Screen -> Gameplay Screen -> Result Screen -> Map Screen
                              |                                    |
                              v                                    v
                         Settings                             Pause Menu
                         Friends                              Settings
                         Shop                                 Quit Level
```

### 15.2 Title Screen

- Candy Crush Saga logo with animated candy background.
- "Play" button.
- Settings gear icon.
- Player profile icon (level, avatar, stars).
- Event banners and notifications.

### 15.3 Map Screen

| Element | Position | Description |
|---------|----------|-------------|
| Map path | Center, scrollable | Winding path through themed candy landscape; nodes represent levels |
| Level nodes | Along the path | Numbered circles; color indicates level type; completed nodes show star rating |
| Player avatar | On current level | Shows player's position on the map |
| Friend avatars | On their levels | Social comparison; shows where friends are |
| Episode name | Top of each section | Themed name for 15-level grouping |
| Lives counter | Top-left | Heart icon with count (0--5) and timer if regenerating |
| Gold Bars counter | Top-right | Gold bar icon with quantity |
| Boosters bar | Bottom | Quick-access to booster inventory |

### 15.4 Level Info Screen (Pre-Game)

| Element | Description |
|---------|-------------|
| Level number | Large display at top |
| Objective icon(s) | Visual representation of level goal (jelly icon, ingredient icon, order items) |
| Objective text | "Clear all the Jelly!" / "Bring down all Ingredients!" / etc. |
| Star score thresholds | Three stars with target scores displayed |
| Moves count | Number of moves available |
| Booster selection | Slots for pre-game boosters; tap to equip from inventory |
| "Play" button | Large button to start the level |
| Previous best score | Displayed if level was attempted before |
| Friend scores | Leaderboard of friends' scores on this level |

### 15.5 Gameplay Screen (HUD)

| Element | Position | Description |
|---------|----------|-------------|
| Game board | Center | 9x9 grid (or subset) filled with candies and blockers |
| Moves counter | Top-left | Large number showing remaining moves |
| Score bar | Top-center | Current score with progress bar toward star thresholds |
| Star indicators | On score bar | 1-star, 2-star, and 3-star markers along the progress bar |
| Objective tracker | Top-right | Icons and counts for level objectives (jelly remaining, ingredients collected, orders filled) |
| Booster tray | Bottom or side | Icons for available in-game boosters (Lollipop Hammer, Free Switch, etc.) |
| Pause button | Top corner | Gear or pause icon |
| Combo text | Center (transient) | "Sweet!", "Tasty!", "Delicious!", "Divine!" pop-up text during cascades |

### 15.6 Result Screen

#### Win Screen

| Element | Description |
|---------|-------------|
| "Sugar Crush!" banner | Celebratory animation |
| Star display | 1, 2, or 3 stars earned (animated fill) |
| Final score | Large score number |
| Score breakdown | Points from matches, cascades, Sugar Crush bonus |
| Friend comparison | "You beat [friend name]!" if applicable |
| "Next" button | Proceed to next level on map |

#### Fail Screen

| Element | Description |
|---------|-------------|
| "Level Failed" banner | Displayed with reason (out of moves, bomb exploded) |
| Continue offer | Option to buy extra moves with Gold Bars |
| "Try Again" button | Restart level (costs 1 life) |
| "Quit" button | Return to map |

### 15.7 Settings Screen

| Setting | Options |
|---------|---------|
| Music | On / Off (toggle) |
| Sound Effects | On / Off (toggle) |
| Notifications | On / Off |
| Language | Multiple language options |
| Account | Connect to Facebook / King account |
| Help | Link to support |

---

## 16. Audio Design

### 16.1 Music

| Context | Description |
|---------|-------------|
| Map screen | Cheerful, whimsical orchestral theme with xylophone and strings; upbeat tempo |
| Gameplay (normal) | Light, playful background loop; moderate tempo; candy/toy-like instrumentation |
| Gameplay (low moves) | Music tempo and intensity increase slightly when moves are low; subtle urgency |
| Sugar Crush | Triumphant, celebratory music sting |
| Level failed | Short, deflating descending melody |

### 16.2 Sound Effects

| Event | Sound Description |
|-------|-------------------|
| Candy swap | Short, light "swoosh" or "swish" |
| Invalid swap (bounce back) | Dull "bonk" or "thud" |
| 3-candy match | Crisp, bright chime (pitch varies by color) |
| 4-candy match (Striped creation) | Higher-pitched ascending chime |
| 5-candy match (Color Bomb / Wrapped creation) | Sparkling, multi-note ascending arpeggio |
| Striped Candy activation | Rapid "whoosh" laser-like sweep |
| Wrapped Candy explosion | Deep, satisfying "boom" with sparkle |
| Color Bomb activation | Dramatic "shimmering cascade" descending notes as candies pop |
| Color Bomb + Color Bomb | Extended dramatic explosion sound |
| Cascade combo (progressive) | Each successive cascade plays a **higher-pitched** version of the match chime, creating an ascending musical scale |
| Blocker destroyed (icing) | "Crack" or "shatter" glass-like sound |
| Chocolate destroyed | Squishy "splat" |
| Candy Bomb countdown warning | Ticking clock sound when bomb is at 3 or fewer moves |
| Candy Bomb explosion (failure) | Dramatic explosion; game-over sting |
| Ingredient collected | Cheerful "ding" collection sound |
| Jelly cleared | Soft "squelch" or "pop" |
| Booster activation | Unique sound per booster type (hammer tap, UFO hum, etc.) |
| Level complete | Triumphant fanfare |
| Level failed | Sad descending notes |
| Star earned | Bright ascending "ding-ding-ding" for each star |
| Button tap (UI) | Light "click" or "pop" |
| Sugar Crush activation | Dramatic ascending arpeggio + voice announcement |
| Super Sugar Crush | Extended explosion fanfare |

### 16.3 Voice Lines

| Trigger | Voice Line | Style |
|---------|-----------|-------|
| 4+ cascades or 12+ candies | **"Sweet!"** | Female voice, enthusiastic |
| 6+ cascades or 18+ candies | **"Tasty!"** | Female voice, more excited |
| 8+ cascades or 24+ candies | **"Delicious!"** | Female voice, very excited |
| 10+ cascades or 30+ candies | **"Divine!"** | Female voice, peak excitement (0.1% alternate voice chance) |
| Level objective completed | **"Sugar Crush!"** | Female voice, celebratory |

### 16.4 Audio Settings

- **Music volume**: Independent toggle (on/off); no slider in original.
- **Sound effects volume**: Independent toggle (on/off).
- Both music and SFX should be pauseable when the game is paused or backgrounded.

---

## 17. Monetization & Premium Currency

### 17.1 Gold Bars

Gold Bars are the premium currency in Candy Crush Saga.

| Gold Bar Package | Price (USD, approximate) |
|-----------------|------------------------|
| 10 Gold Bars | $1.40 |
| 50 Gold Bars | $7.00 |
| 100 Gold Bars | $14.00 |
| 150 Gold Bars | $21.00 |
| 250 Gold Bars | $29.00 |
| 500 Gold Bars | $55.00 |
| 1,000 Gold Bars | $105.00 |

### 17.2 Gold Bar Uses

| Purchase | Gold Bar Cost |
|----------|-------------|
| Refill 1 life | 4 Gold Bars |
| Refill 5 lives | 12 Gold Bars |
| Unlimited lives (6 hours) | 69 Gold Bars |
| Extra moves (+5) on fail | 9 Gold Bars |
| Lollipop Hammer (1x) | 9 Gold Bars |
| Free Switch (1x) | 9 Gold Bars |
| Other boosters | 9--15 Gold Bars each |

### 17.3 Free Gold Bar Sources

| Source | Gold Bars |
|--------|----------|
| Episode race: 1st place | 5 |
| Episode race: 2nd place | 3 |
| Episode race: 3rd place | 1 |
| Daily bonus wheel | 1--3 (rare) |
| Watching ads (when available) | 1--2 |
| Special events/promotions | Varies |
| Achievement rewards | Varies |

---

## Appendix A: Special Candy Quick Reference

### Creation Rules Summary

```
3 in a line       -> Normal clear (60 pts)
4 in a line       -> Striped Candy (120 pts)
L-shape or T-shape -> Wrapped Candy (200 pts)
5 in a line       -> Color Bomb (200 pts)
```

### Combination Effects Summary

```
Striped + Striped     -> Cross clear (1 row + 1 column)
Striped + Wrapped     -> Giant cross clear (3 rows + 3 columns)
Striped + Color Bomb  -> All of one color become Striped, then activate
Wrapped + Wrapped     -> Massive 5x5 explosion
Wrapped + Color Bomb  -> All of one color become Wrapped, then explode
Color Bomb + Color Bomb -> Entire board cleared + 1 layer off all blockers
Color Bomb + Regular  -> All of that color destroyed
```

---

## Appendix B: Resolve Order Reference

The complete resolution order for a single player move:

```
1.  Player swap input validated
2.  Swap animation plays (~200ms)
3.  Board scanned for matches (all simultaneous matches detected)
4.  Special candy creation resolved (highest priority pattern wins)
5.  Matched candies removed; special candy effects activated
6.  Points awarded (base match + special + jelly + blocker)
7.  Gravity applied: candies fall to fill empty cells
8.  New candies spawn from top/cannons
9.  Board re-scanned for new matches
10. If matches found: cascade level increments; return to step 4
11. If no matches found: cascade ends
12. Post-move checks:
    a. Chocolate spread (if no chocolate was cleared this move)
    b. Chocolate Fountain spawn
    c. Candy Bomb countdown decrement
    d. Toffee Tornado movement (if applicable)
    e. Conveyor Belt shift
13. Win condition check (objective met?)
14. Lose condition check (bomb exploded? moves depleted with objective incomplete?)
15. No-moves check (shuffle if needed)
16. Return control to player
```

---

## Appendix C: Level Configuration Data Schema

Each level in Candy Crush Saga is defined by a configuration that specifies:

```
Level Configuration:
  - level_number: integer
  - episode: integer
  - level_type: enum [jelly, ingredients, candy_order, rainbow_rapids, mixed]
  - board_layout: 9x9 boolean grid (true = playable cell, false = empty/blocked)
  - active_colors: list of 2-6 colors from [red, orange, yellow, green, blue, purple]
  - moves_allowed: integer
  - objectives:
    - type: enum [clear_jelly, drop_ingredients, collect_order, connect_rainbow]
    - targets: list of {item, quantity}
  - star_thresholds: [1_star_score, 2_star_score, 3_star_score]
  - blockers: list of {type, position, layer_count}
  - pre_placed_specials: list of {type, position}
  - candy_cannons: list of {column, special_dispense_type (optional), dispense_rate}
  - teleporters: list of {entrance_position, exit_position}
  - conveyor_belts: list of {cells, direction}
  - ingredient_exits: list of {column, row}
  - chocolate_fountains: list of positions
  - candy_bombs: list of {position, color, initial_countdown}
```
