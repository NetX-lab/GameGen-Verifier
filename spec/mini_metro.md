# Mini Metro -- Complete Game Specification

> A comprehensive specification for faithfully recreating Mini Metro (Dinosaur Polo Club, 2015 minimalist subway planning game). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics](#3-core-mechanics)
4. [Station System](#4-station-system)
5. [Passenger System](#5-passenger-system)
6. [Train System](#6-train-system)
7. [Line Management](#7-line-management)
8. [Weekly Upgrade System](#8-weekly-upgrade-system)
9. [Overcrowding and Game Over](#9-overcrowding-and-game-over)
10. [River and Tunnel System](#10-river-and-tunnel-system)
11. [City Maps](#11-city-maps)
12. [Scoring System](#12-scoring-system)
13. [Game Modes](#13-game-modes)
14. [UI Layout](#14-ui-layout)
15. [Audio Design](#15-audio-design)
16. [Achievements and Unlocks](#16-achievements-and-unlocks)

---

## 1. Game Overview

- **Title**: Mini Metro
- **Developer**: Dinosaur Polo Club (Peter Curry, Robert Curry; artist Jamie Churchman; composer Rich Vreeland / Disasterpeace)
- **Genre**: Minimalist puzzle / strategy / transit simulation
- **Perspective**: Top-down 2D, abstract geographic map
- **Engine**: Unity
- **Original Release**: 6 November 2015 (Steam, Windows / macOS / Linux)
- **Other Platforms**: iOS & Android (18 October 2016), Nintendo Switch (30 August 2018), PlayStation 4 (10 September 2019)
- **Origin**: Ludum Dare 26 game jam entry "Mind the Gap" (April 2013); entered Steam Early Access August 2014
- **Input**: Mouse (click and drag) on PC; touch (tap and drag) on mobile; keyboard shortcuts for time controls
- **Objective**: Design an efficient metro network to transport passengers between stations. The score equals the total number of passengers successfully delivered before the system fails.
- **Lose Condition (Normal/Extreme)**: A station remains at maximum passenger capacity for 45 seconds (plus a 2-second hidden grace period), with no train arriving to service it.
- **Core Loop**: Stations appear on the map over time. Passengers spawn at stations, each wanting to reach a station of a specific shape. The player draws metro lines connecting stations, and trains automatically travel along lines picking up and dropping off passengers. Each in-game week the player receives upgrades. As passenger volume grows, the network must be continually expanded and optimised.

---

## 2. Technical Foundation

### Resolution and Display

| Property | Value |
|----------|-------|
| Rendering | Vector-based / resolution-independent |
| Target frame rate | 60 FPS |
| Display mode | Windowed or fullscreen (PC); native (mobile/console) |
| Art style | Minimalist, flat colour, inspired by Harry Beck's London Underground map |
| Background | Solid colour (varies by city map theme) |

### Time System

| Property | Value |
|----------|-------|
| In-game day duration (real time) | ~20 seconds at 1x speed |
| In-game 12-hour period | ~10 seconds at 1x speed |
| In-game week duration (real time) | ~2 minutes 20 seconds at 1x speed |
| Day tick | Midnight (00:00) |
| Day indicator | Clock icon -- white face 6 AM to 6 PM (day), dark face 6 PM to 6 AM (night) |
| Budget increase trigger | End of Sunday each week |
| Speed multipliers | 1x (normal), 2x (fast), 3x (fastest), 0x (paused) |

### Controls (PC)

| Input | Action |
|-------|--------|
| Left-click + drag from station | Create a new line or extend an existing line |
| Left-click + drag line segment | Reroute a line by dragging the path |
| Left-click + drag train icon | Move a train/carriage between lines |
| Spacebar | Toggle pause / play |
| 1 / 2 / 3 | Set speed: pause / normal / fast |
| Left / Right arrow | Decrease / increase speed |
| Up / Down arrow | Show / hide / lock the bottom line menu |
| Enter | Confirm default button (menus) |
| Escape | Back to previous screen |

### Controls (Touch)

| Input | Action |
|-------|--------|
| Tap + drag from station | Create or extend a line |
| Tap + drag existing line | Reroute segments |
| Tap + drag train/carriage | Reassign between lines |
| Tap UI buttons | Pause, speed, menu navigation |

### Game Loop (per frame)

```
1. Process input (mouse/touch: line drawing, rerouting, asset moves)
2. Advance simulation clock by delta * speed_multiplier
3. Check for new station spawns
4. Generate passengers at existing stations
5. Update passenger pathfinding (A* route evaluation)
6. Update all trains:
   a. Move along line path (acceleration, cruising, deceleration)
   b. Stop at stations: alight matching passengers, board waiting passengers
7. Update overcrowding timers for all stations
8. Check game-over condition (any station timer expired)
9. Award weekly budget increase if end-of-week reached
10. Render: background -> water -> line paths -> stations -> passengers -> trains -> UI overlay
```

---

## 3. Core Mechanics

### Line Drawing

- The player creates metro lines by clicking/tapping on a station and dragging to another station, forming a connected route.
- A line is a sequence of connected stations. Trains travel back and forth along the entire line (point-to-point) or around it (loop).
- Lines are drawn as smooth, gently curving paths between stations, following the minimalist style with 45-degree and 90-degree angles preferred.
- A line must contain at least two stations.
- Up to 3 lines can share a straight path segment between two adjacent stations.
- Up to 6 lines can share a path segment that includes an angle.

### Line Types

| Type | Description |
|------|-------------|
| Point-to-point | Train travels from one terminus to the other, then reverses. Stations at the ends are serviced less frequently. |
| Loop | The last station connects back to the first. Train travels continuously around the loop. All stations serviced with equal frequency per pass. |

### Line Extension and Modification

- **Extend**: Drag from an endpoint station of an existing line to a new station to add it to that line.
- **Insert**: Drag a line segment to pass through an intermediate station.
- **Remove station**: Drag a station off the line path to disconnect it.
- **Reroute**: Drag any segment of a line to change its path between stations.
- **Delete line**: Remove all stations from a line to free it up.
- All line modifications can be performed while the game is paused.
- In Extreme mode, lines and assets cannot be modified or moved once placed.

### Line Limits

| Property | Value |
|----------|-------|
| Starting lines | 3 |
| Maximum lines | 7 (map-dependent; some maps cap lower) |
| Maximum trains per line | 11 minus total line count (varies; typically 4 per line) |
| Stations per line | No hard limit, but performance degrades with many stations |

---

## 4. Station System

### Station Types

Stations are represented as geometric shapes. Each shape defines both the visual identity of the station and the destination type that matching passengers seek.

| Station Type | Shape | Frequency Category | Spawn Probability (approx.) | Max per Map |
|-------------|-------|-------------------|---------------------------|-------------|
| Circle | Circle (O) | Common | ~50% of all stations | Unlimited |
| Triangle | Triangle (^) | Common | ~25% of all stations | Unlimited |
| Square | Square ([]) | Semi-common | ~12.5% of all stations | Unlimited |
| Pentagon | Pentagon | Unique/Special | Rare | 1 |
| Diamond | Diamond | Unique/Special | Rare | 1 |
| Star | Star | Unique/Special | Rare | 1 |
| Cross | Cross (+) | Unique/Special | Rare | 1 |
| Wedge | Wedge (semicircle) | Unique/Special | Rare | 1 |
| Gem | Gem (hexagonal) | Unique/Special | Rare | 1 |
| Egg | Egg (oval) | Unique/Special | Rare | 1 |

### Station Frequency Distribution

- **Circles** compose approximately half of all stations on a map.
- **Triangles** compose approximately one quarter.
- **Squares** compose approximately one eighth (half the triangle count).
- **Special/unique shapes** compose the remaining fraction. The first special station (e.g., Star) typically appears as approximately the 15th station, and from that point special stations appear at a rate approaching 20% of subsequent stations.
- Each special shape appears at most once per map, making those stations critical bottleneck destinations.

### Station Properties

| Property | Regular Station | Interchange Station |
|----------|----------------|-------------------|
| Passenger capacity (before overcrowding) | 6 | 18 |
| Overcrowding timer duration | 45 seconds (+ 2s hidden grace) | 45 seconds (+ 2s hidden grace) |
| Passenger boarding/alighting speed | Normal | Significantly faster |
| Removable | N/A (stations cannot be removed) | N/A |
| Upgrade reversible | N/A | No -- interchange upgrade is permanent |

### Station Spawning

| Property | Value |
|----------|-------|
| Starting stations | 3 (one Circle, one Triangle, one Square) |
| New station spawn rate | Approximately one every 20--30 seconds (real time at 1x) |
| Spawn location | At map edges initially, expanding outward as the game progresses |
| Station type mutation | Circle stations can spontaneously change to any other shape during gameplay |
| Station density | Greater toward the centre of the map, sparser at the suburbs |

---

## 5. Passenger System

### Passenger Representation

- Passengers appear as small geometric shapes next to their origin station.
- The passenger's shape indicates their **destination station type**, not their origin.
- A Circle-shaped passenger wants to travel to any Circle station.
- A Star-shaped passenger wants to travel to the single Star station on the map.

### Passenger Generation

| Property | Value |
|----------|-------|
| Spawn location | At existing stations |
| Spawn rate (early game) | Low; a few passengers per in-game day |
| Spawn rate (late game) | Continuously accelerating; noticeable spike around 1,500--1,800 total passengers delivered |
| Spawn scaling | Controlled by `passengerSpawnScale` parameter (baseline 1.0) |
| Centre vs. edge | Higher passenger concentration at central stations |
| Shape distribution | Passengers want to reach station types different from their origin station |
| Most common demand pairing | Circle <-> Triangle (the two most frequent station types) |

### Passenger Pathfinding

Passengers use an **A* search algorithm** to find optimal routes through the network:

1. **Graph construction**: Each train on each line between two stations creates a directed edge. Multiple trains and lines between the same stations create parallel edges.
2. **Cost evaluation**: Each edge cost consists of:
   - Waiting time for the train to arrive at the origin station (predicted via simulation)
   - Travel time from origin to destination on that edge
   - Penalty costs for: backtracking, transfers, not servicing overcrowded stations
3. **Transfer penalty**: Transfers between lines incur an exaggerated cost penalty, favouring direct connections.
4. **Seat reservation**: Passengers reserve capacity on a train they intend to board (considered for the first two pathfinding iterations, then ignored for computational tractability).
5. **Overcrowding avoidance**: Passengers at overcrowded stations will accept longer routes to exit faster.
6. **No return**: Passengers strongly avoid returning to stations they have already visited.

### Passenger Boarding and Alighting

- When a train arrives at a station, passengers whose destination shape matches that station **alight** (disembark) first.
- Then, waiting passengers who want to board that train (based on their pathfinding route) **board** in order.
- Boarding respects the train's remaining capacity.
- At an Interchange station, boarding and alighting occur at a significantly faster rate.
- A train only stops at a station if: (a) passengers need to alight, OR (b) passengers need to board, OR (c) the station creates a sharp turn (< 90 degrees) in the line path forcing a mandatory stop.

---

## 6. Train System

### Train Types

| Property | Locomotive | Shinkansen | Tram |
|----------|-----------|------------|------|
| Base passenger capacity | 6 | 8 | 4 |
| Speed (internal units) | 360 | 480 | 250 |
| Acceleration | 120 | 180 | 1000 (instant) |
| Deceleration | 300 | 300 | 1000 (instant) |
| Behaviour | Standard; must accelerate to top speed | Express; ~2x locomotive speed; only reaches max speed on long segments | Slower top speed but no acceleration ramp-up |
| Availability | Default on all maps | Osaka (and some custom maps) | Melbourne (and some custom maps) |

### Carriages

| Property | Value |
|----------|-------|
| Capacity per carriage | +6 passengers (matches locomotive default) |
| Attachment | Attaches to a locomotive, increasing its total capacity |
| Multiple carriages | Yes; a single locomotive can have multiple carriages |
| Reassignment | Carriages can be moved between locomotives (except in Extreme mode) |
| Cairo exception | Carriages add +4 capacity (matching Cairo's reduced train capacity) |

### Train Movement

- Trains automatically travel along their assigned line.
- **Point-to-point lines**: Train travels from one terminus to the other, stops at each station along the way, then reverses direction and repeats.
- **Loop lines**: Train travels continuously around the loop, visiting every station in order.
- **Multiple trains on one line**: Additional locomotives can be assigned to a line. On loops, multiple trains should ideally travel in the same direction with even spacing for optimal coverage. On point-to-point lines, trains travel independently back and forth.
- **Sharp turns** (< 90 degrees): Force the train to slow down and stop at the station regardless of passenger demand, creating a performance penalty.
- **Soft turns** (>= 90 degrees): Train passes through without stopping if no passengers need to board or alight.
- **Track distance**: The physical distance between stations on the map determines travel time.

### Train Assignment

- Each line starts with one locomotive.
- Additional locomotives are awarded via weekly budget increases and can be freely assigned to any line.
- Locomotives and carriages can be dragged between lines at any time (except Extreme mode).
- When moved, a train completes its current route and drops off all passengers before transferring to the new line.

---

## 7. Line Management

### Creating a Line

1. Click/tap and hold on any station not yet connected to the line being created.
2. Drag to another station to create a two-station line.
3. The first available line colour is automatically assigned.
4. One locomotive is automatically placed on the new line.

### Extending a Line

1. Click/tap on the circular endpoint handle at either terminus of a line.
2. Drag to a new station to extend the line.
3. Release to confirm the connection.

### Creating a Loop

1. Extend one terminus of a line back to the other terminus station.
2. The line becomes a closed loop.
3. Trains now travel continuously in one direction around the loop.

### Rerouting

1. Click/tap on any segment of an existing line.
2. Drag the segment to pass through a different station or path.
3. Release to confirm the new route.
4. Rerouting is instantaneous; trains continue from their current position along the new path.

### Removing Stations from a Line

- Drag a station off the line, or reroute the line to bypass it.
- If a station is removed from all lines, passengers stranded at that station remain there.

### Deleting a Line

- Remove all stations from the line.
- The line colour, locomotive(s), and carriage(s) return to the available pool.

### Shared Paths

- Multiple lines can share the same physical path between two stations.
- Up to 3 lines can share a straight segment.
- Up to 6 lines can share an angled segment.
- Shared segments are rendered as parallel coloured tracks, visually distinct.

---

## 8. Weekly Upgrade System

### Budget Increase (Normal and Extreme Modes)

At the end of every in-game Sunday, the player receives a **budget increase** consisting of:

1. **One locomotive** (always awarded, automatically added to the player's pool).
2. **One choice between two randomly selected upgrades** from the available pool.

The player must select one of the two offered upgrades; the other is forfeited.

### Budget Increase (Endless Mode)

In Endless mode, budget increases are not awarded on a weekly timer. Instead, they are triggered when **efficiency milestones** are reached. Efficiency is tracked by a circular indicator that fills as passengers are delivered and drains as passengers queue. When the indicator is fully filled (all white), a budget increase is awarded.

### Available Upgrades

| Upgrade | Effect | Quantity per Selection | Notes |
|---------|--------|----------------------|-------|
| **Line** | Unlocks a new metro line (new colour) | 1 line | Maximum 7 lines total (map-dependent) |
| **Locomotive** | Adds a new train to the player's pool | 1 locomotive | Can be assigned to any line |
| **Carriage** | Adds a carriage to the pool; attach to any locomotive | 1 carriage (+6 capacity) | Multiple per locomotive allowed |
| **Crossing (Tunnel/Bridge)** | Allows one line to cross a body of water | 2 crossings (default) | Visual style depends on map (tunnel or bridge) |
| **Interchange** | Upgrades one station to hold 18 passengers with fast transfer | 1 interchange | Permanent; cannot be moved or removed |

### Map-Specific Upgrade Variations

| City | Variation |
|------|-----------|
| **Budapest** | Only 1 tunnel per crossing upgrade (instead of 2) |
| **Cairo** | Trains carry 4 passengers; carriages add +4; 2 carriages per upgrade |
| **Hong Kong** | 2 locomotives per budget increase |
| **Mumbai** | 2 carriages per budget increase; only 1 bridge per crossing upgrade |
| **Osaka** | Choice between 2 regular locomotives OR 1 Shinkansen |
| **Melbourne** | Trams replace locomotives (slower but instant acceleration) |
| **New York** | Lower chance of tunnel offerings |

### Interchange Details

| Property | Value |
|----------|-------|
| Capacity increase | From 6 to 18 passengers |
| Transfer speed | Significantly increased boarding/alighting rate |
| Permanence | Cannot be moved to another station or removed once placed |
| Selection | Player clicks on any existing station to upgrade it |
| Availability | Offered as a possible upgrade choice in weekly budget increases |

---

## 9. Overcrowding and Game Over

### Overcrowding Mechanics (Normal and Extreme Modes)

| Property | Value |
|----------|-------|
| Station passenger capacity | 6 (regular) / 18 (interchange) |
| Overcrowding trigger | When passenger count reaches station capacity |
| Overcrowding timer | 45 seconds of real time (at 1x speed) |
| Hidden grace period | +2 seconds after the visible timer completes |
| Total effective timer | 47 seconds |
| Visual indicator | Circular clock/ring around the station that fills as the timer counts down |
| Timer pause | When a train arrives at the overcrowded station, the timer freezes temporarily |
| Timer reset | Timer resets when the passenger count drops below the capacity threshold |

### Game Over Sequence

1. A station's overcrowding timer fully expires (45s visible + 2s grace).
2. No train arrived to reduce passenger count below capacity during that time.
3. The station "explodes" -- the game-over animation plays.
4. The player's final score (total passengers delivered) is displayed.
5. The player can submit their score to leaderboards (if applicable).

### Timer Freeze on Train Arrival

- When a train arrives at an overcrowded station, the overcrowding timer **pauses**.
- Passengers alight and board during the pause, potentially reducing the count below capacity.
- If the count drops below capacity, the timer resets entirely.
- If the count remains at or above capacity after the train departs, the timer resumes.

### Endless Mode Exception

- In Endless mode, stations **do not overcrowd**. There is no overcrowding timer, and the game cannot end due to overcrowding. Stations may accumulate unlimited passengers (though passengers will still try to leave).

---

## 10. River and Tunnel System

### Water Bodies

- Most city maps feature rivers, harbours, or coastlines that divide the map into separate land regions.
- Lines **cannot** cross water unless the player has an available tunnel (or bridge, depending on the map's visual style).

### Tunnel/Bridge Mechanics

| Property | Value |
|----------|-------|
| Resource name | Crossing (displayed as "Tunnel" or "Bridge" per map theme) |
| Starting crossings | Map-dependent (typically 0--2) |
| Crossings per upgrade | 2 (default; varies by map) |
| Usage rule | Crossing any continuous stretch of water with one line uses 1 crossing |
| Curve handling | A line that curves over water still uses only 1 crossing if it crosses one water body |
| Double crossing | If a line crosses two separate water bodies without touching a station between them, it still uses only 1 crossing |
| Station break | If a line stops at a station between two water crossings, each crossing consumes 1 crossing resource |
| Reuse on removal | Removing a line that crossed water returns the crossing resource to the player's pool |

### Strategic Impact

- Water bodies create natural bottlenecks that force meaningful routing decisions.
- Limited crossing resources mean the player must carefully decide which connections justify a tunnel.
- Some maps (e.g., Berlin with the Spree river, New York with the Hudson and East rivers) make crossing management a central strategic challenge.
- Not all maps have water; some are entirely landlocked.

---

## 11. City Maps

### Map Overview

As of the Miniversary Update (July 2023), Mini Metro features **34 normal maps**, **3 historical maps**, and **1 hidden map**.

### Unlock Progression

| Starting Maps | London, Paris, New York City |
|---------------|------------------------------|
| Unlock method | Completing achievements on existing maps unlocks new maps |
| Daily Challenge | Playing a daily challenge on a locked map unlocks it |
| Extreme mode | Unlocked per map by completing that map's harder (second) achievement |

### Complete City Map List

| # | City | Crossing Style | Unique Feature(s) |
|---|------|---------------|--------------------|
| 1 | London | Tunnel | River Thames bisects the map; starting map |
| 2 | Paris | Tunnel | Seine river; starting map |
| 3 | New York City | Tunnel | Hudson + East rivers; multiple boroughs; lower tunnel offering rate |
| 4 | Berlin | Tunnel | Spree river winds through the map; requires careful tunnel use |
| 5 | Hong Kong | Tunnel | Victoria Harbour; 2 locomotives per budget increase |
| 6 | Osaka | Tunnel | Choice between 2 locomotives or 1 Shinkansen (bullet train); rivers |
| 7 | Tokyo | Tunnel | Complex water features |
| 8 | Melbourne | Bridge | Trams replace trains (slower, no acceleration ramp); Yarra River |
| 9 | Saint Petersburg | Bridge | Neva River delta; many water crossings needed |
| 10 | Montreal | Tunnel | Saint Lawrence River; winter theme |
| 11 | San Francisco | Tunnel | Bay and peninsula geography; constrained layout |
| 12 | Seoul | Tunnel | Han River bisects the map |
| 13 | Shanghai | Tunnel | Huangpu River |
| 14 | Mumbai | Bridge | 2 carriages per upgrade; 1 bridge per crossing upgrade; coastal layout |
| 15 | Cairo | Tunnel | 4-passenger train capacity; 2 carriages per upgrade; Nile River |
| 16 | Singapore | Tunnel | Island geography; coastal constraints |
| 17 | Stockholm | Tunnel | Archipelago layout; many islands |
| 18 | Sao Paulo | Bridge | Sprawling urban layout |
| 19 | Istanbul | Tunnel | Bosphorus strait divides European and Asian sides |
| 20 | Auckland | Bridge | Harbour geography |
| 21 | Santiago | Tunnel | Mapocho River |
| 22 | Guangzhou | Tunnel | Pearl River |
| 23 | Chongqing | Tunnel | Yangtze and Jialing rivers confluence |
| 24 | Budapest | Tunnel | Danube River; only 1 tunnel per crossing upgrade |
| 25 | Addis Ababa | N/A | Landlocked; no water crossings required |
| 26 | Lagos | Bridge | Lagoon and coastal geography |
| 27 | Chicago | Tunnel | Lake Michigan and Chicago River |
| 28 | Boston | Tunnel | Charles River and harbour |
| 29 | Lisbon | Tunnel | Tagus River estuary |
| 30 | Nanjing | Tunnel | Yangtze River |
| 31 | Tashkent | N/A | Landlocked; minimal water features |
| 32 | Warsaw | Tunnel | Vistula River |
| 33 | Barcelona | Tunnel | Mediterranean coast |
| 34 | Washington, D.C. | Tunnel | Potomac River |

### Historical / Vintage Maps

| Map | Era | Based On |
|-----|-----|----------|
| London 1960 | 1960s | Historical London Underground |
| Paris 1937 | 1937 | Historical Paris Metro |
| New York 1972 | 1972 | Historical New York City subway |

### Map Visual Themes

- Each city has a **unique colour palette** for its background, water, and line colours, inspired by the real-life metro system of that city.
- Example: London uses colours inspired by the London Underground (red #EB2827, yellow #F0CB16, dark blue #1D347E, cyan #019AD1, green #008D3D).
- Background colour shifts subtly between day and night periods within the game.
- Water is rendered as a distinct colour from the land background.

---

## 12. Scoring System

### Score Calculation

| Property | Value |
|----------|-------|
| Score metric | Total number of passengers successfully delivered to their destination |
| Score increment | +1 per passenger who reaches a station matching their shape |
| Display | Running counter visible on the UI throughout the game |
| Final score | Displayed on game-over screen; submitted to leaderboards |

### Leaderboards

| Feature | Detail |
|---------|--------|
| Per-map leaderboards | Separate rankings for each city map |
| Per-mode leaderboards | Separate rankings for Normal, Extreme, and Endless |
| Daily Challenge leaderboard | Global ranking for each day's pre-selected challenge |
| Friends leaderboard | Compare scores with Steam/platform friends |

### Daily Challenge

| Property | Value |
|----------|-------|
| Format | One specific city map with a fixed random seed |
| Attempts | One attempt per day |
| Scoring | Standard passenger-delivery score |
| Leaderboard submission | Automatic on game over |
| Achievement | "Commuter" -- post a score in the daily challenge every weekday for one week |

---

## 13. Game Modes

### Normal Mode

| Property | Value |
|----------|-------|
| Availability | Default; unlocked from the start on available maps |
| Lose condition | Station overcrowding timer expires |
| Budget increases | Weekly (end of Sunday) |
| Line/asset modification | Fully allowed at any time |
| Scoring | Total passengers delivered |

### Extreme Mode

| Property | Value |
|----------|-------|
| Availability | Unlocked per map by completing that map's second (harder) achievement |
| Lose condition | Station overcrowding timer expires |
| Budget increases | Weekly (end of Sunday) |
| Line/asset modification | **Prohibited** -- lines, locomotives, carriages, and other assets cannot be moved or rerouted once placed |
| Scoring | Total passengers delivered |
| Strategic impact | Requires extremely careful upfront planning; mistakes are permanent |

### Endless Mode

| Property | Value |
|----------|-------|
| Availability | Unlocked alongside Normal mode for each map |
| Lose condition | **None** -- stations do not overcrowd; the game never ends |
| Budget increases | Awarded based on efficiency milestones (circular efficiency indicator) |
| Line/asset modification | Fully allowed at any time |
| Scoring | Total passengers delivered (no game-over trigger) |
| Efficiency indicator | Circular meter: fills when passengers are delivered, drains when passengers queue up; filling it completely triggers a budget increase |

### Creative Mode

| Property | Value |
|----------|-------|
| Availability | Added in 2018 update |
| Lose condition | **None** |
| Budget increases | Unlimited resources -- no waiting for upgrades |
| Special features | Player can create and edit stations, has unlimited locomotives, tunnels, and interchanges |
| Purpose | Sandbox mode for experimentation and artistic creation |
| Scoring | No competitive scoring |

---

## 14. UI Layout

### Main Game Screen

```
+------------------------------------------------------------------+
|  [Week/Day clock]         [Passenger count: 0000]     [Pause/Play/Fast]  |
|                                                                    |
|                                                                    |
|                         MAP AREA                                   |
|         (city geography with water, stations, lines, trains)       |
|                                                                    |
|                                                                    |
|                                                                    |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  | LINE INVENTORY BAR                                            |  |
|  | [Line 1 colour] [Line 2 colour] [Line 3 colour] ... [Line 7] |  |
|  | (train icons) (carriage icons) (tunnel/bridge count)           |  |
|  +--------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

### UI Elements

| Element | Position | Description |
|---------|----------|-------------|
| Clock | Top-left | Circular clock showing current day/time; white = day, dark = night |
| Day/week label | Near clock | Shows current day of the week (Mon, Tue, etc.) |
| Passenger counter | Top-centre or top-right | Running total of passengers delivered |
| Speed controls | Top-right | Pause, 1x, 2x, 3x buttons |
| Map area | Centre (majority of screen) | The city map with all game elements |
| Line inventory bar | Bottom | Shows all lines (coloured circles), available trains, carriages, and crossing resources |
| Budget increase overlay | Centre (when triggered) | Two upgrade cards presented side-by-side for the player to choose between |

### Line Inventory Bar Detail

- Each line is represented by a coloured circle at the bottom of the screen.
- Unassigned trains and carriages appear as small icons next to the line bar.
- Available tunnel/bridge resources shown as a count.
- The bar can be hidden or locked via up/down arrow keys.

### Budget Increase Screen

- Time pauses automatically when the budget increase is presented.
- Two rectangular cards are displayed, each showing one upgrade option (icon + label).
- The player clicks one card to select that upgrade.
- A guaranteed locomotive is automatically awarded (no choice needed).
- After selection, the game resumes.

### Visual Style

| Property | Value |
|----------|-------|
| Lines | Thick coloured paths with rounded ends; parallel when sharing segments |
| Stations | Outlined geometric shapes, approximately 20--30px diameter |
| Passengers | Smaller filled shapes (~8--12px) clustered next to their station |
| Trains | Small rounded rectangles (~15px) that travel along lines |
| Carriages | Smaller rounded rectangles trailing behind their locomotive |
| Water | Solid or semi-transparent fill, distinct from land |
| Overcrowding ring | Circular timer that appears around an overcrowded station, filling clockwise |
| Background | Muted solid colour unique to each city (e.g., cream/off-white for London, light blue for Paris) |

### Colour Palette (Default/London-inspired)

| Element | Hex Code | Description |
|---------|----------|-------------|
| Background (light) | #F4F4F4 | Light grey/off-white |
| Background (mid) | #D4D4D4 | Medium grey |
| Accent | #80C3FF | Light blue for UI highlights |
| Text/icons (mid) | #747474 | Mid grey |
| Text/icons (dark) | #333333 | Near-black |
| Water | Distinct blue (varies per map) | Distinguishes water from land |

### Line Colours (Typical; Varies by Map)

| Line # | Colour |
|--------|--------|
| 1 | Red |
| 2 | Blue |
| 3 | Green |
| 4 | Yellow |
| 5 | Orange |
| 6 | Purple |
| 7 | Brown / Pink |

*Note: Actual line colours vary per city map, inspired by the real-life metro system of that city.*

---

## 15. Audio Design

### Overview

The audio system was designed by **Rich Vreeland (Disasterpeace)** and is entirely **procedural and reactive** -- every sound heard in the game is generated in real time based on the state of the metro network. No pre-composed music track plays; instead, the music emerges organically from gameplay.

### Audio Engine

| Property | Value |
|----------|-------|
| Implementation | G-Audio (Unity plugin) providing rhythmic precision |
| Update loop | Runs at a musical rate (~5 times per bar) rather than 60 FPS |
| Sound synthesis | Serum (software synthesizer) for tonal sounds |
| UI sounds | S-Layer (Reaktor ensemble) with hundreds of random variations |
| Passenger sounds | Sample-based: mouth sounds and drum machine samples with pitch/granular manipulation |
| Base waveform | Most tonal sounds are subtle variations on sine waves |

### Musical Framework

| Concept | Implementation |
|---------|----------------|
| Musical style | Minimalism and serialism (applying data sets to different axes of sound) |
| Harmonic structure | Each city has a predefined set of harmonic progressions and rhythmic choices |
| Line representation | Each metro line corresponds to a musical sequence of pulses at a constant rate and constant pitch |
| Station representation | Each station on a line = one pulse in that line's sequence, with properties: volume, timbre, panning |
| Timbre mapping | Station shape determines the timbre/instrument of that pulse |
| Volume/dynamics | Station passenger occupancy rate determines the volume of the pulse |
| Panning | Station's horizontal position on screen determines left/right audio panning |
| Harmonic progression | Adding or altering a line replaces the oldest note in the harmonic structure with the next in the progression |

### City-Specific Musical Characteristics

| City | Musical Feature |
|------|----------------|
| New York | Swing rhythms |
| Paris | Quintuplets and septuplets |
| Cairo | Uneven/asymmetric rhythms |
| Tokyo | City-specific harmonic set and train engine sounds |
| (All cities) | Unique access to specific rhythms, harmonic choices, and train engine sounds |

### Dynamic Soundscape Behaviour

| Game State | Audio Response |
|------------|---------------|
| Small, quiet metro | Sparse, minimal sound; few pulses, low volume |
| Growing metro | More lines = more simultaneous musical sequences; richer texture |
| Busy/overcrowded metro | Higher dynamics; more frequent passenger sounds; tension increases |
| Passenger boarding | Percussive sample triggered (shape-dependent timbre) |
| Passenger alighting | Distinct percussive sound |
| Train at station | Station pulse triggers |
| New station appears | Notification chime |
| Line modified | Harmonic note change |
| Overcrowding warning | Escalating tension sound |
| Game over | Resolution/conclusion audio event |

### Passenger Audio Scheduling

- Passengers of different shapes trigger their sounds at **different times within the in-game hour**, preventing sonic overload when many passengers act simultaneously.
- This scheduling creates a natural rhythmic structure where different shape types have distinct temporal positions.

---

## 16. Achievements and Unlocks

### Achievement System

| Property | Value |
|----------|-------|
| Total achievements | 73 (base game) |
| Estimated completion time | 20--25 hours |
| Per-map achievements | 2 per city (easy + hard) |
| Easy achievement | Unlocks the next city map |
| Hard achievement | Unlocks Extreme mode for that city |
| Daily challenge achievements | Based on participation streaks |
| Endless mode | Achievements are **not** earnable in Endless mode |

### Achievement Types

| Type | Examples |
|------|---------|
| Passenger threshold | Deliver X passengers on a specific map |
| Constraint challenges | Complete a map with limited lines, no interchanges, etc. |
| Daily challenge | Post a daily challenge score every weekday for a week ("Commuter") |
| Special conditions | Map-specific challenges (e.g., "Only One Tunnel in London") |

### Map Unlock Flow

```
London (start) --> [Easy achievement] --> Paris (start) --> [Easy achievement] --> New York (start)
                                              |
                                              v
                                    [Further achievements unlock subsequent cities]
                                              |
                                              v
                            Cities unlock in a branching progression tree
                                              |
                                              v
                        Daily Challenges can unlock any locked city by playing it
```

---

## Appendix A: Game Constants Summary

| Constant | Value |
|----------|-------|
| Starting stations | 3 (Circle, Triangle, Square) |
| Starting lines | 3 |
| Maximum lines | 7 |
| Station capacity (regular) | 6 passengers |
| Station capacity (interchange) | 18 passengers |
| Overcrowding timer | 45 seconds + 2s grace = 47s total |
| Locomotive capacity (standard) | 6 passengers |
| Locomotive capacity (Shinkansen) | 8 passengers |
| Locomotive capacity (Tram) | 4 passengers |
| Locomotive capacity (Cairo) | 4 passengers |
| Carriage bonus capacity | +6 (or +4 in Cairo) |
| Locomotive speed (standard) | 360 units |
| Locomotive acceleration | 120 units |
| Locomotive deceleration | 300 units |
| Shinkansen speed | 480 units (~2x locomotive) |
| Shinkansen acceleration | 180 units |
| Tram speed | 250 units |
| Tram acceleration | 1000 units (effectively instant) |
| In-game day (real time, 1x) | ~20 seconds |
| In-game week (real time, 1x) | ~2 minutes 20 seconds |
| Crossings per upgrade (default) | 2 |
| New station spawn interval | ~20--30 seconds (real time, 1x) |
| Total city maps (normal) | 34 |
| Total historical maps | 3 |
| Total achievements | 73 |

## Appendix B: Station Shape Reference

```
Circle:    ( O )     -- Most common station; ~50% of all stations
Triangle:  ( /\ )    -- Second most common; ~25% of all stations
Square:    ( [] )    -- Semi-common; ~12.5% of all stations
Pentagon:  ( /--\ )  -- Unique (max 1 per map)
Diamond:   ( <> )    -- Unique (max 1 per map)
Star:      ( * )     -- Unique (max 1 per map)
Cross:     ( + )     -- Unique (max 1 per map)
Wedge:     ( D )     -- Unique (max 1 per map); semicircular shape
Gem:       ( <=> )   -- Unique (max 1 per map); hexagonal shape
Egg:       ( 0 )     -- Unique (max 1 per map); oval shape
```

## Appendix C: Pathfinding Cost Formula (Simplified)

```
TotalCost(route) = SUM over each edge E in route:
    WaitTime(E)         -- predicted time for train to reach pickup station
  + TravelTime(E)       -- time to travel from pickup to dropoff station on this edge
  + TransferPenalty(E)   -- extra cost for changing lines (exaggerated to favour direct routes)
  + BacktrackPenalty(E)  -- cost for revisiting a previously visited station
  + OvercrowdBonus(E)    -- negative cost (discount) for leaving an overcrowded station quickly
```

The A* heuristic uses estimated travel time to the nearest matching destination station.

---

*This specification is based on the retail release of Mini Metro (v1.x) by Dinosaur Polo Club, including updates through the Miniversary Update (July 2023).*
