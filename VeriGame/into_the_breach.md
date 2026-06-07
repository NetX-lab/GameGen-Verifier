# Into the Breach — Complete Game Specification

## 1. Game Overview

Into the Breach is a turn-based tactical strategy game played on 8x8 grids where the player controls a squad of 3 mechs defending civilian buildings from giant alien creatures called Vek. The game features perfect information (all enemy moves are telegraphed), time travel mechanics for replayability, and rogue-like progression.

- Genre: Turn-based tactics / puzzle
- Grid: 8x8 tiles
- Squad Size: 3 mechs
- Campaign Length: 4 islands + final mission
- Input: Mouse click on grid tiles
- Key Design: Perfect information — all enemy attacks are shown before they execute

## 2. Technical Foundation

### 2.1 Grid System
- 8x8 tile grid per mission
- Each tile: 80x80 pixels
- Tile types: Ground, Water, Mountain, Forest, Ice, Sand, Lava, Chasm
- Coordinate system: (x, y) where (0,0) is bottom-left
- Isometric rendering with 2D sprites

### 2.2 Turn Structure
```
Each turn:
  1. ENEMY_INTENT: All Vek telegraph their attacks (shown on grid)
  2. PLAYER_PHASE: Player moves and attacks with up to 3 mechs
     - Each mech gets 1 move + 1 action per turn
     - Actions: attack, repair, or special ability
  3. ENEMY_PHASE: All Vek execute their telegraphed attacks simultaneously
  4. ENVIRONMENT_PHASE: Environmental effects trigger (emerging Vek, tides, etc.)
  5. SPAWN_PHASE: New Vek emerge from spawn points (shown 1 turn in advance)
```

### 2.3 Core Design Principle
All enemy attacks are shown before the player acts. The player's goal is to manipulate enemy positions (via push/pull mechanics) to redirect or cancel enemy attacks, protecting buildings and their own mechs.

## 3. Tile Types

| Tile Type | Properties                                              | Visual    |
|-----------|---------------------------------------------------------|-----------|
| Ground    | Normal traversal, can be damaged                        | Grass/dirt|
| Water     | Drowns non-flying units, deals 99 damage                | Blue      |
| Mountain  | Blocks movement, blocks projectiles, indestructible     | Gray rock |
| Forest    | Catches fire when hit, becomes fire tile for 1 turn     | Trees     |
| Ice       | Cracks when stepped on, breaks to water on second step  | Light blue|
| Sand      | Units sink and are immobilized for 1 turn               | Tan       |
| Lava      | Deals 1 damage per turn to non-flying units             | Orange    |
| Chasm     | Kills any non-flying unit that enters                   | Black void|
| Building  | Has HP, provides grid power, must be defended           | Structures|
| Spawn     | Vek emerge here next turn (shown as cracked ground)     | Cracks    |
| Fire      | Deals 1 damage per turn, lasts 1-3 turns                | Flames    |

### 3.1 Tile Interactions
- **Fire + Forest**: Forest becomes fire tile
- **Fire + Ice**: Ice melts to water
- **Push into Water/Chasm**: Unit drowns/falls (instant kill for non-flying)
- **Push into Mountain**: Push is blocked, unit takes 1 bump damage
- **Push into another unit**: Both units take 1 bump damage, neither moves

## 4. Mech Squads

### 4.1 Rift Walkers (Starter Squad)

#### Combat Mech
- HP: 3
- Move: 3 tiles
- Class: Brute
- Weapon: Titan Fist
  - Damage: 2
  - Range: Melee (1 tile)
  - Effect: Pushes target 1 tile in attack direction
  - Upgrade 1 (+1 reactor): +1 damage
  - Upgrade 2 (+1 reactor): +2 damage

#### Cannon Mech
- HP: 3
- Move: 3 tiles
- Class: Ranged
- Weapon: Taurus Cannon
  - Damage: 1
  - Range: Unlimited straight line (blocked by mountains/units)
  - Effect: Pushes target 1 tile backward
  - Upgrade 1 (+1 reactor): +1 damage
  - Upgrade 2 (+2 reactor): +2 damage

