# Advance Wars — Complete Game Specification

## 1. Game Overview

Advance Wars is a turn-based strategy game played on grid-based maps where two or more armies compete by producing units from bases, capturing properties, and destroying the enemy forces. Features a rock-paper-scissors unit effectiveness system, terrain bonuses, CO powers, and fog of war.

- Genre: Turn-based strategy
- Grid: Variable map sizes (typically 15x10 to 30x20)
- Perspective: Top-down 2D
- Players: 2-4 (human or AI)
- Input: Cursor-based tile selection
- Victory: Rout (destroy all enemy units) or HQ Capture

## 2. Technical Foundation

### 2.1 Grid System
- Tile-based grid
- Each tile: 16x16 pixels (GBA), scalable
- Tile types affect movement cost and defense

### 2.2 Turn Structure
```
Day N:
  Player 1 Turn:
    1. Start of turn: Income from properties, CO power charge
    2. For each unit (in any order):
       a. Move unit (within movement range)
       b. Action: Attack, Capture, Load, Drop, Wait, Join, Supply, Launch
    3. Produce new units from Bases/Ports/Airports
    4. End turn

  Player 2 Turn:
    (same as above)

  Player 3, 4 if applicable...

  Next day (Day N+1)
```

### 2.3 Win Conditions
- **Rout**: Destroy all enemy units
- **HQ Capture**: Capture the enemy headquarters
- **Lab Capture** (some maps): Capture specific buildings

## 3. Terrain System

### 3.1 Terrain Types

| Terrain      | Def Stars | Move Cost | Special                          |
|             |           | Inf/Mech/Tread/Tire/Air/Ship    |                                  |
|-------------|-----------|----------------------------------|----------------------------------|
| Plain       | 1         | 1/1/1/2/1/-                      | Basic terrain                    |
| Road        | 0         | 1/1/1/1/1/-                      | Fastest ground                   |
| Wood        | 2         | 1/1/2/3/1/-                      | Concealment in Fog               |
| Mountain    | 4         | 2/1/-/-/1/-                      | Best defense, +3 vision in Fog   |
| River       | 0         | 2/1/-/-/1/-                      | Slows infantry                   |
| Sea         | 0         | -/-/-/-/1/1                      | Ships and air only               |
| Reef        | 1         | -/-/-/-/1/2                      | Sea defense, concealment         |
| Shoal       | 0         | 1/1/1/1/1/1                      | Beach landing                    |
| City        | 3         | 1/1/1/1/1/-                      | +2000 gold/turn, heals ground    |
| Base        | 3         | 1/1/1/1/1/-                      | +1000 gold/turn, produces ground |
| Airport     | 3         | 1/1/1/1/1/-                      | +1000 gold/turn, produces air    |
| Port        | 3         | 1/1/1/1/1/1                      | +1000 gold/turn, produces naval  |
| HQ          | 4         | 1/1/1/1/1/-                      | +1000 gold/turn, lose if captured|
| Pipe        | -         | -/-/-/-/-/-                      | Impassable wall                  |
| Pipe Seam   | 0         | -/-/-/-/-/-                      | Breakable (99 HP)                |
| Silo        | 3         | 1/1/1/1/1/-                      | Launch missile (one-time)        |

### 3.2 Defense Calculation
```
defense_reduction = terrain_stars * unit_hp_percent * 10
// Example: Unit at 80% HP on 3-star city:
// reduction = 3 * 0.8 * 10 = 24% damage reduction
```

### 3.3 Income
- Each owned property generates gold at start of turn
- City: 1000 gold
- Base: 1000 gold
- Airport: 1000 gold
- Port: 1000 gold
- HQ: 1000 gold
- Properties change ownership when captured

## 4. Unit System

### 4.1 Unit Properties
```
Unit {
  type: UnitType
  hp: 1-100 (displayed as 1-10 in UI, internal is 1-100)
  fuel: int (consumed per tile moved, per day for air/naval)
  ammo: int (primary weapon uses)
  move_range: int
  move_type: Infantry | Mech | Tread | Tire | Air | Ship | Transport
  vision: int (tiles visible in Fog of War)
  cost: int (gold to produce)
  weapons: Primary (ammo-limited) and/or Secondary (unlimited)
}
```

### 4.2 Ground Units

