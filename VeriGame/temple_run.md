# Temple Run — Complete Game Specification

## 1. Game Overview

**Title:** Temple Run
**Genre:** Casual / Endless Runner / Action
**Platform:** Mobile (landscape or portrait), desktop adaptable
**Original Creator:** Imangi Studios (Keith Shepherd, Natalia Luckyanova)
**Release Year:** 2011
**Core Loop:** Run endlessly through a temple ruin, swiping to turn, jump, slide, and tilt to avoid obstacles. Collect coins and power-ups. Survive as long as possible.

Temple Run is a third-person endless runner viewed from behind the character. The player character has stolen a golden idol from a temple and is chased by demonic monkeys. The path consists of straight corridors with 90-degree turns (left or right). The player swipes to turn, jump, slide, and tilts the device to move left/right within the lane.

For a 2D implementation, the game can be rendered as a top-down or side-scrolling runner with lane-based mechanics.

---

## 2. Technical Foundation

### 2.1 Display
- **View:** Third-person behind character (3D) or side-scrolling (2D adaptation)
- **For 2D implementation:** Side view with 3 lanes
- **Logical Resolution:** 480 x 320 (landscape) or 320 x 480 (portrait)
- **Frame Rate:** 60 FPS
- **Scroll Direction:** Character runs forward (screen scrolls toward viewer)

### 2.2 2D Adaptation Layout
For a 2D side-view implementation:
```
+--------------------------------------------------+
|  Score / Coins / Distance         [Pause]        |
|                                                   |
|  Lane 1 (left)  |  Lane 2 (center) | Lane 3 (right)
|                  |                   |              |
|   [obstacle]     |    [player]       |  [coins]    |
|                  |                   |              |
|==================|===================|==============|
|  Ground          |  Ground           |  Ground      |
+--------------------------------------------------+
```

---

## 3. Game States

```
+---------+     +----------+     +---------+     +-----------+
|  MENU   | --> |  RUNNING | --> |  DYING  | --> | GAME_OVER |
+---------+     +----------+     +---------+     +-----------+
     ^               |                                 |
     |               v                                 |
     |          +----------+                           |
     |          |  PAUSED  |                           |
     |          +----------+                           |
     +------------------ restart ---------------------+
```

---

## 4. Player Character

### 4.1 Character Properties

| Parameter              | Value                          |
|------------------------|--------------------------------|
| Character width        | 40 px (2D)                     |
| Character height       | 60 px (standing)               |
| Character height       | 30 px (sliding)                |
| Lane width             | 80 px                          |
| Lane positions         | Left: 80, Center: 160, Right: 240 |
| Lane switch duration   | 200 ms (smooth transition)     |
| Jump height            | 100 px                         |
| Jump duration          | 600 ms (up 300ms, down 300ms)  |
| Slide duration         | 600 ms                         |
| Base run speed         | 5.0 px/frame                   |
| Max run speed          | 12.0 px/frame                  |
| Speed increase rate    | 0.002 px/frame per frame       |
| Stumble recovery time  | 500 ms                         |

### 4.2 Actions

| Action        | Input (Mobile)    | Input (Desktop)  | Effect                              |
|---------------|-------------------|------------------|-------------------------------------|
| Turn Left     | Swipe Left        | Left Arrow / A   | Take left path at intersection      |
| Turn Right    | Swipe Right       | Right Arrow / D  | Take right path at intersection     |
| Jump          | Swipe Up          | Up Arrow / W     | Jump over ground obstacles          |
| Slide         | Swipe Down        | Down Arrow / S   | Slide under overhead obstacles      |
| Move Left     | Tilt Left         | Left Arrow       | Shift to left lane                  |
| Move Right    | Tilt Right        | Right Arrow      | Shift to right lane                 |

### 4.3 Character States
```
RUNNING  --> JUMPING  (swipe up)
RUNNING  --> SLIDING  (swipe down)
RUNNING  --> TURNING  (swipe left/right at intersection)
RUNNING  --> STUMBLE  (hit obstacle, if resurrection available)
RUNNING  --> DYING    (hit obstacle, no resurrection)
JUMPING  --> RUNNING  (land)
SLIDING  --> RUNNING  (slide ends)
```

