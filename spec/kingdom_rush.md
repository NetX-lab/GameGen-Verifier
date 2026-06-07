# Kingdom Rush — Complete Game Specification

## 1. Game Overview

Kingdom Rush is a single-player fantasy tower defense game where the player builds and upgrades four base tower types along predefined build points to stop waves of enemies from reaching the kingdom. The game features a campaign map, hero units, soldier rallying, and special abilities.

- Genre: Tower Defense (fantasy themed)
- Perspective: Top-down isometric
- Resolution: 1280x720 reference, scalable
- Target Framerate: 60 FPS
- Input: Mouse/touch (click to build, click to upgrade, click to rally)

## 2. Technical Foundation

### 2.1 Coordinate System
- Fixed build points on each map (no free placement)
- Map size: 1280x720 logical pixels
- Each map has 8-16 build points
- Enemies follow predefined paths (can have multiple paths merging)

### 2.2 Core Game Loop
```
Each frame:
  1. Process user input (build, upgrade, rally soldiers, activate abilities)
  2. Spawn enemies for current wave
  3. Update enemy positions (move along path, handle combat)
  4. Update tower attacks (find target, fire)
  5. Update soldier positions (patrol rally point, engage enemies)
  6. Process projectiles and effects
  7. Process enemy deaths (award gold, check wave completion)
  8. Update hero (movement, attacks, abilities)
  9. Update cooldowns (Rain of Fire, Reinforcements)
  10. Check win/loss conditions
  11. Render
```

### 2.3 Game States
- WORLD_MAP: Campaign level selection
- LEVEL_PREP: View map, place initial towers before first wave
- WAVE_ACTIVE: Enemies spawning and moving
- BETWEEN_WAVES: Brief pause, countdown timer to next wave (can call early for bonus gold)
- LEVEL_COMPLETE: Star rating screen
- GAME_OVER: Enemies breached, lives at 0

## 3. Tower System

### 3.1 Base Tower Types

All towers are built on predefined build points. Each point can hold one tower.

#### Archer Tower (Ranged DPS)
- Build Cost: 70 gold
- Range: 170px
- Attack Speed: 0.8s per shot
- Damage: 4-6 per arrow (random in range)
- Fires 2 arrows simultaneously at potentially different targets
- Can target flying enemies

| Level | Cost | Damage  | Range | Attack Speed |
|-------|------|---------|-------|-------------|
| 1     | 70   | 4-6     | 170   | 0.8s        |
| 2     | 110  | 7-11    | 180   | 0.7s        |
| 3     | 160  | 13-19   | 190   | 0.6s        |
| 4     | 230  | 21-31   | 200   | 0.5s        |

**Specialization A: Rangers Hideout (Lv4 upgrade) - Cost: 230**
- Damage: 24-36
- Attack Speed: 0.4s
- Poison arrows: 5 damage/sec for 3s
- Wrath of the Forest ability: Vines grab enemies for 3s (15s cooldown)

**Specialization B: Musketeer Garrison (Lv4 upgrade) - Cost: 230**
- Damage: 35-65
- Attack Speed: 1.5s
- Long range: 260px
- Sniper Shot ability: Instant kill on non-boss (<2000 HP), 12s cooldown
- Shrapnel Shot: AoE on impact, 15px radius

#### Barracks (Melee/Block)
- Build Cost: 70 gold
- Spawns 3 soldiers that patrol a rally point
- Soldiers block and engage enemies on the path
- Rally point can be moved by the player within a radius

| Level | Cost | Soldier HP | Damage | Armor | Respawn |
|-------|------|-----------|--------|-------|---------|
| 1     | 70   | 30        | 1-3    | None  | 10s     |
| 2     | 110  | 65        | 3-6    | Low   | 10s     |
| 3     | 160  | 110       | 7-14   | Med   | 10s     |
| 4     | 230  | 195       | 15-25  | High  | 10s     |

