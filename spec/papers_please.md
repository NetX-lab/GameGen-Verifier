# Papers, Please — Complete Game Specification

## 1. Game Overview

Papers, Please is a "dystopian document thriller" where the player works as an
immigration inspector at a border checkpoint of the fictional country Arstotzka.
Each day, the player must review travelers' documents, check for discrepancies,
and decide whether to approve or deny entry. The player must balance following rules,
earning money to support their family, and making moral choices.

Platform: Single-player, 2D point-and-click with document inspection mechanics.
Game length: 31 in-game days (can end earlier based on choices).
Each day: 5-8 minutes of real-time gameplay.
Visual style: Pixel art, muted/drab color palette.

## 2. Technical Foundation

### 2.1 Game State
```
struct GameState {
    day: 1-31
    time_remaining: float         // Seconds left in work day (360 at start)
    money: integer                // Credits (currency)
    citations: integer            // Errors today
    total_citations: integer
    people_processed: integer     // Today's count
    family: FamilyState
    story_flags: dict[string, bool]
    ending_path: integer          // Which of 20 endings
    rules: list[Rule]             // Current day's active rules
    detainments: integer
    penalties: integer            // $5 per citation (after 2 free)
    confiscated_items: list
    tokens: list[Token]           // EZIC tokens/items received
    apartment: ApartmentState
}

struct FamilyState {
    members: list[FamilyMember]
    // Each member: name, status (HEALTHY, SICK, COLD, DEAD)
    // Members: Self, Wife, Son, Mother-in-law, Uncle
    rent: integer                 // Daily rent (always due)
    food_needed: boolean          // Each member needs food daily
    heat_needed: boolean          // Cold weather requires heating
    medicine_needed: list         // Sick members need medicine
}
```

### 2.2 Daily Structure
```
1. Morning briefing: New rules announced
2. Work shift: Process travelers (main gameplay)
3. End of day: Financial summary
4. Evening: Allocate money for family needs
5. Story events may occur between days
```

## 3. Document System

### 3.1 Document Types
| Document          | Introduced | Contents                                      |
|------------------|-----------|------------------------------------------------|
| Passport         | Day 1     | Name, DOB, sex, nationality, photo, expiry     |
| Entry Permit     | Day 3     | Name, purpose, duration, issuing city           |
| Work Pass        | Day 5     | Name, employer, field, end date                 |
| ID Card          | Day 8     | Name, DOB, district, height, weight             |
| Diplomatic Auth  | Day 10    | Name, nation, seal, access list                 |
| Asylum Grant     | Day 14    | Name, nationality, reason, fingerprint          |
| Vaccination Cert | Day 18    | Name, vaccines received, dates                  |
| ID Supplement    | Day 20    | Fingerprint, height, weight                     |
| Access Permit    | Day 23    | Name, nation, purpose, seal                     |

### 3.2 Document Properties
```
struct Passport {
    name: {first: string, last: string}
    date_of_birth: date
    sex: enum(M, F)
    issuing_city: string
    nationality: Country
    expiration_date: date
    photo: Image
    passport_number: string
    seal: SealImage              // May be forged
}

struct EntryPermit {
    name: {first: string, last: string}
    nationality: Country
    purpose: enum(VISIT, TRANSIT, WORK, IMMIGRATION, DIPLOMATIC)
    duration: string             // e.g., "2 DAYS", "14 DAYS", "FOREVER"
    issuing_city: string
    seal: SealImage
}
```

### 3.3 Countries
| Country     | Full Name                   | Valid Passport Color |
|------------|-----------------------------|--------------------|
| Arstotzka  | The State of Arstotzka     | Blue               |
| Antegria   | The Free Republic of Antegria| Red              |
| Impor      | The Republic of Impor       | Green              |
| Kolechia   | The State of Kolechia       | Yellow             |
| Obristan   | The United Federation of Obristan | Purple        |
| Republia   | The Republic of Republia    | Orange             |