### 4.4 Jump Physics (2D)
```
jump_velocity = -8.0 px/frame
gravity = 0.45 px/frame^2
jump apex at: 8.0 / 0.45 = 17.8 frames (297 ms)
max height: 64 / (2 * 0.45) = 71.1 px

// Simplified jump curve (sine-based):
jump_height(t) = jump_max_height * sin(PI * t / jump_duration)
where t goes from 0 to jump_duration
```

---

## 5. Path and Terrain

### 5.1 Path Segments

| Segment Type     | Length (px)  | Description                               |
|------------------|-------------|-------------------------------------------|
| Straight         | 300-600     | Straight corridor, 3 lanes                |
| Left Turn        | N/A         | 90-degree left turn                       |
| Right Turn       | N/A         | 90-degree right turn                      |
| T-Junction       | N/A         | Must choose left or right                 |
| Gap (no floor)   | 60-120      | Must jump over                            |
| Narrow           | 200-400     | Only 1-2 lanes available                  |

### 5.2 Path Generation
```
Segments generated procedurally:
1. Start with 3 straight segments (tutorial area)
2. Then alternate: straight(random_length) -> turn(random_direction)
3. Minimum straight length decreases with distance:
   min_straight = max(300 - distance/1000 * 50, 150)
4. Turn frequency increases with distance
5. Obstacles per segment increases with distance
```

### 5.3 Terrain Tiles
- **Stone path:** Default running surface
- **Wooden bridge:** Over gaps, can collapse
- **Water:** Falling into water = death
- **Lava:** Later levels, visual variant of death zone

---

## 6. Obstacles

### 6.1 Obstacle Types

| Obstacle          | Size (WxH)  | Lanes Blocked | Avoidance                |
|-------------------|-------------|---------------|--------------------------|
| Tree Root (low)   | 80 x 30    | 1 lane        | Jump over                |
| Tree Root (wide)  | 240 x 30   | All 3 lanes   | Jump over                |
| Fire Bar (low)    | 80 x 30    | 1 lane        | Jump over                |
| Low Branch        | 240 x 40   | All 3 lanes   | Slide under              |
| Broken Bridge     | 80 x 60    | 1 lane        | Switch lanes             |
| Rotating Blade    | 40 x 60    | 1 lane        | Switch lanes             |
| Gap in Floor      | 240 x 60   | All 3 lanes   | Jump over                |
| Wall              | 80 x 120   | 1 lane        | Switch lanes             |
| Double Obstacle   | varies      | 2 lanes       | Specific lane required   |

### 6.2 Obstacle Placement Rules
- Minimum distance between obstacles: 150 px (at base speed)
- Minimum distance decreases with speed: `min_dist = max(150 - speed * 5, 80)`
- Never place impossible combinations (all 3 lanes blocked with no action possible)
- Jump obstacles never immediately followed by slide obstacles (100px minimum gap)
- At intersections: no obstacles within 100px before the turn point

### 6.3 Obstacle Patterns by Distance

| Distance Range | Obstacle Density | Pattern Complexity           |
|----------------|-----------------|------------------------------|
| 0 - 500m       | Low (1 per 300px) | Single lane, single type    |
| 500 - 1500m    | Medium (1/200px)  | Two obstacle combos         |
| 1500 - 3000m   | High (1/150px)    | Multi-lane blocking         |
| 3000 - 5000m   | Very High (1/100px)| Complex patterns, tight gaps|
| 5000m+         | Maximum (1/80px)  | Requires near-perfect play  |

---

## 7. Coins

### 7.1 Coin Properties

| Parameter         | Value                    |
|-------------------|--------------------------|
| Coin size         | 20 x 20 px               |
| Coin pickup radius| 25 px (forgiving)        |
| Base coin value   | 1 coin                   |
| Red gem value     | 10 coins                 |
| Blue gem value    | 25 coins                 |
| Green gem value   | 50 coins                 |

### 7.2 Coin Patterns

| Pattern      | Description                                    | Coins in Pattern |
|-------------|------------------------------------------------|-----------------|
| Single Line | Row of coins in one lane                       | 5-8             |
| Arrow       | Arrow shape pointing in run direction          | 7-10            |
| Arc         | Arched pattern requiring jump to collect all   | 5-7             |
| Diamond     | Diamond shape across 2-3 lanes                 | 8-12            |
| Trail       | Winding path across lanes                      | 6-10            |

### 7.3 Coin Placement
```
Coins appear in patterns every 200-400 px
Coin vertical spacing: 30 px
Coin horizontal spacing: 30 px
Coins in air: 40-80 px above ground (collectible during jump)
Gem spawn rate: 1 per 1000-2000 px distance
```

