# Half-Life (1998) -- Complete Game Specification

## 1. Game Overview

- **Title**: Half-Life
- **Developer**: Valve Software
- **Publisher**: Sierra Studios
- **Release Date**: November 19, 1998
- **Platform**: PC (Windows)
- **Engine**: GoldSrc (heavily modified Quake engine)
- **Genre**: First-Person Shooter / Action-Adventure
- **Perspective**: First-person, fully diegetic (no cutscenes; the player never leaves Gordon Freeman's viewpoint)
- **Protagonist**: Dr. Gordon Freeman, a 27-year-old theoretical physicist with a Ph.D. from MIT, employed at the Black Mesa Research Facility in New Mexico
- **Premise**: A routine experiment in the Anomalous Materials lab triggers a "Resonance Cascade," ripping open a dimensional rift to the alien borderworld Xen. Aliens flood Black Mesa, the U.S. military is sent to silence all witnesses, and Freeman must fight through the facility, travel to Xen, and destroy the alien leader -- the Nihilanth -- to close the rift.
- **Narrative Delivery**: Entirely through in-engine scripted sequences, overheard NPC dialogue, environmental storytelling, and radio transmissions. The player retains full control at all times; there are zero traditional cutscenes.

---

## 2. Technical Foundation (GoldSrc Engine)

| Property | Detail |
|---|---|
| Base Engine | id Software Quake engine (idTech 1), approximately 75% rewritten by Valve |
| Language | C/C++ with some legacy C code |
| Rendering Modes | Software renderer, OpenGL hardware renderer (Direct3D 6 support removed in 2013 SteamPipe update) |
| Map Format | BSP30 (Binary Space Partitioning), compiled from .MAP/.RMF source |
| Texture System | .WAD file format; each texture has its own 256-color palette (unlike Quake's single shared palette) |
| Maximum Texture Resolution | 512x512 pixels (soft limit) |
| Animation System | Skeletal animation for characters (facial expressions, body kinematics) |
| Model Format | .MDL (Studio Model) |
| Physics | Basic rigid-body physics with BSP collision; entity-based triggers for environmental interactions |
| AI Navigation | Node-based pathfinding with pre-placed navigation nodes |
| Audio | Software DSP system providing reverb and echo effects; CD audio tracks for music; WAV for sound effects |
| Networking | Client-server architecture for multiplayer deathmatch |
| Coordinate System | 1 unit = approximately 1 inch (2.54 cm); player height ~72 units standing |
| Simulation Rate | Variable frame-dependent in original release; server tick rate configurable (default 72 Hz for multiplayer) |
| Save System | Quick-save/quick-load at any point; level transition autosaves |

---

## 3. Core Mechanics

### 3.1 Movement

| Parameter | Value |
|---|---|
| Walk Speed | 320 units/second (~8.13 m/s at game scale) |
| Crouch Speed | ~160 units/second (50% of walk speed) |
| Ladder Speed | ~200 units/second |
| Swim Speed | ~200 units/second |
| Jump Velocity | ~268 units/second vertical (approximately 45 units height) |
| Long Jump | Crouch + Jump + Forward; greatly increased horizontal velocity (~560 units/second); requires Long Jump Module |
| Standing Hull Height | 72 units |
| Crouching Hull Height | 36 units |
| Stop Speed | 100 units/second (sv_stopspeed) |
| Ground Friction | 4.0 (sv_friction) |
| Air Control | Reduced; strafing while airborne allows directional influence |
| Max Velocity | 2000 units/second (sv_maxvelocity) |
| Bunny Hopping | Possible via air-strafing + frame-perfect jumps; later patches cap bhop speed to 544 ups (resets to 320 ups on next jump if exceeded) |

### 3.2 Fall Damage

- Falls are calculated based on vertical velocity at impact.
- Safe falling speed threshold: 580 units/second (PLAYER_MAX_SAFE_FALL_SPEED).
- Damage type: DMG_FALL -- bypasses HEV armor entirely.
- Safe fall height: approximately 210 units.
- Lethal fall height (at 100 HP): approximately 655 units.

### 3.3 Interaction System

- **Use Key (E)**: Context-sensitive interaction via raycast from camera center. Operates on doors, buttons, levers, valves, health chargers, suit chargers, scientists, and security guards.
- **NPC Following**: Pressing Use on friendly NPCs (scientists, security guards) causes them to follow the player. Pressing Use again tells them to stay.
- **Scientists**: Can unlock retinal-scanner doors; provide health information and narrative exposition.
- **Security Guards (Barney)**: Can follow the player and fight enemies with their Glock pistol; provide narrative exposition.

### 3.4 Flashlight

- Part of the HEV suit; toggled on/off.
- Drains battery power while active; recharges when off.
- Illuminates a forward cone in dark areas.
- Battery is shared with no other system in Half-Life 1.

---

## 4. Health and Armor System

### 4.1 Player Health

| Parameter | Value |
|---|---|
| Maximum Health | 100 |
| Starting Health | 100 |
| Health Kit Pickup | +15 HP (Easy/Normal), +10 HP (Hard) |
| Health Charger (wall-mounted) | Up to +50 HP (Easy), +40 HP (Normal), +25 HP (Hard) per charger |
| Medkit Limit | Cannot exceed 100 HP |

### 4.2 HEV Suit Armor

| Parameter | Value |
|---|---|
| Maximum Armor | 100 |
| Starting Armor | 0 (suit is acquired in Chapter 2: Anomalous Materials) |
| Battery Pickup | +15 Armor (Easy/Normal), +10 Armor (Hard) |
| Suit Charger (wall-mounted) | Up to +75 Armor (Easy), +50 Armor (Normal), +35 Armor (Hard) per charger |
| Armor Absorption Ratio | Armor absorbs approximately 80% of damage from most sources while charged (each point of armor absorbs ~2 HP of damage, with 1 armor point consumed per 2 HP blocked) |
| Damage Types Bypassing Armor | Fall damage (DMG_FALL), drowning |

### 4.3 HEV Suit Features

- **Acquired**: Chapter 2 (Anomalous Materials), in the suit storage room before the test chamber.
- **Voice Announcements**: Computerized female voice announces suit status changes: "HEV Mark IV Protective System activated," damage warnings ("Major fracture detected," "Morphine administered"), hazard warnings ("Warning: hazardous radiation levels detected," "Warning: high voltage," "Chemical hazard detected," "Biohazard detected"), and ammunition/health pickups.
- **Geiger Counter**: Audible clicking near radiation sources.
- **Morphine Administrator**: Auto-administered on serious injury.
- **Long Jump Module**: Acquired in Chapter 14 (Lambda Core). Enables long jumps essential for Xen platforming.
- **Flashlight**: Toggle-able light source with draining battery.
- **Radio**: Picks up enemy communications and allied transmissions.

---

## 5. Weapons -- Complete Statistics

All weapons use a slot-based selection system mapped to number keys 1-5. Each slot can contain multiple weapons, cycled by pressing the slot key multiple times.

### 5.1 Weapon Slot Assignments

| Slot | Weapons |
|---|---|
| 1 (Melee) | Crowbar |
| 2 (Sidearms) | 9mm Glock Pistol, .357 Magnum Revolver |
| 3 (Rifles/Shotguns) | MP5 Submachine Gun, Shotgun, Crossbow |
| 4 (Heavy/Exotic) | RPG, Tau Cannon (Gauss Gun), Gluon Gun (Egon), Hivehand (Hornet Gun) |
| 5 (Explosives/Creatures) | Hand Grenade, Satchel Charge, Tripmine, Snark |

### 5.2 Detailed Weapon Statistics

Values shown as Easy/Normal/Hard where they vary by difficulty; single value means identical across all difficulties. Damage values are from the game's skill.cfg system and singleplayer source code.

#### Crowbar

| Property | Value |
|---|---|
| Damage per Hit | 10 (skill.cfg; first swing from physics reference: 25 in DM; SP uses skill value of 10) |
| Attack Rate | ~2.0 swings/second |
| Range | Melee (~64 units) |
| Ammo | None (infinite use) |
| Acquired | Chapter 3 (Unforeseen Consequences) |
| Notes | Silent weapon; can break crates, vents, and wooden barriers. No ammo cost. First weapon obtained. |

#### 9mm Glock Pistol

| Property | Value |
|---|---|
| Damage per Bullet | 8 |
| Magazine Size | 17 rounds |
| Max Reserve Ammo | 250 (shared with MP5) |
| Primary Fire Rate | 0.3s between shots (~3.3 rps) |
| Secondary Fire Rate | 0.2s between shots (~5 rps, faster but less accurate) |
| Primary Spread | ~1.15 degrees |
| Secondary Spread | ~11.4 degrees (much wider) |
| Reload Time | 1.5 seconds |
| Headshot Multiplier | 3x |
| Range | 8192 units (hitscan) |
| Sound Volume | 600 (Normal) |
| Acquired | Chapter 3 (Unforeseen Consequences), from a dead security guard |
| Notes | Primary fire is semi-automatic and accurate. Secondary fire is rapid but inaccurate. |

#### .357 Magnum Revolver (Colt Python)

| Property | Value |
|---|---|
| Damage per Bullet | 40 |
| Magazine Size | 6 rounds |
| Max Reserve Ammo | 36 |
| Fire Rate | 0.75s between shots |
| Spread | ~1 degree (very accurate) |
| Reload Time | 2.0 seconds |
| Headshot Multiplier | 3x (120 damage headshot) |
| Range | 8192 units (hitscan) |
| Sound Volume | 1000 (Loud) |
| Acquired | Chapter 5 (We've Got Hostiles) |
| Notes | Extremely powerful per-shot; one-shots most common enemies with headshots. Loud report attracts attention. Limited ammo pool. |

#### MP5 Submachine Gun (9mmAR)

| Property | Value |
|---|---|
| Bullet Damage | 5 per bullet |
| Magazine Size | 50 rounds |
| Max Reserve Ammo (bullets) | 250 (shared with Glock) |
| Fire Rate | 0.1s between shots (10 rps, ~50 DPS) |
| Bullet Spread | ~6 degrees |
| Reload Time | 1.5 seconds |
| M203 Grenade Damage | 100 (contact detonation + splash) |
| M203 Max Reserve | 10 grenades |
| M203 Fire Rate | 1.0s between launches |
| M203 Velocity | 800 units/second |
| Headshot Multiplier | 3x (15 damage headshot) |
| Range | 8192 units (hitscan for bullets) |
| Sound Volume | 600 (Normal) |
| Acquired | Chapter 5 (We've Got Hostiles) |
| Notes | Workhorse automatic weapon. Low per-bullet damage but high rate of fire. Contact grenades are powerful area-denial tools. |

#### Shotgun (SPAS-12)

| Property | Value |
|---|---|
| Damage per Pellet | 5 |
| Primary Fire Pellets | 6 pellets (30 total damage) |
| Secondary Fire Pellets | 12 pellets (60 total damage, fires both barrels) |
| Magazine Size | 8 shells |
| Max Reserve Ammo | 125 |
| Primary Fire Rate | 0.75s cycle |
| Secondary Fire Rate | 1.5s cycle |
| Spread | ~10 degrees |
| Reload | Individual shell loading; can be interrupted by firing |
| Range | 2048 units (hitscan, shorter than pistols) |
| Sound Volume | 1000 (Loud) |
| Acquired | Chapter 5 (We've Got Hostiles) |
| Notes | Devastating at close range; double-barrel secondary fire can one-shot most common enemies. Individual shell reload allows tactical flexibility. |

#### Crossbow

| Property | Value |
|---|---|
| Damage (vs monsters, singleplayer) | 50 per bolt (skill: sk_plr_xbow_bolt_monster) |
| Damage (scoped/client) | 120 per bolt (when zoomed; instant hit at distance) |
| Magazine Size | 5 bolts |
| Max Reserve Ammo | 50 |
| Fire Rate | 0.75s cycle |
| Reload Time | 4.5 seconds (full reload) |
| Projectile Velocity | 2000 units/second (3000 in some references; 1000 underwater) |
| Sound Volume | 200 (Quiet) |
| Acquired | Chapter 9 (Apprehension) |
| Notes | Functions as sniper rifle when zoomed (right-click toggles scope). Silent weapon ideal for stealth. Bolts pin enemies to walls. Underwater-capable. |

#### RPG (Rocket Propelled Grenade Launcher)

| Property | Value |
|---|---|
| Damage | 100 (direct + splash) |
| Magazine Size | 1 rocket |
| Max Reserve Ammo | 5 rockets |
| Fire Rate | ~2.5s cycle (includes reload animation) |
| Splash Radius | ~250 units |
| Guidance | Laser-guided; rocket follows the red laser dot |
| Sound Volume | Loud |
| Acquired | Chapter 7 (Power Up) |
| Notes | Primary fire launches laser-guided rocket; laser dot visible on surfaces. Essential for fighting Apaches and Gargantuas. Self-damage possible at close range. |

#### Tau Cannon (Gauss Gun)

| Property | Value |
|---|---|
| Primary Fire Damage | 20 per shot |
| Primary Fire Ammo Cost | 2 uranium cells per shot |
| Primary Fire Rate | 0.2s cycle |
| Secondary Fire (Charged) | Scales with charge time: damage = charge_level * 50, maximum 200 damage at 4-second charge |
| Secondary Fire Ammo Cost | 1 uranium cell per 0.3s of charging |
| Max Ammo | 100 uranium cells (shared with Gluon Gun) |
| Range | 8192 units (hitscan); charged shot can penetrate thin walls |
| Acquired | Chapter 12 (Surface Tension) |
| Notes | Charged secondary fire can penetrate/reflect off walls. Overcharging (beyond 4 seconds) causes self-damage. Charged shot produces recoil that can boost player movement ("gauss boosting"). Beam visually reflects off surfaces. |

#### Gluon Gun (Egon)

| Property | Value |
|---|---|
| Damage | 14 per tick |
| Tick Rate | 0.1s between ticks (140 DPS) |
| Ammo Consumption | 1 uranium cell per tick |
| Max Ammo | 100 uranium cells (shared with Tau Cannon) |
| Range | 2048 units (continuous beam) |
| Acquired | Chapter 11 (Questionable Ethics) |
| Notes | Continuous beam weapon; hold fire to maintain stream. Extremely high DPS but consumes ammo rapidly. Ignores armor on enemies. Beam must be kept on target. |

#### Hivehand (Hornet Gun)

| Property | Value |
|---|---|
| Damage per Hornet | 8 (player-fired hornets; varies by difficulty) |
| Fire Rate | ~0.25s between hornets (primary); ~0.1s (secondary) |
| Max Ammo | 8 hornets; regenerates ammo over time (1 hornet per ~0.5s) |
| Homing | Primary fire: hornets home in on nearest enemy; Secondary fire: hornets fly straight (faster, no homing) |
| Acquired | Chapter 12 (Surface Tension), dropped by Alien Grunts |
| Notes | Biological weapon with infinite regenerating ammo. Hornets bounce off walls. Primary fire auto-targets enemies. No friendly-fire damage to Xen aliens. |

#### Hand Grenade

| Property | Value |
|---|---|
| Damage | 100 (blast + splash) |
| Max Carry | 10 |
| Fuse Time | ~3 seconds after release |
| Gravity | 0.5x multiplier (affected by gravity) |
| Bounce Coefficient | 1.2 |
| Splash Radius | ~250 units |
| Acquired | Chapter 5 (We've Got Hostiles) |
| Notes | Thrown with arc trajectory influenced by player velocity. Can be "cooked" by holding before throwing. Self-damage possible. |

#### Satchel Charge

| Property | Value |
|---|---|
| Damage | 150 (blast + splash) |
| Max Carry | 5 |
| Throw Delay | 0.5s between placement |
| Detonation | Remote-triggered; minimum 1.0s after placement |
| Gravity | 0.5x multiplier |
| Bounce Coefficient | 1.2 |
| Acquired | Chapter 8 (On A Rail) |
| Notes | Place multiple charges then detonate all simultaneously with secondary fire. Useful for traps and ambushes. |

#### Tripmine

| Property | Value |
|---|---|
| Damage | 150 (blast + splash) |
| Max Carry | 5 |
| Placement Delay | 0.3s |
| Activation Time | 1.0-2.5s after placement (spawn-flag dependent) |
| Acquired | Chapter 8 (On A Rail) |
| Notes | Wall-mountable laser mine. Detonates when any entity breaks the laser beam. Can be placed on any valid wall surface. |

#### Snark (Squeak Grenade)

| Property | Value |
|---|---|
| Bite Damage | 10 per bite |
| Snark HP | 2 |
| Explosion Damage | 5 (when snark dies/self-destructs) |
| Max Carry | 15 |
| Lifespan | ~15 seconds before self-destruction |
| Acquired | Chapter 13 (Forget About Freeman) |
| Notes | Biological weapon; thrown snarks seek nearest enemy and attack repeatedly. Turn on the player if no other targets found. Can be killed by enemies. Swarm tactics effective against groups. |

---

## 6. Enemy Types -- Complete Bestiary

### 6.1 Xen Aliens

#### Headcrab

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 10 | 10 | 20 |
| Leap Attack Damage | 5 | 10 | 10 |
| First Encountered | Chapter 3 (Unforeseen Consequences) |

- **Behavior**: Small parasitic alien that leaps at the player from close range. Ambush predator that hides in vents, behind objects, and in dark areas. Telegraphed leap wind-up. Creates zombies by attaching to human heads.
- **Attack Pattern**: Crouches, pauses briefly (telegraph), then launches in a ballistic arc toward the player's head.

#### Zombie (Headcrab Zombie)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 50 | 50 | 100 |
| Claw Swipe Damage | 10 | 20 | 20 |
| Double Slash Damage | 25 | 40 | 40 |
| First Encountered | Chapter 3 (Unforeseen Consequences) |

- **Behavior**: Reanimated human host controlled by a headcrab fused to the head. Slow, shambling movement. Attacks with powerful claw swipes at melee range. Very durable for early enemies. When killed, the headcrab may detach and continue attacking independently.
- **Variants**: Standard zombie (scientist host), armored zombie (security guard host with slightly more HP in some encounters).

#### Vortigaunt (Alien Slave / Islave)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 30 | 30 | 60 |
| Claw Attack Damage | 8 | 10 | 10 |
| Electrical Beam Damage | 10 | 10 | 15 |
| First Encountered | Chapter 3 (Unforeseen Consequences) |

- **Behavior**: Bipedal alien slave of the Nihilanth. Attacks with electrical beams at range (visible green lightning with charge-up telegraph) and claws at melee range. Often encountered in groups of 2-4. Beam attack requires line-of-sight and has a visible charge-up animation providing a reaction window.
- **Tactical Note**: Beam can be interrupted by breaking line of sight or staggering the Vortigaunt.

#### Houndeye

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 20 | 20 | 30 |
| Sonic Attack Damage | 10 | 15 | 15 |
| First Encountered | Chapter 3 (Unforeseen Consequences) |

- **Behavior**: Pack-hunting three-legged alien with a single large eye. Shy and timid alone, but dangerous in groups. Emits a sonic shockwave attack with a visible charging animation (crouches and builds energy). Pack behavior: groups of 3+ deal up to 30% bonus damage (10% per squad member). Sonic blast radius: 384 units, with damage halved if no direct line of sight. Blast color changes based on pack size.
- **Tactical Note**: Easily dispatched individually; focus fire before they group.

#### Bullsquid

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 40 | 40 | 120 |
| Bite Attack Damage | 15 | 25 | 25 |
| Tail Whip Damage | 35 | 35 | 35 |
| Toxic Spit Damage | 10 | 10 | 15 |
| First Encountered | Chapter 3 (Unforeseen Consequences) |

- **Behavior**: Aggressive bipedal alien with tentacles around its mouth. Ranged attack: spits toxic bile at medium range. Melee attacks: powerful bite and devastating tail whip. Hostile to headcrabs and will eat them. Territorial and aggressive; attacks immediately on sight. Extremely durable on Hard difficulty.

#### Barnacle

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | ~35 | ~35 | ~35 |
| Bite Damage | ~25 per bite (kills in 1-3 bites depending on armor) |
| First Encountered | Chapter 3 (Unforeseen Consequences) |

- **Behavior**: Stationary ceiling-dwelling ambush predator. Hangs a long, sticky tongue from the ceiling. Touching the tongue pulls the player upward into its maw. No intelligence -- purely reactive to contact stimulus. While being pulled, the player can look and shoot but cannot move. Killable with 4-5 Glock shots or 1-2 crowbar hits. Can be avoided by simply not touching the tongue.
- **Tactical Note**: Often placed over doorways and in corridors. Can be used against enemies -- NPCs pulled up and eaten.

#### Ichthyosaur

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 200 | 200 | 400 |
| Bite Damage | 20 | 35 | 50 |
| First Encountered | Chapter 9 (Apprehension) |

- **Behavior**: Large aquatic predator encountered in flooded areas. Extremely fast swimmer. Attacks by biting at close range. Must be facing the player to attack. The crossbow is effective underwater. Very dangerous in confined water areas; extremely durable.

#### Alien Grunt

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 60 | 90 | 120 |
| Punch Damage | 10 | 20 | 20 |
| Hornet Attack Damage | 4 | 5 | 8 |
| First Encountered | Chapter 12 (Surface Tension) |

- **Behavior**: Heavily armored bipedal Xen soldier. Fires homing hornets from a biological arm-mounted hivehand. Strong melee punch at close range. Wears natural body armor that can deflect bullets. Often encountered in groups in later chapters and on Xen. Drops hivehand weapon on death.

#### Alien Controller

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 60 | 60 | 100 |
| Energy Ball Damage | 3 | 4 | 5 |
| Psychic Attack Damage | 15 | 25 | 35 |
| First Encountered | Chapter 14 (Lambda Core) / Chapter 15 (Xen) |

- **Behavior**: Floating Xen commander resembling a smaller Nihilanth. Levitates and flies freely. Fires slow-moving energy spheres that deal damage on contact. Also has a close-range psychic attack. Highly mobile and difficult to hit. Often encountered in open areas with limited cover.

#### Leech

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 2 | 2 | 2 |
| Bite Damage | 2 | 2 | 2 |

- **Behavior**: Tiny aquatic creature found in shallow water. Minimal threat individually but encountered in large swarms. Annoying damage-over-time hazard in water sections.

#### Snark (Enemy)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 2 | 2 | 2 |
| Bite Damage | 10 | 10 | 10 |
| Explosion Damage (on death) | 5 | 5 | 5 |

- **Behavior**: Small beetle-like creature found in nests. Aggressively charges nearest target. Self-destructs after ~15 seconds. Also usable as a player weapon.

### 6.2 Human Enemies

#### HECU Marine (Human Grunt)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 50 | 50 | 80 |
| 9mm AR Bullet Damage | 3 | 5 | 6 |
| Shotgun Pellets Per Shot | 3 | 5 | 6 |
| Shotgun Pellet Damage | 5 | 10 | 10 |
| Grenade Damage | 100 (same as player grenades) |
| First Encountered | Chapter 5 (We've Got Hostiles) |

- **Behavior**: The most tactically sophisticated enemy in the game. Operates in squads of 2-5 soldiers. Squad-based AI behaviors include:
  - **Flanking**: Will attempt to move to attack from the player's side or rear if direct assault fails.
  - **Suppressive Fire**: Pins the player behind cover with sustained bursts.
  - **Grenade Usage**: Throws grenades to flush the player from cover or kill behind obstacles.
  - **Cover Usage**: Takes cover behind objects and leans to fire; retreats to cover when reloading.
  - **Communication**: Vocalize tactical information ("Fire in the hole!", "He's flanking us!", "I'm hit!").
  - **Retreat**: Falls back when severely wounded or outgunned.
- **Variants**: Shotgun-armed grunts (closer engagement range, more lethal), MP5-armed grunts (standard), grenade-launcher-equipped grunts.
- **Equipment**: Some wear gas masks; carry grenades regardless of primary weapon.

#### Female Black Ops Assassin

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 30 | 50 | 50 |
| Pistol Damage | 5 | 5 | 8 |
| First Encountered | Chapter 11 (Questionable Ethics) / Chapter 14 (Lambda Core) |

- **Behavior**: Elite government operatives sent to clean up after the HECU. Extremely fast and agile; can sprint faster than any other enemy and jump to extreme heights. Armed with suppressed Glock pistols and hand grenades. On Hard difficulty, possess a cloaking device that renders them partially invisible when stationary (fails during movement; makes an audible electrical zap on activation). Use martial arts kicks and punches at melee range. Throw grenades only from frontal positions at close range.

#### AH-64 Apache Helicopter

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 150 | 250 | 400 |
| Machine Gun Damage | 8 | 10 | 10 |

- **Behavior**: Military attack helicopter encountered in outdoor areas. Strafes the player with machine gun fire and launches rockets. Extremely dangerous in open terrain. Best countered with the RPG launcher. Circles the player's position and makes attack runs.

### 6.3 Turrets and Automated Defenses

#### Ceiling Turret (Automatic Turret)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 50 | 50 | 60 |
| Bullet Damage | 8 | 10 | 10 |

- **Behavior**: Ceiling-mounted rotating turret found in Black Mesa security areas. Detects movement within a cone and fires rapid bursts. Can be destroyed by gunfire.

#### Mini Turret

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 40 | 40 | 50 |
| Bullet Damage | 5 | 5 | 8 |

- **Behavior**: Small floor-mounted turret. Shorter detection range than ceiling turrets.

#### Sentry Turret (Ground)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 40 | 40 | 50 |
| Bullet Damage | 3 | 4 | 5 |

- **Behavior**: Tripod-mounted portable turret placed by HECU forces. Can be knocked over by explosions.

---

## 7. Boss Encounters

### 7.1 Tentacle (Chapter 6: Blast Pit)

- **Type**: Environmental puzzle boss (cannot be damaged by conventional weapons).
- **Description**: Three massive alien tentacles emerging from a rocket silo pit. Each tentacle has a segmented green stalk ending in a sharp blade-like appendage with small grasping arms.
- **Detection**: Tentacles are blind; detect prey exclusively through sound and vibration. Crouching and moving silently allows the player to pass undetected. Walking normally or firing weapons attracts immediate lethal strikes.
- **Damage**: A direct hit from a tentacle is instantly lethal or near-lethal.
- **Distracting**: Throwing grenades causes tentacles to attack the explosion point for approximately 10 seconds.
- **Defeat Method**: The player must navigate three branching paths from the silo to restore Oxygen, Fuel, and Power to the rocket engine. After activating all three systems, the player returns to the control room and initiates a test fire, incinerating the tentacles with rocket exhaust.
- **Key Mechanic**: Stealth + environmental puzzle hybrid. Crouch-walking is nearly silent. The player cannot fight directly; must use the environment.

### 7.2 Gargantua (Chapter 7: Power Up / Chapter 12: Surface Tension)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 800 | 800 | 1000 |
| Stomp/Punch Damage | 10 | 30 | 30 |
| Flame Damage (per tick) | 3 | 5 | 5 |
| Flame Radius | 50 | 100 | 100 |

- **Description**: Towering blue-skinned alien roughly 3 times the player's height. Massive clawed arms that generate flames from the wrists. Extremely durable with resistance to most conventional weapons.
- **Behavior**: Charges the player relentlessly. Melee attacks with devastating punches. Flame attack: opens arms to project flame streams with limited range. Can smash through certain obstacles.
- **Power Up Encounter (Scripted Defeat)**: The first Gargantua is defeated by luring it between two electrical generators and activating the power switch, electrocuting it. This is the intended solution.
- **Surface Tension Encounters**: Later Gargantuas can be fought with heavy weapons (RPG, Tau Cannon, Gluon Gun) though it requires extensive ammunition.
- **Cannot be conventionally killed easily**: Its massive HP pool makes direct combat extremely resource-intensive.

### 7.3 Gonarch (Chapter 16: Gonarch's Lair)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Claw Stomp Damage | 50 | 60 | 70 |
| Acid Mortar Damage | 100 | 120 | 160 |
| Acid Splash Radius | 250 | 250 | 270 |
| Health Factor | 1.0 | 1.0 | 1.0 |

- **Description**: The "Big Momma" -- a massive headcrab matriarch with a dark brown carapace supported by four powerful arthropod legs and a large fleshy egg sac dangling from its underbelly. The only known adult stage of the headcrab lifecycle.
- **Weak Point**: The pendulous egg sac is the only vulnerable area; shots to the carapace/legs deal minimal damage.
- **Attacks**: Charges and stomps with massive legs; hurls yellowish acid mortars from the top of its shell in an arc; continuously spawns baby headcrabs from the egg sac (up to 20 simultaneous babies).
- **Multi-Phase Battle**: The fight spans three arena areas connected by a scripted path system (info_bigmomma nodes). The Gonarch has a base health of ~150 HP per phase; after taking enough damage, it retreats to the next arena, regenerating health at each node. It can only be killed in the final arena when there is no next node.
- **Strategy**: Target the egg sac with explosive and heavy weapons; manage baby headcrab swarms; conserve ammo across all three phases.

### 7.4 Nihilanth (Chapter 18: Nihilanth)

| Property | Easy | Normal | Hard |
|---|---|---|---|
| Health | 800 | 800 | 1000 |
| Energy Sphere Damage | 30 | 30 | 50 |

- **Description**: The final boss. A massive floating alien entity with an enormous head, a baby-like body, and shackled wrists. Commands the Xen alien forces. Telepathically communicates with Freeman throughout Xen ("You are man... he is not man... for you he waits...").
- **Attack Patterns**:
  - **Blue Energy Spheres**: Fast-moving electrical orbs dealing heavy direct damage with small splash radius.
  - **Green Teleportation Orbs**: Slow-moving homing spheres; on contact, teleport Freeman to side chambers populated by Xen aliens. Side chambers contain supplies and a portal back to the boss arena.
- **Shield Mechanic**: Gold-colored energy orbs orbit the Nihilanth's head, rendering it invulnerable. Damage depletes these orbs, but three yellow crystals embedded in the upper walls of the chamber regenerate the shield.
- **Defeat Method**:
  1. Destroy all three wall-mounted crystals (requires using the jump pads to reach sufficient height to target them).
  2. With crystals destroyed, the shield orbs no longer regenerate. Continue dealing damage.
  3. When enough damage is dealt, the Nihilanth's head opens like a flower, revealing its brain -- a large energy sphere atop a fleshy prong.
  4. Fire into the exposed brain to deal critical damage. The brain is the only true weak point.
  5. After sufficient brain damage, the Nihilanth is destroyed.
- **Arena**: Large vertical chamber with floating platforms and jump pads that launch the player upward. The fight requires significant vertical mobility.

---

## 8. Chapter Progression (All 19 Chapters)

### Chapter 1: Black Mesa Inbound

- **Maps**: c0a0, c0a0a, c0a0b, c0a0c, c0a0d, c0a0e
- **Setting**: Black Mesa transit system tram
- **Gameplay**: Non-interactive opening sequence. Player rides the Black Mesa monorail tram system through the facility, witnessing the daily operations of the research complex. Introduces the setting, atmosphere, and scale of the facility. Establishes the G-Man observing from a distant platform.
- **Duration**: ~5 minutes
- **Enemies**: None
- **Weapons**: None
- **Key Events**: Environmental storytelling; introduction of Black Mesa's various sectors; G-Man sighting.

### Chapter 2: Anomalous Materials

- **Setting**: Sector C Test Labs and HEV storage
- **Gameplay**: The player navigates the Anomalous Materials lab, acquires the HEV suit, and pushes the sample cart into the anti-mass spectrometer beam. The Resonance Cascade occurs, teleporting the player briefly to Xen and back.
- **Enemies**: None (pre-disaster)
- **Weapons**: None
- **Key Events**: HEV suit acquisition; the Resonance Cascade; first brief Xen glimpse; scientists in distress.

### Chapter 3: Unforeseen Consequences

- **Setting**: Destroyed Sector C labs and maintenance areas
- **Gameplay**: First combat encounters. Navigate through the damaged facility, encountering teleporting aliens for the first time. Learn basic combat and movement through environmental tutorials (breaking vents, crawling through ducts).
- **Enemies**: Headcrabs, Zombies, Vortigaunts (first appearances), Houndeyes, Bullsquids
- **Weapons Acquired**: Crowbar, 9mm Glock Pistol
- **Key Events**: First alien encounters; scientists provide exposition about what happened; first contact with security guards.

### Chapter 4: Office Complex

- **Setting**: Sector D administrative offices
- **Gameplay**: Navigate through office buildings, cafeterias, and storage areas. Ceiling turrets appear as a new threat. Scientists and guards are barricaded throughout, providing help and information. Environmental storytelling through destroyed offices and alien infestations.
- **Enemies**: Headcrabs, Zombies, Vortigaunts, Ceiling Turrets
- **Weapons Acquired**: None (standard ammo resupply)
- **Key Events**: Scientists mention the military is coming to rescue everyone.

### Chapter 5: "We've Got Hostiles!"

- **Setting**: Sector D storage facility and military staging areas
- **Gameplay**: Introduction of the HECU Marines as enemies. The military is killing scientists, not rescuing them. First major firefights against intelligent human opponents. Trip mines and automated turrets deployed by the military.
- **Enemies**: HECU Marines (first appearance), Headcrabs, Zombies, Turrets
- **Weapons Acquired**: MP5 Submachine Gun, Hand Grenades, .357 Magnum, Shotgun
- **Key Events**: Realization that the military is hostile; witnesses soldiers executing scientists; paradigm shift from alien horror to military combat.

### Chapter 6: Blast Pit

- **Setting**: Sector D High Security Storage, Silo D rocket test facility
- **Gameplay**: Tentacle boss encounter (see Boss Encounters section). The player must restore Oxygen, Fuel, and Power to the rocket engine by navigating three separate paths from the central silo. Heavy puzzle/stealth focus.
- **Enemies**: Tentacle (boss), Headcrabs, Zombies, Bullsquids, Houndeyes, Leeches
- **Weapons Acquired**: None
- **Key Events**: Tentacle boss; rocket test fire; meeting the G-Man walking in an otherwise inaccessible area.

### Chapter 7: Power Up

- **Setting**: Sector E Track Control, power station
- **Gameplay**: First Gargantua encounter. The player must restore power to the rail system while avoiding the Gargantua, then lure it between electrical generators and activate the power to electrocute it. Introduces the rail transport system used in the next chapter.
- **Enemies**: Gargantua (boss), HECU Marines, Vortigaunts, Houndeyes
- **Weapons Acquired**: RPG Launcher
- **Key Events**: Gargantua introduction; G-Man sighting; rail system power restoration; scripted battle between HECU Marines and Gargantua.

### Chapter 8: On A Rail

- **Setting**: Sector E Materials Transport rail system
- **Gameplay**: Vehicle section. The player rides rail carts through a network of underground tunnels, switching tracks at junctions, dismounting to clear obstacles and fight enemies, and navigating to the satellite launch facility. Track switching puzzles and combat while on/near the rail cart.
- **Enemies**: HECU Marines, Vortigaunts, Headcrabs, Zombies, Barnacles, Turrets
- **Weapons Acquired**: Satchel Charges, Tripmines
- **Key Events**: Rail cart riding and track navigation; satellite rocket launch facility approach; G-Man sighting on a departing train.

### Chapter 9: Apprehension

- **Setting**: Sector E industrial/aquatic areas
- **Gameplay**: Underwater sections with Ichthyosaur encounters. The player obtains the crossbow and engages in underwater combat. Chapter climaxes with Freeman being captured by HECU Marines and stripped of all weapons, then dropped into a trash compactor. He escapes using a crowbar found in the trash.
- **Enemies**: Ichthyosaur (first appearance), HECU Marines, Barnacles, Headcrabs
- **Weapons Acquired**: Crossbow (acquired then lost when captured; re-obtained later)
- **Key Events**: First Ichthyosaur encounter; player capture and weapon confiscation; trash compactor escape; G-Man sighting.

### Chapter 10: Residue Processing

- **Setting**: Waste processing facility
- **Gameplay**: Largely combat-free traversal/puzzle chapter. The player navigates through industrial waste processing machinery -- conveyor belts, compactors, furnaces, toxic waste vats -- while weaponless (only crowbar). Environmental hazard navigation is the primary challenge. Gravity-defying conveyor belts and timing-based machinery puzzles.
- **Enemies**: Minimal (Headcrabs, Leeches in waste)
- **Weapons Acquired**: Weapons gradually re-obtained through the chapter
- **Key Events**: Escape from waste processing; regaining weapons; purely environmental gameplay.

### Chapter 11: Questionable Ethics

- **Setting**: Advanced Biological Research Lab (weapons research)
- **Gameplay**: The player discovers Black Mesa was experimenting on Xen aliens and developing energy weapons. Combat-heavy chapter with both HECU Marines and aliens. The player acquires the Gluon Gun from a lab. Puzzles involve using security cards and cooperating with surviving scientists to unlock sealed doors.
- **Enemies**: HECU Marines, Alien Grunts (first appearance), Vortigaunts, Headcrabs, Zombies
- **Weapons Acquired**: Gluon Gun (Egon)
- **Key Events**: Discovery of Xen alien experimentation labs; Gluon Gun acquisition; alien grunt introduction.

### Chapter 12: Surface Tension

- **Setting**: Black Mesa surface -- cliffs, dams, parking lots, outdoor installations
- **Gameplay**: The longest and most combat-intensive chapter. Large-scale outdoor warfare between HECU forces, Black Ops, and aliens. The player navigates cliffs, fights through minefields, battles Apache helicopters, confronts a second Gargantua, and crosses a dam. Features the widest variety of enemies and combat scenarios in the game.
- **Enemies**: HECU Marines (heavy presence), Apache Helicopters, Black Ops Assassins, Alien Grunts, Alien Controllers, Gargantua, Vortigaunts, Headcrabs, Snipers, Turrets, Barnacles
- **Weapons Acquired**: Tau Cannon (Gauss Gun), Hivehand (from killed Alien Grunts)
- **Key Events**: Surface warfare; Apache helicopter battles; cliff traversal; dam crossing; G-Man sightings; introduction of Black Ops.

### Chapter 13: "Forget About Freeman!"

- **Setting**: Underground canals, vehicle bay, industrial areas
- **Gameplay**: The military begins full retreat from Black Mesa. Radio transmissions confirm the pullout. The facility is now overrun by aliens. The player fights through Xen-infested areas with organic alien growth covering walls and floors. Mixed alien and remnant military encounters. Air strikes bombard the surface.
- **Enemies**: HECU Marines (retreating), Alien Grunts, Vortigaunts, Headcrabs, Zombies, Snarks (wild nests)
- **Weapons Acquired**: Snarks
- **Key Events**: HECU retreat; air strikes; heavy Xen infestation; snark nests; approaching Lambda Complex.

### Chapter 14: Lambda Core

- **Setting**: Lambda Complex reactor facility
- **Gameplay**: The player reaches the science team's last holdout. Must flood the Lambda reactor coolant chambers to access the teleportation equipment at the core. Extremely challenging combat against waves of Xen aliens. Scientists provide the Long Jump Module and explain that the Nihilanth must be destroyed to close the rift. The chapter ends with teleportation to Xen.
- **Enemies**: Alien Grunts, Vortigaunts, Alien Controllers, Headcrabs, Zombies
- **Weapons Acquired**: Long Jump Module
- **Key Events**: Lambda team exposition; Long Jump Module acquisition; reactor flooding sequence; teleportation to Xen; final weapon/ammo resupply.

### Chapter 15: Xen

- **Setting**: Xen borderworld -- floating asteroid islands
- **Gameplay**: First Xen chapter. Low-gravity platforming across floating islands. The Long Jump Module is essential. Alien flora provides trampolines (bouncing mushroom-like plants). Environmental hazards include void falls (instant death). Minimal combat; primarily platforming and navigation.
- **Enemies**: Alien Controllers, Headcrabs, Vortigaunts, Houndeyes
- **Key Events**: Arrival on Xen; first low-gravity platforming; alien ecosystem exploration; dead HEV-wearing researchers discovered.

### Chapter 16: Gonarch's Lair

- **Setting**: Xen cave system
- **Gameplay**: Multi-phase boss battle against the Gonarch across three connected arenas (see Boss Encounters). The player fights through Xen cave terrain while being pursued by the Gonarch. Continuous combat interspersed with traversal.
- **Enemies**: Gonarch (boss), Baby Headcrabs (spawned by Gonarch)
- **Key Events**: Gonarch boss fight; descending deeper into Xen.

### Chapter 17: Interloper

- **Setting**: Xen alien factory/military complex
- **Gameplay**: The player infiltrates the Xen alien infrastructure -- vast organic factories where Alien Grunts are produced in pods. Heavy combat against Alien Grunts, Controllers, and Vortigaunts. Conveyor systems and industrial alien machinery. The most combat-dense Xen chapter.
- **Enemies**: Alien Grunts (heavy presence), Alien Controllers, Vortigaunts, Headcrabs
- **Key Events**: Discovery of alien military-industrial complex; alien grunt production facility.

### Chapter 18: Nihilanth

- **Setting**: Nihilanth's chamber at the heart of Xen
- **Gameplay**: Final boss encounter (see Boss Encounters). Vertical arena with jump pads, floating platforms, and the massive Nihilanth at the center. Multi-phase fight requiring crystal destruction, shield depletion, and brain targeting.
- **Enemies**: Nihilanth (final boss), Alien Controllers, Vortigaunts (spawned from teleport portals)
- **Key Events**: Final boss battle; Nihilanth's defeat.

### Chapter 19: Endgame

- **Setting**: Abstract dimension / G-Man's realm
- **Gameplay**: Non-interactive epilogue. After the Nihilanth's destruction, the G-Man appears and offers Freeman a choice: work for his mysterious employers, or face a "battle you have no chance of winning." Regardless of the player's path, the G-Man's monologue concludes the game. Freeman is placed in stasis.
- **Key Events**: G-Man's offer; Freeman's fate; cliffhanger ending leading to Half-Life 2.

---

## 9. Environmental Puzzles

### 9.1 Puzzle Archetypes

| Puzzle Type | Description | Example Chapters |
|---|---|---|
| Power Restoration | Find and activate generators/switches to restore electricity to doors, lifts, or machinery | Blast Pit, Power Up, Lambda Core |
| Valve/Pressure | Turn valves to redirect steam, water, or fuel to clear paths or activate systems | Blast Pit, Residue Processing |
| Machinery Navigation | Time movement through industrial equipment (conveyors, crushers, lifts) to traverse safely | Residue Processing, On A Rail |
| Flood/Drain | Fill or empty water chambers to access submerged paths or floating platforms | Lambda Core, Apprehension |
| Track Switching | Operate rail switches to navigate the rail cart to the correct destination | On A Rail |
| Physics/Object | Push objects (crates, barrels) to create platforms, weigh down buttons, or block hazards | Various chapters |
| Explosive Clearance | Use explosives (satchels, grenades, tripmines) to destroy obstacles blocking paths | Surface Tension, Forget About Freeman |
| NPC Assistance | Lead scientists to retinal scanners or security doors they can unlock; lead guards for fire support | Office Complex, Lambda Core |
| Vent Navigation | Find and break vent covers to access alternative routes through ductwork | Throughout game |

### 9.2 Environmental Hazards

| Hazard Type | Damage Behavior | HEV Announcement |
|---|---|---|
| Radiation (green pools/barrels) | Continuous damage over time while in contact; Geiger counter audible | "Warning: hazardous radiation levels detected" |
| Toxic Waste (brown/green slime) | High continuous damage; often instant death in deep pools | "Warning: hazardous chemical detected" |
| Electrocution (broken wires/water) | Burst damage on contact; can be lethal depending on source | "Warning: high voltage" |
| Fire/Flames | Continuous damage while in fire zone | "Heat damage detected" |
| Explosive Barrels | Detonate when shot or near explosions; splash damage | N/A |
| Crushers/Machinery | Instant death or very high damage from moving machinery | N/A |
| Void/Bottomless Pit | Instant death from falling into void (especially in Xen) | N/A |
| Drowning | Damage begins after oxygen meter depletes (~12 seconds underwater) | "Oxygen reserves depleted" |
| Tripmines (enemy-placed) | 150 damage from laser-triggered mines | N/A |

---

## 10. AI System

### 10.1 HECU Marine Squad AI

The HECU Marines represent the most advanced AI in Half-Life and were groundbreaking for their era. Their behavior system includes:

- **Squad Formation**: Marines operate in squads of 2-5. Squad leader coordinates actions.
- **Cover System**: Marines actively seek cover nodes, crouching behind objects and leaning to fire.
- **Flanking**: If the player holds a position, marines will send squad members along alternate routes to attack from the side or rear.
- **Suppression**: One or more marines maintain fire on the player's position while others reposition.
- **Grenade Tactics**: Marines throw grenades to flush the player from cover. They announce grenade throws vocally ("Fire in the hole!"). Grenades are used when the player is behind solid cover and direct fire is ineffective.
- **Retreat**: Wounded marines fall back to secondary positions. If badly outgunned, squads may retreat entirely.
- **Communication**: Marines vocalize their status and intentions using radio chatter and shouts: taking damage, throwing grenades, reloading, spotting the player, calling for backup.
- **Weapon Behavior**: MP5-armed marines fire in bursts then reposition. Shotgun-armed marines advance aggressively for closer engagement. Grenadier-equipped marines stay at range.

### 10.2 Alien AI Behaviors

| Enemy | AI Type | Key Behaviors |
|---|---|---|
| Headcrab | Ambush Predator | Hides in dark spaces; leaps at detected player; no squad behavior |
| Zombie | Shambler | Slow advance toward noise/sight; attacks at melee range; no tactical behavior |
| Vortigaunt | Ranged Attacker | Maintains medium distance; charges beam attack with telegraph; retreats when wounded |
| Houndeye | Pack Hunter | Timid alone; forms packs; coordinates sonic attacks for bonus damage |
| Bullsquid | Territorial Brute | Aggressive on sight; alternates between ranged spit and melee charges; attacks headcrabs on sight |
| Barnacle | Stationary Trap | No movement; reacts to tongue contact only |
| Ichthyosaur | Aquatic Predator | Fast swimming; lunges at player in water; retreats and circles for re-engagement |
| Alien Grunt | Xen Soldier | Uses hivehand at range; punches at melee; moderate tactical awareness |
| Alien Controller | Flying Caster | Levitates and strafes; fires energy projectiles; stays at distance |

### 10.3 Friendly NPC AI

- **Scientists**: Follow the player when activated; provide exposition through contextual dialogue; unlock retinal-scanner doors; cower and flee from enemies; can be killed (by enemies or player).
- **Security Guards (Barney)**: Follow the player when activated; engage enemies with Glock pistol; take cover when under fire; have limited HP (~35-50) and can be killed. Provide ammunition and narrative information.

---

## 11. Xen Mechanics (Chapters 15-18)

### 11.1 Low Gravity

- Gravity on Xen is significantly reduced compared to Earth levels.
- Gravity is always directed downward (not toward individual asteroids), meaning the player can fall off islands into the void below.
- Jumps travel higher and farther; descents are slower.
- The Long Jump Module (acquired in Chapter 14) is essential for crossing large gaps between floating islands.
- Long Jump execution: Press Crouch, then immediately Jump while holding Forward during the crouching motion (timing-critical).

### 11.2 Alien Flora

| Flora Type | Function |
|---|---|
| Trampoline Plants | Large mushroom-like growths that bounce the player high into the air when stepped on |
| Healing Pools | Glowing green-yellow pools that restore health when waded through |
| Retractable Stalks | Organic platforms that extend/retract, requiring timing to use as stepping stones |
| Light Stalks | Bioluminescent plants providing ambient light in Xen caves |
| Organic Walls | Living tissue barriers that can be destroyed to open paths |

### 11.3 Xen Platforming Design

- Floating asteroid islands serve as platforms of varying sizes.
- Void falls are instant death -- no recovery.
- Platform distances calibrated to require Long Jump for most gaps.
- Trampoline plants serve as mandatory vertical launchers.
- Some platforms are moving or temporary.
- Jump pads (artificial Xen technology) launch the player to specific destinations.

---

## 12. Vehicle Section: Rail Cart (Chapter 8: On A Rail)

### 12.1 Rail Cart Mechanics

| Property | Value |
|---|---|
| Speed | ~250-400 units/second (variable) |
| Control | Forward/Reverse throttle; automatic following of track |
| Track Switching | Dismount and operate track switches at junctions |
| Weapons While Mounted | Player can use all weapons while riding; turret-mounted gun on some carts |
| Dismounting | Jump off at any time; can re-board |
| Mounted Gun | Some carts have a front-mounted gun usable via interaction |

### 12.2 Rail Section Design

- The rail system is a network with multiple branching tracks and loops.
- Incorrect track choices lead to loops or dead ends.
- The player must frequently dismount to clear enemies, operate switches, and solve access puzzles.
- Environmental hazards along tracks include explosive barrels, barnacles over the rail line, and military blockades.
- The objective is to reach the satellite rocket launch facility.

---

## 13. Scripted Sequence System

### 13.1 Design Philosophy

Half-Life pioneered the use of in-engine scripted sequences as an alternative to pre-rendered cutscenes. Key principles:

- The player retains full movement and camera control during all scripted events.
- Events occur in the game world in real-time.
- The player can observe events from any angle or distance (and sometimes miss them entirely).
- NPCs perform scripted animations and deliver dialogue through the game's animation and sound system.
- Sequences range from major plot revelations (the Resonance Cascade) to small environmental details (a headcrab dropping from a vent onto a scientist).

### 13.2 Scripted Sequence Types

| Type | Description | Examples |
|---|---|---|
| Plot Exposition | NPCs deliver critical story information | Scientists explaining the Resonance Cascade; Lambda team briefing |
| Environmental Drama | Witnessed events that build tension/atmosphere | Scientist dragged into vent by headcrab; marines executing scientists; Gargantua fighting soldiers |
| Puzzle Hints | NPCs provide verbal guidance for puzzle solutions | "Maybe you should try using the rocket engine" (Blast Pit) |
| Enemy Introduction | Dramatic first appearance of a new enemy type | Ichthyosaur leaping from water to kill a scientist; Gargantua smashing through a wall |
| G-Man Sightings | The mysterious G-Man observed in otherwise inaccessible locations | Seen on distant platforms, in sealed rooms, boarding trains |
| NPC Deaths | Scripted deaths that cannot be prevented (usually) | Scientists killed by aliens or military to demonstrate threats |
| Combat Set-Pieces | Scripted military vs. alien battles the player witnesses or joins | Marines fighting Vortigaunts; soldiers vs. Gargantua |

### 13.3 Cancelable Sequences

Some scripted NPC events can be interrupted by the player:
- Speaking to an NPC mid-script can cancel their scripted path (e.g., saving the scientist in Blast Pit from being grabbed by the Tentacle; stopping the security guard in Residue Processing from running into a Barnacle).

---

## 14. Audio Design

### 14.1 Music

- **Composer**: Kelly Bailey
- **Style**: Atmospheric industrial electronica; moody, tension-building ambient tracks.
- **Delivery**: CD audio tracks triggered at specific level locations. Music is event-driven, not continuous -- many sections have no music at all, using ambient sound only.
- **Notable Tracks**: "Adrenaline Horror," "Vague Voices," "Cavern Ambience," "Nuclear Mission Jam," "Diabolical Adrenaline Guitar."
- **Design Philosophy**: Music punctuates key moments rather than playing constantly, heightening impact through contrast with silence.

### 14.2 Sound Effects

- **Weapon Sounds**: Each weapon has distinct firing, reloading, and dry-fire sounds. Volume values range from 200 (Quiet, crossbow) to 1000 (Loud, shotgun/magnum).
- **Footstep System**: Material-based footstep sounds tied to surface type (metal, concrete, water, dirt, vent/duct, tile, grate).
- **Environmental Audio**: Machinery hums, dripping water, electrical buzzing, steam vents, distant explosions, Xen ambient sounds.
- **DSP Effects**: Software-based reverb and echo system providing environmental audio processing (reverberant halls, tight corridors, outdoor spaces).
- **HEV Suit Voice**: Computerized female voice providing health, hazard, and status announcements.

### 14.3 Enemy Vocalizations

| Enemy | Sound Design |
|---|---|
| Headcrab | Chittering, squealing; hissing before leap |
| Zombie | Moaning, gurgling; pain screams (reversed human screams) |
| Vortigaunt | Alien speech ("Gah-luh-hung!"); electrical crackling during beam charge |
| Houndeye | Whimpering/whining when calm; harmonic resonance building during attack |
| Bullsquid | Guttural growling; wet spitting sounds |
| HECU Marines | Full tactical radio chatter and shouts; weapon-related callouts; taunts |
| Barnacle | Wet chewing; tongue slurp |
| Alien Grunt | Deep alien vocalizations; hornet buzzing |
| Ichthyosaur | Underwater roaring and thrashing |
| Gargantua | Deep mechanical roaring; flame whoosh |
| Nihilanth | Telepathic whispered speech ("Come... you are man... he is not man...") |

### 14.4 NPC Dialogue

- **Scientists**: Multiple voice actors; context-sensitive lines about the disaster, aliens, military, and plot exposition. Idle chatter, pain sounds, and death screams.
- **Security Guards**: Distinct voice (the "Barney" voice); combat callouts, following/stay responses, contextual dialogue.
- **G-Man**: Distinctive halting, breathy speech pattern; delivers epilogue monologue.

---

## 15. UI / HUD Layout

### 15.1 HUD Elements

| Element | Position | Color | Description |
|---|---|---|---|
| Health Display | Bottom-left | Green | Numeric value (0-100) with red cross icon |
| Armor Display | Bottom-left (above health) | Blue | Numeric value (0-100) with shield icon |
| Ammo (Current Magazine) | Bottom-right | Orange/Yellow | Numeric value showing rounds in current magazine |
| Ammo (Reserve) | Bottom-right (next to magazine) | Orange/Yellow | Numeric value showing total reserve ammunition |
| Weapon Selection | Top-center | Orange | Horizontal slot display triggered by number keys; shows weapon icons within selected slot category |
| Crosshair | Center | Orange | Weapon-specific crosshair design; some weapons (RPG) show laser dot instead |
| Flashlight Indicator | Top-right | Orange | Battery-style icon showing remaining flashlight power |
| HEV Suit Notifications | Center | Orange text | Scrolling text messages from the HEV suit system |
| Damage Indicators | Screen edges | Red flash | Directional red tint indicating damage source direction |

### 15.2 HUD Color Scheme

- Primary HUD color: Orange (RGB approximately 255, 160, 0).
- HUD elements are semi-transparent and unobtrusive.
- No minimap, objective markers, or waypoints -- navigation is entirely through environmental design and NPC guidance.

### 15.3 Menu System

- **Main Menu**: New Game, Load Game, Multiplayer, Options, Quit.
- **Difficulty Selection**: Easy, Normal, Hard (selected at New Game start; cannot be changed mid-game).
- **Save/Load**: Quick Save (F6), Quick Load (F7), Save menu, Load menu. Saves are unlimited and can be created at any time.
- **Options**: Video (resolution, renderer, brightness), Audio (volume, sound quality), Controls (key bindings, mouse sensitivity), Game.

---

## 16. Difficulty Settings

The game's difficulty affects enemy health, enemy damage, item healing values, and some AI behaviors.

### 16.1 Difficulty Multiplier Summary

| Category | Easy | Normal | Hard |
|---|---|---|---|
| Enemy Health | Low | Standard | High (often 1.5-2x) |
| Enemy Damage | Low | Standard | High |
| Health Kit Value | 15 | 15 | 10 |
| Battery Value | 15 | 15 | 10 |
| Health Charger Capacity | 50 | 40 | 25 |
| Suit Charger Capacity | 75 | 50 | 35 |
| Player Weapon Damage | Same across all difficulties (most weapons) |
| Assassin Cloaking | No | No | Yes |

---

## 17. The G-Man

- **Role**: Mysterious observer and orchestrator who appears throughout the game in otherwise inaccessible locations.
- **Appearances**: Every chapter contains at least one G-Man sighting, typically behind glass, on a distant platform, boarding a vehicle, or walking through a sealed area.
- **Behavior**: Cannot be interacted with, shot, or reached during the game. Simply observes and departs.
- **Dialogue**: Speaks only during the Endgame epilogue, delivering a monologue to the player.
- **Visual Design**: Blue suit, red tie, pale complexion, carrying a briefcase. Distinctly out of place in the industrial/military/alien environments.
- **Narrative Function**: Creates ongoing mystery and the sense of being watched/manipulated throughout the entire game.

---

## 18. Damage Model and Combat Formulas

### 18.1 Core Damage Formula

```
raw_damage = weapon_base_damage * hitgroup_multiplier
armor_absorbed = raw_damage * 0.8 (if armor > 0 and damage type is not DMG_FALL)
armor_cost = armor_absorbed * 0.5 (armor points consumed)
health_damage = raw_damage - armor_absorbed
```

Where armor reduces incoming damage by approximately 80%, costing armor points at roughly half the absorbed amount.

### 18.2 Hit Group Multipliers

| Hit Group | Multiplier |
|---|---|
| Head | 3.0x |
| Chest | 1.0x |
| Stomach | 1.0x |
| Arm | 1.0x |
| Leg | 1.0x |

### 18.3 Damage Types

| Type Flag | Description | Armor Interaction |
|---|---|---|
| DMG_BULLET | Hitscan weapons (pistol, MP5, shotgun, magnum) | Absorbed by armor |
| DMG_SLASH | Melee attacks (crowbar, zombie claws) | Absorbed by armor |
| DMG_BLAST | Explosions (grenades, RPG, satchels, tripmines) | Absorbed by armor |
| DMG_SHOCK | Electrical damage (Vortigaunt beam, wires) | Absorbed by armor |
| DMG_BURN | Fire/flame damage (Gargantua) | Absorbed by armor |
| DMG_ENERGYBEAM | Energy weapons (Tau Cannon, Gluon Gun) | Absorbed by armor |
| DMG_FALL | Fall damage | Bypasses armor entirely |
| DMG_DROWN | Drowning/oxygen deprivation | Bypasses armor |
| DMG_RADIATION | Radiation exposure | Partially absorbed |
| DMG_ACID | Acid/toxic damage (Bullsquid spit, Gonarch acid) | Absorbed by armor |
| DMG_SONIC | Sound-based damage (Houndeye blast) | Absorbed by armor |

---

## 19. Multiplayer Deathmatch

Half-Life shipped with a built-in deathmatch mode:

- **Modes**: Free-for-all Deathmatch, Team Deathmatch.
- **Maps**: Custom deathmatch maps (Crossfire, Bounce, Stalkyard, Boot Camp, Subtransit, Snarkpit, Undertow, Datacore, Frenzy, Lambda Bunker).
- **All Weapons Available**: All singleplayer weapons spawn on maps.
- **Damage Values**: Deathmatch uses different damage tuning than singleplayer (generally higher damage for some weapons: crowbar 25, Glock 12, MP5 12, shotgun 20/pellet, crossbow 120 scoped / 40 explosive, RPG 120, Gauss 20/200 charged, Egon 25 per tick, hornet 10, snark 10, grenade/satchel/tripmine 100, satchel 150).
- **Respawn System**: Players respawn at random spawn points with default weapons.
- **Networking**: Client-server architecture with configurable tick rate.

---

## 20. Speedrunning and Advanced Movement

### 20.1 Bunny Hopping

- Exploit of the air acceleration system inherited from the Quake engine.
- Performed by: jumping, then strafing (A or D) while moving the mouse in the corresponding direction, and jumping again immediately upon landing.
- In WON versions (pre-Steam, up to v1.1.0.8): uncapped speed up to sv_maxvelocity (2000 units/second).
- In Steam versions: speed capped at 544 units/second; exceeding this resets speed to 320 on next landing.
- Circle-jumping (initial jump with strafe and mouse turn) achieves ~480 units/second in a single jump vs. normal 352 units/second.

### 20.2 Gauss Boosting

- Charging the Tau Cannon secondary fire while aiming at the ground and releasing creates a physics impulse that propels the player.
- Can be combined with bunny hopping for extreme speed.

### 20.3 Object Boosting

- Standing on certain physics objects (crates) and manipulating them can produce unintended vertical or horizontal velocity.

---

## 21. Technical Data Summary Tables

### 21.1 Complete Weapon Ammo Table

| Weapon | Clip Size | Max Reserve | Ammo Type | Shared With |
|---|---|---|---|---|
| Crowbar | N/A | Infinite | N/A | N/A |
| 9mm Glock | 17 | 250 | 9mm | MP5 |
| .357 Magnum | 6 | 36 | .357 | None |
| MP5 | 50 | 250 | 9mm | Glock |
| MP5 Grenade | N/A | 10 | M203 Grenade | None |
| Shotgun | 8 | 125 | Buckshot | None |
| Crossbow | 5 | 50 | Crossbow Bolt | None |
| RPG | 1 | 5 | Rocket | None |
| Tau Cannon | N/A (no clip) | 100 | Uranium Cell | Gluon Gun |
| Gluon Gun | N/A (no clip) | 100 | Uranium Cell | Tau Cannon |
| Hivehand | N/A (regenerates) | 8 (regenerating) | Hornet | None |
| Hand Grenade | N/A | 10 | Grenade | None |
| Satchel Charge | N/A | 5 | Satchel | None |
| Tripmine | N/A | 5 | Tripmine | None |
| Snark | N/A | 15 | Snark | None |

### 21.2 Complete Enemy Health Reference (Normal Difficulty)

| Enemy | HP (Normal) | Primary Attack Damage (Normal) | Classification |
|---|---|---|---|
| Headcrab | 10 | 10 (leap) | Alien |
| Zombie | 50 | 20 (claw) / 40 (double slash) | Mutant |
| Vortigaunt | 30 | 10 (beam) / 10 (claw) | Alien |
| Houndeye | 20 | 15 (sonic blast) | Alien |
| Bullsquid | 40 | 25 (bite) / 10 (spit) / 35 (tail) | Alien |
| Barnacle | ~35 | ~25 (bite) | Alien |
| Ichthyosaur | 200 | 35 (bite) | Alien |
| Alien Grunt | 90 | 5 (hornet) / 20 (punch) | Alien |
| Alien Controller | 60 | 4 (energy ball) / 25 (psychic) | Alien |
| Leech | 2 | 2 (bite) | Alien |
| Snark | 2 | 10 (bite) / 5 (explosion) | Alien |
| HECU Marine | 50 | 5 (9mmAR) / 10 (shotgun pellet) | Human |
| Female Assassin | 50 | 5 (pistol) | Human |
| Apache | 250 | 10 (machine gun) | Vehicle |
| Ceiling Turret | 50 | 10 (bullets) | Mechanical |
| Mini Turret | 40 | 5 (bullets) | Mechanical |
| Sentry Turret | 40 | 4 (bullets) | Mechanical |
| Gargantua | 800 | 30 (stomp) / 5 (flame tick) | Boss |
| Gonarch | ~150 per phase | 60 (stomp) / 120 (acid) | Boss |
| Nihilanth | 800 | 30 (energy sphere) | Final Boss |

### 21.3 Item Pickup Values (Normal Difficulty)

| Item | Value |
|---|---|
| Health Kit (small) | +15 HP |
| Health Charger (wall) | Up to +40 HP |
| Battery | +15 Armor |
| Suit Charger (wall) | Up to +50 Armor |
| Ammo Box (9mm) | +17 rounds |
| Ammo Box (.357) | +6 rounds |
| Ammo Box (MP5 clip) | +50 rounds |
| Ammo Box (buckshot) | +12 shells |
| Ammo Box (crossbow) | +5 bolts |
| Ammo Box (rockets) | +1 rocket |
| Ammo Box (uranium) | +20 cells |
| Ammo Box (M203 grenades) | +2 grenades |
| Snark Nest | +5 snarks |

---

## 22. Friendly NPC Statistics

### 22.1 Scientists

| Property | Value |
|---|---|
| Health | ~20 (Easy), ~20 (Normal), ~20 (Hard) |
| Weapon | None |
| Special Ability | Unlock retinal-scanner doors; heal player (some encounters) |
| Behavior | Follow player when activated; flee from enemies; provide dialogue |

### 22.2 Security Guards (Barney)

| Property | Value |
|---|---|
| Health | ~35-50 |
| Weapon | 9mm Glock Pistol |
| Damage Output | 8 per shot (same as player Glock) |
| Behavior | Follow player when activated; engage hostile NPCs; take cover; provide dialogue and ammo |

---

## 23. Save System and Progression

- **Save Anywhere**: The player can save at any point during gameplay via Quick Save (F6) or the Save menu.
- **Quick Load**: F7 instantly loads the last quick save.
- **Autosaves**: Created automatically at level transitions between maps.
- **Chapter-Based Progression**: The game is divided into chapters spanning multiple BSP maps. New Game allows starting from the beginning only; completed chapters are not selectable from a menu in the original release.
- **Persistent State**: All player state (health, armor, weapons, ammo, key items) carries across level transitions within a continuous playthrough.
- **Death**: On death, the player sees a "GAME OVER" screen and can load a saved game.

---

## 24. Environmental Storytelling Details

- **No Text Logs or Audio Diaries**: All story information comes from direct NPC speech, overheard conversations, visual environmental details, and the HEV suit voice.
- **Visual Narrative Cues**: Dead scientists, blood trails, alien growth on walls, military supply caches, body bags, equipment destruction -- all communicate what happened in each area before the player arrives.
- **Radio Transmissions**: The player overhears military radio communications revealing their true hostile intent and operational status.
- **G-Man Sightings**: Recurring visual motif creating ongoing mystery through simple observational encounters.
- **Xen Discoveries**: Dead HEV-suited researchers found on Xen confirm previous failed expeditions.
- **Graffiti and Signage**: Facility signs, warning labels, and sector markings aid navigation and world-building.

---

## 25. Performance and System Requirements (Original 1998 Release)

| Requirement | Minimum | Recommended |
|---|---|---|
| CPU | Pentium 133 MHz | Pentium II 233+ MHz |
| RAM | 24 MB | 32+ MB |
| GPU | SVGA compatible | 3D accelerator (OpenGL) |
| Storage | 400 MB | 600+ MB |
| OS | Windows 95/98/NT 4.0 | Windows 95/98 |
| Audio | Windows-compatible sound card | Sound Blaster compatible |
| Input | Keyboard + Mouse | Keyboard + Mouse |

---

*This specification covers the original retail release of Half-Life (version 1.0, November 1998) for PC. Expansion packs (Opposing Force, Blue Shift), the PlayStation 2 port, and later updates/patches may contain additional content or balance changes not reflected in this document. All numeric values are sourced from the game's skill.cfg configuration system, the official Valve SDK source code (github.com/ValveSoftware/halflife), and community-verified references.*
