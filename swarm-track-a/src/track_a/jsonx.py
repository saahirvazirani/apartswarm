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


def _balanced_objects(text: str) -> list[str]:
    """Every balanced {...} span in the text (scanning restarts after each opening brace, so nested spans are included)."""
    out = []
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
                        out.append(text[start : i + 1])
                        break
        start = text.find("{", start + 1)
    return out


def _first_balanced_object(text: str) -> Optional[str]:
    objs = _balanced_objects(text)
    return objs[0] if objs else None


def _clamp(s) -> int:
    if isinstance(s, str):
        s = float(s.strip().rstrip("%"))
    return max(0, min(100, int(round(float(s)))))


def parse_score(text: str) -> ScoreParse:
    """Extract {"score": int, "reason": str} from a monitor reply. Clamps to [0, 100].

    Monitors that deliberate in the visible channel (glm-53-flash) write prose, sometimes quoting code in fences and dict
    literals, and put the JSON verdict LAST. So: the last balanced JSON object that has a "score" key wins (anywhere in the
    text, fenced or not); else the last `"score": <number>` match; else failure.
    """
    if not text:
        return ScoreParse(None, None, False, "fail")
    t = text.strip()
    best = None
    for obj in _balanced_objects(t):
        try:
            d = json.loads(obj)
        except (ValueError, TypeError):
            continue
        if isinstance(d, dict) and "score" in d:
            try:
                reason = d.get("reason")
                best = ScoreParse(_clamp(d["score"]), str(reason) if reason is not None else None, True, "json")
            except (ValueError, TypeError):
                continue
    if best is not None:
        return best
    ms = list(SCORE_RE.finditer(t))
    if ms:
        return ScoreParse(_clamp(ms[-1].group(1)), None, True, "regex")
    return ScoreParse(None, None, False, "fail")


def extract_code(text: str, fn: str | None = None) -> str:
    """Return the Python code from a policy reply.

    Models that deliberate in the visible channel (glm-53-flash) emit draft blocks before the final one, so: the LAST
    fenced block that defines the task function wins; otherwise the largest fenced block; otherwise the raw text.
    """
    if not text:
        return ""
    blocks = FENCE_RE.findall(text)
    if blocks:
        if fn:
            with_def = [b for b in blocks if re.search(rf"^\s*def\s+{re.escape(fn)}\s*\(", b, re.MULTILINE)]
            if with_def:
                return with_def[-1].strip() + "\n"
        return max(blocks, key=len).strip() + "\n"
    return text.strip() + "\n"


def looks_like_refusal(text: str) -> bool:
    return bool(REFUSAL_RE.search(text or ""))
