# RollerCoaster Tycoon (Original) — Complete Game Specification

## 1. Game Overview

RollerCoaster Tycoon is a theme park management simulation where the player designs
rides, manages finances, hires staff, and keeps guests happy. The player builds and
manages an amusement park, placing rides, shops, paths, and scenery to attract guests
and earn money. Each scenario has specific objectives that must be met within a time limit.

Platform: Single-player, isometric 2D tile-based simulation.
Map size: Varies by scenario (typically 128x128 to 256x256 tiles).
Time unit: One game "month" per simulation tick. Game months are ~2 real seconds at normal speed.

## 2. Technical Foundation

### 2.1 Map Structure
- Grid: Variable size per scenario (e.g., 128x128)
- Height levels: 0-14 (each level = 2 meters equivalent)
- Each tile stores:
  - base_height: 0-14
  - surface_type: enum(GRASS, SAND, DIRT, ICE, ROCK, GRID, WATER)
  - path: optional path data
  - ride_track: optional track piece reference
  - scenery: optional scenery object
  - ownership: enum(OWNED, PURCHASABLE, NOT_FOR_SALE)
  - fence: optional edge fences

### 2.2 Coordinate System
- Isometric projection: 2:1 diamond tiles
- Tile size: 32x16 pixels (isometric)
- Height step: 8 pixels vertical offset per level

## 3. Ride System

### 3.1 Ride Categories

#### 3.1.1 Roller Coasters
| Coaster Type           | Base Cost | Excitement Base | Intensity Base | Nausea Base | Max Speed |
|-----------------------|-----------|-----------------|----------------|-------------|-----------|
| Junior Roller Coaster | $1,500    | 2.0             | 1.0            | 0.5         | 30 mph    |
| Wooden Roller Coaster | $3,000    | 4.0             | 3.0            | 2.0         | 55 mph    |
| Steel Roller Coaster  | $4,000    | 5.0             | 4.0            | 2.5         | 65 mph    |
| Corkscrew Coaster     | $4,500    | 5.5             | 5.0            | 4.0         | 60 mph    |
| Looping Coaster       | $5,000    | 6.0             | 5.5            | 4.5         | 60 mph    |
| Mine Train Coaster    | $3,500    | 4.5             | 3.5            | 2.0         | 50 mph    |
| Suspended Coaster     | $5,500    | 6.0             | 4.0            | 3.0         | 55 mph    |
| Stand-up Coaster      | $5,000    | 5.5             | 5.0            | 3.5         | 55 mph    |
| Bobsled Coaster       | $3,800    | 5.0             | 3.5            | 2.5         | 50 mph    |
| Inverted Coaster      | $6,000    | 7.0             | 6.0            | 5.0         | 65 mph    |

#### 3.1.2 Gentle Rides
| Ride Type            | Cost    | Excitement | Intensity | Nausea | Capacity |
|---------------------|---------|------------|-----------|--------|----------|
| Merry-Go-Round      | $1,000  | 2.5        | 0.8       | 0.3    | 16       |
| Ferris Wheel        | $1,500  | 3.0        | 0.5       | 0.2    | 24       |
| Haunted House       | $2,000  | 3.5        | 1.5       | 0.5    | 8        |
| Bumper Cars         | $1,200  | 2.8        | 1.2       | 0.8    | 12       |
| Spiral Slide        | $800    | 2.0        | 1.0       | 0.5    | 4        |
| Hedge Maze          | $1,500  | 3.0        | 0.3       | 0.0    | 20       |
| Observation Tower   | $2,500  | 3.5        | 0.5       | 0.1    | 16       |
| Miniature Railway   | $2,000  | 3.0        | 0.5       | 0.1    | 20       |
| Monorail            | $3,000  | 3.5        | 0.3       | 0.1    | 30       |

