# Royal Match — Complete Game Specification

> A comprehensive specification for faithfully recreating Royal Match (Dream Games, 2021 mobile match-3 puzzle game). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Match-3 Mechanics](#3-core-match-3-mechanics)
4. [Match Items (Base Pieces)](#4-match-items-base-pieces)
5. [Power-Ups (Special Pieces)](#5-power-ups-special-pieces)
6. [Power-Up Combinations](#6-power-up-combinations)
7. [Level Objectives](#7-level-objectives)
8. [Blocker & Game Element Types](#8-blocker--game-element-types)
9. [Board Mechanics](#9-board-mechanics)
10. [King's Nightmare Mode](#10-kings-nightmare-mode)
11. [Area Progression & Decoration](#11-area-progression--decoration)
12. [Economy System](#12-economy-system)
13. [Lives System](#13-lives-system)
14. [Boosters](#14-boosters)
15. [Butler's Gift](#15-butlers-gift)
16. [Team Features](#16-team-features)
17. [Events & Tournaments](#17-events--tournaments)
18. [Royal Pass (Season Pass)](#18-royal-pass-season-pass)
19. [Royal League](#19-royal-league)
20. [Scoring & Difficulty System](#20-scoring--difficulty-system)
21. [UI Layout & Screen Flow](#21-ui-layout--screen-flow)
22. [Audio Design](#22-audio-design)
23. [Characters & Narrative](#23-characters--narrative)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Royal Match |
| Developer / Publisher | Dream Games (Istanbul, Turkey) |
| Genre | Casual match-3 puzzle with meta-decoration |
| Platforms | iOS (App Store), Android (Google Play, Amazon Appstore, Galaxy Store) |
| Engine | Unity |
| Soft-Launch | July 2020 (Canada, Turkey, UK) |
| Global Release | February/March 2021 |
| Business Model | Free-to-play with in-app purchases |
| Content Volume | 12,400+ levels (as of late 2025), new levels added every two weeks |
| Minimum OS | iOS 13.0+, Android 7.0+ |
| Download Size | ~210 MB (APK) |

### Core Loop

1. **Play** a match-3 puzzle level within a limited number of moves.
2. **Earn** 1 star per completed level.
3. **Spend** stars on decoration tasks to restore areas of King Robert's castle.
4. **Complete** all tasks in an area to unlock the next area and receive an Area Chest reward.
5. **Repeat** — new areas, new levels, escalating mechanics.

### Narrative Premise

Players help King Robert restore and refurbish his royal castle, room by room. Each area represents a different part of the castle or grounds. The player's puzzle performance directly funds the renovation through the star currency.

---

## 2. Technical Foundation

### Display & Rendering

| Property | Value |
|----------|-------|
| Orientation | Portrait |
| Target frame rate | 60 FPS |
| Rendering | 2D sprites with particle effects |
| Resolution scaling | Adaptive to device screen |
| Haptic feedback | Yes (on supported devices) |

### Game Loop

```
1. Process input (tap, swipe gestures)
2. Validate swap (adjacent tiles, results in match)
3. Execute swap animation
4. Detect and resolve matches (3+ connected same-color items)
5. Activate any created/triggered power-ups
6. Apply gravity — tiles fall to fill gaps
7. Spawn new tiles from top of columns
8. Cascade detection — check for new matches from settled tiles
9. Allow next move during cascade (unique Royal Match feature)
10. Decrement move counter
11. Check objective completion → win
12. Check moves remaining = 0 with objectives incomplete → fail
13. Render (background → board → pieces → effects → UI overlay)
```

### Key Technical Feature

Royal Match allows players to **make the next move during cascading sequences** without waiting for animations to finish. This is a distinctive feature not present in most competing match-3 games. The board is always ready for interaction, creating a notably fast-paced feel.

---

## 3. Core Match-3 Mechanics

### Basic Matching Rules

| Rule | Description |
|------|-------------|
| Minimum match | 3 identical items in a horizontal or vertical line |
| Swap mechanic | Swipe or tap two adjacent tiles (horizontally or vertically) to swap |
| Invalid swap | If the swap does not create a match, tiles bounce back to original positions |
| Match resolution | Matched tiles are cleared from the board simultaneously |
| Gravity | After clearing, tiles above fall downward; new tiles spawn from the top of each column |
| Cascades | Falling tiles may create new matches, triggering chain reactions |
| Move consumption | One move is consumed per player-initiated swap (cascades are free) |
| Concurrent input | Players may queue the next move while cascades are resolving |

### Match Patterns & Results

| Pattern | Tiles Matched | Result |
|---------|---------------|--------|
| 3 in a line | 3 | Tiles cleared, no power-up created |
| 4 in a horizontal line | 4 | Creates a **Horizontal Rocket** |
| 4 in a vertical line | 4 | Creates a **Vertical Rocket** |
| 4 in a 2x2 square | 4 | Creates a **Propeller** |
| 5 in an L-shape | 5 | Creates a **TNT** |
| 5 in a T-shape | 5 | Creates a **TNT** |
| 5 in a straight line | 5 | Creates a **Light Ball** |
| 6+ in various shapes | 6+ | Creates the highest-tier power-up applicable to the formation |

### End-of-Level Bonus

When a level is completed with **remaining moves**, each leftover move is converted into a random power-up on the board. These power-ups then activate sequentially, clearing additional tiles and earning bonus coins.

---

## 4. Match Items (Base Pieces)

There are **5 distinct match items** in Royal Match. Each has a unique shape and color for instant visual recognition.

| Match Item | Color | Shape/Icon | Description |
|------------|-------|------------|-------------|
| Crown | Blue | Royal crown | Deep royal blue crown icon |
| Book | Red | Open book | Rich red/crimson open book icon |
| Leaf | Green | Leaf/clover | Bright green leaf or clover icon |
| Shield | Yellow | Heraldic shield | Golden yellow shield icon |
| Gem | Purple | Cut gemstone | Vibrant purple faceted gem icon |

### Visual Design Notes

- Each piece has a **bold, saturated color** with high contrast against the board background.
- Pieces feature subtle **3D shading and gloss effects** to appear polished and tactile.
- The color palette (blue, red, green, yellow, purple) is chosen for maximum distinguishability, including for players with color vision deficiency (shapes differ as well).
- Pieces animate with a slight **bounce/squish** when swapped and a **sparkle burst** when cleared.

---

## 5. Power-Ups (Special Pieces)

Power-ups are created by matching tiles in specific formations. They can be activated by **tapping** them or **swapping** them with an adjacent tile.

### Rocket

| Property | Value |
|----------|-------|
| Creation | Match 4 same-colored items in a straight line |
| Orientation | Horizontal (if matched horizontally) or Vertical (if matched vertically) |
| Visual | Arrow-shaped piece in the color of the matched items; animated directional indicator |
| Activation (Horizontal) | Clears the **entire row** the Rocket occupies, removing one layer from any game element in the row |
| Activation (Vertical) | Clears the **entire column** the Rocket occupies, removing one layer from any game element in the column |
| Activation method | Tap, swap, or hit by another power-up blast |

### Propeller

| Property | Value |
|----------|-------|
| Creation | Match 4 same-colored items in a **2x2 square** formation |
| Visual | Spinning propeller piece in the matched color |
| Activation — Stage 1 | Clears tiles in a **"+" pattern** (the 4 orthogonal neighbors) around the Propeller |
| Activation — Stage 2 | Flies to a **random game element** on the board and clears it (counts toward objectives) |
| Activation method | Tap, swap, or hit by another power-up blast |

### TNT (Bomb)

| Property | Value |
|----------|-------|
| Creation | Match 5 same-colored items in an **L-shape** or **T-shape** |
| Visual | TNT barrel/bomb piece; pulsing glow animation |
| Activation | Destroys all items within a **2-tile radius** (5x5 area) around the TNT, removing one layer from any game element in range |
| Activation method | Tap, swap, or hit by another power-up blast |

### Light Ball

| Property | Value |
|----------|-------|
| Creation | Match **5 same-colored items in a straight line** |
| Visual | Rainbow-colored glowing orb; distinct from all colored pieces |
| Activation (swap with colored piece) | Eliminates **every item of that color** currently on the board |
| Activation (tap) | Eliminates all items of the **most prevalent color** on the board |
| Activation method | Tap or swap with any adjacent tile |

---

## 6. Power-Up Combinations

Swapping two power-ups together (regardless of color) creates a **combined effect** that is significantly more powerful than either individual activation.

| Combination | Effect | Blast Area |
|-------------|--------|------------|
| **Rocket + Rocket** | Clears the **entire row AND entire column** of the activation tile simultaneously | Full cross pattern (1 row + 1 column) |
| **Rocket + TNT** | Clears **3 rows AND 3 columns** centered on the activation tile | 3-wide cross pattern |
| **Rocket + Propeller** | Propeller carries the Rocket to a **random game element**, clears neighbors on launch, then Rocket activates at the destination | Neighbors + 1 full row or column at destination |
| **TNT + TNT** | Clears all items within a **4-tile radius** (9x9 area) around the activation tile | Massive 9x9 blast zone |
| **TNT + Propeller** | Propeller carries the TNT to a **random game element**, clears neighbors on launch, then TNT explodes at the destination | Neighbors + 5x5 area at destination |
| **Propeller + Propeller** | Creates **3 Propellers** that each fly to a random game element; each Propeller also clears its neighboring tiles upon launch | 3 separate clearings + 3 neighbor bursts |
| **Light Ball + Rocket** | Converts all items of the **most prevalent color** on the board into Rockets, then all Rockets activate | Board-wide row/column clears |
| **Light Ball + TNT** | Converts all items of the **most prevalent color** on the board into TNTs, then all TNTs activate | Board-wide explosive clearings |
| **Light Ball + Propeller** | Converts all items of the **most prevalent color** on the board into Propellers, then all Propellers activate | Board-wide targeted clearings |
| **Light Ball + Light Ball** | Clears **ALL items on the entire board** and removes **one layer from every game element** | Complete board wipe |

---

## 7. Level Objectives

Each level defines one or more objectives that must be completed within the allotted move count. The objective panel is displayed at the top of the game screen.

### Objective Types

| Objective Type | Description | Example |
|----------------|-------------|---------|
| **Collect Match Items** | Clear a specified number of a particular colored match item | Collect 40 Blue Crowns |
| **Clear Blockers** | Destroy a specified number of a particular blocker type | Clear 15 Boxes |
| **Collect from Producers** | Make matches adjacent to producer elements to release collectible items | Collect 8 Mails from Mailboxes |
| **Bring Down Items** | Guide specific items (Birds, Frogs, Space Shuttles) to the **bottom of the board** by clearing tiles beneath them | Bring down 3 Birds |
| **Clear All of a Type** | Remove every instance of a specific element from the board | Clear all Grass tiles |
| **Fill/Spread** | Spread a material (like Jelly) across designated board cells by matching on them | Fill all Jelly cells |
| **Multi-Objective** | Complete 2-4 different objectives simultaneously within the same level | Collect 30 Gems AND Clear 10 Honey tiles |

### Level Difficulty Tiers

| Tier | Label | Avg. Moves | Avg. Attempts | Crown Reward (Royal League) |
|------|-------|------------|---------------|----------------------------|
| Normal | No label | 25-35 | ~1.2 | 1 |
| Hard | "Hard" banner | 20-28 | ~1.6 | 3 |
| Super Hard | "Super Hard" banner | 18-25 | ~2.5 | 5 |
| Extremely Hard | "Extremely Hard" banner | 15-22 | ~3.0+ | 5+ |

### Move Economy by Progression

| Level Range | Typical Move Count | Notes |
|-------------|-------------------|-------|
| 1-20 | 30-38 | Tutorial and introduction |
| 21-60 | 25-30 | Core mechanics established |
| 61-100 | 23-27 | All basic blockers introduced |
| 100+ | 18-30 (varies) | High variance; difficulty cycles in 5-10 level arcs |

---

## 8. Blocker & Game Element Types

Game elements are obstacles, containers, and special tiles that add strategic depth to levels. They are introduced progressively approximately every 10 levels.

### Tier 1 — Basic Blockers (Levels 1-30)

| Element | Layers/Hits | Clearing Method | Notes |
|---------|-------------|-----------------|-------|
| **Box** | 1-3 | Make a match adjacent to it | Multi-layered boxes require one match per layer; visually cracked as layers are removed |
| **Grass** | 2 | Make a match **on top of** the grass tile | Two matches on the tile clears the grass |
| **Cupboard** | 1 | Make a match adjacent to it | Opens to release contents |
| **Royal Egg** | 1 | Make a match adjacent to it | Single hit clears it |
| **Honey** | 1 | Make a match adjacent to it | Single hit clears; may spread to adjacent empty tiles if not cleared |
| **Chain** | 1 | Power-up hit required | Binds a tile in place; one power-up activation clears it |

### Tier 2 — Intermediate Blockers (Levels 30-80)

| Element | Layers/Hits | Clearing Method | Notes |
|---------|-------------|-----------------|-------|
| **Vase** | 2 | Make 2 matches adjacent to it | Cracks after first hit |
| **Mailbox** | Continuous | Make matches adjacent to it | Produces Mail items that must be collected; mailbox persists |
| **Potion Bottle** | 1 | Match the color matching the bottle's color | Color-specific clearing |
| **Ice** | 1-2 | Make a match adjacent to it | Encases a tile; 1 hit per layer |
| **Color Box** | 1 | Match items of the same color as the box | Color-specific clearing |
| **Honey Pot** | 2 | Make 2 matches adjacent to it | Releases honey when cleared |
| **Flowerpot** | 2 | Make 2 matches adjacent to it | Contains a flower that blooms when freed |

### Tier 3 — Advanced Blockers (Levels 80-200)

| Element | Layers/Hits | Clearing Method | Notes |
|---------|-------------|-----------------|-------|
| **Oyster** | 3 | Make 3 matches adjacent to it | Opens progressively |
| **Magic Hat** | 3 | Make 3 matches adjacent to it | Reveals contents after clearing |
| **Stone** | 3 | Power-up hits only | Cannot be cleared by regular matches |
| **Safe** | 5 | Power-up hits only | Heavy-duty blocker requiring 5 power-up activations |
| **Bush** | 5 | Make 5 matches adjacent to it | Thick vegetation that takes many hits |
| **Owl Statue** | 1 | Power-up hit | Clears with a single power-up activation |
| **Porcelain Piggy** | 1 | Power-up hit | Breaks with a single power-up |
| **Lantern** | 2 | Make 2 consecutive matches adjacent to it | Resets if matches are not consecutive |

### Tier 4 — Complex Blockers (Levels 200+)

| Element | Layers/Hits | Clearing Method | Notes |
|---------|-------------|-----------------|-------|
| **Mole Box** | 4 | Make 4 **consecutive** matches adjacent to it | Progress resets if a non-adjacent match is made |
| **Royal Capsule** | 4 | Make 4 matches adjacent to it | Contains a collectible item |
| **Igloo** | 4 | Make 4 matches adjacent to it | Generates Snowballs upon clearing |
| **Gift Box** | 4 | Make 4 matches adjacent to it | Contains Toys to collect |
| **Cauldron** | 3 | Make 3 matches adjacent to it | Brewing mechanic |
| **Soap** | 4 | Make 4 matches adjacent to it | Sliding mechanic |
| **Birdhouse** | 5 | Make 5 matches adjacent to it | Releases birds |
| **Soil** | 5 | Make 5 matches on the same tile | Must match directly on the soil |
| **Ivy** | 4 | Make 4 matches adjacent to it | Grows/spreads if not cleared |
| **Dark Honey** | 2 | Make 2 matches adjacent to it | Tougher version of Honey |

### Tier 5 — Expert Blockers (Levels 500+)

| Element | Layers/Hits | Clearing Method | Notes |
|---------|-------------|-----------------|-------|
| **Sea Mine** | 5 | Make 5 matches adjacent to it | Explosive marine obstacle |
| **Ancient Statue** | 5 | Make 5 matches adjacent to it | Monumental blocker |
| **Force Field** | 5 | Make 5 matches adjacent to it | Energy barrier |
| **Laser** | 5 | Make 5 matches adjacent to it | High-tech obstacle |
| **Crystal** | 9 | Make matches adjacent to energy box | Energy must be charged to 9 |
| **Grass Bomb** | 9 | Make 9 matches adjacent to it | Ticking time bomb on grass |
| **Jelly Bomb** | 7 | Power-up hits | Heavy jelly obstacle |
| **Clock Tower** | 6 | Power-up hits | Multi-stage tower |
| **Monument** | 4 | Power-up hits | Requires 4 power-up activations |
| **Power Cube** | 3 | Power-up hits (same cube) | Must hit the same cube 3 times |
| **Piggy Helmet** | 3 | Power-up hits | Armored piggy |
| **Giant Piggy** | 3 | Power-up hits | Large-scale piggy obstacle |

### Special Mechanic Elements

| Element | Mechanic | Description |
|---------|----------|-------------|
| **Bird** | Gravity drop | Must be brought to the bottom of the board by clearing tiles beneath it |
| **Frog** | Gravity drop | Must be brought to the bottom of the board |
| **Space Shuttle** | Gravity drop | Must be guided to the bottom |
| **Royal Bot** | Gravity + hits | 3 matches adjacent to crate, then bring to bottom |
| **Curtain** | Color collection | Collect colored items to open curtain panels |
| **Shelf** | Sub-element clearing | Break all cups on the shelf to clear it |
| **Drill** | Color collection | Collect colored items to power the drill |
| **Treasure Map** | Sub-element clearing | Break bottles (2 matches each) to reveal map |
| **Conveyor Belt** | Movement | Carries Jam Jars; rotates one position after each move |
| **Jelly** | Spread mechanic | Match on cells to spread jelly to designated areas |
| **Mushroom** | Reveal mechanic | Match adjacent to reveal ground underneath |
| **Blinds** | Reveal mechanic | Match adjacent to open blinds revealing rows/columns |
| **Vending Machine** | State machine | Multiple states; varies by interaction |
| **Magnet** | Attraction | Match adjacent to bring magnets together |
| **Wall** | Meta-blocker | Clears only when all other board elements are cleared |

---

## 9. Board Mechanics

### Board Configuration

| Property | Value |
|----------|-------|
| Maximum grid size | Up to 10 tiles long x 8 tiles wide |
| Minimum grid size | Variable (small tutorial boards) |
| Board shapes | Rectangular, square, diamond, H-shaped, L-shaped, irregular/custom |
| Tile spacing | Uniform grid with no gaps between adjacent tiles |
| Disconnected sections | Some levels feature separate board regions |

### Special Board Features

| Feature | Description |
|---------|-------------|
| **Portals** | Entrance/exit pairs; when a tile reaches an entrance portal, it disappears and reappears at the corresponding exit portal. Every entrance has exactly one corresponding exit. |
| **Conveyor Belts** | Directional tracks that move tiles one position in the indicated direction after each player move. Carry Jam Jars that require 2 adjacent matches each to clear. Belt disappears when all Jam Jars are broken. |
| **Ice Borders** | Frozen edges that expand or contract; cleared by making matches adjacent to them |
| **Purple Borders** | Immovable, indestructible walls that permanently restrict board space and tile movement |
| **Metal Plates** | Reveal rows/columns when cleared with power-up hits |
| **Locked Tiles** | Tiles bound by Chains that cannot be moved until the Chain is destroyed |
| **Spawn Points** | Top-of-column entry points where new tiles appear after gravity resolution |
| **Column Blockers** | Some columns may be partially or fully blocked, preventing tile flow |

### Gravity System

- Tiles always fall **downward** to fill empty spaces.
- Multiple empty spaces cause tiles to fall through all of them in sequence.
- New tiles spawn from the top of each open column.
- Some levels feature modified gravity with portals redirecting tile flow.

---

## 10. King's Nightmare Mode

### Overview

King's Nightmare levels are **bonus levels** that appear between regular levels at specific intervals. They do not count toward normal level progression.

| Property | Value |
|----------|-------|
| Frequency | Every 50 levels (appears at the midpoint of each area, between levels X50 and X51) |
| Type | Time-based challenge (not move-based) |
| Theme | King Robert is depicted in a dangerous scenario (filling water, fire, etc.) |
| Objective | Complete the puzzle within the time limit to "save" King Robert |
| Boosters | **No** in-game boosters or pre-game boosters allowed |
| Butler's Gift | Does **not** apply |
| Skip option | Players may skip the nightmare if they choose |
| Failure penalty | None — no life lost; can retry or skip |

### Rewards

| Outcome | Reward |
|---------|--------|
| Successful completion | 50 coins + 15-minute timed boosts (e.g., Infinite Lives, boosters) |
| Failed/Skipped | No reward; no penalty |

### Scenario Examples

- King Robert is trapped in a glass box filling with water — complete the board to get a hammer and break him out.
- King Robert is on a platform above lava — clear tiles to build a bridge.
- King Robert is locked in a cage — clear objectives to find the key.

---

## 11. Area Progression & Decoration

### Area System

| Property | Value |
|----------|-------|
| Total areas | 106+ (as of late 2025; continuously expanding) |
| Levels per area | 10-100 (varies by area) |
| Stars per level | 1 (earned upon first completion) |
| Star currency | Cannot be purchased — only earned by beating levels |
| Tasks per area | 5-15 decoration tasks per area |

### Decoration Tasks

Each area contains a series of **tasks** representing different decorations, furnishings, or repairs. Each task costs **1 star** to complete. Tasks are completed sequentially within an area.

### Task Flow

```
1. Player completes a level → earns 1 star
2. Star is automatically available for the current area's next task
3. Player taps the task to spend the star and trigger a decoration animation
4. New visual element appears in the area scene
5. When all tasks in an area are complete → Area Chest is awarded
6. Next area unlocks
```

### Area Chest Rewards

| Contents | Description |
|----------|-------------|
| Coins | Variable amount based on progression |
| Boosters | Random selection of pre-game and in-game boosters |
| Cards | Royal Collection cards (cosmetic card collection system) |

### Example Areas (Early Game)

| Area # | Name | Theme |
|--------|------|-------|
| 1 | King's Castle | Main hall restoration |
| 2 | Throne Room | Royal throne and decor |
| 3 | Dining Room | Banquet hall furnishing |
| 4 | Garden | Outdoor landscaping |
| 5 | Kitchen | Castle kitchen renovation |
| 6 | Library | Book collections and reading room |
| 7 | Bedroom | Royal chambers |
| 8 | Bathroom | Royal bath renovation |
| 9 | Tree House | Exterior magical treehouse |
| 10 | Beach House | Coastal property decoration |

### Area Scene Presentation

- Each area is depicted as a **detailed illustrated scene** in a vertical scrolling view.
- Decoration tasks highlight specific elements of the scene (e.g., a fountain, a bench, a lamp).
- Completed tasks trigger a short **animation** showing the decoration being placed/built.
- Players can revisit completed areas to view their decorated rooms.

---

## 12. Economy System

### Coins

Coins are the primary in-game currency.

| Property | Value |
|----------|-------|
| Starting coins | ~100 (given during tutorial) |
| Earn from level completion | Small coin reward (varies by difficulty) |
| Earn from Area Chests | Variable (increases with progression) |
| Earn from King's Nightmare | 50 coins per successful completion |
| Earn from events | Variable by event type and placement |
| Extra 5 moves (continue) | 900 coins |
| Second continue | 1,900 coins |

### Coin Sinks

| Usage | Cost |
|-------|------|
| Buy 5 extra moves (post-failure continue) | 900 coins |
| Buy additional continues | 1,900 coins |
| Buy extra lives | Variable |
| Buy boosters | Variable |

### In-App Purchase Bundles

| Bundle Tier | Approximate Price (USD) | Typical Contents |
|-------------|------------------------|------------------|
| Starter Pack | $1.99-$2.99 | Coins + basic boosters |
| Mid-tier Bundle | $4.99-$7.99 | Coins + multiple boosters + limited lives |
| Premium Bundle | $9.99-$14.99 | Large coin stack + premium boosters + unlimited lives (timed) |
| Prince's Treasure | $4.99-$9.99 | Special limited-time offer with coins, rockets, TNTs |
| Queen's Treasure | $9.99-$19.99 | Enhanced limited-time bundle |
| King's Treasure | $19.99-$49.99 | Premium limited-time bundle |
| Supreme Treasure | $49.99-$99.99 | Maximum value bundle |

### Monetization Strategy

- **No forced ads** — Royal Match does not show mandatory advertisements.
- Revenue is entirely driven by **IAP** (in-app purchases).
- Limited-time offers create urgency through countdown timers.
- Bundles are offered contextually (e.g., after a level failure, before a hard level).

---

## 13. Lives System

| Property | Value |
|----------|-------|
| Maximum lives | 5 |
| Life regeneration rate | 1 life every **30 minutes** |
| Life lost on | Failing a level (running out of moves without completing objectives) |
| Life NOT lost on | Quitting a level before the final move; winning a level |
| Infinite lives (timed) | Available through events, King's Nightmare rewards, IAP, or Royal Pass |
| Lightning Rush bonus | 1 hour of unlimited lives during the event |

### Life Refill Methods

| Method | Details |
|--------|---------|
| Wait | 30 minutes per life; caps at 5 |
| Request from team | Team members can send lives to each other |
| Event rewards | Various events grant lives or unlimited lives |
| IAP | Purchase life refills or timed unlimited lives |
| King's Nightmare | 15-minute unlimited lives on successful completion |

---

## 14. Boosters

### Pre-Level Boosters

Selected **before starting a level** on the level-start screen. When selected, the corresponding power-up replaces a random tile on the starting board.

| Booster | Effect on Board | Unlock Level |
|---------|----------------|--------------|
| **Rocket** | Places 1 Rocket on the starting board | Early (tutorial) |
| **TNT** | Places 1 TNT on the starting board | ~Level 10 |
| **Light Ball** | Places 1 Light Ball on the starting board | ~Level 20 |

### In-Game Boosters

Used **during gameplay** without consuming a move. Activated by tapping the booster icon in the bottom toolbar, then tapping the target tile.

| Booster | Effect | Unlock Level |
|---------|--------|--------------|
| **Royal Hammer** | Clears **1 tile** or removes **1 layer** from any game element at the tapped location | ~Level 7 |
| **Arrow** | Clears the **entire row** of the tapped tile, removing 1 layer from all game elements in that row | ~Level 15 |
| **Cannon** | Clears the **entire column** of the tapped tile, removing 1 layer from all game elements in that column | ~Level 25 |
| **Jester Hat** | **Shuffles** all tiles on the board randomly without consuming a move | ~Level 35 |

### Booster Acquisition

| Source | Details |
|--------|---------|
| Area Chests | Random boosters on area completion |
| Event rewards | Various events award specific boosters |
| Daily rewards | Login streak and daily challenge rewards |
| Royal Pass | Both free and premium tracks include boosters |
| IAP | Direct purchase through shop or bundle offers |
| Butler's Gift | Free boosters for consecutive wins (see Section 15) |

---

## 15. Butler's Gift

Butler's Gift is a **win-streak reward system** that becomes active at **Level 32**.

### Streak Rewards

| Consecutive Wins | Boosters at Level Start |
|------------------|------------------------|
| 1 win | 1 Propeller + 1 Rocket |
| 2 wins | 1 Propeller + 1 Rocket + 1 TNT |
| 3+ wins (max) | 1 Propeller + 1 Rocket + 1 TNT + 1 Light Ball |

### Mechanics

| Property | Value |
|----------|-------|
| Unlock requirement | Reach Level 32 |
| Activation | Automatic on consecutive level completions |
| Maximum level | 3 consecutive wins (all 4 power-ups) |
| Streak maintenance | Continues at max level as long as no failure occurs |
| Streak reset | Failing any level resets Butler's Gift to 0 |
| Presentation | Butler Winston appears with a tray of boosters before the level |

---

## 16. Team Features

### Team Basics

| Property | Value |
|----------|-------|
| Unlock requirement | Level 23 |
| Maximum team size | 50 players |
| Team types | Open (anyone can join) or Closed (leader/co-leader approval required) |
| Roles | Leader, Co-Leader, Elder, Member |
| Team Score | Sum of all members' levels + crowns collected in Royal League |

### Team Chat

- In-game text chat within the team.
- Players can send life requests and gifts to teammates.
- Animated emoji and sticker support.

### Team Events

| Event | Format | Duration | Players | Description |
|-------|--------|----------|---------|-------------|
| **Team Battle** | 20 teams compete | ~3 days | All team members | Earn shields by completing levels; top 5 teams rewarded |
| **Team Tournament** | 20 teams compete | ~3 days | All team members | Earn tokens converted to lances; top 5 teams rewarded |
| **Team Treasure** | Cooperative | Monday 5pm - Friday 5pm | All team members | Collect ship wheels across 3 stages to reach goals; tiered rewards |

Team Battles and Team Tournaments **alternate** on Fridays.

---

## 17. Events & Tournaments

Royal Match features a rich rotation of solo and competitive events. Events are accessed through the main play button and event banners.

### Solo Progression Events

| Event | Steps | Collectible | Duration | Unlock Level | Description |
|-------|-------|-------------|----------|-------------|-------------|
| **Balloon Rise** | 10 | Cookies | Time-limited | ~Level 30 | Collect cookies by beating levels; claim rewards per step |
| **Propeller Madness** | Multi-step | Propellers | Time-limited | ~Level 40 | Create Propellers during levels to progress |
| **Book of Treasure** | 25 | Books (red items) | Time-limited | ~Level 50 | Destroy red match items to progress through 25 reward tiers |
| **Pinata Party** | 3 | Candies | Time-limited | Level 39+ | Collect candies by beating levels |
| **Hidden Temple** | Multi-step | Varies | Time-limited | Mid-game | Unique boards with per-step rewards |
| **Magic Cauldron** | Multi-step | Formulas | Time-limited | Mid-game | Use formulas to progress through stages |
| **Ocean Odyssey** | Multi-stage | Varies | Time-limited | Mid-game | Clear different objects per stage |
| **Puzzle Break** | Multi-step | Varies | Time-limited | Mid-game | Unique boards per step |
| **Mission Pursuit** | 5 stages | Varies | Time-limited | Mid-game | Different missions per stage |
| **Mission Control** | 4 stages | Varies | Time-limited | Mid-game | Stage-specific missions |
| **Merge Smith** | Multi-step | Anvils | Time-limited | Mid-game | Collect anvils, merge items to discover new objects |

### Competitive Events

| Event | Players | Format | Duration | Description |
|-------|---------|--------|----------|-------------|
| **Lightning Rush** | 5 | Collect lightning bolts | 1 hour | Unlimited lives for 1 hour; most bolts wins |
| **Sky Race** | 5 | Race to complete 15 levels | Time-limited | Top 3 ranked by speed; rewards by placement |
| **King's Cup** | 50 | Collect cups | Time-limited | Large field competition for cups |
| **Weekly Contest** | 10 | Weekly progress race | 1 week | Compete based on weekly level progression |
| **Archery Arena** | 50 | Collect items | Time-limited | Large field competitive collection |
| **Propeller Rush** | 5 | Race format | Time-limited | Speed-based Propeller creation competition |
| **Robot Rivals** | 2 | Head-to-head | Weekend events | 1v1 competition (introduced October 2025) |
| **Champions Clash** | 8 | Bracket elimination | 3 rounds | 8-player elimination tournament |
| **Ancient Adventure** | Multi | First-try levels | Time-limited | Beat levels on first attempt; failure disqualifies |

### Cooperative Events

| Event | Players | Format | Duration | Description |
|-------|---------|--------|----------|-------------|
| **Dragon Nest** | Group | Raise 4 dragons | Time-limited | Collaborative dragon-raising event |
| **Train Journey** | 4 partners | Build rails | Time-limited | Collect trains with 3 partners to build rail tracks |

### Challenge Events

| Event | Format | Description |
|-------|--------|-------------|
| **Lava Quest** | 7 consecutive first-try wins | Must beat 7 levels without failing; Level 66+ required. Grand prize of 10,000 coins shared among winners. |
| **Space Mission** | Consecutive first-try wins | Beat consecutive levels before competitors |

---

## 18. Royal Pass (Season Pass)

The Royal Pass is a monthly battle pass system.

| Property | Value |
|----------|-------|
| Duration | ~1 month (start to end of month) |
| Total tiers | 30 |
| Free track rewards | 30 rewards |
| Premium track rewards | 50 additional rewards (80 total) |
| Progression | Collect keys by completing levels |
| Premium activation | One-time purchase per season |

### Reward Distribution

| Tier Range | Free Track Focus | Premium Track Focus |
|------------|-----------------|---------------------|
| Tiers 1-10 (Early) | Gameplay boosters (Rockets, TNTs) | Extended Infinite Lives, premium chests |
| Tiers 11-20 (Mid) | Core resources (coins, lives) | Rare boosters, card packs |
| Tiers 21-30 (Late) | Milestone rewards (TNT, Gift Box) | Exclusive chests, large coin rewards, cosmetic items |

---

## 19. Royal League

The Royal League is the **endgame competitive mode** for players who have completed all available levels and area tasks.

| Property | Value |
|----------|-------|
| Unlock requirement | Complete all available levels |
| Format | Global leaderboard competition |
| Currency | Crowns |
| Crown rewards | Normal levels = 1 crown, Hard = 3 crowns, Super Hard = 5 crowns |
| Double time | Periodically active; doubles crown rewards |
| Seasons | Regular competitive seasons with rank resets |

### League Tiers

Players compete in tiered leagues with promotion and relegation based on crown count during each season.

---

## 20. Scoring & Difficulty System

### Scoring

Royal Match uses a **star-based progression system** rather than a traditional numeric score for level progression.

| Metric | Value |
|--------|-------|
| Stars per level completion | 1 (always; no variable star ratings) |
| End-of-level bonus | Remaining moves converted to power-ups → coins |
| Coin bonus per leftover move | Variable (depends on power-up type generated) |

### Difficulty Curve Design

| Design Element | Implementation |
|----------------|----------------|
| Cycle length | 5-10 levels per difficulty cycle |
| Cycle structure | Easy entry level → gradual ramp → peak difficulty → relief level |
| New mechanic introduction | Introduced at **easier** difficulty first, then compounded with existing mechanics |
| Hard level placement | Approximately every 10 levels (Levels 39, 45, 49, 55, 65, 75, 85, 95 in first 100) |
| Super Hard peaks | Approximately every 10 levels offset (Levels 59, 69, 79, 89, 99 in first 100) |
| Decision density increase | ~20% increase from Level 1 to Level 100 |

### Move Count Balancing

The game carefully calibrates move counts against objective difficulty:

- **Generous moves** (30+): Tutorial levels, new mechanic introductions, post-hard relief levels.
- **Moderate moves** (22-29): Standard gameplay, balanced challenge.
- **Tight moves** (15-21): Hard/Super Hard levels; require efficient power-up usage and planning.

---

## 21. UI Layout & Screen Flow

### Home Screen (Map View)

```
┌─────────────────────────────┐
│  [Coins] [Lives]  [Settings]│  ← Top bar: currency, lives, settings
│                             │
│  ┌───────────────────────┐  │
│  │                       │  │
│  │   AREA DECORATION     │  │  ← Current area scene (scrollable)
│  │   SCENE               │  │
│  │                       │  │
│  │   [Task indicators]   │  │  ← Highlighted pending tasks
│  │                       │  │
│  └───────────────────────┘  │
│                             │
│  [Event Banners]            │  ← Active event icons/banners
│                             │
│  ┌───────────────────────┐  │
│  │      ▶ PLAY           │  │  ← Large central play button
│  └───────────────────────┘  │
│                             │
│  [Team] [Events] [Shop]    │  ← Bottom navigation bar
└─────────────────────────────┘
```

### Level Start Screen

```
┌─────────────────────────────┐
│  Level [Number]   [Difficulty]│
│                             │
│  OBJECTIVES:                │
│  [Icon] x [Count]          │  ← Required items/blockers to clear
│  [Icon] x [Count]          │
│                             │
│  Moves: [Number]            │
│                             │
│  PRE-LEVEL BOOSTERS:        │
│  [Rocket ○] [TNT ○] [LB ○] │  ← Toggle on/off; shows inventory count
│                             │
│  ┌───────────────────────┐  │
│  │      ▶ START          │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

### In-Game Screen

```
┌─────────────────────────────┐
│ [Obj1] [Obj2]  Moves: [##] │  ← Objective counters + move counter
│ ┌─[King Portrait]────────┐  │  ← King Robert's animated portrait
│ │                         │ │
│ │                         │ │
│ │      GAME BOARD         │ │  ← Match-3 grid (variable size)
│ │      (variable grid)    │ │
│ │                         │ │
│ │                         │ │
│ └─────────────────────────┘ │
│                             │
│ [Hammer][Arrow][Cannon][Hat]│  ← In-game booster toolbar
│ [Coin counter]              │  ← Current coin balance
└─────────────────────────────┘
```

### Level Complete Screen

```
┌─────────────────────────────┐
│                             │
│        ★ LEVEL COMPLETE ★   │
│                             │
│  [King Robert thumbs up]    │  ← Celebratory King animation
│                             │
│  Bonus coins earned: [##]   │  ← From leftover moves
│                             │
│  ┌───────────────────────┐  │
│  │      CONTINUE         │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

### Level Failed Screen

```
┌─────────────────────────────┐
│                             │
│     OUT OF MOVES!           │
│                             │
│  [Butler Winston puzzled]   │  ← Butler's puzzled expression
│                             │
│  +5 Moves: 900 coins       │  ← Continue option
│                             │
│  [Continue] [Give Up]       │
└─────────────────────────────┘
```

### Screen Flow

```
App Launch → Home/Map Screen
  ├── ▶ Play → Level Start Screen → In-Game → Win/Lose
  │     ├── Win → Level Complete → Star earned → Area Task (auto or manual)
  │     └── Lose → Failed Screen → Continue (coins) / Retry / Home
  ├── Area Scene → Task List → Spend Stars → Decoration Animation
  ├── Team → Team Chat / Team Events
  ├── Events → Event List → Event Detail → Play (through main levels)
  ├── Shop → IAP Bundles / Coin Packages
  └── Settings → Sound, Music, Notifications, Account
```

### King Robert's Portrait Reactions

King Robert's animated portrait is visible during gameplay and **reacts to the game state**:

| Game State | King's Reaction |
|------------|----------------|
| Normal play | Neutral/smiling, watching the board |
| Good match/cascade | Happy, encouraging expression |
| Power-up combo | Excited, celebratory |
| Low moves remaining | Nervous, worried expression |
| About to fail | Panicked, distressed |
| Level complete | Thumbs up with both hands, beaming |
| Level failed | Sad/disappointed (transitions to Butler Winston) |

---

## 22. Audio Design

### Music

| Context | Style | Description |
|---------|-------|-------------|
| Home/Map screen | Orchestral, regal | Warm, inviting royal theme with strings and light percussion |
| In-game (normal) | Upbeat, casual | Light melodic loop; non-intrusive; maintains focus |
| In-game (low moves) | Tense | Tempo increase, minor key shift to create urgency |
| Level complete | Fanfare | Short triumphant brass and string celebration |
| Level failed | Deflated | Descending tone, gentle disappointment cue |
| King's Nightmare | Dramatic | Urgent, time-pressure theme with ticking elements |
| Area completion | Grand fanfare | Extended celebratory orchestral piece |
| Event themes | Varied | Each event type has its own musical identity |

### Sound Effects

| Action | Sound Character |
|--------|----------------|
| Tile swap | Soft click/whoosh |
| Match-3 | Bright chime (pitch varies by match size) |
| Match-4 (power-up creation) | Ascending chime + magical sparkle |
| Match-5 (Light Ball creation) | Grand ascending tone + shimmering effect |
| Cascade chain | Escalating pitch sequence (each cascade step higher) |
| Rocket activation | Whoosh + explosion |
| TNT activation | Deep boom + rumble |
| Propeller activation | Whirring + pop at destination |
| Light Ball activation | Sweeping magical wave sound |
| Power-up combination | Enhanced explosion + layered magical effects |
| Blocker break (1 layer) | Crack/crumble |
| Blocker fully cleared | Satisfying shatter + sparkle |
| Objective item collected | Ding + counter increment sound |
| Move counter decrement | Subtle tick |
| Star earned | Bright sting + sparkle |
| Coin collected | Metallic clink |
| Booster used | Distinct sound per booster type |
| Board shuffle (Jester Hat) | Rapid shuffling/whoosh cascade |
| King's reactions | Subtle vocal cues (happy hum, nervous gulp) |
| UI button tap | Clean click |

### Audio Settings

| Setting | Options |
|---------|---------|
| Music | On / Off (toggle) |
| Sound Effects | On / Off (toggle) |
| Haptics | On / Off (toggle) |
| Volume | System volume controls |

---

## 23. Characters & Narrative

### Main Characters

| Character | Role | Appearance | Function |
|-----------|------|------------|----------|
| **King Robert** | Protagonist | Friendly king with golden crown, red robe, warm smile | Appears in portrait during gameplay; reacts to game state; stars in King's Nightmare scenarios; drives area decoration narrative |
| **Butler Winston** | Supporting | Formal butler in tuxedo with white gloves | Appears on level failure; delivers Butler's Gift rewards; occasional narrative interactions |

### Narrative Structure

- **Area Introductions**: Brief scene showing the state of disrepair before renovation begins.
- **Task Completion**: King Robert comments on or reacts to each decoration placed.
- **Area Completion**: Celebratory scene with King Robert admiring the fully restored area.
- **King's Nightmare Interludes**: Story vignettes where King Robert faces humorous peril.
- **No dialogue-heavy cutscenes**: Narrative is conveyed through visual storytelling, short text captions, and character animations.

### Tone

- **Light-hearted and family-friendly**: No violence, conflict, or negative themes.
- **Cozy and aspirational**: The renovation theme creates a sense of progress and home-building.
- **Humorous**: King's Nightmare scenarios are played for comedic effect despite the "danger."

---

## Appendix A: Complete Power-Up Quick Reference

| Power-Up | Creation Pattern | Activation Effect |
|----------|-----------------|-------------------|
| Horizontal Rocket | 4 in horizontal line | Clears entire row |
| Vertical Rocket | 4 in vertical line | Clears entire column |
| Propeller | 4 in 2x2 square | Clears "+" neighbors, then flies to random target |
| TNT | 5 in L or T shape | Clears 2-tile radius (5x5 area) |
| Light Ball | 5 in straight line | Clears all of one color (swapped or most prevalent) |

## Appendix B: Combination Effects Quick Reference

| Combo | Result |
|-------|--------|
| Rocket + Rocket | Full row + full column |
| Rocket + TNT | 3 rows + 3 columns |
| Rocket + Propeller | Propeller carries Rocket to random target |
| TNT + TNT | 4-tile radius (9x9 area) |
| TNT + Propeller | Propeller carries TNT to random target |
| Propeller + Propeller | 3 Propellers to 3 random targets |
| Light Ball + Rocket | All of most common color become Rockets, all activate |
| Light Ball + TNT | All of most common color become TNTs, all activate |
| Light Ball + Propeller | All of most common color become Propellers, all activate |
| Light Ball + Light Ball | Clears entire board + 1 layer from all game elements |

## Appendix C: Event Unlock Levels

| Event | Minimum Level |
|-------|---------------|
| Team Features | 23 |
| Butler's Gift | 32 |
| Pinata Party | 39 |
| Propeller Madness | ~40 |
| Book of Treasure | ~50 |
| Lava Quest | 66 |
| Royal League | All levels completed |

## Appendix D: Key Numeric Constants

| Constant | Value |
|----------|-------|
| Max lives | 5 |
| Life regeneration | 30 minutes |
| Match items (colors) | 5 |
| Base power-up types | 4 (Rocket, Propeller, TNT, Light Ball) |
| In-game booster types | 4 (Hammer, Arrow, Cannon, Jester Hat) |
| Pre-level booster types | 3 (Rocket, TNT, Light Ball) |
| Power-up combinations | 10 unique combos |
| Max team size | 50 players |
| Continue cost (5 moves) | 900 coins |
| Second continue cost | 1,900 coins |
| King's Nightmare reward | 50 coins |
| King's Nightmare frequency | Every 50 levels |
| Royal Pass tiers | 30 |
| Butler's Gift max streak | 3 (all 4 power-ups) |
| Lava Quest levels | 7 consecutive first-try wins |
| Lava Quest grand prize | 10,000 coins (shared) |
| Lightning Rush duration | 1 hour |
| Sky Race levels | 15 |
| King's Cup competitors | 50 |
| Weekly Contest competitors | 10 |
| Team Battle/Tournament teams | 20 |