#### Infantry
- Cost: 1000
- Move: 3
- Vision: 2
- Fuel: 99
- HP: 100
- Move Type: Infantry
- Primary Weapon: None
- Secondary Weapon: Machine Gun (vs Infantry, Mech, Recon, APC)
- Special: Can capture buildings (20 capture points, applies HP/10 per turn)

| Target        | Machine Gun Damage |
|---------------|-------------------|
| Infantry      | 55                |
| Mech          | 45                |
| Recon         | 12                |
| APC           | 14                |
| Tank          | 5                 |
| Md Tank       | 1                 |
| Neotank       | 1                 |
| Copter        | 7                 |

#### Mech (Mechanized Infantry)
- Cost: 3000
- Move: 2
- Vision: 2
- Fuel: 70
- Ammo: 3
- Move Type: Mech
- Primary Weapon: Bazooka (vs vehicles)
- Secondary Weapon: Machine Gun
- Special: Can capture buildings, traverse mountains

| Target        | Bazooka Damage | Machine Gun Damage |
|---------------|---------------|-------------------|
| Infantry      | -             | 65                |
| Mech          | -             | 55                |
| Recon         | 85            | 18                |
| Tank          | 55            | 6                 |
| Md Tank       | 25            | 1                 |
| Neotank       | 15            | 1                 |
| APC           | 75            | 20                |
| Artillery     | 70            | 32                |
| Rockets       | 85            | 35                |
| Anti-Air      | 65            | 6                 |
| Missile       | 85            | 35                |

#### Recon
- Cost: 4000
- Move: 8
- Vision: 5
- Fuel: 80
- Move Type: Tire
- Secondary Weapon: Machine Gun (strong vs infantry)
- Special: High vision, fast on roads

#### Tank
- Cost: 7000
- Move: 6
- Vision: 3
- Fuel: 70
- Ammo: 9
- Move Type: Tread
- Primary Weapon: Cannon
- Secondary Weapon: Machine Gun

| Target        | Cannon Damage |
|---------------|--------------|
| Infantry      | 75           |
| Mech          | 70           |
| Recon         | 85           |
| Tank          | 55           |
| Md Tank       | 15           |
| Neotank       | 15           |
| APC           | 75           |
| Artillery     | 70           |
| Rockets       | 85           |
| Anti-Air      | 65           |
| Missile       | 85           |
| Copter        | -            |
| Bomber        | -            |

#### Medium Tank (Md Tank)
- Cost: 16000
- Move: 5
- Vision: 1
- Fuel: 50
- Ammo: 8
- Move Type: Tread
- Powerful cannon + machine gun

| Target        | Cannon Damage |
|---------------|--------------|
| Infantry      | 105          |
| Tank          | 75           |
| Md Tank       | 55           |
| Neotank       | 45           |

#### Neotank
- Cost: 22000
- Move: 6
- Vision: 1
- Fuel: 99
- Ammo: 9
- Move Type: Tread
- Strongest tank unit

| Target        | Cannon Damage |
|---------------|--------------|
| Infantry      | 125          |
| Tank          | 105          |
| Md Tank       | 75           |
| Neotank       | 55           |

#### APC (Armored Personnel Carrier)
- Cost: 5000
- Move: 6
- Vision: 1
- Fuel: 70
- Move Type: Tread
- No weapons
- Special: Carries 1 infantry/mech, supplies adjacent units

#### Artillery
- Cost: 6000
- Move: 5
- Vision: 1
- Fuel: 50
- Ammo: 9
- Move Type: Tread
- Primary Weapon: Cannon (indirect fire, range 2-3)
- Cannot move and attack in same turn
- Cannot counter-attack

#### Rockets
- Cost: 15000
- Move: 5
- Vision: 1
- Fuel: 50
- Ammo: 6
- Move Type: Tire
- Primary Weapon: Rockets (indirect fire, range 3-5)
- Cannot move and attack in same turn

#### Missiles
- Cost: 12000
- Move: 4
- Vision: 5
- Fuel: 50
- Ammo: 6
- Move Type: Tire
- Primary Weapon: Anti-Air Missiles (indirect fire, range 3-5, air only)
- Devastating vs air units

#### Anti-Air
- Cost: 8000
- Move: 6
- Vision: 2
- Fuel: 60
- Ammo: 9
- Move Type: Tread
- Primary Weapon: Vulcan Cannon (strong vs air and infantry)

| Target        | Vulcan Damage |
|---------------|--------------|
| Infantry      | 105          |
| Mech          | 105          |
| Copter        | 120          |
| Fighter       | 65           |
| Bomber        | 75           |
| Transport Copter| 120       |

