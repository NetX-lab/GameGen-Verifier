# 12_metal_gear - Metal Gear (MSX2, 1987 - Faithful Recreation)

## 1. Game Overview

- **Reference**: Metal Gear, designed and directed by Hideo Kojima, developed and published by Konami for the MSX2 home computer. Originally released July 13, 1987 (Japan). This specification targets the original MSX2 version (product code RC750), not the NES port.
- **Genre**: Top-Down Action-Adventure / Stealth
- **Core Fantasy**: As FOXHOUND rookie operative Solid Snake, infiltrate the fortified nation of Outer Heaven to rescue captured agent Gray Fox, locate and destroy the bipedal nuclear-armed walking tank "Metal Gear TX-55," and uncover the identity of the enemy commander -- your own commanding officer, Big Boss.
- **Operation Codename**: Intrude N313
- **Presentation**: Top-down 2D view with screen-by-screen (flip-screen) traversal. No scrolling; each screen is a discrete room/area. The player navigates through three multi-floor buildings separated by outdoor desert terrain.
- **Target Session**: Full playthrough 1.5-3 hours (first time); speedrun under 45 minutes.
- **Skill Curve**: Stealth-focused design punishes direct combat; mastery comes from memorizing patrol routes, item locations, card key door assignments, and boss patterns.

---

## 2. Technical Foundation

| Parameter | Value |
|---|---|
| Platform | MSX2 home computer |
| Display resolution | 256 x 212 pixels (Screen Mode 5 / GRAPHIC4) |
| Color depth | 16 simultaneous colors from 512-color palette (MSX2 V9938 VDP) |
| Sprite system | Hardware sprites, 16x16 pixel max per sprite; 2 sprites composited per character via OR-color technique |
| Max sprites per scanline | 8 hardware sprites (4 composite characters); excess causes flicker |
| Max sprites on screen | 32 hardware sprites (16 composite characters) |
| Frame rate | ~60 Hz (NTSC) / ~50 Hz (PAL) |
| Sound hardware | AY-3-8910 PSG (3 square-wave channels + 1 noise channel) |
| Music composer | Konami Kukeiha Club (Iku Mizutani, Shigehiro Takenouchi, Motoaki Furukawa) |
| Screen transition | Flip-screen; no scrolling. Moving to screen edge loads adjacent screen. |
| Coordinate system | Tile-based grid; each screen is an 8x6 metatile arrangement (32x32 pixel metatiles) |
| Total screens/rooms | ~251 room definitions (includes variants based on entry direction) |
| Save system | Data save to tape drive or Game Master II cartridge; up to 64 save slots |
| Input | MSX keyboard or joystick; D-pad + 2 action buttons |
| Cartridge size | 128 KB ROM (1 Mbit) |

---

## 3. Controls

| Input | MSX Keyboard | Function |
|---|---|---|
| Move | Arrow Keys | Move Snake in 4 cardinal directions |
| Punch / Action | N key / Button 1 | Melee punch; advance dialog; interact |
| Fire Weapon | Space bar / Button 2 | Fire currently equipped weapon in facing direction |
| Weapon Select | F2 | Open weapon inventory submenu |
| Equipment Select | F3 | Open equipment inventory submenu |
| Transceiver | F4 | Open radio transceiver screen |
| Pause | F1 | Pause game |
| Save | F5 (while paused) | Save current game state |

---

## 4. Core Stealth Mechanics

### 4.1 Stealth Philosophy

The game's defining design principle is avoidance over combat. Snake begins the mission completely unarmed and must scavenge all weapons and equipment from within Outer Heaven. The MSX2 hardware limitation on simultaneous sprites reinforced this design: rather than render many bullets and enemies, the game rewards careful navigation around enemy patrol routes.

### 4.2 Movement & Detection

| Mechanic | Detail |
|---|---|
| Movement speed | Constant 4-directional walk; no run/crouch/crawl |
| Detection method | Proximity and facing-direction based; guards detect Snake when he enters their forward-facing detection zone |
| Vision model | Simple directional check (not cone-shaped FOV); guards detect Snake if he is in front of them along their facing axis within detection range |
| Detection range | Approximately 3-5 tiles in facing direction depending on guard type |
| Noise detection | Firing an unsuppressed weapon alerts all guards on the current screen |
| Camera detection | Security cameras rotate and detect Snake within their sweep arc; instant alert on detection |
| IR sensor detection | Infrared laser beams trigger alert when Snake walks through them |
| Screen-based AI | Guards reset positions when Snake leaves and re-enters a screen; guard placement may change depending on which edge Snake enters from |

### 4.3 Cardboard Box

| Property | Detail |
|---|---|
| Type | Equipment item |
| Effect | When equipped and Snake is stationary, guards walking by will ignore him; security cameras are also bypassed |
| Limitation | Moving while in the box may still trigger detection; guards already in alert mode will not be fooled |
| Location | Found in Building 1, 1F |

### 4.4 Enemy Uniform