---

## 8. Power-Ups

### 8.1 Power-Up Types

| Power-Up        | Duration  | Effect                                          | Icon Color |
|-----------------|-----------|------------------------------------------------|------------|
| Mega Coin       | 15 sec    | All coins worth 2x; coin magnet active         | Gold       |
| Invisibility    | 15 sec    | Pass through all obstacles; no collision        | Blue       |
| Coin Magnet     | 12 sec    | Automatically attract coins from all lanes      | Purple     |
| Boost           | 10 sec    | Run at 2x speed, invincible, auto-collect coins| Red        |
| Shield          | 1 use     | Absorb one collision with obstacle              | Green      |

### 8.2 Power-Up Spawn Rate
```
Base interval: one power-up every 800-1200 px
Power-up selection: equal probability (20% each)
Power-ups appear floating in center lane at head height
Pickup: run through the power-up
Active power-up prevents spawning another (no stacking)
```

### 8.3 Power-Up Visual Effects
- **Mega Coin:** Golden glow around character, trail of sparkles
- **Invisibility:** Character becomes translucent (50% opacity), blue shimmer
- **Coin Magnet:** Purple rings emanate from character, coins curve toward player
- **Boost:** Speed lines on screen, fire trail behind character
- **Shield:** Green bubble around character, breaks with shatter effect on use

---

## 9. Scoring System

### 9.1 Score Sources

| Source              | Points                           |
|---------------------|----------------------------------|
| Distance (per meter)| 1 point per meter                |
| Coin collected      | 1 coin = 1 point (for distance)  |
| Red gem             | 10 points                        |
| Blue gem            | 25 points                        |
| Green gem           | 50 points                        |

### 9.2 Score Multiplier
- Base multiplier: 1x
- Multiplier increases by completing objectives (see objectives section)
- Max multiplier: 10x (original had higher)
- Score = distance_points * multiplier + coin_bonus_points

### 9.3 Distance Calculation
```
distance_meters = total_pixels_scrolled / 10
// 10 pixels = 1 meter
score = distance_meters * multiplier
```

---

## 10. Objectives / Missions

### 10.1 Objective System
- Player has 3 active objectives at any time
- Completing all 3 increases score multiplier by 1
- New objectives generated when current set completed

### 10.2 Objective Types

| Objective                     | Example Target    |
|-------------------------------|-------------------|
| Run X meters                  | 500m, 1000m       |
| Collect X coins in one run    | 100, 250, 500     |
| Score X points in one run     | 5000, 10000       |
| Use X power-ups               | 3, 5              |
| Slide X times in one run      | 10, 25            |
| Jump X times in one run       | 15, 30            |
| Don't collect coins for Xm    | 200m, 500m        |
| Run X meters without stumbling| 500m              |

---

## 11. Upgrades (Coin Shop)

### 11.1 Upgrade Categories

| Upgrade          | Levels | Cost per Level      | Effect                          |
|------------------|--------|--------------------|---------------------------------|
| Mega Coin        | 5      | 500/1000/2500/5000/10000 | +2 sec duration per level  |
| Invisibility     | 5      | 500/1000/2500/5000/10000 | +2 sec duration per level  |
| Coin Magnet      | 5      | 500/1000/2500/5000/10000 | +2 sec duration per level  |
| Boost            | 5      | 500/1000/2500/5000/10000 | +2 sec duration per level  |
| Shield           | 1      | 2500                     | Available from start       |
| Coin Value x2    | 1      | 5000                     | All coins worth double     |
| Head Start       | 3      | 1000/2500/5000           | Start further into the run |
| Resurrection     | N/A    | 1 per use (gems)         | Continue after death       |

### 11.2 Characters

| Character       | Cost (coins) | Special Ability               |
|-----------------|-------------|-------------------------------|
| Guy Dangerous   | Free        | Default (no special)          |
| Scarlett Fox    | 10000       | Faster power-up meter         |
| Barry Bones     | 10000       | Extended boost duration        |
| Karma Lee       | 10000       | Extended shield duration       |
| Montana Smith   | 25000       | Extended coin magnet           |
| Francisco M.    | 25000       | Coin value boost               |
| Zack Wonder     | 50000       | Multiplier boost               |

---

## 12. Demon Monkeys (Chasers)

