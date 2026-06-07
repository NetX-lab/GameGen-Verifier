# Tiny Tower — Complete Game Specification

## 1. Game Overview

Tiny Tower is a vertical tower-building simulation where the player constructs floors,
stocks shops, assigns residents (Bitizens) to jobs, and manages a growing skyscraper.
The game is idle/incremental in nature — businesses earn money over time, and the player
makes strategic decisions about floor placement, staffing, and resource allocation. The
game is open-ended with no win condition.

Platform: Single-player, 2D side-view vertical scrolling.
Visual style: Pixel art with tiny character sprites (Bitizens).
Simulation tick: Real-time with idle mechanics (earnings continue offline).

## 2. Technical Foundation

### 2.1 Core Data Structures
```
struct Tower {
    floors: list[Floor]          // Index 0 = lobby, 1+ = built floors
    max_floor: integer           // Current highest floor (starts at 1)
    bux: integer                 // Premium currency (Tower Bux)
    coins: integer               // Standard currency
    bitizens: list[Bitizen]
    elevator: Elevator
    construction_floor: Floor | null  // Floor being built
    vip_queue: list[VIP]
}

struct Floor {
    number: integer              // 1-based
    type: FloorType              // RESIDENTIAL, FOOD, SERVICE, RECREATION, RETAIL, CREATIVE
    business: Business | null    // null for residential
    residents: list[Bitizen]     // For residential floors (max 5)
    stock: list[StockItem]       // For business floors (3 items)
    is_built: boolean
    construction_time_remaining: integer  // In seconds
    upgrade_level: 0-3
}

struct Bitizen {
    name: string
    appearance: SpriteData       // Randomized pixel appearance
    dream_job: FloorType         // Category they dream of working in
    skill_food: 0-9
    skill_service: 0-9
    skill_recreation: 0-9
    skill_retail: 0-9
    skill_creative: 0-9
    current_floor: integer       // Where they live
    employed_floor: integer      // Where they work (-1 if unemployed)
    happiness: 0-100
}
```

### 2.2 Currency System
- **Coins**: Primary currency. Earned from businesses. Used to build floors and stock items.
- **Tower Bux (Bux)**: Premium currency. Earned slowly from gameplay or purchased. Used to speed up timers, buy special items.

## 3. Floor System

### 3.1 Floor Types
| Type         | Color   | Purpose                            | Businesses Per Floor |
|-------------|---------|-------------------------------------|---------------------|
| Residential | Green   | Houses Bitizens (up to 5)          | N/A                 |
| Food        | Red     | Food businesses                     | 1 business, 3 items |
| Service     | Orange  | Service businesses                  | 1 business, 3 items |
| Recreation  | Purple  | Entertainment businesses            | 1 business, 3 items |
| Retail      | Yellow  | Retail shops                        | 1 business, 3 items |
| Creative    | Blue    | Creative businesses                 | 1 business, 3 items |

### 3.2 Construction Costs
| Floor Number | Cost (Coins) |
|-------------|-------------|
| 1-5         | 1,000       |
| 6-10        | 5,000       |
| 11-15       | 15,000      |
| 16-20       | 35,000      |
| 21-25       | 75,000      |
| 26-30       | 150,000     |
| 31-40       | 300,000     |
| 41-50       | 500,000     |
| 51+         | 750,000 + (floor - 50) * 50,000 |

Formula: `cost = base_cost[tier] + tier_increment * (floor_in_tier - 1)`

### 3.3 Construction Time
```
construction_time_seconds = floor_number * 30 * 60  // 30 minutes per floor level
// Floor 1: 30 minutes
// Floor 10: 5 hours
// Floor 20: 10 hours
// Floor 50: 25 hours
// Can be skipped with Tower Bux (1 Bux per 1 minute remaining)
```

### 3.4 Floor Upgrade
Each business floor can be upgraded (paint/decoration):
| Upgrade Level | Cost (Bux) | Effect                    |
|--------------|-----------|---------------------------|
| 1            | 3 Bux     | +10% stock capacity       |
| 2            | 5 Bux     | +25% stock capacity       |
| 3            | 8 Bux     | +50% stock capacity       |

## 4. Business System

### 4.1 Business Examples by Category

#### Food Businesses
| Business         | Item 1 (Cost/Stock/Profit) | Item 2                   | Item 3                    |
|-----------------|----------------------------|--------------------------|---------------------------|
| Sushi Bar       | Miso Soup (6/50/12)       | Sashimi (75/25/180)     | Dragon Roll (800/10/2000)|
| Pub             | Nachos (4/60/8)           | Fish & Chips (50/30/120)| Steak (600/12/1500)      |
| Bakery          | Bread (3/80/5)            | Cake (40/35/90)         | Wedding Cake (500/8/1200)|
| Pizza Place     | Slice (5/55/10)           | Whole Pizza (60/28/150) | Calzone (700/10/1800)    |
| Burger Barn     | Fries (3/70/6)            | Burger (45/32/100)      | Combo Meal (550/12/1400) |

