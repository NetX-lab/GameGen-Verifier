# Doodle Jump — Complete Game Specification

## 1. Game Overview

**Title:** Doodle Jump
**Genre:** Casual / Platformer
**Platform:** Mobile (portrait orientation), desktop
**Original Creator:** Lima Sky (Igor & Marko Pusenjak)
**Release Year:** 2009
**Core Loop:** Tilt or tap to move a character (the Doodler) as it bounces automatically on platforms, ascending infinitely. Avoid falling off-screen or hitting monsters. Achieve the highest altitude score.

Doodle Jump is a vertically-scrolling platformer where the player character automatically bounces upward on platforms. The player controls only horizontal movement (tilt on mobile, arrow keys on desktop). The camera scrolls upward as the player ascends. If the player falls below the bottom of the visible screen, the game is over. Various platform types, monsters, power-ups, and obstacles add variety.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Portrait
- **Logical Resolution:** 320 x 480 pixels (original iPhone)
- **Coordinate Origin:** Top-left (0, 0)
- **Frame Rate:** 60 FPS
- **Visual Style:** Hand-drawn notebook doodle aesthetic on grid paper background

### 2.2 Rendering Layers
```
Layer 0: Grid paper background (scrolling)
Layer 1: Platforms
Layer 2: Items / Power-ups
Layer 3: Monsters
Layer 4: Player (Doodler)
Layer 5: Projectiles (nose bullets)
Layer 6: Score / UI overlay
```

---

## 3. Game States

```
+--------+      +---------+      +-----------+
| TITLE  | ---> | PLAYING | ---> | GAME_OVER |
+--------+ tap  +---------+ die  +-----------+
    ^                                  |
    +---------- tap (restart) --------+
```

| State     | Description                                              |
|-----------|----------------------------------------------------------|
| TITLE     | Doodler standing on platform, title text, high score     |
| PLAYING   | Main gameplay, camera follows doodler upward             |
| GAME_OVER | "Game Over" text, final score, name entry for leaderboard|

---

## 4. The Doodler (Player Character)

### 4.1 Properties

| Parameter             | Value                         |
|-----------------------|-------------------------------|
| Width                 | 60 px                         |
| Height                | 60 px                         |
| Hitbox width          | 40 px (centered)              |
| Hitbox height         | 50 px (bottom-aligned)        |
| Feet hitbox height    | 10 px (only bottom of sprite) |
| Horizontal speed      | 3.0 px per degree of tilt     |
| Max horizontal speed  | 8.0 px/frame                  |
| Jump velocity         | -9.0 px/frame                 |
| Spring jump velocity  | -14.0 px/frame                |
| Trampoline velocity   | -18.0 px/frame                |
| Gravity               | 0.3 px/frame^2                |
| Terminal fall speed   | 12.0 px/frame                 |

### 4.2 Movement

**Horizontal:**
- Mobile: accelerometer tilt maps to horizontal velocity
- Desktop: left/right arrow keys set velocity to +/- 5.0 px/frame
- Doodler wraps around screen edges (exit left, appear right and vice versa)
- Wrap threshold: if x < -30, set x = 320; if x > 350, set x = -30

**Vertical:**
- Automatic bounce: when feet collide with platform top, velocity = jump_velocity
- Gravity constantly applied
- Camera follows: when doodler rises above screen center (y < 240), scroll everything down

### 4.3 Facing Direction
- Doodler sprite faces left or right based on horizontal movement direction
- Nose (shooting direction) matches facing direction
- Two sprite variants: facing_left, facing_right

### 4.4 Shooting
- Tap anywhere on screen above doodler to shoot upward toward tap point
- Projectile fires from doodler's nose
- Projectile speed: 10.0 px/frame in the direction of tap
- Projectile size: 8 x 8 px
- Projectiles disappear when off-screen
- Max simultaneous projectiles: 4
- Cooldown between shots: 200 ms

---

## 5. Platforms

### 5.1 Platform Types

| Type         | Width | Height | Color      | Behavior                                    |
|--------------|-------|--------|------------|---------------------------------------------|
| Normal       | 58 px | 15 px  | Green      | Static, always safe to land on              |
| Moving       | 58 px | 15 px  | Blue       | Moves horizontally, speed 1.5 px/frame      |
| Breakable    | 58 px | 15 px  | Brown/Tan  | Breaks on contact, doodler falls through    |
| Vanishing    | 58 px | 15 px  | White/Pale | Disappears 300ms after landing              |
| Moving Vert. | 58 px | 15 px  | Blue       | Moves vertically, range 60px, speed 1.0     |
| Explosive    | 58 px | 15 px  | Orange     | Launches doodler extra high on contact      |