#### Artillery Mech
- HP: 2
- Move: 3 tiles
- Class: Ranged
- Weapon: Artemis Artillery
  - Damage: 1 (2 to self tile from pushback)
  - Range: Lob over obstacles, any tile in range (2-8 tiles)
  - Effect: Pushes adjacent units away from target tile
  - Upgrade 1 (+1 reactor): +1 damage
  - Upgrade 2 (+1 reactor): +2 damage

### 4.2 Rusting Hulks

#### Jet Mech
- HP: 2
- Move: 4 tiles (Flying)
- Class: Brute
- Weapon: Aerial Bombs
  - Damage: 1
  - Range: Any tile the mech flies over during movement
  - Effect: Damages tiles along flight path

#### Rocket Mech
- HP: 3
- Move: 3 tiles
- Class: Ranged
- Weapon: Rocket Barrage
  - Damage: 2
  - Range: 2-7 tiles straight line
  - Effect: Hits 2 tiles in a row, pushes targets sideways

#### Pulse Mech
- HP: 3
- Move: 3 tiles
- Class: Science
- Weapon: Repulse
  - Damage: 0
  - Range: Self (AoE around mech)
  - Effect: Pushes all adjacent units 1 tile away, creates smoke on self

### 4.3 Zenith Guard

#### Laser Mech
- HP: 3
- Move: 3 tiles
- Class: Ranged
- Weapon: Burst Beam
  - Damage: 1-3 (increases with each tile hit in line)
  - Range: Unlimited straight line
  - Effect: Hits all tiles in line, damage increases per tile

#### Charge Mech
- HP: 3
- Move: 3 tiles
- Class: Brute
- Weapon: Ramming Speed
  - Damage: 2
  - Range: Mech charges in straight line, stops at target
  - Effect: Mech takes 1 self-damage, pushes target 1 tile

#### Defense Mech
- HP: 3
- Move: 4 tiles
- Class: Science
- Weapon: Shield Projector
  - Damage: 0
  - Range: 1 tile (melee)
  - Effect: Grants Shield to target (absorbs next hit)
  - Also has: Attraction Pulse (pulls all adjacent units 1 tile toward self)

### 4.4 Blitzkrieg

#### Lightning Mech
- HP: 3
- Move: 3 tiles
- Class: Ranged
- Weapon: Electric Whip
  - Damage: 2
  - Range: 2 tile line
  - Effect: Chains to adjacent enemies

#### Hook Mech
- HP: 3
- Move: 3 tiles
- Class: Science
- Weapon: Meat Hook
  - Damage: 1
  - Range: Unlimited straight line
  - Effect: Pulls target to adjacent tile next to mech

#### Boulder Mech
- HP: 3
- Move: 3 tiles
- Class: Brute
- Weapon: Rock Launch
  - Damage: 2
  - Range: 1 tile (melee)
  - Effect: Throws target 2-5 tiles

### 4.5 Additional Squads
- **Steel Judoka**: Focus on displacement without damage
- **Flame Behemoths**: Fire-based attacks
- **Frozen Titans**: Ice and freeze mechanics
- **Hazardous Mechs**: A.C.I.D. and smoke effects
- **Secret Squad**: Unlocked by completing all achievements

## 5. Vek (Enemy Types)

### 5.1 Common Vek

| Vek Type      | HP | Attack | Range    | Effect                  | Move |
|---------------|-----|--------|----------|-------------------------|------|
| Hornet        | 2   | 1      | Melee    | Basic attack            | 4(fly)|
| Scarab        | 2   | 1      | 3 line   | Ranged shot             | 2    |
| Firefly       | 3   | 1      | 1-7 line | Ranged, hits all in line| 2    |
| Leaper        | 1   | 1      | Jump 2-5 | Jumps to target         | 0    |
| Beetle        | 4   | 2      | Melee    | Charges in line         | 3    |
| Centipede     | 3   | 1      | Melee    | Pushes target           | 2    |
| Crab          | 3   | 1      | Melee    | Flips target behind self| 2    |
| Digger        | 2   | 1      | Melee    | Burrows, emerges behind | 0    |
| Spider        | 2   | 0      | N/A      | Spawns 1-HP eggs        | 3    |
| Blob          | 1   | 3      | Self     | Explodes on death AoE   | 3    |
| Burrower      | 3   | 1      | Melee    | Burrows underground     | 3    |
| Moth          | 2   | 2      | Melee    | Flying, applies smoke   | 4(fly)|