#### Service Businesses
| Business         | Item 1                    | Item 2                   | Item 3                    |
|-----------------|---------------------------|--------------------------|---------------------------|
| Barber Shop     | Trim (5/50/10)           | Style (60/25/150)       | Full Service (600/10/1500)|
| Bank            | Checking (8/45/15)       | Savings (80/20/200)     | Investment (900/8/2200)  |
| Dentist         | Cleaning (10/40/20)      | Filling (100/18/250)    | Root Canal (1000/6/2500) |
| Law Office      | Consult (12/35/25)       | Contract (120/15/300)   | Trial (1200/5/3000)      |

#### Retail Businesses
| Business         | Item 1                    | Item 2                   | Item 3                    |
|-----------------|---------------------------|--------------------------|---------------------------|
| Book Store      | Paperback (4/60/8)       | Hardcover (50/30/120)   | Rare Book (500/10/1200)  |
| Toy Store       | Puzzle (6/55/12)         | Board Game (70/25/170)  | Collector (750/8/1800)   |
| Fashion Store   | T-Shirt (5/50/10)        | Dress (80/22/200)       | Designer (800/6/2000)    |

### 4.2 Stocking Mechanics
```
stock_time[item_tier] = {
    tier_1: 1 * 60,        // 1 minute
    tier_2: 10 * 60,       // 10 minutes
    tier_3: 60 * 60,       // 1 hour (60 minutes)
}

// Stocking costs coins (the "Cost" in tables above)
// When stock is ready, it sells automatically over time
// Sell rate depends on floor traffic and Bitizen skill

sell_rate_per_minute = base_rate * (1 + assigned_bitizen_skill * 0.1)
base_rate = 1 unit per 2 minutes

revenue_per_unit = profit value from table
```

### 4.3 Dream Job Bonus
If a Bitizen works at a business matching their dream job category:
- All items on that floor stock **double quantity**
- +1 Tower Bux reward when they start working there

### 4.4 Staffing
- Each business floor can have up to 3 workers
- More workers = more items can be stocked simultaneously
- Workers with higher relevant skill increase sell rate:
  ```
  effective_output = base * (1 + worker_skill * 0.1)
  ```

## 5. Bitizen System

### 5.1 Bitizen Generation
When a residential floor has vacancy, new Bitizens arrive via elevator.
```
bitizen.name = random_from(name_database)
bitizen.appearance = random_pixel_sprite()
bitizen.dream_job = random_choice(FOOD, SERVICE, RECREATION, RETAIL, CREATIVE)
bitizen.skills = [random(0,9) for _ in range(5)]  // One per category
bitizen.happiness = 50
```

### 5.2 Happiness
```
happiness = 50  // base
if employed: happiness += 20
if dream_job_match: happiness += 30
happiness += floor_upgrade_level * 5
if unemployed: happiness -= 10 per day
```

### 5.3 Eviction
Player can evict Bitizens from residential floors.
Eviction frees the slot for new arrivals. No penalty.

## 6. Elevator System

### 6.1 Elevator Mechanics
- The player manually operates the elevator by tapping/clicking
- Bitizens appear in the lobby wanting to go to specific floors
- Player moves elevator to lobby, picks up Bitizen, takes to destination
- Tip received based on distance traveled

### 6.2 Elevator Tipping
```
tip_coins = floor_destination * 10
tip_bux_chance = 0.05  // 5% chance of receiving 1 Bux instead
```

### 6.3 Elevator Upgrades
| Elevator Level | Cost (Bux) | Speed     | Capacity |
|---------------|-----------|-----------|----------|
| 1             | Free      | Slow      | 1        |
| 2             | 5 Bux     | Medium    | 1        |
| 3             | 10 Bux    | Fast      | 1        |
| 4             | 25 Bux    | Very Fast | 1        |
| 5             | 50 Bux    | Lightning | 1        |

Speed values:
```
elevator_speed[level] = {
    1: 1 floor per 2 seconds,
    2: 1 floor per 1.5 seconds,
    3: 1 floor per 1 second,
    4: 1 floor per 0.5 seconds,
    5: 1 floor per 0.25 seconds
}
```

## 7. VIP System

