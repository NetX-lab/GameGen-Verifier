# Metal Slug — Complete Game Specification

> A comprehensive specification for faithfully recreating Metal Slug (SNK, 1996 Neo Geo). This document covers every system, mechanic, entity, and interaction required for a full clone of the original arcade run-and-gun action game.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Player Character Mechanics](#3-player-character-mechanics)
4. [Weapon System](#4-weapon-system)
5. [Metal Slug Vehicle](#5-metal-slug-vehicle)
6. [Enemy System](#6-enemy-system)
7. [Boss Encounters](#7-boss-encounters)
8. [Level Design — All 6 Missions](#8-level-design--all-6-missions)
9. [Item & Pickup System](#9-item--pickup-system)
10. [POW (Prisoner of War) System](#10-pow-prisoner-of-war-system)
11. [Scoring System](#11-scoring-system)
12. [UI Layout & HUD](#12-ui-layout--hud)
13. [Audio Design](#13-audio-design)
14. [Animation System](#14-animation-system)
15. [Continue & Lives System](#15-continue--lives-system)

---

## 1. Game Overview

- **Genre**: Run-and-gun / side-scrolling shooter
- **Perspective**: 2D side-scrolling
- **Players**: 1-2 players (Marco Rossi, Tarma Roving)
- **Input**: 8-way joystick + 3 buttons (Shoot, Jump, Grenade)
- **Objective**: Progress through 6 missions, defeat all enemies and bosses, rescue POWs, and liberate the world from General Morden's rebel army.
- **Lose Condition**: Losing all lives. Continue system available (arcade credits).

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 320 x 224 pixels (Neo Geo) |
| Recommended implementation | 640 x 448 or 1280 x 896 |
| Orientation | Landscape |
| Frame rate | 60 FPS |
| Tile size | 16 x 16 pixels |
| Sprite colors | Up to 16 colors per sprite, 4096 total palette |

### Coordinate System

- Origin (0, 0) at top-left.
- Scrolling is primarily left-to-right.
- Some sections scroll vertically or in both directions.
- Camera follows the player(s), with slight lead in movement direction.

### Game Loop

```
1. Process input (joystick direction, button presses)
2. Update player state (movement, jumping, shooting, crouching)
3. Update all enemy AI and movement
4. Update all projectiles (player and enemy)
5. Update vehicle state (if active)
6. Check collisions (projectiles vs entities, player vs enemies, player vs items)
7. Update explosions and particle effects
8. Check POW rescue triggers
9. Update camera/scroll position
10. Check checkpoint and boss triggers
11. Update score display
12. Render (background layers → enemies → player → projectiles → effects → UI)
```

### Scrolling System

| Property | Value |
|----------|-------|
| Horizontal scroll | Player-driven, cannot backtrack past left edge |
| Vertical scroll | Section-dependent (some areas scroll up/down) |
| Camera dead zone | Player can move within center 40% of screen before scrolling triggers |
| Scroll speed | Matches player walk speed (max ~120 pixels/second) |
| Forced scroll sections | Some areas auto-scroll at fixed speed |

---

## 3. Player Character Mechanics

### Characters

| Character | Player | Visual Difference | Gameplay Difference |
|-----------|--------|-------------------|-------------------|
| Marco Rossi | Player 1 | Brown hair, bandana | None (identical gameplay) |
| Tarma Roving | Player 2 | Blonde hair, cap | None (identical gameplay) |

### Movement

| Action | Speed (pixels/second) | Input |
|--------|----------------------|-------|
| Walk right | 120 | Joystick right |
| Walk left | 120 | Joystick left |
| Crouch walk | 80 | Joystick down-left/down-right |
| Jump | Vertical: 280 initial, gravity 600 px/s^2 | Jump button |
| Jump height | ~130 pixels maximum | — |
| Jump horizontal | Maintains ground speed during jump | — |
| Drop down (platforms) | Pass through thin platforms | Joystick down + Jump on thin platform |
| Climb ladder | 80 (vertical) | Joystick up/down on ladder |

### Player States

| State | Description | Hitbox (W x H) |
|-------|-------------|----------------|
| Standing | Upright, idle or walking | 16 x 32 |
| Crouching | Ducking, reduced hitbox | 16 x 16 |
| Jumping | Airborne | 16 x 32 |
| Shooting (stand) | Standing, firing weapon | 16 x 32 |
| Shooting (crouch) | Crouching, firing weapon | 16 x 16 |
| Shooting (up) | Standing, aiming upward | 16 x 32 |
| Shooting (diagonal up) | Standing, aiming 45 degrees up | 16 x 32 |
| In vehicle | Inside Metal Slug tank | Vehicle hitbox |
| Melee (knife) | Close-range knife slash | 16 x 32, attack range: 24px forward |
| Death | Hit animation, respawn | Invincible during respawn |
| Fat | After eating too much food; larger hitbox, different animations | 24 x 32 |

### Melee Attack (Knife)

| Property | Value |
|----------|-------|
| Damage | 1-hit kill on most infantry |
| Range | 24 pixels forward |
| Speed | ~0.2 second swing |
| Activation | Shoot button when enemy is within melee range |
| Auto-trigger | Yes (when close enough, shoot button does knife instead of gun) |

### Fat Marco/Tarma

| Property | Value |
|----------|-------|
| Trigger | Eating too many food items in sequence (varies by section) |
| Hitbox | 24 x 32 (wider than normal) |
| Movement speed | 100 pixels/second (slower) |
| Jump height | ~100 pixels (lower) |
| Weapon | Cannonball (replaces pistol), same special weapons |
| Grenade | Same as normal |
| Revert | After death or after ~30 seconds |

### Invincibility Frames

| Trigger | Duration |
|---------|----------|
| After respawn | 3.0 seconds |
| After vehicle exit | 1.0 seconds |
| After being hit (vehicle) | 0.5 seconds of vehicle invincibility |

---

## 4. Weapon System

### Default Weapon: Pistol

| Property | Value |
|----------|-------|
| Damage | 1 per shot |
| Fire rate | ~10 shots/second (rapid press) / auto-fire: 7 shots/second (hold) |
| Projectile speed | 400 pixels/second |
| Ammo | Unlimited |
| Projectile size | 4 x 4 pixels |
| Range | Full screen width |

### Special Weapons (Ammo-Limited)

All special weapons revert to pistol when ammo is depleted.

#### Heavy Machine Gun (H)

| Property | Value |
|----------|-------|
| Damage | 2 per shot |
| Fire rate | 12 shots/second |
| Projectile speed | 500 pixels/second |
| Starting ammo | 200 |
| Projectile size | 6 x 4 pixels |
| Visual | Larger, orange bullet |
| Letter indicator | "H" |

#### Rocket Launcher (R)

| Property | Value |
|----------|-------|
| Damage | 10 per rocket |
| Fire rate | 3 rockets/second |
| Projectile speed | 350 pixels/second |
| Starting ammo | 30 |
| Projectile size | 12 x 6 pixels |
| Splash damage | 20 pixel radius |
| Visual | Rocket with exhaust trail |
| Letter indicator | "R" |

#### Shotgun (S)

| Property | Value |
|----------|-------|
| Damage | 3 per pellet, 6 pellets per shot |
| Fire rate | 3 shots/second |
| Spread | 15 degree cone |
| Range | ~160 pixels (pellets disappear after range) |
| Starting ammo | 30 |
| Visual | Spread of small pellets |
| Letter indicator | "S" |

#### Flame Shot (F)

| Property | Value |
|----------|-------|
| Damage | 4 per hit (multi-hit, ~2 hits per enemy) |
| Fire rate | 5 shots/second |
| Projectile speed | 300 pixels/second |
| Range | ~120 pixels |
| Starting ammo | 30 |
| Visual | Flame projectile that lingers |
| Penetration | Hits multiple enemies in line |
| Letter indicator | "F" |

### Grenades

| Property | Value |
|----------|-------|
| Default grenades | 10 per life |
| Damage | 20 (direct hit) |
| Splash radius | 32 pixels |
| Throw arc | Parabolic, ~45 degree angle |
| Throw distance | ~120 pixels forward, ~80 pixels up |
| Fuse time | 1.5 seconds after landing (or instant on enemy contact) |
| Visual | Small grey grenade, bounces once |

### Grenade Types (in Vehicle)

| Property | Value |
|----------|-------|
| Vehicle grenade | Cannon shell (arcing) |
| Damage | 30 |
| Splash radius | 40 pixels |
| Fire rate | 2 per second |
| Ammo | Unlimited (vehicle cannon) |

---

## 5. Metal Slug Vehicle

### SV-001 Metal Slug Tank

| Property | Value |
|----------|-------|
| HP | 3 hits (flashes red at 1 HP remaining) |
| Movement speed | 100 pixels/second |
| Jump height | ~80 pixels (small hop) |
| Hitbox | 48 x 40 pixels |
| Crouch | Tank lowers turret, reduced hitbox: 48 x 28 |

### Vehicle Weapons

| Weapon | Damage | Fire Rate | Ammo | Notes |
|--------|--------|-----------|------|-------|
| Vulcan cannon (main) | 2 per shot | 10/second | Unlimited | Replaces player's pistol |
| Cannon (grenade button) | 30 per shell | 2/second | Unlimited | Arcing explosive shell |

### Vehicle Mechanics

- **Entry**: Walk up to empty Slug and press Up.
- **Exit**: Press Jump while inside (Barry jumps out upward).
- **Forced exit**: At 0 HP, vehicle flashes rapidly for 3 seconds. Player must exit or be caught in explosion. Explosion damages nearby enemies (40 damage, 64 pixel radius).
- **Self-destruct**: Can jump out at any HP. Vehicle continues for 1 second then explodes.
- **Rescue from above**: Some levels drop the Slug from a helicopter.

### Vehicle Damage States

| HP | Visual State |
|----|-------------|
| 3 (full) | Normal appearance |
| 2 | Minor smoke from engine |
| 1 | Heavy smoke, red flashing, sparks |
| 0 | Rapid flashing, 3-second self-destruct countdown |

---

## 6. Enemy System

### 6.1 Infantry

#### Rebel Soldier (Basic)

| Property | Value |
|----------|-------|
| HP | 1 (dies to any hit) |
| Damage to player | 1 (contact or bullet) |
| Speed | 80 pixels/second |
| Behavior | Walks toward player, shoots pistol, throws grenades |
| Fire rate | 1 shot every 2 seconds |
| Grenade frequency | Occasional (every 5 seconds) |
| Score | 100 |

#### Rebel Soldier (Shielded)

| Property | Value |
|----------|-------|
| HP | 1 (shield blocks frontal shots until removed) |
| Shield HP | 5 frontal hits |
| Behavior | Advances with shield, attacks when close |
| Counter | Attack from behind, grenades, or use enough firepower |
| Score | 300 |

#### Rebel Bazooka Soldier

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 per rocket |
| Rocket speed | 200 pixels/second |
| Behavior | Stands in place, fires rockets at player |
| Fire rate | 1 rocket every 3 seconds |
| Score | 200 |

#### Rebel Grenade Soldier

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 per grenade (splash) |
| Behavior | Throws grenades in an arc toward player |
| Grenade interval | Every 4 seconds |
| Score | 200 |

#### Rebel Knife Soldier

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 (melee) |
| Speed | 140 pixels/second (fast runner) |
| Behavior | Runs at player with knife, lunges when close |
| Score | 100 |

### 6.2 Vehicles & Heavy Units

#### Rebel Tank (Di-Cokka)

| Property | Value |
|----------|-------|
| HP | 20 |
| Main cannon damage | 1 per shell |
| Fire rate | 1 shell every 3 seconds |
| Speed | 40 pixels/second |
| Hitbox | 48 x 32 pixels |
| Score | 1,000 |
| Drops | Often drops weapon crate when destroyed |

#### Rebel Helicopter

| Property | Value |
|----------|-------|
| HP | 15 |
| Damage | 1 per bomb or bullet |
| Behavior | Flies overhead, drops bombs or fires downward |
| Speed | 80 pixels/second |
| Bomb drop interval | Every 4 seconds |
| Score | 800 |

#### Rebel Jeep (M-15A Bradley)

| Property | Value |
|----------|-------|
| HP | 10 |
| Damage | 1 (machine gun) |
| Speed | 120 pixels/second |
| Behavior | Drives toward player, fires mounted gun |
| Score | 600 |

#### Mortar Emplacement

| Property | Value |
|----------|-------|
| HP | 8 |
| Damage | 1 per shell |
| Behavior | Stationary, lobs mortars in an arc |
| Fire rate | 1 every 3 seconds |
| Score | 500 |

### 6.3 Specialized Enemies

#### Sniper

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 |
| Behavior | Hides in background, fires precise shots |
| Warning | Scope glint visible before shot |
| Score | 300 |

#### Kamikaze Soldier

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 1 (explosion on death near player) |
| Speed | 160 pixels/second |
| Behavior | Runs at player with lit dynamite, explodes on contact or death |
| Explosion radius | 24 pixels |
| Score | 200 |

#### Submarine (Boss Minion)

| Property | Value |
|----------|-------|
| HP | 10 |
| Damage | 1 per torpedo |
| Behavior | Surfaces, fires torpedo, submerges |
| Score | 500 |

---

## 7. Boss Encounters

### Mission 1 Boss: Tetsuyuki (Giant Bomber Aircraft)

| Property | Value |
|----------|-------|
| HP | 200 |
| Phase 1 attacks | Drops bombs in patterns (3-bomb clusters) |
| Phase 2 attacks (50% HP) | Fires spread of bullets downward, increases bomb frequency |
| Movement | Flies left-right above the player |
| Weak point | Main fuselage (any part takes damage) |
| Score | 10,000 |

### Mission 2 Boss: Hairbuster Riberts (Attack Helicopter)

| Property | Value |
|----------|-------|
| HP | 250 |
| Phase 1 | Fires missiles in 3-round bursts |
| Phase 2 (50% HP) | Deploys mines, fires machine gun |
| Movement | Hovers and repositions, swoops |
| Score | 10,000 |

### Mission 3 Boss: Tani Oh (Armored Fortress Wall)

| Property | Value |
|----------|-------|
| HP | 300 |
| Attacks | Multiple gun turrets, drops soldiers, fires large cannon |
| Turrets | 4 turrets, each with 30 HP, can be destroyed independently |
| Movement | Stationary (scrolling screen pushes player toward it) |
| Score | 15,000 |

### Mission 4 Boss: Shoe & Karn (Twin Tanks)

| Property | Value |
|----------|-------|
| HP | 200 each (total 400) |
| Attacks | Coordinated fire, ram attacks |
| Movement | Two tanks approach from left and right |
| Special | When one is destroyed, the other becomes more aggressive |
| Score | 10,000 each |

### Mission 5 Boss: Iron Nokana (Armored Train Car)

| Property | Value |
|----------|-------|
| HP | 350 |
| Attacks | Side cannons, top turret, troop deployment |
| Movement | Moves along train tracks |
| Phases | 3 phases with increasing weapon activation |
| Score | 15,000 |

### Mission 6 Final Boss: Morden's Flagship + Alien Boss

| Phase 1: Morden's Helicopter |
|------|
| HP: 200 |
| Attacks: Machine guns, missiles |

| Phase 2: Alien Mothership (Rootmars) |
|------|
| HP: 500 |
| Attacks: Energy beams, spawns alien infantry, grabbing tentacles |
| Movement: Hovers above, swoops down |
| Score: 50,000 |

---

## 8. Level Design — All 6 Missions

### Mission 1: "The Coup d'Etat"

| Property | Value |
|----------|-------|
| Setting | City streets, harbor |
| Length | ~3200 pixels (20 screen widths) |
| Sections | 3 (city → harbor → boss area) |
| POWs | 10 |
| Vehicles | 1 Metal Slug (mid-mission) |
| New enemies | Rebel soldiers, tanks, helicopters |
| Boss | Tetsuyuki |
| Difficulty | Easy |

### Mission 2: "Underground Prison"

| Property | Value |
|----------|-------|
| Setting | Military base, underground bunker |
| Length | ~3500 pixels |
| Sections | 3 (exterior → interior → boss area) |
| POWs | 10 |
| Vehicles | 1 Metal Slug |
| New enemies | Shielded soldiers, mortar emplacements |
| Boss | Hairbuster Riberts |
| Difficulty | Easy-Medium |

### Mission 3: "The Valley of the Skulls"

| Property | Value |
|----------|-------|
| Setting | Mountain pass, fortress |
| Length | ~4000 pixels |
| Sections | 4 (mountain path → bridge → fortress exterior → boss) |
| POWs | 10 |
| Vehicles | 1 Metal Slug (bridge section) |
| New enemies | Snipers, kamikaze soldiers |
| Boss | Tani Oh |
| Difficulty | Medium |
| Special | Vertical scrolling section (climbing the fortress) |

### Mission 4: "Morden's Desert"

| Property | Value |
|----------|-------|
| Setting | Desert, oasis, military camp |
| Length | ~4000 pixels |
| Sections | 3 (desert → camp → boss area) |
| POWs | 10 |
| Vehicles | 2 Metal Slugs (one in desert, one before boss) |
| New enemies | Jeeps, bazooka soldiers |
| Boss | Shoe & Karn (twin tanks) |
| Difficulty | Medium-Hard |

### Mission 5: "The Waterfront"

| Property | Value |
|----------|-------|
| Setting | Docks, train yard, warehouse |
| Length | ~4500 pixels |
| Sections | 4 (docks → train → warehouse → boss) |
| POWs | 10 |
| Vehicles | 1 Metal Slug |
| New enemies | Submarines, heavy infantry |
| Boss | Iron Nokana |
| Difficulty | Hard |
| Special | Moving train section (auto-scrolling) |

### Mission 6: "The Final Assault"

| Property | Value |
|----------|-------|
| Setting | Morden's island fortress, alien invasion |
| Length | ~5000 pixels |
| Sections | 4 (beach → fortress → alien landing → final boss) |
| POWs | 10 |
| Vehicles | 2 Metal Slugs |
| New enemies | Alien infantry (Mars People) |
| Boss | Morden's Helicopter → Rootmars (alien) |
| Difficulty | Very Hard |
| Special | Aliens invade mid-mission; temporary alliance with rebel forces |

---

## 9. Item & Pickup System

### Weapon Pickups

| Item | Appearance | Effect |
|------|-----------|--------|
| Heavy Machine Gun (H) | Crate with "H" | Grants HMG with 200 ammo |
| Rocket Launcher (R) | Crate with "R" | Grants RL with 30 ammo |
| Shotgun (S) | Crate with "S" | Grants Shotgun with 30 ammo |
| Flame Shot (F) | Crate with "F" | Grants Flameshot with 30 ammo |
| Grenade Box | Crate with grenade icon | +10 grenades |

### Food Items (Score + Fat Mechanic)

| Item | Score Value | Found In |
|------|-----------|----------|
| Bread | 100 | POW rescue drops |
| Apple | 100 | Destructible crates |
| Banana | 100 | Destructible crates |
| Steak | 500 | POW rescue drops |
| Roast Turkey | 1,000 | Rare, POW rescue |
| Watermelon | 200 | Destructible objects |
| Rice | 100 | Specific levels |

### Score Items (From POW Rescue)

| Item | Score Value | Rarity |
|------|-----------|--------|
| Medal | 500 | Common |
| Coin | 1,000 | Uncommon |
| Gem | 2,000 | Rare |
| Gold Bar | 5,000 | Very Rare |
| Diamond | 10,000 | Ultra Rare |
| Teddy Bear | 50,000 | Legendary (specific POWs) |

---

## 10. POW (Prisoner of War) System

### POW Properties

| Property | Value |
|----------|-------|
| Appearance | Tied-up soldiers in white/grey |
| Total per mission | 10 |
| Rescue method | Walk up to them and touch/slash the ropes |
| Animation | POW salutes, runs off-screen |
| Drop | Each POW drops an item (weapon, food, or score item) |
| Score per rescue | 500 (first POW), increasing for consecutive rescues |

### Consecutive Rescue Bonus

| POW # in Sequence | Score Per Rescue |
|-------------------|-----------------|
| 1 | 500 |
| 2 | 1,000 |
| 3 | 1,500 |
| 4 | 2,000 |
| 5 | 2,500 |
| 6 | 5,000 |
| 7 | 5,000 |
| 8 | 10,000 |
| 9 | 10,000 |
| 10 | 50,000 (all POWs in mission) |

### POW Placement

- POWs are placed in both obvious and hidden locations.
- Some POWs are hidden behind destructible objects.
- Some POWs are in dangerous locations requiring skillful play to reach.
- All 10 POWs in a mission must be rescued in a single credit for the full bonus.

---

## 11. Scoring System

### Score Sources

| Source | Points |
|--------|--------|
| Basic infantry kill | 100 |
| Shielded infantry kill | 300 |
| Bazooka soldier kill | 200 |
| Vehicle destruction | 500-1,000 |
| Boss kill | 10,000-50,000 |
| POW rescue | 500-50,000 (see table) |
| Food item | 100-1,000 |
| Score item | 500-50,000 |
| Melee kill (knife) | 500 (5x normal infantry score) |
| End-of-mission bonus | Varies |

### Melee Kill Bonus

- Killing enemies with the knife (melee) awards **5x the normal kill score**.
- Basic soldier: 500 instead of 100.
- Encourages risky close-range play.

### End-of-Mission Bonuses

| Bonus | Condition | Points |
|-------|-----------|--------|
| POW bonus | Each rescued POW | Varies (see table) |
| All POW bonus | All 10 rescued | 100,000 extra |
| No miss bonus | No deaths in mission | 50,000 |
| Vehicle bonus | Finish mission in Slug | 10,000 |

---

## 12. UI Layout & HUD

### 12.1 In-Game HUD

```
┌──────────────────────────────────────────────────────┐
│ P1 SCORE: 125,400    [WEAPON: H-128]   CREDITS: 3   │
│ LIFE: ♦♦♦           [BOMB: 08]        TIME: --      │
├──────────────────────────────────────────────────────┤
│                                                       │
│                                                       │
│     [Game playfield - scrolling level area]           │
│                                                       │
│                                                       │
│                                                       │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### HUD Elements

| Element | Position | Description |
|---------|----------|-------------|
| Score | Top-left | Current score, 7 digits |
| Lives | Top-left (below score) | Remaining lives as icons |
| Weapon indicator | Top-center | Current weapon letter + ammo count |
| Grenade count | Top-center (below weapon) | "BOMB: XX" |
| Credits | Top-right | Remaining continues |
| Timer | Top-right (some modes) | Time attack modes only |

### 12.2 Title Screen

```
┌──────────────────────────────────────────────────────┐
│                                                       │
│              M E T A L   S L U G                     │
│              [Logo with bullet holes]                │
│                                                       │
│              1 PLAYER                                │
│              2 PLAYERS                               │
│                                                       │
│              INSERT COIN                              │
│                                                       │
│  (C) 1996 SNK                                        │
└──────────────────────────────────────────────────────┘
```

### 12.3 Mission Start Screen

```
┌──────────────────────────────────────────────────────┐
│                                                       │
│                 MISSION 1                             │
│                                                       │
│         " T H E   C O U P   D ' E T A T "           │
│                                                       │
│              [Mission briefing map]                   │
│                                                       │
│                                                       │
│              GET READY!                               │
└──────────────────────────────────────────────────────┘
```

---

## 13. Audio Design

### 13.1 Music

| Track | Mission/Context | Style |
|-------|----------------|-------|
| "Assault Theme" | Mission 1 | Military march, driving tempo |
| "Back to the China" | Mission 2 | Tense, underground infiltration |
| "Judgment" | Mission 3 | Intense, climbing action |
| "Desert" | Mission 4 | Middle-Eastern influenced, hot |
| "Main Theme from MS" | Mission 5 | Heroic, fast-paced |
| "Final Attack" | Mission 6 | Epic, climactic, urgent |
| "Steel Beast" | Boss battles | Heavy metal, aggressive |
| "Hold You Still!" | Victory/results | Triumphant military fanfare |
| "The Military System" | Title screen | Militaristic, proud |

### 13.2 Sound Effects

| Event | Sound Description |
|-------|-------------------|
| Pistol shot | Sharp "pew" |
| HMG shot | Rapid "rata-tat-tat" |
| Rocket fire | "Whoosh" with trail |
| Rocket explosion | Deep "boom" |
| Shotgun blast | "Ka-CHAK" with spread |
| Grenade throw | "Click" (pin pull) + "whomp" (explosion) |
| Grenade explosion | "BOOM" with debris |
| Metal Slug cannon | Heavy "THOOM" |
| Knife slash | Sharp "schwing" |
| Enemy death (infantry) | "AAAGH!" (death scream, multiple variations) |
| Enemy death (vehicle) | Metal crunch + explosion |
| Player death | "AAAH!" + brief music sting |
| Item pickup | Cheerful "bling" |
| Weapon pickup | Announcer: "HEAVY MACHINE GUN!" / "ROCKET LAUNCHER!" etc. |
| POW rescue | POW says "THANK YOU!" |
| Vehicle enter | Hatch clank + engine rev |
| Vehicle damage | Metal crunch |
| Vehicle explode | Large explosion + debris |
| Coin collect | "Cha-ching" |
| Boss warning | Alarm siren |
| Mission start | Announcer: "MISSION [X], START!" |
| Mission clear | Announcer: "MISSION COMPLETE!" |

### 13.3 Voice Lines (Announcer)

| Trigger | Line |
|---------|------|
| Weapon pickup | "HEAVY MACHINE GUN!" / "ROCKET LAUNCHA!" / "SHOTGUN!" / "FLAME SHOT!" |
| Mission start | "MISSION [number] START!" |
| Mission clear | "MISSION COMPLETE!" |
| Game Over | "Oh no!" (brief) |
| Continue | "Come on! Let's go!" |
| All POWs rescued | (Triumphant fanfare) |

---

## 14. Animation System

### 14.1 Player Animations

| Animation | Frames | FPS | Description |
|-----------|--------|-----|-------------|
| Idle (stand) | 4 | 6 | Slight breathing/sway |
| Walk | 12 | 12 | Full walk cycle |
| Run (same as walk) | 12 | 15 | Slightly faster cycle |
| Crouch (idle) | 2 | 4 | Ducking position |
| Crouch walk | 8 | 10 | Low shuffling |
| Jump (ascend) | 3 | 8 | Legs tuck, arms up |
| Jump (descend) | 3 | 8 | Legs extend |
| Land | 2 | 12 | Impact squash |
| Shoot (stand) | 3 | 15 | Gun recoil |
| Shoot (crouch) | 3 | 15 | Crouch gun recoil |
| Shoot (up) | 3 | 15 | Aim up, fire |
| Knife slash | 4 | 20 | Quick forward swipe |
| Grenade throw | 5 | 12 | Windup and throw |
| Death | 8 | 8 | Knocked back, fall |
| Respawn | 4 | 8 | Parachute drop in |
| Enter vehicle | 4 | 10 | Jump into hatch |
| Exit vehicle | 3 | 10 | Jump out upward |
| Fat idle | 4 | 6 | Larger frame, panting |
| Fat walk | 12 | 10 | Waddling gait |

### 14.2 Enemy Animations

| Enemy | States | Description |
|-------|--------|-------------|
| Rebel soldier | Walk(8), Shoot(3), Grenade(4), Death(6), Idle(4) | Standard infantry |
| Shield soldier | Walk(8), Guard(2), Attack(4), Death(6) | Shield up/down states |
| Tank | Move(4), Fire(3), Explode(8) | Treads rolling animation |
| Helicopter | Fly(4), Fire(3), Explode(10) | Rotor spinning |

### 14.3 Explosion Effects

| Type | Frames | Size | Duration |
|------|--------|------|----------|
| Small explosion (infantry) | 6 | 24x24 px | 0.4 seconds |
| Medium explosion (vehicle) | 8 | 48x48 px | 0.5 seconds |
| Large explosion (boss) | 12 | 96x96 px | 0.8 seconds |
| Massive explosion (final boss) | 16 | 128x128 px | 1.2 seconds |

### 14.4 Environmental Animation

- Water ripples (looping 4-frame animation).
- Fire/torch flickering (6-frame loop).
- Background machinery movement (gears, conveyor belts).
- Falling debris from explosions.
- Smoke from damaged vehicles (continuous particle emitter).

---

## 15. Continue & Lives System

### Lives

| Property | Value |
|----------|-------|
| Starting lives | 3 per credit |
| Maximum lives | 9 |
| Extra life | At 500,000 points and 1,500,000 points |
| Respawn | Parachute drop at death location |
| Respawn invincibility | 3.0 seconds |

### Continue System

| Property | Value |
|----------|-------|
| Starting credits | 3 (arcade; can be set in options) |
| Continue countdown | 10 seconds to insert credit |
| On continue | Lives reset to 3, score preserved, restart at last checkpoint |
| Game Over | When all credits exhausted |

### Checkpoints

- Each mission has 2-3 checkpoints (invisible triggers at specific scroll positions).
- Dying respawns the player at the last passed checkpoint.
- Continuing respawns at the same checkpoint.
- Boss areas have a checkpoint at the boss trigger point.

---

## Appendix A: Quick Reference — Player Stats

| Stat | On Foot | In Vehicle | Fat |
|------|---------|-----------|-----|
| Walk speed | 120 px/s | 100 px/s | 100 px/s |
| Jump height | 130 px | 80 px | 100 px |
| Hitbox | 16x32 | 48x40 | 24x32 |
| Default weapon | Pistol (unlimited) | Vulcan (unlimited) | Cannonball (unlimited) |
| Grenade | Yes (10) | Cannon shell (unlimited) | Yes (10) |
| HP | 1 hit = death | 3 hits | 1 hit = death |

## Appendix B: Quick Reference — Weapon Comparison

| Weapon | DPS | Ammo | Best Use |
|--------|-----|------|----------|
| Pistol | ~20/s | Infinite | Fallback |
| HMG | ~24/s | 200 | General purpose |
| Rocket | ~30/s | 30 | Vehicles, groups |
| Shotgun | ~54/s (close) | 30 | Close range clusters |
| Flame | ~40/s | 30 | Crowds, penetration |
| Knife | Instant kill | Infinite | Infantry (5x score) |

## Appendix C: Quick Reference — Enemy HP Tiers

| Tier | HP | Enemies |
|------|-----|---------|
| One-shot | 1 | All infantry types |
| Light vehicle | 8-10 | Jeeps, mortars |
| Medium vehicle | 10-15 | Helicopters |
| Heavy vehicle | 15-20 | Tanks |
| Boss | 200-500 | All bosses |

---

*This specification is based on Metal Slug (1996) by SNK for the Neo Geo arcade platform. Values are sourced from gameplay analysis, arcade data, and community documentation. Minor variations may exist between arcade and console ports.*