### 5.2 Alpha Vek (Stronger versions)
Alpha versions appear in later islands:
- +1 to +3 HP
- +1 damage
- Additional effects (push, AoE, armor)
- Visually larger with red markings

### 5.3 Boss Vek
| Boss           | HP | Special                                    |
|----------------|----|--------------------------------------------|
| Psion Tyrant   | 2  | All Vek regenerate 1 HP per turn           |
| Psion Abomination| 2| All Vek explode on death (1 AoE damage)   |
| Psion Soldier  | 2  | All Vek gain +1 HP (once)                  |
| Hive Leader    | 6  | Spawns additional Vek each turn            |
| Large Goo      | 3  | Splits into 2 smaller Goo when killed      |
| Horror         | 7  | Moves toward power grid, massive attack    |

### 5.4 Vek Behavior AI
```
function vekTurn(vek):
    // Priority: Attack buildings > Attack mechs > Move toward buildings
    targets = getAllValidTargets(vek)

    prioritized = targets.sortBy(target =>
        if target.isBuilding: priority = 0  // Highest priority
        elif target.isMech: priority = 1
        else: priority = 2
    )

    chosenTarget = prioritized[0]

    if canAttack(vek, chosenTarget):
        telegraph(vek.attack, chosenTarget.position)
    else:
        moveToward(chosenTarget)
        if canAttackAfterMove(vek, chosenTarget):
            telegraph(vek.attack, chosenTarget.position)
```

### 5.5 Spawning System
- Each turn, 0-2 spawn points appear (cracked ground tiles)
- Spawn points are visible for 1 full turn before Vek emerges
- If a unit is standing on a spawn point when Vek emerges:
  - The emerging Vek takes 1 damage
  - The unit on the tile is pushed to an adjacent tile
  - If no adjacent tile available, unit takes 1 damage
- Spawn density increases with island difficulty

## 6. Grid Power and Buildings

### 6.1 Grid Power
- Grid Power represents the collective power of civilization
- Starting Grid Power: 7 (out of 7 max by default)
- Each building destroyed: -1 Grid Power
- Grid Power reaches 0: Game Over (civilization collapses)
- Grid Power persists across missions on the same run

### 6.2 Buildings
- Each mission map has 3-7 buildings
- Buildings have 1 HP (destroyed by any damage)
- Shield can protect buildings (absorbs 1 hit)
- Buildings are always on ground tiles
- Some buildings are "objective buildings" tied to bonus objectives

### 6.3 Grid Defense
- 15% chance per building to resist damage (at 7 power)
- Resist chance scales with remaining power:
```
resistChance = basePower * 0.15 + bonuses
```

## 7. Campaign Structure

### 7.1 Island Progression
```
Start: Choose 1 of 4 islands
  -> Complete 4 missions on chosen island
  -> Complete island boss mission
  -> Choose next island (2nd)
  -> Complete 4 missions
  -> Complete boss
  -> Choose 3rd island
  -> Complete 4 missions
  -> Complete boss
  -> Choose 4th island
  -> Complete 4 missions
  -> Complete boss
  -> Final Mission (Volcanic Hive)
```

### 7.2 Islands

| Island     | Environment          | Special Tiles     | Difficulty |
|------------|---------------------|-------------------|-----------|
| Archive    | Grasslands/forests  | Forest fires      | 1-2       |
| R.S.T.     | Frozen tundra       | Ice, cryo mines   | 2-3       |
| Pinnacle   | Desert/sand         | Sand, smoke       | 3-4       |
| Detritus   | Toxic wasteland     | A.C.I.D., lava    | 4-5       |

### 7.3 Mission Structure
Each island has a pool of ~8 missions, player picks 4 to play:
```
Mission {
  map: 8x8 grid layout
  turns: 4-5
  vek_count: 3-7 starting
  vek_spawns_per_turn: 0-2
  buildings: 3-7
  objectives: List<Objective>  // 1 primary + 1-2 bonus
  environment: Optional<EnvironmentEffect>
  reward: Reputation (1-3)
}
```