### 3.4 Cities by Country
| Country    | Cities                                    |
|-----------|-------------------------------------------|
| Arstotzka | Orvech Vonor, East Grestin, Paradizna    |
| Antegria  | St. Marmero, Glorian, Outer Grouse       |
| Impor     | Enkyo, Haihan, Tsunkeido                 |
| Kolechia  | Yurko City, Vedor, West Grestin         |
| Obristan  | Skal, Lorndaz, Mergerous                 |
| Republia  | True Glorian, Lesrenadi, Bostan          |

## 4. Rule System

### 4.1 Rules by Day
| Day | New Rules Added                                          |
|-----|----------------------------------------------------------|
| 1   | Allow only Arstotzkan citizens (passport only)           |
| 2   | Allow all nationalities (still passport only)            |
| 3   | Entry permit required for foreigners                     |
| 4   | Check expiration dates on all documents                  |
| 5   | Work pass required for workers                           |
| 6   | Check issuing cities match country                       |
| 7   | Deny citizens of specific banned country (varies)        |
| 8   | ID card required for Arstotzkan citizens                 |
| 9   | Check for matching names across all documents            |
| 10  | Diplomatic authorization for diplomats                   |
| 11  | Check photo matches person appearance                    |
| 12  | Gender must match across documents and appearance        |
| 13  | Check seal authenticity                                  |
| 14  | Asylum seekers need asylum grant                         |
| 15  | Check for wanted criminals (bulletin board)              |
| 16  | Weight/height verification (random checks)               |
| 17  | Confiscate contraband                                    |
| 18  | Vaccination certificate for specific countries           |
| 19  | Fingerprint verification                                 |
| 20  | ID supplement with additional biometrics                 |
| 21  | Additional country bans (story-driven)                   |
| 22  | Search for weapons/contraband                            |
| 23  | Access permits for restricted areas                      |
| 24  | Multiple simultaneous rule changes                       |
| 25+ | Rules continue evolving based on story                   |

### 4.2 Rule Checking Logic
```
function check_documents(traveler, documents):
    discrepancies = []

    // Check passport exists
    if not has_document(PASSPORT): discrepancies.add("MISSING_PASSPORT")

    // Check passport expiration
    if passport.expiration_date < current_date:
        discrepancies.add("EXPIRED_PASSPORT")

    // Check nationality allowed
    if passport.nationality in banned_countries:
        discrepancies.add("BANNED_COUNTRY")

    // Check foreigner has entry permit (day 3+)
    if passport.nationality != ARSTOTZKA and not has_document(ENTRY_PERMIT):
        discrepancies.add("MISSING_ENTRY_PERMIT")

    // Check name consistency across documents
    for doc1, doc2 in document_pairs:
        if doc1.name != doc2.name:
            discrepancies.add("NAME_MISMATCH")

    // Check photo matches appearance
    if passport.photo != traveler.appearance:
        discrepancies.add("PHOTO_MISMATCH")

    // Check sex matches appearance
    if passport.sex != traveler.apparent_sex:
        discrepancies.add("SEX_MISMATCH")

    // Check issuing city is valid for country
    if passport.issuing_city not in valid_cities[passport.nationality]:
        discrepancies.add("INVALID_CITY")

    // Check work pass for workers (day 5+)
    if entry_permit.purpose == WORK and not has_document(WORK_PASS):
        discrepancies.add("MISSING_WORK_PASS")

    // Check seals
    if not valid_seal(passport.seal, passport.nationality):
        discrepancies.add("FORGED_SEAL")

    // Check wanted list
    if traveler.name in wanted_criminals:
        discrepancies.add("WANTED_CRIMINAL")

    // Check weight/height (when required)
    if abs(document.weight - measured_weight) > 5:
        discrepancies.add("WEIGHT_MISMATCH")

    return discrepancies
```

## 5. Gameplay Mechanics

