# Stack — Complete Game Specification

## 1. Game Overview

**Title:** Stack
**Genre:** Casual / Arcade
**Platform:** Mobile (portrait), desktop
**Original Creator:** Ketchapp
**Release Year:** 2016
**Core Loop:** Tap to place moving blocks on top of each other, building an ever-growing tower. Blocks slide back and forth; tapping drops them. Any overhanging portion is sliced off. The tower gets narrower with imprecise placement. Game ends when the block becomes too narrow to continue.

Stack is a minimalist stacking game where blocks oscillate horizontally (or on alternating axes). The player taps to drop the current block. Any part that does not align with the block below is cut off. Perfect placements (exact alignment) earn combo bonuses and slightly grow the block. The game is an endless score chaser.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Portrait
- **Logical Resolution:** 320 x 568 (iPhone 5 ratio) or 360 x 640
- **View:** 3D isometric (original) or 2D side view (simplified)
- **Frame Rate:** 60 FPS
- **Art Style:** Solid colored blocks, gradient backgrounds, minimal

### 2.2 3D Implementation (Original)
| Parameter          | Value                              |
|--------------------|------------------------------------|
| Camera angle       | ~45 degrees isometric, looking down|
| Block depth        | 20 units (visual only)             |
| Block height       | 8 units per layer                  |
| Camera follow      | Rises with tower height            |

### 2.3 2D Simplified Implementation
| Parameter          | Value                              |
|--------------------|------------------------------------|
| Block height       | 20 px per layer                    |
| Game width         | 320 px                             |
| Block initial width| 200 px                             |
| Visible stack      | ~20 layers on screen               |

### 2.4 Rendering Layers
```
Layer 0: Background gradient
Layer 1: Tower blocks (stacked)
Layer 2: Current moving block
Layer 3: Sliced-off piece (falling)
Layer 4: Score / UI overlay
Layer 5: Combo text
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

## 4. Core Mechanics

### 4.1 Block Movement

| Parameter              | Value                               |
|------------------------|-------------------------------------|
| Initial block width    | 200 px                              |
| Block height           | 20 px                               |
| Move speed (initial)   | 3.0 px/frame (180 px/s)            |
| Move speed (max)       | 8.0 px/frame (480 px/s)            |
| Speed increase         | +0.05 px/frame per successful place |
| Movement range         | -160 px to +480 px (overshoots sides)|
| Movement axis          | Alternates: X, Z, X, Z... (3D)     |
|                        | Or: left-right every layer (2D)     |

**2D Movement:**
```
block.x += block.speed * block.direction
if block.x + block.width > screen_right + 160:
    block.direction = -1
if block.x < screen_left - 160:
    block.direction = 1
```

**3D Alternating Axes:**
- Odd layers: block moves along X-axis (left-right)
- Even layers: block moves along Z-axis (front-back)
- This creates the characteristic alternating direction

### 4.2 Block Placement (Tap)

When the player taps:
1. Stop the block's movement
2. Calculate overlap with the block below
3. Slice off the non-overlapping portion
4. Remaining portion becomes the new top of the tower
5. Sliced portion falls away with physics
6. Spawn new moving block with width = remaining portion width

```
function placeBlock(current_block, previous_block):
    // Calculate overlap
    overlap_left = max(current_block.x, previous_block.x)
    overlap_right = min(current_block.x + current_block.width,
                        previous_block.x + previous_block.width)

    overlap_width = overlap_right - overlap_left

    if overlap_width <= 0:
        // Complete miss - game over
        gameOver()
        return

    // Check for perfect placement
    overhang = abs((current_block.x + current_block.width/2) -
                   (previous_block.x + previous_block.width/2))

    if overhang < PERFECT_THRESHOLD:
        // PERFECT placement
        perfectPlacement(current_block, previous_block)
    else:
        // Normal placement - slice off overhang
        sliceBlock(current_block, overlap_left, overlap_width)
```

### 4.3 Perfect Placement

| Parameter              | Value                          |
|------------------------|--------------------------------|
| Perfect threshold      | 5 px (center offset < 5 px)   |
| Combo bonus growth     | +2 px width per consecutive perfect |
| Max combo growth       | Up to original block width     |
| Perfect visual effect  | White flash, screen shake      |
| Perfect sound          | Ascending tone (pitch + combo) |

```
function perfectPlacement(block, prev):
    combo_count += 1

    // Snap to perfect position
    block.x = prev.x
    block.width = prev.width

    // Grow block if in combo
    if combo_count >= 2:
        growth = min(2 * combo_count, max_growth)
        block.width += growth
        block.width = min(block.width, INITIAL_BLOCK_WIDTH)
        block.x -= growth / 2  // grow evenly from center

    // Visual feedback
    showPerfectText(combo_count)
    screenShake(intensity=2, duration=100ms)
    spawnParticles(block.center, 8, color=WHITE)
