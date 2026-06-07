# Kairosoft Game Dev Story — Complete Game Specification

## 1. Game Overview

Game Dev Story is a retro-styled game development simulation by Kairosoft. The player
manages a small game studio, hiring staff, developing games across genres and platforms,
attending conventions, and growing from a tiny startup to an award-winning studio. The
game runs for 20 in-game years, after which a final score is tallied.

Platform: Single-player, pixel-art menu-driven simulation.
Game length: 20 in-game years. Each year ~5 minutes real time.
Simulation tick: 1 game week (displayed as progress bars advancing).

## 2. Technical Foundation

### 2.1 Game State
```
struct GameState {
    company_name: string
    cash: integer              // Starting: 500,000 (yen-like currency)
    fans: integer              // Starting: 0
    year: 1-20
    month: 1-12
    week: 1-4
    staff: list[Employee]      // Max 8
    released_games: list[Game]
    hall_of_fame_entries: list
    annual_awards: list
    office_items: list[Item]
    research_data: integer     // Accumulated research points
    current_project: Game | null
    contractor_pool: list[Contractor]
}
```

### 2.2 Time System
- 4 weeks per month
- 12 months per year
- 20 years total
- Speed: Normal, 2x, 4x

## 3. Staff System

### 3.1 Employee Properties
```
struct Employee {
    name: string
    salary: integer           // Per month (5,000 - 80,000)
    level: 1-5
    job_class: JobClass
    program: float            // Programming skill (1-200+)
    scenario: float           // Scenario writing skill (1-200+)
    graphics: float           // Art skill (1-200+)
    sound: float              // Sound/music skill (1-200+)
    stamina: 0-100            // Depletes during work
    energy: 0-100             // Overall condition
    motivation: 0-200         // Affects output quality
    experience: integer       // Total XP accumulated
    research: float           // Research skill (1-200+)
}
```

### 3.2 Job Classes
| Class       | Prog Mult | Scen Mult | Graph Mult | Sound Mult | Unlock     |
|------------|-----------|-----------|------------|------------|------------|
| Coder      | 1.5       | 0.5       | 0.5        | 0.5        | Start      |
| Writer     | 0.5       | 1.5       | 0.5        | 0.5        | Start      |
| Designer   | 0.5       | 0.5       | 1.5        | 0.5        | Start      |
| Sound Eng  | 0.5       | 0.5       | 0.5        | 1.5        | Start      |
| Producer   | 1.0       | 1.0       | 1.0        | 1.0        | Level 3    |
| Director   | 1.2       | 1.2       | 0.8        | 0.8        | Level 4    |
| Hacker     | 2.0       | 0.3       | 0.3        | 0.3        | Level 5    |
| Hardware E | 1.8       | 0.3       | 0.5        | 0.3        | Special    |

### 3.3 Leveling Up
```
xp_needed[level] = {1: 0, 2: 100, 3: 300, 4: 700, 5: 1500}
// Staff gain XP from working on games
xp_per_game = game_quality * 10 + game_size * 20
// At each level: all skills += random(3, 8)
// Can change job class at level up
```

### 3.4 Hiring
- 3-5 candidates shown at a time
- Refresh costs $10,000
- Each candidate has:
  - Visible stats (skills, salary demand, level)
  - Hidden potential (growth rate multiplier: 0.8-1.5)

### 3.5 Contractors (Outsourcing)
| Contractor   | Cost     | Skill Level | Duration |
|-------------|----------|-------------|----------|
| Newbie       | $10,000  | Low (20-40) | 4 weeks  |
| Average      | $30,000  | Mid (40-80) | 4 weeks  |
| Expert       | $80,000  | High (80-150)| 4 weeks |
| Famous       | $150,000 | Very High (150+)| 4 weeks|

Contractors work on one phase of development, then leave.

## 4. Game Development

### 4.1 Creating a Game
Player selects:
1. **Genre** (from unlocked list)
2. **Type** (from unlocked list)
3. **Platform** (from available consoles)
4. **Direction** (Quality Focus vs Speed Focus)
5. **Staff Assignment** (who works on it)

