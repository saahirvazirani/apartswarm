"""Tolerant parsing of model outputs: monitor JSON scores and fenced code blocks."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

FENCE_RE = re.compile(r"```(?:[a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)
SCORE_RE = re.compile(r'"?score"?\s*[:=]\s*(-?\d+(?:\.\d+)?)', re.IGNORECASE)
REFUSAL_RE = re.compile(
    r"\b(i\s+can(?:'|no)t|i\s+cannot|i\s+won(?:'|no)t|i\s+will\s+not|i'm\s+unable|i\s+am\s+unable|not\s+able\s+to)\b"
    r".{0,80}\b(comply|assist|help|include|add|insert|do\s+that|fulfil|fulfill|implement|provide)",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class ScoreParse:
    score: Optional[int]
    reason: Optional[str]
    ok: bool
    method: str  # "json" | "regex" | "fail"


def _first_balanced_object(text: str) -> Optional[str]:
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start : i + 1]
        start = text.find("{", start + 1)
    return None


def parse_score(text: str) -> ScoreParse:
    """Extract {"score": int, "reason": str} from a monitor reply. Clamps to [0, 100]."""
    if not text:
        return ScoreParse(None, None, False, "fail")
    t = text.strip()
    m = FENCE_RE.search(t)
    if m:
        t = m.group(1).strip()
    obj = _first_balanced_object(t)
    if obj:
        try:
            d = json.loads(obj)
            if isinstance(d, dict) and "score" in d:
                s = d["score"]
                if isinstance(s, str):
                    s = float(s.strip().rstrip("%"))
                s = int(round(float(s)))
                s = max(0, min(100, s))
                reason = d.get("reason")
                return ScoreParse(s, str(reason) if reason is not None else None, True, "json")
        except (ValueError, TypeError):
            pass
    m = SCORE_RE.search(t)
    if m:
        s = int(round(float(m.group(1))))
        return ScoreParse(max(0, min(100, s)), None, True, "regex")
    return ScoreParse(None, None, False, "fail")


def extract_code(text: str) -> str:
    """Return the Python code from a policy reply: largest fenced block, else the raw text."""
    if not text:
        return ""
    blocks = FENCE_RE.findall(text)
    if blocks:
        return max(blocks, key=len).strip() + "\n"
    return text.strip() + "\n"


def looks_like_refusal(text: str) -> bool:
    return bool(REFUSAL_RE.search(text or ""))
