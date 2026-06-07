# Vampire Survivors — Complete Game Specification

## 1. Game Overview

Vampire Survivors is a single-player auto-attacking rogue-like survival game where the player moves a character on a 2D plane, automatically attacking waves of monsters that grow increasingly numerous and powerful over a 30-minute run. The player levels up by collecting experience gems dropped by enemies, choosing weapons and passive items to create powerful synergies.

- Genre: Rogue-like survival / bullet heaven
- Perspective: Top-down 2D
- Resolution: 1920x1080, pixel art style
- Target Framerate: 60 FPS
- Input: Movement only (WASD/arrow keys/joystick). All attacks are automatic.
- Run Duration: 30 minutes (death or reaper at 30:00)

## 2. Technical Foundation

### 2.1 World System
- Infinite scrolling 2D plane (procedurally tiled background)
- Camera centered on player
- Visible area: ~960x540 logical units
- Background tiles: 64x64 pixels, repeating patterns
- No walls or obstacles in most stages (some stages have environmental features)

### 2.2 Core Game Loop
```
Each frame (60 FPS):
  1. Process player movement input
  2. Update player position (speed * direction * deltaTime)
  3. Update all weapons (cooldown timers, fire if ready)
  4. Update all projectiles (movement, lifetime)
  5. Update all enemies:
     a. Move toward player
     b. Check collision with player (deal contact damage)
  6. Process projectile-enemy collisions (damage, knockback)
  7. Process enemy deaths (spawn XP gems, items)
  8. Process XP gem pickup (magnetic pull toward player)
  9. Check level-up condition
  10. Spawn new enemies based on timer and wave schedule
  11. Update game timer
  12. Render all entities
```

### 2.3 Game States
- MAIN_MENU: Character select, stage select
- GAMEPLAY: Active run
- LEVEL_UP: Pause game, show upgrade choices
- TREASURE: Chest opened, show rewards
- GAME_OVER: Death screen with stats
- VICTORY: Survived 30 minutes (or killed Death)

## 3. Player Character

### 3.1 Base Stats
```
Character {
  maxHP: float (base varies by character)
  currentHP: float
  moveSpeed: float (base 1.0, modified by passives)
  armor: float (base 0, reduces incoming damage by flat amount)
  might: float (base 1.0, multiplier on all damage)
  area: float (base 1.0, multiplier on weapon AoE size)
  speed: float (base 1.0, multiplier on projectile speed)
  duration: float (base 1.0, multiplier on weapon effect duration)
  cooldown: float (base 1.0, multiplier on weapon cooldown, lower = faster)
  amount: int (base 0, extra projectiles per weapon)
  luck: float (base 1.0, affects critical hits and item drops)
  growth: float (base 1.0, XP gain multiplier)
  greed: float (base 1.0, gold gain multiplier)
  magnet: float (base 0, XP gem attraction radius in px)
  revival: int (base 0, extra lives)
  reroll: int (base 0, reroll level-up options)
  skip: int (base 0, skip level-up screen)
  banish: int (base 0, remove item from future offerings)
  curse: float (base 0, increases enemy speed/HP/count)
}
```

### 3.2 Characters

