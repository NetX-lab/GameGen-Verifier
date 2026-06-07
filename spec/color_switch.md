# Color Switch — Complete Game Specification

## 1. Game Overview

**Title:** Color Switch
**Genre:** Casual / Arcade
**Platform:** Mobile (portrait), desktop
**Original Creator:** Fortafy Games (David Reichelt)
**Release Year:** 2015
**Core Loop:** Tap to bounce a colored ball upward through rotating, multi-colored obstacles. The ball can only pass through sections of the obstacle that match its current color. Color switches randomly change the ball's color. Score by passing through obstacles.

Color Switch is a vertically-scrolling arcade game focused on color-matching reflexes. The player controls a ball by tapping to bounce it upward. Obstacles rotate or move and are divided into colored segments. The ball can pass through segments that match its color but dies on contact with any other color.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Portrait
- **Logical Resolution:** 320 x 568 pixels
- **Coordinate Origin:** Top-left (0, 0)
- **Background:** Dark (#1A1A2E or #2C3E50)
- **Frame Rate:** 60 FPS

### 2.2 Color System
The game uses exactly 4 colors:

| Color   | Name    | Hex Code  | Usage                       |
|---------|---------|-----------|------------------------------|
| Color 1 | Yellow  | #FFEB3B   | Ball color, obstacle segment |
| Color 2 | Magenta | #E91E63   | Ball color, obstacle segment |
| Color 3 | Cyan    | #00BCD4   | Ball color, obstacle segment |
| Color 4 | Purple  | #9C27B0   | Ball color, obstacle segment |

### 2.3 Rendering Layers
```
Layer 0: Dark background
Layer 1: Stars (collectible)
Layer 2: Obstacles (rotating shapes)
Layer 3: Color switch pickups
Layer 4: Player ball
Layer 5: Score / UI overlay
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

| Parameter              | Value                           |
|------------------------|---------------------------------|
| Radius                 | 12 px                           |
| Color                  | One of the 4 game colors        |
| Initial color          | Random from 4 colors            |
| Starting position      | Center X = 160, Y = 450        |

### 4.2 Physics

| Parameter              | Value                           |
|------------------------|---------------------------------|
| Gravity                | 0.4 px/frame^2 (downward)      |
| Tap impulse            | -8.0 px/frame (upward)         |
| Max fall speed         | 10.0 px/frame                  |
| Max rise speed         | -8.0 px/frame                  |

```
on_tap:
    ball.velocity_y = tap_impulse  // -8.0 (instant set, not additive)

each_frame:
    ball.velocity_y += gravity
    ball.velocity_y = clamp(ball.velocity_y, max_rise, max_fall)
    ball.y += ball.velocity_y

    if ball.y > screen_height + 50:
        game_over()  // fell off bottom
```

### 4.3 Ball Visual
- Solid circle with slight glow effect (radius + 4px, 30% opacity)
- Color matches one of the 4 game colors
- Subtle pulse animation (radius oscillates 12 +/- 1 px at 2 Hz)

---

## 5. Camera System

```
// Camera follows ball upward only (never down)
if ball.y < camera_target_y:
    camera_target_y = ball.y

camera_y = lerp(camera_y, camera_target_y - screen_height * 0.6, 0.1)
// Ball stays in lower 40% of screen as it ascends
```

- Camera only moves upward
- All obstacles scroll downward relative to camera
- Ball falling below camera bottom = death

---

## 6. Obstacles

### 6.1 Obstacle Types

#### 6.1.1 Rotating Circle
```
     ____
    /YYYY\
   |Y    C|
   |Y    C|    Four quarter-circle arcs
   |M    P|    Each a different color
   |M    P|    Rotates continuously
    \MMMM/
     ----

Outer radius: 70 px
Inner radius: 40 px (passage for ball)
Arc width: 30 px
Rotation speed: 1.5 degrees/frame (90 deg/s)
Gap: The opening matches the ball's passage
```

| Parameter        | Value                          |
|------------------|--------------------------------|
| Outer radius     | 70 px                          |
| Inner radius     | 40 px                          |
| Rotation speed   | 1.0 - 3.0 degrees/frame       |
| Direction        | Clockwise or counter-clockwise |
| Segments         | 4 (one per color)              |

#### 6.1.2 Horizontal Bar
```
|YYYYYY|CCCCCC|MMMMMM|PPPPPP|
```
A horizontal bar divided into 4 colored sections, moving left-right.

| Parameter        | Value                          |
|------------------|--------------------------------|
| Total width      | 280 px (4 segments x 70 px)    |
| Height           | 20 px                          |
| Gap              | None (ball passes through matching color) |
| Movement speed   | 2.0 px/frame (horizontal)     |
| Movement range   | +/- 100 px from center         |

#### 6.1.3 Cross / Plus
```
       |CC|
       |CC|
  --YYYYYY---PPPP--
  --YYYYYY---PPPP--
       |MM|
       |MM|
```
Two perpendicular bars forming a cross shape, rotating around center.

| Parameter        | Value                          |
|------------------|--------------------------------|
| Arm length       | 80 px from center              |
| Arm width        | 20 px                          |
| Rotation speed   | 2.0 degrees/frame              |
| Center gap       | 30 x 30 px (ball passes here)  |

#### 6.1.4 Square (Rotating)
```
  YYYYYYYYYY
  C        M
  C        M
  C        M
  PPPPPPPPPP
```
A square outline divided into 4 sides, each a different color, rotating.

| Parameter        | Value                          |
|------------------|--------------------------------|
| Side length      | 120 px                         |
| Wall thickness   | 15 px                          |
| Rotation speed   | 1.5 degrees/frame              |
| Ball passes through matching color sides |

#### 6.1.5 Triangle (Rotating)
Three sides, three colors (one color repeated or only 3 colors used).

| Parameter        | Value                          |
|------------------|--------------------------------|
| Side length      | 100 px                         |
| Wall thickness   | 15 px                          |
| Rotation speed   | 2.0 degrees/frame              |

#### 6.1.6 Horizontal Lines (Alternating)
Multiple horizontal lines stacked, alternating colors, moving in opposite directions.

| Parameter        | Value                          |
|------------------|--------------------------------|
| Line height      | 12 px                          |
| Spacing          | 30 px vertical                 |
| Count            | 3-5 lines                      |
| Speed            | 1.5 px/frame each              |
| Alternating      | Adjacent lines move opposite   |

#### 6.1.7 Dots / Circles
Small colored dots arranged in a circle pattern, rotating.

| Parameter        | Value                          |
|------------------|--------------------------------|
| Dot radius       | 8 px                           |
| Circle radius    | 60 px                          |
| Dot count        | 8 (2 per color)                |
| Rotation speed   | 1.0 degrees/frame              |

---

### 6.2 Obstacle Collision Detection

```
function checkCollision(ball, obstacle):
    // Get obstacle segment at ball position
    // Determine which color the ball is touching

    for segment in obstacle.segments:
        if circleIntersects(ball, segment.shape):
            if segment.color != ball.color:
                return DEATH
            else:
                return SAFE  // pass through

    return NO_CONTACT
```

**For circular obstacles (precise):**
```
// Ball center distance from obstacle center
dist = distance(ball.center, obstacle.center)

// Is ball within the obstacle ring?
if dist > obstacle.inner_radius - ball.radius and dist < obstacle.outer_radius + ball.radius:
    // Determine which color segment the ball is in
    angle = atan2(ball.y - obstacle.y, ball.x - obstacle.x)
    angle = (angle - obstacle.rotation) % 360

    // Each segment spans 90 degrees
    segment_index = floor(angle / 90)
    segment_color = obstacle.colors[segment_index]

    if segment_color != ball.color:
        die()
```

---

## 7. Color Switch Pickup

### 7.1 Properties
| Parameter        | Value                          |
|------------------|--------------------------------|
| Size             | 16 x 16 px                    |
| Shape            | Circle with "C" or rainbow icon|
| Position         | Between obstacles (centered)   |
| Spacing          | One between every 1-2 obstacles|

### 7.2 Behavior
```
on_contact(ball, color_switch):
    // Change ball color to a DIFFERENT random color
    new_color = random_choice(colors - ball.current_color)
    ball.color = new_color
    color_switch.collected = true

    // Visual: brief flash, particle burst in all 4 colors
    // Sound: bright "switch" chime
```

### 7.3 Placement
- Always placed between obstacles
- Usually centered horizontally
- Vertically: at the midpoint between two obstacles
- Mandatory when next obstacle requires a different color for passage

---

## 8. Star Collectibles

### 8.1 Properties
| Parameter        | Value                          |
|------------------|--------------------------------|
| Size             | 20 x 20 px                    |
| Shape            | 5-pointed star                 |
| Color            | White with glow                |
| Position         | Inside obstacles (center)      |
| Value            | 1 star (currency)              |

### 8.2 Star Placement
- One star inside each obstacle (centered in the passable area)
- Collecting stars is required to pass through obstacles (they serve as score markers)
- Star pickup radius: 20 px

---

## 9. Scoring

| Action                  | Points    |
|-------------------------|-----------|
| Pass through obstacle   | 1 point   |
| Collect star            | 1 star    |

- Score = number of obstacles passed
- Stars = currency for unlocking ball designs
- Score displayed at top center of screen

---

## 10. Difficulty Progression

| Score Range | Changes                                              |
|-------------|------------------------------------------------------|
| 0 - 5      | Slow rotation, simple circles, generous spacing      |
| 5 - 15     | Faster rotation, bars and crosses appear             |
| 15 - 30    | Mixed obstacles, tighter vertical spacing            |
| 30 - 50    | Fast rotation, squares and triangles                 |
| 50+        | Maximum speed, complex obstacle combinations         |

### 10.1 Scaling Parameters
```
rotation_speed_multiplier = 1.0 + score * 0.03  // +3% per point
obstacle_spacing = max(200, 300 - score * 3)     // px between obstacles
movement_speed = 1.0 + score * 0.02              // for moving obstacles
```

### 10.2 Obstacle Selection
```
// Probability of each obstacle type by score:
score 0-5:   circle 80%, bar 20%
score 5-15:  circle 40%, bar 30%, cross 20%, square 10%
score 15-30: circle 25%, bar 25%, cross 20%, square 15%, triangle 10%, lines 5%
score 30+:   all types with equal probability (16% each)
```

---

## 11. Obstacle Generation

```
function generateObstacle(y_position, score):
    type = selectObstacleType(score)
    rotation_speed = baseRotationSpeed(type) * rotation_speed_multiplier(score)
    direction = random_choice(CLOCKWISE, COUNTER_CLOCKWISE)

    obstacle = createObstacle(type, y_position, rotation_speed, direction)

    // Ensure the ball's current color can pass through
    // Rotate obstacle so that at some point, the matching color is at the entry point
    // (This is naturally handled by the continuous rotation)

    // Place color switch between this and next obstacle if:
    // - Random chance (50%) or
    // - Next obstacle requires different color alignment
    if random() < 0.5 or needsColorChange():
        placeColorSwitch(y_position + obstacle_spacing / 2)

    return obstacle
```

---

## 12. UI Layout

### 12.1 Title Screen
```
+---------------------------+
|                           |
|      COLOR SWITCH         |  Y = 80
|    [rainbow circle icon]  |  Y = 140
|                           |
|       Stars: 234          |  Y = 220
|                           |
|         (o)               |  Ball (bouncing animation)
|                           |
|     TAP TO PLAY           |  Y = 420
|                           |
|  [Shop]  [Modes]  [Rate]  |  Y = 500
+---------------------------+
```

### 12.2 Playing Screen
```
+---------------------------+
|          12               |  Score (centered, Y=40)
|                           |
|       ____                |
|      / YY \               |  Rotating circle obstacle
|     |Y   C|               |
|     |M   P|               |
|      \MM /                |
|       ---                 |
|                           |
|        [C]                |  Color switch pickup
|                           |
|     ____                  |
|    /    \                 |  Another obstacle
|   |      |               |
|    \____/                 |
|                           |
|         (O)               |  Player ball
|                           |
+---------------------------+
```

### 12.3 Game Over Screen
```
+---------------------------+
|                           |
|       GAME OVER           |
|                           |
|       Score: 12           |
|       Best:  28           |
|                           |
|    Stars earned: 12       |
|    Total: 246             |
|                           |
|   [  TAP TO RETRY  ]     |
|                           |
|   [Home]  [Share]         |
+---------------------------+
```

---

## 13. Sound Effects

| Sound            | Trigger                   | Description                    |
|------------------|---------------------------|-------------------------------|
| tap_bounce       | Player taps               | Short pop / bounce             |
| pass_obstacle    | Ball passes through       | Bright "ding" / chime          |
| star_collect     | Collect star              | Sparkle / coin sound           |
| color_switch     | Pick up color switch      | Quick "switch" / transition    |
| death            | Hit wrong color           | Shatter / break sound          |
| combo_tone       | Rapid successive passes   | Rising pitch sequence          |

### 13.1 Background Music
- Upbeat electronic / chiptune
- 130 BPM, minor key with bright elements
- 30-second seamless loop
- Volume: 40% (below SFX)

---

## 14. Death Mechanic

### 14.1 Death Trigger
- Ball touches any obstacle segment whose color does not match ball's color
- Ball falls below the screen bottom

### 14.2 Death Animation
```
on_death:
    // Ball explodes into colored particles
    for i in range(12):
        particle = {
            x: ball.x + random(-5, 5),
            y: ball.y + random(-5, 5),
            vx: random(-4, 4),
            vy: random(-6, 2),
            color: random_choice(all_4_colors),
            radius: random(2, 5),
            life: 500ms,
            gravity: 0.2
        }

    // Screen flash: white, 30ms
    // All obstacles freeze rotation
    // Delay 500ms, then show game over
```

---

## 15. Ball Skins (Shop)

### 15.1 Unlockable Balls

| Ball Skin        | Cost (stars) | Visual                        |
|------------------|-------------|-------------------------------|
| Default          | Free        | Solid circle                  |
| Glow             | 50          | Bright glow effect            |
| Star             | 100         | Star shape instead of circle  |
| Square           | 75          | Square shape                  |
| Diamond          | 150         | Diamond/rhombus shape         |
| Ring             | 200         | Circle outline (hollow)       |
| Emoji            | 250         | Smiley face on ball           |
| Galaxy           | 500         | Swirling galaxy texture       |

### 15.2 All skins are cosmetic only (same hitbox).

---

## 16. Game Modes

### 16.1 Classic Mode (Default)
- Described above: tap to bounce through obstacles

### 16.2 Challenge Mode
- Specific obstacle sequences to complete
- 100 levels with increasing difficulty
- Earn stars on completion

### 16.3 Reverse Mode
- Ball falls downward
- Tap to accelerate downward (against upward floatiness)
- Obstacles are below the ball

### 16.4 Race Mode
- Side-scrolling instead of vertical
- Ball rolls along bottom, tap to jump
- Color obstacles overhead

---

## 17. Particle Effects

| Effect             | Trigger                | Details                        |
|--------------------|------------------------|-------------------------------|
| Ball glow          | Always                 | Soft circular glow, ball color|
| Star collect       | Collect star           | 6 white sparkles outward      |
| Color switch       | Pick up color switch   | 4 colored particles (1 each)  |
| Death burst        | Ball dies              | 12 colored fragments          |
| Obstacle glow      | Matching color pass    | Brief brightening of segment  |
| Trail              | Ball moving            | Fading trail of ball color    |

---

## 18. Color Matching Logic (Detailed)

```
// Core color matching rule:
// Ball can pass through obstacle segments ONLY if segment.color == ball.color
// Ball touching ANY other color segment = instant death

// Special case: Ball in the "gap" area (inside ring of circular obstacle)
// is safe regardless of rotation state

// Edge case: Ball exactly at boundary between two color segments
// Use ball CENTER position for color determination
// If center is within 2px of boundary, use the nearest segment

function getSegmentColorAtPoint(obstacle, point):
    if obstacle.type == CIRCLE:
        dx = point.x - obstacle.center_x
        dy = point.y - obstacle.center_y
        angle = atan2(dy, dx) - obstacle.rotation_angle
        angle = normalizeAngle(angle)  // 0 to 360

        segment_index = floor(angle / (360 / obstacle.num_segments))
        return obstacle.colors[segment_index]

    elif obstacle.type == BAR:
        relative_x = point.x - obstacle.x + obstacle.offset
        segment_index = floor(relative_x / obstacle.segment_width)
        segment_index = clamp(segment_index, 0, obstacle.num_segments - 1)
        return obstacle.colors[segment_index]

    // ... similar for other types
```

---

## 19. Performance Optimization

- Only update/render obstacles within 2 screen heights of camera
- Object pool for particles (max 50)
- Pre-calculate rotation matrices for obstacle rendering
- Collision check only for obstacles near ball Y position (+/- 100px)
- Background: static (no per-frame redraw)

---

## 20. Data Persistence

| Key              | Type  | Description                      |
|------------------|-------|----------------------------------|
| high_score       | int   | Best score in classic mode       |
| total_stars      | int   | Stars available for spending     |
| lifetime_stars   | int   | Total stars ever collected       |
| unlocked_balls   | list  | Ball skin IDs unlocked           |
| selected_ball    | string| Currently selected ball skin     |
| games_played     | int   | Total classic mode games         |
| challenge_progress| int  | Highest challenge level beaten   |
| sound_enabled    | bool  | Sound on/off                     |
| music_enabled    | bool  | Music on/off                     |

---

## 21. Implementation Checklist

1. [ ] Set up portrait canvas with dark background
2. [ ] Create ball with tap-to-bounce physics
3. [ ] Implement 4-color system
4. [ ] Create rotating circle obstacle
5. [ ] Implement color-matching collision detection
6. [ ] Create horizontal bar obstacle
7. [ ] Create cross/plus obstacle
8. [ ] Create rotating square obstacle
9. [ ] Create rotating triangle obstacle
10. [ ] Create alternating lines obstacle
11. [ ] Implement color switch pickup
12. [ ] Add star collectibles inside obstacles
13. [ ] Implement camera system (upward follow)
14. [ ] Create procedural obstacle generation
15. [ ] Implement difficulty scaling
16. [ ] Add scoring system
17. [ ] Create death animation (particle burst)
18. [ ] Build title screen
19. [ ] Build game over screen
20. [ ] Add sound effects
21. [ ] Add background music
22. [ ] Implement ball skin shop
23. [ ] Add data persistence
24. [ ] Add particle trail effect
25. [ ] Implement challenge mode (optional)

---

## 22. Mathematical Reference

**Ball trajectory after tap:**
```
initial_velocity = -8.0 px/frame
gravity = 0.4 px/frame^2
time_to_apex = 8.0 / 0.4 = 20 frames = 333 ms
max_height = v^2 / (2*g) = 64 / 0.8 = 80 px

// Ball rises 80 px per tap
// Obstacle spacing should be ~200-300 px
// Requires 3-4 taps to traverse between obstacles
```

**Obstacle rotation timing:**
```
At 1.5 deg/frame:
Full rotation = 360 / 1.5 = 240 frames = 4 seconds
Quarter rotation (safe window) = 60 frames = 1 second
// Player has ~1 second window per matching segment pass

At 3.0 deg/frame:
Full rotation = 120 frames = 2 seconds
Quarter rotation = 30 frames = 0.5 seconds
// Only 0.5 second window - much harder
```

---

End of Color Switch specification.
