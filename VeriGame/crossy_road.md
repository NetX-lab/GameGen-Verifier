# Crossy Road — Complete Game Specification

## 1. Game Overview

**Title:** Crossy Road
**Genre:** Casual / Arcade
**Platform:** Mobile (portrait), desktop
**Original Creator:** Hipster Whale (Matt Hall, Andy Sum)
**Release Year:** 2014
**Core Loop:** Hop forward through an endless series of roads, rivers, train tracks, and grassy fields. Avoid cars, trains, and water. Score increases with each forward hop. Die from traffic, drowning, or standing still too long.

Crossy Road is a modern reinterpretation of Frogger with endless procedural generation, voxel-art aesthetics, and a massive character collection system. The playing field scrolls with the player, and the player hops one tile at a time in a grid-based system.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Portrait
- **Logical Resolution:** 320 x 480 pixels (or tile-based equivalent)
- **View:** Isometric top-down (original) or orthogonal top-down (simplified)
- **Tile Size:** 32 x 32 px per grid cell
- **Grid:** 10 columns wide, visible area ~15 rows tall
- **Frame Rate:** 60 FPS
- **Art Style:** Voxel / blocky / low-poly 3D (or pixel art for 2D)

### 2.2 Coordinate System
- **X-axis:** Left to right (0-9, 10 columns)
- **Y-axis:** Forward direction (away from player start, increases with progress)
- **Screen Y:** Player stays near bottom-center of screen; world scrolls down as player moves forward

### 2.3 Rendering Layers
```
Layer 0: Ground tiles (grass, road, water, tracks)
Layer 1: Lane markings, shadows
Layer 2: Vehicles, logs, lily pads
Layer 3: Player character
Layer 4: Trees, bushes (foreground decoration)
Layer 5: UI overlay (score, pause)
```

---

## 3. Game States

```
+---------+     +----------+     +-----------+
|  TITLE  | --> | PLAYING  | --> | GAME_OVER |
+---------+     +----------+     +-----------+
    ^                                  |
    +---------- tap restart ----------+
```

| State     | Description                                            |
|-----------|--------------------------------------------------------|
| TITLE     | Character idle on grass, logo, "TAP TO PLAY"           |
| PLAYING   | Active hopping, score counting, obstacles moving       |
| GAME_OVER | Splat animation, score display, character unlock prompt |

---

## 4. Grid and Movement System

### 4.1 Grid Properties

| Parameter          | Value                     |
|--------------------|---------------------------|
| Grid columns       | 10 (X: 0-9)              |
| Tile size           | 32 x 32 px                |
| Player start column | 4 or 5 (center)           |
| Player start row    | 3 rows from bottom        |
| Hop distance       | 1 tile (32 px)            |
| Hop duration       | 100 ms (smooth animation) |
| Hop height (visual)| 8 px arc during hop       |

### 4.2 Movement Controls

| Input              | Action                     |
|--------------------|----------------------------|
| Tap / Swipe Up     | Hop forward (main action)  |
| Swipe Left         | Hop left                   |
| Swipe Right        | Hop right                  |
| Swipe Down         | Hop backward               |
| Up Arrow           | Hop forward (desktop)      |
| Left Arrow         | Hop left (desktop)         |
| Right Arrow        | Hop right (desktop)        |
| Down Arrow         | Hop backward (desktop)     |

### 4.3 Hop Animation
```
hop_progress: 0.0 to 1.0 over 100ms

position_x = lerp(start_x, end_x, hop_progress)
position_y = lerp(start_y, end_y, hop_progress)
height_offset = -sin(hop_progress * PI) * 8  // arc shape
scale_squash = 1.0 + sin(hop_progress * PI) * 0.15  // slight stretch
```

### 4.4 Movement Rules
- Cannot hop into trees or bushes (blocked tiles)
- Cannot hop off left/right edges of the grid
- Can hop backward (but camera does not scroll backward)
- Each forward hop increases score by 1
- Backward hops do not decrease score
- Lateral hops do not change score

---

## 5. Lane Types

### 5.1 Lane Catalog

| Lane Type    | Width  | Frequency   | Hazard                      |
|--------------|--------|-------------|-----------------------------|
| Grass        | 1 row  | 30-40%      | None (safe), may have trees |
| Road         | 1 row  | 30-35%      | Cars, trucks                |
| River        | 1 row  | 15-20%      | Water (death), logs/lilypads|
| Train Track  | 1 row  | 5-10%       | Trains (instant death)      |

