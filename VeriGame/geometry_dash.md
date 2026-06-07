# Geometry Dash — Complete Game Specification

## 1. Game Overview

**Title:** Geometry Dash
**Genre:** Casual / Rhythm Platformer
**Platform:** Mobile, desktop (landscape)
**Original Creator:** Robert Topala (RobTop Games)
**Release Year:** 2013
**Core Loop:** Navigate a square icon through a side-scrolling obstacle course synchronized to music. Tap to jump (or fly, in certain modes). One-hit death — restart the entire level from the beginning. Practice until you can complete the level in one run.

Geometry Dash is a rhythm-based platformer where the player character (a cube by default) auto-scrolls rightward at a constant speed. The player's only input is tapping to jump (or hold in certain vehicle modes). Levels are hand-crafted obstacle courses set to electronic music. Contact with any obstacle or hazard means instant death and restart.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Landscape
- **Logical Resolution:** 480 x 270 (16:9) or 960 x 540
- **Coordinate Origin:** Bottom-left
- **Frame Rate:** 60 FPS (critical for timing)
- **Scroll Direction:** Left to right (character stays in left third)

### 2.2 World Units
| Parameter            | Value                          |
|----------------------|--------------------------------|
| Block size           | 30 x 30 px (1 unit)           |
| Player size          | 30 x 30 px (cube mode)        |
| Ground Y position    | Y = 30 px (top of ground row) |
| Ceiling Y position   | Y = 240 px (bottom of ceiling)|
| Normal speed         | 8.4 units/s (252 px/s)        |
| Slow speed           | 7.0 units/s (210 px/s)        |
| Fast speed           | 10.4 units/s (312 px/s)       |
| Very fast speed      | 12.0 units/s (360 px/s)       |
| Ultra fast speed     | 15.6 units/s (468 px/s)       |

### 2.3 Rendering Layers
```
Layer 0: Background color (solid or gradient)
Layer 1: Background decoration (parallax objects)
Layer 2: Ground decoration
Layer 3: Ground / ceiling blocks
Layer 4: Obstacles (spikes, blocks, saws)
Layer 5: Portals and pads
Layer 6: Player icon
Layer 7: Particle trail
Layer 8: UI overlay (progress bar, percentage, pause)
```

---

## 3. Game States

```
+---------+     +----------+     +---------+
|  MENU   | --> | PLAYING  | --> | COMPLETE|
+---------+     +----------+     +---------+
                  |      ^
                  v      |
               +---------+
               | DEATH   | (instant restart)
               +---------+
```

---

## 4. Game Modes (Vehicle Types)

### 4.1 Mode Overview

| Mode        | Icon Shape    | Gravity | Player Input              | Size (px) |
|-------------|---------------|---------|---------------------------|-----------|
| Cube        | Square        | Down    | Tap to jump               | 30 x 30   |
| Ship        | Triangle/Ship | Down    | Hold to fly up, release fall| 30 x 30  |
| Ball        | Circle        | Down    | Tap to switch gravity     | 30 x 30   |
| UFO         | UFO shape     | Down    | Tap for short upward boost| 30 x 30   |
| Wave        | Dart/Arrow    | Down    | Hold=up diagonal, release=down| 30 x 20|
| Robot       | Mech square   | Down    | Hold to jump higher       | 30 x 36   |
| Spider      | Spider shape  | Down    | Tap to teleport to opposite surface | 30 x 30 |

### 4.2 Cube Mode (Default)

| Parameter           | Value                          |
|---------------------|--------------------------------|
| Jump velocity       | -10.2 units/s (upward)         |
| Gravity             | 26.0 units/s^2 (downward)      |
| Max fall speed      | 15.0 units/s                   |
| Jump height         | ~2.0 blocks (60 px)            |
| Jump duration       | ~390 ms (up), ~390 ms (down)   |
| Rotation on jump    | 90 degrees per jump (visual)   |
| Ground snap         | Immediately stops falling on ground |