| Character     | Starting Weapon | Bonus Stats                           | Unlock Condition      |
|---------------|----------------|---------------------------------------|-----------------------|
| Antonio       | Whip           | +10% Might per level (max +50%)       | Default               |
| Imelda        | Magic Wand     | +10% XP Growth per level (max +30%)   | Default               |
| Pasqualina    | Runetracer     | +10% Proj Speed per level (max +30%)  | Default               |
| Gennaro       | Knife          | +1 Amount every 10 levels (max +3)    | Default               |
| Arca          | Fire Wand      | -5% Cooldown per level (max -15%)     | Default               |
| Porta         | Lightning Ring | +10% Area per level (max +30%)        | Reach Lv 10 with any  |
| Dommario      | King Bible     | +10% Duration, +10% Speed, -40% MoveSpd| Kill 5000 enemies   |
| Krochi        | Cross          | +1 Revival, +10% MoveSpeed            | Kill 100,000 enemies  |
| Christine     | Pentagram      | +10% Might, starts at Lv2             | Reach Lv 10 w/ all defaults|
| Pugnala       | Phiera Der Tuphello + Eight The Sparrow | +1% Might every level | Survive 20 min w/ any |
| Poe           | Garlic         | -20% Max HP, +25% pickup magnet       | Kill 3000 enemies     |
| Suor Clerici  | Santa Water    | +0.5 HP/s regen, +30% Duration        | Reach Lv 10 w/ Runetracer|
| Mortaccio     | Bone           | +1 Amount every 20 levels (max +3)    | Kill 3000 Skeletons   |
| Lama          | Axe            | +10% Might, +10% MoveSpeed, -10% curse| Reach Lv 10 with 5 characters|

## 4. Weapon System

### 4.1 Base Weapons

#### Whip
- Base Damage: 10
- Cooldown: 1.15s
- Area: Horizontal sweep in front/behind player
- Hits: All enemies in sweep area
- Pierce: Infinite (hits all in area)
- Knockback: 0

| Level | Damage | Cooldown | Area     | Extra Effect           |
|-------|--------|----------|----------|------------------------|
| 1     | 10     | 1.15s    | 1.0x     | Base                   |
| 2     | 10     | 1.15s    | 1.0x     | Can hit behind player  |
| 3     | 15     | 1.15s    | 1.0x     | -                      |
| 4     | 15     | 1.15s    | 1.2x     | -                      |
| 5     | 20     | 1.15s    | 1.2x     | -                      |
| 6     | 20     | 1.15s    | 1.4x     | -                      |
| 7     | 25     | 1.15s    | 1.4x     | -                      |
| 8     | 25     | 1.15s    | 1.6x     | Max level              |

**Evolution: Bloody Tear** (Whip + Hollow Heart)
- Damage: 40
- Steals HP on hit (heals 1 HP per hit)
- Critical hits deal 2x damage
- Infinite pierce

#### Magic Wand
- Base Damage: 10
- Cooldown: 1.0s
- Projectile: Fires toward nearest enemy
- Pierce: 0 (hits 1 enemy, disappears)
- Speed: Medium
- Knockback: 0

| Level | Damage | Cooldown | Amount | Pierce |
|-------|--------|----------|--------|--------|
| 1     | 10     | 1.0s     | 1      | 0      |
| 2     | 10     | 1.0s     | 1      | 1      |
| 3     | 15     | 1.0s     | 1      | 1      |
| 4     | 15     | 1.0s     | 1      | 2      |
| 5     | 20     | 1.0s     | 1      | 2      |
| 6     | 20     | 1.0s     | 1      | 3      |
| 7     | 25     | 1.0s     | 1      | 3      |
| 8     | 25     | 0.8s     | 1      | 4      |

**Evolution: Holy Wand** (Magic Wand + Empty Tome)
- Fires continuously with no cooldown delay
- Homes on enemies
- Pierce: Infinite

#### Knife
- Base Damage: 7
- Cooldown: 0.35s
- Projectile: Fires in movement direction
- Pierce: 0
- Speed: Fast
- Amount: 1

| Level | Damage | Cooldown | Amount | Pierce |
|-------|--------|----------|--------|--------|
| 1     | 7      | 0.35s    | 1      | 0      |
| 2     | 7      | 0.35s    | 2      | 0      |
| 3     | 10     | 0.35s    | 2      | 0      |
| 4     | 10     | 0.35s    | 3      | 0      |
| 5     | 13     | 0.35s    | 3      | 1      |
| 6     | 13     | 0.35s    | 4      | 1      |
| 7     | 16     | 0.35s    | 4      | 1      |
| 8     | 16     | 0.30s    | 5      | 2      |

