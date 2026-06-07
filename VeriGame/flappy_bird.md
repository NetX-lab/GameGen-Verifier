# Flappy Bird — Complete Game Specification

## 1. Game Overview

**Title:** Flappy Bird
**Genre:** Casual / Arcade
**Platform:** Mobile (portrait orientation), also playable on desktop
**Original Creator:** Dong Nguyen (dotGears)
**Release Year:** 2013
**Core Loop:** Tap to flap, navigate through pipe gaps, survive as long as possible, beat your high score.

Flappy Bird is a side-scrolling endless runner where the player controls a small bird that must fly between columns of green pipes without hitting them. The bird is constantly affected by gravity and the player taps the screen to make the bird flap upward. Each successful pass through a pair of pipes scores one point. The game ends instantly upon collision with a pipe or the ground.

---

## 2. Technical Foundation

### 2.1 Display and Coordinate System
- **Orientation:** Portrait
- **Logical Resolution:** 288 x 512 pixels (original); scale to fit device
- **Coordinate Origin:** Top-left corner (0, 0)
- **X-axis:** Increases rightward
- **Y-axis:** Increases downward
- **Frame Rate:** 60 FPS target
- **Physics Timestep:** Fixed at 1/60 second (16.67ms)

### 2.2 Rendering Layers (back to front)
```
Layer 0: Background (sky gradient, clouds)
Layer 1: Pipes
Layer 2: Ground (scrolling)
Layer 3: Bird
Layer 4: UI / Score overlay
Layer 5: Game Over panel
```

---

## 3. Game States

```
+------------+       +----------+       +---------+       +-----------+
|   SPLASH   | ----> |  READY   | ----> | PLAYING | ----> | GAME_OVER |
| (title)    |  tap  | (get     |  tap  | (main   | die   | (score    |
|            |       |  ready)  |       |  loop)  |       |  panel)   |
+------------+       +----------+       +---------+       +-----------+
      ^                                                        |
      +------------------  tap (restart)  ---------------------+
```

### State Descriptions

| State     | Description                                                        |
|-----------|--------------------------------------------------------------------|
| SPLASH    | Title screen with logo, bird bobbing, "Tap to Play" prompt         |
| READY     | Bird visible, "Get Ready" text, tap instruction; no pipes yet      |
| PLAYING   | Gravity active, pipes scrolling, score counting                    |
| GAME_OVER | Bird fallen, score panel with current/best score, medal, restart   |

---

## 4. Core Mechanics

### 4.1 Bird Physics

The bird is subject to constant downward gravity. Each tap applies an instantaneous upward velocity (impulse).

| Parameter               | Value                        |
|--------------------------|------------------------------|
| Gravity (acceleration)   | 0.25 px/frame (900 px/s^2)  |
| Flap impulse (velocity)  | -4.6 px/frame (-276 px/s)   |
| Max fall speed (terminal)| 8.0 px/frame (480 px/s)     |
| Bird X position (fixed)  | 67 px from left edge         |
| Bird width               | 34 px                        |
| Bird height              | 24 px                        |
| Hitbox                   | Reduced circle, radius 12 px, centered on bird |

**Physics Update (per frame):**
```
velocity = velocity + gravity
if velocity > max_fall_speed:
    velocity = max_fall_speed
bird_y = bird_y + velocity
```

**On Tap (flap):**
```
velocity = flap_impulse   // instantly set, not additive
play_flap_sound()
```

### 4.2 Bird Rotation

The bird rotates to visually indicate direction of travel.

| Condition                     | Target Angle   | Rotation Speed       |
|-------------------------------|----------------|----------------------|
| After flap (velocity < 0)    | -30 degrees    | Instant snap         |
| Falling (velocity > 0)       | +90 degrees    | 4 degrees/frame      |
| Neutral (velocity ~ 0)       | 0 degrees      | Interpolated         |

- Maximum upward tilt: -30 degrees
- Maximum downward tilt: +90 degrees (nosedive)
- After flap, hold -30 degrees for 10 frames, then begin rotating down

