#!/usr/bin/env python3
"""Run parallelization ablation: parallel vs sequential keypoint evaluation.

Usage:
    python3 scripts/ablation/parallel_keypoints.py --games neon_maze_escape --repeats 3
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from harness.quota_control import PAUSED_RETURN_CODE, phase_status_for_process, quota_pause_fields
from harness.agent_runner import ensure_backend_available, normalize_backend
from harness.runner_utils import run_and_capture


NORMAL_SCRIPT = REPO_ROOT / "harness" / "run_normal_eval.py"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "experiments" / "ablation_parallel"


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def run_cmd(
    cmd: List[str],
    *,
    cwd: Path,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    log_path: Optional[Path] = None,
) -> subprocess.CompletedProcess:
    return run_and_capture(
        cmd,
        cwd=cwd,
        env=env,
        timeout=timeout,
        log_path=log_path,
    )


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def parse_overview(summary_md: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    if not summary_md.exists():
        return result
    for line in summary_md.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- Total Keypoints:"):
            result["total_keypoints"] = int(line.split(":", 1)[1].strip())
        elif line.startswith("- Passed:"):
            result["passed"] = int(line.split(":", 1)[1].strip())
        elif line.startswith("- Failed:"):
            result["failed"] = int(line.split(":", 1)[1].strip())
        elif line.startswith("- Incomplete:"):
            result["incomplete"] = int(line.split(":", 1)[1].strip())
        elif line.startswith("- Pass Rate:"):
            result["pass_rate"] = line.split(":", 1)[1].strip()
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run parallelization ablation: parallel vs sequential keypoint evaluation."
    )
    parser.add_argument("--games", nargs="+", required=True)
    parser.add_argument("--backend", choices=["codex", "claude"], default="codex")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--step-timeout", type=int, default=2400, help="Per-session timeout (covers all keypoints in one batch). Default 2400 fits 5 keypoints @ ~7min each.")
    parser.add_argument("--reasoning-effort", default="high", choices=["low", "medium", "high", "xhigh"])
    parser.add_argument("--sequential-workers", type=int, default=1, help="Worker count for sequential arm.")
    parser.add_argument("--parallel-workers", type=int, default=3, help="Worker count for parallel arm.")
    parser.add_argument(
        "--worker-max-retries",
        type=int,
        default=0,
        help="Max retries per keypoint worker on transient backend failures (default 0: one attempt only).",
    )
    parser.add_argument(
        "--retry-incomplete-timeout",
        type=int,
        default=0,
        help="Timeout seconds for the automatic in-run retry of retryable INCOMPLETE keypoints. 0 disables the retry pass.",
    )
    parser.add_argument(
        "--min-keypoints",
        type=int,
        default=30,
        help="Minimum total keypoints required for a run to be considered valid.",
    )
    parser.add_argument(
        "--keypoints-md",
        default="",
        help="Optional path to alternate keypoints.md (e.g. coarse keypoints for kp-ablation). When set, all runs use this file instead of games/<game>/keypoints.md.",
    )
    parser.add_argument("--continue-on-error", action="store_true")
    return parser.parse_args()


def protocol_env() -> Dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/tmp/ms-playwright")
    env.setdefault("NPM_CONFIG_CACHE", "/tmp/npm-cache")
    env.setdefault("PLAYWRIGHT_SKIP_BROWSER_GC", "1")
    return env


def run_single(
    *,
    backend: str,
    game: str,
    mode: str,  # "parallel" or "sequential"
    rep: int,
    execution_root: Path,
    env: Dict[str, str],
    step_timeout: int,
    reasoning_effort: str,
    sequential_workers: int,
    parallel_workers: int,
    min_keypoints: int,
    worker_max_retries: int,
    retry_incomplete_timeout: int,
    keypoints_md: str = "",
) -> Dict[str, Any]:
    max_workers = parallel_workers if mode == "parallel" else sequential_workers
    run_id = f"abl_{mode}_{backend}_{game}_r{rep:02d}_{now_ts()}"
    log_path = execution_root / "logs" / mode / game / f"rep_{rep:02d}" / "normal.log"

    cmd = [
        "python3",
        str(NORMAL_SCRIPT),
        "--workspace",
        str(REPO_ROOT),
        "--game-name",
        game,
        "--run-id",
        run_id,
        "--backend",
        backend,
        "--reasoning-effort",
        reasoning_effort,
        "--step-timeout",
        str(step_timeout),
        "--screenshot-mode",
        "sequence",
        "--screenshot-interval",
        "200",
        "--max-workers",
        str(max_workers),
        "--worker-max-retries",
        str(worker_max_retries),
        "--retry-incomplete-timeout",
        str(retry_incomplete_timeout),
        "--min-keypoints",
        str(min_keypoints),
    ]
    if keypoints_md:
        cmd.extend(["--keypoints-md", keypoints_md])

    started_at = utc_now_iso()
    proc = run_cmd(cmd, cwd=REPO_ROOT, env=env, timeout=None, log_path=log_path)
    ended_at = utc_now_iso()

    run_dir = REPO_ROOT / "runs" / game / run_id
    overview = parse_overview(run_dir / "summary_report.md")
    total_keypoints = int(overview.get("total_keypoints", 0) or 0)
    coverage_ok = total_keypoints >= min_keypoints

    # Compute wall-clock seconds from ISO timestamps
    try:
        t0 = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
        duration_sec = (t1 - t0).total_seconds()
    except Exception:
        duration_sec = -1

    record = {
        "mode": mode,
        "game": game,
        "repeat": rep,
        "run_id": run_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_sec": round(duration_sec, 1),
        "return_code": proc.returncode,
        "log_path": str(log_path),
        "run_dir": str(run_dir),
        "overview": overview,
        "min_keypoints_required": min_keypoints,
        "coverage_ok": coverage_ok,
        "status": "PASS" if proc.returncode == 0 and coverage_ok else phase_status_for_process(proc.returncode, proc.stdout or ""),
    }
    record.update(quota_pause_fields(proc.stdout or ""))
    return record


def main() -> int:
    args = parse_args()
    backend = normalize_backend(args.backend)
    ensure_backend_available(backend)
    execution_root = Path(args.output_root).resolve() / f"parallel_ablation_{now_ts()}"
    execution_root.mkdir(parents=True, exist_ok=True)
    env = protocol_env()

    config = {
        "games": args.games,
        "backend": backend,
        "repeats": args.repeats,
        "step_timeout": args.step_timeout,
        "reasoning_effort": args.reasoning_effort,
        "sequential_workers": args.sequential_workers,
        "parallel_workers": args.parallel_workers,
        "min_keypoints": args.min_keypoints,
        "created_at": utc_now_iso(),
    }
    (execution_root / "resolved_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    records_path = execution_root / "records.jsonl"
    all_records: List[Dict[str, Any]] = []
    paused = False

    for mode in ["sequential", "parallel"]:
        for game in args.games:
            for rep in range(1, args.repeats + 1):
                print(f"\n=== {mode} | {game} | rep {rep}/{args.repeats} ===", flush=True)
                record = run_single(
                    backend=backend,
                    game=game,
                    mode=mode,
                    rep=rep,
                    execution_root=execution_root,
                    env=env,
                    step_timeout=args.step_timeout,
                    reasoning_effort=args.reasoning_effort,
                    sequential_workers=args.sequential_workers,
                    parallel_workers=args.parallel_workers,
                    min_keypoints=args.min_keypoints,
                    worker_max_retries=args.worker_max_retries,
                    retry_incomplete_timeout=args.retry_incomplete_timeout,
                    keypoints_md=args.keypoints_md,
                )
                all_records.append(record)
                append_jsonl(records_path, record)
                print(
                    f"  -> {record['status']} in {record['duration_sec']:.0f}s "
                    f"(P={record['overview'].get('passed','-')} "
                    f"F={record['overview'].get('failed','-')} "
                    f"I={record['overview'].get('incomplete','-')})",
                    flush=True,
                )
                if record["status"] == "PAUSED":
                    paused = True
                    break
            if paused:
                break
        if paused:
            break

    # Write summary
    lines = [
        "# Parallelization Ablation Summary",
        "",
        f"- Games: {', '.join(args.games)}",
        f"- Repeats: {args.repeats}",
        f"- Sequential workers: {args.sequential_workers}",
        f"- Parallel workers: {args.parallel_workers}",
        "",
        "## Results",
        "",
        "| Mode | Game | Rep | Duration (s) | Passed | Failed | Incomplete |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in all_records:
        ov = r.get("overview", {})
        lines.append(
            f"| {r['mode']} | {r['game']} | {r['repeat']} | {r['duration_sec']:.0f} | "
            f"{ov.get('passed', '-')} | {ov.get('failed', '-')} | {ov.get('incomplete', '-')} |"
        )

    # Per-mode averages
    lines.extend(["", "## Average Duration by Mode", ""])
    for mode in ["sequential", "parallel"]:
        durations = [r["duration_sec"] for r in all_records if r["mode"] == mode and r["duration_sec"] > 0]
        if durations:
            avg = sum(durations) / len(durations)
            lines.append(f"- {mode}: {avg:.0f}s average over {len(durations)} runs")
        else:
            lines.append(f"- {mode}: no data")

    (execution_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nOutput: {execution_root}")
    print(f"Summary: {execution_root / 'summary.md'}")
    print(f"Records: {records_path}")
    if paused:
        print("Ablation paused due to quota exhaustion. Resume later from a fresh or resumed phase root.", file=sys.stderr)
        return PAUSED_RETURN_CODE
    failures = sum(1 for record in all_records if record.get("status") != "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