**Cube Physics:**
```
on_tap:
    if on_ground:
        velocity_y = -jump_velocity  // -10.2

each_frame:
    velocity_y += gravity * dt
    velocity_y = min(velocity_y, max_fall_speed)
    position_y += velocity_y * dt

    if position_y <= ground_y:
        position_y = ground_y
        velocity_y = 0
        on_ground = true

    // Visual rotation
    if not on_ground:
        rotation += 360 / jump_duration * dt  // smooth 90-degree turn per jump
    else:
        rotation = snap_to_nearest_90(rotation)
```

### 4.3 Ship Mode

| Parameter           | Value                          |
|---------------------|--------------------------------|
| Fly acceleration    | -15.0 units/s^2 (upward)      |
| Gravity             | 12.0 units/s^2 (downward)      |
| Max fly speed       | -8.0 units/s (upward)          |
| Max fall speed      | 8.0 units/s (downward)         |
| Rotation            | Based on vertical velocity     |

```
each_frame:
    if holding:
        velocity_y -= fly_acceleration * dt
        velocity_y = max(velocity_y, -max_fly_speed)
    else:
        velocity_y += gravity * dt
        velocity_y = min(velocity_y, max_fall_speed)

    position_y += velocity_y * dt
    rotation = atan2(velocity_y, scroll_speed) * (180/PI)
```

### 4.4 Ball Mode

```
on_tap:
    gravity_direction *= -1  // flip gravity
    // Ball switches between floor and ceiling

gravity_magnitude = 26.0 units/s^2
// Ball rolls along current surface
// Visual: constant rotation in direction of movement
```

### 4.5 UFO Mode

```
on_tap:
    velocity_y = -6.0  // small upward boost (not sustained)
    // Does NOT require being on ground

gravity = 18.0 units/s^2  // slightly lower than cube
// UFO slowly falls, each tap gives a small lift
```

### 4.6 Wave Mode

```
each_frame:
    if holding:
        velocity_y = -scroll_speed  // move up diagonally (45 degrees)
    else:
        velocity_y = scroll_speed   // move down diagonally (45 degrees)

    position_y += velocity_y * dt
    // Wave moves in strict 45-degree angles
    // Trail effect behind the wave
```

### 4.7 Robot Mode

```
on_tap_begin:
    jump_start_time = current_time
    velocity_y = -jump_velocity  // start jumping

on_tap_held:
    // Continue applying upward force
    jump_hold_time = current_time - jump_start_time
    if jump_hold_time < max_hold_time:  // 400ms max
        velocity_y -= hold_boost * dt

on_tap_release:
    // Jump height proportional to hold duration
    // Minimum jump = normal cube jump
    // Maximum jump = ~3 blocks high
```

### 4.8 Spider Mode

```
on_tap:
    // Teleport to opposite surface (floor to ceiling or vice versa)
    if on_floor:
        position_y = ceiling_y - player_height
        gravity_direction = UP  // now on ceiling
    elif on_ceiling:
        position_y = floor_y
        gravity_direction = DOWN  // now on floor
    // Instant teleportation, no arc
```

---

## 5. Obstacles

### 5.1 Obstacle Types

| Obstacle            | Size (blocks) | Shape    | Kill Type         |
|---------------------|--------------|----------|-------------------|
| Spike (triangle)    | 1 x 1       | Triangle | Touch kills       |
| Double spike        | 1 x 2       | Triangle | Touch kills       |
| Spike (ceiling)     | 1 x 1       | Inverted | Touch kills       |
| Block               | 1 x 1       | Square   | Collision kills   |
| Block (2x2)         | 2 x 2       | Square   | Collision kills   |
| Saw blade           | 2 x 2       | Circle   | Touch kills       |
| Pillar              | 1 x 4+      | Rect     | Collision kills   |
| Moving spike        | 1 x 1       | Triangle | Moves up/down     |
| Fake block          | 1 x 1       | Square   | Pass-through (visual trick) |

### 5.2 Spike Hitbox
Spikes use triangular hitboxes, slightly smaller than visual to be forgiving:

```
// Visual triangle: full 30x30
// Hitbox triangle: 24x24, centered (3px inset on each side)
// This makes near-misses feel fair
```

### 5.3 Hazard Placement Grid
All obstacles are placed on a grid (30x30 px cells). The level is a long horizontal strip:

```
Level width: 500-3000 blocks (varies by level)
Level height: 8 blocks (ground to ceiling)
Ground: rows 0 (floor)
Ceiling: row 8
Playable space: rows 1-7
```

---

## 6. Portals and Pads

### 6.1 Portals (Mode Changers)

| Portal              | Color    | Effect                            |
|---------------------|----------|-----------------------------------|
| Cube Portal         | Green    | Switch to Cube mode               |
| Ship Portal         | Magenta  | Switch to Ship mode               |
| Ball Portal         | Orange   | Switch to Ball mode               |
| UFO Portal          | Cyan     | Switch to UFO mode                |
| Wave Portal         | Purple   | Switch to Wave mode               |
| Robot Portal        | Brown    | Switch to Robot mode              |
| Spider Portal       | Gray     | Switch to Spider mode             |
| Size Portal (mini)  | Pink     | Shrink to 50% size               |
| Size Portal (big)   | Green    | Return to 100% size              |
| Speed Portal (slow) | Blue     | Set speed to slow (7.0 u/s)      |
| Speed Portal (fast) | Orange   | Set speed to fast (10.4 u/s)     |
| Speed Portal (vfast)| Purple   | Set speed to very fast (12.0)    |
| Gravity Portal      | Blue/Yellow | Flip gravity direction          |
| Dual Portal         | Yellow   | Spawn second player (mirrored)   |
| Teleport Portal     | Blue     | Teleport to specified position   |

Portal size: 30 x 90 px (3 blocks tall)
Activation: player passes through portal
Effect: instant mode/speed/size change

### 6.2 Pads and Orbs

| Pad/Orb          | Color   | Effect                              |
|------------------|---------|-------------------------------------|
| Jump Pad         | Yellow  | Auto-jump when touched (ground pad) |
| Gravity Pad      | Blue    | Reverse gravity when touched        |
| Boost Pad        | Pink    | Launch forward at 2x speed briefly  |
| Jump Orb         | Yellow  | Tap while touching to jump mid-air  |
| Gravity Orb      | Blue    | Tap to flip gravity mid-air         |
| Dash Orb         | Green   | Tap to dash in specified direction  |
| Teleport Orb     | Pink    | Tap to teleport to linked position  |

Pads: placed on ground/ceiling, auto-activate on contact
Orbs: floating in air, require tap to activate (shown as glowing ring)

---

## 7. Music and Rhythm Sync

### 7.1 Music Integration
- Each official level has a specific song
- Obstacles are placed to match beat drops, buildups, and rhythms
- Visual pulses sync with bass beats
- Background color may shift with music sections

### 7.2 Official Level Songs

| Level | Name             | Song                  | BPM | Length (s) | Difficulty |
|-------|------------------|-----------------------|-----|------------|------------|
| 1     | Stereo Madness   | ForeverBound          | 140 | 92         | Easy       |
| 2     | Back On Track    | DJVI                  | 125 | 93         | Easy       |
| 3     | Polargeist       | Step                  | 130 | 98         | Normal     |
| 4     | Dry Out          | DJVI                  | 135 | 95         | Normal     |
| 5     | Base After Base  | DJVI                  | 140 | 96         | Hard       |
| 6     | Can't Let Go     | DJVI                  | 145 | 102        | Hard       |
| 7     | Jumper           | Waterflame            | 130 | 93         | Harder     |
| 8     | Time Machine     | Waterflame            | 132 | 103        | Harder     |
| 9     | Cycles           | DJVI                  | 140 | 106        | Harder     |
| 10    | xStep            | DJVI                  | 138 | 110        | Insane     |
| 11    | Clutterfunk      | Waterflame            | 142 | 107        | Insane     |
| 12    | Theory of Everything | DJ-Nate           | 165 | 112        | Insane     |
| 13    | Electroman Adv.  | Waterflame            | 128 | 130        | Insane     |
| 14    | Clubstep         | DJ-Nate              | 160 | 114        | Demon      |
| 15    | Electrodynamix   | DJ-Nate              | 128 | 120        | Demon      |

---

## 8. Scoring and Progress

### 8.1 Progress Tracking
- Level progress shown as percentage (0-100%)
- Progress = (player_x / level_total_length) * 100
- Progress bar at top of screen
- Attempt counter: tracks total attempts per level
- Best percentage saved per level

