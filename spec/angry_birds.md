# Angry Birds — Complete Game Specification

## 1. Game Overview

**Title:** Angry Birds (Original)
**Genre:** Casual / Physics Puzzle
**Platform:** Mobile (landscape), desktop
**Original Creator:** Rovio Entertainment
**Release Year:** 2009
**Core Loop:** Use a slingshot to launch birds at structures sheltering green pigs. Destroy all pigs to complete the level. Each bird has a unique ability. Minimize birds used for higher score.

Angry Birds is a 2D physics-based puzzle game where players launch projectile birds from a slingshot to demolish structures made of wood, glass, and stone, with the goal of eliminating all pigs in each level. The game features realistic 2D rigid-body physics with gravity, collisions, and material-based destruction.

---

## 2. Technical Foundation

### 2.1 Display
- **Orientation:** Landscape
- **Logical Resolution:** 480 x 320 pixels (original); modern: 960 x 640 or 1280 x 720
- **Physics Engine:** Box2D or equivalent 2D rigid-body physics
- **Coordinate Origin:** Bottom-left (physics convention) or top-left (rendering)
- **Frame Rate:** 60 FPS
- **Physics Timestep:** 1/60 second, velocity iterations: 8, position iterations: 3

### 2.2 Physics World Settings

| Parameter                | Value                          |
|--------------------------|--------------------------------|
| Gravity                  | (0, -9.81) m/s^2              |
| Pixels per meter         | 30 px/m                        |
| World width              | ~16 meters (480 px)            |
| World height             | ~10.7 meters (320 px)          |
| Restitution (bounciness) | Material dependent (0.1-0.5)   |
| Friction                 | Material dependent (0.3-0.8)   |
| Linear damping           | 0.1                            |
| Angular damping          | 0.1                            |
| Sleep threshold          | 0.5 m/s (objects stop moving)  |

### 2.3 Rendering Layers
```
Layer 0: Sky background (gradient + clouds)
Layer 1: Background scenery (hills, trees)
Layer 2: Ground
Layer 3: Structures (blocks, planks)
Layer 4: Pigs
Layer 5: Active bird (in flight)
Layer 6: Slingshot foreground band
Layer 7: UI overlay (score, bird queue, pause)
Layer 8: Level complete / fail panel
```

---

## 3. Game States

```
+---------+     +----------+     +---------+     +--------+     +----------+
|  MENU   | --> | AIMING   | --> | FLYING  | --> | SETTLE | --> | EVALUATE |
+---------+     +----------+     +---------+     +--------+     +----------+
                     ^                                               |
                     +--- next bird (if pigs remain) ----------------+
                                                                     |
                                                              +-----------+
                                                              | WIN/LOSE  |
                                                              +-----------+
```

| State    | Description                                               |
|----------|-----------------------------------------------------------|
| MENU     | Episode/level select screen                               |
| AIMING   | Player drags slingshot band to aim bird                   |
| FLYING   | Bird is in the air (physics simulation)                   |
| SETTLE   | Wait for physics to settle after impact                   |
| EVALUATE | Check if all pigs destroyed; load next bird or end level  |
| WIN      | All pigs destroyed, score tally, star rating              |
| LOSE     | No birds remaining, pigs survive, retry prompt            |

---

## 4. The Slingshot

### 4.1 Slingshot Properties

| Parameter              | Value                          |
|------------------------|--------------------------------|
| Position (base)        | X: 60 px, Y: ground + 80 px   |
| Fork height            | 60 px above base               |
| Max pull distance      | 80 px from fork center         |
| Pull angle range       | 0 to 180 degrees (leftward blocked) |
| Launch velocity        | Proportional to pull distance  |
| Max launch speed       | 20 m/s (600 px/s)             |
| Min launch speed       | 3 m/s (90 px/s)               |

### 4.2 Aiming Mechanics
```
// Mouse/touch drag from bird position
pull_vector = fork_position - touch_position
pull_distance = clamp(magnitude(pull_vector), 0, max_pull_distance)
pull_direction = normalize(pull_vector)

// Restrict: cannot aim rightward (behind slingshot)
if pull_direction.x < 0: block or clamp

launch_velocity = pull_direction * (pull_distance / max_pull_distance) * max_launch_speed
```

