from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
MODULE_PATH = REPO_ROOT / "harness" / "run_normal_eval.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


spec = importlib.util.spec_from_file_location("run_normal_eval", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RunNormalEvalBatchTests(unittest.TestCase):
    def test_chunk_keypoints_groups_in_order(self) -> None:
        keypoints = [
            module.Keypoint(str(i), "Rules", f"kp{i}", f"pre{i}", f"inst{i}", f"exp{i}")
            for i in range(1, 8)
        ]
        chunks = module.chunk_keypoints(keypoints, 3)
        self.assertEqual([[kp.keypoint_id for kp in chunk] for chunk in chunks], [["1", "2", "3"], ["4", "5", "6"], ["7"]])

    def test_build_batch_worker_prompt_includes_all_keypoints(self) -> None:
        keypoints = [
            module.Keypoint("12", "Rules", "first desc", "first pre", "first inst", "first exp"),
            module.Keypoint("13", "Timing", "second desc", "second pre", "second inst", "second exp"),
        ]
        prompt = module.build_batch_worker_prompt(
            workspace=REPO_ROOT,
            game_name="tetris",
            run_id="batch_test",
            batch_id=2,
            keypoints=keypoints,
            game_url="http://127.0.0.1:4271",
            screenshot_mode="sequence",
            screenshot_interval=200,
        )
        self.assertIn("batch of 2 normal-mode keypoint tests", prompt)
        self.assertIn("keypoint_id=12", prompt)
        self.assertIn("keypoint_id=13", prompt)
        self.assertIn("output_dir=runs/tetris/batch_test/keypoint_12/", prompt)
        self.assertIn("output_dir=runs/tetris/batch_test/keypoint_13/", prompt)
        self.assertIn("continue to the next keypoint", prompt)


if __name__ == "__main__":
    unittest.main()
