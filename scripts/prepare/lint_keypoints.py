#!/usr/bin/env python3
"""Lightweight quality checks for keypoints.md."""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common.keypoint_policy import (
    DEFAULT_MAX_WEAK_SHARE,
    DEFAULT_MIN_HARD_SHARE,
    DEFAULT_MIN_KEYPOINT_COUNT,
    DEFAULT_MIN_MULTI_STEP_SHARE,
    DEFAULT_MIN_PER_CATEGORY,
    DEFAULT_MIN_STRONG_CUE_SHARE,
    KEYPOINT_POLICY_VERSION,
    extract_keypoint_policy_version,
)


KEYPOINT_RE = re.compile(r"^##\s+Keypoint\s+(\d+):\s+\[(.+?)\]\s+(.+)$", re.M)
BLOCK_FIELD_RE = {
    "focus": re.compile(
        r"\*\*Verification Focus:\*\*\n(.+?)(?:\n\*\*Precondition Game State Description:\*\*|\n##\s+Keypoint|\Z)",
        re.S,
    ),
    "precondition": re.compile(
        r"\*\*Precondition Game State Description:\*\*\n(.+?)(?:\n\*\*Instruction Description:\*\*|\n##\s+Keypoint|\Z)",
        re.S,
    ),
    "instruction": re.compile(r"\*\*Instruction Description:\*\*\n(.+?)(?:\n\*\*Expected Result Description:\*\*|\Z)", re.S),
    "expected": re.compile(r"\*\*Expected Result Description:\*\*\n(.+?)(?:\n##\s+Keypoint|\Z)", re.S),
}

STRONG_CUE_PATTERNS = [
    r"\bcannot\b",
    r"\bdoes not\b",
    r"\bdo not\b",
    r"\binstead of\b",
    r"\bbut not\b",
    r"\bonly\b",
    r"\bwhile\b",
    r"\bbefore\b",
    r"\bafter\b",
    r"\bwithout\b",
    r"\bpreserv",
    r"\breset",
    r"\brevert",
    r"\bremain",
    r"\bsecond\b",
    r"\brepeated",
    r"\boccupied?\b",
    r"\blocked?\b",
    r"\bfail",
    r"\blimit",
    r"\bescalat",
    r"\babsorb",
    r"\bbypass",
    r"\bprevent",
    r"\bcarry",
    r"\bweight\b",
    r"\bcountdown\b",
    r"\bpressure\b",
    r"\brecovery\b",
    r"\bstumble\b",
    r"\brevive\b",
    r"\bfall\b",
    r"\bdeath\b",
    r"\bsame run\b",
    r"\bnew run\b",
]

MULTI_STEP_CUE_PATTERNS = [
    r"\bthen\b",
    r"\bimmediately\b",
    r"\bshortly before\b",
    r"\bshortly after\b",
    r"\bfirst\b",
    r"\bsecond\b",
    r"\bthird\b",
    r"\bcompare\b",
    r"\bboth\b",
    r"\beither\b",
    r"\bwhile\b",
    r"\bbefore\b",
    r"\bafter\b",
    r"\buntil\b",
    r"\bonce\b",
    r"\bwithin\b",
    r"\bagain\b",
    r"\brepeated",
    r"\bsequence\b",
    r"\border\b",
    r"\bcombo\b",
    r"\bcooldown\b",
    r"\brecharge\b",
    r"\bpersist",
    r"\bpreserv",
    r"\bcarry",
    r"\brefresh\b",
    r"\bstack\b",
    r"\badjacent\b",
    r"\bprerequisite\b",
    r"\brequires?\b",
    r"\bupgrade\b",
    r"\btransition\b",
]

WEAK_HEADING_PATTERNS = [
    r"\bautomatically\b",
    r"\breachable\b",
    r"\bchanges lanes?\b",
    r"\bcollect(?:ing|s)?\s+(?:coins?|gems?)\b",
    r"\bcan move\b",
    r"\bcan be (?:slid|rotated|dragged|used|activated|collected)\b",
    r"\bspeed increases\b",
    r"\bobstacle[- ]free\b",
    r"\bdisables?\b",
    r"\btapping\b",
    r"\bswiping\b",
    r"\bclicking\b",
    r"\bdragging\b",
    r"\bstarts?\b",
    r"\bbegins?\b",
]


def parse_keypoints(text: str) -> List[Dict[str, str]]:
    matches = list(KEYPOINT_RE.finditer(text))
    items: List[Dict[str, str]] = []
    for idx, match in enumerate(matches):
        next_start = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[match.start():next_start].strip()
        keypoint_id, category, heading = match.groups()
        fields: Dict[str, str] = {
            "id": keypoint_id,
            "category": category.strip(),
            "heading": heading.strip(),
            "block": block,
        }
        for field_name, field_re in BLOCK_FIELD_RE.items():
            field_match = field_re.search(block)
            fields[field_name] = " ".join(field_match.group(1).strip().split()) if field_match else ""
        items.append(fields)
    return items


def has_strong_cue(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in STRONG_CUE_PATTERNS)


def has_multi_step_cue(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in MULTI_STEP_CUE_PATTERNS)


def item_text(item: Dict[str, str]) -> str:
    return " ".join(
        [
            item.get("heading", ""),
            item.get("focus", ""),
            item.get("precondition", ""),
            item.get("instruction", ""),
            item.get("expected", ""),
        ]
    ).lower()