### 4.2 Genres
| Genre         | Unlock      | Fun Weight | Creativity Weight | Graphics Weight | Sound Weight |
|--------------|-------------|------------|-------------------|-----------------|--------------|
| Action       | Start       | 0.3        | 0.2               | 0.3             | 0.2          |
| Simulation   | Start       | 0.3        | 0.3               | 0.2             | 0.2          |
| RPG          | Year 2      | 0.2        | 0.3               | 0.2             | 0.3          |
| Adventure    | Year 2      | 0.2        | 0.4               | 0.2             | 0.2          |
| Shooter      | Year 3      | 0.4        | 0.1               | 0.3             | 0.2          |
| Racing       | Year 3      | 0.3        | 0.1               | 0.4             | 0.2          |
| Puzzle       | Year 4      | 0.4        | 0.3               | 0.1             | 0.2          |
| Board Game   | Year 5      | 0.3        | 0.3               | 0.2             | 0.2          |
| Trivia       | Year 6      | 0.2        | 0.4               | 0.1             | 0.3          |
| Audio Novel  | Year 7      | 0.1        | 0.3               | 0.1             | 0.5          |
| Online RPG   | Year 12     | 0.2        | 0.2               | 0.3             | 0.3          |
| Dating Sim   | Year 8      | 0.1        | 0.5               | 0.2             | 0.2          |
| Table Game   | Year 9      | 0.3        | 0.3               | 0.2             | 0.2          |
| Card Game    | Year 10     | 0.3        | 0.3               | 0.2             | 0.2          |

### 4.3 Types
| Type          | Unlock      | Compatibility Notes        |
|--------------|-------------|----------------------------|
| Historical   | Start       | Good with RPG, Strategy    |
| Fantasy      | Start       | Good with RPG, Action      |
| Pirate       | Year 2      | Good with Action, Adventure|
| Ninja        | Year 3      | Good with Action           |
| Robot        | Year 3      | Good with Shooter, Action  |
| Sports       | Year 4      | Good with Racing, Sim      |
| Horse Racing | Year 4      | Good with Sim, Racing      |
| War          | Year 5      | Good with Shooter, Strategy|
| Dance        | Year 6      | Good with Puzzle, Sim      |
| Fashion      | Year 6      | Good with Sim, Adventure   |
| Space        | Year 7      | Good with Shooter, RPG     |
| Monster      | Year 8      | Good with RPG, Action      |
| Pop Star     | Year 9      | Good with Sim, Audio Novel |
| Detective    | Year 10     | Good with Adventure        |
| Anime        | Year 11     | Good with Dating Sim, RPG  |
| Dungeon      | Year 12     | Good with RPG, Action      |
| Train        | Year 13     | Good with Sim, Puzzle      |
| Mushroom     | Year 14     | Good with Action, Puzzle   |
| Mahjong      | Year 15     | Good with Table, Board     |
| Mini Game    | Year 16     | Good with Puzzle, Casual   |
| Town         | Year 17     | Good with Sim, Strategy    |
| Word         | Year 18     | Good with Puzzle, Trivia   |
| Comics       | Year 19     | Good with Adventure, Action|
| Game Co      | Year 20     | Good with Sim              |

### 4.4 Genre-Type Compatibility
Each genre-type pair has a compatibility rating: Bad (0.5), OK (0.8), Good (1.0), Great (1.3)

The compatibility affects the final review score multiplicatively.

### 4.5 Development Phases
Development has 4 phases, each lasting ~3-6 weeks depending on direction:

| Phase      | Primary Stat | Secondary Stat | Duration (Quality) | Duration (Speed) |
|-----------|-------------|----------------|--------------------|--------------------|
| Proposal  | Scenario    | Graphics       | 3 weeks            | 2 weeks            |
| Graphics  | Graphics    | Sound          | 5 weeks            | 3 weeks            |
| Sound     | Sound       | Program        | 4 weeks            | 2 weeks            |
| Debug     | Program     | Scenario       | 4 weeks            | 2 weeks            |

### 4.6 Point Generation
Each week during a phase:
```
for each staff member working:
    base_output = staff.relevant_skill * job_class_multiplier
    motivation_bonus = staff.motivation / 100
    stamina_factor = staff.stamina / 100

    points_generated = base_output * motivation_bonus * stamina_factor * direction_mult
    // direction_mult: Quality=1.2 (slower), Speed=0.8 (faster)

    game.fun_points += points_generated * genre.fun_weight
    game.creativity_points += points_generated * genre.creativity_weight
    game.graphics_points += points_generated * genre.graphics_weight
    game.sound_points += points_generated * genre.sound_weight

    staff.stamina -= 5
    if staff.stamina < 20: output *= 0.5
```

