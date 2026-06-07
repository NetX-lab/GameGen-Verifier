# Cut the Rope — Complete Game Specification

## 1. Game Overview

**Title:** Cut the Rope
**Genre:** Casual / Physics Puzzle
**Platform:** Mobile (portrait), desktop
**Original Creator:** ZeptoLab
**Release Year:** 2010
**Core Loop:** Cut ropes to swing a candy into the mouth of Om Nom (a small green creature). Collect stars along the way. Use various physics-based mechanics (air cushions, bubbles, teleporters) to guide the candy.

Cut the Rope is a 2D physics puzzle game where a piece of candy hangs from one or more ropes. The player cuts ropes by swiping, causing the candy to swing and fall under gravity. The goal is to deliver the candy to Om Nom's open mouth while collecting up to 3 stars per level for maximum score.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Portrait
- **Logical Resolution:** 320 x 480 pixels
- **Coordinate Origin:** Top-left (0, 0)
- **Frame Rate:** 60 FPS
- **Physics Engine:** Custom rope physics + rigid body for candy
- **Physics Timestep:** 1/60 second

### 2.2 Physics Parameters

| Parameter               | Value                         |
|--------------------------|-------------------------------|
| Gravity                  | (0, 500) px/s^2              |
| Candy mass               | 1.0 unit                     |
| Candy radius             | 18 px                        |
| Air resistance           | 0.99 damping per frame       |
| Rope segment length      | 8 px                         |
| Rope stiffness           | 0.9 (spring constant)        |
| Rope damping             | 0.98                         |
| Restitution (bounce)     | 0.3                          |
| Max candy velocity       | 600 px/s                     |

### 2.3 Rendering Layers
```
Layer 0: Background (themed per box)
Layer 1: Background elements (decorative)
Layer 2: Ropes
Layer 3: Stars
Layer 4: Interactive objects (bubbles, cushions, etc.)
Layer 5: Candy
Layer 6: Om Nom
Layer 7: UI overlay (score, stars, buttons)
```

---

## 3. Game States

```
+---------+     +----------+     +---------+     +----------+
|  MENU   | --> | PLAYING  | --> | WIN     | --> | NEXT LVL |
+---------+     +----------+     +---------+     +----------+
                     |                ^
                     v                |
                +---------+           |
                | LOSE    | ----retry-+
                +---------+
```

| State   | Description                                            |
|---------|--------------------------------------------------------|
| MENU    | Box selection and level select                         |
| PLAYING | Active puzzle, player can cut ropes and interact       |
| WIN     | Candy reached Om Nom, star tally, score display        |
| LOSE    | Candy fell off-screen or was destroyed                 |

---

## 4. Core Objects

### 4.1 The Candy

| Parameter          | Value                        |
|--------------------|------------------------------|
| Shape              | Circle                       |
| Radius             | 18 px                        |
| Mass               | 1.0                          |
| Sprite             | Round candy with wrapper tails|
| Color              | Red/green striped             |
| Collision type     | Circle                       |

The candy is the primary physics object. It can:
- Hang from ropes
- Swing when rope is cut
- Fall under gravity
- Be blown by air cushions
- Float inside bubbles
- Teleport through teleporters
- Bounce off walls and bumpers

### 4.2 Om Nom

| Parameter          | Value                        |
|--------------------|------------------------------|
| Size               | 50 x 50 px                   |
| Position           | Fixed per level (usually bottom) |
| Mouth hitbox       | Circle, radius 20 px         |
| Animation states   | Idle, excited, eating, sad   |

Om Nom is the target. He sits in a fixed position and the candy must reach his mouth.

**Om Nom Behavior:**
```
distance_to_candy = distance(om_nom.mouth, candy.position)
if distance_to_candy < 100: om_nom.animation = EXCITED  // eyes follow candy
if distance_to_candy < 20: eat_candy()  // WIN!
if candy_lost: om_nom.animation = SAD  // tears
else: om_nom.animation = IDLE  // blinking
```

### 4.3 Stars

| Parameter          | Value                        |
|--------------------|------------------------------|
| Size               | 24 x 24 px                   |
| Hitbox             | Circle, radius 15 px         |
| Count per level    | 3                            |
| Points per star    | 1,000                        |

Stars are collectible items placed around the level. The candy must touch them to collect them. Stars disappear with a sparkle animation when collected.

Some stars have timers (fading stars) that disappear after a set time:
- Fading star duration: 3-8 seconds (level-specific)
- Visual: star fades in and out, pulsing faster as time runs out

---

## 5. Rope Physics