### 7.1 VIP Types
VIPs appear occasionally at the lobby and provide special bonuses:
| VIP Type        | Effect                                          | Frequency  |
|----------------|------------------------------------------------|------------|
| Big Spender    | Buys out all stock on one floor (full revenue)  | Common     |
| Construction   | Reduces construction time by 3 hours            | Common     |
| Celebrity      | Moves all customers to one floor (+sales)       | Uncommon   |
| Real Estate    | Moves in 1 Bitizen instantly (max dream skill)  | Rare       |
| Inspector      | Doubles earnings on one floor for 24 hours      | Rare       |

### 7.2 VIP Delivery
Player must deliver VIP via elevator to the appropriate floor.
VIP effect triggers upon arrival.

## 8. Missions System

### 8.1 Mission Types
| Mission Type            | Example                              | Reward       |
|------------------------|--------------------------------------|-------------|
| Stock items            | "Stock 3 items at Sushi Bar"         | 1-3 Bux     |
| Deliver Bitizens       | "Deliver 5 Bitizens via elevator"    | 1-2 Bux     |
| Build floors           | "Build 2 new floors"                 | 2-5 Bux     |
| Find Bitizen           | "Find where [name] is hiding"        | 1 Bux       |
| Employ Bitizens        | "Employ 3 Bitizens at dream jobs"    | 2-3 Bux     |
| Earn coins             | "Earn 10,000 coins"                  | 1-3 Bux     |
| Fully stock            | "Fully stock 5 business floors"      | 2-4 Bux     |

### 8.2 Mission Refresh
- One active mission at a time
- New mission every 4-8 hours (real time)
- Can skip with 1 Bux

## 9. Idle Mechanics

### 9.1 Offline Earnings
When player is away:
```
offline_earnings = sum(
    floor.sell_rate * floor.current_stock * time_offline
    for floor in business_floors
    if floor.stock > 0
)
// Capped at 8 hours of offline earnings
// Stock depletes while offline
```

### 9.2 Notifications
Push notifications for:
- Construction complete
- Floor fully stocked
- New Bitizen arrived
- VIP waiting in lobby
- Mission available

## 10. Tower Cosmetics

### 10.1 Roof Styles
| Roof         | Cost (Bux) |
|-------------|-----------|
| Default     | Free      |
| Castle      | 5         |
| Pyramid     | 8         |
| Dome        | 10        |
| Spire       | 15        |
| Modern      | 12        |

### 10.2 Elevator Skins
| Skin        | Cost (Bux) |
|------------|-----------|
| Default    | Free      |
| Gold       | 10        |
| Glass      | 8         |
| Neon       | 12        |
| Wooden     | 6         |

### 10.3 Lobby Decorations
Various decorations can be placed in the lobby for Bux.

## 11. Economy Balance

### 11.1 Coin Income Rates (per minute, per business)
```
income_rate = sum(
    item.profit * sell_rate * stock_available
    for item in floor.items
)

// Typical income per floor per hour:
// Early game (floor 1-10): 100-500 coins/hour
// Mid game (floor 11-30): 500-2000 coins/hour
// Late game (floor 30+): 2000-5000 coins/hour
```

### 11.2 Bux Earning Rates
- Elevator tips: ~1 Bux per 20 deliveries (5% chance)
- Missions: ~3 Bux per 6 hours
- Finding hidden Bitizens: 1 Bux each
- Dream job placement: 1 Bux each
- Total natural rate: ~5-10 Bux per day of active play

### 11.3 Bux Spending
- Speed up construction: 1 Bux per minute skipped
- Elevator upgrades: 5-50 Bux
- Floor upgrades: 3-8 Bux
- Convert to coins: 1 Bux = 1,000 coins (early), scaling up
- Cosmetics: 5-15 Bux each

## 12. Progression Milestones

| Floors Built | Milestone                    | Reward        |
|-------------|------------------------------|---------------|
| 5           | "Small Tower"                | 5 Bux         |
| 10          | "Growing Up"                 | 10 Bux        |
| 20          | "Getting Tall"               | 15 Bux        |
| 30          | "Skyscraper"                 | 20 Bux        |
| 50          | "Mega Tower"                 | 50 Bux        |
| 75          | "Cloud Piercer"              | 75 Bux        |
| 100         | "Stratosphere"               | 100 Bux       |
| 150         | "Space Elevator"             | 200 Bux       |
| 200         | "Legendary Tower"            | 500 Bux       |

## 13. UI Layout

