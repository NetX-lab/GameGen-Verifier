# Tap Tap Dash — Complete Game Specification

## 1. Game Overview

**Title:** Tap Tap Dash
**Genre:** Casual / Arcade / Endless Runner
**Platform:** Mobile (portrait), desktop
**Original Creator:** Second Arm (Cheetah Games)
**Release Year:** 2015
**Core Loop:** A ball rolls along a narrow winding path. Tap to jump over gaps and change direction at corners. The path twists through 90-degree turns on an isometric grid. Missing a jump or failing to turn at a corner sends the ball off the edge. Score by traveling as far as possible.

Tap Tap Dash is a minimalist one-tap endless runner where the player's ball automatically moves forward along a zigzagging path. The only input is tapping: tap once to jump over a gap, tap once at a corner to turn 90 degrees. The challenge is reading the upcoming path and reacting with correctly timed single taps.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Portrait
- **Logical Resolution:** 320 x 568 pixels
- **View:** Isometric top-down
- **Frame Rate:** 60 FPS
- **Art Style:** Minimalist, geometric, pastel colors

### 2.2 Isometric Grid
| Parameter          | Value                              |
|--------------------|------------------------------------|
| Tile size          | 40 x 20 px (isometric diamond)     |
| Path width         | 1 tile (40 px)                     |
| Ball size          | 14 px diameter                     |
| Tile gap size      | 1 tile (40 px gap)                 |

### 2.3 Rendering Layers
```
Layer 0: Background (solid color)
Layer 1: Path tiles (isometric blocks)
Layer 2: Gems / collectibles
Layer 3: Player ball
Layer 4: Particle trail
Layer 5: UI overlay (score)
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

---

## 4. Player Ball

### 4.1 Properties

| Parameter             | Value                          |
|-----------------------|--------------------------------|
| Radius                | 7 px                           |
| Color                 | White (default)                |
| Move speed (initial)  | 3.0 tiles/second               |
| Move speed (max)      | 6.0 tiles/second               |
| Speed increase rate   | +0.01 tiles/s per tile traveled|
| Jump height (visual)  | 20 px arc                      |
| Jump duration         | 300 ms                         |
| Shadow                | Dark ellipse beneath ball      |

### 4.2 Movement
The ball moves automatically along the current direction. There are exactly two possible directions at any time based on the isometric grid:
- **Direction A:** Moving along the positive X-axis (diagonally down-right on screen)
- **Direction B:** Moving along the positive Z-axis (diagonally down-left on screen)

The ball always moves in one of these two directions and changes direction at corners.

```
// Ball movement (isometric)
if direction == A:
    ball.world_x += speed * dt
    ball.screen_x = toScreenX(ball.world_x, ball.world_z)
    ball.screen_y = toScreenY(ball.world_x, ball.world_z)
elif direction == B:
    ball.world_z += speed * dt
    // Convert to screen coordinates
```

### 4.3 Jumping
```
on_tap (when approaching gap):
    jump_timer = 0
    jumping = true

while jumping:
    jump_timer += dt
    progress = jump_timer / jump_duration
    if progress >= 1.0:
        jumping = false
        progress = 1.0

    // Arc height (sine curve)
    jump_height = sin(progress * PI) * max_jump_height
    // Ball visual Y offset = -jump_height

    // Ball continues moving forward during jump
    ball.position += direction * speed * dt
```

### 4.4 Turning
```
on_tap (when at corner tile):
    if direction == A:
        direction = B  // turn left (in world space)
    elif direction == B:
        direction = A  // turn right (in world space)

    // No pause in movement - instant direction change
    // Visual: ball smoothly transitions direction
```

---

## 5. Path Generation

### 5.1 Path Structure
The path is a sequence of straight segments connected by corners. Segments are made of individual tiles.

| Parameter              | Value                          |
|------------------------|--------------------------------|
| Min segment length     | 2 tiles                        |
| Max segment length     | 8 tiles                        |
| Average segment length | 4 tiles                        |
| Gap frequency          | 1 gap per 3-6 tiles           |
| Gap length             | 1 tile (single gap)            |

### 5.2 Path Generation Algorithm
```
function generatePath(num_tiles):
    path = []
    current_pos = (0, 0)
    current_dir = A  // start going right

    while path.length < num_tiles:
        // Generate a straight segment
        segment_length = random(2, 8)

        for i in range(segment_length):
            // Decide if this tile is a gap
            if random() < gap_probability and i > 0 and i < segment_length - 1:
                path.append(Tile(pos=current_pos, type=GAP))
            else:
                path.append(Tile(pos=current_pos, type=SOLID))

            current_pos += direction_vector(current_dir)

        // Add corner tile and change direction
        path.append(Tile(pos=current_pos, type=CORNER))
        current_dir = opposite_dir(current_dir)
        current_pos += direction_vector(current_dir)

    return path
