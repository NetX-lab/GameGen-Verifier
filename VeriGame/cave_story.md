# Cave Story — Complete Game Specification

> A comprehensive specification for faithfully recreating Cave Story (Doukutsu Monogatari, Studio Pixel, 2004 freeware PC version). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics](#3-core-mechanics)
4. [Player Character — Quote](#4-player-character--quote)
5. [Weapons System](#5-weapons-system)
6. [All Enemies — Complete Stats](#6-all-enemies--complete-stats)
7. [All Bosses](#7-all-bosses)
8. [Level/Area Progression](#8-levelarea-progression)
9. [NPCs & Dialog System](#9-npcs--dialog-system)
10. [Items & Pickups](#10-items--pickups)
11. [UI Layout & Screens](#11-ui-layout--screens)
12. [Audio Design](#12-audio-design)
13. [Save System](#13-save-system)
14. [Story & Branching Paths](#14-story--branching-paths)
15. [Best Ending Route](#15-best-ending-route)

---

## 1. Game Overview

- **Genre**: Action-adventure platformer (Metroidvania)
- **Perspective**: 2D side-scrolling
- **Input**: Keyboard (arrow keys for movement, Z = jump, X = shoot, A/S = cycle weapons, W = map, Q = inventory). Controller supported.
- **Objective**: Navigate through a floating island's cave system, uncover the story of the Mimiga race, and defeat the Doctor who threatens them.
- **Lose Condition**: HP reaches zero. Restart from last save point.
- **Win Condition**: Defeat final boss (varies by route: Undead Core or Ballos).
- **Multiple Endings**: 3 endings based on player choices and optional areas explored.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 320 x 240 pixels |
| Scaled display | 640 x 480 (2x), or windowed at native |
| Tile size | 16 x 16 pixels |
| Frame rate | 50 FPS (original freeware) |
| Sprite format | BMP with transparency color key (black = transparent in original) |
| Map format | PXM (tile map), PXE (entity placement), TSC (scripting) |

### Coordinate System

- Origin (0, 0) at top-left.
- Sub-pixel precision: coordinates stored as fixed-point values. 1 tile = 0x2000 sub-pixels (8192). 1 pixel = 0x200 sub-pixels (512).
- Gravity, speed, etc. all use sub-pixel units internally.

### Game Loop

```
1. Process input
2. Run TSC script engine (dialog, events, cutscenes)
3. Update player (movement, physics, weapon fire)
4. Update all NPCs/enemies (AI, movement, attacks)
5. Update all projectiles (bullets, enemy shots)
6. Update particles/effects
7. Check collisions (player-enemy, bullet-enemy, player-pickup)
8. Check triggers (event tiles, NPC interaction zones)
9. Scroll camera to follow player
10. Render background layers (parallax)
11. Render tilemap
12. Render entities (NPCs, enemies, items)
13. Render player
14. Render projectiles and particles
15. Render HUD overlay
16. Render dialog box (if active)
```

---

## 3. Core Mechanics

### Physics

All values in sub-pixel units (1 pixel = 0x200 = 512 sub-pixels).

| Parameter | Value (sub-pixels/frame) | Pixels/frame |
|-----------|--------------------------|--------------|
| Gravity | 0x50 (80) | 0.156 |
| Max fall speed | 0x5FF (1535) | 3.0 |
| Walk acceleration | 0x55 (85) | 0.166 |
| Walk deceleration (friction) | 0x33 (51) | 0.1 |
| Max walk speed | 0x32C (812) | 1.586 |
| Jump initial velocity | -0x500 (-1280) | -2.5 |
| Jump gravity (while holding button) | 0x20 (32) | 0.0625 |
| Jump gravity (button released) | 0x50 (80) | 0.156 |
| Air friction | 0x33 (51) | 0.1 |
| Max air speed (horizontal) | 0x32C (812) | 1.586 |

### Jump Mechanics

- **Jump height**: Varies based on how long the jump button is held.
  - Maximum jump (full hold): approximately 64 pixels (4 tiles).
  - Minimum jump (tap): approximately 16 pixels (1 tile).
- **Variable gravity**: While jump button is held AND vertical velocity is negative (ascending), gravity is reduced (0x20 vs 0x50).
- **Coyote time**: None in original (must be on ground to jump).
- **Double jump**: Not available by default. Booster 2.0 provides upward boost ability.

### Collision Detection

- **Tile collision**: Checked against player's bounding box. Player hitbox: 10 x 16 pixels (centered horizontally on 16x16 sprite).
- **Tile types**:
  | ID | Type | Behavior |
  |----|------|----------|
  | 0x00 | Air | No collision |
  | 0x01-0x3F | Solid | Full block collision from all sides |
  | 0x40 | Slope (45° up-right) | Ramp collision, smooth walking |
  | 0x41 | Slope (45° up-left) | Ramp collision |
  | 0x42 | Slope (gentle up-right, lower) | Half-slope |
  | 0x43 | Slope (gentle up-right, upper) | Half-slope |
  | 0x44 | Spike | Damage tile, 10 HP damage on contact |
  | 0x50 | One-way platform | Solid only from top, can jump through from below |
  | 0x60 | Water (current) | Reduced gravity, different physics |
  | 0x61 | Water (still) | Same as current but no push |
  | 0x62 | Wind (left) | Pushes player left |
  | 0x63 | Wind (up) | Pushes player up |
  | 0x80+ | Breakable | Destroyed by weapons, becomes air |

### Water Physics

When player is submerged in water tiles:
- Gravity: 0x28 (half normal)
- Max fall speed: 0x2FF (half normal)
- Walk speed: 0x196 (half normal)
- Jump velocity: -0x280 (half normal)
- Air meter: Player can survive 100 frames (2 seconds) underwater before taking 10 damage and restarting air timer.
- Air meter resets when surfacing.
- Air bubbles appear every 20 frames while submerged (cosmetic).

---

## 4. Player Character — Quote

### Stats

| Stat | Starting | Maximum |
|------|----------|---------|
| HP | 3 | 50 (with all Life Capsules) |
| Weapons | None (Polar Star found early) | Up to 5 weapons equipped |
| Movement | Walk + Jump | Walk + Jump + Booster (0.8 or 2.0) |

### Hitbox

- **Body hitbox**: 10 pixels wide x 16 pixels tall, centered on sprite.
- **Offset from sprite**: Sprite is 16x16; hitbox is inset 3 pixels on each side horizontally.

### Health System

- HP displayed as numeric value on HUD (e.g., "03/03").
- Damage taken reduces HP.
- At 0 HP: Death. Screen fades, "Game Over" message, restart from last save.
- **No invincibility frames on damage** by default (some events grant temporary invincibility).
- Actually, player gets 2 seconds (~100 frames) of invincibility after damage from a projectile or enemy collision.
- During invincibility, player sprite flickers (every 2 frames).

### Life Capsules

Increase max HP by set amounts. Located throughout the game:

| # | Location | HP Increase |
|---|----------|-------------|
| 1 | First Cave | +3 (total: 6) |
| 2 | Mimiga Village (Yamashita Farm) | +3 (total: 9) |
| 3 | Egg Corridor | +3 (total: 12) |
| 4 | Bushlands | +5 (total: 17) |
| 5 | Sand Zone | +5 (total: 22) |
| 6 | Labyrinth | +5 (total: 27) |
| 7 | Plantation | +5 (total: 32) |
| 8 | Plantation (hidden) | +5 (total: 37) |
| 9 | Last Cave | +5 (total: 42) |
| 10 | Sacred Ground (Hell) | +3 (total: 45) |
| 11 | Sacred Ground (Hell) | +5 (total: 50) |

---

## 5. Weapons System

### Weapon Experience System

- Enemies drop **yellow triangles** (weapon energy/EXP).
- Collecting EXP increases the current weapon's level (1 -> 2 -> 3).
- Taking damage reduces weapon EXP (may cause level down).
- Each weapon has 3 levels, each with different behavior and damage.

### EXP Thresholds per Level

| Level | EXP Required (from previous level) |
|-------|-------------------------------------|
| Level 1 | 0 (base) |
| Level 2 | Varies by weapon (see below) |
| Level 3 | Varies by weapon (see below) |

### Damage on Hit (EXP loss)

- When Quote takes damage, current weapon loses EXP equal to the damage taken.
- If EXP drops below 0 at Level 2, weapon reverts to Level 1 (EXP set to max of Level 1).
- If EXP drops below 0 at Level 3, weapon reverts to Level 2 (EXP set to max of Level 2).

### All Weapons

#### Polar Star (Starting weapon)
| Level | EXP to Next | Damage | Fire Rate (frames between shots) | Max Bullets on Screen | Range | Description |
|-------|-------------|--------|-----------------------------------|----------------------|-------|-------------|
| 1 | 10 | 1 | 8 | 3 | 6 tiles | Small bullet, short range |
| 2 | 20 | 2 | 6 | 3 | 8 tiles | Medium bullet, medium range |
| 3 | MAX | 4 | 4 | 3 | 12 tiles | Large bullet, long range with slight trail |

- **Obtained**: Found in First Cave.
- **Fire direction**: 4 directions (left, right, up, down).
- **Bullet speed**: 4 pixels/frame.

#### Fireball
| Level | EXP to Next | Damage | Fire Rate | Max Bullets | Behavior |
|-------|-------------|--------|-----------|-------------|----------|
| 1 | 10 | 2 | 10 | 2 | Single fireball, bounces along ground |
| 2 | 20 | 3 | 8 | 3 | Two fireballs |
| 3 | MAX | 4 | 6 | 4 | Three fireballs, larger, passes through walls |

- **Obtained**: Santa's house in Mimiga Village (given by Santa).
- **Special**: Affected by gravity; bounces off floors and walls.
- **Fireball speed**: 2 px/frame horizontal, gravity-affected vertically.

#### Missile Launcher
| Level | EXP to Next | Damage | Fire Rate | Max Missiles | Ammo |
|-------|-------------|--------|-----------|-------------|------|
| 1 | 10 | 10 | 12 | 1 | Uses missile ammo (max varies) |
| 2 | 20 | 15 | 10 | 2 | Same |
| 3 | MAX | 20 | 8 | 3 | Same + slight homing |

- **Obtained**: Egg Corridor (Egg No. 00).
- **Ammo**: Limited missile ammo. Starting max: 10. Upgradeable to 24 (Missile Expansion items).
- **Replenished by**: Missile pickups from enemies (2 missiles each).
- **Level 3 homing**: Missiles gently curve toward nearest enemy (turning rate: 2 degrees/frame).

#### Super Missile Launcher
- Replaces Missile Launcher (upgraded version).
- Same stats but Level 3 does triple damage (60) and larger explosion radius (32x32 pixels).
- **Obtained**: Traded in Labyrinth.

#### Bubbler
| Level | EXP to Next | Damage | Fire Rate | Behavior |
|-------|-------------|--------|-----------|----------|
| 1 | 10 | 1 | 4 | Tiny bubbles that travel a short distance |
| 2 | 20 | 2 | 3 | Bubbles orbit around Quote as a shield |
| 3 | MAX | 3 | 2 | Level 2 shield + pressing fire releases all as projectiles |

- **Obtained**: Mimiga Village (trade Polar Star to Bubbler exchange).
- **Note**: Trading away Polar Star means losing it. Affects weapon path.

#### Blade
| Level | EXP to Next | Damage | Fire Rate | Behavior |
|-------|-------------|--------|-----------|----------|
| 1 | 30 | 15 | 10 | Slash directly in front |
| 2 | 60 | 18 | 10 | Slash + a spirit projectile follows |
| 3 | MAX | 1 per hit (rapid) | 1 | King's spirit fires forward continuously, massive damage over time |

- **Obtained**: After King's death (Sand Zone, story event).
- **Level 3**: Summons King's ghost as a continuous forward beam. Hits multiple times for massive DPS.

#### Snake
| Level | EXP to Next | Damage | Fire Rate | Max Bullets | Behavior |
|-------|-------------|--------|-----------|-------------|----------|
| 1 | 10 | 4 | 6 | 2 | Wavy projectile, passes through walls |
| 2 | 20 | 6 | 6 | 3 | Larger wavy projectile |
| 3 | MAX | 8 | 6 | 4 | Large snake, passes through walls and enemies |

- **Obtained**: Trade Polar Star for Snake (Chaba in Sand Zone). Cannot get both Snake and Bubbler.

#### Nemesis
| Level | EXP to Next | Damage | Fire Rate | Behavior |
|-------|-------------|--------|-----------|----------|
| 1 | 1 | 12 | 4 | Powerful wide shot |
| 2 | 1 | 6 | 6 | Medium shot |
| 3 | MAX | 1 | 10 | Rubber ducks. Intentionally terrible. |

- **Obtained**: Trade Blade for Nemesis in Plantation.
- **Gimmick**: Gets WORSE at higher levels. Best used at Level 1. Encourages getting hit to lose EXP.

#### Spur (Best Ending route only)
| Charge Level | Damage | Behavior |
|-------------|--------|----------|
| Uncharged | 4 | Like Polar Star Level 3 |
| Charge 1 | 12 | Medium beam |
| Charge 2 | 20 | Large beam |
| MAX Charge | 40 | Massive beam, pierces all enemies, screen-wide |

- **Obtained**: Do NOT trade Polar Star. Return to First Cave with Booster 2.0. Professor Booster upgrades Polar Star to Spur.
- **Mechanic**: Hold fire button to charge. Release to fire. No ammo limit.
- **Charge time**: ~2 seconds to MAX charge. Visual indicator on Quote (glowing effect intensifies).

---

## 6. All Enemies — Complete Stats

### First Cave / Mimiga Village Area

| Enemy | HP | Damage (contact) | EXP Drop | Behavior |
|-------|----|-------------------|----------|----------|
| Critter (small, blue) | 1 | 1 | 1 | Hops toward player. Jump height: 2 tiles. |
| Bat (small) | 1 | 1 | 1 | Flies in sine wave pattern. Speed: 1 px/frame. |
| Door (Mimiga Village) | N/A | 0 | 0 | Interactive object, not enemy |

### Egg Corridor

| Enemy | HP | Damage | EXP | Behavior |
|-------|----|--------|-----|----------|
| Beetle (green) | 3 | 2 | 2 | Walks on ceiling, drops down when player is below. |
| Basil | 4 | 3 | 3 | Flies horizontally back and forth. Speed: 2 px/frame. |
| Beetle (orange) | 5 | 3 | 4 | Same as green but faster, drops immediately. |
| Critter (orange) | 3 | 2 | 2 | Like blue critter but higher jumps and faster. |
| Sky Dragon (mini) | 5 | 2 | 5 | Stationary, shoots fireballs. Fireball speed: 3 px/frame. |

### Grasstown / Bushlands

| Enemy | HP | Damage | EXP | Behavior |
|-------|----|--------|-----|----------|
| Jelly | 4 | 2 | 3 | Floats up and down, shoots small projectiles downward every 60 frames. |
| Frog (small) | 3 | 2 | 2 | Hops toward player. Faster than critters. |
| Frog (large) | 8 | 3 | 5 | Big hops, spawns 2 small frogs on death. |
| Power Critter | 6 | 3 | 6 | Large critter. Fast jumps, high damage. |
| Press | 10 | 10 | 0 | Giant block that falls from ceiling. Instant kill essentially. Respawns after 120 frames. |
| Pignon | 3 | 2 | 2 | Mushroom enemy. Walks back and forth on platforms. |

### Sand Zone

| Enemy | HP | Damage | EXP | Behavior |
|-------|----|--------|-----|----------|
| Crow | 3 | 3 | 3 | Perches until player is near, then swoops diagonally. |
| Skeleton | 8 | 3 | 5 | Throws bones in arc. Bone damage: 2. |
| Polish | 12 | 3 | 8 | Large bouncing enemy. Splits into 2 Baby Polishes on death. |
| Baby Polish | 4 | 2 | 3 | Small bouncing enemy from Polish split. |
| Sandcroc | 6 | 5 | 4 | Hidden in sand. Lunges upward when player walks over. |
| Armadillo | 10 | 3 | 6 | Rolls into ball, charges at player. Speed: 3 px/frame when rolling. |
| Curly's Mimigas | 10 | 3 | 0 | Friendly fire during Curly boss fight. Don't kill. |

### Labyrinth

| Enemy | HP | Damage | EXP | Behavior |
|-------|----|--------|-----|----------|
| Gaudi | 5 | 3 | 4 | Insect. Walks walls and ceilings. |
| Gaudi (armored) | 10 | 4 | 6 | Same but with shell; takes reduced damage from front. |
| Gaudi (flying) | 6 | 3 | 5 | Flies in patterns, shoots projectiles. |
| Fire Whirl | 8 | 4 | 5 | Orbits around a fixed point. Radius: 3 tiles. |
| Buyobuyo | 4 | 3 | 3 | Bounces off walls unpredictably. |
| Pooh Black | 20 | 5 | 10 | Mini-boss type. Charges, throws projectiles. |

### Waterway

| Enemy | HP | Damage | EXP | Behavior |
|-------|----|--------|-----|----------|
| Jelly (water) | 5 | 2 | 3 | Floats in water, homes toward player slowly. |
| Current Pushers | N/A | 0 | 0 | Water current tiles, environmental hazard. |
| Ironhead (boss) | See bosses | | | |

### Egg Corridor 2 (Revisited)

| Enemy | HP | Damage | EXP | Behavior |
|-------|----|--------|-----|----------|
| Dragon (zombie) | 15 | 5 | 8 | Reanimated Sky Dragons. Shoot fireballs rapidly. |
| Beetle (red) | 8 | 4 | 5 | Fast, aggressive, drops from ceiling instantly. |
| Sisters | Boss | | | See bosses. |

### Plantation

| Enemy | HP | Damage | EXP | Behavior |
|-------|----|--------|-----|----------|
| Droll | 10 | 3 | 5 | Tall enemy, jumps and shoots bouncing projectiles. |
| Puppy | 1 | 0 | 0 | Friendly NPC dogs. Don't harm. |
| Midorin | 6 | 2 | 3 | Plant enemy, stationary, shoots seeds. |
| Press (Plantation) | 10 | 10 | 0 | Same as Bushlands Press. |
| Stumpy | 8 | 3 | 5 | Tree stump that hops toward player. |

### Last Cave / Sacred Ground (Hell)

| Enemy | HP | Damage | EXP | Behavior |
|-------|----|--------|-----|----------|
| Bute (sword) | 5 | 5 | 3 | Fast flying enemy with sword slash attack. |
| Bute (archer) | 5 | 5 (arrow: 3) | 3 | Flies, shoots arrows at player. |
| Mesa (large block) | 20 | 10 | 5 | Giant block that falls. Very heavy damage. |
| Deleet | 10 | 10 (explosion) | 0 | Stationary bomb. Counts down from 3 (displayed). Explodes in 8-tile radius. |
| Rolling | 15 | 8 | 5 | Spiked ball that rolls along surfaces. |
| Green Devil | 8 | 5 | 4 | Fast flying, erratic movement. |

---

## 7. All Bosses

### Boss: Balrog (Recurring)

Fought 3 times. Each encounter has more HP and new attacks.

**Fight 1 (Mimiga Village)**:
- HP: 30
- Attacks: Charges left/right (speed: 2 px/frame). Jumps to player's position.
- Damage: 2 (contact)
- Pattern: Jump -> land near player -> charge -> repeat

**Fight 2 (Sand Zone)**:
- HP: 50
- Attacks: Previous + drops from ceiling, shockwave on landing (16px range).
- Damage: 3
- New: Throws smaller enemies (2 Critters) periodically.

**Fight 3 (Plantation)**:
- HP: 80
- Attacks: All previous + missile barrage (4 missiles, homing slightly).
- Damage: 5
- Missiles: 3 damage each, speed 3 px/frame.

### Boss: Igor (Egg Corridor)

- HP: 50
- Attacks: Throws boulders (arc trajectory), charges forward.
- Boulder damage: 3, speed: 2 px/frame parabolic.
- Charge damage: 5, speed: 3 px/frame.
- Pattern: Throw 3 boulders -> charge -> pause 60 frames -> repeat.
- Arena: Flat room, 20 tiles wide.

### Boss: Balfrog (Mimiga Village, Gum Room)

- HP: 60
- Phase 1: Small frog form, hops around, shoots projectiles.
  - Projectile: 3 damage, speed 2 px/frame, aimed at player.
  - 3 hops then shoot, repeat.
- Phase 2 (at 30 HP): Transforms into giant frog.
  - Fills half the room. Jumps to ceiling, drops down.
  - Landing shockwave: 5 damage, 3-tile range.
  - Spawns small frogs (3 HP each) from mouth every 2 jumps.
  - Only vulnerable when mouth is open (after landing, 30 frames).

### Boss: Curly Brace (Sand Zone)

- HP: 50
- Attacks: Polar Star shots (Level 2 equivalent), missile launcher shots.
- Polar Star: 2 damage, rapid fire (every 6 frames).
- Missiles: 5 damage each, slight homing.
- Behavior: Strafes left/right, jumps to dodge player shots, aims at player.
- After defeat: Becomes ally (story event).

### Boss: Omega (Egg Corridor, Hidden)

- HP: 80
- Attacks: Rises from ground, shoots eggs that hatch into small enemies.
- Egg damage: 3, hatched enemy: 2 HP, 2 damage.
- Body slam when player is directly below: 5 damage.
- Only vulnerable at head (top portion of sprite, 16x16 pixel area).
- Rises and descends periodically. Exposed for 90 frames, submerged for 60 frames.

### Boss: Monster X (Labyrinth)

- HP: 100
- Phase 1: Drives back and forth (tank-like). Shoots bullets from turrets.
  - 4 turrets, each fires every 30 frames. Bullet damage: 3.
  - Destroy turrets individually (15 HP each) to reduce fire.
  - Contact damage: 5.
- Phase 2 (all turrets destroyed): Opens face. Charges rapidly back and forth.
  - Speed: 4 px/frame.
  - Only vulnerable during open-face pause (20 frames every 3 charges).

### Boss: Core (Waterway Chamber)

- HP: 150
- Phase: Large stationary core protected by 5 orbiting mini-cores.
- Mini-cores: 30 HP each. Shoot projectiles.
- Mini-core projectile: 3 damage, speed 2 px/frame.
- Core exposed when 3+ mini-cores destroyed. Fires massive beam.
- Beam: 10 damage per hit, sweeps vertically over 3 seconds.
- Player fights while on raft (forced scrolling section beforehand).
- Water rises during fight; drowning hazard.

### Boss: Ironhead (Waterway)

- HP: 60
- Arena: Underwater auto-scrolling.
- Attacks: Charges from right side of screen. Speed: 4 px/frame.
- Contact: 5 damage.
- Spawns fish enemies (1 HP, 2 damage) periodically.
- Pattern: Charge across screen -> exit left -> reenter from right after 60 frames.
- Player must shoot while managing air meter.

### Boss: Sisters (Egg Corridor 2)

- HP: 100 each (2 dragons).
- Dragon 1: Sweeps left-right, shoots 3-fireball spread.
- Dragon 2: Follows delayed pattern, shoots 5-fireball spread.
- Fireball: 4 damage, speed 3 px/frame.
- Must kill both. When first dies, second becomes faster and more aggressive.

### Boss: Undead Core (Final boss, Normal ending)

- HP: 200
- Phase 1: Core opens periodically, shoots homing orbs.
  - Orbs: 5 damage, speed 1.5 px/frame, homing.
  - Core vulnerable when open: 30 frames every 120 frames.
- Phase 2 (100 HP): Fires sweeping beam + orbs simultaneously.
  - Beam: 8 damage, sweeps 180° over 2 seconds.
- Phase 3 (50 HP): Summons enemies from sides, rapid orb fire.
- Curly assists (shoots at core, deals ~1 damage/second to core).
- Misery and Sue attack player periodically (3 damage projectiles).

### Boss: Heavy Press (Sacred Ground / Hell)

- HP: 200
- Giant block that drops from ceiling.
- Damage: Instant kill on contact.
- After dodging drop, vulnerable on sides for 60 frames.
- Shoots lightning bolts during vulnerable phase. Lightning: 10 damage.
- Speed increases each cycle (drop speed: 4 -> 6 -> 8 px/frame).

### Boss: Ballos (Final boss, Best Ending)

- HP: 500 total across 4 phases.
- **Phase 1** (HP 500-375): Floats, throws eye projectiles in expanding circles.
  - 8 projectiles per volley, damage: 5.
  - Vulnerable at all times.
- **Phase 2** (HP 375-250): Bounces around room like a ball.
  - Contact: 10 damage.
  - Creates shockwaves on landing that travel along floor.
  - Shockwave: 5 damage.
- **Phase 3** (HP 250-125): Grows spiked crown. Spins spiked balls on chains.
  - 8 spiked balls orbiting. Each: 10 damage.
  - Orbit radius expands and contracts.
  - Eyes shoot targeted beams: 8 damage.
- **Phase 4** (HP 125-0): Ceiling collapses. Spikes descend from top.
  - Must avoid falling spikes (instant kill) while attacking Ballos.
  - Ballos charges left/right. Speed: 5 px/frame.
  - Butes spawn from sides (2 every 5 seconds).

---

## 8. Level/Area Progression

### Area Order (Main Route)

| Order | Area Name | Description | Key Events |
|-------|-----------|-------------|------------|
| 1 | Start Point (First Cave) | Tutorial area, get Polar Star | Learn controls |
| 2 | Mimiga Village | Hub area with NPCs, shops, save | Meet Mimigas |
| 3 | Egg Corridor | Linear corridor with eggs and enemies | Fight Igor |
| 4 | Grasstown (Bushlands) | Large area with Execution Chamber | Get Jellyfish Juice, fight Balfrog |
| 5 | Sand Zone | Desert caves, meet Curly Brace | Fight Omega (optional), get Blade |
| 6 | Labyrinth | Complex maze area | Fight Monster X, get Booster |
| 7 | Waterway | Underwater section | Fight Ironhead |
| 8 | Mimiga Village (Revisited) | Changed after events | Story events |
| 9 | Egg Corridor 2 | Destroyed version of Egg Corridor | Fight Sisters |
| 10 | Outer Wall | Exterior of island | Scenic, few enemies |
| 11 | Plantation | Slave camp area | Prepare for final |
| 12 | Last Cave | Difficult platforming | Final challenge before boss |
| 13 | Balcony / Throne Room | Final area | Fight Undead Core (normal) |
| 14 | Sacred Ground (Hell) | Optional hardest area | Fight Heavy Press, Ballos (best ending) |

### Area Dimensions (approximate)

| Area | Width (tiles) | Height (tiles) | Rooms/Maps |
|------|--------------|----------------|------------|
| First Cave | 80 | 20 | 1 |
| Mimiga Village | 120 | 40 | 5 sub-maps |
| Egg Corridor | 200 | 30 | 1 long corridor |
| Grasstown | 150 | 80 | 3 sub-maps |
| Sand Zone | 160 | 60 | 3 sub-maps |
| Labyrinth | 200 | 100 | 6 sub-maps |
| Waterway | 300 | 25 | 1 (auto-scroll) |
| Plantation | 100 | 80 | 2 sub-maps |
| Last Cave | 120 | 40 | 1 |
| Sacred Ground | 80 | 200 | 4 sub-maps |

### Save Points

Save points are scattered through each area (glowing floppy disk icon):
- First Cave: 1
- Mimiga Village: 2
- Egg Corridor: 2
- Grasstown: 3
- Sand Zone: 2
- Labyrinth: 3
- Waterway: 1
- Plantation: 2
- Last Cave: 1
- Sacred Ground: 0 (no saves in Hell — must complete in one run)

---

## 9. NPCs & Dialog System

### Dialog System

- Text appears in a box at bottom of screen (240 pixels wide, 48 pixels tall).
- Text renders character by character at 2 characters per frame (25 chars/second at 50 FPS).
- Pressing jump/confirm button during text: skips to end of current message.
- NPC interaction: Stand near NPC + press Down arrow.
- Dialog boxes can show NPC portrait (left side, 48x48 pixels).
- TSC script system controls all dialog, events, map transitions, and cutscenes.

### Key NPCs

| NPC | Location | Role |
|-----|----------|------|
| King | Mimiga Village | Mimiga leader. Gives Blade weapon upon death. |
| Toroko | Mimiga Village | Central to plot. Kidnapped by Doctor. |
| Sue Sakamoto | Various | Human researcher turned Mimiga. Ally. |
| Kazuma | Various | Sue's brother. Computer expert. |
| Curly Brace | Sand Zone, later ally | Robot like Quote. Becomes ally after boss fight. |
| Professor Booster | Labyrinth/First Cave | Inventor. Gives Booster item. Key to best ending. |
| Balrog | Various | Recurring mini-boss, eventually helps player. Catchphrase: "Huzzah!" |
| Misery | Various | Witch, servant of the Doctor. |
| The Doctor | Plantation/Final | Main antagonist. Seeks Demon Crown. |
| Jenka | Sand Zone | Old witch. Sends player on puppy quest (5 puppies). |
| Santa | Mimiga Village | Gives Fireball weapon. |
| Jack | Mimiga Village | Mimiga NPC. Various info. |
| Mahin | Mimiga Village | Mimiga NPC. |
| Chaba | Sand Zone | Weapon trader. Trades Polar Star for Snake. |
| Mrs. Little | Various | Tiny NPC. Easy to miss. |
| Itoh | Plantation | Human prisoner. |
| Momorin | Plantation | Kazuma's mother. Builds rocket. |

---

## 10. Items & Pickups

### Dropped Pickups (from enemies)

| Pickup | Appearance | Effect |
|--------|-----------|--------|
| Energy (small) | Small yellow triangle | +1 weapon EXP |
| Energy (medium) | Medium yellow triangle | +3 weapon EXP |
| Energy (large) | Large yellow triangle | +5 weapon EXP |
| Heart (small) | Small red heart | Restore 2 HP |
| Heart (large) | Large red heart | Restore 6 HP |
| Missile ammo | Small missile icon | +2 missiles (capped at max) |

### Key Items (Inventory)

| Item | Obtained | Purpose |
|------|----------|---------|
| Map System | Mimiga Village | Enables map display (W key) |
| Arthur's Key | Mimiga Village | Opens Arthur's house |
| ID Card | Egg Corridor | Opens barriers in Egg Corridor |
| Jellyfish Juice | Grasstown | Puts out fireplace in Mimiga Village |
| Charcoal | Mimiga Village | Given to Mahin for explosive |
| Gum Key | Mimiga Village | Opens Gum Room |
| Puppies (5) | Sand Zone | Return to Jenka |
| Clinic Key | Plantation | Opens clinic |
| Mushroom Badge | Mimiga Village | Show to Ma Pignon |
| Curly's Panties | Curly's House | Joke item. Shows in inventory. |
| Booster 0.8 | Labyrinth | Horizontal air boost. Press jump in air for burst of horizontal speed. |
| Booster 2.0 | Labyrinth (best ending only) | Omni-directional air boost. Press jump + direction in air. |
| Tow Rope | Waterway | Carry Curly Brace |
| Air Tank | Waterway | Curly can survive underwater |
| Arms Barrier | Plantation | Halves weapon EXP loss on damage |
| Alien Medal | Sacred Ground | Proof of completing Hell route |

### Booster Item Details

**Booster 0.8**:
- Activates when pressing jump while airborne.
- Provides horizontal boost in facing direction: 3 px/frame for 30 frames.
- Can only be used once per airborne period.
- Fuel gauge: 100%. Depletes at 3.3% per frame while active. Recharges on ground.

**Booster 2.0**:
- Activates when pressing jump + direction while airborne.
- All 4 directions + diagonals.
- Vertical boost: -3 px/frame upward for 30 frames.
- Horizontal boost: 3 px/frame for 30 frames.
- Same fuel system as 0.8 but recharges in 30 frames on ground.
- Required for accessing Sacred Ground (Hell).

---

## 11. UI Layout & Screens

### HUD (In-game)

```
+------------------------------------------------------------------+
|  [WEAPON ICON] Lv3  [EXP BAR ████████░░]  HP: 32/32             |
|  [AMMO: 24/24]                                                    |
|                                                                   |
|                   (GAMEPLAY AREA)                                 |
|                   320 x 200 pixels                                |
|                                                                   |
|                                                                   |
+------------------------------------------------------------------+
```

- **Top-left**: Current weapon icon (16x16) + Level indicator ("Lv1", "Lv2", "Lv3").
- **EXP Bar**: 40 pixels wide. Fills as EXP collected. Flashes when at max level.
- **HP**: Numeric display "current/max" in white text.
- **Ammo**: Only shown for Missile Launcher. "current/max" below weapon icon.
- **Air meter**: Appears when underwater. Bar depletes over 100 frames. Red when low.

### Title Screen

```
+----------------------------------+
|                                  |
|         CAVE STORY               |
|      ドウクツ物語                  |
|                                  |
|   [Quote sprite animation]       |
|                                  |
|       NEW GAME                   |
|       LOAD GAME                  |
|                                  |
|    2004 Studio Pixel             |
+----------------------------------+
```

### Map Screen (W key)

```
+----------------------------------+
|  [Current Area Name]             |
|  +----------------------------+  |
|  |                            |  |
|  |  Tile map of current area  |  |
|  |  Player position = white   |  |
|  |  dot, blinking             |  |
|  |  Save points = blue dots   |  |
|  |                            |  |
|  +----------------------------+  |
+----------------------------------+
```

### Inventory Screen (Q key or I key)

```
+----------------------------------+
|        INVENTORY                 |
|  +---+---+---+---+---+---+      |
|  | 1 | 2 | 3 | 4 | 5 | 6 |     |
|  +---+---+---+---+---+---+      |
|  Weapons (cycle with A/S)       |
|                                  |
|  KEY ITEMS:                      |
|  [Item 1] [Item 2] [Item 3]     |
|  [Item 4] [Item 5] [Item 6]     |
|  [Item 7] [Item 8] ...          |
|                                  |
|  [Selected item description]    |
+----------------------------------+
```

### Save/Load Screen

```
+----------------------------------+
|         SAVE GAME                |
|                                  |
|  Location: [Area Name]          |
|  HP: XX/XX                       |
|  Time: HH:MM                    |
|  Weapon: [Current Weapon]       |
|                                  |
|    > SAVE    CANCEL              |
+----------------------------------+
```

### Game Over Screen

```
+----------------------------------+
|                                  |
|        GAME OVER                 |
|                                  |
|   [Quote falling sprite]        |
|                                  |
|     CONTINUE                     |
|     TITLE SCREEN                 |
|                                  |
+----------------------------------+
```

---

## 12. Audio Design

### Music Tracks (ORG format — original chiptune)

| Track # | Name | Context | Tempo (BPM) | Feel |
|---------|------|---------|-------------|------|
| 01 | "Mischievous Robot" | Title screen | 140 | Upbeat, bouncy |
| 02 | "Mimiga Village" | Mimiga Village | 120 | Calm, homey |
| 03 | "Plant" | Grasstown/Bushlands | 130 | Adventurous, steady |
| 04 | "Pulse" | Egg Corridor | 150 | Urgent, driving |
| 05 | "Gravity" | First Cave | 100 | Mysterious, quiet |
| 06 | "Eyes of Flame" | Boss fights (various) | 160 | Intense, aggressive |
| 07 | "Gestation" | Sand Zone | 110 | Desert feel, tense |
| 08 | "Labyrinth Fight" | Labyrinth combat | 140 | Frantic |
| 09 | "Scorching Back" | Last Cave | 170 | High energy, desperate |
| 10 | "Moonsong" | Outer Wall | 90 | Melancholic, beautiful |
| 11 | "Hero's End" | Ending (normal) | 100 | Bittersweet |
| 12 | "Balrog's Theme" | Balrog encounters | 150 | Comedic, threatening |
| 13 | "Running Hell" | Sacred Ground | 180 | Extreme intensity |
| 14 | "Seal Chamber" | Ballos fight | 170 | Epic, dark |
| 15 | "White" | Best ending | 80 | Peaceful, serene |
| 16 | "Safety" | Save rooms | 70 | Calm, safe |
| 17 | "Fanfare" | Item acquired | 130 | Triumphant (5 seconds) |
| 18 | "Waterway" | Waterway area | 120 | Flowing, aquatic |
| 19 | "Jenka 1" | Jenka's house | 80 | Old, mystical |
| 20 | "Jenka 2" | Jenka backstory | 60 | Sad, slow |

### Sound Effects

| Sound | Trigger | Description |
|-------|---------|-------------|
| Shot fire | Pressing X with weapon | Short blip, varies by weapon |
| Enemy hit | Bullet hits enemy | Impact thud |
| Enemy death | Enemy HP reaches 0 | Pop/explosion, pitch varies by enemy size |
| Player hurt | Quote takes damage | Sharp buzz/impact |
| Player death | HP reaches 0 | Descending tone |
| Jump | Pressing Z on ground | Short whoosh |
| Land | Quote lands on ground | Soft thud |
| Door open | Entering door/transition | Mechanical click |
| Item get | Collecting key item | Ascending chime (triggers fanfare music) |
| Health pickup | Heart collected | Soft chime |
| EXP pickup | Triangle collected | Quick ding (higher pitch for larger) |
| Level up | Weapon levels up | Ascending sweep |
| Level down | Weapon loses level on damage | Descending buzz |
| Save | Using save point | Confirmation tone |
| Menu open | Opening inventory/map | Click |
| Booster | Using booster item | Jet/whoosh sound |
| Explosion | Bomb/missile explosion | Deep boom |
| Splash | Entering/exiting water | Water splash |
| Bubble | Air bubble in water | Soft pop |
| NPC talk | Dialog text printing | Soft blip per character |

---

## 13. Save System

- **Save points**: Physical objects in game world (floppy disk icon, 16x16 sprite).
- Walk up to save point and press Down to interact.
- **Single save slot** in original freeware version.
- **Saved data**: Player position (area + coordinates), HP, weapons and their levels/EXP, all key items collected, all flags (story events triggered), missile ammo, playtime.
- **Save file**: Profile.dat in game directory.
- **Continue**: Loads from last save point. Player restarts at that save point's exact location.
- **No auto-save**: Player must manually save at save points.

---

## 14. Story & Branching Paths

### Three Endings

**Bad Ending (Kazuma Ending)**:
- Trigger: Agree to escape with Kazuma in Plantation (say "Yes" to his request).
- Result: Quote and Kazuma flee the island. Mimigas and others are left behind.
- Cutscene: Simple text ending showing island's fate.

**Normal Ending**:
- Trigger: Refuse Kazuma's offer. Fight through Last Cave. Defeat Undead Core.
- Result: Island saved but Curly dies (if not rescued properly).
- Cutscene: Quote escapes with surviving characters. Bittersweet.

**Best Ending**:
- Trigger: Complete all optional requirements (see Section 15).
- Result: Quote saves everyone including Curly. Defeats Ballos in Sacred Ground.
- Cutscene: Full happy ending. All characters shown in epilogue.

### Key Story Flags

| Flag | Event | Impact |
|------|-------|--------|
| BOOSTER_SKIP | Don't talk to Professor Booster when he falls in Labyrinth | Get Booster 2.0 instead of 0.8 later |
| CURLY_SAVED | Drain water from Curly in Waterway with Tow Rope | Curly survives for best ending |
| MUSHROOM | Get Ma Pignon mushroom in Mimiga Village cemetery | Trade for item needed for Hell |
| IRON_BOND | Get Iron Bond item from Curly in Plantation (she must be alive) | Required to access Sacred Ground |
| CLINIC | Visit Plantation clinic to cure Curly of amnesia | Part of best ending chain |

---

## 15. Best Ending Route — Detailed Requirements

1. **Do NOT talk to Professor Booster** when he falls in Labyrinth. Walk past him. He survives and upgrades Polar Star to Spur later, and gives Booster 2.0.
2. **Get the Tow Rope** in Waterway house before fighting Core boss.
3. **Carry Curly** through Waterway after Core fight (she's unconscious).
4. **Drain Curly** at the small cabin in Waterway (interact with bed/drainage).
5. **In Plantation**: Visit Curly in clinic. Show Mushroom Badge to Ma Pignon in cemetery (must fight Ma Pignon mini-boss, 30 HP).
6. **Get Iron Bond** from Curly (she's in Plantation after being cured).
7. **Get Booster 2.0** from Professor Booster (alive because you skipped him earlier).
8. **Return to First Cave** with Booster 2.0. Professor Booster upgrades Polar Star to **Spur**.
9. **After defeating Undead Core**: Use Iron Bond to access the prefab building on Balcony.
10. **Enter Sacred Ground (Hell)**: 4 rooms of extremely difficult platforming + 2 bosses (Heavy Press + Ballos).
11. **Defeat Ballos** to get Best Ending.

---

## Appendix A: TSC Script System

The game's events are controlled by TSC (Text Script) files:

### Key Commands

| Command | Parameters | Effect |
|---------|-----------|--------|
| `<MSG` | None | Open text box |
| `<END` | None | Close text box, end event |
| `<TRA` | Map, Event, X, Y | Transport player to map at position |
| `<GIT` | Item ID | Show item graphic in text box |
| `<FAC` | Face ID | Show NPC portrait |
| `<SOU` | Sound ID | Play sound effect |
| `<CMU` | Track ID | Change music |
| `<FL+` | Flag ID | Set flag |
| `<FL-` | Flag ID | Clear flag |
| `<FLJ` | Flag, Event | Jump to event if flag set |
| `<AM+` | Weapon ID, Ammo | Give weapon |
| `<AM-` | Weapon ID | Remove weapon |
| `<EQ+` | Equipment bits | Give equipment |
| `<IT+` | Item ID | Give inventory item |
| `<ML+` | Amount | Increase max HP |
| `<ANP` | Entity, Anim, Dir | Animate NPC |
| `<MNP` | Entity, X, Y, Dir | Move NPC |
| `<DNP` | Entity | Delete NPC |
| `<NOD` | None | Wait for player input |
| `<WAI` | Frames | Wait N frames |
| `<QUA` | Duration | Screen shake |

---

## Appendix B: Timing Constants

| Constant | Value | Notes |
|----------|-------|-------|
| Frames per second | 50 | Original freeware |
| Invincibility after damage | 100 frames | 2 seconds |
| Sprite flicker rate | Every 2 frames | During invincibility |
| Air timer underwater | 100 frames | 2 seconds |
| Text display speed | 2 chars/frame | 25 chars/sec |
| Save point proximity | 16 pixels | Must be within 16px to interact |
| Boss health bar fill rate | 2 HP/frame | Visual bar fills on boss entry |
| Screen fade duration | 20 frames | 0.4 seconds |
| Map transition | 30 frames | 0.6 seconds fade + load |
| Booster fuel | 100% | Depletes at 3.3%/frame when active |
| Booster recharge | 30 frames | When on ground |
| Weapon level up flash | 30 frames | Visual effect duration |
| Heart pickup despawn | 600 frames | 12 seconds |
| EXP pickup despawn | 600 frames | 12 seconds |
| Missile pickup despawn | 600 frames | 12 seconds |