### 4.3 Air Units

#### Battle Copter (B Copter)
- Cost: 9000
- Move: 6
- Vision: 3
- Fuel: 99 (-2/day)
- Ammo: 6
- Move Type: Air
- Primary: Air-to-ground missiles (vs vehicles)
- Secondary: Machine Gun (vs infantry, copters)

| Target        | Missiles Damage | MG Damage |
|---------------|----------------|-----------|
| Infantry      | -              | 75        |
| Mech          | -              | 75        |
| Tank          | 55             | 6         |
| Md Tank       | 25             | 1         |
| Anti-Air      | 25             | 6         |
| Copter        | -              | 65        |
| Fighter       | -              | -         |
| Bomber        | -              | -         |

#### Transport Copter (T Copter)
- Cost: 5000
- Move: 6
- Vision: 2
- Fuel: 99 (-2/day)
- No weapons
- Carries 1 infantry/mech

#### Fighter
- Cost: 20000
- Move: 9
- Vision: 2
- Fuel: 99 (-5/day)
- Ammo: 9
- Move Type: Air
- Primary: Air-to-air missiles
- Dominates air combat, cannot attack ground

| Target        | Missiles Damage |
|---------------|----------------|
| Copter        | 100            |
| Fighter       | 55             |
| Bomber        | 100            |

#### Bomber
- Cost: 22000
- Move: 7
- Vision: 2
- Fuel: 99 (-5/day)
- Ammo: 9
- Move Type: Air
- Primary: Bombs (devastating vs ground/naval)

| Target        | Bombs Damage |
|---------------|-------------|
| Infantry      | 110         |
| Mech          | 110         |
| Tank          | 105         |
| Md Tank       | 95          |
| Neotank       | 90          |
| Anti-Air      | 95          |
| Battleship    | 75          |
| Cruiser       | 85          |
| Submarine     | 95          |

### 4.4 Naval Units

#### Battleship
- Cost: 28000
- Move: 5
- Vision: 2
- Fuel: 99 (-1/day)
- Ammo: 9
- Move Type: Ship
- Primary: Cannons (indirect fire, range 2-6)
- Most powerful indirect unit

#### Cruiser
- Cost: 18000
- Move: 6
- Vision: 3
- Fuel: 99 (-1/day)
- Ammo: 9
- Move Type: Ship
- Primary: Anti-Air missiles (vs air)
- Secondary: Anti-Sub depth charges
- Can carry 2 copters

#### Submarine (Sub)
- Cost: 20000
- Move: 5
- Vision: 5
- Fuel: 60 (-1/day, -5/day when dived)
- Ammo: 6
- Move Type: Ship
- Primary: Torpedoes (vs ships)
- Can dive (invisible except to adjacent units)

#### Lander
- Cost: 12000
- Move: 6
- Vision: 1
- Fuel: 99 (-1/day)
- Move Type: Transport
- No weapons
- Carries 2 ground units, deploys on shoals

## 5. Damage Formula

### 5.1 Base Damage Calculation
```
function calculateDamage(attacker, defender):
    baseDamage = damageChart[attacker.type][defender.type]  // from damage tables

    // Attacker strength based on HP
    attackerHPPercent = attacker.hp / 100

    // Defender terrain defense
    terrainStars = getTerrainStars(defender.position)
    terrainDefense = terrainStars * (defender.hp / 100) * 10

    // CO bonus (attack/defense modifiers)
    attackBonus = attacker.co.attackBonus  // e.g., 1.1 for 110%
    defenseBonus = defender.co.defenseBonus

    damage = baseDamage * (attackerHPPercent / 100) * attackBonus
    damage = damage - (damage * terrainDefense / 100) * defenseBonus

    // Luck factor
    luck = random(0, attacker.co.luckBonus)  // usually 0-9
    damage += luck

    // Bad luck (some COs)
    badLuck = random(0, attacker.co.badLuck)
    damage -= badLuck

    return clamp(damage, 0, 100)
```

### 5.2 Counter-Attack
- Defending unit counter-attacks with reduced HP (after taking damage)
- Counter-attack uses same formula but with the defender's now-reduced HP
- Indirect units cannot counter-attack
- Air units cannot counter ground attacks (unless they have ground weapons)

## 6. Capture System

