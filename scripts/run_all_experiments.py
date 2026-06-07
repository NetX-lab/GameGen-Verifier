#!/usr/bin/env python3
"""One-command launcher for the end-to-end pipeline.

Runs the requested phases sequentially over the requested games:

    prepare   -> generate games, distill keypoints, export clean copies
    ours      -> normal evaluation + recheck (one or more repeats per game)
    ablation  -> parallel-vs-sequential keypoint ablation

Smoke mode (`--smoke`) only runs the unit tests and `--help` on every public
entry point; it makes no backend calls and is safe to run anywhere.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
ALL_PHASES = ("prepare", "ours", "ablation")
DEFAULT_PHASES = ("prepare", "ours")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--games",
        nargs="+",
        help="Game names (file stems under descriptions_example/). Required unless --smoke.",
    )
    parser.add_argument(
        "--phases",
        nargs="+",
        choices=ALL_PHASES,
        default=list(DEFAULT_PHASES),
        help=f"Phases to run. Default: {' '.join(DEFAULT_PHASES)}",
    )
    parser.add_argument(
        "--repeats", type=int, default=1, help="Number of normal-eval repeats per game."
    )
    parser.add_argument(
        "--backend",
        choices=["codex", "claude"],
        default="codex",
    )
    parser.add_argument(
        "--output-root",
        default=str(REPO_ROOT / "experiments" / "all_runs"),
        help="Where to write the per-launch execution directory.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Abort the launch on the first non-zero return code.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run unit tests + --help on every entry point. No backend calls.",
    )
    return parser.parse_args()


def run(cmd: List[str]) -> int:
    print("+ " + " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    return int(proc.returncode)


def smoke() -> int:
    checks = [
        ["python3", "-B", "-m", "unittest", "discover", "-s", "tests"],
        ["python3", "-B", "scripts/run_all_experiments.py", "--help"],
        ["python3", "-B", "harness/run_normal_eval.py", "--help"],
        ["python3", "-B", "harness/run_recheck_eval.py", "--help"],
        ["python3", "-B", "scripts/prepare/generate_games.py", "--help"],
        ["python3", "-B", "scripts/prepare/distill_keypoints.py", "--help"],
        ["python3", "-B", "scripts/prepare/export_clean_games.py", "--help"],
        ["python3", "-B", "scripts/ablation/parallel_keypoints.py", "--help"],
    ]
    for cmd in checks:
        rc = run(cmd)
        if rc != 0:
            return rc
    return 0


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def phase_prepare(games: List[str], stop_on_error: bool) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for game in games:
        for cmd in (
            ["python3", "scripts/prepare/generate_games.py", "--games", game, "--skip-existing"],
            ["python3", "scripts/prepare/distill_keypoints.py", "--games", game],
            ["python3", "scripts/prepare/export_clean_games.py", "--games", game, "--force"],
        ):
            rc = run(cmd)
            rows.append({"phase": "prepare", "game": game, "cmd": cmd, "rc": rc})
            if rc != 0 and stop_on_error:
                return rows
    return rows


def phase_ours(
    games: List[str], repeats: int, backend: str, stop_on_error: bool
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for game in games:
        for repeat_idx in range(1, repeats + 1):
            run_id = f"all_run_{now_ts()}_r{repeat_idx:02d}"
            normal_cmd = [
                "python3", "harness/run_normal_eval.py",
                "--workspace", str(REPO_ROOT),
                "--game-name", game,
                "--run-id", run_id,
                "--backend", backend,
            ]
            rc = run(normal_cmd)
            rows.append({"phase": "ours.normal", "game": game, "run_id": run_id, "rc": rc})
            if rc != 0 and stop_on_error:
                return rows
            if rc != 0:
                continue
            recheck_cmd = [
                "python3", "harness/run_recheck_eval.py",
                "--workspace", str(REPO_ROOT),
                "--game-name", game,
                "--run-id", run_id,
                "--backend", backend,
            ]
            rc2 = run(recheck_cmd)
            rows.append({"phase": "ours.recheck", "game": game, "run_id": run_id, "rc": rc2})
            if rc2 != 0 and stop_on_error:
                return rows
    return rows


def phase_ablation(
    games: List[str], repeats: int, stop_on_error: bool
) -> List[Dict[str, object]]:
    cmd = [
        "python3", "scripts/ablation/parallel_keypoints.py",
        "--games", *games,
        "--repeats", str(repeats),
    ]
    rc = run(cmd)
    return [{"phase": "ablation", "games": games, "rc": rc}]


def main() -> int:
    args = parse_args()
    if args.smoke:
        return smoke()
    if not args.games:
        print("error: --games is required (or pass --smoke)", file=sys.stderr)
        return 2

    output_root = Path(args.output_root) / f"launch_{now_ts()}"
    output_root.mkdir(parents=True, exist_ok=True)

    log: List[Dict[str, object]] = []
    summary: Dict[str, object] = {
        "started_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "games": args.games,
        "phases": args.phases,
        "repeats": args.repeats,
        "backend": args.backend,
        "output_root": str(output_root),
        "rows": log,
    }
    summary_path = output_root / "summary.json"

    def flush() -> None:
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    try:
        if "prepare" in args.phases:
            log.extend(phase_prepare(args.games, args.stop_on_error))
            flush()
            if args.stop_on_error and any(r.get("rc") != 0 for r in log):
                return 1
        if "ours" in args.phases:
            log.extend(
                phase_ours(args.games, args.repeats, args.backend, args.stop_on_error)
            )
            flush()
            if args.stop_on_error and any(r.get("rc") != 0 for r in log):
                return 1
        if "ablation" in args.phases:
            log.extend(phase_ablation(args.games, args.repeats, args.stop_on_error))
            flush()
    finally:
        summary["finished_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        flush()

    failed = [r for r in log if r.get("rc") not in (0, None)]
    print(
        f"\nLaunch complete: {len(log) - len(failed)} ok, {len(failed)} failed. "
        f"Summary: {summary_path}",
        flush=True,
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
