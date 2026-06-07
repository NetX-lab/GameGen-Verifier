#!/usr/bin/env python3
"""Run direct cross-verification on an existing evaluation run."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import shlex
import shutil
import subprocess
import sys
import time
from functools import lru_cache
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from harness.quota_control import PAUSED_RETURN_CODE, extract_retry_after_hint, is_quota_exceeded_text
from harness.agent_runner import build_agent_cmd, ensure_backend_available, normalize_backend
from harness.runner_utils import run_and_capture


@dataclass
class RecheckTarget:
    keypoint_id: str
    category: str
    description: str
    keypoint_dir: Path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


@lru_cache(maxsize=None)
def load_skill_text(workspace_root: str, skill_name: str) -> str:
    path = Path(workspace_root) / ".codex" / "skills" / skill_name / "SKILL.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def recheck_system_prompt(workspace: Path) -> str:
    return load_skill_text(str(workspace), "cross-verification")


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


_RETRYABLE_ERRORS = [
    "stream disconnected before completion",
    "Transport error:",
    "Reconnecting...",
    "We're currently experiencing high demand",
    "connection reset",
    "ECONNRESET",
]


def _is_retryable(output: str) -> bool:
    return any(ind in output for ind in _RETRYABLE_ERRORS)


class QuotaExceededError(Exception):
    """Raised when backend quota is exceeded and the recheck should pause."""
    pass


def timeout_output_text(exc: subprocess.TimeoutExpired) -> str:
    output = exc.output or ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return str(output)


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
            if attempt > 1:
                try:
                    log_path.write_text(attempt_log.read_text(encoding="utf-8"), encoding="utf-8")
                except Exception:
                    pass
            return proc
        except subprocess.TimeoutExpired as exc:
            last_exc = exc
            output = timeout_output_text(exc)
            if is_quota_exceeded_text(output):
                raise QuotaExceededError(output)
            if attempt <= max_retries:
                print(
                    f"[RETRY] {backend} recheck worker timed out (attempt {attempt}/{max_retries + 1}), "
                    f"retrying in {retry_backoff}s...",
                    file=sys.stderr,
                )
                time.sleep(retry_backoff)
                continue
            raise
        except RuntimeError as exc:
            last_exc = exc
            output = str(exc)
            if is_quota_exceeded_text(output):
                raise QuotaExceededError(output)
            if attempt <= max_retries and _is_retryable(output):
                print(
                    f"[RETRY] {backend} recheck worker failed (attempt {attempt}/{max_retries + 1}), "
                    f"retrying in {retry_backoff}s...",
                    file=sys.stderr,
                )
                time.sleep(retry_backoff)
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("run_backend_prompt_with_retry: unexpected exit")


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def short_text(value: Any, *, max_len: int = 240) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    text = " ".join(text.split())
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def normalize_confidence(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(max(0, min(100, value)))
    return 0


def normalize_reasoning(value: Any) -> List[str]:
    if isinstance(value, list):
        items = [short_text(item) for item in value]
    elif isinstance(value, str):
        items = [short_text(value)]
    else:
        items = []
    return [item for item in items if item][:5]


def normalize_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "pass"}:
            return True
        if lowered in {"false", "0", "no", "n", "fail"}:
            return False
    return None


def bool_for_status(status: str) -> Optional[bool]:
    if status == "PASS":
        return True
    if status == "FAIL":
        return False
    return None


def resolve_original_status(result: Dict[str, Any]) -> str:
    status = str(result.get("status", "")).strip().upper()
    if status in {"PASS", "FAIL", "INCOMPLETE"}:
        return status
    error = result.get("error")
    if isinstance(error, dict):
        err_type = str(error.get("type", "")).strip()
        if err_type == "visual_evidence_insufficient" or err_type in {
            "page_load_error",
            "game_init_error",
            "action_execution_error",
            "state_retrieval_error",
            "worker_execution_error",
            "missing_result",
            "missing_test_result",
        }:
            return "INCOMPLETE"
    explanation = str(result.get("explanation", "")).strip().lower()
    if explanation.startswith("incomplete judgment"):
        return "INCOMPLETE"
    passed = normalize_bool(result.get("passed"))
    if passed is True:
        return "PASS"
    if passed is False:
        return "FAIL"
    return "INCOMPLETE"


def resolve_recheck_status(recheck_result: Dict[str, Any]) -> str:
    status = str(recheck_result.get("status", "")).strip().upper()
    if status in {"PASS", "FAIL", "INCOMPLETE"}:
        return status
    error = recheck_result.get("error")
    if isinstance(error, dict):
        err_type = str(error.get("type", "")).strip()
        if err_type == "visual_evidence_insufficient":
            return "INCOMPLETE"
        if err_type:
            return "INCOMPLETE"
    passed = normalize_bool(recheck_result.get("passed"))
    if passed is True:
        return "PASS"
    if passed is False:
        return "FAIL"
    return "INCOMPLETE"


def infer_verification_mode(keypoint_dir: Path, result: Dict[str, Any]) -> str:
    mode = str(result.get("verification_mode", "")).strip()
    if mode:
        return mode
    return "normal"


def required_recheck_artifacts(keypoint_dir: Path) -> List[str]:
    required = [
        keypoint_dir / "result.json",
        keypoint_dir / "test_result.json",
        keypoint_dir / "screenshots" / "before.png",
        keypoint_dir / "screenshots" / "after.png",
    ]
    missing = [str(path.relative_to(keypoint_dir)) for path in required if not path.exists()]
    if not (keypoint_dir / "test_config.json").exists():
        missing.append("test_config.json")
    return missing


def build_conflict_analysis(
    *,
    original_status: str,
    original_confidence: int,
    recheck_status: str,
    recheck_confidence: int,
    explanation_hint: str = "",
) -> Dict[str, Any]:
    confidence_delta = abs(original_confidence - recheck_confidence)
    if original_status != recheck_status:
        if {original_status, recheck_status} == {"PASS", "FAIL"} and min(original_confidence, recheck_confidence) >= 70:
            severity = "high"
        elif "INCOMPLETE" in {original_status, recheck_status}:
            severity = "medium"
        else:
            severity = "medium"
        explanation = explanation_hint.strip() or (
            f"Original status {original_status} conflicts with recheck status {recheck_status}."
        )
        return {
            "type": "status_mismatch",
            "severity": severity,
            "explanation": explanation,
            "confidence_delta": confidence_delta,
        }

    if confidence_delta > 30:
        severity = "medium" if confidence_delta > 50 else "low"
        explanation = explanation_hint.strip() or (
            f"Both runs concluded {original_status}, but confidence differs by {confidence_delta} points."
        )
        return {
            "type": "confidence_divergence",
            "severity": severity,
            "explanation": explanation,
            "confidence_delta": confidence_delta,
        }

    explanation = explanation_hint.strip() or (
        f"Original and recheck both concluded {original_status} without significant confidence divergence."
    )
    return {
        "type": "no_conflict",
        "severity": "none",
        "explanation": explanation,
        "confidence_delta": confidence_delta,
    }


def summarize_conflict_buckets(conflicts: List[Dict[str, Any]]) -> Dict[str, int]:
    buckets = {
        "pass_fail_flips": 0,
        "evidence_downgrades": 0,
        "confidence_divergences": 0,
    }
    for item in conflicts:
        original_status = str(item.get("original", {}).get("status", "INCOMPLETE")).upper()
        recheck_status = str(item.get("recheck", {}).get("status", "INCOMPLETE")).upper()
        conflict_type = str(item.get("type", "no_conflict"))
        if {original_status, recheck_status} == {"PASS", "FAIL"}:
            buckets["pass_fail_flips"] += 1
        elif original_status != recheck_status and "INCOMPLETE" in {original_status, recheck_status}:
            buckets["evidence_downgrades"] += 1
        elif conflict_type == "confidence_divergence":
            buckets["confidence_divergences"] += 1
    return buckets


def normalize_recheck_result(keypoint_dir: Path, keypoint_id: str) -> Dict[str, Any]:
    result_path = keypoint_dir / "result.json"
    recheck_path = keypoint_dir / "recheck_result.json"
    original = load_json(result_path)
    recheck_doc = load_json(recheck_path)

    original_status = resolve_original_status(original)
    original_confidence = normalize_confidence(original.get("confidence"))
    verification_mode = infer_verification_mode(keypoint_dir, original)

    nested = recheck_doc.get("recheck_result")
    nested = nested if isinstance(nested, dict) else {}
    recheck_status = resolve_recheck_status(nested if nested else recheck_doc)
    recheck_confidence = normalize_confidence(nested.get("confidence", recheck_doc.get("confidence")))

    reasoning = normalize_reasoning(nested.get("reasoning", recheck_doc.get("reasoning")))
    if not reasoning:
        reasoning = [
            f"Original status was {original_status} with confidence {original_confidence}.",
            f"Fresh recheck status is {recheck_status} with confidence {recheck_confidence}.",
            "The detailed evidence available in artifacts was insufficiently structured, so this normalized summary was generated by the runner.",
        ]

    explanation = nested.get("explanation", recheck_doc.get("explanation"))
    if not isinstance(explanation, str) or not explanation.strip():
        explanation = (
            f"{recheck_status} judgment. The recheck runner normalized the result from existing artifacts under "
            f"{keypoint_dir.name} and compared it against the original {original_status} outcome."
        )
    else:
        explanation = explanation.strip()

    existing_conflict = recheck_doc.get("conflict_analysis")
    existing_conflict = existing_conflict if isinstance(existing_conflict, dict) else {}
    conflict_analysis = build_conflict_analysis(
        original_status=original_status,
        original_confidence=original_confidence,
        recheck_status=recheck_status,
        recheck_confidence=recheck_confidence,
        explanation_hint=str(existing_conflict.get("explanation", "")),
    )
    normalized = {
        "keypoint_id": str(keypoint_id),
        "recheck_timestamp": recheck_doc.get("recheck_timestamp") or utc_now_iso(),
        "original_result": {
            "status": original_status,
            "passed": bool_for_status(original_status),
            "confidence": original_confidence,
            "verification_mode": verification_mode,
        },
        "recheck_result": {
            "status": recheck_status,
            "passed": bool_for_status(recheck_status),
            "confidence": recheck_confidence,
            "reasoning": reasoning,
            "explanation": explanation,
        },
        "conflict": conflict_analysis["type"] != "no_conflict",
        "conflict_analysis": conflict_analysis,
    }
    recheck_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return normalized


def write_incomplete_recheck_result(
    *,
    keypoint_dir: Path,
    keypoint_id: str,
    reason: str,
) -> Dict[str, Any]:
    original = load_json(keypoint_dir / "result.json")
    original_status = resolve_original_status(original)
    original_confidence = normalize_confidence(original.get("confidence"))
    verification_mode = infer_verification_mode(keypoint_dir, original)
    explanation = f"INCOMPLETE judgment. {reason}"
    conflict_analysis = build_conflict_analysis(
        original_status=original_status,
        original_confidence=original_confidence,
        recheck_status="INCOMPLETE",
        recheck_confidence=0,
        explanation_hint=explanation,
    )
    doc = {
        "keypoint_id": str(keypoint_id),
        "recheck_timestamp": utc_now_iso(),
        "original_result": {
            "status": original_status,
            "passed": bool_for_status(original_status),
            "confidence": original_confidence,
            "verification_mode": verification_mode,
        },
        "recheck_result": {
            "status": "INCOMPLETE",
            "passed": None,
            "confidence": 0,
            "reasoning": [
                f"Recheck could not reach a fresh verdict for keypoint {keypoint_id}.",
                reason,
                "The original artifacts remain unchanged and should be inspected manually.",
            ],
            "explanation": explanation,
        },
        "conflict": conflict_analysis["type"] != "no_conflict",
        "conflict_analysis": conflict_analysis,
    }
    (keypoint_dir / "recheck_result.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return doc


def find_targets(run_dir: Path) -> List[RecheckTarget]:
    dirs = [path for path in run_dir.glob("keypoint_*") if path.is_dir()]

    def sort_key(path: Path) -> tuple[int, str]:
        match = re.search(r"keypoint_(\d+)$", path.name)
        if match:
            return (int(match.group(1)), path.name)
        return (10**9, path.name)

    targets: List[RecheckTarget] = []
    for keypoint_dir in sorted(dirs, key=sort_key):
        match = re.search(r"keypoint_(\d+)$", keypoint_dir.name)
        keypoint_id = match.group(1) if match else keypoint_dir.name
        result = load_json(keypoint_dir / "result.json")
        targets.append(
            RecheckTarget(
                keypoint_id=keypoint_id,
                category=str(result.get("category", "")).strip(),
                description=str(result.get("description", "")).strip() or keypoint_dir.name,
                keypoint_dir=keypoint_dir,
            )
        )
    return targets


def existing_recheck_status(keypoint_dir: Path) -> str:
    data = load_json(keypoint_dir / "recheck_result.json")
    if not data:
        return ""
    nested = data.get("recheck_result")
    if isinstance(nested, dict):
        return resolve_recheck_status(nested)
    return resolve_recheck_status(data)


def target_needs_recheck(target: RecheckTarget) -> bool:
    status = existing_recheck_status(target.keypoint_dir)
    if not status:
        return True
    return status == "INCOMPLETE"


def chunk_targets(targets: List[RecheckTarget], chunk_size: int) -> List[List[RecheckTarget]]:
    size = max(1, int(chunk_size))
    return [targets[i:i + size] for i in range(0, len(targets), size)]


def batch_log_stem(targets: List[RecheckTarget]) -> str:
    first_id = targets[0].keypoint_id
    last_id = targets[-1].keypoint_id
    if first_id == last_id:
        return f"recheck_keypoint_{first_id}"
    return f"recheck_batch_{first_id}_{last_id}"


def batch_timeout(per_target_timeout: int, batch_size: int) -> int:
    size = max(1, int(batch_size))
    return max(per_target_timeout, per_target_timeout * size + 120)


def build_recheck_prompt(
    *,
    workspace: Path,
    game_name: str,
    targets: List[RecheckTarget],
) -> str:
    lines = [
        f"You are rechecking a batch of {len(targets)} completed keypoint evaluations in one session.",
        "Run directly in this session. Do not use sub-agents.",
        "Use the `cross-verification` skill for each target.",
        "Process targets sequentially in the exact order listed below.",
        "Do not rerun Playwright, do not modify original artifacts, and only write `recheck_result.json` under each output_dir.",
        "If one target cannot be rechecked, write an INCOMPLETE recheck_result.json for that target and continue to the next target.",
        "",
        "Hard requirements for each target:",
        "- Read only existing evidence from result.json, test_result.json, test_config.json, and screenshots.",
        "- Do not use jq; it is not available in this environment. Use Node.js or Python for structured inspection.",
        "- Produce a fresh verdict with status PASS, FAIL, or INCOMPLETE.",
        "- Include 3-5 reasoning bullets and a complete natural-language explanation.",
        "- Compare the fresh verdict with the original verdict and describe any conflict.",
        "",
        "Ownership constraints:",
        "- You are not alone in this codebase. Do not revert others' edits.",
        "- Only touch the output directories listed below.",
        "",
        f"game_name={game_name}",
        f"project_root={workspace}",
        "",
        "Targets:",
    ]
    for index, target in enumerate(targets, start=1):
        lines.extend(
            [
                f"### Target {index}/{len(targets)}",
                f"keypoint_id={target.keypoint_id}",
                f"category={target.category}",
                f"description={target.description}",
                f"output_dir={target.keypoint_dir.relative_to(workspace)}/",
                "",
            ]
        )
    lines.append("At the end, print one short line per keypoint with its recheck status, then a final batch summary line.")
    return "\n".join(lines)


def write_reports(run_dir: Path, targets: List[RecheckTarget]) -> None:
    comparison_items: List[Dict[str, Any]] = []
    agreements: List[int] = []
    conflicts: List[Dict[str, Any]] = []
    recheck_pass = 0
    recheck_fail = 0
    recheck_incomplete = 0

    for target in targets:
        data = load_json(target.keypoint_dir / "recheck_result.json")
        if not data:
            data = write_incomplete_recheck_result(
                keypoint_dir=target.keypoint_dir,
                keypoint_id=target.keypoint_id,
                reason="recheck_result.json was missing when the comparison report was generated.",
            )

        original = data.get("original_result", {})
        recheck = data.get("recheck_result", {})
        conflict_analysis = data.get("conflict_analysis", {})
        status = str(recheck.get("status", "INCOMPLETE")).upper()
        if status == "PASS":
            recheck_pass += 1
        elif status == "FAIL":
            recheck_fail += 1
        else:
            recheck_incomplete += 1

        item = {
            "keypoint_id": str(target.keypoint_id),
            "category": target.category,
            "description": target.description,
            "type": str(conflict_analysis.get("type", "no_conflict")),
            "severity": str(conflict_analysis.get("severity", "none")),
            "original": {
                "status": str(original.get("status", "INCOMPLETE")),
                "passed": original.get("passed"),
                "confidence": normalize_confidence(original.get("confidence")),
            },
            "recheck": {
                "status": str(recheck.get("status", "INCOMPLETE")),
                "passed": recheck.get("passed"),
                "confidence": normalize_confidence(recheck.get("confidence")),
            },
            "explanation": str(conflict_analysis.get("explanation", "")).strip(),
        }
        comparison_items.append(item)

        if data.get("conflict"):
            conflicts.append(item)
        else:
            try:
                agreements.append(int(target.keypoint_id))
            except ValueError:
                continue

    high_severity = sum(1 for item in conflicts if item["severity"] == "high")
    medium_severity = sum(1 for item in conflicts if item["severity"] == "medium")
    low_severity = sum(1 for item in conflicts if item["severity"] == "low")
    buckets = summarize_conflict_buckets(conflicts)
    total = len(targets)
    comparison = {
        "summary": {
            "total_keypoints": total,
            "recheck_pass": recheck_pass,
            "recheck_fail": recheck_fail,
            "recheck_incomplete": recheck_incomplete,
            "agreements": len(agreements),
            "conflicts": len(conflicts),
            "conflict_rate": (len(conflicts) / total) if total else 0.0,
            "high_severity": high_severity,
            "medium_severity": medium_severity,
            "low_severity": low_severity,
            "pass_fail_flips": buckets["pass_fail_flips"],
            "pass_fail_flip_rate": (buckets["pass_fail_flips"] / total) if total else 0.0,
            "evidence_downgrades": buckets["evidence_downgrades"],
            "evidence_downgrade_rate": (buckets["evidence_downgrades"] / total) if total else 0.0,
            "confidence_divergences": buckets["confidence_divergences"],
            "confidence_divergence_rate": (buckets["confidence_divergences"] / total) if total else 0.0,
        },
        "conflicts": conflicts,
        "agreements": agreements,
    }
    (run_dir / "recheck_comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"# Cross-Verification Report: {run_dir.parent.name}",
        "",
        f"Run ID: {run_dir.name}",
        f"Recheck Date: {utc_now_iso()}",
        "",
        "## Summary",
        f"- Total Keypoints: {total}",
        f"- Recheck PASS: {recheck_pass}",
        f"- Recheck FAIL: {recheck_fail}",
        f"- Recheck INCOMPLETE: {recheck_incomplete}",
        f"- Agreements: {len(agreements)}",
        f"- Conflicts: {len(conflicts)}",
        f"- Conflict Rate: {comparison['summary']['conflict_rate']:.2%}",
        f"- PASS<->FAIL Flips: {buckets['pass_fail_flips']} ({comparison['summary']['pass_fail_flip_rate']:.2%})",
        f"- FAIL/PASS <-> INCOMPLETE: {buckets['evidence_downgrades']} ({comparison['summary']['evidence_downgrade_rate']:.2%})",
        f"- Confidence Divergences: {buckets['confidence_divergences']} ({comparison['summary']['confidence_divergence_rate']:.2%})",
        f"- High Severity: {high_severity}",
        f"- Medium Severity: {medium_severity}",
        f"- Low Severity: {low_severity}",
        "",
        "## Conflicts",
    ]
    if not conflicts:
        lines.append("- No conflicts detected.")
    else:
        for item in conflicts:
            lines.extend(
                [
                    f"### Keypoint {item['keypoint_id']}: [{item['category']}] {item['description']}",
                    f"- Type: {item['type']}",
                    f"- Severity: {item['severity']}",
                    (
                        f"- Original: {item['original']['status']} "
                        f"(confidence={item['original']['confidence']})"
                    ),
                    (
                        f"- Recheck: {item['recheck']['status']} "
                        f"(confidence={item['recheck']['confidence']})"
                    ),
                    f"- Explanation: {item['explanation']}",
                    f"- Artifact: keypoint_{item['keypoint_id']}/recheck_result.json",
                    "",
                ]
            )

    lines.append("## Agreements")
    if agreements:
        lines.append("- Keypoints: " + ", ".join(str(item) for item in agreements))
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Per-Keypoint Recheck Status")
    for item in comparison_items:
        lines.append(
            f"- Keypoint {item['keypoint_id']}: original={item['original']['status']} -> "
            f"recheck={item['recheck']['status']} "
            f"(conflict={item['type'] != 'no_conflict'})"
        )

    (run_dir / "recheck_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run direct recheck on an existing evaluation run.")
    parser.add_argument("--workspace", required=True, help="Workspace root path containing runs/ and .codex/")
    parser.add_argument("--game-name", required=True, help="Game name, e.g. tetris")
    parser.add_argument("--run-id", required=True, help="Existing run id under runs/{game_name}/")
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=1,
        help="Max concurrent recheck workers within a single game run.",
    )
    parser.add_argument("--backend", choices=["codex", "claude"], default="codex")
    parser.add_argument("--model", default="", help="Optional model override")
    parser.add_argument("--reasoning-effort", default="high", choices=["low", "medium", "high", "xhigh"], help="Backend reasoning effort")
    parser.add_argument("--step-timeout", type=int, default=600, help="Timeout seconds for each recheck worker call")
    parser.add_argument(
        "--keypoints-per-session",
        type=int,
        default=5,
        help="Number of keypoints rechecked sequentially inside one backend session.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend = normalize_backend(args.backend)
    workspace = Path(args.workspace).resolve()
    run_dir = workspace / "runs" / args.game_name / args.run_id

    try:
        ensure_backend_available(backend)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not run_dir.exists():
        raise FileNotFoundError(f"Missing run directory: {run_dir}")
    if not (run_dir / "summary_report.md").exists():
        raise FileNotFoundError(f"Missing summary_report.md under: {run_dir}")

    log_dir = run_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    targets = find_targets(run_dir)
    if not targets:
        raise RuntimeError(f"No keypoint_* directories found under: {run_dir}")

    pending_targets = [target for target in targets if target_needs_recheck(target)]
    skipped_targets = len(targets) - len(pending_targets)
    if skipped_targets:
        print(
            f"[RESUME] Reusing {skipped_targets} completed recheck results from existing artifacts.",
            file=sys.stderr,
        )

    worker_failures = 0
    missing_recheck_results = 0
    paused = False
    pause_message = ""
    max_concurrent = max(1, args.max_concurrent)
    keypoints_per_session = max(1, args.keypoints_per_session)

    def run_single_target(target: RecheckTarget) -> Dict[str, int]:
        missing = required_recheck_artifacts(target.keypoint_dir)
        if missing:
            write_incomplete_recheck_result(
                keypoint_dir=target.keypoint_dir,
                keypoint_id=target.keypoint_id,
                reason=(
                    "Recheck could not start because required artifacts are missing: "
                    + ", ".join(missing)
                ),
            )
            normalize_recheck_result(target.keypoint_dir, target.keypoint_id)
            return {"worker_failures": 0, "missing_recheck_results": 0}

        prompt = (
            "You are rechecking one completed keypoint evaluation. "
            "Run directly in this session (do not use sub-agents). "
            "Use the `cross-verification` skill. "
            "Do not rerun Playwright, do not modify original artifacts, and only write "
            "`recheck_result.json` under the output_dir.\n\n"
            f"Ownership: only produce artifacts under `{target.keypoint_dir}`.\n"
            "You are not alone in this codebase. Do not revert others' edits.\n\n"
            "Hard requirements:\n"
            "- Read only existing evidence from result.json, test_result.json, test_config.json, and screenshots.\n"
            "- Do not use jq; it is not available in this environment. Use Node.js or Python for any structured inspection.\n"
            "- Produce a fresh verdict with status PASS, FAIL, or INCOMPLETE.\n"
            "- Include 3-5 reasoning bullets and a complete natural-language explanation.\n"
            "- Compare the fresh verdict with the original verdict and describe any conflict.\n\n"
            "Parameters:\n"
            f"game_name={args.game_name}\n"
            f"keypoint_id={target.keypoint_id}\n"
            f"output_dir={target.keypoint_dir.relative_to(workspace)}/\n"
            f"project_root={workspace}\n\n"
            "At the end, ensure `recheck_result.json` exists in output_dir and print one-line status."
        )

        worker_error: Optional[str] = None
        try:
            run_backend_prompt_with_retry(
                workspace,
                backend=backend,
                prompt=prompt,
                model=args.model,
                reasoning_effort=args.reasoning_effort,
                timeout=args.step_timeout,
                log_path=log_dir / f"recheck_keypoint_{target.keypoint_id}.log",
                system_prompt=recheck_system_prompt(workspace),
            )
        except QuotaExceededError:
            raise
        except Exception as exc:
            worker_error = str(exc)
            worker_log = log_dir / f"recheck_keypoint_{target.keypoint_id}.log"
            with worker_log.open("a", encoding="utf-8") as handle:
                handle.write("\n\n[runner_error]\n")
                handle.write(worker_error)
                handle.write("\n")

        recheck_path = target.keypoint_dir / "recheck_result.json"
        missing_count = 0
        if not recheck_path.exists():
            missing_count = 1
            reason = "recheck_result.json missing after worker execution"
            if worker_error:
                reason = f"Worker execution error prevented recheck completion: {worker_error}"
            write_incomplete_recheck_result(
                keypoint_dir=target.keypoint_dir,
                keypoint_id=target.keypoint_id,
                reason=reason,
            )

        normalize_recheck_result(target.keypoint_dir, target.keypoint_id)
        return {
            "worker_failures": 1 if worker_error else 0,
            "missing_recheck_results": missing_count,
        }

    def run_target_batch(batch: List[RecheckTarget]) -> Dict[str, int]:
        ready_targets: List[RecheckTarget] = []
        worker_failures_local = 0
        missing_recheck_results_local = 0

        for target in batch:
            missing = required_recheck_artifacts(target.keypoint_dir)
            if missing:
                write_incomplete_recheck_result(
                    keypoint_dir=target.keypoint_dir,
                    keypoint_id=target.keypoint_id,
                    reason=(
                        "Recheck could not start because required artifacts are missing: "
                        + ", ".join(missing)
                    ),
                )
                normalize_recheck_result(target.keypoint_dir, target.keypoint_id)
            else:
                ready_targets.append(target)

        if not ready_targets:
            return {
                "worker_failures": worker_failures_local,
                "missing_recheck_results": missing_recheck_results_local,
            }

        prompt = build_recheck_prompt(
            workspace=workspace,
            game_name=args.game_name,
            targets=ready_targets,
        )
        worker_error: Optional[str] = None
        log_path = log_dir / f"{batch_log_stem(ready_targets)}.log"
        try:
            run_backend_prompt_with_retry(
                workspace,
                backend=backend,
                prompt=prompt,
                model=args.model,
                reasoning_effort=args.reasoning_effort,
                timeout=batch_timeout(args.step_timeout, len(ready_targets)),
                log_path=log_path,
                system_prompt=recheck_system_prompt(workspace),
            )
        except QuotaExceededError:
            raise
        except Exception as exc:
            worker_error = str(exc)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write("\n\n[runner_error]\n")
                handle.write(worker_error)
                handle.write("\n")

        for target in ready_targets:
            recheck_path = target.keypoint_dir / "recheck_result.json"
            if not recheck_path.exists():
                missing_recheck_results_local += 1
                reason = "recheck_result.json missing after batch worker execution"
                if worker_error:
                    reason = f"Worker execution error prevented recheck completion: {worker_error}"
                write_incomplete_recheck_result(
                    keypoint_dir=target.keypoint_dir,
                    keypoint_id=target.keypoint_id,
                    reason=reason,
                )
            normalize_recheck_result(target.keypoint_dir, target.keypoint_id)

        if worker_error:
            worker_failures_local += len(ready_targets)
        return {
            "worker_failures": worker_failures_local,
            "missing_recheck_results": missing_recheck_results_local,
        }

    if pending_targets:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as pool:
            batches = chunk_targets(pending_targets, keypoints_per_session)
            futures = {pool.submit(run_target_batch, batch): batch for batch in batches}
            for future in concurrent.futures.as_completed(futures):
                batch = futures[future]
                try:
                    result = future.result()
                    worker_failures += int(result.get("worker_failures", 0) or 0)
                    missing_recheck_results += int(result.get("missing_recheck_results", 0) or 0)
                except QuotaExceededError as exc:
                    paused = True
                    pause_message = str(exc)
                    for other in futures:
                        other.cancel()
                    break
                except Exception as exc:
                    worker_failures += len(batch)
                    worker_error = str(exc)
                    worker_log = log_dir / f"{batch_log_stem(batch)}.log"
                    with worker_log.open("a", encoding="utf-8") as handle:
                        handle.write("\n\n[runner_error]\n")
                        handle.write(worker_error)
                        handle.write("\n")
                    for target in batch:
                        write_incomplete_recheck_result(
                            keypoint_dir=target.keypoint_dir,
                            keypoint_id=target.keypoint_id,
                            reason=f"Worker execution error prevented recheck completion: {worker_error}",
                        )
                        normalize_recheck_result(target.keypoint_dir, target.keypoint_id)

    write_reports(run_dir, targets)

    print(f"Run dir: {run_dir}")
    print(f"Recheck summary: {run_dir / 'recheck_summary.md'}")
    print(f"Recheck comparison: {run_dir / 'recheck_comparison.json'}")
    if paused:
        (run_dir / "recheck_pause_state.json").write_text(
            json.dumps(
                {
                    "status": "PAUSED",
                    "reason": "quota_exceeded",
                    "retry_after_hint": extract_retry_after_hint(pause_message),
                    "message": pause_message,
                    "pending_keypoints": [target.keypoint_id for target in pending_targets if target_needs_recheck(target)],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print("Recheck paused due to quota exhaustion. Resume later from the same run directory.", file=sys.stderr)
        return PAUSED_RETURN_CODE
    pause_state_path = run_dir / "recheck_pause_state.json"
    if pause_state_path.exists():
        pause_state_path.unlink()
    if worker_failures or missing_recheck_results:
        print(
            "Recheck execution issues: "
            f"worker_failures={worker_failures}, "
            f"missing_recheck_results={missing_recheck_results}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