| Property | Detail |
|---|---|
| Type | Equipment item |
| Effect | Allows Snake to walk past certain guard checkpoints without triggering alert |
| Location | Acquired after defeating Shoot Gunner (Building 1, B1 area) |

### 4.5 Silencer / Suppressor

| Property | Detail |
|---|---|
| Type | Equipment item (auto-applied when in inventory) |
| Effect | Suppresses gunshot sounds from Handgun and Submachine Gun; prevents noise-based alerts when firing |
| Location | Building 1, 3F (acquired by defeating four mercenaries) |
| Durability | Permanent once acquired; does not degrade |

---

## 5. Alert System

The alert system has distinct phases that govern enemy behavior across the entire game.

### 5.1 Alert Phases

| Phase | Indicator | Trigger | Enemy Behavior | Resolution |
|---|---|---|---|---|
| **Normal (Infiltration)** | Radar operational; white dots show enemies | Default state | Guards follow fixed patrol routes; do not pursue Snake | N/A -- default state |
| **Alert (!)** | Single red exclamation mark (!) above detecting enemy; radar jammed | Guard spots Snake directly; unsuppressed weapon fire | Guards on current screen attack; no cross-screen pursuit | Defeated all alerted guards on screen, OR leave the screen (transition to adjacent screen) |
| **Red Alert (!!)** | Double red exclamation marks (!!) in yellow speech bubble; radar fully jammed | Camera detection; IR sensor triggered; simultaneous multi-guard detection | Reinforcement guards spawn and pursue Snake across screens; continuous spawning | Kill a set number of reinforcement guards (~8-12), OR enter an elevator, OR reach a different floor/building |
| **Evasion / Caution** | Radar partially scrambled | Transition from Alert/Red Alert after conditions met | Guards return to patrol routes; heightened awareness briefly | Timer expires (several seconds); returns to Normal |

### 5.2 Alert Rules

| Rule | Detail |
|---|---|
| Mandatory alerts | 8 scripted/unavoidable alerts occur during a normal playthrough (e.g., Hind-D encounter, Building 2 roof) |
| Elevator escape | Entering an elevator immediately cancels any active alert |
| Floor transition | Moving to a different floor cancels alert |
| Building transition | Moving to a different building cancels alert |
| Radar behavior during alert | Radar display is scrambled (shows static); enemy positions not visible |
| Radar during evasion | Radar partially recovers; enemies shown intermittently |

---

## 6. Weapons

All weapons must be found within Outer Heaven. Snake starts completely unarmed.

### 6.1 Weapon Table

| Weapon | Description | Ammo Type | Use | Location Found |
|---|---|---|---|---|
| **Bare Fists (Punch)** | Default melee attack; short range; 1 tile forward | Unlimited | Kill guards at close range; break certain walls to find weak spots; advance dialog | Always available |
| **Handgun (Beretta M92F)** | Semi-automatic pistol; fires one bullet per press; moderate range | Handgun Bullets | Primary ranged weapon; can be suppressed with Silencer | Building 1, 1F (western truck area) |
| **Submachine Gun** | Automatic fire; rapid bullets in facing direction | SMG Bullets | Rapid-fire combat; can be suppressed with Silencer | Building 1, 1F (west room) |
| **Grenade Launcher (M79)** | Launches grenades in an arc; passes over low obstacles | Grenades | Anti-vehicle; boss fights (Hind-D, Bulldozer) | Building 1, 3F |
| **Rocket Launcher** | Fires straight-line rockets; high damage per hit | Rockets | Boss fights (Arnolds, Big Boss); requires 4-star rank to receive from Jennifer | Delivered by Jennifer via radio after reaching 4-star rank |
| **Remote Controlled Missiles (RC Missiles)** | Player-guided missile; Snake cannot move during guidance | RC Missiles | Destroy power boxes to disable electrified floors; attack bosses from cover (Shoot Gunner, Machine Gun Kid) | Building 1, B1 |
| **Plastic Explosives (C4)** | Timer-detonated bomb; place and retreat; one per screen | Plastic Explosives | Destroy walls to open passages; destroy TX-55 Metal Gear (16 charges required) | Various locations; Building 2 exit area |
| **Land Mines** | Proximity-triggered explosive placed on ground; cannot be retrieved once placed | Mines | Anti-vehicle (Tank boss -- 11 mines needed); area denial | Building 1, 1F (eastern truck) |

### 6.2 Ammo Capacity by Rank

| Weapon | 1 Star | 2 Stars | 3 Stars | 4 Stars |
|---|---|---|---|---|
| Handgun Bullets | 50 | 100 | 200 | 300 |
| SMG Bullets | 50 | 100 | 200 | 300 |
| Grenades | 15 | 30 | 60 | 90 |
| Rockets | 5 | 10 | 20 | 30 |
| RC Missiles | 5 | 10 | 15 | 20 |
| Plastic Explosives | 5 | 10 | 15 | 20 |
| Land Mines | 5 | 10 | 15 | 20 |

---

## 7. Equipment & Items

Equipment is selected via the F3 menu and provides passive or active effects.

### 7.1 Equipment Table

