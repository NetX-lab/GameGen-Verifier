#!/usr/bin/env python3
"""Batch-regenerate specification-first keypoints with quality gating."""

from __future__ import annotations

import argparse
import concurrent.futures
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from common.game_catalog import description_dir, description_relpath, list_description_games
from common.keypoint_policy import (
    DEFAULT_MAX_WEAK_SHARE,
    DEFAULT_MIN_HARD_SHARE,
    DEFAULT_MIN_KEYPOINT_COUNT,
    DEFAULT_MIN_MULTI_STEP_SHARE,
    DEFAULT_MIN_PER_CATEGORY,
    DEFAULT_MIN_STRONG_CUE_SHARE,
    DEFAULT_TARGET_KEYPOINT_MAX,
    DEFAULT_TARGET_KEYPOINT_MIN,
    KEYPOINT_POLICY_HEADER,
)
from harness.agent_runner import build_agent_cmd, ensure_backend_available, normalize_backend
from harness.quota_control import PAUSED_RETURN_CODE, extract_retry_after_hint, is_quota_exceeded_text
from harness.runner_utils import run_and_capture


DESCRIPTIONS_DIR = description_dir(REPO_ROOT)
LINT_SCRIPT = REPO_ROOT / "scripts" / "prepare" / "lint_keypoints.py"
SKILL_PROMPT_PATH = REPO_ROOT / ".codex" / "skills" / "distill-verified-keypoints" / "SKILL.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate keypoints with stronger extraction constraints.")
    parser.add_argument("--games", nargs="*", help="Specific game names. Default: all descriptions.")
    parser.add_argument("--backend", choices=["codex", "claude"], default="codex")
    parser.add_argument("--model", default="", help="Optional model override.")
    parser.add_argument("--reasoning-effort", default="high", choices=["low", "medium", "high", "xhigh"])
    parser.add_argument("--timeout", type=int, default=1800, help="Per-attempt timeout in seconds.")
    parser.add_argument("--parallel", type=int, default=1, help="Concurrent distillation workers.")
    parser.add_argument(
        "--min-count",
        type=int,
        default=DEFAULT_MIN_KEYPOINT_COUNT,
        help="Minimum keypoint count required by lint.",
    )
    parser.add_argument("--min-per-category", type=int, default=DEFAULT_MIN_PER_CATEGORY)
    parser.add_argument("--max-weak-share", type=float, default=DEFAULT_MAX_WEAK_SHARE)
    parser.add_argument("--min-strong-cue-share", type=float, default=DEFAULT_MIN_STRONG_CUE_SHARE)
    parser.add_argument("--min-multi-step-share", type=float, default=DEFAULT_MIN_MULTI_STEP_SHARE)
    parser.add_argument("--min-hard-share", type=float, default=DEFAULT_MIN_HARD_SHARE)
    parser.add_argument("--max-attempts", type=int, default=2, help="Total distill attempts per game.")
    parser.add_argument("--continue-on-error", action="store_true")
    return parser.parse_args()


def list_games(explicit: Optional[List[str]]) -> List[str]:
    if explicit:
        return list(explicit)
    return list_description_games(REPO_ROOT)


def read_skill_prompt() -> str:
    return SKILL_PROMPT_PATH.read_text(encoding="utf-8")


def build_backend_cmd(*, backend: str, prompt: str, model: str, reasoning_effort: str, system_prompt: str) -> List[str]:
    return build_agent_cmd(
        repo=REPO_ROOT,
        backend=backend,
        prompt=prompt,
        model=model,
        reasoning_effort=reasoning_effort,
        system_prompt=system_prompt,
        disable_multi_agent=True,
        sandbox="danger-full-access",
        approval="never",
        allowed_dirs=[REPO_ROOT],
    )