### 8.2 Completion Rewards
| Achievement              | Stars Earned |
|--------------------------|-------------|
| Complete Normal mode     | 1 star      |
| Collect all 3 coins      | 1 star      |
| Complete Practice mode   | N/A         |

### 8.3 Secret Coins
- 3 user coins hidden per level
- Located in secret paths or hard-to-reach areas
- Coin size: 20 x 20 px, gold with star
- Collecting all 3: achievement + unlock reward
- Coins persist across attempts (once collected, stays collected)

### 8.4 Statistics
- Total attempts per level
- Total jumps
- Total play time
- Stars earned
- User coins collected
- Demons completed

---

## 9. Practice Mode

| Feature              | Description                                |
|----------------------|--------------------------------------------|
| Checkpoints          | Auto-placed or manual every ~5 seconds     |
| Respawn              | Restart from last checkpoint, not beginning |
| Progress shown       | Same percentage bar                        |
| No score tracking    | Practice doesn't count for completion      |
| Slow down option     | Play at 0.5x or 0.75x speed               |

Practice mode is essential for learning level layouts. Green checkpoints appear as diamond-shaped markers. On death, respawn at last passed checkpoint.

---

## 10. Visual Effects

### 10.1 Background
```
Background: solid color or gradient
Background pulses with music (brightness +/- 10%)
Parallax layers: 2-3 layers of geometric shapes scrolling at different speeds
Ground line: pulsing with beat
```

### 10.2 Player Effects

| Effect            | Trigger              | Description                     |
|-------------------|----------------------|---------------------------------|
| Trail             | Always (if enabled)  | Color streak behind player      |
| Death particles   | On death             | Player explodes into fragments  |
| Jump particles    | On jump              | Small dust puff at feet         |
| Portal transition | Enter portal         | Flash + mode morph animation    |
| Pad activation    | Hit jump/gravity pad | Bright flash at pad position    |
| Wave trail        | Wave mode            | Continuous colored line trail   |

### 10.3 Death Effect
```
on_death:
    // Player shatters into 8-12 triangular fragments
    for i in range(10):
        fragment = create_triangle(
            position = player.position + random_offset(5),
            velocity = random_direction() * random(200, 400),
            rotation_speed = random(-720, 720),  // degrees/s
            color = player.color,
            lifetime = 0.8 seconds
        )
        fragments.add(fragment)

    // Screen flash (white, 50ms)
    // Camera shake (amplitude 3px, duration 200ms)
    // Restart level after 500ms delay
```

---

## 11. UI Layout

### 11.1 Main Menu
```
+--------------------------------------------------+
|                                                   |
|           GEOMETRY DASH                           |
|           [cube icon spinning]                    |
|                                                   |
|    [Play]   [Create]   [Saved]                   |
|                                                   |
|    [Garage]  [Online]  [Options]                 |
|                                                   |
|    Stars: 45    Coins: 12    Diamonds: 230       |
+--------------------------------------------------+
```

### 11.2 Level Select
```
+--------------------------------------------------+
| [Back]        OFFICIAL LEVELS                     |
|                                                   |
|  +------+  +------+  +------+  +------+         |
|  | L1   |  | L2   |  | L3   |  | L4   |         |
|  | ***  |  | ***  |  | ** . |  | *..  |         |
|  | Easy |  | Easy |  |Normal|  |Normal|         |
|  +------+  +------+  +------+  +------+         |
|                                                   |
|  +------+  +------+  +------+  +------+         |
|  | L5   |  | L6   |  | L7   |  | L8   |         |
|  | ...  |  | ...  |  | ...  |  | ...  |         |
|  | Hard |  | Hard |  |Harder|  |Harder|         |
|  +------+  +------+  +------+  +------+         |
|                                                   |
+--------------------------------------------------+
```

### 11.3 In-Game HUD
```
+--------------------------------------------------+
| [====........................................] 12% |
|  [Pause]                                          |
|                                                   |
|                                                   |
|         (game area - obstacle course)             |
|                                                   |
|                                                   |
|                                                   |
|==========GROUND===================================|
+--------------------------------------------------+
```