### 7.4 Objectives

**Primary (always present):**
- Defend the Grid: Survive all turns without losing all grid power

**Bonus objectives (1-2 per mission):**
| Objective                    | Reputation |
|------------------------------|-----------|
| Kill X Vek                   | 1         |
| Block X spawning Vek         | 1         |
| Protect specific building    | 1         |
| Don't lose any Grid Power    | 1         |
| Kill all enemies             | 2         |
| Protect train/convoy         | 1         |
| Protect NPC unit             | 1         |
| Terraform X tiles            | 1         |

### 7.5 Reputation Spending
After completing an island, spend reputation at the store:
| Item                    | Cost | Effect                           |
|-------------------------|------|----------------------------------|
| +1 Grid Power           | 1    | Restore 1 grid power             |
| +1 Reactor Core         | 1    | Power up mech upgrades           |
| Random Weapon            | 1    | New weapon for any mech          |
| Specific Pilot           | 2    | Recruit a new pilot              |
| +2 Grid Power           | 3    | Restore 2 grid power             |

## 8. Reactor System

### 8.1 Reactor Cores
- Each mech has a reactor with limited power
- Starting reactor power: varies by mech (typically 1-3)
- Additional reactor cores earned from missions/shops
- Reactor power is allocated to upgrade slots

### 8.2 Upgrade Slots
Each mech can upgrade:
- **Primary Weapon**: 1-3 upgrade tiers (+damage, +effects)
- **Move**: +1 or +2 move (1-2 reactor each)
- **HP**: +1 or +2 HP (1 reactor each)
- **Secondary Weapon/Passive**: If equipped (1-3 reactor per tier)

### 8.3 Reactor Allocation
```
MechReactor {
  total_cores: int (base + earned)
  allocations: {
    weapon_upgrade_1: 0 or 1
    weapon_upgrade_2: 0 or 1
    move_upgrade: 0 or 1
    hp_upgrade_1: 0 or 1
    hp_upgrade_2: 0 or 1
    secondary_weapon: 0-3
  }
  // Sum of allocations <= total_cores
}
```

## 9. Pilot System

### 9.1 Pilot Mechanics
- Each mech has 1 pilot
- Pilots gain XP from missions (25 XP per mission completed)
- Pilots level up and gain perks
- If mech is destroyed, pilot ejects (lost for rest of island)
- One pilot can travel back in time on a failed run

### 9.2 Pilot Levels
| Level | XP Required | Perk Unlocked                        |
|-------|-------------|--------------------------------------|
| 1     | 0           | Base pilot ability                   |
| 2     | 25          | +1 random stat (Move, HP, Reactor, Grid Def)|
| 3     | 75          | +1 random stat                       |

### 9.3 Named Pilots and Abilities
| Pilot          | Ability                                      |
|----------------|----------------------------------------------|
| Ralph Karlsson | +2 Move on first turn of mission             |
| Isaac Jones    | Armored (half damage, rounded up)            |
| Henry Kwan     | +3 Move (replaces normal move)               |
| Abe Isamu      | Armored                                      |
| Chen Rong      | +1 Grid Def on kills                         |
| Harold Schmidt | +1 Reactor Core                              |
| Silica         | Double attack when not moved                 |
| Mafan          | Shield on first turn, Flying                 |
| Bethany Jones  | +1 Grid Power at start                       |
| Camila Vera    | Immune to fire, smoke, A.C.I.D.              |
| Prospero       | Flying, +2 HP                                |
| Archimedes     | +1 Move, +1 Reactor                          |

### 9.4 Time Travel
- When the game is lost, the player can send 1 pilot back in time
- That pilot retains their level and perks
- All other progress is reset
- New run begins with the time-traveled pilot placed in any mech

## 10. Status Effects

