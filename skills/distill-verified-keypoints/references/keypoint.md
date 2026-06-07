<!-- @LABEL: Design Here are our specific design details -->

## Keypoint Extraction Principles

The first line of every generated `keypoints.md` must be:
- `<!-- KEYPOINT_POLICY_VERSION: 2026-04-23-spec-v4 -->`

**What is a Keypoint:**
- A keypoint is a **discrete, verifiable assertion** in game logic
- Each keypoint describes the behavior the game should exhibit under specific states/conditions
- Keypoints should be **atomic**, meaning they can be verified independently
- For substantial games in this workflow, generate **30-40 keypoints**
- For substantial games in this workflow, prefer **30-40 strong keypoints** instead of generating a larger but weaker list
- A good keypoint is **discriminative**: a shallow implementation should plausibly fail it
- A good keypoint is **specification-specific**: it should come from this game's actual design, not from generic genre expectations alone
- A good keypoint is **short-horizon verifiable**: the verifier should be able to judge it after state localization, without needing a full playthrough

**Keypoint Categories:**
1. **State Transition**: When condition X is met, state Y should change to Z
   - Example: "When player health drops to 0, game state should change to GameOver"
2. **Boundary Condition**: Behavior when parameters are at boundary values
   - Example: "Player coordinates should not exceed map boundaries (0-800, 0-600)"
3. **Interaction Logic**: Interaction rules between game objects
   - Example: "When bullet collides with enemy, enemy should be destroyed and score should increase by 10"
4. **Game Rule**: Core rules based on game description
   - Example: "After collecting all coins, victory screen should be displayed"

## Specification-First Extraction Guidance

Prefer keypoints that check:
- exception handling
- resource preservation
- carry-over state
- multi-step progression
- precedence between competing rules
- multi-entity interactions
- nearby positive/negative contrasts
- confounder separation
- consequences that are directly observable after a short interaction

For each core mechanic, usually think in a small family:
- one success case
- one nearby failure/boundary/forbidden case
- one persistence/order/precedence/resource-consequence case when the description supports it
- one confounder case when nearby incorrect behavior could look superficially successful

Examples of stronger keypoints:
- "A revive resumes the same run with preserved score/currency instead of restarting from zero"
- "A pressure plate effect reverts after the occupant leaves, unlike a permanent switch"
- "A moving platform carries a rider entity with it instead of only updating hidden state"
- "A shield blocks obstacle damage but does not protect against falling off the path"

Examples of weak keypoints that should be kept to a minority:
- "The player can move"
- "The game starts"
- "A reachable destination can be tapped"
- "Coins are collectible"
- "A button changes something"

## Difficulty Budget

For a strong keypoint set:
- basic sanity checks should be a small minority
- many keypoints should be failure/boundary/negative cases
- many keypoints should require multiple conditions or multiple interacting mechanics
- headings should state the invariant or consequence, not just the input action
- a majority of keypoints should be hard either because they are contrastive or because they require multi-step/order-sensitive logic
- each keypoint should have a clear reason why it catches a plausible shallow or buggy implementation

If a mechanic only has an easy positive case, add a nearby counterexample:
- when it should fail
- when it should not apply
- what invariant must remain preserved
- what state must carry over after the transition

## Keypoint Verification Approach

For each keypoint verification, we will construct a prestate game state that makes it easy to verify the keypoint. After positioning to this state, the Interaction Agent executes the given Instruction, and then determines whether the short-term interaction is correct based on the Expected Result. In the keypoint extraction step, you only need to provide fuzzy language descriptions from the Game Description for: prestate game state description, instruction description, and expected result description. In subsequent steps, these will be combined with the generated code to provide precise and specific prestate game state positioning, instructions, and expected results.