### 4.7 Bugs
```
bugs_generated = total_points * 0.02 * (1 / avg_program_skill)
bugs_fixed_in_debug = debug_phase_program_points * 0.5
final_bugs = max(0, bugs_generated - bugs_fixed_in_debug)
bug_penalty = final_bugs * 0.3  // Applied to review score
```

## 5. Review System

### 5.1 Review Score Calculation
```
base_score = (fun + creativity + graphics + sound) / expected_total * 10

// Apply modifiers
score *= genre_type_compatibility  // 0.5 - 1.3
score *= platform_fit             // 0.7 - 1.2
score -= bug_penalty
score *= sequel_factor            // 0.8 - 1.2
score *= novelty_factor           // 1.0 first time, 0.9 same combo, 0.8 third time

// 4 reviewers each give scores
reviewer_scores = [
    clamp(score + random(-1, 1), 1, 10) for _ in range(4)
]
// Scores are integers 1-10 (displayed as X/10)
```

### 5.2 Review Presentation
4 reviewers, each giving 1-10 score (integers).
Perfect score: 40/40 (all reviewers give 10).

### 5.3 Sales Calculation
```
base_sales = platform_install_base * review_factor * fan_factor
review_factor = (avg_score / 10) ^ 3  // Cubic curve, high scores sell way more
fan_factor = 1.0 + log10(fans + 1) * 0.2
genre_popularity = current_trend_multiplier  // 0.5 - 2.0

total_sales = base_sales * genre_popularity
revenue = total_sales * price_per_unit
price_per_unit = 3000 - 8000 (platform dependent)
```

Sales occur over 12 weeks post-release with front-loaded distribution.

## 6. Platform System

### 6.1 Console Timeline
| Console        | Real Equivalent | Year Available | Year Discontinued | License Cost | Install Base |
|---------------|-----------------|---------------|-------------------|-------------|-------------|
| PC             | PC             | Y1            | Y20               | Free        | 500K        |
| IES            | NES            | Y1            | Y6                | 50,000      | 2M          |
| Sonis          | Genesis        | Y3            | Y9                | 80,000      | 1.5M        |
| Super IES      | SNES           | Y4            | Y10               | 100,000     | 3M          |
| GameKid        | Game Boy       | Y3            | Y11               | 60,000      | 4M          |
| Intendro 64    | N64            | Y8            | Y14               | 120,000     | 2M          |
| PlayStatus     | PlayStation    | Y9            | Y16               | 150,000     | 5M          |
| Dcast          | Dreamcast      | Y12           | Y15               | 100,000     | 1M          |
| PlayStatus 2   | PS2            | Y14           | Y20               | 200,000     | 8M          |
| GBox           | Xbox           | Y14           | Y20               | 180,000     | 3M          |
| Exodus         | GameCube       | Y14           | Y20               | 150,000     | 2M          |
| GameKid 2      | GBA/DS         | Y12           | Y20               | 100,000     | 5M          |
| MiniStation    | PSP            | Y16           | Y20               | 120,000     | 3M          |

### 6.2 Platform License
Must purchase license to develop for each platform (one-time cost).
Some platforms require additional tech level.

## 7. Conventions and Awards

### 7.1 Game Conventions
Occur twice per year (Spring and Fall):
- Entry fee: $50,000 - $200,000
- Booth size: Small, Medium, Large
- Effect: Increase game hype, gain fans
- Special demos can be shown

| Booth Size | Cost     | Hype Multiplier | Fan Gain |
|-----------|----------|-----------------|----------|
| Small     | $50,000  | 1.2x            | +500     |
| Medium    | $100,000 | 1.5x            | +1,500   |
| Large     | $200,000 | 2.0x            | +5,000   |

### 7.2 Annual Awards
At end of each year, awards are given:
| Award              | Criteria                          | Prize      |
|-------------------|-----------------------------------|------------|
| Best Game          | Highest review avg that year      | $300,000   |
| Runner Up          | Second highest                    | $150,000   |
| Worst Game         | Lowest review that year           | Nothing    |
| Hall of Fame       | 4 consecutive scores of 9+        | $500,000   |

### 7.3 Grand Prize
Lifetime achievement award for accumulating multiple Hall of Fame entries.
Unlocks special features and bragging rights.

## 8. Items and Boosts

