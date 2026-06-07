# Monument Valley — Complete Game Specification

> A comprehensive specification for faithfully recreating Monument Valley (ustwo Games, 2014 mobile puzzle game). This document covers every system, mechanic, level, and interaction required for a full clone of the original release including the Forgotten Shores and Ida's (RED) Dream expansions.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics — Impossible Geometry](#3-core-mechanics--impossible-geometry)
4. [Player Movement System](#4-player-movement-system)
5. [Interaction Types](#5-interaction-types)
6. [Puzzle Element Types](#6-puzzle-element-types)
7. [Crow People System](#7-crow-people-system)
8. [Totem Mechanics](#8-totem-mechanics)
9. [The Storyteller (Ghost NPC)](#9-the-storyteller-ghost-npc)
10. [All Chapters — Main Game (I through X)](#10-all-chapters--main-game-i-through-x)
11. [Forgotten Shores Expansion (Appendices i through viii)](#11-forgotten-shores-expansion-appendices-i-through-viii)
12. [Ida's (RED) Dream Expansion](#12-idas-red-dream-expansion)
13. [Visual & Perspective System](#13-visual--perspective-system)
14. [Narrative System](#14-narrative-system)
15. [UI Layout](#15-ui-layout)
16. [Audio Design](#16-audio-design)
17. [Art Direction](#17-art-direction)
18. [Sacred Geometry Collectibles](#18-sacred-geometry-collectibles)

---

## 1. Game Overview

- **Title**: Monument Valley
- **Developer**: ustwo Games (London, UK)
- **Original Release**: April 3, 2014 (iOS); subsequently Android, Windows Phone, PC (Panoramic Edition)
- **Genre**: Isometric puzzle / exploration / optical illusion
- **Perspective**: Fixed isometric (30-degree axonometric projection)
- **Input**: Touch-only (tap to move, drag to rotate/slide). No on-screen buttons for movement.
- **Orientation**: Portrait (vertical) on mobile devices
- **Objective**: Guide Princess Ida through impossible architecture to return pieces of Sacred Geometry at the end of each level.
- **Fail Condition**: None. The player cannot die, fall, or lose. Crow People block paths but never kill Ida.
- **Win Condition**: Reach the designated exit point of each level, typically a pedestal where Sacred Geometry is returned.
- **Total Levels**: 10 main chapters + 8 Forgotten Shores appendices + 1 Ida's Dream hub with 5 sub-levels = **24 playable stages**
- **Average Playtime**: 2–3 hours for the main 10 chapters; ~1.5 hours per expansion
- **Price Model**: Premium (paid up-front). Forgotten Shores was an additional in-app purchase ($1.99 USD). Ida's Dream was initially $0.99 for charity (RED), later included free.

---

## 2. Technical Foundation

### Engine & Rendering

| Property | Value |
|----------|-------|
| Engine | Unity (C#) |
| Projection | Orthographic (isometric) — NOT perspective |
| Camera angle | Fixed 30-degree isometric (dimetric approximation) |
| Camera behavior | Static per scene; no player-controlled camera rotation |
| Rendering style | Flat-shaded, low-poly geometry with no textures on architecture |
| Shadow model | Pre-baked ambient occlusion; no real-time shadows |
| Target frame rate | 60 FPS on mobile devices |
| Audio middleware | Fabric plugin for Unity |

### Isometric Grid Rules

| Property | Value |
|----------|-------|
| Grid angle | All visible edges are at exactly 30 degrees, 120 degrees, or perfectly vertical (90 degrees) |
| Grid unit | 1 block = 1 walkable tile; Ida occupies exactly 1 tile |
| Vertical step height | 1 block unit (Ida can ascend/descend 1 block via stairs or ramps) |
| Coordinate system | 3D world space rendered through orthographic camera; Z-depth has no visual effect on object size |
| Tile connectivity | Nodes on walkable surfaces; edges between adjacent nodes form valid paths |

### Display

| Property | Value |
|----------|-------|
| Original target device | iPad (portrait orientation) |
| Aspect ratio | Flexible; scales to device (optimized for both phone and tablet) |
| Portrait orientation | Required on mobile; Panoramic Edition supports landscape |
| Scaling mode | Levels centered in viewport; letterboxed if necessary |
| Anti-aliasing | MSAA or FXAA depending on device capability |

### Game Loop

```
1. Process input (tap location, drag gesture start/continue/end)
2. Determine input target:
   a. Tap on walkable surface → pathfind Ida to destination
   b. Drag on Rotator → rotate associated geometry
   c. Drag on Dragger → slide associated geometry
   d. Drag on Drawer → extend/retract platform
3. Update navigation graph (recompute node connectivity based on new geometry positions)
4. Update Ida movement (walk along path, animate step-by-step)
5. Update Totem movement (if controlled, slide along rail)
6. Update Crow People patrol (advance along fixed patrol paths)
7. Check button/switch triggers (entity on pressure plate? → activate effect)
8. Update environmental animations (water, flags, particles)
9. Check level completion (Ida on exit tile → trigger Sacred Geometry return cutscene)
10. Render (background → water → architecture → characters → particles → UI overlay)
```

### Navigation System

| Property | Description |
|----------|-------------|
| Node placement | Walkable surfaces are marked with navigation nodes at each tile position |
| Edge rules | Two nodes are connected if: (a) they are adjacent on the same surface, OR (b) they visually align in the isometric view regardless of actual 3D position |
| Impossible connections | When geometry is rotated/slid such that two surfaces appear to touch from the camera's viewpoint, their nodes become connected — even if they are far apart in 3D space |
| Path recalculation | Triggered every time any geometry is moved (rotate, slide, or drawer) |
| Pathfinding algorithm | Breadth-first search or A* on the navigation graph |
| Node highlighting | Reachable nodes are subtly highlighted when Ida could walk to them; unreachable nodes are not |
| Walk validation | Ida only walks to a tapped position if a valid path exists from her current node to the target node |

---

## 3. Core Mechanics — Impossible Geometry

### Fundamental Principle

Monument Valley's core mechanic is that **visual alignment equals physical connection**. If two walkable surfaces appear to touch from the fixed isometric camera angle, they ARE connected for navigation purposes — even if in true 3D space they are meters apart. This is the game's central illusion and the basis of every puzzle.

### Impossible Object Types Used

| Illusion Type | Description | Example Usage |
|---------------|-------------|---------------|
| Penrose Triangle | A triangle whose three sides each appear to recede in perspective but connect seamlessly | Chapter IV: Water Palace uses triangular paths that fold back on themselves |
| Penrose Stairs | A staircase that ascends perpetually in a closed loop | Chapter V: The Spire features looping stairways around the tower |
| Impossible Cube (Necker Cube) | A cube where edges connect in contradictory ways | Chapter VIII: The Box is built entirely around this concept |
| Escher-style multi-gravity | Surfaces on which characters walk sideways or upside-down relative to the player's frame | Chapter IV introduces sideways walking; Chapter VIII uses all orientations |
| False depth | Two surfaces at different 3D depths that appear coplanar from isometric view | Used throughout; rotating geometry changes which surfaces visually align |

### How Connections Work

1. **Static connections**: Standard adjacency — two tiles sharing an edge on the same plane.
2. **Dynamic connections**: Created when the player manipulates geometry (rotate, slide) so that two previously disconnected surfaces visually align.
3. **Broken connections**: Rotating or sliding geometry can also disconnect paths that were previously valid.
4. **Gravity-defying connections**: Ida can walk from a horizontal surface onto a vertical wall if they share a visual edge. She rotates 90 degrees to match the surface orientation.

### Perspective Manipulation Rules

| Rule | Detail |
|------|--------|
| Single viewpoint | The camera never rotates; all illusions work because the viewpoint is fixed |
| Orthographic projection | No perspective foreshortening; parallel lines remain parallel, enabling clean impossible geometry |
| Edge alignment tolerance | If two walkable edges are within approximately 2 pixels of visual alignment, they snap-connect |
| Z-fighting resolution | When two surfaces overlap visually, the one Ida is currently on (or moving toward) takes priority |
| Transition animation | When Ida crosses an impossible connection, she smoothly walks across; no teleportation visible to the player |

---

## 4. Player Movement System

### Princess Ida — Character Properties

| Property | Value |
|----------|-------|
| Appearance | Small white figure wearing a pointed white hat (conical); minimal facial features |
| Height | Approximately 1.5 block units tall |
| Width | Approximately 0.5 block units |
| Walk speed | ~2.5 tiles per second (steady, unhurried pace) |
| Stair speed | Same as walk speed; Ida steps up/down stairs smoothly |
| Ladder speed | Slightly slower than walk speed (~2 tiles/second) |
| Wall-walk transition | 0.3-second rotation animation to align with new surface |
| Idle animation | Subtle breathing/swaying; Ida looks around after ~5 seconds of inactivity |
| Hat behavior | Hat bobs slightly with walking; removed during Chapter III of Forgotten Shores (The Thief) |
| Carrying items | Can pick up a red flower (Chapter IX) by walking adjacent to it |

### Movement Rules

1. **Tap-to-move**: The player taps any reachable walkable tile. Ida pathfinds and walks there autonomously.
2. **No direct control**: There is no joystick, D-pad, or swipe-to-move. Movement is entirely tap-based.
3. **Path display**: A faint dotted line briefly shows the path Ida will take (only on some versions).
4. **Queueing**: If the player taps a new destination while Ida is walking, she redirects to the new destination immediately.
5. **Blocked paths**: If no valid path exists to the tapped location, Ida does not move. No error sound or visual feedback — she simply stays put.
6. **Stairs**: Ida automatically ascends/descends stairs when they are part of her path. Stairs are 1-block-high transitions rendered as 2–4 small steps.
7. **Ladders**: Ida can climb vertical ladders connecting different levels of a structure. She pauses briefly at top/bottom transitions.
8. **Wall walking**: When Ida reaches an edge where a horizontal surface meets a vertical surface (and they are connected), she rotates 90 degrees and walks along the wall as though it were the floor.
9. **Underside walking**: Similarly, Ida can walk on the underside of platforms if the geometry routes her there.
10. **Riding the Totem**: Ida can stand on top of the Totem. When the Totem is slid by the player, Ida rides along on top. She can then step off onto adjacent walkable surfaces.
11. **Riding moving platforms**: If Ida is standing on a platform that is rotated or slid, she moves with it.

### Ida's Footstep Sounds

| Surface | Sound |
|---------|-------|
| Stone/default | Soft tap-tap at walk tempo |
| Water/shallow | Light splash |
| Metal grate | Higher-pitched clink |
| Wooden bridge | Hollow thump |

---

## 5. Interaction Types

Monument Valley features exactly **four** types of interactive elements the player can manipulate, plus tap-to-move.

### 5.1 Rotators (Cranks/Wheels)

| Property | Value |
|----------|-------|
| Appearance | A circular handle protruding from the face of a structure, with a visible grip circle |
| Interaction | Drag in a circular motion (clockwise or counter-clockwise) |
| Effect | Rotates the geometry that the rotator is attached to — typically a platform, tower section, or stairway |
| Rotation axis | Depends on placement: can be horizontal (spinning like a top), vertical (like a turntable), or along the structure's primary axis |
| Snap angles | Many rotators snap to 90-degree increments; some allow continuous 360-degree rotation |
| Ida constraint | Rotators CANNOT be used while Ida is standing on the geometry they move (to prevent breaking path continuity with Ida mid-walk) |
| Visual feedback | The geometry smoothly rotates in real-time as the player drags. Impossible connections form/break dynamically |
| Audio feedback | Stone grinding sound during rotation; click/snap at rest positions |

### 5.2 Draggers (Slide Handles)

| Property | Value |
|----------|-------|
| Appearance | Small protruding circles (dot handles) on the face of a movable object or platform |
| Interaction | Drag linearly (up/down or left/right depending on the dragger's rail axis) |
| Effect | Slides the associated platform, pillar, or block along a constrained linear axis |
| Rail constraints | Movement is limited to a fixed rail/track; the dragger cannot be pulled past its endpoints |
| Ida constraint | Draggers CAN be used while Ida is standing on the platform they move — this is the key difference from Rotators |
| Totem constraint | Draggers on the Totem allow the player to slide the Totem while Ida rides it |
| Visual feedback | Platform slides smoothly in real-time along the rail |
| Audio feedback | Stone sliding sound; soft thud at rail endpoints |
| Typical usage | Moving platforms horizontally or vertically to bridge gaps, reach buttons, or align paths |

### 5.3 Drawers (Pull-out Platforms)

| Property | Value |
|----------|-------|
| Appearance | A small rectangular handle recessed into a wall |
| Interaction | Tap and drag outward from the wall |
| Effect | Extends a hidden platform out of the wall, creating a new walkable surface |
| Retraction | When Ida steps onto the drawer platform, the handle retracts and the platform locks in place (cannot be pulled back while occupied) |
| Levels used | Chapter IX: The Descent and Appendix vii: The Oubliette (only 2 levels use drawers) |
| Visual feedback | Platform slides out of wall slot smoothly |
| Audio feedback | Stone drawer sliding sound |

### 5.4 Buttons / Switches

| Property | Value |
|----------|-------|
| Appearance | Small raised geometric shapes on walkable surfaces — typically colored circles or squares |
| Interaction | Ida (or the Totem, or a Crow Person) walks onto the button tile |
| Activation | Triggered when any valid entity occupies the button tile |

#### Button Subtypes

| Subtype | Behavior | Visual |
|---------|----------|--------|
| Permanent Switch | Once pressed, stays activated forever; effect is permanent | Glows and stays depressed after activation |
| Pressure Plate (Short Switch) | Active only while an entity stands on it; reverts when entity leaves | Glows while occupied; rises back up when vacated |
| Sequence Button | Part of a sequence; all buttons in the set must be pressed (sometimes in order) to trigger effect | Each button lights up individually; final activation when all are lit |

#### Button Effects

| Effect Type | Description |
|-------------|-------------|
| Reveal stairs | Hidden stairway extends or unfolds from a wall |
| Move platform | A platform slides to a new position |
| Open door | A doorway opens or a wall retracts |
| Activate rotator | A previously locked rotator becomes usable |
| Raise/lower water | Water level changes in the area |
| Extend bridge | A bridge or walkway extends across a gap |
| Light a beacon | A colored light illuminates (aesthetic + progress tracking in Chapter X) |
| Trigger geometry shift | The entire level geometry reconfigures |

### 5.5 Doors

| Property | Value |
|----------|-------|
| Appearance | Rectangular openings in walls, often with a darker interior |
| Interaction | Ida walks into a door and emerges from a corresponding exit door elsewhere in the level |
| Behavior | Doors are one-way transitions between sections of a level. Ida enters one side and exits from the other. The camera may pan or cut to the new area. |
| Types | Some doors are pre-open; others require button activation to unlock |

---

## 6. Puzzle Element Types

### Environmental Puzzle Elements

| Element | Description | First Appearance |
|---------|-------------|-----------------|
| Rotating tower/pillar | A vertical structure that can be spun via a rotator; stairways on its surface connect to different platforms at different rotation angles | Chapter I |
| Sliding platform | A horizontal or vertical platform on a rail, moved via a dragger | Chapter III |
| Extending bridge | A platform that slides out from a wall when a button is pressed | Chapter II |
| Penrose staircase loop | A looping stairway where ascending leads back to the starting height | Chapter V |
| Impossible fork path | A path that splits and reconnects in ways only possible through perspective illusion | Chapter IV |
| Water reflection path | Ida can walk on the reflection of a structure in water | Appendix ii |
| Gravity flip zone | A transition point where Ida's orientation changes (walking on walls/ceilings) | Chapter IV |
| Nested structure | A level-within-a-level (e.g., a box that unfolds to reveal interior rooms) | Chapter VIII |
| Multi-section hub | A central structure that connects to several sub-puzzles | Chapter X, Ida's Dream |
| Collapsing/unfolding architecture | Structures that fold out, unfold, or collapse as the player progresses | Appendix i |
| Twisting tower | A structure whose sections can be twisted relative to each other via a gear | Appendix ii |
| Water level control | Levers that raise or lower the water, opening or blocking paths | Appendix iv |
| Crusher trap | A heavy block that repeatedly slams downward; must be blocked or avoided | Appendix v |

---

## 7. Crow People System

### Overview

The Crow People (also called "Crows" or "The Bothersome Crow People") are the primary obstacle in Monument Valley. They are not enemies in a combat sense — they cannot kill Ida — but they block her path and force the player to find detours or time their movements.

### Lore

The Crow People were originally Princess Ida's subjects. When Ida stole the Sacred Geometry from the valley's human civilization, the humans died and Ida's people were cursed to wander the monuments as dark, bird-like creatures. Ida's quest to return the Sacred Geometry is an act of penance that ultimately lifts their curse.

### Appearance

| Property | Value |
|----------|-------|
| Shape | Roughly humanoid with a prominent crow-like beak protruding upward |
| Color | Solid black with minimal detail |
| Size | Approximately the same height as Ida (1.5 block units) |
| Eyes | Not visible; the beak is the dominant feature |
| Animation | Bobbing walk cycle; head tilts; occasional squawking animation |

### Behavior & Patrol Patterns

| Property | Value |
|----------|-------|
| Movement type | Fixed patrol paths; walk back and forth along a predetermined route |
| Speed | Approximately the same as Ida (~2.5 tiles/second) |
| Patrol route | Linear back-and-forth between 2 endpoints on a walkable surface |
| Direction change | At each endpoint, the crow pauses briefly (~0.5 seconds) then reverses direction |
| Awareness of Ida | None — crows do not chase, follow, or target Ida |
| Blocking behavior | If Ida's desired path passes through a tile occupied by a crow, Ida cannot walk through. She stops at the adjacent tile and the crow squawks at her. |
| Response to geometry changes | Crows walk on whatever geometry they are placed on. If that geometry rotates or slides, the crow moves with it and continues its patrol on the new orientation. |
| Button interaction | Crows CAN trigger buttons/pressure plates by walking over them. This is used as a puzzle mechanic in several levels (notably Chapter VII: The Rookery). |
| Totem interaction | Crows treat the Totem as a wall — they reverse direction when they reach it, enabling the player to use the Totem to block crow patrol routes |

### Crow Appearances by Chapter

| Chapter | Crow Presence | Role |
|---------|--------------|------|
| I: Monument Valley | None | Tutorial; no obstacles |
| II: The Garden | Sitting crows (stationary) | Decorative / first introduction |
| III: Hidden Temple | None | Dragger introduction |
| IV: Water Palace | Stationary crows on walls | Blocking certain wall-walk paths |
| V: The Spire | **First walking crows** (3–5 patrolling) | Primary obstacle; timing puzzles |
| VI: The Labyrinth | 1–2 stationary crows | Minor obstacle; focus is on Totem |
| VII: The Rookery | Multiple walking crows | Crows are used as puzzle tools (they press buttons) |
| VIII: The Box | 1–2 crows inside box compartments | Timing puzzles within confined spaces |
| IX: The Descent | None | Atmospheric/narrative level |
| X: Observatory | 2–3 crows; 4 crows in ending ceremony | Moderate obstacle; final challenge |

### Player Strategies for Crows

1. **Wait and time**: Watch the crow's patrol loop and move when it walks away.
2. **Geometry manipulation**: Rotate or slide geometry to redirect crow patrols or create detour paths.
3. **Use the Totem**: Place the Totem in a crow's patrol path to shorten its route or block it entirely.
4. **Use crows as tools**: In some levels, the player must route crows onto pressure plates to trigger effects.

---

## 8. Totem Mechanics

### Overview

The Totem is a friendly NPC introduced in Chapter VI: The Labyrinth. It is a sentient pillar that aids Ida by serving as a movable platform and button presser. The Totem has a significant narrative arc across the Forgotten Shores expansion.

### Appearance

| Property | Value |
|----------|-------|
| Shape | Rectangular column, 4 blocks tall, 1 block wide |
| Color | Yellow/gold body with turquoise geometric patterns |
| Eye | Single large eye on the top block (purple iris with white sclera) |
| Expression | The eye blinks and looks around; conveys emotion through pupil direction and blink rate |
| Drag handles | Two protruding circular dots on the lower two blocks (dragger interaction points) |

### Movement Rules

| Property | Value |
|----------|-------|
| Control method | Player drags the Totem's handle dots (Dragger mechanic) |
| Movement axis | Linear sliding along a rail/track; horizontal or vertical depending on level geometry |
| Speed | Slides at the speed the player drags; snaps to grid positions when released |
| Ida riding | Ida can walk onto the top of the Totem. When the Totem moves, Ida rides along on top. |
| Button pressing | The Totem's base can trigger buttons/pressure plates, functioning as a permanent weight |
| Blocking crows | Crows reverse direction when encountering the Totem, treating it as a wall |
| Gravity | The Totem obeys the same impossible-geometry gravity as Ida — it stays on whatever surface it is placed on |
| Interaction with geometry | If the Totem is on a platform that rotates or slides, the Totem moves with it |

### Totem Appearances

| Chapter/Appendix | Totem Role |
|------------------|-----------|
| Chapter VI: The Labyrinth | Introduction; Ida meets the Totem and learns to slide it. Totem helps press buttons and bridge gaps. |
| Appendix i: The Chasm | Totem appears from lava to rescue Ida. Used as an elevator and platform. |
| Appendix ii: The Serpent Lake | Not present |
| Appendix iii: The Thief | Not present |
| Appendix iv: Halcyon Court | Not present |
| Appendix v: The Lost Falls | Totem sacrifices itself — attempts to block a crusher but is destroyed. Its 4 blocks scatter into the chasm below. |
| Appendix vi: The Citadel of Deceit | Not present (Ida grieves) |
| Appendix vii: The Oubliette | Not present |
| Appendix viii: Nocturne | Ida finds and reassembles the Totem's 4 scattered pieces. The Totem is restored. |

### Totem Narrative Arc

1. **Introduction (Chapter VI)**: Ida discovers the Totem trapped in the Labyrinth. They become companions.
2. **Partnership (Appendix i)**: The Totem rescues Ida from rising lava, establishing mutual trust.
3. **Sacrifice (Appendix v)**: The Totem selflessly stands beneath a crushing mechanism to hold it open for Ida. The crusher repeatedly strikes the Totem, eventually shattering it into its 4 component blocks that fall into the abyss.
4. **Grief (Appendix vi)**: Ida traverses a gray, desaturated world representing her sorrow.
5. **Restoration (Appendix viii)**: Ida collects the Totem's 4 scattered pieces from across a dark nighttime level, reassembles the Totem on a pedestal of light, and the Totem is reborn.

---

## 9. The Storyteller (Ghost NPC)

### Overview

The Storyteller (also called "the Ghost") is a spectral NPC that appears at certain points throughout the game to deliver dialogue and advance the narrative. It is the only character that speaks.

### Appearance

| Property | Value |
|----------|-------|
| Shape | Translucent, ghost-like figure; appears as a tall, thin spirit |
| Color | White/pale with slight transparency |
| Animation | Fades in and out; hovers slightly above the ground |
| Location | Found at fixed positions in specific chapters; Ida must walk near it to trigger dialogue |

### Dialogue by Chapter

| Chapter | Dialogue (approximate) |
|---------|----------------------|
| III: Hidden Temple | "Long have these old bones waited in darkness. How far have you wandered, silent princess? Why are you here?" |
| IV: Water Palace | "This was the valley of men. Now all that remains are our monuments, stripped of their glories. Thieving princess, why have you returned?" |
| VII: The Rookery | "Long ages lie heavy on old bones in these buried halls. Sacred geometry was our pride, our downfall. But forever will our monuments stand in this valley." |
| IX: The Descent | "How many monuments have you restored? How many still lie ahead? Forgetful princess confuses past, present and future. When all sacred geometry is returned, so too shall be your crown." |
| Appendix iv: Halcyon Court | Additional lore about Ida's reward for returning Sacred Geometry |

### Narrative Function

- Provides backstory about the valley's lost human civilization
- Reveals Ida's identity as the thief who stole Sacred Geometry
- Foreshadows Ida's redemption and the return of her crown
- Addresses Ida with titles that reflect her guilt: "silent princess," "thieving princess," "forgetful princess"

---

## 10. All Chapters — Main Game (I through X)

### Chapter I: Monument Valley (Tutorial)

| Property | Value |
|----------|-------|
| Subtitle | "Monument Valley" |
| Theme | Introduction / Tutorial |
| Color palette | Warm beige, soft peach, muted orange |
| Primary mechanic introduced | Tap-to-move, Rotators |
| Sacred Geometry returned | No (tutorial only — no Sacred Geometry piece) |
| Crow presence | None |
| Totem presence | None |
| Estimated duration | 1–2 minutes |

**Level Description**: A single small monument floating against a pastel sky. Ida stands at the bottom. The only interactive element is one rotator handle on the side of the structure. The player learns to tap to move Ida, then discovers the rotator by dragging it. Rotating the handle 180 degrees aligns a stairway with Ida's path. Walking up the newly connected stairs leads to the level exit at the top. A simple text prompt ("Tap where you would like the princess to go") teaches the controls.

**Puzzle Elements**: 1 rotator, 1 stairway realignment.

---

### Chapter II: The Garden

| Property | Value |
|----------|-------|
| Subtitle | "The Garden" |
| Theme | Expanding on basics; introducing buttons |
| Color palette | Lush greens, soft pinks, cream whites |
| Primary mechanic introduced | Buttons/Switches, extending bridges |
| Sacred Geometry returned | Yes |
| Crow presence | Stationary crows (sitting, decorative) — first appearance |
| Totem presence | None |
| Estimated duration | 3–5 minutes |

**Level Description**: A garden-like structure with hedges and rounded architectural elements. Ida begins at the top and must descend through multiple tiers. The player encounters the first rotator wheel that connects a path to a button. Pressing the button extends a bridge. A second button reveals a new stairway. The level introduces the core loop: manipulate geometry → press button → new path opens → progress. At the end, Ida places her first piece of Sacred Geometry on a pedestal. Stationary crows sit on ledges as a visual introduction — they do not block any path.

**Puzzle Elements**: 2 rotators, 3 buttons, 2 extending bridges, 1 ladder.

---

### Chapter III: Hidden Temple

| Property | Value |
|----------|-------|
| Subtitle | "Hidden Temple" |
| Theme | Introducing sliding mechanics; first Storyteller encounter |
| Color palette | Dusty terracotta, warm sandstone, deep red accents |
| Primary mechanic introduced | Draggers (sliding platforms) |
| Sacred Geometry returned | Yes |
| Crow presence | None |
| Totem presence | None |
| Storyteller | First appearance — delivers opening lore dialogue |
| Estimated duration | 5–8 minutes |

**Level Description**: A temple carved into warm sandstone with multiple tiers. This chapter introduces Draggers — movable platforms that slide on rails. The player must position Ida on a sliding platform, then drag it to bridge gaps. Two sliding platforms in the middle section must be coordinated: slide the right piece down, walk Ida across, slide the left piece up until both paths connect in the middle. A blue button at the end reveals the final staircase to the Sacred Geometry pedestal. The Storyteller (Ghost) appears for the first time, asking Ida why she has returned.

**Puzzle Elements**: 3 draggers (sliding platforms), 2 buttons, 1 ladder.

---

### Chapter IV: Water Palace

| Property | Value |
|----------|-------|
| Subtitle | "Water Palace" |
| Theme | Gravity-defying wall walking; Penrose geometry |
| Color palette | Soft pinks, rose, coral, with water (blue-green) below |
| Primary mechanic introduced | Wall walking (gravity rotation), impossible triangles |
| Sacred Geometry returned | Yes |
| Crow presence | Stationary crows on wall paths |
| Totem presence | None |
| Storyteller | Appears — "This was the valley of men" dialogue |
| Estimated duration | 8–12 minutes |

**Level Description**: Several pink architectural structures rise above a calm lake with lily pads. This is the first level to feature impossible geometry as a core puzzle mechanic. Ida begins on a conventional platform. A rotator turns the middle section, and when a platform aligns with Ida's position, she can walk to it. The breakthrough moment: pressing a gold button rotates the section Ida stands on 90 degrees, causing her to walk sideways on a wall. This introduces the gravity-rotation mechanic. The level features a Penrose triangle — an impossible triangular path that connects back to itself. By rotating sections, the player creates and breaks connections between surfaces at different orientations. The Storyteller appears again, lamenting the fall of the valley's civilization. Stationary crows on wall surfaces demonstrate that crows also obey impossible-geometry gravity.

**Puzzle Elements**: 3 rotators, 2 buttons (including 1 gravity-flip trigger), 1 impossible triangle path, wall-walking transitions.

---

### Chapter V: The Spire

| Property | Value |
|----------|-------|
| Subtitle | "The Spire" |
| Theme | Vertical tower; first walking Crow People; timing puzzles |
| Color palette | Cool blues, slate grays, white stone |
| Primary mechanic introduced | Walking (patrolling) Crow People |
| Sacred Geometry returned | Yes |
| Crow presence | 3–5 walking crows on patrol routes |
| Totem presence | None |
| Estimated duration | 10–15 minutes |

**Level Description**: A tall, narrow tower (the "Spire") that Ida must ascend from bottom to top. The tower features spiraling staircases and multiple rotator-controlled sections. The defining feature is the introduction of **walking Crow People** — black bird-like creatures that patrol back and forth along fixed paths. The player must time Ida's movements to slip past crows when they walk away. The first section has one crow on a stairway; the player waits for it to move right, then quickly moves Ida up. Later sections feature multiple crows on converging paths, requiring careful timing. Some crows can be diverted by rotating the platform they patrol on to a different orientation. A rotator at the mid-level creates a Penrose staircase loop — Ida ascends what appears to be an infinite staircase, but rotating the handle changes which floor she exits onto. The level culminates in navigating past the final crows to reach the top of the spire.

**Puzzle Elements**: 4 rotators, 3 buttons, 3–5 patrolling crows, Penrose staircase loop.

---

### Chapter VI: The Labyrinth

| Property | Value |
|----------|-------|
| Subtitle | "The Labyrinth" |
| Theme | Introduction of the Totem; cooperative puzzles |
| Color palette | Deep blue, teal, aquamarine, gold (Totem) |
| Primary mechanic introduced | Totem (friendly NPC pillar) |
| Sacred Geometry returned | Yes |
| Crow presence | 1–2 stationary crows |
| Totem presence | **Yes — first appearance** |
| Estimated duration | 10–15 minutes |

**Level Description**: A subterranean labyrinth of interconnected platforms. Ida encounters the Totem for the first time — a yellow pillar with a single eye that watches Ida and communicates through gentle eye movements. The player learns to drag the Totem using its handle dots, sliding it along rails. The core mechanic: Ida stands on the Totem's head, the player slides the Totem to a new position, and Ida steps off onto a previously unreachable platform. Puzzles require using the Totem as both a mobile platform and a weight for pressure plates. One key puzzle: slide the Totem onto a pressure plate to raise a distant platform, then walk Ida across the raised platform to a permanent switch that locks the path in place. The Totem's eye follows Ida's movements, establishing its character.

**Puzzle Elements**: 3 draggers (including Totem rails), 4 buttons (2 pressure plates requiring Totem weight), 1 rotator.

---

### Chapter VII: The Rookery

| Property | Value |
|----------|-------|
| Subtitle | "The Rookery" |
| Theme | Using Crow People as puzzle tools |
| Color palette | Warm amber, deep brown, red accents, golden light |
| Primary mechanic introduced | Crows pressing buttons (crow-as-tool mechanic) |
| Sacred Geometry returned | Yes |
| Crow presence | Multiple walking crows used as puzzle elements |
| Totem presence | None |
| Storyteller | Appears — "Sacred geometry was our pride, our downfall" dialogue |
| Estimated duration | 10–15 minutes |

**Level Description**: A warm-toned rookery (crow nesting ground) built as a rotating multi-level structure. This level inverts the player's relationship with Crow People — instead of avoiding them, the player must **use them**. The first section shows a single crow patrolling a platform with a button. The player rotates the level geometry so the crow's patrol path crosses the button, causing the crow to step on it and open a door for Ida. Later puzzles require multi-step crow manipulation: rotating platforms to redirect crow paths, using sliding pieces to block crows in specific positions, and timing rotations so crows land on buttons at the right moment. One puzzle involves raising a wall to block a crow, keeping Ida on a button, pulling a dragger down, then sending Ida through a door before the crow undoes it. The level features rotating building sections — the player turns the entire building to align staircases between floors. The Storyteller appears with heavy dialogue about the civilization's fall. The level ends with 4 crows standing at attention as Ida walks down a red carpet to the Sacred Geometry pedestal.

**Puzzle Elements**: 3 rotators (full-building rotators), 4 buttons (pressure plates activated by crows), multiple walking crows, 1 dragger.

---

### Chapter VIII: The Box

| Property | Value |
|----------|-------|
| Subtitle | "The Box" |
| Theme | Nested spaces; unfolding architecture; multi-perspective |
| Color palette | Multi-colored compartments — orange, green, blue, purple sections |
| Primary mechanic introduced | Nested structures that unfold; multi-room cube navigation |
| Sacred Geometry returned | Yes |
| Crow presence | 1–2 crows inside compartments |
| Totem presence | None |
| Estimated duration | 12–18 minutes |

**Level Description**: The most architecturally complex level in the main game. It begins with a small, closed box. The player lifts the lid (a drag gesture) to reveal the first compartment — a blue room. Inside, Ida walks to a button that lights a blue beacon. Exiting through a door leads to more box surfaces that unfold, revealing additional compartments. The box continuously opens, folds, and reconfigures, each time revealing a new colored section with its own mini-puzzle. Each section requires Ida to activate a colored beacon (blue, green, orange, purple) by reaching a button. Some sections feature wall-walking, with Ida navigating sideways rooms. One section has a crow on a timed patrol that steps on a bridge button, requiring Ida to move quickly. Another section features a ramp where Ida walks sideways. A rotating wheel inside one compartment rotates the camera perspective, changing which walls are floors. The level concludes when all 4 colored beacons are lit and the box fully unfolds into the Sacred Geometry pedestal.

**Puzzle Elements**: 2 rotators (including internal perspective rotation), 4 colored beacon buttons, 2 draggers, 1–2 crows, multiple door transitions between compartments.

---

### Chapter IX: The Descent

| Property | Value |
|----------|-------|
| Subtitle | "The Descent" |
| Theme | Backstory revelation; somber atmosphere; descent underground |
| Color palette | Dark blues, charcoal grays, deep purples; storm at opening; warm underground gold |
| Primary mechanic introduced | Drawers (pull-out platforms); flower carrying |
| Sacred Geometry returned | No — instead, Ida places a red flower at a grave |
| Crow presence | None |
| Totem presence | None |
| Storyteller | Appears — "When all sacred geometry is returned, so too shall be your crown" |
| Estimated duration | 8–12 minutes |

**Level Description**: The most narratively significant chapter. It opens during a storm at sea — Ida stands on a bare, rocky island with rain falling and waves crashing. A single red flower sits on the island; walking near it causes Ida to pick it up. The player uses drawers (pull-out handles on walls) to extend platforms and descend deeper underground. The architecture transitions from stormy exterior to ancient catacombs with warm golden light. The mood shifts from desolate to sacred. Gregorian-style chanting fills the audio as Ida descends further. She passes through burial halls lined with old stone tombs. The Storyteller speaks for the final time in the main game, revealing that returning all Sacred Geometry will restore Ida's crown. At the very bottom, Ida reaches a prominent grave and places the red flower upon it. This is one of only two chapters (alongside Chapter I) where Sacred Geometry is not returned. The chapter's icon on the level select screen shows the red flower instead of a geometric shape.

**Puzzle Elements**: 3 drawers (pull-out platforms), 2 buttons, atmospheric storytelling (minimal puzzle complexity).

---

### Chapter X: Observatory

| Property | Value |
|----------|-------|
| Subtitle | "Observatory" |
| Theme | Final challenge; multi-section hub; culmination of all mechanics |
| Color palette | Multi-sectioned — orange area, purple area, green area; white/gold for finale |
| Primary mechanic introduced | Hub-and-spoke level structure (central cube connecting to sub-levels) |
| Sacred Geometry returned | Yes — final piece; triggers ending cutscene |
| Crow presence | 2–3 patrolling crows; 4 ceremonial crows in ending |
| Totem presence | None |
| Estimated duration | 15–25 minutes |

**Level Description**: The longest and most challenging level, combining all mechanics learned throughout the game. It begins with a large central cube that the player can rotate by touching dotted grip points on its surface. The cube has colored pillars on its bottom face that can be spun independently. Rotating the cube reveals doorways into three distinct sub-levels, each themed by color:

1. **Orange Section**: Features rotating platforms, wall-walking, and crow-timing puzzles. A rotator creates impossible connections between upper and lower paths. Ida must light an orange beacon by reaching the section's button.

2. **Purple Section**: Features multiple rotations and door transitions. Complex stairway routing where the player must rotate the structure multiple times to create a continuous path upward. Ida lights a purple beacon.

3. **Green Section**: Features sliding platforms and Penrose-style impossible paths. The final crow-timing challenge guards the green beacon button.

After all three beacons are lit, the central cube reconfigures one final time, revealing the final Sacred Geometry pedestal at its summit. Ida walks up a grand staircase to the pedestal and returns the last geometric shape.

**Ending Cutscene**: The sky brightens. The Crow People transform — their black forms shift to white, becoming colorful birds. A glowing white crown descends from above. Ida looks at her hands, recognizing herself. She accepts the crown with open arms. She transforms into a white bird and flies away with the other birds — Princess Ida has been redeemed and restored as the true Princess of the Crow People. Sacred Geometry has been returned to the valley. The monuments stand forever.

**Puzzle Elements**: Full-cube rotation, 3 sub-level rotators, 3 colored beacons, draggers, 2–3 crows, wall-walking, impossible paths.

---

## 11. Forgotten Shores Expansion (Appendices i through viii)

> Released November 12, 2014. Eight new chapters set between Chapter IX: The Descent and Chapter X: Observatory in the narrative timeline. Introduces new mechanics including water level controls, twisting geometry, and the Totem's narrative arc.

### Appendix i: The Chasm

| Property | Value |
|----------|-------|
| Subtitle | "The Chasm" |
| Theme | Descent into an unstable chasm; Totem reunion |
| Color palette | Warm oranges, volcanic reds, dark stone |
| Key mechanic | Collapsing and rotating monument fragments; lava/rising hazard; Totem reappearance |
| Sacred Geometry returned | Yes |
| Totem presence | Yes — Totem rescues Ida from rising lava |
| Estimated duration | 10–15 minutes |

**Level Description**: Ida descends into a deep chasm where monument fragments rotate and collapse around her. Pieces of ancient structures tumble and lock into new positions, alternately blocking and creating paths. At the lowest point, the platform Ida stands on begins sinking into glowing lava. In a dramatic moment, the Totem rises from the lava, offering its head as a stepping stone. The player slides the Totem upward, with Ida riding on top, climbing out of the lava pit. Later sections involve rotating stone totem poles (not the Totem character) so the Totem can climb them like steps. The level establishes the Totem's loyalty and courage.

**Puzzle Elements**: Totem dragger, rotating stone fragments, pressure plates, lava rising trigger.

---

### Appendix ii: The Serpent Lake

| Property | Value |
|----------|-------|
| Subtitle | "The Serpent Lake" |
| Theme | Water reflections; twisting architecture |
| Color palette | Teal, dark blue-green water, silver architecture |
| Key mechanic | **Twisting mechanic** (unique to this level) — gear-driven rotation of tower sections relative to each other; water reflection walking |
| Sacred Geometry returned | Yes |
| Totem presence | No |
| Estimated duration | 10–12 minutes |

**Level Description**: A tower sits above a still lake. The level's signature mechanic is a twisting gear that rotates individual sections of the tower independently, spiraling stairways into new configurations. The player turns the gear to twist the building, creating paths between formerly disconnected sections. Switches trigger spiral columns to rearrange. The culminating puzzle: Ida walks onto the tower's reflection in the water — a direct visual metaphor. The reflection functions as a valid walkable surface, and Ida completes the level by navigating the mirror image of the structure to reach the exit.

**Puzzle Elements**: Twisting gears (unique mechanic), 3 switches, water reflection path, spiral columns.

---

### Appendix iii: The Thief

| Property | Value |
|----------|-------|
| Subtitle | "The Thief" |
| Theme | Ida's hat is stolen; pursuit and recovery |
| Color palette | Muted purples, lavender, dark gray crows |
| Key mechanic | Ida loses her hat to a Crow; must navigate without it and recover it; using crows and levers cooperatively |
| Sacred Geometry returned | Yes (only after hat recovery) |
| Totem presence | No |
| Estimated duration | 8–12 minutes |

**Level Description**: A Crow Person steals Ida's distinctive white hat at the beginning of the level. Ida appears bareheaded for the first and only time. The level's puzzles involve manipulating levers to guide the thieving crow through the environment. The player turns a lever to reveal the crow's position, then strategically uses switches and geometry to trap the crow on specific platforms. At one point, the player must step off a switch when the crow is directly over a target area to lock it in place. The level is a commentary on Ida's own history as a thief (of Sacred Geometry), reflected in a crow stealing from her. Ida recovers her hat before the final pedestal.

**Puzzle Elements**: Lever rotators, pressure plates, crow-trapping sequences, 3 buttons.

---

### Appendix iv: Halcyon Court

| Property | Value |
|----------|-------|
| Subtitle | "Halcyon Court" |
| Theme | Water level control; Storyteller continuation |
| Color palette | Pastel blues, soft whites, warm gold sunlight |
| Key mechanic | **Water level control** — levers that raise and lower the water, flooding or draining sections to open/block paths |
| Sacred Geometry returned | Yes |
| Totem presence | No |
| Storyteller | Appears with additional lore about Ida's eventual reward |
| Estimated duration | 10–15 minutes |

**Level Description**: A beautiful court of white and gold structures above a pool of water. The player controls the water level via a set of levers. Raising the water floods lower paths but creates new connections at higher levels; lowering it reveals submerged stairs and platforms. The core puzzle loop involves: rotating a crank to flow water in one direction, moving Ida to a switch, pushing levers to change the water level, then using newly revealed paths to progress. A multi-step sequence requires raising the water two increments, pressing a button, then raising it fully. The Storyteller appears to explain what awaits Ida upon completion of her quest.

**Puzzle Elements**: Water level levers (3 positions: low, mid, high), 4 buttons, 1 crank/rotator, door transitions.

---

### Appendix v: The Lost Falls

| Property | Value |
|----------|-------|
| Subtitle | "The Lost Falls" |
| Theme | Waterfalls; the Totem's sacrifice |
| Color palette | Lush greens, white waterfalls, gray stone |
| Key mechanic | Crusher trap; Totem destruction sequence |
| Sacred Geometry returned | Yes |
| Totem presence | Yes — **destroyed in this level** |
| Estimated duration | 12–15 minutes |

**Level Description**: A verdant landscape with cascading waterfalls. Ida and the Totem traverse platforms together. The level builds tension toward its climax: a massive crusher mechanism blocks the only exit. The Totem positions itself beneath the crusher to hold it open so Ida can pass. But the crusher is too powerful — it slams down repeatedly on the Totem's head. With each impact, the Totem cracks. After several strikes, the Totem shatters into its 4 individual blocks, which tumble into the chasm below. Ida watches helplessly. The level continues with Ida alone, completing the final puzzle to reach the Sacred Geometry pedestal. This is the most emotionally impactful moment in the game.

**Puzzle Elements**: Totem cooperation puzzles, crusher mechanism, waterfall traversal, 3 buttons, final solo section.

---

### Appendix vi: The Citadel of Deceit

| Property | Value |
|----------|-------|
| Subtitle | "The Citadel of Deceit" |
| Theme | Grief; optical illusions at their most extreme |
| Color palette | Desaturated grays, monochrome stone; transitions to pink sunrise at ending |
| Key mechanic | Heavy impossible geometry; perspective deception; emotional atmosphere |
| Sacred Geometry returned | Yes |
| Totem presence | No (Totem destroyed in previous level) |
| Estimated duration | 10–12 minutes |

**Level Description**: Following the Totem's destruction, Ida traverses a world drained of color. The architecture is gray and warped — heavy use of impossible connections and perspective tricks. The level represents Ida's internal grief and self-deception. Walkways connect in visually confusing ways; the player must rely heavily on tapping to discover which paths are actually valid. Sliding middle walkways and passing through doors leads to disorienting shifts in perspective. At the level's conclusion, the gray sky transitions to a soft pink sunrise — a symbol of acceptance and the beginning of healing. Sacred Geometry is returned in a more subdued ceremony.

**Puzzle Elements**: Multiple draggers, doors with perspective shifts, heavy impossible geometry, emotional pacing.

---

### Appendix vii: The Oubliette

| Property | Value |
|----------|-------|
| Subtitle | "The Oubliette" |
| Theme | Imprisonment; drawers return; dark underground |
| Color palette | Dark purple, stone gray, dim warm light from below |
| Key mechanic | Drawers (pull-out platforms) — second of only two levels to use them; circular pool rotation |
| Sacred Geometry returned | Yes |
| Totem presence | No |
| Estimated duration | 8–12 minutes |

**Level Description**: An oubliette — a dungeon with no exit except from above. Ida must escape by ascending from the bottom of a deep, dark chamber. The level features drawers (pull-out platforms from walls) that create stepping stones upward. A circular pool in the center acts as a rotating platform — Ida walks onto it and it spins her to face a different door on each rotation. The player must combine drawer extensions, button presses, and rotations to create a path from the bottom of the prison to the exit at the top. The level's compact, claustrophobic design contrasts with the open spaces of most chapters.

**Puzzle Elements**: 3 drawers, rotating central pool, 4 buttons, view-rotation for hidden buttons.

---

### Appendix viii: Nocturne

| Property | Value |
|----------|-------|
| Subtitle | "Nocturne" |
| Theme | Night; searching for the Totem's pieces; reunion |
| Color palette | Deep midnight blue, warm yellow/gold lights, starry sky |
| Key mechanic | Collecting 4 Totem pieces scattered across the level; reassembly |
| Sacred Geometry returned | Yes |
| Totem presence | Yes — restored at level's end |
| Estimated duration | 15–20 minutes |

**Level Description**: The final Forgotten Shores level takes place under a starlit night sky. The level is structured as a search — the Totem's 4 blocks are scattered across different sections of the environment, each locked behind its own puzzle. The player must solve 4 mini-puzzles to retrieve each piece. Mechanics from throughout the game appear in condensed form: rotators, draggers, buttons, impossible paths. Once all 4 pieces are collected, Ida brings them to a central pedestal of light. The pieces float upward and reassemble themselves — the Totem's eye opens, blinks, and looks at Ida. A grand staircase appears. At the top, the platform gives way to reveal the fully restored Totem standing tall. The reunion is wordless but deeply emotional. Sacred Geometry is returned. The Forgotten Shores storyline is complete.

**Puzzle Elements**: 4 mini-puzzles (one per Totem piece), rotators, draggers, buttons, impossible paths, assembly pedestal.

---

## 12. Ida's (RED) Dream Expansion

> Released June 25, 2015 as a charity fundraiser. Later included free with the base game.

| Property | Value |
|----------|-------|
| Structure | Hub world (windmill) with 5 doors leading to 5 sub-levels |
| Theme | Dream-like; surreal; elevated difficulty |
| Color palette | Deep reds, warm pinks, and the dreamlike glow of sunset tones |
| Unique mechanic | Wall-climbing system (final sub-level); non-linear level selection |
| Sacred Geometry returned | Yes (upon completing all 5 sub-levels) |
| Estimated duration | 30–45 minutes |
| Difficulty | Higher than main game and Forgotten Shores |

**Level Description**: Ida enters a windmill hub structure with 5 doors. Each door leads to a compact but challenging puzzle room. The player can complete the rooms in any order. Early rooms revisit and combine established mechanics (rotators + crows, draggers + buttons, impossible geometry + wall-walking). The final room introduces a wall-climbing system that allows Ida to move between surfaces in new ways, adding a unique variable. Upon completing all 5 rooms, the windmill hub reconfigures for a final ascent to the Sacred Geometry pedestal.

---

## 13. Visual & Perspective System

### Isometric Projection Details

| Property | Value |
|----------|-------|
| Projection type | Orthographic (no perspective foreshortening) |
| Camera angle | ~30 degrees from horizontal (true isometric is 30 degrees for both axes) |
| Camera rotation | Fixed — never rotates during gameplay |
| Zoom | Fixed — no player-controlled zoom |
| Pan | Minimal automatic pan to follow Ida between sections; no player-controlled pan |
| Why orthographic | Perspective projection would break impossible geometry illusions (parallel lines must remain parallel) |

### How Visual Alignment Creates Paths

The following rules govern when two walkable surfaces are treated as connected:

1. **Visual edge overlap**: If two walkable surface edges overlap within a tolerance of approximately 2 screen pixels when rendered through the orthographic camera, they are connected.
2. **Real-time evaluation**: Connections are re-evaluated every time any geometry moves (rotate, slide, drawer extend).
3. **No animation glitch**: When Ida crosses an impossible connection, her walking animation transitions smoothly — there is no visible jump or teleport.
4. **Priority system**: If Ida is standing on one of two overlapping surfaces, that surface takes navigation priority.
5. **Stair alignment**: Stairs at the edge of a platform connect to any surface that visually aligns with the stair's top or bottom step.

### Perspective Illusion Catalog

| Illusion | Visual Description | Mechanical Effect |
|----------|--------------------|-------------------|
| Penrose Triangle | Three connected ramps form a closed triangle that appears to ascend perpetually | Walking around the triangle brings Ida back to her starting height |
| Penrose Stairs | A looping staircase that appears to always go up (or down) | Ida walks in a loop; rotating a connected element changes which floor the loop exits to |
| False bridge | Two disconnected surfaces at different depths appear to touch | Rotating geometry brings them to the same depth, creating a real connection |
| Wall-floor transition | A horizontal surface and a vertical surface share an edge at a corner | Ida transitions from walking horizontally to walking vertically (or vice versa) |
| Depth ambiguity | A single edge could be the front face of one block or the back face of another | Rotating connected geometry resolves the ambiguity, choosing one interpretation |
| Reflection path | A structure's reflection in water appears as a valid walkable surface | Ida walks on the reflection as though it were solid ground |

---

## 14. Narrative System

### Story Structure

Monument Valley tells its story with extreme minimalism — no cutscenes (except the ending), no dialogue trees, and only one speaking character (the Storyteller). The narrative is conveyed through:

| Channel | Method |
|---------|--------|
| Environmental storytelling | Architecture, color, weather, and atmosphere convey mood and history |
| Storyteller dialogue | Brief text bubbles at fixed story points (see Section 9) |
| Ida's actions | Placing Sacred Geometry, picking up the flower, losing her hat — all wordless |
| Totem's emotions | Eye movement, blinking, and body language (sacrifice scene) |
| Crow People transformation | The ending reveals crows' true nature through visual metamorphosis |
| Level names | Titles like "The Descent," "The Thief," and "Nocturne" carry thematic weight |
| Color transitions | Shifts from gray to pink (Appendix vi) or dark to dawn (Appendix viii) convey emotional arcs |

### Complete Narrative Summary

1. **Ida's Crime**: In the distant past, Princess Ida stole Sacred Geometry from the valley's human civilization. This act killed the humans and cursed Ida's own people (the Crow People) to wander the monuments as dark, mindless birds.
2. **The Quest Begins (Ch. I–IV)**: Ida silently returns to the valley. She begins returning Sacred Geometry to the monuments. The Storyteller confronts her: "Thieving princess, why have you returned?"
3. **Obstacles (Ch. V–VII)**: The cursed Crow People block Ida's path. She must navigate around or work with them. The Totem joins her as an ally (Ch. VI).
4. **The Box (Ch. VIII)**: Ida navigates the most complex monument, proving her mastery of the valley's geometry.
5. **Remembrance (Ch. IX)**: Ida descends to an underground graveyard during a storm. She places a red flower on a grave. The Storyteller tells her that returning all geometry will restore her crown.
6. **Forgotten Shores Arc**: Ida and the Totem continue their journey. The Totem sacrifices itself (Appendix v). Ida grieves (Appendix vi) and eventually restores the Totem by finding its scattered pieces (Appendix viii).
7. **The Redemption (Ch. X)**: Ida returns the final piece of Sacred Geometry. The Crow People are freed from their curse and transform into colorful birds. A crown descends from the sky. Ida accepts it and transforms into a white bird, flying away as the redeemed Princess of the Crow People.

### Emotional Beats

| Chapter | Emotion | Mechanism |
|---------|---------|-----------|
| I | Wonder, curiosity | First view of impossible architecture |
| IV | Surprise, delight | First wall-walking moment |
| V | Tension, satisfaction | First crow-timing challenge |
| VI | Warmth, companionship | Meeting the Totem |
| VIII | Awe, confusion | The unfolding box |
| IX | Melancholy, reverence | Storm, graveyard, flower |
| Appendix v | Shock, sadness | Totem's destruction |
| Appendix vi | Grief, numbness | Desaturated world |
| Appendix viii | Hope, joy | Totem's restoration |
| X (ending) | Catharsis, transcendence | Crown, transformation, flight |

---

## 15. UI Layout

### Main Menu

| Element | Position | Description |
|---------|----------|-------------|
| Title logo | Upper center | "MONUMENT VALLEY" in Museo slab-serif typeface; white text |
| Start/Continue button | Center | Large tap target; shows chapter select if save exists |
| Settings icon | Top-right corner | Gear icon; opens audio/settings panel |
| Background | Full screen | Animated isometric structure with subtle movement |

### Chapter Select Screen

| Element | Position | Description |
|---------|----------|-------------|
| Chapter grid | Centered, scrollable vertically | Each chapter shown as an icon of its Sacred Geometry piece (or red flower for Ch. IX) |
| Chapter number | Below icon | Roman numeral (I, II, III, etc.) |
| Chapter name | Below number | Subtitle text (e.g., "The Garden") |
| Lock state | Overlay on icon | Locked chapters show a lock icon; chapters unlock sequentially |
| Completion state | Checkmark overlay | Completed chapters show a faint checkmark |
| Forgotten Shores section | Below main chapters | Separated header: "FORGOTTEN SHORES"; same icon grid layout |
| Ida's Dream section | Below Forgotten Shores | Separated header: "IDA'S DREAM" |

### In-Game HUD

Monument Valley has an **extremely minimal HUD**. The design philosophy is that the game world IS the interface.

| Element | Visibility | Description |
|---------|------------|-------------|
| Pause button | Top-left corner | Small square icon; translucent; tapping pauses and shows menu |
| Level name | Shown briefly at start | Chapter number and name fade in at level start, then fade out after ~3 seconds |
| Dialogue text | Triggered by Storyteller proximity | Text bubble appears near the Storyteller; white text on semi-transparent dark background; fades after ~5 seconds or on tap |
| No health bar | N/A | There is no health, lives, or damage system |
| No score | N/A | There is no scoring system |
| No timer | N/A | There is no time limit |
| No hint system | N/A | There are no hints, tips, or help buttons during gameplay |
| No inventory | N/A | Items (flower) are carried automatically; no inventory screen |

### Pause Menu

| Element | Description |
|---------|-------------|
| Resume button | Returns to gameplay |
| Restart level button | Resets current chapter to beginning |
| Return to map button | Returns to chapter select |
| Sound toggle | On/off for music |
| Sound effects toggle | On/off for sound effects |

### Transition Screens

| Transition | Animation |
|------------|-----------|
| Level start | Camera fades in from black; level name fades in then out |
| Level complete | Sacred Geometry piece rises from Ida's hat; floats to pedestal; geometry glows; screen fades to white |
| Chapter end card | White screen with chapter number, name, and Sacred Geometry icon; "Continue" tap target |
| Between sections | Camera smoothly pans to new area; brief fade-through-black for door transitions |

---

## 16. Audio Design

### Composers & Sound Designer

| Role | Person(s) |
|------|-----------|
| Sound design | Stafford Bawler |
| Music composition | Stafford Bawler, Obfusc, Grigori |
| Audio middleware | Fabric plugin for Unity |
| Soundtrack release | July 1, 2014 — 16 tracks, ~40 minutes total |

### Music Characteristics

| Property | Value |
|----------|-------|
| Genre | Ambient, minimalist, electronic with organic textures |
| Tempo | Slow to moderate (60–90 BPM typical) |
| Key instruments | Synthesizers, piano, strings (often solo cello or violin), choir/vocal pads, field recordings |
| Dynamic music | Music responds subtly to gameplay state; intensity shifts when puzzles are near completion |
| Looping | Tracks loop seamlessly with long crossfade durations |
| Per-chapter theming | Each chapter has a unique musical identity; palette shifts match visual color palette shifts |

### Sound Effects

| Sound | Trigger | Description |
|-------|---------|-------------|
| Footsteps | Ida walking | Soft, rhythmic tapping; varies by surface type |
| Stone rotation | Rotator being dragged | Low grinding/scraping; pitch varies with rotation speed |
| Stone sliding | Dragger being dragged | Smooth sliding sound; heavier than rotation |
| Stone snap | Rotator reaching snap position | Brief click/thud |
| Button press | Entity steps on button | Soft click with a subtle harmonic tone (musical note) |
| Button release | Entity leaves pressure plate | Softer reverse click |
| Bridge extend | Button triggers bridge | Mechanical sliding sound |
| Drawer extend | Drawer pulled out | Stone sliding from wall |
| Door open | Ida enters door | Soft whoosh; resonant echo |
| Crow squawk | Crow blocks Ida or patrols | Sharp, short bird-like caw |
| Water ambient | Levels with water | Continuous gentle lapping/flowing |
| Wind ambient | Exterior levels | Subtle wind movement |
| Rain | Chapter IX opening | Rainfall with distant thunder |
| Chanting | Chapter IX underground | Gregorian-style male choir |
| Totem slide | Totem moved via dragger | Heavy stone sliding with a lower pitch than standard draggers |
| Totem impact | Crusher strikes Totem (Appendix v) | Deep, resonant thud; increasing desperation |
| Totem destruction | Totem shatters | Stone cracking/shattering; pieces falling |
| Sacred Geometry collection | Level completion | Rising harmonic chord; crystalline chime |
| Crown descent | Final ending (Ch. X) | Celestial choir swell; bright harmonic resolution |
| Bird transformation | Ending (Ch. X) | Fluttering wings; ascending melodic phrase |

### Interactive Audio Details

| Feature | Description |
|---------|-------------|
| Musical button notes | Each button press produces a specific musical note. In levels with multiple buttons, pressing them in sequence can create a simple melody. |
| Rotation audio pitch | The pitch of stone rotation sounds varies with the speed and angle of the player's drag gesture. |
| Environmental audio layers | Each level has multiple ambient audio layers (wind, water, birds, distant sounds) that crossfade based on Ida's position in the level. |
| Silence as design | Some transitions use deliberate silence (no music) for emotional impact, particularly in Chapter IX. |

---

## 17. Art Direction

### Visual Philosophy

Monument Valley aspires to make **every screen a work of art**. The developers' stated goal was that any screenshot could be framed and hung on a wall. This drives every art decision:

| Principle | Implementation |
|-----------|---------------|
| Minimalism | No textures on architecture; flat-shaded polygons with clean edges |
| Geometric purity | All structures built from simple geometric primitives (cubes, cylinders, triangles) |
| Deliberate detail | Detail is added only to draw attention to interactive elements or story points |
| Color as storytelling | Warm colors indicate comfort/progress; cool colors indicate mystery/danger; desaturation indicates grief |
| Negative space | Sky and water fill large portions of the screen; architecture is often small and centered |

### Inspirations

| Source | Influence |
|--------|-----------|
| M.C. Escher | Impossible architecture, perspective paradoxes, recursive spaces |
| Oscar Reutersvard | Impossible objects (Penrose triangle originator) |
| Japanese woodblock prints | Flat color fields, strong outlines, compositional balance |
| Minimalist sculpture | Clean geometric forms, material simplicity |
| Fez (Polytron, 2012) | Isometric perspective manipulation |
| Windosill (Vectorpark, 2009) | Tactile interaction, whimsical world |
| Superbrothers: Sword & Sworcery EP (2011) | Pixel-minimalist aesthetic, atmospheric storytelling |

### Color Palette by Chapter

| Chapter | Primary Colors | Mood |
|---------|---------------|------|
| I: Monument Valley | Beige, peach, soft orange | Warm welcome |
| II: The Garden | Green, pink, cream | Natural, fresh |
| III: Hidden Temple | Terracotta, sandstone, red | Ancient, warm |
| IV: Water Palace | Pink, rose, coral, blue-green water | Elegant, surprising |
| V: The Spire | Cool blue, slate gray, white | Tense, vertical |
| VI: The Labyrinth | Deep blue, teal, gold | Mysterious, subterranean |
| VII: The Rookery | Amber, brown, red, golden light | Warm but complex |
| VIII: The Box | Multi-colored (orange, green, blue, purple per section) | Vibrant, varied |
| IX: The Descent | Dark blue, charcoal, deep purple → warm gold underground | Somber → sacred |
| X: Observatory | Multi-sectioned; white/gold finale | Climactic, transcendent |
| App. i: The Chasm | Volcanic red, orange, dark stone | Dangerous, intense |
| App. ii: Serpent Lake | Teal, silver, dark blue-green | Mysterious, reflective |
| App. iii: The Thief | Muted purple, lavender, gray | Subdued, personal |
| App. iv: Halcyon Court | Pastel blue, white, warm gold | Serene, elevated |
| App. v: Lost Falls | Lush green, white waterfalls, gray | Verdant → tragic |
| App. vi: Citadel of Deceit | Desaturated gray → pink sunrise | Grief → acceptance |
| App. vii: The Oubliette | Dark purple, stone gray, dim gold | Claustrophobic, heavy |
| App. viii: Nocturne | Midnight blue, warm gold lights, starry sky | Hopeful, nocturnal |

### Color Design Rules

| Rule | Detail |
|------|--------|
| Saturation limit | Heavily saturated, dark hues are never used. The palette stays in light, medium, or desaturated ranges. |
| Interactive element color | Warm colors (often distinct from background) highlight interactive elements like buttons and handles |
| Color continuity | The entire game was printed out and arranged as a color script on a wall; adjustments were made to ensure smooth transitions |
| Per-level identity | No two chapters share the same primary color palette |
| Crow color | Always solid black — maximum contrast against pastel environments |
| Ida color | Always white — maximum visibility in any environment |
| Totem color | Always yellow/gold with turquoise — warm and distinct from architecture |

### Typography

| Usage | Font | Weight | Notes |
|-------|------|--------|-------|
| Body text / UI | Museo | 300–500 | OpenType slab-serif; first notable mobile game use of this web-popular font |
| Logo / title | Custom (based on Anisette Std Petite Light or similar) | Light | Thin, elegant, geometric |
| Dialogue text | Museo | 300 | White text on semi-transparent dark background |
| Chapter titles | Museo | 500 | Displayed at level start; clean and readable |

### Character Design

| Character | Design Philosophy |
|-----------|-------------------|
| Princess Ida | Abstracted to essentials: white triangular hat, small body, minimal limbs. No face detail. Universally relatable through simplicity. |
| Crow People | Black silhouettes with a single prominent beak. No eyes visible. Represent cursed, mindless wandering. |
| The Totem | Geometric block tower with a single expressive eye. Personality conveyed entirely through eye movement and body orientation. |
| The Storyteller | Translucent, ghostly. Form is suggestive rather than detailed. Represents the past. |

### Animation Principles

| Property | Value |
|----------|-------|
| Style | Smooth, gentle, deliberate — no sudden movements |
| Frame rate | 60 FPS target; animations interpolated |
| Ida walk cycle | 4-frame bob cycle at ~5 steps/second; arms swing subtly |
| Ida idle | Gentle breathing; looks around after ~5 seconds |
| Crow walk | Distinctive bob/waddle; faster tempo than Ida |
| Crow squawk | Head tilts back; beak opens; brief wing flap |
| Totem eye | Blinks every ~4 seconds; pupil tracks Ida's position; squints during concern |
| Water | Subtle sine-wave displacement on water surface; reflection ripples |
| Flags/banners | Gentle wave animation driven by simulated wind |
| Particles | Occasional floating dust motes in interior levels; rain in Ch. IX |
| Geometry rotation | Smooth interpolation; approximately 0.5 seconds for a 90-degree snap rotation |
| Geometry sliding | Continuous tracking of drag gesture; snaps to grid when released |

---

## 18. Sacred Geometry Collectibles

### Overview

Sacred Geometry is the core narrative MacGuffin. Each level (except Chapter I and Chapter IX) ends with Ida returning a piece of Sacred Geometry to its monument. The pieces are abstract geometric shapes that glow and float.

### Collection Ritual

1. Ida reaches the level's final pedestal/altar.
2. Ida removes her hat.
3. A glowing geometric shape rises from inside the hat.
4. The shape floats to the pedestal and locks into place.
5. The pedestal glows; ambient light increases.
6. A harmonic chord plays.
7. The screen fades to the chapter completion card.

### Geometry Shapes by Chapter

| Chapter | Sacred Geometry Shape | Color |
|---------|----------------------|-------|
| I: Monument Valley | None (tutorial) | N/A |
| II: The Garden | Octahedron (double pyramid) | Green-gold |
| III: Hidden Temple | Cube | Red-gold |
| IV: Water Palace | Triangular prism | Pink-gold |
| V: The Spire | Star tetrahedron | Blue-silver |
| VI: The Labyrinth | Icosahedron | Teal-gold |
| VII: The Rookery | Dodecahedron | Amber-gold |
| VIII: The Box | Nested cubes | Multi-colored |
| IX: The Descent | Red flower (not geometry) | Red |
| X: Observatory | Complex polyhedron (final piece) | White-gold |

### Level Select Icons

Each completed level displays its Sacred Geometry shape as a small icon on the chapter select screen. Incomplete levels show a lock. Chapter IX shows the red flower icon instead of geometry.

---

*End of Specification*

> This specification covers all systems, mechanics, levels, characters, and design details necessary to faithfully recreate Monument Valley (2014) including the Forgotten Shores and Ida's (RED) Dream expansions. Implementation should prioritize the orthographic impossible-geometry engine and the navigation node system, as these are the technical foundation upon which all puzzles are built.