### 12.1 Properties

| Parameter             | Value                         |
|-----------------------|-------------------------------|
| Number of monkeys     | 3 (chasing behind)            |
| Chase distance        | 100 px behind player          |
| Close distance        | 50 px (danger zone)           |
| Catch distance        | 0 px (game over)              |
| Approach speed        | Player speed + 0.5 px/frame   |

### 12.2 Behavior
- Monkeys always visible behind player (in 3D: over the shoulder)
- When player stumbles: monkeys rush closer (distance decreases by 30px)
- When player runs cleanly: monkeys maintain distance
- If player uses boost: monkeys fall far behind (reset to 200px)
- Visual: three snarling monkey faces, glowing eyes
- 2D representation: shadowy figures at the bottom/back of screen

### 12.3 Stumble Mechanic
- Near-miss with obstacle causes stumble (within 15px of obstacle edge)
- Stumble animation: 500ms of staggering
- During stumble: no inputs accepted
- Monkeys close 30px gap during stumble
- If monkeys reach player during stumble: death

---

## 13. Resurrection Mechanic

When the player dies:
1. "Save Me?" prompt appears with 3-second countdown
2. Player can spend 1 gem to resurrect
3. On resurrection: invincible for 3 seconds, monkeys reset to max distance
4. Can only resurrect once per run (optional: increase cost each time)
5. If no gems or player declines: game over screen

---

## 14. UI Layout

### 14.1 HUD During Play
```
+--------------------------------------------------+
| [Pause]  Score: 12345     x3     [coin]x 234     |
|                                                   |
|  [Power-up timer bar: ========------]             |
|                                                   |
|                   GAME AREA                       |
|                                                   |
|   [objective progress: "Slide 5 more times"]      |
+--------------------------------------------------+
```

### 14.2 Game Over Screen
```
+--------------------------------------------------+
|                                                   |
|              GAME OVER                            |
|                                                   |
|    Distance:    2,345 m                           |
|    Coins:       156                               |
|    Score:       7,035                              |
|    Multiplier:  x3                                |
|    Total:       21,105                            |
|                                                   |
|    Best: 45,230                                   |
|                                                   |
|    [  PLAY AGAIN  ]    [  STORE  ]                |
|                                                   |
+--------------------------------------------------+
```

### 14.3 Store / Upgrade Screen
```
+--------------------------------------------------+
| [Back]           STORE            Coins: 2,345    |
|                                                   |
|  POWER-UPS           CHARACTERS      UTILITIES    |
|  -----------         ----------      ----------   |
|  Mega Coin Lv3       Guy Danger.     Head Start   |
|  [Upgrade: 2500]     [Equipped]      [Buy: 1000]  |
|                                                   |
|  Invisibility Lv2    Scarlett Fox    Resurrection  |
|  [Upgrade: 1000]     [Buy: 10000]    [1 gem/use]  |
|                                                   |
+--------------------------------------------------+
```

---

## 15. Sound Effects

| Sound              | Trigger                          | Description                    |
|--------------------|----------------------------------|-------------------------------|
| footsteps          | Constant during running          | Rhythmic stone tapping (loop) |
| coin_collect       | Pick up coin                     | Bright "ting" sound            |
| gem_collect        | Pick up gem                      | Richer chime, sparkle          |
| jump               | Player jumps                     | Whoosh upward                  |
| slide              | Player slides                    | Scraping / rushing sound       |
| turn               | Player turns at intersection     | Quick footstep pivot           |
| stumble            | Near-miss with obstacle          | Grunt + stagger sound          |
| obstacle_hit       | Collision with obstacle          | Heavy thud / crash             |
| monkey_roar        | Game start, death approach       | Aggressive roar / screech      |
| power_up_collect   | Pick up power-up                 | Ascending magical chime        |
| power_up_end       | Power-up expires                 | Descending tone                |
| boost_whoosh       | During boost power-up            | Wind rushing (loop)            |
| death              | Final collision                  | Dramatic crash + monkey howl   |

---

## 16. Music

- **Menu:** Ambient mystical theme, medium tempo, percussion-heavy
- **Gameplay:** Dynamic music that intensifies with speed
  - Base layer: tribal drums at 120 BPM
  - Intensity layer: added strings/brass as speed increases
  - Danger layer: when monkeys are close, pulse increases
- **Game Over:** Short dramatic sting, then somber melody