### 5.2 Platform Generation

Platforms are generated procedurally as the player ascends.

**Generation Algorithm:**
```
base_spacing = 60 px (vertical distance between platforms)
max_spacing = min(base_spacing + (altitude / 2000) * 40, 140)
spacing = random(base_spacing, max_spacing)

x_position = random(10, 250)  // leaving margins

// Platform type probability (changes with altitude):
At altitude 0-2000:
    Normal: 70%, Moving: 15%, Breakable: 10%, Vanishing: 5%
At altitude 2000-5000:
    Normal: 45%, Moving: 25%, Breakable: 15%, Vanishing: 10%, Explosive: 5%
At altitude 5000-10000:
    Normal: 30%, Moving: 25%, Breakable: 20%, Vanishing: 15%, Explosive: 10%
At altitude 10000+:
    Normal: 20%, Moving: 30%, Breakable: 25%, Vanishing: 15%, Explosive: 10%
```

### 5.3 Platform Rules
- Always guarantee at least one reachable platform (no impossible gaps)
- Maximum vertical gap: never exceed jump apex height (135 px for normal jump)
- Moving platforms range: 0 to (320 - platform_width)
- Breakable platforms show crack animation over 4 frames (150ms) then fragments fall
- Vanishing platforms blink 3 times over 300ms before disappearing

### 5.4 Collision Detection (Platform Landing)
Only detect collision when:
1. Doodler is **falling** (velocity > 0)
2. Doodler's **feet** overlap the platform's top edge
3. Specifically: `doodler_bottom >= platform_top AND doodler_bottom <= platform_top + 10 AND doodler_x + doodler_width > platform_x AND doodler_x < platform_x + platform_width`

---

## 6. Monsters / Enemies

### 6.1 Monster Types

| Monster       | Width | Height | HP  | Behavior                                   | Points |
|---------------|-------|--------|-----|--------------------------------------------|--------|
| Green Blob    | 40 px | 40 px  | 1   | Sits on platform, static                   | 100    |
| Blue Wing     | 50 px | 40 px  | 1   | Flies horizontally, speed 1.5 px/frame     | 200    |
| Red Mouth     | 50 px | 50 px  | 2   | Moves vertically, range 80 px              | 300    |
| UFO           | 60 px | 40 px  | 3   | Moves in sine wave pattern                 | 500    |
| Black Hole    | 70 px | 70 px  | Inf | Sucks doodler toward center, instant kill  | 0      |
| Purple Wing   | 45 px | 45 px  | 1   | Flies toward doodler at 2.0 px/frame       | 250    |

### 6.2 Monster Spawning

```
First monster appears at altitude: 1000
Spawn rate: 1 monster per 800 altitude units (decreasing gap with altitude)
At altitude > 5000: 1 per 500 altitude units
At altitude > 10000: 1 per 300 altitude units

Monster type probabilities by altitude:
0-3000:   Green Blob 60%, Blue Wing 30%, Red Mouth 10%
3000-7000: Green Blob 30%, Blue Wing 25%, Red Mouth 20%, Purple Wing 15%, UFO 10%
7000+:     All types with Black Hole at 5%
```

### 6.3 Defeating Monsters
1. **Jumping on top:** Land on monster from above (feet hit monster top) -- instant kill, bounce off
2. **Shooting:** Projectile hits monster hitbox -- damage 1 HP per hit
3. **Power-up shield:** Propeller hat / jetpack makes doodler invincible

### 6.4 Monster Death Animation
- Monster squishes vertically (scale Y from 1.0 to 0.2 over 200ms)
- Then falls off screen with slight horizontal drift
- Particle effect: 4-6 small fragments

---

## 7. Power-Ups / Items

### 7.1 Item Types

| Item              | Size    | Duration    | Effect                                        |
|-------------------|---------|-------------|-----------------------------------------------|
| Spring             | 20x15  | Instant     | Bounce 2x higher (velocity = -14.0)           |
| Trampoline         | 30x15  | Instant     | Bounce 3x higher (velocity = -18.0)           |
| Propeller Hat      | 25x20  | 4.0 sec     | Fly upward at -6.0 px/frame, ignore platforms |
| Jetpack            | 20x30  | 5.0 sec     | Fly upward at -8.0 px/frame, ignore platforms |
| Rocket             | 20x35  | 3.0 sec     | Fly upward at -12.0 px/frame, invincible      |
| Shield             | 40x40  | 8.0 sec     | Absorb one monster hit                        |
| Spring Shoes       | 30x15  | 5 jumps     | Every bounce is spring-powered for 5 bounces  |