#### 3.1.3 Thrill Rides
| Ride Type            | Cost    | Excitement | Intensity | Nausea | Capacity |
|---------------------|---------|------------|-----------|--------|----------|
| Pirate Ship         | $2,000  | 4.0        | 3.5       | 2.0    | 20       |
| Gravitron           | $2,500  | 4.5        | 4.0       | 3.0    | 16       |
| Launched Freefall   | $3,000  | 5.0        | 5.5       | 3.0    | 4        |
| Scrambled Eggs      | $1,800  | 3.5        | 3.0       | 2.5    | 16       |
| Swinging Inverter   | $3,500  | 5.5        | 5.0       | 4.0    | 12       |
| Go Karts            | $2,000  | 4.0        | 2.5       | 1.0    | 8        |
| Top Spin            | $2,800  | 4.5        | 4.5       | 3.5    | 12       |

#### 3.1.4 Water Rides
| Ride Type            | Cost    | Excitement | Intensity | Nausea | Capacity |
|---------------------|---------|------------|-----------|--------|----------|
| Log Flume           | $2,500  | 4.5        | 2.5       | 1.5    | 4/boat   |
| River Rapids        | $3,000  | 4.0        | 3.0       | 1.5    | 8/raft   |
| Splash Boats        | $3,500  | 5.0        | 3.5       | 2.0    | 6/boat   |
| Water Slide         | $2,000  | 4.0        | 3.0       | 2.0    | 1        |
| Boat Hire           | $1,000  | 2.5        | 0.3       | 0.1    | 2/boat   |

### 3.2 Ride Statistics Calculation

#### 3.2.1 Excitement Rating
```
excitement = base_excitement
excitement += length_bonus          # +0.01 per 10 meters of track
excitement += speed_bonus           # +0.01 per 1 mph over 20 mph
excitement += drops_bonus           # +0.1 per drop
excitement += inversions_bonus      # +0.2 per inversion (max +2.0 at 10)
excitement += scenery_bonus         # +0.0 to +2.0 based on nearby scenery
excitement += variety_bonus         # +0.1 per unique track piece type
excitement -= age_penalty           # -0.02 per month of age (min 0)
excitement *= proximity_bonus       # x1.0-1.2 for nearby rides
```

#### 3.2.2 Intensity Rating
```
intensity = base_intensity
intensity += max_speed_factor       # +0.01 per 1 mph
intensity += max_g_force            # +0.5 per positive G above 2.0
intensity += inversions * 0.3
intensity += drops_height * 0.02
```

#### 3.2.3 Nausea Rating
```
nausea = base_nausea
nausea += lateral_g * 2.0           # Lateral G-forces are nausea-inducing
nausea += inversions * 0.15
nausea += spinning_factor
nausea += duration * 0.01           # Long rides increase nausea
```

#### 3.2.4 Rating Thresholds
| Rating    | Value Range | Guest Reaction          |
|-----------|------------|-------------------------|
| Very Low  | 0.0 - 2.0  | "Boring"               |
| Low       | 2.0 - 4.0  | "Not very exciting"    |
| Medium    | 4.0 - 6.0  | "Pretty good"          |
| High      | 6.0 - 8.0  | "Really exciting!"     |
| Very High | 8.0 - 10.0 | "Best ride ever!"      |
| Extreme   | 10.0+      | Too intense, avoided   |

### 3.3 Coaster Track Pieces
| Piece Type        | Cost/piece | Properties                      |
|-------------------|-----------|----------------------------------|
| Flat straight     | $50       | No elevation change              |
| Flat curve (45)   | $75       | 45-degree turn                   |
| Flat curve (90)   | $100      | 90-degree turn                   |
| Slope up (gentle) | $75       | +1 height level                  |
| Slope up (steep)  | $100      | +2 height levels                 |
| Slope down        | $75       | -1 height level                  |
| Chain lift        | $200      | Pulls train uphill               |
| Station           | $150      | Load/unload point                |
| Loop              | $500      | 360-degree vertical loop         |
| Corkscrew         | $400      | 360-degree barrel roll           |
| Half loop         | $300      | 180-degree vertical              |
| Helix (small)     | $350      | Tight spiral                     |
| Helix (large)     | $500      | Wide spiral                      |
| Banked curve      | $125      | Tilted curve                     |
| Brakes            | $100      | Reduces speed                    |
| Block brakes      | $150      | Allows multiple trains           |
| On-ride photo     | $200      | Generates photo revenue          |
| Boosters          | $300      | Increases speed                  |