```

### 5.3 Gap Rules
- Gaps never appear on corner tiles
- Gaps never appear as the first or last tile of a segment
- No two consecutive gaps (always at least 1 solid tile between)
- Gaps never appear in the first 5 tiles (tutorial area)

### 5.4 Path Appearance
Each tile is rendered as an isometric block:
```
     /\
    /  \      <- top face (light color)
   /    \
   \    /     <- right face (medium color)
    \  /
     \/       <- bottom edge
```

---

## 6. Tile Types

| Tile Type  | Appearance                  | Behavior                        |
|------------|-----------------------------|---------------------------------|
| Solid      | Full block                  | Ball rolls over safely          |
| Gap        | Missing tile (empty space)  | Must jump over, fall = death    |
| Corner     | Full block with arrow       | Must tap to turn, no tap = fall |
| Gem tile   | Solid with gem on top       | Collect gem by rolling over     |
| Crumble    | Cracked block               | Collapses 500ms after ball passes |

---

## 7. Corner Mechanic

### 7.1 Corner Detection
```
// Ball approaching corner tile
// Player MUST tap within the corner tile to change direction
// If ball passes through corner without tapping: ball continues straight off the edge

corner_tolerance = 0.3 tiles  // How far past corner center the tap is still valid

function onTap():
    nearest_corner = findNearestCorner(ball.position)
    if distance(ball.position, nearest_corner.position) < corner_tolerance:
        changeDirection()
        playSound("turn")
    elif nearestGap(ball.position):
        startJump()
```

### 7.2 Corner Visual
- Corner tiles have a subtle directional arrow or marking
- Arrow indicates the direction the ball will turn toward
- Slight highlight color to differentiate from normal tiles

---

## 8. Gems / Collectibles

### 8.1 Properties

| Parameter       | Value                       |
|-----------------|-----------------------------|
| Gem size        | 10 x 10 px                  |
| Gem shape       | Diamond / octagon           |
| Gem color       | Gold (#FFD700) with sparkle |
| Pickup radius   | 15 px                       |
| Placement       | On solid tiles, centered    |
| Frequency       | 1 gem per 5-10 tiles        |
| Value           | 1 gem (currency)            |

### 8.2 Gem Placement
```
gem_probability = 0.15  // 15% chance per solid tile
// Never on corners or gaps
// Never on first 3 tiles
```

---

## 9. Scoring

| Action                | Points       |
|-----------------------|-------------|
| Each tile traversed   | +1           |
| Gem collected         | +1 gem (separate counter) |

- Score = total tiles traversed
- Display: centered at top of screen, large white number
- Score animates (subtle scale pulse) on increment

---

## 10. Difficulty Progression

| Score Range | Changes                                             |
|-------------|-----------------------------------------------------|
| 0 - 20     | No gaps, slow speed, long segments                   |
| 20 - 50    | Gaps appear (rare), slight speed increase            |
| 50 - 100   | More gaps, shorter segments, faster speed            |
| 100 - 200  | Frequent gaps, crumbling tiles appear               |
| 200 - 500  | Very fast, short segments, many gaps                |
| 500+       | Maximum difficulty sustained                         |

### 10.1 Scaling Formulas
```
speed = min(3.0 + score * 0.015, 6.0)  // tiles per second
gap_probability = min(0.05 + score * 0.001, 0.25)
min_segment_length = max(2, 5 - score / 100)
max_segment_length = max(3, 8 - score / 50)
crumble_probability = max(0, (score - 100) * 0.002)  // appears after score 100
```

---

## 11. Death Conditions

| Cause                    | Visual                               |
|--------------------------|--------------------------------------|
| Fall into gap (no jump)  | Ball falls straight down, fades      |
| Miss corner turn         | Ball rolls off edge, falls           |
| Step on crumbled tile    | Ball falls as tile collapses         |

### 11.1 Death Animation
```
on_death:
    ball.velocity_y = 2.0  // fall downward
    ball.velocity_y += 0.3 * dt  // accelerating fall
    ball.scale = lerp(1.0, 0.0, fall_progress)  // shrink
    ball.alpha = lerp(1.0, 0.0, fall_progress)  // fade

    // Spawn 6 small particles in ball color
    for i in range(6):
        particle = {
            vx: random(-2, 2),
            vy: random(-3, -1),
            color: ball.color,
            size: random(2, 4),
            life: 400ms
        }

    // After 800ms: show game over screen
```

---

## 12. Camera System

### 12.1 Camera Following
```
// Camera follows the ball with slight offset ahead
// In isometric view, camera centers on ball position

camera_target_x = ball.screen_x
camera_target_y = ball.screen_y - 100  // ball slightly below center

