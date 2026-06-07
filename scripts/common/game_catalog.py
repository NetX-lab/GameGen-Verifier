from __future__ import annotations

import re
from pathlib import Path
from typing import List


REPO_ROOT = Path(__file__).resolve().parents[2]
DESCRIPTION_DIRNAME = "descriptions_example"


def description_dir(repo_root: Path = REPO_ROOT) -> Path:
    return repo_root / DESCRIPTION_DIRNAME


def description_path(game_name: str, repo_root: Path = REPO_ROOT) -> Path:
    return description_dir(repo_root) / f"{game_name}.md"


def description_relpath(game_name: str) -> str:
    return f"{DESCRIPTION_DIRNAME}/{game_name}.md"


def list_description_games(repo_root: Path = REPO_ROOT) -> List[str]:
    root = description_dir(repo_root)
    if not root.exists():
        return []
    return sorted(path.stem for path in root.glob("*.md"))


def normalize_description_relpath(relpath: str, repo_root: Path = REPO_ROOT) -> str:
    normalized = str(relpath or "").strip().replace("\\", "/")
    if not normalized:
        return normalized
    basename = Path(normalized).name
    candidate = description_dir(repo_root) / basename
    if candidate.exists():
        return f"{DESCRIPTION_DIRNAME}/{basename}"
    return normalized


def _canonicalize_genre(raw: str) -> str:
    text = raw.strip().lower()
    if not text:
        return "Unknown"
    if any(token in text for token in ("board", "tabletop", "tile-based", "card game", "set collection")):
        return "Board"
    if any(token in text for token in ("match-3", "puzzle", "optical illusion")):
        return "Puzzle"
    if any(token in text for token in ("strategy", "tower defense", "auto battler")):
        return "Strategy"
    if any(token in text for token in ("simulation", "city-builder", "life sim", "management")):
        return "Simulation"
    if any(token in text for token in ("role-playing", "rpg")):
        return "Role-Playing"
    if any(token in text for token in ("adventure", "exploration", "stealth")):
        return "Adventure"
    if any(token in text for token in ("casual", "rhythm")):
        return "Casual"
    if any(token in text for token in ("action", "runner", "platformer", "fighter", "shooter", "racing", "arcade")):
        return "Action"
    return "Unknown"


def genre_for_game(game_name: str, repo_root: Path = REPO_ROOT) -> str:
    path = description_path(game_name, repo_root)
    if not path.exists():
        return "Unknown"

    text = path.read_text(encoding="utf-8", errors="ignore")
    patterns = [
        r"\|\s*\*\*Genre(?: Family)?\*\*\s*\|\s*([^|\n]+)",
        r"\|\s*Genre(?: Family)?\s*\|\s*([^|\n]+)",
        r"-\s*\*\*Genre(?: Family)?\*\*:\s*([^\n]+)",
        r"\*\*Genre(?: Family)?\*\*:\s*([^\n]+)",
        r"-\s*Genre(?: Family)?\s*:\s*([^\n]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return _canonicalize_genre(match.group(1))
    return "Unknown"