### 4.3 Trajectory Preview
- While aiming, show dotted trajectory arc
- 8-12 dots showing parabolic path
- Dots fade with distance
- Only show during aiming phase
- Trajectory: `pos(t) = start + velocity*t + 0.5*gravity*t^2`

### 4.4 Slingshot Visual
```
     Y        Y      <-- Fork prongs
      \      /
       \    /
        \  /
    ----[BIRD]----    <-- Elastic bands connect fork to bird
        /  \
       /    \
      /      \
     |   ||   |      <-- Base/trunk
     |   ||   |
=====|===||===|=====  <-- Ground
```

---

## 5. Birds

### 5.1 Bird Types

| Bird       | Name     | Size (px) | Mass (kg) | Special Ability              | Activation      |
|-----------|----------|-----------|-----------|------------------------------|-----------------|
| Red       | Red      | 30 x 30  | 1.0       | None (basic bird)            | N/A             |
| Blue      | The Blues | 24 x 24  | 0.5 each  | Splits into 3 birds         | Tap mid-flight  |
| Yellow    | Chuck    | 32 x 28  | 0.8       | Speed boost forward          | Tap mid-flight  |
| Black     | Bomb     | 36 x 36  | 1.5       | Explodes on impact or tap    | Tap or impact   |
| White     | Matilda  | 34 x 40  | 1.2       | Drops egg bomb, flies up     | Tap mid-flight  |
| Big Red   | Terence  | 44 x 44  | 3.0       | Extra mass, no ability       | N/A             |
| Green     | Hal      | 30 x 30  | 0.9       | Boomerang (reverses)         | Tap mid-flight  |
| Orange    | Bubbles  | 26 x 26  | 0.7       | Inflates to 3x size on tap   | Tap mid-flight  |

### 5.2 Bird Ability Details

**Blue Bird (The Blues) - Split:**
```
On tap:
    remove original bird
    create 3 smaller birds at current position
    bird_1.velocity = original.velocity + rotate(-15 degrees)
    bird_2.velocity = original.velocity  // straight
    bird_3.velocity = original.velocity + rotate(+15 degrees)
    each small bird: mass = 0.5, radius = 12 px
```

**Yellow Bird (Chuck) - Speed Boost:**
```
On tap:
    bird.velocity.x *= 2.5
    bird.velocity.y *= 0.3  // flatten trajectory
    play acceleration effect (motion blur)
    effective for 0.5 seconds, then normal physics resume
```

**Black Bird (Bomb) - Explosion:**
```
On tap OR 3 seconds after first collision:
    create explosion at bird position
    explosion_radius = 80 px (2.67 m)
    explosion_force = 30 N (applied radially outward)
    damage all objects within radius
    force = explosion_force * (1 - distance/explosion_radius)
    remove bird, replace with smoke particles
```

**White Bird (Matilda) - Egg Bomb:**
```
On tap:
    spawn egg projectile at bird position
    egg.velocity = (0, -15 m/s)  // straight down
    egg.mass = 1.0
    bird.velocity.y = 8 m/s   // bird shoots upward
    bird.velocity.x *= 0.5
    egg explodes on impact (similar to bomb but smaller: radius 50 px)
```

**Green Bird (Hal) - Boomerang:**
```
On tap:
    bird.velocity.x = -bird.velocity.x * 1.5  // reverse horizontal
    bird.velocity.y = -2 m/s  // slight upward
    boomerang is one-time use
```

**Orange Bird (Bubbles) - Inflate:**
```
On tap OR on first impact:
    bird.radius *= 3 (26 -> 78 px)
    bird.mass *= 4
    expand over 200ms (animation)
    push all overlapping objects outward
    expansion_force = 20 N radially
    deflate after 3 seconds
```

---

## 6. Pigs

### 6.1 Pig Types

| Pig Type       | Size (px) | HP     | Points (destroy) | Description            |
|----------------|-----------|--------|-------------------|------------------------|
| Small Pig      | 24 x 24   | 50     | 5,000            | Minion, easiest to pop |
| Medium Pig     | 32 x 32   | 100    | 5,000            | Standard pig           |
| Large Pig      | 40 x 40   | 200    | 5,000            | Tougher, takes more    |
| Helmet Pig     | 32 x 38   | 300    | 5,000            | Wears construction hat |
| King Pig       | 48 x 48   | 500    | 10,000           | Crown, boss levels     |
| Moustache Pig  | 36 x 36   | 250    | 5,000            | Military moustache     |

