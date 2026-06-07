# Jetpack Joyride — Complete Game Specification

> A comprehensive specification for faithfully recreating Jetpack Joyride (Halfbrick Studios, 2011). This document covers every system, mechanic, entity, and interaction required for a full clone of this endless side-scrolling action game.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Movement Mechanics](#3-core-movement-mechanics)
4. [Level Generation System](#4-level-generation-system)
5. [Obstacle System](#5-obstacle-system)
6. [Coin System](#6-coin-system)
7. [Vehicle System](#7-vehicle-system)
8. [Scientist & Environment NPCs](#8-scientist--environment-npcs)
9. [Gadget System](#9-gadget-system)
10. [Mission System](#10-mission-system)
11. [Scoring & Distance](#11-scoring--distance)
12. [Shop & Economy](#12-shop--economy)
13. [Slot Machine (Final Spin)](#13-slot-machine-final-spin)
14. [UI Layout & Screen Flow](#14-ui-layout--screen-flow)
15. [Visual Design & Animation](#15-visual-design--animation)
16. [Audio Design](#16-audio-design)
17. [Progression System](#17-progression-system)

---

## 1. Game Overview

- **Genre**: Endless runner / side-scroller
- **Perspective**: 2D side-view, horizontal scrolling
- **Input**: Single-button (touch screen = hold to fire jetpack upward, release to fall). Mouse click or spacebar for desktop.
- **Objective**: Travel as far as possible through an endless laboratory, avoiding obstacles, collecting coins, and completing missions.
- **Lose Condition**: Barry collides with any obstacle (zappers, missiles, lasers). Death triggers the Final Spin slot machine.
- **Setting**: Legitimate Research facility. Barry Steakfries breaks in and steals an experimental jetpack.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Original resolution | 480 x 320 (iPhone), scales to device |
| Recommended implementation | 1920 x 1080 |
| Orientation | Landscape |
| Frame rate target | 60 FPS |
| Scroll direction | Right-to-left (player moves left-to-right conceptually) |

### Coordinate System

- Origin (0, 0) at bottom-left.
- Player character is positioned at a fixed X (~15-20% from left edge).
- Background and obstacles scroll from right to left.
- Floor at y = 0; ceiling at y = screen_height.

### Game Loop

```
1. Process input (touch/release state)
2. Apply thrust or gravity to player
3. Clamp player Y position (floor/ceiling bounds)
4. Advance scroll position (increasing game speed)
5. Generate new level segments if needed
6. Update all obstacle positions (scroll leftward)
7. Update coin positions (scroll leftward)
8. Check collisions (player vs obstacles)
9. Check coin collection (player vs coins)
10. Check vehicle pickup collisions
11. Update vehicle-specific behavior
12. Update scientist NPCs
13. Update particle effects (jetpack flame, etc.)
14. Update missions progress
15. Render (background → lab elements → coins → obstacles → player → UI)
```

### Physics Constants

| Constant | Value |
|----------|-------|
| Gravity | 1200 pixels/s^2 downward |
| Jetpack thrust | 2400 pixels/s^2 upward |
| Maximum upward velocity | 600 pixels/s |
| Maximum downward velocity | 800 pixels/s |
| Terminal fall velocity | 800 pixels/s |
| Floor Y position | 80 pixels (above screen bottom, accounting for floor art) |
| Ceiling Y position | screen_height - 60 pixels |
| Player hitbox width | 40 pixels |
| Player hitbox height | 70 pixels |

---

## 3. Core Movement Mechanics

### Barry Steakfries

| Property | Value |
|----------|-------|
| Default position X | 15% of screen width from left edge |
| Hitbox | 40 x 70 pixels (rectangle) |
| States | Running, Flying, Falling, Vehicle, Dead |

### Jetpack Physics

When the player **holds the input button**:
- Apply upward thrust: acceleration = 2400 px/s^2 upward
- Velocity is capped at 600 px/s upward
- Jetpack flame particle effect emits downward
- Scientists below the jetpack flame are knocked down

When the player **releases the input button**:
- Gravity applies: acceleration = 1200 px/s^2 downward
- Velocity is capped at 800 px/s downward
- Barry falls with a slight forward lean animation

### Movement Feel

```
Position update per frame:
  if (input_held):
    velocity.y += thrust * delta_time
    velocity.y = min(velocity.y, max_upward_velocity)
  else:
    velocity.y -= gravity * delta_time
    velocity.y = max(velocity.y, -max_downward_velocity)

  position.y += velocity.y * delta_time
  position.y = clamp(position.y, floor_y, ceiling_y)

  if (position.y == floor_y):
    velocity.y = 0  // Landing
    state = RUNNING
  elif (position.y == ceiling_y):
    velocity.y = 0  // Ceiling bump
```

### Running Animation

- When Barry is on the floor (y = floor_y) and not holding input, he runs.
- Running animation: 8-frame cycle at 12 FPS.
- Footstep dust particles emit from feet every 4th frame.

---

## 4. Level Generation System

### Segment-Based Generation

The level is composed of scrolling segments that are procedurally selected.

| Property | Value |
|----------|-------|
| Segment width | 1920 pixels (one screen width) |
| Buffer segments | 2 segments ahead of current view |
| Scroll speed (initial) | 400 pixels/second |
| Scroll speed (maximum) | 900 pixels/second |
| Speed increase rate | +2 pixels/second per second elapsed |
| Time to reach max speed | ~250 seconds |

### Background Layers (Parallax)

| Layer | Scroll Speed (relative to game scroll) | Content |
|-------|----------------------------------------|---------|
| Far background | 0.1x | Sky/exterior through windows |
| Mid background | 0.3x | Lab walls, pipes, panels |
| Near background | 0.6x | Equipment, shelves, monitors |
| Floor/Ceiling | 1.0x | Metal floor panels, ceiling lights |
| Foreground (decorative) | 1.2x | Occasional foreground elements |

### Lab Section Themes

The laboratory has visual variety through themed sections:

| Section | Visual Style | Frequency |
|---------|-------------|-----------|
| Standard Lab | White/grey walls, monitors, equipment | 40% |
| Bio Lab | Green tanks, specimens, organic pipes | 15% |
| Engineering Bay | Orange/brown, gears, machinery | 15% |
| Server Room | Blue-lit, server racks, cables | 10% |
| Hallway | Corridor with doors, windows | 10% |
| Warehouse | Crates, shelving, dim lighting | 10% |

Section transitions occur every 3000-5000 pixels with a brief visual blend.

---

## 5. Obstacle System

### 5.1 Zappers

| Property | Value |
|----------|-------|
| Appearance | Two electrified poles connected by a beam of electricity |
| Hitbox | Rectangle between the two poles, width = pole separation, height = beam thickness |
| Beam thickness | 40 pixels |
| Orientations | Horizontal, Vertical, Diagonal (45-degree) |
| Pole length | 60 pixels each |
| Total obstacle size | 60-300 pixels depending on orientation |
| Animation | Electric beam flickers at 15 FPS, sparks emit at poles |
| Warning | None (static obstacles, visible on screen) |

#### Zapper Configurations

| Configuration | Description | Placement |
|--------------|-------------|-----------|
| Floor horizontal | Poles on floor and ~120px up, beam horizontal | Ground level |
| Ceiling horizontal | Poles at ceiling and ~120px down | Ceiling level |
| Vertical | Poles side by side, beam vertical | Any Y range |
| Diagonal (up) | 45-degree angle, floor-left to ceiling-right | Spanning height |
| Diagonal (down) | 45-degree angle, ceiling-left to floor-right | Spanning height |
| Mid-air horizontal | Floating in the middle of the screen | Mid-screen |
| Spinning | Rotates around its center at 60 deg/s | Any position |
| Double | Two zappers forming a gap | Creates passage |

### 5.2 Missiles

| Property | Value |
|----------|-------|
| Appearance | Red/silver missile with flame trail |
| Hitbox | 80 x 30 pixels (rectangle) |
| Speed | 800-1200 pixels/second (from right to left) |
| Warning time | ~1.5 seconds before arrival |
| Warning indicator | Flashing "!" icon on right edge at the Y-level the missile will travel |
| Tracking | Missile locks onto Barry's Y position at warning time, then travels in a straight line at that Y |

#### Missile Behavior Sequence

```
1. Warning phase (1.5s):
   - "!" icon appears on right screen edge
   - Y position = Barry's current Y at warning start
   - Audio: rising siren sound

2. Launch phase:
   - Missile appears at right edge at locked Y
   - Travels left at constant speed
   - Flame trail particles emit from rear

3. Collision or pass:
   - If hitting Barry: explosion, death
   - If passing off-screen left: despawn
```

#### Missile Frequency

| Distance | Missile Interval |
|----------|-----------------|
| 0-500m | No missiles |
| 500-1500m | Every 8-12 seconds |
| 1500-3000m | Every 5-8 seconds |
| 3000-5000m | Every 3-6 seconds |
| 5000m+ | Every 2-5 seconds |

### 5.3 Lasers

| Property | Value |
|----------|-------|
| Appearance | Red beam spanning floor-to-ceiling or partial height |
| Hitbox | Full beam width (20 pixels wide), height varies |
| Warning time | ~2 seconds |
| Warning indicator | Red glow at laser source points, pulsing |
| Active duration | 1.5 seconds |
| Cooldown | 0.5 seconds (laser off) |
| Cycle | Warning → Active → Off → Active → Off → Deactivate |

#### Laser Configurations

| Type | Description |
|------|-------------|
| Full vertical | Floor to ceiling, blocks all movement |
| Half vertical (bottom) | Floor to mid-screen |
| Half vertical (top) | Mid-screen to ceiling |
| Horizontal sweep | Beam sweeps vertically (moves up/down) |
| Triple laser | Three parallel vertical beams with gaps |

#### Laser Behavior Sequence

```
1. Warning phase (2.0s):
   - Laser source nodes glow red, pulsing
   - Thin red targeting line appears (10% opacity)
   - Audio: charging hum, rising pitch

2. Active phase:
   - Full-power beam activates (deadly)
   - Bright red with glow effect
   - Stays active for 1.5 seconds
   - Audio: sustained buzz

3. Deactivate:
   - Beam turns off
   - Nodes stop glowing
   - Safe to pass
```

### 5.4 Obstacle Frequency by Distance

| Distance (m) | Zapper Density | Missile Rate | Laser Rate |
|-------------|----------------|-------------|------------|
| 0-200 | Low (1 per 400px) | None | None |
| 200-500 | Medium (1 per 300px) | None | None |
| 500-1000 | Medium-High | Low | None |
| 1000-2000 | High (1 per 200px) | Medium | Low |
| 2000-3500 | High | Medium-High | Medium |
| 3500-5000 | Very High (1 per 150px) | High | Medium-High |
| 5000+ | Maximum | High | High |

---

## 6. Coin System

### Coin Types

| Coin | Value | Appearance | Size |
|------|-------|-----------|------|
| Standard coin | 1 | Gold circular coin, spinning | 24 x 24 px |
| Double coin (magnet) | 1 (attracted) | Same as standard | 24 x 24 px |

### Coin Patterns

Coins are placed in formations that encourage skillful navigation:

| Pattern | Description | Coin Count |
|---------|-------------|-----------|
| Line (horizontal) | Row of coins at constant Y | 5-10 |
| Line (vertical) | Column of coins at constant X | 3-6 |
| Diagonal line | Coins in ascending/descending line | 5-8 |
| Arc | Coins following a parabolic arc | 8-12 |
| Circle/Ring | Coins in a circular arrangement | 8-10 |
| Zigzag | Alternating up-down pattern | 6-10 |
| Arrow | Arrow shape pointing in scroll direction | 7 |
| Heart | Heart shape | 12 |
| Letter (J, H, etc.) | Coins forming a letter | 8-15 |
| Filled rectangle | Dense rectangle of coins | 12-20 |

### Coin Collection

| Property | Value |
|----------|-------|
| Collection radius | 30 pixels from player center |
| Magnet collection radius | 300 pixels (with Coin Magnet gadget) |
| Magnet attraction speed | 1500 pixels/second toward player |
| Coin pickup sound | Light "ding" |
| Score popup | "+1" floats briefly above collection point |

### Spin Token

| Property | Value |
|----------|-------|
| Appearance | Blue/purple token with "S" marking |
| Size | 28 x 28 pixels |
| Spawn rate | ~1 per 1500-2500 pixels of distance |
| Effect | Adds one free spin token for the Final Spin slot machine |
| Placement | Often in challenging positions (near obstacles) |

---

## 7. Vehicle System

### Vehicle Pickup

| Property | Value |
|----------|-------|
| Appearance | Floating vehicle crate/pod with "?" marking |
| Hitbox | 60 x 60 pixels |
| Spawn rate | ~1 per 2000-4000 pixels of distance |
| Collection | Fly into the crate to activate |
| Effect | Barry enters a vehicle. Vehicle acts as an extra life and has unique controls. |
| Vehicle selection | Random from unlocked vehicles |

### Vehicle Properties

When riding a vehicle, the vehicle's hitbox replaces Barry's. If the vehicle is hit by an obstacle, the vehicle is destroyed and Barry tumbles (invincible for ~1 second) before resuming normal jetpack gameplay.

#### 7.1 Bad As Hog (Motorcycle)

| Property | Value |
|----------|-------|
| Hitbox | 100 x 60 pixels |
| Control | Hold input = wheelie (lifts front, jumps ramps). Release = ride flat. |
| Movement | Rides along the floor. Hold input to perform a wheelie/jump. |
| Jump height | Up to 200 pixels |
| Special | Destroys zappers on contact (without damage). Cannot avoid ceiling obstacles. |
| Scientists | Knocks down all scientists on contact |

#### 7.2 Lil' Stomper (Mech Walker)

| Property | Value |
|----------|-------|
| Hitbox | 80 x 100 pixels |
| Control | Hold input = jetpack thrust (same as Barry but heavier). Release = stomp down fast. |
| Stomp speed | 3x normal gravity |
| Special | Screen shake on landing. Destroys floor-level zappers when stomping. |
| Weight feel | Slower upward acceleration (1800 px/s^2 vs 2400) |

#### 7.3 Profit Bird (Flappy Bird-like)

| Property | Value |
|----------|-------|
| Hitbox | 50 x 40 pixels |
| Control | Tap input = flap (impulse upward). Gravity pulls down between flaps. |
| Flap impulse | 500 pixels/second upward (instant velocity set) |
| Gravity | 1400 pixels/s^2 (heavier than normal) |
| Special | Drops eggs that bounce on the floor (cosmetic) |

#### 7.4 Gravity Guy (Gravity Suit)

| Property | Value |
|----------|-------|
| Hitbox | 40 x 70 pixels (same as Barry) |
| Control | Tap input = toggle gravity direction (floor ↔ ceiling). |
| Transition speed | Accelerates at 2000 px/s^2 toward the target surface |
| Special | Barry runs on the ceiling when gravity is flipped. |
| Visual | Barry flips 180 degrees smoothly over 0.2 seconds |

#### 7.5 Crazy Freaking Teleporter

| Property | Value |
|----------|-------|
| Hitbox | 40 x 70 pixels |
| Control | Hold input = rise (same as jetpack). Release = fall. |
| Special | Every 0.5 seconds while held, Barry teleports randomly ±100 pixels vertically. |
| Visual | Flicker/glitch effect during teleportation |
| Difficulty | Hardest vehicle to control |

### Vehicle Destruction

- When a vehicle is hit, it explodes (vehicle-specific explosion animation).
- Barry is thrown upward with a tumble animation.
- Invincibility period: 1.0 seconds after vehicle destruction.
- Barry resumes normal jetpack controls after the tumble.
- Vehicle wreckage slides along the floor briefly.

---

## 8. Scientist & Environment NPCs

### Scientists

| Property | Value |
|----------|-------|
| Appearance | White lab coat, safety goggles |
| Hitbox | None (cannot hurt Barry) |
| Behavior | Walk left-to-right in the lab. Flee when Barry approaches. |
| Knockdown | Jetpack flame or running into them knocks them flat |
| Animation | Walk cycle (6 frames), flee animation (8 frames, faster), knocked-down ragdoll |
| Spawn rate | 1-3 per segment |
| Purpose | Cosmetic / mission objectives ("knock down X scientists") |

### Scientist Types

| Type | Appearance | Behavior |
|------|-----------|----------|
| Standard | White coat | Walks, flees from Barry |
| Female | White coat, ponytail | Same as standard |
| Bald | No hair, glasses | Same, slightly slower flee |

---

## 9. Gadget System

Players can equip **2 gadgets** before each run. Gadgets modify gameplay.

### Gadget List

| Gadget | Effect | Cost (Coins) |
|--------|--------|-------------|
| Coin Magnet | Attracts nearby coins (300px radius) | 5,000 |
| Gravity Belt | Reduces gravity by 30% | 8,000 |
| Air Barrys | Double-tap to activate brief hover (2s) | 10,000 |
| Dezapinator | 10% chance zappers are disabled on approach | 15,000 |
| Token Gift | Start with 1 free spin token | 2,000 |
| Lucky Last | 50% chance to survive first hit | 20,000 |
| Free Ride | Start each run in a random vehicle | 12,000 |
| Nerd Repellent | Scientists flee at greater distance | 1,000 |
| X-Ray Specs | See upcoming obstacles slightly earlier | 7,000 |
| Missile Jammer | 20% chance missiles malfunction | 18,000 |
| Gemology | 10% chance coins are worth double | 15,000 |
| Ezy-Dodge Missiles | Missiles move 15% slower | 12,000 |
| Flash | 200m head start at run beginning | 25,000 |
| Freeze | Obstacles freeze in place for first 5 seconds | 10,000 |
| Turbo Boost | Start with a speed boost for 3 seconds | 8,000 |

### Gadget Upgrades

Some gadgets can be upgraded (up to Level 5):

| Gadget | Upgrade Effect | Cost Per Level |
|--------|---------------|----------------|
| Coin Magnet | +50px radius per level (300→500) | 5,000 per level |
| Dezapinator | +5% chance per level (10%→30%) | 8,000 per level |
| Lucky Last | +10% chance per level (50%→90%) | 10,000 per level |
| Missile Jammer | +5% chance per level (20%→40%) | 9,000 per level |
| Flash | +100m per level (200→600m) | 12,000 per level |

---

## 10. Mission System

### Mission Structure

- Players have **3 active missions** at all times.
- Completing a mission awards **stars** that fill the level progression bar.
- Each mission has a tier corresponding to difficulty.
- When a mission is completed, a new one replaces it.

### Mission Types

| Mission Type | Example | Stars |
|-------------|---------|-------|
| Distance | Travel 500m in a single run | 1 |
| Distance milestone | Travel 2000m in a single run | 2 |
| Coin collection | Collect 300 coins in a single run | 1 |
| Coin total | Collect 5000 coins total | 2 |
| Vehicle use | Travel 500m in vehicles (cumulative) | 1 |
| Vehicle specific | Travel 200m on Bad As Hog | 1 |
| Scientist knockdown | Knock down 50 scientists (cumulative) | 1 |
| Near miss | Fly within 20px of 5 zappers without hitting | 2 |
| High five | High-five 10 scientists while running | 1 |
| No coins | Travel 500m without collecting any coins | 2 |
| Missile dodge | Dodge 5 missiles in a single run | 1 |
| Combo | Complete 3 missions in a single run | 3 |
| Head start | Use the Head Start to travel 750m+ | 1 |
| Rub head | Rub Barry's head after death | 1 |
| Specific death | Die by a specific obstacle type | 1 |

### Mission Difficulty Tiers

| Tier | Stars Per Mission | Unlock Level |
|------|------------------|-------------|
| 1 | 1 | Level 1 |
| 2 | 1-2 | Level 3 |
| 3 | 2 | Level 6 |
| 4 | 2-3 | Level 10 |
| 5 | 3 | Level 15 |

---

## 11. Scoring & Distance

### Distance Measurement

| Property | Value |
|----------|-------|
| Unit | Meters |
| Pixels per meter | ~10 pixels = 1 meter |
| Display | Bottom-left of screen, running counter |
| Format | "0000m" |

### Score Calculation

The primary metric is **distance traveled** in meters. Secondary metrics:

| Metric | Display |
|--------|---------|
| Distance | Main score (meters) |
| Coins collected | Coin counter in HUD |
| Best distance | Personal best, shown on death |

---

## 12. Shop & Economy

### Currency

| Currency | Source |
|----------|--------|
| Coins | Collected during runs, earned from slot machine |
| Real money (IAP) | Coin packs, cosmetics (not required for spec) |

### Shop Categories

#### Jetpacks

| Jetpack | Appearance | Cost | Effect |
|---------|-----------|------|--------|
| Machine Gun Jetpack | Default, bullet stream downward | Free | Standard |
| Bubble Gun Jetpack | Emits bubbles | 5,000 | Cosmetic |
| Laser Jetpack | Red laser beam downward | 15,000 | Cosmetic |
| Steam Jetpack | Steam clouds | 10,000 | Cosmetic |
| Rainbow Jetpack | Rainbow trail | 25,000 | Cosmetic |
| Fruit Jetpack | Fruit particles | 20,000 | Cosmetic |
| Snow Machine | Snowflakes | 30,000 | Cosmetic |
| Gold Jetpack | Gold particle stream | 50,000 | Cosmetic |

#### Clothing/Outfits

| Outfit | Cost | Description |
|--------|------|-------------|
| Default | Free | White shirt, jeans |
| Ninja | 10,000 | Black ninja outfit |
| Tuxedo | 15,000 | Formal black suit |
| Space Suit | 20,000 | White space suit |
| Zombie | 25,000 | Zombie Barry |
| Robot | 30,000 | Metallic robot suit |
| Santa | 15,000 | Red Santa outfit |
| Pirate | 20,000 | Pirate hat and outfit |

#### Head Accessories

| Item | Cost | Description |
|------|------|-------------|
| None | Free | Default |
| Viking Helmet | 5,000 | Horned helmet |
| Top Hat | 8,000 | Formal top hat |
| Crown | 15,000 | Gold crown |
| Mohawk | 3,000 | Red mohawk wig |
| Halo | 10,000 | Floating golden halo |

---

## 13. Slot Machine (Final Spin)

### Activation

After every death, the **Final Spin** slot machine appears.

| Property | Value |
|----------|-------|
| Free spins | 1 (default) + bonus from spin tokens |
| Additional spin cost | 100 coins per extra spin |
| Maximum extra spins | 2 (total 3 spins maximum) |

### Slot Machine Layout

Three reels, each with the following symbols:

| Symbol | Reel Weight | Effect When 3 Match |
|--------|-----------|-------------------|
| Bomb | 30% | Explosion: destroy all nearby obstacles (cosmetic, no gameplay effect post-death) |
| Coin | 25% | Win coins: 50-200 coins |
| Spin Token | 15% | Win a free spin token for next run |
| Barry | 10% | Second chance: continue run from death point |
| Wings | 10% | Double coins earned this run |
| Heart | 10% | Extra spin tokens (2 free tokens) |

### Matching Rules

| Match | Effect |
|-------|--------|
| 3 identical symbols | Prize awarded (see above) |
| 2 matching + 1 different | Small consolation: 10-50 coins |
| All different | No prize |
| 3 x Barry | Revive! Continue the run (most valuable) |

### Nudge Mechanic

- After the spin, if 2 reels match, the third reel can sometimes be "nudged" one position.
- Nudge is free and automatic (brief dramatic pause before nudge).
- Nudge chance: 30% when 2 reels already match.

---

## 14. UI Layout & Screen Flow

### 14.1 Main Menu

```
┌──────────────────────────────────────────────────────┐
│                 JETPACK JOYRIDE                       │
│                                                       │
│     [Barry running animation in lab background]       │
│                                                       │
│              ┌──────────────┐                        │
│              │    PLAY      │                        │
│              └──────────────┘                        │
│                                                       │
│  [Shop]  [Gadgets]  [Stats]            Coins: 12,450 │
│                                                       │
│  [Missions]  [Achievements]           [Settings]     │
└──────────────────────────────────────────────────────┘
```

### 14.2 In-Game HUD

```
┌──────────────────────────────────────────────────────┐
│                                        Coins: 247    │
│                                                       │
│                                                       │
│  Barry→ ♦     [Obstacles and lab environment]        │
│          ↑                                            │
│       Jetpack                                        │
│        flame                                          │
│                                                       │
│ 1,247m                              [Pause ║]        │
│ ★★★ (active missions)                                │
└──────────────────────────────────────────────────────┘
```

### 14.3 Death / Final Spin Screen

```
┌──────────────────────────────────────────────────────┐
│                                                       │
│              DISTANCE: 2,847m                        │
│              BEST: 4,102m                            │
│              COINS: 347                              │
│                                                       │
│           ┌─────┬─────┬─────┐                        │
│           │  ☆  │  ●  │  ☆  │   ← Slot Reels        │
│           └─────┴─────┴─────┘                        │
│                                                       │
│              [SPIN] (1 free)                          │
│           [Continue: 100 coins]                      │
│                                                       │
│              [End Run]                                │
└──────────────────────────────────────────────────────┘
```

### 14.4 Screen Flow

```
Splash → Main Menu → (Optional: Shop/Gadgets) → Run Start → Gameplay → Death → Final Spin → Results
                                                                                       ↓
                                                                                  Main Menu
```

---

## 15. Visual Design & Animation

### 15.1 Barry Steakfries Animations

| Animation | Frames | FPS | Trigger |
|-----------|--------|-----|---------|
| Run (floor) | 8 | 12 | On ground, no input |
| Fly (jetpack) | 4 (loop) | 10 | Input held, airborne |
| Fall | 2 (loop) | 8 | Input released, airborne |
| Land | 3 | 15 | Transition from air to ground |
| Death (zapper) | 6 | 10 | Electrocution death |
| Death (missile) | 5 | 10 | Explosion death |
| Death (laser) | 4 | 10 | Laser death |
| Tumble (vehicle loss) | 8 (loop) | 12 | Vehicle destroyed |
| Slide (post-death) | 6 | 8 | Ragdoll slide on floor after death |

### 15.2 Jetpack Effects

| Jetpack | Particle Type | Color | Particles/Second |
|---------|-------------|-------|-----------------|
| Machine Gun | Bullet casings + muzzle flash | Yellow/orange | 30 |
| Bubble Gun | Bubbles | Blue/transparent | 15 |
| Laser | Beam + sparks | Red | Continuous beam + 20 sparks |
| Steam | Steam clouds | White/grey | 10 |
| Rainbow | Color-cycling particles | Rainbow | 25 |

### 15.3 Background Animation

- Ceiling lights flicker occasionally.
- Computer monitors display scrolling code/data.
- Pipes occasionally release steam puffs.
- Emergency lights flash red when missiles are incoming.

### 15.4 Death Sequence

1. Barry is hit → impact flash (white, 0.1s).
2. Appropriate death animation plays (electrocution/explosion/laser).
3. Game scroll slows to 0 over 1.5 seconds.
4. Barry ragdolls and slides along the floor.
5. Slide distance is proportional to speed at death (50-300 pixels).
6. Coins picked up during slide still count.
7. Scientists flee from the sliding body.
8. Final position determines end-of-run distance bonus (+slide distance).

---

## 16. Audio Design

### 16.1 Music

| Track | Context | Style |
|-------|---------|-------|
| Main Theme | Main menu | Energetic chip-tune, catchy melody |
| Gameplay Loop | During run | Driving electronic beat, builds with distance |
| Vehicle Theme | While in vehicle | Intensified version of gameplay loop |
| Shop Theme | In shop/menus | Chill electronic |
| Slot Machine | Final Spin | Casino-style jingle |
| Game Over | Death/results | Descending tones, brief |

### 16.2 Sound Effects

| Event | Sound Description |
|-------|-------------------|
| Jetpack fire | Continuous "whoosh" with slight mechanical rattle |
| Jetpack off | Descending "whirr" fade-out |
| Coin collect | Light metallic "ding" (pitch increases with rapid collection) |
| Zapper buzz | Constant electrical hum when on-screen |
| Zapper death | Sharp electrical "zap" + crackle |
| Missile warning | Rising siren "whee-oo-whee-oo" |
| Missile fly-by | Rocket whoosh |
| Missile death | Deep explosion "boom" |
| Laser charge | Rising electronic hum |
| Laser fire | Sustained "BZZZZZ" |
| Laser death | Sharp "zzt" |
| Vehicle pickup | "Clunk" + power-up chime |
| Vehicle destroy | Explosion + metal crunch |
| Scientist scream | "AHHH!" (varies) |
| Landing | Soft "thud" |
| Spin token collect | Magical chime |
| Slot machine spin | Reel spinning ratchet sound |
| Slot machine win | Celebratory jingle |
| Barry slide | Scraping/sliding sound |
| Menu button | Soft click |

---

## 17. Progression System

### Player Level

| Level | Stars Required | Cumulative Stars |
|-------|---------------|-----------------|
| 1 | 0 | 0 |
| 2 | 3 | 3 |
| 3 | 5 | 8 |
| 4 | 7 | 15 |
| 5 | 9 | 24 |
| 6 | 11 | 35 |
| 7 | 13 | 48 |
| 8 | 15 | 63 |
| 9 | 17 | 80 |
| 10 | 19 | 99 |
| 11-15 | 21 each | 99-204 |
| 16+ | Stars reset, rank name changes | Prestige system |

### Rank Names

| Level Range | Rank Title |
|------------|-----------|
| 1-5 | Trainee |
| 6-10 | Soldier |
| 11-15 | Sergeant |
| 16-20 | Lieutenant |
| 21-25 | Captain |
| 26-30 | Major |
| 31+ | General |

### Statistics Tracked

| Stat | Description |
|------|-------------|
| Best Distance | Longest single run |
| Total Distance | Cumulative distance across all runs |
| Total Coins | All coins ever collected |
| Games Played | Total number of runs |
| Scientists Bumped | Total scientists knocked down |
| Vehicles Used | Total vehicle pickups |
| Zappers Dodged | Near-miss count |
| Missiles Dodged | Total missiles survived |
| High Fives | Scientists high-fived |

---

## Appendix A: Quick Reference — Timing Values

| Mechanic | Time |
|----------|------|
| Missile warning duration | 1.5 seconds |
| Laser warning duration | 2.0 seconds |
| Laser active duration | 1.5 seconds |
| Vehicle invincibility after destruction | 1.0 seconds |
| Death slide duration | 1.0-2.5 seconds |
| Slot machine spin duration | 2 seconds per reel |
| Head start travel time | 3 seconds |
| Freeze gadget duration | 5 seconds |
| Coin magnet attraction time | 0.3 seconds (travel to player) |

## Appendix B: Quick Reference — Speed Progression

```
Speed (px/s)
    ^
900 |                                      ___________
800 |                              _______/
700 |                      _______/
600 |              _______/
500 |      _______/
400 |_____/
    +----+----+----+----+----+----+----+-----> Time (s)
    0   30   60   90  120  150  200  250+
```

## Appendix C: Vehicle Comparison

| Vehicle | Hitbox | Control Style | Difficulty | Special Ability |
|---------|--------|-------------|-----------|----------------|
| Bad As Hog | Large | Hold=jump | Easy | Destroys floor zappers |
| Lil' Stomper | Large | Hold=rise, Release=stomp | Medium | Screen shake, floor zap destroy |
| Profit Bird | Small | Tap=flap | Hard | Drops eggs (cosmetic) |
| Gravity Guy | Normal | Tap=flip gravity | Medium | Ceiling running |
| Crazy Teleporter | Normal | Hold=rise+teleport | Very Hard | Random vertical teleports |

---

*This specification is based on Jetpack Joyride (2011) by Halfbrick Studios, primarily the iOS version. Values are sourced from gameplay analysis and community documentation. Minor variations may exist between platform versions.*