### 6.1 Capture Mechanics
- Only Infantry and Mech can capture
- Each building has 20 capture points
- Each turn on the building: capture progress += unit_hp / 10 (rounded down)
  - Full HP (100) unit captures 10 points per turn
  - Half HP (50) unit captures 5 points per turn
- Building captured when capture points reach 20
- Moving off building resets capture progress
- Captured building changes to captor's color/faction

### 6.2 Building Benefits
- All buildings provide 1000 gold per turn
- Bases, Airports, Ports allow unit production
- Cities, Bases, Airports, Ports heal ground units 2 HP/turn (20 internal HP)
- Ports also heal naval units

## 7. CO (Commanding Officer) System

### 7.1 CO Mechanics
- Each army is led by a CO with unique abilities
- Passive abilities affect all units always
- CO Power charges by dealing/receiving damage
- Two power levels: CO Power and Super CO Power (SCOP)

### 7.2 CO Roster

#### Andy
- Passive: No special advantages or disadvantages (balanced)
- CO Power Cost: 3 stars
- CO Power "Hyper Repair": All units heal 2 HP
- SCOP Cost: 6 stars
- SCOP "Hyper Upgrade": All units heal 5 HP, +10% attack, +10% defense

#### Max
- Passive: Direct units +20% attack, indirect units -10% attack, -1 indirect range
- CO Power Cost: 3 stars
- CO Power "Max Force": Direct units +30% attack (total +50%)
- SCOP Cost: 6 stars
- SCOP "Max Blast": Direct units +50% attack (total +70%), +1 move

#### Sami
- Passive: Infantry +30% attack, capture speed x1.5, vehicles -10% attack
- CO Power Cost: 3 stars
- CO Power "Double Time": Infantry +1 move, +20% attack
- SCOP Cost: 6 stars
- SCOP "Victory March": Infantry +2 move, instant capture (capture progress = 20)

#### Olaf
- Passive: Unaffected by snow, all units normal
- CO Power Cost: 3 stars
- CO Power "Blizzard": Causes snow weather for 1 day (all enemies -1 move, -30% fuel/day)
- SCOP Cost: 7 stars
- SCOP "Winter Fury": 2 HP damage to all enemy units + blizzard

#### Grit
- Passive: Indirect units +20% attack, +1 range; direct units -20% attack
- CO Power Cost: 3 stars
- CO Power "Snipe Attack": Indirect +30% attack, +1 more range
- SCOP Cost: 6 stars
- SCOP "Super Snipe": Indirect +50% attack, +2 more range

#### Eagle
- Passive: Air units +15% attack, -20% fuel cost; naval units -30% attack
- CO Power Cost: 3 stars
- CO Power "Lightning Drive": Non-infantry units gain second action (half-strength)
- SCOP Cost: 9 stars
- SCOP "Lightning Strike": All non-infantry units get full second action

#### Drake
- Passive: Naval units +10% attack, +1 defense; air units -30% attack
- CO Power Cost: 4 stars
- CO Power "Tsunami": 1 HP damage to all enemies, halve fuel
- SCOP Cost: 7 stars
- SCOP "Typhoon": 2 HP damage to all enemies, halve fuel, causes rain

#### Kanbei
- Passive: All units +30% attack, +30% defense; units cost 120%
- CO Power Cost: 4 stars
- CO Power "Morale Boost": +40% attack, +40% defense
- SCOP Cost: 7 stars
- SCOP "Samurai Spirit": Counter-attack at 2x strength + stat boost

#### Sonja
- Passive: Hidden HP display for enemy, enhanced terrain stars in Fog; -10% luck
- CO Power Cost: 3 stars
- CO Power "Enhanced Vision": +1 vision, see into woods/reefs
- SCOP Cost: 5 stars
- SCOP "Counter Break": All attacks are counter-attacks (strike after enemy)

#### Sturm
- Passive: All units +20% attack, +20% defense, no terrain movement penalties
- CO Power Cost: 6 stars
- CO Power "Meteor Strike": 8 HP damage in 13-tile diamond on strongest cluster
- SCOP Cost: 10 stars
- SCOP "Meteor Strike II": 12 HP damage in larger area + stat boost

### 7.3 CO Power Charge
```
chargeGained = damageDealt * 0.5 (attacking)
chargeGained = damageReceived * 1.0 (defending)
// Measured in HP units of damage
// CO Power costs in "stars" where 1 star ~ 9000 charge points
```

## 8. Weather System