### 5.1 Rope Structure
Each rope is modeled as a chain of connected segments using Verlet integration.

| Parameter              | Value                       |
|------------------------|-----------------------------|
| Segment count          | Variable (rope length / 8)  |
| Segment rest length    | 8 px                        |
| Constraint iterations  | 5 per frame                 |
| Rope visual width      | 3 px                        |
| Rope color             | Brown #8B6914               |

### 5.2 Rope Endpoints
- **Anchor point:** Fixed position (ceiling, wall, or object)
- **Candy attachment:** The last segment connects to the candy's center

### 5.3 Verlet Integration
```
for each segment_point:
    velocity = (point.position - point.old_position) * damping
    point.old_position = point.position
    point.position += velocity
    point.position.y += gravity * dt * dt  // gravity

// Constraint satisfaction (repeat 5 times):
for each adjacent pair (a, b):
    delta = b.position - a.position
    distance = magnitude(delta)
    difference = (distance - rest_length) / distance
    correction = delta * 0.5 * difference
    if a is not anchor: a.position += correction
    if b is not anchor: b.position -= correction
```

### 5.4 Cutting Ropes
- Player swipes across the screen
- Detect intersection between swipe line and rope segments
- Cut at the intersection point
- Above-cut segments remain attached to anchor (dangle)
- Below-cut segments detach and fall with candy
- Cutting is instantaneous on the frame of the swipe

**Rope-Swipe Intersection:**
```
for each rope:
    for each segment (point_a, point_b):
        if lineSegmentsIntersect(swipe_start, swipe_end, point_a, point_b):
            cutRopeAtSegment(rope, segment_index)
            break
```

### 5.5 Multiple Ropes
- A candy can be attached to multiple ropes simultaneously
- Each rope independently applies tension to the candy
- Cutting one rope causes the candy to swing on remaining ropes
- Cutting all ropes causes free fall

---

## 6. Interactive Elements

### 6.1 Air Cushion / Bellows

| Parameter          | Value                        |
|--------------------|------------------------------|
| Size               | 50 x 40 px                   |
| Force              | 300 px/s^2 (in blow direction)|
| Range              | 150 px                       |
| Direction          | Fixed per cushion (up/left/right) |
| Activation         | Tap to activate              |
| Duration           | Continuous while held         |
| Cooldown           | None                         |

Air cushions blow the candy in a fixed direction when tapped and held. Force decreases with distance from the cushion.

```
force_at_distance(d) = max_force * max(0, 1 - d / range)
// Apply force to candy velocity
candy.velocity += force_direction * force_at_distance(candy_distance) * dt
```

### 6.2 Bubble

| Parameter          | Value                        |
|--------------------|------------------------------|
| Size               | 40 x 40 px                   |
| Float speed        | -60 px/s (upward)            |
| Horizontal drift   | Player tilt or fixed          |
| Pop trigger        | Tap, or hit obstacle          |
| Appears            | Pre-placed in level          |

When the candy touches a bubble, it gets encased and floats upward. Player taps to pop the bubble, releasing the candy.

```
if candy_in_bubble:
    candy.velocity.y = -60  // constant upward
    candy.velocity.x *= 0.95  // slow horizontal
    gravity_disabled = true
    if player_taps or candy_hits_obstacle:
        pop_bubble()
        gravity_disabled = false
```

### 6.3 Teleporter

| Parameter          | Value                        |
|--------------------|------------------------------|
| Size               | 40 x 40 px                   |
| Color              | Paired by color (A and B)    |
| Activation         | Candy enters opening          |
| Behavior           | Candy appears at paired exit  |

Teleporters come in pairs. Candy entering one exits the other with the same velocity.

```
if candy enters teleporter_A:
    candy.position = teleporter_B.exit_position
    candy.velocity = candy.velocity  // preserved
    // Optional: velocity direction adjusted based on exit orientation
```

### 6.4 Elastic Rope / Bungee

| Parameter           | Value                       |
|---------------------|-----------------------------|
| Behavior            | Rope can stretch beyond rest length |
| Max stretch         | 2x rest length              |
| Spring constant     | Higher than normal rope (0.95) |
| Snap threshold      | 3x rest length (breaks)     |

Elastic ropes stretch and pull the candy back, creating a bungee effect.

### 6.5 Spike / Buzzer

| Parameter          | Value                        |
|--------------------|------------------------------|
| Size               | Various (20-60 px)           |
| Behavior           | Destroys candy on contact    |
| Types              | Static spikes, rotating blades |
| Kill radius        | Shape-dependent              |

Contact with spikes instantly destroys the candy (game over for that attempt).

### 6.6 Moving Hook / Slider