| Equipment | Effect | Location Found |
|---|---|---|
| **Binoculars** | View adjacent screen in outdoor/open areas using directional keys | Building 1, 1F (eastern truck) |
| **Gas Mask** | Prevents poison gas damage in gas-filled rooms | Building 1, 1F (locked room with sleeping guard) |
| **Body Armor** | Reduces damage taken from enemy attacks; limited protection against lasers | Building 1, 3F |
| **Bomb Blast Suit** | Protects against wind hazards on Building 1 Roof; required to traverse rooftop | Building 1, 3F |
| **Cardboard Box** | Stealth item; guards and cameras ignore stationary Snake when equipped | Building 1, 1F |
| **Enemy Uniform** | Allows passage through certain guard checkpoints without detection | Building 1, B1 (after Shoot Gunner) |
| **IR Goggles (Infrared Goggles)** | Reveals invisible infrared laser beams on floors with IR traps | Building 1, B2 |
| **Mine Detector** | Reveals location of hidden land mines on the ground | Desert area |
| **Compass** | Required for desert crossing; indicates direction | Desert area (Building 1 exit) |
| **Flashlight** | Illuminates dark underground tunnel areas | Underground tunnel between buildings |
| **Antenna** | Extends transceiver range; required to contact certain radio frequencies | Building 2, 1F |
| **Oxygen Tanks (O2 Tanks)** | Allows Snake to swim through underwater passages without drowning | Building 3, B100 area |
| **Parachute** | Enables safe descent from Building 1 Roof after Hind-D boss fight | Building 1, Roof |
| **Silencer (Suppressor)** | Suppresses gunshot noise from Handgun and SMG; prevents noise alerts | Building 1, 3F |
| **Transmitter (Enemy Bug)** | Hidden tracking device planted on Snake; must be discarded to prevent guards from tracking player | Found automatically; must be dropped |

### 7.2 Consumable Items

| Item | Effect | Max Capacity (by Rank) |
|---|---|---|
| **Rations** | Fully restores Snake's LIFE gauge when manually used from equipment menu. Does NOT auto-trigger on death (unlike Metal Gear 2). | 1-Star: 3 / 2-Star: 6 / 3-Star: 9 / 4-Star: 12 |
| **Antidote** | Cures scorpion poison inflicted in desert areas | Consumable; found in desert region |
| **Cigarettes** | Extend the self-destruct escape timer by 1000 seconds during the endgame sequence | Found in Building 1 |

---

## 8. Enemy AI System

### 8.1 Enemy Types

| Enemy Type | Behavior | Threat Level | Notes |
|---|---|---|---|
| **Standard Guard (Soldier)** | Patrols fixed route; faces one direction while walking; turns at patrol endpoints | Low-Medium | Defeated by 1 punch or 1 handgun bullet; alerts on sight or gunshot noise |
| **Sleeping Guard** | Stationary; asleep; wakes if Snake makes noise nearby (weapon fire, close proximity) | Low | Can be bypassed silently; killing is optional |
| **Rocket Guard** | Stationary or patrolling; fires rockets at Snake; cannot be fooled by Cardboard Box | High | Must be eliminated; cannot evade |
| **Attack Dog (German Shepherd)** | Aggressive pursuit on sight; fast movement speed | Medium-High | Found in Building 1 courtyard and basement; must be shot |
| **Security Camera** | Rotates in fixed arc; triggers Red Alert (!!) on detection | Variable | Can be destroyed with weapons; present in Buildings 1-3 |
| **Infrared Sensor (IR Beam)** | Invisible laser tripwire across corridors; triggers Red Alert (!!) | High | Invisible without IR Goggles; cannot be destroyed |
| **Reinforcement Soldiers** | Spawn during Red Alert; pursue Snake across screens | High | Appear in waves; killing enough (~8-12) or fleeing to elevator/new floor ends pursuit |

### 8.2 Guard Patrol AI

| Behavior | Detail |
|---|---|
| Patrol pattern | Fixed linear routes (horizontal or vertical); guard walks back and forth along set path |
| Turn behavior | Guard pauses briefly at each endpoint before reversing direction |
| Entry-dependent placement | Guard starting positions on a screen may change depending on which edge Snake enters from |
| Re-entry reset | Leaving a screen and re-entering resets guard positions to default |
| Alert behavior (!) | Guard stops patrol; fires weapon toward Snake; does not pursue across screen edges |
| Red Alert behavior (!!) | Reinforcement guards spawn from screen edges; run toward Snake; pursue across screen transitions |
| Item respawn | Ammo pickups and rations in rooms respawn when Snake leaves and re-enters the screen |

---

## 9. Building Layout & Progression

### 9.1 Outer Heaven Fortress Overview

The fortress consists of three main buildings connected by outdoor desert terrain. Progression is gated by card keys (Cards 1-8), specific equipment, and rank requirements.

```
[Building 1] ---(Desert)--- [Building 2] ---(Scorpion Desert)--- [Building 3]
```

### 9.2 Building 1

