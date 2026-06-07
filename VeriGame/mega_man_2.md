# Mega Man 2 — Complete Game Specification

> A comprehensive specification for faithfully recreating Mega Man 2 (Capcom, 1988 NES). This document covers every system, mechanic, entity, and interaction required for a full clone of this legendary action-platformer.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Player Character Mechanics](#3-player-character-mechanics)
4. [Weapon System](#4-weapon-system)
5. [Robot Master Stages](#5-robot-master-stages)
6. [Robot Master Boss Fights](#6-robot-master-boss-fights)
7. [Dr. Wily's Castle](#7-dr-wilys-castle)
8. [Enemy Compendium](#8-enemy-compendium)
9. [Item & Pickup System](#9-item--pickup-system)
10. [Utility Items](#10-utility-items)
11. [Scoring & Lives System](#11-scoring--lives-system)
12. [UI Layout & HUD](#12-ui-layout--hud)
13. [Audio Design](#13-audio-design)
14. [Animation System](#14-animation-system)
15. [Damage Chart](#15-damage-chart)

---

## 1. Game Overview

- **Genre**: Action-platformer
- **Perspective**: 2D side-scrolling
- **Players**: 1 player
- **Input**: D-pad + 2 buttons (Shoot, Jump) + Start (pause/weapon select) + Select (not used in gameplay)
- **Objective**: Defeat 8 Robot Masters, then storm Dr. Wily's Castle to defeat Dr. Wily and save the world.
- **Key feature**: After defeating a Robot Master, Mega Man acquires their special weapon. Each Robot Master has a weakness to another's weapon, creating a strategic order.
- **Difficulty**: Normal and Difficult modes (Japanese "Rockman 2" had one difficulty; international release added "Normal" as an easier mode with reduced damage taken).

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| NES resolution | 256 x 240 pixels |
| Recommended implementation | 512 x 480 or 1024 x 960 |
| Orientation | Landscape |
| Frame rate | 60 FPS (NTSC) |
| Tile size | 16 x 16 pixels |
| Screen transition | Smooth scroll for horizontal; screen-by-screen flip for vertical |

### Coordinate System

- Origin (0, 0) at top-left.
- Horizontal scrolling follows player movement.
- Vertical room transitions are screen-by-screen (the camera scrolls one full screen height up or down when Mega Man crosses a screen boundary).

### Game Loop

```
1. Process input (D-pad, buttons)
2. Update Mega Man position and state
3. Apply gravity and check ground collision
4. Update Mega Man projectiles
5. Update all enemy AI, positions, and projectiles
6. Check player vs enemy/projectile collisions
7. Check player projectile vs enemy collisions
8. Check player vs item pickups
9. Check screen boundaries and transitions
10. Handle invincibility frames
11. Update animations
12. Render (background → enemies → items → Mega Man → projectiles → UI)
```

---

## 3. Player Character Mechanics

### Mega Man Properties

| Property | Value |
|----------|-------|
| HP | 28 units (displayed as 28 bars in life gauge) |
| Hitbox | 14 x 22 pixels |
| Walk speed | 1.3 px/frame (78 px/s) |
| Jump velocity (initial) | -4.8 px/frame |
| Gravity | 0.25 px/frame^2 |
| Max fall speed | 7 px/frame |
| Jump height | ~46 pixels |
| Invincibility frames after hit | 60 frames (1 second) |
| Knockback on hit | 4 pixels backward |

### Movement Details

| Action | Input | Description |
|--------|-------|-------------|
| Walk left/right | D-pad | Constant speed, no acceleration |
| Jump | A button | Variable height (release early for short jump) |
| Shoot | B button | Fire current weapon |
| Climb ladder | D-pad up/down on ladder | Fixed climb speed: 1 px/frame |
| Slide | Not available | (Introduced in Mega Man 3) |

### Jumping Mechanics

| Property | Value |
|----------|-------|
| Initial velocity | -4.8 px/frame upward |
| Gravity | 0.25 px/frame^2 |
| Variable jump | Releasing A stops upward velocity (gravity takes over) |
| Minimum jump height | ~16 pixels (quick tap) |
| Maximum jump height | ~46 pixels (full hold) |
| Air control | Full horizontal movement while airborne |
| Landing | Instant state change to standing/walking |

### Ladder Mechanics

| Property | Value |
|----------|-------|
| Climb speed | 1 px/frame |
| Mounting | Walk onto ladder tile and press Up, or jump onto ladder and press Up |
| Dismounting | At top: continues walking. At bottom: drops off. Jump button: jumps off ladder. |
| Shooting | Can shoot while on ladder (horizontal only) |
| Hitbox while climbing | Same as standing (14 x 22) |

### Damage and Death

| Property | Value |
|----------|-------|
| Invincibility after hit | 60 frames (1 second) |
| Visual indicator | Mega Man flickers during invincibility |
| Knockback | 4 pixels backward, slight upward push |
| Pit death | Instant death (falling off screen bottom) |
| Spike death | Instant death (any contact with spikes, even with invincibility) |
| Death animation | Mega Man explodes into energy particles |

---

## 4. Weapon System

### Mega Buster (Default)

| Property | Value |
|----------|-------|
| Damage | 1 per shot |
| Fire rate | 10 shots/second |
| Max on-screen | 3 |
| Projectile speed | 5 px/frame |
| Projectile size | 6 x 6 pixels |
| Ammo | Unlimited |
| Color | Light blue |

### Special Weapons (Acquired from Robot Masters)

#### Metal Blade (from Metal Man)

| Property | Value |
|----------|-------|
| Damage | 1-3 (varies by enemy) |
| Ammo | 28 units (112 uses — costs 0.25 per shot) |
| Fire rate | Fast (~10/second) |
| Max on-screen | 3 |
| Directions | 8-way (all cardinal and diagonal) |
| Projectile speed | 5 px/frame |
| Projectile size | 8 x 8 pixels |
| Special | Can be fired in any of 8 directions using D-pad |
| Weakness of | Metal Man, Bubble Man |
| Mega Man color | Dark grey/red |

#### Air Shooter (from Air Man)

| Property | Value |
|----------|-------|
| Damage | 2 |
| Ammo | 28 units (14 uses — costs 2 per shot) |
| Fire rate | Medium (~5/second) |
| Projectiles per shot | 3 (fan upward-forward pattern) |
| Projectile speed | 3 px/frame with upward drift |
| Special | 3 tornadoes spread upward in a fan |
| Weakness of | Crash Man, (partially) Wood Man |
| Mega Man color | Light blue/white |

#### Bubble Lead (from Bubble Man)

| Property | Value |
|----------|-------|
| Damage | 1-2 |
| Ammo | 28 units (14 uses — costs 2 per shot) |
| Fire rate | Medium |
| Max on-screen | 1 |
| Behavior | Drops to ground, rolls along floor following terrain |
| Speed | 2 px/frame horizontal, falls at gravity speed |
| Special | Travels along the ground surface, drops off edges |
| Weakness of | Heat Man, Wily Machine final form |
| Mega Man color | Dark blue/grey |

#### Quick Boomerang (from Quick Man)

| Property | Value |
|----------|-------|
| Damage | 1 |
| Ammo | 28 units (56 uses — costs 0.5 per shot) |
| Fire rate | Very fast (~12/second) |
| Max on-screen | 4 |
| Range | Short (~64 pixels) then returns |
| Behavior | Fires forward in a small arc, returns like a boomerang |
| Speed | 4 px/frame |
| Special | Short range but very rapid fire. Arcs in a small loop. |
| Weakness of | (Minor effectiveness on some enemies) |
| Mega Man color | Dark red/maroon |

#### Crash Bomber (from Crash Man)

| Property | Value |
|----------|-------|
| Damage | 4 |
| Ammo | 28 units (4 uses — costs 7 per shot) |
| Fire rate | Slow (~2/second) |
| Max on-screen | 1 |
| Behavior | Fires horizontally; attaches to first wall/enemy it hits |
| Fuse time | 2 seconds after attachment |
| Explosion radius | 16 pixel radius |
| Special | Sticks to surfaces, explodes after delay. Can destroy certain walls. |
| Weakness of | (Wily stage bosses, specific walls) |
| Mega Man color | Red/orange |

#### Time Stopper (from Flash Man)

| Property | Value |
|----------|-------|
| Damage | Drains target HP continuously (1 damage per ~30 frames) |
| Ammo | 28 units (drains continuously while active) |
| Duration | Until ammo depletes (about 4.5 seconds) |
| Special | Freezes ALL enemies and projectiles on screen. Cannot be toggled off once activated. |
| Weakness of | Quick Man (deals ~50% of his HP) |
| Mega Man color | Dark purple |
| Limitation | Cannot switch weapons while active. Drains completely before deactivating. |

#### Atomic Fire (from Heat Man)

| Property | Value |
|----------|-------|
| Damage (no charge) | 2 |
| Damage (half charge) | 4 |
| Damage (full charge) | 10 |
| Ammo cost (no charge) | 2 |
| Ammo cost (half charge) | 6 |
| Ammo cost (full charge) | 10 |
| Charge time (half) | 1 second |
| Charge time (full) | 2 seconds |
| Projectile speed | 4 px/frame |
| Special | One of the first charge-shot weapons. Hold B to charge, release to fire. |
| Weakness of | Wood Man (full charge does massive damage) |
| Mega Man color | Red/orange |

#### Leaf Shield (from Wood Man)

| Property | Value |
|----------|-------|
| Damage | 3 per leaf hit |
| Ammo | 28 units (costs 3 per activation) |
| Behavior | 4 leaves orbit Mega Man as a shield. Pressing a direction throws the shield forward. |
| Shield duration | Until thrown or hit by an enemy |
| Throw speed | 4 px/frame |
| Special | Acts as a shield absorbing projectiles, then can be thrown as an attack |
| Weakness of | Air Man |
| Mega Man color | Green |
| Limitation | Cannot shoot Mega Buster while Leaf Shield is active. Cannot move while shield forms. |

---

## 5. Robot Master Stages

### Stage Selection Screen

After the intro sequence, the player can select any of the 8 Robot Master stages in any order.

```
┌──────────────────────────────────────┐
│  [Bubble]  [Air]    [Quick]          │
│                                      │
│  [Heat]   [MEGA MAN] [Wood]          │
│                                      │
│  [Metal]   [Flash]   [Crash]         │
└──────────────────────────────────────┘
```

### 5.1 Metal Man Stage

| Property | Value |
|----------|-------|
| Theme | Industrial factory with conveyor belts |
| Hazards | Conveyor belts (move Mega Man left or right), crushers, gear platforms |
| Conveyor speed | 1 px/frame (adds to or subtracts from walk speed) |
| Key enemies | Mole drills, gear throwers, spring jumpers |
| Length | ~12 screens |
| Boss | Metal Man |
| E-Tanks | 1 (hidden) |

### 5.2 Air Man Stage

| Property | Value |
|----------|-------|
| Theme | Sky fortress with cloud platforms |
| Hazards | Wind gusts (push Mega Man), bottomless pits |
| Wind force | 0.8 px/frame horizontal push |
| Key enemies | Cloud demons (Goblin), flying platform robots |
| Length | ~10 screens |
| Boss | Air Man |
| E-Tanks | 0 |

### 5.3 Bubble Man Stage

| Property | Value |
|----------|-------|
| Theme | Underwater cavern/waterfall |
| Hazards | Spikes, underwater physics |
| Underwater physics | Lower gravity (0.15 px/frame^2), higher jump, slower fall |
| Key enemies | Angler fish, crabs, frogs |
| Length | ~12 screens |
| Boss | Bubble Man |
| E-Tanks | 1 |

### 5.4 Quick Man Stage

| Property | Value |
|----------|-------|
| Theme | High-speed facility |
| Hazards | Instant-kill laser beams (horizontal, sweep vertically) |
| Laser speed | Sweeps at 4 px/frame |
| Laser sections | 3 separate laser gauntlets |
| Key enemies | Quick lasers, sniper robots |
| Length | ~14 screens (long due to laser sections) |
| Boss | Quick Man |
| E-Tanks | 0 |
| Note | Time Stopper can freeze the lasers |

### 5.5 Crash Man Stage

| Property | Value |
|----------|-------|
| Theme | Climbing stage, vertical ascent |
| Hazards | Bottomless pits, ladder enemies |
| Orientation | Primarily vertical scrolling (climbing) |
| Key enemies | Telly (floating bomb), pipe enemies, ladder pressers |
| Length | ~12 screens (mostly vertical) |
| Boss | Crash Man |
| E-Tanks | 1 |

### 5.6 Flash Man Stage

| Property | Value |
|----------|-------|
| Theme | Crystal/ice facility |
| Hazards | Ice physics (reduced friction), disappearing blocks |
| Ice friction | Deceleration: 0.1 px/frame^2 (instead of instant stop) |
| Disappearing blocks | Platforms appear/disappear in sequence (1 second on, 1 second off) |
| Key enemies | Sniper Joe, turrets |
| Length | ~10 screens |
| Boss | Flash Man |
| E-Tanks | 1 |

### 5.7 Heat Man Stage

| Property | Value |
|----------|-------|
| Theme | Volcanic factory, fire and lava |
| Hazards | Lava (instant death), disappearing blocks over lava |
| Disappearing block sequence | Critical section — memorize the pattern or use Item-2 (jet board) |
| Key enemies | Fire wheels, flame pillars |
| Length | ~10 screens |
| Boss | Heat Man |
| E-Tanks | 1 |

### 5.8 Wood Man Stage

| Property | Value |
|----------|-------|
| Theme | Forest, outdoor nature |
| Hazards | Falling flame enemies, dogs with jumping attacks |
| Key enemies | Robotic dogs, fire-dropping birds, rabbit robots |
| Length | ~10 screens |
| Boss | Wood Man |
| E-Tanks | 1 |

---

## 6. Robot Master Boss Fights

All Robot Masters are fought in a single-screen room at the end of their stage.

### Universal Boss Properties

| Property | Value |
|----------|-------|
| Arena size | 256 x 208 pixels (1 screen) |
| HP | 28 (same as Mega Man) |
| Contact damage | 4 (Normal mode) / 8 (Difficult) |
| HP bar | Right side of screen |

### Metal Man

| Property | Value |
|----------|-------|
| Pattern | Jumps to one of 3 platforms, throws Metal Blades |
| Jump height | Medium |
| Attack | Throws 1-3 Metal Blades at Mega Man (aimed) |
| Attack interval | Every 1.5 seconds |
| Blade speed | 4 px/frame |
| Blade directions | Aimed at Mega Man's current position |
| Weakness | Metal Blade (2 damage), Quick Boomerang (2) |
| Extreme weakness | His own Metal Blade deals 14 damage (half HP) — 2 hits to kill |

### Air Man

| Property | Value |
|----------|-------|
| Pattern | Jumps across arena, fires tornado pattern |
| Attack | Fires 3-5 small tornadoes in a spread pattern |
| Tornado count per volley | Alternates between 3 and 5 |
| Tornado speed | 2 px/frame horizontal, slight vertical drift |
| Attack interval | After each jump |
| Wind push | Pushes Mega Man backward during attack |
| Weakness | Leaf Shield (4 damage), Atomic Fire full charge |

### Bubble Man

| Property | Value |
|----------|-------|
| Pattern | Jumps high (underwater physics), falls slowly, fires bubbles |
| Attack | Fires Bubble Lead along ceiling, drops down |
| Secondary attack | Fires 3 bubbles upward in a spread |
| Jump height | Very high (underwater gravity) |
| Weakness | Metal Blade (4 damage) |

### Quick Man

| Property | Value |
|----------|-------|
| Pattern | Runs extremely fast, jumps, throws Quick Boomerangs |
| Speed | 3 px/frame (fastest Robot Master) |
| Attack | 3 Quick Boomerangs in spread pattern |
| Behavior | Constantly running and jumping, difficult to hit |
| Weakness | Time Stopper (drains ~14 HP), Crash Bomber (4 damage) |
| Note | Time Stopper can only be activated once; must finish with another weapon |

### Crash Man

| Property | Value |
|----------|-------|
| Pattern | Jumps toward Mega Man, fires Crash Bombs |
| Jump height | High |
| Attack | Fires Crash Bomber when Mega Man shoots (reactive) |
| Behavior | Jumps in response to Mega Man's movement; fires when shot at |
| Weakness | Air Shooter (2 damage per tornado, can hit with all 3) |

### Flash Man

| Property | Value |
|----------|-------|
| Pattern | Walks toward Mega Man, activates Time Stopper periodically |
| Time Stopper duration | 3 seconds (freezes Mega Man) |
| Attack during freeze | Fires 3 shots at frozen Mega Man |
| Shot speed | 3 px/frame |
| Weakness | Metal Blade (4 damage), Crash Bomber (4 damage) |

### Heat Man

| Property | Value |
|----------|-------|
| Pattern | Throws fireballs, charges across screen as a fireball |
| Attack 1 | 3 fireballs in a spread pattern |
| Attack 2 | Transforms into fireball, charges across arena at high speed |
| Charge speed | 5 px/frame |
| Fireball speed | 3 px/frame |
| Weakness | Bubble Lead (4 damage) |
| Note | After being hit, Heat Man charges immediately (react quickly) |

### Wood Man

| Property | Value |
|----------|-------|
| Pattern | Activates Leaf Shield, throws it, rains leaves |
| Phase 1 | Summons Leaf Shield (4 leaves orbit) — invulnerable during this |
| Phase 2 | Throws Leaf Shield forward at Mega Man |
| Phase 3 | Rains 4 falling leaves from above |
| Shield duration | ~2 seconds before throwing |
| Weakness | Atomic Fire fully charged (14 damage — 2 hits to kill), Metal Blade (2 damage) |

---

## 7. Dr. Wily's Castle

After defeating all 8 Robot Masters, Dr. Wily's Castle stages unlock (played sequentially).

### Wily Stage 1: Dragon Stage

| Property | Value |
|----------|-------|
| Theme | Fortress exterior, climbing |
| Length | ~8 screens |
| Boss | Mecha Dragon (large mechanical dragon) |
| Boss HP | 28 |
| Boss attacks | Fireball volleys (3 at a time), charges forward |
| Boss weakness | Quick Boomerang (4 damage), Crash Bomber (4 damage), Atomic Fire (4 damage) |
| Special | Fight takes place on floating platforms over a pit |

### Wily Stage 2: Picopico-kun Stage

| Property | Value |
|----------|-------|
| Theme | Fortress interior, waterfall |
| Length | ~10 screens |
| Boss | Picopico-kun (room of floating blocks) |
| Boss HP | 28 (distributed across wall panel) |
| Boss attacks | 14 small blocks circle the room in a complex pattern |
| Boss weakness | Bubble Lead (2 damage), Quick Boomerang |
| Special | Must destroy the single target block among many |

### Wily Stage 3: Guts Tank Stage

| Property | Value |
|----------|-------|
| Theme | Fortress interior, military base |
| Length | ~8 screens |
| Boss | Guts Tank (large tank that occupies the floor) |
| Boss HP | 28 |
| Boss attacks | Fires Guts blocks (indestructible), charges forward |
| Boss weakness | Quick Boomerang (4 damage) |

### Wily Stage 4: Robot Master Refights

| Property | Value |
|----------|-------|
| Theme | Teleporter room with 8 teleporters |
| Structure | Player enters teleporters to refight each Robot Master |
| Robot Master HP | 28 each (same as original fights) |
| Healing | E-tanks and weapon energy refills between fights |
| Boss at end | None (stage ends after all 8 refights) |

### Wily Stage 5: Wily Machine

| Property | Value |
|----------|-------|
| Theme | Final room |
| Boss Phase 1 | Wily Machine 2 (large machine) |
| Phase 1 HP | 28 |
| Phase 1 attacks | Bouncing energy shots, charges forward |
| Phase 1 weakness | Atomic Fire fully charged (14 damage), Crash Bomber, Metal Blade |
| Boss Phase 2 | Wily Capsule (Wily in a small pod) |
| Phase 2 HP | 28 |
| Phase 2 attacks | Fires aimed energy shots in bursts of 5 |
| Phase 2 weakness | Bubble Lead (4 damage — ONLY weapon that works) |
| Victory | Dr. Wily begs for mercy. Game ending sequence plays. |

---

## 8. Enemy Compendium

### Common Enemies

| Enemy | HP | Damage | Speed | Behavior | Score |
|-------|-----|--------|-------|----------|-------|
| Met (Hard Hat) | 1 (vulnerable when exposed) | 2 | 0 (stationary) | Hides under helmet (invulnerable), periodically pops up and fires 3 shots | 200 |
| Telly | 1 | 2 | 1 px/frame (follows) | Small floating bomb, slowly follows Mega Man | 100 |
| Sniper Joe | 3 | 2 | 0.5 px/frame | Shield blocks shots; fires between shield drops | 400 |
| Pipi (bird) | 1 | 2 | 2 px/frame | Flies overhead, drops egg that spawns small birds | 300 |
| Springer | 1 | 2 | 1 px/frame (bouncing) | Spring-based enemy, bounces toward player | 200 |
| Blocky | 4 | 4 | 0.5 px/frame | Large block enemy, splits into 4 smaller blocks | 500 |
| Shotman | 1 | 2 | 0 (stationary) | Wall-mounted turret, fires aimed shots | 200 |
| Batton | 1 | 2 | 2 px/frame | Hanging bat, dives at player when close | 100 |
| Scworm | 1 | 2 | 1 px/frame | Worm enemies on walls/ceilings | 100 |
| Mole (Matasaburo) | 1 | 2 | 2 px/frame | Emerges from ground, fires wind gusts | 200 |
| Friender (robotic dog) | 5 | 4 | 2 px/frame (jump) | Leaps at player from a distance | 500 |
| Kaminari Goro | 3 | 4 | 0 | Cloud enemy, drops lightning bolts | 400 |

### Stage-Specific Enemies

| Stage | Unique Enemy | Description |
|-------|-------------|-------------|
| Metal Man | Press (crusher) | Ceiling-mounted crusher, drops periodically |
| Air Man | Goblin (cloud demon) | Rides clouds, fires small tornados |
| Bubble Man | Anko (angler fish) | Swims and charges at player |
| Quick Man | Quick beam traps | Environmental hazard, not a standard enemy |
| Crash Man | Telly swarms | Large numbers of floating bombs |
| Flash Man | Sniper Joe shield variant | Enhanced Sniper Joe |
| Heat Man | Changkey (fire wheel) | Circles around platforms in fixed patterns |
| Wood Man | Atomic Chicken | Drops fire, hard to avoid |

---

## 9. Item & Pickup System

### Energy Pickups

| Item | HP Restored | Drop Source |
|------|------------|-------------|
| Small energy pellet | 2 HP | Common enemy drop |
| Large energy pellet | 10 HP | Rare enemy drop, hidden |
| Small weapon energy | 2 weapon units | Common enemy drop |
| Large weapon energy | 10 weapon units | Rare enemy drop, hidden |

### Extra Lives

| Item | Effect | Source |
|------|--------|--------|
| 1-UP | +1 life | Hidden in stages, rare enemy drops |

### E-Tank (Energy Tank)

| Property | Value |
|----------|-------|
| Effect | Fully restores HP (28 units) |
| Max carry | 4 |
| Usage | Select from pause menu |
| Persistence | Carried between stages |
| Locations | 1-2 per Robot Master stage, hidden or in challenging spots |

### Drop Rates

| Item | Drop Chance |
|------|------------|
| Nothing | 50% |
| Small HP energy | 15% |
| Large HP energy | 5% |
| Small weapon energy | 15% |
| Large weapon energy | 5% |
| 1-UP | 2% |
| Score bonus | 8% |

---

## 10. Utility Items

Acquired from specific Robot Master stage completions. Equip via pause menu.

### Item-1 (from Heat Man stage)

| Property | Value |
|----------|-------|
| Function | Creates a floating platform that rises upward |
| Ammo | 28 units (costs 3.5 per use) |
| Platform duration | ~5 seconds |
| Rise speed | 1 px/frame upward |
| Usage | Creates a platform at Mega Man's position; it rises |

### Item-2 (from Air Man stage)

| Property | Value |
|----------|-------|
| Function | Creates a horizontal jet sled platform |
| Ammo | 28 units (costs 7 per use) |
| Platform duration | Until hitting a wall or ammo runs out |
| Speed | 3 px/frame horizontal |
| Usage | Must be deployed on a flat surface; Mega Man rides on it |
| Note | Essential for crossing Heat Man's disappearing block section |

### Item-3 (from Flash Man stage)

| Property | Value |
|----------|-------|
| Function | Creates a platform that climbs walls |
| Ammo | 28 units (costs 3.5 per use) |
| Behavior | Attaches to nearest wall and climbs upward |
| Climb speed | 1.5 px/frame |
| Usage | Deploy near a wall; platform climbs up the wall surface |

---

## 11. Scoring & Lives System

### Scoring

| Source | Points |
|--------|--------|
| Common enemy | 100-500 |
| Boss | 0 (no score for bosses) |
| Score pickup (small) | 200 |
| Score pickup (large) | 1,000 |

### Lives

| Property | Value |
|----------|-------|
| Starting lives | 2 (plus current life = 3 total) |
| Maximum lives | 9 |
| Extra life at | Not score-based; found as 1-UP items |
| Continue | Unlimited continues; restart at stage beginning |
| Password | 5x5 grid password system to save progress |

### Password System

- After game over or stage select, a password is displayed.
- Password is a 5x5 grid of red dots.
- Encodes: defeated Robot Masters, E-Tank count, and game progress.
- Enter password at title screen to resume progress.

---

## 12. UI Layout & HUD

### 12.1 In-Game HUD

```
┌──────────────────────────────────────┐
│ READY                                │
│ ┌───┐                        ┌───┐  │
│ │ M │ ████████████████████ █ │ B │  │
│ │ E │ (Mega Man HP bar)    █ │ O │  │
│ │ G │                      █ │ S │  │
│ │ A │                      █ │ S │  │
│ └───┘                      █ └───┘  │
│                             █       │
│     [Game playfield]        █       │
│                             █       │
│                                      │
│ LIVES: ♦♦                            │
└──────────────────────────────────────┘
```

### HUD Elements

| Element | Position | Description |
|---------|----------|-------------|
| Mega Man HP bar | Top-left, vertical | 28-unit bar, depletes downward |
| Boss HP bar | Top-right, vertical | 28-unit bar (appears during boss fights) |
| Lives counter | Bottom-left | Remaining lives as number or icons |
| "READY" text | Center screen | Appears for 2 seconds at stage start |
| Weapon energy | Shown on pause menu | Per-weapon ammo bars |

### 12.2 Pause/Weapon Select Menu

```
┌──────────────────────────────────────┐
│ WEAPON SELECT                        │
│                                      │
│ [P] Mega Buster    ████████████████  │
│ [H] Atomic Fire    ███████████       │
│ [A] Air Shooter    ██████████████    │
│ [B] Bubble Lead    █████████████████ │
│ [Q] Quick Boomerang ████████████████ │
│ [C] Crash Bomber   ███████████       │
│ [F] Time Stopper   ██████            │
│ [M] Metal Blade    █████████████████ │
│ [W] Leaf Shield    ████████████████  │
│                                      │
│ [1] Item-1         ████████████████  │
│ [2] Item-2         ███████████       │
│ [3] Item-3         ████████████████  │
│                                      │
│ E-TANKS: ♦♦♦                         │
└──────────────────────────────────────┘
```

### 12.3 Stage Select Screen

```
┌──────────────────────────────────────┐
│         STAGE SELECT                 │
│                                      │
│   [Bubble Man] [Air Man]  [Quick Man]│
│                                      │
│   [Heat Man]  [MEGA MAN] [Wood Man]  │
│                                      │
│   [Metal Man] [Flash Man][Crash Man] │
│                                      │
│   [PASSWORD]                         │
└──────────────────────────────────────┘
```

---

## 13. Audio Design

### 13.1 Music (Composer: Takashi Tateishi / Manami Matsumae)

| Track | Context | Notable Feature |
|-------|---------|-----------------|
| "Title" | Title screen | Dramatic intro |
| "Stage Select" | Robot Master selection | Short, catchy loop |
| "Metal Man" | Metal Man stage | Driving, iconic rock |
| "Air Man" | Air Man stage | Soaring, heroic melody |
| "Bubble Man" | Bubble Man stage | Underwater feel, dreamy |
| "Quick Man" | Quick Man stage | Intense, fast-paced |
| "Crash Man" | Crash Man stage | Climbing, urgent |
| "Flash Man" | Flash Man stage | Mysterious, crystalline |
| "Heat Man" | Heat Man stage | Hot, intense rhythm |
| "Wood Man" | Wood Man stage | Nature-inspired, bouncy |
| "Dr. Wily Stage 1-2" | Wily Castle 1-2 | One of the most iconic VGM tracks ever |
| "Dr. Wily Stage 3-4" | Wily Castle 3-4 | Darker, more urgent |
| "Boss" | Robot Master fights | Intense battle theme |
| "Wily Boss" | Wily Machine fight | Final confrontation |
| "Stage Clear" | After beating a stage | Short fanfare |
| "Get Weapon" | Receiving new weapon | Brief jingle |
| "Game Over" | Game over screen | Somber |
| "Ending" | Credits/ending | Triumphant, emotional |
| "Password" | Password screen | Calm, waiting |

### 13.2 Sound Effects

| Event | Description |
|-------|-------------|
| Mega Buster shot | Short "pew" |
| Metal Blade throw | Metallic "shing" |
| Crash Bomber attach | "Clank" |
| Crash Bomber explode | "Boom" |
| Time Stopper activate | Freezing "whirrr" |
| Bubble Lead drop | Bubbly "blub" |
| Player hit | Sharp "damage" sting |
| Player death | Explosion with descending pitch |
| Enemy hit | Impact "thud" |
| Enemy death | Small explosion pop |
| Energy pickup | Rising "ding" |
| 1-UP | Celebratory jingle |
| E-Tank use | Filling/restoration sound |
| Charged shot (Atomic Fire) | Rising charge hum |
| Boss door opening | Rumbling slide |
| Teleporter | Warping "beam" sound |
| Landing | Soft "thud" |
| Menu select | Click |

---

## 14. Animation System

### 14.1 Mega Man Animations

| Animation | Frames | FPS | Description |
|-----------|--------|-----|-------------|
| Idle | 1 (2 with blink) | 1 blink every 4s | Standing still |
| Walk | 4 | 10 | Walking cycle |
| Jump (ascend) | 1 | — | Jumping pose |
| Jump (descend) | 1 | — | Falling pose |
| Shoot (stand) | 2 | 15 | Arm cannon fires |
| Shoot (walk) | 4 (walk with arm forward) | 10 | Walking while shooting |
| Shoot (jump) | 1 | — | Jumping while shooting |
| Climb ladder | 2 | 8 | Alternating hand grips |
| Hit/damage | 2 | 30 (flicker) | Knockback and flicker |
| Death | 8 | 12 | Explodes into particles |
| Teleport in | 6 | 10 | Beam down into stage |
| Teleport out | 6 | 10 | Beam up after stage clear |
| Get weapon | Special | — | Weapon acquisition pose |

### 14.2 Color Palette Changes

Mega Man's color palette changes based on equipped weapon:

| Weapon | Primary Color | Secondary Color |
|--------|--------------|----------------|
| Mega Buster | Cyan | Dark Blue |
| Metal Blade | Dark Grey | Red |
| Air Shooter | Light Blue | White |
| Bubble Lead | Dark Blue | Grey |
| Quick Boomerang | Dark Red | Maroon |
| Crash Bomber | Red | Orange |
| Time Stopper | Purple | Dark Purple |
| Atomic Fire | Red | Orange |
| Leaf Shield | Green | Dark Green |

---

## 15. Damage Chart

### Robot Master Weakness Chart (Damage per hit)

| Weapon → / Boss ↓ | Buster | Metal | Air | Bubble | Quick | Crash | Time | Atomic | Leaf |
|--------------------|--------|-------|-----|--------|-------|-------|------|--------|------|
| Metal Man | 1 | 14 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| Air Man | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 2 | 4 |
| Bubble Man | 1 | 4 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Quick Man | 1 | 1 | 0 | 0 | 0 | 4 | drain | 0 | 0 |
| Crash Man | 1 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| Flash Man | 1 | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| Heat Man | 1 | 1 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| Wood Man | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 6/14 | 0 |

### Recommended Boss Order

1. Metal Man (use Mega Buster)
2. Wood Man (use Metal Blade, or Atomic Fire)
3. Air Man (use Leaf Shield)
4. Crash Man (use Air Shooter)
5. Flash Man (use Metal Blade or Crash Bomber)
6. Quick Man (use Time Stopper + Crash Bomber)
7. Bubble Man (use Metal Blade)
8. Heat Man (use Bubble Lead)

---

## Appendix A: Optimal Weapon Usage

| Weapon | Total Ammo (uses) | Primary Use |
|--------|-------------------|-------------|
| Metal Blade | 112 shots | General purpose (best weapon) |
| Quick Boomerang | 56 shots | Rapid damage, short range |
| Air Shooter | 14 shots | Anti-air, Crash Man |
| Bubble Lead | 14 shots | Heat Man, Wily Final |
| Crash Bomber | 4 shots | Destructible walls, specific bosses |
| Atomic Fire | 2-14 shots | Wood Man (charged), general |
| Time Stopper | 1 use (full drain) | Quick Man stage lasers, Quick Man fight |
| Leaf Shield | 9 uses | Air Man, defensive |

## Appendix B: Quick Reference — Stage Difficulty

| Stage | Difficulty | Recommended Weapons |
|-------|-----------|-------------------|
| Metal Man | Easy | Mega Buster |
| Air Man | Medium | Metal Blade |
| Bubble Man | Easy-Medium | Metal Blade |
| Quick Man | Hard | Time Stopper + any |
| Crash Man | Medium | Air Shooter |
| Flash Man | Medium | Metal Blade |
| Heat Man | Hard | Bubble Lead, Item-2 |
| Wood Man | Easy-Medium | Atomic Fire (charged) |
| Wily 1 | Hard | Quick Boomerang |
| Wily 2 | Medium | Bubble Lead |
| Wily 3 | Medium | Quick Boomerang |
| Wily 4 | Hard | All weapons needed |
| Wily 5 | Very Hard | Bubble Lead (required) |

---

*This specification is based on Mega Man 2 (1988/1989) by Capcom for the Nintendo Entertainment System (NES). Values are sourced from ROM data analysis, gameplay testing, and community documentation. The Japanese "Rockman 2" has slightly different difficulty tuning.*
