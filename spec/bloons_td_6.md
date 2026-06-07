# Bloons TD 6 — Complete Game Specification

## 1. Game Overview

Bloons TD 6 is a single-player tower defense game where the player places monkey towers along a path to pop waves of balloons (bloons) before they reach the exit. The game features multiple maps, difficulty modes, heroes, and a deep upgrade system with three distinct paths per tower.

- Genre: Tower Defense
- Platform: 2D top-down with pseudo-3D tower models
- Resolution: 1920x1080 reference, responsive scaling
- Target Framerate: 60 FPS
- Input: Mouse/touch (click to place, click to select, click to upgrade)

## 2. Technical Foundation

### 2.1 Coordinate System
- Grid-free placement: Towers can be placed anywhere on valid terrain
- Map size: 1920x1080 logical pixels
- Tower footprint: Circular, radius varies by tower type (18-40px)
- Path defined as a series of bezier curve segments

### 2.2 Core Loop
```
Each frame:
  1. Process user input (tower placement, upgrades, ability activation)
  2. Spawn bloons for current round if active
  3. Update all bloons (move along path)
  4. Update all towers (acquire target, rotate, attack)
  5. Process projectiles (move, collision detection)
  6. Process bloon pops (spawn children, award cash)
  7. Check round completion
  8. Check lives remaining
  9. Render all entities
```

### 2.3 Game States
- MAIN_MENU: Map selection, difficulty selection
- PREP_PHASE: Place towers before starting round
- WAVE_ACTIVE: Bloons spawning and moving
- BETWEEN_ROUNDS: Brief pause, can place/upgrade towers
- GAME_OVER: Lives reached 0
- VICTORY: All rounds completed

## 3. Bloon Types

### 3.1 Standard Bloons

| Bloon Type   | RBE | Speed | Layer | Children on Pop      | Color    |
|-------------|-----|-------|-------|----------------------|----------|
| Red         | 1   | 1.0   | 1     | None                 | #FF0000  |
| Blue        | 2   | 1.4   | 2     | 1 Red                | #0066FF  |
| Green       | 3   | 1.8   | 3     | 1 Blue               | #00CC00  |
| Yellow      | 4   | 3.2   | 4     | 1 Green              | #FFFF00  |
| Pink        | 5   | 3.5   | 5     | 1 Yellow             | #FF69B4  |
| Purple      | 5   | 3.0   | 5     | 1 Pink               | #9900CC  |
| Black       | 6   | 1.8   | 6     | 2 Pink               | #1A1A1A  |
| White       | 6   | 2.0   | 6     | 2 Pink               | #FFFFFF  |
| Lead        | 1   | 1.0   | 1     | 2 Black              | #708090  |
| Zebra       | 12  | 1.8   | 7     | 1 Black + 1 White    | #B0B0B0  |
| Rainbow     | 24  | 2.2   | 8     | 2 Zebra              | Rainbow  |
| Ceramic     | 74  | 2.5   | 9     | 2 Rainbow (10HP)     | #CC6600  |

RBE = Red Bloon Equivalent (total pops to fully destroy)

### 3.2 MOAB-Class Bloons

| MOAB Type | RBE    | Speed | HP   | Children on Pop  | Color   |
|-----------|--------|-------|------|------------------|---------|
| MOAB      | 616    | 1.0   | 200  | 4 Ceramic        | #0000CC |
| BFB       | 3164   | 0.25  | 700  | 4 MOAB           | #CC0000 |
| ZOMG      | 16656  | 0.18  | 4000 | 4 BFB            | #006600 |
| DDT       | 816    | 2.75  | 400  | 4 Ceramic (Camo) | #333333 |
| BAD       | 55760  | 0.18  | 20000| 2 ZOMG + 3 DDT   | #660066 |

### 3.3 Bloon Properties
- **Camo**: Only detectable by towers with camo detection. Visual: semi-transparent with camo pattern.
- **Regrow**: Regenerates one layer every 3.0 seconds. Visual: green heart icon on bloon.
- **Fortified**: Double HP for MOAB-class, +2 layers for Ceramic/Lead. Visual: metal band around bloon.