---

## 17. Visual Effects

| Effect            | Trigger                    | Description                      |
|-------------------|----------------------------|----------------------------------|
| Coin sparkle      | Coin collected             | 4-particle burst, yellow         |
| Gem glow          | Gem collected              | 6-particle burst, gem color      |
| Speed lines       | During boost               | Horizontal white lines on edges  |
| Dust cloud        | Landing after jump         | 3-4 brown particles at feet      |
| Shield break      | Shield absorbs hit         | Circular shatter, green shards   |
| Power-up aura     | Active power-up            | Glow outline around character    |
| Monkey eyes       | Behind player              | Red glowing dots in background   |

---

## 18. Difficulty Scaling

```
speed(distance) = base_speed + distance / 1000 * speed_increase_rate
// At distance 0: 5.0 px/frame
// At distance 5000m: 5.0 + 5.0 * 0.002 * 60 * 5 = ~8.0 px/frame (approximate)

Obstacle density scales:
density(distance) = base_density * (1 + distance / 2000)

Turn frequency scales:
turns_per_km = 2 + distance / 1000

Gap size between obstacles:
min_gap(speed) = 120 / speed * base_speed
```

---

## 19. Environment Themes

| Theme     | Distance Range | Visual Style                         | Unique Obstacles     |
|-----------|---------------|--------------------------------------|----------------------|
| Temple    | 0 - 2000m     | Stone corridors, torches, moss       | Tree roots, statues  |
| Forest    | 2000 - 4000m  | Dense jungle, vines, waterfalls      | Log bridges, vines   |
| Mine      | 4000 - 6000m  | Dark tunnels, mine carts, crystals   | Low ceilings, carts  |
| Cliff     | 6000 - 8000m  | Narrow cliff paths, wind, eagles     | Crumbling edges      |
| Ruins     | 8000m+        | Ancient ruins, fire, lava            | Fire bars, lava gaps |

Themes cycle after completing all five.

---

## 20. Controls Summary (2D Adaptation)

| Control           | Action              | Implementation              |
|-------------------|---------------------|-----------------------------|
| Swipe/Arrow Up    | Jump                | Apply jump velocity         |
| Swipe/Arrow Down  | Slide               | Reduce hitbox height 600ms  |
| Swipe/Arrow Left  | Move/Turn Left      | Switch to left lane / turn  |
| Swipe/Arrow Right | Move/Turn Right     | Switch to right lane / turn |
| Tap / Spacebar    | Alternative jump     | Same as swipe up           |

---

## 21. Data Persistence

| Key                  | Type    | Description                    |
|----------------------|---------|--------------------------------|
| best_score           | int     | All-time high score            |
| best_distance        | int     | Farthest distance in meters    |
| total_coins          | int     | Lifetime coins collected       |
| current_coins        | int     | Coins available to spend       |
| gems                 | int     | Premium currency               |
| upgrade_levels       | dict    | Level of each upgrade          |
| unlocked_characters  | list    | Which characters are unlocked  |
| active_character     | string  | Currently selected character   |
| objectives           | list    | Current 3 objectives + progress|
| multiplier           | int     | Current score multiplier       |
| total_runs           | int     | Number of games played         |

---

## 22. Implementation Checklist

1. [ ] Set up scrolling corridor with 3 lanes
2. [ ] Implement player character with running animation
3. [ ] Add jump mechanic with proper arc
4. [ ] Add slide mechanic with hitbox reduction
5. [ ] Add lane switching (smooth transition)
6. [ ] Generate procedural path with turns
7. [ ] Implement turn mechanic at intersections
8. [ ] Create obstacle types (low, high, lane-blocking)
9. [ ] Implement collision detection per-lane
10. [ ] Add coin collection with patterns
11. [ ] Add gem collection
12. [ ] Implement power-up system (5 types)
13. [ ] Add score system with multiplier
14. [ ] Create objective/mission system
15. [ ] Implement stumble mechanic
16. [ ] Add demon monkey chasers
17. [ ] Implement resurrection mechanic
18. [ ] Create upgrade store
19. [ ] Add character selection
20. [ ] Implement speed scaling with distance
21. [ ] Create environment theme transitions
22. [ ] Build HUD with score, coins, power-up timer
23. [ ] Create game over screen with stats
24. [ ] Add sound effects and music
25. [ ] Implement data persistence

---

End of Temple Run specification.