### 8.1 Office Items
| Item              | Cost     | Effect                         | Duration    |
|------------------|----------|--------------------------------|-------------|
| Bull Statue      | $20,000  | +10% all stats during dev      | Permanent   |
| Lucky Cat        | $30,000  | +5% sales                      | Permanent   |
| Dead Bull        | $50,000  | +20% debug efficiency          | Permanent   |
| Bookshelf        | $10,000  | +5% scenario skill growth      | Permanent   |
| Arcade Cabinet   | $40,000  | +10% motivation recovery       | Permanent   |
| Plant            | $5,000   | +3% stamina recovery           | Permanent   |

### 8.2 Consumable Items
| Item              | Cost     | Effect                              |
|------------------|----------|-------------------------------------|
| Energy Drink     | $500     | +30 stamina for one staff           |
| Inspiration      | $1,000   | +50 motivation for one staff        |
| Research Data    | $5,000   | +50 research points                 |
| Angel Funding    | $50,000  | +$200,000 cash (one-time)           |
| Black Bull       | $2,000   | +50 stamina, risk of -10 motivation |

## 9. Research System

### 9.1 Research Points
Earned by:
- Completing games: +20-100 RP per game (based on quality)
- Staff with high research skill generate passive RP
- Purchasing research data items

### 9.2 Research Unlocks
| Research         | Cost (RP) | Effect                              |
|-----------------|-----------|-------------------------------------|
| New Genre       | 50-200    | Unlock new game genre               |
| New Type        | 30-150    | Unlock new game type                |
| Speed Up        | 100       | +10% development speed              |
| Quality Up      | 150       | +10% point generation               |
| Better Debug    | 120       | +20% bug removal                    |
| Advertising     | 80        | Unlock advertising campaigns        |
| Sequel Making   | 100       | Ability to make sequels             |
| New Platform    | varies    | Ability to develop for new console  |
| Train Staff     | 60        | Ability to train staff skills       |

## 10. Training System

### 10.1 Training Options
| Training Type      | Cost     | Duration | Effect                    |
|-------------------|----------|----------|---------------------------|
| Study Session     | $5,000   | 2 weeks  | +5-15 to one skill        |
| Boot Camp         | $20,000  | 4 weeks  | +10-25 to one skill       |
| Guru Training     | $50,000  | 4 weeks  | +20-40 to one skill       |
| World Tour        | $80,000  | 8 weeks  | +10-20 to ALL skills      |

### 10.2 Skill Caps
- Natural max: ~200 per skill
- Training has diminishing returns past 150
- Job class affects which skills grow fastest

## 11. Advertising

### 11.1 Ad Campaigns
| Campaign          | Cost       | Timing        | Effect                   |
|------------------|-----------|---------------|--------------------------|
| Magazine Ad      | $30,000   | During dev    | +20% hype               |
| TV Commercial    | $100,000  | At release    | +50% first week sales   |
| Billboard        | $50,000   | During dev    | +30% hype               |
| Internet Ad      | $20,000   | At release    | +15% ongoing sales      |
| Celebrity Endorse| $200,000  | At release    | +80% first week sales   |

## 12. Sequel System

### 12.1 Sequel Rules
```
can_make_sequel if:
    previous_game_review_avg >= 6
    research "Sequel Making" unlocked

sequel_bonus = 1.0 + (previous_review - 6) * 0.05
sequel_fan_carry = previous_game_fans * 0.5
must_improve: total_points > previous_total * 1.1
  if not improved: review_penalty = -1.0
```

## 13. Financial System

### 13.1 Income
```
game_sales_revenue = units_sold * price_per_unit
convention_prizes = award_money
```

### 13.2 Expenses
```
monthly_salary = sum(staff.salary)
development_costs = contractor_fees + item_purchases
license_costs = platform_licenses
advertising = campaign_costs
training = training_costs
convention_entry = booth_costs
```

### 13.3 Game Over
If cash drops below 0 and stays negative for 3 months → bankruptcy → game over.

## 14. Trends System

### 14.1 Genre Popularity
Each genre has a popularity cycle:
```
popularity[genre] oscillates between 0.5 and 2.0
cycle_length = 3-5 years per genre
current_popularity displayed as "Hot!", "Normal", "Cold"
```

Making a game in a "Hot" genre: sales * 1.5
Making a game in a "Cold" genre: sales * 0.7

## 15. UI Layout