### 3.4 Bloon Movement
- Bloons follow the path defined by waypoints
- Speed is measured in pixels per frame at 60 FPS
- Base speed multiplied by bloon type speed modifier
- Distance along path stored as float [0.0, 1.0] where 1.0 = exit
- Movement formula: `distance += (speed * speedMultiplier) / pathLength / 60`

## 4. Tower Types and Stats

### 4.1 Primary Towers

#### Dart Monkey
- Base Cost: $200
- Footprint Radius: 20px
- Attack Speed: 0.95s
- Range: 130px
- Damage: 1
- Pierce: 2
- Projectile: Dart (travels 200px/s in straight line)
- Targeting: First, Last, Strong, Close

**Upgrade Path 1 (Top):**
| Tier | Name              | Cost  | Effect                                    |
|------|-------------------|-------|-------------------------------------------|
| 1    | Sharp Shots       | $140  | +1 pierce (total 3)                       |
| 2    | Razor Sharp Shots | $220  | +3 pierce (total 6)                       |
| 3    | Spike-o-pult      | $300  | Throws spiked balls, 22 pierce, 1.15s atk |
| 4    | Juggernaut        | $1800 | Giant ball, 50 pierce, +2 damage to Ceramic|
| 5    | Ultra-Juggernaut  | $15000| 200 pierce, spawns 6 mini juggernauts     |

**Upgrade Path 2 (Middle):**
| Tier | Name              | Cost  | Effect                                    |
|------|-------------------|-------|-------------------------------------------|
| 1    | Quick Shots       | $100  | Attack speed 0.79s                        |
| 2    | Very Quick Shots  | $190  | Attack speed 0.63s                        |
| 3    | Triple Shot       | $400  | Fires 3 darts in spread pattern           |
| 4    | Super Monkey Fan Club| $8000| Ability: transforms nearby dart monkeys   |
| 5    | Plasma Monkey Fan Club|$50000| Enhanced transformation, plasma attacks   |

**Upgrade Path 3 (Bottom):**
| Tier | Name              | Cost  | Effect                                    |
|------|-------------------|-------|-------------------------------------------|
| 1    | Long Range Darts  | $90   | +15% range                                |
| 2    | Enhanced Eyesight | $200  | +15% range, camo detection                |
| 3    | Crossbow          | $625  | 3 damage, +30% range, faster projectile   |
| 4    | Sharp Shooter     | $2000 | 6 damage, crit every 8-12 shots (50 dmg)  |
| 5    | Crossbow Master   | $25000| 8 damage, 4x attack speed, crit every 4-8 |

#### Tack Shooter
- Base Cost: $280
- Footprint Radius: 20px
- Attack Speed: 1.4s
- Range: 100px
- Damage: 1
- Pierce: 1
- Projectile: 8 tacks fired in radial pattern (45-degree intervals)
- Targeting: N/A (fires in all directions)

**Upgrade Path 1 (Top):**
| Tier | Name              | Cost  | Effect                                    |
|------|-------------------|-------|-------------------------------------------|
| 1    | Faster Shooting   | $150  | Attack speed 1.07s                        |
| 2    | Even Faster Shooting| $300 | Attack speed 0.76s                        |
| 3    | Hot Shots         | $600  | Tacks deal fire damage, pop Lead/Frozen   |
| 4    | Ring of Fire      | $4500 | Fire ring, 3 damage, 60 pierce, constant  |
| 5    | Inferno Ring      | $45500| Meteor ability, massive fire damage       |

**Upgrade Path 2 (Middle):**
| Tier | Name              | Cost  | Effect                                    |
|------|-------------------|-------|-------------------------------------------|
| 1    | Long Range Tacks  | $100  | +16% range                                |
| 2    | Super Range Tacks | $225  | +16% range                                |
| 3    | Blade Shooter     | $500  | Fires spinning blades, 4 pierce each      |
| 4    | Blade Maelstrom   | $2700 | Ability: massive blade burst (200 blades)  |
| 5    | Super Maelstrom   | $15000| Enhanced ability, shorter cooldown         |

**Upgrade Path 3 (Bottom):**
| Tier | Name              | Cost  | Effect                                    |
|------|-------------------|-------|-------------------------------------------|
| 1    | More Tacks        | $100  | 10 tacks per volley                       |
| 2    | Even More Tacks   | $100  | 12 tacks per volley                       |
| 3    | Tack Sprayer      | $400  | 16 tacks per volley                       |
| 4    | Overdrive         | $3200 | 0.28s attack speed                        |
| 5    | The Tack Zone     | $20000| 32 tacks, +1 damage, +1 pierce            |