### 6.2 Pig Damage
```
damage = impact_velocity * impacting_mass * material_multiplier
if damage > pig.hp:
    pig.destroy()  // pop animation
    score += pig.points
else:
    pig.hp -= damage
    pig.show_damage_sprite()  // bruised appearance

// Damage sprites:
hp > 66%: normal face
hp 33-66%: slightly bruised, one eye closed
hp < 33%: heavily bruised, stars circling head
```

### 6.3 Pig Physics
- Pigs are circles in the physics engine
- They can roll, bounce, and be knocked around
- Pigs sitting on structures may fall when supports are destroyed
- Falling damage: `damage = fall_height * pig.mass * 5`
- Pigs killed by falling: same points as direct hit

---

## 7. Structure Materials

### 7.1 Material Properties

| Material | Density | Friction | Restitution | HP (plank) | HP (block) | Color/Texture |
|----------|---------|----------|-------------|------------|------------|---------------|
| Wood     | 0.5     | 0.5      | 0.2         | 100        | 150        | Brown, grain   |
| Glass    | 0.3     | 0.2      | 0.1         | 30         | 50         | Light blue     |
| Stone    | 1.0     | 0.8      | 0.3         | 300        | 500        | Gray, texture  |

### 7.2 Block Shapes

| Shape           | Dimensions (px) | Physics Shape | Mass Factor |
|-----------------|-----------------|---------------|-------------|
| Small square    | 20 x 20         | Box           | 1.0         |
| Large square    | 40 x 40         | Box           | 4.0         |
| Thin plank      | 80 x 10         | Box           | 2.0         |
| Thick plank     | 80 x 20         | Box           | 4.0         |
| Short plank     | 40 x 10         | Box           | 1.0         |
| Triangle        | 40 x 40         | Polygon       | 2.0         |
| Circle          | 30 diameter     | Circle        | 1.5         |
| Tall column     | 15 x 80         | Box           | 3.0         |

### 7.3 Block Damage
```
block.hp -= impact_force * material_vulnerability[impacting_type]

// Vulnerability matrix (multiplier):
//              vs Wood  vs Glass  vs Stone
// Red bird      1.0      1.5       0.3
// Blue bird     0.5      3.0       0.1
// Yellow bird   2.0      1.5       0.5
// Black bird    2.0      2.0       2.0  (explosion)
// White bird    1.5      2.0       1.0  (egg)
// Big Red       2.0      2.0       1.5
// Green bird    1.0      1.5       0.3
// Orange bird   1.5      2.0       0.8  (inflation)

Damage states:
hp > 66%: intact
hp 33-66%: cracked appearance (cracks overlay)
hp < 33%: heavily cracked, ready to break
hp <= 0: destroyed (particle effect, score awarded)
```

### 7.4 Destruction Scoring

| Block Type     | Material | Points      |
|----------------|----------|-------------|
| Small block    | Wood     | 500         |
| Small block    | Glass    | 500         |
| Small block    | Stone    | 500         |
| Large block    | Wood     | 1,000       |
| Large block    | Glass    | 1,000       |
| Large block    | Stone    | 1,000       |
| Plank          | Wood     | 500         |
| Plank          | Glass    | 500         |
| Plank          | Stone    | 500         |

---

## 8. Scoring System

### 8.1 Score Components

| Component              | Points                              |
|------------------------|--------------------------------------|
| Pig destroyed          | 5,000 per pig (10,000 for King)     |
| Block destroyed        | 500 - 1,000 per block               |
| Unused bird bonus      | 10,000 per remaining bird           |

### 8.2 Star Rating

| Stars | Score Threshold (varies per level) |
|-------|------------------------------------|
| 1 star | Complete level (all pigs destroyed) |
| 2 stars | Score > level_2star_threshold     |
| 3 stars | Score > level_3star_threshold     |

Typical thresholds:
- 1 star: Any completion
- 2 stars: ~60% of maximum possible score
- 3 stars: ~85% of maximum possible score

