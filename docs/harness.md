# Harness Substrate

The harness is the substrate that runs a verifier agent against a generated
game keypoint by keypoint, with a real browser, a queued worker pool, retry,
and quota-aware pausing. It is **not** a single file; it is split between the
Python orchestration layer and the prompt-side worker skill.

This document is a map: when something goes wrong, here is where each piece
lives.

## Python orchestration layer (`harness/`)

| File                                  | Role                                                                   |
| ------------------------------------- | ---------------------------------------------------------------------- |
| `harness/run_normal_eval.py`  | Main harness driver: queues keypoints, fans out workers, writes runs/. |
| `harness/run_recheck_eval.py` | Recheck pass: re-runs the verifier with the prior verdict in context.  |
| `harness/agent_runner.py`     | Backend abstraction over the coding-agent CLI (`codex` / `claude`).    |
| `harness/quota_control.py`    | Detects backend quota exhaustion and converts it to a `PAUSED` exit.   |
| `harness/runner_utils.py`     | Subprocess wrapper with logging, timeouts, and retry plumbing.         |

## Cross-cutting utilities (`scripts/common/`)

| File                              | Role                                                       |
| --------------------------------- | ---------------------------------------------------------- |
| `scripts/common/game_catalog.py`  | Description-directory helpers used by every flow.          |
| `scripts/common/keypoint_policy.py` | Keypoint-quality policy header used by `lint_keypoints.py`. |

## Worker-side artifacts

The Python harness driver does the batching, queueing, retry, and timeout
itself; the per-keypoint worker session is launched stateless with a
**single** SKILL.md inlined as system prompt (or auto-loaded by Codex from
`.codex/skills/`). The remaining `skills/<orchestrator>/SKILL.md` files
under `keypoint-orchestrator/` and `recheck-orchestrator/` document the
orchestration contract that the Python driver implements; they are not
loaded by the driver. The `keypoint-orchestrator/scripts/*.py` files,
however, are actually invoked.

| File                                                                     | How it is used                                                                |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| `skills/short-interaction-verification/SKILL.md`                         | Inlined as part of the worker system prompt for each keypoint (normal pass).  |
| `skills/generative-state-construction/SKILL.md`                          | Inlined alongside the verifier SKILL.md for each keypoint (normal pass).      |
| `skills/cross-verification/SKILL.md`                                     | Inlined as the worker system prompt for each keypoint (recheck pass).         |
| `skills/auto-eval/scripts/dev_server_lifecycle.sh`                       | Vite dev server lifecycle (start, ready-probe, stop) -- shelled out by driver.|
| `skills/keypoint-orchestrator/scripts/check_keypoint_count.py`           | Subprocess invocation from `run_normal_eval.py` to validate keypoint count.   |
| `skills/keypoint-orchestrator/scripts/validate_artifacts.py`             | Subprocess invocation from `run_normal_eval.py` to validate worker artifacts. |
| `skills/keypoint-orchestrator/SKILL.md`                                  | Documentation of the orchestration contract (Python implements it).           |
| `skills/keypoint-orchestrator/references/fixed_batch_concurrency_pattern.md` | Documentation of the fixed-batch concurrency pattern the driver follows.  |
| `skills/keypoint-orchestrator/references/minimal_context_principle.md`   | Documentation of the worker-context contract.                                 |
| `skills/recheck-orchestrator/SKILL.md`                                   | Documentation of the recheck orchestration contract.                          |
| `skills/distill-verified-keypoints/SKILL.md`                             | Used by `scripts/prepare/distill_keypoints.py` (auto-loaded by Codex).        |
| `skills/game-gen-with-data/SKILL.md`                                     | Used by `scripts/prepare/generate_games.py` (auto-loaded by Codex).           |
| `skills/analyze-game-implementation/SKILL.md`                            | Available for diagnostic analysis sessions.                                   |

## Data flow

```text
scripts/run_all_experiments.py
  -> harness/run_normal_eval.py                        (Python driver
                                                                does the batching
                                                                + queue + retries;
                                                                no orchestrator
                                                                skill is loaded.)
       -> skills/auto-eval/scripts/dev_server_lifecycle.sh     (vite up)
       -> games/<game>/keypoints.md                            (load queue)
       -> for each keypoint: codex exec | claude -p            (per --backend)
            with system prompt = skills/generative-state-construction/SKILL.md
                               + skills/short-interaction-verification/SKILL.md
       -> runs/<game>/<run_id>/keypoint_<id>/{result.json, screenshots/}
       -> runs/<game>/<run_id>/{summary_report.md, evaluation_report.md}
  -> harness/run_recheck_eval.py                       (Python driver does
                                                                the orchestration;
                                                                only cross-verification
                                                                is loaded as worker
                                                                system prompt)
       -> for each keypoint with prior verdict:
            codex exec | claude -p with system prompt = skills/cross-verification/SKILL.md
       -> runs/<game>/<run_id>/keypoint_<id>/recheck_result.json
       -> runs/<game>/<run_id>/{recheck_summary.md, recheck_comparison.json}
```

## Resume / quota-pause contract

`harness/quota_control.py` defines a non-zero `PAUSED_RETURN_CODE`. Any
backend call that hits a usage-limit error propagates this code up through:

- the worker subprocess in `run_normal_eval.py` / `run_recheck_eval.py`
- `scripts/run_all_experiments.py` (which logs the row and stops if
  `--stop-on-error`)

This is what makes resumes deterministic: a paused run leaves
`runs/<game>/<run_id>/` in a consistent half-finished state, and re-running
the same entry point with `--resume-run` (eval) skips the keypoints that
already produced a `PASS`/`FAIL`.

## Where to make changes

- New verifier behavior -> edit the prompt-side skills in `skills/`.
- New backend (e.g. another coding-agent CLI) -> extend `agent_runner.py`.
- New retry/quota policy -> `quota_control.py` + `runner_utils.py`.
- New experiment/aggregation -> add a phase to `run_all_experiments.py`; do
  not introduce a new top-level launcher.