| Effect    | Duration | Visual       | Mechanic                              |
|-----------|----------|-------------|---------------------------------------|
| Fire      | Until ext| Flames      | 1 damage per turn, spreads to forest  |
| Freeze    | 1 turn   | Ice crystal | Cannot act, takes no damage           |
| Shield    | Until hit| Blue glow   | Absorbs next instance of damage       |
| Smoke     | 1 turn   | Gray cloud  | Cannot attack (but can move)          |
| A.C.I.D.  | Permanent| Green drip  | Takes double damage from all sources  |
| Web       | 1 turn   | White web   | Cannot move (can still attack)        |
| Armor     | Permanent| Metal plates| Takes half damage (rounded up)        |

## 11. Push/Pull Mechanics

### 11.1 Push Resolution
```
function resolvePush(unit, direction):
    targetTile = unit.position + direction

    if targetTile.isBlocked():  // Mountain, edge of map, or occupied
        if targetTile.isOccupied():
            unit.takeDamage(1)  // Bump damage
            targetTile.occupant.takeDamage(1)  // Bump damage
        elif targetTile.isMountain() or targetTile.isEdge():
            unit.takeDamage(1)  // Bump damage
        return  // No movement

    unit.moveTo(targetTile)

    if targetTile.isWater() and not unit.isFlying():
        unit.kill()  // Drown
    elif targetTile.isChasm() and not unit.isFlying():
        unit.kill()  // Fall
    elif targetTile.isFire():
        unit.applyStatus(FIRE)
    elif targetTile.isLava():
        unit.takeDamage(1)
```

### 11.2 Push Directions
- Cardinal only (up, down, left, right)
- Diagonal pushes do not exist in base game
- Push distance is always 1 tile unless specified

## 12. Combat Resolution

### 12.1 Attack Resolution Order
```
Player Phase:
  - Player chooses actions for each mech (order matters!)
  - Each action resolves immediately before next mech acts
  - Push/damage applied instantly

Enemy Phase:
  - All enemy attacks resolve simultaneously
  - Damage is applied at the same time
  - Push effects chain (pushed into another push resolves sequentially)
```

### 12.2 Damage Calculation
```
finalDamage = baseDamage
if target.hasACID: finalDamage *= 2
if target.hasArmor: finalDamage = ceil(finalDamage / 2)
if target.hasShield: finalDamage = 0; removeShield()
target.HP -= finalDamage
if target.HP <= 0: target.die()
```

## 13. User Interface Layout

### 13.1 Mission Screen
```
+------------------------------------------------------------------+
| Grid Power: [|||||||---] 7/10    Turn: 2/5    Objectives          |
+------------------------------------------------------------------+
|          |                                       |                 |
|  Mech 1  |          8 x 8 GRID                  | Enemy Info      |
|  HP: 3/3 |                                       | Firefly         |
|  [Wep]   |   M1  .  .  .  V1  .  .  .          | HP: 3           |
|          |   .   .  B  .  .   .  B  .           | Attack: 3-tile  |
|  Mech 2  |   .   .  .  .  .   .  .  .           | line            |
|  HP: 2/3 |   .   V2 .  M2 .   .  .  B           |                 |
|  [Wep]   |   .   .  .  .  .   .  .  .           |                 |
|          |   .   .  B  .  .   V3 .  .           |                 |
|  Mech 3  |   .   .  .  .  M3  .  .  .           |                 |
|  HP: 2/2 |   .   .  .  .  .   .  .  .           |                 |
|  [Wep]   |                                       |                 |
+------------------------------------------------------------------+
| [Undo Move]  [End Turn]  [Reset Turn]            Time Pod: (3,5)  |
+------------------------------------------------------------------+

M = Mech, V = Vek, B = Building, . = Empty ground
```

### 13.2 Attack Preview
When hovering over a target with weapon selected:
- Green overlay on targeted tiles
- Red arrows showing push directions
- Damage numbers shown on affected units
- Building damage warnings highlighted in red
- Friendly fire warnings shown

### 13.3 Island Map
```
+------------------------------------------------------------------+
| ARCHIVE ISLAND                                Corporate HQ: [!]   |
|                                                                    |
|   [Mission 1]----[Mission 2]                                      |
|        \              |                                            |
|     [Mission 3]--[Mission 4]----[BOSS]                            |
|         |              |                                           |
|     [Mission 5]  [Mission 6]                                      |
|                                                                    |
| Completed: 2/4    Grid Power: 6/7    Reputation: 4                |
+------------------------------------------------------------------+
```