def looks_weak(item: Dict[str, str]) -> bool:
    heading = item["heading"].strip().lower()
    if not heading:
        return True
    joined = item_text(item)
    if has_strong_cue(joined) or has_multi_step_cue(joined):
        return False
    if heading.count(" and ") >= 1 and len(heading.split()) >= 10:
        return False
    if "," in heading and len(heading.split()) >= 10:
        return False
    return any(re.search(pattern, heading) for pattern in WEAK_HEADING_PATTERNS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint keypoints quality heuristically.")
    parser.add_argument("--keypoints-file", required=True, help="Path to keypoints.md")
    parser.add_argument(
        "--min-count",
        type=int,
        default=DEFAULT_MIN_KEYPOINT_COUNT,
        help="Minimum required keypoint count",
    )
    parser.add_argument(
        "--min-per-category",
        type=int,
        default=DEFAULT_MIN_PER_CATEGORY,
        help="Minimum keypoints required per category",
    )
    parser.add_argument(
        "--max-weak-share",
        type=float,
        default=DEFAULT_MAX_WEAK_SHARE,
        help="Maximum allowed share of weak/basic keypoints",
    )
    parser.add_argument(
        "--min-strong-cue-share",
        type=float,
        default=DEFAULT_MIN_STRONG_CUE_SHARE,
        help="Minimum required share of strong/contrastive keypoints",
    )
    parser.add_argument(
        "--min-multi-step-share",
        type=float,
        default=DEFAULT_MIN_MULTI_STEP_SHARE,
        help="Minimum required share of multi-step/persistence/order-sensitive keypoints",
    )
    parser.add_argument(
        "--min-hard-share",
        type=float,
        default=DEFAULT_MIN_HARD_SHARE,
        help="Minimum required share of keypoints that are either contrastive or multi-step.",
    )
    args = parser.parse_args()

    path = Path(args.keypoints_file)
    if not path.exists():
        print(f"ERROR: keypoints file not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    items = parse_keypoints(text)
    if not items:
        print(f"ERROR: no keypoints parsed from {path}", file=sys.stderr)
        return 2

    policy_version = extract_keypoint_policy_version(text)
    if policy_version != KEYPOINT_POLICY_VERSION:
        got = policy_version or "missing"
        print(
            f"ERROR: keypoint policy version is {got}; expected {KEYPOINT_POLICY_VERSION}",
            file=sys.stderr,
        )
        return 1

    ids = [int(item["id"]) for item in items]
    unique_ids = sorted(set(ids))
    expected_ids = list(range(1, unique_ids[-1] + 1))
    if unique_ids != expected_ids:
        print(
            f"ERROR: non-contiguous keypoint ids: got {unique_ids[:12]}{'...' if len(unique_ids) > 12 else ''}",
            file=sys.stderr,
        )
        return 1

    total = len(items)
    category_counts = Counter(item["category"] for item in items)
    weak_items = [item for item in items if looks_weak(item)]
    missing_focus_items = [item for item in items if not item.get("focus", "").strip()]
    strong_cue_items = [
        item for item in items if has_strong_cue(item_text(item))
    ]
    multi_step_items = [item for item in items if has_multi_step_cue(item_text(item))]
    hard_items = [item for item in items if has_strong_cue(item_text(item)) or has_multi_step_cue(item_text(item))]

    weak_share = len(weak_items) / total
    strong_cue_share = len(strong_cue_items) / total
    multi_step_share = len(multi_step_items) / total
    hard_share = len(hard_items) / total

    print(f"Keypoints parsed: {total}")
    print(f"Policy version: {policy_version}")
    print(f"Categories: {dict(category_counts)}")
    print(f"Verification focus present: {total - len(missing_focus_items)}/{total}")
    print(f"Weak/basic share: {len(weak_items)}/{total} = {weak_share:.1%}")
    print(f"Strong/contrastive share: {len(strong_cue_items)}/{total} = {strong_cue_share:.1%}")
    print(f"Multi-step/persistence share: {len(multi_step_items)}/{total} = {multi_step_share:.1%}")
    print(f"Hard-share (contrastive or multi-step): {len(hard_items)}/{total} = {hard_share:.1%}")

    failures: List[str] = []
    if total < args.min_count:
        failures.append(f"keypoint count {total} is below minimum {args.min_count}")

    for category in ["State Transition", "Boundary Condition", "Interaction Logic", "Game Rule"]:
        if category_counts.get(category, 0) < args.min_per_category:
            failures.append(
                f"category '{category}' has only {category_counts.get(category, 0)} keypoints (< {args.min_per_category})"
            )

    max_weak_allowed = math.floor(total * args.max_weak_share + 1e-9)
    min_strong_required = math.ceil(total * args.min_strong_cue_share - 1e-9)
    min_multi_step_required = math.ceil(total * args.min_multi_step_share - 1e-9)
    min_hard_required = math.ceil(total * args.min_hard_share - 1e-9)

    if len(weak_items) > max_weak_allowed:
        weak_labels = ", ".join(f"{item['id']}:{item['heading']}" for item in weak_items[:8])
        failures.append(
            f"too many weak/basic keypoints ({len(weak_items)} > {max_weak_allowed}); examples: {weak_labels}"
        )

    if missing_focus_items:
        focus_labels = ", ".join(f"{item['id']}:{item['heading']}" for item in missing_focus_items[:8])
        failures.append(
            f"missing Verification Focus on {len(missing_focus_items)} keypoints; examples: {focus_labels}"
        )

    if len(strong_cue_items) < min_strong_required:
        failures.append(
            f"strong/contrastive keypoints too few ({len(strong_cue_items)} < {min_strong_required})"
        )

    if len(multi_step_items) < min_multi_step_required:
        failures.append(
            f"multi-step/persistence keypoints too few ({len(multi_step_items)} < {min_multi_step_required})"
        )

    if len(hard_items) < min_hard_required:
        failures.append(
            f"hard keypoints too few ({len(hard_items)} < {min_hard_required})"
        )

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