### 11.4 Level Complete
```
+--------------------------------------------------+
|                                                   |
|         LEVEL COMPLETE!                           |
|                                                   |
|    Attempts: 47                                   |
|    Jumps: 234                                     |
|    Time: 1:42                                     |
|                                                   |
|    Coins: [*] [*] [ ]                            |
|                                                   |
|    [Menu]  [Practice]  [Next Level]              |
|                                                   |
+--------------------------------------------------+
```

---

## 12. Difficulty Ratings

| Rating     | Stars | Color  | Description                           |
|------------|-------|--------|---------------------------------------|
| Auto       | 1     | N/A    | Plays itself                          |
| Easy       | 1-2   | Blue   | Simple jumps, slow speed              |
| Normal     | 3     | Green  | Basic obstacles, moderate timing      |
| Hard       | 4-5   | Yellow | Tight timing, mixed modes             |
| Harder     | 6-7   | Orange | Complex patterns, fast speed          |
| Insane     | 8-9   | Red    | Very precise timing required          |
| Demon      | 10    | Red+   | Extreme precision, multiple modes     |

---

## 13. Sound Effects

| Sound          | Trigger                  | Description                  |
|----------------|--------------------------|------------------------------|
| jump           | Cube/Robot jump          | Quick "pop" / click          |
| death          | Hit obstacle             | Crash / shatter              |
| orb_activate   | Tap jump orb             | Bright "ting"                |
| pad_jump       | Hit jump pad             | Boing / spring               |
| portal_enter   | Enter mode portal        | Whoosh / transform           |
| speed_change   | Enter speed portal       | Accelerate / decelerate tone |
| coin_collect   | Pick up secret coin      | Sparkle chime                |
| gravity_flip   | Gravity change           | Reverse whoosh               |
| level_start    | Level begins             | 3-2-1 countdown tones        |
| level_complete | Reach end of level       | Triumphant fanfare           |

---

## 14. Player Customization (Garage)

### 14.1 Icon Categories
| Category    | Description              | Unlock Method            |
|-------------|--------------------------|--------------------------|
| Cube icons  | 50+ designs              | Stars, achievements      |
| Ship icons  | 30+ designs              | Stars, achievements      |
| Ball icons  | 30+ designs              | Stars, achievements      |
| UFO icons   | 30+ designs              | Stars, achievements      |
| Wave icons  | 30+ designs              | Stars, achievements      |
| Robot icons | 20+ designs              | Stars, achievements      |
| Spider icons| 20+ designs              | Stars, achievements      |
| Trail effects| 10+ effects             | Stars, achievements      |
| Death effects| 5+ effects              | Stars, achievements      |

### 14.2 Color Customization
- Primary color: player icon color (20+ options)
- Secondary color: glow/outline color (20+ options)
- Glow effect: toggle on/off

---

## 15. Color Palette

| Element          | Color (Hex)  |
|------------------|--------------|
| Default background| #0066FF     |
| Ground           | #1A1A2E      |
| Spike            | #000000 (outline) |
| Jump pad         | #FFD700      |
| Gravity pad      | #00BFFF      |
| Boost pad        | #FF69B4      |
| Jump orb         | #FFD700      |
| Gravity orb      | #00BFFF      |
| Default player   | #00FF00      |
| Progress bar bg  | #333333      |
| Progress bar fill| #00FF00      |
| Portal (ship)    | #FF00FF      |
| Portal (ball)    | #FF8800      |
| Portal (UFO)     | #00FFFF      |
| Portal (wave)    | #8800FF      |
| Death particles  | Player color |
| Coin             | #FFD700      |
| Star (UI)        | #FFD700      |

---

## 16. Camera System

```
camera_x = player_x - screen_width * 0.3  // player at 30% from left
camera_y = 0  // fixed vertical (no vertical scroll in most modes)

// Exception: in ship/UFO/wave modes with tall sections,
// camera may smoothly follow vertical position
if mode in [SHIP, UFO, WAVE]:
    camera_y = lerp(camera_y, player_y - screen_height/2, 0.1)
```

---

## 17. Implementation Pseudocode

