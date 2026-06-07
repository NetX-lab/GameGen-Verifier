# Game Dev Tycoon — Complete Game Specification

## 1. Game Overview

Game Dev Tycoon is a business simulation where the player runs a game development
company from the 1980s through the 2030s. Starting in a garage, the player creates
games, researches technologies, grows their team, and navigates the evolving game
industry. The game simulates ~35 years of gaming history with fictionalized versions
of real platforms, events, and trends.

Platform: Single-player, menu/UI-driven simulation. No spatial map.
Game length: ~35 in-game years. Each year is approximately 5-7 minutes of real time.
Simulation tick: 1 game week. 4 weeks = 1 month, 12 months = 1 year.

## 2. Technical Foundation

### 2.1 Game State
```
struct GameState {
    company_name: string
    cash: float              // Starting: $70,000
    fans: integer            // Starting: 0
    research_points: float   // Starting: 0
    design_points: float     // Starting: 0
    technology_points: float // Starting: 0
    current_year: integer    // Starting: Year 1 (maps to ~1985)
    current_week: integer    // 1-52
    staff: list[Employee]
    released_games: list[Game]
    unlocked_topics: list[Topic]
    unlocked_platforms: list[Platform]
    unlocked_features: list[Feature]
    office_level: 0-3        // 0=garage, 1=small, 2=medium, 3=large
    active_game: Game | null
    game_history: list[GameResult]
    research_queue: list[ResearchItem]
}
```

### 2.2 Time Progression
- Game speed: Normal (1x), Fast (2x), Ultra (4x)
- 1 tick = 1 game week
- Normal speed: ~1 real second per game week
- Events trigger at specific year/week combinations

## 3. Game Development Process

### 3.1 Creating a New Game
Player selects:
1. **Game name** (free text)
2. **Topic** (from unlocked topics)
3. **Genre** (from available genres)
4. **Platform** (from available platforms)
5. **Game size** (Small/Medium/Large/AAA — based on office level)

### 3.2 Topics
| Topic           | Unlock     | Design Weight | Tech Weight |
|----------------|------------|---------------|-------------|
| Medieval       | Start      | 0.6           | 0.4         |
| Business       | Start      | 0.7           | 0.3         |
| Sci-Fi         | Start      | 0.5           | 0.5         |
| Fantasy        | Start      | 0.6           | 0.4         |
| Military       | Year 2     | 0.4           | 0.6         |
| Horror         | Year 2     | 0.5           | 0.5         |
| Mystery        | Year 3     | 0.7           | 0.3         |
| Sports         | Year 3     | 0.3           | 0.7         |
| Comedy         | Year 4     | 0.8           | 0.2         |
| Romance        | Year 5     | 0.8           | 0.2         |
| Superhero      | Year 6     | 0.5           | 0.5         |
| Ninja          | Year 6     | 0.5           | 0.5         |
| Space          | Year 7     | 0.3           | 0.7         |
| Cyberpunk      | Year 8     | 0.4           | 0.6         |
| Post-Apocalyptic| Year 9    | 0.5           | 0.5         |
| Pirate         | Year 10    | 0.6           | 0.4         |
| Vampire        | Year 11    | 0.6           | 0.4         |
| Hunting        | Year 12    | 0.4           | 0.6         |
| Prison         | Year 13    | 0.5           | 0.5         |
| Hacking        | Year 14    | 0.3           | 0.7         |
| Evolution      | Year 15    | 0.5           | 0.5         |
| Vocabulary     | Year 16    | 0.8           | 0.2         |
| Music          | Year 17    | 0.5           | 0.5         |
| Dance          | Year 18    | 0.5           | 0.5         |
| Martial Arts   | Year 19    | 0.5           | 0.5         |
| City           | Year 20    | 0.6           | 0.4         |
| Virtual Pet    | Year 21    | 0.6           | 0.4         |
| Cooking        | Year 22    | 0.7           | 0.3         |

### 3.3 Genres
| Genre          | Design Focus        | Tech Focus          |
|---------------|---------------------|---------------------|
| Action        | Gameplay, Story     | Engine, AI          |
| Adventure     | Story, Dialogue     | World, Graphics     |
| RPG           | Story, Quests       | World, Engine       |
| Simulation    | Gameplay, World     | Engine, AI          |
| Strategy      | Gameplay, AI        | Engine, AI          |
| Casual        | Gameplay, Polish    | Graphics, Sound     |

