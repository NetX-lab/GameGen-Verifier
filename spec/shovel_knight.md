# Shovel Knight — Complete Game Specification

> A comprehensive specification for faithfully recreating Shovel Knight: Shovel of Hope (Yacht Club Games, 2014). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics](#3-core-mechanics)
4. [Player Character — Shovel Knight](#4-player-character--shovel-knight)
5. [Relics (Sub-weapons)](#5-relics-sub-weapons)
6. [All Stages & Level Design](#6-all-stages--level-design)
7. [All Enemies — Complete Stats](#7-all-enemies--complete-stats)
8. [All Bosses](#8-all-bosses)
9. [Overworld Map](#9-overworld-map)
10. [Towns & NPCs](#10-towns--npc)
11. [Economy & Upgrades](#11-economy--upgrades)
12. [UI Layout & Screens](#12-ui-layout--screens)
13. [Audio Design](#13-audio-design)
14. [New Game Plus & Extras](#14-new-game-plus--extras)

---

## 1. Game Overview

- **Genre**: 2D action platformer (NES-inspired)
- **Perspective**: 2D side-scrolling
- **Input**: D-pad (left/right movement), A (jump), B (attack/shovel), Up+B (use relic), Down (in air: shovel bounce)
- **Objective**: Defeat the Order of No Quarter (8 knights) and confront The Enchantress at the Tower of Fate.
- **Lose Condition**: HP reaches zero. Lose portion of gold. Respawn at last checkpoint.
- **Win Condition**: Complete all stages and defeat The Enchantress in the Tower of Fate.
- **Art style**: NES-era pixel art with expanded color palette (more colors than actual NES).

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 400 x 240 pixels |
| Tile size | 16 x 16 pixels |
| Frame rate | 60 FPS |
| Color palette | NES-inspired but expanded (full 24-bit, limited self-imposed per-sprite) |
| Max sprites visible | No hard limit (unlike real NES) |
| Parallax layers | 2-3 per stage |

### Coordinate System

- Origin (0, 0) at top-left.
- Pixel-perfect collision.
- Sub-pixel movement tracked internally.
- Camera: Horizontal scroll follows player. Vertical: shows full room height or scrolls with player in tall rooms.

### Game Loop

```
1. Process input
2. Update player state machine (idle, walk, jump, attack, shovel bounce, hurt, relic use)
3. Update all enemies (AI state machines, movement, attacks)
4. Update projectiles
5. Update environment objects (moving platforms, breakable blocks, checkpoints)
6. Check collisions (player-enemy, player-environment, projectile-enemy)
7. Update camera
8. Render parallax backgrounds
9. Render tilemap
10. Render entities (enemies, items, player)
11. Render particles/effects
12. Render HUD
```

---

## 3. Core Mechanics

### Movement

| Parameter | Value |
|-----------|-------|
| Walk speed | 1.5 px/frame (90 px/sec) |
| Jump height | ~64 pixels (4 tiles) |
| Jump velocity | -4.5 px/frame upward |
| Gravity | 0.25 px/frame² |
| Max fall speed | 5.0 px/frame |
| Air control | Full horizontal control in air |
| Coyote time | 4 frames |

### Shovel Attack (Ground)

| Parameter | Value |
|-----------|-------|
| Attack duration | 12 frames |
| Hitbox | 20 x 10 pixels, forward from Shovel Knight |
| Damage | Varies by upgrade (see table below) |
| Recovery | 6 frames before next attack |
| Movement | Can walk during attack |
| Direction | Always forward (facing direction) |

### Shovel Drop / Bounce (Signature Mechanic)

| Parameter | Value |
|-----------|-------|
| Activation | Hold Down while airborne |
| Hitbox | 10 x 8 pixels, directly below Shovel Knight |
| Damage | Same as shovel attack |
| Bounce height | 48 pixels (3 tiles) — same as small jump |
| Bounce off enemy | Resets jump ability (can bounce infinitely) |
| Bounce off terrain | Certain shiny/special surfaces allow bounce |
| Movement | Full horizontal control during drop |
| Speed | Falls at normal gravity (not accelerated) |

### Dig Attack

- Press Down on ground near **dirt piles** or **breakable blocks** to dig.
- Dig cycle: 8 frames per dig.
- Dirt piles yield gems (random: 1-50 gold each).
- Breakable blocks shatter (may contain items or hidden rooms).

### Checkpoint System

- Checkpoints are **glowing globes** on pedestals throughout stages.
- Touching one activates it (visual change: globe lights up).
- On death: Respawn at last activated checkpoint.
- **Destroying checkpoints**: Player can shovel-attack checkpoints to break them for bonus gold (50-200 gold). But that checkpoint is permanently lost — respawn at earlier checkpoint if you die.
- This is a risk/reward mechanic central to the game's design.

### Death & Gold Loss

- On death, Shovel Knight loses **25% of current gold**.
- Lost gold appears as **3 floating gold bags** at the death location.
- Bags float in place for the attempt. If player reaches them, gold is recovered.
- If player dies again before recovery, previous bags disappear (gold lost permanently).
- Bag values: Split roughly evenly among 3 bags.
- Bags float at the death position, bobbing up and down slightly (sinusoidal, 2px amplitude, 60-frame period).

---

## 4. Player Character — Shovel Knight

### Stats

| Stat | Starting | Maximum |
|------|----------|---------|
| HP | 8 (4 meal tickets visible as hearts) | 14 (10 full meal tickets after all upgrades) |
| Magic | 0 (no magic bar initially) | 100 (after all magic upgrades) |
| Attack (Shovel) | 2 per hit | 6 per hit (with Dynamo Mail) |
| Gold | 0 | Unlimited (no cap) |
| Relics | 0 | 12 |

### Health System

- Health displayed as **meal tickets** (heart-shaped).
- Each meal ticket = 2 HP.
- Starting: 4 meal tickets (8 HP).
- After all upgrades: 10 meal tickets (20 HP) — wait, the game has 8 base + up to 6 more from Meal Tickets purchased = 14 total meal tickets visible.
- Actually the maximum health upgrades provide 2 HP each. There are 5 health upgrades for 10 extra HP = 18 HP max total displayed as full/half hearts.

### Armor Sets

| Armor | Cost (Gold) | Effect |
|-------|-------------|--------|
| Stalwart Plate (default) | — | No special effect. Standard defense. |
| Final Guard | 3000 | Lose less gold on death (12.5% instead of 25%). No knockback from hits. |
| Dynamo Mail | 6000 | Shovel attack charges: 2 successive hits without pause = 3rd hit does 2x damage. Shovel drop sparks on ground. |
| Mail of Momentum | 4000 | Cannot be knocked back. Slightly reduced traction (slides on stop). |
| Ornate Plate | 8000 | Lose MORE gold on death (37.5%) but gain gold faster from digging (+50% dig yields). |
| Conjurer's Coat | 5000 | Magic costs reduced by 50%. Magic meter is halved (50 max). |

### Shovel Upgrades

| Upgrade | Cost | Effect |
|---------|------|--------|
| Charge Handle | 4000 | Hold attack button to charge. Release for powerful forward thrust (3x damage, 2x range). Charge time: 45 frames. |
| Drop Spark | 6000 | Shovel drop on ground creates spark projectile that travels forward (3 tiles, same damage as shovel). |
| Trench Blade | 3000 | Dig piles send debris forward as projectile (damage: 1, range: 4 tiles). |

---

## 5. Relics (Sub-weapons)

Relics are special items purchased from Chester (treasure chest NPC) found in stages, or from the Relic merchant in town.

| Relic | Found In | Cost | Magic Cost | Damage | Effect |
|-------|----------|------|-----------|--------|--------|
| Flare Wand | Plains of Passage | 1000 | 4 | 2 | Fires fireball forward. Travels 8 tiles. Bounces off walls once. |
| Phase Locket | Pridemoor Keep | 1000 | 8/sec | 0 | Become invincible while held. Drains magic continuously. Can walk through enemies and projectiles. |
| Dust Knuckles | Lost City | 3000 | 2 | 2 | Punches forward through dirt blocks. Can be used in air. Short range (1.5 tiles). Rapid fire (6 frame cooldown). |
| Throwing Anchor | Iron Whale | 3000 | 6 | 3 | Throws anchor in arc. Travels ~4 tiles distance. Bounces off ground once. |
| Alchemy Coin | Explodatorium | 3000 | 8 | 3 | Bouncing coin projectile. Bounces 3 times off walls/floor, gaining damage each bounce (+1 per bounce). |
| Mobile Gear | Clockwork Tower | 3000 | 6 | 1 | Deploys gear on ground that travels forward. Shovel Knight can ride it. Speed: 3 px/frame. Lasts until hitting wall. |
| War Horn | Lich Yard | 4000 | 20 | 4 | Screen-wide attack. Damages all enemies visible. Massive magic cost. |
| Propeller Dagger | Flying Machine | 4000 | 4 | 1 | Dash forward in midair. Distance: 6 tiles. Can be aimed slightly up/down. Reusable in air. |
| Chaos Sphere | Stranded Ship | 4000 | 8 | 2 | Bouncing energy ball. Ricochets off all surfaces for 5 seconds. |
| Fishing Rod | Village shop | 1250 | 0 | 0 | Cast into sparkle points to catch items (gold, meal ticket, etc.). Found at specific spots. |
| Troupple Chalice | Troupple Pond | 1500 | 0 | 0 | Container for Troupple King's blessings (Ichor). Holds 2 ichors. |

### Troupple Ichors

| Ichor | Effect |
|-------|--------|
| Ichor of Renewal | Full health + full magic restore |
| Ichor of Boldness | Invincibility for 10 seconds |

---

## 6. All Stages & Level Design

### Stage Order (Overworld Progression)

| Stage | Knight Boss | Theme | Length (screens) | New Mechanic/Gimmick |
|-------|------------|-------|------------------|---------------------|
| Plains of Passage | — (intro stage) | Grassy plains | 12 | Tutorial: basic mechanics |
| Pridemoor Keep | King Knight | Castle | 15 | Chandeliers (swing), confetti cannons |
| The Lich Yard | Specter Knight | Graveyard/undead | 14 | Lightning, skeleton platforms, rising darkness |
| Explodatorium | Plague Knight | Alchemy lab | 15 | Explosive barrels, chemical vats, timed fuses |
| Iron Whale | Treasure Knight | Submarine/underwater | 14 | Conveyor belts, anchor traps, pressure |
| Lost City | Mole Knight | Underground ruins | 14 | Lava pits, burrowing sections, collapsing floors |
| Clockwork Tower | Tinker Knight | Mechanical tower | 15 | Gears, moving cogs, conveyor platforms, precision timing |
| Stranded Ship | Polar Knight | Ice/shipwreck | 14 | Ice physics (slide), snow drifts, wind |
| Flying Machine | Propeller Knight | Airship | 13 | Wind gusts, propeller platforms, falling sections |
| Tower of Fate: Entrance | — | Dark castle | 10 | All mechanics combined |
| Tower of Fate: Ascent | Order of No Quarter rematches | Tower interior | 15 | Boss gauntlet (all 8 knights) |
| Tower of Fate: ??? | The Enchantress / Shield Knight | Final area | 5 | Final boss encounters |

### Stage Design Principles

Each stage has:
- **3-5 checkpoints** (destroyable for gold).
- **1 Chester location** (sells a Relic specific to that stage).
- **2-3 hidden music sheets** (collectible side quest).
- **Multiple secret walls** (bombable or breakable, containing gold or items).
- **1-3 meal ticket pickups** (restore health).
- **Gem-filled dirt piles** scattered throughout.

### Plains of Passage — Detailed Layout

**Screen 1 (Tutorial: Walking)**
```
████████████████████████████████████████
█                                      █
█  SK-->           GEM  GEM            █
█  ██████████  ████████████████████████ █
████████████████████████████████████████
SK = Shovel Knight start
GEM = gem pickup (5 gold)
Flat terrain, walk right to proceed.
```

**Screen 2 (Tutorial: Jumping)**
```
████████████████████████████████████████
█                                      █
█              ████                    █
█      ████          ████              █
█  ████                    ████  ████████
█                    PIT                █
████████████████████████████████████████
PIT = bottomless pit (death).
Jump across platforms.
```

**Screen 3 (Tutorial: Shovel Attack)**
```
████████████████████████████████████████
█                                      █
█         [BEETO] [BEETO]              █
█  ████████████████████████  ██████████ █
█                         DP           █
████████████████████████████████████████
BEETO = beetle enemy (1 HP)
DP = dirt pile (dig for gold)
```

**Screen 4 (Tutorial: Shovel Drop)**
```
████████████████████████████████████████
█                                      █
█  SK        ◆◆◆        ████          █
█  ████      ◆◆◆              ████    █
█            ◆◆◆                       █
█      ████████████████                █
████████████████████████████████████████
◆ = bounce blocks (shovel drop to bounce upward and reach high platform)
```

### Pridemoor Keep — Key Features

- Chandeliers: Shovel drop onto chandelier = swings forward, releasing after reaching apex. Launch distance: ~4 tiles.
- Guards: Sword-wielding enemies that block frontal attacks. Must attack from behind or shovel drop.
- Dining hall: Long room with food on tables (meal tickets) and attacking servants.
- Throne room: Boss arena (King Knight).

### Clockwork Tower — Key Features

- Large gears: Rotating platforms. Player stands on teeth and rides around. Jump off at right moment.
- Conveyor belts: Move player left/right at 1 px/frame.
- Timed sections: Platforms appear/disappear on 120-frame cycles.
- Crushing pistons: Move up/down every 90 frames. Being underneath = instant death.

---

## 7. All Enemies — Complete Stats

### Common Enemies

| Enemy | HP | Damage | Gold Drop | Behavior | Found In |
|-------|----|----|----------|----------|----------|
| Beeto | 1 | 1 | 5 | Walks back and forth on platform edge | Plains, multiple |
| Blorb | 2 | 1 | 10 | Blob. Hops toward player every 60 frames. | Multiple |
| Boneclang | 3 | 1 | 15 | Skeleton warrior. Swings sword. 2-hit combo. Blocks occasionally. | Lich Yard |
| Bonerang | 2 | 1 | 12 | Throws bone boomerang. Range: 5 tiles. | Lich Yard |
| Birder | 2 | 1 | 15 | Flying bird. Swoops diagonally at player. | Plains, Flying Machine |
| Blitzsteed | 2 | 1 | 10 | Horse enemy. Charges horizontally at 3 px/frame. | Pridemoor Keep |
| Cogslotter | 3 | 1 | 20 | Rides gear, throws wrenches. | Clockwork Tower |
| Dozedrake | 4 | 2 | 25 | Dragon. Breathes fire (flame: 3 tiles range, 1 damage). | Lost City |
| Electrodent | 3 | 2 | 20 | Electric eel. Electrifies platforms periodically. | Iron Whale |
| Floatzinger | 3 | 1 | 15 | Flying jellyfish. Shoots electricity downward every 90 frames. | Iron Whale |
| Goldarmor | 4 | 2 | 30 | Gold knight. Charges, blocks attacks. Must hit from behind. | Tower of Fate |
| Hover Meanie | 1 | 1 | 5 | Hovers in place, fires small projectile when player is near. | Multiple |
| Lich | 3 | 2 | 25 | Summons skeleton minions (1 HP each). Teleports. | Lich Yard |
| Macawbe | 2 | 1 | 10 | Carries Beeto/enemy, drops when over player. | Flying Machine |
| Propellerrat | 2 | 1 | 15 | Flies with propeller. Chases player slowly. | Flying Machine |
| Superske | 3 | 1 | 15 | Skeleton with lance. Charges with lance extended. | Multiple |
| Tadvolt | 1 | 1 | 5 | Small electric creature. Moves in sine wave. | Multiple |
| Wizzem | 3 | 1 | 20 | Wizard. Teleports items/player across room. Can teleport player into hazards. | Multiple |

### Mini-Bosses (Stage Mid-Points)

| Mini-Boss | HP | Damage | Stage | Behavior |
|-----------|----|----|-------|----------|
| Black Knight (1st) | 12 | 2 | Plains of Passage | Sword combos, charge, shovel drop counter |
| Baz | 15 | 2 | Overworld encounter | Whip attacks, electrified whip slam |
| Phantom Striker | 15 | 2 | Overworld encounter | Teleporting sword strikes, lightning |
| Reize | 10 | 1 | Overworld encounter | Boomerang throws, acrobatic jumps |

---

## 8. All Bosses

### King Knight (Pridemoor Keep)

- **HP**: 18
- **Arena**: Flat throne room with chandelier above center.
- **Attacks**:
  - Charge: Runs at player at 2.5 px/frame. Damage: 2. Bounces off wall.
  - Trumpet Blast: Calls confetti from above (4 confetti pieces, fall in columns). Damage: 1 each.
  - Jump: Leaps in arc to player's position. Ground pound on landing. Shockwave: 1 damage, 2 tiles.
  - After bounce off wall: Does spinning attack while falling. Damage: 1.
- **Pattern**: Charge -> wall bounce -> fall -> trumpet -> jump -> repeat.
- **Speed increases**: Below 8 HP, all actions 20% faster.

### Specter Knight (Lich Yard)

- **HP**: 20
- **Attacks**:
  - Scythe Swing: Melee range, 2 damage. Very fast (8 frame wind-up).
  - Scythe Throw: Throws scythe like boomerang. Range: full screen. Damage: 2. Returns to Specter.
  - Teleport Slash: Disappears, reappears behind player, slashes. 1 second tell (dark particles at destination).
  - Summon Skeletons: Raises 2 skeletons (3 HP each) from ground. Every 90 frames.
- **Pattern**: Mix of melee and ranged. Teleports when player is far.
- **Phase 2** (HP < 10): Scythe throw frequency doubles. Teleports more often.

### Plague Knight (Explodatorium)

- **HP**: 18
- **Attacks**:
  - Bomb Toss: Throws 3 bombs in arc. Bombs explode after 45 frames or on contact with ground. Blast: 24x24 pixels, 2 damage.
  - Chemical Vat Drop: Drops green chemical that pools on ground (16x8 pixels). Touching pool: 1 damage. Lasts 180 frames.
  - Burst Jump: Explosive jump upward, leaves explosion at takeoff point. Damage: 2.
  - Rapid Fire: Throws 5 small bombs in quick succession (1 bomb every 8 frames).
- **Pattern**: Hops around arena, tossing bombs. Burst jump when player is close.

### Treasure Knight (Iron Whale)

- **HP**: 22
- **Attacks**:
  - Anchor Toss: Throws anchor forward. Range: 6 tiles. Damage: 2. Drags along ground on return.
  - Chest Shield: Holds treasure chest as shield. Blocks frontal attacks. Must attack from above or behind.
  - Grapple Pull: Launches chain, grabs player, pulls toward him. Damage: 1.
  - Water Burst: Floods lower portion of arena for 120 frames. Standing in water: reduced speed.
- **Pattern**: Defensive, waits for player. Anchor toss -> shield -> grapple -> repeat.

### Mole Knight (Lost City)

- **HP**: 20
- **Attacks**:
  - Burrow: Digs underground, tracks player, surfaces with upward slash. Damage: 2. Underground time: 60 frames.
  - Claw Slash: Quick melee combo (2 slashes). Damage: 1 each.
  - Fire Trail: Leaves fire on ground when burrowing. Fire: 1 damage per contact. Lasts 120 frames.
  - Lava Geyser: Triggers 3 lava geysers from ground. Random positions. Damage: 2. Height: 4 tiles. Duration: 30 frames.
- **Phase 2** (HP < 10): Burrow speed increased. Fire trail is wider.

### Tinker Knight (Clockwork Tower)

- **HP Phase 1**: 8. **HP Phase 2**: 24.
- **Phase 1** (Walking):
  - Tiny, runs back and forth in panic. Throws wrenches (arc trajectory). Damage: 1.
  - Easy phase. Quick to defeat.
- **Phase 2** (Mech Suit): Tinker Knight enters giant mech robot.
  - Rocket Fist: Fires fist forward. Range: full screen. Damage: 2. Returns to mech.
  - Drill: Drills downward from above. Damage: 2.
  - Missiles: Fires 4 missiles upward that rain down. Damage: 1 each.
  - Charge: Mech charges across arena. Speed: 3 px/frame. Damage: 2.
  - Weakness: Jump on head to damage. Shovel drop on head platform.
  - Mech is 48x64 pixels.

### Polar Knight (Stranded Ship)

- **HP**: 24
- **Attacks**:
  - Shovel Slam: Slams giant shovel creating shockwave. Range: 3 tiles. Damage: 2.
  - Snow Throw: Scoops snow, throws arc of snowballs (3 snowballs). Damage: 1 each.
  - Ice Spike: Summons ice spike from ground at player position. 1 second delay (flash warning). Damage: 2.
  - Charge: Slow charge with shovel forward. Speed: 1.5 px/frame. Damage: 2.
- **Arena**: Ice floor (reduced traction, player slides).
- **Phase 2** (HP < 12): Arena floor partially collapses. Must fight on remaining platforms.

### Propeller Knight (Flying Machine)

- **HP**: 20
- **Attacks**:
  - Rapier Thrust: Quick forward thrust. Range: 2 tiles. Damage: 1.
  - Propeller Lift: Flies upward, creates downward wind that pushes player toward edge. Wind: 1 px/frame push.
  - Bombing Run: Flies across screen dropping 4 bombs. Damage: 1 each.
  - Rapier Combo: 3-hit combo with advancing thrusts. Damage: 1 per hit.
- **Arena**: Airship deck. Edges are instant death (falling off ship).
- **Phase 2** (HP < 10): Wind gusts become stronger (2 px/frame). Bombs increase to 6.

### Black Knight (Tower of Fate — Final encounter)

- **HP**: 25
- **Attacks**: Mirrors Shovel Knight's moveset.
  - Shovel Swing: 2 damage.
  - Shovel Drop: Bounces off player's head. 2 damage.
  - Charge: Runs at player. 2 damage.
  - Counter: Blocks player's attack, counter-slashes.
- **Phase 2** (HP < 12): Uses purple magic projectiles (3 orbs in spread, 1 damage each).

### The Enchantress (Final Boss)

- **HP**: 30
- **Phase 1**:
  - Fireball Barrage: 6 fireballs in spread pattern. Damage: 2. Speed: 2.5 px/frame.
  - Teleport: Disappears for 30 frames, reappears at random position.
  - Dark Orbs: 3 homing orbs. Speed: 1.5 px/frame. Damage: 1. Homing for 120 frames then dissipate.
  - Pillar: Summons dark pillar from ground. Width: 2 tiles. Damage: 2. Lasts 60 frames.
- **Phase 2** (HP < 15): Floats above. Continuous fireball rain. Must use shovel drop on floating platforms to reach her.

### Shield Knight (Epilogue Boss — Cooperative)

- Shield Knight fights alongside Shovel Knight against The Enchantress's final form (Remnant of Fate).
- Shield Knight AI: Blocks projectiles aimed at player, reflects them at boss.
- Player must bounce attacks off Shield Knight to hit aerial boss.
- **Remnant of Fate HP**: 20.
- **Attacks**: Falling orbs (8 per wave, 1 damage each), sweeping beam (2 damage, 120 frames).
- Phase ends when defeated. Story conclusion follows.

---

## 9. Overworld Map

### Map Layout

```
+----------------------------------------------------------+
|                        Tower of Fate                       |
|                            ★                               |
|                           / \                              |
|             Flying Machine    Stranded Ship                |
|                  ●                ●                        |
|                 / \              / \                       |
|        Clock Tower  ●--Village 3--●  Iron Whale            |
|             ●         (Armor Outpost)      ●              |
|            / \                            / \              |
|   Lost City   ●--- Village 2 ---●  Explodatorium         |
|       ●           (Juice Bar)          ●                  |
|      / \                              / \                  |
| Lich Yard  ●----- Village 1 -----●  Pridemoor Keep        |
|     ●           (The Village)          ●                  |
|                      |                                     |
|              Plains of Passage                             |
|                      ●                                     |
+----------------------------------------------------------+
```

### Overworld Navigation

- Player moves Shovel Knight icon along paths between nodes.
- Paths unlock as stages are completed.
- **Wandering Encounters**: On paths, random encounter icons (skulls) appear. Walking into them triggers a small combat arena (1-2 screens, enemies, gold rewards).
- 3 wandering encounter types: Boneclang battle, Birder swarm, Goldarmor gauntlet.
- Each awards 200-400 gold.

### Stage Unlock Order

- **Tier 1** (any order): Plains of Passage, Pridemoor Keep, Lich Yard
- **Tier 2** (after completing 2 Tier 1): Explodatorium, Lost City, Iron Whale
- **Tier 3** (after completing 2 Tier 2): Clockwork Tower, Stranded Ship, Flying Machine
- **Tower of Fate** (after all 8 Order stages complete)

---

## 10. Towns & NPCs

### Village 1 — The Village

| NPC | Service |
|-----|---------|
| Gastronomer | Sells Meal Tickets (HP upgrades). 1st: 1000g, 2nd: 2500g, 3rd: 5000g. Each adds 2 HP. |
| Magicist | Sells Magic upgrades. 1st: 1000g, 2nd: 3000g, 3rd: 6000g. Each adds 10 max magic. |
| Mona | Hint NPC (Plague Knight's campaign reference) |
| Bard | Plays music sheets you've collected. Each sheet unlocked adds 500g reward. |
| Mr. Hat | Sells Shovel upgrades (see Section 4) |
| Shovel Smith | Sharpens shovel for gold (attack upgrade path) |

### Village 2 — Armor Outpost

| NPC | Service |
|-----|---------|
| Armorer | Sells armor sets (see Section 4, Armor Sets) |
| Mr. Hat | Additional headgear customization (cosmetic) |
| Goatician | Sells relics not found in stages |
| Troupple Acolyte | Access to Troupple Pond (Troupple King for ichors) |

### Village 3 — (Above Armor Outpost)

Additional shops and NPCs that appear as game progresses.

### Troupple Pond

- Accessible from overworld.
- Dance with the Troupple King to fill Troupple Chalices.
- Choose: Ichor of Renewal (full restore) or Ichor of Boldness (invincibility).
- Each Chalice holds 1 ichor. Can carry up to 2 chalices.

---

## 11. Economy & Upgrades

### Gold Sources

| Source | Amount |
|--------|--------|
| Gem (small, blue) | 1 |
| Gem (medium, green) | 5 |
| Gem (large, red) | 25 |
| Gem (diamond) | 100 |
| Gem (gold bar) | 300 |
| Dirt pile dig | 1-50 (random) |
| Enemy kill | 5-30 (varies) |
| Checkpoint destroy | 50-200 |
| Hidden room treasure | 100-500 |
| Wandering encounter | 200-400 |
| Music sheet to Bard | 500 each |
| Boss bonus | 300-1000 |

### Upgrade Costs Summary

| Upgrade Category | Total Cost (all levels) |
|-----------------|------------------------|
| Meal Tickets (HP) | 8,500 |
| Magic upgrades | 10,000 |
| Shovel upgrades | 13,000 |
| Armor sets | 26,000 |
| Relics | ~30,000 |
| Total to buy everything | ~87,500 |

### Music Sheet Locations

- 46 music sheets total.
- 2-3 per stage (hidden in secret areas).
- Additional sheets from overworld encounters.
- Each returned to Bard: 500 gold reward.
- All sheets returned: Bard plays full soundtrack (jukebox unlocked).

---

## 12. UI Layout & Screens

### In-Game HUD

```
+------------------------------------------------------------------+
| [♥♥♥♥♥♥♥][♥♥♥]    [B-ITEM ICON]    [GOLD: 01234]               |
| (HP hearts, full    (current relic)   (gold counter)              |
|  and empty)                                                       |
| [▓▓▓▓▓▓░░░░]                                                    |
| (Magic meter)                                                     |
|                                                                   |
|                    (GAMEPLAY AREA)                                |
|                    400 x 210 pixels                               |
|                                                                   |
+------------------------------------------------------------------+
```

- **HP**: Top-left. Heart icons (full = red, empty = grey outline). Half hearts shown as half-filled.
- **Magic Meter**: Below HP. Blue bar. Depletes as relics are used.
- **Relic Icon**: Top-center. Currently equipped relic (Up+B to use).
- **Gold**: Top-right. Numeric counter.

### Pause Menu / Inventory

```
+--------------------------------------------------+
|  SHOVEL KNIGHT                                     |
|                                                    |
|  RELICS:                                           |
|  [Icon1] [Icon2] [Icon3] ... [Icon12]             |
|  (Select with D-pad, confirm to equip)            |
|                                                    |
|  TROUPPLE CHALICES: [Full/Empty] [Full/Empty]     |
|  MUSIC SHEETS: 23/46                               |
|                                                    |
|  > RESUME                                          |
|    OPTIONS                                         |
|    FEATS (achievements)                            |
|    QUIT TO MAP                                     |
+--------------------------------------------------+
```

### Title Screen

```
+----------------------------------+
|                                  |
|       SHOVEL KNIGHT              |
|    SHOVEL OF HOPE                |
|                                  |
|  [Shovel Knight silhouette      |
|   against campfire]             |
|                                  |
|    > START GAME                  |
|      OPTIONS                     |
|      FEATS                       |
|                                  |
|  © 2014 Yacht Club Games        |
+----------------------------------+
```

### Stage Clear Screen

```
+------------------------------------------+
|    STAGE CLEAR!                           |
|                                           |
|    Stage: Pridemoor Keep                  |
|    Gold Earned: 3,456                     |
|    Total Gold: 15,789                     |
|                                           |
|    [Shovel Knight victory pose]           |
|                                           |
|    PRESS START TO CONTINUE               |
+------------------------------------------+
```

---

## 13. Audio Design

### Music (Composed by Jake Kaufman, Manami Matsumae)

| Track | Stage/Context | BPM | Style |
|-------|--------------|-----|-------|
| "Strike the Earth!" | Plains of Passage | 160 | Upbeat NES-chiptune, heroic |
| "The Rival" | Black Knight encounters | 150 | Intense, driving |
| "Pridemoor Keep" | Pridemoor Keep stage | 140 | Regal, medieval chip |
| "La Danse Macabre" | Lich Yard | 120 | Spooky, minor key, organs |
| "The Vital Vitriol" | Explodatorium | 150 | Frantic, bubbling arpeggios |
| "High Above the Land" | Flying Machine | 140 | Adventurous, wind-swept |
| "The Schemer" | Clockwork Tower | 130 | Mechanical, precise rhythms |
| "A Cargo of Fineries" | Iron Whale | 120 | Deep, submarine |
| "In the Halls of the Usurper" | Tower of Fate | 160 | Dark, epic, final dungeon |
| "The Apparition" | Specter Knight boss | 150 | Haunting, fast |
| "End of Days" | Final boss themes | 170 | Intense, climactic |
| "Main Theme" | Title screen | 120 | Nostalgic, hopeful |
| "Of Devious Machinations" | Tinker Knight boss | 140 | Playful then intense |
| "Village" | Town themes | 100 | Peaceful, shops |
| "Campfire" | Dream sequences/campfire | 80 | Melancholic, slow |

### Sound Effects

| Sound | Trigger |
|-------|---------|
| Shovel swing | Attack button |
| Shovel hit (enemy) | Damage dealt to enemy |
| Shovel hit (ground/dirt) | Dig action |
| Shovel bounce | Shovel drop on enemy/surface |
| Jump | Jump button |
| Land | Touching ground |
| Damage taken | Player hit |
| Gold collect | Picking up gems |
| Gold drop (death) | Dying, gold bags spawning |
| Relic use | Up+B with relic |
| Checkpoint activate | Touching checkpoint globe |
| Checkpoint destroy | Breaking checkpoint |
| Boss intro | Boss appears |
| Boss death | Boss defeated |
| Music sheet get | Collecting music sheet |
| Meal ticket use | Eating food/restoring health |
| Menu navigate | D-pad in menu |
| Menu confirm | A in menu |
| Stage clear | Completing a stage |

---

## 14. New Game Plus & Extras

### New Game Plus

After completing the game, New Game Plus is available:
- All gold and relics carry over.
- Enemies deal **double damage** (2 becomes 4, etc.).
- Fewer checkpoints in stages.
- No gameplay changes to mechanics.
- Can re-purchase any missed items.

### Feats (Achievements)

48 total feats tracking various accomplishments:
- Complete each stage.
- Defeat bosses without taking damage.
- Collect all music sheets.
- Break every checkpoint in a stage.
- Complete the game in under 90 minutes (speedrun feat).
- Complete without dying (deathless feat).
- Complete without buying armor.
- Various relic-specific challenges.

### Dream Sequences

Between stages, Shovel Knight has campfire dream sequences:
- Player catches falling Shield Knight sprite.
- Each dream gets progressively more enemies interfering.
- Score based on how long Shield Knight stays caught.
- Purely cosmetic/story — no gameplay reward.
- 3 dream sequences total (after stage tiers 1, 2, and 3).

---

## Appendix: Timing Constants

| Constant | Value |
|----------|-------|
| Frames per second | 60 |
| Walk speed | 1.5 px/frame |
| Jump velocity | -4.5 px/frame |
| Gravity | 0.25 px/frame² |
| Max fall speed | 5.0 px/frame |
| Shovel attack duration | 12 frames |
| Shovel attack recovery | 6 frames |
| Shovel drop bounce height | 48 pixels |
| Coyote time | 4 frames |
| Invincibility after hit | 60 frames (1 second) |
| Knockback duration | 12 frames |
| Checkpoint flash | 8 frames |
| Bomb fuse (Plague Knight stage) | 45 frames |
| Boss pattern cycle | ~180-300 frames per cycle |
| Screen transition | 20 frames (0.33 seconds) |
| Death animation | 30 frames |
| Respawn animation | 20 frames |
| Gold bag bob amplitude | 2 pixels |
| Gold bag bob period | 60 frames |
| Charge attack charge time | 45 frames |
| Phase Locket drain | 8 magic/second |