```

### 4.4 Block Slicing

```
function sliceBlock(block, overlap_left, overlap_width):
    combo_count = 0  // reset combo

    // Create the remaining (placed) piece
    placed_piece.x = overlap_left
    placed_piece.width = overlap_width
    placed_piece.y = block.y

    // Create the falling (sliced) piece
    if block.x < overlap_left:
        // Overhang on the left
        sliced.x = block.x
        sliced.width = overlap_left - block.x
    else:
        // Overhang on the right
        sliced.x = overlap_left + overlap_width
        sliced.width = (block.x + block.width) - (overlap_left + overlap_width)

    sliced.velocity_y = 0
    sliced.velocity_x = block.direction * 2.0  // drift in movement direction
    sliced.gravity = 0.3 px/frame^2
    sliced.rotation_speed = block.direction * 3 degrees/frame

    falling_pieces.add(sliced)
```

### 4.5 Falling Sliced Piece Physics
```
each_frame:
    for piece in falling_pieces:
        piece.velocity_y += 0.3  // gravity
        piece.y += piece.velocity_y
        piece.x += piece.velocity_x
        piece.rotation += piece.rotation_speed

        if piece.y > screen_height + 100:
            falling_pieces.remove(piece)
```

---

## 5. Camera System

### 5.1 Camera Behavior
- Camera rises smoothly as tower grows
- Each new block placed: camera target moves up by block_height (20 px)
- Smooth follow: `camera_y = lerp(camera_y, target_y, 0.1)`
- Tower always visible from current block down as far as screen allows
- Old blocks scroll off the bottom of the screen

### 5.2 Camera for 3D
```
camera_position.y = tower_height * block_height + offset_y
camera_look_at = tower_top_center
// Smooth interpolation toward target each frame
```

---

## 6. Scoring

### 6.1 Score Rules

| Action              | Points                             |
|---------------------|------------------------------------|
| Normal placement    | 1 point                            |
| Perfect placement   | 1 + combo_count points             |
| Combo chain         | Consecutive perfects: 1, 2, 3, 4...|

```
score formula:
    if perfect:
        score += 1 + combo_count
    else:
        score += 1
    combo resets to 0 on non-perfect
```

### 6.2 Score Display
- Large centered number at top of screen
- Font: bold, sans-serif, white with slight shadow
- Animates (scale up briefly) when score increases
- Size: ~48 px font equivalent

### 6.3 Combo Display
- "PERFECT" text appears on perfect placement
- "x2", "x3", "x4"... for consecutive perfects
- Text floats up and fades over 600ms
- Each successive perfect: text gets larger and bolder
- Font color: white to gold gradient at high combos

---

## 7. Visual Design

### 7.1 Block Colors
Each layer has a slightly different hue, creating a rainbow gradient effect as the tower grows.

```
function blockColor(layer_index):
    hue = (layer_index * 15) % 360  // 15-degree hue shift per layer
    saturation = 70%
    lightness = 55%
    return HSL(hue, saturation, lightness)
```

Color sequence example (first 12 layers):
| Layer | Hue  | Color Name (approx.) | Hex       |
|-------|------|----------------------|-----------|
| 1     | 0    | Red                  | #D94452   |
| 2     | 15   | Red-Orange           | #D96344   |
| 3     | 30   | Orange               | #D98244   |
| 4     | 45   | Gold                 | #D9A144   |
| 5     | 60   | Yellow               | #D9D944   |
| 6     | 75   | Yellow-Green         | #A1D944   |
| 7     | 90   | Green                | #63D944   |
| 8     | 105  | Green                | #44D963   |
| 9     | 120  | Green                | #44D9A1   |
| 10    | 135  | Teal                 | #44D9D9   |
| 11    | 150  | Cyan                 | #44A1D9   |
| 12    | 165  | Blue                 | #4463D9   |

### 7.2 Background
- Gradient that shifts with tower height
- Colors complement the current block color
- Dark at bottom, lighter at top
- Smooth transition as tower grows

```
bg_top_color = desaturate(blockColor(current_layer), 30%) + lighten(20%)
bg_bottom_color = darken(bg_top_color, 40%)
```

### 7.3 Block Styling
- Flat colored with subtle 3D effect (lighter top face, darker side face)
- Top face: base color
- Front face: darken(base_color, 15%)
- Side face: darken(base_color, 30%)
- No outlines, clean flat aesthetic

---

## 8. Animations

### 8.1 Block Place Animation
```
on_place:
    // Slight bounce of the tower
    tower_offset_y = -3 px
    animate tower_offset_y back to 0 over 150ms (ease-out)

    // Scale pop on placed block
    placed_block.scale = 1.05
    animate placed_block.scale to 1.0 over 100ms