**Specialization A: Holy Order (Lv4 upgrade) - Cost: 230**
- 3 Paladins: HP 600, Damage 24-36, Heavy Armor
- Heal ability: Restore 100 HP to all paladins, 10s cooldown
- Holy Light: 90-110 area damage, 20s cooldown
- Shield of Valor: Temporary invulnerability for 3s, 30s cooldown

**Specialization B: Barbarian Mead Hall (Lv4 upgrade) - Cost: 230**
- 3 Barbarians: HP 400, Damage 32-48, Medium Armor
- Throwing Axes: Ranged attack 40-60 damage when enemies out of melee range
- More Axes ability: +2 soldiers (5 total)
- Whirlwind Attack: AoE melee hitting all nearby, 8s cooldown

#### Mage Tower (Magic DPS)
- Build Cost: 100 gold
- Range: 160px
- Attack Speed: 1.5s
- Damage: 9-17 (magic damage, ignores armor)
- Cannot target flying enemies (by default)

| Level | Cost | Damage | Range | Attack Speed |
|-------|------|--------|-------|-------------|
| 1     | 100  | 9-17   | 160   | 1.5s        |
| 2     | 160  | 22-38  | 170   | 1.4s        |
| 3     | 240  | 40-72  | 180   | 1.3s        |
| 4     | 300  | 56-96  | 190   | 1.2s        |

**Specialization A: Arcane Wizard (Lv4 upgrade) - Cost: 300**
- Damage: 70-130
- Teleport ability: Teleport enemy back along path, 8s cooldown
- Death Ray: Sustained beam, 45 DPS for 3.5s, 16s cooldown
- Twister: Disable and damage enemies in area, 20s cooldown

**Specialization B: Sorcerer Mage (Lv4 upgrade) - Cost: 300**
- Polymorph: Turn enemy into sheep (instakill if HP < 800), 8s cooldown
- Summon Elemental: Spawn earth elemental (HP 500, 20-34 dmg), 25s cooldown
- Elemental HP scales: +100 HP per polymorph used in level

#### Artillery (AoE)
- Build Cost: 125 gold
- Range: 200px
- Attack Speed: 3.0s
- Damage: 8-15 (AoE, explosion radius 50px)
- Cannot target flying enemies

| Level | Cost | Damage | Range | AoE Radius | Attack Speed |
|-------|------|--------|-------|-----------|-------------|
| 1     | 125  | 8-15   | 200   | 50px      | 3.0s        |
| 2     | 190  | 20-44  | 210   | 55px      | 2.8s        |
| 3     | 260  | 52-96  | 220   | 60px      | 2.6s        |
| 4     | 340  | 82-150 | 230   | 65px      | 2.4s        |

**Specialization A: Big Bertha (Lv4 upgrade) - Cost: 340**
- Damage: 100-180
- AoE Radius: 80px
- Dragonbreath Launcher: Fire AoE dealing 40/s for 4s, 18s cooldown
- Cluster Launcher: Fires 5 mini-bombs on impact, each 15-30 dmg

**Specialization B: Tesla x104 (Lv4 upgrade) - Cost: 340**
- Chain lightning: Hits 3 targets, 90-160 damage each
- Attack Speed: 2.2s
- Overcharge: Supercharged bolt, 280 damage AoE, 14s cooldown
- Supercharged Bolt: Stuns targets for 2.5s

### 3.2 Tower Selling
- Sell value: 60% of total gold invested (build + upgrades)
- Selling is instant, tower removed, build point freed

## 4. Enemy Types

### 4.1 Standard Enemies