### 3.4 Ride Pricing
```
suggested_price = (excitement * 0.5 + intensity * 0.2) * age_factor
age_factor = max(0.3, 1.0 - ride_age_months * 0.005)
max_price_guests_accept = suggested_price * 1.5
```

Price is in units of $0.10 (e.g., price=50 means $5.00).
Guests compare ride price to their perceived value based on excitement.

### 3.5 Ride Capacity and Throughput
```
hourly_throughput = (cars_per_train * seats_per_car * trains) / cycle_time_minutes * 60
cycle_time = track_length / avg_speed + load_time + unload_time
load_time = 5 + (seats_per_car * 0.5) seconds
```

## 4. Guest System

### 4.1 Guest Properties
Each guest (peep) has:
```
struct Guest {
    happiness: 0-255          // 128 = neutral
    hunger: 0-255             // 0 = full, 255 = starving
    thirst: 0-255             // 0 = not thirsty, 255 = very thirsty
    nausea: 0-255             // 0 = fine, 255 = about to vomit
    toilet_urgency: 0-255     // 0 = fine, 255 = desperate
    energy: 0-255             // 255 = full, 0 = exhausted
    cash: $20 - $100          // Random on entry
    ride_intensity_pref: 0-3  // 0=gentle, 1=moderate, 2=thrill, 3=extreme
    nausea_tolerance: 0-3     // Higher = less nausea from rides
    patience: 0-255           // How long they wait in queues
    favorite_ride: ride_id    // Set after riding
    name: string              // Random from name list
    thought_queue: list       // Recent thoughts (max 8)
}
```

### 4.2 Guest Behavior per Tick
```
hunger += 1 (every 30 ticks)
thirst += 1 (every 20 ticks)
toilet_urgency += 1 (every 60 ticks, faster after drinks)
energy -= 1 (every 40 ticks)
nausea -= 2 (natural decay)

if hunger > 150: seek food stall
if thirst > 150: seek drink stall
if toilet_urgency > 200: seek bathroom
if nausea > 170: may vomit (10% chance per tick)
if energy < 50: seek bench
if happiness < 40: may leave park
```

### 4.3 Guest Happiness Modifiers
| Event                    | Happiness Change |
|--------------------------|-----------------|
| Rode exciting ride       | +20 to +50      |
| Rode boring ride         | -5              |
| Waited too long in queue | -15             |
| Got lost                 | -10 per minute  |
| Vomited                  | -30             |
| Can't find bathroom      | -20             |
| Can't find food          | -15             |
| Path is dirty            | -5              |
| Path is crowded          | -3              |
| Saw vandalism            | -5              |
| Nice scenery nearby      | +5              |
| Won prize at stall       | +10             |
| Bought balloon           | +8              |
| Raining and no umbrella  | -10             |
| Ride broke down          | -15             |
| Found good deal          | +5              |

### 4.4 Guest Pathfinding
- A* algorithm on path network
- Guests have limited "memory" of 4 junctions
- If lost for > 5 minutes (game time), think "I'm lost!"
- Guests prefer wider paths
- Dead ends cause confusion

### 4.5 Guest Spawning
```
spawn_rate = base_rate * park_rating / 1000 * marketing_bonus
base_rate = 1 guest per 2 ticks
max_guests = scenario_limit (typically 1000-4000)
marketing_bonus = 1.0 + active_campaigns * 0.25
```

### 4.6 Guest Thoughts
Guests display thought bubbles:
- "I want to go on [ride name]"
- "I'm hungry"
- "I'm thirsty"
- "I need the bathroom"
- "[Ride name] was great value"
- "[Ride name] is too expensive"
- "I'm not paying that much for [food item]"
- "This path is disgusting"
- "I'm lost!"
- "I want to go home"
- "Help! I'm drowning!" (in water)
- "Just looking at [ride] makes me feel sick"

## 5. Shop and Stall System