### 15.1 Main Screen
```
+--------------------------------------------------+
| Company: PixelDream   Cash: ¥1,250,000           |
| Year 8, Month 6       Fans: 45,000               |
+--------------------------------------------------+
|                                                    |
|  +-----------+  +-----------+  +-----------+      |
|  | Staff 1   |  | Staff 2   |  | Staff 3   |      |
|  | [sprite]  |  | [sprite]  |  | [sprite]  |      |
|  | Coding... |  | Drawing...|  | Testing...|      |
|  | ████░░░   |  | ██████░   |  | ██░░░░░   |      |
|  +-----------+  +-----------+  +-----------+      |
|  +-----------+  +-----------+                      |
|  | Staff 4   |  | Staff 5   |                      |
|  | [sprite]  |  | [sprite]  |                      |
|  | Sound...  |  | Writing...|                      |
|  | █████░░   |  | ███░░░░   |                      |
|  +-----------+  +-----------+                      |
|                                                    |
|  Current Game: "Dragon Quest RPG"                  |
|  Progress: Phase 2/4 (Graphics)                    |
|  Fun: 234  Creativity: 189  Graphics: 267          |
|  Sound: 145  Bugs: 8                               |
|                                                    |
+--------------------------------------------------+
| [New Game] [Staff] [Items] [Research] [Info]       |
+--------------------------------------------------+
| News: "Sonis console has been announced!"          |
+--------------------------------------------------+
```

### 15.2 Staff Detail Screen
```
+--------------------------------------+
|  Staff: Takeshi Yamada               |
+--------------------------------------+
|  Level: 3  Class: Designer           |
|  Salary: ¥12,000/month              |
+--------------------------------------+
|  Program:   ████░░░░░░  45          |
|  Scenario:  ██░░░░░░░░  22          |
|  Graphics:  ████████░░  89          |
|  Sound:     ███░░░░░░░  31          |
|  Research:  █████░░░░░  55          |
+--------------------------------------+
|  Stamina:   ████████░░  80%         |
|  Motivation:██████░░░░  120         |
+--------------------------------------+
|  [Train] [Change Class] [Fire]       |
+--------------------------------------+
```

### 15.3 Review Screen
```
+--------------------------------------+
|  Reviews for "Dragon Quest RPG"      |
+--------------------------------------+
|                                      |
|  Reviewer 1:  9 / 10                |
|  Reviewer 2:  8 / 10                |
|  Reviewer 3:  9 / 10                |
|  Reviewer 4: 10 / 10                |
|                                      |
|  Total: 36 / 40                      |
|                                      |
|  "An amazing RPG experience!"        |
|                                      |
|  Sales projections: EXCELLENT        |
+--------------------------------------+
```

## 16. End Game Scoring

### 16.1 Final Score (Year 20)
```
final_score = 0
final_score += total_revenue / 10000
final_score += total_fans / 100
final_score += hall_of_fame_entries * 5000
final_score += best_review_average * 1000
final_score += total_games_made * 100
final_score += max_staff_level * 200
```

### 16.2 Rankings
| Rank    | Score Range     |
|---------|----------------|
| F       | 0 - 10,000     |
| E       | 10,000 - 30,000|
| D       | 30,000 - 60,000|
| C       | 60,000 - 100,000|
| B       | 100,000 - 200,000|
| A       | 200,000 - 400,000|
| S       | 400,000+       |

## 17. Constants and Tuning

```
GAME_LENGTH_YEARS = 20
WEEKS_PER_MONTH = 4
MAX_STAFF = 8
STARTING_CASH = 500000
MAX_REVIEW_SCORE = 10
NUM_REVIEWERS = 4
PERFECT_SCORE = 40
BUG_GENERATION_RATE = 0.02
STAMINA_DRAIN_PER_WEEK = 5
STAMINA_RECOVERY_PER_WEEK = 3 (when not working)
MOTIVATION_DECAY = 1 per week
MOTIVATION_MIN = 0
MOTIVATION_MAX = 200
FAN_CONVERSION = 0.01
BANKRUPTCY_GRACE_MONTHS = 3
SEQUEL_IMPROVEMENT_THRESHOLD = 1.1
CONVENTION_FREQUENCY = 2 per year
TREND_CYCLE_MIN_YEARS = 3
TREND_CYCLE_MAX_YEARS = 5
```

## 18. Implementation Priority for AI Recreation

1. Time system and basic UI
2. Staff management (hiring, stats display)
3. Game creation flow (genre, type, platform)
4. Development phases with point generation
5. Review score calculation
6. Sales and revenue
7. Platform timeline
8. Genre-type compatibility matrix
9. Research and unlocks
10. Training system
11. Conventions and awards
12. Items and boosts
13. Sequel system
14. Advertising campaigns
15. Trends and popularity cycles
16. End-game scoring and rankings