### 7.2 Item Placement
- Items appear on top of platforms (centered on platform)
- Spring/Trampoline: 1 per 600-1000 altitude units
- Propeller Hat: 1 per 2000-3000 altitude units
- Jetpack: 1 per 4000-5000 altitude units
- Rocket: 1 per 8000-10000 altitude units
- Only one active flight power-up at a time
- Items on breakable platforms: never

### 7.3 Item Behavior
- Spring: compresses on contact (4-frame animation, 100ms), then launches doodler
- Trampoline: larger bounce animation (6 frames, 150ms)
- Propeller Hat: attaches to doodler's head, propeller spins (rotation animation)
- Jetpack: attaches to doodler's back, flame particles emit downward
- Shield: translucent bubble around doodler

---

## 8. Scoring

### 8.1 Score Calculation
- Score = maximum altitude reached (in abstract units)
- 1 altitude unit = 1 pixel of upward scroll
- Score only increases (never decreases when falling)
- Score updates in real-time during play

### 8.2 Bonus Points
| Action                  | Points  |
|-------------------------|---------|
| Kill monster (jump)     | 100-500 (depends on type) |
| Kill monster (shoot)    | Same as jump kill          |
| Collect coin (if added) | 50                         |

### 8.3 Score Display
- Top-left corner, Y = 15, X = 10
- Font: hand-drawn style, black ink on paper
- Size: 18px equivalent
- Right-aligned to X = 120 for consistent positioning

---

## 9. Camera System

### 9.1 Camera Behavior
- Camera only moves **upward**, never downward
- Camera target: doodler should stay at or below vertical center (Y = 240)
- When doodler rises above Y = 240: scroll all entities down by the difference
- Smooth follow: `camera_offset = doodler_y - 240` when doodler_y < 240

### 9.2 Entity Scrolling
When camera moves up by `delta`:
```
for each platform: platform.y += delta
for each monster: monster.y += delta
for each item: item.y += delta
for each projectile: projectile.y += delta
background_offset += delta * 0.3  // parallax
```

### 9.3 Off-Screen Cleanup
- Remove platforms when y > 520 (below screen)
- Remove monsters when y > 520
- Remove projectiles when y < -20 (above screen)
- Generate new platforms above screen (y < -20)

---

## 10. Death Conditions

| Condition                  | Animation                                      |
|----------------------------|-------------------------------------------------|
| Fall below screen bottom   | Doodler falls out of view, "Game Over" appears   |
| Hit monster (from side)    | Doodler makes sad face, falls downward           |
| Hit monster (from below)   | Same as side hit                                 |
| Sucked into black hole     | Doodler spirals inward, shrinks to nothing       |

### 10.1 Death Sequence
1. Doodler changes to "hurt" sprite (X eyes, open mouth)
2. Velocity set to -5.0 (slight upward bounce)
3. Gravity applies, doodler falls
4. Doodler passes through all platforms (no collision)
5. When doodler goes below screen bottom: show Game Over
6. Total death animation: ~1.5 seconds

---

## 11. UI Layout

### 11.1 Title Screen
```
+--------------------------------+  (0,0)
|                                |
|     DOODLE JUMP!               |  Y = 40
|                                |
|     High Score: 12345          |  Y = 80
|                                |
|                                |
|  +---------+                   |
|  | Doodler |  <-- standing     |  Y = 300
|  +---------+                   |
|  ============  <-- platform    |  Y = 360
|                                |
|     TAP TO START               |  Y = 420
|                                |
+--------------------------------+  (320, 480)
```

### 11.2 Playing Screen
```
+--------------------------------+
| Score: 4520          [Pause]   |  Y = 10
|                                |
|        ====                    |  platforms at various positions
|                                |
|   ====        /^^^\            |  monster on platform
|              |o  o|            |
|    ====       \--/             |
|                                |
|          +---+                 |
|   ====   | D |   ====         |  doodler mid-jump
|          +---+                 |
|                                |
|   ====      [spring]          |  item on platform
|             ====               |
+--------------------------------+
```

### 11.3 Game Over Screen
```
+--------------------------------+
|                                |
|       GAME OVER                |  Y = 100
|                                |
|    Your Score: 8432            |  Y = 180
|    Best Score: 12345           |  Y = 210
|                                |
|    Enter Name: [___________]   |  Y = 280
|                                |
|    [  PLAY AGAIN  ]           |  Y = 360
|                                |
|    [  LEADERBOARD ]           |  Y = 410
|                                |
+--------------------------------+
```

---

## 12. Themes / Visual Variants

The original Doodle Jump features multiple themes that change the visual style:

| Theme         | Background        | Platform Style    | Doodler Style     |
|---------------|-------------------|-------------------|-------------------|
| Default       | Grid paper        | Green bars        | Green creature    |
| Space         | Star field        | Meteor platforms  | Astronaut suit    |
| Jungle        | Vine background   | Wooden logs       | Safari outfit     |
| Underwater    | Ocean blue        | Coral/shells      | Scuba gear        |
| Christmas     | Snowy             | Candy canes       | Santa hat         |
| Halloween     | Spooky purple     | Pumpkin platforms | Vampire cape      |

For implementation, start with the Default theme only.

---

## 13. Sound Effects

| Sound         | Trigger                     | Description                        |
|---------------|-----------------------------|------------------------------------|
| jump          | Land on platform            | Short boing / spring sound         |
| spring_jump   | Hit spring item             | Higher pitched boing               |
| shoot         | Tap to fire projectile      | Short "pew" sound                  |
| monster_kill  | Defeat a monster            | Squish / pop sound                 |
| power_up      | Collect propeller/jetpack   | Ascending chime                    |
| jetpack_loop  | While jetpack active        | Engine rumble (looping)            |
| break         | Land on breakable platform  | Crack / snap sound                 |
| fall_death    | Fall below screen           | Descending whistle                 |
| game_over     | Death confirmed             | Sad trombone / jingle              |

---

## 14. Background

### 14.1 Grid Paper
- Light cream/white background: #FDF6E3
- Grid lines: thin, light gray #D0D0D0
- Grid spacing: 20 x 20 px
- Grid scrolls with parallax at 0.3x camera speed
- Margin line on left: red #FF0000, at X = 30 px

### 14.2 Doodle Aesthetic
- All sprites drawn with a "hand-drawn" look
- Visible pencil/pen lines, slightly uneven edges
- Platform surfaces have slight hand-drawn texture
- Numbers in hand-drawn font style

---

## 15. Difficulty Progression

| Altitude Range | Description                                              |
|----------------|----------------------------------------------------------|
| 0 - 1000       | Tutorial feel: mostly normal platforms, close together   |
| 1000 - 3000    | Moving platforms appear, first monsters                  |
| 3000 - 5000    | Breakable platforms increase, more monsters              |
| 5000 - 8000    | Vanishing platforms, wider gaps, aggressive monsters     |
| 8000 - 12000   | Many moving platforms, frequent monsters, tight gaps     |
| 12000 - 20000  | UFOs and black holes appear, few normal platforms        |
| 20000+         | Extreme: mostly moving/vanishing, constant threats       |

### 15.1 Gap Scaling Formula
```
max_gap(altitude) = 60 + min(altitude / 200, 80)
// At altitude 0: max gap = 60px
// At altitude 5000: max gap = 85px
// At altitude 16000+: max gap = 140px (capped)
```

---

## 16. Wrap-Around Mechanic

The Doodler and horizontally-moving monsters wrap around screen edges:

```
if entity.x + entity.width < 0:
    entity.x = screen_width
elif entity.x > screen_width:
    entity.x = -entity.width
```

- Provides seamless horizontal movement
- Visual: entity partially visible on both edges during transition
- Projectiles do NOT wrap (they disappear off-screen)

---

## 17. Pause System

- Pause button in top-right corner (20x20 px, "||" icon)
- Pausing freezes all physics, animation, and timers
- Dim overlay (black, 50% opacity) covers game
- "PAUSED" text centered on screen
- Tap anywhere to resume
- Power-up durations pause (timer stops)

---

## 18. Physics Details

### 18.1 Jump Arc Calculation
```
Normal jump:
    initial_velocity = -9.0 px/frame
    gravity = 0.3 px/frame^2
    time_to_apex = 9.0 / 0.3 = 30 frames = 500 ms
    max_height = v^2 / (2*g) = 81 / 0.6 = 135 px

Spring jump:
    initial_velocity = -14.0 px/frame
    time_to_apex = 14.0 / 0.3 = 46.67 frames = 778 ms
    max_height = 196 / 0.6 = 326.67 px

Trampoline jump:
    initial_velocity = -18.0 px/frame
    time_to_apex = 60 frames = 1000 ms
    max_height = 324 / 0.6 = 540 px

Propeller Hat flight:
    constant velocity = -6.0 px/frame for 4 seconds
    total distance = 6.0 * 240 = 1440 px

Jetpack flight:
    constant velocity = -8.0 px/frame for 5 seconds
    total distance = 8.0 * 300 = 2400 px

Rocket flight:
    constant velocity = -12.0 px/frame for 3 seconds
    total distance = 12.0 * 180 = 2160 px
```