| Parameter          | Value                        |
|--------------------|------------------------------|
| Track length       | 100-200 px                   |
| Speed              | 2.0 px/frame                 |
| Direction          | Horizontal or vertical       |
| Behavior           | Rope anchor moves along track |

A moving hook carries the rope anchor point along a track, swinging the candy.

### 6.7 Bouncy Bumper

| Parameter          | Value                        |
|--------------------|------------------------------|
| Size               | 40 x 40 px                   |
| Restitution        | 0.8 (very bouncy)            |
| Shape              | Circle or curved wall        |
| Behavior           | Candy bounces off with high energy return |

### 6.8 Gravity Switcher

| Parameter          | Value                        |
|--------------------|------------------------------|
| Size               | 30 x 30 px                   |
| Behavior           | Reverses or changes gravity direction |
| Activation         | Tap to toggle                |
| Gravity options    | Down, Up, Left, Right        |

---

## 7. Level Structure

### 7.1 Boxes (Level Packs)
Each "box" is a themed collection of 25 levels introducing new mechanics.

| Box Name           | Levels | New Mechanic Introduced        | Theme Color |
|--------------------|--------|--------------------------------|-------------|
| Cardboard Box      | 1-25   | Ropes, basic physics           | Brown       |
| Fabric Box         | 26-50  | Air Cushions                   | Blue        |
| Foil Box           | 51-75  | Bubbles                        | Silver      |
| Magic Box          | 76-100 | Magic hats (teleporters)       | Purple      |
| Valentine Box      | 101-125| Suction cups (sticky anchors)  | Red/Pink    |
| Tool Box           | 126-150| Elastic ropes                  | Gray        |
| Buzz Box           | 151-175| Electric buzzers (spikes)      | Yellow      |
| DJ Box             | 176-200| Gravity switching, music pads  | Neon        |

### 7.2 Level Layout Example
```
+---------------------------+
| [*]            [*]        |  Stars
|  |              |         |
|  |   A-----B    |         |  Rope from A to B (A=anchor, B=candy)
|  |         |    |         |
|  |       (candy) [*]      |  Star near candy
|  |              |         |
|  |    [SPIKE]   |         |  Obstacle
|  |              |         |
|  |  (air cushion ->)      |  Air cushion pointing right
|  |              |         |
|  |      ^       |         |
|  |     /O\      |         |  Om Nom at bottom
|  |    (---)     |         |
+---------------------------+
```

---

## 8. Scoring

### 8.1 Score Components

| Component           | Points                        |
|---------------------|-------------------------------|
| Star collected      | 1,000 each (max 3,000)       |
| Level completed     | 500 base                      |
| Time bonus          | (max_time - elapsed) * 10    |
| Total possible      | ~4,000 - 5,000 per level     |

### 8.2 Star Tracking
- Each level tracks whether each of the 3 stars was collected
- Stars are displayed on level select screen
- Total star count displayed in box overview
- Collecting all stars in a box unlocks bonus content

---

## 9. Difficulty Progression

| Level Range | Concepts                                              |
|-------------|-------------------------------------------------------|
| 1-5         | Single rope, direct path to Om Nom                  |
| 6-10        | Multiple ropes, timing required                      |
| 11-15       | Stars require detour from direct path                |
| 16-20       | First interactive elements introduced                |
| 21-25       | Combined mechanics, tighter timing                   |
| 26+         | Each box builds on all previous mechanics            |

### 9.1 Design Principles
- Every level has a solution for all 3 stars
- Most levels can be solved without all stars (easier path)
- Optimal solution often requires precise timing of cuts
- Some levels have multiple valid solutions
- Later levels require understanding physics interactions deeply

---

## 10. UI Layout

### 10.1 Level Select
```
+---------------------------+
| [Back]  CARDBOARD BOX     |
|                           |
|  [***] [***] [***] [***] [***]
|   1-1   1-2   1-3   1-4   1-5
|                           |
|  [***] [** ] [*  ] [   ] [LOCK]
|   1-6   1-7   1-8   1-9  1-10
|                           |
|  [LOCK][LOCK][LOCK][LOCK][LOCK]
|  1-11  1-12  1-13  1-14  1-15
|                           |
|  [LOCK][LOCK][LOCK][LOCK][LOCK]
|  1-16  1-17  1-18  1-19  1-20
|                           |
|  [LOCK][LOCK][LOCK][LOCK][LOCK]
|  1-21  1-22  1-23  1-24  1-25
+---------------------------+
```