### 5.2 Lane Generation Rules
```
function generateNextLane(previous_lane_type):
    // Never have more than 5 consecutive roads
    // Never have more than 3 consecutive rivers
    // Always have at least 1 grass lane between road and river sections
    // Train tracks are always isolated (grass on both sides)
    // Guarantee at least 1 safe path through every lane

    weights = {
        GRASS: 35,
        ROAD: 35,
        RIVER: 20,
        TRAIN: 10
    }
    // Adjust weights based on consecutive count
    if consecutive_roads >= 4: weights[ROAD] = 0
    if consecutive_rivers >= 2: weights[RIVER] = 0

    return weightedRandom(weights)
```

---

## 6. Obstacles and Hazards

### 6.1 Vehicles (Road Lanes)

| Vehicle      | Width (tiles) | Speed (px/frame) | Color Variants       |
|--------------|---------------|-------------------|-----------------------|
| Small Car    | 1             | 1.5 - 3.0        | Red, Blue, Yellow     |
| Sedan        | 2             | 1.0 - 2.5        | White, Black, Green   |
| Truck        | 3             | 0.8 - 2.0        | Gray, Brown, Orange   |
| Bus          | 4             | 0.5 - 1.5        | Yellow, Red           |

- All vehicles in a lane move in the same direction (left or right)
- Direction is randomized per lane (50/50)
- Vehicle spacing: random gap of 3-8 tiles between vehicles
- Speed assigned per lane (all vehicles same speed in one lane)
- Speed increases slightly with distance: `speed = base + distance/5000`

### 6.2 Trains (Train Track Lanes)

| Parameter         | Value                           |
|-------------------|---------------------------------|
| Train width       | 10 tiles (fills entire screen)  |
| Train speed       | 15.0 px/frame (very fast)       |
| Warning time      | 1.5 seconds before arrival      |
| Warning signal    | Flashing lights + bell sound    |
| Train frequency   | One train every 4-8 seconds     |
| Kill zone         | Entire lane when train present  |

- Train warning: lights at both edges of track flash red
- Player can safely stand on tracks between trains
- Train appears from one side and crosses entire screen

### 6.3 River (Water Lanes)

| Object       | Width (tiles) | Speed (px/frame) | Capacity    |
|-------------|---------------|-------------------|-------------|
| Small Log    | 2             | 1.0 - 2.0        | 2 players   |
| Large Log    | 3             | 0.8 - 1.5        | 3 players   |
| Lily Pad     | 1             | 0.5 - 1.0        | 1 player    |

- All objects in a river lane move in the same direction
- Gaps between objects: 2-4 tiles
- Player MUST land on a log or lily pad (water = instant death)
- Player rides on the object (moves with it)
- If object carries player off-screen edge: death
- Lily pads sink 1.5 seconds after player lands on them

### 6.4 Trees and Bushes (Grass Lanes)

| Object   | Size    | Placement                        |
|----------|---------|----------------------------------|
| Tree     | 1 tile  | 0-4 per grass lane, random spots |
| Bush     | 1 tile  | 0-3 per grass lane, random spots |
| Rock     | 1 tile  | 0-2 per grass lane               |

- Trees/bushes are solid obstacles (block movement)
- Guarantee at least 1 clear forward path through any sequence
- Decorative only; no damage, just block movement

---

## 7. Scoring

### 7.1 Score Rules

| Action                   | Points    |
|--------------------------|-----------|
| Hop forward              | +1        |
| Hop backward             | 0         |
| Hop sideways             | 0         |
| Reach new farthest row   | +1        |
| Hop backward past record | 0 (score stays at max) |

- Score = maximum row reached
- Display: large centered number at top of screen
- Score only goes up, never down

### 7.2 Coin Collection
- Gold coins appear rarely on the field (1 per 50-100 rows)
- Picking up a coin: add 1 to coin counter
- Coins used to unlock new characters (100 coins per random unlock)
- Coin size: 1 tile, with spinning animation

---

## 8. Death Conditions and Animations

### 8.1 Death Types

| Cause              | Animation                              | Duration |
|--------------------|----------------------------------------|----------|
| Hit by car/truck   | Flatten/splat, character flattened     | 500ms    |
| Hit by train       | Dramatic impact, character flung       | 600ms    |
| Fall in water      | Splash effect, ripples, character sinks| 400ms    |
| Carried off-screen | Character slides off edge              | 300ms    |
| Idle timeout       | Eagle swoops down and grabs character  | 1200ms   |
| Lily pad sinks     | Same as water death                    | 400ms    |