#### Boomerang Monkey
- Base Cost: $325
- Footprint Radius: 22px
- Attack Speed: 1.2s
- Range: 130px
- Damage: 1
- Pierce: 4
- Projectile: Boomerang (follows curved path, returns to monkey)

#### Bomb Shooter
- Base Cost: $525
- Footprint Radius: 22px
- Attack Speed: 1.5s
- Range: 130px
- Damage: 1
- Pierce: 18
- Projectile: Bomb (explosive, AoE radius 30px)
- Note: Cannot pop Black/Zebra bloons (explosion immunity)

#### Ice Monkey
- Base Cost: $500
- Footprint Radius: 20px
- Attack Speed: 2.4s (freeze duration)
- Range: 80px
- Damage: 0 (freezes only)
- Effect: Freezes all bloons in range for 1.5s
- Note: Cannot affect White/Zebra bloons (cold immunity)

#### Glue Gunner
- Base Cost: $275
- Footprint Radius: 20px
- Attack Speed: 1.0s
- Range: 130px
- Damage: 0
- Pierce: 1
- Effect: Slows target by 50% for 11s

### 4.2 Military Towers

#### Sniper Monkey
- Base Cost: $350
- Range: Infinite (targets anywhere on map)
- Attack Speed: 1.59s
- Damage: 2
- Pierce: 1 (single target)

#### Monkey Sub
- Base Cost: $325
- Must be placed on water
- Attack Speed: 0.75s
- Range: 130px
- Damage: 1
- Pierce: 2
- Projectile: Dart (homing within range)

#### Monkey Buccaneer
- Base Cost: $500
- Must be placed on water
- Attack Speed: 1.0s (grapes), 1.0s (darts)
- Range: 120px
- Dual attack: darts (2 pierce) + grapes (5 pierce, shorter range)

#### Monkey Ace
- Base Cost: $800
- Flies in circular pattern around rally point
- Attack Speed: 1.68s
- Damage: 1
- Pierce: 5
- Fires 8 darts radially while flying

#### Heli Pilot
- Base Cost: $1600
- Follows mouse cursor or patrol modes
- Attack Speed: 0.57s
- Damage: 1
- Pierce: 3

#### Mortar Monkey
- Base Cost: $750
- Targets a fixed location on the map
- Attack Speed: 2.0s
- Damage: 1
- Pierce: 40 (AoE explosion radius 40px)

#### Dartling Gunner
- Base Cost: $850
- Aims toward mouse cursor
- Attack Speed: 0.2s
- Damage: 1
- Pierce: 1
- High fire rate, low accuracy (spread angle +/- 15 degrees)

### 4.3 Magic Towers

#### Wizard Monkey
- Base Cost: $375
- Attack Speed: 1.1s
- Range: 130px
- Damage: 1
- Pierce: 3
- Projectile: Magic bolt (follows curved path)

#### Super Monkey
- Base Cost: $2500
- Attack Speed: 0.06s (fastest in game)
- Range: 170px
- Damage: 1
- Pierce: 1
- Projectile: Dart (very high fire rate)

#### Ninja Monkey
- Base Cost: $500
- Attack Speed: 0.7s
- Range: 130px
- Damage: 1
- Pierce: 2
- Has innate camo detection
- Projectile: Shuriken (seeks targets)

#### Alchemist
- Base Cost: $550
- Attack Speed: 2.0s
- Range: 90px
- Damage: 1
- Pierce: 15 (acid splash)
- Key upgrades buff nearby towers

#### Druid
- Base Cost: $425
- Attack Speed: 1.1s
- Range: 130px
- Damage: 1
- Pierce: 1
- Fires thorns

### 4.4 Support Towers

#### Banana Farm
- Base Cost: $1250
- Produces bananas each round worth cash
- Base production: $80 per round (4 bananas x $20 each)
- Player must click bananas to collect (auto-collect radius: 0px base)

#### Spike Factory
- Base Cost: $1000
- Places spike piles on the track
- Attack Speed: 4.0s
- Damage: 1
- Pierce: 5 per pile
- Spike piles persist until used or round ends

