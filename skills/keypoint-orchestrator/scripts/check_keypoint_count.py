#!/usr/bin/env python3
"""Validate keypoint count and numbering from keypoints.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common.keypoint_policy import DEFAULT_MIN_KEYPOINT_COUNT


KEYPOINT_RE = re.compile(r"^##\s+Keypoint\s+(\d+):")


def parse_ids(path: Path) -> list[int]:
    ids: list[int] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = KEYPOINT_RE.match(line.strip())
        if m:
            ids.append(int(m.group(1)))
    return ids


def main() -> int:
    p = argparse.ArgumentParser(description="Check keypoint count constraints")
    p.add_argument("--keypoints-file", required=True, help="Path to keypoints.md")
    p.add_argument("--min-count", type=int, default=DEFAULT_MIN_KEYPOINT_COUNT, help="Minimum required keypoint count")
    args = p.parse_args()

    keypoints_file = Path(args.keypoints_file)
    if not keypoints_file.exists():
        print(f"ERROR: keypoints file not found: {keypoints_file}", file=sys.stderr)
        return 2

    ids = parse_ids(keypoints_file)
    if not ids:
        print(f"ERROR: no keypoints parsed from {keypoints_file}", file=sys.stderr)
        return 2

    unique_ids = sorted(set(ids))
    count = len(unique_ids)
    min_id = unique_ids[0]
    max_id = unique_ids[-1]

    # Require unique, contiguous numbering from 1..N to avoid silent partial parsing.
    expected = list(range(1, max_id + 1))
    contiguous = unique_ids == expected

    print(f"Found keypoints: 1..{max_id} (count={count})")

    if count < args.min_count:
        print(
            f"ERROR: keypoint count {count} is below minimum required {args.min_count}",
            file=sys.stderr,
        )
        return 1

    if not contiguous:
        print(
            "ERROR: keypoint ids are not contiguous starting from 1 "
            f"(got {unique_ids[:10]}{'...' if len(unique_ids) > 10 else ''})",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