### 5.1 Inspection Booth Layout
```
+---------------------------------------------------------------------+
|                         EXTERIOR (queue of travelers)                 |
|  [Traveler approaches when called]                                   |
|  [Speaker icon] "Next!"                                              |
+---------------------------------------------------------------------+
|                                                                       |
|  +--BOOTH WINDOW---------+    +--RULE BOOK-----------+               |
|  |                       |    |                       |               |
|  | [Traveler portrait]   |    | Current Rules:        |               |
|  | [Traveler speaks]     |    | - Arstotzkan: passport|               |
|  |                       |    |   + ID card           |               |
|  | Documents provided:   |    | - Foreigners: passport|               |
|  | [passport] [permit]   |    |   + entry permit      |               |
|  |                       |    | - Workers: work pass  |               |
|  +--INSPECTION DESK------+    | - Check all expiry    |               |
|  |                       |    | - Banned: Kolechia    |               |
|  | [Document inspection  |    |                       |               |
|  |  area - drag docs     |    | [Page 1] [Page 2]    |               |
|  |  here to examine]     |    +--BULLETIN BOARD------+               |
|  |                       |    | WANTED:               |               |
|  | [Inspect mode]        |    | [photo] Dari Ludum   |               |
|  | [Highlight to compare]|    | Reason: Murder       |               |
|  |                       |    +----------------------+               |
|  +--STAMPS---------------+                                           |
|  | [APPROVED] [DENIED]   |    +--CLOCK---------------+               |
|  |  (stamp on passport)  |    | 4:32 PM              |               |
|  +------------------------+    | People today: 7      |               |
|                                +----------------------+               |
+---------------------------------------------------------------------+
```

### 5.2 Interrogation Mechanic
When a discrepancy is found:
1. Click "Inspect" mode
2. Highlight the discrepancy on one document
3. Highlight the contradicting info on another document (or the person)
4. System shows the discrepancy message
5. Traveler may explain, provide additional documents, or confess
6. Player decides: APPROVE or DENY

### 5.3 Moral Choices
Certain travelers present moral dilemmas:
- Husband approved, wife has expired permit (separate them?)
- Refugee fleeing danger but missing documents
- EZIC agents asking for help (revolutionary group)
- Corrupt officials demanding entry
- Offering bribes

### 5.4 Time Mechanics
```
work_day_duration = 360 seconds (6 real minutes)
time_per_traveler = varies (30-90 seconds depending on complexity)
// Faster processing = more money
// More travelers per day = more income

// Time advances even while inspecting
// Clock visible in corner
// Day ends at 6:00 PM game time (18:00)
```

## 6. Economy System

### 6.1 Income
```
pay_per_traveler = 5 credits (for each processed after citation threshold)
// First 2 citations per day: FREE (no penalty)
// 3rd citation onwards: -5 credits each

daily_income = (travelers_processed * 5) - (max(0, citations - 2) * 5)
```

### 6.2 Daily Expenses
| Expense      | Cost    | Required | Consequence if Skipped      |
|-------------|---------|----------|-----------------------------|
| Rent        | 30-40   | Yes      | Game over after 2 days      |
| Food (each) | 10      | Yes      | Family member gets HUNGRY   |
| Heat        | 10-20   | Seasonal | Family member gets COLD     |
| Medicine    | 20      | If sick  | SICK→DEAD if untreated     |

### 6.3 Family Health Progression
```
if member.status == HEALTHY and (not_fed or cold):
    member.status = SICK (next day)
if member.status == SICK and no_medicine:
    member.status = DEAD (2 days later)
if member.status == SICK and medicine_given:
    member.status = HEALTHY (next day)
// Dead family members cannot be revived
// If player dies: game over
```

### 6.4 Financial Balance
```
typical_day_income = 7 travelers * 5 credits = 35 credits
typical_expenses = 30 rent + 50 food (5 members * 10) + 15 heat = 95 credits
// Player MUST process quickly and avoid citations to stay solvent
// Or accept bribes / EZIC payments (morally questionable)
```

## 7. Story and Endings

### 7.1 Story Arcs
1. **Main duty**: Just do your job correctly
2. **EZIC storyline**: Help or oppose the revolutionary group
3. **Family survival**: Keep everyone alive
4. **Corruption**: Accept bribes, detain innocents for bonuses
5. **Escape**: Eventually flee Arstotzka

### 7.2 EZIC Organization
EZIC agents approach on specific days with tasks:
| Day | EZIC Task                                    |
|-----|----------------------------------------------|
| 7   | First contact, receive EZIC token            |
| 11  | Allow specific EZIC agent through            |
| 15  | Receive EZIC money (bribe)                   |
| 19  | Use EZIC token to help agent                 |
| 23  | Poison specific entrant (assassination)      |
| 27  | Final loyalty choice                         |
| 29  | Armed uprising (participate or not)          |