def build_prompt(game_name: str, *, lint_feedback: str = "") -> str:
    feedback_block = ""
    if lint_feedback.strip():
        feedback_block = (
            "\nPrevious draft failed quality checks. Rewrite the entire file and address these issues exactly:\n"
            f"{lint_feedback.strip()}\n"
        )
    return (
        f"Use the `distill-verified-keypoints` skill to rewrite `games/{game_name}/keypoints.md` "
        f"from `{description_relpath(game_name)}`.\n"
        "Hard requirements:\n"
        "- Overwrite the full file; do not append.\n"
        f"- The first line must be exactly `{KEYPOINT_POLICY_HEADER}`.\n"
        f"- Use the target description and `skills/distill-verified-keypoints/references/keypoint.md` as the primary sources. Consult files under `games/{game_name}/` only if the description is ambiguous; do not inspect other games' `keypoints.md` files or use other games as templates.\n"
        f"- Target {DEFAULT_TARGET_KEYPOINT_MIN}-{DEFAULT_TARGET_KEYPOINT_MAX} keypoints for a substantial specification.\n"
        "- Keep basic sanity/control-existence checks to a tiny minority.\n"
        "- Prefer specification-specific failure, recovery, persistence, counterexample, and rule-precedence keypoints.\n"
        "- For each core mechanic, usually extract a family of keypoints: one success case, one nearby failure or boundary case, and one persistence/order/precedence/resource-consequence case when the specification supports it.\n"
        "- Pair positive cases with nearby negative or boundary cases whenever possible.\n"
        "- Avoid generic genre checks like simple movement, simple reachability, or basic collectible existence unless they support a harder paired rule.\n"
        "- Headings and expected results should state the invariant, contrast, or consequence explicitly, not just the action being performed.\n"
        "- Every keypoint should be easy to localize into a short-horizon scenario, but semantically hard enough that a shallow implementation could plausibly fail it.\n"
        f"{feedback_block}"
        f"Finish only after `games/{game_name}/keypoints.md` reflects the stronger specification-first set."
    )


def lint_one_game(
    game_name: str,
    *,
    min_count: int,
    min_per_category: int,
    max_weak_share: float,
    min_strong_cue_share: float,
    min_multi_step_share: float,
    min_hard_share: float,
    log_path: Path,
) -> subprocess.CompletedProcess:
    keypoints_path = REPO_ROOT / "games" / game_name / "keypoints.md"
    cmd = [
        "python3",
        str(LINT_SCRIPT),
        "--keypoints-file",
        str(keypoints_path),
        "--min-count",
        str(min_count),
        "--min-per-category",
        str(min_per_category),
        "--max-weak-share",
        str(max_weak_share),
        "--min-strong-cue-share",
        str(min_strong_cue_share),
        "--min-multi-step-share",
        str(min_multi_step_share),
        "--min-hard-share",
        str(min_hard_share),
    ]
    return run_and_capture(cmd, cwd=REPO_ROOT, log_path=log_path, echo_output=False)


def distill_one_game(
    game_name: str,
    *,
    backend: str,
    skill_prompt: str,
    model: str,
    reasoning_effort: str,
    timeout: int,
    min_count: int,
    min_per_category: int,
    max_weak_share: float,
    min_strong_cue_share: float,
    min_multi_step_share: float,
    min_hard_share: float,
    max_attempts: int,
) -> Dict[str, object]:
    desc_path = DESCRIPTIONS_DIR / f"{game_name}.md"
    game_dir = REPO_ROOT / "games" / game_name
    log_dir = game_dir / ".keypoint_log"
    log_dir.mkdir(parents=True, exist_ok=True)
    if not desc_path.exists():
        return {"game": game_name, "status": "ERROR", "error": f"missing description: {desc_path}"}
    if not game_dir.exists():
        return {"game": game_name, "status": "ERROR", "error": f"missing game dir: {game_dir}"}

    lint_feedback = ""
    started = time.time()
    for attempt in range(1, max_attempts + 1):
        print(f"[DISTILL] Starting {game_name} attempt {attempt}/{max_attempts} ...", flush=True)
        prompt = build_prompt(game_name, lint_feedback=lint_feedback)
        cmd = build_backend_cmd(
            backend=backend,
            prompt=prompt,
            model=model,
            reasoning_effort=reasoning_effort,
            system_prompt=skill_prompt,
        )
        codex_log = log_dir / f"distill_attempt_{attempt}.log"
        try:
            proc = run_and_capture(
                cmd,
                cwd=REPO_ROOT,
                timeout=timeout,
                log_path=codex_log,
                log_preamble=f"GAME: {game_name}\nATTEMPT: {attempt}\n\n",
            )
        except subprocess.TimeoutExpired:
            return {
                "game": game_name,
                "status": "TIMEOUT",
                "attempt": attempt,
                "duration_sec": round(time.time() - started, 1),
                "log": str(codex_log),
            }
        except Exception as exc:
            return {
                "game": game_name,
                "status": "ERROR",
                "attempt": attempt,
                "duration_sec": round(time.time() - started, 1),
                "log": str(codex_log),
                "error": str(exc),
            }

        if proc.returncode != 0:
            output = proc.stdout or ""
            if is_quota_exceeded_text(output):
                retry_after_hint = extract_retry_after_hint(output)
                print(f"[DISTILL] PAUSED {game_name} attempt {attempt}", flush=True)
                return {
                    "game": game_name,
                    "status": "PAUSED",
                    "attempt": attempt,
                    "duration_sec": round(time.time() - started, 1),
                    "retry_after_hint": retry_after_hint,
                    "log": str(codex_log),
                }
            print(f"[DISTILL] FAILED {game_name} attempt {attempt} (rc={proc.returncode})", flush=True)
            return {
                "game": game_name,
                "status": "FAILED",
                "attempt": attempt,
                "duration_sec": round(time.time() - started, 1),
                "return_code": proc.returncode,
                "log": str(codex_log),
            }

        lint_log = log_dir / f"lint_attempt_{attempt}.log"
        lint_proc = lint_one_game(
            game_name,
            min_count=min_count,
            min_per_category=min_per_category,
            max_weak_share=max_weak_share,
            min_strong_cue_share=min_strong_cue_share,
            min_multi_step_share=min_multi_step_share,
            min_hard_share=min_hard_share,
            log_path=lint_log,
        )
        if lint_proc.returncode == 0:
            duration = round(time.time() - started, 1)
            print(f"[DISTILL] OK {game_name} ({duration}s)", flush=True)
            return {
                "game": game_name,
                "status": "OK",
                "attempt": attempt,
                "duration_sec": duration,
                "log": str(codex_log),
                "lint_log": str(lint_log),
            }

        lint_feedback = (lint_proc.stdout or "").strip()
        print(f"[DISTILL] LINT FAIL {game_name} attempt {attempt} — refining", flush=True)

    return {
        "game": game_name,
        "status": "FAILED",
        "attempt": max_attempts,
        "duration_sec": round(time.time() - started, 1),
        "error": "quality gate failed after max attempts",
        "log": str(log_dir / f"distill_attempt_{max_attempts}.log"),
        "lint_log": str(log_dir / f"lint_attempt_{max_attempts}.log"),
    }