### 10.2 In-Game HUD
```
+---------------------------+
| [Menu] [Restart]   Stars: [*][*][ ] |
|                                      |
|                                      |
|           (puzzle area)              |
|                                      |
|                                      |
|                                      |
|                                      |
|                                      |
+--------------------------------------+
```

### 10.3 Level Complete
```
+---------------------------+
|                           |
|     LEVEL COMPLETE!       |
|                           |
|   Stars: [*] [*] [*]     |
|                           |
|   Score: 3,850            |
|                           |
|   [Retry] [Menu] [Next]  |
|                           |
+---------------------------+
```

---

## 11. Sound Effects

| Sound           | Trigger                     | Description                     |
|-----------------|-----------------------------|---------------------------------|
| rope_cut        | Swipe cuts a rope           | Quick snap / slice              |
| candy_swing     | Candy swinging on rope      | Gentle whoosh (subtle)          |
| star_collect    | Candy touches star          | Bright sparkle chime            |
| bubble_encase   | Candy enters bubble         | Gentle "bloop"                  |
| bubble_pop      | Tap to pop bubble           | Pop sound                       |
| air_blow        | Air cushion activated       | Whooshing air                   |
| teleport        | Candy enters teleporter     | Magical zap                     |
| spike_hit       | Candy hits spike            | Electric buzz + sad trombone    |
| bounce          | Candy hits bumper           | Boing / spring                  |
| om_nom_eat      | Candy reaches Om Nom        | Chomping / munching             |
| om_nom_happy    | Level complete              | Happy "am nam nam!"             |
| om_nom_sad      | Level failed                | Sad whimper                     |
| candy_fall      | Candy falls off screen      | Descending whistle              |
| level_complete  | All done                    | Victory fanfare                 |

---

## 12. Om Nom Animations

| State       | Description                                    | Frames | Duration |
|-------------|------------------------------------------------|--------|----------|
| Idle        | Eyes blink occasionally, slight sway           | 4      | 3000ms loop |
| Excited     | Eyes wide, mouth opens wider, bouncing         | 6      | 500ms loop  |
| Eating      | Chomp animation, candy disappears into mouth   | 8      | 600ms       |
| Happy       | Big smile, jumping with joy, hearts            | 10     | 1200ms      |
| Sad         | Tears fall, droopy posture                     | 6      | 1000ms      |
| Looking     | Eyes follow candy position (computed)           | N/A    | Continuous  |

```
// Eye tracking:
eye_direction = normalize(candy.position - om_nom.eye_position)
eye_offset = eye_direction * 3  // 3px max eye movement
draw_pupils(om_nom.eye_position + eye_offset)
```

---

## 13. Candy Physics Detail

### 13.1 Free Fall
```
candy.velocity.x *= air_resistance  // 0.99
candy.velocity.y += gravity * dt    // 500 * dt
candy.velocity.y = min(candy.velocity.y, max_velocity)
candy.position += candy.velocity * dt
```

### 13.2 Rope Tension
```
for each attached_rope:
    last_segment = rope.segments.last
    delta = last_segment.position - candy.position
    distance = magnitude(delta)
    if distance > rope.rest_total_length:
        // Rope is taut: apply constraint
        correction = (distance - rope.rest_total_length) / distance
        candy.position += delta * correction * 0.5
        candy.velocity += delta * correction * stiffness
```

### 13.3 Wall Collision
```
// Screen boundaries
if candy.x - candy.radius < 0:
    candy.x = candy.radius
    candy.velocity.x *= -restitution
if candy.x + candy.radius > screen_width:
    candy.x = screen_width - candy.radius
    candy.velocity.x *= -restitution
// Bottom: candy falls off screen = lose
if candy.y > screen_height + candy.radius:
    lose_level()
```

---

## 14. Visual Themes by Box

| Box           | Background         | Rope Style        | Ambient Elements    |
|---------------|--------------------|-------------------|---------------------|
| Cardboard     | Brown cardboard    | Brown string      | Tape, stickers      |
| Fabric        | Blue fabric weave  | Thread            | Buttons, patches    |
| Foil          | Silver metallic    | Wire              | Rivets, vents       |
| Magic         | Purple starfield   | Magic chain       | Stars, moons        |
| Valentine     | Pink hearts        | Red ribbon        | Hearts, flowers     |
| Tool          | Gray metal         | Cable             | Gears, bolts        |
| Buzz          | Yellow electric    | Copper wire       | Lightning, sparks   |
| DJ            | Neon dance floor   | Laser beam        | Music notes, lights |

---

## 15. Color Palette