#### Monkey Village
- Base Cost: $1200
- Range: 130px (buff radius)
- Buffs all towers in range
- Base effect: +10% range to all towers in radius

#### Engineer Monkey
- Base Cost: $400
- Attack Speed: 0.7s
- Range: 110px
- Damage: 1
- Pierce: 3
- Can deploy sentries and traps

## 5. Heroes

Heroes are unique towers that level up during the game. Only one hero per game. They gain XP from pops and round completions.

### 5.1 Quincy (Starter Hero)
- Cost: $540
- Base Damage: 1
- Base Range: 130px
- Attack Speed: 0.95s
- Pierce: 3

| Level | XP Required | Bonus                                        |
|-------|-------------|----------------------------------------------|
| 1     | 0           | Base stats                                   |
| 2     | 180         | +5% range                                    |
| 3     | 460         | Rapid Shot ability (burst of arrows)          |
| 4     | 1000        | +1 pierce                                    |
| 5     | 1860        | +1 damage                                    |
| 6     | 3280        | +1 pierce                                    |
| 7     | 5180        | Attack speed 0.75s                           |
| 8     | 8320        | +10% range                                   |
| 9     | 9380        | +1 damage                                    |
| 10    | 13620       | Storm of Arrows ability (massive AoE)        |
| 11    | 16380       | +2 pierce                                    |
| 12    | 14400       | +1 damage                                    |
| 13    | 16650       | Attack speed 0.5s                            |
| 14    | 14940       | +10% range                                   |
| 15    | 16380       | +2 damage                                    |
| 16    | 17820       | Storm of Arrows enhanced                     |
| 17    | 19260       | +3 pierce                                    |
| 18    | 20700       | +2 damage                                    |
| 19    | 16470       | +10% range                                   |
| 20    | 17280       | All abilities enhanced, +5 damage            |

### 5.2 Gwendolin
- Cost: $725
- Attack: Flamethrower (short range, AoE)
- Range: 90px
- Abilities: Cocktail of Fire (Lv3), Firestorm (Lv10)

### 5.3 Obyn Greenfoot
- Cost: $650
- Attack: Nature's wrath (magic bolt)
- Range: 130px
- Buffs magic towers in range
- Abilities: Brambles (Lv3), Wall of Trees (Lv10)

## 6. Economy System

### 6.1 Income
- Starting cash: $650 (Easy), $650 (Medium), $600 (Hard), $500 (Impoppable)
- Cash per pop: $1 per RBE
- End of round bonus: $100 + current_round
- Banana Farm income: Based on upgrades
- Sell value: 70% of total spent (tower + upgrades)

### 6.2 Difficulty Multipliers

| Difficulty  | Cost Mult | Starting Cash | Starting Lives | Rounds  |
|-------------|-----------|---------------|----------------|---------|
| Easy        | 0.85      | 650           | 200            | 1-40    |
| Medium      | 1.00      | 650           | 150            | 1-60    |
| Hard        | 1.08      | 600           | 100            | 3-80    |
| Impoppable  | 1.20      | 500           | 1              | 6-100   |

### 6.3 Game Modes
- Standard: Normal rules
- Deflation: Fixed cash, no income
- Apopalypse: All rounds continuous, no breaks
- Reverse: Bloons travel path in reverse
- Half Cash: Earn 50% cash from all sources
- Double HP MOABs: MOAB-class HP doubled
- ABR (Alternate Bloons Rounds): Different round compositions
- CHIMPS: No continues, hearts lost, income, monkey knowledge, powers, selling

## 7. Round System

### 7.1 Round Structure
Each round sends a predefined set of bloons. Bloons spawn from the entrance point at intervals.