### 4.3 Bird Animation

The bird has 3 animation frames for wing flapping:

| Frame | Description       | Duration         |
|-------|-------------------|------------------|
| 0     | Wings up          | 100 ms           |
| 1     | Wings mid         | 100 ms           |
| 2     | Wings down        | 100 ms           |

- Animation cycles continuously during READY and PLAYING states
- Animation stops on death (frozen on current frame)
- Total cycle: 300 ms (3.33 cycles per second)

---

## 5. Pipes

### 5.1 Pipe Properties

| Parameter                 | Value                          |
|---------------------------|--------------------------------|
| Pipe width                | 52 px                          |
| Pipe cap width            | 56 px (2px overhang each side) |
| Pipe cap height           | 26 px                          |
| Gap between top/bottom    | 100 px (vertical opening)      |
| Horizontal spacing        | 180 px (center to center)      |
| Scroll speed              | 2.0 px/frame (120 px/s)        |
| Pipe color                | Green (#73BF2E body, #558B2F cap) |

### 5.2 Pipe Generation

Pipes are generated off-screen to the right and scroll leftward.

**Gap Position Randomization:**
```
min_gap_top = 80 px    (top of gap, measured from top of screen)
max_gap_top = 280 px   (top of gap, measured from top of screen)
gap_top = random_integer(min_gap_top, max_gap_top)
gap_bottom = gap_top + 100
```

**Spawning Logic:**
- First pipe spawns at x = 350 px (gives player time to prepare)
- Subsequent pipes spawn every 180 px horizontally
- Pipes are recycled when they scroll fully off-screen (x < -56 px)
- Maintain a pool of 4-6 pipe pairs for efficient rendering

### 5.3 Pipe Hitbox

Each pipe pair has two rectangular collision zones:
```
Top pipe:    (pipe_x, 0) to (pipe_x + 52, gap_top)
Bottom pipe: (pipe_x, gap_bottom) to (pipe_x + 52, 512)
```

---

## 6. Ground

| Parameter          | Value                        |
|--------------------|------------------------------|
| Ground height      | 112 px (bottom of screen)    |
| Ground Y position  | 400 px (top of ground area)  |
| Scroll speed       | 2.0 px/frame (matches pipes) |
| Ground texture     | Repeating pattern, 336 px wide |

- Ground scrolls continuously in READY and PLAYING states
- Ground stops scrolling on GAME_OVER
- Ground is a hard collision boundary (instant death)

---

## 7. Scoring

### 7.1 Point Scoring
- Player earns **1 point** each time the bird's center X passes the center X of a pipe pair
- Score check: `bird_x > pipe_center_x` and pipe has not been scored yet
- Each pipe pair can only be scored once (flag it after scoring)

### 7.2 Score Display

**During Play:**
- Large white digits centered horizontally at Y = 50 px
- Each digit is a sprite (0-9), width ~24 px, height ~36 px
- Black outline/shadow offset: 1px right, 1px down
- Font style: bold, blocky pixel font

**Game Over Panel:**
```
+----------------------------------+
|          GAME OVER               |
|                                  |
|  +----------------------------+  |
|  |  Score:              XXX   |  |
|  |  Best:               XXX   |  |
|  |  Medal: [O]                |  |
|  +----------------------------+  |
|                                  |
|       [   OK   ]                 |
|                                  |
|    [Share]   [Leaderboard]       |
+----------------------------------+
```

### 7.3 Medals

| Medal    | Score Range | Color         |
|----------|-------------|---------------|
| None     | 0-9         | N/A           |
| Bronze   | 10-19       | #CD7F32       |
| Silver   | 20-29       | #C0C0C0       |
| Gold     | 30-39       | #FFD700       |
| Platinum | 40+         | #E5E4E2       |

- Medal appears in the score panel with a sparkle animation
- New best score triggers a "NEW" badge next to best score

---

## 8. Collision Detection

### 8.1 Algorithm
Use **circle-rectangle** collision for bird against pipes:

```
bird_circle = Circle(center=(bird_x + 17, bird_y + 12), radius=12)

For each pipe rectangle:
    closest_x = clamp(bird_circle.cx, rect.left, rect.right)
    closest_y = clamp(bird_circle.cy, rect.top, rect.bottom)
    dx = bird_circle.cx - closest_x
    dy = bird_circle.cy - closest_y
    if (dx*dx + dy*dy) < (bird_circle.radius * bird_circle.radius):
        COLLISION DETECTED
```

### 8.2 Collision Zones
1. **Top pipe body** — rectangle
2. **Top pipe cap** — rectangle (slightly wider)
3. **Bottom pipe body** — rectangle
4. **Bottom pipe cap** — rectangle (slightly wider)
5. **Ground** — horizontal line at Y = 400
6. **Ceiling** — bird cannot go above Y = 0 (clamped, no death)

### 8.3 Death Sequence
1. On collision: immediately stop pipe scrolling
2. Play "hit" sound effect
3. Bird velocity set to flap impulse (bounce up slightly): -3.0 px/frame
4. Bird then falls under gravity to ground
5. Play "die" sound when bird starts falling after bounce
6. Play "ground hit" sound when bird reaches Y = 400
7. Show game over panel after bird lands (300ms delay)

---

## 9. Background

### 9.1 Sky
- **Day theme:** Gradient from #4EC0CA (top) to #E8FCF0 (bottom, above ground)
- **Night theme:** Gradient from #1A1A2E (top) to #2D4059 (bottom)
- Theme selected randomly at game start (50/50 chance)

### 9.2 Clouds / Cityscape
- Silhouetted buildings and bushes at Y = 300-400 px
- Scroll at 0.5 px/frame (parallax, slower than pipes)
- Seamlessly tiling pattern, 288 px wide

---

## 10. Sound Effects

| Sound       | Trigger                       | Duration | Description                     |
|-------------|-------------------------------|----------|---------------------------------|
| flap        | Player taps                   | ~50ms    | Short "whoosh" / wing beat      |
| point       | Pass through pipe pair        | ~100ms   | "Ding" / bright chime           |
| hit         | Collide with pipe             | ~80ms    | Dull thud / impact              |
| die         | After hit, bird starts falling| ~200ms   | Falling whistle                 |
| swoosh      | UI panel transitions          | ~150ms   | Gentle swoosh                   |

---

## 11. UI Layout

### 11.1 Title / Splash Screen
```
+------------------------------+  (0,0)
|                              |
|      [FLAPPY BIRD LOGO]     |  Y = 100
|                              |
|         /---\                |  Y = 200
|        | o > |  <-- bird     |  (bobbing animation)
|         \---/                |
|                              |
|      [  TAP TO PLAY  ]      |  Y = 350
|                              |
|============================  |  Y = 400 (ground)
|  ////  ////  ////  ////     |
+------------------------------+  (288, 512)
```

### 11.2 Get Ready Screen
```
+------------------------------+
|                              |
|       [ GET READY ]          |  Y = 130
|                              |
|         /---\                |
|        | o > |               |  Y = 240 (bird at start pos)
|         \---/                |
|                              |
|       [tap icon: hand]       |  Y = 300
|                              |
|==============================|  Y = 400
|  ////  ////  ////  ////     |
+------------------------------+
```

### 11.3 Playing Screen
```
+------------------------------+
|            5                 |  score at Y = 50, centered
|                              |
|    +--+         +--+         |
|    |  |         |  |         |  pipes
|    +--+         +--+         |
|    |  |         |  |         |
|    +==+         +==+         |  pipe caps
|                              |
|    +==+   /---\ +==+        |
|    |  |  | o > ||  |        |  bird between pipes
|    +--+   \---/ +--+        |
|    |  |         |  |         |
|    |  |         |  |         |
|==============================|
|  ////  ////  ////  ////     |
+------------------------------+
```

---

## 12. Difficulty Curve

Flappy Bird has NO difficulty curve — the parameters remain constant throughout the entire game. The difficulty is inherent in the precision required. However, perceived difficulty increases as:
- Player fatigue increases reaction time
- Psychological pressure from high score
- Random gap positions can create harder sequences

---

## 13. Input Handling

| Input              | Action                                          |
|--------------------|-------------------------------------------------|
| Tap / Click        | Flap (PLAYING), Start (SPLASH/READY), Restart   |
| Spacebar           | Same as tap (desktop)                            |
| Up Arrow           | Same as tap (desktop)                            |
| Mouse click        | Same as tap (desktop)                            |

- Input is ignored during death animation
- Input during GAME_OVER only registers on "OK" button or after panel fully visible
- No multi-touch handling needed (single input only)
- Input buffer: none (only register taps on the frame they occur)

---

## 14. Data Persistence

### 14.1 High Score
- Store best score in local storage / PlayerPrefs
- Key: "flappy_best_score"
- Display on game over panel
- "NEW" indicator when current score > best score

### 14.2 Reset
- No explicit reset option for high score in original
- Clearing app data resets everything

---

## 15. Performance Considerations

- Object pooling for pipes (reuse off-screen pipes)
- Minimize draw calls (batch sprites)
- Use sprite sheets for all game assets
- Limit particle effects (original has none)
- Ground texture scrolling via UV offset, not object movement

---

## 16. Color Palette

| Element          | Color (Hex) | Description          |
|------------------|-------------|----------------------|
| Sky (day)        | #4EC0CA     | Cyan sky             |
| Sky (night)      | #1A1A2E     | Dark blue            |
| Ground top       | #DED895     | Sandy tan            |
| Ground stripes   | #58A342     | Green grass          |
| Pipe body        | #73BF2E     | Bright green         |
| Pipe cap         | #558B2F     | Dark green           |
| Pipe highlight   | #8EE63A     | Light green edge     |
| Bird body        | #F8C53A     | Yellow-orange        |
| Bird wing        | #E8A030     | Darker orange        |
| Bird beak        | #FA6A34     | Red-orange           |
| Bird eye white   | #FFFFFF     | White                |
| Bird eye pupil   | #000000     | Black                |
| Score text       | #FFFFFF     | White with outline   |
| Score outline    | #000000     | Black shadow         |

---

## 17. Bird Variants

The original game randomly selects one of three bird colors at start:

| Variant  | Body Color | Wing Color | Description    |
|----------|-----------|------------|----------------|
| Yellow   | #F8C53A   | #E8A030    | Default        |
| Blue     | #69C8F2   | #4FACCC    | Blue tint      |
| Red      | #F45C5C   | #D84040    | Red tint       |

Selected randomly at game start with equal probability (33.3% each).

---

## 18. Frame-by-Frame Game Loop

```
function gameLoop():
    // Input
    tapped = checkInput()

    if state == SPLASH:
        animateBirdBobbing()    // sine wave, amplitude 8px, period 800ms
        scrollGround()
        if tapped: state = READY

    else if state == READY:
        animateBirdBobbing()
        animateBirdWings()
        scrollGround()
        if tapped:
            state = PLAYING
            bird.velocity = flap_impulse

    else if state == PLAYING:
        // Physics
        if tapped:
            bird.velocity = flap_impulse
            playSound("flap")

        bird.velocity += gravity
        bird.velocity = min(bird.velocity, max_fall_speed)
        bird.y += bird.velocity

        // Clamp to ceiling
        if bird.y < 0:
            bird.y = 0
            bird.velocity = 0

        // Update rotation
        updateBirdRotation()
        animateBirdWings()

        // Move pipes
        for pipe in pipes:
            pipe.x -= scroll_speed
            if pipe.x < -56:
                recyclePipe(pipe)

        // Spawn new pipes
        maybeSpawnPipe()

        // Score check
        for pipe in pipes:
            if bird.x > pipe.center_x and not pipe.scored:
                score += 1
                pipe.scored = true
                playSound("point")

        // Collision
        if checkCollision():
            state = GAME_OVER
            playSound("hit")
            bird.velocity = -3.0  // death bounce
            scheduleAfter(300ms, showGameOverPanel)

        // Ground collision
        if bird.y >= ground_y - bird.height:
            bird.y = ground_y - bird.height
            state = GAME_OVER
            playSound("hit")

        scrollGround()

    else if state == GAME_OVER:
        // Bird falls if not on ground
        if bird.y < ground_y - bird.height:
            bird.velocity += gravity
            bird.y += bird.velocity
            if bird.y >= ground_y - bird.height:
                bird.y = ground_y - bird.height
                playSound("ground_hit")

        if tapped and gameOverPanelVisible:
            resetGame()
            state = SPLASH

    render()
```

---

## 19. Exact Sprite Dimensions

| Sprite              | Width (px) | Height (px) |
|---------------------|-----------|-------------|
| Bird (each frame)   | 34        | 24          |
| Pipe body segment   | 52        | variable    |
| Pipe cap            | 56        | 26          |
| Ground tile         | 336       | 112         |
| Background          | 288       | 512         |
| Digit (0-9)         | 24        | 36          |
| "Get Ready" text    | 184       | 50          |
| "Game Over" text    | 204       | 54          |
| Score panel         | 226       | 114         |
| Medal               | 44        | 44          |
| OK button           | 80        | 28          |
| Tap instruction     | 114       | 98          |
| Logo                | 178       | 50          |

---

## 20. Implementation Checklist

1. [ ] Set up canvas/renderer at 288x512 logical pixels
2. [ ] Implement game state machine (SPLASH, READY, PLAYING, GAME_OVER)
3. [ ] Create bird with 3-frame wing animation
4. [ ] Implement gravity and flap physics
5. [ ] Implement bird rotation based on velocity
6. [ ] Create scrolling ground with seamless tiling
7. [ ] Implement pipe generation with random gap positions
8. [ ] Implement pipe recycling (object pool)
9. [ ] Add circle-rectangle collision detection
10. [ ] Implement scoring (pipe pass detection)
11. [ ] Create death sequence (bounce, fall, ground hit)
12. [ ] Build score display (sprite-based digits)
13. [ ] Build game over panel with score, best, medal
14. [ ] Add medal system (bronze/silver/gold/platinum)
15. [ ] Implement high score persistence
16. [ ] Add parallax background scrolling
17. [ ] Add day/night theme randomization
18. [ ] Add bird color variant randomization
19. [ ] Implement all sound effects
20. [ ] Add "Get Ready" and title screens
21. [ ] Polish: screen shake on death (optional, not in original)
22. [ ] Performance: sprite batching, object pooling

---

## 21. Common Pitfalls

- Bird must not die when touching ceiling (only clamped)
- Pipe gap must remain constant (100px) throughout entire game
- Score only increments once per pipe pair
- Death bounce must happen BEFORE falling (not just straight drop)
- Ground must stop scrolling on death
- Pipes must stop scrolling on death
- Bird wing animation must stop on death
- The bird's X position never changes (only Y moves)

---

## 22. Mathematical Reference

**Time to fall through gap at terminal velocity:**
```
gap_height = 100 px
terminal_velocity = 8.0 px/frame
time = 100 / 8.0 = 12.5 frames = 208 ms
```

**Time for pipe to cross screen:**
```
screen_width + pipe_width = 288 + 52 = 340 px
scroll_speed = 2.0 px/frame
time = 340 / 2.0 = 170 frames = 2.83 seconds
```

**Time between pipes:**
```
pipe_spacing = 180 px
scroll_speed = 2.0 px/frame
time = 180 / 2.0 = 90 frames = 1.5 seconds
```

**Flap apex (time to reach highest point after flap):**
```
velocity_after_flap = -4.6 px/frame
gravity = 0.25 px/frame^2
time_to_apex = 4.6 / 0.25 = 18.4 frames = 307 ms
height_gained = v^2 / (2*g) = 4.6^2 / (2*0.25) = 42.32 px
```

---

End of Flappy Bird specification.
