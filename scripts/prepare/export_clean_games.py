#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[2]
GAMES_ROOT = REPO_ROOT / "games"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "games_clean"

SKIP_DIRS = {"node_modules", "dist", ".vite"}
SKIP_FILES = {"data.md", "state_injection_api.md", "keypoints.md"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export clean game copies without evaluation/injection APIs."
    )
    parser.add_argument(
        "--games",
        nargs="*",
        help="Specific game directory names under games/. If omitted, export all current game dirs except oldgame.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Destination root for clean exports. Default: games_clean/",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete an existing clean export directory before re-exporting.",
    )
    return parser.parse_args()


def selected_games(explicit: Iterable[str] | None) -> List[str]:
    if explicit:
        return list(explicit)
    return sorted(
        path.name
        for path in GAMES_ROOT.iterdir()
        if path.is_dir() and path.name != "oldgame" and not path.name.startswith(".")
    )


def ignore_copy(_src: str, names: List[str]) -> List[str]:
    ignored: List[str] = []
    for name in names:
        if name in SKIP_DIRS or name in SKIP_FILES:
            ignored.append(name)
    return ignored


def patch_main_ts(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    kept: List[str] = []
    for line in lines:
        stripped = line.strip()
        if "from \"./eval_adapter\"" in line or "from './eval_adapter'" in line:
            continue
        if "mountEvalAdapter(" in line:
            continue
        if "markGameReady(" in line:
            continue
        if "evalAdapter.markReady(" in line:
            continue
        kept.append(line)

    patched = "\n".join(kept).strip() + "\n"
    patched = re.sub(r"\n{3,}", "\n\n", patched)
    path.write_text(patched, encoding="utf-8")


def build_clean_readme(src_game_dir: Path, game_name: str) -> str:
    src_readme = src_game_dir / "README.md"
    title = game_name
    summary = "Clean export generated from the evaluation-enabled source version."
    if src_readme.exists():
        text = src_readme.read_text(encoding="utf-8")
        lines = [line.rstrip() for line in text.splitlines()]
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        body_lines = [line.strip() for line in lines if line.strip() and not line.startswith("# ")]
        if body_lines:
            summary = body_lines[0]

    return "\n".join(
        [
            f"# {title}",
            "",
            summary,
            "",
            "## Clean Export",
            "",
            f"This directory is a clean export derived from `games/{game_name}`.",
            "It removes evaluation-specific files and browser globals used only for automated testing.",
            "",
            "Removed from this export:",
            "",
            "- `src/eval_adapter.ts`",
            "- `data.md`",
            "- `state_injection_api.md`",
            "- `keypoints.md`",
            "- build artifacts such as `dist/`",
            "- local dependencies such as `node_modules/`",
            "",
            "## Run",
            "",
            "```bash",
            f"cd games_clean/{game_name}",
            "npm install",
            "npm run dev",
            "```",
            "",
            "## Build",
            "",
            "```bash",
            f"cd games_clean/{game_name}",
            "npm run build",
            "```",
            "",
            "## Notes",
            "",
            "- Core gameplay/runtime code is preserved.",
            "- Evaluation globals are intentionally removed from the clean export.",
            "- To refresh this directory after source changes, rerun `scripts/prepare/export_clean_games.py`.",
            "",
        ]
    )


def export_one(game_name: str, output_root: Path, force: bool) -> None:
    src_game_dir = GAMES_ROOT / game_name
    if not src_game_dir.is_dir():
        raise FileNotFoundError(f"Missing game directory: {src_game_dir}")

    dst_game_dir = output_root / game_name
    if dst_game_dir.exists():
        if not force:
            raise FileExistsError(
                f"Destination already exists: {dst_game_dir}. Re-run with --force to overwrite."
            )
        shutil.rmtree(dst_game_dir)

    shutil.copytree(src_game_dir, dst_game_dir, ignore=ignore_copy)

    eval_adapter = dst_game_dir / "src" / "eval_adapter.ts"
    if eval_adapter.exists():
        eval_adapter.unlink()

    main_ts = dst_game_dir / "src" / "main.ts"
    if main_ts.exists():
        patch_main_ts(main_ts)

    readme = dst_game_dir / "README.md"
    readme.write_text(build_clean_readme(src_game_dir, game_name), encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    games = selected_games(args.games)
    if not games:
        raise RuntimeError("No game directories selected for export.")

    for game_name in games:
        export_one(game_name, output_root, args.force)
        print(f"EXPORTED\t{game_name}\t{output_root / game_name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