### 5.1 Food Stalls
| Stall Type      | Cost  | Item Price Range | Hunger Reduction |
|----------------|-------|------------------|-----------------|
| Burger Bar     | $800  | $1.00 - $3.50    | -100            |
| Pizza Stall    | $850  | $1.00 - $3.50    | -120            |
| Candy Floss    | $600  | $0.50 - $2.00    | -50             |
| Popcorn Stall  | $600  | $0.50 - $2.00    | -60             |
| Hot Dog Stand  | $700  | $0.80 - $3.00    | -90             |
| Chicken Stall  | $800  | $1.00 - $3.50    | -110            |
| Cookie Shop    | $700  | $0.50 - $2.50    | -70             |

### 5.2 Drink Stalls
| Stall Type      | Cost  | Item Price Range | Thirst Reduction | Toilet Effect |
|----------------|-------|------------------|-----------------|---------------|
| Drinks Stall   | $600  | $0.50 - $2.50    | -120            | +50 urgency   |
| Coffee Shop    | $700  | $0.80 - $3.00    | -100            | +60 urgency   |
| Ice Cream      | $650  | $0.60 - $2.50    | -80             | +20 urgency   |

### 5.3 Other Stalls
| Stall Type      | Cost  | Item Price Range | Effect           |
|----------------|-------|------------------|-----------------|
| Balloon Stall  | $500  | $0.50 - $3.00    | +8 happiness    |
| Hat Stall      | $500  | $1.00 - $4.00    | Rain protection |
| T-Shirt Stand  | $600  | $2.00 - $5.00    | Souvenir        |
| Umbrella Stall | $500  | $1.00 - $5.00    | Rain protection |
| Map Stall      | $300  | $0.50 - $2.00    | Reduces "lost"  |
| Information    | $400  | Free              | Reduces "lost"  |
| First Aid      | $500  | Free              | -100 nausea     |
| Bathroom       | $400  | $0.00 - $1.00    | -255 urgency    |
| Photo Stall    | $500  | $1.00 - $4.00    | Souvenir        |

## 6. Staff System

### 6.1 Staff Types
| Staff Type     | Wage/month | Function                               |
|---------------|-----------|----------------------------------------|
| Handyman      | $50       | Sweeps paths, mows lawns, empties bins, waters gardens |
| Mechanic      | $80       | Inspects and fixes rides               |
| Security Guard| $60       | Reduces vandalism in patrol area       |
| Entertainer   | $55       | Increases guest happiness in area      |

### 6.2 Staff Behavior
Handyman tasks (prioritized):
1. Sweep vomit (highest priority)
2. Empty full litter bins
3. Sweep litter
4. Mow grass
5. Water gardens

Mechanic tasks:
1. Fix broken-down rides (immediate)
2. Inspect rides on schedule
3. Default inspection interval: every 10 minutes

### 6.3 Staff Patrol Areas
- Staff can be assigned patrol routes (series of path tiles)
- Without patrol: wander randomly
- With patrol: follow assigned path loop
- Patrol area is defined by clicking path tiles

### 6.4 Ride Breakdowns
```
breakdown_chance_per_tick = base_chance * age_factor * reliability_factor
base_chance = 0.001
age_factor = 1.0 + (ride_age_months * 0.01)
reliability_factor = 1.0 / (last_inspection_recency + 1)

// When breakdown occurs:
breakdown_type = random_choice([
    SAFETY_CUT_OUT,     // 40% - Ride stops, guests wait
    BRAKES_FAILURE,     // 10% - Dangerous, ride at max speed
    VEHICLE_MALFUNCTION,// 30% - One vehicle stops
    STATION_MALFUNCTION // 20% - Loading/unloading stops
])
```

## 7. Park Management

### 7.1 Park Rating (0-999)
```
rating = 0
for each guest in park:
    if guest.happiness > 128: rating += 2
    if guest.happiness > 200: rating += 1
    if guest.happiness < 64: rating -= 2
rating += unique_rides * 10
rating -= litter_count * 2
rating -= vomit_count * 4
rating -= vandalism_count * 3
rating -= broken_rides * 20
rating = clamp(rating, 0, 999)
```

### 7.2 Park Entrance Fee vs. Ride Fees
Two models:
1. **Pay-per-ride**: Park entrance free, charge per ride
2. **Pay-per-entry**: Charge entrance fee, rides free
3. **Hybrid**: Charge both (guests resist high prices in both)