| Weather | Effect                                              | Duration |
|---------|-----------------------------------------------------|----------|
| Clear   | Normal conditions                                   | Default  |
| Rain    | -1 vision in Fog, +10% fuel cost                   | 1-3 days |
| Snow    | -1 move for all units, +20% fuel cost               | 1-3 days |
| Sandstorm| -1 vision, -30% attack for air and naval           | 1-3 days |

Weather can be triggered by CO powers or be part of map design.

## 9. Fog of War

### 9.1 Vision Rules
- Each unit has a vision range (in tiles)
- Terrain, friendly buildings, and allied units are always visible
- Enemy units only visible if within vision range of a friendly unit
- Mountains give +3 vision to infantry/mech standing on them
- Woods and reefs hide units (only revealed when adjacent or by specific abilities)
- Fog only applies in Fog of War mode (not all maps)

### 9.2 Hidden Units
- Units in forests/reefs are invisible even in vision range
- Must be adjacent to reveal hidden units
- Some COs can see into forests (Sonja's SCOP)

## 10. Map Design

### 10.1 Map Properties
```
Map {
  name: String
  width: int (10-30)
  height: int (10-20)
  players: int (2-4)
  terrain: 2D array of TileType
  properties: List<{type, owner, position}>  // buildings with initial ownership
  predeployed_units: List<{type, owner, position, hp}>
  fog: bool
  weather: Weather
  starting_funds: int per player
}
```

### 10.2 Example Map: Little Island (2 Player)
```
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| S | S | S | S | S | S | S | S | S | S | S | S | S | S | S |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| S |Sh |Pl |Rd |Cy1|Rd |Pl |Rd |Rd |Rd |Rd |Cy2|Rd |Sh | S |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| S |Sh |Wd |Pl |Bs1|Pl |Wd |Pl |Wd |Pl |Bs2|Pl |Wd |Sh | S |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| S |Sh |Pl |Wd |HQ1|Rd |Wd |Mt |Wd |Rd |HQ2|Wd |Pl |Sh | S |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| S |Sh |Wd |Pl |Bs1|Pl |Wd |Pl |Wd |Pl |Bs2|Pl |Wd |Sh | S |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| S |Sh |Pl |Rd |Cy1|Rd |Pl |Rd |Rd |Rd |Rd |Cy2|Rd |Sh | S |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| S | S | S | S | S | S | S | S | S | S | S | S | S | S | S |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

Legend: S=Sea, Sh=Shoal, Pl=Plain, Rd=Road, Wd=Wood, Mt=Mountain
        Cy=City, Bs=Base, HQ=Headquarters
        1=Player 1, 2=Player 2
```

## 11. Production System

### 11.1 Unit Production
- Units produced from owned Bases (ground), Airports (air), Ports (naval)
- Must have enough funds (gold)
- New units appear on the building tile
- New units cannot act on the turn they are produced
- Cannot produce if building is occupied

### 11.2 Unit Costs
| Unit          | Cost   | Produced From |
|---------------|--------|---------------|
| Infantry      | 1000   | Base          |
| Mech          | 3000   | Base          |
| Recon         | 4000   | Base          |
| APC           | 5000   | Base          |
| Artillery     | 6000   | Base          |
| Tank          | 7000   | Base          |
| Anti-Air      | 8000   | Base          |
| Missiles      | 12000  | Base          |
| Rockets       | 15000  | Base          |
| Md Tank       | 16000  | Base          |
| Neotank       | 22000  | Base          |
| T Copter      | 5000   | Airport       |
| B Copter      | 9000   | Airport       |
| Fighter       | 20000  | Airport       |
| Bomber        | 22000  | Airport       |
| Lander        | 12000  | Port          |
| Cruiser       | 18000  | Port          |
| Submarine     | 20000  | Port          |
| Battleship    | 28000  | Port          |

## 12. AI Behavior

### 12.1 AI Strategy
```
function aiTurn(ai):
    // Phase 1: Evaluate threats
    threats = identifyThreats(ai.units, enemy.units)

    // Phase 2: Production
    if ai.funds >= 7000 and needsOffensiveUnits():
        produce(TANK)
    elif ai.funds >= 3000 and needsCapturers():
        produce(MECH)
    elif ai.funds >= 1000:
        produce(INFANTRY)

    // Phase 3: Unit actions (priority order)
    for unit in ai.units.sortByPriority():
        if unit.isCapturing:
            continue  // keep capturing
        elif unit.canCapture and nearbyUnownedProperty:
            moveToCapture(unit)
        elif unit.canAttack and profitableTarget:
            moveAndAttack(unit, bestTarget)
        elif unit.isIndirect and goodPosition:
            wait(unit)
        else:
            moveTowardObjective(unit)
```

### 12.2 AI Target Selection
```
function selectTarget(unit, targets):
    bestScore = -999
    for target in targets:
        score = predictDamage(unit, target) * 2
        score -= predictCounterDamage(target, unit)
        score += targetValueBonus(target)  // higher for expensive units
        if canKill(unit, target): score += 50
        if target.isCapturing: score += 30  // priority to stop capture
        if score > bestScore:
            bestTarget = target
            bestScore = score
    return bestTarget
```

## 13. User Interface

### 13.1 Map Screen
```
+------------------------------------------------------------------+
| Day 5   |  Player 1 (Andy)  | Funds: 14,000  | Units: 8/50      |
+------------------------------------------------------------------+
|                                                                    |
|              [Grid map with terrain and units]                     |
|                                                                    |
|  Blue squares = Player 1 units                                    |
|  Red squares = Player 2 units                                     |
|                                                                    |
|  Move range = blue highlight                                      |
|  Attack range = red highlight                                     |
|                                                                    |
+------------------------------------------------------------------+
| [Unit Info]  Infantry  HP: 7  Fuel: 68  Ammo: -                  |
| [Terrain]    City (3 stars)   Owner: Player 1                     |
+------------------------------------------------------------------+
```

### 13.2 Combat Preview
```
+-----------------------------------+
|  Tank (7HP)  vs  Md Tank (10HP)   |
|  Damage: ~35%                     |
|  Counter: ~55%                    |
|  Terrain: Plain (1*)  Wood (2*)   |
+-----------------------------------+
```

### 13.3 Production Menu
```
+---------------------------+
| BASE - Production Menu    |
|                            |
| Infantry    1000  [Build] |
| Mech        3000  [Build] |
| Recon       4000  [Build] |
| APC         5000  [Build] |
| Artillery   6000  [Build] |
| Tank        7000  [Build] |
| Anti-Air    8000  [Build] |
|                            |
| Funds: 14,000             |
+---------------------------+
```

## 14. Campaign Structure

### 14.1 Campaign Mode
- 18 missions with increasing difficulty
- Story-driven with dialogue between missions
- New COs introduced as allies and enemies
- Tutorial missions teach mechanics gradually

### 14.2 War Room
- Standalone maps for scoring
- Ranked by speed, power, and technique
- S-Rank requires optimal play

### 14.3 Scoring
```
Speed Score = max(0, 100 - (turns - parTurns) * 5)
Power Score = (damageDealt / damageReceived) * 20, capped at 100
Technique Score = (unitsLost == 0) ? 100 : max(0, 100 - unitsLost * 10)
Total Score = (Speed + Power + Technique) / 3
Rank: S (95+), A (80+), B (60+), C (40+), D (<40)
```

## 15. Multiplayer / VS Mode

### 15.1 Versus Rules
- 2-4 players on selected map
- Each player selects a CO
- Turn order by player number
- Same rules as campaign
- Can enable/disable Fog of War
- Funds can be set to: Normal, Increased, Decreased

### 15.2 Map Editor
- Players can create custom maps
- Place terrain, buildings, pre-deployed units
- Set starting funds and weather
- Share maps via link codes

## 16. Supply and Fuel

### 16.1 Fuel Consumption
- Ground units: 0 fuel when stationary, variable per tile moved (usually 1 per tile)
- Air units: Consume fuel daily (-2 for copters, -5 for planes), plus movement
- Naval units: Consume fuel daily (-1), plus movement
- Submarines consume -5 fuel/day when dived
- Unit destroyed when fuel reaches 0 (air/naval crash)

### 16.2 Resupply
- APC: Supplies all adjacent allied units (refuel + rearm)
- Properties: Ground units on owned cities/bases are resupplied at start of turn
- Ports: Naval units are resupplied
- Airports: Air units are resupplied

## 17. Join Mechanic
- Two units of the same type on the same tile can "Join"
- HP combines (capped at 100)
- Fuel and ammo average
- Excess HP converted to funds
- Useful for consolidating damaged units

## 18. Save System
- Save between any turn
- Multiple save slots
- Campaign progress tracked separately from VS mode
- Rankings and scores persist