camera_x = lerp(camera_x, camera_target_x, 0.08)
camera_y = lerp(camera_y, camera_target_y, 0.08)
```

### 12.2 Visible Area
- Render tiles within 400px of camera center
- Remove tiles more than 600px behind camera
- Pre-generate 40+ tiles ahead of ball

---

## 13. Visual Design

### 13.1 Color Themes
The game cycles through color themes as the player progresses:

| Theme Range | Path Color   | Background    | Accent       |
|-------------|-------------|---------------|--------------|
| 0 - 30      | #4FC3F7     | #1A237E       | #FFFFFF      |
| 30 - 60     | #81C784     | #1B5E20       | #FFFFFF      |
| 60 - 90     | #FFB74D     | #BF360C       | #FFFFFF      |
| 90 - 120    | #CE93D8     | #4A148C       | #FFFFFF      |
| 120 - 150   | #EF5350     | #B71C1C       | #FFFFFF      |
| 150+        | Cycle repeats                                 |

Theme transitions happen smoothly over 10 tiles (lerp colors).

### 13.2 Tile Shading (Isometric)
```
// For each tile, three faces are visible:
top_face_color = theme.path_color
left_face_color = darken(theme.path_color, 20%)
right_face_color = darken(theme.path_color, 40%)
```

### 13.3 Ball Visual
- White circle with subtle shadow beneath
- Shadow is an ellipse (squished vertically for isometric)
- Ball has slight bounce animation while rolling (2px vertical oscillation at 8 Hz)
- Trail: 5-8 fading circles behind ball, decreasing size

---

## 14. UI Layout

### 14.1 Title Screen
```
+---------------------------+
|                           |
|      TAP TAP DASH         |  Y = 80
|                           |
|      [ball rolling        |
|       on demo path]       |  Y = 200-350
|                           |
|      TAP TO START         |  Y = 430
|                           |
|  Gems: 234  Best: 156    |  Y = 510
|                           |
|  [Shop]  [Skins]  [Rate]  |  Y = 540
+---------------------------+
```

### 14.2 Playing Screen
```
+---------------------------+
|          47               |  Score
|                           |
|          /\               |
|         /  \              |  Upcoming path
|        /    \             |
|       /      \    /\      |
|      [  GAP   ]  /  \    |
|     /\        / /    \   |
|    /  \      / /      \  |
|   /  O \    / /        \ |  Ball on path
|  / (ball)\  //          \|
|  \      / \/             |
|   \    /                 |
|    \  /                  |
|     \/                   |
+---------------------------+
```

### 14.3 Game Over Screen
```
+---------------------------+
|                           |
|       GAME OVER           |
|                           |
|       Score: 47           |
|       Best:  156          |
|                           |
|   Gems: +8  (Total: 242) |
|                           |
|   [  TAP TO RETRY  ]     |
|                           |
|   [Home]  [Share]         |
+---------------------------+
```

---

## 15. Sound Effects

| Sound          | Trigger                  | Description                   |
|----------------|--------------------------|-------------------------------|
| roll           | Ball rolling (loop)      | Soft rolling / ambient tone   |
| jump           | Tap to jump              | Quick "whoosh" upward         |
| land           | Land after jump          | Soft thud / tap               |
| turn           | Tap to turn at corner    | Click / direction change      |
| gem_collect    | Pick up gem              | Bright chime                  |
| fall_death     | Fall off edge            | Descending whistle / whoosh   |
| crumble        | Crumble tile collapses   | Cracking / crumbling          |
| milestone      | Every 50 score           | Achievement tone              |

### 15.1 Background Music
- Ambient, rhythmic electronic
- Minimal beats, calming
- 100 BPM, seamless loop
- Volume: 30% (background)

---

## 16. Ball Skins (Shop)

| Skin         | Cost (gems) | Description                 |
|--------------|-------------|------------------------------|
| Default      | Free        | White ball                   |
| Fire         | 50          | Orange with flame trail      |
| Ice          | 50          | Light blue with frost trail  |
| Neon         | 100         | Green with glow effect       |
| Gold         | 150         | Gold metallic                |
| Rainbow      | 200         | Cycles through colors        |
| Pixel        | 100         | Pixelated square             |
| Ghost        | 250         | Translucent with wisp trail  |
| Star         | 300         | Star-shaped                  |
| Galaxy       | 500         | Cosmic texture               |

All skins are cosmetic only (same hitbox and physics).

---

## 17. Advanced Mechanics

### 17.1 Combo System
Consecutive successful jumps or turns without error build a combo:
```
combo_count = 0

on_successful_jump:
    combo_count += 1
on_successful_turn:
    combo_count += 1

if combo_count >= 5:
    show_combo_text("x5 COMBO!")
    // Visual: ball trail intensifies