| Floor | Color Code | Key Features |
|---|---|---|
| **1F** | Red ground | Starting area; truck hangar (west) with weapons/items; guard patrols; inner courtyard with dogs; two elevators (left: access to 1F/3F; right: access to all floors + roof) |
| **2F** | Blue ground | IR laser-trapped corridors (require IR Goggles); POW rescue rooms; Machine Gun Kid boss; elevator access |
| **3F** | Dark gray ground | Security cameras (trigger Red Alert); gas-filled rooms (require Gas Mask); electrified floor (destroy power box with RC Missile); multiple card keys and POWs; weapons storage area |
| **B1 (Basement 1)** | Dark green / brick | Main prison block; Shoot Gunner boss; attack dogs; Gray Fox's cell (must get captured to access); spiral passages with traps |
| **B2 (Basement 2)** | Dark green / brick | Multiple POW locations; laser floor traps; IR Goggles acquisition |
| **Roof** | Open sky | Wind hazards (require Bomb Blast Suit); shaky bridges; rocket guards; Hind-D helicopter boss; Parachute for descent |

### 9.3 Desert

| Section | Features |
|---|---|
| **Desert (Building 1 to 2)** | Open terrain; Compass required for navigation; scorpions inflict poison (use Antidote); quicksand pits (instant death on full submersion); Tank boss encounter |
| **Scorpion Desert (Building 2 to 3)** | More scorpions; Mine Detector recommended; hidden mines |

### 9.4 Building 2

| Floor | Key Features |
|---|---|
| **1F** | Drainage systems; laser floors; guard patrols; water passages; Bulldozer boss; Coward Duck boss (with POW human shields) |
| **2F** | Arnolds (Bloody Brad) boss encounter; POW rescues; Dr. Pettrovich Madnar location; Card key acquisition |
| **B1 (Basement 1)** | Gas rooms; impostor Dr. Madnar trap; Fire Trooper boss; Card 6; water drainage passages; Ellen rescue |

### 9.5 Building 3

| Floor | Key Features |
|---|---|
| **1F** | Heavy guard presence; pit traps; Plastic Explosive wall-breach required; elevator to B100 |
| **B100** | Final area; laser-shooting security cameras (shoot lasers, not alerts); Oxygen Tanks; Mine field; TX-55 Metal Gear boss; Big Boss final encounter; self-destruct escape sequence |

### 9.6 Progression Flow

1. Building 1, 1F -- Acquire initial weapons and Card 1
2. Building 1, B1 -- Get captured; find Gray Fox; learn about Metal Gear
3. Building 1, B2 -- Obtain IR Goggles
4. Building 1, 2F-3F -- Acquire Gas Mask, Silencer, Body Armor, Bomb Blast Suit, higher card keys
5. Building 1, Roof -- Defeat Hind-D; parachute to desert
6. Desert -- Defeat Tank; cross to Building 2
7. Building 2, 1F-2F -- Find Dr. Madnar (beware impostor); rescue Ellen
8. Building 2, B1 -- Defeat Fire Trooper; obtain Card 6
9. Building 2, 2F -- Defeat Arnolds; obtain Card 7
10. Building 2, 1F -- Defeat Coward Duck; obtain Card 8
11. Building 3, 1F -- Breach walls; descend to B100
12. Building 3, B100 -- Destroy TX-55 Metal Gear with 16 Plastic Explosives
13. Building 3, B100 -- Defeat Big Boss; escape during self-destruct countdown

---

## 10. Boss Encounters

### 10.1 Boss Table

| # | Boss Name | Alias | Location | Weapon Required | Hits to Defeat | Strategy |
|---|---|---|---|---|---|---|
| 1 | **Shoot Gunner** | Shotmaker | Building 1, B1 | Handgun or RC Missiles | 10 Handgun hits OR 4 RC Missiles | Rush toward him while firing rapidly; he fires shotgun blasts (smoke-like projectiles). Use crates as cover with RC Missiles for safer approach. |
| 2 | **Machine Gun Kid** | -- | Building 1, 2F | Handgun or SMG | 10 Handgun hits | Use walls as cover; attack from flanks. He fires rapid bursts. SMG works well for trading fire. |
| 3 | **Hind-D** | Helicopter | Building 1, Roof | Grenade Launcher | ~20 Grenade hits | Position Snake where helicopter gunfire cannot reach; lob grenades at cockpit. Equip Body Armor for damage reduction. |
| 4 | **Tank** | -- | Desert | Land Mines | 11 Mines | Cannot be damaged by bullets or explosives; touching it is instant death. Wait for tank to reverse, place mines in its path. Tank runs over mines for damage. |
| 5 | **Bulldozer** | -- | Building 2, 1F | Grenade Launcher | 8 Grenades | Fire two grenades, retreat; repeat. Watch for charging pattern. Bulldozer accelerates toward Snake periodically. |
| 6 | **Fire Trooper** | -- | Building 2, B1 | Handgun | 15 Handgun hits | Approach along north wall; fire when trooper pauses between flamethrower bursts. He sweeps fire in arcs. |
| 7 | **Bloody Brad** | The Arnolds (TX-11 Androids) | Building 2, 2F | Rocket Launcher | 4 Rockets each (2 androids = 8 total) | Two identical android enemies. Requires Rocket Launcher (need 4-star rank). Position where enemies cannot retaliate and fire rockets. |
| 8 | **Coward Duck** | Dirty Duck | Building 2, 1F | Handgun or Rocket Launcher | 10 Handgun hits OR 2 Rockets | Most complex boss: uses 3 POW hostages as human shields. Center pit means instant death. Must achieve precise angle to hit Duck without killing POWs. Move to left wall, position north of Duck. Killing any POW fails the game. |
| 9 | **TX-55 Metal Gear** | Metal Gear | Building 3, B100 | Plastic Explosives | 16 Plastic Explosive charges | Not a combat boss -- puzzle boss. Place C4 on Metal Gear's feet in exact sequence provided by Dr. Madnar. Laser cameras fire at Snake during placement. Use Rations for healing. |
| 10 | **Big Boss** | -- | Building 3, B100 | Rocket Launcher | 4-5 Rockets | Final boss. Extremely fast movement. Hide behind southwest crate; emerge to fire rockets. Opening weapon select screen resets Big Boss position (exploit). |