Example rounds:
```
Round 1:  20 Red bloons, 1.0s spacing
Round 2:  30 Red bloons, 0.8s spacing
Round 3:  5 Red + 20 Blue, 0.6s spacing
Round 4:  30 Blue bloons, 0.6s spacing
Round 5:  5 Blue + 25 Red, 0.5s spacing
Round 6:  15 Green bloons, 0.7s spacing
Round 7:  20 Green + 5 Red, 0.5s spacing
Round 8:  10 Blue + 20 Red, 0.4s spacing
Round 10: 6 Yellow + 10 Green, 0.4s spacing
Round 13: 50 Blue + 25 Green, 0.3s spacing
Round 15: 20 Pink + 15 Yellow, 0.3s spacing
Round 20: 6 Black + 4 White, 0.4s spacing
Round 24: Camo Green (30), 0.3s spacing
Round 28: 15 Lead bloons, 0.5s spacing
Round 30: 30 Zebra + 10 Rainbow, 0.3s spacing
Round 33: 20 Rainbow + Regrow Yellows, 0.3s spacing
Round 38: 10 Ceramic + 20 Rainbow, 0.3s spacing
Round 40: 1 MOAB
Round 46: 3 MOAB
Round 50: 5 MOAB + 30 Ceramic
Round 60: 1 BFB + 4 MOAB
Round 70: 3 BFB + 10 MOAB
Round 75: 1 ZOMG
Round 80: 2 ZOMG + 6 BFB
Round 85: 3 DDT (camo, lead, black properties)
Round 90: 5 DDT + 2 ZOMG
Round 95: 10 DDT + 3 ZOMG + 20 BFB
Round 100: 1 BAD
```

### 7.2 Round Ramping
After round 80, bloon speed increases:
- Rounds 81-100: speed *= 1.0 + (round - 80) * 0.02
- Rounds 101-150: speed *= 1.5 + (round - 100) * 0.01
- Rounds 151+: speed *= 2.0 + (round - 150) * 0.02

After round 80, MOAB HP also scales:
- HP multiplier: 1.0 + (round - 80) * 0.05

## 8. Map System

### 8.1 Map Categories
- Beginner: Long paths, single track, easy placement
- Intermediate: Medium paths, some water, obstacles
- Advanced: Short paths, multiple entrances, limited space
- Expert: Very short paths, complex terrain, minimal placement

### 8.2 Map Properties
```
Map {
  name: String
  difficulty: Beginner|Intermediate|Advanced|Expert
  path: List<BezierCurve>          // Main bloon path
  water_zones: List<Polygon>       // Where water towers can be placed
  obstacle_zones: List<Polygon>    // Where towers cannot be placed
  removable_obstacles: List<{polygon, cost}>  // Obstacles that can be removed for cash
  line_of_sight_blockers: List<Polygon>  // Block projectiles
  entrances: List<Point>           // Where bloons enter
  exits: List<Point>               // Where bloons exit
}
```

### 8.3 Example Map: Monkey Meadow (Beginner)
```
+--------------------------------------------------+
|                                                    |
|     ___                                            |
|    /   \         _____                             |
|   | ENT |------>|     |                            |
|    \___/        | pond|                            |
|        \        |_____|                            |
|         \                                          |
|          \_________                                |
|                    \                               |
|                     \        ____                  |
|                      \______|    |                 |
|                              |   |                 |
|           ___________________|   |                 |
|          /                       |                 |
|         /                ________|                 |
|        /                /                          |
|       |                /                           |
|       |               /                            |
|        \_____________/--------> EXIT               |
|                                                    |
+--------------------------------------------------+
```

## 9. Targeting System

### 9.1 Targeting Priorities
Each tower can be set to one of four targeting modes:
- **First**: Target the bloon closest to the exit (furthest along path)
- **Last**: Target the bloon closest to the entrance (least progress)
- **Strong**: Target the bloon with the highest RBE
- **Close**: Target the bloon closest to the tower (Euclidean distance)

### 9.2 Target Acquisition Algorithm
```
function acquireTarget(tower, bloons, mode):
    validTargets = bloons.filter(b =>
        distance(tower.pos, b.pos) <= tower.range
        AND (tower.hasCamoDetect OR NOT b.isCamo)
        AND b.isAlive
    )
    if validTargets.empty: return null

    switch mode:
        FIRST:  return validTargets.maxBy(b => b.pathProgress)
        LAST:   return validTargets.minBy(b => b.pathProgress)
        STRONG: return validTargets.maxBy(b => b.RBE)
        CLOSE:  return validTargets.minBy(b => distance(tower.pos, b.pos))
```

## 10. Projectile System