### 8.3 Level Complete Tally
```
+-------------------------------------+
|         LEVEL COMPLETE!             |
|                                     |
|  Pigs destroyed:    3 x 5,000 = 15,000 |
|  Blocks destroyed: 12 x  500 =  6,000 |
|  Unused birds:      2 x 10,000 = 20,000|
|                                     |
|  TOTAL:                    41,000   |
|                                     |
|  Rating:  [*] [*] [*]              |
|                                     |
|  [Retry]    [Next Level]            |
+-------------------------------------+
```

---

## 9. Level Design

### 9.1 Level Structure
```
+-----------------------------------------------------------------------+
| Sky (gradient)                                                        |
|                                                                       |
|   Clouds                                                              |
|                                                                       |
|                          +---+                                        |
|                          |   | stone                                  |
|    Slingshot       +---+ +---+ +---+                                  |
|      /\            | P |       | P |  <-- pigs                       |
|     /  \     +-----+---+-------+---+-----+                            |
|    /    \    |  wood plank      wood plank|                            |
|   | BIRD |   +---+---+---+---+---+---+---+                            |
|   +------+   |   |   |   |   |   |   |   |  <-- wood blocks          |
|              +---+---+---+---+---+---+---+                            |
|==================================GROUND===============================|
+-----------------------------------------------------------------------+
  X: 0          60       200     280     360     440     480
```

### 9.2 Level Zones
- **Left zone (0-120 px):** Slingshot area, bird queue
- **Middle zone (120-200 px):** Open space (flight path)
- **Right zone (200-480 px):** Structure and pig placement
- Ground level: Y = 40 px from bottom

### 9.3 Episodes (Original Game)
| Episode            | Levels | Theme                    | New Bird Introduced |
|--------------------|--------|--------------------------|---------------------|
| Poached Eggs       | 1-21   | Grassy hills             | Red, Blue, Yellow   |
| Mighty Hoax        | 22-42  | Forest backdrop          | Black               |
| Danger Above       | 43-57  | Cliffs and caves         | White               |
| The Big Setup      | 58-72  | Construction site        | Green               |
| Ham 'Em High       | 73-87  | Western desert           | Orange              |
| Mine and Dine      | 88-105 | Underground caves        | All                 |

### 9.4 Level Design Principles
- First 3-5 levels: tutorial (1 bird type, simple structures)
- Introduce one new bird type per episode
- Each level has an "elegant" solution using minimum birds
- Multiple valid strategies exist for most levels
- Difficulty curve: gradual within episodes, step up between episodes
- Bonus levels: hidden golden eggs in certain levels

---

## 10. Camera System

### 10.1 Camera Controls

| Action          | Input                   | Effect                         |
|-----------------|-------------------------|--------------------------------|
| Pan             | Drag on empty space     | Move camera view               |
| Zoom in/out     | Pinch (mobile)          | Zoom level 0.5x to 2.0x       |
| Auto-follow     | Bird launched           | Camera follows bird trajectory |
| Reset           | Double-tap empty space  | Reset to default view          |

### 10.2 Camera Behavior
```
During AIMING:
    camera centered on slingshot area
    zoom level: 1.0x (full level visible)

During FLYING:
    camera smoothly follows active bird
    follow_speed = lerp factor 0.05
    keep some lead space in direction of travel
    zoom: 1.2x (slightly closer)

During SETTLE:
    camera shows area of impact
    slowly pan to show full level
    zoom: 1.0x

During EVALUATE:
    camera shows remaining pigs (if any)
    brief focus on each surviving pig
```

---

## 11. Physics Simulation Details

### 11.1 Collision Resolution
```
// Box2D handles collision automatically
// Custom callbacks for:
on_collision(body_a, body_b, contact):
    impulse = contact.normal_impulse
    // Calculate damage based on impulse magnitude
    damage = impulse * damage_multiplier

    if body_a.is_bird and body_b.is_block:
        body_b.take_damage(damage * bird_material_bonus[bird.type][block.material])
    if body_a.is_block and body_b.is_pig:
        body_b.take_damage(damage)
    if body_a.is_bird and body_b.is_pig:
        body_b.take_damage(damage * 2.0)  // direct hit bonus
```

### 11.2 Settling Detection
```
all_settled = true
for body in world.bodies:
    if body.linear_velocity.magnitude > 0.5 or body.angular_velocity > 0.5:
        all_settled = false
        break

// Also enforce maximum settle time: 8 seconds
if settle_timer > 8.0:
    force_settle()  // stop all bodies
```