| Enemy          | HP   | Speed | Damage | Armor | Gold | Special           |
|----------------|------|-------|--------|-------|------|-------------------|
| Goblin         | 30   | Fast  | 2-4    | None  | 5    | -                 |
| Orc            | 120  | Med   | 8-14   | Low   | 10   | -                 |
| Orc Champion   | 300  | Med   | 20-30  | Med   | 20   | -                 |
| Wolf            | 80   | VFast | 5-8    | None  | 8    | Cannot be blocked |
| Wolf Rider     | 250  | Fast  | 14-22  | Low   | 20   | Rider dismounts   |
| Dark Knight    | 500  | Slow  | 25-40  | Heavy | 30   | High armor        |
| Brigand        | 70   | Fast  | 5-10   | None  | 5    | Dodges 20% attacks|
| Shadow Archer  | 60   | Med   | 8-12   | None  | 8    | Ranged attack     |
| Troll          | 800  | Slow  | 40-60  | Med   | 50   | Regenerates 20HP/s|
| Troll Champion | 1500 | Slow  | 60-80  | High  | 80   | Regen 40HP/s      |
| Dark Slayer    | 250  | Fast  | 30-50  | None  | 25   | Teleports past block|
| Necromancer    | 400  | Slow  | 15-25  | None  | 35   | Summons skeletons |
| Skeleton       | 40   | Med   | 3-5    | None  | 0    | Summoned          |
| Gargoyle       | 120  | Fast  | 10-15  | Low   | 15   | Flying            |
| Demon          | 600  | Med   | 35-55  | Med   | 45   | Fire immune       |
| Demon Lord     | 2000 | Slow  | 60-90  | Heavy | 100  | Fire immune, AoE  |
| Yeti           | 1800 | Slow  | 50-70  | Heavy | 80   | Freezes soldiers  |

### 4.2 Boss Enemies

| Boss           | HP    | Speed | Abilities                              | Gold |
|----------------|-------|-------|----------------------------------------|------|
| Juggernaut     | 3000  | Slow  | AoE slam, high armor                   | 200  |
| J.T.           | 5000  | Slow  | Summons trolls, regenerates            | 300  |
| Vez'nan        | 8000  | Slow  | Magic shield, summon demons, teleport  | 500  |
| Myconid        | 4000  | Med   | Poison cloud, spawns mushrooms         | 250  |

### 4.3 Armor System
Armor reduces physical damage by a percentage:
| Armor Level | Damage Reduction |
|-------------|-----------------|
| None        | 0%              |
| Low         | 20%             |
| Medium      | 40%             |
| High        | 60%             |
| Hero Armor  | 80%             |

Magic damage bypasses all armor.

### 4.4 Speed Values
| Speed Category | Pixels per Second |
|----------------|-------------------|
| Very Slow      | 20                |
| Slow           | 35                |
| Medium         | 50                |
| Fast           | 70                |
| Very Fast      | 100               |

## 5. Hero System

### 5.1 Hero Mechanics
- One hero per level, free to deploy
- Heroes are placed on the map and can be moved to any walkable location
- Heroes attack automatically and have special abilities
- Heroes respawn after death (15-30s depending on hero)
- Heroes gain XP from kills and level up

### 5.2 Available Heroes

#### Alleria Swiftwind (Ranger)
- Cost: Free (starter)
- HP: 200 + 20/level
- Damage: 15-25 + 5/level (ranged)
- Attack Speed: 0.6s
- Range: 180px
- Ability 1 (Lv2): Multishot - Fires 3 arrows, 10s cooldown
- Ability 2 (Lv4): Rain of Arrows - AoE damage in area, 20s cooldown
- Max Level: 10

#### Malik Hammerfury (Paladin)
- Cost: Free (starter)
- HP: 400 + 40/level
- Damage: 20-40 + 8/level (melee)
- Attack Speed: 1.0s
- Armor: Heavy
- Ability 1 (Lv2): Shield Bash - Stun all nearby for 2s, 12s cooldown
- Ability 2 (Lv4): Holy Light - Heal self and nearby soldiers 200HP, 18s cooldown
- Max Level: 10