### 13.1 Main Screen
```
+------------------------+
|  Coins: 245,000        |
|  Bux: 23               |
+------------------------+
|                        |
|  Floor 15: [Fashion]   |
|  ┌──────────────────┐  |
|  │ 👗 👔 🎩        │  |
|  │ OPEN  ███░░░░░░  │  |
|  └──────────────────┘  |
|                        |
|  Floor 14: [Dentist]   |
|  ┌──────────────────┐  |
|  │ 🦷 💊 🪥        │  |
|  │ OPEN  █████░░░░  │  |
|  └──────────────────┘  |
|                        |
|  Floor 13: [Apartment] |
|  ┌──────────────────┐  |
|  │ 👤👤👤👤░        │  |
|  │ 4/5 residents     │  |
|  └──────────────────┘  |
|                        |
|  ...                   |
|                        |
|  Floor 1: [LOBBY]      |
|  ┌──────────────────┐  |
|  │ 🛗 👤👤           │  |
|  │ [Waiting: Fl 12]  │  |
|  └──────────────────┘  |
|                        |
+------------------------+
| [Menu] [Build] [Stock] |
| [Bitz] [Missions]      |
+------------------------+
```

### 13.2 Floor Detail View
```
+----------------------------------+
|  SUSHI BAR  (Floor 7)           |
+----------------------------------+
|  Workers: 3/3                    |
|  ┌─────────────────────────────┐ |
|  │ Worker 1: Kenji (Skill: 8) │ |
|  │ Worker 2: Amy (Skill: 5)   │ |
|  │ Worker 3: Bob (Skill: 3)   │ |
|  └─────────────────────────────┘ |
|                                  |
|  Stock:                          |
|  1. Miso Soup   ████████░░ 40/50|
|     Revenue: $12/unit            |
|                                  |
|  2. Sashimi     ███░░░░░░░ 8/25 |
|     Revenue: $180/unit           |
|     [RESTOCK $75]                |
|                                  |
|  3. Dragon Roll ░░░░░░░░░░ 0/10 |
|     Revenue: $2,000/unit         |
|     [RESTOCK $800]               |
|                                  |
|  [Upgrade Floor] [Rename]        |
+----------------------------------+
```

### 13.3 Bitizen Profile
```
+----------------------------------+
|  BITIZEN: Sarah Johnson          |
|  [pixel sprite image]            |
+----------------------------------+
|  Dream Job: Creative ★           |
|  Lives on: Floor 13              |
|  Works at: Fashion Store (Fl 15) |
|  Happiness: ████████░░ 80%       |
+----------------------------------+
|  Skills:                         |
|  Food:       ██░░░░░░░░  2      |
|  Service:    ████░░░░░░  4      |
|  Recreation: █████░░░░░  5      |
|  Retail:     ███████░░░  7      |
|  Creative:   █████████░  9  ★   |
+----------------------------------+
|  [Move In] [Evict] [Assign Job]  |
+----------------------------------+
```

## 14. Social Features (Simplified for AI)

### 14.1 Visit Friends
- Visit other towers (simulated)
- Find hidden Bitizens in friend's towers for Bux

### 14.2 Bitizen Gifting
- Send unwanted Bitizens to friends
- Receive Bitizens with specific dream jobs

## 15. Sound Design

| Event                  | Sound                   |
|-----------------------|-------------------------|
| Elevator moving       | Mechanical whir         |
| Elevator arrives      | Ding                    |
| Item stocked          | Cash register           |
| Floor built           | Construction completion |
| Bitizen arrives       | Welcome chime           |
| VIP arrives           | Special fanfare         |
| Mission complete      | Achievement sound       |
| Stock depleted        | Warning tone            |

## 16. Constants and Tuning

```
MAX_FLOORS = 200+ (effectively unlimited)
MAX_RESIDENTS_PER_FLOOR = 5
MAX_WORKERS_PER_BUSINESS = 3
ITEMS_PER_BUSINESS = 3
SKILL_RANGE = 0-9
HAPPINESS_RANGE = 0-100
BASE_SELL_RATE = 1 unit per 2 minutes
ELEVATOR_TIP_PER_FLOOR = 10 coins
BUX_TIP_CHANCE = 0.05
OFFLINE_CAP_HOURS = 8
DREAM_JOB_STOCK_MULTIPLIER = 2.0
DREAM_JOB_BUX_REWARD = 1
MISSION_COOLDOWN_HOURS = 4-8
CONSTRUCTION_TIME_PER_FLOOR = 1800 seconds (30 min) per floor number
BUX_TO_COINS_RATE = 1000 (base, scales)
VIP_SPAWN_INTERVAL = 600 seconds (10 minutes average)
```

## 17. Implementation Priority for AI Recreation

1. Tower rendering with scrollable floors
2. Floor construction system
3. Business placement and stocking
4. Coin economy (earning and spending)
5. Bitizen spawning and assignment
6. Elevator mechanic (manual delivery)
7. Skill system and dream job matching
8. Idle income calculation
9. Tower Bux economy
10. VIP system
11. Missions
12. Floor upgrades
13. Elevator upgrades
14. Cosmetics
15. Offline earnings calculation
16. Milestones and progression
