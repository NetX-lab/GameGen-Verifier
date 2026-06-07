# BitLife — Complete Game Specification

> A comprehensive specification for faithfully recreating BitLife (Candywriter LLC, 2018 mobile life simulation game). This document covers every system, mechanic, entity, and interaction required for a full clone of the original mobile experience.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Aging Mechanic](#3-core-aging-mechanic)
4. [Character Creation System](#4-character-creation-system)
5. [Character Stats System](#5-character-stats-system)
6. [Life Stages](#6-life-stages)
7. [Education System](#7-education-system)
8. [Career System](#8-career-system)
9. [Relationship System](#9-relationship-system)
10. [Crime & Legal System](#10-crime--legal-system)
11. [Health System](#11-health-system)
12. [Financial System](#12-financial-system)
13. [Activities System](#13-activities-system)
14. [Fame & Social Media System](#14-fame--social-media-system)
15. [Immigration & Emigration System](#15-immigration--emigration-system)
16. [Military System](#16-military-system)
17. [Random Events](#17-random-events)
18. [Mini-Games](#18-mini-games)
19. [Legacy & Generational System](#19-legacy--generational-system)
20. [Achievements & Ribbons](#20-achievements--ribbons)
21. [Monetization & Premium Features](#21-monetization--premium-features)
22. [UI Layout](#22-ui-layout)
23. [Audio Design](#23-audio-design)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | BitLife - Life Simulator |
| Developer | Candywriter LLC |
| Initial Release | September 29, 2018 (iOS); March 22, 2019 (Android) |
| Genre | Life simulation / interactive fiction |
| Platform | iOS, Android (portrait orientation, single-hand mobile play) |
| Perspective | 2D text-and-UI-driven vertical scrolling interface |
| Core Fantasy | Live an entire human life from birth to death through year-by-year decisions |
| Input | Tap-only; no physical controls, no accelerometer |
| Session Length | 5-20 minutes per complete life |
| Content Rating | 17+ (mature themes: crime, substance use, sexual content) |

### Design Pillars

1. **One-tap aging**: Every tap of the Age button advances the character one year, generating events and updating all stats.
2. **Branching life narrative**: Player choices cascade across decades, creating unique life stories each playthrough.
3. **Accessible depth**: Instantly understandable tap-to-play surface with hundreds of interconnected systems beneath.
4. **Replayability through randomization**: Birth country, family wealth, base stats, and events are randomized each new life.
5. **Legacy continuity**: Death is not the end; players can continue as their children and build multi-generational dynasties.

---

## 2. Technical Foundation

### Display & Rendering

| Property | Value |
|----------|-------|
| Orientation | Portrait (vertical) only |
| Target resolution | Device-native; UI scales with Safe Area insets |
| Frame rate | 60 FPS for UI animations and transitions |
| Rendering approach | UIKit / native views (iOS); XML layouts (Android) — not a game engine |
| Text rendering | System fonts, dynamic type support |
| Character avatars | Emoji-style 2D vector heads with customizable features |

### Architecture

```
1. Player taps Age+ button or selects an activity/action
2. Game engine resolves all pending actions in deterministic order
3. Random events are generated from weighted probability tables seeded per-year
4. Stats are recalculated (health, happiness, smarts, looks, hidden stats)
5. Relationship meters are updated based on interactions and neglect
6. Financial calculations run (salary, expenses, asset appreciation/depreciation)
7. Death check runs (age + health + karma + random factor)
8. UI refreshes: life log entry appended, stat bars animated, modals queued
9. If character dies: death summary screen, ribbon award, legacy option
```

### Update Resolution Order (Per Year Tick)

```
1. Process player-initiated actions (activities, purchases, interactions)
2. Generate and present forced random events (require player choice)
3. Auto-resolve passive systems (school grades, job performance, relationship decay)
4. Apply stat deltas from all sources
5. Process financial transactions (salary, bills, loan interest, asset changes)
6. Run health/disease progression
7. Run death probability check
8. Advance age counter by 1 year (or 6 months if half-year mode enabled)
9. Unlock/lock age-gated activities and menus
10. Append year summary to life log
11. Check achievement/ribbon progress
```

### Data Persistence

| Property | Value |
|----------|-------|
| Save format | Local device storage (SQLite / CoreData on iOS; SharedPreferences + SQLite on Android) |
| Auto-save | After every year advancement |
| Cloud sync | iCloud (iOS) / Google Play Games (Android) for Bitizen users |
| Save slots | 1 active life + cemetery of past lives |

---

## 3. Core Aging Mechanic

### The Age Button

The central interaction of BitLife. A large circular button labeled with a **"+"** symbol, positioned at the bottom-center of the main screen.

| Property | Value |
|----------|-------|
| Location | Bottom-center of screen, above bottom tab bar |
| Label | "Age +" or "AGE" with current age displayed |
| Tap behavior | Advances character age by 1 year (default) or 6 months (if half-year aging enabled in settings) |
| Availability | Disabled when a modal event is pending resolution |
| Animation | Brief pulse/bounce on tap; stat bars animate to new values |
| Cooldown | None; can be tapped rapidly to speed through years |

### Half-Year Aging (Optional Setting)

| Property | Value |
|----------|-------|
| Toggle location | Settings menu |
| Effect | Each tap advances 6 months instead of 1 year |
| Event generation | Events can fire at each half-year increment |
| Age display | Shows fractional ages (e.g., 14.5) |

### Year Resolution Flow

```
Player taps Age+
  |
  v
[Pre-age events fire] --> forced modals if any (e.g., "Your teacher caught you cheating")
  |
  v
[Optional activities already queued are resolved]
  |
  v
[Passive systems update: school grades, job performance, relationships]
  |
  v
[Random events generated and presented one at a time]
  |
  v
[Stats recalculated]
  |
  v
[Financial update: salary deposited, expenses deducted]
  |
  v
[Disease/health progression]
  |
  v
[Death check]
  |
  v
[Age counter incremented]
  |
  v
[Life log entry appended to scrollable history]
```

---

## 4. Character Creation System

### New Life Screen

When starting a new life, the player is presented with a character creation screen.

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| First Name | Text input | Random from country-appropriate name pool | Player can type custom name |
| Last Name | Text input | Random from country-appropriate name pool | Inherited from parents in generational play |
| Gender | Selection | Random | Male, Female (non-binary added in later updates) |
| Country | Selection | Random | 100+ countries with unique laws, economies, and customs |
| City | Auto-assigned | Random city within selected country | Determines local cost of living and available jobs |

### Randomized Birth Conditions

| Property | Range | Notes |
|----------|-------|-------|
| Happiness | 0-100 | Randomized at birth; influenced by family wealth and stability |
| Health | 0-100 | Randomized; can be low if born with congenital condition |
| Smarts | 0-100 | Randomized; partially inherited from parents |
| Looks | 0-100 | Randomized; partially inherited from parents |
| Karma (hidden) | 0-100 | Starts at 50 by default |
| Willpower (hidden) | 0-100 | Randomized at birth |
| Discipline (hidden) | 0-100 | Randomized at birth |
| Fertility (hidden) | 0-100 | Randomized; determines ability to conceive |

### Family Context at Birth

| Family Member | Always Present | Properties |
|---------------|----------------|------------|
| Mother | Yes | Name, age (18-45), relationship meter (starts 60-100), occupation, wealth |
| Father | Usually | Name, age (18-55), relationship meter (starts 40-100), occupation, wealth; may be absent |
| Siblings | Random (0-4) | Name, age, gender, relationship meter |
| Step-parents | Possible | If parents divorced before character's birth |
| Grandparents | Possible | May appear in relationship list |

### God Mode Character Creation (Premium)

With God Mode ($8.99 one-time purchase), the player can customize:

| Customizable Property | Options |
|-----------------------|---------|
| All 4 visible stats | Set any value 0-100 |
| Hidden stats | Set Willpower, Discipline, Fertility, Karma 0-100 |
| Appearance | Eye color, hair style, facial hair, brow shape |
| Country | Full selection (not random) |
| Sexuality | Straight, Gay, Bisexual |
| Royalty toggle | Born into royal family (country must have monarchy) |
| Parent stats | Customize mother/father attributes |

**Limitations**: Cannot change birthday, conception method, siblings at birth, or skin color.

---

## 5. Character Stats System

### Primary (Visible) Stats

Four horizontal progress bars displayed beneath the character avatar on the main screen.

| Stat | Range | Color | Description | Raises When | Drops When |
|------|-------|-------|-------------|-------------|------------|
| Happiness | 0-100 | Green | Emotional well-being and life satisfaction | Positive events, vacations, good relationships, meditation, entertainment | Negative events, death of loved ones, job loss, prison, illness, loneliness |
| Health | 0-100 | Red | Physical condition and vitality | Doctor visits, gym, healthy diet, walks, martial arts | Aging (gradual), disease, injury, substance abuse, unhealthy diet, stress |
| Smarts | 0-100 | Blue | Intelligence and knowledge | Library visits, reading books, studying harder, puzzle games | Difficult to lower; drug use, head injuries, severe illness |
| Looks | 0-100 | Purple/Pink | Physical attractiveness | Gym, plastic surgery, good health maintenance | Aging (especially after 40), injuries, botched surgery, weight gain |

### Hidden Stats

Not displayed on the main screen. Revealed through meditation (available from age 12) which randomly reveals one hidden stat per session.

| Stat | Range | Effect |
|------|-------|--------|
| Karma | 0-100 | Influences luck of random events; higher karma = longer lifespan and more positive outcomes. Increases from good deeds (charity, volunteering, complimenting). Decreases from crime, cruelty, selfishness. |
| Willpower | 0-100 | Determines ability to overcome addictions (alcohol, drugs, gambling). High willpower = faster addiction recovery. |
| Discipline | 0-100 | Affects school/work performance and resistance to gaining addictions. High discipline = better grades and job evaluations without extra effort. |
| Fertility | 0-100 | Probability modifier for conceiving children. Low fertility may require fertility treatments. |
| Craziness | 0-100 | NPC stat only. Determines partner willingness for exotic pets, threesomes, risky proposals. |
| Athleticism | 0-100 | Hidden fitness stat. Affects sports performance, military deployment success, and physical confrontation outcomes. |

### Special Stats (Conditional)

| Stat | Visibility | When Active | Range |
|------|-----------|-------------|-------|
| Fame | Visible bar (5th bar) | When character becomes famous through career or social media | 0-100 |
| Respect | Visible bar (replaces Fame) | When character is royalty | 0-100 |
| Greatness | Visible bar | When character is a professional athlete | 0-100 |
| Grades | Visible in school menu | During education (elementary through graduate school) | Letter grades A+ to F or percentage |
| Popularity | Visible in school menu | During school years | 0-100 |
| Job Performance | Visible in career menu | While employed | 0-100 (bar) |
| Stress | Internal modifier | Always | Affects Happiness and Health decay rates |

### Stat Change Magnitudes (Approximate)

| Action | Stat Affected | Typical Change |
|--------|---------------|----------------|
| Visit gym | Health +2 to +5, Looks +1 to +3 | Per year |
| Visit library | Smarts +2 to +6 | Per year |
| Read a book | Smarts +1 to +4 | Per year |
| Meditate | Happiness +1 to +5, Health +1 to +3 | Per year |
| Go for a walk | Health +1 to +3, Happiness +1 to +2 | Per year |
| Healthy diet | Health +3 to +8 per year | Sustained effect |
| High-calorie diet | Health -10 to -17 per year | Sustained effect |
| Visit doctor | Health +5 to +20 | Depends on treatment |
| Vacation | Happiness +5 to +15 | One-time per trip |
| Plastic surgery (successful) | Looks +5 to +20 | One-time |
| Plastic surgery (botched) | Looks -10 to -30, Health -5 to -15 | One-time |
| Natural aging per year (after 40) | Health -1 to -3, Looks -1 to -2 | Gradual |
| Prison year served | Happiness -5 to -15 | Per year in prison |
| Death of close relative | Happiness -10 to -40 | One-time |

---

## 6. Life Stages

### Stage Definitions

| Stage | Age Range | Key Unlocks | Restrictions |
|-------|-----------|-------------|--------------|
| Infant | 0-1 | None; purely event-driven (born events, family context) | No player actions available |
| Toddler | 2-4 | Minimal interactions; can talk to family | No menus; random baby events only |
| Child | 5-11 | School begins (age 5-6 country-dependent); library; family interactions; can have pets | No jobs, no romance, no driving, no crime |
| Tween/Pre-Teen | 12-13 | Meditation, gym, memory test, school clubs; social media accounts (age 13) | Limited romance (crushes, school dance) |
| Teenager | 14-17 | Dating begins (age 14); part-time jobs (age 14-16); driving test (age 15-17 country-dependent); school sports and clubs | Cannot buy property, limited crime options |
| Young Adult | 18-29 | Full career access; university; military; full crime; marriage; property purchase; emigration; nightlife; casino (age 21 in US); all medical options | None |
| Adult | 30-49 | Peak earning years; career promotions; midlife events | Health begins gradual decline |
| Middle-Aged | 50-64 | Retirement becomes available; increased illness frequency | Accelerated health/looks decline |
| Senior | 65-79 | Retirement; increased disease risk; legacy planning intensifies | Many physical activities less effective |
| Elderly | 80-99 | High death probability each year; end-of-life events | Severe stat decline each year |
| Centenarian | 100-122 | Maximum theoretical lifespan; extremely rare | Near-certain death each year; 120+ is the practical cap |

### Age-Gated Activities Unlock Table

| Activity | Minimum Age | Notes |
|----------|-------------|-------|
| Library | 6 (school age) | Increases Smarts |
| Meditation | 12 | Reveals hidden stats |
| Gym | 12 | Increases Health and Looks |
| Memory Test | 12 | Mini-game for Smarts |
| Social Media | 13 | Create accounts on platforms |
| School Dance | 13 | Relationship event |
| Dating | 14 | Can ask out classmates |
| Part-Time Job | 14-16 | Country-dependent; limited hours |
| Driving Test | 15-19 | Country-dependent |
| Full-Time Job | 18 | All careers available |
| University | 18 | After high school graduation |
| Military Enlistment | 18 | All branches |
| Nightlife/Clubbing | 18 | Country-dependent |
| Property Purchase | 18 | Houses, cars, etc. |
| Emigration | 18 | After high school |
| Casino/Gambling | 18-21 | Country-dependent (21 in US) |
| Plastic Surgery | 18 | All cosmetic procedures |
| Exotic Pets | 18 | Requires Bitizen |
| Alcohol (legal) | 18-21 | Country-dependent |
| Run for Political Office | 18+ | Varies by office level |

---

## 7. Education System

### Education Progression

```
Elementary School (age 5-6 to 10-11, country-dependent)
  |
  v
Middle School / Junior High (age 11-13)
  |
  v
High School / Secondary School (age 14-17/18/19, country-dependent)
  |
  v
[Choice Point: Work / University / Military / Gap Year]
  |
  v
University (4 years) --> [Choice Point: Work / Graduate School / Professional School]
  |
  v
Graduate School (2-3 years) / Professional School (2-4 years)
```

### Elementary School

| Property | Value |
|----------|-------|
| Entry age | 5-6 (country-dependent) |
| Duration | 5-6 years |
| Player actions | Study harder, ask parent to help with homework |
| Grades | Affected by Smarts stat and "study harder" choice |
| Events | Bullying, teacher interactions, field trips, show-and-tell |

### Middle School / Junior High

| Property | Value |
|----------|-------|
| Entry age | 11-12 |
| Duration | 2-3 years |
| New features | Clubs, sports teams, cliques, school dance |
| Cliques available | Brainy Kids, Mean Girls (female only), Jocks (male only), Skaters, Goths, Emo Kids, Band Geeks, Talented Kids |
| Popularity system | 0-100 bar; affected by clique, clubs, looks, events |
| Grades | Letter grades A+ through F |

### High School / Secondary School

| Property | Value |
|----------|-------|
| Entry age | 14-15 |
| Graduation age | 17-19 (country-dependent) |
| New features | Part-time jobs, dating, driving test, SAT/ACT equivalent |
| Sports teams | Football, Basketball, Soccer, Baseball, Swimming, Track, Volleyball, Tennis, etc. |
| Clubs | Drama, Band, Chess, Debate, Student Government, Yearbook, Art, Computer, etc. |
| Dropout option | Can drop out (age 16+ in most countries); permanently limits career options |
| Expulsion | Possible from disciplinary issues; affects future education |

### University

| Property | Value |
|----------|-------|
| Duration | 4 years |
| Tuition | Varies by country ($10,000-$100,000+ total in US) |
| Payment options | Scholarship (requires high grades/smarts), parents pay, student loan, cash |
| Major selection | 30+ majors (see table below) |
| Fraternity/Sorority | Available in US/Canada; requires passing Greek mythology trivia question |
| Graduation GPA | Affected by Smarts, Discipline, study habits |
| Dropout | Can drop out at any point; still accumulates debt |

### University Majors (Partial List)

| Major | Career Paths Unlocked |
|-------|----------------------|
| Biology | Medical School, Veterinary School, Pharmacy School |
| Chemistry | Medical School, Pharmacy School, Lab careers |
| Criminal Justice | Law School, Police, FBI |
| Computer Science | Software, IT, Game Development |
| English | Law School, Writing, Journalism |
| Finance | Business School, Banking, Accounting |
| Economics | Business School, Finance careers |
| Nursing | Direct nursing career |
| Political Science | Law School, Political career |
| Psychology | Graduate School, Counseling |
| Mathematics | Business School, Engineering, Academia |
| Music | Music career (supplementary) |
| Art | Art careers, Design |
| Marketing | Business School, Marketing careers |
| Information Systems | Business School, IT careers |
| Accounting | Business School, Accounting careers |
| History | Graduate School, Teaching, Law School |
| Philosophy | Graduate School, Law School |
| Engineering | Engineering careers, Graduate School |

### Graduate & Professional Schools

| School | Duration | Prerequisites | Career Paths |
|--------|----------|---------------|--------------|
| Graduate School (M.A./M.S./Ph.D.) | 2-3 years | Bachelor's degree | Academia, Research, Specialized roles |
| Medical School | 4 years | Biology, Chemistry, or Nursing major | Doctor, Surgeon, Psychiatrist |
| Law School | 3 years | Criminal Justice, Political Science, English, Philosophy, or History major | Lawyer, Judge, Magistrate |
| Business School (MBA) | 2 years | Accounting, Economics, English, Finance, Info Systems, Marketing, or Mathematics major | CEO, Executive, Business Manager |
| Dental School | 4 years | Biology or Chemistry major | Dentist |
| Veterinary School | 4 years | Biology major | Veterinarian |
| Pharmacy School | 4 years | Biology or Chemistry major | Pharmacist |
| Nursing School | 2 years | Direct entry or Biology major | Registered Nurse |

---

## 8. Career System

### Career Categories

| Category | Entry Requirement | Example Roles |
|----------|-------------------|---------------|
| Part-Time | Age 14-16+ | Babysitter, Dog Walker, Newspaper Delivery, Fast Food Worker, Retail Clerk |
| Freelance/Gig | Age 18+ | Freelance Writer, Photographer, Tutor, Handyman |
| Corporate/Standard | Age 18+ (some require degrees) | 200+ job titles across industries |
| Military | Age 18+ | Enlisted (5 branches) or Officer (requires degree) |
| Special: Musician | Age 18+; must master instrument/vocals | Solo Artist or Band Member |
| Special: Actor | Age 18+; high Looks (70+); acting lessons | Voice Actor, TV Actor, Movie Star |
| Special: Athlete | Age 18+; school sports history | Professional sports across multiple leagues |
| Special: Politics | Age 18+; high stats; wealth for campaigns | School Board to President/Prime Minister |
| Special: Organized Crime | Age 18+ | Mafia Associate to Godfather |
| Special: Royalty | Birth into royal family | Prince/Princess to King/Queen |

### Career Progression Mechanics

| Property | Details |
|----------|---------|
| Job listings | Randomized each year; 5-15 available positions refreshed annually |
| Application | Tap to apply; success based on education, experience, Smarts, Looks, criminal record |
| Interviews | Some jobs require interview; questions may test relevant knowledge |
| Starting salary | Varies by role: $15,000 (entry-level) to $80,000+ (professional) |
| Raises | Annual; 1-10% based on performance rating |
| Promotions | Typical path: Jr. [Title] -> [Title] -> Sr. [Title] or equivalent; 3-5 years between promotions |
| Performance | 0-100 bar; affected by Smarts, Discipline, actions ("Work Harder", "Suck Up to Boss") |
| Firing | Possible from poor performance, absenteeism, criminal record discovery, economic events |
| Retirement | Available after age 50+; pension depends on years worked and career type |
| Coworker interactions | Can befriend, date, argue with, or assault coworkers |
| Boss interactions | Can request raise, complain, suck up to, or have conflicts with supervisor |

### Salary Ranges by Career Tier

| Tier | Examples | Salary Range (USD equivalent) |
|------|----------|-------------------------------|
| Entry Level | Cashier, Server, Janitor | $15,000 - $30,000 |
| Skilled Labor | Electrician, Mechanic, Plumber | $30,000 - $60,000 |
| Professional | Accountant, Engineer, Teacher | $40,000 - $90,000 |
| Advanced Professional | Lawyer, Doctor, Dentist, Pilot | $80,000 - $250,000 |
| Executive | CEO, VP, Director | $100,000 - $500,000+ |
| Special Career (peak) | Famous Actor, Star Athlete, Hit Musician | $500,000 - $10,000,000+ |
| Royalty | King/Queen | Depends on country; stipend + palace |

### Military Career Specifics

| Branch | Enlisted Path | Officer Path |
|--------|--------------|--------------|
| Army | Private -> Specialist -> Sergeant -> Staff Sergeant -> Sergeant First Class -> Master Sergeant -> Sergeant Major | 2nd Lieutenant -> 1st Lieutenant -> Captain -> Major -> Lt. Colonel -> Colonel -> Brigadier General -> Major General -> Lt. General -> General |
| Navy | Seaman Recruit -> Seaman Apprentice -> Seaman -> Petty Officer (3rd/2nd/1st) -> Chief Petty Officer -> Senior/Master CPO | Ensign -> Lieutenant JG -> Lieutenant -> Lt. Commander -> Commander -> Captain -> Rear Admiral -> Vice Admiral -> Admiral |
| Air Force | Airman Basic -> Airman -> Airman First Class -> Staff/Tech/Master Sergeant -> Chief Master Sergeant | Same as Army (with Air Force titles) |
| Marines | Private -> PFC -> Lance Corporal -> Corporal -> Sergeant -> Staff Sergeant -> Gunnery Sergeant -> Master Sergeant | Same as Army structure |
| Coast Guard | Similar to Navy enlisted | Similar to Navy officer |

| Military Property | Value |
|-------------------|-------|
| Enlistment requirement | Age 18, high school diploma |
| Officer requirement | Age 18+, bachelor's degree |
| Deployment | Random; Minesweeper mini-game (3-10 mines) |
| AWOL option | Can go AWOL; results in dishonorable discharge + possible prison |
| Retirement | After 20+ years of service; military pension |
| Medals | Awarded for successful deployments |

---

## 9. Relationship System

### Relationship Categories

| Category | Members | Meter Range | Key Interactions |
|----------|---------|-------------|------------------|
| Family | Parents, siblings, children, grandparents, aunts/uncles, nieces/nephews, step-relatives | 0-100 | Spend time, compliment, argue, give gift, have conversation, insult, assault |
| Romantic | Boyfriend/girlfriend, fiance, spouse, ex-partners | 0-100 | Date, propose, marry, make love, break up, divorce, cheat, threesome |
| Friends | School friends, work friends, neighbors | 0-100 | Hang out, compliment, gift, argue, unfriend, best friend designation |
| Enemies | Formed from conflicts | 0-100 (hostility) | Confront, insult, assault, reconcile |
| Coworkers | Workplace associates | 0-100 | Befriend, conflict, romance |
| Classmates | School associates | 0-100 | Befriend, bully, school dance |

### Relationship Meter Mechanics

| Property | Value |
|----------|-------|
| Starting value (parents) | 60-100 (randomized; affected by family stability) |
| Starting value (new friend) | 30-60 |
| Starting value (new romantic partner) | 40-70 |
| Decay per year (no interaction) | -3 to -8 per year |
| Positive interaction boost | +2 to +15 per action |
| Negative interaction penalty | -5 to -30 per action |
| Threshold for break-up risk | Below 30 |
| Threshold for divorce initiation by NPC | Below 20 |

### Romance & Dating

| Feature | Details |
|---------|---------|
| Minimum dating age | 14 (school crushes/dates) |
| Finding partners | School classmates, coworkers, dating app (age 18+), random encounters, friends-of-friends |
| Dating app | Swipe-style interface; shows name, age, looks, occupation; can like or pass |
| Hookups | One-night stands available; risk of STDs and unwanted pregnancy |
| Love at first sight | Rare random event; instant high relationship |
| Sexuality | Straight, Gay, Bisexual (set at birth or via God Mode) |

### Marriage System

| Step | Details |
|------|---------|
| Proposal | Player can propose with ring (purchased from jewelry store) or no ring; ring increases acceptance |
| Ring types | Fake ring (cheap, may be detected by smart partner), modest ring, expensive ring, diamond ring |
| Acceptance factors | Relationship level, ring quality, partner's Craziness, relationship duration |
| Prenuptial agreement | Optional; protects pre-marriage assets; partner often refuses (high rejection rate) |
| Wedding | Choose venue and honeymoon destination; wedding costs vary |
| Honeymoon | Travel event with positive stat boosts |
| Married life | Spouse moves in; shared finances; can request spouse stop working; fertility options |
| Divorce | Initiated by player or spouse; assets split 50/50 without prenup; emotional/financial impact |
| Remarriage | Can re-engage and remarry an ex-spouse if relationship rebuilt |

### Children

| Property | Value |
|----------|-------|
| Conception | Natural (requires fertility + sexual activity), fertility treatment, adoption |
| Birth control | Can be used or refused; partner may agree or disagree |
| Pregnancy | 1 year duration (1 age tick) |
| Adoption | Available at any adult age; choose from available children of varying ages |
| Child stats | Randomized at birth; partially inherited from parents |
| Parenting actions | Spend time, read to, take to movies, discipline, neglect, abandon |
| Abandonment | Child removed from active relationship but remains in list with destroyed relationship |
| Child's autonomy | As children age, they develop their own stats, education, relationships |
| Playable child | On death, player can continue as any living child |

### Pets

| Category | Examples | Availability |
|----------|----------|-------------|
| Dogs | Labrador, Golden Retriever, Poodle, etc. (20+ breeds) | Pet shop, breeder (Bitizen) |
| Cats | Siamese, Persian, Maine Coon, etc. (15+ breeds) | Pet shop, breeder (Bitizen) |
| Small animals | Hamster, Rabbit, Goldfish, Turtle, Parrot | Pet shop |
| Exotic pets | Tiger, Lion, Monkey, Gorilla, Panther, Snake, Coyote | Exotic dealer (Bitizen, age 18+) |
| Horses | Various breeds | Horse ranch (Bitizen, age 18+); requires equestrian property |
| Unicorn | Single mythical breed | Extremely rare encounter event |

| Pet Property | Value |
|-------------|-------|
| Relationship meter | 0-100 |
| Health meter | 0-100 |
| Lifespan | Varies by species (goldfish ~5 years, dog ~12 years, horse ~30 years) |
| Interactions | Pet, walk, bathe, vet visit, play, release, put down |
| Death | Natural causes, illness, attack (mauling); affects Happiness |

---

## 10. Crime & Legal System

### Crime Types

| Crime | Risk Level | Potential Gain | Arrest Chance | Sentence Range |
|-------|-----------|----------------|---------------|----------------|
| Pickpocket | Low | $10 - $500 | 20-40% | 0-1 year |
| Shoplifting | Low | Item value | 25-45% | 0-1 year |
| Burglary | Medium | $500 - $50,000+ (mini-game) | 30-50% | 1-5 years |
| Grand Theft Auto | Medium | Car value | 30-60% | 1-5 years |
| Bank Robbery | High | $10,000 - $500,000 | 50-80% | 5-20 years |
| Train Robbery | High | $5,000 - $200,000 | 40-70% | 5-15 years |
| Murder | Very High | None (eliminates target) | 40-90% | 15-life / death penalty |
| Assault | Medium | None | 30-60% | 1-5 years |
| Drug Dealing | Medium-High | $1,000 - $100,000 | 30-60% | 2-10 years |
| Arson | High | None | 40-70% | 3-10 years |
| Tax Evasion | Medium | Tax savings | 20-40% | 1-5 years + fines |
| Insurance Fraud | Medium | Claim amount | 25-50% | 1-5 years + fines |
| Extortion | Medium | Variable | 30-50% | 2-8 years |
| Porch Piracy | Low | Package value | 20-35% | 0-1 year |

### Legal Process

| Stage | Details |
|-------|---------|
| Arrest | Immediate upon failed crime; shown arrest notification |
| Trial | Choose: plead guilty, plead not guilty, or hire lawyer |
| Lawyer | Costs $5,000 - $50,000+; reduces sentence; public defender is free but less effective |
| Verdict | Guilty or Not Guilty; influenced by evidence, lawyer quality, crime severity |
| Sentencing | Prison time assigned; displayed in years |
| Appeal | Can appeal verdict once; chance of reduced sentence or acquittal |

### Prison System

| Property | Value |
|----------|-------|
| Security levels | Minimum, Medium, Maximum, Supermax |
| Assignment basis | Crime severity and repeat offenses |
| Activities in prison | Start a riot, escape, join gang, get prison job, appeal, age up |
| Gang joining | Can join prison gang; provides protection but requires criminal acts |
| Prison jobs | Available for reduced boredom; small income |
| Good behavior | Can reduce sentence; early parole possible |
| Solitary confinement | Triggered by bad behavior; severe Happiness penalty |
| Stat effects | Happiness -5 to -15/year; Health may decline; Looks may decline |
| Release | After serving sentence; criminal record persists |
| Parole | Possible with good behavior; must maintain conditions |

### Organized Crime

| Property | Value |
|----------|-------|
| Joining | Available at age 18+; must apply and be accepted |
| Syndicates | Mafia, Yakuza, Triads, Cartel, Irish Mob, Russian Mafia (country-dependent) |
| Ranks | Associate -> Soldier -> Capo -> Underboss -> Boss/Godfather |
| Activities | Extort businesses, commit heists, whack members, donate to family |
| Extortion options (if refused) | Leave alone, shake them down, whack them out, scare them |
| Income | Cut of family operations; increases with rank |
| Leaving | Very difficult; may be "whacked" for trying to leave |
| Boss challenges | Can challenge current boss for leadership |

### Death Penalty

| Property | Value |
|----------|-------|
| Availability | Country/state-dependent |
| Methods | Lethal injection, electric chair, firing squad, hanging |
| Trigger | Murder conviction (especially multiple counts) in death-penalty jurisdiction |
| Appeal | Can appeal death sentence; chance of commutation to life |

---

## 11. Health System

### Disease Categories

| Category | Examples | Severity | Treatment |
|----------|----------|----------|-----------|
| Common illnesses | Cold, Flu, Stomach virus | Low | Doctor visit; self-resolving |
| Chronic conditions | Asthma, Diabetes, High blood pressure, Sickle cell | Medium | Ongoing treatment; manageable |
| Mental illness | Depression, Anxiety, PTSD, Schizophrenia, Bipolar, Anorexia, Bulimia | Medium-High | Psychiatrist visits; medication |
| Cancer | Various types (lung, brain, breast, etc.) | High | Medical treatment; may be terminal |
| STDs | HIV, Herpes, Chlamydia, Gonorrhea | Medium-High | Doctor treatment; some incurable |
| Tropical diseases | Malaria, Yellow Fever | Very High | Medical treatment; often fatal without treatment |
| Rare/Fatal | Rabies, Plague, Ebola, Lupus | Very High | Emergency treatment; high mortality |
| Gym-related | Athlete's foot, Ringworm | Low | Doctor visit |
| Addiction-related | Liver disease, Lung cancer (from smoking) | High | Medical treatment |
| Congenital | Various birth defects | Varies | Depends on condition |

### Medical Providers

| Provider | Available Age | Cost | Effectiveness | Notes |
|----------|--------------|------|---------------|-------|
| Medical Doctor | Any (via parents if <18) | $$ | High | Standard treatment for physical ailments |
| Psychiatrist | 18+ | $$$ | High | For mental illness; medication and therapy |
| Alternative Doctor | 18+ | $ | Low-Medium | Unorthodox treatments; mixed results |
| Witch Doctor | 18+ | $ | Very Low (random) | May cure, do nothing, or kill the character |
| Emergency Room | Any | $$$$ | Very High | For critical conditions |

### Plastic Surgery

| Procedure | Cost Range | Looks Boost | Risk of Botch | Limit |
|-----------|-----------|-------------|----------------|-------|
| Botox | $500 - $5,000 | +2 to +8 | 10-30% | Unlimited |
| Facelift | $5,000 - $30,000 | +5 to +15 | 15-35% | Unlimited |
| Nose Job (Rhinoplasty) | $3,000 - $15,000 | +3 to +12 | 10-30% | Multiple |
| Liposuction | $3,000 - $20,000 | +3 to +10 | 15-35% | Multiple |
| Breast Augmentation | $5,000 - $15,000 | +3 to +10 | 10-25% | Once |
| Brazilian Butt Lift | $5,000 - $20,000 | +3 to +10 | 15-35% | Multiple |
| Eyelid Surgery | $2,000 - $10,000 | +2 to +8 | 10-25% | Multiple |
| Tummy Tuck | $5,000 - $15,000 | +3 to +10 | 15-30% | Multiple |
| Gender Reassignment | $20,000 - $100,000 | Varies | 20-40% | Once |

**Surgeon selection**: Two surgeons offered per procedure. Higher-priced surgeon has higher Reputation bar and lower botch chance. Cheaper surgeon has high botch probability.

**Botched surgery effects**: Looks -10 to -30, Health -5 to -15, Happiness -10 to -25.

### Diet Options

| Diet | Health Effect/Year | Looks Effect | Notes |
|------|-------------------|--------------|-------|
| Mediterranean | +3 to +6 | +1 to +2 | Balanced, healthy |
| Vegetarian | +2 to +5 | +1 | Good health impact |
| Vegan | +2 to +4 | +1 | Slight health boost |
| Keto | +1 to +3 | +1 to +3 | Good for weight loss |
| Paleo | +1 to +3 | +1 to +2 | Moderate benefit |
| High Calorie | -10 to -17 | -2 to -5 | Causes weight gain, heart disease risk |
| Nutrisystem | +2 to +4 | +1 to +2 | Moderate benefit |
| Jenny Craig | +2 to +4 | +1 to +2 | Moderate benefit |

### Mind & Body Activities

| Activity | Available Age | Effect |
|----------|-------------|--------|
| Gym | 12+ | Health +2-5, Looks +1-3 |
| Library | 6+ | Smarts +2-6 |
| Meditation | 12+ | Happiness +1-5, Health +1-3; reveals one hidden stat |
| Read a Book | 6+ | Smarts +1-4; choose from multiple titles |
| Go for a Walk | 12+ | Health +1-3, Happiness +1-2 |
| Martial Arts | 12+ | Health +2-4, Athleticism boost; self-defense skill |
| Gardening | 12+ | Happiness +1-3 |
| Diet | 12+ | See diet table above |
| Memory Test | 12+ | Mini-game; boosts Smarts on success |

### Death Mechanics

| Cause | Trigger |
|-------|---------|
| Old age | Age 70+ with declining health; probability increases each year |
| Disease (untreated) | Leaving serious illness untreated for 1-3 years |
| Disease (terminal) | Cancer or other terminal illness despite treatment |
| Overdose | Drug addiction + continued use |
| Heart attack / Stroke | High blood pressure + stress + age |
| Murder (by NPC) | Prison violence, organized crime, random assault |
| Accident | Car crash, plane crash, shipwreck |
| Execution | Death penalty sentence carried out |
| Suicide | Player chooses "Surrender" option |
| Animal attack | Exotic pet mauling, wild animal encounter |
| Botched surgery | Rare outcome from plastic surgery |
| Military combat | Failed deployment mini-game |
| Drowning | Shipwreck without swimming ability |
| Electrocution | Prison escape attempt or rare event |

### Death Probability Formula (Approximate)

```
base_death_chance = 0.01% (age 0-30)
                  + 0.05% per year (age 30-50)
                  + 0.2% per year (age 50-65)
                  + 0.5% per year (age 65-80)
                  + 2% per year (age 80-90)
                  + 5% per year (age 90-100)
                  + 15% per year (age 100-110)
                  + 30% per year (age 110+)

modifiers:
  + health_penalty: (100 - health) * 0.1%
  - karma_bonus: karma * 0.05%
  + disease_modifier: active serious disease adds 5-30%
  + addiction_modifier: active addiction adds 1-5%
```

---

## 12. Financial System

### Income Sources

| Source | Details |
|--------|---------|
| Salary | Paid annually upon age-up; amount depends on career |
| Inheritance | Received when relatives die; amount depends on their wealth and will |
| Lottery winnings | Purchased tickets; very low win probability |
| Casino winnings | From gambling mini-games |
| Horse racing winnings | 5x bet if correct horse wins |
| Crime proceeds | From successful criminal activities |
| Asset sales | Profit from selling appreciated assets |
| Social media income | From sponsored posts when famous |
| Book royalties | From published books (famous characters) |
| Alimony received | From divorced wealthy spouse |
| Trust fund | If born into wealthy family |

### Expenses

| Expense | Details |
|---------|---------|
| Living expenses | Automatic annual deduction; scales with lifestyle |
| Mortgage / Rent | Monthly housing costs |
| Car payment | If financed |
| Student loans | Annual payment until paid off; accumulates interest |
| Child support / Alimony | If divorced with children |
| Medical bills | Doctor visits, surgery, treatment |
| Lawyer fees | $5,000 - $50,000+ per legal matter |
| Taxes | Income tax (country-dependent rate); estate tax on inheritance |
| Pet care | Vet bills, food, maintenance |

### Asset System

#### Real Estate

| Property | Value |
|----------|-------|
| Types | Apartment, Condo, Townhouse, Single Family, Ranch, Mansion, Castle, Equestrian Estate |
| Price range | $30,000 - $50,000,000+ |
| Purchase age | 18+ |
| Condition bar | 0-100%; deteriorates annually |
| Appreciation | Houses can appreciate 1-5% per year |
| Renovation | Costs money; restores condition and increases value |
| House flipping | Buy cheap -> renovate -> sell for profit |
| Mortgage | Available; monthly payments with interest |
| Multiple properties | Can own multiple homes simultaneously |
| Country restriction | Cannot use properties in country after emigrating (but can still own them) |

#### Vehicles

| Vehicle Type | Price Range | Notes |
|-------------|-------------|-------|
| Economy Car | $5,000 - $25,000 | Basic transportation |
| Sedan | $20,000 - $50,000 | Mid-range |
| SUV | $25,000 - $70,000 | Family vehicle |
| Sports Car | $50,000 - $300,000 | High-end |
| Supercar | $200,000 - $5,000,000+ | Luxury |
| Motorcycle | $3,000 - $30,000 | Two-wheeled |
| Boat | $10,000 - $1,000,000+ | Requires boating license |
| Aircraft | $100,000 - $50,000,000+ | Requires pilot license |

| Vehicle Property | Value |
|-----------------|-------|
| Condition bar | 0-100%; deteriorates annually |
| Maintenance | Costs money; slows deterioration but does not restore condition |
| Depreciation | Cars lose value each year regardless of maintenance |
| Selling | Player sets price; buyers may haggle |
| Insurance | Optional; protects against accident loss |

#### Jewelry

| Property | Value |
|----------|-------|
| Types | Rings, Necklaces, Bracelets, Watches, Earrings |
| Price range | $500 - $500,000+ |
| Value trend | Generally depreciates over time even with maintenance |
| Gifting | Can give jewelry to partners (increases relationship) |
| Heirloom potential | Some jewelry becomes family heirloom |

### Casino & Gambling

| Game | Available Age | Mechanics |
|------|-------------|-----------|
| Blackjack | 18-21+ (country-dependent) | Standard blackjack rules; hit, stand, double down, split; win pays 2x bet |
| Horse Racing | 18-21+ | Choose 1 of 5 horses; if winner, pays 5x bet |
| Slots | 18-21+ | Pull lever; randomized outcome |
| Lottery | 18+ | Buy tickets; extremely low win probability; jackpots can be millions |

### Gambling Addiction Risk

Repeated gambling can trigger gambling addiction; affected by Discipline and Willpower stats.

---

## 13. Activities System

### Activities Menu Categories

The Activities tab is the primary hub for player-initiated actions beyond the age-up button.

| Category | Sub-Activities |
|----------|---------------|
| Mind & Body | Gym, Library, Meditation, Read Book, Walk, Martial Arts, Diet, Garden, Memory Test |
| Love | Dating App, Hookup, Propose, Wedding Planning, Divorce |
| Crime | Pickpocket, Shoplifting, Burglary, Grand Theft Auto, Bank Robbery, Train Robbery, Murder, Porch Piracy, Arson, Drug Dealing, Extortion |
| Nightlife | Bar, Nightclub, House Party (age 18+) |
| Shopping | Cars, Houses, Jewelry, Musical Instruments, Boats, Aircraft |
| Relationships | Spend time, Gift, Conversation, Compliment, Insult, Assault (per relationship) |
| Medical | Doctor, Psychiatrist, Alternative Doctor, Witch Doctor, Plastic Surgery, Fertility Treatment |
| Travel | Vacation (plane), Cruise (ship) |
| Social Media | Post, Check notifications, Promote product (if famous) |
| Gamble | Casino, Horse Racing, Lottery |
| Emigrate | Request emigration to another country |
| Military | Enlist, Deploy, Go AWOL |
| Surrender | End character's life voluntarily |
| Assets | View and manage owned properties, vehicles, jewelry |
| Licenses | Driving test, Boating license, Pilot license |
| Fame Activities | Write book, Appear in commercial, Do talk show, Charity event (if famous) |
| Politics | Run for office, Campaign (if in politics) |

### Vacation System

| Property | Value |
|----------|-------|
| Vacation types | Plane trip to city/country; Cruise |
| Plane classes | Budget, Economy, Business, First Class |
| Cruise cabins | Interior, Ocean View, Balcony, Suite |
| Cost range | $500 (budget plane) to $50,000+ (suite cruise) |
| Happiness boost | +5 to +15 depending on quality |
| Travel events | Random encounters (positive or negative); shipwreck possible on cruise |
| Shipwreck survival | Depends on swimming ability (school swim team) |
| Travel with family | Can bring partner and children; higher cost |

### Driving Test

| Property | Value |
|----------|-------|
| Available age | 15-19 (country-dependent) |
| Cost | Free first attempt |
| Format | Multiple-choice questions about road rules |
| Pass requirement | Answer all questions correctly |
| Failure | Can retake next year |
| Benefit | Required to own and drive cars |

---

## 14. Fame & Social Media System

### Paths to Fame

| Path | Requirements |
|------|-------------|
| Acting | High Looks (70+); acting lessons; audition for roles |
| Music | Master instrument/vocals from childhood; join band or go solo at 18+ |
| Sports | Play school sports; get recruited to professional league |
| Writing | Publish books (available when famous from other means, or as career) |
| Social Media | Build followers to 300,000+ on any platform |
| Royalty | Born into royal family (automatic fame as "Respect") |
| Politics | Elected to high office |
| Crime (infamy) | Notorious criminal acts can generate negative fame |
| Modeling | High Looks; model career |
| Game Development | Successful game developer career |

### Fame Bar

| Property | Value |
|----------|-------|
| Range | 0-100 |
| Display | 5th stat bar beneath the standard four |
| Threshold for "Famous" status | Approximately 25+ fame |
| Effects of fame | Celebrity dating app access, paparazzi events, fan encounters, book/commercial opportunities |
| Fame decay | Slowly decreases if character stops doing fame-generating activities |

### Social Media Platforms

| Platform | Available Age | Best Content Types | Follower Mechanics |
|----------|-------------|-------------------|-------------------|
| Facebook | 13+ | Motivational posts, family updates, political opinions | Slowest growth |
| Instagram | 13+ | Thirst traps, lifestyle photos | Fast growth with high Looks |
| Twitter | 13+ | Political takes, hot takes, memes | Fast growth with controversy |
| YouTube | 13+ | Varied content; consistent posting required | Moderate growth |
| TikTok | 13+ | Thirst traps, trends, comedy | Fastest growth potential |
| Twitch | 13+ | Streaming content | Moderate growth |
| OnlyFans | 18+ | Adult content; thirst traps | Fast growth with high Looks |

| Social Media Property | Value |
|----------------------|-------|
| Verification threshold | 100,000+ followers AND 25+ fame |
| Post frequency | Can post multiple times per year |
| Content types | Political, Motivational, Thirst Trap, Comedy, Meme, Social Justice, Family |
| Follower growth (non-famous) | Slow; 10-1,000 per post |
| Follower growth (famous) | Exponential; 10,000-1,000,000+ per post |
| Sponsored posts | Available when famous; income based on follower count |
| Negative outcomes | Can lose followers from bad posts; controversy can help or hurt |

---

## 15. Immigration & Emigration System

### Emigration Process

| Property | Value |
|----------|-------|
| Available age | 18+ (after high school graduation) |
| Location | Activities tab -> Emigrate |
| Options shown | 8 randomized countries per attempt (refresh by closing and reopening) |
| Application | Request approval to live in selected country |
| Approval factors | Criminal record (major negative), career/education (positive), military service (may block) |
| Denial reasons | Criminal record, military service obligation, exotic pets deemed dangerous |
| Illegal immigration | If denied, option to sneak in; risk of being caught and deported |
| Golden Passport | Premium item; allows choosing any country instead of random 8 |

### Country Differences

| Property | Varies By Country |
|----------|-------------------|
| Currency | Local currency with exchange rates |
| Tax rates | Income and estate tax rates differ |
| Cost of living | Salary and expenses scale by country economy |
| Legal ages | Drinking, driving, gambling, marriage, military |
| Education system | School start age, graduation age, tuition costs |
| Healthcare costs | Free in some countries; expensive in others |
| Available careers | Some jobs country-specific |
| Royal families | Only certain countries have royalty option |
| Death penalty | Available in some countries only |
| Organized crime groups | Mafia (Italy), Yakuza (Japan), Triads (China), Cartel (Mexico/Colombia), etc. |
| Marriage laws | Same-sex marriage legal in some countries |

### Emigration Effects

| Effect | Details |
|--------|---------|
| Career | Lose current job; must find new employment in new country |
| Property | Cannot use properties in former country (but still own them) |
| Relationships | Can bring spouse and children (at extra cost); others remain behind |
| Citizenship | Gain citizenship in new country |
| Return visits | Can visit people in former country; attend funerals abroad |
| Currency conversion | Finances converted to new country's currency |

---

## 16. Military System

### Overview

| Property | Value |
|----------|-------|
| Branches | Army, Navy, Air Force, Marines, Coast Guard |
| Entry types | Enlisted (high school diploma) or Officer (bachelor's degree) |
| Enlistment age | 18+ |
| Tour of duty | Ongoing until retirement, discharge, or AWOL |
| Retirement benefit | Military pension after 20+ years of service |

### Deployment

| Property | Value |
|----------|-------|
| Frequency | Random; may be offered 0-2 times per year |
| Refusal | Can refuse deployment; risks disciplinary action or forced deployment |
| Mini-game | Minesweeper-style grid |
| First deployment mines | 3 mines |
| Subsequent deployments | Up to 10 mines |
| Success reward | Medal, promotion consideration |
| Failure consequence | Injury or death |

### AWOL (Absent Without Leave)

| Property | Value |
|----------|-------|
| Option | Can go AWOL at any time during military service |
| Consequence | Dishonorable discharge; possible prison time |
| Criminal record | AWOL creates permanent criminal record |

---

## 17. Random Events

### Event Categories

| Category | Frequency | Age Range | Examples |
|----------|-----------|-----------|---------|
| Childhood Events | 1-3 per year | 0-12 | Bully encounter, teacher interaction, finding a stray animal, imaginary friend |
| School Events | 1-2 per year | 6-22 | Pop quiz, school dance invitation, caught cheating, graduation ceremony |
| Work Events | 1-2 per year | 14+ (employed) | Overtime request, team building, office romance, boss conflict |
| Relationship Events | 1-3 per year | 14+ | Partner discovers cheating, surprise pregnancy, proposal from NPC, breakup |
| Health Events | 0-2 per year | Any | Random illness, injury, disease diagnosis |
| Financial Events | 0-2 per year | 18+ | Inheritance, lawsuit, tax audit, found money, lottery win |
| Crime Witness Events | 0-1 per year | Any | Witness a crime; choose to report, intervene, or ignore |
| Animal Encounters | 0-1 per year | Any | Stray animal, wild animal encounter, pet emergency |
| SOS Events | 0-1 per year | Any | Drowning person, car accident, fire; choose to help or ignore |
| Travel Events | 0-1 per trip | 18+ | Shipwreck, turbulence, lost luggage, romantic encounter abroad |
| Fame Events | 1-3 per year | Famous only | Stalker, paparazzi, celebrity feud, endorsement offer |
| Haunted House Events | Rare | 18+ | Paranormal activity; can cause PTSD or high blood pressure |
| Death Events | 0-1 per year | 60+ | Near-death experience, final illness, peaceful passing |

### Event Structure

Each random event follows this format:

```
[Emoji Icon] Event Title
---
Narrative text describing the situation (1-3 paragraphs).
---
[Option A] - First choice
[Option B] - Second choice  
[Option C] - Third choice (optional)
[Option D] - Fourth choice (optional)
```

### Childhood Event Examples

| Event | Options | Outcomes |
|-------|---------|----------|
| Bully teases you | Do nothing, Assault bully, Report to teacher, Talk to bully, Ask sibling for help | Varies: ignored, fight, resolution, continued bullying |
| Found $20 on ground | Keep it, Turn it in | Keep: +$20, slight karma loss; Turn in: karma boost, happiness boost |
| Stray cat appears | Adopt it, Ignore it, Chase it away | Adopt: new pet; Ignore: nothing; Chase: possible scratch |
| Parent argues | Side with mom, Side with dad, Stay out of it | Affects parent relationship meters differently |
| Teacher praises work | Thank teacher, Act modest, Show off to class | Different happiness and popularity effects |

### Adult Event Examples

| Event | Options | Outcomes |
|-------|---------|----------|
| Stranger offers drugs | Accept, Decline, Report to police | Accept: addiction risk; Decline: nothing; Report: karma boost |
| Found briefcase of money | Keep it, Turn it in to police, Look for owner | Keep: $5,000-$50,000 + karma loss; Turn in: karma boost; Look for owner: possible reward |
| Co-worker asks for loan | Lend money, Decline | Lend: lose money, relationship boost; Decline: slight relationship hit |
| Partner caught cheating | Confront, Forgive, Break up, Cheat in revenge | Various relationship and stat outcomes |
| Tornado/natural disaster | Seek shelter, Stay put, Help neighbors | Different health and property damage outcomes |

---

## 18. Mini-Games

### 18.1 Prison Escape

| Property | Value |
|----------|-------|
| Trigger | Choose "Escape" option while in prison |
| Grid size | 3x4 to 8x8 depending on prison security level |
| Player symbol | Character icon |
| Guard symbol | Guard icon |
| Exit | Marked position on grid edge |
| Walls | Gray blocks; impassable by player and guard |

**Movement Rules**:
- Player moves one cell per turn (up, down, left, right)
- Guard moves **two cells** per player move
- Guard prioritizes horizontal movement toward player first, then vertical
- Guard is blocked by walls
- Player must reach exit without being caught

**Security Level Grid Sizes**:

| Security Level | Grid Size | Difficulty |
|----------------|-----------|------------|
| Minimum | 3x4 to 5x4 | Easy; direct path often available |
| Medium | 5x5 to 6x6 | Moderate; requires wall manipulation |
| Maximum | 7x7 to 8x7 | Hard; complex wall mazes |
| Supermax | 8x8 | Very hard; multiple guard traps |

**Outcomes**:
- **Success**: Character escapes prison; becomes a fugitive; can be recaptured
- **Failure**: Additional 1-3 years added to sentence; "Attempted Escape" felony

**Strategy**: Lure guard behind walls so horizontal path is blocked, then move vertically to gain distance and reach exit.

### 18.2 Prison Riot (Snake Game)

| Property | Value |
|----------|-------|
| Trigger | Choose "Riot" option while in prison |
| Mechanic | Snake-style game; player controls character movement |
| Controls | Swipe or arrow button tap (up/down/left/right) |
| Objective | Recruit prisoners by moving into them; build chain of followers |
| Obstacles | Walls, guards, own prisoner chain (self-collision) |
| Required recruits | Varies; typically 5-10 prisoners |

**Outcomes**:
- **Success**: Riot succeeds; rare chance of escape; Happiness boost
- **Failure (caught by guard)**: Additional years added to sentence
- **Failure (self-collision)**: Riot fails; minor penalty

### 18.3 Burglary (Pac-Man Style)

| Property | Value |
|----------|-------|
| Trigger | Choose "Burglary" from Crime menu |
| Layout | Maze-style house floor plan |
| Player | Character icon; moves in straight lines until hitting a wall |
| Enemies | Homeowner, guard dogs (patrol set paths) |
| Collectibles | Teddy bear, computer, laptop, guitar, diamond, watch, cash piles |
| Controls | Swipe or tap direction |
| Movement | Character slides in chosen direction until hitting a wall (cannot stop mid-slide) |

**Items and Values**:

| Item | Approximate Value |
|------|-------------------|
| Cash pile | $100 - $5,000 (random) |
| Watch | $200 - $2,000 |
| Laptop | $500 - $2,000 |
| Computer | $300 - $1,500 |
| Guitar | $200 - $1,000 |
| Diamond | $1,000 - $10,000 |
| Teddy Bear | $10 - $50 |

**Outcomes**:
- **Escape with loot**: Keep all collected items' value
- **Caught by homeowner**: Reprimanded, assaulted, or turned over to police
- **Caught by police**: Arrested for burglary

### 18.4 Military Deployment (Minesweeper)

| Property | Value |
|----------|-------|
| Trigger | Accept deployment while in military |
| Grid | Standard Minesweeper grid |
| Mines (first deployment) | 3 |
| Mines (subsequent) | Increases up to 10 |
| Mechanic | Standard Minesweeper rules; number reveals indicate adjacent mines |
| Win condition | Flag all mines and clear all safe cells |

**Outcomes**:
- **Success**: Medal awarded; promotion consideration; stat boosts
- **Failure (hit mine)**: Injury (Health loss) or death

### 18.5 Memory Test (Simon Says)

| Property | Value |
|----------|-------|
| Trigger | Mind & Body -> Memory Test |
| Mechanic | Simon Says game; colored panels light up in sequence |
| Input | Tap colored panels in correct order |
| Difficulty | Sequence length increases by 1 each round |
| Smarts reward | +1 to +3 per successful sequence |
| Achievement | "Hyperthymesia" achievement at 20 sequences |

### 18.6 Heirloom Search (Flashlight)

| Property | Value |
|----------|-------|
| Trigger | Daily heirloom search (once per real-world day) |
| Mechanic | Dark attic room; drag flashlight beam to search |
| Objective | Find hidden heirloom by illuminating it |
| Time limit | Limited flashlight battery (time-based) |
| Reward | Heirloom item added to collection with rarity and estimated value |
| Total heirlooms | 182+ unique items |
| Heirloom persistence | Pass down through generations; lost if starting new non-legacy life |

### 18.7 Intelligence Test (IQ Test)

| Property | Value |
|----------|-------|
| Trigger | Occasionally offered as random event |
| Mechanic | Pattern recognition, number sequences, spatial reasoning questions |
| Result | IQ score displayed |
| Effect | Can boost or validate Smarts stat |

---

## 19. Legacy & Generational System

### Death & Continuation

When the player character dies, the following sequence occurs:

```
1. Death notification with cause of death
2. Death summary screen displaying:
   - Name, birth year, death year, age at death
   - Final stats (Happiness, Health, Smarts, Looks)
   - Net worth at death
   - Career history summary
   - Number of children, marriages, criminal record
   - Cause of death
3. Ribbon awarded (see Section 20)
4. Options presented:
   a. Continue as child (if eligible children exist)
   b. Start a new life
   c. View cemetery
```

### Continuing as Child

| Property | Value |
|----------|-------|
| Eligibility | Must have at least one living child (biological, adopted, or step-child) |
| Selection | Player chooses which child to continue as |
| Starting age | The child's current age at the time of parent's death |
| Inheritance | Money and assets inherited based on will distribution minus estate tax |
| Heirlooms | All heirlooms transfer to the continued generation |
| Bitizen limit | Unlimited generations (Bitizen); 2 generations only (free) |

### Will & Testament

| Property | Value |
|----------|-------|
| Access | Available in Activities menu for adult characters |
| Default distribution | Equal split among all children |
| Custom distribution | Can allocate 0-100% to any child |
| Favoritism consequence | Other children's relationships drop when will is changed |
| Strategy | Change will near end of life to avoid long-term relationship damage |

### Estate Tax

| Property | Value |
|----------|-------|
| Application | Country-dependent; applies when inheriting |
| Rate | Varies by country (0% to 40%+) |
| Avoidance | Can gift money/assets to children before death; some countries have no estate tax |
| Effect | Reduces inherited amount |

### Generational Continuity

| What Carries Over | What Resets |
|-------------------|------------|
| Inherited money (minus estate tax) | Career (must find own job) |
| Heirloom collection | Education (at current grade level for age) |
| Family relationships (living relatives) | Relationship meters (may be low) |
| Inherited properties and vehicles | Health, Happiness, Smarts, Looks (child's own stats) |
| Family name / legacy history | Criminal record (child has own clean record) |
| Cemetery of past lives | Fame (starts at 0 unless born into fame) |

---

## 20. Achievements & Ribbons

### Ribbon System

Ribbons are awarded at death based on the dominant theme of the character's life. They appear as decorations on the character's gravestone in the cemetery.

**Total Ribbons**: 40 (including 4 secret ribbons)

**Priority System**: The game evaluates the entire life history and assigns the ribbon that best matches the dominant lifestyle. If no strong match exists, the "Mediocre" ribbon is awarded as default.

### Complete Ribbon List

| Ribbon | Emoji | Requirement Summary |
|--------|-------|---------------------|
| Academic | Graduation cap | Complete highest education possible (graduate/professional school); high Smarts throughout life |
| Addict | Syringe | Die with at least 2 active addictions (alcohol, drugs, gambling) |
| Barbie Girl | Doll | Get 5+ plastic surgeries and maintain 90+ Looks throughout adult life |
| Bandit | Masked face | Escape prison at least once and commit multiple crimes |
| Boring | Sleeping face | Live an unremarkable life with no major achievements, crimes, or events |
| Bubonic | Skull | Die of a plague/rare disease |
| Cat Lady | Cat | Own 5+ cats simultaneously and never marry |
| Cunning | Fox | Successfully commit crimes without ever being caught |
| Deadly | Knife | Murder 5+ people |
| Diva | Crown | Maintain extremely high Looks and fame; demand luxury lifestyle |
| Family Guy / Family Gal | Family | Raise 4+ children with high relationship meters; strong family focus |
| Famous | Star | Achieve maximum fame through celebrity career |
| Fertile | Baby | Have 10+ biological children |
| Generous | Gift | Donate large sums to charity consistently throughout life |
| Geriatric | Elder | Live to age 120 or older |
| Gold Digger | Money bag | Marry wealthy spouses; acquire millions through divorce/death without working |
| Hero | Shield | Save multiple lives through SOS events; military heroism |
| Houdini | Lock | Escape from prison multiple times |
| Influencer | Phone | Gain 1,000,000+ social media followers |
| Jailbird | Prison bars | Spend most of adult life in prison |
| Lazy | Couch | Never work, exercise, or engage in activities; just age up |
| Loaded | Money stack | Accumulate $50,000,000+ net worth |
| Lustful | Heart | Have 20+ sexual partners; high promiscuity |
| Mediocre | Shrug | Default ribbon when no other ribbon criteria strongly met |
| Model Bitizen | Angel | High karma; good deeds; never commit crime; help others |
| Monopoly | Buildings | Own 10+ properties simultaneously |
| Mooch | Open hand | Live off others' money; never hold a job; rely on partners/parents |
| Movie Buff | Film | Watch 100+ movies throughout life |
| Rich | Dollar sign | Accumulate $10,000,000+ net worth |
| Rowdy | Fist | Get into frequent fights and altercations |
| Scandalous | Newspaper | Generate multiple scandals; cheating, public incidents |
| Stupid | Dunce cap | Low Smarts; drop out of school; make consistently bad decisions |
| Successful | Trophy | Reach top of career ladder (CEO, partner, etc.) with high wealth |
| Tarzan | Tree | Own multiple exotic animals |
| Thief | Mask | Commit frequent theft without extensive violence |
| Unlucky | Lightning | Experience multiple misfortunes; accidents, diseases, bad events |
| Veteran | Medal | Complete full military career with honorable discharge |
| Wasteful | Trash | Spend excessively; go from rich to broke |
| (Secret 1-4) | ??? | Hidden until first earned by player |

### Achievements (Separate from Ribbons)

Achievements are tracked separately and persist across lives. They unlock based on specific one-time accomplishments.

| Achievement Example | Requirement |
|--------------------|-------------|
| Hyperthymesia | Score 20 on Memory Test |
| Giggity | Have 100 sexual partners in one life |
| Octogenarian | Live to 80 |
| Centenarian | Live to 100 |
| Ark Builder | Own 10+ pets simultaneously |
| Globetrotter | Emigrate to 5+ countries in one life |
| Lawsuit & Tie | Get sued by an employee |
| Jackpot | Win lottery jackpot |
| Escape Artist | Escape prison 3 times |
| From Rags to Riches | Start life in poverty; accumulate $10M+ |

---

## 21. Monetization & Premium Features

### Free Tier

| Feature | Details |
|---------|---------|
| Core gameplay | Full life simulation with all basic systems |
| Ads | Interstitial ads between lives; rewarded video ads for boosts |
| Generations | Limited to 2 generations |
| Pets | Basic pets only (no exotics, no breeders) |
| Social media sharing | Required for some social media features |
| Time Machine | Not available |

### Bitizenship (One-Time Purchase ~$7.99)

| Feature | Details |
|---------|---------|
| Ad removal | All ads removed |
| Dark mode | Black theme option |
| Unlimited generations | No generation limit |
| Pet access | Full exotic pet dealer, breeders, horse ranch |
| Social media | No sharing requirements |
| Exclusive content | Bitizen-only events and options |
| Custom emoji | Customizable character appearance |

### God Mode (One-Time Purchase ~$8.99)

| Feature | Details |
|---------|---------|
| Character editing | Set all stats (visible and hidden) at birth |
| NPC editing | Edit any NPC's name, stats, and appearance |
| Appearance customization | Eye color, hair, facial hair, brow shape |
| Sexuality selection | Choose orientation at birth |
| Royalty toggle | Born into royal family in eligible countries |
| Re-editing | Can edit stats at any time during life |

### Boss Mode (One-Time Purchase ~$7.99)

| Feature | Details |
|---------|---------|
| Business ownership | Start and manage businesses |
| Employee management | Hire, fire, promote, manage staff |
| Business types | Restaurants, tech companies, retail, etc. |
| Revenue system | Business income added to personal wealth |

### Time Machine ($0.99 or included with Bitizen)

| Feature | Details |
|---------|---------|
| Function | Rewind one year to undo an unwanted outcome |
| Limit | Once per life (per purchase) |
| Use case | Undo accidental death, bad event outcome, etc. |

---

## 22. UI Layout

### Main Screen Layout (Top to Bottom)

```
+---------------------------------------------+
|  [Settings]          [Top Bar]     [God Mode]|
|                                              |
|  [Country Flag] [Character Name, Age]        |
|  [Character Avatar - Emoji Head]             |
|                                              |
|  Happiness  [============================]   |
|  Health     [========================    ]   |
|  Smarts     [==================          ]   |
|  Looks      [======================      ]   |
|  (Fame)     [================            ]   |
|                                              |
|  +---------------------------------------+   |
|  |          Life Event Log               |   |
|  |  (Scrollable text entries)            |   |
|  |                                       |   |
|  |  Age 24: You graduated from           |   |
|  |  university with a degree in...       |   |
|  |                                       |   |
|  |  Age 24: You got a job as a           |   |
|  |  Junior Software Developer...         |   |
|  |                                       |   |
|  |  Age 25: Your father passed away...   |   |
|  |                                       |   |
|  +---------------------------------------+   |
|                                              |
|              [ AGE + ]                       |
|          (Large circular button)             |
|                                              |
| [Relationships] [Occupation] [Assets]        |
|   [Activities]              [Cemetery]       |
+---------------------------------------------+
```

### Bottom Tab Bar

| Tab | Icon | Function |
|-----|------|----------|
| Relationships | People icon | View and interact with all relationships (family, friends, partners) |
| Occupation | Briefcase icon | View current job, apply for jobs, school info |
| Activities | Lightning bolt | Access all activities (Mind & Body, Crime, Nightlife, etc.) |
| Assets | Dollar sign | View owned properties, vehicles, jewelry, bank balance |
| Cemetery | Tombstone | View past lives and their ribbons |

### Modal Event Panel

```
+---------------------------------------------+
|  [Emoji]  Event Title                        |
|  -----------------------------------------  |
|                                              |
|  "Your chemistry teacher caught you          |
|   cheating on a test. She's considering      |
|   reporting you to the principal."           |
|                                              |
|  [Apologize]                                 |
|  [Deny it]                                   |
|  [Beg for mercy]                             |
|  [Insult her]                                |
+---------------------------------------------+
```

### Color Scheme

| Element | Default (Light Mode) | Dark Mode |
|---------|---------------------|-----------|
| Background | White (#FFFFFF) | Black (#000000) |
| Text | Dark gray (#333333) | Light gray (#E0E0E0) |
| Happiness bar | Green (#4CAF50) | Green (#4CAF50) |
| Health bar | Red (#F44336) | Red (#F44336) |
| Smarts bar | Blue (#2196F3) | Blue (#2196F3) |
| Looks bar | Purple (#9C27B0) | Purple (#9C27B0) |
| Fame bar | Gold (#FFD700) | Gold (#FFD700) |
| Age button | Green (#4CAF50) with white text | Green (#4CAF50) with white text |
| Modal background | White with shadow | Dark gray (#222222) |
| Positive option buttons | Green tint | Green tint |
| Negative option buttons | Red tint | Red tint |

### Character Avatar System

Characters are represented by emoji-style 2D vector heads that change based on:

| Factor | Effect on Avatar |
|--------|-----------------|
| Age 0-4 | Baby face |
| Age 5-12 | Child face |
| Age 13-17 | Teen face |
| Age 18-44 | Adult face (customizable with God Mode) |
| Age 45-64 | Middle-aged face (gray hair begins) |
| Age 65+ | Elderly face (wrinkles, white hair) |
| Gender | Male/female features |
| Skin tone | Randomized at birth; inherited from parents |
| Accessories | Glasses, hats (contextual) |
| Prison | Orange jumpsuit overlay |
| Military | Uniform overlay |
| Royalty | Crown overlay |
| Celebrity | Sunglasses overlay |

---

## 23. Audio Design

### Sound Design Philosophy

BitLife uses minimal audio, relying primarily on device haptics and UI sounds rather than continuous music. The audio is supplementary to the text-driven experience.

### Sound Effects

| Event | Sound | Description |
|-------|-------|-------------|
| Age up tap | Soft click/pop | Satisfying confirmation of year progression |
| Stat increase | Rising chime | Brief ascending tone when stat bar fills |
| Stat decrease | Descending tone | Brief falling tone when stat bar drops |
| Positive event | Happy jingle | Short cheerful melody (2-3 notes) |
| Negative event | Somber sting | Low, brief negative tone |
| Modal appearance | Whoosh/slide | Panel sliding in from bottom |
| Option selection | Tap click | Standard button press feedback |
| Death | Somber bell toll | Single low bell or flatline tone |
| Money gained | Cash register / coin sound | Brief monetary jingle |
| Money lost | Reverse coin sound | Descending monetary tone |
| Achievement unlocked | Celebratory fanfare | Short triumphant melody |
| Prison escape success | Triumphant chord | Brief victory sting |
| Prison escape failure | Buzzer / alarm | Failure indication |
| Mini-game start | Game start jingle | Brief energetic intro |
| Ribbon awarded | Soft, reflective melody | End-of-life ribbon reveal |

### Haptic Feedback (Mobile)

| Event | Haptic Type |
|-------|-------------|
| Age up | Light tap |
| Major life event | Medium impact |
| Death | Heavy impact |
| Positive outcome | Success pattern |
| Negative outcome | Error pattern |
| Button press | Soft tap |

### Background Music

| Context | Music Style | Notes |
|---------|-------------|-------|
| Main menu | Calm, ambient | Low-key lo-fi or ambient pad |
| Gameplay (normal) | None or very subtle ambient | Most gameplay has no music; text-focused |
| Mini-games | Upbeat, arcade-style | Increases tension; tempo matches difficulty |
| Death screen | Somber, reflective | Piano or strings; brief |
| Cemetery | Quiet, respectful | Ambient wind or quiet melody |

### Audio Settings

| Setting | Options |
|---------|---------|
| Sound effects | On / Off |
| Music | On / Off |
| Haptics | On / Off |
| Volume | Slider (0-100%) |

---

## Appendix A: Country List (Partial)

The following countries are available at launch and through updates:

**Original 37 Countries**: Argentina, Australia, Brazil, Canada, Chile, China, Colombia, Cuba, Egypt, Ethiopia, France, Germany, Greece, India, Iran, Ireland, Israel, Italy, Jamaica, Japan, Mexico, Netherlands, New Zealand, Nigeria, Panama, Peru, Philippines, Russia, Saudi Arabia, Serbia, South Africa, South Korea, Spain, Sweden, Turkey, United Kingdom, United States, Venezuela.

**Wave 2 (March 2019)**: Denmark, Estonia, Finland, Indonesia, Norway, Portugal, Romania, Singapore.

**Wave 3+ (2020-2022)**: Andorra, Angola, Aruba, Belize, El Salvador, Guatemala, Guyana, Haiti, Nicaragua, Papua New Guinea, Paraguay, Samoa, Tunisia, Uganda, and additional territories.

**Total**: 100+ playable nations/territories.

---

## Appendix B: Addiction System

### Addiction Types

| Addiction | Trigger | Cure | Withdrawal Effects |
|-----------|---------|------|--------------------|
| Alcohol | Repeated nightlife/drinking | Rehab, willpower, time | Happiness -5 to -15/year |
| Hard Drugs | Accepting drugs, repeated use | Rehab, willpower, time | Health -5 to -20/year; overdose risk |
| Gambling | Repeated casino/horse racing | Rehab, willpower, time | Financial ruin risk |
| Prescription drugs | Overuse of prescribed medication | Rehab, willpower | Health -3 to -10/year |

### Addiction Mechanics

| Property | Value |
|----------|-------|
| Onset | Random chance per exposure; modified by Discipline and Willpower |
| Severity levels | Mild, Moderate, Severe |
| Treatment | Rehab facility ($5,000 - $30,000); success depends on Willpower |
| Relapse | Possible after treatment; higher Willpower reduces risk |
| Stat effects | Ongoing health, happiness, and financial penalties while addicted |
| Death risk | Severe addiction + continued use = overdose possibility |

---

## Appendix C: Heirloom System

### Heirloom Properties

| Property | Value |
|----------|-------|
| Total unique heirlooms | 182+ |
| Discovery method | Daily flashlight attic mini-game |
| Rarity tiers | Common, Uncommon, Rare, Very Rare, Legendary |
| Value range | $10 - $10,000,000+ |
| Actions | Discard, Donate, Play (if instrument), Refurbish, Sell |
| Generation transfer | Automatically passed to next generation character |
| Special effects | Some heirlooms grant bonuses (e.g., Lucky Dice improves gambling odds) |
| Collection persistence | Only within generational play; lost on new non-legacy life |

### Heirloom Categories

| Category | Examples |
|----------|----------|
| Musical Instruments | Antique piano, vintage guitar, rare violin |
| Jewelry | Family ring, antique brooch, vintage watch |
| Art | Paintings, sculptures, rare books |
| Toys | Antique dolls, vintage board games, rare figurines |
| Technology | Vintage computer, antique radio, early phone |
| Miscellaneous | Lucky dice, crystal ball, family Bible, war medals |

---

## Appendix D: Key Numeric Constants

| Constant | Value |
|----------|-------|
| Maximum age (theoretical) | 122 years |
| Maximum stat value | 100 |
| Minimum stat value | 0 |
| Starting cash | $0 (unless born wealthy) |
| Maximum number of children | No hard limit |
| Maximum properties owned | No hard limit |
| Relationship decay per year (no contact) | -3 to -8 |
| Positive interaction boost | +2 to +15 |
| School graduation GPA for scholarships | 3.5+ |
| University tuition (US, approximate) | $40,000 - $200,000 total |
| Medical school tuition (US) | $100,000 - $300,000 total |
| Prenup effectiveness | Protects pre-marriage assets only |
| Estate tax range | 0% - 40% (country-dependent) |
| Social media verification threshold | 100,000 followers + 25 fame |
| Fame threshold for "Famous" status | 25+ on 0-100 scale |
| Prison escape guard speed | 2 moves per 1 player move |
| Minesweeper first deployment mines | 3 |
| Minesweeper max deployment mines | 10 |
| Horse racing payout | 5x bet |
| Blackjack payout | 2x bet |
| Time Machine uses per life | 1 |
| Maximum generations (free) | 2 |
| Maximum generations (Bitizen) | Unlimited |
