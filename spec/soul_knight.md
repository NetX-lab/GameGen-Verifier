# Soul Knight -- Complete Game Specification

> A comprehensive specification for faithfully recreating Soul Knight (ChillyRoom Inc., 2017, Android/iOS/Switch). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Combat Mechanics](#3-core-combat-mechanics)
4. [Character System -- All Playable Heroes](#4-character-system----all-playable-heroes)
5. [Skill System](#5-skill-system)
6. [Weapon System](#6-weapon-system)
7. [Weapon Attachments & Merging](#7-weapon-attachments--merging)
8. [Dungeon Generation & Floor Structure](#8-dungeon-generation--floor-structure)
9. [Enemy Types per Biome](#9-enemy-types-per-biome)
10. [Boss Encounters](#10-boss-encounters)
11. [Energy & Mana System](#11-energy--mana-system)
12. [Shield, Armor & HP Mechanics](#12-shield-armor--hp-mechanics)
13. [Buff System](#13-buff-system)
14. [Status Effects & Elemental Damage](#14-status-effects--elemental-damage)
15. [Garden & Base Mechanics](#15-garden--base-mechanics)
16. [Pet System](#16-pet-system)
17. [Follower & Mercenary System](#17-follower--mercenary-system)
18. [Currency & Economy](#18-currency--economy)
19. [Crafting, Forging & Workshop](#19-crafting-forging--workshop)
20. [Game Modes](#20-game-modes)
21. [Multiplayer Co-op](#21-multiplayer-co-op)
22. [UI Layout & HUD](#22-ui-layout--hud)
23. [Audio Design](#23-audio-design)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Soul Knight |
| Developer | ChillyRoom Inc. |
| Initial Release | February 17, 2017 |
| Platforms | Android, iOS, Nintendo Switch |
| Genre | Roguelike top-down shooter |
| Perspective | Top-down 2D with pixel-art visuals |
| Input | Dual virtual joystick (move left, shoot right) + skill button |
| Objective | Retrieve the Magic Stone from the dungeon's final floor by clearing procedurally generated rooms of enemies and bosses |
| Lose Condition | Player HP reaches 0 with no revival options remaining |
| Win Condition | Defeat the final boss on Floor 3 (level 3-5) and interact with the Magic Stone |
| Session Length | A typical successful run takes 15--30 minutes |

### Premise

Aliens have stolen the Magic Stone that maintains balance in the world. Players choose a hero, enter a procedurally generated dungeon, fight through three floors of enemies and bosses, collect weapons and buffs, and reclaim the Magic Stone. The tone is lighthearted with pixel-art humor, pop-culture weapon references, and comedic enemy designs.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Art style | 16-bit pixel art (approximately 16x16 pixel character sprites) |
| Native aspect ratio | 16:9 (landscape orientation on mobile) |
| Frame rate target | 60 FPS |
| Rendering | 2D sprite-based with tile-based room layouts |
| Camera | Follows player; room-locked during combat |

### Game Loop

```
1. Process input (virtual joystick position, fire button, skill button)
2. Update player movement and facing direction
3. Update weapon fire timers; spawn projectiles if firing
4. Update all projectile positions and check collisions
5. Update enemy AI (movement, attack patterns, spawning)
6. Update pet/follower AI
7. Check room clear condition (all enemies dead)
8. Update energy regeneration / armor regeneration timers
9. Check win/lose conditions
10. Render: floor tiles -> obstacles -> items -> enemies -> player -> projectiles -> particles -> UI overlay
```

### Random Number Generation

- All dungeon layouts, enemy spawns, weapon drops, and buff selections are seeded per run.
- Weapon drops use weighted RNG based on rarity tier (see Section 6).
- Boss selection per floor is random from the biome's boss pool.

---

## 3. Core Combat Mechanics

### Movement

| Property | Value |
|----------|-------|
| Default move speed | ~3.0 tiles/second (varies by character) |
| Movement control | Left virtual joystick; 360-degree analog |
| Dodge/roll | Character-specific (Rogue's Dodge skill) |
| Speed reduction when firing | 10% reduction while attack button is held |

### Attacking

- The right virtual joystick (or fire button) fires the currently equipped weapon.
- **Auto-aim**: Weapons automatically target the nearest enemy within range.
- **Melee weapons**: Swing in an arc in front of the player; block incoming projectiles during the swing animation.
- **Ranged weapons**: Fire projectiles that travel in a straight line toward the auto-aimed target, subject to weapon-specific inaccuracy.
- Players can hold **two weapons** at a time (three with the Extra Weapon buff). Tap the weapon-swap button to toggle. Picking up a third weapon drops the currently held weapon.

### Damage Calculation

```
Final Damage = Base Weapon Damage * (1 + Crit Multiplier if crit) * Buff Multipliers
Crit Multiplier = 2x base damage
Crit Chance = Weapon Crit % + Character Crit Bonus + Buff Crit Bonus
```

- **Melee weapons** have guaranteed-hit properties; projectiles cannot miss at melee range.
- **Inaccuracy** stat determines the angular spread of ranged projectiles. Lower values = more accurate.

### Room Clearing

- Entering a room with enemies locks all exits (doors close).
- All enemies in the room must be killed to unlock exits.
- Clearing a room may drop energy orbs, coins, or weapons.

---

## 4. Character System -- All Playable Heroes

There are approximately 26 core playable characters (with additional crossover/event characters bringing the total to ~41). Each character has unique base stats, a set of unlockable skills (up to 3), and a starter weapon.

### Base Stats

Stats consist of: **Health** (HP), **Armor** (regenerating shield points), **Energy** (mana for weapons), and each character has innate **Crit Chance** and **Melee Damage** values.

| Character | HP (base/max) | Armor (base/max) | Energy (base/max) | Unlock Cost | Starter Weapon |
|-----------|---------------|-------------------|--------------------|-------------|----------------|
| Knight | 7 (8) | 7 (8) | 200 (220) | Free (default) | Bad Pistol |
| Rogue | 5 (6) | 3 (4) | 180 (200) | Free | Bad Pistol |
| Wizard (Witch) | 4 (5) | 6 (7) | 260 (280) | 2,000 Gems | Staff of Thunder |
| Paladin | 1 (2) | 8 (9) | 120 (140) | 6,000 Gems | Bad Pistol |
| Assassin | 4 (5) | 4 (5) | 180 (200) | 5,000 Gems | Meat |
| Priest (Priestess) | 5 (6) | 5 (6) | 200 (220) | 4,000 Gems | Bad Pistol |
| Engineer | 4 (5) | 5 (6) | 180 (200) | 5,000 Gems | Old Pistol |
| Alchemist | 5 (6) | 5 (6) | 180 (200) | 5,000 Gems | Bad Pistol |
| Robot | 4 (5) | 7 (8) | 200 (220) | 6,000 Gems | Bad Pistol |
| Werewolf | 8 (9) | 2 (3) | 140 (160) | 4,000 Gems | Fists |
| Vampire | 4 (5) | 5 (6) | 140 (160) | 5,000 Gems | Bad Pistol |
| Elf | 3 (4) | 4 (5) | 200 (220) | 6,000 Gems | Elf's Bow |
| Necromancer | 3 (4) | 5 (6) | 240 (260) | 6,000 Gems | Soul Calibre |
| Druid | 4 (5) | 2 (3) | 160 (180) | 6,000 Gems | Bad Pistol |
| Berserker | 6 (7) | 2 (3) | 160 (180) | 6,000 Gems | Meat |
| Officer | 4 (5) | 4 (5) | 200 (220) | 8,000 Gems | Handgun |
| Taoist | 4 (5) | 5 (6) | 200 (220) | 8,000 Gems | Peachwood Sword |
| Airbender | 3 (4) | 5 (6) | 220 (240) | 8,000 Gems | Bad Pistol |
| Demonmancer | 5 (6) | 4 (5) | 180 (200) | 8,000 Gems | Bad Pistol |
| Miner | 4 (5) | 4 (5) | 160 (180) | 4,000 Gems | Pickaxe |
| Inter-dimension Traveler | 4 (5) | 5 (6) | 200 (220) | 12,000 Gems | Portal Wand |
| Trap Master | 4 (5) | 4 (5) | 180 (200) | $0.99 (IAP) | Bad Pistol |
| Element Envoy | 4 (5) | 5 (6) | 200 (220) | $1.99 (IAP) | Bad Pistol |
| Special Forces | 5 | 8 | 200 | Event/IAP | Assault Rifle |
| Physicist | 4 (5) | 4 (5) | 180 (200) | 8,000 Gems | Bad Pistol |

> **Note**: Values in parentheses are upgraded stats (typically achieved at character upgrade level 1-2). Further upgrades at levels 3-8 add energy, skill cooldown reductions, passive buffs, and weapon upgrades.

### Character Upgrade Progression

| Star Level | Bonus |
|------------|-------|
| 1-2 | +1 Health and/or +1 Armor |
| 3 | +20 Energy |
| 4 | Skill cooldown reduced by 2 seconds |
| 5 | Skill upgrade (affects all skill variants) |
| 6 | Permanent passive buff unique to character |
| 7 | Starter weapon upgraded |
| 8 | Unlocks Summoner's Artifact development |

---

## 5. Skill System

Each character has up to 3 skill variants (Skill 1 unlocked by default; Skills 2 and 3 unlocked via gameplay or upgrade). Skills consume a cooldown timer and sometimes energy.

### Core Character Skills

| Character | Skill 1 | Skill 2 | Skill 3 |
|-----------|---------|---------|---------|
| Knight | **Dual Wield** -- Wield all held weapons simultaneously for 5 sec; +3 energy/0.5s; kills extend duration by 0.5s | **Superior Fire** -- Increases fire rate and damage temporarily | **Chaotic Strike** -- Attacks inflict random debuffs |
| Rogue | **Dodge** -- Short dash forward with invincibility frames | **Iaido** -- Quick-draw slash dealing heavy damage | **Cartwheel** -- Longer dodge with area-of-effect damage |
| Wizard (Witch) | **Piercing Frost** -- Fires piercing ice projectiles that freeze enemies | **Firestorm** -- Summons fire pillars that rain down | **Electric Zone** -- Creates an electrified area damaging enemies within |
| Paladin | **Energy Shield** -- Creates invincible barrier for 5 sec; damage taken is converted to energy | **Holy Warrior** -- Temporary melee damage boost with divine strikes | **Splash Bash** -- Ground-slam area attack |
| Assassin | **Dark Blade** -- Teleports to nearest enemy and delivers a critical strike | **Doppelganger** -- Creates a shadow clone that attacks | **Invisibility** -- Become invisible; next attack is guaranteed critical |
| Priest | **Regeneration Pact** -- Healing circle: restores 2 HP x3 (self) and 5 HP x3 (allies) | **Pray** -- Summons divine lightning on enemies in area | **Resurrection** -- Revive fallen allies or self with reduced HP |
| Engineer | **Armor Mount** -- Equips a mounted turret/vehicle that provides extra HP and firepower | **Gun Turret** -- Deploys a stationary turret that auto-attacks enemies | **Interceptor** -- Deploys a laser turret that intercepts enemy bullets |
| Alchemist | **Elemental Potions** -- Throws potions creating fire, ice, or poison AoE zones | **Plague Doctor** -- Sprays toxic mist in a cone | **Alchemical Disaster** -- Massive explosion combining all elements |
| Robot | **Fire Mode** -- Converts all current energy into a powerful laser beam (damage scales with energy spent) | **Drone Swarm** -- Deploys multiple attack drones | **EMP** -- Electromagnetic pulse stuns all enemies and disables bullets |
| Werewolf | **Werewolf Rush** -- Charges forward dealing melee damage to all enemies in path | **Roar** -- AoE damage and knockback around character | **Bloodthirst** -- Killing enemies restores HP during skill duration |
| Vampire | **Bat Swarm** -- Releases bats attacking enemies; restores HP, energy, and armor on kills | **Blood Pact** -- Drains life from enemies in area | **Alien Swirl** -- Summons a vortex pulling enemies inward |
| Elf | **Guardian Elf** -- Summons elemental elf companion (Fire, Wind, or Water) that fights alongside | **Arrow Rain** -- Fires a volley of arrows into the sky that rain down on enemies | **Nature's Call** -- Summons vines that trap and damage enemies |
| Necromancer | **Nightmare** -- Summons dark spirits that home in on enemies | **Omen Stone** -- Places a cursed stone that pulses damage | **Souls Resurrect** -- Defeated enemies rise as allied undead |
| Druid | **Wolf Companion** -- Summons wolves; casting skill imbues wolves with elemental power, increasing size and restoring their HP | **Vine Whip** -- Summons grasping vines | **Nature Fury** -- Transforms into a powerful beast form |
| Berserker | **Berserk** -- Temporarily increases attack speed and damage; reduces defense | **Axe Throw** -- Throws a spinning axe that pierces enemies | **Ground Pound** -- Leaps and slams the ground for AoE damage |
| Taoist | **Sword Formation** -- Summons 7 swords that orbit the player, destroying enemy bullets; when skill ends, swords fly at enemies (prioritizing marked targets) | **Lightning Strike** -- Calls down lightning on enemies | **Spirit Seal** -- Places talismans that explode when enemies approach |

### Skill Cooldowns

| Typical Cooldown Range | Notes |
|------------------------|-------|
| 5 -- 12 seconds base | Varies per skill and character |
| -2 seconds at Star Level 4 | Applies to all skills for that character |
| Buff-reducible | "Reduce skill cooldown" buff further lowers timer |

---

## 6. Weapon System

### Weapon Count & Categories

There are **500+ weapons** across **18 categories**:

| Category | Description | Typical Energy Cost | Example |
|----------|-------------|---------------------|---------|
| Handguns/Pistols | Single-shot sidearms; low damage, low energy cost | 0--2 | Bad Pistol, New Pistol |
| Assault Rifles | Automatic fire; moderate damage | 2--4 | M4 Assault Rifle, Pro Assault Rifle |
| SMGs (Sub-Machine Guns) | Very high fire rate; low per-shot damage | 1--2 | Next-gen SMG, Uzi |
| Shotguns | Multiple projectiles per shot; short range | 3--6 | Double Barrel, Judge |
| Sniper Rifles | Very high damage; slow fire rate; high crit chance | 4--8 | AWP, Crosshair |
| Rifles | Semi-automatic; balanced stats | 2--4 | AK47, RPG |
| Laser Guns | Continuous beam or burst-fire energy bolts | 3--7 | Laser Therapy, Electrical Therapy |
| Railguns | Charged shots that penetrate and explode; hold to charge | 5--10 | Rail Gun, Thunder Rail |
| Bows | Charged ranged; moderate damage; low energy cost | 1--4 | Hero's Bow, Fire Bow, Ice Bow |
| Crossbows | Similar to bows but faster; lower charge time | 1--3 | Crossbow, Crossbow Plus |
| Staffs/Wands | Magic projectiles; often AoE or elemental | 3--6 | Staff of Thunder, Staff of Incantation, Magic Staff |
| Melee Weapons | Swords, hammers, fists; no energy cost for most; block projectiles | 0--2 | Meat, Nunchaku, Knight's Fist, Thunder Sword |
| Throwing Weapons | Thrown projectiles; moderate damage | 1--3 | Ninja Stars, Boomerang |
| Explosives | Grenades, rockets; AoE damage | 3--8 | Grenade, Missile Battery |
| Boss Weapons | Dropped by specific bosses; unique mechanics | Varies | Varkolyn Assault Rifle, Zulan Staff |
| Mergeable Weapons | Created by combining specific weapons during a run | N/A | See Section 7 |
| Rings | Passive effect items worn in weapon slot | 0 | Jade Ring (energy regen) |
| Mythical Weapons | Rarest tier; three built-in abilities; no attachments | Varies | Caliburn, Rainbow Gatling |

### Weapon Rarity Tiers

| Rarity | Name Color | Drop Weight | Typical Damage Range | Notes |
|--------|------------|-------------|----------------------|-------|
| Common | White | ~40% | 2--6 | Found everywhere; weakest |
| Uncommon | Green | ~25% | 5--10 | Found in chests, shops |
| Rare | Blue | ~18% | 8--15 | Found in blue/golden chests |
| Very Rare | Purple | ~10% | 12--20 | Found in golden chests, bosses |
| Epic | Orange | ~5% | 16--30 | Rare boss/chest drops |
| Legendary | Red | ~1.5% | 25--50+ | Always has a special ability; cannot have attachments |
| Mythical | Magenta | ~0.5% | 40--80+ | Up to 3 built-in abilities; cannot have attachments |

### Weapon Stat Fields

Every weapon has the following stats displayed in its tooltip:

| Stat | Description | Display |
|------|-------------|---------|
| Damage | Base damage per hit / per projectile | Integer (e.g., 8) |
| Energy Cost | Energy consumed per shot / swing | Integer (e.g., 4) |
| Crit Chance | Probability of dealing 2x damage | Percentage (e.g., 10%) |
| Inaccuracy | Angular spread of projectiles (lower = more accurate) | Integer (0 = perfect aim) |
| Fire Rate | Shots per second | Implicit via fire interval |

### Example Weapons

| Weapon | Category | Rarity | Damage | Energy | Crit% | Inaccuracy | Special |
|--------|----------|--------|--------|--------|-------|------------|---------|
| Bad Pistol | Pistol | White | 3 | 0 | 0% | 2 | Default starter; no energy cost |
| Staff of Thunder | Staff | Purple | 6 x13 | 4 | 0% | N/A | 13 bouncing electric projectiles in all directions; bounce 3 times off walls |
| AWP | Sniper | Blue | 24 | 6 | 40% | 0 | Single-shot; high crit |
| Double Barrel | Shotgun | Green | 4 x8 | 4 | 5% | 12 | Fires 8 pellets in wide spread |
| Knight's Fist | Melee | Green | 8 | 0 | 10% | N/A | Punch combo; blocks bullets |
| Caliburn | Melee | Mythical | 12 | 0 | 50% | N/A | Legendary sword; built-in abilities |
| Jade Ring | Ring | Green | 0 | 0 | 0% | N/A | Restores 1 energy per second passively |
| Missile Battery | Explosive | Orange | 16 x4 | 8 | 0% | 5 | Fires 4 homing missiles |
| Fire Bow | Bow | Green | 7 | 2 | 5% | 1 | Arrows inflict Burn |
| Ice Bow | Bow | Green | 6 | 2 | 5% | 1 | Arrows inflict Freeze |
| Laser Therapy | Laser | Blue | 2/tick | 5 | 0% | 0 | Continuous beam; heals allies on hit |
| Meat | Melee | White | 5 | 0 | 0% | N/A | Starter melee; restores 1 HP on kill |

---

## 7. Weapon Attachments & Merging

### Attachments

Attachments are modifiers that can be applied to non-Red/non-Mythical weapons. They are obtained from the Weaponsmith NPC or Engineer's starting ability. One attachment per weapon.

| Attachment | Effect |
|------------|--------|
| Shotgun Buff | Increases pellet count of shotguns |
| Bounce | Projectiles bounce off walls once |
| Laser Buff | Increases beam width by 200% for optoelectronic weapons |
| Energy Stone | 33% chance to restore 2 Energy per shot |
| Upgrade Kit | +50% damage; changes weapon rarity up one tier |
| Scope | Reduces inaccuracy to 0 |
| Crit Buff | +10% crit chance |
| Penetration | Projectiles pierce through one additional enemy |

### Weapon Merging

During a run, two (or more) specific weapons can be merged by placing one on the ground and holding the other. A merge icon appears if the combination is valid.

| Components | Result | Rarity |
|------------|--------|--------|
| Frost Sword + Fire Sword | Thunder Sword | Red |
| Green Lightsaber + Red Lightsaber + Blue Lightsaber | Golden Lightsaber | Red |
| Fire Bow + Ice Bow + Jade Bow | Star Bow | Red |
| Next-gen SMG + Next-gen SMG | Next-Next-gen SMG | Blue |
| Next-Next-gen SMG + Next-Next-gen SMG | Next-Next-Next-gen SMG | Purple |
| Bad Pistol x4 | Fantastic Gun | Red |
| Knight's Fist + Staff of Thunder | Fist of Heaven | Red |
| Reusable Life Potion + Reusable Energy Potion | Reusable Restoration Potion | Orange |
| Furnace + Glacier | Aurora | Red |
| Crossbow + Crossbow | Crossbow Plus | Blue |
| Bow + Bow | Bow Plus | Blue |
| Hero's Bow + Wind Force | Magic Bow | Red |
| Electrical Therapy + Laser Therapy | Dual Therapy | Red |
| Red Laser Sword + Blue Laser Sword | Purple Laser Sword | Orange |
| Broken Hilt + Damaged Blade | Reforged Sacred Sword | Red |
| Frost Eagle + Flame Eagle | Ice and Fire Eagle | Orange |
| Butcher Knife + Old Rifle | Bayonet Rifle | Blue |
| Bazooka + Glacier | Ice Bazooka | Orange |

---

## 8. Dungeon Generation & Floor Structure

### Overall Structure

| Property | Value |
|----------|-------|
| Total Floors | 3 main floors (+ optional 4th) |
| Levels per Floor | 5 (labeled x-1 through x-5) |
| Total Levels (standard run) | 15 (1-1 through 3-5) |
| Boss Level | x-5 on each floor (boss room) |
| Portal/Transition | After boss defeat, portal to next floor or ending |
| Optional 4th Floor | Monolithic Range Ruins (accessed via special portal) |

### Biomes per Floor

| Floor | Biome Options | Theme |
|-------|--------------|-------|
| Floor 1 | Forest, Glacier, Relics (Temple), Mechanical Ruins | Nature/Ancient |
| Floor 2 | Knight Kingdom, Dungeon, Halloween, Chiseltown | Medieval/Spooky |
| Floor 2 (Hidden) | Swamp, Cave, Grave | Accessed via special conditions |
| Floor 3 | Spaceship, Volcano, Neo Isle | Sci-fi/Volcanic |
| Floor 4 (Optional) | Monolithic Range Ruins | Endgame |

The biome for each floor is selected randomly at the start of the run. Each biome determines the tileset, enemy types, and boss pool.

### Room Layout Per Level

Each level (e.g., 1-3) consists of a connected graph of rooms:

| Room Type | Count Per Level | Description |
|-----------|----------------|-------------|
| Starting Room | 1 | Player spawns here; may contain a weapon chest |
| Enemy Rooms | 2--5 | Contain enemy waves; must be cleared |
| Chest Room | 0--1 | Contains a weapon chest (Golden Box icon on minimap) |
| Crystal Mine Room | 0--1 | Contains Crystal Mine (yellow ! on minimap); 40 HP; drops 10 energy orbs |
| Shop Room | 0--1 | NPC merchant selling weapons, health potions, energy potions for gold |
| Special Room | 0--1 | May contain Chester, Mysterious Trader, Turret Room, Wishing Well, or NPC |
| Secret Room | 0--1 | Hidden; requires specific actions to access (e.g., bombing a wall) |
| Portal Room | 1 | Exit to next level; unlocked when all mandatory rooms are cleared |
| Boss Room (x-5 only) | 1 | Red-visor helmet icon; contains floor boss; replaces portal room |

### Room Generation Rules

1. Rooms are arranged in a branching graph with corridors connecting them.
2. The minimum path from start to portal always passes through at least 2 enemy rooms.
3. Non-mandatory side rooms (0--3 per level) branch off the main path.
4. There can never be more than one Golden Box room per level.
5. Boss levels (x-5) always end with the boss room as the final room.
6. After defeating the boss, a Golden Chest spawns containing a high-rarity weapon.

### Buff Selection Between Floors

After completing Floor x-5 (boss floor), the player enters a transition room and is offered a **buff selection screen** (see Section 13).

---

## 9. Enemy Types per Biome

Enemies are categorized by rarity (mirroring weapon tiers): **White** (weakest), **Green** (uncommon), **Blue** (powerful), **Purple** (dangerous), **Orange** (elite/mini-boss threats).

### Floor 1 Enemies

#### Forest

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Goblin | Melee rush | 8 | 1 | Basic melee |
| Goblin Guard | Melee; shields front | 15 | 2 | Block frontal attacks |
| Goblin Archer | Ranged; fires arrows | 8 | 2 | Stationary; aims at player |
| Goblin Shaman | Ranged; fires 3 splitting bullets | 12 | 2 | Bullets split into 3 more |
| Elite Goblin | Melee rush; fast | 20 | 3 | Green rarity |
| Large Goblin | Ranged barrage | 30 | 3 | Fires in cross/diagonal patterns |
| Mushroom | Stationary; releases spore clouds | 10 | 1 | Poison AoE on death |
| Tentacle Plant | Spawns when enemies die | 6 | 1 | Replaces slain enemies in later levels |

#### Glacier

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Ice Goblin | Melee; frost attacks | 10 | 2 | Attacks inflict Freeze |
| Ice Archer | Ranged; frost arrows | 10 | 2 | Arrows slow/freeze player |
| Snow Bat | Flying; dive attack | 8 | 2 | Fast; erratic movement |
| Ice Slime | Bouncing; contact damage | 6 | 1 | Splits into 2 smaller slimes on death |
| Yeti | Melee charge | 25 | 4 | Charges in straight line |

#### Relics (Temple)

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Skeleton Warrior | Melee | 12 | 2 | Reassembles once after death |
| Skeleton Archer | Ranged; bone arrows | 10 | 2 | |
| Mummy | Slow melee; high HP | 30 | 3 | Poison on contact |
| Stone Golem | Melee; very slow | 40 | 5 | High defense; resists knockback |
| Scarab | Fast melee swarm | 4 | 1 | Spawns in groups of 4--6 |

#### Mechanical Ruins

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Robot Drone | Flying; laser burst | 10 | 2 | |
| Turret | Stationary; rapid fire | 15 | 2 | Cannot move; 360-degree aim |
| Mech Walker | Melee; armored | 25 | 3 | Reduced damage from ranged attacks |

### Floor 2 Enemies

#### Knight Kingdom

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Knight Soldier | Melee with shield | 20 | 3 | Blocks frontal projectiles |
| Knight Archer | Ranged crossbow | 15 | 3 | |
| Knight Mage | Ranged magic; fire/ice | 15 | 4 | Elemental attacks |
| Armored Knight | Heavy melee; high HP | 35 | 4 | Very slow; charges occasionally |
| Slime (various colors) | Bouncing contact | 8--15 | 1--3 | Splits on death |

#### Dungeon

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Dungeon Bat | Flying swarm | 6 | 1 | Very fast; erratic |
| Dungeon Skeleton | Melee; bone throw | 15 | 3 | Throws bones at range |
| Dungeon Mage | Ranged dark magic | 18 | 4 | Homing projectiles |
| Spike Trap | Stationary hazard | N/A | 2 | Environmental damage |
| Mimic (Chester) | Disguised as chest; leaps when approached | 25 | 4 | Surprise attack |

#### Halloween

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Phantom | Invisible; random drift | 15 | 3 | Becomes visible when attacking |
| Pumpkin Head | Melee; explodes on death | 12 | 2 + 4 (explosion) | |
| Witch | Ranged; summons minions | 20 | 3 | Spawns 2 bats every 5 seconds |
| Zombie | Slow melee | 18 | 3 | Can be poisoned from own attacks |

### Floor 3 Enemies

#### Spaceship

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Varkolyn Soldier | Ranged plasma shots | 20 | 4 | Alien infantry |
| Varkolyn Shieldbearer | Melee with energy shield | 30 | 4 | Shield absorbs 15 damage |
| Varkolyn Sniper | Long-range laser | 15 | 6 | High damage; slow fire rate |
| Alien Spawn Pod | Spawns smaller aliens | 25 | 0 | Produces 1 alien every 3 seconds |
| Alien Drone | Flying; kamikaze | 8 | 5 | Explodes on contact |

#### Volcano

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Fire Goblin | Melee; fire damage | 20 | 3 | Leaves fire trail |
| Lava Slime | Bouncing; fire contact | 15 | 3 | Inflicts Burn |
| Fire Mage | Ranged fire magic | 20 | 5 | Fireball AoE |
| Magma Golem | Slow melee; heavy | 45 | 6 | Splits into 2 small golems on death |
| Dragon Whelp | Flying; fire breath | 25 | 4 | Cone fire attack |

#### Neo Isle

| Enemy | Behavior | HP | Damage | Notes |
|-------|----------|----|----|-------|
| Cyber Soldier | Ranged pulse rifle | 22 | 4 | |
| Mech Guardian | Melee; electrified | 35 | 5 | Electrify on contact |
| Drone Carrier | Spawns drones | 30 | 0 | Produces 2 drones every 4 seconds |

### Champion Enemies

Any enemy can appear as a **Champion** variant (indicated by a golden aura):
- HP: 2x normal
- Damage: 1.5x normal
- May gain new attack patterns
- More likely in later floors and on Badass Mode

---

## 10. Boss Encounters

Bosses appear on level x-5 of each floor. Each biome has a pool of 3--4 possible bosses, one of which is randomly selected.

### Universal Boss Mechanics

- Bosses have a health bar displayed at the top of the screen.
- At **50% HP**, bosses enter **Enraged Mode**: attacks become faster, more aggressive, and may gain new attack patterns.
- Upon death, bosses drop: large amount of gold, materials, energy orbs, and sometimes a unique weapon.
- A **Golden Chest** spawns after boss death containing a weapon of Blue rarity or higher.

### Floor 1 Bosses

| Boss | Biome(s) | HP (Normal/Badass) | Key Attacks | Enraged Behavior |
|------|----------|---------------------|-------------|------------------|
| **Grand Slime** | Knight Kingdom, Forest | 400 / 500 | Bounces around room; spawns mini-slimes; slime rain attack from above | Faster bouncing; more mini-slimes |
| **Baby Dragon Bros** | Volcano, Forest | 350+350 / 440+440 | Dual boss (red and blue dragon); fire/ice breath; bullet floods; simultaneous laser beams | Both dragons attack simultaneously; screen-filling fire + ice patterns |
| **King Snow Ape** | Glacier | 500 / 625 | Ground pound shockwaves; throws ice boulders; charge attack | Faster charges; triple shockwave |
| **Nian** | Relics | 450 / 560 | Rush attack; fireball barrage; summons minions | Faster rushes; double fireball rate |
| **Easter Bunny** | Forest, Relics | 400 / 500 | Egg bombs (poison, fire, freeze variants); hop attack; summons rabbit minions | More egg types; faster spawning |

### Floor 2 Bosses

| Boss | Biome(s) | HP (Normal/Badass) | Key Attacks | Enraged Behavior |
|------|----------|---------------------|-------------|------------------|
| **Skeleton King** | Dungeon, Halloween | 600 / 750 | Summons skeleton army; bone tornado; dark energy beam; ground eruption | Triple summon rate; beam becomes sweeping |
| **Gold Mask** | Relics, Knight Kingdom | 550 / 690 | Fires golden rings; teleportation; ground slam creating gold shockwave | Faster teleporting; ring patterns more dense |
| **Phantom King** | Halloween, Dungeon | 500 / 625 | Disappears (invincible while invisible); spawns phantom minions; dark slash attack | Longer invisibility; more phantoms |
| **C6H8O6** | Chiseltown | 600 / 750 | Acid spray in patterns; bouncing chemical projectiles; toxic cloud AoE | Spray covers wider area; clouds linger longer |
| **Giant Crystal Crab** | Cave | 700 / 875 | Claw swipes; crystal barrage; burrow + emerge attack; can regenerate HP in enraged phase | Crystal attacks from below; HP regeneration at 25% HP |

### Floor 3 Bosses

| Boss | Biome(s) | HP (Normal/Badass) | Key Attacks | Enraged Behavior |
|------|----------|---------------------|-------------|------------------|
| **Varkolyn Leader** | Spaceship | 800 / 1000 | Plasma burst patterns; summons Varkolyn soldiers; shield phase (invulnerable until minions killed); orbital laser | Shield recharges faster; summons Champions |
| **Zulan the Colossus** | Spaceship | 1000 / 1250 | Multi-directional laser beams; bullet hell spiral patterns; EMP pulse; spawns drones | Continuous laser rotation; triple drone spawn |
| **Floating Laser UFO** | Spaceship, Neo Isle | 800 / 1000 | Laser grid pattern; tracking missiles; tractor beam (pulls player); rapid-fire plasma | Laser grid rotates; missiles become homing |
| **Volcanic Sandworm** | Volcano | 900 / 1125 | Burrows underground; emerges for bite attack; fires magma projectiles; tail swipe | Faster burrow/emerge cycle; magma rain |
| **Prehistoric Colossus** | Volcano | 1000 / 1250 | Stone fist slam; boulder throw; ground tremor (full-room shockwave); summons rock minions | Can regenerate HP; double slam speed |
| **Grand Knight** | Knight Kingdom | 800 / 1000 | Sword combo attacks; shield charge; summons knight soldiers; spinning blade throw | Faster combos; shield becomes projectile-reflecting |
| **Dark Grand Knight** | Dungeon | 900 / 1125 | Similar to Grand Knight but with dark energy; teleportation slash; dark energy eruption | Dark AoE expands; teleport combo chains |
| **Anubis** | Relics | 850 / 1060 | Summons mummy minions; sandstorm (obscures vision); scepter beam; curse (drains energy); can regenerate HP in enraged phase | Curse lasts longer; sandstorm permanent |

### Boss Drops

| Drop Type | Details |
|-----------|---------|
| Gold | 50--150 coins |
| Materials | 2--5 random materials |
| Energy Orbs | 10--20 energy restoration |
| Unique Weapon (rare) | Boss-specific weapon (~15% chance) |
| Character Fragments | Specific skin/unlock fragments |
| Golden Chest | Always spawns; contains Blue+ rarity weapon |

---

## 11. Energy & Mana System

### Energy Properties

| Property | Value |
|----------|-------|
| Max Energy | Character-dependent (120--280 base) |
| Energy Bar Location | Top-left of screen (blue bar) |
| Energy per weapon shot | Weapon-specific (0--10; shown on tooltip) |
| Energy from Crystal Mine | 10 orbs (1 energy each) from normal mine |
| Energy from enemy drops | Random; ~1--2 orbs per enemy kill |
| Energy from boss drops | 10--20 orbs |
| Passive regeneration | None by default |
| Energy potion | Restores 50 energy; found in shops/chests |
| Restoration potion | Restores both HP and Energy |

### Energy Sources During a Run

| Source | Energy Restored | Availability |
|--------|----------------|--------------|
| Energy Orbs (enemy drops) | 1 per orb | Random on enemy kill |
| Crystal Mine | 10 total | 0--1 per level |
| Energy Potion (shop) | 50 | Costs 10--15 gold |
| Restoration Potion (shop) | 25 energy + 1 HP | Costs 15--20 gold |
| Vending Machine | 50 energy | 0--1 per level; costs gold or free (ad) |
| Jade Ring (weapon) | 1/second passive | Must equip as weapon |
| Energy Stone (attachment) | 33% chance of +2 per shot | Attached to weapon |
| Dual Wield (Knight skill) | +3 per 0.5 seconds during skill | Knight only |
| Robot Fire Mode | Converts energy to damage | Spends energy |

### Running Out of Energy

When energy reaches 0, all weapons that cost energy become unusable. The player must rely on:
- Free weapons (Bad Pistol, melee weapons with 0 energy cost)
- Energy pickups from killing enemies
- Waiting for room-clear energy drops

---

## 12. Shield, Armor & HP Mechanics

### Health (HP)

| Property | Value |
|----------|-------|
| Display | Red hearts at top-left; each heart = 1 HP |
| Starting HP | Character-dependent (1--8) |
| Maximum HP | Base + upgrades + buffs (typically 2--12) |
| Regeneration | None by default; only via Priest skill, potions, or specific buffs |
| HP Potion | Restores 1 HP; found in shops for 5--10 gold |
| Losing all HP | Character dies; run ends (unless revive available) |

### Armor (Shield Points)

| Property | Value |
|----------|-------|
| Display | Gray shield icons at top-left; each icon = 1 armor point |
| Starting Armor | Character-dependent (2--9) |
| Regeneration | Automatically regenerates 1 point every ~3 seconds after not taking damage for ~5 seconds |
| Damage Priority | Armor absorbs damage first; when armor = 0, HP takes damage |
| Extra Damage | When armor is 0, incoming hits deal +1 bonus damage (mitigated by "No extra damage when shield is down" buff) |
| Full Armor Bonus | When armor is completely full, some weapons gain guaranteed critical hit (character-specific) |

### Damage Flow

```
Incoming Attack (X damage):
  1. If Armor > 0:
     -> Armor -= X (minimum 0)
     -> Remaining damage (if X > current Armor) dealt to HP
  2. If Armor = 0:
     -> HP -= (X + 1)  [extra damage penalty]
     -> Unless "No Extra Damage" buff is active, then HP -= X
  3. If HP <= 0:
     -> Character dies
     -> Check for revival mechanics (Necromancer skill, consumable, etc.)
```

### Armor Regeneration Timer

```
On taking damage:
  -> Reset regen timer to 5 seconds
  -> Armor does NOT regenerate while timer is active

After 5 seconds of no damage:
  -> Regenerate 1 armor point every 3 seconds
  -> Continue until armor is full or player takes damage again
```

---

## 13. Buff System

### Buff Acquisition

Buffs are selected between floors (after completing x-5 boss levels) and occasionally from special rooms.

| Source | Frequency | Selection |
|--------|-----------|-----------|
| Post-boss selection screen | After each floor (3 per run) | Choose 1 of 3 random buffs |
| Trader NPC | Random in dungeon rooms | Purchase for gold |
| Mysterious Trader | Random; rare spawn | Special buff for gold |
| Fantastic Flower (garden) | Pre-run garden harvest | Single specific buff |
| Legendary Buff Room (secret) | Rare secret room | Choose 1 of 3 legendary buffs (with penalty) |

### Buff Slots

| Mode | Max Buff Slots |
|------|----------------|
| Level Mode | 7 |
| Boss Rush | 7 |
| Matrix Mode | 38 |
| The Origin | 10 |

Once a buff is chosen, it will **not appear again** in future buff selections during the same run.

### Common Buffs

| Buff Name | Effect | Category |
|-----------|--------|----------|
| Extra HP | +1 maximum HP | Defensive |
| Extra Shield | +1 maximum armor | Defensive |
| No Extra Damage When Shield Down | Removes +1 damage penalty when armor = 0 | Defensive |
| Fire Rate Up | +10% weapon fire rate (applies to all weapons including charged ones) | Offensive |
| Accuracy Up | Reduces weapon inaccuracy | Offensive |
| Shotgun Buff | Increases pellet count for shotguns | Offensive |
| Melee Damage Up | +2 melee weapon damage | Offensive |
| Crit Chance Up | +10% critical hit chance | Offensive |
| Energy Regen | Slowly regenerate energy over time | Utility |
| Cooldown Reduction | Skill cooldown reduced by 20% | Utility |
| Extra Weapon Slot | Can hold 3 weapons instead of 2 | Utility |
| Berserker (Buff) | Damage increases as HP decreases | Offensive |
| Bounce | Projectiles bounce off walls once | Offensive |
| Pierce | Projectiles penetrate through 1 additional enemy | Offensive |
| Poison Bullet | 15% chance for attacks to inflict Poison | Offensive |
| Fire Bullet | 15% chance for attacks to inflict Burn | Offensive |
| Freeze Bullet | 15% chance for attacks to inflict Freeze | Offensive |
| Laser Buff | +200% beam width for laser/optoelectronic weapons; immunity to electro damage | Offensive |
| Speed Up | +20% movement speed | Utility |
| Gold Increase | +50% gold from enemies | Economy |
| Attract | Items automatically pulled toward player at greater range | Utility |
| Combo Buff | Damage increases with consecutive hits (resets if player stops attacking for 2 sec) | Offensive |
| Skill Damage Up | Each skill use increases next skill damage by 10% (stacking) | Offensive |
| Revive | Upon death, revive once with 1 HP | Defensive |

### Special Buffs

Special buffs are acquired through unique means and share effects with all multiplayer teammates:

| Buff | Source | Effect |
|------|--------|--------|
| Statue of the Knight | Coin offering at Knight statue | +20% melee damage for 3 rooms |
| Statue of the Sorcerer | Coin offering at Sorcerer statue | +20% energy efficiency for 3 rooms |
| Statue of the Paladin | Coin offering at Paladin statue | +2 temporary armor for 3 rooms |
| Statue of the Berserker | Coin offering at Berserker statue | +30% damage at cost of -1 armor for 3 rooms |

### Unique Buffs (Character Passives)

Each character at Star Level 6 gains a permanent passive buff that only affects them (not shared in multiplayer).

---

## 14. Status Effects & Elemental Damage

### Status Effects

| Effect | On Player | On Enemy | Duration |
|--------|-----------|----------|----------|
| **Burn** | Disabled in recent updates | +3 damage per hit | 2.5 seconds |
| **Poison** | 1 damage/sec (2 in Badass) | +3 damage per hit; zaps 2 nearby enemies | 2.5 seconds |
| **Freeze** | Movement and attacking locked; skill cooldown paused; immune to hazards | Movement and attacking locked; still takes damage | 2.0 seconds (player) / 2.8 seconds (enemy) |
| **Electrify** | Movement briefly stunned | +3 damage per hit; zaps 2 nearby enemies | 2.0 seconds |
| **Dark** | Reduced vision radius | Takes increased damage | 3.0 seconds |

### Elemental Interactions

| Combination | Result |
|-------------|--------|
| Fire + Poison on same enemy | Explosion dealing 8 damage + Burn |
| Freeze + Electrify on same enemy | Shatter dealing 10 damage |
| All three (Fire + Ice + Electric) | Massive AoE explosion |

---

## 15. Garden & Base Mechanics

### Living Room (Main Lobby)

The Living Room is the hub area containing:

| Feature | Location | Function |
|---------|----------|----------|
| Character Selection | Center | Choose hero; view/upgrade characters |
| Pet Display | Follows player | Current active pet; feed/swap pets |
| Gashapon Machine | Right side | Spend gems for random rewards (weapons, seeds, blueprints, gems) |
| Beverage Vending Machine | Near entrance | Provides temporary buff for a run (costs gold or watching an ad) |
| Fish Tank | Interior | Decorative; may contain hidden rewards |
| Living Room Chest | Center-left | Daily reward chest |
| Weapon Display | Various | Equipped weapons and starter weapon |
| Door to Garden | Left exit | Leads to Garden area |
| Door to Workshop | Right exit | Leads to Workshop |
| Door to Cellar | Lower-left | Leads to collection/display area |
| Door to Magic Area | Bottom exit | Leads to special challenge areas |
| Dungeon Entrance | Top | Start a run |

### Garden

The Garden is unlocked after playing 3 times in Level Mode. It contains plant plots that the player can sow seeds into and water.

#### Resource Plants

| Plant | Growth Time | Harvest Type | Output |
|-------|-------------|-------------|--------|
| Gem Flower | 1 day | Single use | 288 Gems |
| Gear Flower | 1 day | Single use | 3 Parts |
| Ironwood | 1 day | Single use | 3 Ironstone |
| Trumpet Flower | 1 day | Single use | 4 Organic Matter |
| Oak Tree | 3 days | Single use | 10 Timber |
| Gem Tree | 4 days | Renewable (daily) | 222 Gems |

#### Weapon Plants

| Plant | Growth Time | Harvest Type | Weapon |
|-------|-------------|-------------|--------|
| Carrot | 1 day | Single use | Melee weapon; deflects enemy shots |
| Green Onions | 1 day | Single use | Dual ranged/melee capability |
| Vine | 2 days | Single use | Swinging melee; poison on crit |
| Bamboo | 3 days | Renewable (daily) | Throwable + melee thrust |

#### Buff Plants

| Plant | Growth Time | Harvest Type | Effect |
|-------|-------------|-------------|--------|
| Mandrake | 2 days | Renewable (daily) | Poison immunity buff |
| Caterpillar Fungus | 3 days | Renewable (daily) | +1 max HP buff |
| Crystal Mushroom | 2 days | Renewable (daily) | Enhanced gem drops per run |
| Heptacolour Viola | 1 day | Single use | +1 buff slot (stackable) |
| Dragon Fruit Tree | 4 days | Renewable (daily) | Fire resistance buff |
| Cactus | 3 days | Renewable (daily) | Trap resistance buff |
| Magic Flower | 3 days | Renewable (daily) | Energy gain on monster kill |

#### Pet Plants

| Plant | Growth Time | Harvest Type | Pet |
|-------|-------------|-------------|-----|
| Devil's Snare | 7 days | Renewable (daily) | Shoots 3 poisonous projectiles in cone |
| Titan Arum | 1 day | Single use (plant dies) | Melee pet dealing 5 damage per bite |

#### Garden Mechanics

- **Watering**: Each plant must be watered once daily. Missing a day does not kill the plant but delays growth.
- **Seeds**: Obtained from Gashapon Machine, enemy drops, boss drops, or the shop.
- **Plot Slots**: Initially 4 plots; expandable through upgrades.
- **Harvesting**: Tap the mature plant to collect its yield.

### Cellar

The Cellar is unlocked after playing Level Mode 6 times. Located to the left of the Living Room.

| Floor | Contents |
|-------|----------|
| Floor 1 | Weapon collection display; shows all weapons ever obtained |
| Floor 2 | Enemy/boss bestiary; NPC collection |
| Floor 3 | Achievement displays; plant effects reference |

---

## 16. Pet System

### Pet Properties

| Property | Value |
|----------|-------|
| Total Pets | 35+ |
| Base HP (all pets) | 5 |
| Base Damage (all pets) | 3 |
| Death behavior | Pets do not permanently die; become inactive for 30 seconds when HP depleted |
| Healing | Priest's skill can heal pets; pet food upgrades add +2 damage and +10 HP |
| Active pets per run | 1 |

### Affinity System

Every pet has an **Affinity** stat that increases by feeding the pet in the Living Room.

| Affinity Milestone | Reward |
|--------------------|----|
| 50% (120 points for standard pets) | Signature animation unlocked |
| 100% (240 points for standard pets) | Pet skill unlocked |

Exceptions:
- **Pepper**: Max affinity 300 points
- **Purpur** and **Pochi**: Max affinity 180 points

### Pet List

| Pet | Unlock Method | Ability (at 100% affinity) |
|-----|--------------|---------------------------|
| Chilly (Cat) | Default (free) | Freezes nearby enemies periodically |
| Dog | 1,000 Gems | Fetches dropped items; brings coins to player |
| Pig | 1,000 Gems | Occasionally drops health orbs |
| Slime | 1,000 Gems | Bounces into enemies dealing contact damage |
| Robot | 1,000 Gems | Fires weak laser beams at enemies |
| Rabbit | 1,000 Gems | Increases player speed slightly |
| Can-bellied Pig | 1,000 Gems | Drops energy orbs occasionally |
| Pigeon | 6,666 Gems | Drops bombs on enemies from above |
| Panda | Premium (IAP) | Rolls into enemies; stuns on contact |
| Owl | Achievement unlock | Reveals secret rooms on minimap |
| Inherited Bug | Family Treasure achievement | Burrows and attacks enemies from below |
| Wayne (Bat) | Feed Vampire's weapon to Halloween bat 3 times | Lifesteal attacks; restores player HP on kill |
| Devil's Snare | Garden (7-day plant) | 3-way poisonous projectile cone |
| Titan Arum | Garden (1-day plant) | Melee bite; 5 damage per attack |
| Baby Seal | TapTap platform + cloud save | Slides into enemies; slows nearby foes |
| Pepper | Special event | Fire breath attack |

### Pet Behavior

- Pets follow the player at a slight distance.
- Automatically attack the nearest enemy.
- Can absorb some enemy projectiles (tanking).
- When HP is depleted, the pet enters a "resting" state and returns after 30 seconds.
- Priest's healing skills can restore pet HP.

---

## 17. Follower & Mercenary System

Followers (mercenaries) are NPC companions hired during a run. Unlike pets, they can permanently die.

### Mercenary Properties

| Property | Value |
|----------|-------|
| Total mercenaries | 13 |
| Hiring method | Pay gold at NPC encounter in dungeon, or rescue from cage (free but unarmed) |
| Maximum followers | 1 (some skills/buffs allow more) |
| Death | Permanent for the run; no revival |
| Carry-over | Surviving mercenaries persist to next floor (gain default weapon if rescued unarmed) |
| Damage scaling | Mercenary attacks are more powerful than pet attacks |

### Mercenary Tier List

| Tier | Mercenaries |
|------|------------|
| S (Best) | Healing Knight, BarbarQ, Royal Knight, Don Quixote |
| A | Mercenary Intern, Shared Robot |
| B | Soot Soot, Legendary Apprentice |
| C (Weakest) | Muscleman, Mad Scientist, Jim Smiley, Headgear Hero, Pharaoh |

### Notable Mercenaries

| Mercenary | HP | Special Trait |
|-----------|----|----|
| Healing Knight | 30 | Periodically heals player for 1 HP |
| Royal Knight | 40 | Only mercenary with a defense stat; blocks projectiles with shield |
| BarbarQ | 35 | High melee damage; charges into enemies |
| Don Quixote | 25 | Lance charge attack; long range melee |

---

## 18. Currency & Economy

### Currency Types

Soul Knight features **6 currencies**:

| Currency | Icon | Earned From | Primary Use |
|----------|------|-------------|-------------|
| **Gold (Coins)** | Yellow coin | Enemy kills during runs | Buy weapons/items from in-run shops; hire mercenaries; use statues |
| **Gems** | Blue diamond | End-of-run rewards; garden; daily login | Unlock characters; upgrade characters; use Gashapon Machine; forge weapons |
| **Materials** (Ironstone, Organic Matter, Timber) | Various icons | Green chests; garden; dismantling weapons; enemy drops | Forge weapons at Forge Table; craft items at Workshop |
| **Parts** | Gear icon | Enemy drops; garden; dismantling | Forge Armor Mounts; repair Robot/Motorcycle; trade with Retired Knight |
| **Blueprints** | Scroll icon | Gashapon Machine; green chests; Turret Rooms; Wishing Well | Develop specific weapons/Armor Mounts at Design Table |
| **Fish** | Fish icon | Fishing mini-game | Trade for items; feed pets; certain crafting recipes |

### Gold Economy (In-Run)

| Source | Amount |
|--------|--------|
| Regular enemy kill | 1--3 coins |
| Champion enemy kill | 3--5 coins |
| Boss kill | 50--150 coins |
| Gold Mine (secret room) | 60 total (6 mines x 10 each) |
| Gold from chests | 10--30 coins |

| Expenditure | Cost |
|-------------|------|
| Shop weapon (Common) | 8--15 gold |
| Shop weapon (Uncommon) | 15--25 gold |
| Shop weapon (Rare+) | 25--50 gold |
| HP Potion | 5--10 gold |
| Energy Potion | 10--15 gold |
| Statue offering | 5--15 gold |
| Mercenary hire | 15--30 gold (scales with floor) |

### Gem Economy (Persistent)

| Source | Amount |
|--------|--------|
| Completing a run (success) | 50--100 gems |
| Completing a run (failure) | 10--30 gems |
| Leftover gold conversion | ~5 gold = 1 gem (approximate) |
| Gem Flower (garden) | 288 gems |
| Gem Tree (garden, daily) | 222 gems |
| Watching ads | 50--100 gems per ad |
| Daily login | 20--200 gems |

| Expenditure | Cost |
|-------------|------|
| Character unlock (low tier) | 2,000--4,000 gems |
| Character unlock (mid tier) | 5,000--8,000 gems |
| Character unlock (high tier) | 12,000+ gems |
| Character upgrade (per star) | 500--5,000 gems (scales with level) |
| Gashapon Machine pull | 200 gems per pull |
| Weapon forge (varies) | 50--500 gems + materials |

---

## 19. Crafting, Forging & Workshop

### Workshop Area

The Workshop is located to the right of the Living Room and contains:

| Station | Function |
|---------|----------|
| **Forge Table** | Forge previously-obtained weapons using materials + gems for use in the next run |
| **Design Table** | Develop new weapons/Armor Mounts from blueprints + gems |
| **Resetting Furnace** | Dismantle weapons into materials |
| **Material Shop** | Buy/sell crafting materials |
| **Retired Knight** | Trade Parts for rare items |

### Forge Table

- A weapon must have been **obtained 8 times** before it becomes available for forging.
- Forged weapons are placed in the starting room at the beginning of the next run.
- **Forged weapons are single-use**: they disappear after one run.
- Cost: Varies by weapon rarity; typically 2--10 materials + 50--500 gems.

### Design Table

- Requires a specific Blueprint to unlock development.
- Blueprints are found from: Gashapon Machine, Green Chests, Turret Rooms, Wishing Well.
- Developed weapons are added to the Forge Table pool permanently.
- Before Update 1.10.0, developed weapons could ONLY be obtained via forging.

### Material Types

| Material | Source | Common Use |
|----------|--------|------------|
| Ironstone | Garden (Ironwood); enemy drops; chests | Metal weapon forging |
| Organic Matter | Garden (Trumpet Flower); enemy drops | Staff/magic weapon forging |
| Timber | Garden (Oak Tree); enemy drops | Bow/crossbow forging |
| Parts | Enemy drops; garden (Gear Flower); dismantling | Armor Mount forging; repairs |

---

## 20. Game Modes

### Level Mode (Main Mode)

| Property | Value |
|----------|-------|
| Structure | 3 Floors x 5 Levels = 15 levels |
| Goal | Reach and reclaim the Magic Stone |
| Lives system | 6 lives per run (Badass: fewer) |
| Buff selection | After each floor (choose 1 of 3) |
| Difficulty scaling | Enemy HP and damage increase per floor |

### Badass Mode

| Property | Value |
|----------|-------|
| Unlock condition | Complete Level Mode once |
| Enemy changes | All enemies are Champion variants; +20% HP; increased aggression |
| Player changes | Armor regeneration reduced; some buffs unavailable |
| Bullet changes | Enemies fire faster; more bullet patterns |
| Boss changes | +25% HP; new attack patterns available |
| Rewards | Better weapon drops; exclusive achievements |

### Boss Rush Mode

| Property | Value |
|----------|-------|
| Structure | 3 floors x 4-5 levels = 13 levels |
| Content | Boss fights only; every boss is a Champion |
| Badass modifier | Additional +20% boss HP if enabled |
| Rewards | High-rarity weapons; exclusive cosmetics |

### The Origin

| Property | Value |
|----------|-------|
| Structure | 12 stages x 3 waves each = 36 waves (excluding opening) |
| Content | Horde survival mode with portal-spawned enemies |
| Buff slots | 10 |
| Badass modifier | All portal enemies become Champion |
| Rewards | Exclusive weapons and materials |

### Challenge Conditions

Optional modifiers that can be activated for increased difficulty and rewards:

| Condition | Effect |
|-----------|--------|
| Boss Duo | 2 slightly nerfed bosses spawn instead of 1 |
| No Energy Recovery | Energy orbs do not drop |
| Increased Enemy Count | +50% enemies per room |
| Random Weapon Start | Start with a random weapon instead of starter |
| Curse | Specific negative modifier (e.g., "No healing") |

---

## 21. Multiplayer Co-op

### Connection & Players

| Property | Value |
|----------|-------|
| Maximum players | 4 |
| Connection type | Local WiFi (LAN) built-in; Online co-op available |
| Host/Client model | One player hosts; others join via room code or LAN discovery |
| Cross-platform | iOS and Android can play together via LAN |

### Multiplayer Scaling

| Players | Enemy HP Multiplier |
|---------|---------------------|
| 1 (solo) | 100% (base) |
| 2 | 150% |
| 3 | 200% |
| 4 | 250% |

### Multiplayer Rules

- If any player enters an enemy room, **all other players are warped** to that room.
- Buff selection: Each player independently chooses their buff.
- **Special Buff sharing**: Special Buffs (statue buffs) are shared among all players.
- **Unique Buffs**: Character passive buffs are NOT shared.
- **Revival**: Fallen players can be revived by Priest or specific items; otherwise they spectate until the floor ends.
- **Loot**: Weapons in chests and shops are available to all players; first-come-first-served.
- **Gold**: Each player has their own gold pool.

---

## 22. UI Layout & HUD

### In-Game HUD Layout

```
+------------------------------------------------------------------+
|  [HP Hearts] [Armor Shields] [Energy Bar]      [Minimap]         |
|  [Red ****]  [Gray ****]     [Blue ====]       [Grid of rooms]   |
|                                                                    |
|                                                                    |
|                         [GAME WORLD]                               |
|                         [Player + Enemies]                         |
|                                                                    |
|  [Move Joystick]                          [Weapon Icon 1] [Swap]  |
|  (Left thumb)                             [Weapon Icon 2]         |
|                                           [Fire Button]           |
|                               [Skill Button]    (Right thumb)     |
+------------------------------------------------------------------+
```

### HUD Elements

| Element | Position | Details |
|---------|----------|---------|
| HP Bar | Top-left | Red hearts; each heart = 1 HP |
| Armor Bar | Top-left (below HP) | Gray shield icons; each icon = 1 armor |
| Energy Bar | Top-left (below Armor) | Blue bar with numerical value (e.g., 180/200) |
| Minimap | Top-right | Grid showing room layout; current room highlighted; icons for chest/shop/boss rooms |
| Move Joystick | Bottom-left | Virtual analog stick; appears on touch |
| Fire Button | Bottom-right | Large circular button; hold to auto-fire |
| Skill Button | Bottom-center-right | Smaller button; shows cooldown timer overlay |
| Weapon Slots | Right side | Shows both equipped weapons; tap to swap; current weapon highlighted |
| Weapon Swap | Right side | Button between weapon icons |
| Gold Counter | Top-center | Coin icon + current gold amount |
| Floor/Level Indicator | Top-center | "1-3" format showing current floor and level |
| Boss HP Bar | Top-center (boss rooms only) | Large health bar with boss name |
| Pause Button | Top-right corner | Pauses game; shows settings |

### Minimap Symbols

| Symbol | Meaning |
|--------|---------|
| White square | Unvisited room |
| Green square | Cleared enemy room |
| Gold chest icon | Chest room |
| Yellow ! | Crystal Mine / special room |
| Shop bag icon | Shop room |
| Red skull icon | Boss room |
| Blue arrow | Current room |
| Doorway lines | Connections between rooms |

### Menu Screens

1. **Main Menu**: Living Room view with character, pet, and interactive objects.
2. **Character Select**: Grid of all characters with lock/unlock status, stats preview.
3. **Pre-Run Screen**: Selected character + pet + forged weapon + garden buffs.
4. **Buff Selection Screen**: Three buff cards displayed; tap to select one.
5. **Death Screen**: Stats summary (rooms cleared, enemies killed, gold earned, gems earned).
6. **Victory Screen**: Magic Stone recovered animation; stats summary; gem rewards.

---

## 23. Audio Design

### Music System

| Context | Track Style | Notes |
|---------|-------------|-------|
| Living Room / Lobby | Upbeat chiptune; relaxed tempo | Looping ambient track |
| Floor 1 Biomes | Mid-tempo electronic with retro synths | Unique per biome; ~2-minute loops |
| Floor 2 Biomes | Faster tempo; more intense | Percussion-heavy; builds tension |
| Floor 3 Biomes | High-energy electronic; sci-fi elements | Spaceship has futuristic synth; Volcano has heavy bass |
| Boss Battles | Intense fast-tempo; driving percussion | Distinct boss theme; shared across all bosses |
| Boss Enraged Phase | Tempo/intensity increase from normal boss theme | Layered additional instruments |
| Buff Selection | Calm interlude track | Brief; plays during transition |
| Victory | Triumphant fanfare; chiptune | Short celebratory jingle |
| Death / Game Over | Somber; descending tones | Brief; leads to death screen |

### Sound Effects

| Event | Sound |
|-------|-------|
| Player footsteps | Soft pixel-art style tap sounds |
| Weapon fire (gun) | Sharp "pew" or "bang" depending on weapon category |
| Weapon fire (laser) | Sustained "bzzt" or "vwoom" |
| Weapon fire (staff) | Magical shimmer/chime |
| Melee swing | Whoosh followed by impact thud |
| Projectile hit (enemy) | Squelchy impact; varies by element |
| Projectile hit (wall) | Dull thud |
| Bullet blocked (melee) | Metallic clang/ping |
| Enemy death | Pop/splat with brief particle burst |
| Boss death | Extended explosion with screen shake |
| Chest opening | Wooden creak followed by sparkle |
| Item pickup (gold) | Coin jingle |
| Item pickup (energy orb) | Ascending chime |
| Item pickup (weapon) | Distinctive equip sound |
| HP lost | Sharp alarm ding |
| Armor break | Glass/shield shatter sound |
| Armor regenerate | Soft ascending tone |
| Skill activation | Character-specific; magical burst |
| Skill cooldown complete | Subtle ready ping |
| Room cleared | Door unlock sound + brief fanfare |
| Portal enter | Whoosh + dimension-warp sound |
| Buff selection | Card flip sound on reveal; confirm chime on select |
| Freeze effect | Crystalline snap |
| Burn effect | Crackling flame |
| Poison effect | Bubbling/hissing |
| Electrify effect | Zapping/sparking |

### Audio Settings

| Setting | Options |
|---------|---------|
| Music Volume | Slider 0--100% |
| SFX Volume | Slider 0--100% |
| Vibration | On/Off (mobile haptics on weapon fire, damage taken) |