### 3.4 Topic-Genre Compatibility Matrix
Each topic-genre pair has a compatibility score (0.0 to 1.0):

| Topic/Genre   | Action | Adventure | RPG  | Simulation | Strategy | Casual |
|--------------|--------|-----------|------|------------|----------|--------|
| Medieval     | 0.8    | 0.9       | 1.0  | 0.6        | 0.9      | 0.3    |
| Business     | 0.2    | 0.4       | 0.3  | 1.0        | 0.7      | 0.8    |
| Sci-Fi       | 0.9    | 0.8       | 0.9  | 0.6        | 0.8      | 0.4    |
| Fantasy      | 0.8    | 1.0       | 1.0  | 0.4        | 0.7      | 0.5    |
| Military     | 1.0    | 0.6       | 0.5  | 0.7        | 1.0      | 0.2    |
| Horror       | 0.8    | 1.0       | 0.6  | 0.3        | 0.3      | 0.4    |
| Mystery      | 0.5    | 1.0       | 0.6  | 0.3        | 0.4      | 0.6    |
| Sports       | 0.7    | 0.2       | 0.2  | 1.0        | 0.4      | 0.9    |
| Comedy       | 0.5    | 0.8       | 0.6  | 0.5        | 0.3      | 1.0    |
| Romance      | 0.2    | 0.9       | 0.7  | 0.5        | 0.2      | 0.8    |
| Superhero    | 1.0    | 0.8       | 0.8  | 0.3        | 0.4      | 0.5    |
| Space        | 0.9    | 0.7       | 0.7  | 0.8        | 0.9      | 0.3    |
| Cyberpunk    | 0.9    | 0.8       | 0.9  | 0.4        | 0.5      | 0.2    |

### 3.5 Development Phases
Game development proceeds in 3 phases. In each phase, the player allocates
effort using sliders across different aspects.

#### Phase 1: Core Development
| Slider       | Design Points | Tech Points | Weight |
|-------------|---------------|-------------|--------|
| Engine       | 0.0           | 1.0         | 0.25   |
| Gameplay     | 0.8           | 0.2         | 0.30   |
| Story/Quests | 1.0           | 0.0         | 0.25   |
| Dialogues    | 1.0           | 0.0         | 0.20   |

#### Phase 2: Feature Development
| Slider        | Design Points | Tech Points | Weight |
|--------------|---------------|-------------|--------|
| Level Design  | 0.7           | 0.3         | 0.25   |
| AI            | 0.2           | 0.8         | 0.25   |
| World Design  | 0.6           | 0.4         | 0.25   |
| Graphics      | 0.2           | 0.8         | 0.25   |

#### Phase 3: Polish
| Slider         | Design Points | Tech Points | Weight |
|---------------|---------------|-------------|--------|
| Sound/Music    | 0.5           | 0.5         | 0.30   |
| Testing        | 0.3           | 0.7         | 0.35   |
| Marketing      | 0.8           | 0.2         | 0.35   |

### 3.6 Development Duration
| Game Size | Duration (weeks) | Base Cost | Staff Required |
|----------|-----------------|-----------|----------------|
| Small    | 5               | $5,000    | 1              |
| Medium   | 8               | $25,000   | 2-4            |
| Large    | 12              | $80,000   | 4-6            |
| AAA      | 18              | $200,000  | 6+             |

### 3.7 Point Generation During Development
```
points_per_tick = sum(
    staff.skill[slider_type] * slider_value * effort_allocation
    for staff in assigned_staff
)
design_points_total += points_per_tick * slider.design_ratio
tech_points_total += points_per_tick * slider.tech_ratio
```

### 3.8 Bugs
```
bug_count = total_tech_points * 0.03 * (1 - testing_allocation)
bug_penalty = bug_count * 0.5  // subtracted from final score
```

## 4. Game Scoring and Reviews

### 4.1 Review Score Calculation
```
// Step 1: Calculate raw quality
genre_weights = get_genre_weights(genre)  // which sliders matter more
topic_match = topic_genre_compatibility[topic][genre]

design_score = design_points * topic_match * genre_weights.design
tech_score = tech_points * topic_match * genre_weights.tech

quality = (design_score + tech_score) / expected_points[game_size]

// Step 2: Apply modifiers
quality *= platform_match_bonus      // 0.8-1.2
quality *= trend_bonus               // 0.9-1.3 (hot topics)
quality *= sequel_bonus_or_penalty   // 0.7-1.2
quality *= innovation_bonus          // 1.0-1.3

// Step 3: Bug penalty
quality -= bug_count * 0.01

// Step 4: Scale to review scores
review_score = quality_to_review(quality)  // Maps to 1-10 scale
// 4 reviewers each give ±0.5 variance

// Step 5: Individual reviewer scores
for i in 0..3:
    reviews[i] = clamp(review_score + random(-0.5, 0.5), 1.0, 10.0)
```

