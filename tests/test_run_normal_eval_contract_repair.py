from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
MODULE_PATH = REPO_ROOT / "harness" / "run_normal_eval.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


spec = importlib.util.spec_from_file_location("run_normal_eval_contract_repair", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RunNormalEvalContractRepairTests(unittest.TestCase):
    def test_ensure_minimal_keypoint_contract_artifacts_repairs_partial_test_config(self) -> None:
        kp = module.Keypoint(
            "78",
            "Interaction Logic",
            "Projectile destroys target only after collision",
            "Player is lined up with a target and a projectile is ready.",
            "Fire once toward the target.",
            "The target is removed only after a visible hit.",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            keypoint_dir = Path(tmpdir) / "keypoint_78"
            keypoint_dir.mkdir(parents=True)
            partial = {
                "verification_contract": {
                    "required_observations": ["target disappears after collision"],
                }
            }
            (keypoint_dir / "test_config.json").write_text(
                json.dumps(partial, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            module.ensure_minimal_keypoint_contract_artifacts(
                keypoint_dir=keypoint_dir,
                kp=kp,
                game_url="http://127.0.0.1:4271",
            )

            repaired = json.loads((keypoint_dir / "test_config.json").read_text(encoding="utf-8"))
            self.assertEqual(repaired["game_url"], "http://127.0.0.1:4271")
            self.assertIsInstance(repaired["precondition_state"], dict)
            self.assertIsInstance(repaired["expected_state"], dict)
            self.assertEqual(repaired["interaction"]["actions"], [])
            self.assertEqual(repaired["required_observations"], ["target disappears after collision"])
            self.assertEqual(
                repaired["verification_contract"]["required_observations"],
                ["target disappears after collision"],
            )
            self.assertEqual(repaired["precondition_checks"], [])
            self.assertEqual(repaired["forbidden_observations"], [])
            self.assertEqual(repaired["metadata"]["keypoint_id"], "78")
            self.assertEqual(repaired["metadata"]["category"], "Interaction Logic")
            self.assertEqual(
                repaired["metadata"]["description"],
                "Projectile destroys target only after collision",
            )


if __name__ == "__main__":
    unittest.main()
