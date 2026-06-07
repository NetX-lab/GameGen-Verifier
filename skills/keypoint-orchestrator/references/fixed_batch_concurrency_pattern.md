# Fixed Batch Concurrency Pattern

## Overview

This document describes the **fixed batch execution pattern** used by the keypoint-orchestrator to maintain predictable parallel execution while strictly respecting concurrency limits.

## Key Principle

**Process keypoints in fixed-size batches** by spawning N agents together, waiting for ALL to complete, then spawning the next batch. This ensures concurrency never exceeds the limit.

## Concurrency Limit

- **Maximum concurrent agents**: 3 (configurable, but typically 2-3 to avoid API rate limits)
- **Never exceed this limit** to avoid 429 rate limit errors
- **Batch size equals concurrency limit** for predictable execution

## Execution Pattern

### Phase 1: Batch 1 (First N keypoints)

Spawn the first batch of N agents.

**Result**: 3 agents running in parallel (KP1, KP2, KP3)

**Note**: For true parallelism, start each `Task` and put it in the background so multiple subagents can run concurrently.

### Phase 2: Wait for Batch Completion

Wait for ALL agents in the current batch to complete:

```
Time T1: KP1 completes → Still waiting (KP2, KP3 running)
Time T2: KP2 completes → Still waiting (KP3 running)
Time T3: KP3 completes → Batch 1 complete! ✓
```

**Do NOT spawn new agents** until the entire batch completes.

### Phase 3: Batch 2 (Next N keypoints)

Once Batch 1 completes, spawn Batch 2.

**Result**: 3 agents running in parallel (KP4, KP5, KP6)

### Phase 4: Continue Until All Keypoints Processed

Repeat the pattern:
1. Spawn batch (up to max_concurrent Tasks)
2. Wait for ALL to complete
3. Spawn next batch

```
Batch 1: KP1, KP2, KP3 → Wait for all → Complete
Batch 2: KP4, KP5, KP6 → Wait for all → Complete
Batch 3: KP7, KP8, KP9 → Wait for all → Complete
Batch 4: KP10, KP11, KP12 → Wait for all → Complete ✓
```

### Phase 5: Final Batch (Partial)

If the number of keypoints is not divisible by batch size, the final batch will be smaller:

```
Batch 5: KP13, KP14 (only 2 agents) → Wait for all → Complete ✓
```

## Implementation Details

### Batching Logic

```python
def orchestrate(keypoints, max_concurrent=3):
    pending = list(keypoints)
    batch_size = max_concurrent
    all_results = []

    while pending:
        # Take next batch
        current_batch = pending[:batch_size]
        pending = pending[batch_size:]

        # Spawn all agents in batch (up to max_concurrent)
        agents = []
        for kp in current_batch:
            agent = spawn(kp)
            agents.append(agent)

        # Wait for ALL agents in batch to complete
        for agent in agents:
            result = wait_for_completion(agent)
            all_results.append(result)

        # Batch complete, proceed to next batch

    return all_results
```

### State Tracking

The orchestrator maintains:

```python
all_keypoints = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
batch_size = 3

# Batch 1
current_batch = [1, 2, 3]
pending = [4, 5, 6, 7, 8, 9, 10, 11, 12]

# After Batch 1 completes
completed = [1, 2, 3]

# Batch 2
current_batch = [4, 5, 6]
pending = [7, 8, 9, 10, 11, 12]

# ... and so on
```

### Timing Example (12 keypoints, 3 concurrent, ~30s per test)

```
Time 0s:   Spawn KP1, KP2, KP3  (Batch 1)
Time 30s:  KP1 done → Still waiting
Time 35s:  KP2 done → Still waiting
Time 40s:  KP3 done → Batch 1 complete!

Time 40s:  Spawn KP4, KP5, KP6  (Batch 2)
Time 70s:  KP4 done → Still waiting
Time 75s:  KP5 done → Still waiting
Time 80s:  KP6 done → Batch 2 complete!

Time 80s:  Spawn KP7, KP8, KP9  (Batch 3)
Time 110s: KP7 done → Still waiting
Time 115s: KP8 done → Still waiting
Time 120s: KP9 done → Batch 3 complete!

Time 120s: Spawn KP10, KP11, KP12 (Batch 4)
Time 150s: KP10 done → Still waiting
Time 155s: KP11 done → Still waiting
Time 160s: KP12 done → Batch 4 complete! ✓ All done
```

**Total time**: ~160 seconds

**Note**: Each batch waits for the slowest agent in that batch before proceeding.

## Benefits

1. **Predictable concurrency**: Never exceeds max_concurrent limit
2. **Simple to implement**: Clear batch boundaries
3. **Easy to debug**: Can inspect results after each batch
4. **Respects limits**: Guaranteed to avoid rate limit errors
5. **Reliable**: No complex state management needed

## Configuration

```python
# Adjust based on API rate limits
MAX_CONCURRENT = 3  # Conservative for most APIs
```

## Error Handling

If a spawn fails due to rate limits:
1. Wait 3 minutes (as per API error message)
2. Retry the entire batch
3. Continue with remaining batches

## Summary

The key insight is: **Process in fixed batches, wait for all to complete**. This provides predictable, reliable parallel execution while strictly respecting concurrency limits.