### 4.2 Quality-to-Review Mapping
| Quality Range | Average Review |
|--------------|----------------|
| 0.0 - 0.2   | 1.0 - 3.0     |
| 0.2 - 0.4   | 3.0 - 5.0     |
| 0.4 - 0.6   | 5.0 - 7.0     |
| 0.6 - 0.8   | 7.0 - 8.5     |
| 0.8 - 0.95  | 8.5 - 9.5     |
| 0.95 - 1.0+ | 9.5 - 10.0    |

### 4.3 Review Impact on Sales
```
average_review = sum(reviews) / 4
hype_factor = marketing_points * 0.1
fan_factor = log2(fans + 1) * 0.5
platform_install_base = platform.market_share * 1000000

base_sales = platform_install_base * review_multiplier[average_review]
total_sales = base_sales * hype_factor * fan_factor * game_size_multiplier

// Review multiplier table
review_multiplier = {
    1: 0.001, 2: 0.005, 3: 0.01, 4: 0.02,
    5: 0.04, 6: 0.08, 7: 0.15, 8: 0.25,
    9: 0.40, 10: 0.60
}
```

### 4.4 Sales Distribution Over Time
Sales occur over 8 weeks after release:
```
week_1: 35% of total
week_2: 20%
week_3: 15%
week_4: 10%
week_5: 8%
week_6: 5%
week_7: 4%
week_8: 3%
```

### 4.5 Revenue Calculation
```
revenue_per_unit = game_price - platform_royalty
game_price: Small=$5, Medium=$10, Large=$20, AAA=$30
platform_royalty: typically 15-30% depending on platform
```

## 5. Platform System (Fictionalized)

### 5.1 Platforms Timeline
| Platform         | Real Equivalent  | Release Year | End Year | Market Peak |
|-----------------|------------------|-------------|----------|-------------|
| Govodore 64     | Commodore 64     | Y1          | Y5       | Y2          |
| PC              | IBM PC           | Y1          | Y35+     | Y15+        |
| TES              | NES             | Y2          | Y7       | Y4          |
| Master V        | Master System    | Y2          | Y6       | Y3          |
| Super TES       | SNES             | Y5          | Y12      | Y8          |
| Mega Drive      | Genesis          | Y5          | Y11      | Y7          |
| Game Sphere     | Game Boy         | Y4          | Y14      | Y8          |
| Playsystem      | PlayStation      | Y10         | Y17      | Y13         |
| Nuu 64          | N64              | Y11         | Y17      | Y13         |
| DreamVast       | Dreamcast        | Y13         | Y16      | Y14         |
| Playsystem 2    | PS2              | Y15         | Y22      | Y18         |
| GS              | GameCube         | Y16         | Y22      | Y18         |
| mBox            | Xbox             | Y16         | Y22      | Y18         |
| Wuu             | Wii              | Y21         | Y28      | Y24         |
| Playsystem 3    | PS3              | Y21         | Y28      | Y24         |
| mBox 360        | Xbox 360         | Y20         | Y28      | Y24         |
| grPhone         | iPhone           | Y22         | Y35+     | Y28+        |
| grPad           | iPad             | Y25         | Y35+     | Y30+        |
| Playsystem 4    | PS4              | Y28         | Y35+     | Y32         |
| mBox Next       | Xbox One         | Y28         | Y35+     | Y32         |

### 5.2 Platform Properties
```
struct Platform {
    name: string
    release_year: int
    end_of_life_year: int
    peak_year: int
    max_market_share: float     // 0.0-1.0
    license_cost: int           // One-time cost to develop for it
    royalty_rate: float          // Percentage of sales
    tech_level: int             // 1-10, affects graphics requirements
    audience: enum(YOUNG, EVERYONE, CORE, CASUAL)
}
```