**Evolution: Thousand Edge** (Knife + Bracer)
- Massive projectile count
- Very fast fire rate
- Pierce: 3

#### Fire Wand
- Base Damage: 20
- Cooldown: 1.5s
- Projectile: Fires at random enemy in range
- Pierce: 0
- Speed: Slow
- Creates fire trail on hit (AoE damage over time)

| Level | Damage | Cooldown | Effect                |
|-------|--------|----------|-----------------------|
| 1     | 20     | 1.5s     | Base                  |
| 2     | 20     | 1.5s     | +20% area             |
| 3     | 30     | 1.5s     | -                     |
| 4     | 30     | 1.5s     | +20% area             |
| 5     | 40     | 1.5s     | -                     |
| 6     | 40     | 1.5s     | +20% area             |
| 7     | 50     | 1.3s     | -                     |
| 8     | 50     | 1.1s     | +20% area             |

**Evolution: Hellfire** (Fire Wand + Spinach)
- Deals massive AoE damage
- Fires multiple projectiles
- Pierces all enemies

#### King Bible
- Base Damage: 10
- Cooldown: 3.5s
- Behavior: Orbits around player
- Duration: 3.5s per orbit cycle
- Amount: 1 orbiting bible
- Pierce: Infinite (while orbiting)

| Level | Damage | Amount | Speed   | Duration |
|-------|--------|--------|---------|----------|
| 1     | 10     | 1      | 1.0x    | 3.5s     |
| 2     | 10     | 2      | 1.0x    | 3.5s     |
| 3     | 10     | 2      | 1.2x    | 4.0s     |
| 4     | 15     | 2      | 1.2x    | 4.0s     |
| 5     | 15     | 3      | 1.2x    | 4.5s     |
| 6     | 15     | 3      | 1.4x    | 4.5s     |
| 7     | 20     | 3      | 1.4x    | 5.0s     |
| 8     | 20     | 4      | 1.6x    | 5.5s     |

**Evolution: Unholy Vespers** (King Bible + Spellbinder)
- Never expires (permanent orbit)
- Massive damage
- 6 orbiting projectiles

#### Garlic
- Damage: 5
- Cooldown: Constant (aura effect)
- Area: Circle around player (60px radius base)
- Effect: Damages enemies in area, knockback, reduces enemy resistance
- Pierce: Infinite

| Level | Damage | Area  | Knockback | Extra Effect              |
|-------|--------|-------|-----------|---------------------------|
| 1     | 5      | 1.0x  | Small     | Base                      |
| 2     | 5      | 1.0x  | Small     | +10% knockback            |
| 3     | 5      | 1.2x  | Med       | -                         |
| 4     | 7      | 1.2x  | Med       | +10% knockback            |
| 5     | 7      | 1.4x  | Large     | Reduces enemy resistance  |

**Evolution: Soul Eater** (Garlic + Pummarola)
- Steals HP on hit
- Massive area
- Huge knockback

#### Cross (Boomerang)
- Damage: 15
- Cooldown: 1.5s
- Projectile: Throws in front, returns like boomerang
- Pierce: Infinite (going and returning)
- Amount: 1

#### Axe
- Damage: 20
- Cooldown: 1.5s
- Projectile: Thrown upward in arc, falls back down
- Pierce: Infinite
- Random horizontal spread

#### Lightning Ring
- Damage: 10
- Cooldown: 2.0s
- Behavior: Strikes random enemy on screen
- Pierce: N/A (direct hit)
- Amount: 1

#### Santa Water
- Damage: 5 per tick
- Cooldown: 3.0s
- Behavior: Drops damaging zone at random location near player
- Duration: 3.0s
- Area: Circle (40px radius)
- Ticks every 0.5s

#### Runetracer
- Damage: 10
- Cooldown: 3.0s
- Projectile: Bounces off screen edges
- Pierce: Infinite
- Duration: 5.0s
- Speed: Fast