```

### 8.2 Perfect Placement Animation
```
on_perfect:
    // White flash overlay on block
    flash_alpha = 0.8
    animate flash_alpha to 0 over 200ms

    // Screen shake
    shake_amplitude = 2 + combo_count * 0.5  // grows with combo
    shake_duration = 100 + combo_count * 20   // ms
    shake_frequency = 30 Hz

    // Particle burst
    for i in range(8 + combo_count * 2):
        particle = {
            x: block.center_x + random(-30, 30),
            y: block.y,
            vx: random(-3, 3),
            vy: random(-5, -1),
            life: 400ms,
            color: WHITE,
            size: random(2, 5)
        }

    // Floating combo text
    combo_text = "PERFECT x" + combo_count if combo_count > 1 else "PERFECT"
    text_y = block.y - 20
    animate text_y to text_y - 40, fade alpha 1.0 to 0.0 over 600ms
```

### 8.3 Game Over Animation
```
on_game_over:
    // Tower falls apart
    for each block in tower (top to bottom, staggered):
        delay = (tower.length - block.index) * 50ms  // top falls first
        after delay:
            block.physics_enabled = true
            block.velocity_x = random(-2, 2)
            block.velocity_y = random(-3, 0)
            block.gravity = 0.4
            block.rotation_speed = random(-5, 5)

    // After all blocks have fallen (1.5 seconds):
    show game_over_panel
```

---

## 9. UI Layout

### 9.1 Title Screen
```
+---------------------------+
|                           |
|          STACK            |  Y = 100
|                           |
|    +------------------+   |
|    |                  |   |
|    +------------------+   |  Pre-built
|      +------------+       |  decorative
|      |            |       |  tower
|      +------------+       |
|        +--------+         |
|        |        |         |
|        +--------+         |
|                           |
|     TAP TO START          |  Y = 480
|                           |
|   Best: 42                |  Y = 520
+---------------------------+
```

### 9.2 Playing Screen
```
+---------------------------+
|          23               |  Score (centered, Y=40)
|                           |
|  [  moving block   ] -->  |  Current block oscillating
|  +-------------------+    |  Top of tower
|   +-----------------+     |  Previous block (slightly narrower)
|    +---------------+      |  Stack getting narrower
|     +-------------+       |
|      +-----------+        |
|       +---------+         |
|        +-------+          |
|         +-----+           |
|          +---+            |
|           +-+             |
|                           |
+---------------------------+
```

### 9.3 Game Over Screen
```
+---------------------------+
|                           |
|       GAME OVER           |
|                           |
|       Score: 23           |
|       Best:  42           |
|                           |
|    [  TAP TO RETRY  ]    |
|                           |
|    [Share]   [Rate]       |
|                           |
+---------------------------+
```

---

## 10. Difficulty Progression

The game gets harder naturally as:
1. Block width decreases with each imperfect placement
2. Movement speed increases (+0.05/frame per placement)
3. Narrower blocks require more precise timing

| Block Width Range | Perceived Difficulty | Speed (px/frame) |
|-------------------|---------------------|-------------------|
| 200 - 150 px      | Easy                | 3.0 - 4.0        |
| 150 - 100 px      | Medium              | 4.0 - 5.5        |
| 100 - 50 px       | Hard                | 5.5 - 7.0        |
| 50 - 20 px        | Very Hard           | 7.0 - 8.0        |
| < 20 px           | Nearly impossible   | 8.0 (max)        |

### 10.1 Minimum Block Width
- If block width < 2 px after slicing: game over
- Visual: block becomes a thin line before game ends

---

## 11. Sound Design

| Sound           | Trigger                   | Description                     |
|-----------------|---------------------------|---------------------------------|
| place_normal    | Block placed (non-perfect)| Soft thud / click               |
| place_perfect   | Perfect placement         | Bright chime (pitch increases)  |
| combo_2         | 2nd consecutive perfect   | Higher chime                    |
| combo_3         | 3rd consecutive perfect   | Even higher chime               |
| combo_high      | 4+ consecutive perfect    | Musical ascending scale         |
| slice           | Block sliced              | Quick slice / cut sound         |
| piece_fall      | Sliced piece falls        | Fading whoosh                   |
| game_over       | Game ends                 | Tower crumble + sad tone        |
| tower_collapse  | Blocks fall apart         | Cascading thuds                 |

### 11.1 Dynamic Music Note
Perfect placements can play ascending musical notes:
```
note_pitch = base_pitch + combo_count * semitone_interval
// Creates a musical scale with consecutive perfects
// Pentatonic scale: C, D, E, G, A, C', D', E', G', A'...
```

---

## 12. Data Persistence

| Key            | Type  | Description                   |
|----------------|-------|-------------------------------|
| high_score     | int   | Best score achieved           |
| games_played   | int   | Total games played            |
| total_blocks   | int   | Lifetime blocks placed        |
| best_combo     | int   | Longest perfect combo         |
| total_perfects | int   | Lifetime perfect placements   |

---

## 13. Advanced Features

### 13.1 Themes / Skins
| Theme      | Block Style        | Background            |
|------------|--------------------|-----------------------|
| Classic    | Solid flat colors  | Gradient (matching)   |
| Neon       | Glowing edges      | Dark with glow        |
| Pastel     | Soft muted colors  | Light cream/white     |
| Monochrome | Grayscale          | Black to white gradient|
| Wood       | Wood texture       | Warm brown gradient   |

### 13.2 Achievements
| Achievement              | Requirement          |
|--------------------------|----------------------|
| First Stack              | Complete 1 game      |
| Stacker                  | Score 25             |
| Tower Builder            | Score 50             |
| Architect                | Score 100            |
| Perfect x5               | 5 consecutive perfects|
| Perfect x10              | 10 consecutive perfects|
| Marathon                 | 500 total blocks     |

---

## 14. 3D Implementation Notes (Isometric)

For the original 3D isometric look:
```
// Convert 3D position to 2D screen position
function toScreen(x, y, z):
    screen_x = (x - z) * cos(30) * scale + screen_center_x
    screen_y = -y * scale + (x + z) * sin(30) * scale + screen_center_y
    return (screen_x, screen_y)

