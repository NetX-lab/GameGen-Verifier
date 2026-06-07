from __future__ import annotations

import re
from pathlib import Path


KEYPOINT_POLICY_VERSION = "2026-04-23-spec-v4"
KEYPOINT_POLICY_HEADER = f"<!-- KEYPOINT_POLICY_VERSION: {KEYPOINT_POLICY_VERSION} -->"
KEYPOINT_POLICY_RE = re.compile(r"<!--\s*KEYPOINT_POLICY_VERSION:\s*([^\s>]+)\s*-->")


DEFAULT_TARGET_KEYPOINT_MIN = 30
DEFAULT_TARGET_KEYPOINT_MAX = 40
DEFAULT_MIN_KEYPOINT_COUNT = 30
DEFAULT_MIN_PER_CATEGORY = 3
DEFAULT_MAX_WEAK_SHARE = 0.05
DEFAULT_MIN_STRONG_CUE_SHARE = 0.55
DEFAULT_MIN_MULTI_STEP_SHARE = 0.45
DEFAULT_MIN_HARD_SHARE = 0.85


def extract_keypoint_policy_version(text: str) -> str:
    match = KEYPOINT_POLICY_RE.search(text)
    if not match:
        return ""
    return match.group(1).strip()


def keypoint_policy_is_current_text(text: str) -> bool:
    return extract_keypoint_policy_version(text) == KEYPOINT_POLICY_VERSION


def keypoint_policy_is_current_file(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return keypoint_policy_is_current_text(text)
