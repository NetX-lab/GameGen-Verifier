# Ghosts 'n Goblins — Complete Game Specification

> A comprehensive specification for faithfully recreating Ghosts 'n Goblins (Capcom, 1985 Arcade / 1986 NES). This document covers every system, mechanic, entity, and interaction required for a full clone of this notoriously difficult action-platformer.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Player Character Mechanics](#3-player-character-mechanics)
4. [Weapon System](#4-weapon-system)
5. [Armor System](#5-armor-system)
6. [Enemy Compendium](#6-enemy-compendium)
7. [Level Design — All 6 Stages](#7-level-design--all-6-stages)
8. [Boss Encounters](#8-boss-encounters)
9. [Item & Pickup System](#9-item--pickup-system)
10. [Scoring System](#10-scoring-system)
11. [UI Layout & HUD](#11-ui-layout--hud)
12. [Audio Design](#12-audio-design)
13. [Animation System](#13-animation-system)
14. [Lives, Timer & Continue System](#14-lives-timer--continue-system)
15. [Second Loop](#15-second-loop)

---

## 1. Game Overview

- **Genre**: Action-platformer
- **Perspective**: 2D side-scrolling
- **Players**: 1-2 players (alternating turns)
- **Input**: 8-way joystick + 2 buttons (Shoot, Jump)
- **Objective**: Control knight Arthur through 6 stages to rescue Princess Prin-Prin from the demon king Astaroth (Satan in some versions).
- **Lose Condition**: Losing all lives.
- **Key feature**: Extreme difficulty. Arthur can only take 2 hits (armor → no armor → death). The game must be completed TWICE to see the true ending.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Arcade resolution | 256 x 224 pixels |
| NES resolution | 256 x 240 pixels |
| Recommended implementation | 512 x 448 |
| Frame rate | 60 FPS |
| Tile size | 16 x 16 pixels |

### Game Loop

```
1. Process input
2. Update Arthur state (walk, jump, throw, crouch)
3. Apply gravity and platform collision
4. Update weapon projectiles
5. Update all enemy AI and projectiles
6. Check Arthur vs enemy/projectile collisions
7. Check weapon vs enemy collisions
8. Check Arthur vs item pickups
9. Update spawn timers (Red Arremer, zombies, etc.)
10. Update timer countdown
11. Render (background → platforms → enemies → Arthur → projectiles → UI)
```

---

## 3. Player Character Mechanics

### Arthur Properties

| Property | Value |
|----------|-------|
| HP | 2 hits (armor → underwear → death) |
| Hitbox | 14 x 28 pixels (standing), 14 x 16 (crouching) |
| Walk speed | 1.2 px/frame (72 px/s) |
| Jump velocity (initial) | -5 px/frame |
| Gravity | 0.3 px/frame^2 |
| Max fall speed | 6 px/frame |
| Jump height | ~42 pixels |
| Jump horizontal distance | ~72 pixels |

### Movement Characteristics

| Action | Description |
|--------|-------------|
| Walk left/right | Constant speed, no acceleration |
| Jump | **Fixed trajectory** — once airborne, cannot change horizontal direction |
| Crouch | D-pad down while on ground; cannot move while crouching |
| Climb ladder | D-pad up/down on ladders; fixed speed 1 px/frame |
| Attack | Throw weapon forward (or upward with up + attack on some versions) |
| No air control | Like Castlevania, jump trajectory is committed at takeoff |
| Double jump | NOT available (single jump only) |

### Shooting While Jumping

- Arthur CAN throw weapons while jumping.
- Throwing briefly pauses the sprite animation but does not alter trajectory.
- Maximum 2 projectiles on screen at a time.

### Ladder Mechanics

| Property | Value |
|----------|-------|
| Climb speed | 1 px/frame |
| Can attack on ladder | Yes (throw weapon horizontally) |
| Can jump off ladder | Yes (jump button dismounts with a small hop) |
| Vulnerability | Fully vulnerable while climbing |

---

## 4. Weapon System

### Default Weapon: Lance (Javelin)

| Property | Value |
|----------|-------|
| Damage | 1 per hit |
| Speed | 4 px/frame |
| Trajectory | Straight horizontal |
| Max on screen | 2 |
| Range | Full screen |

### Special Weapons (Found in Pots/Containers)

#### Dagger

| Property | Value |
|----------|-------|
| Damage | 1 |
| Speed | 6 px/frame (fastest weapon) |
| Trajectory | Straight horizontal |
| Max on screen | 2 |
| Best use | Fast, reliable; good general weapon |

#### Torch

| Property | Value |
|----------|-------|
| Damage | 1 (contact) + ground fire damage |
| Speed | 3 px/frame |
| Trajectory | Parabolic arc (like a grenade) |
| Ground fire | Creates a 16-pixel flame on the ground for ~2 seconds |
| Ground fire damage | 1 per hit (can hit enemies walking over it) |
| Max on screen | 2 |
| Best use | Area denial, hitting enemies below |

#### Axe

| Property | Value |
|----------|-------|
| Damage | 1 |
| Speed | 3 px/frame |
| Trajectory | Large parabolic arc (higher than torch) |
| Max on screen | 1 (NES version) |
| Best use | Hitting enemies at specific heights |
| Note | Generally considered the worst weapon due to slow speed and high arc |

#### Cross/Shield (required for final boss)

| Property | Value |
|----------|-------|
| Damage | 2 |
| Speed | 3 px/frame |
| Trajectory | Straight horizontal |
| Max on screen | 1 |
| Special | **Required** to damage the final boss in the second loop |
| Best use | Essential for game completion |

---

## 5. Armor System

### Armor States

| State | Visual | Damage Threshold | Effect of Getting Hit |
|-------|--------|-----------------|----------------------|
| Full Armor (Steel) | Full knight armor, grey/silver | Can take 1 hit | Loses armor, reduced to underwear |
| No Armor (Underwear) | Arthur in white boxer shorts | Next hit = death | Dies, loses a life |

### Armor Pickup

| Property | Value |
|----------|-------|
| Source | Hidden in certain platforms/pots |
| Effect | Restores armor (underwear → full armor) |
| Rarity | Rare — 2-3 per stage |
| Visual | Flashing suit of armor icon |

### Hit Response

- When hit with armor: Arthur's armor flies off in pieces. Brief invincibility (~1 second). He continues in underwear.
- When hit without armor: Death animation plays (Arthur becomes a skeleton, then a ghost rises).

---

## 6. Enemy Compendium

### 6.1 Common Enemies

#### Zombie

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 hit (armor loss or death) |
| Speed | 0.5-1 px/frame (variable) |
| Behavior | Rises from the ground, walks toward Arthur |
| Spawn | Continuously spawns from the ground in graveyard areas |
| Spawn rate | Every 2-4 seconds |
| Score | 100 |
| Stage | 1, 2 |

#### Red Arremer (Red Devil)

| Property | Value |
|----------|-------|
| HP | 3 |
| Damage | 1 |
| Speed | 2 px/frame (flight) |
| Behavior | Perches on walls/ground. When Arthur approaches, flies erratically and dive-bombs. Retreats and re-approaches. |
| AI | Actively dodges Arthur's projectiles; swoops when Arthur attacks |
| Score | 1,000 |
| Stage | 1, 3, 5, 6 |
| Note | One of the most feared enemies in gaming history. Very difficult to hit. |

#### Ghost (Phantom)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 |
| Speed | 1.5 px/frame |
| Behavior | Floats in sine wave pattern toward Arthur |
| Sine amplitude | 16 pixels |
| Sine period | ~48 pixels |
| Score | 200 |
| Stage | 2, 4, 6 |

#### Skeleton

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 |
| Speed | 1 px/frame |
| Behavior | Walks forward, throws bones in an arc |
| Bone speed | 2 px/frame |
| Score | 200 |
| Stage | 2, 3, 5 |

#### Crow (Raven)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 |
| Speed | 2.5 px/frame |
| Behavior | Flies horizontally, sometimes dives at Arthur |
| Score | 200 |
| Stage | 1, 2, 3 |

#### Plant (Venus Fly Trap)

| Property | Value |
|----------|-------|
| HP | 2 |
| Damage | 1 |
| Speed | 0 (stationary) |
| Behavior | Stationary, fires projectiles upward at intervals |
| Fire rate | Every 3 seconds |
| Score | 300 |
| Stage | 1, 3 |

#### Ogre (Big Man)

| Property | Value |
|----------|-------|
| HP | 3 |
| Damage | 1 |
| Speed | 1.5 px/frame |
| Behavior | Large enemy, charges forward, throws club |
| Score | 500 |
| Stage | 2, 4, 5 |

#### Blue Killer (Flying Knight)

| Property | Value |
|----------|-------|
| HP | 2 |
| Damage | 1 |
| Speed | 2 px/frame |
| Behavior | Flies in patterns, drops projectiles |
| Score | 500 |
| Stage | 4, 5, 6 |

#### Fire (Magma)

| Property | Value |
|----------|-------|
| HP | Invincible |
| Damage | 1 |
| Speed | 1 px/frame upward |
| Behavior | Rises from lava/fire pits periodically |
| Score | 0 |
| Stage | 4 (Fire stage) |

### 6.2 Red Arremer AI Detail

The Red Arremer deserves special attention due to its complex behavior:

```
1. PERCH: Sits on wall/ground. Waits for Arthur to enter range (~128 pixels).
2. LAUNCH: Takes off, flies to a position above and in front of Arthur.
3. DODGE: If Arthur fires a weapon, Red Arremer moves to dodge trajectory.
4. SWOOP: Dives toward Arthur at 3 px/frame diagonal.
5. PULL UP: After passing Arthur's Y level, pulls up and repositions.
6. REPEAT: Cycles between DODGE and SWOOP until killed or off-screen.
```

Dodge reaction time: ~6 frames (0.1 seconds) — reacts before the projectile reaches it.

---

## 7. Level Design — All 6 Stages

### Stage 1: Graveyard

| Property | Value |
|----------|-------|
| Setting | Cemetery with tombstones, dead trees |
| Enemies | Zombies (infinite spawning), crows, plant monsters, Red Arremers |
| Hazards | Tombstones (obstacles), pits |
| Terrain | Flat with small platforms, some pits |
| Length | ~2560 pixels |
| Timer | 300 seconds |
| Boss | Unicorn (one-headed dragon) |

### Stage 2: Ghost Forest

| Property | Value |
|----------|-------|
| Setting | Dark forest with dead trees and floating platforms |
| Enemies | Ghosts, skeletons, ogres, crows |
| Hazards | Moving platforms over pits, ladders |
| Terrain | Multi-level with platforms and ladders |
| Length | ~3072 pixels |
| Timer | 300 seconds |
| Boss | Unicorn (same as Stage 1 boss) |

### Stage 3: Ice Palace / Cave

| Property | Value |
|----------|-------|
| Setting | Icy cavern with stalactites |
| Enemies | Red Arremers, skeletons, flying enemies |
| Hazards | Falling ice, slippery surfaces (NES version may not have ice physics) |
| Terrain | Cavern with ladders, narrow platforms |
| Length | ~2560 pixels |
| Timer | 250 seconds |
| Boss | Dragon (two-headed) |

### Stage 4: Bridge / Fire Stage

| Property | Value |
|----------|-------|
| Setting | Bridge over fire/lava, volcanic area |
| Enemies | Ogres, flying knights, fire from below |
| Hazards | Fire rising from below, crumbling bridge segments |
| Terrain | Long bridge with gaps and moving platforms |
| Length | ~3072 pixels |
| Timer | 250 seconds |
| Boss | Dragon (twin dragons) |

### Stage 5: Castle Entrance

| Property | Value |
|----------|-------|
| Setting | Castle exterior, walls, and battlements |
| Enemies | Red Arremers, skeletons, axe knights, blue killers |
| Hazards | Moving platforms, long jumps, dense enemy placement |
| Terrain | Vertical and horizontal sections |
| Length | ~3072 pixels |
| Timer | 250 seconds |
| Boss | Satan (Astaroth) — false final boss |

### Stage 6: Demon Realm

| Property | Value |
|----------|-------|
| Setting | Interior of the demon castle, hellscape |
| Enemies | All enemy types combined, maximum density |
| Hazards | Every hazard combined, tightest platforming |
| Terrain | Complex multi-level layout |
| Length | ~3584 pixels |
| Timer | 200 seconds |
| Boss | Astaroth (true final boss — requires Cross weapon in second loop) |

---

## 8. Boss Encounters

### Stage 1 & 2 Boss: Unicorn (Shielder)

| Property | Value |
|----------|-------|
| HP | 8 |
| Damage | 1 |
| Pattern | Charges back and forth, fires projectiles |
| Speed | 2 px/frame |
| Projectile | Fireball aimed at Arthur |
| Fire rate | Every 2 seconds |
| Arena | Flat room, ~256 pixels wide |
| Score | 5,000 |

### Stage 3 & 4 Boss: Dragon

| Property | Value |
|----------|-------|
| HP | 12 |
| Damage | 1 |
| Pattern | Two heads that fire independently |
| Head 1 | Fires fireballs in 3-shot spread |
| Head 2 | Fires aimed fireballs |
| Fire rate | Each head fires every 2.5 seconds |
| Arena | Flat room with minor platforms |
| Score | 10,000 |

### Stage 5 Boss: Satan (Astaroth Form 1)

| Property | Value |
|----------|-------|
| HP | 16 |
| Damage | 1 |
| Pattern | Large demon, throws projectiles, ground pound |
| Speed | 1 px/frame |
| Projectiles | Homing flames |
| Ground pound | Shakes screen, stuns Arthur if on ground |
| Arena | Large room with platforms |
| Score | 20,000 |

### Stage 6 Final Boss: Astaroth

| Property | Value |
|----------|-------|
| HP | 20 (second loop: requires Cross weapon) |
| Damage | 1 |
| Pattern | Enhanced version of Satan fight, faster attacks |
| Special | In second loop, ONLY the Cross weapon can deal damage |
| Projectiles | Multiple homing flames, faster speed |
| Score | 50,000 |
| Victory | True ending only on second loop completion |

---

## 9. Item & Pickup System

### Container System

Pots and treasure chests appear at fixed locations. Breaking them reveals items.

| Container | Contents |
|-----------|----------|
| Pot (standard) | Weapon pickups, score items |
| Treasure chest | Armor, weapons, money bags |
| Magician pot (trap!) | Transforms Arthur into a frog for ~10 seconds |

### Item Drops

| Item | Effect | Source |
|------|--------|--------|
| Lance | Weapon: Lance | Pots |
| Dagger | Weapon: Dagger | Pots |
| Torch | Weapon: Torch | Pots |
| Axe | Weapon: Axe | Pots |
| Cross/Shield | Weapon: Cross (required for final boss) | Pots (specific locations) |
| Armor | Restores armor state | Treasure chests (rare) |
| Money Bag (200) | 200 points | Pots |
| Money Bag (500) | 500 points | Pots |
| Money Bag (1000) | 1,000 points | Treasure chests |
| Crown | 5,000 points | Very rare, specific locations |
| Frog transformation | Transforms Arthur to frog | Magician trap pot |

### Frog Transformation

| Property | Value |
|----------|-------|
| Duration | ~10 seconds |
| Movement | Can walk and jump (no attack) |
| Hitbox | Smaller (8 x 8 pixels) |
| Vulnerability | Still dies in 1 hit without armor |
| Trigger | Opening a magician pot |

---

## 10. Scoring System

| Source | Points |
|--------|--------|
| Zombie | 100 |
| Crow | 200 |
| Ghost | 200 |
| Skeleton | 200 |
| Plant | 300 |
| Red Arremer | 1,000 |
| Ogre | 500 |
| Flying Knight | 500 |
| Boss (Unicorn) | 5,000 |
| Boss (Dragon) | 10,000 |
| Boss (Satan) | 20,000 |
| Boss (Astaroth) | 50,000 |
| Time bonus | Remaining time x 100 |
| Money Bag | 200-1,000 |
| Crown | 5,000 |

### Extra Lives

| Score | Effect |
|-------|--------|
| 20,000 | 1 extra life |
| 70,000 | 1 extra life |
| Every 70,000 after | 1 extra life |

---

## 11. UI Layout & HUD

```
┌──────────────────────────────────────────────────────┐
│ SCORE  007,500      1P     HI  045,000    TIME 0237  │
│                     ♦♦♦                               │
├──────────────────────────────────────────────────────┤
│                                                       │
│     [Game playfield - graveyard/castle]               │
│                                                       │
│                                                       │
│                                                       │
│                                                       │
│                      STAGE 01                         │
└──────────────────────────────────────────────────────┘
```

### HUD Elements

| Element | Position | Description |
|---------|----------|-------------|
| SCORE | Top-left | Current score |
| 1P / Lives | Top-center | Player indicator and remaining lives |
| HI-SCORE | Top-center-right | Highest score |
| TIME | Top-right | Countdown timer |
| Stage number | Bottom-center | Current stage display |
| Weapon indicator | Not displayed | (Player must remember current weapon) |

---

## 12. Audio Design

### 12.1 Music (Composer: Ayako Mori)

| Track | Context | Style |
|-------|---------|-------|
| "The Graveyard" | Stage 1 | Iconic opening theme, driving and heroic |
| "The Ghost Forest" | Stage 2 | Eerie, darker variation |
| "The Ice Cave" | Stage 3 | Cold, haunting melody |
| "The Bridge" | Stage 4 | Intense, urgent |
| "The Castle" | Stage 5 | Dramatic, foreboding |
| "The Demon Realm" | Stage 6 | Dark, climactic |
| "Boss Battle" | All bosses | Heavy, aggressive |
| "Stage Clear" | After boss | Short fanfare |
| "Game Over" | Game over | Brief somber tune |
| "Map Screen" | Between stages | Brief transition music |
| "Ending" | Credits | Triumphant (or false ending message) |

### 12.2 Sound Effects

| Event | Description |
|-------|-------------|
| Weapon throw | "Whoosh" throwing sound |
| Weapon hit | Impact thud |
| Arthur hit (armor loss) | Armor breaking "crash" + brief stun sound |
| Arthur death | Death jingle + ghost rising sound |
| Enemy death | Explosion pop |
| Zombie rising | Dirt/rumble sound |
| Red Arremer screech | High-pitched screech on launch |
| Boss damage | Heavy impact |
| Item pickup | Chime |
| Frog transformation | Comic "poof" sound |
| Timer warning | Faster music tempo when time < 60 |
| Jump | Light hop sound |
| Landing | Soft thud |

---

## 13. Animation System

### 13.1 Arthur Animations

| Animation | Frames | FPS | Description |
|-----------|--------|-----|-------------|
| Idle (armored) | 1 | — | Standing with lance |
| Walk (armored) | 4 | 10 | Marching walk cycle |
| Jump (armored) | 2 | 8 | Legs tucked then extended |
| Throw (armored) | 3 | 15 | Wind-up, throw, recovery |
| Crouch (armored) | 1 | — | Kneeling |
| Climb ladder | 4 | 8 | Hand-over-hand climbing |
| Hit (armor break) | 4 | 12 | Armor flies off in pieces |
| Idle (underwear) | 1 | — | Same pose but in boxers |
| Walk (underwear) | 4 | 10 | Same cycle but in boxers |
| Death | 4 | 8 | Transforms to skeleton, ghost rises |
| Frog | 2 walk | 8 | Small frog hopping |

### 13.2 Enemy Animations

| Enemy | Key Animations |
|-------|---------------|
| Zombie | Rise from ground (4 frames), Walk (4 frames) |
| Red Arremer | Perch (2), Fly (4), Swoop (3), Dodge (2) |
| Ghost | Float (4 frames, sine wave) |
| Skeleton | Walk (4), Throw (3), Death (3) |
| Crow | Fly (4), Dive (2) |
| Boss | Multiple attack animations (4-6 frames each) |

---

## 14. Lives, Timer & Continue System

### Lives

| Property | Value |
|----------|-------|
| Starting lives | 3 |
| Maximum lives | 9 |
| Extra lives | At 20,000, 70,000, and every 70,000 after |

### Timer

| Property | Value |
|----------|-------|
| Starting time | 250-300 seconds per stage |
| Countdown speed | 1 unit per second |
| Time up | Instant death |
| Time bonus | Remaining time x 100 points at stage clear |
| Warning | Music tempo increases when time < 60 |

### Continues

| Property | Value |
|----------|-------|
| Arcade | Insert coin to continue |
| NES | 3 continues, restart at stage beginning |
| On continue | Lives reset to 3, score preserved |

---

## 15. Second Loop

### The Infamous Second Playthrough

| Property | Value |
|----------|-------|
| Trigger | Completing all 6 stages |
| Message | "This room is an illusion and is a trap devised by Satan. Go ahead dauntlessly! Make rapid progress!" |
| Effect | Game restarts from Stage 1 with increased difficulty |
| Enemy changes | More enemies, faster movement, more aggressive AI |
| Required weapon | Must reach final boss with the Cross/Shield weapon |
| Final boss | Can ONLY be damaged by Cross weapon |
| True ending | Only shown after completing the second loop |
| False ending | First loop ends with a message telling you to replay |

### Second Loop Difficulty Changes

| Change | Description |
|--------|-------------|
| Enemy speed | +25% to all enemy speeds |
| Enemy density | +50% more enemies spawned |
| Projectile speed | +30% faster enemy projectiles |
| Red Arremer | Even more aggressive dodge pattern |
| Timer | Reduced by 30 seconds per stage |
| Armor frequency | Fewer armor pickups |

---

## Appendix A: Difficulty Comparison

| Aspect | First Loop | Second Loop |
|--------|-----------|-------------|
| Enemy speed | Normal | +25% |
| Enemy count | Normal | +50% |
| Projectile speed | Normal | +30% |
| Timer | 250-300s | 220-270s |
| Armor pickups | Normal | Reduced |
| Final boss | Vulnerable to all weapons | Cross only |
| Ending | False ending | True ending |

## Appendix B: Quick Reference — Weapon Stats

| Weapon | Damage | Speed | Arc | On Screen | Rating |
|--------|--------|-------|-----|-----------|--------|
| Lance | 1 | 4 | Straight | 2 | Good |
| Dagger | 1 | 6 | Straight | 2 | Best |
| Torch | 1+area | 3 | Parabolic | 2 | Situational |
| Axe | 1 | 3 | High arc | 1 | Worst |
| Cross | 2 | 3 | Straight | 1 | Required |

---

*This specification is based on Ghosts 'n Goblins (1985 Arcade / 1986 NES) by Capcom. Values are sourced from gameplay analysis and community documentation. The arcade and NES versions have differences in enemy count, stage layout, and some mechanics.*
