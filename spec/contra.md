# Contra (NES) — Complete Game Specification

> A comprehensive specification for faithfully recreating Contra (Konami, 1988 NES version). This document covers every system, mechanic, entity, and interaction required for a full clone of this classic run-and-gun action game.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Player Character Mechanics](#3-player-character-mechanics)
4. [Weapon System](#4-weapon-system)
5. [Enemy System](#5-enemy-system)
6. [Level Design — All 8 Stages](#6-level-design--all-8-stages)
7. [Boss Encounters](#7-boss-encounters)
8. [Power-Up System](#8-power-up-system)
9. [Pseudo-3D Base Stages](#9-pseudo-3d-base-stages)
10. [Scoring System](#10-scoring-system)
11. [UI Layout & HUD](#11-ui-layout--hud)
12. [Audio Design](#12-audio-design)
13. [Animation System](#13-animation-system)
14. [Lives & Continue System](#14-lives--continue-system)

---

## 1. Game Overview

- **Genre**: Run-and-gun / side-scrolling shooter
- **Perspective**: 2D side-scrolling (stages 1,3,4,5,6,7,8) and pseudo-3D behind-the-back (stages 2,4)
- **Players**: 1-2 simultaneous players
- **Input**: D-pad (8-way aiming) + 2 buttons (Shoot, Jump)
- **Objective**: Progress through 8 stages to defeat the alien forces of Red Falcon.
- **Lose Condition**: Losing all lives ends the game.
- **Special**: The Konami Code (Up Up Down Down Left Right Left Right B A Start) grants 30 lives at the title screen.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| NES resolution | 256 x 240 pixels |
| Recommended implementation | 512 x 480 or 1024 x 960 |
| Orientation | Landscape |
| Frame rate | 60 FPS (NTSC) |
| Tile size | 8 x 8 pixels (16 x 16 metatiles) |
| Sprite limit | 8 sprites per scanline (NES limitation) |

### Coordinate System

- Origin (0, 0) at top-left.
- Side-scrolling stages scroll left-to-right.
- Some sections scroll vertically (upward).
- Base stages use pseudo-3D perspective.

### Game Loop

```
1. Process input (D-pad direction, button presses)
2. Update player position and state
3. Update 8-way aiming direction
4. Update all player projectiles
5. Update all enemy AI and positions
6. Update enemy projectiles
7. Check player-enemy collisions (instant death)
8. Check projectile-enemy collisions
9. Check player-pickup collisions
10. Update scroll position
11. Spawn enemies based on scroll triggers
12. Update score
13. Render (background → enemies → player → projectiles → UI)
```

---

## 3. Player Character Mechanics

### Characters

| Character | Player | Description |
|-----------|--------|-------------|
| Bill Rizer | Player 1 | Blue pants, no shirt, headband |
| Lance Bean | Player 2 | Red pants, no shirt, headband |

### Movement

| Action | Speed (pixels/frame) | Input |
|--------|---------------------|-------|
| Walk right | 2 px/frame (120 px/s) | D-pad right |
| Walk left | 2 px/frame | D-pad left |
| Jump | Vertical: 5 px/frame initial, gravity 0.4 px/frame^2 | Jump button |
| Jump height | ~48 pixels maximum | — |
| Prone (lie flat) | Immediate state change | D-pad down (on ground) |
| Swim (water sections) | 1.5 px/frame | D-pad left/right in water |

### 8-Way Aiming

The player can aim in 8 directions using the D-pad:

| D-pad Input | Aim Direction | Angle |
|-------------|--------------|-------|
| Right | Forward | 0 degrees |
| Right + Up | Diagonal up-right | 45 degrees |
| Up | Straight up | 90 degrees |
| Left + Up | Diagonal up-left | 135 degrees |
| Left | Backward | 180 degrees |
| Left + Down | Diagonal down-left | 225 degrees (while jumping) |
| Down | Straight down | 270 degrees (while jumping only) |
| Right + Down | Diagonal down-right | 315 degrees (while jumping) |

**Note**: Down-aiming is only possible while airborne. On the ground, pressing Down causes the player to go prone.

### Player States

| State | Hitbox (W x H pixels) | Description |
|-------|----------------------|-------------|
| Standing | 8 x 24 | Normal upright |
| Walking | 8 x 24 | Moving left/right |
| Prone | 16 x 8 | Lying flat (D-pad down on ground) |
| Jumping | 8 x 24 | Airborne |
| Swimming | 8 x 16 | In water, only upper body exposed |
| Climbing | 8 x 24 | On ladder or hanging from rail |
| Dead | N/A | Death animation (flies backward) |

### Jumping Mechanics

| Property | Value |
|----------|-------|
| Jump velocity (initial) | -5 px/frame upward |
| Gravity | 0.4 px/frame^2 |
| Jump duration | ~25 frames (0.42 seconds) |
| Maximum jump height | ~48 pixels |
| Air control | Full horizontal control while airborne |
| Variable jump | Release jump early for shorter jump |
| Platform drop-through | Down + Jump on thin platforms drops through |

### Water Mechanics (Stage 1)

- Player submerges to chest height.
- Movement speed reduced to 75%.
- Can still shoot in all upward directions.
- Cannot go prone.
- Jump height reduced by 30%.

---

## 4. Weapon System

### Default Weapon: Rifle

| Property | Value |
|----------|-------|
| Damage | 1 per shot |
| Fire rate | ~7 shots/second (manual rapid press) |
| Max on-screen bullets | 4 |
| Projectile speed | 6 px/frame (360 px/s) |
| Projectile size | 4 x 4 pixels |
| Direction | Matches player's 8-way aim |

### Special Weapons

All special weapons are obtained from Flying Capsules (Falcons) or Sensor Bombs.

#### Machine Gun (M)

| Property | Value |
|----------|-------|
| Damage | 1 per shot |
| Fire rate | ~12 shots/second (hold button for auto-fire) |
| Max on-screen bullets | 6 |
| Projectile speed | 6 px/frame |
| Key feature | Auto-fire (hold shoot button) |

#### Spread Gun (S)

| Property | Value |
|----------|-------|
| Damage | 1 per shot |
| Fire rate | ~5 shots/second |
| Bullets per shot | 5 (fan pattern) |
| Spread angle | ~60 degrees total (15 degrees between each bullet) |
| Max on-screen | 20 (5 per volley x 4 volleys) |
| Projectile speed | 6 px/frame |
| Key feature | Most powerful weapon overall due to coverage |

#### Laser (L)

| Property | Value |
|----------|-------|
| Damage | 3 per hit (pierces through enemies) |
| Fire rate | ~3 shots/second |
| Max on-screen | 1 (only one laser beam at a time) |
| Projectile speed | 8 px/frame |
| Projectile size | 24 x 2 pixels (long beam) |
| Key feature | Penetrates all enemies in a line |
| Drawback | Only 1 beam on screen at a time; slow fire rate |

#### Fire Ball (F)

| Property | Value |
|----------|-------|
| Damage | 1 per hit |
| Fire rate | ~5 shots/second |
| Max on-screen | 4 |
| Projectile speed | 5 px/frame |
| Behavior | Spirals forward in a corkscrew pattern |
| Spiral radius | 8 pixels |
| Spiral speed | 720 degrees/second |
| Key feature | Wider coverage due to spiral path |

#### Rapid Fire (R)

| Property | Value |
|----------|-------|
| Effect | Increases fire rate of current weapon by ~50% |
| Stacking | Does not stack (collecting second R has no additional effect) |
| Application | Applied on top of any weapon (including default) |
| Note | Not a weapon itself; a weapon modifier |

### Weapon Loss

- Player loses their current special weapon upon death.
- Respawn always starts with the default rifle.
- Rapid Fire modifier is also lost on death.

---

## 5. Enemy System

### 5.1 Common Enemies (Side-Scrolling Stages)

#### Running Soldier

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 (contact or bullet) |
| Speed | 1.5 px/frame |
| Behavior | Runs toward player, may jump, may fire |
| Fire rate | 1 shot every 2-3 seconds |
| Bullet speed | 3 px/frame |
| Score | 100 |
| Spawn | Continuously from screen edges based on scroll triggers |

#### Sniper (Stationary Soldier)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 |
| Behavior | Stands in fixed position, aims at player and fires |
| Fire rate | 1 shot every 1.5 seconds |
| Score | 100 |

#### Turret (Wall-Mounted)

| Property | Value |
|----------|-------|
| HP | 3 |
| Damage | 1 per bullet |
| Behavior | Rotates to track player, fires in aimed direction |
| Fire rate | 1 shot every 1 second |
| Score | 500 |

#### Cannon (Embedded)

| Property | Value |
|----------|-------|
| HP | 5 |
| Damage | 1 per shell |
| Behavior | Fires in fixed direction at regular intervals |
| Fire rate | 1 shell every 2 seconds |
| Shell speed | 2 px/frame |
| Score | 500 |

#### Rock Boulder (Stage 3)

| Property | Value |
|----------|-------|
| HP | Invincible |
| Damage | 1 (instant death on contact) |
| Behavior | Rolls down slopes, bounces off ledges |
| Speed | 3 px/frame |
| Score | N/A (cannot be killed) |

#### Xenomorph (Alien Runner, Stage 7-8)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 |
| Speed | 2.5 px/frame (fast) |
| Behavior | Leaps from walls/ceiling, charges at player |
| Score | 300 |

#### Wall Crawler (Alien, Stage 7-8)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 |
| Behavior | Crawls along walls/ceiling, drops toward player |
| Score | 200 |

### 5.2 Flying Enemies

#### Bridge Bombs (Stage 1)

| Property | Value |
|----------|-------|
| HP | Invincible (environmental hazard) |
| Behavior | Explosions destroy bridge sections beneath player |
| Timing | Triggered by player position |

#### Dive Bomber

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 |
| Speed | 3 px/frame |
| Behavior | Flies from right, dives toward player's position |
| Score | 200 |

### 5.3 Spawn System

- Enemies spawn from screen edges based on scroll position triggers.
- Each screen position has a spawn table defining which enemies appear.
- Infinite respawn soldiers (capped at 3-4 on screen simultaneously).
- Boss enemies are unique per encounter.
- Turrets and cannons are part of the level geometry.

---

## 6. Level Design — All 8 Stages

### Stage 1: Jungle

| Property | Value |
|----------|-------|
| Orientation | Horizontal scrolling |
| Length | ~2560 pixels (10 screen widths) |
| Terrain | Jungle, river crossing, fortress entrance |
| Enemies | Running soldiers, snipers, bridge bombs |
| Hazards | Water (slows movement), falling bridges |
| Power-ups | 3 Falcons (S, M, R) |
| Boss | Defense wall with core |
| Difficulty | Easy |

### Stage 2: Base 1

| Property | Value |
|----------|-------|
| Orientation | Pseudo-3D (behind-the-back view) |
| Rooms | 5 rooms, each with a defense system |
| Enemies | Soldiers emerging from doors, grenade rollers |
| Hazards | Electric barriers (timed) |
| Power-ups | 2 (varies) |
| Boss | Core at end of corridor |
| Difficulty | Easy-Medium |

### Stage 3: Waterfall

| Property | Value |
|----------|-------|
| Orientation | Vertical scrolling (upward) |
| Height | ~2400 pixels |
| Terrain | Rocky waterfall cliff face |
| Enemies | Snipers on ledges, falling boulders, turrets |
| Hazards | Falling boulders (indestructible), falling off ledges |
| Power-ups | 3 Falcons |
| Boss | Top-of-cliff defense system |
| Difficulty | Medium |

### Stage 4: Base 2

| Property | Value |
|----------|-------|
| Orientation | Pseudo-3D |
| Rooms | 5 rooms, more complex than Base 1 |
| Enemies | More soldiers, rollers, ceiling guns |
| Hazards | Electric barriers (faster timing) |
| Power-ups | 2 (varies) |
| Boss | Core with additional turrets |
| Difficulty | Medium |

### Stage 5: Snow Field

| Property | Value |
|----------|-------|
| Orientation | Horizontal scrolling |
| Length | ~3072 pixels |
| Terrain | Snowy landscape, bunkers, trenches |
| Enemies | Soldiers, tanks, mortar emplacements |
| Hazards | Grenades from off-screen, mortar fire |
| Power-ups | 3 Falcons (S, L, R) |
| Boss | Twin turret defense system |
| Difficulty | Medium-Hard |

### Stage 6: Energy Zone

| Property | Value |
|----------|-------|
| Orientation | Horizontal scrolling |
| Length | ~3072 pixels |
| Terrain | Industrial/mechanical facility, fire hazards |
| Enemies | Soldiers, fire emitters, mechanical traps |
| Hazards | Periodic fire jets, moving platforms |
| Power-ups | 3 Falcons |
| Boss | Rotating defense system with fire |
| Difficulty | Hard |

### Stage 7: Hangar

| Property | Value |
|----------|-------|
| Orientation | Horizontal scrolling |
| Length | ~3072 pixels |
| Terrain | Alien-infested hangar/cave |
| Enemies | Xenomorphs, wall crawlers, alien pods |
| Hazards | Alien pods that spawn enemies when destroyed |
| Power-ups | 3 Falcons |
| Boss | Alien defense wall |
| Difficulty | Hard |

### Stage 8: Alien's Lair

| Property | Value |
|----------|-------|
| Orientation | Horizontal scrolling |
| Length | ~3584 pixels |
| Terrain | Organic alien cave, living walls |
| Enemies | Xenomorphs, face huggers, spawning eggs |
| Hazards | Living wall mouths that fire projectiles |
| Power-ups | 3 Falcons (often S) |
| Boss | Red Falcon (final boss — alien heart) |
| Difficulty | Very Hard |

---

## 7. Boss Encounters

### Stage 1 Boss: Fortress Gate

| Property | Value |
|----------|-------|
| HP (Core) | 30 |
| HP (Side turrets) | 10 each |
| Attacks | Turrets fire aimed shots; soldiers spawn from doors |
| Strategy | Destroy side turrets first, then target the core |
| Score | 3,000 |

### Stage 2 Boss: Base Core

| Property | Value |
|----------|-------|
| HP | 20 |
| Attacks | Fires energy rings outward |
| Defense | Electric barrier cycles on/off every 2 seconds |
| Score | 5,000 |

### Stage 3 Boss: Waterfall Top Defense

| Property | Value |
|----------|-------|
| HP | 25 |
| Attacks | Dual cannons fire downward, soldier spawns |
| Score | 3,000 |

### Stage 4 Boss: Enhanced Base Core

| Property | Value |
|----------|-------|
| HP | 30 |
| Attacks | Faster energy rings, turret support |
| Score | 5,000 |

### Stage 5 Boss: Defense Wall

| Property | Value |
|----------|-------|
| HP (each turret) | 15 |
| HP (main core) | 25 |
| Attacks | Twin turrets + grenade lobbers |
| Score | 5,000 |

### Stage 6 Boss: Energy Core

| Property | Value |
|----------|-------|
| HP | 35 |
| Attacks | Rotating fire arms, energy projectiles |
| Score | 5,000 |

### Stage 7 Boss: Alien Defense

| Property | Value |
|----------|-------|
| HP | 40 |
| Attacks | Spawns xenomorphs, fires acid projectiles |
| Score | 5,000 |

### Stage 8 Final Boss: Red Falcon Heart

| Property | Value |
|----------|-------|
| HP (Phase 1: Face) | 50 |
| HP (Phase 2: Heart) | 50 |
| Phase 1 attacks | Face fires energy rings, spawns face huggers |
| Phase 2 attacks | Heart fires rapid projectiles in all directions, spawns xenomorphs |
| Score | 50,000 |
| Victory | Stage cleared = game complete |

---

## 8. Power-Up System

### Flying Capsules (Falcons)

| Property | Value |
|----------|-------|
| Appearance | Flying winged pod, moves horizontally across screen |
| Speed | 2 px/frame |
| HP | 1 (one shot to destroy) |
| Behavior | Flies across screen; destroying it releases the contained power-up |
| Drop | Weapon letter icon that drifts slowly downward |

### Sensor Bombs (Ground Pods)

| Property | Value |
|----------|-------|
| Appearance | Red sensor pod on the ground |
| HP | 1 |
| Behavior | Stationary; shooting it releases the power-up |
| Drop | Same as Falcon drops |

### Power-Up Items

| Letter | Weapon | Color |
|--------|--------|-------|
| M | Machine Gun | Blue |
| S | Spread Gun | Red |
| L | Laser | Blue |
| F | Fire Ball | Red |
| R | Rapid Fire (modifier) | Red |
| B | Barrier (invincibility ~15 seconds) | Red |

### Barrier (B) Details

| Property | Value |
|----------|-------|
| Duration | ~15 seconds (~900 frames) |
| Effect | Complete invincibility; player flashes |
| Visual | Player sprite flickers rapidly |
| Note | Very rare; appears only in specific locations |

---

## 9. Pseudo-3D Base Stages

### Overview (Stages 2 and 4)

These stages use a behind-the-back perspective looking down a corridor.

### Base Stage Layout

```
┌──────────────────────────────────────┐
│                                      │
│     ┌─────┐  ┌─────┐  ┌─────┐      │
│     │ Door│  │ Core │  │ Door│      │
│     └─────┘  └─────┘  └─────┘      │
│                                      │
│            Player (P)                │
│              ↑                       │
│     [Left]  [Center]  [Right]        │
│                                      │
│     ←── Movement positions ──→       │
└──────────────────────────────────────┘
```

### Movement

| Action | Input | Description |
|--------|-------|-------------|
| Move left | D-pad left | Shift to left position |
| Move right | D-pad right | Shift to right position |
| Positions | 3 horizontal positions | Left, Center, Right |
| Aim | Fixed (straight ahead into screen) | Cannot aim up/down/diagonal |

### Base Stage Mechanics

- Player faces away from camera, shooting into the corridor.
- Enemies run toward the player from the far end.
- Doors on left and right sides open to spawn enemies.
- The core (center target) must be destroyed to proceed.
- Each room has a defense system that must be destroyed.
- Electric barriers flash on/off (must time shots between barrier cycles).

### Base Stage Enemies

| Enemy | Behavior | HP |
|-------|----------|-----|
| Running soldier | Runs toward camera, fires at player | 1 |
| Grenade roller | Rolls grenades along the floor toward player | 1 |
| Ceiling gun | Mounted gun that fires downward | 3 |
| Core defense | Fires energy rings that expand outward | Varies |

### Room Progression

Each base stage has 5 rooms:
1. Destroy the core in each room.
2. Advance to the next room (screen scrolls forward).
3. Final room contains the boss core.

---

## 10. Scoring System

### Kill Scores

| Enemy | Score |
|-------|-------|
| Running soldier | 100 |
| Sniper | 100 |
| Turret | 500 |
| Cannon | 500 |
| Dive bomber | 200 |
| Xenomorph | 300 |
| Wall crawler | 200 |
| Base soldier | 100 |
| Boss (varies) | 3,000-50,000 |

### Stage Clear Bonuses

| Bonus | Points |
|-------|--------|
| Stage clear base | 10,000 |
| No deaths bonus | 20,000 (if cleared without dying) |

### Extra Lives from Score

| Score Threshold | Lives Awarded |
|----------------|--------------|
| 20,000 | 1 extra life |
| 60,000 | 1 extra life |
| Every 60,000 after | 1 extra life |

---

## 11. UI Layout & HUD

### 11.1 In-Game HUD

```
┌──────────────────────────────────────┐
│ 1UP  HI-SCORE  2UP                  │
│ 025400  078600  012800               │
│ ♦♦♦      REST 02                     │
│                                      │
│                                      │
│     [Game playfield area]            │
│                                      │
│                                      │
│                                      │
└──────────────────────────────────────┘
```

### HUD Elements

| Element | Position | Format |
|---------|----------|--------|
| 1UP Score | Top-left | 6-digit number |
| HI-SCORE | Top-center | 6-digit number |
| 2UP Score | Top-right | 6-digit number |
| Lives remaining | Below 1UP score | "REST XX" (or life icons) |

### 11.2 Title Screen

```
┌──────────────────────────────────────┐
│                                      │
│         C O N T R A                  │
│                                      │
│       1 PLAYER                       │
│       2 PLAYERS                      │
│                                      │
│   (C) 1988 KONAMI                    │
└──────────────────────────────────────┘
```

### 11.3 Stage Introduction

```
┌──────────────────────────────────────┐
│                                      │
│         STAGE 1                      │
│                                      │
│         JUNGLE                       │
│                                      │
│      PLAYER 1: REST 02              │
│                                      │
└──────────────────────────────────────┘
```

Displayed for 3 seconds before stage begins.

---

## 12. Audio Design

### 12.1 Music

| Track | Stage/Context | Style |
|-------|--------------|-------|
| Title Theme | Title screen | Militaristic, foreboding |
| "Jungle" | Stage 1: Jungle | Iconic opening riff, driving rock |
| "Base 1" | Stage 2: Base 1 | Tense, electronic pulse |
| "Waterfall" | Stage 3: Waterfall | Rising intensity, heroic |
| "Base 2" | Stage 4: Base 2 | More intense version of Base 1 |
| "Snow Field" | Stage 5: Snow Field | Cold, determined marching rhythm |
| "Energy Zone" | Stage 6: Energy Zone | Fast-paced, mechanical |
| "Hangar" | Stage 7: Hangar | Ominous, alien atmosphere |
| "Alien's Lair" | Stage 8: Alien's Lair | Dark, urgent, climactic |
| "Boss Theme" | All bosses | Intense, driving rhythm |
| "Stage Clear" | After beating stage | Short triumphant fanfare |
| "Game Over" | Game over screen | Somber, brief |
| "Ending" | Credits/ending | Heroic, triumphant |

### 12.2 Sound Effects

| Event | Description |
|-------|-------------|
| Player shot (rifle) | Short "pew" |
| Player shot (spread) | Wider "pew-pew" |
| Player shot (laser) | Long "bzzzz" |
| Player shot (fire) | Sizzling "fwoosh" |
| Player shot (machine) | Rapid "rat-tat-tat" |
| Enemy shot | Lower-pitched "pew" |
| Explosion (small) | Short "boom" |
| Explosion (large/boss) | Deep, sustained "BOOM" |
| Player death | Brief "death" jingle |
| Player jump | Light "hop" sound |
| Power-up appear | Rising chime |
| Power-up collect | Bright "ding" |
| Barrier activate | Shimmering sound |
| Boss damage | Impact "thud" |
| Extra life | 1-UP jingle |
| Falling into pit | Descending tone |
| Water splash | Splash sound |

---

## 13. Animation System

### 13.1 Player Animations

| Animation | Frames | Rate | Trigger |
|-----------|--------|------|---------|
| Idle (stand) | 1 | Static | No input |
| Walk | 3 | 10 FPS | D-pad left/right |
| Jump | 4 (flip rotation) | 15 FPS | Jump button |
| Prone | 1 | Static | D-pad down on ground |
| Shoot (stand) | 2 | 15 FPS | Shoot button |
| Shoot (up) | 2 | 15 FPS | Shoot + D-pad up |
| Shoot (diagonal) | 2 | 15 FPS | Shoot + diagonal |
| Shoot (prone) | 2 | 15 FPS | Shoot while prone |
| Swim | 2 | 8 FPS | In water |
| Climb | 2 | 8 FPS | On ladder |
| Death | 3 | 8 FPS | Hit by enemy/projectile |
| Respawn | Flash | 60 FPS flicker | After death, dropping in from top |

### 13.2 Enemy Animations

| Enemy | Animation States |
|-------|-----------------|
| Running soldier | Run (3 frames), Shoot (2 frames), Death (2 frames) |
| Sniper | Idle (1), Aim (1), Shoot (2), Death (2) |
| Turret | Rotate (8 directional sprites), Fire (2 frames), Explosion (4 frames) |
| Xenomorph | Run (4 frames), Leap (3 frames), Death (3 frames) |

### 13.3 Visual Effects

| Effect | Frames | Description |
|--------|--------|-------------|
| Small explosion | 4 | Bullet impact on destructible object |
| Medium explosion | 6 | Enemy vehicle/turret destruction |
| Large explosion | 8 | Boss destruction |
| Bullet impact (wall) | 2 | Spark on indestructible surface |
| Water splash | 3 | Player entering/leaving water |
| Power-up sparkle | 4 (loop) | Floating weapon letter |

---

## 14. Lives & Continue System

### Lives

| Property | Value |
|----------|-------|
| Starting lives | 3 (or 30 with Konami Code) |
| Maximum lives | 29 (display cap) |
| Extra life at | 20,000 points, then every 60,000 |
| Death condition | Any enemy contact, any enemy projectile, falling into pit |
| Respawn | Instant at last position (side-scroll) or start of room (base) |
| Invincibility after respawn | ~2 seconds (player flashes) |

### Konami Code

| Sequence | At Title Screen |
|----------|----------------|
| Up, Up, Down, Down, Left, Right, Left, Right, B, A, Start | Grants 30 lives |
| 2-player variant | Up, Up, Down, Down, Left, Right, Left, Right, B, A, Select, Start | Both players get 30 lives |

### Continue System (NES Version)

| Property | Value |
|----------|-------|
| Continues | Unlimited (NES version) |
| Continue behavior | Restart at the beginning of the current stage |
| Score on continue | Reset to 0 |
| Lives on continue | Reset to 3 |

### Game Completion

- After defeating Stage 8's final boss, the ending sequence plays.
- The island explodes; the heroes escape in a helicopter.
- Credits roll with ending music.
- Second loop: Game restarts from Stage 1 with increased difficulty (more enemies, faster projectiles). Score carries over.

---

## Appendix A: Quick Reference — Weapon Comparison

| Weapon | Damage | Fire Rate | Max On-Screen | Best For |
|--------|--------|-----------|---------------|----------|
| Rifle | 1 | 7/s | 4 | Default fallback |
| Machine Gun (M) | 1 | 12/s (auto) | 6 | Sustained fire |
| Spread (S) | 1x5 | 5/s | 20 | Everything (best weapon) |
| Laser (L) | 3 | 3/s | 1 | Single tough targets |
| Fire Ball (F) | 1 | 5/s | 4 | Coverage |
| Rapid Fire (R) | — | +50% rate | — | Modifier, stacks with any |

## Appendix B: Quick Reference — Stage Summary

| Stage | Type | Length | Boss | Difficulty |
|-------|------|--------|------|-----------|
| 1 Jungle | Side-scroll | 2560 px | Fortress Gate | Easy |
| 2 Base 1 | Pseudo-3D | 5 rooms | Core | Easy-Medium |
| 3 Waterfall | Vertical scroll | 2400 px | Top Defense | Medium |
| 4 Base 2 | Pseudo-3D | 5 rooms | Enhanced Core | Medium |
| 5 Snow Field | Side-scroll | 3072 px | Defense Wall | Medium-Hard |
| 6 Energy Zone | Side-scroll | 3072 px | Energy Core | Hard |
| 7 Hangar | Side-scroll | 3072 px | Alien Defense | Hard |
| 8 Alien's Lair | Side-scroll | 3584 px | Red Falcon | Very Hard |

## Appendix C: Quick Reference — Enemy HP

| Enemy | HP | Score |
|-------|-----|-------|
| All infantry | 1 | 100 |
| Turret | 3 | 500 |
| Cannon | 5 | 500 |
| Dive bomber | 1 | 200 |
| Xenomorph | 1 | 300 |
| Boss cores | 20-50 | 3,000-50,000 |

---

*This specification is based on Contra (1988) by Konami for the Nintendo Entertainment System (NES). Values are sourced from gameplay analysis, ROM data examination, and community documentation. The arcade version has some differences in mechanics and content.*