```
// Pay-per-entry suggested price:
entrance_fee = total_ride_value * 0.1
// where total_ride_value = sum(ride.excitement * 10 for ride in rides)
```

### 7.3 Marketing Campaigns
| Campaign              | Cost/week | Duration | Effect                     |
|----------------------|-----------|----------|----------------------------|
| Park Entry Ads       | $200      | 6 weeks  | +50% guest spawn rate      |
| Ride Advertising     | $150      | 6 weeks  | Guests seek specific ride  |
| Vouchers (half-price)| $300      | 6 weeks  | Guests accept higher prices|
| Free Entry Vouchers  | $100      | 6 weeks  | +100% spawn, no entry fee  |

### 7.4 Research System
```
research_budget = $0 - $400 per month
research_categories = [ROLLER_COASTERS, THRILL_RIDES, GENTLE_RIDES, SHOPS, SCENERY, RIDE_IMPROVEMENTS]
research_speed = budget / 100  // points per tick
each unlock requires 200-1000 research points
```

Priority can be set to focus on one category.

### 7.5 Loan System
```
max_loan = $30,000 (scenario dependent)
interest_rate = 10% per year
minimum_repayment = $1,000 increments
monthly_interest = current_loan * 0.10 / 12
```

## 8. Financial System

### 8.1 Income Sources
```
ride_income = sum(ride.price * ride.riders_this_month for ride in rides)
shop_income = sum(shop.price * shop.sales_this_month for shop in shops)
entrance_income = entrance_fee * new_guests_this_month
on_ride_photo_income = photo_price * photos_sold
```

### 8.2 Expenses
```
ride_running_cost = sum(ride.running_cost for ride in operating_rides)
staff_wages = sum(staff.wage for staff in staff)
research_cost = research_budget
loan_interest = current_loan * 0.10 / 12
construction_cost = one-time costs
land_purchase = tile_cost * tiles_bought
marketing_cost = active_campaigns total
```

### 8.3 Financial Summary Window
```
+------------------------------------------+
|           FINANCIAL SUMMARY              |
+------------------------------------------+
| Income:                                  |
|   Ride tickets:         $2,450           |
|   Shop sales:           $1,230           |
|   Park entrance:        $3,200           |
|   On-ride photos:         $180           |
|   Total Income:         $7,060           |
|                                          |
| Expenses:                                |
|   Ride running costs:   $1,500           |
|   Staff wages:            $680           |
|   Research:               $200           |
|   Marketing:              $150           |
|   Loan interest:          $250           |
|   Total Expenses:       $2,780           |
|                                          |
| Profit:                 $4,280           |
| Cash:                  $15,620           |
| Loan:                  $10,000           |
+------------------------------------------+
```

## 9. Weather System

| Weather     | Probability | Effect                                     |
|------------|------------|---------------------------------------------|
| Sunny      | 40%        | Normal operations                           |
| Cloudy     | 25%        | Slight happiness reduction (-2)             |
| Light Rain | 15%        | Guests seek cover, -10 happiness            |
| Heavy Rain | 10%        | Guests leave outdoor queues, -20 happiness  |
| Thunder    | 5%         | Outdoor rides may shut down                 |
| Snow       | 5%         | Rare, -5 happiness, slower walking          |

Rain effects: Guests with umbrella: no penalty. Others: happiness drops.

## 10. Scenery System

### 10.1 Scenery Categories
| Category      | Items                              | Cost Range   | Effect             |
|--------------|------------------------------------|--------------|--------------------|
| Trees         | Oak, Pine, Palm, Willow (12 types) | $20-$80      | +scenery score     |
| Flowers       | Beds, pots, hanging baskets        | $15-$50      | +scenery score     |
| Fences        | Wood, iron, brick, hedge           | $5-$30/tile  | Path control       |
| Walls         | Stone, brick, wood panels          | $20-$60      | Theming            |
| Statues       | Small, medium, large               | $50-$500     | +scenery score     |
| Fountains     | Small, large, elaborate            | $100-$1000   | +scenery score     |
| Themed        | Castle, space, pirate, western     | $30-$200     | +ride excitement   |

