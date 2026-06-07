# Return of the Obra Dinn - Complete Game Specification

> A comprehensive specification for recreating Return of the Obra Dinn (Lucas Pope, 2018), the single-player first-person deduction adventure. This spec focuses on explorable ship space, death memories, identity deduction, fate validation, and notebook UI.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Return of the Obra Dinn |
| Developer | Lucas Pope |
| Initial Release | October 18, 2018 |
| Source Store | Steam |
| Genre | Mystery adventure / deduction puzzle |
| Perspective | First-person 3D with monochrome dithered rendering |
| Input | Keyboard/mouse or controller |
| Session Length | 6-10 hours in the original; compact clone may target 2-4 hours |
| Primary Objective | Determine the identity and fate of every person aboard a missing ship |
| Lose Condition | None; deduction can be wrong but the game does not kill the player |
| Win Condition | Correctly complete all required identity/fate entries and leave with final report |
| Online Requirement | None |

## 2. AI-Generation Scope

Minimum viable clone:

- A compact ship with 20-30 crew/passengers.
- Corpse interaction using a magic watch to enter frozen death memories.
- Notebook with manifest, sketches, ship map, memory chapters, identities, fates, and validation in sets of three.
- First-person exploration with locked/unlocked areas tied to discovered memories.

High-fidelity target:

- 60-person manifest, ten chapters, nested memories, audio transcripts, location labeling, and full epilogue scoring.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | First-person 3D; monochrome 1-bit or limited-palette shader |
| World | Static ship environment with interactable corpses and memory entry points |
| Memories | Frozen tableaux scenes with positioned characters, props, audio, and transcript |
| Notebook | Data-heavy UI; should be fast to open and cross-reference |
| Save | Persistent deductions, discovered bodies, opened doors, and memory links |
| No Fail State | Player can always revise guesses until validated |

Game loop:

```text
1. Explore current ship area
2. Find corpse, remains, or memory anchor
3. Use watch to play death audio and transition to frozen memory
4. Inspect characters, props, cause of death, location, and dialogue clues
5. Notebook records chapter page, sketch labels, and unknown participants
6. Player assigns names and fates in notebook
7. When three complete entries are correct, lock them as validated
8. New bodies or areas may become available
9. When all required fates are solved, allow final departure
```

## 4. Ship Exploration

Ship layout:

- Main deck.
- Gun deck.
- Cargo hold.
- Crew quarters.
- Captain's quarters.
- Surgery/medical area.
- Lifeboat area.
- Bow and stern exterior.

Exploration rules:

- Player walks but cannot jump.
- Doors may be locked until memories reveal keys or routes.
- Important remains are highlighted only through subtle audio/watch cues.
- The ship is quiet and mostly empty outside memories.

## 5. Memory System

Each memory is a frozen scene at the instant of death.

Memory fields:

```text
id, chapter, part, death_person_id, location, audio_transcript,
freeze_time, participants, visible_props, linked_bodies, unlocks
```

Memory sequence:

1. Watch opens.
2. Black screen with audio only.
3. Gunshot, scream, impact, or final line marks death.
4. Scene fades in as frozen 3D tableau.
5. Player can walk around within a bounded radius.
6. Notebook opens automatically for new chapter page.
7. Exiting returns to corpse location.

Nested memories:

- Some bodies inside a memory can be inspected to jump to another memory.
- This creates a discovery chain and should be tracked in notebook order.

## 6. Deduction Data Model

Person fields:

```text
id, real_name, role, nationality, appearance_tags, relationships,
sketch_position, first_memory, last_memory, correct_fate
```

Fate fields:

```text
cause_category, cause_detail, killer_or_responsible_party,
location_or_context, optional_notes
```

Common fate categories:

- Shot.
- Stabbed.
- Speared.
- Crushed.
- Burned.
- Drowned.
- Fell.
- Clubbed.
- Poisoned.
- Torn apart.
- Eaten.
- Missing/escaped.

Some fates require responsible party. Examples: "shot by X", "killed by beast", "drowned at sea", "escaped in lifeboat".

## 7. Validation Rules

The original-style validation locks correct answers in sets of three.

Implementation:

- The player may freely assign names and fates.
- After any edit, check all unresolved persons.
- If at least three complete person entries are exactly correct, validate exactly three and lock them.
- Locked entries cannot be edited and receive a visual stamp.
- Do not reveal which wrong entries are close; this preserves deduction.

Difficulty options:

- Strict: exact killer and cause required.
- Friendly: cause category enough for some ambiguous deaths.
- Hint mode: notebook marks pages with enough information available.

## 8. Clue Types

Clues must be fair and cross-referenced:

| Clue Type | Example |
|-----------|---------|
| Dialogue | Names, accents, ranks, relationships |
| Uniform | Officer, sailor, passenger, surgeon |
| Location | Hammock number, cabin assignment, work station |
| Language | Nationality inferred from speech |
| Social Group | People standing together in sketches or memories |
| Object | Weapon, instrument, cargo, personal item |
| Timeline | Alive in one memory, dead in a later one |

Every identity should have at least two clue paths, and every fate should be visible or inferable.

## 9. Notebook UI

Notebook sections:

- Manifest list.
- Artist sketch with clickable faces.
- Ship map by deck.
- Chapter index.
- Fate entry form.
- Glossary of causes and names.

Face labeling:

- Unknown faces start blurred or unconfirmed.
- Faces become clear after enough memories include the person.
- Clicking a face opens person page with seen memories and current guess.

Fate entry:

- Select person name.
- Select cause.
- Select responsible party if required.
- Optional location/context.

## 10. Chapter Structure

Recommended compact chapter list:

| Chapter | Theme |
|---------|-------|
| The End | Final deaths near return |
| Murder | Human conflict and first clear weapon clues |
| Disease | Medical and passenger identities |
| Escape | Lifeboat fates |
| Disaster | Beast or storm deaths |
| Mutiny | Chain of responsibility |

Each chapter should have 3-6 deaths in a compact clone.

## 11. Visual And Audio Direction

- Monochrome rendering should preserve object readability.
- Important props need strong silhouettes.
- Frozen memories should contain no character animation after reveal.
- Audio is essential: footsteps, watch ticking, door creaks, ocean, dialogue, death sounds.
- Transcripts must be available after first listening.

## 12. Validation Checklist

- Each corpse opens the correct memory only after watch use.
- A memory can contain another inspectable corpse.
- Notebook records all seen participants and locations.
- Three correct fates validate together and lock.
- No fail state blocks the player from revising guesses.
- All identities and fates can be solved from visible or audible clues.