#### Bolin Farslayer (Artillery)
- Cost: 500 gems
- HP: 280 + 25/level
- Damage: 40-80 + 10/level (AoE, ranged)
- Attack Speed: 2.5s
- Range: 220px
- Ability 1 (Lv2): Oil Bomb - Slow enemies 50% for 4s, 14s cooldown
- Ability 2 (Lv4): TNT Rain - Multiple explosions, 25s cooldown
- Max Level: 10

#### Elora Wintersong (Mage)
- Cost: 500 gems
- HP: 250 + 22/level
- Damage: 30-60 + 12/level (magic, ranged)
- Attack Speed: 1.4s
- Range: 170px
- Ability 1 (Lv2): Ice Storm - Freeze enemies in area for 3s, 15s cooldown
- Ability 2 (Lv4): Chain Lightning - Hits 4 targets for 120 dmg each, 20s cooldown
- Max Level: 10

### 5.3 Hero XP and Leveling
```
XP per kill = enemy_gold_value / 2
XP needed per level = 100 * level * level
Max level per campaign level = campaign_level_number + 3
```

## 6. Special Abilities (Spells)

### 6.1 Rain of Fire
- Unlocked: Level 1
- Cooldown: 60s (can be upgraded)
- Click a target area on the map
- 5 fireballs drop randomly in a 100px radius
- Each fireball: 40-80 damage, 30px AoE

| Upgrade Level | Cost (stars) | Effect                    |
|---------------|-------------|---------------------------|
| 1             | 1           | Base damage 40-80         |
| 2             | 1           | Damage 60-120             |
| 3             | 1           | Damage 80-160, 6 fireballs|

### 6.2 Reinforcements
- Unlocked: Level 3
- Cooldown: 50s (can be upgraded)
- Drop 2 soldiers at target location
- Soldiers last 20s or until killed

| Upgrade Level | Cost (stars) | Effect                           |
|---------------|-------------|----------------------------------|
| 1             | 1           | 2 soldiers, 100HP, 5-10 dmg     |
| 2             | 1           | 2 soldiers, 200HP, 10-20 dmg    |
| 3             | 1           | 3 soldiers, 300HP, 15-30 dmg    |

## 7. Star Rating and Upgrade System

### 7.1 Star Rating Per Level
- 3 Stars: No enemies reach the exit (20 lives remaining)
- 2 Stars: 1-6 enemies reach the exit (14-19 lives)
- 1 Star: 7-18 enemies reach the exit (2-13 lives)
- 0 Stars: 19+ enemies reach exit (lose the level)

Starting lives per level: 20

### 7.2 Stars as Currency
Stars earned from completing levels are used to upgrade:
- Rain of Fire (3 levels, 1 star each)
- Reinforcements (3 levels, 1 star each)
- Global tower buffs (various costs)

### 7.3 Upgrade Tree (Meta-progression using stars)

**Archer Upgrades:**
| Upgrade           | Stars | Effect                      |
|-------------------|-------|-----------------------------|
| Salvage           | 1     | 90% sell value (up from 60%)|
| Eagle Eye         | 1     | +10% range for all archers  |
| Piercing Shots    | 2     | 10% chance to ignore armor  |
| Far Shot          | 2     | +15% range for all archers  |
| Steady Hand       | 3     | +10% damage for all archers |

**Barracks Upgrades:**
| Upgrade           | Stars | Effect                      |
|-------------------|-------|-----------------------------|
| Toughness         | 1     | +10% soldier HP             |
| Better Armor      | 1     | +10% armor rating           |
| Improved Deploy   | 2     | -3s respawn time            |
| Endurance         | 2     | +20% soldier HP             |
| Spiked Armor      | 3     | Reflect 10% melee damage    |

**Mage Upgrades:**
| Upgrade           | Stars | Effect                      |
|-------------------|-------|-----------------------------|
| Spell Reach       | 1     | +10% range                  |
| Arcane Shatter    | 1     | +5% damage vs armor         |
| Hermetic Study    | 2     | +10% attack speed           |
| Empowered Magic   | 2     | +15% damage                 |
| Slow Curse        | 3     | 15% chance to slow on hit   |