#### Pentagram
- Damage: 9999
- Cooldown: 30.0s
- Behavior: Kills ALL enemies on screen
- Chance to erase XP gems: 50% (reduced by Luck)

#### Bone
- Damage: 8
- Cooldown: 0.6s
- Projectile: Thrown in movement direction, bounces back
- Pierce: 3
- Amount: 1

### 4.2 Passive Items

| Passive Item     | Max Lv | Effect Per Level                           | Evolution Pair     |
|------------------|--------|--------------------------------------------|--------------------|
| Spinach          | 5      | +10% Might                                 | Fire Wand          |
| Armor            | 3      | +1 Armor (flat damage reduction)           | -                  |
| Hollow Heart     | 5      | +10% Max HP                                | Whip               |
| Pummarola        | 5      | +0.2 HP/s regeneration                     | Garlic             |
| Empty Tome       | 5      | -8% Cooldown                               | Magic Wand         |
| Candelabrador    | 5      | +10% Area                                  | Santa Water        |
| Bracer           | 5      | +10% Projectile Speed                      | Knife              |
| Spellbinder      | 5      | +10% Duration                              | King Bible         |
| Duplicator       | 5      | +1 Amount (extra projectile per weapon)     | -                  |
| Wings            | 5      | +10% Move Speed                            | -                  |
| Attractorb       | 5      | +50% Magnet (XP pickup range)              | -                  |
| Clover           | 5      | +10% Luck                                  | -                  |
| Crown            | 5      | +8% XP Growth                              | -                  |
| Stone Mask       | 5      | +10% Greed (gold bonus)                    | -                  |
| Skull O'Maniac   | 5      | +10% Curse (more/harder enemies, more XP)  | -                  |
| Tiragisu         | 2      | +1 Revival                                 | -                  |
| Torrona's Box    | 5      | +1% Might/Area/Speed/Duration/Cooldown per level | -            |

### 4.3 Evolution Rules
- Weapon must be at max level (Level 8)
- Required passive must be in inventory (any level)
- Open a treasure chest after meeting both conditions
- Evolved weapon replaces the base weapon
- Only one evolution per weapon

### 4.4 Weapon Combinations (Unions)
Some weapons combine into new weapons:
| Weapon A         | Weapon B        | Union Weapon     | Requirement        |
|------------------|-----------------|------------------|--------------------|
| Peachone         | Ebony Wings     | Vandalier        | Both at max level  |
| Phiera Der T.    | Eight Sparrow   | Phieraggi        | Both at max level  |

## 5. Enemy System

### 5.1 Enemy Properties
```
Enemy {
  name: String
  hp: float
  speed: float
  damage: float (contact damage per tick)
  xp_value: float
  knockback_resist: float (0.0 - 1.0)
  sprite_size: int
  special: Optional<String>
}
```

### 5.2 Common Enemies

| Enemy          | Base HP | Speed | Damage | XP  | Special                  |
|----------------|---------|-------|--------|-----|--------------------------|
| Bat            | 5       | 1.5   | 1      | 1   | Fast, weak               |
| Skeleton       | 10      | 0.8   | 2      | 1   | Slow, average            |
| Zombie         | 20      | 0.5   | 3      | 2   | Very slow, tanky         |
| Ghost          | 8       | 1.2   | 2      | 2   | Phases through terrain   |
| Mummy          | 30      | 0.6   | 4      | 3   | Tanky                    |
| Witch          | 12      | 1.0   | 3      | 3   | Occasionally teleports   |
| Werewolf       | 25      | 1.8   | 5      | 4   | Fast, strong             |
| Medusa         | 40      | 0.7   | 4      | 5   | Tanky, slows on contact  |
| Mantis         | 15      | 2.0   | 3      | 3   | Very fast                |
| Flower         | 50      | 0.3   | 6      | 5   | Very slow, very tanky    |
| Dragonfly      | 8       | 2.5   | 2      | 2   | Extremely fast           |
| Golem          | 100     | 0.4   | 8      | 10  | Boss-tier normal         |
| Mage           | 20      | 0.9   | 5      | 4   | Fires projectiles        |