### 10.2 TX-55 Plastic Explosive Placement Sequence

Dr. Madnar provides the following sequence for placing C4 on Metal Gear's left (L) and right (R) feet:

```
R, R, L, R, L, L, R, L, L, R, R, L, R, L, R, R
```

Total: 16 charges. Place one at a time; retreat to corner until detonation; return for next placement.

---

## 11. Radio Transceiver System

### 11.1 Overview

The transceiver (accessed via F4) allows Snake to communicate with support contacts. The player manually tunes to a frequency number using the transceiver interface. Contacts provide mission guidance, hints, story exposition, and critical gameplay information.

### 11.2 Radio Contacts

| Contact | Frequency | Role | How Obtained |
|---|---|---|---|
| **Big Boss** | 120.85 | FOXHOUND commander; provides general mission guidance, weapon/item descriptions, tactical advice | Available from start (given in mission briefing) |
| **Schneider** | 120.79 | Resistance leader inside Outer Heaven; provides navigation hints, building layout intel, warns of traps | Discovered by tuning transceiver 2 screens north of start; incoming transmission reveals frequency |
| **Diane** | 120.33 | Enemy intelligence specialist; provides info on boss weaknesses and strategies | Frequency obtained from rescued POW |
| **Jennifer** | 120.48 | Resistance operative; delivers the Rocket Launcher when Snake reaches 4-star rank; provides key card hints | Frequency obtained from rescued POW; must listen to full transmission without skipping |

### 11.3 Radio Rules

| Rule | Detail |
|---|---|
| Context-sensitive calls | Contacts provide different information depending on Snake's current location and game progress |
| Automatic transmissions | Some transmissions trigger automatically when Snake enters specific areas |
| Antenna requirement | The Antenna equipment item (Building 2, 1F) is required to contact certain frequencies in certain areas |
| Jennifer delivery | Jennifer will only deliver the Rocket Launcher if Snake has achieved 4-star rank; otherwise she does not respond |
| Story exposition | Big Boss subtly misdirects Snake throughout the game (foreshadowing the twist) |

---

## 12. Health & Lives System

### 12.1 LIFE Gauge

| Parameter | Value |
|---|---|
| Display | Horizontal LIFE bar in the HUD area |
| Starting health | Base amount at 1-star rank; increases with each rank |
| Maximum health | Increases at each rank promotion (every 5 POW rescues) |
| Health at 1-Star | Base health bar (shortest) |
| Health at 4-Stars | Maximum health bar (approximately 4x base length) |
| Damage sources | Enemy bullets, melee attacks, environmental hazards (gas, electricity, fire, mines, scorpion poison) |
| Instant death | Touching Tank boss; falling into pits; full submersion in quicksand; rolling cylinder trap |
| Healing | Rations (manual use from equipment menu; fully restores LIFE bar) |
| No auto-ration | Unlike Metal Gear 2, rations do NOT auto-trigger when health reaches zero |

### 12.2 Continue System

| Parameter | Value |
|---|---|
| Lives | Unlimited continues |
| On death | Snake respawns at the beginning of the current building/major area |
| Inventory on death | All items, weapons, and ammo are retained |
| Rank on death | Rank is retained |
| Continue count | Tracked for final score/rank evaluation |
| Save system | Manual save via F5 (while paused); load from save menu. Up to 64 save slots on MSX2. |

---

## 13. Card Key System

### 13.1 Overview

Eight numbered card keys (Card 1 through Card 8) gate progression throughout Outer Heaven. Each locked door requires a specific card number. There is no in-game indicator showing which card opens which door -- the player must try each card or memorize assignments.

### 13.2 Card Key Table