**Artillery Upgrades:**
| Upgrade           | Stars | Effect                      |
|-------------------|-------|-----------------------------|
| Bigger Explosions | 1     | +10% AoE radius             |
| Concentrated Fire | 1     | +5% damage                  |
| Field Logistic    | 2     | -10% build cost             |
| Smart Targeting   | 2     | Prioritize strongest enemy  |
| Shock and Awe     | 3     | 10% chance to stun 1s       |

## 8. Campaign Map and Level Progression

### 8.1 Campaign Structure
- 15 main campaign levels
- Each level unlocks the next on the world map
- Difficulty modes: Casual, Normal, Veteran
- Challenge modes unlock after completing a level:
  - Heroic Challenge: Restricted tower types, harder waves
  - Iron Challenge: Even harder, specific constraints

### 8.2 Level Design Template
```
Level {
  id: int (1-15)
  name: String
  terrain_type: Forest|Desert|Mountain|Swamp|Dark
  build_points: int (8-16)
  paths: int (1-3)  // number of enemy entry paths
  path_merge_points: List<Point>  // where paths converge
  waves: int (8-18)
  has_flying_enemies: bool
  has_boss: bool
  difficulty_rating: 1-5
  background_music: String
  special_mechanic: Optional<String>  // e.g., "bridge can be destroyed"
}
```

### 8.3 Example Level Layout: Southport (Level 1)
```
+-------------------------------------------------------+
|                                                         |
|  ENTRANCE ============================                  |
|                                       \                 |
|      [B1]          [B2]               \                |
|                                        |                |
|                    [B3]          [B4]   |               |
|                                        /                |
|  ENTRANCE ============================                  |
|                    \                                    |
|      [B5]           \        [B6]                      |
|                      \                                  |
|                       ======== [B7] ===> EXIT          |
|                                                         |
|      [B8]                                              |
|                                                         |
+-------------------------------------------------------+

[Bn] = Build point n
==== = Enemy path
```

### 8.4 Wave Composition Example (Level 5)
```
Wave 1:  10 Goblins (1.5s spacing)
Wave 2:  8 Goblins + 4 Orcs (1.2s spacing)
Wave 3:  6 Orcs + 4 Wolves (1.0s spacing, wolves from path 2)
Wave 4:  12 Goblins + 6 Orcs (0.8s spacing)
Wave 5:  4 Orc Champions + 8 Orcs (1.0s spacing)
Wave 6:  10 Wolves + 4 Brigands (0.7s spacing, split paths)
Wave 7:  6 Shadow Archers + 4 Orc Champions (0.8s spacing)
Wave 8:  3 Dark Knights + 6 Orcs + 10 Goblins (1.0s spacing)
Wave 9:  5 Gargoyles + 8 Orc Champions (flying + ground)
Wave 10: 2 Trolls + 4 Dark Knights + 10 Orcs (boss wave)
```

## 9. Enemy Path and Movement

### 9.1 Path Definition
- Paths defined as series of waypoints
- Enemies move from waypoint to waypoint in straight lines
- Multiple paths can share segments (merge points)
- Path width: 40px (enemies stay within this band)

### 9.2 Blocking Mechanics
- Soldiers from Barracks stand on/near the path at rally point
- When an enemy reaches a soldier, combat begins
- Enemy stops moving, attacks the soldier
- Maximum enemies engaged by one soldier: 1
- Each soldier can block 1 enemy
- Blocked enemies stack behind, waiting their turn
- Some enemies cannot be blocked (wolves, flyers, teleporters)

### 9.3 Enemy Attack Behavior
```
function enemyUpdate(enemy):
    if enemy.blocked_by_soldier:
        attack(soldier)
        if soldier.hp <= 0:
            soldier.startRespawn()
            enemy.resume_movement()
    elif enemy.is_ranged and nearby_soldier:
        attack(nearby_soldier)  // while still moving
    else:
        move_toward_next_waypoint()
        if reached_exit:
            player.lives -= enemy.lives_cost
            enemy.remove()
```