```
function gameLoop():
    dt = 1/60

    if state == PLAYING:
        // Move player forward
        player.x += scroll_speed * dt

        // Handle input
        if mode == CUBE:
            if tapped and on_ground:
                player.vy = -jump_velocity
                on_ground = false
        elif mode == SHIP:
            if holding:
                player.vy -= fly_accel * dt
            else:
                player.vy += gravity * dt
            clamp(player.vy, -max_fly, max_fall)
        elif mode == BALL:
            if tapped:
                gravity_dir *= -1
        elif mode == UFO:
            if tapped:
                player.vy = -ufo_boost
            player.vy += gravity * dt
        elif mode == WAVE:
            if holding:
                player.vy = -scroll_speed
            else:
                player.vy = scroll_speed

        // Apply gravity (cube, ball, ufo, robot, spider)
        if mode in [CUBE, ROBOT, SPIDER]:
            player.vy += gravity * gravity_dir * dt
            player.vy = clamp(player.vy, -max_fall, max_fall)

        player.y += player.vy * dt

        // Ground/ceiling collision
        if player.y <= ground_y:
            player.y = ground_y
            player.vy = 0
            on_ground = true
        if player.y + player.height >= ceiling_y:
            player.y = ceiling_y - player.height
            player.vy = 0

        // Obstacle collision
        for obstacle in getVisibleObstacles():
            if collides(player, obstacle):
                die()

        // Portal collision
        for portal in getVisiblePortals():
            if collides(player, portal):
                applyPortalEffect(portal)

        // Pad collision
        for pad in getVisiblePads():
            if collides(player, pad):
                applyPadEffect(pad)

        // Coin collection
        for coin in getVisibleCoins():
            if collides(player, coin) and not coin.collected:
                coin.collected = true
                playSound("coin")

        // Progress
        progress = player.x / level_length * 100

        // Level complete
        if player.x >= level_length:
            state = COMPLETE

        // Update camera
        camera.x = player.x - screen_width * 0.3

    render()
```

---

## 18. Level Data Format

```
// Levels stored as arrays of objects on a grid
level = {
    "name": "Stereo Madness",
    "song": "stereo_madness.mp3",
    "bpm": 140,
    "length": 1500,  // blocks
    "speed": NORMAL,
    "background_color": "#0066FF",
    "ground_color": "#1A1A2E",
    "objects": [
        {"type": "spike", "x": 20, "y": 1, "rotation": 0},
        {"type": "block", "x": 25, "y": 1},
        {"type": "block", "x": 25, "y": 2},
        {"type": "jump_pad", "x": 30, "y": 1},
        {"type": "portal_ship", "x": 50, "y": 1},
        {"type": "portal_cube", "x": 120, "y": 1},
        {"type": "speed_fast", "x": 80, "y": 1},
        {"type": "coin", "x": 45, "y": 4},
    ]
}
```

---

## 19. Implementation Checklist

1. [ ] Set up landscape canvas with side-scrolling
2. [ ] Implement cube mode with tap-to-jump
3. [ ] Add gravity and ground collision
4. [ ] Create spike obstacles with triangular hitbox
5. [ ] Create block obstacles
6. [ ] Implement instant death and level restart
7. [ ] Add progress bar (percentage)
8. [ ] Implement ship mode (hold to fly)
9. [ ] Implement ball mode (tap to flip gravity)
10. [ ] Implement UFO mode (tap for boost)
11. [ ] Implement wave mode (hold up/release down)
12. [ ] Implement robot mode (hold for higher jump)
13. [ ] Implement spider mode (teleport to opposite surface)
14. [ ] Create mode-change portals
15. [ ] Create speed-change portals
16. [ ] Create size-change portals
17. [ ] Create gravity portals
18. [ ] Implement jump pads and gravity pads
19. [ ] Implement jump orbs (tap mid-air)
20. [ ] Add secret coins (3 per level)
21. [ ] Music integration and synchronization
22. [ ] Add death particle effect
23. [ ] Implement practice mode with checkpoints
24. [ ] Build level data loader
25. [ ] Design at least Level 1 (Stereo Madness)
26. [ ] Create main menu and level select
27. [ ] Add player icon customization
28. [ ] Implement attempt counter
29. [ ] Save progress and statistics
30. [ ] Add all sound effects

---

End of Geometry Dash specification.
