#!/usr/bin/env python3
"""Run normal-mode evaluation directly without multi-agent orchestration.

This script avoids nested Codex sub-agents by invoking one Codex exec per keypoint
with `features.multi_agent=false`, while still reusing existing evaluation skills.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shlex
import concurrent.futures
import subprocess
import sys
import time
from functools import lru_cache
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from harness.agent_runner import build_agent_cmd, ensure_backend_available, normalize_backend
from common.keypoint_policy import DEFAULT_MIN_KEYPOINT_COUNT, keypoint_policy_is_current_file
from harness.quota_control import PAUSED_RETURN_CODE, extract_retry_after_hint, is_quota_exceeded_text
from common.game_catalog import DESCRIPTION_DIRNAME, description_path
from harness.runner_utils import run_and_capture


DISTILL_KEYPOINTS_SCRIPT = REPO_ROOT / "scripts" / "prepare" / "distill_keypoints.py"
LINT_KEYPOINTS_SCRIPT = REPO_ROOT / "scripts" / "prepare" / "lint_keypoints.py"


@dataclass
class Keypoint:
    keypoint_id: str
    category: str
    description: str
    prestate: str
    instruction: str
    expected: str


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def run_cmd(
    cmd: List[str],
    *,
    cwd: Path,
    timeout: int,
    log_path: Optional[Path] = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    proc = run_and_capture(
        cmd,
        cwd=cwd,
        timeout=timeout,
        log_path=log_path,
    )
    output = proc.stdout or ""
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(shlex.quote(x) for x in cmd)}\n{output[-4000:]}"
    )
    return proc


def cleanup_stale_vite_servers(workspace: Path, *, log_path: Optional[Path] = None) -> None:
    patterns = [
        str(workspace / "games"),
        "node_modules/.bin/vite --host 127.0.0.1 --port",
    ]
    try:
        listed = subprocess.run(
            ["pgrep", "-af", "vite --host 127.0.0.1 --port"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return

    matching_pids: List[str] = []
    for line in (listed.stdout or "").splitlines():
        if all(pattern in line for pattern in patterns):
            pid = line.split(None, 1)[0]
            if pid.isdigit() and int(pid) != os.getpid():
                matching_pids.append(pid)

    if not matching_pids:
        return

    note = f"[cleanup] stale vite servers: {' '.join(matching_pids)}\n"
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(note)
    else:
        print(note.strip(), file=sys.stderr)

    for signal_name in ("TERM", "KILL"):
        try:
            subprocess.run(
                ["pkill", f"-{signal_name}", "-f", "vite --host 127.0.0.1 --port"],
                cwd=workspace,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            break
        time.sleep(1)


def start_server_with_recovery(
    *,
    workspace: Path,
    lifecycle: Path,
    game_name: str,
    log_path: Path,
) -> subprocess.CompletedProcess:
    cmd = [
        str(lifecycle),
        "start",
        "--repo-root",
        str(workspace),
        "--game-name",
        game_name,
        "--bootstrap-playwright",
    ]
    try:
        return run_cmd(
            cmd,
            cwd=workspace,
            timeout=600,
            log_path=log_path,
            check=True,
        )
    except RuntimeError as exc:
        if "No free port found" not in str(exc):
            raise
        cleanup_stale_vite_servers(workspace, log_path=log_path)
        return run_cmd(
            cmd,
            cwd=workspace,
            timeout=600,
            log_path=log_path,
            check=True,
        )


def ensure_inputs(workspace: Path, game_name: str) -> None:
    required = [
        description_path(game_name, workspace),
        workspace / "games" / game_name / "src",
        workspace / "games" / game_name / "data.md",
        workspace / "games" / game_name / "state_injection_api.md",
        workspace / "games" / game_name / "package.json",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required files:\n" + "\n".join(missing))


def parse_keypoints(keypoints_md: Path) -> List[Keypoint]:
    text = keypoints_md.read_text(encoding="utf-8")
    result: List[Keypoint] = []
    heading_re = re.compile(r"^## Keypoint (\d+): \[(.+?)\] (.+)$", re.M)
    matches = list(heading_re.finditer(text))

    def extract_block(part: str, label: str) -> str:
        m = re.search(rf"\*\*{re.escape(label)}:\*\*\n(.+?)(?:\n\n|\Z)", part, re.S)
        if not m:
            return ""
        return " ".join(m.group(1).strip().split())

    for index, match in enumerate(matches):
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        part = text[match.start():next_start]
        kid, category, desc = match.groups()
        result.append(
            Keypoint(
                keypoint_id=kid,
                category=category,
                description=desc.strip(),
                prestate=extract_block(part, "Precondition Game State Description"),
                instruction=extract_block(part, "Instruction Description"),
                expected=extract_block(part, "Expected Result Description"),
            )
        )

    result.sort(key=lambda x: int(x.keypoint_id))
    if not result:
        raise RuntimeError(f"No keypoints parsed from: {keypoints_md}")
    if len(result) != len(matches):
        raise RuntimeError(
            f"Keypoint parse mismatch for {keypoints_md}: headings={len(matches)} parsed={len(result)}"
        )
    return result


def enforce_min_keypoint_count(workspace: Path, keypoints_md: Path, minimum: int = DEFAULT_MIN_KEYPOINT_COUNT) -> None:
    if not keypoints_md.exists():
        raise FileNotFoundError(f"Missing keypoints file: {keypoints_md}")

    run_cmd(
        [
            "python3",
            str(workspace / ".codex" / "skills" / "keypoint-orchestrator" / "scripts" / "check_keypoint_count.py"),
            "--keypoints-file",
            str(keypoints_md),
            "--min-count",
            str(minimum),
        ],
        cwd=workspace,
        timeout=60,
        check=True,
    )


def parse_assignments(stdout_text: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in stdout_text.splitlines():
        if "=" not in line:
            continue
        if not re.match(r"^[A-Z0-9_]+=", line.strip()):
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


@lru_cache(maxsize=None)
def load_skill_text(workspace_root: str, skill_name: str) -> str:
    path = Path(workspace_root) / ".codex" / "skills" / skill_name / "SKILL.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def worker_system_prompt(workspace: Path) -> str:
    parts = [
        load_skill_text(str(workspace), "generative-state-construction").strip(),
        load_skill_text(str(workspace), "short-interaction-verification").strip(),
    ]
    return "\n\n".join(part for part in parts if part)


def keypoint_output_dir(*, game_name: str, run_id: str, keypoint_id: str) -> str:
    return f"runs/{game_name}/{run_id}/keypoint_{keypoint_id}/"


def chunk_keypoints(keypoints: List[Keypoint], chunk_size: int) -> List[List[Keypoint]]:
    size = max(1, int(chunk_size))
    return [keypoints[i:i + size] for i in range(0, len(keypoints), size)]


def build_backend_cmd(
    workspace: Path,
    *,
    backend: str,
    prompt: str,
    model: str,
    reasoning_effort: str,
    system_prompt: str = "",
) -> List[str]:
    return build_agent_cmd(
        repo=workspace,
        backend=backend,
        prompt=prompt,
        model=model,
        reasoning_effort=reasoning_effort,
        system_prompt=system_prompt,
        disable_multi_agent=True,
        sandbox="danger-full-access",
        approval="never",
        allowed_dirs=[workspace],
    )


def run_backend_prompt(
    workspace: Path,
    *,
    backend: str,
    prompt: str,
    model: str,
    reasoning_effort: str,
    timeout: int,
    log_path: Path,
    system_prompt: str = "",
) -> subprocess.CompletedProcess:
    cmd = build_backend_cmd(
        workspace,
        backend=backend,
        prompt=prompt,
        model=model,
        reasoning_effort=reasoning_effort,
        system_prompt=system_prompt,
    )
    return run_cmd(cmd, cwd=workspace, timeout=timeout, log_path=log_path, check=True)


def is_retryable_backend_error(output: str) -> bool:
    """Detect transient backend failures that warrant a retry."""
    indicators = [
        "stream disconnected before completion",
        "Transport error:",
        "Reconnecting...",
        "We're currently experiencing high demand",
        "connection reset",
        "ECONNRESET",
    ]
    return any(ind in output for ind in indicators)


def is_quota_exceeded(output: str) -> bool:
    """Detect backend quota/rate-limit errors that should halt the run."""
    return is_quota_exceeded_text(output)


def timeout_output_text(exc: subprocess.TimeoutExpired) -> str:
    output = exc.output or ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return str(output)


class QuotaExceededError(Exception):
    """Raised when backend quota is exceeded and the run should pause."""
    pass


def run_backend_prompt_with_retry(
    workspace: Path,
    *,
    backend: str,
    prompt: str,
    model: str,
    reasoning_effort: str,
    timeout: int,
    log_path: Path,
    max_retries: int = 2,
    retry_backoff: int = 15,
    system_prompt: str = "",
) -> subprocess.CompletedProcess:
    """Run one backend prompt with automatic retry on transient failures."""
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_retries + 2):
        attempt_log = log_path
        if attempt > 1:
            attempt_log = log_path.with_name(
                f"{log_path.stem}.retry{attempt - 1}{log_path.suffix}"
            )
        try:
            proc = run_backend_prompt(
                workspace,
                backend=backend,
                prompt=prompt,
                model=model,
                reasoning_effort=reasoning_effort,
                timeout=timeout,
                log_path=attempt_log,
                system_prompt=system_prompt,
            )
            # On success, copy attempt log to primary log path if it was a retry
            if attempt > 1:
                try:
                    log_path.write_text(attempt_log.read_text(encoding="utf-8"), encoding="utf-8")
                except Exception:
                    pass
            return proc
        except subprocess.TimeoutExpired as exc:
            last_exc = exc
            output = timeout_output_text(exc)
            if is_quota_exceeded(output):
                raise QuotaExceededError(output)
            if attempt <= max_retries:
                print(
                    f"[RETRY] {backend} worker timed out (attempt {attempt}/{max_retries + 1}), "
                    f"retrying in {retry_backoff}s...",
                    file=sys.stderr,
                )
                time.sleep(retry_backoff)
                continue
            raise
        except RuntimeError as exc:
            last_exc = exc
            output = str(exc)
            if is_quota_exceeded(output):
                raise QuotaExceededError(output)
            if attempt <= max_retries and is_retryable_backend_error(output):
                print(
                    f"[RETRY] {backend} worker failed (attempt {attempt}/{max_retries + 1}), "
                    f"retrying in {retry_backoff}s...",
                    file=sys.stderr,
                )
                time.sleep(retry_backoff)
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("run_backend_prompt_with_retry: unexpected exit")


def write_fallback_result(
    *,
    result_path: Path,
    kp: Keypoint,
    error_type: str,
    message: str,
    step: str,
) -> None:
    fallback = {
        "keypoint_id": kp.keypoint_id,
        "category": kp.category,
        "description": kp.description,
        "prestate": kp.prestate,
        "instruction": kp.instruction,
        "expected": kp.expected,
        "actual_before_state": "No validated pre-action observation is available because the keypoint worker did not complete successfully.",
        "actual_after_state": "No validated post-action observation is available because the keypoint worker did not complete successfully.",
        "status": "INCOMPLETE",
        "result": "INCOMPLETE",
        "passed": False,
        "success": False,
        "confidence": 0,
        "reasoning": [
            f"Execution issue prevented a full verdict for keypoint {kp.keypoint_id}.",
            f"Failure step: {step}.",
            f"Error type: {error_type}.",
        ],
        "explanation": (
            f"INCOMPLETE judgment. The runner could not finish this keypoint because "
            f"{error_type} occurred during {step}: {message}"
        ),
        "error": {
            "type": error_type,
            "message": message,
            "step": step,
        },
        "state_verification": None,
        "visual_verification": None,
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(fallback, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def summarize_state_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = " ".join(value.split())
        return text[:1000]
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        text = str(value)
    text = " ".join(text.split())
    return text[:1000]


def normalize_test_result_artifacts(test_result_path: Path) -> None:
    if not test_result_path.exists():
        return
    try:
        data = json.loads(test_result_path.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(data, dict):
        return

    screenshots = data.get("screenshots")
    if not isinstance(screenshots, dict):
        return
    sequence = screenshots.get("sequence")
    if not isinstance(sequence, dict):
        return
    frame_times = sequence.get("frame_times_ms")
    if not isinstance(frame_times, list):
        return

    normalized: List[int] = []
    previous = 0
    changed = False
    for index, value in enumerate(frame_times):
        try:
            current = int(round(float(value)))
        except Exception:
            current = previous
            changed = True
        if current < 0:
            current = 0
            changed = True
        if index == 0 and current != 0:
            current = 0
            changed = True
        if index > 0 and current < previous:
            current = previous
            changed = True
        if value != current:
            changed = True
        normalized.append(current)
        previous = current

    if changed:
        sequence["frame_times_ms"] = normalized
        test_result_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_test_config_contract_fields(*, test_config_path: Path, kp: Keypoint, game_url: str) -> None:
    data: Dict[str, object] = {}
    if test_config_path.exists():
        try:
            loaded = json.loads(test_config_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}

    changed = False

    if data.get("game_url") != game_url:
        data["game_url"] = game_url
        changed = True

    for field_name in ("precondition_state", "expected_state"):
        value = data.get(field_name)
        if not isinstance(value, dict):
            data[field_name] = {}
            changed = True

    interaction = data.get("interaction")
    if not isinstance(interaction, dict):
        interaction = {"actions": []}
        data["interaction"] = interaction
        changed = True
    elif not isinstance(interaction.get("actions"), list):
        interaction["actions"] = []
        changed = True

    verification_contract = data.get("verification_contract")
    if not isinstance(verification_contract, dict):
        verification_contract = {}
        data["verification_contract"] = verification_contract
        changed = True

    for field_name in ("precondition_checks", "required_observations", "forbidden_observations"):
        top_level = data.get(field_name)
        nested = verification_contract.get(field_name)
        normalized = top_level if isinstance(top_level, list) else nested if isinstance(nested, list) else []
        if data.get(field_name) != normalized:
            data[field_name] = normalized
            changed = True
        if verification_contract.get(field_name) != normalized:
            verification_contract[field_name] = normalized
            changed = True

    if not isinstance(verification_contract.get("decision_rule"), str) or not str(
        verification_contract.get("decision_rule", "")
    ).strip():
        verification_contract["decision_rule"] = "all required, none forbidden"
        changed = True

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
        data["metadata"] = metadata
        changed = True
    for field_name, field_value in {
        "keypoint_id": kp.keypoint_id,
        "category": kp.category,
        "description": kp.description,
    }.items():
        if metadata.get(field_name) != field_value:
            metadata[field_name] = field_value
            changed = True

    if changed or not test_config_path.exists():
        test_config_path.parent.mkdir(parents=True, exist_ok=True)
        test_config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _normalize_legacy_result_schema(data: Dict[str, object]) -> bool:
    """Translate alternative schemas (legacy worker outputs that emit
    verdict/verification fields) into canonical fields
    (passed/state_verification/reasoning/explanation). Returns True if changed.
    Idempotent and conservative: never overrides existing canonical values.
    """
    if not isinstance(data, dict):
        return False
    changed = False
    verdict = data.get("verdict")
    if isinstance(verdict, str):
        v = verdict.strip().upper()
        if not isinstance(data.get("passed"), bool):
            if v in {"PASS", "TRUE", "OK", "SUCCESS"}:
                data["passed"] = True
                changed = True
            elif v in {"FAIL", "FAILED", "FALSE", "FAILURE"}:
                data["passed"] = False
                changed = True
        canonical_status = str(data.get("status", "")).strip().upper()
        if canonical_status not in {"PASS", "FAIL", "INCOMPLETE"}:
            if v in {"PASS", "TRUE", "OK", "SUCCESS"}:
                data["status"] = "PASS"
                changed = True
            elif v in {"FAIL", "FAILED", "FALSE", "FAILURE"}:
                data["status"] = "FAIL"
                changed = True
    if "state_verification" not in data or data.get("state_verification") in (None, {}, ""):
        verification = data.get("verification")
        if isinstance(verification, dict) and verification:
            data["state_verification"] = verification
            changed = True
    reasoning = data.get("reasoning")
    if not isinstance(reasoning, list) or not [r for r in reasoning if str(r).strip()]:
        bits: List[str] = []
        ver = data.get("state_verification") or data.get("verification")
        if isinstance(ver, dict):
            notes = ver.get("notes")
            if isinstance(notes, str) and notes.strip():
                bits.append(notes.strip())
            for k in ("stageChanged", "scoreIncreased", "isWin", "passed"):
                if k in ver:
                    bits.append(f"{k}={ver[k]}")
        for k in ("actual_before_state", "actual_after_state", "expected", "instruction"):
            v = data.get(k)
            if isinstance(v, str) and v.strip() and not v.strip().startswith("No validated"):
                bits.append(f"{k}: {v.strip()}")
                break
        if not bits:
            bits.append("No structured reasoning captured by worker; verdict inferred from verdict/verification.")
        data["reasoning"] = bits
        changed = True
    explanation = data.get("explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        verdict_text = str(data.get("verdict", data.get("status", ""))).strip() or "UNKNOWN"
        ver = data.get("state_verification") or data.get("verification") or {}
        notes = ""
        if isinstance(ver, dict):
            n = ver.get("notes")
            if isinstance(n, str) and n.strip():
                notes = n.strip()
        if notes:
            data["explanation"] = f"Worker reported {verdict_text}. {notes}"
        else:
            data["explanation"] = f"Worker reported {verdict_text}."
        changed = True
    return changed


def ensure_result_contract_fields(*, result_path: Path, test_result_path: Path, kp: Keypoint) -> None:
    if not result_path.exists():
        return
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(data, dict):
        return

    if _normalize_legacy_result_schema(data):
        result_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    test_data: Dict[str, object] = {}
    if test_result_path.exists():
        try:
            loaded = json.loads(test_result_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                test_data = loaded
        except Exception:
            test_data = {}

    before_candidates = [
        test_data.get("actual_before_state"),
        test_data.get("before_state"),
        test_data.get("pre_action_state"),
        test_data.get("injected_state"),
        test_data.get("initial_state"),
    ]
    after_candidates = [
        test_data.get("actual_after_state"),
        test_data.get("after_state"),
        test_data.get("finalState"),
        test_data.get("final_state"),
    ]

    def first_summary(candidates: List[object], fallback: str) -> str:
        for candidate in candidates:
            text = summarize_state_text(candidate)
            if text:
                return text
        return fallback

    changed = False
    if not isinstance(data.get("prestate"), str) or not str(data.get("prestate", "")).strip():
        data["prestate"] = kp.prestate
        changed = True
    if not isinstance(data.get("instruction"), str) or not str(data.get("instruction", "")).strip():
        data["instruction"] = kp.instruction
        changed = True
    if not isinstance(data.get("expected"), str) or not str(data.get("expected", "")).strip():
        data["expected"] = kp.expected
        changed = True
    if not isinstance(data.get("actual_before_state"), str) or not str(data.get("actual_before_state", "")).strip():
        data["actual_before_state"] = first_summary(
            before_candidates,
            "No validated pre-action runtime snapshot is available.",
        )
        changed = True
    if not isinstance(data.get("actual_after_state"), str) or not str(data.get("actual_after_state", "")).strip():
        data["actual_after_state"] = first_summary(
            after_candidates,
            "No validated post-action runtime snapshot is available.",
        )
        changed = True
    if "visual_verification" not in data:
        data["visual_verification"] = None
        changed = True
    if data.get("error") is None and "state_verification" not in data:
        data["state_verification"] = None
        changed = True

    if changed:
        result_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_worker_prompt(
    *,
    workspace: Path,
    game_name: str,
    run_id: str,
    kp: Keypoint,
    game_url: str,
    screenshot_mode: str,
    screenshot_interval: int,
) -> str:
    output_dir = keypoint_output_dir(game_name=game_name, run_id=run_id, keypoint_id=kp.keypoint_id)
    return (
        "You are running one normal-mode keypoint test. "
        "Run directly in this session (do not use sub-agents). "
        "Follow the keypoint-tester workflow: first `generative-state-construction`, "
        "then `short-interaction-verification`.\n\n"
        "Hard browser constraint:\n"
        "- Use only Playwright-bundled Chromium in headless mode\n"
        "- Use `chromium.launch({ headless: true })`\n"
        "- Do not use `channel`\n"
        "- Do not use `executablePath`\n"
        "- Do not fall back to system Chrome, Edge, Brave, or any other installed browser\n"
        "- If bundled Chromium launch fails, write `INCOMPLETE` with the browser launch error\n"
        "- In `test_result.json`, `screenshots.sequence.frame_times_ms` must be non-negative integers and start with `0`\n"
        "- Use a monotonic elapsed timer for screenshot/sample timings; do not rely on raw `Date.now()` differences that can go backward\n\n"
        f"Ownership: only produce artifacts under `{output_dir}`.\n"
        "You are not alone in this codebase. Do not revert others' edits.\n\n"
        "Parameters:\n"
        f"game_name={game_name}\n"
        f"keypoint_id={kp.keypoint_id}\n"
        f"category={kp.category}\n"
        f"description={kp.description}\n"
        f"output_dir={output_dir}\n"
        f"game_url={game_url}\n"
        f"project_root={workspace}\n"
        f"screenshot_mode={screenshot_mode}\n"
        f"screenshot_interval={screenshot_interval}\n"
        f"prestate={kp.prestate}\n"
        f"instruction={kp.instruction}\n"
        f"expected={kp.expected}\n\n"
        "At the end, ensure `result.json` exists in the output_dir and print one-line status."
    )


def build_batch_worker_prompt(
    *,
    workspace: Path,
    game_name: str,
    run_id: str,
    batch_id: int,
    keypoints: List[Keypoint],
    game_url: str,
    screenshot_mode: str,
    screenshot_interval: int,
) -> str:
    lines = [
        f"You are running a batch of {len(keypoints)} normal-mode keypoint tests in one session.",
        "Run directly in this session. Do not use sub-agents.",
        "Process the keypoints sequentially in the exact order listed below.",
        "For each keypoint, follow the keypoint-tester workflow:",
        "1. Run `generative-state-construction` for that keypoint.",
        "2. Run `short-interaction-verification` for that keypoint.",
        "3. Write artifacts only inside that keypoint's output_dir.",
        "4. Ensure `result.json` exists in that output_dir before moving on.",
        "5. If one keypoint fails or is incomplete, continue to the next keypoint instead of stopping the batch.",
        "",
        "Hard browser constraint:",
        "- Use only Playwright-bundled Chromium in headless mode",
        "- Use `chromium.launch({ headless: true })`",
        "- Do not use `channel`",
        "- Do not use `executablePath`",
        "- Do not fall back to system Chrome, Edge, Brave, or any other installed browser",
        "- If bundled Chromium launch fails, write `INCOMPLETE` with the browser launch error",
        "- In `test_result.json`, `screenshots.sequence.frame_times_ms` must be non-negative integers and start with `0`",
        "- Use a monotonic elapsed timer for screenshot/sample timings; do not rely on raw `Date.now()` differences that can go backward",
        "",
        f"Batch metadata:",
        f"- batch_id={batch_id}",
        f"- game_name={game_name}",
        f"- game_url={game_url}",
        f"- project_root={workspace}",
        f"- screenshot_mode={screenshot_mode}",
        f"- screenshot_interval={screenshot_interval}",
        "",
        "Ownership constraints:",
        "- You are not alone in this codebase. Do not revert others' edits.",
        "- Only touch the output directories listed below.",
        "",
        "Keypoints:",
    ]

    for index, kp in enumerate(keypoints, start=1):
        output_dir = keypoint_output_dir(game_name=game_name, run_id=run_id, keypoint_id=kp.keypoint_id)
        lines.extend(
            [
                f"### Keypoint {index}/{len(keypoints)}",
                f"keypoint_id={kp.keypoint_id}",
                f"category={kp.category}",
                f"description={kp.description}",
                f"output_dir={output_dir}",
                f"prestate={kp.prestate}",
                f"instruction={kp.instruction}",
                f"expected={kp.expected}",
                "",
            ]
        )

    lines.extend(
        [
            "After finishing the batch, print one short line per keypoint with its status, then a final batch summary line.",
        ]
    )
    return "\n".join(lines)


def batch_log_stem(keypoints: List[Keypoint]) -> str:
    first_id = keypoints[0].keypoint_id
    last_id = keypoints[-1].keypoint_id
    if first_id == last_id:
        return f"keypoint_{first_id}"
    return f"batch_{first_id}_{last_id}"


def batch_timeout(per_keypoint_timeout: int, batch_size: int) -> int:
    size = max(1, int(batch_size))
    return max(per_keypoint_timeout, per_keypoint_timeout * size + 180)


def get_result_status(result_path: Path) -> str:
    if not result_path.exists():
        return "INCOMPLETE"
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception:
        return "INCOMPLETE"
    return resolve_result_status(data)


def get_result_error_type(result_path: Path) -> str:
    if not result_path.exists():
        return "missing_result"
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception:
        return "invalid_result_json"
    error = data.get("error")
    if isinstance(error, dict):
        return str(error.get("type", "")).strip()
    return ""


def existing_result_keypoint_ids(run_dir: Path) -> Set[str]:
    ids: Set[str] = set()
    for path in run_dir.glob("keypoint_*/result.json"):
        m = re.search(r"keypoint_(\d+)", str(path.parent.name))
        if m:
            ids.add(m.group(1))
    return ids


RESUMABLE_INCOMPLETE_ERROR_TYPES = {
    "",
    "worker_execution_error",
    "missing_result",
    "missing_test_result",
    "page_load_error",
    "action_execution_error",
    "invalid_result_json",
}


def keypoints_are_stale(description_path: Path, keypoints_path: Path) -> bool:
    if not keypoints_path.exists():
        return True
    if not keypoint_policy_is_current_file(keypoints_path):
        return True
    return description_path.stat().st_mtime > keypoints_path.stat().st_mtime


def lint_keypoints_file(
    workspace: Path,
    keypoints_path: Path,
    *,
    timeout: int,
    log_path: Path,
) -> subprocess.CompletedProcess:
    cmd = [
        "python3",
        str(LINT_KEYPOINTS_SCRIPT),
        "--keypoints-file",
        str(keypoints_path),
    ]
    return run_cmd(cmd, cwd=workspace, timeout=timeout, log_path=log_path, check=False)


def refresh_keypoints_with_quality_gate(
    workspace: Path,
    *,
    backend: str,
    game_name: str,
    model: str,
    reasoning_effort: str,
    step_timeout: int,
    log_path: Path,
) -> int:
    cmd = [
        "python3",
        str(DISTILL_KEYPOINTS_SCRIPT),
        "--games",
        game_name,
        "--backend",
        backend,
        "--reasoning-effort",
        reasoning_effort,
        "--timeout",
        str(step_timeout),
        "--max-attempts",
        "2",
    ]
    if model:
        cmd.extend(["--model", model])
    outer_timeout = max(step_timeout * 3, step_timeout + 300)
    proc = run_cmd(cmd, cwd=workspace, timeout=outer_timeout, log_path=log_path, check=False)
    return proc.returncode


def snapshot_keypoints_file(source_path: Path, snapshot_path: Path) -> None:
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")


def keypoint_needs_execution_on_resume(run_dir: Path, kp: Keypoint) -> bool:
    result_path = run_dir / f"keypoint_{kp.keypoint_id}" / "result.json"
    if not result_path.exists():
        return True
    status = get_result_status(result_path)
    if status in {"PASS", "FAIL"}:
        return False
    error_type = get_result_error_type(result_path)
    return error_type in RESUMABLE_INCOMPLETE_ERROR_TYPES


def resolve_result_status(data: Dict[str, object]) -> str:
    status = str(data.get("status", "")).strip().upper()
    if status in {"PASS", "FAIL", "INCOMPLETE"}:
        return status
    error = data.get("error")
    if isinstance(error, dict) and str(error.get("type", "")).strip() == "visual_evidence_insufficient":
        return "INCOMPLETE"
    ok = data.get("passed")
    if ok is True:
        return "PASS"
    if ok is False:
        return "FAIL"
    return "INCOMPLETE"


def resolve_result_detail(data: Dict[str, object]) -> str:
    explanation = data.get("explanation")
    if isinstance(explanation, str) and explanation.strip():
        return explanation.strip()
    error = data.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    reasoning = data.get("reasoning")
    if isinstance(reasoning, list):
        items = [str(item).strip() for item in reasoning if str(item).strip()]
        if items:
            return " ".join(items)
    return ""


PLACEHOLDER_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7+F7YAAAAASUVORK5CYII="
)


def ensure_minimal_keypoint_contract_artifacts(keypoint_dir: Path, kp: Keypoint, game_url: str) -> None:
    keypoint_dir.mkdir(parents=True, exist_ok=True)

    test_config_path = keypoint_dir / "test_config.json"
    ensure_test_config_contract_fields(test_config_path=test_config_path, kp=kp, game_url=game_url)

    test_script_path = keypoint_dir / "test_script.mjs"
    if not test_script_path.exists():
        test_script_path.write_text(
            "// Placeholder test script generated by run_normal_eval.py\n",
            encoding="utf-8",
        )

    test_result_path = keypoint_dir / "test_result.json"
    if not test_result_path.exists():
        test_result = {
            "success": False,
            "before_state": None,
            "after_state": None,
            "error": {
                "type": "missing_test_result",
                "message": "test_result.json missing; placeholder generated by runner",
            },
        }
        test_result_path.write_text(json.dumps(test_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    screenshots_dir = keypoint_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    for name in ("before.png", "after.png"):
        p = screenshots_dir / name
        if not p.exists():
            p.write_bytes(PLACEHOLDER_PNG)


def collect_result_contract_failures(run_dir: Path, keypoints: List[Keypoint]) -> List[str]:
    failures: List[str] = []
    for kp in keypoints:
        result_path = run_dir / f"keypoint_{kp.keypoint_id}" / "result.json"
        if not result_path.exists():
            failures.append(f"keypoint_{kp.keypoint_id}: missing result.json")
            continue
        try:
            data = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"keypoint_{kp.keypoint_id}: invalid result.json ({exc})")
            continue
        if not isinstance(data.get("passed"), bool):
            failures.append(f"keypoint_{kp.keypoint_id}: result.json missing boolean 'passed'")
        reasoning = data.get("reasoning")
        if not isinstance(reasoning, list) or not reasoning:
            failures.append(f"keypoint_{kp.keypoint_id}: result.json missing non-empty 'reasoning'")
        explanation = data.get("explanation")
        if not isinstance(explanation, str) or not explanation.strip():
            failures.append(f"keypoint_{kp.keypoint_id}: result.json missing non-empty 'explanation'")
    return failures


def repair_keypoint_artifacts_for_validation(
    *,
    run_dir: Path,
    keypoints: List[Keypoint],
    game_name: str,
    run_id: str,
    game_url: str,
) -> None:
    for kp in keypoints:
        keypoint_dir = run_dir / f"keypoint_{kp.keypoint_id}"
        ensure_minimal_keypoint_contract_artifacts(keypoint_dir, kp, game_url)
        normalize_test_result_artifacts(keypoint_dir / "test_result.json")
        ensure_result_contract_fields(
            result_path=keypoint_dir / "result.json",
            test_result_path=keypoint_dir / "test_result.json",
            kp=kp,
        )
        screenshots_dir = keypoint_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        for name in ("before.png", "after.png"):
            path = screenshots_dir / name
            if not path.exists():
                path.write_bytes(PLACEHOLDER_PNG)


def write_reports(run_dir: Path, keypoints: List[Keypoint]) -> None:
    rows = []
    passed = 0
    failed = 0
    incomplete = 0

    for kp in keypoints:
        kp_dir = run_dir / f"keypoint_{kp.keypoint_id}"
        result_path = kp_dir / "result.json"
        status = "INCOMPLETE"
        confidence = "-"
        detail = "missing result.json"

        if result_path.exists():
            try:
                data = json.loads(result_path.read_text(encoding="utf-8"))
                status = resolve_result_status(data)
                confidence = str(data.get("confidence", "-"))
                detail = resolve_result_detail(data)
                if status == "PASS":
                    passed += 1
                elif status == "FAIL":
                    failed += 1
                else:
                    incomplete += 1
            except Exception as exc:
                status = "INCOMPLETE"
                detail = f"invalid result.json: {exc}"
                incomplete += 1
        else:
            incomplete += 1

        rows.append((kp.keypoint_id, kp.description, status, confidence, detail))

    total = len(keypoints)
    pass_rate = (passed / total * 100.0) if total else 0.0

    summary_lines = [
        "# Keypoint Verification Summary",
        "",
        "## Overview",
        f"- Game: {run_dir.parent.name}",
        f"- Run ID: {run_dir.name}",
        f"- Total Keypoints: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- Incomplete: {incomplete}",
        f"- Pass Rate: {pass_rate:.1f}%",
        "",
        "## Detailed Results",
    ]
    for kid, desc, status, conf, detail in rows:
        summary_lines.append(f"- Keypoint {kid}: {status} (confidence={conf}) - {desc}")
        if detail:
            summary_lines.append(f"  - Detail: {detail}")
    (run_dir / "summary_report.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    eval_lines = [
        f"# Evaluation Report: {run_dir.parent.name}",
        "",
        "## Summary",
        f"- Total: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- Incomplete: {incomplete}",
        f"- Pass Rate: {pass_rate:.1f}%",
        "",
        "## Results",
        "| Keypoint | Status | Confidence | Detail |",
        "|---|---|---:|---|",
    ]
    for kid, _, status, conf, detail in rows:
        detail_clean = detail.replace("\n", " ").strip()
        eval_lines.append(f"| {kid} | {status} | {conf} | {detail_clean} |")
    (run_dir / "evaluation_report.md").write_text("\n".join(eval_lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run direct normal evaluation without multi-agent orchestration.")
    p.add_argument("--workspace", required=True, help=f"Workspace root path containing {DESCRIPTION_DIRNAME}/, games/, .codex/")
    p.add_argument("--game-name", required=True, help="Game name, e.g. tetris")
    p.add_argument("--run-id", default=f"manual_normal_{now_ts()}", help="Output run id under runs/{game}/")
    p.add_argument("--backend", choices=["codex", "claude"], default="codex")
    p.add_argument("--model", default="", help="Optional model override")
    p.add_argument("--reasoning-effort", default="high", choices=["low", "medium", "high", "xhigh"], help="Backend reasoning effort")
    p.add_argument("--step-timeout", type=int, default=2400, help="Timeout seconds for each backend session (covers all keypoints in --keypoints-per-session). Default 2400 fits 5 keypoints @ ~7min each.")
    p.add_argument(
        "--screenshot-mode",
        default="sequence",
        choices=["standard", "sequence"],
        help="Screenshot capture mode for interaction verification",
    )
    p.add_argument(
        "--screenshot-interval",
        type=int,
        default=200,
        help="Interval in ms when --screenshot-mode=sequence",
    )
    p.add_argument(
        "--only-keypoints",
        default="",
        help="Optional comma-separated keypoint IDs to run, e.g. 4,7,9. When omitted, run all keypoints.",
    )
    p.add_argument(
        "--retry-incomplete-timeout",
        type=int,
        default=0,
        help="Timeout seconds for the automatic in-run retry of retryable INCOMPLETE keypoints. 0 disables the retry pass.",
    )
    p.add_argument(
        "--retry-incomplete-screenshot-mode",
        default="standard",
        choices=["standard", "sequence"],
        help="Screenshot mode used for the automatic retry pass on retryable INCOMPLETE keypoints.",
    )
    p.add_argument(
        "--worker-max-retries",
        type=int,
        default=0,
        help="Max retries per keypoint worker on transient backend failures (default 0: one attempt only).",
    )
    p.add_argument(
        "--worker-retry-backoff",
        type=int,
        default=15,
        help="Backoff seconds between keypoint worker retries.",
    )
    p.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="Max parallel keypoint workers (concurrent backend calls).",
    )
    p.add_argument(
        "--keypoints-per-session",
        type=int,
        default=1,
        help="Number of keypoints processed sequentially inside one backend session.",
    )
    p.add_argument(
        "--refresh-keypoints",
        action="store_true",
        help=f"Force re-distillation from {DESCRIPTION_DIRNAME}/{{game}}.md before evaluation.",
    )
    p.add_argument(
        "--resume-run",
        action="store_true",
        help="Resume an existing run_id by skipping completed keypoints and reusing keypoints.snapshot.md when present.",
    )
    p.add_argument(
        "--keypoints-md",
        default="",
        help="Override path to keypoints.md (default: games/<game>/keypoints.md). Used by ablation runs that supply alternate keypoint files (e.g. coarse keypoints).",
    )
    p.add_argument(
        "--min-keypoints",
        type=int,
        default=DEFAULT_MIN_KEYPOINT_COUNT,
        help=f"Minimum keypoint count gate (default: {DEFAULT_MIN_KEYPOINT_COUNT}). Lower for ablation runs that use coarse keypoint files.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    backend = normalize_backend(args.backend)
    ensure_backend_available(backend)
    workspace = Path(args.workspace).resolve()
    game_name = args.game_name
    run_id = args.run_id
    run_dir = workspace / "runs" / game_name / run_id
    log_dir = run_dir / "logs"

    ensure_inputs(workspace, game_name)

    if run_dir.exists() and any(run_dir.iterdir()) and not args.resume_run:
        raise RuntimeError(
            f"Run directory already exists: {run_dir}. "
            "Choose a new --run-id or pass --resume-run to continue the existing run."
        )

    run_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    current_description_path = description_path(game_name, workspace)
    if args.keypoints_md.strip():
        kp_override = Path(args.keypoints_md).expanduser()
        if not kp_override.is_absolute():
            kp_override = (workspace / kp_override).resolve()
        if not kp_override.exists():
            raise FileNotFoundError(f"--keypoints-md path does not exist: {kp_override}")
        workspace_keypoints_md = kp_override
    else:
        workspace_keypoints_md = workspace / "games" / game_name / "keypoints.md"
    snapshot_keypoints_md = run_dir / "keypoints.snapshot.md"

    use_snapshot = args.resume_run and snapshot_keypoints_md.exists()
    if not use_snapshot and not args.refresh_keypoints and workspace_keypoints_md.exists():
        lint_proc = lint_keypoints_file(
            workspace,
            workspace_keypoints_md,
            timeout=min(180, args.step_timeout),
            log_path=log_dir / "00_lint_existing.log",
        )
        if lint_proc.returncode != 0:
            print(
                "Existing keypoints failed the quality gate; forcing regeneration with the current policy.",
                file=sys.stderr,
            )
            args.refresh_keypoints = True

    if not use_snapshot and (args.refresh_keypoints or keypoints_are_stale(current_description_path, workspace_keypoints_md)):
        try:
            rc = refresh_keypoints_with_quality_gate(
                workspace,
                backend=backend,
                game_name=game_name,
                model=args.model,
                reasoning_effort=args.reasoning_effort,
                step_timeout=args.step_timeout,
                log_path=log_dir / "00_distill.log",
            )
        except RuntimeError as exc:
            if is_quota_exceeded(str(exc)):
                (run_dir / "pause_state.json").write_text(
                    json.dumps(
                        {
                            "status": "PAUSED",
                            "reason": "quota_exceeded",
                            "retry_after_hint": extract_retry_after_hint(str(exc)),
                            "message": str(exc),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                print("Paused before keypoint execution due to quota exhaustion.", file=sys.stderr)
                return PAUSED_RETURN_CODE
            raise
        if rc == PAUSED_RETURN_CODE:
            (run_dir / "pause_state.json").write_text(
                json.dumps(
                    {
                        "status": "PAUSED",
                        "reason": "quota_exceeded",
                        "message": "Keypoint distillation paused before execution.",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            print("Paused before keypoint execution due to keypoint distillation pause.", file=sys.stderr)
            return PAUSED_RETURN_CODE
        if rc != 0:
            raise RuntimeError(
                f"Keypoint distillation failed for {game_name}. See {log_dir / '00_distill.log'}."
            )

    if use_snapshot:
        keypoints_md = snapshot_keypoints_md
    else:
        if not workspace_keypoints_md.exists():
            raise FileNotFoundError(f"Missing keypoints file: {workspace_keypoints_md}")
        lint_proc = lint_keypoints_file(
            workspace,
            workspace_keypoints_md,
            timeout=min(180, args.step_timeout),
            log_path=log_dir / "00_lint_final.log",
        )
        if lint_proc.returncode != 0:
            raise RuntimeError(
                f"Keypoints quality gate failed for {workspace_keypoints_md}. "
                f"See {log_dir / '00_lint_final.log'}."
            )
        snapshot_keypoints_file(workspace_keypoints_md, snapshot_keypoints_md)
        keypoints_md = snapshot_keypoints_md

    enforce_min_keypoint_count(workspace, keypoints_md, minimum=args.min_keypoints)
    all_keypoints = parse_keypoints(keypoints_md)
    selected_keypoints = all_keypoints
    if args.only_keypoints.strip():
        requested = {
            token.strip()
            for token in args.only_keypoints.split(",")
            if token.strip()
        }
        selected_keypoints = [kp for kp in selected_keypoints if kp.keypoint_id in requested]
        if not selected_keypoints:
            raise RuntimeError(
                f"--only-keypoints requested {sorted(requested)} but none matched parsed keypoints"
            )

    keypoints = selected_keypoints
    if args.resume_run:
        keypoints = [
            kp for kp in selected_keypoints
            if keypoint_needs_execution_on_resume(run_dir, kp)
        ]
        skipped = len(selected_keypoints) - len(keypoints)
        if skipped:
            print(
                f"[RESUME] Reusing {skipped} completed keypoints from existing run artifacts.",
                file=sys.stderr,
            )

    lifecycle = workspace / ".codex" / "skills" / "auto-eval" / "scripts" / "dev_server_lifecycle.sh"
    if not lifecycle.exists():
        raise FileNotFoundError(f"Missing lifecycle script: {lifecycle}")

    started_server = False
    server_pid = ""
    server_state_file = ""
    game_url = ""
    worker_execution_failures = 0
    worker_missing_result_failures = 0
    validation_failed = False
    contract_failures: List[str] = []
    quota_error_message = ""

    try:
        start_proc = start_server_with_recovery(
            workspace=workspace,
            lifecycle=lifecycle,
            game_name=game_name,
            log_path=log_dir / "01_server_start.log",
        )
        env_map = parse_assignments(start_proc.stdout or "")
        started_server = env_map.get("STARTED_SERVER", "0") == "1"
        server_pid = env_map.get("SERVER_PID", "")
        server_state_file = env_map.get("SERVER_STATE_FILE", "")
        game_url = env_map.get("GAME_URL", "")
        if not game_url:
            raise RuntimeError("Failed to resolve GAME_URL from dev_server_lifecycle.sh start output.")

        def run_single_keypoint(kp, *, screenshot_mode_override=None, step="run_worker") -> Dict:
            """Run a single keypoint worker. Returns a result dict for thread-safe aggregation."""
            sm = screenshot_mode_override or args.screenshot_mode
            keypoint_dir = run_dir / f"keypoint_{kp.keypoint_id}"
            ensure_minimal_keypoint_contract_artifacts(keypoint_dir, kp, game_url)
            prompt = build_worker_prompt(
                workspace=workspace,
                game_name=game_name,
                run_id=run_id,
                kp=kp,
                game_url=game_url,
                screenshot_mode=sm,
                screenshot_interval=args.screenshot_interval,
            )
            worker_error: Optional[str] = None
            try:
                run_backend_prompt_with_retry(
                    workspace,
                    backend=backend,
                    prompt=prompt,
                    model=args.model,
                    reasoning_effort=args.reasoning_effort,
                    timeout=args.step_timeout if step == "run_worker" else args.retry_incomplete_timeout,
                    log_path=log_dir / f"keypoint_{kp.keypoint_id}.log" if step == "run_worker" else log_dir / f"keypoint_{kp.keypoint_id}.retry.log",
                    max_retries=args.worker_max_retries,
                    retry_backoff=args.worker_retry_backoff,
                    system_prompt=worker_system_prompt(workspace),
                )
            except QuotaExceededError:
                raise
            except Exception as exc:
                worker_error = str(exc)
                worker_log = log_dir / f"keypoint_{kp.keypoint_id}.log" if step == "run_worker" else log_dir / f"keypoint_{kp.keypoint_id}.retry.log"
                worker_log.parent.mkdir(parents=True, exist_ok=True)
                with worker_log.open("a", encoding="utf-8") as f:
                    f.write("\n\n[runner_error]\n")
                    f.write(worker_error)
                    f.write("\n")

            result_json = run_dir / f"keypoint_{kp.keypoint_id}" / "result.json"
            if not result_json.exists():
                if worker_error:
                    write_fallback_result(
                        result_path=result_json, kp=kp,
                        error_type="worker_execution_error", message=worker_error, step=step,
                    )
                else:
                    write_fallback_result(
                        result_path=result_json, kp=kp,
                        error_type="missing_result", message="result.json missing after worker execution", step=step,
                    )
            normalize_test_result_artifacts(keypoint_dir / "test_result.json")
            ensure_result_contract_fields(
                result_path=result_json,
                test_result_path=keypoint_dir / "test_result.json",
                kp=kp,
            )
            return {
                "kp_id": kp.keypoint_id,
                "worker_error": worker_error,
                "has_result": (keypoint_dir / "result.json").exists(),
            }

        def run_keypoint_batch(batch: List[Keypoint], *, batch_id: int, screenshot_mode_override=None, step="run_worker") -> List[Dict[str, object]]:
            """Run one backend session over several keypoints sequentially."""
            sm = screenshot_mode_override or args.screenshot_mode
            for kp in batch:
                ensure_minimal_keypoint_contract_artifacts(
                    run_dir / f"keypoint_{kp.keypoint_id}",
                    kp,
                    game_url,
                )

            prompt = build_batch_worker_prompt(
                workspace=workspace,
                game_name=game_name,
                run_id=run_id,
                batch_id=batch_id,
                keypoints=batch,
                game_url=game_url,
                screenshot_mode=sm,
                screenshot_interval=args.screenshot_interval,
            )
            log_name = batch_log_stem(batch)
            worker_error: Optional[str] = None
            try:
                per_keypoint_timeout = args.step_timeout if step == "run_worker" else args.retry_incomplete_timeout
                run_backend_prompt_with_retry(
                    workspace,
                    backend=backend,
                    prompt=prompt,
                    model=args.model,
                    reasoning_effort=args.reasoning_effort,
                    timeout=batch_timeout(per_keypoint_timeout, len(batch)),
                    log_path=log_dir / f"{log_name}.log" if step == "run_worker" else log_dir / f"{log_name}.retry.log",
                    max_retries=args.worker_max_retries,
                    retry_backoff=args.worker_retry_backoff,
                    system_prompt=worker_system_prompt(workspace),
                )
            except QuotaExceededError:
                raise
            except Exception as exc:
                worker_error = str(exc)
                worker_log = log_dir / f"{log_name}.log" if step == "run_worker" else log_dir / f"{log_name}.retry.log"
                worker_log.parent.mkdir(parents=True, exist_ok=True)
                with worker_log.open("a", encoding="utf-8") as f:
                    f.write("\n\n[runner_error]\n")
                    f.write(worker_error)
                    f.write("\n")

            results: List[Dict[str, object]] = []
            for kp in batch:
                keypoint_dir = run_dir / f"keypoint_{kp.keypoint_id}"
                result_json = keypoint_dir / "result.json"
                if not result_json.exists():
                    if worker_error:
                        write_fallback_result(
                            result_path=result_json,
                            kp=kp,
                            error_type="worker_execution_error",
                            message=worker_error,
                            step=step,
                        )
                    else:
                        write_fallback_result(
                            result_path=result_json,
                            kp=kp,
                            error_type="missing_result",
                            message="result.json missing after batch worker execution",
                            step=step,
                        )
                normalize_test_result_artifacts(keypoint_dir / "test_result.json")
                ensure_result_contract_fields(
                    result_path=result_json,
                    test_result_path=keypoint_dir / "test_result.json",
                    kp=kp,
                )
                results.append(
                    {
                        "kp_id": kp.keypoint_id,
                        "worker_error": worker_error,
                        "has_result": result_json.exists(),
                    }
                )
            return results

        max_workers = max(1, args.max_workers)
        keypoints_per_session = max(1, args.keypoints_per_session)
        initial_batches = chunk_keypoints(keypoints, keypoints_per_session)
        quota_exceeded = False
        if initial_batches:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {
                    pool.submit(run_keypoint_batch, batch, batch_id=batch_index): batch
                    for batch_index, batch in enumerate(initial_batches, start=1)
                }
                for future in concurrent.futures.as_completed(futures):
                    batch = futures[future]
                    try:
                        batch_results = future.result()
                        for result in batch_results:
                            if result["worker_error"]:
                                worker_execution_failures += 1
                            if not result["has_result"]:
                                worker_missing_result_failures += 1
                    except QuotaExceededError as exc:
                        quota_exceeded = True
                        quota_error_message = str(exc) or "quota exceeded during initial keypoint worker pass"
                        for f in futures:
                            f.cancel()
                        break
                    except Exception as exc:
                        worker_execution_failures += len(batch)
                        batch_label = ",".join(kp.keypoint_id for kp in batch)
                        print(f"[ERROR] keypoint batch [{batch_label}] thread failed: {exc}", file=sys.stderr)

        if quota_exceeded:
            print("[FATAL] Codex API quota exceeded. Halting run (reports will still be generated for completed keypoints).", file=sys.stderr)
        else:
            retryable_error_types = {
                "worker_execution_error",
                "missing_result",
                "page_load_error",
                "action_execution_error",
                "visual_evidence_insufficient",
            }
            retry_candidates = [
                kp
                for kp in selected_keypoints
                if get_result_status(run_dir / f"keypoint_{kp.keypoint_id}" / "result.json") == "INCOMPLETE"
                and get_result_error_type(run_dir / f"keypoint_{kp.keypoint_id}" / "result.json") in retryable_error_types
            ]

            if retry_candidates and args.retry_incomplete_timeout > 0:
                print(f"[INFO] Retrying {len(retry_candidates)} INCOMPLETE keypoints...", file=sys.stderr)
                retry_batches = chunk_keypoints(retry_candidates, keypoints_per_session)
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
                    futures = {
                        pool.submit(
                            run_keypoint_batch,
                            batch,
                            batch_id=batch_index,
                            screenshot_mode_override=args.retry_incomplete_screenshot_mode,
                            step="retry_run_worker",
                        ): batch
                        for batch_index, batch in enumerate(retry_batches, start=1)
                    }
                    for future in concurrent.futures.as_completed(futures):
                        batch = futures[future]
                        try:
                            batch_results = future.result()
                            for result in batch_results:
                                if result["worker_error"]:
                                    worker_execution_failures += 1
                                if not result["has_result"]:
                                    worker_missing_result_failures += 1
                        except QuotaExceededError as exc:
                            quota_exceeded = True
                            quota_error_message = str(exc) or "quota exceeded during retry keypoint worker pass"
                            for f in futures:
                                f.cancel()
                            break
                        except Exception as exc:
                            worker_execution_failures += len(batch)
                            batch_label = ",".join(kp.keypoint_id for kp in batch)
                            print(f"[ERROR] retry keypoint batch [{batch_label}] thread failed: {exc}", file=sys.stderr)

        # Always generate reports, even if quota was exceeded
        report_keypoints = selected_keypoints
        if args.only_keypoints.strip():
            existing_ids = existing_result_keypoint_ids(run_dir)
            selected_ids = {kp.keypoint_id for kp in selected_keypoints}
            if existing_ids - selected_ids:
                report_keypoints = all_keypoints

        repair_keypoint_artifacts_for_validation(
            run_dir=run_dir,
            keypoints=report_keypoints,
            game_name=game_name,
            run_id=run_id,
            game_url=game_url,
        )

        contract_failures = collect_result_contract_failures(run_dir, report_keypoints)
        write_reports(run_dir, report_keypoints)

        validation_proc = run_cmd(
            [
                "python3",
                str(workspace / ".codex" / "skills" / "keypoint-orchestrator" / "scripts" / "validate_artifacts.py"),
                "--repo-root",
                str(workspace),
                "--game-name",
                game_name,
                "--run-id",
                run_id,
                "--test-mode",
                "normal",
                "--expected-keypoint-count",
                str(len(report_keypoints)),
                "--json-output",
                str(run_dir / "validation_report.json"),
            ],
            cwd=workspace,
            timeout=120,
            log_path=log_dir / "99_validate.log",
            check=False,
        )
        validation_failed = validation_proc.returncode != 0

    finally:
        if started_server or server_pid or server_state_file:
            stop_cmd = [str(lifecycle), "stop"]
            if server_state_file:
                stop_cmd.extend(["--state-file", server_state_file])
            if server_pid:
                stop_cmd.extend(["--server-pid", server_pid])
            try:
                run_cmd(
                    stop_cmd,
                    cwd=workspace,
                    timeout=60,
                    log_path=log_dir / "02_server_stop.log",
                    check=False,
                )
            except Exception:
                pass

    print(f"Run dir: {run_dir}")
    print(f"Summary: {run_dir / 'summary_report.md'}")
    print(f"Evaluation: {run_dir / 'evaluation_report.md'}")
    print(f"Validation: {run_dir / 'validation_report.json'}")
    if quota_exceeded:
        completed_keypoints = sorted(existing_result_keypoint_ids(run_dir), key=int)
        pending_keypoints = sorted(
            [
                kp.keypoint_id
                for kp in selected_keypoints
                if keypoint_needs_execution_on_resume(run_dir, kp)
            ],
            key=int,
        )
        (run_dir / "pause_state.json").write_text(
            json.dumps(
                {
                    "status": "PAUSED",
                    "reason": "quota_exceeded",
                    "retry_after_hint": extract_retry_after_hint(quota_error_message),
                    "message": quota_error_message or "quota exceeded during keypoint execution",
                    "run_id": run_id,
                    "completed_keypoints": completed_keypoints,
                    "pending_keypoints": pending_keypoints,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print("Run paused due to quota exhaustion. Resume later from the same suite/execution root.", file=sys.stderr)
        return PAUSED_RETURN_CODE
    pause_state_path = run_dir / "pause_state.json"
    if pause_state_path.exists():
        pause_state_path.unlink()
    if worker_execution_failures or worker_missing_result_failures or validation_failed or contract_failures:
        print(
            "Execution issues: "
            f"worker_failures={worker_execution_failures}, "
            f"missing_results={worker_missing_result_failures}, "
            f"contract_failures={len(contract_failures)}, "
            f"validation_failed={validation_failed}",
            file=sys.stderr,
        )
        for failure in contract_failures:
            print(f"Contract failure: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
