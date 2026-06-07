from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from harness import agent_runner


class AgentRunnerTests(unittest.TestCase):
    def test_resolve_codex_model_provider_prefers_env_then_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir)
            (codex_home / "config.toml").write_text(
                'model_provider = "crs"\n[model_providers.crs]\nname = "Custom"\n',
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}, clear=True):
                self.assertEqual(agent_runner.resolve_codex_model_provider(), "crs")
                with mock.patch.dict(os.environ, {"CODEX_HOME": str(codex_home), "CODEX_MODEL_PROVIDER": "alt"}, clear=True):
                    self.assertEqual(agent_runner.resolve_codex_model_provider(), "alt")

    def test_build_agent_cmd_uses_resolved_provider_not_hardcoded_oaiapi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir)
            (codex_home / "config.toml").write_text(
                'model_provider = "crs"\n[model_providers.crs]\nname = "Custom"\n',
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}, clear=True):
                cmd = agent_runner.build_agent_cmd(
                    repo=REPO_ROOT,
                    backend="codex",
                    prompt="test prompt",
                    model="gpt-5.4",
                    reasoning_effort="high",
                    disable_multi_agent=True,
                )
        self.assertIn('model_provider="crs"', cmd)
        self.assertNotIn('model_provider="oaiapi"', cmd)

    def test_ensure_backend_available_rejects_undeclared_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir)
            (codex_home / "config.toml").write_text(
                'model_provider = "missing"\n[model_providers.crs]\nname = "Custom"\n',
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}, clear=True):
                with mock.patch("harness.agent_runner.shutil.which", return_value="/usr/bin/codex"):
                    with self.assertRaises(RuntimeError):
                        agent_runner.ensure_backend_available("codex")


if __name__ == "__main__":
    unittest.main()