def main() -> int:
    args = parse_args()
    backend = normalize_backend(args.backend)
    try:
        ensure_backend_available(backend)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    games = list_games(args.games)
    if not games:
        print("No games selected for keypoint distillation.", file=sys.stderr)
        return 1

    print(f"[PLAN] Distilling keypoints for {len(games)} games: {', '.join(games)}", flush=True)
    results: List[Dict[str, object]] = []
    skill_prompt = read_skill_prompt()

    def run_one(game: str) -> Dict[str, object]:
        return distill_one_game(
            game,
            backend=backend,
            skill_prompt=skill_prompt,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            timeout=args.timeout,
            min_count=args.min_count,
            min_per_category=args.min_per_category,
            max_weak_share=args.max_weak_share,
            min_strong_cue_share=args.min_strong_cue_share,
            min_multi_step_share=args.min_multi_step_share,
            min_hard_share=args.min_hard_share,
            max_attempts=args.max_attempts,
        )

    max_workers = max(1, args.parallel)
    if max_workers == 1:
        for idx, game in enumerate(games, 1):
            print(f"\n=== [{idx}/{len(games)}] {game} ===", flush=True)
            result = run_one(game)
            results.append(result)
            if result["status"] == "PAUSED":
                break
            if result["status"] not in {"OK"} and not args.continue_on_error:
                break
    else:
        print(f"[PARALLEL] Running {max_workers} concurrent keypoint distillations", flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_map = {pool.submit(run_one, game): game for game in games}
            for idx, future in enumerate(concurrent.futures.as_completed(future_map), 1):
                game = future_map[future]
                print(f"\n=== [{idx}/{len(games)}] {game} ===", flush=True)
                try:
                    result = future.result()
                except Exception as exc:
                    result = {"game": game, "status": "ERROR", "error": str(exc)}
                results.append(result)

    print("\n" + "=" * 60)
    print("KEYPOINT DISTILL SUMMARY")
    print("=" * 60)
    paused = [r for r in results if r["status"] == "PAUSED"]
    failed = [r for r in results if r["status"] not in {"OK", "PAUSED"}]
    ok = [r for r in results if r["status"] == "OK"]
    for row in results:
        print(f"  {str(row['game']):40s} {str(row['status']):10s} {float(row.get('duration_sec', 0) or 0):.0f}s")
    print(f"\nTotal: {len(ok)}/{len(results)} succeeded")
    if paused:
        return PAUSED_RETURN_CODE
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
