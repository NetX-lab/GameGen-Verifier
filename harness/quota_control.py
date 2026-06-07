from __future__ import annotations

import re
from typing import Dict


PAUSED_RETURN_CODE = 75
QUOTA_ERROR_TYPE = "quota_exceeded"
QUOTA_EXCEEDED_INDICATORS = (
    "You've hit your usage limit",
    "insufficient_quota",
    "too many requests",
    "402 Payment Required",
    "Payment Required",
)
QUOTA_EXCEEDED_PATTERNS = (
    r"\brate limit(?:ed|ing)?\b",
    r"\bstatus(?: code)?\s*429\b",
    r"\berror\s*429\b",
    r"\bhttp\s*429\b",
    r"\bstatus(?: code)?\s*402\b",
    r"\berror\s*402\b",
    r"\bhttp\s*402\b",
    r"\b402\s+payment\s+required\b",
)


def is_quota_exceeded_text(text: str) -> bool:
    # Real quota errors appear at the END of process output (last failing API call).
    # Documentation/keypoint text scattered earlier in the log can include words like
    # "402 Payment Required" or "rate limit" without indicating an actual quota event.
    # Restrict the scan to the trailing window to avoid false positives.
    if not text:
        return False
    tail = text[-12000:]
    lowered = tail.lower()
    if any(indicator.lower() in lowered for indicator in QUOTA_EXCEEDED_INDICATORS):
        return True
    return any(re.search(pattern, tail, re.IGNORECASE) for pattern in QUOTA_EXCEEDED_PATTERNS)


def extract_retry_after_hint(text: str) -> str:
    patterns = (
        r"try again at\s+([^\.\n]+)",
        r"retry after\s+([^\.\n]+)",
        r"please try again in\s+([^\.\n]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return " ".join(match.group(1).strip().split())
    return ""


def quota_pause_fields(text: str) -> Dict[str, str]:
    if not is_quota_exceeded_text(text):
        return {}
    fields = {"pause_reason": QUOTA_ERROR_TYPE}
    retry_after_hint = extract_retry_after_hint(text)
    if retry_after_hint:
        fields["retry_after_hint"] = retry_after_hint
    return fields


def is_paused_process(returncode: int, output: str = "") -> bool:
    return returncode == PAUSED_RETURN_CODE or is_quota_exceeded_text(output)


def phase_status_for_process(returncode: int, output: str = "") -> str:
    if returncode == 0:
        return "PASS"
    if is_paused_process(returncode, output):
        return "PAUSED"
    return "FAIL"