### 7.3 Endings (20 total)
| Ending | Condition                                    | Type      |
|--------|----------------------------------------------|-----------|
| 1      | Arrested for letting in too many criminals   | Bad       |
| 2      | Family all dead                              | Bad       |
| 3      | Cannot pay rent, evicted                     | Bad       |
| 4      | Shot for attacking guard                     | Bad       |
| 5      | Detained for EZIC involvement               | Bad       |
| 6-8    | Various arrest conditions                    | Bad       |
| 9-11   | Escape alone or with family (partial)        | Neutral   |
| 12-15  | Complete duty, various family outcomes       | Neutral   |
| 16-18  | Help EZIC succeed                            | Mixed     |
| 19     | EZIC fails, you survive                      | Neutral   |
| 20     | Perfect ending: family alive, escape success | Best      |

## 8. Traveler Generation

### 8.1 Traveler Types
```
struct Traveler {
    name: string
    nationality: Country
    sex: enum(M, F)
    appearance: AppearanceData
    documents: list[Document]
    has_discrepancy: boolean
    discrepancy_type: DiscrepancyType | null
    is_story_character: boolean
    story_id: string | null
    dialogue: list[string]
    contraband: Item | null
}
```

### 8.2 Discrepancy Types and Frequency
| Discrepancy Type      | Frequency | Detection Difficulty |
|----------------------|-----------|---------------------|
| Expired document     | 20%       | Easy                |
| Name mismatch        | 15%       | Easy                |
| Wrong issuing city   | 10%       | Medium              |
| Photo mismatch       | 10%       | Medium              |
| Missing document     | 15%       | Easy                |
| Forged seal          | 5%        | Hard                |
| Sex mismatch         | 5%        | Medium              |
| Wanted criminal      | 5%        | Medium              |
| Weight/height wrong  | 5%        | Medium              |
| Invalid entry purpose| 5%        | Hard                |
| Contraband           | 5%        | Hard                |

### 8.3 Traveler Generation per Day
```
travelers_per_day = 8-12 (varies)
  - ~40% have valid documents (should be approved)
  - ~40% have discrepancies (should be denied)
  - ~10% are story characters (scripted)
  - ~10% are ambiguous (moral choices)
```

## 9. Detainment and Search

### 9.1 Detainment
```
// Can call guards to detain a traveler
detain_bonus = 5 credits per correct detainment
// Detain wanted criminals: always correct
// Detain innocents: citation penalty
// Detainment available from Day 15
```

### 9.2 Full Body Search (Day 22+)
```
// Can request full body search
// Reveals hidden contraband: weapons, drugs
// Contraband confiscation: +5 credits
// Searching innocent person: citation
search_result:
  - CLEAN: no contraband (risk of citation)
  - WEAPON: confiscate, deny entry
  - DRUGS: confiscate, deny entry
  - DOCUMENTS: hidden forged documents
```

## 10. Audio/Visual Design

### 10.1 Sound Design
| Event                    | Sound                      |
|--------------------------|----------------------------|
| "Next!" call             | Gruff voice                |
| Stamp: Approved          | Green stamp thud           |
| Stamp: Denied            | Red stamp thud             |
| Document placed          | Paper shuffle              |
| Citation received        | Harsh buzzer               |
| Discrepancy found        | Ding notification          |
| End of day               | Closing bell               |
| Gunshot (story events)   | Loud crack                 |
| EZIC contact             | Mysterious tone            |
| Family death news        | Somber melody              |

### 10.2 Visual Style
- Muted green/brown/gray color palette
- Pixel art at ~320x200 native resolution
- Portraits: ~64x64 pixel faces with distinguishing features
- Documents: Detailed pixel art with readable text
- Stamps leave permanent marks on passports
- Weather effects: snow, overcast (match season)

## 11. Day-by-Day Progression