// Block faces (draw back to front):
// 1. Top face (lightest)
// 2. Left face (medium)
// 3. Right face (darkest)

// Each face is a parallelogram in screen space
```

### 14.1 Block 3D Dimensions
| Dimension | Value    |
|-----------|----------|
| Width (X) | varies   |
| Depth (Z) | varies   |
| Height (Y)| 8 units  |

- Odd layers: width varies, depth = previous depth
- Even layers: depth varies, width = previous width

---

## 15. Implementation Checklist

1. [ ] Set up portrait canvas (320x568 or 360x640)
2. [ ] Create block with oscillating movement
3. [ ] Implement tap-to-place mechanic
4. [ ] Calculate overlap between current and previous block
5. [ ] Implement block slicing (create placed + falling pieces)
6. [ ] Add falling piece physics (gravity, rotation, drift)
7. [ ] Detect perfect placement (threshold check)
8. [ ] Implement combo system (consecutive perfects)
9. [ ] Add block width growth on perfect combos
10. [ ] Implement camera follow (smooth rise)
11. [ ] Create rainbow color system for layers
12. [ ] Add background gradient that shifts
13. [ ] Implement scoring (normal + combo bonus)
14. [ ] Add score display with animation
15. [ ] Add "PERFECT" floating text
16. [ ] Create game over condition (block too narrow or complete miss)
17. [ ] Add game over animation (tower collapse)
18. [ ] Build title screen
19. [ ] Build game over screen with score/best
20. [ ] Add speed increase with progress
21. [ ] Add screen shake on perfect
22. [ ] Add particle effects
23. [ ] Implement all sound effects
24. [ ] Add data persistence (high score)
25. [ ] Optional: 3D isometric rendering
26. [ ] Optional: alternating X/Z axis movement (3D)

---

## 16. Mathematical Analysis

**Probability of perfect placement at various speeds and widths:**
```
// Player reaction precision assumed ~30ms variance (gaussian)
// Block moves speed px/frame, so in 30ms it moves:
movement_in_reaction = speed * (30/16.67) px

// For a "perfect" threshold of 5px:
// Need to tap within 5px window
// Window duration = 5 / speed frames = 5 / speed * 16.67 ms

At speed 3.0: window = 27.8 ms (very achievable)
At speed 5.0: window = 16.7 ms (challenging)
At speed 7.0: window = 11.9 ms (very hard)
At speed 8.0: window = 10.4 ms (extremely hard)
```

**Expected game length (mathematical model):**
```
Starting width: 200 px
Average overhang per non-perfect placement: ~10-20 px
Average game length: 15-25 placements for casual player
Expert with combos: 50-100+ placements
```

---

End of Stack specification.