### 5.3 Platform Market Share Over Time
```
market_share(year) =
    if year < release_year: 0
    if year < peak_year: max_share * (year - release_year) / (peak_year - release_year)
    if year < end_year: max_share * (end_year - year) / (end_year - peak_year)
    else: 0
```

## 6. Staff System

### 6.1 Employee Properties
```
struct Employee {
    name: string
    salary: int                  // Monthly, $2000-$15000
    design_skill: float          // 1.0-10.0
    technology_skill: float      // 1.0-10.0
    speed_skill: float           // 1.0-10.0
    research_skill: float        // 1.0-10.0
    experience: float            // Grows over time
    specialization: enum(NONE, DESIGN, TECHNOLOGY, SPEED, RESEARCH)
    morale: float                // 0-100, affects output
}
```

### 6.2 Hiring
| Office Level | Max Staff | Salary Range     |
|-------------|----------|-----------------|
| Garage      | 1 (you)  | N/A             |
| Small       | 4        | $2,000-$5,000   |
| Medium      | 6        | $3,000-$8,000   |
| Large       | 8+       | $4,000-$15,000  |

Hiring process:
1. Post job listing (costs $500-$2000)
2. 3-5 candidates appear with random stats
3. Player chooses one to hire
4. Training: can send staff to training ($2000-$5000, improves one skill by 1-2 points)

### 6.3 Skill Growth
```
experience_gain = games_worked_on * 0.1
skill_growth = experience_gain * 0.05 (per game completed)
max_natural_skill = 7.0 (training can push higher)
```

### 6.4 Staff Morale
```
morale starts at 80
morale += 5 per successful game (review > 7)
morale -= 10 per failed game (review < 4)
morale -= 2 per month of overwork (no vacation)
morale += 15 per vacation (costs $2000, takes 2 weeks)
if morale < 30: productivity * 0.5
if morale < 10: employee may quit
```

## 7. Research System

### 7.1 Research Categories
| Category        | Unlocks                              |
|----------------|--------------------------------------|
| Game Engine    | Engine components, custom engine      |
| Design         | New genres, features, game sizes      |
| Technology     | Better graphics, AI, networking       |
| Marketing      | Better marketing options              |
| Business       | Better deals, new revenue streams     |

### 7.2 Research Items (Partial List)
| Item                 | Category   | Cost (RP) | Prerequisite        | Effect                    |
|---------------------|------------|-----------|---------------------|---------------------------|
| Target Audience     | Design     | 20        | None                | Choose audience per game  |
| Medium Games        | Design     | 40        | 3 games made        | Unlock medium game size   |
| Large Games         | Design     | 100       | Office level 2      | Unlock large game size    |
| AAA Games           | Design     | 200       | Office level 3      | Unlock AAA game size      |
| Custom Engine       | Engine     | 80        | 5 games made        | Build reusable engine     |
| 2D Graphics v2      | Technology | 30        | None                | Better 2D visuals         |
| 3D Graphics v1      | Technology | 60        | Year 8+             | Enable 3D                 |
| 3D Graphics v2      | Technology | 120       | 3D v1               | Better 3D                 |
| 3D Graphics v3      | Technology | 200       | 3D v2               | High-end 3D              |
| Online Multiplayer  | Technology | 150       | Year 15+            | Add online features       |
| Sound               | Technology | 20        | None                | Better sound              |
| Advanced AI         | Technology | 80        | Year 10+            | Better game AI            |
| Marketing           | Marketing  | 40        | Small office        | Hype campaigns            |
| Sequels             | Design     | 30        | 3 games made        | Make sequels              |
| Multi-platform      | Technology | 100       | Medium office        | Release on 2+ platforms   |
| Expansion Packs     | Design     | 60        | Large games         | Create expansions         |
| MMO                 | Technology | 250       | Large office        | Create MMOs               |
| R&D Lab             | Business   | 150       | Large office        | Faster research           |
| Hardware Lab        | Business   | 200       | Large office        | Create game console       |

### 7.3 Custom Engine
```
struct CustomEngine {
    name: string
    components: list[EngineComponent]
    // Each component has a tech level 1-5
    // Components: 2D, 3D, Sound, AI, Networking, Physics
    // Building costs research points and time
    // Reusable across multiple games
    // Upgrading components costs less than full rebuild
}
```

## 8. Office Progression