### 11.1 Complexity Curve
| Day Range | Documents to Check | Rules Active | Avg Time/Traveler |
|-----------|-------------------|-------------|-------------------|
| 1-3       | 1-2               | 3-5         | 30 seconds        |
| 4-8       | 2-3               | 6-10        | 45 seconds        |
| 9-15      | 3-4               | 10-15       | 60 seconds        |
| 16-22     | 3-5               | 15-20       | 75 seconds        |
| 23-31     | 4-6               | 20+         | 90 seconds        |

### 11.2 Newspaper Headlines (Between Days)
Each morning shows newspaper with headlines reflecting:
- Yesterday's border events
- Story progression
- War/political developments
- Player's actions' consequences

## 12. Token/Item System

### 12.1 Special Items
| Item              | Source   | Use                                   |
|------------------|---------|---------------------------------------|
| EZIC Token       | EZIC    | Give to specific travelers            |
| Poison           | EZIC    | Kill specific target                  |
| Key              | Story   | Unlock specific ending                |
| Locket           | Traveler| Moral choice item                     |
| Diplomatic Seal  | Story   | Verify diplomatic documents           |
| Tranquilizer     | EZIC    | Incapacitate target                   |

## 13. Performance Metrics

### 13.1 End-of-Day Summary
```
+------------------------------------------+
|  END OF DAY 12                           |
+------------------------------------------+
|  Travelers processed: 8                  |
|  Correct decisions: 7                    |
|  Citations: 1                            |
|                                          |
|  Earnings: 40 credits                    |
|  Penalties: 0 credits                    |
|  NET PAY: 40 credits                     |
+------------------------------------------+
|  Savings: 15 credits                     |
|                                          |
|  Expenses:         Cost:    Pay:         |
|  [x] Rent          30       [ ]          |
|  [x] Food (self)   10       [ ]          |
|  [x] Food (wife)   10       [ ]          |
|  [x] Food (son)    10       [ ]          |
|  [ ] Food (mother) 10       [ ]          |
|  [ ] Heat          15       [ ]          |
|  [ ] Medicine      20       [ ]          |
|                                          |
|  Total needed: 105                       |
|  Available: 55                           |
|  SHORTFALL: 50 credits                   |
|  (Must choose who goes without)          |
+------------------------------------------+
```

## 14. Input Controls

| Action               | Input              |
|---------------------|---------------------|
| Call next traveler   | Click speaker/bell  |
| Pick up document    | Click and drag      |
| Inspect mode        | Click inspect button|
| Highlight item      | Click on text/detail|
| Compare             | Highlight two items |
| Stamp passport      | Drag stamp to passport|
| Open rule book      | Click rule book     |
| Open bulletin       | Click bulletin board|
| Detain              | Click detain button |
| Search              | Click search button |

## 15. Constants and Tuning

```
TOTAL_DAYS = 31
WORK_DAY_SECONDS = 360
PAY_PER_PERSON = 5
CITATION_PENALTY = 5
FREE_CITATIONS_PER_DAY = 2
RENT_COST = 30-40
FOOD_COST = 10
HEAT_COST = 10-20
MEDICINE_COST = 20
DETAIN_BONUS = 5
CONFISCATE_BONUS = 5
TRAVELERS_PER_DAY = 8-12
DISCREPANCY_RATE = 0.40
STORY_CHARACTER_RATE = 0.10
NUM_COUNTRIES = 6
NUM_ENDINGS = 20
SICK_TO_DEAD_DAYS = 2
RENT_GRACE_DAYS = 2
DOCUMENT_TYPES = 9
MAX_DOCUMENTS_PER_PERSON = 6
```

## 16. Implementation Priority for AI Recreation

1. Document display and inspection mechanic
2. Basic passport checking (name, photo, expiry)
3. Stamp approve/deny system
4. Day/income/expense cycle
5. Family management (feed, heat, medicine)
6. Rule progression by day
7. Entry permit checking
8. Discrepancy detection and interrogation
9. Multiple document cross-referencing
10. Story events and EZIC storyline
11. Wanted criminals bulletin
12. Detainment and search mechanics
13. Contraband system
14. Multiple endings logic
15. Newspaper between days
16. Full 31-day progression
