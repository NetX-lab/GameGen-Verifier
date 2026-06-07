# SimCity (1989) -- Complete Game Specification

> A comprehensive specification for faithfully recreating the original SimCity (Maxis, 1989 IBM PC/DOS version -- often called SimCity Classic). This document covers every system, mechanic, formula, and interaction required for a full clone, as validated against the open-source Micropolis codebase and the original manual.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Map & Terrain](#3-map--terrain)
4. [Zone System (R/C/I)](#4-zone-system-rci)
5. [Infrastructure Systems](#5-infrastructure-systems)
6. [Power System](#6-power-system)
7. [Economy & Budget](#7-economy--budget)
8. [Simulation Systems](#8-simulation-systems)
9. [Service Buildings](#9-service-buildings)
10. [Disaster System](#10-disaster-system)
11. [Population & Growth](#11-population--growth)
12. [RCI Demand](#12-rci-demand)
13. [City Evaluation & Scoring](#13-city-evaluation--scoring)
14. [Scenarios](#14-scenarios)
15. [UI Layout](#15-ui-layout)
16. [Audio Design](#16-audio-design)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | SimCity |
| Developer | Maxis Software |
| Designer | Will Wright |
| Original release | February 2, 1989 |
| Genre | City-building simulation |
| Perspective | Top-down isometric tile map |
| Input | Mouse + keyboard |
| Players | 1 (single-player) |
| Objective | Build and manage a thriving city with no fixed win condition in sandbox mode; meet scenario goals in scenario mode |
| Lose condition | None in sandbox; scenario time-out or failure to meet goal in scenario mode |
| Difficulty levels | Easy, Medium, Hard |
| Starting funds (sandbox) | $20,000 (all difficulty levels) |
| Starting date | January 1900 (sandbox mode) |
| Open-source derivative | Micropolis (GPL, released 2008 for OLPC) |

### Core Loop

```
1. Zone land (Residential / Commercial / Industrial)
2. Connect zones with roads and/or rail
3. Supply power via power plants and power lines
4. Provide city services (police, fire)
5. Manage budget (set tax rate, fund departments)
6. Monitor simulation feedback (crime, pollution, traffic, land value)
7. Respond to disasters
8. Grow population toward city classification milestones
```

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| EGA mode | 640 x 350 (16 color) or 320 x 200 (16 color) |
| VGA mode (v2.00 Classic) | 640 x 480 (16 color) or 320 x 200 (256 color) |
| CGA mode | 640 x 200 (monochrome) |
| Hercules mode | 720 x 348 (monochrome) |
| Tandy mode | 640 x 200 |
| Tile size | 16 x 16 pixels (base tile at standard zoom) |
| Zoom levels | 2 (normal and zoomed-out overview in map window) |

### Map Dimensions

| Property | Value |
|----------|-------|
| Map width | 120 tiles |
| Map height | 100 tiles |
| Total tiles | 12,000 |
| Tile data | 16-bit signed integer per tile (stores tile type + flag bits) |

### Tile Flag Bits

Each 16-bit tile word encodes:

| Bit(s) | Name | Purpose |
|--------|------|---------|
| 0-9 | LOMASK | Tile type index (0-1023) |
| 10 | BULLBIT | Bulldozeable flag |
| 11 | BURNBIT | Burnable flag |
| 12 | CONDBIT | Conducts power flag |
| 13 | ANIMBIT | Animated tile flag |
| 14 | POWERBIT | Currently powered flag |
| 15 | ZONEBIT | Is a zone center flag |

### Simulation Timing

| Property | Value |
|----------|-------|
| Simulation speeds | Paused, Slow, Medium (default), Fast |
| Budget/tax cycle | Once per simulated year (at TAXFREQ intervals) |
| Census cycle | Every 4 simulation ticks |
| Evaluation cycle | Once per year (coincides with budget) |
| Power scan | Every simulation cycle |
| Crime/pollution update | Smoothed over 4-period ramp |

### Game Loop (per tick)

```
1. Increment simulation clock
2. Scan map tiles (process zones, update population counts)
3. Run power distribution (flood-fill from power plants)
4. Calculate traffic density
5. Calculate pollution map (diffusion from sources)
6. Calculate crime map (density-based with police suppression)
7. Calculate land value map
8. Update RCI demand valves
9. Process disasters (if active)
10. If TAXFREQ reached: collect taxes, run budget, run city evaluation
11. Update graph histories
12. Render map and UI
```

---

## 3. Map & Terrain

### Terrain Types

| Terrain | Tile Range | Buildable | Notes |
|---------|-----------|-----------|-------|
| Clear land | Light/tan tiles | Yes | Default buildable surface |
| Water | Dark blue tiles | No | Raises adjacent land value; requires bridges/tunnels to cross |
| Forest/trees | Green tiles | No (must bulldoze first) | Bulldoze cost $1 per tile to clear |
| Rubble | Grey tiles | No (must bulldoze first) | Left after disasters or demolition |
| Radioactive | Yellow hazard tiles | No | Left after nuclear meltdown; persists essentially forever |

### Terrain Generation

- New maps are procedurally generated with random coastlines, rivers, lakes, and forest patches.
- The player can request a new random terrain repeatedly before starting.
- An optional **Terrain Editor** (separate tool, sold separately) allows custom map creation with land, water, and forest painting.
- Less water is generally preferred since water tiles are unbuildable, but waterfront land has elevated land value.

### Terrain Modification

| Action | Cost | Effect |
|--------|------|--------|
| Bulldoze land tile | $1 | Clears trees, rubble, or existing development |
| Bulldoze water | N/A | Cannot bulldoze water tiles |
| Road on water | $50 (bridge) | Automatically creates bridge segment |
| Rail on water | $100 (tunnel) | Automatically creates underwater tunnel |
| Power line on water | $25 | Automatically creates underwater cable |

---

## 4. Zone System (R/C/I)

### Zone Basics

| Property | All Zone Types |
|----------|---------------|
| Zone placement size | 3 x 3 tiles |
| Cost per zone | $100 |
| Requires power | Yes (flashing lightning bolt icon when unpowered) |
| Requires road/rail access | Yes (for growth; zones without transport access stagnate) |

### Residential Zones

Residential zones house the population (Sims). Growth depends on the RCI R-demand valve, land value, and pollution level.

#### Development Stages

| Stage | Visual | Population | Requirements |
|-------|--------|-----------|--------------|
| Empty zone | Bare land with "R" marker | 0 | Freshly zoned |
| Small houses | Up to 8 individual houses | 20 per house (max 160) | Power + road access |
| R-1 (Lower density) | Small apartment building | 320 | Population density >= 66; positive R-demand |
| R-2 (Medium density) | Medium apartment | ~400-500 | Higher land value; continued R-demand |
| R-3 (Higher density) | Larger apartment | ~600 | Higher land value; low crime/pollution |
| R-4 (High density) | Tall apartment tower | 800 | High land value; very low pollution |
| RTOP (Maximum) | Skyscraper/high-rise | 1,920 | Two adjacent R-4 zones merge; highest land value |

#### Residential Growth Factors

| Factor | Effect |
|--------|--------|
| R-demand (RCI valve) | Primary driver; positive valve enables growth |
| Land value | Higher value enables higher density stages |
| Pollution | Negative effect; reduces growth and land value (double penalty) |
| Crime rate | Negative; depresses land value which further reduces growth |
| Power supply | Required; unpowered zones cannot develop |
| Road/rail access | Required for commute trips to reach jobs |
| Population density of surrounding area | Density >= 66 needed for R-1 transition |

#### Residential Sub-types (appear organically)

- Houses (single-family)
- Apartments (multi-family)
- Churches (appear in residential areas; do not contribute population)
- Hospitals (appear in residential areas; provide health metric)

### Commercial Zones

Commercial zones provide shops, offices, and services. Growth depends on C-demand, internal markets, and labor supply.

#### Development Stages

| Stage | Visual | Description |
|-------|--------|-------------|
| Empty zone | Bare land with "C" marker | Freshly zoned |
| C-1 (Low) | Small shop / gas station | Basic retail |
| C-2 (Medium-low) | Strip mall / small office | Growing retail |
| C-3 (Medium-high) | Office building | Established commercial |
| C-4 (High) | Large office / department store | Major commercial |
| CTOP (Maximum) | High-rise office tower | Two adjacent C-4 merge |

#### Commercial Growth Factors

| Factor | Effect |
|--------|--------|
| C-demand (RCI valve) | Primary growth driver |
| Internal market | (ResPop + ComPop + IndPop) / 3.7 |
| Labor supply | Residential population provides workers |
| Land value | Limits maximum development stage |
| Pollution | Negative effect |
| Crime | Negative effect |
| Traffic density | High traffic reduces desirability |
| Airport presence | Boosts commercial demand (acts as external market) |
| Transit access | Required for customer/worker flow |
| Power | Required |

### Industrial Zones

Industrial zones provide jobs and economic base. Growth depends primarily on I-demand and is less sensitive to land value.

#### Development Stages

| Stage | Visual | Description |
|-------|--------|-------------|
| Empty zone | Bare land with "I" marker | Freshly zoned |
| I-1 (Low) | Small warehouse / pumping station | Light industry |
| I-2 (Medium) | Medium factory | Growing industry |
| I-3 (High) | Large factory complex | Heavy industry |
| I-4 (Maximum) | Full industrial complex | Maximum industrial |

#### Industrial Growth Factors

| Factor | Effect |
|--------|--------|
| I-demand (RCI valve) | Primary and almost sole growth driver |
| External market | Grows with overall city population |
| Seaport presence | Boosts industrial demand significantly |
| Transit access | Required for worker/freight flow |
| Labor supply | Residential population provides workers |
| Power | Required |
| Land value | Minimal effect (industry tolerates low land value) |
| Pollution output | Industrial zones are the primary pollution source |

---

## 5. Infrastructure Systems

### Transportation

#### Roads

| Property | Value |
|----------|-------|
| Placement cost (land) | $10 per tile |
| Placement cost (water/bridge) | $50 per tile |
| Annual maintenance | $1 per road tile, $4 per bridge tile |
| Tile size | 1 x 1 |
| Function | Enables zone access and commuter trips |
| Capacity | Each road tile has a traffic capacity; excess creates congestion |
| Deterioration | Under-funded roads deteriorate randomly each year |

#### Rail / Transit Lines

| Property | Value |
|----------|-------|
| Placement cost (land) | $20 per tile |
| Placement cost (water/tunnel) | $100 per tile |
| Annual maintenance | $4 per rail tile, $10 per tunnel tile |
| Tile size | 1 x 1 |
| Function | Identical to roads for zone access; reduces traffic density |
| Capacity | Higher effective capacity than roads |
| Deterioration | Under-funded rail deteriorates randomly each year |

#### Transportation Behavior

- Sims do **not** distinguish between road and rail; both serve as valid transit routes.
- Alternating road and rail tiles still form a continuous path.
- Each populated zone generates trips proportional to its population.
- Trips pathfind via shortest route on the transport network to reach destination zones.
- Failed trips (no path or excessive congestion) reduce zone desirability and land value.
- Traffic density is accumulated along used routes and mapped to a 0-255 scale per tile.

#### Power Lines

| Property | Value |
|----------|-------|
| Placement cost (land) | $5 per tile |
| Placement cost (water) | $25 per tile |
| Tile size | 1 x 1 |
| Function | Conducts electricity from power plants to zones |
| Buildable over | Clear land, under roads/rail (auto-connects) |
| Cannot cross | Trees/forest (must bulldoze first), zoned land |

### Parks

| Property | Value |
|----------|-------|
| Placement cost | $10 per tile |
| Tile size | 1 x 1 |
| Function | Raises land value of surrounding area |
| Maintenance | None |

---

## 6. Power System

### Power Plants

| Property | Coal Power Plant | Nuclear Power Plant |
|----------|-----------------|---------------------|
| Size | 4 x 4 tiles | 4 x 4 tiles |
| Cost | $3,000 | $5,000 |
| Zone capacity | ~50 zones powered | ~150 zones powered |
| Pollution | Yes (significant) | No (clean energy) |
| Meltdown risk | No | Yes (random; higher on harder difficulty) |
| Lifespan | Degrades over time | Degrades over time |

### Power Distribution Algorithm

Power propagates via a **flood-fill** algorithm:

```
1. Reset POWERBIT on all tiles
2. For each power plant:
   a. Push plant location onto power stack
3. While power stack is not empty:
   a. Pop tile from stack
   b. Set POWERBIT on this tile
   c. For each of the 4 cardinal neighbors:
      - If neighbor has CONDBIT set (is a conductor) AND POWERBIT not yet set:
        - Push neighbor onto stack
4. Any zone without POWERBIT set displays unpowered indicator
```

### Power Conductors

The following tile types conduct power (have CONDBIT):
- Power lines
- All zone center tiles (R/C/I zones)
- Roads and rail (auto-conduct when adjacent to powered tiles)
- Power plants themselves
- All zone tiles that are part of a 3x3 zone (power flows through developed zones)

### Power Behavior Rules

- **All developed zones require power** to function. Unpowered zones stagnate and eventually decline.
- Zones display a **flashing lightning bolt** when unpowered.
- Power lines connecting directly to a zone edge will power that zone.
- Adjacent zones power each other through shared edges (no power line needed between touching zones).
- Only **one** power plant needs to be connected to the grid; additional plants add to total capacity even if not directly wired in (they are always on-grid by the flood-fill).
- Power line transmission has minor inefficiency losses over distance.

---

## 7. Economy & Budget

### Tax Collection

Taxes are collected once per simulated year. The formula is:

```
TaxFund = (TotalPop * LandValueAverage / 120) * CityTax * GameLevelMultiplier
```

| Variable | Description |
|----------|-------------|
| TotalPop | Sum of residential + commercial + industrial population |
| LandValueAverage | Average land value across all developed tiles |
| CityTax | Player-set tax rate (0-20%) |
| GameLevelMultiplier | Easy: 1.4, Medium: 1.2, Hard: 0.8 |

### Tax Rate Effects

| Tax Rate | Effect |
|----------|--------|
| 0-4% | Very fast growth; very low revenue |
| 5-7% | Optimal balance of growth and income |
| 8-9% | Slowed growth; adequate revenue |
| 10-12% | Growth stalls; high short-term revenue |
| 13-20% | Population decline; diminishing returns on revenue |

### Department Funding

Three departments require annual funding:

| Department | Requested Budget | Unit Cost |
|------------|-----------------|-----------|
| Police | $100 per police station per year | Per station |
| Fire | $100 per fire station per year | Per station |
| Transportation | Variable (see below) | Per tile |

#### Transportation Maintenance Costs

| Infrastructure | Annual Cost per Tile |
|----------------|---------------------|
| Road (land) | $1 |
| Bridge (road over water) | $4 |
| Rail (land) | $4 |
| Tunnel (rail over water) | $10 |

### Funding Levels

- Each department can be funded from **0% to 100%** of its requested budget using slider controls.
- Underfunding reduces effectiveness:
  - **Police**: Reduced crime suppression radius and strength.
  - **Fire**: Reduced fire suppression radius and response.
  - **Transportation**: Random road/rail deterioration; tiles may revert to rubble.

### Funding Effectiveness Ratios

The simulation tracks three effectiveness values:

| Ratio | Max Value | Effect |
|-------|-----------|--------|
| RoadEffect | 32 (at 100% funding) | Higher = better road maintenance |
| PoliceEffect | 1000 (at 100% funding) | Higher = better crime suppression |
| FireEffect | 1000 (at 100% funding) | Higher = better fire response |

### Cash Flow

```
CashFlow = TaxFund - (PoliceFund + FireFund + RoadFund)
```

- **No deficit spending**: SimCity does not allow negative balances. If funds reach $0, construction is blocked.
- **Loans**: Not available in the original 1989 PC version. (The SNES version introduced a bank gift building allowing a $10,000 loan.)

### Auto-Budget

- When enabled in Options, the budget window does not appear each year; previous year's settings are reused automatically.

---

## 8. Simulation Systems

All simulation layers operate on map-wide grids, typically using 2x2 or 4x4 block averaging for performance.

### Traffic Density

| Property | Value |
|----------|-------|
| Scale | 0-255 per tile |
| Sources | Trips generated by populated zones |
| Routing | Pathfinding from residential to commercial/industrial zones via road/rail |
| Effects | High traffic increases pollution; reduces land value and zone desirability |
| Mitigation | Build more roads/rail; distribute zones; reduce commute distances |

### Pollution

| Property | Value |
|----------|-------|
| Scale | 0-255 per tile |
| Sources | Industrial zones (primary), traffic density, coal power plants, airports, seaports |
| Spread | Diffusion algorithm; pollution radiates outward from sources |
| Effects | Reduces residential desirability; reduces land value; negative growth modifier |
| Smoothing | `PollutionRamp += (PollutionAverage - PollutionRamp) / 4` (4-period smooth) |
| Mitigation | Separate industry from residential; reduce traffic; use nuclear power |

### Crime

| Property | Value |
|----------|-------|
| Scale | Baseline of 128 (on 0-255 scale) |
| Increase factors | High population density, low land value, lack of police coverage |
| Decrease factors | Police stations (radius-based suppression), high land value |
| Feedback | Crime reduces land value; low land value increases crime (vicious cycle) |
| Smoothing | `CrimeRamp += (CrimeAverage - CrimeRamp) / 4` (4-period smooth) |
| Mitigation | Build police stations; raise land value with parks and services |

### Land Value

| Property | Value |
|----------|-------|
| Scale | 0-255 per tile |
| Positive factors | Proximity to water, parks, city center, service buildings; low crime; low pollution |
| Negative factors | Pollution, crime, long commute distance, proximity to industry |
| Effects | Determines zone development stage caps; higher value = higher density possible |
| Tax interaction | Land value is a multiplier in the tax collection formula |

### Land Value Calculation

```
LandValue = TerrainBonus
           + DistanceToCenterBonus
           + ParkProximityBonus
           + WaterProximityBonus
           - PollutionPenalty
           - CrimePenalty
```

- Values are computed per tile, then averaged across 2x2 blocks for the simulation overlay.
- `LandValueAverage` (city-wide) is used in the tax formula.

---

## 9. Service Buildings

### Police Station

| Property | Value |
|----------|-------|
| Size | 3 x 3 tiles |
| Cost | $500 |
| Annual funding | $100 (at 100%) |
| Effect | Reduces crime rate in surrounding area |
| Coverage radius | ~15-20 tiles (at full funding); shrinks with reduced funding |
| Placement tip | Distribute evenly; one per ~10,000-15,000 population |

### Fire Station

| Property | Value |
|----------|-------|
| Size | 3 x 3 tiles |
| Cost | $500 |
| Annual funding | $100 (at 100%) |
| Effect | Suppresses fire spread in surrounding area; responds to fires |
| Coverage radius | ~15-20 tiles (at full funding); shrinks with reduced funding |
| Placement tip | Distribute evenly; especially near industrial zones and forests |

### Stadium

| Property | Value |
|----------|-------|
| Size | 4 x 4 tiles |
| Cost | $3,000 |
| Annual funding | None |
| Effect | Satisfies residential demand cap; boosts land value slightly |
| Requirement trigger | RCI demand cap hit when population exceeds ~20,000 without a stadium |
| Limit | One stadium is sufficient for most cities |

### Seaport

| Property | Value |
|----------|-------|
| Size | 4 x 4 tiles |
| Cost | $5,000 |
| Annual funding | None |
| Effect | Boosts industrial growth by providing external market access |
| Placement | Must be adjacent to water |
| Pollution | Generates moderate pollution |
| Shipwreck risk | Enables shipwreck disaster |
| Requirement trigger | Industrial demand cap when population lacks port access |

### Airport

| Property | Value |
|----------|-------|
| Size | 6 x 6 tiles |
| Cost | $10,000 |
| Annual funding | None |
| Effect | Boosts commercial growth by providing external market access |
| Placement | Requires large flat area; preferably away from residential (noise/pollution) |
| Pollution | Generates significant noise pollution |
| Crash risk | Enables air crash disaster |
| Requirement trigger | Commercial demand cap when population exceeds ~40,000 without airport |

### Coal Power Plant

| Property | Value |
|----------|-------|
| Size | 4 x 4 tiles |
| Cost | $3,000 |
| Zone capacity | ~50 zones |
| Pollution | Heavy (major pollution source) |
| Meltdown risk | None |
| Lifespan | Degrades over many game-years |

### Nuclear Power Plant

| Property | Value |
|----------|-------|
| Size | 4 x 4 tiles |
| Cost | $5,000 |
| Zone capacity | ~150 zones |
| Pollution | None |
| Meltdown risk | Random chance; never on Easy difficulty |
| Meltdown effect | Destroys plant and surrounding area; creates permanent radioactive zone |
| Lifespan | Degrades over many game-years |

---

## 10. Disaster System

Disasters can occur **randomly** based on city conditions or be **manually triggered** via the Disasters menu. Disasters can be toggled off entirely in the Options menu.

### Disaster Types

| Disaster | Menu Trigger | Random Trigger | Size/Scope |
|----------|-------------|----------------|------------|
| Fire | Yes | Yes (random) | Starts at single tile; spreads |
| Flood | Yes | Yes (near water) | Spreads from waterfront |
| Air Crash | Yes | Yes (requires airport) | Creates fire at crash site |
| Tornado | Yes | Yes (random) | Moves across map; destroys path |
| Earthquake | Yes | Yes (rare) | City-wide; 8.0-9.0 Richter scale |
| Monster Attack | Yes | Yes (high pollution) | Monster traverses map, destroys and sets fires |
| Nuclear Meltdown | No (random only) | Yes (nuclear plant) | Destroys plant; irradiates surrounding area |
| Shipwreck | No (random only) | Yes (requires seaport) | Fire at coastal crash site |

### Fire Mechanics

| Property | Value |
|----------|-------|
| Spread rate | Adjacent tiles per tick; faster through forest |
| Spread direction | All 4 cardinal directions |
| Blocked by | Water, clear land (firebreaks), bulldozed rubble |
| Suppression | Fire stations reduce spread rate in coverage area |
| Player action | Bulldoze tiles around fire to create firebreaks |
| Damage | Burns buildings/zones to rubble; destroys power lines and roads |

### Flood Mechanics

| Property | Value |
|----------|-------|
| Origin | Coastal/waterfront tiles |
| Spread | Gradual outward from water edges |
| Damage | Destroys buildings and infrastructure in flooded tiles |
| Duration | Self-limiting; recedes after a period |
| Mitigation | Avoid building directly on waterfront |

### Tornado Mechanics

| Property | Value |
|----------|-------|
| Movement | Travels across map in a semi-random path |
| Damage | Destroys everything in its path (1-2 tile width) |
| Duration | Crosses map then dissipates |
| Mitigation | None; purely destructive |

### Earthquake Mechanics

| Property | Value |
|----------|-------|
| Magnitude | 8.0-9.0 on Richter Scale |
| Damage | Randomly destroys buildings across entire city |
| Secondary | ~25% of damaged tiles catch fire |
| Duration | Instantaneous primary damage; fires persist |
| Mitigation | Fire department coverage limits secondary fire damage |

### Monster Attack Mechanics

| Property | Value |
|----------|-------|
| Trigger | High pollution levels attract the monster |
| Movement | Traverses map targeting pollution sources |
| Damage | Destroys tiles in path; starts fires |
| Duration | Crosses city then leaves |
| Visual | Large creature (Godzilla-inspired) |

### Nuclear Meltdown Mechanics

| Property | Value |
|----------|-------|
| Trigger | Random (nuclear plant age/condition); fire near plant; earthquake damage |
| Never occurs | Easy difficulty (nuclear power is 100% safe on Easy) |
| Damage | Destroys the power plant and surrounding ~10-15 tile radius |
| Radiation | Irradiated tiles are permanently unusable (tens of thousands of years to decay) |
| Visual | Radioactive warning symbols on contaminated tiles |
| Mitigation | Use coal power; or accept risk for triple power capacity |

### Shipwreck & Air Crash

| Property | Shipwreck | Air Crash |
|----------|-----------|-----------|
| Trigger | Random; requires seaport | Random; requires airport |
| Damage | Fire at coastal crash site | Fire at crash site (or harmless if over water) |
| Mitigation | Fire station coverage | Fire station coverage |

---

## 11. Population & Growth

### Population Calculation

Total population is derived from zone populations:

```
TotalPop = (ResPop + (ComPop + IndPop) * 8) * 20
```

Where:
- `ResPop` = raw residential population count (sum of all residential tiles)
- `ComPop` = raw commercial zone count
- `IndPop` = raw industrial zone count
- Commercial and industrial zones are weighted 8x, then the total is multiplied by 20

#### Normalized Population

```
NormResPop = ResPop / 8
```

### Population Dynamics

| Metric | Formula |
|--------|---------|
| Birth rate | `Births = NormResPop * 0.02` (2% per year) |
| Migration | `Migration = NormResPop * (Employment - 1.0)` |
| Employment ratio | Based on available commercial + industrial jobs vs. residential labor supply |

### City Classification Thresholds

| Classification | Population Required |
|----------------|-------------------|
| Village | 0 - 1,999 |
| Town | 2,000 - 9,999 |
| City | 10,000 - 49,999 |
| Capital | 50,000 - 99,999 |
| Metropolis | 100,000 - 499,999 |
| Megalopolis | 500,000+ |

### Growth Requirements Summary

For a city to grow, the following must be maintained:

| Requirement | Details |
|-------------|---------|
| Power | All zones must be powered |
| Transportation | Zones must be adjacent to roads or rail |
| Zone balance | Maintain R/C/I ratios matching demand indicators |
| Low taxes | 5-7% optimal; above 9% slows growth |
| Services | Police and fire stations at adequate coverage |
| Low pollution | Keep industry away from residential |
| Low crime | Adequate police coverage and high land value |
| Infrastructure | Seaport and airport for demand caps |
| Stadium | Required after ~20,000 population |

---

## 12. RCI Demand

### The RCI Demand Indicator

The RCI indicator is a vertical bar graph with three bars displayed in the Edit Window:
- **R** (Green) = Residential demand
- **C** (Blue) = Commercial demand
- **I** (Yellow) = Industrial demand

Bars extending **upward** indicate positive demand (zone more of this type). Bars extending **downward** indicate oversupply (zone less of this type).

### Demand Valve System

Three internal valve variables control growth velocity:

| Valve | Range | Purpose |
|-------|-------|---------|
| RValve (Residential) | -2000 to +2000 | Controls residential zone growth rate |
| CValve (Commercial) | -1500 to +1500 | Controls commercial zone growth rate |
| IValve (Industrial) | -1500 to +1500 | Controls industrial zone growth rate |

### Demand Calculation Factors

#### Residential Demand

```
- Driven by employment availability (commercial + industrial jobs)
- Positive when more jobs available than workers
- Negative when unemployment is high
- Modified by tax rate (high tax reduces demand)
```

#### Commercial Demand

```
- Driven by internal market size: (ResPop + ComPop + IndPop) / 3.7
- Requires residential labor supply (LaborBase ratio capped at minimum 1.3)
- Boosted by airport presence (external market access)
- Reduced by high crime, pollution, traffic
```

#### Industrial Demand

```
- Driven by labor supply and external market
- Boosted by seaport presence
- Less sensitive to pollution and crime than commercial
- Primary driver of early-game economy
```

### Demand Caps

Certain infrastructure triggers demand caps that halt growth until the building is provided:

| Cap Trigger | Required Building | Effect if Missing |
|-------------|------------------|-------------------|
| Residential cap | Stadium | R-demand capped at ~-1500 (penalty) |
| Commercial cap | Airport | C-demand capped at ~-1500 (penalty) |
| Industrial cap | Seaport | I-demand capped at ~-1500 (penalty) |

The evaluation score applies a **-15% penalty per zone type** that is hitting its demand cap.

---

## 13. City Evaluation & Scoring

### Evaluation Window

The Evaluation Window (accessed via Windows menu or keyboard shortcut) displays:

1. **Public Opinion** -- "Is the mayor doing a good job?"
   - **Yes** percentage and **No** percentage
2. **What are the worst problems?** -- Top 4 problems ranked by severity with percentage
3. **Statistics** -- Population, Net Migration, Assessed Value
4. **City Classification** -- Village / Town / City / Capital / Metropolis / Megalopolis
5. **Overall City Score** -- 0 to 1000

### Problem Categories

Citizens can complain about the following issues:

| Problem Category | Cause |
|-----------------|-------|
| Crime | High crime rate; insufficient police |
| Pollution | Industrial zones, traffic, coal plants |
| Housing costs | Low residential supply vs. demand |
| Taxes | Tax rate too high (>7% starts complaints) |
| Traffic | Congested roads; insufficient transit |
| Unemployment | Too few commercial/industrial jobs |
| Fire protection | Insufficient fire station coverage |
| Unpowered zones | Zones without electricity |

### City Score Calculation

The Overall City Score (0-1000) is calculated as follows:

```
Step 1: Sum all 7 problem values
Step 2: RawScore = (250 - min(ProblemSum / 3, 250)) * 4
         (This yields 0-1000 where fewer problems = higher score)

Step 3: Apply penalties:
  - -15% per zone type hitting demand cap (up to 3 zone types = -45%)
  - Road/rail maintenance shortfall penalty
  - Police underfunding penalty (up to -10%)
  - Fire underfunding penalty (up to -10%)
  - Collapsed RCI demand penalty (-15% each if valve < -1000)
  - Fire severity penalty
  - Tax level penalty (progressive above 7%)
  - Unpowered zone ratio penalty (unpowered / total zones)

Step 4: Population growth bonus (positive migration adds points)
         Population decline penalty (negative migration subtracts)

Step 5: Smooth with previous score:
         FinalScore = (RawScore + PreviousScore) / 2
         (50/50 average with last year; initial score starts at 500)
```

### Score Interpretation

| Score Range | Rating |
|-------------|--------|
| 900-1000 | Excellent |
| 700-899 | Good |
| 500-699 | Average |
| 300-499 | Below Average |
| 100-299 | Poor |
| 0-99 | Terrible |

---

## 14. Scenarios

Scenarios are **goal-oriented, time-limited** challenges based on real (or fictional) cities and historical events. Each scenario presents a pre-built city with a specific problem to solve.

### Scenario List (Original PC Version)

| # | City | Year | Disaster/Challenge | Difficulty | Goal |
|---|------|------|--------------------|------------|------|
| 1 | Dullsville, USA | 1900 | Boredom (stagnation) | Easy | Build Dullsville into a thriving metropolis within 30 years |
| 2 | San Francisco, CA | 1906 | 8.0 Earthquake | Very Difficult | Control fires, rebuild the city, restore population |
| 3 | Hamburg, Germany | 1944 | Allied bombing / firestorm | Very Difficult | Mitigate bomb damage, fight fires, rebuild |
| 4 | Bern, Switzerland | 1965 | Traffic congestion | Easy | Reduce traffic problems and improve city infrastructure |
| 5 | Tokyo, Japan | 1957 | Monster attack (Godzilla) | Moderate | Limit monster damage, rebuild, restore prosperity |
| 6 | Detroit, Michigan | 1972 | Crime and economic depression | Moderate | Reduce crime, reorganize and revitalize the city |
| 7 | Boston, Massachusetts | 2010 | Nuclear meltdown | Very Difficult | Contain radiation, restructure city around contaminated zone, rebuild |
| 8 | Rio de Janeiro, Brazil | 2047 | Coastal flooding (global warming) | Moderate | Control flooding, rebuild infrastructure, restore city |

### Scenario Mechanics

- Each scenario has a **time limit** (typically 5-30 game years).
- The scenario starts with a pre-built city and the designated disaster occurs shortly after start (some immediately, some after a delay via `DisasterWait` counter).
- Win condition is typically reaching a target population, score, or resolving the designated crisis.
- Losing occurs by running out of time or letting the city deteriorate beyond recovery.
- **Hamburg** scenario uses a unique bombing disaster (not available in sandbox mode).
- **Platform note**: Hamburg and Dullsville scenarios were included in the PC, Amiga, and Atari ST versions but **not** the SNES version.

### SNES-Exclusive Content

The SNES version (1991, developed by Nintendo EAD) added:
- **Freeland scenario**: Blank map, no water; goal is to reach 500,000 population with no time limit.
- **Las Vegas scenario**: Year 2096, alien (UFO) invasion.
- **Gift/reward buildings** (see below).
- **Dr. Wright** advisor character.

---

## 15. UI Layout

### Screen Organization

The SimCity interface consists of multiple overlapping windows:

```
+------------------------------------------------------------------+
|  Menu Bar                                                         |
|  [File] [Options] [Disasters] [Windows] [Speed]                  |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------------------+  +---------------------------+  |
|  | EDIT WINDOW                   |  | MAP WINDOW               |  |
|  | (Main City View)              |  | (Minimap Overview)       |  |
|  |                               |  |                           |  |
|  | [Title Bar]                   |  | Entire city at reduced   |  |
|  | [Message Bar]                 |  | scale; flashing box      |  |
|  | [RCI Demand Indicator]        |  | shows current edit       |  |
|  |                               |  | window viewport          |  |
|  | Scrollable isometric          |  |                           |  |
|  | tile map view                 |  | Click to navigate        |  |
|  |                               |  |                           |  |
|  | [Tool Icon] [Cost Display]    |  +---------------------------+  |
|  | [Date] [Funds]                |                                 |
|  +------------------------------+                                 |
|                                                                    |
+------------------------------------------------------------------+
```

### Menu Bar

| Menu | Items |
|------|-------|
| **File** | Load Scenario, Start New City, Load City, Save City, Print City, Quit |
| **Options** | Auto-Bulldoze (toggle), Auto-Budget (toggle), Auto-Goto (toggle), Sound (toggle) |
| **Disasters** | Fire, Flood, Air Crash, Tornado, Earthquake, Monster |
| **Windows** | Maps, Budget, Graphs, Evaluation, Edit |
| **Speed** | Pause, Slow, Medium, Fast |

### Edit Window Components

| Component | Location | Description |
|-----------|----------|-------------|
| Title bar | Top | Window title; drag to move window |
| Message bar | Below title | Scrolling news ticker with city events and advisor messages |
| RCI Demand indicator | Upper area | Three vertical bars (R/C/I) showing current demand |
| Tool palette | Left side or bottom | Icons for all buildable items |
| Selected tool + cost | Bottom | Shows currently selected tool and per-use cost |
| Date display | Bottom | Current month and year |
| Funds display | Bottom | Current treasury balance |
| Scroll arrows | Window edges | Click to scroll the map view |
| Zoom box | Corner | Toggle between zoom levels |

### Tool Palette Icons

| Icon | Tool | Keyboard Shortcut |
|------|------|-------------------|
| Bulldozer | Demolish / clear | B |
| Road | Place road | R |
| Rail / Transit | Place rail | T |
| Power Line | Place power line | P |
| Residential Zone | Zone 3x3 residential | (Z/X to cycle) |
| Commercial Zone | Zone 3x3 commercial | (Z/X to cycle) |
| Industrial Zone | Zone 3x3 industrial | (Z/X to cycle) |
| Fire Station | Place fire station | (Z/X to cycle) |
| Police Station | Place police station | (Z/X to cycle) |
| Power Plant (Coal) | Place coal plant | (Z/X to cycle) |
| Power Plant (Nuclear) | Place nuclear plant | (Z/X to cycle) |
| Stadium | Place stadium | (Z/X to cycle) |
| Seaport | Place seaport | (Z/X to cycle) |
| Airport | Place airport | (Z/X to cycle) |
| Park | Place park | (Z/X to cycle) |
| Query | Inspect tile info | Q |

### Map Window

The Map Window shows the **entire city** at a reduced scale. It supports multiple overlay modes:

| Overlay | Display |
|---------|---------|
| City Form | Default view; shows all zones, buildings, terrain |
| Power Grid | Highlights powered (lit) and unpowered (dark) areas |
| Transportation | Shows road and rail network |
| Population Density | Heat map of population (blue = low, red = high) |
| Growth Rate | Areas gaining (green) or losing (red) population |
| Traffic Density | Heat map of traffic congestion |
| Pollution | Heat map of pollution levels |
| Crime Rate | Heat map of crime levels |
| Land Value | Heat map of property values |
| Police Coverage | Radius overlay of police station effectiveness |
| Fire Coverage | Radius overlay of fire station effectiveness |

### Budget Window

Appears annually (unless Auto-Budget is on) or when manually opened:

```
+----------------------------------------+
| BUDGET WINDOW                          |
|                                        |
| Tax Rate: [<] 7% [>]                  |
| Tax Revenue: $4,200                    |
|                                        |
| Department Funding:                    |
|   Transportation: $852 / $852  [====] |
|   Police Dept:    $500 / $500  [====] |
|   Fire Dept:      $300 / $300  [====] |
|                                        |
| Cash Flow: +$2,548                     |
| Treasury: $22,548                      |
|                                        |
| [GO WITH THESE FIGURES]                |
+----------------------------------------+
```

- **Tax rate**: Adjustable from 0% to 20% using arrow buttons.
- **Department sliders**: Drag to set funding from 0% to 100% of requested amount.
- **GO WITH THESE FIGURES**: Confirms budget and advances the simulation.

### Graphs Window

Displays historical data on two time scales:

| Time Scale | Coverage |
|------------|----------|
| 10-year graph | Last 10 simulated years |
| 120-year graph | Last 120 simulated years |

Toggleable graph lines (click icons on left to show/hide):

| Graph Line | Color | Data |
|------------|-------|------|
| Residential | Green | Residential population over time |
| Commercial | Blue | Commercial population over time |
| Industrial | Yellow | Industrial population over time |
| Crime | Red | Crime rate average over time |
| Cash Flow | Cyan | Revenue minus expenses over time |
| Pollution | Brown | Pollution average over time |

### Evaluation Window

```
+----------------------------------------+
| EVALUATION WINDOW                      |
|                                        |
| Public Opinion:                        |
|   Is the mayor doing a good job?       |
|   YES: 62%    NO: 38%                 |
|                                        |
| What are the worst problems?           |
|   Crime .............. 22%             |
|   Traffic ............ 18%             |
|   Pollution .......... 15%             |
|   Housing costs ...... 11%             |
|                                        |
| Statistics:                            |
|   Population:    45,230               |
|   Net Migration: +1,250               |
|   Assessed Value: $128,000            |
|                                        |
| Category: City                         |
| Overall City Score: 612                |
+----------------------------------------+
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Q | Query tool (inspect tile) |
| B | Bulldozer tool |
| R | Road tool |
| T | Transit (rail) tool |
| P | Power line tool |
| Z / X | Cycle through tool icons (backward / forward) |
| Arrow keys | Scroll terrain in Edit Window |
| 0 | Pause game |
| 1 | Slow speed |
| 2 | Medium speed |
| 3 | Fast speed |
| Ctrl+S | Save city |
| Ctrl+L | Load city |
| Ctrl+N | New city |

---

## 16. Audio Design

### PC Speaker / AdLib / Sound Blaster Audio

The original 1989 DOS version has **minimal audio**:

| Sound | Trigger | Description |
|-------|---------|-------------|
| Bulldozer | Clearing a tile | Short mechanical crunch sound |
| Zone placement | Placing any zone | Brief stamp/thud sound |
| Road/rail placement | Placing infrastructure | Click/tap sound |
| Building placement | Placing buildings | Heavier thud |
| Disaster alarm | Disaster occurs | Warning siren / alert tone |
| Monster roar | Monster attack | Low growl (if sound card present) |
| Explosion | Meltdown / crash / bombing | Explosion burst |
| Error buzz | Cannot build here | Short buzz/rejection tone |
| Budget chime | Annual budget time | Bell/chime notification |

- The original DOS version relied primarily on **PC speaker beeps** for sound effects.
- Later versions with **AdLib** or **Sound Blaster** support had slightly richer sound effects.
- There is **no continuous background music** in the original DOS/PC version.

### SNES Version Audio (1991, for reference)

The SNES version, with music composed by **Soyo Oka** (Nintendo), features a full soundtrack:

| Track | Plays During | Mood |
|-------|-------------|------|
| Title Screen | Main menu | Upbeat, welcoming |
| Village theme | Population < 2,000 | Soothing, pastoral, slow tempo |
| Town theme | Population 2,000-9,999 | Slightly more energetic |
| City theme | Population 10,000-49,999 | Urban, increasing tempo |
| Capital theme | Population 50,000-99,999 | Bustling, complex |
| Metropolis theme | Population 100,000+ | Rapid, technological, mechanized |
| Disaster theme | During active disaster | Urgent, tense |
| Budget theme | Budget screen | Thoughtful, slower |
| Scenario clear | Scenario win | Triumphant fanfare |

- Music evolves with city size, becoming "more mechanized and technological" as population grows.
- Sound effects include construction sounds, disaster alerts, and ambient city noise.

---

## Appendix A: Complete Building & Item Cost Reference

| Item | Size | Cost | Annual Maintenance |
|------|------|------|--------------------|
| Bulldoze | 1x1 | $1 | -- |
| Road | 1x1 | $10 | $1/tile/year |
| Bridge (road over water) | 1x1 | $50 | $4/tile/year |
| Rail | 1x1 | $20 | $4/tile/year |
| Rail tunnel (over water) | 1x1 | $100 | $10/tile/year |
| Power line (land) | 1x1 | $5 | -- |
| Power line (water) | 1x1 | $25 | -- |
| Park | 1x1 | $10 | -- |
| Residential zone | 3x3 | $100 | -- |
| Commercial zone | 3x3 | $100 | -- |
| Industrial zone | 3x3 | $100 | -- |
| Police station | 3x3 | $500 | $100/year |
| Fire station | 3x3 | $500 | $100/year |
| Coal power plant | 4x4 | $3,000 | -- |
| Nuclear power plant | 4x4 | $5,000 | -- |
| Stadium | 4x4 | $3,000 | -- |
| Seaport | 4x4 | $5,000 | -- |
| Airport | 6x6 | $10,000 | -- |

---

## Appendix B: Difficulty Level Effects

| Parameter | Easy | Medium | Hard |
|-----------|------|--------|------|
| Starting funds | $20,000 | $20,000 | $20,000 |
| Tax revenue multiplier | 1.4x | 1.2x | 0.8x |
| Disaster frequency | Low | Normal | High |
| Nuclear meltdown | Never | Possible | More likely |
| Tax tolerance | High | Normal | Low |
| Citizen patience | Forgiving | Normal | Demanding |
| Road/rail deterioration | Slow | Normal | Fast |

---

## Appendix C: Map Overlay Data Ranges

| Overlay | Data Range | Low Color | High Color |
|---------|-----------|-----------|------------|
| Population density | 0-255 | Blue (empty) | Red (dense) |
| Traffic density | 0-255 | Green (clear) | Red (congested) |
| Pollution | 0-255 | Green (clean) | Brown/Red (polluted) |
| Crime rate | 0-255 (baseline 128) | Green (safe) | Red (dangerous) |
| Land value | 0-255 | Brown (worthless) | Blue/Green (valuable) |
| Police coverage | 0-1000 (effectiveness) | Red (uncovered) | Blue (covered) |
| Fire coverage | 0-1000 (effectiveness) | Red (uncovered) | Blue (covered) |

---

## Appendix D: SNES Gift Buildings (for reference)

The SNES version (1991) introduced reward buildings granted at population milestones or conditions. These are **not** in the original 1989 PC version but are documented for completeness.

| Gift | Quantity | Cost | Effect | Trigger |
|------|----------|------|--------|---------|
| Your House (Mayor's Mansion) | 1 | $100 | Raises local land value | Awarded early in gameplay |
| Bank | 1 | $100 | Allows $10,000 loan | Awarded at early population |
| Park (Large) | 3 | $100 each | Raises land value significantly | Population milestone |
| Zoo | 2 | $100 each | Raises land value | Population milestone |
| Library | 3 | $100 each | Raises land value | Population milestone |
| Fountain | 1 | $100 | Raises land value | Population milestone |
| Windmill | 2 | $100 each | Raises land value | Population milestone |
| Amusement Park | 5 | $100 each | Raises land value | Population milestone |
| Casino | 5 | $100 each | Generates income | Population milestone |
| Expo | 1 | $100 | Raises land value | High population |
| Train Station | 2 | $100 each | Improves transit | Population milestone |
| Fire Headquarters | 3 | $100 each | Extended fire coverage | Population milestone |
| Police Headquarters | 3 | $100 each | Extended police coverage | Population milestone |
| Land Fill | 9 | $100 each | Only gift that does NOT raise land value | Available throughout |
| Mario Statue | 1 | $100 | Special landmark | 500,000 population |

- All gift buildings occupy **3x3 tiles**.
- Maximum of **4 pending gifts** at a time; claim gifts before more can be awarded.

---

## Appendix E: Simulation Constants (from Micropolis Source)

| Constant | Value | Purpose |
|----------|-------|---------|
| WORLD_X | 120 | Map width in tiles |
| WORLD_Y | 100 | Map height in tiles |
| TAXFREQ | 48 | Simulation ticks between tax/evaluation cycles (1 game year) |
| HISTLEN | 480 | Length of history arrays (10 years at TAXFREQ resolution) |
| MISCHISTLEN | 240 | Length of miscellaneous history arrays |
| Birth rate | 0.02 | 2% of normalized residential population per year |
| LaborBase minimum | 1.3 | Minimum labor ratio for demand calculations |
| Internal market divisor | 3.7 | (ResPop + ComPop + IndPop) / 3.7 for commercial demand |
| RValve range | -2000 to +2000 | Residential demand valve bounds |
| CValve range | -1500 to +1500 | Commercial demand valve bounds |
| IValve range | -1500 to +1500 | Industrial demand valve bounds |
| RoadEffect max | 32 | Maximum road maintenance effectiveness |
| PoliceEffect max | 1000 | Maximum police effectiveness |
| FireEffect max | 1000 | Maximum fire effectiveness |
| Crime baseline | 128 | Starting crime value (midpoint of 0-255 byte) |
| FLevels[Easy] | 1.4 | Tax revenue multiplier for Easy |
| FLevels[Medium] | 1.2 | Tax revenue multiplier for Medium |
| FLevels[Hard] | 0.8 | Tax revenue multiplier for Hard |
| Score smoothing | 50/50 | New score averaged with previous score |
| Initial score | 500 | Starting city score for new cities |
| Population multiplier | 20 | Applied to zone population sum |
| Com/Ind weight | 8 | Commercial/Industrial zones weighted 8x in population calc |
| Density threshold for R-1 | 66 | Minimum population density for residential upgrade |
| R-4 population | 800 | Population of a fully developed R-4 zone |
| RTOP population | 1,920 | Population of merged RTOP zone |
| Small house population | 20 | Population per individual small house tile |
| Max small houses per zone | 8 | 8 houses = 160 pop before R-1 upgrade |

---

## Appendix F: Key Formulas Summary

### Tax Revenue
```
TaxFund = (TotalPop * LandValueAverage / 120) * CityTax * FLevels[GameLevel]
```

### Cash Flow
```
CashFlow = TaxFund - (PoliceFund + FireFund + RoadFund)
```

### Population
```
TotalPop = (ResPop + (ComPop + IndPop) * 8) * 20
NormResPop = ResPop / 8
Births = NormResPop * 0.02
Migration = NormResPop * (Employment - 1.0)
```

### City Score
```
ProblemScore = (250 - min(ProblemSum / 3, 250)) * 4
FinalScore = (ProblemScore_with_penalties + PreviousScore) / 2
```

### Crime Smoothing
```
CrimeRamp += (CrimeAverage - CrimeRamp) / 4
```

### Pollution Smoothing
```
PollutionRamp += (PollutionAverage - PollutionRamp) / 4
```

### Internal Market (Commercial)
```
IntMarket = (NormResPop + ComPop + IndPop) / 3.7
```