| Card | Primary Area of Use | Acquisition Location |
|---|---|---|
| **Card 1** | Building 1, 1F basic doors | Building 1, 1F (early area; found in truck/room) |
| **Card 2** | Building 1, 1F-B1 progression doors | Building 1, 1F (inside room opened by Card 1) |
| **Card 3** | Building 1, B1-B2 deeper areas | Building 1, B1 (after Shoot Gunner area) |
| **Card 4** | Building 1, 3F and desert transition | Building 1, 2F-3F area |
| **Card 5** | Building 2 upper level doors | Building 1, 3F / Building 2, 1F |
| **Card 6** | Building 2 advanced areas | Building 2, B1 (after Fire Trooper) |
| **Card 7** | Building 3 access doors | Building 2, 2F (after defeating Arnolds) |
| **Card 8** | Final POW rescue; Building 3 deepest areas | Building 2, 1F (after defeating Coward Duck) |

### 13.3 Card Key Mechanics

| Rule | Detail |
|---|---|
| Equipping | Must be equipped as current equipment item (F3 menu) to open matching doors |
| Swapping | Only one card can be equipped at a time; frequent swapping required |
| No visual indicator | Doors do not display which card they require; trial-and-error or memorization |
| Permanent | Cards are never lost or consumed once acquired |
| Stacking | All 8 cards are held simultaneously in inventory |

---

## 14. POW / Hostage Rescue System

### 14.1 Overview

Prisoners of War (POWs) are scattered throughout all three buildings. Rescuing them is mandatory for rank advancement and game completion.

### 14.2 Mechanics