| Element          | Color (Hex)  |
|------------------|--------------|
| Candy body       | #E53935      |
| Candy stripe     | #FFFFFF      |
| Candy wrapper    | #43A047      |
| Om Nom body      | #66BB6A      |
| Om Nom belly     | #A5D6A7      |
| Om Nom eyes      | #FFFFFF      |
| Om Nom pupils    | #212121      |
| Om Nom mouth     | #B71C1C      |
| Star             | #FFD600      |
| Star outline     | #FF8F00      |
| Rope             | #8B6914      |
| Bubble           | #B3E5FC (50% alpha) |
| Air cushion      | #78909C      |
| Spike            | #F44336      |
| Teleporter A     | #7B1FA2      |
| Teleporter B     | #7B1FA2      |
| Background       | #EFEBE9      |

---

## 16. Touch / Input Handling

### 16.1 Swipe to Cut
```
on_touch_begin(x, y):
    swipe_start = (x, y)
    swipe_points = [(x, y)]

on_touch_move(x, y):
    swipe_points.append((x, y))
    // Check intersection with ropes between consecutive swipe points
    for i in range(len(swipe_points) - 1):
        checkCutAlongSwipe(swipe_points[i], swipe_points[i+1])

on_touch_end(x, y):
    swipe_points = []
```

### 16.2 Tap to Interact
```
on_tap(x, y):
    // Check if tap is on an interactive element
    for element in interactive_elements:
        if element.hitbox.contains(x, y):
            if element.type == BUBBLE and candy_in_bubble:
                pop_bubble()
            elif element.type == AIR_CUSHION:
                start_blowing(element)
```

### 16.3 Input Priority
1. Bubble pop (if candy is in bubble)
2. Air cushion activation
3. Other tappable elements
4. Rope cutting (swipe)

---

## 17. Level Data Format

```json
{
    "level_id": "1-3",
    "box": "cardboard",
    "om_nom_position": {"x": 160, "y": 440},
    "ropes": [
        {
            "anchor": {"x": 100, "y": 20},
            "length": 120,
            "candy_attached": true
        },
        {
            "anchor": {"x": 220, "y": 50},
            "length": 80,
            "candy_attached": true
        }
    ],
    "candy_start": {"x": 160, "y": 140},
    "stars": [
        {"x": 80, "y": 200, "timed": false},
        {"x": 240, "y": 300, "timed": true, "duration": 5.0},
        {"x": 160, "y": 380, "timed": false}
    ],
    "elements": [
        {"type": "air_cushion", "x": 30, "y": 300, "direction": "right"},
        {"type": "spike", "x": 160, "y": 260, "width": 60}
    ]
}
```

---

## 18. Implementation Checklist

1. [ ] Set up portrait canvas at 320x480
2. [ ] Implement Verlet rope physics (chain of segments)
3. [ ] Create candy as physics circle with gravity
4. [ ] Implement rope constraint (candy hangs from anchor)
5. [ ] Implement swipe-to-cut detection (line-segment intersection)
6. [ ] Create rope cutting with visual split
7. [ ] Support multiple ropes attached to one candy
8. [ ] Implement wall collision for candy
9. [ ] Create Om Nom with eye tracking and animations
10. [ ] Implement candy-to-Om Nom collision (win condition)
11. [ ] Create and place collectible stars
12. [ ] Implement timed/fading stars
13. [ ] Add air cushion element
14. [ ] Add bubble element (float up, tap to pop)
15. [ ] Add teleporter pairs
16. [ ] Add spike hazards (instant fail)
17. [ ] Add bouncy bumper element
18. [ ] Implement elastic rope variant
19. [ ] Create scoring system (stars + time bonus)
20. [ ] Build level data loader
21. [ ] Design at least 25 levels (Box 1)
22. [ ] Create level select screen
23. [ ] Create in-game HUD (menu, restart, star count)
24. [ ] Create level complete/fail screens
25. [ ] Add all sound effects
26. [ ] Add particle effects (star sparkle, bubble pop)
27. [ ] Implement candy trail effect
28. [ ] Save progress (stars per level)
29. [ ] Add themed backgrounds per box

---

## 19. Hint System

- After failing a level 3 times, a hint button appears
- Hint shows a glowing path or highlights the first cut to make
- Hints can be purchased with in-game currency or watched ads
- Hint visual: animated dotted line showing swipe path, fading over 3 seconds

---

## 20. Performance Notes

- Rope physics: max 4 ropes per level, each max 20 segments
- Use spatial indexing for rope-swipe intersection tests
- Particle system cap: 30 active particles
- Om Nom animation: pre-rendered frames, not computed
- Cache background as single texture (no per-frame redraw)

---

End of Cut the Rope specification.
