# Super Mario Bros. — Complete Game Specification

> A comprehensive specification for faithfully recreating the original Super Mario Bros. (Nintendo, 1985 NES/Famicom version). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Physics System](#3-physics-system)
4. [Player States & Power-ups](#4-player-states--power-ups)
5. [All Enemy Types — Complete Stats](#5-all-enemy-types--complete-stats)
6. [Block & Item System](#6-block--item-system)
7. [Level Structure — All 8 Worlds](#7-level-structure--all-8-worlds)
8. [World-Specific Mechanics](#8-world-specific-mechanics)
9. [Scoring System](#9-scoring-system)
10. [UI Layout & Screen Flow](#10-ui-layout--screen-flow)
11. [Audio Design](#11-audio-design)
12. [Animation System](#12-animation-system)
13. [Game Progression & Second Quest](#13-game-progression--second-quest)

---

## 1. Game Overview

- **Title**: Super Mario Bros.
- **Developer**: Nintendo R&D4
- **Designer**: Shigeru Miyamoto, Takashi Tezuka
- **Composer**: Koji Kondo
- **Platform**: Nintendo Entertainment System (NES) / Famicom
- **Release**: September 13, 1985 (Japan); October 18, 1985 (North America)
- **Genre**: Side-scrolling platformer
- **Players**: 1-2 (alternating turns — Player 1 as Mario, Player 2 as Luigi)
- **Cartridge Size**: 40 KB (32 KB PRG ROM + 8 KB CHR ROM)
- **Objective**: Traverse 32 levels across 8 worlds to rescue Princess Toadstool from the Koopa King, Bowser.
- **Win Condition**: Defeat or bypass Bowser in World 8-4 and reach the Princess.
- **Lose Condition**: Run out of lives. Mario starts with 3 lives.
- **Continue**: After Game Over, hold A and press Start on the title screen to restart from the beginning of the world where the player died.

### Story

Bowser, King of the Koopa, has invaded the Mushroom Kingdom, turning its inhabitants into blocks, bricks, and plants using dark magic. He has kidnapped Princess Toadstool, the only one who can break the spell. Mario (and his brother Luigi) must journey through 8 worlds to defeat Bowser and rescue the Princess.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 256 x 240 pixels (NTSC cuts to 256 x 224 visible) |
| Tile size | 16 x 16 pixels (metatiles composed of 4 x 8x8 CHR tiles) |
| Frame rate | 60 FPS (NTSC) / 50 FPS (PAL) |
| Color palette | NES system palette (54 usable colors + black) |
| Sprites on screen | Max 64 sprites total; max 8 per scanline |
| Sprite size | 8 x 8 or 8 x 16 pixel mode (SMB uses 8x16 mode) |
| Background layers | 1 scrollable background + fixed status bar |
| Scrolling | Horizontal only; left-to-right ratchet scrolling (cannot scroll backward) |

### Coordinate System

- Origin (0, 0) at top-left of screen.
- The status bar (HUD) occupies the top ~32 pixels, rendered using the NES "Sprite 0 Hit" split-screen technique to keep it fixed while the gameplay area scrolls.
- Mario's position and speed are tracked with 8.8 fixed-point precision (8 bits integer, 8 bits fractional = 1/256 pixel subpixel resolution).
- Each level is composed of horizontal screens; typical overworld levels span 10-14 screens (approximately 3,200 to 4,480 pixels wide).

### Frame Rule

| Property | Value |
|----------|-------|
| Frame rule interval | 21 frames (~0.35 seconds at 60 FPS) |
| Function | Global interval timer ticks down every 21 frames |
| Level transition | When a level ends, the game waits until the next frame-rule boundary to begin loading |
| Pipe/area transitions | Black-screen delay rounds up to the next 21-frame boundary |
| Exceptions | Timer pauses during: pauses, lag frames, power-up transformations, pipe entry animations |

### Game Loop

```
1. Read controller input (D-pad, A, B, Start, Select)
2. Process game timer (decrement every 24 frames)
3. Update player physics (acceleration, velocity, position)
4. Update player state (power-up, invincibility, animation)
5. Update enemy AI and movement
6. Update projectiles (fireballs, hammers, Bowser fire)
7. Process block interactions (bump, break, spawn items)
8. Process item movement (mushrooms, stars, coins)
9. Check collision detection (player-enemy, player-item, player-block)
10. Check pit/lava death
11. Check flagpole/axe/pipe triggers
12. Render background tiles
13. Render sprites (player, enemies, items, effects)
14. Render HUD (fixed via sprite-0 split)
```

---

## 3. Physics System

All values below are in NES native units: **pixels** (px) for position, **pixels per frame** (px/f) for speed, and **pixels per frame per frame** (px/f^2) for acceleration. Subpixel values are expressed as fractions of 1/256 pixel.

### 3.1 Horizontal Movement

#### Walking (B not held)

| Property | Value (hex) | Value (decimal) |
|----------|------------|-----------------|
| Max walking speed (right) | $01.1C | 1.109 px/f |
| Max walking speed (left) | $FE.E4 | -1.109 px/f |
| Acceleration (facing same direction) | Varies by current speed | ~0.0625 px/f^2 |
| Acceleration (facing opposite direction / turnaround) | Double the normal rate | ~0.125 px/f^2 |
| Friction / deceleration (no input) | Slightly faster than acceleration | ~0.078 px/f^2 |

#### Running (B held)

| Property | Value (hex) | Value (decimal) |
|----------|------------|-----------------|
| Max running speed (right) | $02.90 | 2.5625 px/f |
| Max running speed (left) | $FD.70 | -2.5625 px/f |
| Acceleration (same direction) | Varies by current speed | ~0.0625-0.098 px/f^2 |
| Skid deceleration (opposite direction while moving) | Higher than walk decel | ~0.15 px/f^2 |

**Note**: Maximum walking speed is approximately 3/5 of maximum running speed.

#### Acceleration Detail

The acceleration magnitude has three tiers, mostly depending on how fast Mario is already moving:
1. **Low speed** (below walk threshold): Higher acceleration to get moving
2. **Mid speed** (walk-to-run transition): Moderate acceleration
3. **High speed** (approaching max run): Lower acceleration (asymptotic approach)

Acceleration is **doubled** when Mario is not facing the direction he is moving (turnaround/skid).

#### Air Control

- Mario retains full horizontal acceleration control while airborne.
- Air friction is slightly lower than ground friction.
- Horizontal speed is preserved when jumping; no artificial air drag.

### 3.2 Vertical Movement — Jumping

Jump physics use a variable-height system controlled by holding the A button.

#### Initial Jump Velocity

| Horizontal Speed State | Initial Y Velocity (upward) | Gravity (A held) | Gravity (A released) |
|------------------------|---------------------------|-------------------|---------------------|
| Standing / slow walk | $FB (-5 px/f) | $0.30 (0.1875 px/f^2) | $0.A8 (0.656 px/f^2) |
| Full walking speed | $FB (-5 px/f) | $0.2D (0.176 px/f^2) | $0.90 (0.5625 px/f^2) |
| Full running speed | $FB (-5 px/f) | $0.38 (0.219 px/f^2) | $0.D0 (0.8125 px/f^2) |

#### Jump Mechanics

- **A button press**: Applies initial upward velocity of approximately -5 px/f (negative = upward).
- **A button held**: Reduced gravity while Mario is ascending (allows higher jumps).
- **A button released**: Gravity approximately **doubles** for the remainder of the ascent, creating the signature "short hop" mechanic.
- **Falling**: Same higher gravity applies once Mario reaches the apex and begins descending.
- **Terminal velocity**: ~4 px/f downward (capped to prevent Mario from falling through platforms).

#### Jump Heights (approximate)

| Jump Type | Approximate Height |
|-----------|-------------------|
| Minimum jump (tap A) | ~1 tile (16 px) |
| Short jump (brief A hold, standing) | ~2 tiles (32 px) |
| Full jump (hold A, standing) | ~4 tiles (64 px) |
| Full jump (hold A, walking) | ~4.5 tiles (72 px) |
| Full running jump (hold A, running) | ~5 tiles (80 px) |

#### Stomp Bounce

- When Mario lands on an enemy, he receives a small upward bounce of approximately -4 px/f.
- If A is held during the stomp, the bounce is amplified to a full jump (~-5 px/f initial velocity).

### 3.3 Swimming (Underwater Levels)

| Property | Value |
|----------|-------|
| Swimming flag | RAM $0704 = 1 |
| A button press | Small upward impulse (~-2 px/f) |
| Sink rate (no input) | Gentle constant downward acceleration (~0.1 px/f^2) |
| Max sink speed | ~2 px/f downward |
| Horizontal movement | Same as ground walking (B has no running effect underwater) |
| Horizontal max speed | Walking speed only (~1.1 px/f) |

- Pressing A repeatedly causes Mario to "flutter" upward in small bursts.
- Mario can walk along the bottom of the water area.
- There is no jump-out-of-water mechanic; the level ends with a pipe exit.

### 3.4 Springboard

| Property | Value |
|----------|-------|
| Small bounce (A not held) | ~-8 px/f initial velocity (very high) |
| Large bounce (A held on contact) | ~-10 px/f initial velocity (extreme height) |
| Mario must land on the springboard | Landing beside it has no effect |

### 3.5 Collision Detection

- Collision is checked **every other frame** for performance.
- Mario's collision box is smaller than his visual sprite:
  - Small Mario: approximately 12 x 15 pixels
  - Super/Fire Mario: approximately 12 x 28 pixels (crouching: 12 x 15)
- Enemy collision boxes are typically 12-16 pixels wide, 16 pixels tall.
- Block collision is metatile-based (16 x 16 grid-aligned).
- Stomping: Vertical overlap + Mario descending + Mario's feet above enemy's midpoint.

---

## 4. Player States & Power-ups

### 4.1 State Variables

The game tracks Mario's power-up in two independent variables:

| Variable | Values | Purpose |
|----------|--------|---------|
| Player Size | 0 = Small, 1 = Super (big) | Determines sprite set and brick-breaking ability |
| Upgrade State | 0 = Needs Mushroom, 1 = Needs Fire Flower, 2 = Has Fire Flower | Determines what spawns from blocks and damage behavior |

### 4.2 Small Mario

| Property | Value |
|----------|-------|
| Height | 1 tile (16 px) — single 8x16 sprite |
| Width | ~12 px (hitbox) |
| Can break bricks | No |
| Damage result | Death (lose 1 life) |
| Block spawns | Super Mushroom from ? Blocks |

### 4.3 Super Mario

| Property | Value |
|----------|-------|
| Height | 2 tiles (32 px) — two 8x16 sprites stacked |
| Width | ~12 px (hitbox) |
| Can break bricks | Yes (headbutt from below destroys standard bricks) |
| Crouching | Hold Down — hitbox shrinks to ~16 px height; can slide under low passages |
| Damage result | Revert to Small Mario (not death); ~2 seconds of invincibility flashing |
| Block spawns | Fire Flower from ? Blocks |
| Transformation animation | ~1 second of flickering between Small and Super sprites |

### 4.4 Fire Mario

| Property | Value |
|----------|-------|
| Height | 2 tiles (32 px, same as Super) |
| Visual | White hat and shirt with red/orange overalls (swapped palette) |
| Can break bricks | Yes |
| Fireball | Press B to throw; max 2 fireballs on screen at once |
| Damage result | Revert to Small Mario (skips Super state) |
| Block spawns | Fire Flower from ? Blocks (gives 1,000 points but no state change) |

#### Fireball Mechanics

| Property | Value |
|----------|-------|
| Speed | ~4 px/f horizontal (same direction Mario faces) |
| Gravity | Affected by gravity; bounces off ground surfaces |
| Bounce height | ~2 tiles per bounce |
| Lifetime | Until it leaves the screen or hits an enemy/wall |
| Max on screen | 2 fireballs simultaneously |
| Kills Bowser | 5 fireballs (awards 5,000 points) |
| Immune enemies | Buzzy Beetle, Podoboo (lava ball) |

### 4.5 Star Power (Invincibility)

| Property | Value |
|----------|-------|
| Source | Super Star item (from certain Brick Blocks) |
| Duration | ~10-12 seconds (varies by frame rule; approximately 15 timer intervals x 21 frames) |
| Effect | Mario is invulnerable to all enemies and hazards (except pits and time-out) |
| Enemy contact | Kills enemies on touch (uses shell-kick point sequence) |
| Visual | Mario's sprite rapidly cycles through color palettes (flashing) |
| Music | Overrides current BGM with Starman theme |
| Movement | No change to physics; Mario retains normal movement |
| End warning | Sprite flashing slows down during final ~2 seconds |

### 4.6 Damage & Invincibility Frames

| Property | Value |
|----------|-------|
| Post-hit invincibility | ~2 seconds of sprite flashing |
| During invincibility | Mario can pass through enemies without harm |
| Visual | Sprite flickers (alternates visible/invisible every few frames) |
| Pit death | Instant; no invincibility frames can save Mario |
| Crush death | If trapped between a moving block and a wall, instant death regardless of state |

### 4.7 Item Behavior When Spawned

| Item | Movement Behavior | Source |
|------|-------------------|--------|
| Super Mushroom | Emerges from block, slides right at ~1.1 px/f, reverses on wall contact, falls off ledges, affected by gravity | ? Blocks (when Small Mario) |
| Fire Flower | Emerges from block, **stationary** — does not move | ? Blocks (when Super/Fire Mario) |
| Super Star | Emerges from block, bounces forward at ~1.5 px/f with high bounces, reverses on wall contact | Certain Brick Blocks |
| 1-Up Mushroom | Same behavior as Super Mushroom (slides right, bounces off walls, falls off ledges) | Hidden Blocks, certain ? Blocks |
| Coin (from block) | Pops up from block with brief animation, collected automatically | ? Blocks, Brick Blocks, Hidden Blocks |
| Vine/Beanstalk | Grows upward from block to top of screen; Mario can climb it to reach cloud bonus areas | Certain Brick Blocks and ? Blocks |

---

## 5. All Enemy Types — Complete Stats

### 5.1 Enemy Reference Table

| Enemy | Points (Stomp) | Points (Fireball) | Points (Shell/Star) | Speed | Behavior |
|-------|---------------|--------------------|---------------------|-------|----------|
| Little Goomba | 100 | 100 | 100+ (chain) | ~0.75 px/f | Walks forward; reverses at walls; falls off ledges |
| Green Koopa Troopa | 100 | 100 | 400 (kick) | ~0.75 px/f | Walks forward; **falls off ledges** |
| Red Koopa Troopa | 100 | 100 | 400 (kick) | ~0.75 px/f | Walks forward; **turns at ledges** (never falls) |
| Green Koopa Paratroopa | 400 | 100 | 400 (kick) | ~0.75 px/f | Bounces along ground; stomp removes wings (becomes Green Koopa Troopa) |
| Red Koopa Paratroopa | 400 | 100 | 400 (kick) | ~0.75 px/f | Flies up and down in fixed vertical path; stomp removes wings |
| Buzzy Beetle | 100 | Immune | 400 (kick) | ~0.75 px/f | Walks like Goomba; immune to fireballs; shell behaves like Koopa shell |
| Spiny | 200 | 200 | N/A | ~0.75 px/f | Stomping damages Mario; can only kill with fireball, star, or shell |
| Spiny Egg | N/A | N/A | N/A | Falls from Lakitu | Hatches into Spiny on ground contact |
| Lakitu | 200 (stomp) | 200 | 200+ (chain) | Follows Mario | Rides cloud at top of screen; throws Spiny Eggs; respawns after defeat |
| Piranha Plant | N/A (no stomp) | 200 | N/A | Stationary | Emerges from pipes periodically; will not emerge if Mario is adjacent to or on the pipe |
| Hammer Brother | 1,000 | 1,000 | 1,000 | Hops in place | Throws hammers in arcs; jumps between platform rows; appears in pairs |
| Bullet Bill | 200 | Immune | 200 | ~1.5 px/f | Flies horizontally from off-screen cannons; unaffected by fireballs |
| Cheep-Cheep (Red, surface) | 200 | 200 | N/A | Arcing leap | Leaps from below bridge levels in arcs |
| Cheep-Cheep (Red, underwater) | 200 | 200 | N/A | ~0.5 px/f | Swims slowly in horizontal paths |
| Cheep-Cheep (Grey/Green, underwater) | 200 | 200 | N/A | ~1.0 px/f | Swims faster; more aggressive tracking |
| Blooper (Bloober) | 200 | 200 | N/A | Erratic | Underwater squid; sinks slowly, lunges diagonally upward toward Mario |
| Podoboo (Lava Bubble) | N/A | Immune | N/A | Vertical leap | Jumps out of lava pools in castles; completely invincible |
| Fire Bar | N/A | N/A | N/A | Rotational | Chain of fireballs rotating clockwise or counterclockwise around a pivot |
| Bowser | 5,000 (fireball x5) | 5,000 | N/A | Slow pace | Breathes fire, jumps; later worlds add hammer throwing |

### 5.2 Detailed Enemy Behaviors

#### Goomba

- Walks in a straight line at constant speed (~0.75 px/f).
- Reverses direction upon hitting a wall or another enemy.
- Falls off ledge edges (does not turn at edges).
- Defeated by: stomp (flattens, disappears after ~0.5s), fireball, kicked shell, star, block bump from below.
- When bumped from below (block hit), flips upside-down and falls off screen.

#### Koopa Troopa (Green)

- Walks forward at constant speed.
- **Falls off ledges** (does not patrol).
- When stomped: retracts into shell (stopped).
- Shell behavior: remains still until kicked; kicked shell slides at ~3-4 px/f, killing all enemies in its path.
- Shell can be kicked again after stopping, or picked up (not in SMB1 — that mechanic is SMB3).
- Shell rebounds off walls; can kill Mario if it bounces back.
- If left in shell too long (~8-10 seconds), Koopa re-emerges and resumes walking.

#### Koopa Troopa (Red)

- Identical to Green except: **turns around at ledge edges** (patrols a platform).
- Shell behavior identical to Green shell when stomped.

#### Koopa Paratroopa (Green)

- Bounces along the ground in small hops.
- First stomp: loses wings, becomes Green Koopa Troopa (walking, falls off edges).
- Second stomp: retracts into shell.

#### Koopa Paratroopa (Red)

- Flies up and down in a fixed vertical range (~3-4 tiles).
- Does not move horizontally (patrols vertically in place).
- First stomp: loses wings, becomes Red Koopa Troopa (walking, patrols edges).
- Second stomp: retracts into shell.

#### Buzzy Beetle

- Walks and behaves identically to Goomba.
- **Immune to fireballs** — fireballs bounce off harmlessly.
- When stomped: retracts into shell (same behavior as Koopa shell).
- Shell can be kicked and kills enemies in its path.
- Replaces all Goombas in Hard Mode (second quest).

#### Hammer Brother

- Always appears in pairs (two Hammer Bros on adjacent platforms).
- Each one hops back and forth on a short section of blocks.
- Periodically jumps up or down between platform rows.
- Throws hammers in parabolic arcs at regular intervals (~1-2 seconds).
- Hammers travel in an arc and cannot be destroyed.
- Mario can pass safely between hammers or underneath the Hammer Bros.
- If Mario stays too long on one side, Hammer Bros slowly advance toward him.
- Defeated by: stomp (1,000 pts), fireball (1,000 pts), shell, star, or block bump from below.

#### Lakitu

- Rides a cloud near the top of the screen.
- Tracks Mario's horizontal position (hovers above or slightly ahead).
- Periodically tosses Spiny Eggs downward.
- **Bug/feature**: Spiny Eggs drop straight down with no horizontal momentum (originally intended to have complex trajectory physics, but a bug removed horizontal component).
- Only one Lakitu exists at a time per level section.
- Defeated by stomp (200 pts) or fireball (200 pts).
- Respawns after a short period if Mario remains in Lakitu's designated zone.
- Stops pursuing and disappears near the flagpole.

#### Spiny

- Hatches from Spiny Egg upon ground contact.
- Walks forward like a Goomba (reverses at walls, falls off ledges).
- **Cannot be stomped** — contact from above damages Mario.
- Defeated by: fireball (200 pts), kicked shell, star, or block bump from below.

#### Piranha Plant

- Lives inside pipes; periodically emerges (rises ~2 tiles above pipe) then retracts.
- Cycle: ~2 seconds up, ~2 seconds down, ~1 second pause.
- **Will not emerge** if Mario is standing directly adjacent to or on top of the pipe.
- Cannot be stomped (no hit detection from above while in pipe).
- Defeated only by fireball (200 pts) or star power.
- Green Piranha Plants appear in the standard game.

#### Bullet Bill

- Fired from cannon blocks (Bill Blasters) positioned in the level.
- Flies in a straight horizontal line at ~1.5 px/f.
- **Immune to fireballs**.
- Defeated by: stomp (200 pts) or star power.
- The cannon will not fire if Mario is standing directly adjacent to it.
- Multiple Bullet Bills can be on screen simultaneously.

#### Cheep-Cheep (Bridge Levels)

- Red Cheep-Cheeps leap from below the screen in parabolic arcs on bridge/overwater levels (e.g., World 2-3, 7-3).
- Spawn continuously from random horizontal positions below the screen.
- Can be stomped (200 pts) or hit with fireball (200 pts).

#### Cheep-Cheep (Underwater)

- Red: swims slowly in horizontal lines.
- Grey/Green: swims faster and can change vertical direction to track Mario somewhat.
- Can only be killed by fireballs underwater (no stomping mechanic underwater).

#### Blooper (Bloober)

- Underwater squid enemy.
- Movement: sinks slowly, then lunges diagonally upward toward Mario's position.
- Pauses briefly at peak of lunge before sinking again.
- Can only be killed by fireballs (200 pts) or star power.

#### Podoboo (Lava Bubble)

- Found only in castle levels.
- Jumps vertically out of lava at fixed intervals.
- Jump height: approximately 4-6 tiles above the lava surface.
- **Completely invincible** — cannot be killed by any means.
- Mario must time movement to pass when Podoboo is submerged.
- First appearance: World 2-4.

#### Fire Bar (Fire Rod)

- Chain of fireballs rotating around a central pivot point.
- Standard length: 6 fireballs.
- Long variant: 10-12 fireballs (first appears in World 5-4).
- Rotation types (stored as object IDs):
  - $1B: Clockwise (standard)
  - $1C: Fast clockwise (used only in World 5-4)
  - $1D: Counterclockwise (standard)
  - $1E: Fast counterclockwise (unused in original game)
  - $1F: Long fire bar
- Found only in castle levels.
- **Completely invincible** — cannot be destroyed.

#### Bowser

| Property | Worlds 1-5 | Worlds 6-7 | World 8 |
|----------|-----------|-----------|---------|
| Attack 1 | Fire breath (periodic fireballs) | Hammer throwing | Fire breath + Hammer throwing |
| Attack 2 | Jumping | Jumping + Hammers | Jumping + Fire + Hammers |
| Movement | Paces back and forth on bridge | Same | Same |
| HP (fireballs) | 5 hits | 5 hits | 5 hits |
| Defeat method 1 | Touch the Axe behind Bowser | Same | Same |
| Defeat method 2 | 5 fireballs as Fire Mario | Same | Same |
| Bridge collapse | Axe destroys bridge; Bowser falls into lava | Same | Same |
| True identity | Impostor (common enemy) | Impostor | Real Bowser |

**Bowser Fire Breath**: Bowser periodically shoots a fireball that travels horizontally at ~2 px/f. Cannot be blocked or destroyed.

**Bowser Hammers** (Worlds 6+): Throws multiple hammers in arcing trajectories, similar to Hammer Brothers but more rapid.

### 5.3 Fake Bowser Identities

When defeated by fireballs, the impostor Bowsers in Worlds 1-7 revert to their true forms:

| World | True Identity |
|-------|--------------|
| 1-4 | Goomba |
| 2-4 | Green Koopa Troopa |
| 3-4 | Buzzy Beetle |
| 4-4 | Spiny |
| 5-4 | Lakitu |
| 6-4 | Blooper |
| 7-4 | Hammer Brother |
| 8-4 | Real Bowser (no transformation) |

---

## 6. Block & Item System

### 6.1 Block Types

| Block Type | Visual | Behavior | Breakable by Super Mario |
|------------|--------|----------|--------------------------|
| ? Block (Question Block) | Flashing "?" pattern | Hit from below to release contents; becomes empty (used) block | No (becomes inert) |
| Brick Block | Brown brick pattern | Small Mario bumps it; Super Mario breaks it (unless it contains item) | Yes (empty bricks) |
| Multi-Coin Brick | Identical to Brick Block | Rapidly hitting releases up to 16 coins; becomes empty block when timer expires | No (becomes inert) |
| Hidden Block (Invisible) | Invisible until struck | Appears only when Mario headbutts from below; contains 1-Up Mushroom or coin | No (becomes inert) |
| Used Block (Empty) | Dark/metallic appearance | No interaction; acts as solid platform | No |
| Hard Block (Stone) | Gray stone appearance | Completely indestructible; forms staircases and terrain | No |
| Ground Block | Brown terrain | Forms the ground; indestructible | No |
| Pipe (Green) | Vertical green cylinders | Some are enterable (press Down); some contain Piranha Plants | No |
| Coin Block (? or Brick) | Contains coins | Releases 1 coin per hit or multiple coins (multi-coin variant) | N/A |
| Bill Blaster (Cannon) | Dark cylindrical block | Fires Bullet Bills at intervals; acts as solid platform | No |

### 6.2 Block Contents

| Content | Found In | Condition |
|---------|----------|-----------|
| Coin (single) | ? Blocks, Brick Blocks, Hidden Blocks | Default content for many blocks |
| Super Mushroom | ? Blocks | Player is Small Mario |
| Fire Flower | ? Blocks | Player is Super or Fire Mario |
| Super Star | Specific Brick Blocks | Fixed placement per level |
| 1-Up Mushroom | Hidden Blocks (invisible), some visible blocks | See 1-Up rules below |
| Vine (Beanstalk) | Specific Brick Blocks / ? Blocks | Grows upward; leads to cloud bonus areas |
| Multi-Coin | Specific Brick Blocks | Releases coins rapidly when hit repeatedly |

### 6.3 Block Interaction

- **Small Mario hitting Brick Block**: Block bumps up slightly; enemies standing on top are knocked off. Block is NOT broken.
- **Super/Fire Mario hitting Brick Block (empty)**: Block shatters into 4 fragments that fly outward (50 points).
- **Super/Fire Mario hitting Brick Block (contains item)**: Block bumps and releases item. Block is NOT broken (becomes empty block).
- **Any Mario hitting ? Block**: Block bumps, releases contents. Becomes an empty/used block.
- **Block bump killing enemies**: Any enemy standing on top of a bumped block is defeated (flips upside-down and falls off screen).

### 6.4 1-Up Mushroom System

| Property | Value |
|----------|-------|
| Total 1-Up blocks in game | Up to 10 (2 visible, 8 invisible) |
| Visible 1-Up locations | World 1-2, World 8-2 |
| Invisible 1-Up locations | One in the first level of each world (1-1, 2-1, 3-1, 4-1, 5-1, 6-1, 7-1, 8-1) |

**Conditional Appearance Rule**: The invisible 1-Up Mushroom in each world's first level only appears if the player collected **every coin** in the third level of the previous world. Exception: World 1-3 allows missing up to 2 coins and still triggering the 1-Up in World 2-1.

### 6.5 Coin System

| Property | Value |
|----------|-------|
| Points per coin | 200 |
| Coins for 1-Up | 100 coins = 1 extra life |
| Coin counter | Displayed on HUD; resets to 0 after reaching 100 |
| Sources | Floating coins in air, coins from blocks, coins in bonus rooms |

---

## 7. Level Structure — All 8 Worlds

Each world contains 4 levels following a consistent pattern:
- **X-1**: Overworld / themed outdoor level
- **X-2**: Underground or underwater level (some exceptions)
- **X-3**: Athletic / elevated platforming level (treetops, bridges, mushroom platforms)
- **X-4**: Castle level (Bowser encounter at end)

### 7.1 World 1 — Ground / Introduction

**Theme**: Bright daytime overworld with green hills, blue sky, and white clouds.

| Level | Type | Timer | Description |
|-------|------|-------|-------------|
| 1-1 | Overworld | 400 | Tutorial level. Introduces Goombas, ? Blocks, Brick Blocks, coins, Super Mushroom, Fire Flower, pits, pipes (one leads to underground coin room). First hidden 1-Up block is located before the first pit. |
| 1-2 | Underground | 400 | Subterranean level with Goombas and Koopa Troopas. Contains entrance to the Warp Zone (Worlds 2, 3, or 4) accessible by running along the ceiling past the exit pipe. Contains a visible 1-Up mushroom. Ends with pipe to outdoor flagpole. |
| 1-3 | Athletic | 400 | Elevated treetop platforming on mushroom/tree platforms. Red Koopa Troopas patrol platforms. Introduces moving platforms (scale lifts). Floating coins form guide paths. |
| 1-4 | Castle | 400 | First castle. Introduces Fire Bars (rotating chains). Simple bridge with Bowser (Goomba impostor) at end. Axe behind Bowser collapses bridge. Mushroom Retainer says: "Thank you, Mario! But our Princess is in another castle!" |

### 7.2 World 2 — Underground / Water

**Theme**: Mix of underground and aquatic environments.

| Level | Type | Timer | Description |
|-------|------|-------|-------------|
| 2-1 | Overworld | 400 | Overworld with Koopa Troopas and Goombas. Features springboard. First pipe leads to underground coin room. Contains beanstalk to cloud bonus area. |
| 2-2 | Underwater | 400 | First underwater level. Bloopers and Cheep-Cheeps. Coral formations. Mario swims using A button. Ends at pipe exit. No flagpole (exits via pipe to small overworld section with flagpole). |
| 2-3 | Bridge | 400 | Overwater bridge level. Red Cheep-Cheeps leap from below in arcing patterns. Narrow bridge platforms. |
| 2-4 | Castle | 400 | Castle with Fire Bars and Podoboos. Bowser (Green Koopa Troopa impostor) at end. Moving fire bars of varying lengths. |

### 7.3 World 3 — Night / Athletic

**Theme**: Nighttime sky with elevated platforms.

| Level | Type | Timer | Description |
|-------|------|-------|-------------|
| 3-1 | Overworld (Night) | 400 | Night-themed overworld. Introduces Hammer Brothers. Green Koopa Paratroopas bounce along ground. Dense enemy placement. |
| 3-2 | Overworld | 300 | Shorter overworld level. Features Koopa Troopas near staircase sections. |
| 3-3 | Athletic (Night) | 400 | Treetop platforming at night. Scale-lift platforms (connected by pulley — one goes up as the other goes down). Red Koopa Paratroopas fly vertically. |
| 3-4 | Castle | 400 | Castle with more complex Fire Bar arrangements and Podoboos. Bowser (Buzzy Beetle impostor). |

### 7.4 World 4 — Lakitu / Spiny

**Theme**: Introduces Lakitu and his Spiny minions.

| Level | Type | Timer | Description |
|-------|------|-------|-------------|
| 4-1 | Overworld | 400 | First appearance of Lakitu, who rides a cloud and throws Spiny Eggs. Spinies patrol the ground. Defeating Lakitu provides temporary relief but he respawns. |
| 4-2 | Underground | 400 | Underground level with two Warp Zones: one hidden beanstalk leads to Warp Zone (Worlds 6, 7, 8); one pipe at end leads to Warp Zone (World 5 only). Contains Buzzy Beetles. |
| 4-3 | Athletic | 400 | Elevated mushroom-platform level. Red Koopa Troopas and Koopa Paratroopas. Moving platforms. |
| 4-4 | Castle (Maze) | 400 | **First maze castle.** Level loops if incorrect path is taken. Player must take specific pipe/path sequence to advance. Fire Bars on walls and on bridge. Bowser (Spiny impostor). |

### 7.5 World 5 — Mixed Challenges

**Theme**: Higher difficulty remixes of earlier themes.

| Level | Type | Timer | Description |
|-------|------|-------|-------------|
| 5-1 | Overworld | 300 | Bullet Bill cannons introduced. Multiple Bullet Bills fire from Bill Blasters. Dense enemy gauntlet. |
| 5-2 | Overworld | 400 | Overworld with Hammer Brothers, Bullet Bills, and pits. Cloud bonus area accessible via beanstalk. |
| 5-3 | Athletic | 300 | Treetop level with Bullet Bills and Red Koopa Paratroopas. Narrow platforms. |
| 5-4 | Castle | 400 | Castle with **fast-rotating Fire Bars** and long (12-fireball) Fire Bars (unique to this level). Bowser (Lakitu impostor) throws hammers. |

### 7.6 World 6 — Dense Overworld

**Theme**: Challenging overworld variations with heavy enemy density.

| Level | Type | Timer | Description |
|-------|------|-------|-------------|
| 6-1 | Overworld | 400 | Dense enemy layout with Lakitu returning. Multiple Spinies on ground. |
| 6-2 | Overworld | 400 | Overworld with Hammer Brothers, Bullet Bills, and numerous pits. Contains warp pipe to bonus coin area. |
| 6-3 | Athletic | 400 | Elevated platforms with fire-based Cheep-Cheeps leaping from below and Bullet Bills. |
| 6-4 | Castle (Maze) | 400 | **Second maze castle.** Looping path requires correct sequence. Bowser (Blooper impostor) throws hammers. |

### 7.7 World 7 — Advanced

**Theme**: High-difficulty remixes; second underwater level.

| Level | Type | Timer | Description |
|-------|------|-------|-------------|
| 7-1 | Overworld | 400 | Hammer Brothers and Bullet Bills. Dense combat encounters. |
| 7-2 | Underwater | 400 | Second underwater level. More Bloopers and faster Cheep-Cheeps than 2-2. More complex coral maze. Exits via pipe. |
| 7-3 | Bridge | 400 | Bridge level over water. Red Cheep-Cheeps leap rapidly. Koopa Troopas on narrow platforms. Very aggressive enemy spawning. |
| 7-4 | Castle (Maze) | 400 | **Third maze castle.** Most complex looping path in the game. Bowser (Hammer Brother impostor) throws hammers and breathes fire. |

### 7.8 World 8 — Final World

**Theme**: Bowser's domain. Maximum difficulty. Dark/ominous overworld.

| Level | Type | Timer | Description |
|-------|------|-------|-------------|
| 8-1 | Overworld | 300 | **Longest overworld level.** Gauntlet of Goombas, Koopa Troopas, Koopa Paratroopas, Buzzy Beetles, and Hammer Brothers. Extended run with very few power-ups. |
| 8-2 | Overworld | 400 | Continues the gauntlet. Bullet Bills, Lakitu, Spinies, and treacherous platforming. Contains a visible 1-Up Mushroom. Wide pits. |
| 8-3 | Overworld | 300 | Hammer Brothers gauntlet — multiple pairs of Hammer Bros on elevated platforms. Bullet Bills between encounters. |
| 8-4 | Castle (Maze) | 400 | **Final level.** Multi-room maze castle navigated via pipes. Four distinct sections connected by correct pipe choices (always the first pipe after a lava gap). Contains an underwater section with Fire Bars and Bloopers. Final section features Fire Bars, a Podoboo, and the real Bowser who throws hammers AND breathes fire simultaneously. Defeating Bowser or reaching the Axe rescues Princess Toadstool. |

### 7.9 Warp Zones

| Location | Accessible Destinations | How to Reach |
|----------|------------------------|--------------|
| World 1-2 (end) | Worlds 2, 3, or 4 (three pipes) | Run along the ceiling past the exit pipe; reach the area above the normal exit |
| World 4-2 (beanstalk) | Worlds 6, 7, or 8 (three pipes) | Find hidden beanstalk block; climb to cloud area; walk right to Warp Zone |
| World 4-2 (end) | World 5 only (one pipe) | Run along the ceiling past the normal exit pipe (similar to 1-2 trick) |

### 7.10 Level Length Reference

| Timer Value | Real-Time Duration | Levels Using This Timer |
|-------------|-------------------|------------------------|
| 400 | ~160 seconds (2 min 40 sec) | Most levels; all castle/maze levels |
| 300 | ~120 seconds (2 min) | 3-2, 5-1, 5-3, 8-1, 8-3 |

**Timer speed**: 1 game-time unit = 24 frames (NTSC) = 0.4 real seconds.

---

## 8. World-Specific Mechanics

### 8.1 Overworld Levels

- Standard platforming with bottomless pits.
- Scrolling is strictly left-to-right (ratchet scrolling — screen never scrolls back).
- Power-up blocks placed strategically before difficult sections.
- Pipe entrances (press Down while standing on certain pipes) lead to underground coin rooms.
- Levels end at a flagpole (see Scoring section).

### 8.2 Underground Levels

- Darker color palette (blue/black background).
- Different background music (Underground Theme).
- Brick Block ceilings; Mario can run along the top of the ceiling in some sections.
- Typically feature Buzzy Beetles, Goombas, and Piranha Plants in pipes.
- May contain Warp Zone access (Worlds 1-2, 4-2).

### 8.3 Athletic / Treetop Levels

- Elevated mushroom platforms and trees against sky backdrop.
- Heavy emphasis on precision platforming.
- Scale lifts (pulley-connected platforms — stepping on one side lowers it while the other rises).
- Moving platforms (horizontal or vertical) that travel on fixed paths.
- Red Koopa Paratroopas as primary threats.
- No flagpole at the end — these levels end at a flagpole in outdoor setting.

### 8.4 Underwater Levels (2-2, 7-2)

- Swimming physics replace jumping (see Section 3.3).
- A button provides upward thrust; Mario sinks without input.
- Enemies: Bloopers and Cheep-Cheeps only.
- Only fireballs can kill enemies (no stomping underwater).
- Coral formations serve as terrain obstacles.
- No pits (floor is continuous).
- Levels exit via pipe to a small overworld section with a flagpole.

### 8.5 Bridge / Over-Water Levels (2-3, 7-3)

- Series of narrow bridge platforms over water.
- Red Cheep-Cheeps constantly leap from below in parabolic arcs.
- Falling into the water = death (treated as a pit).
- Standard ground physics (not swimming).

### 8.6 Castle Levels (X-4)

- Stone/dungeon aesthetic with dark background.
- Castle-specific BGM (Castle Theme).
- No standard enemies from overworld; instead: Fire Bars, Podoboos, and Bowser.
- Bowser encounter at the end on a bridge over lava.
- **Axe**: Located at the far end of the bridge behind Bowser. Touching it destroys the bridge, and Bowser falls into the lava.
- **Fireball defeat**: 5 fireballs kill Bowser/Impostor (5,000 pts; reveals true form for impostors).
- **No timer bonus**: Castle levels do not award timer bonus points at completion.
- **Toad rescue**: After each castle in Worlds 1-7, a Mushroom Retainer (Toad) appears and says: "Thank you, Mario! But our Princess is in another castle!"
- **World 8-4 ending**: Princess Toadstool is rescued; game displays ending message and offers to replay in Hard Mode.

#### Maze Castle Mechanics (4-4, 6-4, 7-4, 8-4)

- If the player takes the wrong path or pipe, the level section loops back to the beginning of that section.
- The correct path typically involves taking the first pipe encountered after a lava pool/gap.
- In 8-4, the maze consists of 4 distinct rooms connected by correct pipe choices, including one underwater section.
- No visual hint distinguishes correct pipes from incorrect ones (knowledge or trial-and-error required).

### 8.7 Bonus Areas

| Type | Access Method | Contents |
|------|---------------|----------|
| Underground Coin Room | Enter specific pipes (press Down) | Rows of coins; 10-coin blocks; exits via pipe further into level |
| Cloud Bonus (Coin Heaven) | Climb beanstalk from hidden/specific block | Ride a moving cloud platform; collect floating coins in the sky; fall back to level |
| Warp Zone | Special access (ceiling run in 1-2, 4-2; beanstalk in 4-2) | Pipes labeled with destination world numbers |

---

## 9. Scoring System

### 9.1 Enemy Points

#### Single Enemy Defeat

| Enemy | Stomp | Fireball | Star/Contact |
|-------|-------|----------|--------------|
| Goomba | 100 | 100 | Chain sequence |
| Koopa Troopa | 100 | 100 | Chain sequence |
| Koopa Paratroopa | 400 | 100 | Chain sequence |
| Buzzy Beetle | 100 | Immune | Chain sequence |
| Spiny | Cannot stomp | 200 | Chain sequence |
| Lakitu | 200 | 200 | Chain sequence |
| Hammer Brother | 1,000 | 1,000 | Chain sequence |
| Bullet Bill | 200 | Immune | Chain sequence |
| Cheep-Cheep | 200 | 200 | Chain sequence |
| Blooper | 200 | 200 | Chain sequence |
| Piranha Plant | Cannot stomp | 200 | Chain sequence |
| Bowser | Cannot stomp | 5,000 (5 hits) | N/A |

#### Consecutive Stomp Chain (Without Touching Ground)

When Mario stomps multiple enemies in a single jump (or via a kicked shell hitting sequential enemies):

| Hit # | Points |
|--------|--------|
| 1st | 100 |
| 2nd | 200 |
| 3rd | 400 |
| 4th | 500 |
| 5th | 800 |
| 6th | 1,000 |
| 7th | 2,000 |
| 8th | 4,000 |
| 9th | 5,000 |
| 10th | 8,000 |
| 11th+ | 1-Up (extra life) |

#### Kicked Shell Chain

When a kicked Koopa/Buzzy Beetle shell hits sequential enemies:

| Hit # | Points |
|--------|--------|
| 1st | 500 |
| 2nd | 800 |
| 3rd | 1,000 |
| 4th | 2,000 |
| 5th | 4,000 |
| 6th | 5,000 |
| 7th | 8,000 |
| 8th+ | 1-Up (extra life) |

### 9.2 Item & Block Points

| Action | Points |
|--------|--------|
| Collect coin (floating or from block) | 200 |
| Collect Super Mushroom | 1,000 |
| Collect Fire Flower | 1,000 |
| Collect Super Star | 1,000 |
| Collect 1-Up Mushroom | 0 points (awards extra life) |
| Break brick block | 50 |
| Block bump killing enemy above | Same as stomp points |

### 9.3 Flagpole Points

At the end of each non-castle level, Mario grabs the flagpole. Points are awarded based on the height at which Mario contacts the pole:

| Position on Pole | Points |
|-----------------|--------|
| Bottom section | 100 |
| Lower-middle section | 400 |
| Middle section | 800 |
| Upper-middle section | 2,000 |
| Very top of pole | 5,000 |

Grabbing the very top of the flagpole is difficult due to the small target area at the peak.

### 9.4 Fireworks Bonus

After grabbing the flagpole, if the **last digit of the timer** is 1, 3, or 6:

| Last Timer Digit | Fireworks | Bonus Points |
|------------------|-----------|-------------|
| 1 | 1 firework | 500 |
| 3 | 3 fireworks | 1,500 |
| 6 | 6 fireworks | 3,000 |
| Any other digit | No fireworks | 0 |

Each firework explosion awards 500 points.

### 9.5 Timer Bonus

| Property | Value |
|----------|-------|
| Timer bonus | 50 points per remaining time unit |
| Castle levels | **No timer bonus** |
| Countdown speed | Timer counts down rapidly after flagpole/castle completion |
| Example | 200 remaining time units = 10,000 bonus points |

### 9.6 Lives System

| Property | Value |
|----------|-------|
| Starting lives | 3 |
| Maximum lives display | Lives counter goes up to 99; behavior beyond varies |
| Life sources | 1-Up Mushroom, 100 coins, consecutive stomp/shell chain |
| Life lost by | Enemy damage (Small Mario), falling in pit, falling in lava, time running out, being crushed |

---

## 10. UI Layout & Screen Flow

### 10.1 HUD (In-Game)

The HUD is displayed in the top 32 pixels of the screen, fixed in place using the NES Sprite 0 Hit technique while the game world scrolls below.

```
+-----------------------------------------------------------------------+
| MARIO              WORLD  TIME                                        |
| 000000  x06        1-1    400                                         |
+-----------------------------------------------------------------------+
```

| HUD Element | Position | Format |
|-------------|----------|--------|
| "MARIO" label | Top-left | Static text |
| Score | Below "MARIO" | 6 digits, zero-padded |
| Coin counter | Center-left | Coin icon + "x" + 2-digit count |
| "WORLD" label | Center | Static text |
| World indicator | Below "WORLD" | Format: "X-Y" (e.g., "1-1") |
| "TIME" label | Right | Static text |
| Timer | Below "TIME" | 3 digits (counts down) |

### 10.2 Screen Flow

```
Power On
  |
  v
Title Screen
  |-- Press Start (1 Player) --> World Start Screen --> Gameplay
  |-- Press Select (toggle 1P/2P)
  |-- Press Start (2 Players) --> World Start Screen (alternating Mario/Luigi)
  |
Gameplay
  |-- Complete level (flagpole) --> Score tally (timer countdown) --> Next level
  |-- Complete castle (axe/Bowser defeat) --> Toad message / Princess rescue --> Next world
  |-- Die --> Death animation --> Lives remaining?
  |     |-- Yes --> Respawn at level start (or checkpoint if applicable)
  |     |-- No --> Game Over screen
  |
Game Over Screen
  |-- Hold A + Press Start --> Continue from current world (start of world)
  |-- No input --> Return to Title Screen
  |
Game Complete (8-4 cleared)
  |-- Princess rescued message
  |-- "Your quest is over" message for 1-player; offers second quest (Hard Mode)
  |-- Press B on title screen to start from World 1 in Hard Mode
```

### 10.3 Title Screen

- Black background with game logo "SUPER MARIO BROS." at top.
- Animated demo plays if no input for several seconds (attract mode).
- "1 PLAYER GAME" and "2 PLAYER GAME" options.
- Select button toggles between options; Start begins game.
- "TOP - " followed by high score (resets on power-off; no save).
- Copyright notice: "(C)1985 NINTENDO" at bottom.

### 10.4 World Start Screen

- Black screen displayed for ~2 seconds before each world/life.
- Shows:
  - "WORLD X-Y" (centered)
  - Mario sprite icon + "x" + remaining lives count
  - Current score at top

### 10.5 Death Sequence

1. All enemies and objects freeze.
2. Mario's death animation plays (rises slightly, then falls off the bottom of the screen).
3. Death jingle plays (~2 seconds).
4. Brief black screen.
5. If lives remain: World Start Screen for current level.
6. If no lives remain: Game Over screen.

### 10.6 Level Complete Sequence (Flagpole)

1. Mario grabs the flagpole; flag slides down.
2. Mario slides down the pole to the base.
3. Flagpole height points awarded (100-5,000).
4. Mario walks to the right toward the fortress/castle entrance.
5. Timer counts down rapidly; 50 points per remaining unit.
6. If timer's last digit was 1, 3, or 6: fireworks display (500 pts each).
7. Mario enters the fortress; screen transitions to next level.

### 10.7 Castle Complete Sequence

1. Bowser falls (axe) or is defeated (fireballs).
2. Mario walks right past the Bowser arena.
3. Mushroom Retainer (Worlds 1-7) or Princess Toadstool (World 8) appears.
4. Text message displayed.
5. No timer bonus awarded.
6. Screen transitions to next world's start screen.

---

## 11. Audio Design

### 11.1 Music Tracks

All music composed by **Koji Kondo** for the NES/Famicom sound hardware (2 pulse channels, 1 triangle channel, 1 noise channel, 1 DPCM sample channel).

| Track | BPM | Key | Usage |
|-------|-----|-----|-------|
| Overworld Theme | ~200 (swung) | C Major | Overworld levels (1-1, 2-1, 3-1, etc.) |
| Underground Theme | ~160 | C Minor | Underground/subterranean levels (1-2, 4-2) |
| Underwater Theme | ~120 (waltz 3/4 time) | Bb Major | Underwater levels (2-2, 7-2) |
| Castle Theme | ~180 | A Minor | All castle levels (X-4) |
| Starman Theme | ~240 | C Major | During Super Star invincibility |
| Hurry Up! Overworld | ~260 | C Major | Overworld when timer < 100 |
| Hurry Up! Underground | ~200 | C Minor | Underground when timer < 100 |
| Hurry Up! Underwater | ~160 | Bb Major | Underwater when timer < 100 |
| Hurry Up! Castle | ~240 | A Minor | Castle when timer < 100 |

### 11.2 Jingles (Non-Looping)

| Jingle | Duration | Trigger |
|--------|----------|---------|
| Level Complete Fanfare | ~6 seconds | Grabbing the flagpole |
| Castle Complete Fanfare | ~4 seconds | Bowser defeated / bridge collapsed |
| Death Jingle | ~3 seconds | Mario dies |
| Game Over Jingle | ~3 seconds | No lives remaining |
| World Clear (Princess) | ~10 seconds | Rescuing Princess Toadstool (World 8-4) |
| Hurry Up! Warning | ~1 second | Timer reaches 100 (one-shot jingle before sped-up BGM) |
| Power-Up | ~0.5 seconds | Collecting Super Mushroom or Fire Flower |
| 1-Up | ~0.5 seconds | Collecting 1-Up Mushroom or earning extra life |

### 11.3 Sound Effects

| Sound Effect | Trigger |
|-------------|---------|
| Small jump | Mario jumps (Small Mario) |
| Big jump | Mario jumps (Super/Fire Mario) |
| Stomp | Landing on an enemy |
| Kick | Kicking a Koopa/Buzzy Beetle shell |
| Brick break | Breaking a Brick Block |
| Block bump | Hitting a block from below |
| Coin collect | Collecting any coin |
| Fireball throw | Pressing B as Fire Mario |
| Fireball hit | Fireball strikes enemy or wall |
| Power-up appear | Item emerging from block |
| Pipe travel | Entering or exiting a warp pipe |
| Bowser fire | Bowser shooting a fireball |
| Bowser fall | Bowser falling after bridge collapse |
| Vine grow | Beanstalk extending upward from block |
| Flagpole slide | Flag sliding down the pole |
| Timer tick-down | Rapid beeping during end-of-level timer countdown |
| Firework explosion | Each firework at level end |
| Pause | Pressing Start to pause |
| Swimming stroke | Each A press while swimming |

---

## 12. Animation System

### 12.1 Mario Sprite Animations

The NES uses 8x16 pixel sprites. Mario is composed of multiple sprites depending on his current state.

#### Small Mario Sprite States

| State | Sprites Used | Frames | Description |
|-------|-------------|--------|-------------|
| Standing idle | 1 sprite (8x16) | 1 frame | Mario facing right, standing still |
| Walking | 1 sprite (8x16) | 3 frames (ping-pong: 1-2-3-2) | Leg animation; speed of cycle varies with movement speed |
| Running | Same as walking | 3 frames (faster cycle) | Same frames as walking but faster animation rate |
| Jumping / Falling | 1 sprite (8x16) | 1 frame | Arms up, legs apart in mid-air pose |
| Skidding | 1 sprite (8x16) | 1 frame | Turning/braking pose; dust effect |
| Climbing (flagpole/vine) | 1 sprite (8x16) | 2 frames (alternating) | Climbing animation |
| Swimming | 1 sprite (8x16) | 3 frames | Arm stroke animation |
| Death | 1 sprite (8x16) | 1 frame | Arms up, rises then falls |

#### Super/Fire Mario Sprite States

| State | Sprites Used | Frames | Description |
|-------|-------------|--------|-------------|
| Standing idle | 2 sprites (8x16 stacked) | 1 frame | Tall Mario standing |
| Walking | 2 sprites (8x16 stacked) | 3 frames (ping-pong) | Same cycle as Small but with tall sprites |
| Running | 2 sprites (8x16 stacked) | 3 frames (faster) | Faster walk animation |
| Jumping / Falling | 2 sprites (8x16 stacked) | 1 frame | Arms forward, mid-air |
| Crouching | 2 sprites (8x16 stacked) | 1 frame | Ducked-down pose; reduced height |
| Skidding | 2 sprites (8x16 stacked) | 1 frame | Turn/brake pose |
| Throwing fireball | 2 sprites (8x16 stacked) | 1 frame | Arm extended forward (Fire Mario only) |
| Climbing | 2 sprites (8x16 stacked) | 2 frames | Climbing animation |
| Swimming | 2 sprites (8x16 stacked) | 3 frames | Stroke animation |

### 12.2 Walk Animation Timing

| Movement Speed | Frame Duration (per animation frame) |
|---------------|--------------------------------------|
| Slow walk | 5 game frames per animation frame |
| Full walking speed | 3 game frames per animation frame |
| Running speed | 2 game frames per animation frame |

### 12.3 Power-Up Transformation Animation

| Transition | Duration | Visual |
|-----------|----------|--------|
| Small -> Super | ~1 second | Rapid flickering between Small and Super Mario sprites (3 cycles) |
| Super -> Fire | Instant palette swap | No size change; palette swaps from standard to Fire Mario colors |
| Super/Fire -> Small (damage) | ~0.5 seconds | Brief flicker, shrink to Small Mario; invincibility flashing begins |
| Star invincibility | ~10-12 seconds | Mario's sprite palette cycles rapidly through available color palettes |

### 12.4 Enemy Animations

| Enemy | Idle/Walk Frames | Notes |
|-------|-----------------|-------|
| Goomba | 2 frames (alternating feet) | Flattens to 1 frame when stomped |
| Koopa Troopa | 2 frames (walking) | Shell is 1 static frame |
| Koopa Paratroopa | 2 frames (walking + wing flap) | Wings are separate sprite overlay |
| Buzzy Beetle | 2 frames (walking) | Shell identical behavior to Koopa |
| Piranha Plant | 2 frames (mouth open/closed) | Rises/lowers from pipe smoothly |
| Hammer Brother | 2 frames (walking/throwing) | Hammer is separate sprite |
| Lakitu | 2 frames (peeking from cloud) | Cloud is background; Lakitu peeks out |
| Blooper | 2 frames (tentacles spread/together) | Smooth vertical movement |
| Cheep-Cheep | 2 frames (tail fin) | Smooth swimming/arcing |
| Bullet Bill | 1 frame (static) | Rotates (no animation; single sprite) |
| Bowser | 2 frames (walking) | Mouth opens for fire breath; arm moves for hammer throw |

### 12.5 Block Animations

| Block | Animation | Frames |
|-------|-----------|--------|
| ? Block | Shimmering "?" pattern | 3-4 frames cycling |
| Brick break | 4 fragments fly in diagonal arcs | ~30 frames total (fragments use gravity) |
| Block bump | Block rises ~4 px then returns to position | ~8 frames (quick bounce) |
| Coin from block | Coin pops up, spins, then disappears | ~16 frames (pop + sparkle) |
| Coin (floating) | Spinning/flashing animation | 4 frames cycling |

### 12.6 Special Effects

| Effect | Description |
|--------|-------------|
| Score popup | Points value text rises briefly above the defeated enemy/collected item (e.g., "100", "200") |
| Star sparkle | Brief sparkle particles when star is collected |
| Fireball impact | Small burst animation when fireball hits a wall or enemy |
| Firework | Circular expansion animation at level end |
| Flag slide | Flag smoothly descends the pole |
| Bridge collapse | Blocks fall one by one from Bowser's end to the axe end |
| Podoboo trail | Lava bubble leaves brief trail as it rises |

---

## 13. Game Progression & Second Quest

### 13.1 Normal Game Flow

1. Start at World 1-1 as Small Mario with 3 lives and 0 score.
2. Progress through 32 levels (8 worlds x 4 levels).
3. Warp Zones allow skipping worlds:
   - World 1-2 -> Worlds 2, 3, or 4
   - World 4-2 -> Worlds 6, 7, or 8
   - World 4-2 -> World 5
4. Defeat Bowser in World 8-4 to rescue Princess Toadstool.
5. Princess says: "Thank you, Mario! Your quest is over. We present you a new quest." (followed by "Push Button B to select a world.")

### 13.2 Hard Mode (Second Quest)

After completing the game, pressing B on the title screen starts Hard Mode. Changes include:

| Modification | Details |
|-------------|---------|
| Goomba replacement | All Goombas are replaced by Buzzy Beetles (fireproof) |
| Enemy speed increase | Koopa Troopas and Buzzy Beetles move faster |
| Shell recovery | Enemies re-emerge from shells faster (~5s instead of ~8-10s) |
| Platform shrinkage | All moving lifts use the short variant (even where long lifts originally appeared) |
| Hammer Bros aggression | Hammer Brothers advance toward Mario more quickly |
| Level remapping | Some early levels are replaced with later, harder versions: |
| | World 1-3 uses World 5-3 layout |
| | World 1-4 uses World 6-4 layout |
| | World 2-2 uses World 7-2 layout |
| | World 2-3 uses World 7-3 layout |
| | World 2-4 uses World 5-4 layout |

### 13.3 Two-Player Mode

- Players alternate turns: Player 1 controls Mario, Player 2 controls Luigi.
- Luigi is visually identical to Mario (same sprites with a palette swap to green/white).
- Players switch after one player dies.
- Each player has independent: lives, score, power-up state, world progress.
- The game ends when both players have exhausted all lives.

### 13.4 Minus World (Glitch)

An unintended glitch level accessible in World 1-2:

1. Stand at the pipe leading to the Warp Zone at the end of 1-2.
2. Break the second block from the right next to the pipe, but not the first.
3. Face left, perform a precise crouch-jump backward to clip through the first remaining block.
4. Enter the pipe before the Warp Zone text loads.
5. Result: World " -1" (displayed as "World -1" due to a blank tile being read as a space).
6. The level is a glitched underwater stage that loops infinitely (exit pipe returns to the start).
7. The level cannot be completed; the player must lose all lives or reset.

---

*This specification is based on the NTSC NES release of Super Mario Bros. (1985). PAL versions run at 50 FPS with slightly different timing values. The VS. System arcade version has minor differences in level layouts and difficulty.*