### 5.3 Elite / Mini-Boss Enemies

| Enemy          | HP    | Speed | Damage | XP  | Special                     |
|----------------|-------|-------|--------|-----|-----------------------------|
| Blue Bat Swarm | 80    | 1.5   | 5      | 15  | Group of 5 linked bats      |
| Giant Skeleton | 200   | 0.5   | 10     | 25  | Drops chest on death         |
| Vampire Lord   | 300   | 1.0   | 12     | 50  | Regenerates 2 HP/s          |
| Dragon         | 500   | 0.8   | 15     | 80  | Fire breath (ranged AoE)    |
| Reaper (Death) | 65535 | 2.0   | 999    | 0   | Appears at 30:00, unkillable|

### 5.4 Enemy Scaling
Enemies scale with time:
```
function getEnemyStats(baseEnemy, gameTime):
    timeMultiplier = 1.0 + (gameTime / 60.0) * 0.3  // +30% per minute
    hp = baseEnemy.hp * timeMultiplier
    damage = baseEnemy.damage * (1.0 + gameTime / 180.0)  // slower damage scaling
    speed = baseEnemy.speed * (1.0 + gameTime / 600.0)  // very slow speed scaling
    return ScaledEnemy(hp, speed, damage)
```

Additional curse scaling:
```
curseMultiplier = 1.0 + player.curse * 0.1
hp *= curseMultiplier
speed *= (1.0 + player.curse * 0.05)
count *= (1.0 + player.curse * 0.15)
```

### 5.5 Spawn System
```
function spawnEnemies(gameTime, player):
    wave = getWaveForTime(gameTime)

    // Enemies spawn from just outside visible screen
    spawnRadius = max(screenWidth, screenHeight) / 2 + 100

    for each enemyGroup in wave.groups:
        count = enemyGroup.count * (1 + floor(gameTime / 60) * 0.2)

        for i in range(count):
            angle = random(0, 2 * PI)
            spawnPos = player.pos + (cos(angle), sin(angle)) * spawnRadius
            spawn(enemyGroup.type, spawnPos)

    // Continuous trickle spawning between waves
    trickleRate = 1 + gameTime / 30  // enemies per second
    spawn random basic enemies at trickleRate
```

## 6. Wave Schedule

### 6.1 Stage: Mad Forest (Default)
```
Time     | Enemy Types                    | Count | Special
---------|--------------------------------|-------|--------
0:00     | Bats                           | 10    | Tutorial wave
0:30     | Bats + Skeletons               | 20    |
1:00     | Skeletons                      | 30    |
2:00     | Zombies + Skeletons            | 40    |
3:00     | Ghosts                         | 25    |
4:00     | Skeleton + Ghost mix           | 50    |
5:00     | Mummies                        | 20    | Tanky wave
6:00     | Witches + Bats                 | 40    |
7:00     | Werewolves                     | 15    | Fast wave
8:00     | Mixed (all previous)           | 60    |
9:00     | Werewolves + Mummies           | 30    |
10:00    | ELITE: Giant Skeleton          | 1     | Drops chest
11:00    | Medusa + Flowers               | 25    |
12:00    | Mantis swarm                   | 80    | Speed wave
13:00    | Mixed large wave               | 100   |
14:00    | Golems                         | 5     | Mini-boss wave
15:00    | ELITE: Blue Bat Swarm          | 3     |
16:00    | Dragon + Mummies               | 30    |
17:00    | Massive mixed wave             | 150   |
18:00    | Werewolf + Mantis              | 60    |
19:00    | All types mixed                | 120   |
20:00    | ELITE: Vampire Lord            | 2     | Drops chest
21:00    | Extreme density mixed          | 200   |
22:00    | Extreme density continued      | 200   |
23:00    | Dense Golems + Dragons         | 50    |
24:00    | Massive swarm                  | 300   |
25:00    | ELITE: Giant Skeleton x5       | 5     |
26:00    | Overwhelming wave              | 400   |
27:00    | Near-impossible density         | 500   |
28:00    | Final wave buildup             | 500   |
29:00    | Maximum enemy density           | 600   |
30:00    | DEATH appears                  | 1     | Unkillable
```