---

## 19. Implementation Pseudocode

```
function update():
    dt = 1  // frame-based

    if state != PLAYING: return

    // Horizontal input
    if isMobile:
        tilt = getAccelerometerX()
        doodler.vx = tilt * 3.0
    else:
        if leftKeyDown: doodler.vx = -5.0
        elif rightKeyDown: doodler.vx = 5.0
        else: doodler.vx = 0

    doodler.vx = clamp(doodler.vx, -8.0, 8.0)
    doodler.x += doodler.vx

    // Wrap around
    if doodler.x < -30: doodler.x = 320
    if doodler.x > 350: doodler.x = -30

    // Vertical physics
    if not doodler.powered_flight:
        doodler.vy += gravity
        doodler.vy = min(doodler.vy, terminal_velocity)
    doodler.y += doodler.vy

    // Camera scroll
    if doodler.y < 240:
        scroll = 240 - doodler.y
        doodler.y = 240
        score += scroll
        for entity in all_entities:
            entity.y += scroll
        generateNewPlatforms()
        removeOffScreenEntities()

    // Platform collision (only when falling)
    if doodler.vy > 0:
        for platform in platforms:
            if feetOverlap(doodler, platform):
                if platform.type == BREAKABLE:
                    platform.break()
                elif platform.type == VANISHING:
                    platform.startVanish()
                    doodler.vy = jump_velocity
                else:
                    doodler.vy = jump_velocity
                    // Check for items on platform
                    if platform.hasItem:
                        activateItem(platform.item)

    // Monster collision
    for monster in monsters:
        if collides(doodler, monster):
            if doodler.vy > 0 and doodler.bottom < monster.centerY:
                // Stomped from above
                killMonster(monster)
                doodler.vy = jump_velocity
            elif doodler.hasShield:
                doodler.hasShield = false
                killMonster(monster)
            else:
                killDoodler()

    // Shooting
    if screenTapped and tapY < doodler.y:
        fireProjectile(tapX, tapY)

    // Projectile updates
    for proj in projectiles:
        proj.update()
        for monster in monsters:
            if collides(proj, monster):
                monster.hp -= 1
                removeProjectile(proj)
                if monster.hp <= 0:
                    killMonster(monster)

    // Death check
    if doodler.y > 500:
        state = GAME_OVER

    // Update all animations
    updateAnimations()
```

---

## 20. Leaderboard

- Local leaderboard stores top 10 scores
- Each entry: name (3 characters) + score
- Sorted descending by score
- Default entries: "AAA" with scores 100, 200, ..., 1000
- Name entry on game over: 3-character input

---

## 21. Color Palette

| Element          | Color (Hex)  |
|------------------|--------------|
| Background paper | #FDF6E3      |
| Grid lines       | #D0D0D0      |
| Margin line      | #FF0000      |
| Normal platform  | #6ABF4B      |
| Moving platform  | #5B9BD5      |
| Breakable plat.  | #C4A882      |
| Vanishing plat.  | #E0E0E0      |
| Explosive plat.  | #FF8C00      |
| Doodler body     | #7BC96A      |
| Doodler nose     | #E8883C      |
| Monster (green)  | #4CAF50      |
| Monster (blue)   | #2196F3      |
| Monster (red)    | #F44336      |
| Score text       | #333333      |
| Game over text   | #333333      |
| Spring           | #808080      |
| Jetpack flame    | #FF6600      |

---

## 22. Implementation Checklist

1. [ ] Set up canvas at 320x480 with grid paper background
2. [ ] Create Doodler with left/right movement and screen wrap
3. [ ] Implement automatic bouncing with gravity
4. [ ] Create normal platforms with collision detection (falling only)
5. [ ] Implement camera system (upward scroll only)
6. [ ] Add procedural platform generation
7. [ ] Add moving platforms (horizontal)
8. [ ] Add breakable platforms with break animation
9. [ ] Add vanishing platforms with blink animation
10. [ ] Add spring and trampoline items
11. [ ] Add propeller hat power-up
12. [ ] Add jetpack power-up
13. [ ] Add rocket power-up
14. [ ] Implement monsters (static, moving types)
15. [ ] Add shooting mechanic
16. [ ] Add monster-stomp mechanic
17. [ ] Implement scoring (altitude-based)
18. [ ] Add death detection and animation
19. [ ] Create title screen
20. [ ] Create game over screen with name entry
21. [ ] Implement local leaderboard
22. [ ] Add difficulty progression
23. [ ] Add all sound effects
24. [ ] Add pause functionality

---

End of Doodle Jump specification.