### 11.3 Ground
- Ground is a static physics body
- Extends full width of level
- Slight variations in height for terrain (optional)
- Collision with ground at high speed damages pigs and breakable blocks

---

## 12. UI Layout

### 12.1 Main Menu
```
+-----------------------------------------------------------------------+
|                                                                       |
|              ANGRY BIRDS                                              |
|              [Logo with Red Bird]                                     |
|                                                                       |
|              [   PLAY   ]                                             |
|                                                                       |
|     [Options]      [Scores]       [About]                             |
|                                                                       |
+-----------------------------------------------------------------------+
```

### 12.2 Level Select
```
+-----------------------------------------------------------------------+
| [Back]          POACHED EGGS                           Page 1/3       |
|                                                                       |
|   [***]  [***]  [***]  [***]  [***]                                  |
|    1-1    1-2    1-3    1-4    1-5                                    |
|                                                                       |
|   [***]  [** ]  [*  ]  [   ]  [LOCK]                                |
|    1-6    1-7    1-8    1-9   1-10                                    |
|                                                                       |
|   [LOCK] [LOCK] [LOCK] [LOCK] [LOCK]                                |
|   1-11   1-12   1-13   1-14   1-15                                   |
|                                                                       |
+-----------------------------------------------------------------------+
```

### 12.3 In-Game HUD
```
+-----------------------------------------------------------------------+
| [Pause]                                        Score: 23,500          |
|                                                                       |
|                                                                       |
|                       (game area)                                     |
|                                                                       |
|                                                                       |
|   Bird queue:  [B] [Y] [R]                                          |
+-----------------------------------------------------------------------+
```

---

## 13. Sound Effects

| Sound              | Trigger                          | Description                    |
|--------------------|----------------------------------|-------------------------------|
| slingshot_stretch  | Pulling back slingshot           | Rubber stretching              |
| slingshot_release  | Release bird                     | Snap / twang                   |
| bird_flying        | Bird in air                      | Whoosh / whistle               |
| bird_ability       | Tap to activate ability          | Unique per bird type           |
| bird_red_yell      | Red launched                     | "Hiyaaa!" battle cry           |
| bird_blue_split    | Blue splits                      | Triple chirp                   |
| bird_yellow_boost  | Yellow boosts                    | Turbo whoosh                   |
| bird_black_fuse    | Bomb starts ticking              | Fuse sizzle                    |
| explosion          | Black bird or egg explodes       | Deep boom                      |
| bird_white_egg     | White drops egg                  | Cluck + whistle down           |
| wood_break         | Wood block destroyed             | Cracking / splintering         |
| glass_break        | Glass block destroyed            | Shattering                     |
| stone_break        | Stone block destroyed            | Crumbling / thud               |
| pig_oink           | Pig hit (not killed)             | Pained oink                    |
| pig_pop            | Pig destroyed                    | Pop + squeal                   |
| pig_laugh          | Pigs survive (level idle)        | Snickering / laughing          |
| level_complete     | All pigs destroyed               | Victory fanfare                |
| level_fail         | No birds, pigs remain            | Sad trombone                   |
| score_count        | Score tallying                   | Rapid ticking                  |
| star_earn          | Star awarded                     | Chime / ding                   |

---

## 14. Particle Effects

| Effect             | Trigger               | Particles | Duration | Description           |
|--------------------|-----------------------|-----------|----------|-----------------------|
| Wood destruction   | Wood HP <= 0          | 6-10      | 500ms    | Brown splinters       |
| Glass destruction  | Glass HP <= 0         | 8-12      | 400ms    | Blue/white shards     |
| Stone destruction  | Stone HP <= 0         | 4-8       | 600ms    | Gray chunks           |
| Pig pop            | Pig HP <= 0           | 5-8       | 300ms    | Green puff + stars    |
| Explosion          | Bomb/egg detonation   | 12-20     | 800ms    | Fire + smoke          |
| Feather poof       | Bird impacts          | 3-6       | 400ms    | Feathers (bird color) |
| Score popup        | Points awarded        | 1 text    | 1000ms   | Floating "+5000"      |
| Dust               | Heavy impact          | 4-8       | 500ms    | Brown/gray cloud      |

---

## 15. Bird Queue and Selection