### 8.1 Office Levels
| Level  | Name      | Cost      | Max Staff | Unlocks                      |
|--------|----------|-----------|-----------|------------------------------|
| 0      | Garage   | Free      | 1         | Small games only             |
| 1      | Small    | $70,000   | 4         | Medium games, marketing      |
| 2      | Medium   | $250,000  | 6         | Large games, R&D lab         |
| 3      | Large    | $1,000,000| 8+        | AAA games, hardware lab, MMO |

### 8.2 Office Upgrades (within level)
| Upgrade          | Cost     | Effect                        |
|-----------------|----------|-------------------------------|
| Better Furniture| $10,000  | +5% staff productivity        |
| Coffee Machine  | $5,000   | +3% speed                     |
| Server Room     | $50,000  | Required for online features  |
| Motion Capture  | $100,000 | +graphics quality for 3D games|
| Sound Studio    | $75,000  | +sound quality                |

## 9. Marketing System

### 9.1 Marketing Campaigns
| Campaign Type    | Cost     | Duration | Hype Bonus |
|-----------------|----------|----------|------------|
| Small Campaign  | $10,000  | 4 weeks  | 1.1x       |
| Medium Campaign | $50,000  | 4 weeks  | 1.3x       |
| Large Campaign  | $200,000 | 4 weeks  | 1.6x       |
| Magazine Deal   | $30,000  | 2 weeks  | 1.2x       |
| Convention Booth| $80,000  | 1 week   | 1.4x       |

Marketing must be launched DURING development (Phase 3) or within
2 weeks of release to be effective.

## 10. Sequel System

### 10.1 Sequel Bonuses
```
sequel_bonus = 1.0 + (predecessor_review_avg - 5) * 0.05
// If predecessor was 9.0: bonus = 1.0 + 4 * 0.05 = 1.20
// If predecessor was 3.0: bonus = 1.0 + (-2) * 0.05 = 0.90

sequel_must_improve:
    design_points >= predecessor.design_points * 1.1
    tech_points >= predecessor.tech_points * 1.1
    // If not improved: quality *= 0.8 ("feels like a rehash")
```

### 10.2 Sequel Numbering
Sequels automatically append number (Game 2, Game 3, etc.)
Max effective sequel: 5 (diminishing returns after 3)

## 11. Fan System

### 11.1 Fan Accumulation
```
new_fans = total_sales * 0.01 * review_multiplier
if review_avg >= 9: new_fans *= 2.0 (word of mouth)
if review_avg >= 8: new_fans *= 1.5
if review_avg < 4: fans -= total_fans * 0.05 (fans leave)
```

### 11.2 Fan Effects
- Higher fans → more base sales for next game
- Fans provide hype even without marketing
- Fans expect quality to increase over time

## 12. Industry Events

### 12.1 Timed Events
| Year | Event                                      |
|------|---------------------------------------------|
| Y1   | "Welcome to game development!"              |
| Y2   | TES console launched                        |
| Y3   | First game expo announced                   |
| Y5   | Super TES and Mega Drive launch             |
| Y8   | 3D graphics revolution begins               |
| Y10  | Playsystem launches                         |
| Y12  | Internet gaming emerges                     |
| Y15  | Playsystem 2 and mBox launch               |
| Y18  | Digital distribution begins                 |
| Y20  | mBox 360 launches                           |
| Y22  | grPhone launches (mobile gaming)            |
| Y25  | grPad launches (tablet gaming)              |
| Y28  | Next-gen consoles                           |
| Y30  | VR gaming begins                            |

### 12.2 Random Events
| Event                          | Probability | Effect                    |
|-------------------------------|-------------|---------------------------|
| Game Award nomination         | 5% per game | +fans, +cash if won       |
| Publisher deal offer          | 10%/year    | Advance cash for game     |
| Employee poached              | 5%/year     | Lose staff member         |
| Industry award                | 3%/year     | +reputation, +fans        |
| Game convention invitation    | 8%/year     | Marketing opportunity     |
| Technology breakthrough       | 5%/year     | Free research points      |
| Market crash                  | 2%/year     | -30% sales for 6 months   |

## 13. Game of the Year / Awards

### 13.1 Award Conditions
```
GOTY eligible if:
    review_average >= 9.0
    sales > 500,000 units
    no game this year scored higher

Awards boost:
    fans += 10,000
    cash += $100,000 bonus
    future_game_hype *= 1.2
```

## 14. Difficulty and Game Over

### 14.1 Game Over Condition
```
if cash < 0 and no_games_in_development:
    if cash < -$100,000: immediate game over
    else: 2-month grace period
    if cash still < 0 after grace: game over
```