### 10.1 Projectile Types
- **Straight**: Travels in a line from tower to target position
- **Seeking**: Homes in on target bloon, turns at limited rate
- **AoE**: Explodes on contact, damaging all bloons in radius
- **Zone**: Affects all bloons within tower range (no projectile)
- **Boomerang**: Curved path, returns to tower
- **Mortar**: Lobbed to target location with travel time

### 10.2 Projectile Properties
```
Projectile {
  speed: float          // pixels per frame
  damage: int           // damage per hit
  pierce: int           // number of bloons it can hit
  lifetime: float       // seconds before despawn
  aoe_radius: float     // explosion radius (0 for non-AoE)
  can_pop_lead: bool    // can damage lead bloons
  can_pop_frozen: bool  // can damage frozen bloons
  damage_type: Normal|Sharp|Explosive|Fire|Cold|Plasma|Energy
  status_effects: List<StatusEffect>
}
```

### 10.3 Damage Type Interactions
| Damage Type | Cannot Pop     | Extra Damage To |
|-------------|----------------|-----------------|
| Sharp       | Lead           | -               |
| Explosive   | Black, Zebra   | -               |
| Cold        | White, Zebra   | -               |
| Fire        | Purple         | Lead (melts)    |
| Normal      | -              | -               |
| Plasma      | Purple         | -               |
| Energy      | -              | -               |

## 11. Lives System

- Bloons that exit the path cost lives equal to their RBE
- Red = 1 life, Blue = 2 lives, MOAB = 616 lives, BAD = 55760 lives
- When lives reach 0: Game Over
- Some upgrades/abilities can regenerate lives

## 12. Upgrade System Rules

### 12.1 Cross-Path Restrictions
- Each tower has 3 upgrade paths
- Maximum of 2 paths can have upgrades
- One path can go up to Tier 5
- The second path can go up to Tier 2
- Third path must remain at Tier 0

Example valid configurations for Dart Monkey:
- 5/2/0, 5/0/2, 0/5/2, 2/5/0, 2/0/5, 0/2/5
- 5/0/0, 0/5/0, 0/0/5, 3/2/0, etc.

Invalid: 3/3/0 (both paths > tier 2), 1/1/1 (three paths upgraded)

### 12.2 Upgrade Cost Application
Upgrade costs are modified by difficulty multiplier:
- `actualCost = baseCost * difficultyMultiplier`
- Costs are rounded to nearest $5

## 13. User Interface Layout

### 13.1 Main Game Screen
```
+------------------------------------------------------------------+
| [Pause] [FF>>] [Play]  Round: 47/80   Cash: $12,450   Lives: 143 |
+------------------------------------------------------------------+
|                                                                    |
|                                                                    |
|                    GAME MAP AREA                                   |
|                    (1920 x 880)                                    |
|                                                                    |
|                                                                    |
|                                                                    |
+------------------------------------------------------------------+
|  [Dart] [Tack] [Boom] [Bomb] [Ice] [Glue] | [Hero] | [Powers]    |
|  [Snip] [Sub]  [Bucc] [Ace]  [Heli][Mort]  | $540  |             |
|  [Wiz]  [Sup]  [Ninj] [Alch] [Dru]         |       |             |
|  [Farm] [Spik] [Vill] [Eng]                |       |             |
+------------------------------------------------------------------+
```

### 13.2 Tower Selection Panel
When a placed tower is clicked:
```
+---------------------------+
| Dart Monkey (2/0/3)       |
| Pops: 1,247               |
|                            |
| [Path 1]  [Path 2]  [Path3]|
| [Tier 3]  [-----]  [Tier 4]|
| Spike-o   ------   Sharp   |
|                             |
| Next: Juggernaut $1,800    |
| [UPGRADE]                  |
|                             |
| Targeting: [First v]       |
| Priority:  [Normal]        |
|                             |
| [Sell: $689]               |
+-----------------------------+
```

### 13.3 Speed Controls
- Normal speed: 1x
- Fast Forward: 3x
- Can toggle between speeds during gameplay

## 14. Collision Detection

### 14.1 Bloon-Projectile Collision
- Bloons have circular hitbox (radius based on type: 8-24px)
- Projectiles use point-circle or circle-circle intersection
- Check: `distance(projectile.pos, bloon.pos) < bloon.radius + projectile.radius`