### 8.2 Idle Timeout (Eagle)
- If player doesn't move forward for **5 seconds**: eagle warning
- Eagle shadow appears, grows larger over 2 seconds
- After 2 more seconds: eagle swoops down and grabs player
- Total idle time before death: ~7 seconds
- Moving forward resets the timer
- Backward/sideways hops do NOT reset the timer

### 8.3 Death Sequence
1. Death animation plays (type-specific)
2. Screen dims slightly (20% dark overlay)
3. Score displays prominently in center
4. "TAP TO RETRY" appears
5. Optional: ad or character unlock opportunity
6. Tap anywhere to restart

---

## 9. Camera System

### 9.1 Camera Behavior
- Camera follows player's forward movement
- Camera scrolls smoothly when player hops forward
- Camera NEVER scrolls backward
- If player is more than 5 rows behind the camera bottom edge: eagle timer starts
- Camera position: player is ~1/3 from bottom of visible area

### 9.2 Camera Scroll
```
target_camera_y = player_row - 4  // player 4 rows from bottom
if target_camera_y > current_camera_y:
    current_camera_y = lerp(current_camera_y, target_camera_y, 0.2)
```

---

## 10. Characters

### 10.1 Character System
- 150+ characters in original game
- All characters are cosmetic only (same hitbox, speed)
- Characters are voxel-art styled animals, people, and objects
- Some characters change the game theme (e.g., penguin = ice theme)

### 10.2 Character Unlock Methods
1. **Coin Machine:** Spend 100 coins for random character (gacha)
2. **Free Gift:** One free character every 6 hours
3. **Special Unlock:** Complete specific challenge
4. **Purchase:** IAP for specific characters

### 10.3 Sample Characters

| Character     | Theme Change     | Unlock Method    |
|---------------|------------------|------------------|
| Chicken       | Default          | Free (starter)   |
| Dog           | Default          | Coin Machine     |
| Cat           | Default          | Coin Machine     |
| Penguin       | Ice / Snow       | Coin Machine     |
| Frog          | Swamp            | Coin Machine     |
| Robot         | Sci-fi           | Coin Machine     |
| Pirate        | Ocean            | Special          |
| Astronaut     | Space            | Special          |
| Zombie        | Halloween        | Seasonal         |
| Snowman       | Christmas        | Seasonal         |

### 10.4 Theme Variations
When certain characters are selected, the environment changes:

| Theme      | Grass           | Road           | Water          | Trees        |
|------------|-----------------|----------------|----------------|--------------|
| Default    | Green grass     | Gray asphalt   | Blue water     | Oak trees    |
| Snow       | White snow      | Icy road       | Frozen river   | Pine trees   |
| Desert     | Sand            | Dirt road      | Oasis          | Cacti        |
| Space      | Moon surface    | Crater lanes   | Lava streams   | Crystals     |
| Swamp      | Muddy ground    | Wooden bridges | Murky water    | Mangroves    |

---

## 11. UI Layout

### 11.1 Playing Screen
```
+---------------------------+
|          42               |  Score (centered, Y=30)
|                           |
| T . . . . . . . T . .    |  Grass with trees (T)
| . . . C . . . . . . .    |  Coin on grass
|>>>>>  [ CAR ]  >>>>>>    |  Road with car
|>>>>>>>>>>>>>  >>>>>>>>   |  Road (traffic)
| . . . . . . . . . . .    |  Grass (safe)
|<<<  [TRUCK]  <<<<<<<<<   |  Road
| ===    ===    ===         |  River with logs
|    ===     ===    ===     |  River with logs
| . . T . . . . T . . .    |  Grass
|---[FLASH]---[FLASH]---   |  Train tracks
| . . . . . . . . . . .    |  Grass
| . . . .[P]. . . . . .    |  Player on grass
| . . . . . . . . . . .    |
+---------------------------+
```

### 11.2 Title Screen
```
+---------------------------+
|                           |
|     CROSSY ROAD           |  Logo at Y=80
|                           |
|                           |
|        [Chicken]          |  Character idle at center
|     ===============       |  Grass lane
|                           |
|                           |
|     TAP TO PLAY           |  Y=350
|                           |
|  [Gift]  [Shop]  [Chars]  |  Bottom buttons
+---------------------------+
```