| Mechanic | Detail |
|---|---|
| Rescue method | Touch/walk into a POW to rescue them; they follow Snake briefly then disappear |
| Rank promotion | Every 5 POWs rescued increases Snake's rank by 1 star |
| Maximum rank | 4 stars (requires 20 POW rescues) |
| Rank demotion | Killing ANY POW demotes Snake by 1 star |
| Game-ending POWs | Killing certain key POWs (Ellen, Jennifer's brother) makes the game unwinnable |
| 4-star requirement | 4-star rank is REQUIRED to obtain the Rocket Launcher from Jennifer, which is REQUIRED to defeat the Arnolds and Big Boss. Without 4 stars, the game cannot be completed. |
| POW intel | Some rescued POWs provide radio frequency numbers, hints, or story information |
| Key POWs | Gray Fox (provides Metal Gear intel); Dr. Pettrovich Madnar (provides TX-55 destruction sequence); Ellen (Madnar's daughter; must rescue for Madnar to cooperate) |

### 14.3 Special POW Encounters

| POW | Location | Significance |
|---|---|---|
| **Gray Fox** | Building 1, B1 (secret cell; must get captured) | Reveals Metal Gear's existence; instructs Snake to find Dr. Madnar |
| **Dr. Pettrovich Madnar** | Building 2, 2F (beware impostor in B1) | Creator of Metal Gear; provides C4 placement sequence for TX-55 destruction |
| **Ellen** | Building 2, B1 (basement) | Madnar's daughter; must rescue her before Madnar cooperates |
| **Impostor Madnar** | Building 2, B1 | Trap; fake Dr. Madnar who triggers ambush |

---

## 15. Rank / Class System

### 15.1 Rank Progression

| Rank | Stars | POWs Required | Effects |
|---|---|---|---|
| **1 Star** | * | Starting rank | Base health; base ammo capacity |
| **2 Stars** | ** | 5 POWs rescued | Health bar extended; ammo capacity doubled |
| **3 Stars** | *** | 10 POWs rescued | Health bar extended further; ammo capacity increased |
| **4 Stars** | **** | 20 POWs rescued | Maximum health bar; maximum ammo capacity; Rocket Launcher unlocked via Jennifer |

### 15.2 End-Game Scoring / Codename

The game evaluates performance at the end screen based on multiple criteria:

| Criterion | Big Boss Rank Requirement |
|---|---|
| Difficulty | Original (not Easy) |
| Play Time | Under 45 minutes (44:59 or less) |
| Continues Used | 0 |
| Alerts Triggered | 8 or fewer (8 are unavoidable/mandatory) |
| Enemies Killed | 0 (pacifist run) |
| Rations Used | 1 or fewer |
| Special Items Used | None |

---

## 16. Environmental Hazards & Traps

| Hazard | Effect | Countermeasure | Location |
|---|---|---|---|
| **Poison Gas Rooms** | Continuous health drain while in room | Gas Mask (equipment) | Building 1, 3F; Building 2, B1 |
| **Electrified Floor** | Continuous health drain while walking on electrified tiles | Destroy power box with RC Missile to disable | Building 1, 3F |
| **Infrared Laser Beams** | Trigger Red Alert (!!) when walked through; invisible by default | IR Goggles reveal beams; walk between them | Building 1, 2F; Building 2 |
| **Pit Traps (Pitfalls)** | Holes open in floor; falling in causes death | Run away when pit starts forming; let it fully expand then navigate around | Building 3, 1F; various |
| **Rolling Cylinder** | Continuously moving obstacle; instant death on contact | Time movement to pass when cylinder is at far end of travel | Building 1, B1 |
| **Quicksand** | Snake sinks progressively; complete submersion = death | Move through quickly; avoid stopping in sand | Desert areas |
| **Scorpion Poison** | Scorpions in desert inflict poison; continuous health drain | Antidote item cures poison | Desert between buildings |
| **Wind (Rooftop)** | Strong wind pushes Snake off building edges | Bomb Blast Suit negates wind effects | Building 1, Roof |
| **Land Mines (Enemy)** | Hidden mines in ground; explode on proximity | Mine Detector reveals mine positions | Desert; Building 3, B100 |
| **Laser Cameras (B100)** | Security cameras in Building 3 B100 fire laser beams rather than triggering alerts | Avoid beam paths; use Rations to heal through damage | Building 3, B100 (TX-55 area) |

---

## 17. Audio Design

### 17.1 Sound Hardware

| Component | Specification |
|---|---|
| Chip | AY-3-8910 PSG (Programmable Sound Generator) |
| Channels | 3 square-wave tone channels + 1 noise channel |
| Output | Mono |
| Note | The original Metal Gear does NOT use the Konami SCC expansion chip (SCC was used in later Konami MSX2 titles such as Metal Gear 2: Solid Snake) |

### 17.2 Soundtrack

| Track | Context |
|---|---|
| **Title** | Title screen music |
| **Operation Intrude N313** | Opening/mission briefing theme |
| **Theme of Tara** | Main gameplay theme; plays during infiltration in Building 1 |
| **Red Alert (!)** | Plays during Alert phase when guards detect Snake |
| **Sneaking Mission** | Alternate infiltration theme for later buildings |
| **Mercenary** | Boss encounter theme |
| **TX-55 Metal Gear** | Plays during the TX-55 Metal Gear boss encounter |
| **Escape -- Beyond Big Boss** | Self-destruct escape sequence theme |
| **Return of Fox Hounder** | Ending/credits theme |
| **Just Another Dead Soldier** | Game Over screen music |
| **Red Alert (Security Camera)** | Variant alert theme triggered by camera detection |

### 17.3 Sound Effects

| Effect | Trigger |
|---|---|
| Gunshot | Firing Handgun or SMG (suppressed version when Silencer equipped) |
| Explosion | Grenade, Rocket, Plastic Explosive, or Mine detonation |
| Alert chime | (!) exclamation point detection |
| Red Alert siren | (!!) double exclamation detection |
| Punch hit | Successful melee strike |
| Door open | Card key successfully opens door |
| Item pickup | Collecting weapon, ammo, equipment, or key item |
| Radio static | Opening transceiver; tuning frequencies |
| Damage hit | Snake takes damage |
| Boss defeat | Boss enemy destroyed |
| Death | Snake's LIFE reaches zero |

---

## 18. UI Layout

### 18.1 HUD Elements

The HUD occupies a panel to the right of the gameplay area (or below, depending on screen layout). The game viewport and HUD share the 256x212 pixel screen.

| HUD Element | Position | Description |
|---|---|---|
| **LIFE Gauge** | Top of HUD panel | Horizontal bar showing Snake's current health; length increases with rank |
| **Weapon Icon** | Below LIFE gauge | Shows currently equipped weapon sprite; empty if no weapon selected |
| **Equipment Icon** | Below weapon icon | Shows currently equipped equipment sprite; empty if no equipment selected |
| **Ammo Counter** | Adjacent to weapon icon | Numeric count of current weapon's remaining ammunition |
| **Radar / Map** | Center of HUD panel | 3x3 grid showing current screen (center) and 8 adjacent screens; Snake shown as red/blinking dot; enemies shown as white dots |
| **Class Rank** | Lower portion of HUD | Star display showing current rank (1-4 stars) |

### 18.2 Radar Behavior

| State | Radar Display |
|---|---|
| **Normal (Infiltration)** | Full radar operational; red dot = Snake; white dots = enemies; layout visible |
| **Alert (!)** | Radar scrambled; static/noise replaces map display |
| **Red Alert (!!)** | Radar fully jammed; complete static |
| **Evasion** | Radar partially recovers; intermittent enemy display |
| **Indoor rooms** | Radar shows room layout with door positions |
| **Boss rooms** | Radar may be disabled or show simplified layout |

### 18.3 Menu Screens

| Screen | Access | Content |
|---|---|---|
| **Weapon Select** | F2 | Grid of all acquired weapons with ammo counts; select to equip; select current weapon to unequip |
| **Equipment Select** | F3 | Grid of all acquired equipment items with quantities (for consumables); select to equip |
| **Transceiver** | F4 | Frequency dial interface; tune to contact frequency; call button to initiate radio conversation |
| **Pause** | F1 | Game paused; access save (F5) |

---

## 19. Story Summary

### 19.1 Setting

The year is 1995. A fortified military nation called Outer Heaven, located 200 km north of the fictional Galzburg in South Africa, is constructing a weapon of mass destruction. FOXHOUND, a special forces unit under the command of legendary soldier Big Boss, sends operative Gray Fox to infiltrate. Gray Fox's last transmission before going silent is two words: "METAL GEAR."

### 19.2 Mission

Big Boss dispatches rookie operative Solid Snake on Operation Intrude N313 to infiltrate Outer Heaven, rescue Gray Fox, determine the nature of Metal Gear, and destroy it.

### 19.3 Key Plot Points

1. Snake infiltrates Building 1, acquires weapons, and allows himself to be captured to reach Gray Fox in the basement prison.
2. Gray Fox reveals Metal Gear is a bipedal nuclear-armed walking tank. Its creator, Dr. Pettrovich Madnar, is also held captive.
3. Snake must rescue Madnar's daughter Ellen before the doctor will cooperate.
4. After rescuing Ellen, Dr. Madnar provides the C4 placement sequence to destroy TX-55 Metal Gear.
5. Snake fights through Building 3 to reach B100 and destroys Metal Gear.
6. Big Boss reveals himself as the leader of Outer Heaven and the final boss.
7. Snake defeats Big Boss and escapes during the self-destruct countdown.

### 19.4 Self-Destruct Escape

After defeating Big Boss, a self-destruct sequence activates. Snake must escape through the fortress before the timer expires. The Cigarettes item extends this timer by 1000 seconds. The player must navigate back through corridors to reach the exit.

---

## 20. Miscellaneous Mechanics

### 20.1 Getting Captured

| Mechanic | Detail |
|---|---|
| Trigger | Walking into a specific trap room in Building 1 |
| Effect | Snake is stripped of ALL weapons and items; placed in a prison cell |
| Purpose | Required to access Gray Fox's adjacent cell by punching through a false wall |
| Recovery | Must re-acquire weapons from pickup rooms after escaping |

### 20.2 Wall Punching

| Mechanic | Detail |
|---|---|
| Action | Punch walls repeatedly to test for weak/hollow spots |
| Result | Weak walls make a distinct sound; continued punching or Plastic Explosives breach them |
| Purpose | Opens secret passages; required progression in several areas |

### 20.3 Transmitter Bug

| Mechanic | Detail |
|---|---|
| Problem | An enemy transmitter is hidden among Snake's items; guards track his position |
| Solution | Check equipment menu for the Transmitter item; unequip and discard it |
| Consequence of keeping | Guards will find Snake more easily; heightened detection |

### 20.4 Impostor Trap

| Mechanic | Detail |
|---|---|
| Location | Building 2, B1 |
| Trap | A fake Dr. Madnar provides false information and triggers a guard ambush |
| Real Madnar | Located in Building 2, 2F; will only help after Ellen is rescued |

### 20.5 Cheat Codes (MSX2)

| Code | Method | Effect |
|---|---|---|
| INTRUDER | Pause (F1), type "INTRUDER", press Enter, unpause (F1) | Sets all ammo and item counts to 999 |

---

## 21. Complete Progression Checklist

| Step | Objective | Key Items / Requirements |
|---|---|---|
| 1 | Enter Outer Heaven; acquire Handgun, Card 1 | Navigate Building 1, 1F |
| 2 | Obtain Card 2, Binoculars, Gas Mask | Building 1, 1F rooms |
| 3 | Get captured; find Gray Fox; learn about Metal Gear | Building 1, B1 prison |
| 4 | Defeat Shoot Gunner; obtain Enemy Uniform | Building 1, B1 |
| 5 | Obtain IR Goggles | Building 1, B2 |
| 6 | Navigate IR laser corridors; defeat Machine Gun Kid | Building 1, 2F; Card 3-4 |
| 7 | Acquire Gas Mask, Silencer, Grenade Launcher, Bomb Blast Suit, Body Armor | Building 1, 3F |
| 8 | Disable electrified floor with RC Missile | Building 1, 3F |
| 9 | Reach Roof; defeat Hind-D helicopter | Building 1, Roof; Grenade Launcher |
| 10 | Parachute to desert; obtain Compass, Mine Detector | Desert |
| 11 | Defeat Tank | Desert; Land Mines (11) |
| 12 | Enter Building 2; rescue POWs; reach 4-star rank | Building 2, 1F-2F |
| 13 | Rescue Ellen from Building 2, B1 | Card 5-6 |
| 14 | Defeat Fire Trooper; obtain Card 6 | Building 2, B1 |
| 15 | Find real Dr. Madnar; receive TX-55 destruction sequence | Building 2, 2F |
| 16 | Obtain Rocket Launcher from Jennifer | 4-star rank required; radio 120.48 |
| 17 | Defeat Arnolds (Bloody Brad); obtain Card 7 | Building 2, 2F; Rocket Launcher |
| 18 | Defeat Coward Duck (carefully -- POW shields); obtain Card 8 | Building 2, 1F; precision aiming |
| 19 | Cross to Building 3; breach walls with Plastic Explosives | Building 3, 1F |
| 20 | Descend to B100; destroy TX-55 Metal Gear | 16 Plastic Explosives in L/R sequence |
| 21 | Defeat Big Boss | Rocket Launcher (4-5 hits) |
| 22 | Escape during self-destruct countdown | Navigate to exit; Cigarettes extend timer |
