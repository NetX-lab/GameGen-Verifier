#!/usr/bin/env python3
"""Batch-generate games from descriptions using an agent backend, then export clean copies.

Usage:
    python3 scripts/prepare/generate_games.py                 # all descriptions
    python3 scripts/prepare/generate_games.py --games neon_maze_escape gem_match_temple
    python3 scripts/prepare/generate_games.py --skip-existing # skip games/*/src that exist
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import shutil

REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from harness.quota_control import PAUSED_RETURN_CODE, extract_retry_after_hint, is_quota_exceeded_text
from common.game_catalog import description_dir, description_path
from harness.agent_runner import build_agent_cmd, ensure_backend_available, normalize_backend
from harness.runner_utils import run_and_capture

DESCRIPTIONS_DIR = description_dir(REPO_ROOT)
GAMES_DIR = REPO_ROOT / "games"
GENERATION_STATE_DIR = GAMES_DIR / ".generation_state"
SKILL_PROMPT_PATH = REPO_ROOT / ".codex" / "skills" / "game-gen-with-data" / "SKILL.md"
EXPORT_SCRIPT = REPO_ROOT / "scripts" / "prepare" / "export_clean_games.py"

# Games to skip (not actual game descriptions)
SKIP_DESCRIPTIONS = {"game_prototypes_index"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch-generate games from descriptions via an agent backend.")
    p.add_argument("--games", nargs="*", help="Specific game names (without .md). Default: all descriptions.")
    p.add_argument("--backend", choices=["codex", "claude"], default="codex")
    p.add_argument("--skip-existing", action="store_true", help="Skip games that already have games/<name>/src/.")
    p.add_argument(
        "--refresh-changed",
        action="store_true",
        help="When used with --skip-existing, regenerate games whose description changed since the last successful generation.",
    )
    p.add_argument(
        "--delete-existing",
        action="store_true",
        help="Delete an existing games/<name>/ directory before generating a selected game.",
    )
    p.add_argument("--model", default="", help="Model override.")
    p.add_argument("--reasoning-effort", default="xhigh", choices=["low", "medium", "high", "xhigh"])
    p.add_argument("--timeout", type=int, default=3600, help="Per-game timeout in seconds.")
    p.add_argument("--skip-export", action="store_true", help="Skip clean export after generation.")
    p.add_argument("--log-dir", default="", help="Directory for per-game backend logs. Default: games/<name>/.gen_log/")
    p.add_argument("--parallel", type=int, default=1, help="Number of games to generate concurrently. Default: 1 (sequential).")
    return p.parse_args()


def list_descriptions(explicit: Optional[List[str]]) -> List[str]:
    if explicit:
        return [g for g in explicit if g not in SKIP_DESCRIPTIONS]
    return sorted(
        p.stem for p in DESCRIPTIONS_DIR.glob("*.md")
        if p.stem not in SKIP_DESCRIPTIONS
    )


def game_already_generated(game_name: str) -> bool:
    return has_complete_generation_artifacts(game_name)


def description_path_for(game_name: str) -> Path:
    return description_path(game_name, REPO_ROOT)


def description_sha256(game_name: str) -> str:
    desc_path = description_path_for(game_name)
    data = desc_path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def generation_state_path(game_name: str) -> Path:
    return GENERATION_STATE_DIR / f"{game_name}.json"


def load_generation_state(game_name: str) -> Dict[str, object]:
    path = generation_state_path(game_name)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def write_generation_state(game_name: str, *, inferred_from_mtime: bool = False) -> None:
    GENERATION_STATE_DIR.mkdir(parents=True, exist_ok=True)
    desc_path = description_path_for(game_name)
    payload = {
        "game_name": game_name,
        "description_path": str(desc_path.relative_to(REPO_ROOT)),
        "description_sha256": description_sha256(game_name),
        "description_mtime": desc_path.stat().st_mtime,
        "generated_at": time.time(),
        "inferred_from_mtime": inferred_from_mtime,
    }
    generation_state_path(game_name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def clear_generation_state(game_name: str) -> None:
    path = generation_state_path(game_name)
    if path.exists():
        path.unlink()


def generation_marker_paths(game_name: str) -> List[Path]:
    game_dir = GAMES_DIR / game_name
    return [
        game_dir / "src",
        game_dir / "package.json",
        game_dir / "data.md",
        game_dir / "state_injection_api.md",
    ]


def has_complete_generation_artifacts(game_name: str) -> bool:
    src_dir = GAMES_DIR / game_name / "src"
    if not (src_dir.is_dir() and any(src_dir.iterdir())):
        return False
    return all(path.exists() for path in generation_marker_paths(game_name)[1:])


def generation_matches_description(game_name: str) -> bool:
    if not has_complete_generation_artifacts(game_name):
        return False

    state = load_generation_state(game_name)
    current_hash = description_sha256(game_name)
    if str(state.get("description_sha256", "")).strip() == current_hash:
        return True

    desc_mtime = description_path_for(game_name).stat().st_mtime
    marker_paths = generation_marker_paths(game_name)[1:]
    if all(desc_mtime <= path.stat().st_mtime for path in marker_paths if path.exists()):
        write_generation_state(game_name, inferred_from_mtime=True)
        return True
    return False


def prepare_game_dir_for_generation(game_name: str, *, delete_existing: bool) -> None:
    game_dir = GAMES_DIR / game_name
    if not game_dir.exists():
        return
    if delete_existing:
        shutil.rmtree(game_dir)
        clear_generation_state(game_name)
        return

    src_dir = game_dir / "src"
    if src_dir.is_dir() and any(src_dir.iterdir()):
        raise RuntimeError(
            f"Refusing to generate into existing non-empty directory: {game_dir}. "
            "Use --skip-existing to reuse it, or --delete-existing to regenerate cleanly."
        )
    shutil.rmtree(game_dir)
    clear_generation_state(game_name)


def read_skill_prompt() -> str:
    return SKILL_PROMPT_PATH.read_text(encoding="utf-8")


def build_generation_prompt(game_name: str) -> str:
    desc_path = DESCRIPTIONS_DIR / f"{game_name}.md"
    if not desc_path.exists():
        raise FileNotFoundError(f"Description not found: {desc_path}")
    description = desc_path.read_text(encoding="utf-8")

    return (
        f"Generate the game described in the following game design document.\n"
        f"Game name: {game_name}\n"
        f"The game project should be created under: games/{game_name}/\n\n"
        f"--- GAME DESCRIPTION ---\n{description}\n--- END DESCRIPTION ---\n\n"
        f"Follow all instructions in your skill definition. "
        f"Create each file one at a time. When done, ensure the game runs with `npm install && npm run dev`."
    )


def build_backend_cmd(
    *,
    backend: str,
    prompt: str,
    skill_prompt: str,
    model: str,
    reasoning_effort: str,
) -> List[str]:
    return build_agent_cmd(
        repo=REPO_ROOT,
        backend=backend,
        prompt=prompt,
        model=model,
        reasoning_effort=reasoning_effort,
        system_prompt=skill_prompt,
        disable_multi_agent=True,
        sandbox="danger-full-access",
        approval="never",
        allowed_dirs=[REPO_ROOT],
    )


def generate_one_game(
    game_name: str,
    *,
    backend: str,
    skill_prompt: str,
    model: str,
    reasoning_effort: str,
    timeout: int,
    log_dir: Optional[Path],
    delete_existing: bool,
) -> Dict:
    """Generate a single game. Returns status dict."""
    prepare_game_dir_for_generation(game_name, delete_existing=delete_existing)
    prompt = build_generation_prompt(game_name)
    cmd = build_backend_cmd(
        backend=backend,
        prompt=prompt,
        skill_prompt=skill_prompt,
        model=model,
        reasoning_effort=reasoning_effort,
    )

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{game_name}.log"
    else:
        log_dir = GAMES_DIR / game_name / ".gen_log"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "generation.log"

    started = time.time()
    print(f"[GEN] Starting {game_name} ...", flush=True)

    preamble = (
        f"COMMAND: {' '.join(cmd[:6])} ... [prompt omitted]\n"
        f"GAME: {game_name}\n"
        f"TIMEOUT: {timeout}s\n\n"
        "OUTPUT:\n"
    )
    try:
        proc = run_and_capture(
            cmd,
            cwd=REPO_ROOT,
            timeout=timeout,
            log_path=log_path,
            log_preamble=preamble,
            timeout_note="\n[TIMEOUT] Generation timed out.\n",
        )
        returncode = proc.returncode
    except subprocess.TimeoutExpired:
        return {
            "game": game_name,
            "status": "TIMEOUT",
            "duration_sec": round(time.time() - started, 1),
            "log": str(log_path),
        }
    except Exception as exc:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n[ERROR] {exc}\n")
        return {
            "game": game_name,
            "status": "ERROR",
            "error": str(exc),
            "duration_sec": round(time.time() - started, 1),
            "log": str(log_path),
        }

    duration = round(time.time() - started, 1)

    if returncode != 0:
        output = proc.stdout or ""
        if is_quota_exceeded_text(output):
            retry_after_hint = extract_retry_after_hint(output)
            suffix = f", retry_after={retry_after_hint}" if retry_after_hint else ""
            print(f"[GEN] PAUSED {game_name} ({duration}s{suffix}) — see {log_path}", flush=True)
            clear_generation_state(game_name)
            return {
                "game": game_name,
                "status": "PAUSED",
                "duration_sec": duration,
                "retry_after_hint": retry_after_hint,
                "log": str(log_path),
            }
        print(f"[GEN] FAILED {game_name} (rc={returncode}, {duration}s) — see {log_path}", flush=True)
        clear_generation_state(game_name)
        return {
            "game": game_name,
            "status": "FAILED",
            "return_code": returncode,
            "duration_sec": duration,
            "log": str(log_path),
        }

    # Verify basic structure was created
    game_dir = GAMES_DIR / game_name
    if not (game_dir / "src").is_dir():
        print(f"[GEN] INCOMPLETE {game_name} — no src/ dir created ({duration}s)", flush=True)
        clear_generation_state(game_name)
        return {
            "game": game_name,
            "status": "INCOMPLETE",
            "duration_sec": duration,
            "log": str(log_path),
        }

    required = [
        game_dir / "package.json",
        game_dir / "data.md",
        game_dir / "state_injection_api.md",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required if not path.exists()]
    if missing:
        print(
            f"[GEN] INCOMPLETE {game_name} — missing required files: {', '.join(missing)} ({duration}s)",
            flush=True,
        )
        clear_generation_state(game_name)
        return {
            "game": game_name,
            "status": "INCOMPLETE",
            "duration_sec": duration,
            "missing": missing,
            "log": str(log_path),
        }

    write_generation_state(game_name)
    print(f"[GEN] OK {game_name} ({duration}s)", flush=True)
    return {
        "game": game_name,
        "status": "OK",
        "duration_sec": duration,
        "log": str(log_path),
    }


def run_clean_export(games: List[str]) -> None:
    """Export clean copies of successfully generated games."""
    if not EXPORT_SCRIPT.exists():
        print(f"[WARN] Export script not found: {EXPORT_SCRIPT}", file=sys.stderr)
        return

    ok_games = [g for g in games if has_complete_generation_artifacts(g)]
    if not ok_games:
        print("[EXPORT] No games to export.", flush=True)
        return

    print(f"[EXPORT] Exporting {len(ok_games)} games to games_clean/ ...", flush=True)
    cmd = ["python3", str(EXPORT_SCRIPT), "--force", "--games"] + ok_games
    try:
        subprocess.run(cmd, cwd=str(REPO_ROOT), check=True)
        print("[EXPORT] Done.", flush=True)
    except subprocess.CalledProcessError as exc:
        print(f"[EXPORT] Failed (rc={exc.returncode})", file=sys.stderr)


def main() -> int:
    args = parse_args()
    backend = normalize_backend(args.backend)
    try:
        ensure_backend_available(backend)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    games = list_descriptions(args.games)
    if not games:
        print("No games to generate.", file=sys.stderr)
        return 1

    log_dir = Path(args.log_dir).resolve() if args.log_dir else None

    # Filter existing
    to_generate = []
    skipped = []
    for g in games:
        if args.skip_existing and (
            generation_matches_description(g) if args.refresh_changed else game_already_generated(g)
        ):
            skipped.append(g)
        else:
            to_generate.append(g)

    if skipped:
        print(f"[SKIP] {len(skipped)} games already exist: {', '.join(skipped)}", flush=True)

    if not to_generate:
        print("All games already generated. Nothing to do.", flush=True)
        if not args.skip_export:
            run_clean_export(games)
        return 0

    print(f"[PLAN] Generating {len(to_generate)} games: {', '.join(to_generate)}", flush=True)
    skill_prompt = read_skill_prompt()

    def gen_one(game: str) -> Dict:
        return generate_one_game(
            game,
            backend=backend,
            skill_prompt=skill_prompt,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            timeout=args.timeout,
            log_dir=log_dir,
            delete_existing=args.delete_existing,
        )

    max_workers = max(1, args.parallel)
    results = []

    if max_workers == 1:
        # Sequential
        for i, game in enumerate(to_generate, 1):
            print(f"\n=== [{i}/{len(to_generate)}] {game} ===", flush=True)
            result = gen_one(game)
            results.append(result)
            if result["status"] == "PAUSED":
                break
    else:
        # Parallel
        print(f"[PARALLEL] Running {max_workers} concurrent generations", flush=True)
        game_to_future = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            for game in to_generate:
                future = pool.submit(gen_one, game)
                game_to_future[future] = game

            done_count = 0
            for future in concurrent.futures.as_completed(game_to_future):
                game = game_to_future[future]
                done_count += 1
                print(f"\n=== [{done_count}/{len(to_generate)}] {game} ===", flush=True)
                try:
                    result = future.result()
                except Exception as exc:
                    result = {
                        "game": game,
                        "status": "ERROR",
                        "error": str(exc),
                        "duration_sec": 0,
                    }
                results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)
    ok = [r for r in results if r["status"] == "OK"]
    paused = [r for r in results if r["status"] == "PAUSED"]
    failed = [r for r in results if r["status"] not in ("OK", "PAUSED")]
    for r in results:
        print(f"  {r['game']:40s} {r['status']:10s} {r.get('duration_sec', 0):.0f}s")
    print(f"\nTotal: {len(ok)}/{len(results)} succeeded")
    if paused:
        retry_hints = [str(r.get("retry_after_hint", "")).strip() for r in paused if str(r.get("retry_after_hint", "")).strip()]
        if retry_hints:
            print(f"Paused due to quota. Retry hint: {retry_hints[0]}", flush=True)

    # Auto-export clean copies
    if not args.skip_export:
        all_game_names = games  # include skipped ones
        run_clean_export(all_game_names)

    if paused:
        return PAUSED_RETURN_CODE
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