if combo_count >= 10:
    show_combo_text("x10 COMBO!")
    // Visual: screen edges glow
```

### 17.2 Close Call
When the ball barely makes a jump (lands within 3px of edge):
```
if landing_distance_from_edge < 3:
    show_text("CLOSE CALL!")
    bonus_score += 1
    screen_shake(1px, 50ms)
```

---

## 18. Isometric Rendering

### 18.1 Coordinate Conversion
```
// World (grid) to Screen coordinates
function toScreenX(world_x, world_z):
    return (world_x - world_z) * tile_half_width + screen_center_x

function toScreenY(world_x, world_z):
    return (world_x + world_z) * tile_half_height + screen_offset_y

// tile_half_width = 20 px
// tile_half_height = 10 px
```

### 18.2 Drawing Order
```
// Sort all tiles and entities by (world_x + world_z) for correct overlap
// Higher values drawn last (appear in front)
sort_key(entity) = entity.world_x + entity.world_z
```

### 18.3 Tile Drawing
```
function drawIsometricTile(screen_x, screen_y, color):
    // Top face (diamond shape)
    draw_polygon([
        (screen_x, screen_y - tile_height),      // top
        (screen_x + half_w, screen_y - tile_height + half_h),  // right
        (screen_x, screen_y - tile_height + tile_h),  // bottom
        (screen_x - half_w, screen_y - tile_height + half_h)   // left
    ], color)

    // Left face
    draw_polygon([
        (screen_x - half_w, screen_y - tile_height + half_h),
        (screen_x, screen_y - tile_height + tile_h),
        (screen_x, screen_y),
        (screen_x - half_w, screen_y - half_h)
    ], darken(color, 20%))

    // Right face
    draw_polygon([
        (screen_x + half_w, screen_y - tile_height + half_h),
        (screen_x, screen_y - tile_height + tile_h),
        (screen_x, screen_y),
        (screen_x + half_w, screen_y - half_h)
    ], darken(color, 40%))
```

---

## 19. Input Handling

| Input        | Context             | Action                          |
|--------------|---------------------|---------------------------------|
| Tap          | Approaching gap     | Jump over gap                   |
| Tap          | On corner tile      | Change direction (turn)         |
| Tap          | On normal tile      | Nothing (wasted tap, no penalty)|
| Tap          | Title screen        | Start game                      |
| Tap          | Game over screen    | Restart                         |

### 19.1 Input Disambiguation
```
// How to determine if tap should jump or turn:
// Check what's ahead of the ball within the next few tiles

next_event = lookAhead(ball.position, direction, look_distance=3 tiles)

if next_event.type == GAP:
    // Tap = jump
    jump_at = next_event.position  // when ball reaches gap
elif next_event.type == CORNER:
    // Tap = turn
    turn_at = next_event.position

// Actually, in the original game:
// The action is context-free. Tap always does the NEXT required action.
// If next thing is a gap: tap = jump
// If next thing is a corner: tap = turn
// This simplifies input to always just "tap at the right time"
```

---

## 20. Data Persistence

| Key              | Type  | Description                    |
|------------------|-------|--------------------------------|
| high_score       | int   | Best score                     |
| total_gems       | int   | Gems available                 |
| lifetime_gems    | int   | Total gems ever earned         |
| unlocked_skins   | list  | Skin IDs unlocked              |
| selected_skin    | string| Current skin                   |
| games_played     | int   | Total runs                     |
| total_distance   | int   | Lifetime tiles traversed       |

---

## 21. Implementation Checklist

1. [ ] Set up portrait canvas with dark background
2. [ ] Implement isometric coordinate system
3. [ ] Create isometric tile rendering (3 faces)
4. [ ] Generate straight path segments
5. [ ] Generate corners with alternating directions
6. [ ] Add gaps in path segments
7. [ ] Create ball with auto-movement along path
8. [ ] Implement tap-to-jump over gaps
9. [ ] Implement tap-to-turn at corners
10. [ ] Add death detection (fall off edge, miss jump)
11. [ ] Implement camera following in isometric space
12. [ ] Add gem collectibles on tiles
13. [ ] Create scoring system (tiles traversed)
14. [ ] Add difficulty scaling (speed, gap frequency)
15. [ ] Implement color theme transitions
16. [ ] Add crumbling tiles (post score 100)
17. [ ] Create death animation (fall + particles)
18. [ ] Add ball trail effect
19. [ ] Build title screen
20. [ ] Build game over screen
21. [ ] Add sound effects
22. [ ] Implement ball skin shop
23. [ ] Add data persistence
24. [ ] Add combo system (optional)
25. [ ] Polish: bounce animation, close call feedback

---

End of Tap Tap Dash specification.
