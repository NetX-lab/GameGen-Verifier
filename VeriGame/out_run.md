# OutRun (1986 Arcade) — Complete Game Specification

> A comprehensive specification for faithfully recreating the original OutRun (Sega AM2, 1986 arcade version). This document covers every system, mechanic, visual element, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Pseudo-3D Road Rendering](#3-pseudo-3d-road-rendering)
4. [Core Driving Mechanics](#4-core-driving-mechanics)
5. [Road System & Stage Layout](#5-road-system--stage-layout)
6. [All 15 Stages](#6-all-15-stages)
7. [Traffic System](#7-traffic-system)
8. [Collision & Recovery](#8-collision--recovery)
9. [Timer & Checkpoint System](#9-timer--checkpoint-system)
10. [Scoring System](#10-scoring-system)
11. [Music Selection System](#11-music-selection-system)
12. [Audio Design](#12-audio-design)
13. [UI Layout](#13-ui-layout)
14. [Cabinet & Input Hardware](#14-cabinet--input-hardware)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Out Run |
| Developer | Sega AM2 |
| Director / Designer | Yu Suzuki |
| Composer | Hiroshi Kawaguchi (a.k.a. Hiroshi Miyauchi) |
| Platform | Arcade (Sega OutRun hardware) |
| Release date | September 20, 1986 (Japan) |
| Genre | Driving / Racing (non-competitive, time-attack) |
| Players | 1 |
| Perspective | Third-person, behind-the-car |
| Playable vehicle | Ferrari Testarossa Spider (convertible) |
| Passengers | Male driver + female passenger |

### Objective

Drive the Ferrari Testarossa from Coconut Beach through five consecutive stages, reaching each checkpoint before the timer expires. At the end of each stage the road forks into two paths (left or right), creating a branching tree of 15 total stages with 5 unique endpoints (Goals A through E). There is no opponent to "beat" -- the only enemy is the clock.

### Lose Condition

The countdown timer reaches zero before the player crosses the next checkpoint or the final goal line.

### Win Condition

Cross the goal line of any Stage 5 destination with time remaining. One of five unique ending cutscenes plays depending on which Goal (A-E) was reached.

---

## 2. Technical Foundation

### Hardware Specifications

| Component | Detail |
|-----------|--------|
| System board | Sega OutRun (custom, based on Sega System 16) |
| Main CPUs | 2 x Motorola 68000 @ 12.5 MHz |
| Sound CPU | Zilog Z80 @ 4 MHz |
| FM sound chip | Yamaha YM2151 @ 4 MHz (8 FM channels) |
| PCM sound chip | Sega 315-5218 (SegaPCM) @ 4 MHz (16 PCM channels, 12-bit depth, 31.25 kHz sampling rate, stereo) |
| Display resolution | 320 x 224 pixels (visible); 400 x 262 (total with overscan) |
| Refresh rate | 60 Hz vertical sync |
| Effective frame rate | 30 FPS (game logic updates at 30 Hz, every other vblank) |
| Color depth | 15-bit RGB (32,768 possible colors) |
| On-screen colors | Up to 4,096 simultaneous colors from 32,768 palette |
| Sprite capacity | 128 sprites on-screen simultaneously |
| Sprite scaling | Hardware sprite-scaling / zooming (Super Scaler technology) |
| Sprite fill rate | 7,680 sprites/textures scaled per second |
| Road hardware | Dedicated road rendering layer capable of drawing 2 independent roads |
| Road fill rate | 1,024 texels per scanline; 268,288 texels per frame |
| Program ROM | Up to 872 KB |
| Graphics ROM | Up to 1,888 KB |
| Monitor size | 20-inch (upright) / 26-inch (sit-down deluxe) |
| Orientation | Horizontal |
| Power consumption | 165 W (upright mini) to 350 W (deluxe sit-down) |

### Game Loop (30 Hz)

```
1. Read input (steering wheel analog position, accelerator pedal analog, brake pedal analog, gear shift toggle)
2. Update timer (decrement time_counter each 30-frame cycle = 1 displayed second)
3. Update car physics (acceleration, deceleration, steering, gear state)
4. Update road position (advance car_increment based on speed, evaluate road_curve)
5. Update road rendering (project segments, apply curves/hills, calculate split forks)
6. Update traffic vehicles (AI movement patterns, lane changes)
7. Check collisions (player car vs. traffic, player car vs. roadside scenery)
8. If collision: initiate crash sequence or speed penalty
9. Update scenery sprite positions (parallax scrolling, sprite scaling)
10. Update score (continuous scoring based on speed/gear)
11. Check checkpoint/goal crossing
12. Render (sky gradient -> ground plane -> road layers -> scenery sprites -> traffic sprites -> player car -> HUD overlay)
```

---

## 3. Pseudo-3D Road Rendering

OutRun uses the "Super Scaler" pseudo-3D technique pioneered by Yu Suzuki. The road is not rendered in true 3D; instead, it is drawn scanline-by-scanline from the bottom of the screen upward toward the horizon, with each scanline representing a road segment at increasing distance from the camera.

### Road Segment Model

| Parameter | Value / Description |
|-----------|---------------------|
| Segment count | ~500 segments define one full stage |
| Segment length | 200 world units per segment |
| Road half-width | 2,000 world units (road spans -2000 to +2000 from center) |
| Draw distance | ~300 segments rendered per frame (horizon clipping) |
| Rumble strip length | 3 segments per color alternation |
| Camera height | ~1,000 world units above ground plane |
| Field of view | ~100 degrees |

### Projection Pipeline

Each segment stores two edge points (`p1` near, `p2` far). For each point, the rendering follows three steps:

1. **Translation**: Convert world coordinates to camera-relative coordinates.
   - `cameraX = worldX - playerX`
   - `cameraY = worldY - cameraHeight`
   - `cameraZ = worldZ - playerZ`

2. **Projection**: Apply perspective using similar triangles.
   - Scale factor: `scale = cameraDepth / cameraZ` where `cameraDepth = 1 / tan(FOV / 2)`
   - `projectedX = scale * cameraX`
   - `projectedY = scale * cameraY`
   - `projectedW = scale * roadWidth`

3. **Screen mapping**: Convert normalized projected coordinates to pixel coordinates.
   - `screenX = (screenWidth / 2) + (projectedX * screenWidth / 2)`
   - `screenY = (screenHeight / 2) - (projectedY * screenHeight / 2)`
   - `screenW = projectedW * screenWidth / 2`

### Curve Implementation

Curves are simulated by applying a cumulative horizontal offset (`road_curve`) to the center line of each segment. As segments are rendered from bottom to top:

- Each scanline's center position shifts left or right by an accumulating `dx` value.
- `dx += road_curve * segment_scale_factor`
- Left curves use positive `road_curve`; right curves use negative.
- The visual result: the road appears to bend smoothly toward the vanishing point.
- Road types: `ROAD_STRAIGHT` (curve = 0), `ROAD_RIGHT`, `ROAD_LEFT`

### Hill Implementation

Hills are implemented by assigning non-zero Y coordinates to road segment points:

- Uphill: successive segments have increasing Y values, causing the road to visually rise.
- Downhill: segments have decreasing Y values, road dips toward the horizon.
- The camera naturally follows the player's Y position, creating crest and valley effects.

### Road Splitting (Fork Rendering)

The hardware supports rendering two independent roads simultaneously:

- As the player approaches a fork, two road layers diverge from a shared origin.
- `rd_split_state` progresses through states: `SPLIT_NONE` -> `SPLIT_INIT` -> `SPLIT_CHOICE1` / `SPLIT_CHOICE2`
- Road width at merge point: `RD_WIDTH_MERGE = 0xD4` (212 pixels)
- The non-chosen road fades or is clipped after the player commits to a fork direction.

### Scenery Sprite Scaling

Roadside objects (trees, signs, buildings, rocks) are 2D sprites scaled by the same perspective `scale` factor:

- Sprite width and height are multiplied by `cameraDepth / cameraZ`
- Sprites are z-sorted and drawn back-to-front
- Objects placed at specific segment positions along the road
- Maximum 128 sprites visible simultaneously

---

## 4. Core Driving Mechanics

### Gear System

| Property | Low Gear | High Gear |
|----------|----------|-----------|
| Top speed (displayed) | ~193 km/h | ~293 km/h |
| Acceleration | Faster from standstill | Slower from standstill, faster at high speed |
| Handling | Easier / more forgiving | Harder / twitchier at top speed |
| Scoring rate | Base rate | ~2x base rate |
| Recommended use | Starting from stop, tight curves | Straights, high-speed sections |

- The gear shift is a **two-position toggle**: Low and High. There is no neutral or reverse.
- Shifting from Low to High at speed produces a burst of acceleration.
- Shifting from High to Low at speed produces engine braking (mild deceleration).
- Optimal launch: Hold accelerator, shift to High when tachometer enters the high-green zone (just below redline).

### Acceleration & Speed

| State | Behavior |
|-------|----------|
| Full throttle, Low gear | Rapid acceleration up to ~193 km/h cap |
| Full throttle, High gear | Gradual acceleration up to ~293 km/h cap |
| No throttle | Gradual deceleration (engine braking / coasting) |
| Brake applied | Strong deceleration; speed drops rapidly |
| Off-road (grass/dirt) | Severe speed penalty; car decelerates sharply toward ~80 km/h |
| Off-road + gear trick | Rapidly toggling Low->High while off-road can maintain speed for ~1-2 seconds |
| Cornering at high speed | Slight speed loss if steering hard; car slides outward |
| After crash | Speed drops to 0; must re-accelerate from standstill |

### Steering

| Parameter | Description |
|-----------|-------------|
| Input type | Analog steering wheel (270-degree rotation range) |
| Dead zone | Small center dead zone for stability on straights |
| Sensitivity scaling | Steering effect increases with speed up to a threshold, then becomes twitchier |
| Maximum lateral movement | `car_x_pos` ranges from center (0) to road edge; beyond edge = off-road |
| Drift behavior | At high speed with hard steering input, rear end slides outward (oversteer characteristic of rear-wheel-drive Testarossa) |
| AI assist | Subtle AI assistance to prevent excessive twitchiness; tire grip is slightly softened so the car does not feel "on rails" |
| Steering adjustment cap | +/- 0x40 maximum change per frame |
| Speed-dependent reduction | At speeds <= 0x7F internal units, steering effect is reduced proportionally |

### Off-Road Behavior

- Driving off either edge of the road onto grass, dirt, or sand causes:
  - Immediate speed reduction (deceleration to approximately 80 km/h if sustained)
  - Rumble effect on steering wheel (force feedback vibration on deluxe cabinet)
  - Visual: car kicks up dust/debris particles
- Hitting a roadside object (tree, sign, rock, building) while off-road triggers a crash.
- The "gear gacha" technique (rapidly toggling Low/High gear at the moment of leaving the road) exploits a timing window to maintain full speed off-road for 1-2 seconds.

---

## 5. Road System & Stage Layout

### Branching Structure

OutRun has a binary tree of 15 stages organized into 5 tiers. The player always starts at Coconut Beach (Stage 1) and plays exactly 5 stages per run. At the end of each stage (except Stage 5), the road forks and the player chooses left or right, leading to a different Stage in the next tier.

```
                          Stage 1
                       Coconut Beach
                      /              \
                 LEFT                 RIGHT
                /                         \
          Stage 2A                    Stage 2B
          Gateway                  Devil's Canyon
         /       \                /             \
    Stage 3A   Stage 3B     Stage 3B        Stage 3C
     Desert      Alps         Alps        Cloudy Mountain
    /    \      /    \       /    \        /          \
  4A     4B  4B     4C    4C     4D     4D           4E (N/A - see note)
 Wild.  Old  Old   Wheat  Wheat  Sea.   Sea.
  |  \  |  \ |  \  |  \   |  \  |  \   |  \
 5A  5B 5B 5C 5C 5D 5D 5E 5E    ...
```

**Note**: Stages can be shared between adjacent branches. For example, Alps (3B) is reachable from both Gateway (2A, right fork) and Devil's Canyon (2B, left fork).

### Stage Tier Layout

| Tier | Position | Stage Name (International) | Stage Name (Japan) |
|------|----------|---------------------------|-------------------|
| 1 | 1 | Coconut Beach | Coconut Beach |
| 2 | 2A (left) | Gateway | Big Gate |
| 2 | 2B (right) | Devil's Canyon | Walls |
| 3 | 3A (leftmost) | Desert | Desert |
| 3 | 3B (center) | Alps | Alps |
| 3 | 3C (rightmost) | Cloudy Mountain | Cloudy Mountain |
| 4 | 4A (leftmost) | Wilderness | Wilderness |
| 4 | 4B | Old Capital | Old Capital |
| 4 | 4C | Wheat Field | Wheat Field |
| 4 | 4D (rightmost) | Seaside Town | Seaside Town |
| 5 | 5A (leftmost) - Goal A | Vineyard | Vineyard |
| 5 | 5B | Death Valley | Death Valley |
| 5 | 5C | Desolation Hill | Stone Hill |
| 5 | 5D | Autobahn | Dual Way |
| 5 | 5E (rightmost) - Goal E | Lakeside | Lakeside |

### Route Selection Logic

- `route_selected = -1` for left fork, `0` for right fork
- Route encoding uses additive increments per stage:
  - Stage 1 fork: +8 (left) or +0 (right)
  - Stage 2 fork: +4 (left) or +0 (right)
  - Stage 3 fork: +2 (left) or +0 (right)
  - Stage 4 fork: +1 (left) or +0 (right)
- Base route value: +10 per stage
- This produces a unique route code for each of the 16 possible paths.

### General Rule of Difficulty

- **Left forks** lead to easier routes (wider roads, gentler curves, less traffic).
- **Right forks** lead to harder routes (narrower roads, tighter curves, denser traffic).
- The leftmost path through the tree (all left forks: Coconut Beach -> Gateway -> Desert -> Wilderness -> Vineyard) is the easiest complete route.
- The rightmost path (all right forks: Coconut Beach -> Devil's Canyon -> Cloudy Mountain -> Seaside Town -> Lakeside) is the hardest.

### Road Properties Per Stage

All stages are the same physical length in terms of road segments, ensuring consistent scoring regardless of route. Difficulty varies through:

| Difficulty Factor | Easy Stages (left) | Hard Stages (right) |
|-------------------|--------------------|---------------------|
| Road width | Wide (6-lane feel) | Narrow (2-4 lane feel) |
| Curve frequency | Low | High |
| Curve sharpness | Gentle | Sharp / hairpin |
| Hill frequency | Low | Moderate to high |
| Traffic density | Light | Heavy |
| Roadside object proximity | Far from road edge | Close to road edge |

---

## 6. All 15 Stages

### Stage 1: Coconut Beach (Tier 1)

| Property | Value |
|----------|-------|
| Position | Starting stage (all routes) |
| Theme | Tropical beach / coastal highway |
| Sky | Bright blue with white clouds |
| Scenery | Palm trees, ocean waves, beach houses, boardwalk structures, sailboats on horizon |
| Road surface | Light grey asphalt |
| Roadside ground | Sandy beach / light grass |
| Curves | Gentle, wide sweeping turns |
| Hills | Minimal undulation |
| Traffic density | Light (introduction) |
| Difficulty | Easiest |

### Stage 2A: Gateway (Tier 2, Left)

| Property | Value |
|----------|-------|
| Position | 2A (left fork from Coconut Beach) |
| Theme | European seaside town with grand stone gateway arches |
| Sky | Clear blue |
| Scenery | Stone columns/pillars, arched gates, Mediterranean buildings, low walls |
| Road surface | Grey asphalt |
| Roadside ground | Stone/paved shoulders |
| Curves | Moderate, medium-radius |
| Hills | Gentle rolling |
| Traffic density | Light to moderate |
| Difficulty | Easy |

### Stage 2B: Devil's Canyon (Tier 2, Right)

| Property | Value |
|----------|-------|
| Position | 2B (right fork from Coconut Beach) |
| Theme | Deep rocky canyon with towering cliff walls |
| Sky | Narrow strip visible between canyon walls; dusky orange |
| Scenery | Massive rock formations, cliff faces, boulders, sparse desert scrub |
| Road surface | Dark grey / brownish asphalt |
| Roadside ground | Rocky terrain |
| Curves | Sharp, road narrows between cliff walls |
| Hills | Moderate; road dips and rises through canyon |
| Traffic density | Moderate to heavy |
| Difficulty | Moderate-hard |

### Stage 3A: Desert (Tier 3, Leftmost)

| Property | Value |
|----------|-------|
| Position | 3A (left fork from Gateway) |
| Theme | Arid red rock desert |
| Sky | Deep blue fading to purple at horizon; vivid sunset hues |
| Scenery | Red rock formations, cacti, dry brush, distant mesas, sand dunes |
| Road surface | Dusty tan/grey asphalt |
| Roadside ground | Red sand / dirt |
| Curves | Moderate, sweeping desert turns |
| Hills | Low rolling dunes |
| Traffic density | Moderate |
| Difficulty | Moderate |

### Stage 3B: Alps (Tier 3, Center)

| Property | Value |
|----------|-------|
| Position | 3B (right from Gateway OR left from Devil's Canyon) |
| Theme | Alpine mountain meadows with snow-capped peaks |
| Sky | Clear blue with wispy clouds |
| Scenery | Fields of pink/yellow wildflowers, wooden chalets, icy mountain peaks on horizon, pine trees |
| Road surface | Clean grey asphalt |
| Roadside ground | Green grass with flower patches |
| Curves | Moderate to sharp alpine switchbacks |
| Hills | Significant; mountain passes with crests and valleys |
| Traffic density | Moderate |
| Difficulty | Moderate |

### Stage 3C: Cloudy Mountain (Tier 3, Rightmost)

| Property | Value |
|----------|-------|
| Position | 3C (right fork from Devil's Canyon) |
| Theme | Misty mountain pass shrouded in clouds |
| Sky | Overcast grey/white cloud cover |
| Scenery | Pine forests, fog banks, rocky outcrops, distant mountain silhouettes in mist |
| Road surface | Damp dark grey asphalt |
| Roadside ground | Dark green grass, mossy rocks |
| Curves | Sharp and frequent |
| Hills | Steep climbs and descents |
| Traffic density | Heavy |
| Difficulty | Hard |

### Stage 4A: Wilderness (Tier 4, Leftmost)

| Property | Value |
|----------|-------|
| Position | 4A (left fork from Desert) |
| Theme | Arid scrubland with distant city skyline on horizon |
| Sky | Hazy blue-grey |
| Scenery | Low shrubs, dry grass, scattered rocks, city buildings visible in far distance |
| Road surface | Weathered grey asphalt |
| Roadside ground | Dry scrubland / dirt |
| Curves | Moderate |
| Hills | Low to moderate |
| Traffic density | Moderate |
| Difficulty | Moderate |

### Stage 4B: Old Capital (Tier 4)

| Property | Value |
|----------|-------|
| Position | 4B (right from Desert OR left from Alps) |
| Theme | Ancient European city / historic urban area |
| Sky | Warm golden/amber (late afternoon sun) |
| Scenery | Old stone buildings, castle walls, clock towers, cobblestone-bordered roads, archways |
| Road surface | Smooth grey asphalt |
| Roadside ground | Stone curbs, building facades |
| Curves | Frequent medium-radius city turns |
| Hills | Gentle |
| Traffic density | Moderate to heavy |
| Difficulty | Moderate-hard |

### Stage 4C: Wheat Field (Tier 4)

| Property | Value |
|----------|-------|
| Position | 4C (right from Alps OR left from Cloudy Mountain) |
| Theme | Golden wheat fields and windmills (Netherlands/rural Europe) |
| Sky | Bright blue with scattered clouds |
| Scenery | Tall golden wheat on both sides, windmills, farmhouses, tulip patches |
| Road surface | Light grey asphalt |
| Roadside ground | Golden wheat / green grass |
| Curves | Moderate, sweeping through fields |
| Hills | Gentle rolling countryside |
| Traffic density | Moderate |
| Difficulty | Moderate |

### Stage 4D: Seaside Town (Tier 4, Rightmost)

| Property | Value |
|----------|-------|
| Position | 4D (right fork from Cloudy Mountain) |
| Theme | Coastal Mediterranean town |
| Sky | Vivid blue, low sun angle |
| Scenery | White-washed buildings, harbor views, lighthouses, fishing boats, seagulls |
| Road surface | Light asphalt |
| Roadside ground | Sandy/stone |
| Curves | Sharp, tight town streets |
| Hills | Moderate (coastal elevation changes) |
| Traffic density | Heavy |
| Difficulty | Hard |

### Stage 5A: Vineyard (Goal A, Leftmost)

| Property | Value |
|----------|-------|
| Position | 5A - Goal A (left fork from Wilderness) |
| Theme | Lush vineyard / wine country |
| Sky | Warm golden sunset |
| Scenery | Rows of grapevines, rustic stone walls, rolling green hills, wine estate buildings |
| Road surface | Clean asphalt |
| Roadside ground | Vine rows, green grass |
| Curves | Gentle to moderate |
| Hills | Rolling vineyard hills |
| Traffic density | Light to moderate |
| Difficulty | Easiest Goal |
| Ending | Driver hoisted by crowd, gets distracted by woman, is dropped |

### Stage 5B: Death Valley (Goal B)

| Property | Value |
|----------|-------|
| Position | 5B - Goal B (right from Wilderness OR left from Old Capital) |
| Theme | Harsh desert wasteland |
| Sky | Blazing orange/red |
| Scenery | Bleached rock formations, dried bones/skulls, cracked earth, heat shimmer |
| Road surface | Bleached pale asphalt |
| Roadside ground | Cracked dry desert floor |
| Curves | Moderate to sharp |
| Hills | Moderate |
| Traffic density | Moderate |
| Difficulty | Moderate |
| Ending | Ferrari falls apart at the finish line; driver awaits roadside assistance |

### Stage 5C: Desolation Hill (Goal C)

| Property | Value |
|----------|-------|
| Position | 5C - Goal C (right from Old Capital OR left from Wheat Field) |
| Theme | Barren rocky hillside / desert with ancient ruins |
| Sky | Dusky purple/twilight |
| Scenery | Sparse rock formations, sand, ruins, desolate landscape |
| Road surface | Worn dark asphalt |
| Roadside ground | Rocky barren ground |
| Curves | Sharp and technical |
| Hills | Steep |
| Traffic density | Heavy |
| Difficulty | Hard |
| Ending | Ferrari runs out of fuel; driver discovers a magic lamp and wishes for a harem |

### Stage 5D: Autobahn (Goal D)

| Property | Value |
|----------|-------|
| Position | 5D - Goal D (right from Wheat Field OR left from Seaside Town) |
| Theme | German highway / high-speed motorway |
| Sky | Clear blue, bright daylight |
| Scenery | Highway barriers, road signs, modern buildings, German countryside, castles in distance |
| Road surface | Smooth dark asphalt (highway quality) |
| Roadside ground | Green grass, guardrails |
| Curves | Long high-speed sweepers, occasional sharp turns |
| Hills | Moderate |
| Traffic density | Heavy (fast-moving traffic) |
| Difficulty | Hard |
| Ending | Trophy ceremony: presenter bypasses driver and awards trophy to female passenger |

### Stage 5E: Lakeside (Goal E, Rightmost)

| Property | Value |
|----------|-------|
| Position | 5E - Goal E (right fork from Seaside Town) |
| Theme | Mountain lakeside / alpine lake |
| Sky | Clear, bright |
| Scenery | Crystal lake, pine forests, mountain reflections, wooden bridges, alpine lodges |
| Road surface | Narrow asphalt |
| Roadside ground | Pine needles, rocky shore |
| Curves | Extremely sharp and frequent; hairpin turns |
| Hills | Very steep mountain terrain |
| Traffic density | Very heavy |
| Difficulty | Hardest Goal |
| Ending | Driver finally receives trophy, then flexes biceps in celebration |

---

## 7. Traffic System

### Traffic Vehicle Types

| Vehicle | Based On | Visual Description | Behavior |
|---------|----------|-------------------|----------|
| Volkswagen Beetle | VW Beetle | Small rounded sedan, various colors | Slow-moving, predictable, stays in lane |
| Corvette | Chevrolet Corvette (C3, ~1971) | Long sporty coupe, red/white | Aggressive; never yields; cuts in front of player |
| Porsche | Porsche 911 Turbo (~1975) | Sleek sports car, silver/white | Fast-moving; tends to move out of player's way |
| BMW | BMW 3 Series (~1986) | Mid-size sedan, dark colors | Moderate speed; changes lanes unpredictably |
| Convertible | Made-for-game design | Open-top car, bright colors | Moderate speed; standard lane behavior |
| Truck / Lorry | Made-for-game design | Large cab-over truck, grey/blue | Very slow; wide vehicle; hard to pass; a major obstacle |
| Motorcycle | KTM 250 Enduro Sport (~1985) | Small single-rider bike | Fast; weaves between lanes |
| Suzuki Jeep | Suzuki SJ (Samurai) | Small 4x4, boxy shape | Moderate speed; steady lane |

### Traffic AI Behavior

| Behavior | Description |
|----------|-------------|
| Lane occupation | Traffic vehicles occupy specific lanes and maintain their lane center position |
| Lane changing | Vehicles periodically shift lanes; frequency increases on harder stages |
| Speed variation | Each vehicle type has a base speed range; trucks are slowest (~150-180 km/h), sports cars fastest (~220-260 km/h) |
| Player-reactive | Some vehicles (Corvette) actively drift into player's path; others (Porsche) drift away |
| Spawning | Traffic spawns ahead of the player at draw distance; density controlled by DIP switch "Enemy Density" setting |
| Road sharing | All traffic moves in the same direction as the player (no oncoming traffic) |
| Maximum on-screen | Up to 6-8 traffic vehicles visible simultaneously |
| Cluster patterns | Traffic often appears in clusters of 2-3 vehicles side-by-side, forcing the player to find gaps |

### Traffic Density by DIP Setting

| DIP Setting | Approximate Traffic Level |
|-------------|--------------------------|
| Easy | ~40% of normal spawn rate |
| Normal (default) | Base spawn rate |
| Hard | ~130% of normal spawn rate |
| Hardest | ~160% of normal spawn rate |

---

## 8. Collision & Recovery

### Collision Types

| Collision Type | Trigger | Result |
|----------------|---------|--------|
| Sideswipe (traffic) | Player car clips side of traffic vehicle at slight angle | Speed penalty; car pushed sideways; minor time loss (~1-2 seconds) |
| Head-on (traffic) | Player car hits rear of traffic vehicle directly | Full crash sequence; car tumbles |
| Roadside object | Player car contacts tree, sign, rock, building while off-road or at road edge | Full crash sequence; car tumbles |
| Off-road (no object) | Player drives onto grass/dirt without hitting object | Speed penalty only; no crash |

### Crash Sequence

When a full crash is triggered:

| Phase | Duration | Description |
|-------|----------|-------------|
| Impact | ~0.5 sec | Car jolts; initial collision frame |
| Tumble / Barrel roll | ~2.5-3.0 sec | Car flips end-over-end and/or barrel rolls through the air; driver and passenger are thrown out and tumble separately. Car, driver, and passenger are all separate sprites during this animation. |
| Landing | ~0.5 sec | Car lands back on wheels (or rights itself); driver and passenger land nearby |
| Recovery | ~1.5-2.0 sec | Driver and passenger climb back into car; engine restarts |
| **Total crash time** | **~5-6 seconds** | Speed resets to 0 km/h; player must re-accelerate from standstill |

### Crash Design Philosophy

Yu Suzuki deliberately avoided having the car explode on impact, as was common in racing games of the era. Instead, the crash is dramatic but non-destructive -- the car tumbles, the occupants fly out, but everyone gets back in and continues. This maintains the game's lighthearted, vacation-driving tone.

### Crash Effects on Cabinet

| Cabinet Type | Crash Feedback |
|-------------|----------------|
| Upright (standard) | None |
| Upright (large) | Steering wheel force feedback vibration |
| Sit-down standard | Steering wheel vibration + seat vibration |
| Sit-down deluxe | Full hydraulic cabinet shakes; steering column struck repeatedly causing wheel vibration |

### Speed Penalties (Non-Crash)

| Situation | Speed Effect |
|-----------|-------------|
| Light sideswipe | ~30-50 km/h instant speed reduction |
| Off-road driving | Continuous deceleration; cap at ~80 km/h |
| Braking in curve | Controlled deceleration; maintains some speed |
| Coasting (no gas) | Gradual deceleration ~5 km/h per frame-cycle |

---

## 9. Timer & Checkpoint System

### Timer Operation

| Parameter | Value |
|-----------|-------|
| Timer display | Digital countdown displayed as whole seconds in HUD |
| Internal counter | 30-frame cycle per displayed second (at 30 FPS game logic = 1 real second per game second) |
| Frame reset value | 30 frames per countdown tick |
| Timer display | Shows seconds remaining; counts down to 00 |
| Time carry-over | Remaining time at checkpoint carries forward to next stage |

### Stage Time Limits (Normal DIP Setting)

| Stage | Initial Time Allocation | Notes |
|-------|------------------------|-------|
| Stage 1 (Coconut Beach) | 80 seconds | Starting time; generous for learning |
| Stage 2 (any) | 65 seconds | Added at Stage 1 checkpoint |
| Stage 3 (any) | 60 seconds | Added at Stage 2 checkpoint |
| Stage 4 (any) | 62 seconds | Added at Stage 3 checkpoint |
| Stage 5 (any) | 58 seconds | Added at Stage 4 checkpoint |

**Note**: The player starts with 80 seconds. When they cross the Stage 1 checkpoint, 65 seconds are added to whatever time remains. This means skilled players who reach checkpoints quickly accumulate a time buffer. These values are configurable via DIP switches.

### DIP Switch Time Settings

| DIP Setting | Effect on Time Allocations |
|-------------|---------------------------|
| Easy | All stage times increased by ~10-15% over Normal |
| Normal | Default values as listed above |
| Hard | All stage times reduced by ~10-15% from Normal |
| Hardest | All stage times reduced by ~20-25% from Normal |

### Checkpoint Mechanics

- A visual "CHECKPOINT" banner appears across the road as the player approaches the end of each stage.
- Crossing the checkpoint line triggers:
  1. Time extension (new seconds added)
  2. "EXTEND TIME" text flashes on screen for ~2 seconds (`extend_play_timer = 0x80`)
  3. Score bonus calculation
  4. Road fork appears shortly after checkpoint

### Game Over

- When timer reaches 00, the game displays "GAME OVER" for 3 seconds.
- If the timer runs out very close to a checkpoint, the game may grant a brief grace period of ~1-2 seconds to cross.
- High score entry screen appears if the player qualifies.

---

## 10. Scoring System

### Continuous Scoring

Points accumulate continuously while driving, based on speed and gear:

| Condition | Points Per Game Second (approx.) |
|-----------|----------------------------------|
| High gear, top speed (~293 km/h) | ~131,072 points/sec (doubled rate) |
| High gear, moderate speed (~200 km/h) | ~65,536 points/sec |
| Low gear, top speed (~193 km/h) | ~32,768 points/sec (base rate) |
| Low gear, moderate speed (~120 km/h) | ~16,384 points/sec |
| Stopped / very slow | 0 points |

**Key rule**: Driving in High gear at higher speeds awards approximately **twice** the points compared to Low gear at equivalent progress. This creates a risk/reward dynamic: High gear is faster and scores more, but is harder to control.

### Stage Completion Bonus

Upon crossing a checkpoint:
- No explicit per-stage bonus beyond the continuous scoring during that stage.
- All stages are the same length, so maximum points per stage are consistent regardless of path chosen.

### Goal Completion Bonus (Final Stage)

Upon crossing the Goal line at the end of Stage 5:

| Bonus Type | Value |
|------------|-------|
| Time remaining bonus | 1,000,000 points x seconds remaining on timer |
| Example: 15 seconds left | 15,000,000 bonus points |

This massive time bonus makes efficient driving through all 5 stages critical for high scores. Skilled players who accumulate large time reserves earn enormous bonuses.

### Score Display

- Score is displayed as a numeric value in the HUD, updating in real-time.
- Maximum displayable score: 99,999,999 (8 digits).
- High score table: Stores initials (3 characters) and score for top performers.

### Difficulty and Scoring

The game does not award more points for harder routes. Since all stages are the same length, the scoring potential is identical for all 16 possible paths. However, harder routes mean more time lost to crashes and slow-downs, resulting in less time remaining for the Goal bonus.

---

## 11. Music Selection System

### Radio Selection Screen

Before the race begins, the player is presented with a music selection screen:

| Element | Description |
|---------|-------------|
| Visual metaphor | Car radio dial / tuner displayed on screen |
| Input method | Steering wheel left/right or gear shift to cycle between stations |
| Confirm | Pressing accelerator pedal or waiting through attract timer |
| Number of selectable tracks | 3 |
| Display | Track name displayed as the player scrolls through options |

### Selectable Tracks

| Track Name | Genre / Style | Tempo | Character |
|------------|---------------|-------|-----------|
| **Magical Sound Shower** | Latin pop / Caribbean fusion | ~130 BPM | Upbeat, energetic, bright brass melody with driving percussion; most popular choice. Influenced by Latin jazz musician Naoya Matsuoka. |
| **Passing Breeze** | Smooth jazz / bossa nova | ~110 BPM | Relaxed, mellow, smooth saxophone lead over gentle rhythm; evokes a leisurely cruise. |
| **Splash Wave** | Synth-pop / fusion rock | ~140 BPM | Driving synth melody with electric guitar accents; energetic and forward-pushing. Most "racing" feel of the three. |

### Non-Selectable Tracks

| Track Name | When It Plays | Style |
|------------|---------------|-------|
| **Last Wave** | Final score screen / ending sequence after completing all 5 stages | Triumphant, celebratory orchestral-Latin fusion; plays over the ending animation and high score entry |

### Music Technical Implementation

| Property | Value |
|----------|-------|
| FM channels used | Up to 8 (Yamaha YM2151) |
| PCM channels used | Up to 5 (Sega 315-5218) for drums and samples |
| Composition format | MML (Music Macro Language) transcribed from sheet music |
| Loop behavior | Selected track loops continuously throughout all 5 stages |
| Music does NOT change | Between stages; same track plays from start to goal |

---

## 12. Audio Design

### Sound Chip Architecture

| Chip | Role | Channels | Specs |
|------|------|----------|-------|
| Yamaha YM2151 | FM synthesis (melodies, bass, harmonies) | 8 FM channels | 4 MHz clock, 4-operator FM |
| Sega 315-5218 (SegaPCM) | PCM sample playback (drums, SFX, voice) | 16 PCM channels | 4 MHz clock, 12-bit audio, 31.25 kHz sample rate, stereo output |
| Z80 CPU | Sound driver / sequencer | N/A | 4 MHz; runs the music macro language interpreter |

### Sound Effects

| Sound Effect | Trigger | Description |
|-------------|---------|-------------|
| Engine idle | Game start, low speed | Low rumbling idle, pitch-shifts with RPM |
| Engine acceleration | Throttle applied | Rising pitch engine whine; pitch proportional to speed |
| Engine high gear | High gear at speed | Higher-pitched engine note than low gear |
| Gear shift | Toggling gear lever | Brief mechanical "clunk" followed by RPM change |
| Tire screech | Hard steering at speed, or braking | High-pitched squeal; longer duration for harder inputs |
| Off-road rumble | Driving on grass/dirt | Crunchy gravel/dirt sound effect |
| Crash impact | Collision with object/traffic | Metal impact crash sound |
| Crash tumble | During barrel roll animation | Tumbling/rolling metallic sounds |
| Checkpoint chime | Crossing checkpoint line | Bright chime/bell sound + "EXTEND TIME" jingle |
| Crowd cheering | Reaching goal line | Crowd roar / celebration sound |
| Wave splash | Coconut Beach (ambient) | Ocean wave sounds |
| Wind | High speed | Rushing wind sound, volume proportional to speed |
| Music radio tuning | Music selection screen | Static/tuning sound between stations |
| Game Over | Timer expires | Descending tone / fanfare |
| Coin insert | Credit added | Standard coin-in chime |

### Stereo Sound

- Both sit-down cabinet models feature **stereo speakers mounted behind the driver's head**.
- Engine sound is centered; music is in full stereo.
- Passing traffic produces brief stereo panning effects (left speaker -> right speaker as a car is overtaken).

---

## 13. UI Layout

### HUD Elements (During Gameplay)

The HUD is overlaid on the game view and occupies minimal screen space:

```
+----------------------------------------------------------+
|  SCORE: 00000000              TIME: 75          LAP: --  |
|  [Top bar - score left, time center-right]               |
|                                                          |
|                                                          |
|                    (Game View)                            |
|                                                          |
|                                                          |
|                                                          |
|  SPEED: 293 km/h          [TACHOMETER]      STAGE: 3    |
|  [Bottom bar - speed left, tacho center, stage right]    |
+----------------------------------------------------------+
```

| HUD Element | Position | Format | Description |
|-------------|----------|--------|-------------|
| Score | Top-left | 8-digit number | Running score, updates in real-time |
| Time | Top-center to top-right | 2-digit countdown | Seconds remaining; flashes red when < 10 seconds |
| Speed | Bottom-left | 3-digit number + "km/h" | Current speed in kilometers per hour (0-293) |
| Tachometer | Bottom-center | Vertical bar graph | Row of colored blocks indicating engine RPM; rises with speed. Colors: green (low), yellow (mid), red (high/redline) |
| Stage indicator | Bottom-right | "STAGE X" (1-5) | Current stage number |
| Gear indicator | Near speed display | "LOW" / "HIGH" | Current gear selection |
| High score | Top area (flashing) | "HI: XXXXXXXX" | Shown intermittently or at game start |

### Tachometer Detail

| RPM Zone | Block Color | Meaning |
|----------|-------------|---------|
| Low RPM | Green blocks | Safe acceleration range |
| Mid RPM | Yellow blocks | Optimal shift point approaching |
| High RPM / Redline | Red blocks | Maximum power; optimal moment to shift to High gear |

The tachometer is displayed as a set of blocks which rise and fall according to engine RPM and speed. The number of lit blocks increases as speed increases within the current gear.

### Special Screen Overlays

| Overlay | Trigger | Display |
|---------|---------|---------|
| Music selection | Game start (before race) | Radio tuner graphic with 3 track names; steering selects |
| CHECKPOINT | Reaching end of stage | Large "CHECKPOINT" banner across road + "EXTEND TIME" text |
| GAME OVER | Timer reaches 00 | "GAME OVER" centered on screen for 3 seconds |
| Goal reached | Crossing Stage 5 finish | "GOAL" banner + ending cutscene triggers |
| EXTEND PLAY | Continue prompt (if enabled) | Countdown for credit insertion |
| High score entry | After game end if qualifying | 3-character initial entry with on-screen keyboard |
| Attract mode | No credits / idle | Cycles between gameplay demo, high score table, and title screen |

### Attract Mode Views

The attract mode cycles through 3 camera perspectives:

| View | Description |
|------|-------------|
| Original | Standard behind-car view (normal gameplay camera) |
| Elevated | Higher camera angle, more of the road visible |
| In-car | Cockpit-adjacent view from driver's perspective |

Attract mode cycles views every 240 frames (~8 seconds at 30 FPS).

### Screen Transitions

| Transition | Effect |
|-----------|--------|
| Stage to stage | Seamless -- road forks and new scenery loads progressively; no loading screen |
| Crash to recovery | In-place animation; no screen change |
| Goal to ending | Brief fade/cut to ending scene illustration |
| Ending to score | Dissolve to high score / "Last Wave" plays |

---

## 14. Cabinet & Input Hardware

### Cabinet Variants

| Cabinet Type | Description | Special Features |
|-------------|-------------|-----------------|
| Mini Upright | Compact standing cabinet; 20" monitor | No force feedback |
| Standard Upright | Full-size standing cabinet; 20" monitor | Steering wheel force feedback |
| Sit-Down Standard | Enclosed sitting cabinet resembling car cockpit; 26" monitor | Force feedback steering + seat vibration |
| Sit-Down Deluxe (Hydraulic) | Full motion simulator cabinet shaped like a Ferrari; 26" monitor | Hydraulic actuators tilt/shake entire cabinet; force feedback steering; stereo speakers behind headrest |

### Input Controls

| Control | Type | Range | Function |
|---------|------|-------|----------|
| Steering wheel | Analog (potentiometer) | ~270 degrees of rotation | Lateral car control |
| Accelerator pedal | Analog (potentiometer) | 0-100% depression | Speed / throttle control |
| Brake pedal | Analog (potentiometer) | 0-100% depression | Deceleration |
| Gear shift lever | Digital toggle (2 positions) | Low / High | Gear selection |
| Start button | Digital | Momentary | Start game / insert credit |
| Coin slot(s) | Mechanical | N/A | Credit insertion |

### DIP Switch Configuration Summary

| Switch Bank | Setting | Options | Default |
|-------------|---------|---------|---------|
| A | Coin configuration | Multiple credit ratios (1C/1Cr through Free Play) | 1 Coin / 1 Credit |
| B | Cabinet type | Moving, Up Cockpit, Mini Up, Cockpit | Varies by cabinet |
| B | Time adjustment | Easy, Normal, Hard, Hardest | Normal |
| B | Enemy (traffic) density | Easy, Normal, Hard, Hardest | Normal |
| B | Advertise sound | On / Off | On |

---

## Appendix: Complete Route Table

All 16 possible paths through the 5-stage tree:

| Route # | Stage 1 | Fork | Stage 2 | Fork | Stage 3 | Fork | Stage 4 | Fork | Stage 5 (Goal) | Difficulty |
|---------|---------|------|---------|------|---------|------|---------|------|----------------|------------|
| 1 | Coconut Beach | L | Gateway | L | Desert | L | Wilderness | L | Vineyard (A) | Easiest |
| 2 | Coconut Beach | L | Gateway | L | Desert | L | Wilderness | R | Death Valley (B) | Easy |
| 3 | Coconut Beach | L | Gateway | L | Desert | R | Old Capital | L | Death Valley (B) | Easy-Med |
| 4 | Coconut Beach | L | Gateway | L | Desert | R | Old Capital | R | Desolation Hill (C) | Medium |
| 5 | Coconut Beach | L | Gateway | R | Alps | L | Old Capital | L | Death Valley (B) | Medium |
| 6 | Coconut Beach | L | Gateway | R | Alps | L | Old Capital | R | Desolation Hill (C) | Medium |
| 7 | Coconut Beach | L | Gateway | R | Alps | R | Wheat Field | L | Desolation Hill (C) | Medium |
| 8 | Coconut Beach | L | Gateway | R | Alps | R | Wheat Field | R | Autobahn (D) | Med-Hard |
| 9 | Coconut Beach | R | Devil's Canyon | L | Alps | L | Old Capital | L | Death Valley (B) | Medium |
| 10 | Coconut Beach | R | Devil's Canyon | L | Alps | L | Old Capital | R | Desolation Hill (C) | Medium |
| 11 | Coconut Beach | R | Devil's Canyon | L | Alps | R | Wheat Field | L | Desolation Hill (C) | Med-Hard |
| 12 | Coconut Beach | R | Devil's Canyon | L | Alps | R | Wheat Field | R | Autobahn (D) | Hard |
| 13 | Coconut Beach | R | Devil's Canyon | R | Cloudy Mountain | L | Wheat Field | L | Desolation Hill (C) | Hard |
| 14 | Coconut Beach | R | Devil's Canyon | R | Cloudy Mountain | L | Wheat Field | R | Autobahn (D) | Hard |
| 15 | Coconut Beach | R | Devil's Canyon | R | Cloudy Mountain | R | Seaside Town | L | Autobahn (D) | Very Hard |
| 16 | Coconut Beach | R | Devil's Canyon | R | Cloudy Mountain | R | Seaside Town | R | Lakeside (E) | Hardest |
