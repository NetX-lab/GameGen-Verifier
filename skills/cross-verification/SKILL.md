---
name: cross-verification
description: Recheck an existing normal keypoint evaluation artifact without rerunning the game.
---

# Cross Verification

Use this skill to inspect an existing keypoint artifact directory and write a
fresh `recheck_result.json`.

Read only:

- `result.json`
- `test_result.json`
- `test_config.json`
- existing screenshots or traces, if present

Do not rerun Playwright, do not modify original artifacts, and do not inspect
unrelated runs.

The output file must contain:

- `status`: `PASS`, `FAIL`, or `INCOMPLETE`
- `passed`: boolean when status is binary, otherwise `false`
- `confidence`: integer 0-100
- `reasoning`: list of concise evidence bullets
- `explanation`: complete natural-language explanation
- `conflict_with_original`: boolean