### 10.2 Scenery Score Effect on Rides
```
nearby_scenery = count scenery items within 5 tiles of ride
scenery_value = sum(item.scenery_score for item in nearby_scenery)
excitement_bonus = min(2.0, scenery_value * 0.01)
```

## 11. Path System

### 11.1 Path Types
| Path Type       | Cost/tile | Width | Effect              |
|----------------|-----------|-------|---------------------|
| Tarmac         | $12       | 1     | Standard            |
| Crazy Paving   | $15       | 1     | Slightly decorative |
| Dirt Path      | $8        | 1     | Cheaper, less neat  |
| Queue Line     | $12       | 1     | For ride queues     |

### 11.2 Path Features
| Feature        | Cost  | Effect                            |
|---------------|-------|-----------------------------------|
| Litter Bin    | $30   | Guests use instead of littering   |
| Bench         | $25   | Guests rest, recover energy       |
| Lamp          | $40   | Illumination (aesthetic)          |
| Queue TV      | $200  | Reduces perceived queue wait      |

### 11.3 Queue System
```
queue_length = guests_in_queue
wait_time = queue_length * seconds_per_guest
seconds_per_guest = ride_cycle_time / ride_capacity
max_queue_wait_tolerance = guest.patience * 2 minutes
if wait_time > tolerance: guest leaves queue, happiness -= 15
```

## 12. Land and Construction

### 12.1 Land Modification
| Action           | Cost/tile | Effect                    |
|-----------------|-----------|---------------------------|
| Raise land      | $20       | +1 height level           |
| Lower land      | $20       | -1 height level           |
| Smooth land     | $10       | Average with neighbors    |
| Buy land        | $50-$200  | Expand park boundaries    |
| Build on water  | $100      | Place foundation          |

### 12.2 Construction Rights
- Some scenarios have land not for sale
- Construction rights allow building above land without owning it
- Cost: $40 per tile for rights only

## 13. Scenario System

### 13.1 Scenario Objectives
Typical objectives:
- "Have at least X guests in your park by end of Year Y"
- "Achieve a park rating of X by end of Year Y"
- "Have a park value of $X by end of Year Y"
- "Repay your loan and have park value of $X"

### 13.2 Example Scenarios
| Scenario        | Start Cash | Objective                          | Time  |
|----------------|-----------|-------------------------------------|-------|
| Forest Frontiers| $10,000   | 250 guests, end of Year 1           | 1 yr  |
| Dynamite Dunes | $10,000   | 650 guests, end of Year 3           | 3 yr  |
| Leafy Lake     | $10,000   | 500 guests, end of Year 3           | 3 yr  |
| Diamond Heights| $15,000   | Park value $40,000, end of Year 3   | 3 yr  |
| Evergreen Gdns | $10,000   | 1000 guests, end of Year 4          | 4 yr  |
| Bumbly Beach   | $10,000   | 900 guests, end of Year 3           | 3 yr  |
| Trinity Islands| $10,000   | Park value $50,000, end of Year 3   | 3 yr  |
| Katie's World  | $15,000   | 2000 guests, end of Year 4          | 4 yr  |
| Mega Park      | $50,000   | No objective, free build            | None  |

### 13.3 Scenario Unlock
Complete scenarios to unlock harder ones. Tree structure with branches.

## 14. UI Layout

```
+---------------------------------------------------------------------+
| Menu: [File] [View] [Options]                                        |
+---------------------------------------------------------------------+
| Toolbar:                                                             |
| [Pause|1x|2x] [Rides▼] [Shops▼] [Scenery▼] [Paths] [Land▼]        |
| [Staff] [Finances] [Research] [Map] [Guests] [Park Info] [Messages]  |
+---------------------------------------------------------------------+
|                                                                      |
|                     ISOMETRIC MAP VIEWPORT                           |
|                                                                      |
|                    /\    /\    /\                                     |
|                   /  \  /  \  /  \                                    |
|                  / G  \/ P  \/ G  \                                   |
|                  \    /\    /\    /                                    |
|                   \  /  \  /  \  /                                    |
|                    \/    \/    \/                                     |
|                                                                      |
|  [Scrollable with mouse drag, arrow keys, or edge scrolling]         |
|                                                                      |
+---------------------------------------------------------------------+
| Status: Cash: $15,620 | Guests: 342 | Rating: 756 | Date: Mar Yr 2 |
+---------------------------------------------------------------------+
```