## 14. Undo System

### 14.1 Undo Rules
- Player can undo the last mech's move (but not attack)
- Full turn reset available once per mission
- Cannot undo after enemy phase begins
- Time travel pod: reset entire run (rogue-like mechanic)

## 15. Weapon List

### 15.1 Primary Weapons
| Weapon          | Type    | Damage | Range      | Effect              |
|-----------------|---------|--------|-----------|---------------------|
| Titan Fist      | Melee   | 2      | 1 tile    | Push 1              |
| Taurus Cannon   | Ranged  | 1      | Line      | Push 1 backward     |
| Artemis Artillery| Ranged | 1      | Lob 2-8   | Push adjacent away   |
| Electric Whip   | Ranged  | 2      | 2 line    | Chains to adjacent  |
| Flame Thrower   | Ranged  | 0      | 1-3 line  | Sets tiles on fire  |
| Ice Generator   | Ranged  | 0      | Lob 2-7   | Freezes target      |
| Cluster Missiles| Ranged  | 1      | Lob 2-6   | Hits 3x3 area       |
| Grapple Hook    | Ranged  | 0      | Line      | Pulls target adj.   |
| Mercury Fist    | Melee   | 1      | 1 tile    | Pushes all adj.     |
| Science Beam    | Ranged  | 0      | Line      | Removes status      |
| Vortex Fist     | Melee   | 0      | 1 tile    | Flips target behind |
| Janus Cannon    | Ranged  | 1      | 1 tile    | Fires both dirs.    |

### 15.2 Secondary Weapons / Passives
| Equipment        | Reactor | Effect                                |
|------------------|---------|---------------------------------------|
| Viscera Nanobots | 1       | Heal 1 HP when adjacent to Vek kill  |
| Boosters         | 1       | +2 move on first turn                |
| A.C.I.D. Launcher| 1      | Apply A.C.I.D. to target (ranged)    |
| Smoke Bomb       | 1       | Apply Smoke to adjacent tiles        |
| Shield Generator | 1       | Shield self at start of each turn    |
| Auto-Repair      | 1       | Heal 1 HP if no damage taken this turn|

## 16. Scoring System

### 16.1 Score Calculation
```
islandScore = sum(missionScores) + bonusObjectives * 100
missionScore = (turnsRemaining * 50) + (buildingsSaved * 100) + (vekKilled * 25)
totalScore = sum(islandScores) + finalMissionScore + gridPowerBonus
gridPowerBonus = remainingGridPower * 500
```

### 16.2 Victory Conditions
- **Mission Victory**: Survive all turns (4-5 turns per mission)
- **Island Victory**: Complete boss mission
- **Campaign Victory**: Complete final Volcanic Hive mission
- **Game Over**: Grid Power reaches 0

## 17. Final Mission: Volcanic Hive

### 17.1 Structure
- 2-phase mission
- Phase 1: Defend pylons for 5 turns
- Phase 2: Destroy the Vek Hive (boss with 7 HP and shield)
- All 3 mechs participate
- Grid Power still matters

### 17.2 Hive Boss
- HP: 7 (Phase 2)
- Shield regenerates each turn (must be broken first)
- Spawns 2 Vek per turn
- Environmental lava flows each turn
- Victory: Reduce Hive to 0 HP

## 18. Rogue-Like Progression

### 18.1 Per-Run Progression
- Earn reactor cores from missions
- Find weapons from time pods and rewards
- Pilots level up
- Grid power fluctuates based on building defense

### 18.2 Meta-Progression (Across Runs)
- Unlock new squads by completing achievements
- Coins earned from victories unlock random squads
- High scores tracked per squad
- Achievements track specific challenges

### 18.3 Achievement Examples
| Achievement              | Requirement                              | Reward        |
|--------------------------|------------------------------------------|---------------|
| Perfect Island           | Complete island with 0 buildings lost     | +1 Coin       |
| Completion               | Complete the game                        | Unlock squad  |
| Hard Mode Victory        | Win on Hard difficulty                   | +3 Coins      |
| No Mech Deaths           | Complete game without losing a mech      | +2 Coins      |