## 7. Experience and Leveling

### 7.1 XP Gems
| Gem Type | XP Value | Color  | Drop Rate |
|----------|----------|--------|-----------|
| Small    | 1        | Blue   | 70%       |
| Medium   | 3        | Green  | 20%       |
| Large    | 7        | Red    | 8%        |
| Diamond  | 25       | White  | 2%        |

### 7.2 XP Magnet
- Base pickup radius: 32px
- Magnet stat increases pickup radius
- Attractorb passive: +50% per level
- At high magnet, gems fly toward player from across screen
- Floor chicken (heal item) and gold coins also affected by magnet

### 7.3 Leveling Formula
```
xpForLevel(level) = floor(5 + level * 10 + level^1.6)

Example:
Level 2:  20 XP
Level 5:  65 XP
Level 10: 145 XP
Level 20: 350 XP
Level 30: 600 XP
Level 50: 1200 XP
Level 100: 3500 XP
```

### 7.4 Level-Up Choices
On level up, player chooses 1 of 3-5 options:
- New weapon (if fewer than 6 weapons equipped)
- Weapon upgrade (if weapon not at max level)
- New passive item (if fewer than 6 passives equipped)
- Passive item upgrade (if passive not at max level)

Maximum equipment: 6 weapons + 6 passives = 12 total items

## 8. Treasure Chests

### 8.1 Chest Types
| Chest     | Source                 | Contents                           |
|-----------|------------------------|------------------------------------|
| Brown     | Floor spawn (rare)     | 1 random item (coins or upgrade)   |
| Silver    | Elite enemy kill       | 3 item choices                     |
| Gold      | Boss kill, 10 min mark | 5 item choices, may contain evolution|
| Green     | Random event           | 1-3 items                          |

### 8.2 Evolution from Chests
- If a weapon is at max level and its paired passive is owned, opening a gold/silver chest has a chance to evolve the weapon
- Evolution replaces the weapon permanently
- Multiple evolutions can trigger from one chest if conditions met

## 9. Stages

### 9.1 Stage List
| Stage          | Duration | Background   | Special Feature                |
|----------------|----------|-------------|-------------------------------|
| Mad Forest     | 30 min   | Dark forest | Standard stage                |
| Inlaid Library | 30 min   | Library     | Vertical enemy waves          |
| Dairy Plant    | 30 min   | Industrial  | Fast enemy waves              |
| Gallo Tower    | 30 min   | Tower       | Vertical scrolling            |
| Cappella Magna | 30 min   | Cathedral   | Boss rush elements            |
| Il Molise      | 15 min   | Open field  | Hyper mode (faster scaling)   |
| Moongolow      | 15 min   | Night field | Unlock stage                  |
| Green Acres    | 30 min   | Farm        | Bonus stage (easy)            |
| Bone Zone      | 30 min   | Graveyard   | Skeleton themed               |
| Boss Rash      | 15 min   | Arena       | Boss-only stage               |

### 9.2 Stage Unlocks
- Mad Forest: Default
- Inlaid Library: Reach Lv 20 in Mad Forest
- Dairy Plant: Reach Lv 40 in Inlaid Library
- Gallo Tower: Reach Lv 60 in Dairy Plant
- Cappella Magna: Clear previous stages

## 10. Gold and Meta-Progression