### 14.1 Ride Window
```
+--------------------------------------+
| [Ride Name: Thunder Mountain]        |
+--------------------------------------+
| Status: OPEN                         |
| Excitement: 7.23 (High)             |
| Intensity:  5.81 (High)             |
| Nausea:     3.42 (Medium)           |
+--------------------------------------+
| Guests:     142 this month          |
| Income:     $426 this month         |
| Running cost: $120 this month       |
+--------------------------------------+
| Price: $5.00 [- ] [+ ]             |
| Mode:  [Continuous] [Shutdown]       |
| Cars:  3 trains, 6 cars each       |
+--------------------------------------+
| [Open/Close] [Test] [Demolish]       |
+--------------------------------------+
```

### 14.2 Guest Window
```
+-------------------------------+
| Guest: John Smith             |
+-------------------------------+
| Happiness: ████████░░ 80%    |
| Energy:    ██████░░░░ 60%    |
| Hunger:    ██░░░░░░░░ 20%    |
| Thirst:    ████░░░░░░ 40%    |
| Nausea:    ░░░░░░░░░░  0%    |
| Toilet:    █░░░░░░░░░ 10%    |
+-------------------------------+
| Cash: $45.60                  |
| Thinking: "I want to go on   |
|  Thunder Mountain"            |
| Rides ridden: 5              |
+-------------------------------+
```

## 15. Awards System

Annual awards given at end of each game year:
| Award                    | Condition                              |
|-------------------------|----------------------------------------|
| Most Beautiful Park     | Highest scenery score                  |
| Safest Park             | Fewest breakdowns                      |
| Best Value Park         | Highest guest satisfaction vs. price   |
| Most Exciting Park      | Highest avg ride excitement            |
| Tidiest Park            | Least litter                           |
| Best Food              | Most food stall variety                |
| Most Disappointing     | Lowest park rating (negative award)    |
| Untidiest Park         | Most litter (negative award)           |

## 16. Sound Design

| Event                    | Sound                    |
|--------------------------|--------------------------|
| Coaster climbing lift    | Click-click-click        |
| Coaster dropping         | Whoosh + screams         |
| Guest vomiting           | Splat sound              |
| Ride breakdown           | Mechanical failure       |
| Cash register            | Ka-ching                 |
| Rain starting            | Rain ambience            |
| Park award               | Fanfare                  |
| Guest applause           | Clapping                 |
| Balloon pop              | Pop                      |
| Merry-go-round           | Carousel music           |

## 17. Constants and Tuning

```
MAX_GUESTS = 4915
MAX_RIDES = 255
MAX_STAFF = 200
MAX_RIDE_PRICE = $20.00
MAX_ENTRANCE_FEE = $100.00
GUEST_STARTING_CASH_MIN = $20
GUEST_STARTING_CASH_MAX = $100
PATH_LITTER_DECAY_TICKS = 100
VOMIT_DECAY_TICKS = 200
RIDE_AGE_EXCITEMENT_DECAY = 0.005 per month
MECHANIC_WALK_SPEED = 2 tiles/tick
HANDYMAN_SWEEP_TIME = 3 ticks
GUEST_WALK_SPEED = 1 tile/tick
RAIN_HAPPINESS_PENALTY = -10 per tick (without umbrella)
BENCH_ENERGY_RECOVERY = +5 per tick
SCENERY_RADIUS = 5 tiles
MAX_LOAN = $30000 (scenario dependent)
INTEREST_RATE = 10%
```

## 18. Implementation Priority for AI Recreation

1. Tile-based map with height levels
2. Path placement and guest spawning
3. Pre-built flat rides (Merry-Go-Round, etc.)
4. Guest AI: needs, pathfinding, happiness
5. Shop/stall system
6. Financial tracking
7. Staff system
8. Roller coaster track builder
9. Ride statistics calculation
10. Research system
11. Weather system
12. Scenery and its effects
13. Scenario objectives and awards
14. Marketing campaigns
