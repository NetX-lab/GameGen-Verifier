from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
LINT_SCRIPT = REPO_ROOT / "scripts" / "prepare" / "lint_keypoints.py"

import sys

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common.keypoint_policy import KEYPOINT_POLICY_HEADER


def run_lint(keypoints_text: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "keypoints.md"
        path.write_text(keypoints_text, encoding="utf-8")
        return subprocess.run(
            [
                "python3",
                str(LINT_SCRIPT),
                "--keypoints-file",
                str(path),
                "--min-count",
                "4",
                "--min-per-category",
                "1",
                "--max-weak-share",
                "0.25",
                "--min-strong-cue-share",
                "0.50",
                "--min-multi-step-share",
                "0.50",
                "--min-hard-share",
                "0.75",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )


class KeypointQualityTests(unittest.TestCase):
    def test_strong_keypoints_pass_lint(self) -> None:
        text = KEYPOINT_POLICY_HEADER + "\n" + textwrap.dedent(
            """\
            ## Keypoint 1: [Game Rule] Revive resumes the same run without resetting score or inventory
            **Verification Focus:**
            This separates same-run recovery from a fake revive that secretly restarts the run.

            **Precondition Game State Description:**
            The player has progressed deep into an active run with non-zero score and collected inventory.

            **Instruction Description:**
            Trigger a lethal failure, accept the revive, then continue the run immediately afterward.

            **Expected Result Description:**
            The run resumes from the revive point, score and inventory remain preserved, and the game does not start a new run instead.

            ## Keypoint 2: [Boundary Condition] A locked door remains closed when the player lacks the key, but opens after the key is collected
            **Verification Focus:**
            This checks prerequisite gating instead of a superficial always-open door.

            **Precondition Game State Description:**
            The player can attempt the same locked door both before and after collecting its matching key.

            **Instruction Description:**
            First try to open the door without the key, then collect the key and try again.

            **Expected Result Description:**
            The first attempt fails while the second succeeds, and the door does not bypass its prerequisite.

            ## Keypoint 3: [Interaction Logic] A pressure plate opens the bridge only while it remains occupied
            **Verification Focus:**
            This checks revert-on-release behavior rather than a permanent switch disguised as a pressure plate.

            **Precondition Game State Description:**
            The player is standing near a pressure plate that controls a bridge over a hazard.

            **Instruction Description:**
            Step onto the pressure plate, cross-check the bridge, then step off and observe again.

            **Expected Result Description:**
            The bridge opens while the plate is occupied and reverts after the player leaves instead of staying permanently open.

            ## Keypoint 4: [State Transition] A chained combo requires jump first and slide immediately after; reversing the order fails
            **Verification Focus:**
            This checks order sensitivity and rejects partial completion as false success.

            **Precondition Game State Description:**
            The player is positioned just before a two-part obstacle where a gap is followed by a low barrier.

            **Instruction Description:**
            Compare the correct sequence of jump then slide with the reversed order.

            **Expected Result Description:**
            Only the ordered sequence clears both hazards, while the reversed order causes failure on the remaining obstacle.
            """
        )
        proc = run_lint(text)
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)

    def test_missing_policy_header_fails_lint(self) -> None:
        text = textwrap.dedent(
            """\
            ## Keypoint 1: [State Transition] Player can move right
            **Precondition Game State Description:**
            The run has started.

            **Instruction Description:**
            Press right.

            **Expected Result Description:**
            The player moves right.
            """
        )
        proc = run_lint(text)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("policy version", proc.stderr.lower())

    def test_weak_smoke_tests_fail_lint(self) -> None:
        text = KEYPOINT_POLICY_HEADER + "\n" + textwrap.dedent(
            """\
            ## Keypoint 1: [State Transition] The game starts
            **Verification Focus:**
            Startup happens.

            **Precondition Game State Description:**
            The page is loaded.

            **Instruction Description:**
            Wait briefly.

            **Expected Result Description:**
            The game begins.

            ## Keypoint 2: [Boundary Condition] The player can move left
            **Verification Focus:**
            Left movement exists.

            **Precondition Game State Description:**
            The player is visible.

            **Instruction Description:**
            Press left.

            **Expected Result Description:**
            The player moves left.

            ## Keypoint 3: [Interaction Logic] Coins can be collected
            **Verification Focus:**
            Coins are there.

            **Precondition Game State Description:**
            A coin is nearby.

            **Instruction Description:**
            Touch the coin.

            **Expected Result Description:**
            The coin disappears.

            ## Keypoint 4: [Game Rule] A button changes something
            **Verification Focus:**
            Buttons respond.

            **Precondition Game State Description:**
            A button is visible.

            **Instruction Description:**
            Click the button.

            **Expected Result Description:**
            Something changes.
            """
        )
        proc = run_lint(text)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("weak/basic", (proc.stdout + proc.stderr).lower())


if __name__ == "__main__":
    unittest.main()