### 14.2 Tower Placement Validation
```
function canPlaceTower(tower, position, map):
    // Check not on path
    for segment in map.path:
        if distanceToSegment(position, segment) < tower.radius + pathWidth:
            return false

    // Check not on obstacles
    for obstacle in map.obstacles:
        if pointInPolygon(position, obstacle):
            return false

    // Check not overlapping other towers
    for other in placedTowers:
        if distance(position, other.pos) < tower.radius + other.radius:
            return false

    // Check water requirement
    if tower.requiresWater:
        if not anyPolygonContains(map.waterZones, position):
            return false
    elif not tower.requiresWater:
        if anyPolygonContains(map.waterZones, position):
            return false

    return true
```

## 15. Special Mechanics

### 15.1 Abilities
- Cooldown-based active abilities (unlocked at Tier 3 and 5)
- Activated by clicking ability icon in bottom-left
- Cooldown timer shown as radial fill on icon
- Cannot be used during prep phase

### 15.2 Monkey Knowledge
Passive bonuses unlocked between games:
- Primary: +200 starting cash, faster attacks, etc.
- Military: Free dart monkey, camo detection, etc.
- Magic: Cheaper magic towers, extra pierce, etc.
- Support: Extra starting lives, better sell price, etc.

### 15.3 Power-ups (Consumables)
- Cash Drop: +$2500
- Monkey Boost: All towers attack 2x for 15s
- Thrive: +$600 per round for 5 rounds
- Time Stop: Freeze all bloons for 10s

## 16. Audio and Visual Effects

### 16.1 Sound Effects
- Bloon pop: "pop" sound with pitch variation based on layer
- MOAB damage: Deep thud
- Tower placement: Click/thunk
- Upgrade: Ascending chime
- Ability activation: Whoosh + type-specific effect
- Round start: Horn/alarm
- Game over: Deflating sound

### 16.2 Visual Effects
- Pop animation: Small burst particles in bloon color
- MOAB damage: Crack textures appear on hull
- Upgrade: Golden sparkle effect on tower
- Ability: Full-screen flash + effect
- Critical hit: Large number popup with yellow glow

## 17. Save System

### 17.1 Auto-Save
- Game state saved between each round
- Save includes: all tower positions, upgrades, targeting
- Round number, cash, lives, hero level
- All bloon positions if saving mid-round

### 17.2 Save Data Structure
```
SaveData {
  map_id: String
  difficulty: Difficulty
  mode: GameMode
  round: int
  cash: int
  lives: int
  towers: List<TowerSave>
  hero: HeroSave
  bloons_on_screen: List<BloonSave>  // only if mid-round
}
```

## 18. Performance Optimization Notes

### 18.1 Spatial Partitioning
- Use grid-based spatial hash for collision detection
- Grid cell size: 64px
- Only check towers against bloons in nearby cells

### 18.2 Object Pooling
- Pool bloon objects to avoid garbage collection spikes
- Pool projectile objects
- Pre-allocate pools based on estimated max concurrent entities:
  - Bloons: 2000
  - Projectiles: 500
  - Particles: 1000

### 18.3 Rendering Optimization
- Layer-based rendering: background, path, towers, bloons, projectiles, UI
- Only redraw changed layers
- Batch similar sprites together
- Use sprite sheets for bloon animations (4 frames per type)

## 19. Freeplay Mode

After completing all standard rounds, the game continues with procedurally generated rounds:
- Bloon types and counts scale exponentially
- MOAB-class bloons become more common
- Fortified and Camo properties applied more frequently
- Speed ramping continues
- No defined end point

Formula for freeplay round RBE:
```
baseRBE = round * round * 50
moabChance = min(0.9, 0.1 + (round - 100) * 0.008)
fortifiedChance = min(0.5, (round - 100) * 0.005)
camoChance = min(0.7, (round - 80) * 0.007)
```

## 20. Win/Loss Conditions

### 20.1 Win Condition
- Complete all rounds for the selected difficulty
- Easy: Round 40, Medium: Round 60, Hard: Round 80, Impoppable: Round 100

### 20.2 Loss Condition
- Lives reach 0 at any point
- In CHIMPS mode: Lose 1 life = game over

### 20.3 Rewards
- XP earned based on rounds completed and difficulty
- Monkey Money earned: `difficulty_mult * rounds_completed * 2`
- First-time completion medals (Bronze/Silver/Gold/Black border)