- Birds for each level are predefined (level designer sets the order and types)
- Bird queue displayed at bottom-left of screen
- 1 to 5 birds per level (varies)
- Next bird automatically loads onto slingshot after previous settles
- Player cannot choose bird order (fixed sequence)
- Queue shows remaining birds as small icons

---

## 16. Special Objects

| Object          | Size     | Behavior                                    |
|-----------------|----------|---------------------------------------------|
| TNT Crate       | 30 x 30 | Explodes when damaged (radius 100px, force 40N) |
| Balloon         | 20 x 30 | Attached to blocks, lifts them; pop to drop  |
| Rubber block    | varies   | High restitution (0.8), bounces birds back   |
| Wheel           | 30 dia.  | Circle, rolls when supports removed          |

---

## 17. Color Palette

| Element          | Color (Hex)  |
|------------------|--------------|
| Sky (top)        | #87CEEB      |
| Sky (bottom)     | #E0F0FF      |
| Ground           | #8B7355      |
| Grass            | #4CAF50      |
| Wood block       | #C49A6C      |
| Wood crack       | #8B6914      |
| Glass block      | #B3E5FC      |
| Glass crack      | #81D4FA      |
| Stone block      | #9E9E9E      |
| Stone crack      | #616161      |
| Red bird         | #F44336      |
| Blue bird        | #2196F3      |
| Yellow bird      | #FFEB3B      |
| Black bird       | #212121      |
| White bird       | #FAFAFA      |
| Green bird       | #4CAF50      |
| Orange bird      | #FF9800      |
| Pig body         | #8BC34A      |
| Pig snout        | #689F38      |
| TNT crate        | #B71C1C      |
| Slingshot        | #5D4037      |
| Elastic band     | #3E2723      |

---

## 18. Performance Notes

- Use spatial hashing for broad-phase collision (Box2D handles this)
- Limit active physics bodies to ~100 per level
- Sleep inactive bodies to reduce simulation cost
- Particle systems: max 50 active particles
- Destroy off-screen debris after 2 seconds
- Pre-calculate structure layouts (no runtime generation needed)

---

## 19. Level Data Format

```json
{
    "level_id": "1-5",
    "episode": "poached_eggs",
    "birds": ["red", "blue", "yellow"],
    "star_thresholds": [0, 25000, 45000],
    "ground_y": 40,
    "structures": [
        {
            "type": "wood_plank",
            "x": 300, "y": 50,
            "angle": 0
        },
        {
            "type": "wood_block",
            "x": 280, "y": 40,
            "angle": 0
        }
    ],
    "pigs": [
        {
            "type": "medium",
            "x": 300, "y": 72
        }
    ],
    "special_objects": [
        {
            "type": "tnt",
            "x": 350, "y": 45
        }
    ]
}
```

---

## 20. Implementation Checklist

1. [ ] Set up 2D physics engine (Box2D or equivalent)
2. [ ] Create slingshot with drag-to-aim mechanic
3. [ ] Implement trajectory preview (dotted line)
4. [ ] Create Red Bird (basic projectile, no ability)
5. [ ] Create Blue Bird with split ability
6. [ ] Create Yellow Bird with speed boost
7. [ ] Create Black Bird with explosion
8. [ ] Create White Bird with egg drop
9. [ ] Create remaining bird types
10. [ ] Implement wood blocks with HP and destruction
11. [ ] Implement glass blocks (fragile)
12. [ ] Implement stone blocks (tough)
13. [ ] Create block shapes (squares, planks, triangles, circles)
14. [ ] Implement pig types with varying HP
15. [ ] Add pig damage visualization
16. [ ] Implement collision damage calculation
17. [ ] Add TNT crate special object
18. [ ] Create scoring system (blocks + pigs + unused bird bonus)
19. [ ] Implement star rating system
20. [ ] Build level data loader
21. [ ] Design at least 21 levels (Episode 1)
22. [ ] Create camera system (pan, zoom, follow)
23. [ ] Build level select screen
24. [ ] Build in-game HUD
25. [ ] Add level complete/fail panels
26. [ ] Implement settling detection
27. [ ] Add all sound effects
28. [ ] Add particle effects for destruction
29. [ ] Implement score popups
30. [ ] Add bird queue display
31. [ ] Save progress (stars, scores per level)

---

End of Angry Birds specification.