### 11.3 Game Over Screen
```
+---------------------------+
|                           |
|          42               |  Final score
|     NEW HIGH SCORE!       |  (if applicable)
|                           |
|   [death scene visible]   |
|                           |
|   +-------------------+   |
|   | [Coin] x 342      |   |  Total coins
|   | [Gift] Available!  |   |
|   +-------------------+   |
|                           |
|     TAP TO RETRY          |
|                           |
|   [Home]  [Share]         |
+---------------------------+
```

---

## 12. Sound Effects

| Sound           | Trigger                    | Description                   |
|-----------------|----------------------------|-------------------------------|
| hop             | Player hops                | Quick "pop" / footstep        |
| car_pass        | Car passes nearby          | Whoosh / engine sound         |
| car_hit         | Hit by vehicle             | Crunch / splat               |
| train_warning   | Train approaching          | Bell dinging                  |
| train_pass      | Train crosses              | Heavy rumble / horn           |
| splash          | Fall in water              | Water splash                  |
| log_land        | Land on log                | Wooden thunk                  |
| coin_collect    | Pick up coin               | Cheerful ding                 |
| eagle_swoop     | Eagle attacks              | Screech + whoosh              |
| character_unlock| New character unlocked     | Fanfare / celebration         |

---

## 13. Music
- **Gameplay:** Upbeat, bouncy chiptune music
- **Tempo:** 130 BPM, major key
- **Style:** Minimal, cheerful, not distracting
- **Loop length:** 30-60 seconds seamless loop
- **No music in original** (sound effects only) -- implementation choice

---

## 14. Visual Effects

| Effect          | Trigger               | Description                        |
|-----------------|-----------------------|------------------------------------|
| Hop squash      | Landing from hop      | Character squashes slightly        |
| Splash particles| Water death           | 6-8 water droplet particles        |
| Dust puff       | Landing on ground     | 3-4 small brown particles          |
| Coin sparkle    | Coin appears          | Rotating coin with sparkle         |
| Flatten         | Car death             | Character flattens vertically      |
| Shadow          | Always under player   | Small oval shadow beneath character|
| Eagle shadow    | Idle timeout warning  | Growing circular shadow            |

---

## 15. Difficulty Progression

Crossy Road has subtle difficulty scaling:

| Distance (rows) | Change                                        |
|------------------|-----------------------------------------------|
| 0 - 50          | Slow vehicles, wide gaps, many grass lanes    |
| 50 - 150        | More roads, faster vehicles, some rivers      |
| 150 - 300       | Train tracks appear, smaller log gaps         |
| 300 - 500       | Dense traffic, more rivers, fewer safe lanes  |
| 500 - 1000      | Maximum density, fast vehicles, narrow gaps   |
| 1000+           | Sustained maximum difficulty                  |

### 15.1 Scaling Formulas
```
vehicle_speed_multiplier = 1.0 + min(distance / 500, 1.0)
vehicle_gap_reduction = max(0, (distance / 100) * 0.5)  // tiles fewer gap
grass_frequency = max(20, 40 - distance / 25)  // percentage
river_frequency = min(25, 15 + distance / 50)   // percentage
```

---

## 16. Procedural Generation Algorithm

```
function generateLane(row_number):
    type = selectLaneType(row_number)  // based on weights + rules

    if type == GRASS:
        num_trees = random(0, min(4, 1 + row_number / 100))
        tree_positions = randomUniquePositions(num_trees, 10)
        // Ensure at least 3 adjacent empty columns for passage
        ensurePassage(tree_positions)
        coin = (random() < 0.01) ? randomEmptyPosition() : null

    elif type == ROAD:
        direction = random(LEFT, RIGHT)
        speed = random(1.0, 2.0) * vehicle_speed_multiplier
        vehicle_type = randomVehicle()
        gap = random(3, 8) - vehicle_gap_reduction
        gap = max(gap, 2)  // minimum gap of 2 tiles

    elif type == RIVER:
        direction = random(LEFT, RIGHT)
        speed = random(0.8, 1.5)
        log_type = random(SMALL_LOG, LARGE_LOG, LILY_PAD)
        gap = random(2, 4)
        // Ensure player can reach next log from current

    elif type == TRAIN:
        frequency = random(4.0, 8.0)  // seconds between trains
        direction = random(LEFT, RIGHT)

    return Lane(type, properties)
```