### 10.1 Gold Sources
- Gold coins dropped by enemies (value: 1-25)
- Gold bags from special enemies (value: 25-100)
- Treasure chests sometimes contain gold
- Greed stat multiplies all gold earned

### 10.2 Power-Up Shop (Between Runs)
| Power-Up       | Max Level | Cost Per Level | Effect                     |
|----------------|-----------|----------------|----------------------------|
| Might          | 5         | 200-1000       | +5% damage per level       |
| Armor          | 3         | 600-1200       | +1 Armor per level         |
| Max Health     | 3         | 200-1000       | +10% Max HP per level      |
| Recovery       | 5         | 200-1000       | +0.1 HP/s per level        |
| Cooldown       | 2         | 800-3000       | -3% Cooldown per level     |
| Area           | 2         | 800-3000       | +5% Area per level         |
| Speed          | 2         | 800-3000       | +5% Proj Speed per level   |
| Duration       | 2         | 800-3000       | +5% Duration per level     |
| Amount         | 1         | 5000           | +1 Amount                  |
| Move Speed     | 2         | 500-2000       | +5% Move Speed per level   |
| Magnet         | 2         | 500-2000       | +25% Magnet per level      |
| Luck           | 3         | 600-2000       | +10% Luck per level        |
| Growth         | 5         | 500-2000       | +3% XP Growth per level    |
| Greed          | 5         | 500-2000       | +5% Greed per level        |
| Curse          | 5         | 500-2000       | +10% Curse per level       |
| Revival        | 1         | 10000          | +1 Revival                 |
| Reroll         | 5         | 1000-5000      | +1 Reroll per level        |
| Skip           | 5         | 1000-3000      | +1 Skip per level          |
| Banish         | 5         | 1000-3000      | +1 Banish per level        |

## 11. Collision and Damage System

### 11.1 Contact Damage
- Enemies deal contact damage on collision with player
- Damage tick rate: every 0.5s while overlapping
- Damage reduced by player Armor stat
- Formula: `actualDamage = max(1, enemyDamage - playerArmor)`
- Invincibility frames: 0.5s after taking damage

### 11.2 Weapon Damage
```
function calculateWeaponDamage(weapon, player, enemy):
    baseDamage = weapon.damage
    damage = baseDamage * player.might

    // Critical hit check
    if random() < 0.05 * player.luck:
        damage *= 2  // Critical hit

    // Apply enemy resistance (some enemies resist certain damage types)
    damage *= (1.0 - enemy.resistance)

    return floor(damage)
```

### 11.3 Knockback
```
knockbackForce = weapon.knockback * (1.0 - enemy.knockbackResist)
enemy.velocity += normalize(enemy.pos - player.pos) * knockbackForce
// Knockback velocity decays over 0.3s
```

## 12. User Interface

### 12.1 In-Game HUD
```
+------------------------------------------------------------------+
| [Level Bar ============-----] Lv 15    Timer: 12:34               |
| HP: [||||||||||||------] 85/120                                    |
+------------------------------------------------------------------+
|                                                                    |
|                                                                    |
|                    GAME AREA                                       |
|                   (scrolling)                                      |
|                                                                    |
|                      [PLAYER]                                      |
|                                                                    |
|                                                                    |
+------------------------------------------------------------------+
| Weapons: [Whip8] [Wand5] [Bible3] [---] [---] [---]              |
| Passives: [Spinach3] [Tome2] [---] [---] [---] [---]             |
| Gold: 1,247                                          Kills: 8,432 |
+------------------------------------------------------------------+
```

### 12.2 Level-Up Screen
```
+------------------------------------------------------------------+
|                    LEVEL UP!                                       |
|                                                                    |
|  +--------------------------------------------------+             |
|  | [NEW] Lightning Ring                              |             |
|  | Strikes random foes. Passes through walls.        |             |
|  +--------------------------------------------------+             |
|                                                                    |
|  +--------------------------------------------------+             |
|  | [LV4] Whip                                       |             |
|  | Base damage up. Pass through more enemies.        |             |
|  +--------------------------------------------------+             |
|                                                                    |
|  +--------------------------------------------------+             |
|  | [LV3] Spinach                                    |             |
|  | +10% Might                                       |             |
|  +--------------------------------------------------+             |
|                                                                    |
|  [Reroll: 2]   [Skip: 1]   [Banish]                              |
+------------------------------------------------------------------+
```