### 14.2 Score at End
```
final_score = cash + (fans * 10) + sum(game_reviews * 1000) + company_value
```

## 15. UI Layout

### 15.1 Main Screen
```
+------------------------------------------------------------------+
| [Menu] Company: GameCorp    Cash: $245,000    Fans: 12,500       |
| Week 24, Year 12            [1x] [2x] [4x]                       |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------+     +---------------------------------+      |
|  |                  |     |                                 |      |
|  |   OFFICE VIEW    |     |    Currently Developing:        |      |
|  |                  |     |    "Space Quest 3"              |      |
|  |  [Staff shown    |     |    Genre: Adventure             |      |
|  |   at desks,      |     |    Topic: Space                 |      |
|  |   working on     |     |    Platform: PC                 |      |
|  |   computers]     |     |    Progress: ████████░░ 80%     |      |
|  |                  |     |    Phase: 3 (Polish)            |      |
|  |                  |     |    Design: 145 pts              |      |
|  |                  |     |    Tech: 132 pts                |      |
|  |                  |     |    Bugs: 12                     |      |
|  +------------------+     +---------------------------------+      |
|                                                                    |
|  Actions:                                                          |
|  [New Game] [Research] [Staff] [Marketing] [Office] [Game Reports]|
+------------------------------------------------------------------+
| Log: "Space Quest 3 Phase 2 complete. Moving to Phase 3..."       |
+------------------------------------------------------------------+
```

### 15.2 Game Development Slider Screen
```
+------------------------------------------+
|        PHASE 1: Core Development          |
+------------------------------------------+
|                                           |
|  Engine:    [====|======] 60%            |
|  Gameplay:  [========|==] 80%            |
|  Story:     [======|====] 60%            |
|  Dialogues: [===|=======] 30%            |
|                                           |
|  Design focus: ████████░░ HIGH           |
|  Tech focus:   ████░░░░░░ MEDIUM         |
|                                           |
|  [Start Development]                      |
+------------------------------------------+
```

### 15.3 Review Screen
```
+------------------------------------------+
|     GAME REVIEWS: "Space Quest 3"        |
+------------------------------------------+
|                                           |
|  All Games Magazine:     ★★★★★★★★★☆ 9.0 |
|  Game Hero:              ★★★★★★★★☆☆ 8.5 |
|  Informed Gamer:         ★★★★★★★★★☆ 9.0 |
|  Game Rater:             ★★★★★★★★★★ 9.5 |
|                                           |
|  Average Score: 9.0                       |
|                                           |
|  Sales this week: 125,000 units          |
|  Total sales: 890,000 units              |
|  Revenue: $4,450,000                     |
|  Profit: $3,200,000                      |
|                                           |
|  New fans gained: 8,900                  |
+------------------------------------------+
```

## 16. Save/Load System

Auto-save every in-game year. Manual save anytime.
Save data: Complete GameState struct serialized to JSON/binary.

## 17. Constants and Tuning

```
STARTING_CASH = 70000
STARTING_FANS = 0
WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12
MAX_REVIEW_SCORE = 10.0
MIN_REVIEW_SCORE = 1.0
REVIEW_VARIANCE = 0.5
SALES_WEEKS = 8
FAN_CONVERSION_RATE = 0.01
BUG_RATE = 0.03
SEQUEL_IMPROVEMENT_THRESHOLD = 1.1
MAX_SEQUEL_BONUS = 1.3
GAME_OVER_DEBT_LIMIT = -100000
GRACE_PERIOD_MONTHS = 2
TRAINING_COST_MIN = 2000
TRAINING_COST_MAX = 5000
TRAINING_SKILL_GAIN_MIN = 1.0
TRAINING_SKILL_GAIN_MAX = 2.0
VACATION_COST = 2000
VACATION_DURATION_WEEKS = 2
VACATION_MORALE_BOOST = 15
```

## 18. Implementation Priority for AI Recreation

1. Time progression and basic UI
2. Game creation flow (topic, genre, platform selection)
3. Development phases with sliders
4. Point generation system
5. Review score calculation
6. Sales and revenue model
7. Platform timeline (console generations)
8. Staff hiring and management
9. Research system and unlocks
10. Office progression
11. Marketing campaigns
12. Fan system
13. Sequel system
14. Industry events and awards
15. Custom engine system
16. Advanced features (MMO, expansions, hardware)