---

## 17. Collision Detection

### 17.1 Grid-Based Collision
```
player_tile = (player_x / tile_size, player_y / tile_size)

// Tree/bush collision: check before allowing hop
if grid[target_x][target_y].blocked:
    deny_movement()

// Vehicle collision: check after hop and continuously
for vehicle in current_lane.vehicles:
    if rectanglesOverlap(player_rect, vehicle_rect):
        kill_player("vehicle")

// Water collision: check if player is on log/lilypad
if current_lane.type == RIVER:
    on_object = false
    for obj in current_lane.objects:
        if playerOnObject(player, obj):
            on_object = true
            player.x += obj.speed * obj.direction  // ride the object
    if not on_object:
        kill_player("water")

// Train collision
if current_lane.type == TRAIN and train_present:
    kill_player("train")
```

### 17.2 Hitboxes

| Entity       | Hitbox (px)       |
|-------------|-------------------|
| Player       | 24 x 24 (centered in 32x32 tile) |
| Small Car    | 28 x 28          |
| Sedan        | 56 x 28          |
| Truck        | 84 x 28          |
| Bus          | 112 x 28         |
| Log (small)  | 60 x 28          |
| Log (large)  | 92 x 28          |
| Lily pad     | 24 x 24          |
| Train        | 320 x 30 (full width) |
| Coin         | 20 x 20          |

---

## 18. Data Persistence

| Key               | Type    | Description                     |
|-------------------|---------|---------------------------------|
| high_score        | int     | Best distance reached           |
| total_coins       | int     | Coins available for spending    |
| lifetime_coins    | int     | Total coins ever collected      |
| unlocked_chars    | list    | Character IDs unlocked          |
| selected_char     | string  | Currently selected character    |
| games_played      | int     | Total number of runs            |
| last_gift_time    | timestamp | When free gift was last claimed|
| sound_enabled     | bool    | Sound on/off setting            |

---

## 19. Performance Optimization

- Only render and update lanes within 3 rows of visible area (buffer)
- Object pool for vehicles (reuse when off-screen)
- Object pool for logs/lilypads
- Remove lanes more than 5 rows behind camera
- Pre-generate 20 lanes ahead of player
- Batch render ground tiles as single draw call

---

## 20. Color Palette

| Element          | Color (Hex)  |
|------------------|--------------|
| Grass (light)    | #7EC850      |
| Grass (dark)     | #5DA83A      |
| Road asphalt     | #4A4A4A      |
| Road lines       | #FFFF00      |
| Water            | #4FC3F7      |
| Water (deep)     | #2196F3      |
| Log              | #8D6E63      |
| Lily pad         | #4CAF50      |
| Train track      | #757575      |
| Rail             | #9E9E9E      |
| Chicken (body)   | #FFFFFF      |
| Chicken (comb)   | #F44336      |
| Chicken (beak)   | #FF9800      |
| Coin             | #FFD700      |
| Tree trunk       | #6D4C41      |
| Tree leaves      | #388E3C      |
| UI text          | #FFFFFF      |
| Score shadow     | #000000      |

---

## 21. Implementation Checklist

1. [ ] Set up grid-based world (10 columns, scrolling rows)
2. [ ] Create player character with hop animation
3. [ ] Implement 4-directional hopping (forward, back, left, right)
4. [ ] Implement camera that follows forward movement only
5. [ ] Generate grass lanes with trees as blockers
6. [ ] Generate road lanes with moving vehicles
7. [ ] Implement vehicle spawning with gaps and speeds
8. [ ] Generate river lanes with moving logs and lily pads
9. [ ] Implement log-riding mechanic (player moves with log)
10. [ ] Generate train track lanes with warning system
11. [ ] Implement collision detection (vehicles, water, trains)
12. [ ] Add death animations for each death type
13. [ ] Implement eagle idle-timeout mechanic
14. [ ] Add scoring system (forward hops only)
15. [ ] Add coin spawning and collection
16. [ ] Implement character unlock system (gacha)
17. [ ] Create title screen
18. [ ] Create game over screen with stats
19. [ ] Add sound effects
20. [ ] Implement difficulty scaling with distance
21. [ ] Add procedural lane generation with rules
22. [ ] Ensure playable path always exists
23. [ ] Add data persistence (high score, coins, characters)
24. [ ] Polish: squash/stretch, particles, shadows

---

End of Crossy Road specification.