### 12.3 Game Over / Results Screen
```
+------------------------------------------------------------------+
|                    GAME OVER                                       |
|                                                                    |
|  Survived: 18:32                                                   |
|  Level Reached: 47                                                 |
|  Enemies Killed: 12,847                                            |
|  Gold Earned: 2,145                                                |
|                                                                    |
|  Weapons:                                                          |
|  [Bloody Tear] [Holy Wand] [Unholy Vespers]                      |
|  [Thousand Edge] [Hellfire] [Soul Eater]                          |
|                                                                    |
|  Passives:                                                         |
|  [Spinach 5] [Empty Tome 5] [Hollow Heart 5]                     |
|  [Bracer 5] [Pummarola 5] [Spellbinder 5]                        |
|                                                                    |
|  [RETRY]  [CHARACTER SELECT]  [MAIN MENU]                         |
+------------------------------------------------------------------+
```

## 13. Performance Optimization

### 13.1 Entity Limits
- Maximum enemies on screen: 500 (soft cap), 1000 (hard cap)
- Maximum projectiles: 2000
- Maximum XP gems on ground: 500 (oldest are merged into larger gems)
- Maximum visual effects: 300

### 13.2 Optimization Techniques
- Spatial hash grid for collision detection (cell size: 64px)
- Enemy culling: Enemies beyond 2x screen distance are removed
- Projectile pooling: Pre-allocate projectile arrays
- Batch rendering: Group sprites by texture atlas
- Damage numbers: Pool and reuse text objects
- XP gem merging: When too many gems, merge nearby small gems into larger ones

### 13.3 Rendering Order
```
Layers (back to front):
  1. Background tiles
  2. Shadow layer
  3. XP gems and items
  4. Enemies (sorted by Y position)
  5. Player
  6. Projectiles
  7. Damage numbers and effects
  8. HUD
```

## 14. Audio Design

### 14.1 Music
- Each stage has a unique looping background track
- Music intensity increases with enemy density
- Boss encounters have intensified music

### 14.2 Sound Effects
- Weapon hit: Different per weapon type (slash, zap, thud, etc.)
- Enemy death: Pop/squish sound
- Level up: Ascending chime
- XP pickup: Subtle ding (pitch varies with gem size)
- Chest open: Triumphant fanfare
- Player damage: Pain grunt + screen flash
- Evolution: Epic fanfare

## 15. Death (The Reaper)

### 15.1 Death Mechanics
- Appears at exactly 30:00 game time
- HP: 65,535 (effectively unkillable normally)
- Speed: 2.0 (faster than most characters)
- Damage: 65,535 per tick (instant kill)
- Cannot be knocked back
- Purpose: End the run at 30 minutes

### 15.2 Killing Death (Secret)
- Requires specific item combinations and extreme damage output
- If killed, an even stronger Death appears
- Killing the second Death grants achievement and special unlock

## 16. Save System

### 16.1 Persistent Data
```
SaveData {
  gold: int
  powerups: Map<PowerUp, int>  // purchased levels
  characters_unlocked: List<Character>
  stages_unlocked: List<Stage>
  achievements: List<Achievement>
  total_kills: int
  total_gold_earned: int
  total_games: int
  best_time_per_stage: Map<Stage, float>
  collections: Map<Weapon, bool>  // weapons discovered
}
```

### 16.2 Run Data (Not Saved Between Runs)
- Current weapons and levels
- Current passives and levels
- Current HP, position
- Enemies on screen
- Game timer
- Level and XP
