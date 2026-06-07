# Plants vs. Zombies — Complete Game Specification

> A comprehensive specification for faithfully recreating the original Plants vs. Zombies (PopCap Games, 2009 PC version). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Game Mechanics](#3-core-game-mechanics)
4. [Sun Economy System](#4-sun-economy-system)
5. [The Lawn Grid](#5-the-lawn-grid)
6. [Planting System](#6-planting-system)
7. [All Plants — Complete Stats](#7-all-plants--complete-stats)
8. [All Zombies — Complete Stats](#8-all-zombies--complete-stats)
9. [Wave & Spawning System](#9-wave--spawning-system)
10. [Projectile & Combat System](#10-projectile--combat-system)
11. [Collision & Interaction Rules](#11-collision--interaction-rules)
12. [Level Progression — All 50 Levels](#12-level-progression--all-50-levels)
13. [World-Specific Mechanics](#13-world-specific-mechanics)
14. [Special Level Types](#14-special-level-types)
15. [Game Modes](#15-game-modes)
16. [Economy & Shop System](#16-economy--shop-system)
17. [UI Layout & Screen Flow](#17-ui-layout--screen-flow)
18. [Audio Design](#18-audio-design)
19. [Animation System](#19-animation-system)
20. [Zen Garden](#20-zen-garden)
21. [Achievements & Unlocks](#21-achievements--unlocks)

---

## 1. Game Overview

- **Genre**: Tower defense
- **Perspective**: 2D side-view with top-down grid placement
- **Input**: Mouse-only (point and click). No keyboard gameplay controls.
- **Objective**: Prevent zombies from crossing the lawn and entering the player's house by strategically placing plants that attack, block, or produce resources.
- **Lose Condition**: Any zombie reaches the left edge of any row after the lawnmower for that row has already been used.
- **Win Condition**: Survive all waves in a level. The last zombie killed drops a reward (plant seed packet, item, or money bag).

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 800 × 600 pixels |
| Display mode | Windowed or Fullscreen |
| Frame rate target | 100 FPS (internal logic at ~100 ticks/second) |
| Animation format | Reanim (.reanim XML) — sprite-part transforms per frame |

### Coordinate System

- Origin (0, 0) at top-left of screen.
- The lawn grid begins approximately at pixel (40, 80) and extends to about (775, 560) on a standard 5-row layout.
- Each grid cell is approximately **80 × 96 pixels** (width × height).

### Game Loop

```
1. Process input (mouse clicks, hover state)
2. Update sun timers (sky drops, plant production)
3. Update plant recharge timers
4. Update all plant entities (attack, animate, produce)
5. Update all zombie entities (move, eat, special actions)
6. Update all projectiles (move, check collisions)
7. Check lawnmower triggers
8. Check wave advancement conditions
9. Check win/lose conditions
10. Render (background → plants → zombies → projectiles → UI → particles)
```

---

## 3. Core Game Mechanics

### Lawnmowers / Lane Cleaners

- Each row starts with **one lawnmower** at the far-left edge.
- **Trigger**: When any zombie passes the last column (reaches the house-side edge), the lawnmower activates.
- **Behavior**: Charges forward at high speed, instantly killing every zombie in that lane.
- **Single-use**: After firing, the lawnmower is gone for the rest of the level.
- **Second breach**: If another zombie reaches the end of a lane with no lawnmower, the player **loses**.
- **End-of-level bonus**: Each unused lawnmower awards **$50**.
- **Variants by world**:
  - Day/Night: Lawnmowers (ground lanes)
  - Pool/Fog: Lawnmowers (ground lanes) + Pool Cleaners (water lanes)
  - Roof: Roof Cleaners (all lanes)

### Shovel

- **Unlocked at**: Level 1-4
- **Function**: Removes any planted entity from the grid instantly.
- **Sun refund**: None (0 sun returned).
- **Cooldown**: None — can be used repeatedly without delay.
- **Usage**: Click shovel icon → click target plant on grid.

### Seed Tray

- Horizontal bar at the top-left of the screen.
- Contains the player's chosen plant seed packets.
- **Starting slots**: 6
- **Maximum slots**: 10 (additional slots purchased from Crazy Dave's shop)
- Each slot displays: plant icon, sun cost number, and a **grayscale recharge overlay** that fills from bottom to top as the cooldown completes.
- A fully recharged and affordable packet is **bright and clickable**. An unavailable packet (recharging or too expensive) is **dimmed/grayed**.

---

## 4. Sun Economy System

### Sun Properties

| Property | Value |
|----------|-------|
| Starting sun per level | 50 |
| Value of one sun orb | 25 |
| Sun lifetime before disappearing | ~8 seconds (10 seconds for sky sun) |
| Sun collection | Click to collect; flies to sun counter |

### Sun Sources

| Source | Amount | Interval | Conditions |
|--------|--------|----------|------------|
| Sky (falling sun) | 25 | Every ~10 seconds | Day levels only (Worlds 1, 3, 5) |
| Sunflower | 25 | Every ~24 seconds (first at ~7s after planting) | Always active |
| Twin Sunflower | 50 (two 25-drops) | Every ~24 seconds | Always active |
| Sun-shroom (small) | 15 | Every ~24 seconds | First ~120 seconds after planting |
| Sun-shroom (grown) | 25 | Every ~24 seconds | After ~120 seconds growth |
| Gold Sunflower (2nd playthrough) | 50-150 | Varies | Rare sun drops |

### Sky Sun Behavior

- Sun falls from random horizontal positions within the playable lawn area.
- Falls at a gentle constant speed (~1.5 seconds to land).
- Lands on the ground and persists for ~10 seconds before fading.
- Not produced during Night or Fog levels (Worlds 2, 4).

---

## 5. The Lawn Grid

### Grid Dimensions by World

| World | Rows | Columns | Water Lanes | Notes |
|-------|------|---------|-------------|-------|
| Day (World 1) | 5 | 9 | 0 | Standard grass lawn |
| Night (World 2) | 5 | 9 | 0 | Graves spawn in rightmost columns |
| Pool (World 3) | 6 | 9 | 2 (rows 3-4) | Water requires Lily Pad for planting |
| Fog (World 4) | 6 | 9 | 2 (rows 3-4) | Water + fog covering right ~4 columns |
| Roof (World 5) | 5 | 9 | 0 | Sloped tiles (cols 1-4); flat tiles (cols 5-9); Flower Pot required |

### Tile Types

| Tile Type | Can Plant Directly | Required Platform | Found In |
|-----------|-------------------|-------------------|----------|
| Grass | Yes | None | Day, Night |
| Water | No | Lily Pad | Pool, Fog |
| Roof (flat) | No | Flower Pot | Roof |
| Roof (sloped) | No | Flower Pot | Roof |
| Crater (Doom-shroom) | No | Nothing (unusable ~3 min) | Any after Doom-shroom |
| Ice Trail (Zomboni) | Yes (zombies slide) | None | Pool, Fog |
| Grave | No (occupied) | Grave Buster to clear | Night, Fog |

### Planting Rules

- **One plant per tile** (ground-level).
- **Pumpkin** can be placed **over** any existing plant (acts as armor shell).
- **Cob Cannon** occupies **two adjacent horizontal tiles** (replaces two Kernel-pults).
- **Lily Pad** is placed on water; another plant is then placed on top of the Lily Pad.
- **Flower Pot** is placed on roof; another plant is placed on top of the Flower Pot.
- **Coffee Bean** is placed on a sleeping mushroom; it is consumed instantly.
- **Upgrade plants** (Gatling Pea, Twin Sunflower, etc.) must be placed **on top of** their prerequisite plant.

---

## 6. Planting System

### Recharge Categories

| Category | Cooldown Duration | Initial Wait at Level Start |
|----------|------------------|-----------------------------|
| Fast | 7.5 seconds | 0 seconds (ready immediately) |
| Slow | 30 seconds | ~15-20 seconds |
| Very Slow | 50 seconds | ~35 seconds |

### Planting Flow

1. Player clicks a seed packet in the tray (must be recharged and affordable).
2. A "ghost" version of the plant follows the cursor.
3. Player clicks a valid grid tile to place the plant.
4. Sun is deducted immediately upon placement.
5. The seed packet enters cooldown (grayscale overlay begins).
6. The plant appears on the tile and begins its idle animation.

### Plant Selection Screen ("Choose Your Seeds")

- Appears before each level starting from Level 1-7 (when the player has more plants than tray slots).
- **Left panel**: Grid of all unlocked plant seed packets.
- **Top bar**: Current seed tray showing selected plants.
- **Right panel**: Zombie preview — shows portraits of zombie types that will appear in the upcoming level (but not exact quantities).
- **"Let's Rock!" button**: Confirms selection and starts the level.
- **Imitater**: If purchased, appears as a gray card. Clicking it opens a second selection screen to choose which plant to copy.

---

## 7. All Plants — Complete Stats

### Damage Reference

- **1 normal damage point (ndp)** = 20 HP of damage (one normal pea).
- Internal HP values are used below. A basic zombie has 270 HP total.
- **Instant-kill threshold** = 1800 damage.

### 7.1 Day Plants (World 1)

#### Peashooter

| Property | Value |
|----------|-------|
| Sun cost | 100 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per pea |
| Fire rate | 1 pea every 1.425 seconds |
| Range | Entire lane (straight line) |
| Unlocked | Level 1-1 (starter plant) |

#### Sunflower

| Property | Value |
|----------|-------|
| Sun cost | 50 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | None |
| Production | 25 sun every ~24 seconds |
| First sun delay | ~7 seconds after planting |
| Unlocked | Level 1-1 |

#### Cherry Bomb

| Property | Value |
|----------|-------|
| Sun cost | 150 |
| Recharge | Very Slow (50s) |
| Health | N/A (instant use, single use) |
| Damage | 1800 (instant kill to all standard zombies) |
| Area | 3×3 tiles centered on placement |
| Animation | 1.2-second expansion before detonation |
| Visual | "POWIE!!" text cloud on explosion |
| Unlocked | Level 1-2 |

#### Wall-nut

| Property | Value |
|----------|-------|
| Sun cost | 50 |
| Recharge | Slow (30s) |
| Health | 4000 HP |
| Damage | None (blocker) |
| Visual states | 3 damage stages: full → cracked → severely cracked |
| Crack thresholds | Stage 2 at ~2667 HP remaining; Stage 3 at ~1333 HP remaining |
| Unlocked | Level 1-3 |

#### Potato Mine

| Property | Value |
|----------|-------|
| Sun cost | 25 |
| Recharge | Slow (30s) |
| Health | 300 HP (while unarmed, can be eaten) |
| Damage | 1800 (instant kill) |
| Area | Single tile (1×1) |
| Arming time | ~15 seconds after planting |
| State | Unarmed (brown lump, vulnerable) → Armed (pops up, glowing eyes) |
| Unlocked | Level 1-5 |

#### Snow Pea

| Property | Value |
|----------|-------|
| Sun cost | 175 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per frozen pea |
| Fire rate | 1 pea every 1.425 seconds |
| Range | Entire lane |
| Special | Slows zombies to 50% movement speed; visual ice/blue pea |
| Interaction | Frozen peas passing through Torchwood revert to normal peas (lose slow) |
| Unlocked | Level 1-6 |

#### Chomper

| Property | Value |
|----------|-------|
| Sun cost | 150 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | Instant kill (one zombie, any HP) |
| Range | 1 tile directly ahead |
| Chewing time | ~42 seconds (cannot attack while chewing) |
| Unlocked | Level 1-7 |

#### Repeater

| Property | Value |
|----------|-------|
| Sun cost | 200 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per pea × 2 peas per volley |
| Fire rate | 2 peas every 1.425 seconds |
| Range | Entire lane |
| Unlocked | Level 1-8 |

### 7.2 Night Plants — Mushrooms (World 2)

All mushrooms are **nocturnal**: they are awake at Night and Fog levels but **fall asleep** during Day, Pool, and Roof levels. Use **Coffee Bean** to wake them during daytime.

#### Puff-shroom

| Property | Value |
|----------|-------|
| Sun cost | 0 (free) |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per spore |
| Fire rate | 1 spore every 1.425 seconds |
| Range | ~3 tiles |
| Lifespan | Disappears after ~4 minutes |
| Nocturnal | Yes |
| Unlocked | Level 1-10 |

#### Sun-shroom

| Property | Value |
|----------|-------|
| Sun cost | 25 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Production (small) | 15 sun every ~24 seconds |
| Growth time | ~120 seconds |
| Production (grown) | 25 sun every ~24 seconds |
| Nocturnal | Yes |
| Unlocked | Level 2-1 |

#### Fume-shroom

| Property | Value |
|----------|-------|
| Sun cost | 75 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per fume burst |
| Fire rate | 1 fume every 1.425 seconds |
| Range | ~4 tiles |
| Special | **Penetrating**: hits ALL zombies in range. **Bypasses** Screen Door and Ladder shields. |
| Nocturnal | Yes |
| Unlocked | Level 2-2 |

#### Grave Buster

| Property | Value |
|----------|-------|
| Sun cost | 75 |
| Recharge | Fast (7.5s) |
| Health | N/A (single use, placed on grave) |
| Function | Destroys a grave tile over ~4.5 seconds |
| Drop | Graves may drop coins, diamonds, or plants when busted |
| Nocturnal | Yes |
| Unlocked | Level 2-3 |

#### Hypno-shroom

| Property | Value |
|----------|-------|
| Sun cost | 75 |
| Recharge | Slow (30s) |
| Health | 300 HP |
| Function | When eaten by a zombie, that zombie turns around and fights for the player |
| Hypnotized zombie | Retains all its stats (HP, speed, damage) and walks right, attacking other zombies |
| Nocturnal | Yes |
| Unlocked | Level 2-5 |

#### Scaredy-shroom

| Property | Value |
|----------|-------|
| Sun cost | 25 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per spore |
| Fire rate | 1 spore every 1.425 seconds |
| Range | Entire lane |
| Special | **Hides** (stops firing, ducks down) when any zombie is within ~1.5 tiles |
| Nocturnal | Yes |
| Unlocked | Level 2-6 |

#### Ice-shroom

| Property | Value |
|----------|-------|
| Sun cost | 75 |
| Recharge | Very Slow (50s) |
| Health | N/A (single use) |
| Damage | 20 to all zombies on screen |
| Area | **Entire screen** |
| Special | Freezes all zombies for ~10 seconds (complete immobilization) |
| Nocturnal | Yes |
| Unlocked | Level 2-7 |

#### Doom-shroom

| Property | Value |
|----------|-------|
| Sun cost | 125 |
| Recharge | Very Slow (50s) |
| Health | N/A (single use) |
| Damage | 1800 (instant kill) |
| Area | Large radius ~3.5 tiles (roughly 5×7 tile area) |
| Special | Leaves a **crater** at detonation point — no planting for ~3 minutes |
| Nocturnal | Yes |
| Unlocked | Level 2-8 |

### 7.3 Pool Plants (World 3)

#### Lily Pad

| Property | Value |
|----------|-------|
| Sun cost | 25 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Function | Platform for planting on water tiles |
| Placement | Water tiles only |
| Unlocked | Level 2-10 |

#### Squash

| Property | Value |
|----------|-------|
| Sun cost | 50 |
| Recharge | Slow (30s) |
| Health | 300 HP |
| Damage | 1800 (instant kill) |
| Target | Jumps to nearest zombie within detection range (~1 tile forward or behind) |
| Behavior | Leaps into the air, lands on target zombie, crushing it. Then disappears. |
| Unlocked | Level 3-1 |

#### Threepeater

| Property | Value |
|----------|-------|
| Sun cost | 325 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per pea × 3 lanes |
| Fire rate | 1 pea per adjacent lane every 1.425 seconds |
| Range | Fires in its own lane AND the lanes directly above and below |
| Edge behavior | On the top row, only fires in its lane and the lane below (2 peas). Same for bottom row. |
| Unlocked | Level 3-2 |

#### Tangle Kelp

| Property | Value |
|----------|-------|
| Sun cost | 25 |
| Recharge | Slow (30s) |
| Health | N/A (single use) |
| Damage | Instant kill (drags zombie underwater) |
| Placement | Water tiles only |
| Target | First zombie to enter its tile |
| Unlocked | Level 3-3 |

#### Jalapeno

| Property | Value |
|----------|-------|
| Sun cost | 125 |
| Recharge | Very Slow (50s) |
| Health | N/A (single use) |
| Damage | 1800 (instant kill) |
| Area | **Entire lane** (all 9 columns in the row where planted) |
| Special | Removes Zomboni ice trails in that lane |
| Unlocked | Level 3-5 |

#### Spikeweed

| Property | Value |
|----------|-------|
| Sun cost | 100 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per contact hit (~1 hit per second) |
| Placement | Ground tiles only (not water, not roof) |
| Special | Zombies walk **over** it (don't stop to eat). Pops Zomboni tires but is **destroyed** in the process. |
| Unlocked | Level 3-6 |

#### Torchwood

| Property | Value |
|----------|-------|
| Sun cost | 175 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | None (modifier) |
| Function | Peas passing through Torchwood become **fire peas** |
| Fire pea stats | 40 damage (2× normal) + small splash (~14 damage) in 1×1 area |
| Frozen pea interaction | Frozen pea → Torchwood = **normal pea** (thaws, loses slow, no fire bonus) |
| Double Torchwood | Fire pea through second Torchwood = no additional bonus |
| Unlocked | Level 3-7 |

#### Tall-nut

| Property | Value |
|----------|-------|
| Sun cost | 125 |
| Recharge | Slow (30s) |
| Health | 8000 HP |
| Damage | None (blocker) |
| Visual states | 3 damage stages (like Wall-nut but taller) |
| Special | Blocks **vaulting/jumping** zombies (Pole Vaulter, Dolphin Rider, Pogo). They cannot jump over Tall-nut. |
| Unlocked | Level 3-8 |

### 7.4 Fog Plants (World 4)

#### Sea-shroom

| Property | Value |
|----------|-------|
| Sun cost | 0 (free) |
| Recharge | Slow (30s) |
| Health | 300 HP |
| Damage | 20 per spore |
| Fire rate | 1 spore every 1.425 seconds |
| Range | ~3 tiles |
| Placement | Water tiles only (no Lily Pad needed) |
| Nocturnal | Yes |
| Unlocked | Level 3-10 |

#### Plantern

| Property | Value |
|----------|-------|
| Sun cost | 25 |
| Recharge | Slow (30s) |
| Health | 300 HP |
| Function | Clears fog in a ~4×4 tile area around it |
| Nocturnal | Yes |
| Unlocked | Level 4-1 |

#### Cactus

| Property | Value |
|----------|-------|
| Sun cost | 125 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per spike |
| Fire rate | 1 spike every 1.425 seconds |
| Range | Entire lane |
| Special | **Extends upward** to pop Balloon Zombies when one is in its lane |
| Unlocked | Level 4-2 |

#### Blover

| Property | Value |
|----------|-------|
| Sun cost | 100 |
| Recharge | Fast (7.5s) |
| Health | N/A (single use) |
| Function | Instantly **blows away all Balloon Zombies** on screen. Temporarily clears fog (~15 seconds). |
| Unlocked | Level 4-3 |

#### Split Pea

| Property | Value |
|----------|-------|
| Sun cost | 125 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage (forward) | 20 per pea (1 pea per volley) |
| Damage (backward) | 20 per pea × 2 peas per volley |
| Fire rate | 1.425 seconds per volley |
| Range | Both directions in lane |
| Purpose | Counters Digger Zombie (attacks from behind) |
| Unlocked | Level 4-5 |

#### Starfruit

| Property | Value |
|----------|-------|
| Sun cost | 125 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 per star projectile |
| Fire rate | 5 stars every 1.425 seconds |
| Directions | Fires in 5 directions: up-left, up-right, down-left, down-right, and directly left. Does **NOT** fire directly right (forward). |
| Unlocked | Level 4-6 |

#### Pumpkin

| Property | Value |
|----------|-------|
| Sun cost | 125 |
| Recharge | Slow (30s) |
| Health | 4000 HP (same as Wall-nut) |
| Function | Placed **over** any existing plant as an armor shell |
| Damage states | 3 visual stages (like Wall-nut) |
| Behavior | Zombies eat the Pumpkin first; the inner plant continues to function normally |
| Unlocked | Level 4-7 |

#### Magnet-shroom

| Property | Value |
|----------|-------|
| Sun cost | 100 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Range | ~3.5 tile radius |
| Cooldown | ~15 seconds between attractions |
| Targets | Removes: Buckets, Screen Doors, Football Helmets, Pogo Sticks, Ladders, Jack-in-the-Boxes |
| Nocturnal | Yes |
| Unlocked | Level 4-8 |

### 7.5 Roof Plants (World 5)

#### Flower Pot

| Property | Value |
|----------|-------|
| Sun cost | 25 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Function | Platform required for planting on all Roof tiles |
| Unlocked | Level 5-1 |

#### Cabbage-pult

| Property | Value |
|----------|-------|
| Sun cost | 100 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 40 per cabbage |
| Fire rate | 1 cabbage every ~3 seconds (~22 lobs/minute) |
| Range | Entire lane (lobbed trajectory) |
| Special | Lobs over Screen Doors and Ladders (bypasses shields) |
| Unlocked | Level 4-10 |

#### Kernel-pult

| Property | Value |
|----------|-------|
| Sun cost | 100 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage | 20 (kernel) or 40 (butter) |
| Fire rate | 1 projectile every ~3 seconds |
| Range | Entire lane (lobbed) |
| Kernel chance | ~75% |
| Butter chance | ~25% — also **immobilizes** target for ~4 seconds |
| Unlocked | Level 5-2 |

#### Coffee Bean

| Property | Value |
|----------|-------|
| Sun cost | 75 |
| Recharge | Fast (7.5s) |
| Health | N/A (consumed on use) |
| Function | Wakes up a sleeping (nocturnal) mushroom for daytime use |
| Placement | On any sleeping mushroom |
| Unlocked | Level 5-3 |

#### Garlic

| Property | Value |
|----------|-------|
| Sun cost | 50 |
| Recharge | Fast (7.5s) |
| Health | 400 HP |
| Damage | None |
| Function | Zombies that bite it are **diverted** to an adjacent lane |
| Bites before death | ~3 bites (each bite causes lane change) |
| Lane change rules | Zombies on edge rows can only move inward. On middle rows, tend to move upward. |
| Immune zombies | Zomboni, Catapult Zombie, Bungee Zombie, Gargantuar (don't eat it). Pole Vaulter and Pogo jump over. Balloon floats over. |
| Unlocked | Level 5-5 |

#### Umbrella Leaf

| Property | Value |
|----------|-------|
| Sun cost | 100 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Protection area | 3×3 tiles (centered on Umbrella Leaf) |
| Function | Deflects **Bungee Zombies** and **Catapult Zombie basketballs** within its area |
| Unlocked | Level 5-6 |

#### Marigold

| Property | Value |
|----------|-------|
| Sun cost | 50 |
| Recharge | Slow (30s) |
| Health | 300 HP |
| Production | Drops silver coins (occasionally gold) at regular intervals (~24s) |
| Purpose | Money farming |
| Unlocked | Level 5-7 |

#### Melon-pult

| Property | Value |
|----------|-------|
| Sun cost | 300 |
| Recharge | Fast (7.5s) |
| Health | 300 HP |
| Damage (direct) | 80 |
| Damage (splash) | 26-40 to nearby zombies within ~1 tile of impact |
| Fire rate | 1 melon every ~3 seconds |
| Range | Entire lane (lobbed) |
| Unlocked | Level 5-8 |

### 7.6 Upgrade Plants (Purchased from Crazy Dave's Shop)

Upgrade plants are placed **on top of** their prerequisite base plant.

#### Gatling Pea

| Property | Value |
|----------|-------|
| Sun cost | 250 |
| Shop price | $5,000 |
| Recharge | Very Slow (50s) |
| Health | 300 HP |
| Damage | 20 per pea × 4 peas per volley |
| Prerequisite | Repeater |
| Available after | Level 3-4 |

#### Twin Sunflower

| Property | Value |
|----------|-------|
| Sun cost | 150 |
| Shop price | $5,000 |
| Recharge | Very Slow (50s) |
| Health | 300 HP |
| Production | 50 sun (two 25-drops) every ~24 seconds |
| Prerequisite | Sunflower |
| Available after | Level 3-4 |

#### Gloom-shroom

| Property | Value |
|----------|-------|
| Sun cost | 150 |
| Shop price | $7,500 |
| Recharge | Very Slow (50s) |
| Health | 300 HP |
| Damage | 80 per fume burst (20 × 4 in rapid succession) |
| Fire rate | ~1 burst every 1.9 seconds (~32 bursts/minute) |
| Range | All 8 surrounding tiles + its own tile (3×3 area) — very short range |
| Prerequisite | Fume-shroom |
| Special | Penetrating (hits all zombies in range); bypasses shields |
| Available after | Level 4-4 |

#### Cattail

| Property | Value |
|----------|-------|
| Sun cost | 225 |
| Shop price | $10,000 |
| Recharge | Very Slow (50s) |
| Health | 300 HP |
| Damage | 20 per homing spike |
| Fire rate | 1 spike every 1.425 seconds |
| Range | **Entire screen** (homing — targets nearest zombie anywhere) |
| Special | Pops Balloon Zombies; prioritizes Balloon Zombies |
| Prerequisite | Lily Pad (water-only) |
| Available after | Level 4-4 |

#### Winter Melon

| Property | Value |
|----------|-------|
| Sun cost | 200 |
| Shop price | $10,000 |
| Recharge | Very Slow (50s) |
| Health | 300 HP |
| Damage (direct) | 80 + slow effect |
| Damage (splash) | 26-40 + slow effect to all splashed zombies |
| Fire rate | 1 melon every ~3 seconds |
| Prerequisite | Melon-pult |
| Special | Slows ALL zombies hit (direct AND splash) to 50% speed |
| Available after | Adventure Mode completion |

#### Gold Magnet

| Property | Value |
|----------|-------|
| Sun cost | 50 |
| Shop price | $3,000 |
| Recharge | Very Slow (50s) |
| Health | 300 HP |
| Function | Automatically collects coins and diamonds on screen every ~5 seconds |
| Prerequisite | Magnet-shroom |
| Available after | Level 5-1 |

#### Spikerock

| Property | Value |
|----------|-------|
| Sun cost | 125 |
| Shop price | $7,500 |
| Recharge | Very Slow (50s) |
| Health | 9 vehicle/Gargantuar hits before breaking |
| Damage | 40 per contact hit (2× Spikeweed) |
| Prerequisite | Spikeweed |
| Special | Survives Zomboni (kills it without being destroyed, up to 9 times). Survives Gargantuar smash (up to 9 times). |
| Available after | Level 5-1 |

#### Cob Cannon

| Property | Value |
|----------|-------|
| Sun cost | 500 |
| Shop price | $20,000 |
| Recharge | Very Slow (50s) |
| Health | 300 HP |
| Damage | 1800 (instant kill) |
| Area | 3×3 tiles — player-targeted anywhere on the screen |
| Rearm time | ~35 seconds between launches |
| Size | Occupies **2 horizontal tiles** |
| Prerequisite | 2 adjacent Kernel-pults |
| Usage | Click Cob Cannon → click target location on lawn |
| Available after | Adventure Mode completion |

#### Imitater

| Property | Value |
|----------|-------|
| Sun cost | Same as the copied plant |
| Shop price | $30,000 |
| Recharge | Same as the copied plant |
| Function | Mimics any non-upgrade plant. Transforms after ~3.2 seconds of being planted. |
| Strategic use | Effectively halves the cooldown of one plant type (carry two copies) |
| Restriction | Cannot copy upgrade plants |
| Available after | Adventure Mode completion |

---

## 8. All Zombies — Complete Stats

### Damage Reference

- Zombies deal **100 damage per bite** at a rate of approximately **1 bite per 0.5-1 second** while eating (effectively ~100 DPS).
- A standard plant (300 HP) is eaten in approximately **3 seconds**.

### Health Notation

Zombie HP values represent total durability. For zombies with accessories (cone, bucket, etc.), the accessory and body HP are noted separately.

### 8.1 Basic Zombies

#### Zombie (Basic)

| Property | Value |
|----------|-------|
| Total HP | 270 |
| Speed | 4.7 seconds/tile |
| Damage | 100/bite |
| Degradation | Arm falls off at ~90 HP lost; head falls off at ~181 HP lost |
| Death animation | Head detaches, stumbles backward, collapses |

#### Flag Zombie

| Property | Value |
|----------|-------|
| Total HP | 270 |
| Speed | 3.7 seconds/tile (faster than basic) |
| Damage | 100/bite |
| Role | Signals start of "huge wave"; always appears first in a huge wave |

#### Conehead Zombie

| Property | Value |
|----------|-------|
| Total HP | 640 (370 cone + 270 body) |
| Speed | 4.7 seconds/tile |
| Damage | 100/bite |
| Cone states | Cone degrades visually, then falls off → becomes basic zombie |

#### Buckethead Zombie

| Property | Value |
|----------|-------|
| Total HP | 1370 (1100 bucket + 270 body) |
| Speed | 4.7 seconds/tile |
| Damage | 100/bite |
| Bucket states | Bucket dents and changes color as damaged |
| Magnetic | Bucket can be removed by Magnet-shroom |

### 8.2 Special Zombies

#### Pole Vaulting Zombie

| Property | Value |
|----------|-------|
| Total HP | 500 |
| Speed (running) | 2.5 seconds/tile |
| Speed (after jump) | 4.7 seconds/tile |
| Damage | 100/bite |
| Special | Vaults over the first plant encountered (except Tall-nut). Drops pole after jumping — becomes a slow walker. |

#### Newspaper Zombie

| Property | Value |
|----------|-------|
| Total HP | 420 (150 newspaper + 270 body) |
| Speed (normal) | 4.7 seconds/tile |
| Speed (enraged) | ~1.8-2.5 seconds/tile |
| Damage | 100/bite |
| Special | When newspaper is destroyed, becomes enraged and moves much faster |

#### Screen Door Zombie

| Property | Value |
|----------|-------|
| Total HP | 1370 (1100 door + 270 body) |
| Speed | 4.7 seconds/tile |
| Damage | 100/bite |
| Shield | Screen door blocks straight-shot projectiles (peas). Does NOT block: fumes, lobbed projectiles, spikes. |
| Magnetic | Door can be removed by Magnet-shroom |

#### Football Zombie

| Property | Value |
|----------|-------|
| Total HP | 1670 |
| Speed | 2.5 seconds/tile |
| Damage | 100/bite |
| Magnetic | Helmet can be removed by Magnet-shroom (reduces HP significantly) |

#### Dancing Zombie

| Property | Value |
|----------|-------|
| Total HP | 500 |
| Speed | Variable (1.5-5.5 seconds/tile, moonwalk pattern) |
| Damage | 100/bite |
| Special | Summons 4 Backup Dancers in adjacent tiles (one in each cardinal direction) |
| Summon timing | Summons dancers shortly after appearing on lawn |

#### Backup Dancer

| Property | Value |
|----------|-------|
| Total HP | 270 |
| Speed | 5.5 seconds/tile |
| Damage | 100/bite |
| Behavior | Summoned by Dancing Zombie; acts independently after spawning |

### 8.3 Pool/Aquatic Zombies

#### Ducky Tube Zombie

| Property | Value |
|----------|-------|
| Total HP | Same as base type (basic, conehead, or buckethead variant) |
| Speed | Same as base type |
| Function | Any land zombie with an inflatable tube for traversing pool lanes |

#### Snorkel Zombie

| Property | Value |
|----------|-------|
| Total HP | 270 |
| Speed | 4.0 seconds/tile |
| Damage | 100/bite |
| Special | **Submerges** while moving (immune to most projectiles). **Surfaces** to eat plants — vulnerable while eating. |
| Counters | Lobbed-shot plants, Tangle Kelp (instant kill while submerged) |

#### Zomboni

| Property | Value |
|----------|-------|
| Total HP | 1151 |
| Speed | Variable |
| Damage | Instant kill (crushes plants by driving over them) |
| Special | Creates an **ice trail** behind it. Ice trail allows Zombie Bobsled Team to spawn. |
| Counter | Spikeweed/Spikerock (pops tires, kills Zomboni). Jalapeno (destroys + melts ice). |

#### Zombie Bobsled Team

| Property | Value |
|----------|-------|
| Total HP | ~1024 total (4 zombies, ~256 each) |
| Speed (on ice) | 1.2 seconds/tile |
| Speed (walking) | 4.7 seconds/tile |
| Spawning | Only appear on Zomboni ice trails |
| Behavior | Team of 4 in a bobsled; exit sled at end of ice trail and walk individually |

#### Dolphin Rider Zombie

| Property | Value |
|----------|-------|
| Total HP | 500 |
| Speed (riding) | 0.8 seconds/tile (extremely fast) |
| Speed (walking) | 4.7 seconds/tile |
| Damage | 100/bite |
| Special | Jumps over the first plant (except Tall-nut). Loses dolphin after jumping. |
| Lane | Water lanes only |

### 8.4 Special Mechanic Zombies

#### Jack-in-the-Box Zombie

| Property | Value |
|----------|-------|
| Total HP | 500 |
| Speed | 2.2 seconds/tile |
| Damage | Instant kill (explosion, ~1×1 area when box detonates) |
| Special | Carries a jack-in-the-box that randomly explodes, destroying the zombie and nearby plants |
| Magnetic | Jack-in-the-box can be removed by Magnet-shroom (prevents explosion) |

#### Balloon Zombie

| Property | Value |
|----------|-------|
| Total HP | 201 |
| Speed | 2.5 seconds/tile (floating) |
| Damage | 100/bite |
| Special | **Floats above all ground-level plants** — immune to all non-aerial attacks |
| Counters | Cactus (extends to pop balloon), Cattail (homing spikes), Blover (blows away) |
| When popped | Falls to ground and walks normally as a basic zombie (very low HP) |

#### Digger Zombie

| Property | Value |
|----------|-------|
| Total HP | 281 |
| Speed (underground) | 1.2 seconds/tile |
| Speed (surface) | 4.7 seconds/tile |
| Damage | 100/bite |
| Special | Tunnels underground from right to left, bypassing all plants. Surfaces at column 1 and **walks right** (backward). |
| Magnetic | Pickaxe can be removed by Magnet-shroom (forces surface immediately) |
| Counter | Split Pea (backward-firing peas), Magnet-shroom |

#### Pogo Zombie

| Property | Value |
|----------|-------|
| Total HP | 500 |
| Speed | 1.9-3.8 seconds/tile |
| Damage | 100/bite |
| Special | **Bounces over every plant** continuously. Only stops if Tall-nut blocks or pogo is removed. |
| Magnetic | Pogo stick can be removed by Magnet-shroom |

#### Zombie Yeti

| Property | Value |
|----------|-------|
| Total HP | 901 |
| Speed (approaching) | 5.0 seconds/tile |
| Speed (fleeing) | 2.1 seconds/tile |
| Damage | 100/bite |
| Behavior | Extremely rare. Appears briefly, then turns around and runs away. |
| Drop | 4 diamonds ($4,000 total) when killed |
| First appearance | Level 4-10 on second playthrough |

### 8.5 Roof Zombies

#### Bungee Zombie

| Property | Value |
|----------|-------|
| Total HP | 450 |
| Speed | Descends in ~4 seconds |
| Damage | Steals one plant (instant removal) |
| Behavior | Drops from the sky targeting a random plant, grabs it, and flies away |
| Counter | Umbrella Leaf (deflects within 3×3 area) |
| Combat | Can be killed during the descent/ascent phase if enough damage is dealt |

#### Ladder Zombie

| Property | Value |
|----------|-------|
| Total HP | 835 (500 ladder + 335 body) |
| Speed (with ladder) | 2.0 seconds/tile |
| Speed (without) | 4.7 seconds/tile |
| Damage | 100/bite |
| Special | Places ladder on first Wall-nut/Tall-nut/Pumpkin encountered. Ladder allows **all subsequent zombies** to climb over that obstacle. |
| Magnetic | Ladder can be removed by Magnet-shroom before it's placed |

#### Catapult Zombie (Basketball)

| Property | Value |
|----------|-------|
| Total HP | 651 |
| Speed | 2.5 seconds/tile |
| Damage | 75 per basketball |
| Behavior | Drives vehicle that launches basketballs at the **furthest-left plant** in the lane |
| End behavior | When vehicle reaches a plant, it crushes plants by driving forward |
| Counter | Umbrella Leaf (deflects basketballs in 3×3 area) |

### 8.6 Boss Zombies

#### Gargantuar

| Property | Value |
|----------|-------|
| Total HP | 3000 |
| Speed | 4.7 seconds/tile |
| Damage | **Instant kill** (smashes any plant with one hit using telephone pole) |
| Special | Cannot be killed by a single instant-kill plant (survives Cherry Bomb, Squash, etc. once — needs 2 to kill) |
| Imp throw | At ~50% HP (1500 damage taken), throws an Imp deep into the player's defenses (around columns 6-7) |

#### Imp

| Property | Value |
|----------|-------|
| Total HP | 181 |
| Speed | 4.7 seconds/tile |
| Damage | 100/bite |
| Spawning | Thrown by Gargantuar at 50% HP |
| Landing | Lands approximately 6-7 columns from the right edge |

#### Dr. Zomboss (Zombot)

| Property | Value |
|----------|-------|
| Total HP | ~40,000 (first playthrough); ~60,000 (Dr. Zomboss's Revenge) |
| Position | Stationary mechanical suit at the right edge of the Roof |
| Attacks | See [Section 14.1: Boss Fight](#141-dr-zomboss-boss-fight) |

---

## 9. Wave & Spawning System

### Wave Structure

Each level has a set number of **flags**. Each flag represents a major checkpoint, culminating in a "huge wave."

- **Between flags**: Multiple smaller waves of zombies spawn incrementally.
- **At each flag**: A "huge wave" occurs with the message **"A HUGE WAVE OF ZOMBIES IS APPROACHING!"**
- **Flag Zombie**: Always appears at the start of each huge wave, carrying a flag.
- **Final wave**: Last and most intense wave; clearing it wins the level.

### Waves Per Flag Count

| Flags | Total Waves | Waves Per Flag |
|-------|------------|----------------|
| 0 flags | ~5 small waves | No huge wave |
| 1 flag | ~10 waves | Huge wave at end |
| 2 flags | ~20 waves | Huge wave at wave 10 and 20 |
| 3 flags | ~30 waves | Huge wave at wave 10, 20, and 30 |

### Progress Bar

- Located at **bottom-right** of the screen.
- Horizontal bar with a zombie head icon that moves left-to-right as waves progress.
- Flag markers indicate huge wave positions.
- Bar is color-coded: unfilled portion is dark, filled portion is lighter.

### Wave Advancement Conditions

A new wave is triggered when **either** condition is met:

1. **Time elapsed**: A minimum of ~6 seconds since the last wave spawned (varies by level difficulty).
2. **Damage dealt**: The player has dealt **≥50% of the current wave's total zombie HP**, triggering the next wave early. Exception: waves 9, 19, 29 (pre-huge-wave) are not advanced early by damage.

### Zombie Spawning Algorithm

Each wave operates on a **point budget** system:

1. The level has a base difficulty tier and a wave count.
2. Each wave is assigned a **point budget** that increases with wave number.
3. Each zombie type has:
   - A **point cost** (stronger zombies cost more).
   - A **selection weight** (probability of being chosen).
   - An **earliest wave** (certain zombies cannot appear before a specified wave).
4. The game fills each wave by randomly selecting zombies (weighted) until the point budget is spent.
5. Special zombies (Flag Zombie, Backup Dancers) are spawned by triggers, not the random system.
6. Zombie Yeti has an extremely low weight (1) and special appearance rules.

### Zombie Type Availability by World

| World | Zombie Types Available |
|-------|----------------------|
| Day | Basic, Flag, Conehead, Buckethead, Pole Vaulting |
| Night | Above + Newspaper, Screen Door, Football, Dancing, Backup Dancer |
| Pool | Above + Ducky Tube variants, Snorkel, Zomboni, Bobsled Team, Dolphin Rider |
| Fog | Above + Jack-in-the-Box, Balloon, Digger, Pogo, Zombie Yeti |
| Roof | Above + Bungee, Ladder, Catapult, Gargantuar, Imp, Dr. Zomboss |

---

## 10. Projectile & Combat System

### Projectile Types

| Projectile | Source | Damage | Speed | Trajectory | Special |
|------------|--------|--------|-------|------------|---------|
| Pea (green) | Peashooter, Repeater, Threepeater, Split Pea, Gatling Pea | 20 | Fast straight line | Horizontal | Single target, consumed on hit |
| Frozen pea (blue) | Snow Pea | 20 + slow | Fast straight line | Horizontal | Slows target to 50% speed |
| Fire pea (orange) | Pea through Torchwood | 40 + splash | Fast straight line | Horizontal | Small splash (~14 damage) in 1×1 area around impact |
| Spore | Puff-shroom, Scaredy-shroom, Sea-shroom | 20 | Fast straight line | Horizontal | Limited range (~3 tiles) |
| Fume | Fume-shroom, Gloom-shroom | 20 (Fume) / 80 (Gloom) | Instant in range | Area | Penetrates all targets and shields |
| Cabbage | Cabbage-pult | 40 | Arcing lob | Lobbed | Bypasses shields, targets first zombie |
| Kernel | Kernel-pult | 20 | Arcing lob | Lobbed | ~75% chance |
| Butter | Kernel-pult | 40 + immobilize | Arcing lob | Lobbed | ~25% chance; immobilizes for ~4 seconds |
| Melon | Melon-pult | 80 + 26-40 splash | Arcing lob | Lobbed | Splash hits adjacent zombies |
| Winter Melon | Winter Melon | 80 + 26-40 splash + slow | Arcing lob | Lobbed | All targets (direct + splash) are slowed |
| Star | Starfruit | 20 | Fast | 5 diagonal/horizontal directions | 5 projectiles per volley |
| Spike (homing) | Cattail | 20 | Fast, homing | Follows target | Targets nearest zombie, prioritizes Balloon |
| Spike (straight) | Cactus | 20 | Fast straight line | Horizontal/vertical | Extends vertically for airborne targets |

### Lobbed Projectile Behavior

- Lobbed projectiles arc through the air and land on the **first zombie** in the lane.
- They bypass Screen Doors and Ladders (hit from above).
- On the Roof, lobbed shots function normally from any tile (critical advantage over pea-shooters on sloped tiles).

### Pea-Shooter on Roof Issue

- Pea-shooters planted on the **sloped section** of the roof (columns 1-4) fire peas upward at an angle.
- These peas fly **over zombies' heads** for most of their trajectory, severely limiting effective range to ~1-2 tiles.
- Pea-shooters on the **flat section** (columns 5-9) function normally.
- This makes **catapult plants** essential for roof levels.

---

## 11. Collision & Interaction Rules

### Zombie Targeting

- Zombies walk in a straight line in their lane.
- They **eat the first plant** they physically reach (no target selection AI).
- Exceptions:
  - **Bungee Zombie**: Targets a random plant on the field.
  - **Catapult Zombie**: Launches basketballs at the **leftmost** plant in its lane.
  - **Digger Zombie**: Bypasses all plants, surfaces at column 1, walks right.
  - **Gargantuar**: Smashes the first plant (instant kill) instead of eating.

### Eating Mechanics

- Eating deals **~100 DPS** (damage per second).
- Multiple zombies eating the same plant **stack** their damage.
- Standard plant (300 HP) takes ~3 seconds to eat.
- Wall-nut (4000 HP) takes ~40 seconds.
- Tall-nut (8000 HP) takes ~80 seconds.

### Projectile Collision

- **Single-target peas**: Hit the first zombie in their path and are consumed.
- **Fume**: Hits ALL zombies within range simultaneously (no consumption).
- **Lobbed**: Targets the first zombie; splash damage hits nearby zombies.
- **Homing (Cattail)**: Tracks nearest zombie across the entire screen.
- **Stars (Starfruit)**: Travel in fixed directions indefinitely until hitting a zombie or leaving the screen.

### Shield Interactions

| Shield Type | Blocks | Does NOT Block |
|-------------|--------|----------------|
| Screen Door | Peas, spores, frozen peas | Fumes, lobbed shots, spikes, fire peas (destroyed by fire) |
| Newspaper | Peas (briefly) | Everything (very low HP shield) |
| Ladder (placed on plant) | Nothing — allows zombies to climb over | N/A |
| Bucket | Nothing — just extra HP | N/A |

### Slow/Freeze Interactions

| Effect | Duration | Speed Reduction | Stacking |
|--------|----------|-----------------|----------|
| Snow Pea slow | ~10 seconds per hit (refreshed on each hit) | 50% speed reduction | Does not stack with itself |
| Winter Melon slow | ~10 seconds | 50% speed reduction | Does not stack with Snow Pea |
| Ice-shroom freeze | ~10 seconds | 100% (complete stop) | Overrides slow effects |
| Butter immobilize | ~4 seconds | 100% (complete stop) | Independent timer |

### Fire vs. Ice Interactions

- **Frozen pea → Torchwood**: Becomes a normal pea (loses slow, no fire bonus).
- **Fire pea on frozen zombie**: Thaws the zombie (removes ice/slow effect). Deals 40 damage.
- **Jalapeno**: Removes Zomboni ice trails. Thaws frozen zombies.
- **Ice-shroom during boss fight**: Freezes Dr. Zomboss. Do NOT use Jalapeno while frozen (unfreezes him).

### Area Damage Rules

| Source | Area | Damage | Notes |
|--------|------|--------|-------|
| Cherry Bomb | 3×3 centered on tile | 1800 | Destroys most zombies instantly |
| Doom-shroom | ~3.5 tile radius | 1800 | Leaves crater (no planting for ~3 min) |
| Jalapeno | Entire lane (1 row, all columns) | 1800 | Removes ice trails |
| Potato Mine | 1×1 (its own tile) | 1800 | Must arm for 15 seconds first |
| Squash | 1×1 (target zombie) | 1800 | Jumps to nearest zombie |
| Cob Cannon | 3×3 player-targeted | 1800 | Player chooses impact point |

### Special Zombie Interactions

| Zombie | Interaction Rule |
|--------|-----------------|
| Gargantuar | Survives ONE instant-kill effect. Two instant-kills needed. |
| Pole Vaulter | Jumps first plant (unless Tall-nut). Only jumps once. |
| Dolphin Rider | Jumps first plant in water (unless Tall-nut). Only jumps once. |
| Pogo | Continuously jumps over ALL plants until Tall-nut or Magnet-shroom removes pogo. |
| Ladder | Places ladder on first defensive plant (Wall-nut/Tall-nut/Pumpkin). Ladder stays permanently. |
| Digger | Underground = immune to all projectiles. Surfaced = vulnerable. |
| Snorkel | Submerged = immune to most projectiles. Surfaces to eat. |
| Balloon | Airborne = immune to all non-aerial attacks. |
| Bungee | Can be killed during descent/ascent with enough DPS. Umbrella Leaf deflects. |

---

## 12. Level Progression — All 50 Levels

### World 1: Day (Levels 1-1 to 1-10)

| Level | Flags | Unlock | New Zombie(s) | Special Notes |
|-------|-------|--------|---------------|---------------|
| 1-1 | 0 | Peashooter, Sunflower | Basic Zombie | Tutorial; only 1 lane active; forced Peashooter placement |
| 1-2 | 1 | Cherry Bomb | Flag Zombie | 3 lanes active |
| 1-3 | 1 | Wall-nut | Conehead Zombie | All 5 lanes active |
| 1-4 | 1 | Shovel | — | Shovel tutorial |
| 1-5 | 1 | Potato Mine | — | **Mini-game: Wall-nut Bowling** |
| 1-6 | 1 | Snow Pea | Pole Vaulting Zombie | |
| 1-7 | 2 | Chomper | — | First level with seed selection screen |
| 1-8 | 1 | Repeater | Buckethead Zombie | |
| 1-9 | 2 | Note from zombies | — | |
| 1-10 | 2 | Puff-shroom | — | **Conveyor belt level** |

### World 2: Night (Levels 2-1 to 2-10)

No falling sun. Graves appear in rightmost columns. Mushrooms are awake.

| Level | Flags | Unlock | New Zombie(s) | Special Notes |
|-------|-------|--------|---------------|---------------|
| 2-1 | 1 | Sun-shroom | Newspaper Zombie | Night mechanics introduced |
| 2-2 | 2 | Fume-shroom | — | |
| 2-3 | 1 | Grave Buster | Screen Door Zombie | |
| 2-4 | 2 | Suburban Almanac | — | |
| 2-5 | 0 | Hypno-shroom | — | **Mini-game: Whack a Zombie** |
| 2-6 | 1 | Scaredy-shroom | Football Zombie | |
| 2-7 | 2 | Ice-shroom | — | |
| 2-8 | 1 | Doom-shroom | Dancing Zombie, Backup Dancer | |
| 2-9 | 2 | Note from zombies | — | |
| 2-10 | 2 | Lily Pad | — | **Conveyor belt level** |

### World 3: Pool (Levels 3-1 to 3-10)

6 lanes (2 water lanes: rows 3 and 4). Daytime with falling sun.

| Level | Flags | Unlock | New Zombie(s) | Special Notes |
|-------|-------|--------|---------------|---------------|
| 3-1 | 1 | Squash | Ducky Tube Zombie | Water lanes introduced |
| 3-2 | 2 | Threepeater | — | Unlocks Mini-games mode |
| 3-3 | 2 | Tangle Kelp | Snorkel Zombie | |
| 3-4 | 3 | Bacon (item for Crazy Dave) | — | |
| 3-5 | 2 | Jalapeno | — | **Mini-game: Big Trouble Little Zombie** |
| 3-6 | 2 | Spikeweed | Zomboni, Bobsled Team | |
| 3-7 | 3 | Torchwood | — | |
| 3-8 | 2 | Tall-nut | Dolphin Rider Zombie | |
| 3-9 | 3 | Note from zombies | — | |
| 3-10 | 3 | Sea-shroom | — | **Conveyor belt level** |

### World 4: Fog (Levels 4-1 to 4-10)

6 lanes with water. Nighttime. Fog covers approximately the right 4-5 columns.

| Level | Flags | Unlock | New Zombie(s) | Special Notes |
|-------|-------|--------|---------------|---------------|
| 4-1 | 1 | Plantern | Jack-in-the-Box Zombie | Fog mechanics introduced |
| 4-2 | 2 | Cactus | — | |
| 4-3 | 1 | Blover | Balloon Zombie | |
| 4-4 | 2 | Taco (item for Crazy Dave) | — | |
| 4-5 | 3 | Split Pea | — | **Mini-game: Vasebreaker** (night, no fog) |
| 4-6 | 1 | Starfruit | Digger Zombie | Unlocks Puzzle Mode |
| 4-7 | 2 | Pumpkin | — | |
| 4-8 | 1 | Magnet-shroom | Pogo Zombie | |
| 4-9 | 2 | Note from zombies | — | |
| 4-10 | 2 | Cabbage-pult | — | **Conveyor belt level** |

### World 5: Roof (Levels 5-1 to 5-10)

5 lanes. Slanted roof (columns 1-4 sloped, columns 5-9 flat). Flower Pot required on all tiles.

| Level | Flags | Unlock | New Zombie(s) | Special Notes |
|-------|-------|--------|---------------|---------------|
| 5-1 | 1 | Flower Pot | Bungee Zombie | Roof + Flower Pot mechanics |
| 5-2 | 2 | Kernel-pult | — | |
| 5-3 | 2 | Coffee Bean | Ladder Zombie | |
| 5-4 | 3 | Watering Can (Zen Garden) | — | |
| 5-5 | 2 | Garlic | — | **Mini-game: Bungee Blitz** |
| 5-6 | 2 | Umbrella Leaf | Catapult Zombie | |
| 5-7 | 3 | Marigold | — | |
| 5-8 | 2 | Melon-pult | Gargantuar, Imp | |
| 5-9 | 3 | Note from zombies | — | |
| 5-10 | Final | Trophy + all mode access | Dr. Zomboss | **Boss fight (conveyor belt)** |

---

## 13. World-Specific Mechanics

### 13.1 Day (World 1)

- Standard lawn, 5 rows × 9 columns.
- Sun falls from the sky every ~10 seconds.
- All standard plants function normally.
- Graves: None.

### 13.2 Night (World 2)

- **No falling sun** — must rely on Sun-shroom and mushroom economy.
- **Mushrooms are awake** — no Coffee Bean needed.
- **Graves**: Tombstones appear in the rightmost 3-4 columns before the level starts.
  - Graves block planting on their tile.
  - At the start of "huge waves," graves may spawn additional zombies.
  - **Grave Buster** can destroy graves (4.5-second animation). May drop coins/rewards.
- **Lighting**: Darker visual atmosphere; no gameplay visibility changes (unlike Fog).

### 13.3 Pool (World 3)

- **6 rows**: Rows 1-2 (grass), Rows 3-4 (water), Rows 5-6 (grass).
- **Water lanes**: Cannot plant directly. Require **Lily Pad** as a platform.
- **Aquatic zombies**: Ducky Tube, Snorkel, Dolphins appear in water lanes.
- **Pool Cleaners**: Replace lawnmowers for water lanes.
- Sun falls from sky (daytime).

### 13.4 Fog (World 4)

- Same 6-row layout as Pool (with water lanes).
- **Nighttime**: No falling sun. Mushrooms awake.
- **Fog**: Covers the right ~4-5 columns with a thick fog layer.
  - Player cannot see zombies or plants in fogged area.
  - **Plantern**: Clears fog in a ~4×4 area around it.
  - **Blover**: Temporarily clears all fog for ~15 seconds.
  - Lightning (from environmental flashes) may briefly illuminate fogged areas.
- **Graves**: May appear (same as Night mechanics).

### 13.5 Roof (World 5)

- **5 rows** on the house roof.
- **Flower Pot required**: No plant can be placed on a roof tile without first placing a Flower Pot.
- **Sloped tiles** (columns 1-4): Pea-shooters planted here fire at an upward angle, causing peas to fly over zombies' heads. Effective range is severely limited (~1-2 tiles). **Catapult plants are essential**.
- **Flat tiles** (columns 5-9): Pea-shooters function normally.
- **Roof Cleaners**: Replace lawnmowers.
- **No water lanes**.
- Sun falls from sky (daytime).

---

## 14. Special Level Types

### 14.1 Dr. Zomboss Boss Fight (Level 5-10)

**Setting**: Roof, conveyor belt level (no sun economy).

**Conveyor Plants Available**: Flower Pot, Cabbage-pult, Kernel-pult, Melon-pult, Jalapeno, Ice-shroom.

**Zomboss Behavior Pattern** (initial sequence is fixed, then randomized):

| Phase | Action |
|-------|--------|
| 1 | Deploys 4 basic Zombies |
| 2 | Deploys 4-5 Conehead Zombies |
| 3 | **Lowers head** → fires Fireball OR Iceball |
| 4 | Deploys 4-5 Buckethead Zombies |
| 5 | **Lowers head** → fires projectile |
| 6 | Summons 3 **Bungee Zombies** |
| 7 | **Drops RV/Camper van** (crushes 2×3 area) |
| 8+ | All attacks become **random** |

**Attack Details**:

| Attack | Visual Cue | Effect | Counter |
|--------|-----------|--------|---------|
| Fireball | Eyes glow **orange** | Rolls down lane, destroys plants + Roof Cleaners | **Ice-shroom** (destroys fireball from anywhere on field) |
| Iceball | Eyes glow **blue** | Rolls down lane, destroys plants | **Jalapeno** (must be planted in the SAME lane) |
| RV Drop | Zomboss reaches down | Crushes 2×3 area of plants | Rebuild quickly |
| Stomp | Mech foot comes down | Crushes 2×4 area on flat section | Rebuild |
| Bungee | 3 Bungees descend | Steal up to 3 plants | None on conveyor belt (no Umbrella Leaf) |
| Zombie deploy | Head opens | Various zombies deployed onto roof | Standard plant defenses |

**Victory**: Deplete all ~40,000 HP. Head-lowering phases are the main DPS opportunity (vulnerable to lobbed attacks hitting the head).

### 14.2 Conveyor Belt Levels

**Levels**: 1-5, 1-10, 2-5, 2-10, 3-5, 3-10, 4-5, 4-10, 5-5, 5-10, and many mini-games.

**Mechanics**:
- **No sun economy**: Sun counter is absent. No falling sun. No sun-producing plants appear.
- **Seed packets arrive on a moving belt** at the top of the screen, scrolling right-to-left.
- Player picks up a seed packet from the belt and places it on the grid (no sun cost).
- **Delivery rate**: Slows when 2+ unplaced packets sit on the belt. Picking up packets speeds delivery.
- **Belt capacity**: ~6-8 packets visible at once.
- **Pre-selected plants**: The game controls which plants appear. Player cannot choose.
- **Sunflowers, Sun-shrooms, Marigolds, Umbrella Leaves, upgrade plants, and Imitater** never appear on the belt.

### 14.3 Last Stand

- **Setting**: Pool (6 lanes).
- **Setup phase**: 5,000 sun to build full defenses before zombies arrive.
- **Gameplay**: Survive 5 flags (5 huge waves).
- **No sun-producing plants allowed** (Sunflower, Sun-shroom, Twin Sunflower blocked).
- **No free plants** (Puff-shroom, Sea-shroom blocked).
- **Sun replenishment**: Last zombie of each flag drops 250 sun.
- **No seed switching** between flags.

### 14.4 Vasebreaker (Puzzle Mode)

- Grid of **colored vases** placed on the lawn.
- **Click a vase** to break it and reveal contents.
- **Green vases** (with leaf pattern): Always contain a **plant** seed packet.
- **Other vases**: Random contents (zombie, plant, or sun).
- Breaking a zombie vase **spawns it immediately** in that lane.
- Received plant packets can be planted on any empty tile.
- **Plantern** (if received) reveals vase contents in a 3×3 area.
- **10 levels** with increasing difficulty, ending with Vasebreaker Endless.

### 14.5 I, Zombie (Puzzle Mode)

- **Roles reversed**: Player deploys zombies; plants are pre-placed as defenders.
- **Objective**: Eat the **brain** at the end of each lane (left side).
- **Economy**: Zombies cost sun. Sun is earned by having zombies eat **Sunflowers** (each gives 200 sun).
- **Starting sun**: Varies per level.
- **Available zombies**: Basic Zombie (50 sun), Conehead (75), Buckethead (125), Pole Vaulter (75), Dancing Zombie (350), Digger (125), Ladder (150), Football (175), Imp (50), Gargantuar (no cost / special).
- **Strategy**: Efficiently manage sun by eating Sunflowers first in cheaply defended lanes.
- **10 levels** ending with I, Zombie Endless.

---

## 15. Game Modes

### 15.1 Adventure Mode

- **50 levels** across 5 worlds (10 levels each).
- Linear progression — complete one level to unlock the next.
- **First playthrough**: Teaches mechanics progressively; new plants/zombies introduced per level.
- **Second playthrough** (after completion): Harder difficulty, may feature randomized plant selection (some levels force specific seed slots). Zombie Yeti can appear.

### 15.2 Mini-Games (20 total)

| # | Mini-Game | Description |
|---|-----------|-------------|
| 1 | ZomBotany | Zombies with Peashooter/Wall-nut heads |
| 2 | Wall-nut Bowling | Bowl Wall-nuts at zombies (conveyor) |
| 3 | Slot Machine | Spend sun to spin a slot machine for random plants |
| 4 | It's Raining Seeds | Random seed packets fall from the sky |
| 5 | Beghouled | Match-3 puzzle using plants on the grid |
| 6 | Invisi-ghoul | All zombies are invisible |
| 7 | Seeing Stars | Plant Starfruit on marked star-shaped positions |
| 8 | Zombiquarium | Feed Snorkel Zombies in an aquarium to earn sun |
| 9 | Beghouled Twist | Match-3 with rotation mechanic |
| 10 | Big Trouble Little Zombie | Tiny, fast zombies (conveyor) |
| 11 | Portal Combat | Portals redirect projectiles and zombies between lanes |
| 12 | Column Like You See 'Em | Each plant placed fills an entire column (conveyor) |
| 13 | Bobsled Bonanza | All lanes are ice; Zomboni + Bobsled Teams |
| 14 | Zombie Nimble Zombie Quick | Everything moves at 2× speed |
| 15 | Whack a Zombie | Whack-a-mole with zombies emerging from graves |
| 16 | Last Stand | Pre-set defense, survive 5 flags (see 14.3) |
| 17 | ZomBotany 2 | Harder ZomBotany in the Pool |
| 18 | Wall-nut Bowling 2 | Harder bowling variant |
| 19 | Pogo Party | Mass Pogo Zombies on the Roof |
| 20 | Dr. Zomboss's Revenge | Boss fight rematch (2× HP) |

**Unlocking**: Mini-games unlock progressively. First batch available after Level 3-2. Additional games unlock by completing Adventure Mode levels.

### 15.3 Puzzle Mode

- **Vasebreaker**: 9 levels + Endless (see 14.4).
- **I, Zombie**: 9 levels + Endless (see 14.5).
- Unlocked after Level 4-6.

### 15.4 Survival Mode

Unlocked after completing Adventure Mode.

**Normal Survival** (5 levels, 5 flags each):
- Survival: Day
- Survival: Night
- Survival: Pool
- Survival: Fog
- Survival: Roof

Between each flag, the player can **swap seed slots** (choose new plants for the seed tray). Existing plants remain on the field.

**Hard Survival** (5 levels, 10 flags each):
- Survival: Day (Hard)
- Survival: Night (Hard)
- Survival: Pool (Hard)
- Survival: Fog (Hard)
- Survival: Roof (Hard)

**Survival: Endless** (unlocked after all 10 Survival levels):
- Pool setting, unlimited flags.
- Difficulty escalates indefinitely (more Gargantuars, faster spawns).
- Considered the ultimate endgame challenge. No win condition — play until defeat.

---

## 16. Economy & Shop System

### 16.1 Currency

| Currency | Value | Drop Source |
|----------|-------|-------------|
| Silver Coin | $10 | Common zombie drop |
| Gold Coin | $50 | Uncommon zombie drop, Marigold |
| Diamond | $1,000 | Rare, Zen Garden, Zombie Yeti |
| Money Bag (level end) | $250 | Last zombie killed in level |
| Money Bag (Level 5-10) | $3,000 | Completing the final level |
| Unused Lawnmower | $50 each | End-of-level bonus per surviving mower |

**Money Cap**: $999,990

### 16.2 Crazy Dave's Twiddydinkies (Shop)

Crazy Dave's shop appears between certain levels and is accessible from the main menu.

#### Seed Slot Upgrades

| Item | Price |
|------|-------|
| 7th seed slot | $750 |
| 8th seed slot | $5,000 |
| 9th seed slot | $20,000 |
| 10th seed slot | $80,000 |

#### Defensive Items

| Item | Price | Function |
|------|-------|----------|
| Garden Rake | $200 | Kills first zombie in a random lane (3 uses per purchase) |
| Pool Cleaners | $1,000 | Adds pool cleaners to water lanes |
| Roof Cleaners | $3,000 | Adds roof cleaners to roof lanes |

#### Upgrade Plants

| Plant | Price | Available After |
|-------|-------|-----------------|
| Gatling Pea | $5,000 | Level 3-4 |
| Twin Sunflower | $5,000 | Level 3-4 |
| Gloom-shroom | $7,500 | Level 4-4 |
| Cattail | $10,000 | Level 4-4 |
| Spikerock | $7,500 | Level 5-1 |
| Gold Magnet | $3,000 | Level 5-1 |
| Winter Melon | $10,000 | After Adventure Mode |
| Cob Cannon | $20,000 | After Adventure Mode |
| Imitater | $30,000 | After Adventure Mode |

#### Zen Garden Items

| Item | Price | Function |
|------|-------|----------|
| Marigold Sprout | $2,500 (max 3/day) | Adds a Marigold to Zen Garden |
| Golden Watering Can | $10,000 | Watering can upgrade |
| Fertilizer (5 pack) | $750 | Grows plants in Zen Garden |
| Bug Spray (5 pack) | $1,000 | Keeps pests away from plants |
| Phonograph | $15,000 | Plays music to make plants happy |
| Gardening Glove | $1,000 | Move plants between garden slots |
| Mushroom Garden | $30,000 | 8-slot garden for nocturnal plants |
| Aquarium Garden | $30,000 | 8-slot garden for aquatic plants |
| Wheel Barrow | $200 | Transport plants to other gardens |
| Stinky the Snail | $3,000 | Auto-collects coins in the garden |
| Tree of Wisdom | $10,000 | Grows with Tree Food; gives tips |
| Tree Food | $2,500 per | Feeds Tree of Wisdom (one foot per food) |
| Wall-nut First Aid | $2,000 | Allows replanting Wall-nut over damaged Wall-nut |

---

## 17. UI Layout & Screen Flow

### 17.1 Main Menu

**Background**: Animated lawn/graveyard scene. Interactive — clicking zombies that wander produces reactions.

**Buttons**:
- **Adventure** — Start/continue campaign
- **Mini-Games** — (grayed until Level 3-2)
- **Puzzle** — (grayed until Level 4-6)
- **Survival** — (grayed until Adventure Mode completion)
- **Zen Garden** — (grayed until Level 5-4)
- **Options** — Audio sliders, fullscreen toggle
- **Help** — Instructions
- **Quit** — Exit game

**Top**: Player name display.
**Bottom**: Clickable gravestones / interactive elements.

### 17.2 In-Game HUD

```
┌─────────────────────────────────────────────────────────────────┐
│ [Sun: 150] [Seed1][Seed2][Seed3][Seed4][Seed5][Seed6] [Shovel] │ [Menu]
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Row 1: [Mower] [ ][ ][ ][ ][ ][ ][ ][ ][ ]                 │
│   Row 2: [Mower] [ ][ ][ ][ ][ ][ ][ ][ ][ ]                 │
│   Row 3: [Mower] [ ][ ][ ][ ][ ][ ][ ][ ][ ]                 │
│   Row 4: [Mower] [ ][ ][ ][ ][ ][ ][ ][ ][ ]                 │
│   Row 5: [Mower] [ ][ ][ ][ ][ ][ ][ ][ ][ ]                 │
│                                                                 │
│                                   ─────────────[🏴─🏴─🏴──🧟] │
│                                   Progress Bar (bottom-right)   │
└─────────────────────────────────────────────────────────────────┘
```

- **Seed Tray**: Top-left. Sun counter integrated at far left.
- **Shovel**: Immediately right of seed tray.
- **Menu button**: Top-right corner.
- **Progress bar**: Bottom-right. Horizontal bar with zombie head marker and flag indicators.
- **Lawnmowers**: Far-left of each lane row.

### 17.3 Pause Menu

Triggered by clicking "Menu" button (top-right).

**Contents**:
- Music volume slider
- Sound FX volume slider
- 3D Acceleration toggle
- Back to Game button
- Restart Level button
- Main Menu button

### 17.4 Plant Selection Screen ("Choose Your Seeds")

Appears before each level (starting Level 1-7).

```
┌──────────────────────────────────────────────────┐
│              CHOOSE YOUR SEEDS                    │
├──────────────────────────────────────────────────┤
│ [Selected Tray: slot1 | slot2 | ... | slot6-10]  │
├──────────────┬───────────────────────────────────┤
│ Available     │  Zombie Preview:                  │
│ Plants Grid:  │  [Basic] [Conehead] [Buckethead] │
│ [Peashooter]  │  [Football] [Pogo]               │
│ [Sunflower]   │                                   │
│ [Cherry Bomb] │                                   │
│ [Wall-nut]    │                                   │
│ ...           │                                   │
├──────────────┴───────────────────────────────────┤
│              [LET'S ROCK!]                        │
└──────────────────────────────────────────────────┘
```

- Click a plant to add it to the tray.
- Click a tray slot to remove that plant.
- Zombie portraits on the right preview which zombie types will appear (not quantities).
- "Let's Rock!" confirms and starts the level.

### 17.5 Suburban Almanac

**Two tabs**: Plants | Zombies

**Plant entries** show:
- Plant image and name
- Sun cost
- Recharge speed (Fast/Slow/Very Slow)
- Damage category (Normal/Heavy/Very Heavy/None)
- Range
- Humorous flavor text description

**Zombie entries** show:
- Zombie image and name
- Toughness rating (Low/Medium/High/Very High)
- Speed rating
- Special abilities
- Humorous flavor text
- Entries show "(not encountered yet)" until met in gameplay

---

## 18. Audio Design

### 18.1 Music Tracks

**Composer**: Laura Shigihara

| Track Name | Plays During | Key Character |
|------------|-------------|---------------|
| Grasswalk | Day levels (World 1) | Light, playful |
| Moongrains | Night levels (World 2) | 2/4 time, haunting |
| Watery Graves | Pool levels (World 3) | Aquatic, bouncy |
| Rigor Mormist | Fog levels (World 4) | Eerie, suspenseful |
| Graze the Roof | Roof levels (World 5) | Upbeat, urgent |
| Loonboon | Mini-game/conveyor levels | Fast-paced |
| Cerebrawl | Puzzle mode levels | Strategic, tense |
| Ultimate Battle | Conveyor boss levels (1-10, 2-10, 3-10) | Intense, dramatic |
| Brainiac Maniac | Final boss (5-10) | Epic, climactic |
| Choose Your Seeds | Seed selection screen | Calm, preparatory |
| Zen Garden | Zen Garden mode | Relaxing, C major |
| Crazy Dave (Intro Theme) | Crazy Dave interactions | Quirky |
| Zombies on Your Lawn | End credits | Pop song with vocals |

**Horde themes**: During huge waves, the music intensifies with a heavier arrangement layered on top of the base track. (Note: absent from some mobile ports.)

### 18.2 Key Sound Effects

| Event | Sound Description |
|-------|-------------------|
| Plant placement | Soft earthy "thud" |
| Sun collection | Bright chiming "ding" |
| Pea hit on zombie | Wet "splat" |
| Zombie groan | "Braaaaains" (processed voice) |
| Zombie eating | Crunching/munching sounds |
| Lawnmower activation | Engine revving, accelerating sound |
| Cherry Bomb / explosion | Deep boom with cartoon impact |
| "Huge wave" alert | Dramatic warning horn/sound |
| Level complete | Triumphant jingle |
| Game Over | Scream as zombie enters house |
| Zombie death | Groan + collapse sound |
| Seed packet recharge complete | Subtle "ready" chime |
| Shovel dig | Digging/earth sound |
| Coin collection | Light "cha-ching" |

---

## 19. Animation System

### 19.1 Animation Format

The original game uses the **Reanim** system:
- Animations are defined in `.reanim` files (XML-based).
- Each animation references **sprite parts** (individual body part images).
- Frame-by-frame **transforms** (position, rotation, scale) are stored for each part.
- Parts are composited at runtime to create fluid animations.

### 19.2 Plant Animations

| Animation State | Description |
|-----------------|-------------|
| **Idle** | Looping ambient animation (bobbing, swaying). Each plant has a unique idle. |
| **Attack** | Firing/attacking animation (e.g., Peashooter head recoil, Chomper lunge). |
| **Produce** | Sun/coin production animation (Sunflower glows, Marigold sparkles). |
| **Placement** | Brief "popping in" animation when planted. |
| **Death** | Plant disappears (eaten through). No elaborate death animation for most plants. |
| **Damage states** | Wall-nut and Tall-nut: 3 visual stages (full, cracked, severely cracked). Pumpkin: 3 stages. |
| **Sleeping** | Mushrooms in daytime: Z-Z-Z animation with closed eyes. |

### 19.3 Zombie Animations

| Animation State | Description |
|-----------------|-------------|
| **Walk** | Shuffling gait. 4 steps per tile. Arms swing. |
| **Eat** | Leans forward, chomps repeatedly. |
| **Arm loss** | At ~33% HP: one arm detaches (continues walking/eating). |
| **Head loss** | At ~67% HP: head detaches. Zombie stumbles briefly then collapses. |
| **Death** | Body falls forward or backward. May show fist-shaking animation. |
| **Burning** | When hit by Jalapeno/Cherry Bomb: charred skeleton briefly visible. |
| **Frozen** | Ice-shroom: zombie turns blue/icy, completely motionless. |
| **Slowed** | Snow Pea: blue tint/frost effect on zombie. Slower walk cycle. |
| **Special** | Each special zombie has unique animations (Pole Vaulter jump, Balloon float, Dancing moonwalk, etc.). |

### 19.4 Visual Effects

| Effect | Description |
|--------|-------------|
| Sun drop | Golden orb falls from sky with gentle rotation. |
| Sun collection | Flies in arc toward sun counter when clicked. |
| Pea projectile | Small green sphere traveling horizontally. |
| Frozen pea | Blue/icy sphere with trail particles. |
| Fire pea | Orange/red sphere with flame trail. |
| Explosion (Cherry Bomb) | Expanding circle with "POWIE!!" comic text. Red/orange burst. |
| Doom-shroom | Mushroom cloud explosion. Purple/dark tones. |
| Jalapeno | Line of fire across entire lane. |
| Coin drop | Spinning silver/gold coin with sparkle. |
| Diamond drop | Sparkling gemstone. |
| Crater | Blackened circular hole where Doom-shroom detonated. |
| Ice trail | Blue/white frozen ground where Zomboni passed. |
| Fog | Semi-transparent gray-white layer, slowly drifting. |

---

## 20. Zen Garden

### 20.1 Overview

A virtual garden where the player nurtures collected plants. Serves as the primary money-farming mechanic.

### 20.2 Gardens

| Garden | Slots | Cost | Plants Accepted |
|--------|-------|------|-----------------|
| Main Garden | 32 | Free | Standard (non-mushroom, non-aquatic) plants |
| Mushroom Garden | 8 | $30,000 | Nocturnal mushroom plants |
| Aquarium Garden | 8 | $30,000 | Aquatic plants |

### 20.3 Plant Care Cycle

Plants go through growth stages and periodically need care:

1. **Water** — Plant droops, needs watering (use Watering Can).
2. **Fertilize** — After watering, may need fertilizer to advance growth stage.
3. **Bug Spray** — Occasionally needs pest removal.
4. **Music** — Phonograph makes plants happy (produces coins faster).

**Growth stages**: Sprout → Small → Medium → Full size → Blooming (maximum happiness).

### 20.4 Coin Production

- Happy/mature plants periodically drop **silver and gold coins**.
- Plants need regular attention to stay happy and productive.
- **Stinky the Snail** ($3,000): Auto-collects dropped coins. Falls asleep after ~3 minutes of inactivity; click to wake. Chocolate keeps him awake permanently for the session.

### 20.5 Tree of Wisdom

- Separate area purchased for $10,000.
- Grows by feeding **Tree Food** ($2,500 per foot).
- At certain heights, reveals **tips, trivia, and cheat codes**:
  - 100 feet: "daisies" cheat (zombies leave small daisies when dying)
  - 500 feet: "dance" cheat (zombies all dance)
  - 1000 feet: "pinata" cheat (zombies explode into candy when dying)

### 20.6 Plant Acquisition

Plants for the Zen Garden are obtained as random drops from:
- Killed zombies (rare chance)
- Presents from Crazy Dave
- Gifts from completing levels
- Purchasing Marigold Sprouts from the shop

---

## 21. Achievements & Unlocks

### 21.1 Unlockable Features (by Progression)

| Trigger | Unlocks |
|---------|---------|
| Complete Level 1-4 | Shovel |
| Complete Level 2-4 | Suburban Almanac |
| Complete Level 3-2 | Mini-Games mode |
| Complete Level 4-6 | Puzzle mode |
| Complete Level 5-4 | Zen Garden (Watering Can) |
| Complete Adventure Mode | Survival mode, second playthrough, upgrade plants in shop |
| Complete all 10 Survival levels | Survival: Endless |

### 21.2 Crazy Dave Interactions

Crazy Dave appears between certain levels to:
- Offer **tutorials** (early levels).
- Sell items from his **Twiddydinkies shop**.
- Deliver humorous **story dialogue**.
- Request specific items (Bacon at Level 3-4, Taco at Level 4-4) — these trigger his shop.
- Provide **hints** about upcoming zombie threats.

**Crazy Dave's Speech**: Displayed as text with a garbled/nonsensical voice effect. Always accompanied by his animated portrait (pot on head, drooling, wild eyes).

### 21.3 Second Playthrough Changes

- All levels are harder (more zombies, tougher compositions).
- Some levels feature **randomized seed selection** (Crazy Dave picks some of your plants).
- **Zombie Yeti** can appear (first in Level 4-10).
- All plants and upgrades are available from the start.

---

## Appendix A: Quick Reference — Plant Damage Tiers

| Tier | Damage/Second | Plants |
|------|---------------|--------|
| Very Heavy | 56+ DPS | Gatling Pea (~56 DPS), Gloom-shroom (~42 DPS per target), Cob Cannon (burst), Winter Melon (~27 DPS + slow) |
| Heavy | 28-55 DPS | Repeater (~28 DPS), Melon-pult (~27 DPS + splash), Threepeater (~42 DPS total across 3 lanes) |
| Normal | 14-27 DPS | Peashooter (~14 DPS), Snow Pea (~14 DPS + slow), Fume-shroom (~14 DPS penetrating), Cabbage-pult (~13 DPS) |
| Light | <14 DPS | Scaredy-shroom, Puff-shroom, Sea-shroom, Starfruit (per direction), Kernel-pult |
| Instant Kill | 1800 burst | Cherry Bomb, Doom-shroom, Jalapeno, Potato Mine, Squash, Cob Cannon, Chomper (single target) |

## Appendix B: Quick Reference — Zombie Toughness Tiers

| Tier | HP Range | Zombies |
|------|----------|---------|
| Very High | 1370+ | Buckethead (1370), Screen Door (1370), Football (1670), Gargantuar (3000), Zomboni (1151) |
| High | 500-901 | Pole Vaulter (500), Dancing (500), Jack-in-the-Box (500), Dolphin Rider (500), Pogo (500), Ladder (835), Catapult (651), Zombie Yeti (901) |
| Medium | 270-420 | Basic (270), Flag (270), Conehead (640), Newspaper (420), Bungee (450) |
| Low | <270 | Imp (181), Balloon (201), Backup Dancer (270) |

## Appendix C: Timing Quick Reference

| Mechanic | Time |
|----------|------|
| Fast recharge | 7.5 seconds |
| Slow recharge | 30 seconds |
| Very Slow recharge | 50 seconds |
| Pea fire interval | 1.425 seconds |
| Catapult fire interval | ~3 seconds |
| Sunflower production interval | ~24 seconds |
| Sky sun drop interval | ~10 seconds |
| Potato Mine arming | ~15 seconds |
| Chomper chewing | ~42 seconds |
| Ice-shroom freeze duration | ~10 seconds |
| Butter immobilize duration | ~4 seconds |
| Cob Cannon rearm | ~35 seconds |
| Puff-shroom lifespan | ~4 minutes |
| Sun-shroom growth time | ~120 seconds |
| Doom-shroom crater duration | ~3 minutes |
| Imitater transform time | ~3.2 seconds |
| Magnet-shroom cooldown | ~15 seconds |
| Min time between waves | ~6 seconds |

---

*This specification is based on the original Plants vs. Zombies (2009) PC version by PopCap Games. All values are sourced from community wikis, game data mining, and extensive gameplay analysis. Minor variations may exist between platform versions (PC, Mac, iOS, Android, console).*