## 10. Gold Economy

### 10.1 Income Sources
- Starting gold: 200-400 (varies by level)
- Gold per kill: Varies by enemy type (see enemy table)
- Early wave bonus: +10 gold per wave called early
- No passive income

### 10.2 Spending
- Tower construction: 70-125 gold
- Tower upgrades: 110-340 gold per level
- Specialization: Additional 230-340 gold
- No tower abilities cost gold (only cooldowns)

### 10.3 Sell Values
- Base sell value: 60% of total invested
- With Salvage upgrade: 90% of total invested

## 11. Damage Calculation

### 11.1 Physical Damage Formula
```
actualDamage = baseDamage * (1 - armorReduction)
```

### 11.2 Magic Damage Formula
```
actualDamage = baseDamage  // ignores armor entirely
```

### 11.3 True Damage
- Rain of Fire, some special abilities
- Cannot be reduced by any means

### 11.4 Damage Types by Tower
| Tower        | Damage Type |
|--------------|-------------|
| Archer       | Physical    |
| Barracks     | Physical    |
| Mage         | Magic       |
| Artillery    | Physical    |
| Rain of Fire | True        |

## 12. User Interface Layout

### 12.1 In-Game HUD
```
+------------------------------------------------------------------+
|  [Menu] [Pause]              Wave: 5/12       Lives: 20  Gold: 450|
+------------------------------------------------------------------+
|                                                                    |
|                                                                    |
|                      MAP AREA                                      |
|                                                                    |
|                                                                    |
|                                                                    |
|                                                                    |
+------------------------------------------------------------------+
| [Rain of Fire]  [Reinforcements]            [Next Wave >>] [FF>>] |
|   CD: 45s          CD: 32s                                        |
+------------------------------------------------------------------+
```

### 12.2 Tower Build Menu
When clicking an empty build point:
```
      [Archer $70]
[Barracks $70]  [Mage $100]
      [Artillery $125]
```

### 12.3 Tower Upgrade Menu
When clicking a built tower:
```
+---------------------------+
| Archer Tower Lv2          |
| Damage: 7-11              |
|                            |
| [Upgrade Lv3: $160]       |
|                            |
| [Sell: $108]               |
| Targeting: [First v]       |
+---------------------------+
```

### 12.4 Specialization Menu
When clicking a Lv4 tower:
```
+---------------------------------------------+
|           CHOOSE SPECIALIZATION              |
|                                              |
|  [Rangers Hideout]    [Musketeer Garrison]   |
|  Cost: $230           Cost: $230             |
|  - Poison arrows      - High damage          |
|  - Vine trap          - Sniper shot          |
|  - Fast attacks       - Shrapnel             |
+---------------------------------------------+
```

## 13. Targeting Priorities

### 13.1 Default Priority
Towers target the enemy closest to the exit by default.

### 13.2 Configurable Targeting (after upgrade)
- **Nearest Exit**: Enemy closest to exit
- **Strongest**: Enemy with highest current HP
- **Weakest**: Enemy with lowest current HP
- **Nearest**: Enemy closest to tower

### 13.3 Special Targeting Rules
- Archer Towers can target flying enemies
- Mage Towers cannot target flying enemies (until upgraded)
- Artillery cannot target flying enemies
- Barracks automatically engage nearest enemy within patrol radius

## 14. Difficulty Modes

### 14.1 Casual
- Enemy HP: 70% of normal
- Enemy damage: 70% of normal
- Starting gold: +50 bonus
- Lives: 25

### 14.2 Normal
- All values at 100%
- Lives: 20

### 14.3 Veteran
- Enemy HP: 130% of normal
- Enemy damage: 130% of normal
- Starting gold: -30
- Lives: 15
- Enemies move 10% faster