## 19. Difficulty Settings

| Setting   | Vek HP    | Spawns/Turn | Grid Power | Bonus        |
|-----------|-----------|-------------|-----------|--------------|
| Easy      | -1 HP     | Reduced     | 8         | Extra reactor|
| Normal    | Standard  | Standard    | 7         | -            |
| Hard      | +1-2 HP   | Increased   | 6         | Alpha Vek more common|
| Unfair    | +2-3 HP   | Maximum     | 5         | Boss Vek in normal missions|

## 20. Random Map Generation

### 20.1 Map Generation Algorithm
```
function generateMission(island, difficulty):
    grid = new Grid(8, 8)

    // Place mountains (2-5)
    mountainCount = random(2, 5)
    placeTiles(grid, MOUNTAIN, mountainCount, avoidEdges=true)

    // Place buildings (3-7)
    buildingCount = random(3, 7)
    placeTiles(grid, BUILDING, buildingCount, mustBeOnGround=true, minDistFromEdge=1)

    // Place environment-specific tiles
    if island == ARCHIVE:
        placeForests(grid, random(3, 8))
    elif island == RST:
        placeIce(grid, random(4, 10))
    elif island == PINNACLE:
        placeSand(grid, random(3, 7))
    elif island == DETRITUS:
        placeLava(grid, random(2, 5))

    // Place mech starting positions (near bottom)
    placeMechStarts(grid, 3, row=0 or row=1)

    // Place initial Vek (3-5)
    vekCount = difficulty.baseVek + random(0, 2)
    placeVek(grid, vekCount, avoidMechStarts=true)

    // Place spawn points for turn 1
    placeSpawns(grid, random(1, 2))

    // Place optional time pod
    if random() < 0.3:
        placeTimePod(grid)

    return grid
```

### 20.2 Objective Generation
```
function generateObjectives(mission):
    primary = SURVIVE_ALL_TURNS
    bonus = []

    pool = [KILL_X_VEK, PROTECT_BUILDING, BLOCK_SPAWNS, NO_GRID_DAMAGE, ...]
    bonus.add(randomChoice(pool))
    if random() < 0.5:
        bonus.add(randomChoice(pool - bonus))

    return (primary, bonus)
```

## 21. Visual and Audio Design

### 21.1 Visual Style
- Pixel art with clean, readable sprites
- Mech sprites: 32x32 with detailed animations
- Vek sprites: 24x24 to 48x48 based on size
- Isometric grid with clear tile boundaries
- Attack telegraphs shown as colored overlays (red for damage, yellow for push)

### 21.2 Color Coding
| Element         | Color     | Hex     |
|-----------------|-----------|---------|
| Mech highlight  | Blue      | #4488FF |
| Vek highlight   | Red       | #FF4444 |
| Building        | White     | #FFFFFF |
| Damage preview  | Red       | #FF0000 |
| Push arrow      | Yellow    | #FFCC00 |
| Shield          | Cyan      | #00CCFF |
| Fire            | Orange    | #FF6600 |
| A.C.I.D.        | Green     | #00FF00 |

### 21.3 Sound Design
- Mech movement: Mechanical stomping/rolling
- Weapon fire: Type-specific (energy blast, cannon shot, etc.)
- Vek screech: Alien chittering
- Building destroyed: Crumbling/crash
- Push impact: Thud/crunch
- Turn transition: Subtle chime
- Grid power loss: Warning alarm

## 22. Save System

### 22.1 Auto-Save Points
- Between every turn
- Between every mission
- On island map

### 22.2 Save Data
```
SaveData {
  current_run: {
    islands_completed: List<Island>
    current_island: Island
    missions_completed: int
    grid_power: int
    mechs: List<MechState>
    pilots: List<PilotState>
    reputation: int
    weapons_inventory: List<Weapon>
  }
  meta: {
    squads_unlocked: List<Squad>
    coins: int
    achievements: List<Achievement>
    high_scores: Map<Squad, int>
    time_travel_pilots: List<Pilot>
  }
}
```