## 15. Audio Design

### 15.1 Sound Effects
- Tower placement: Stone/metal placement thud
- Archer shot: Bow twang
- Mage shot: Magical whoosh
- Artillery shot: Cannon boom
- Enemy death: Type-specific death sound
- Wave start: War horn
- Ability activation: Magical chime
- Soldier death: Oof/groan
- Gold earned: Coin clink

### 15.2 Music
- World map: Orchestral adventure theme
- Forest levels: Light medieval theme
- Dark levels: Ominous orchestral
- Boss waves: Intensified version of level theme

## 16. Animation System

### 16.1 Tower Animations
- Idle: Subtle breathing/movement (2-4 frames, 0.5s loop)
- Attack: Wind-up + release (3-5 frames, matches attack speed)
- Upgrade: Sparkle effect + structure morph (15 frames)

### 16.2 Enemy Animations
- Walk: 6-8 frame walk cycle
- Attack: 4-6 frame attack animation
- Death: 5-8 frame death animation + fade
- Special: Type-specific (troll regen glow, necromancer summon)

### 16.3 Projectile Animations
- Arrow: Straight line with rotation to match trajectory
- Magic bolt: Glowing particle trail
- Cannonball: Arc trajectory with shadow
- Fire: Particle system falling from sky

## 17. Challenge Modes

### 17.1 Heroic Challenge
- Available after 3-star completion of a level
- Restrictions: Only 2 tower types available
- +30% enemy HP
- Rewards: 1 bonus star

### 17.2 Iron Challenge
- Available after Heroic completion
- One specific tower type only
- +50% enemy HP
- No hero available
- Rewards: 1 bonus star

### 17.3 Endless Mode (Bonus)
- Available after campaign completion
- Continuous waves of increasing difficulty
- Score tracked (total enemies killed)
- Wave difficulty formula:
```
waveHP = baseHP * (1.0 + wave_number * 0.15)
waveCount = baseCount + wave_number
waveGold = baseGold * max(0.5, 1.0 - wave_number * 0.02)
```

## 18. Save System

### 18.1 Progress Saved
- Campaign progress (levels completed, stars earned)
- Star allocation (upgrades purchased)
- Heroes unlocked
- Challenge completions
- Total stats (enemies killed, gold earned)

### 18.2 Level Auto-Save
- No mid-level save
- Level must be completed or restarted from scratch

## 19. Visual Style Guide

### 19.1 Color Palette
- Terrain greens: #2D5A1E, #3A7D28, #4CAF50
- Path/road: #8B7355, #A0896C
- Water: #3498DB, #2980B9
- UI background: #2C1810 (dark wood)
- Gold text: #FFD700
- HP bar red: #E74C3C
- HP bar green: #27AE60
- Build point glow: #F39C12

### 19.2 Sprite Sizes
- Tower: 64x64 base, 80x80 for level 4+
- Enemy: 32x32 standard, 64x64 boss
- Projectile: 8x8 to 16x16
- Hero: 48x48
- Build point indicator: 40x40

## 20. Performance Targets

### 20.1 Entity Limits
- Maximum enemies on screen: 100
- Maximum projectiles on screen: 200
- Maximum soldiers on screen: 50
- Maximum particle effects: 300

### 20.2 Optimization Strategies
- Sprite batching by layer
- Object pooling for projectiles and particles
- Spatial grid for range checks (cell size: 80px)
- Off-screen culling for particles

## 21. Lives and Exit System

### 21.1 Lives Cost Per Enemy
- Most enemies: 1 life
- Orc Champion: 2 lives
- Dark Knight: 2 lives
- Troll: 3 lives
- Boss enemies: 5-10 lives
- Flying enemies: 1 life

### 21.2 Exit Behavior
- When an enemy reaches the exit point, it is removed
- Lives are deducted immediately
- Visual: Enemy fades out at exit, red flash on lives counter
- If lives reach 0: immediate game over, all action stops
