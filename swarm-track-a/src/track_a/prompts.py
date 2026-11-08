"""Frozen prompt loading, rendering and hashing (CLAUDE.md rule 6)."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from .config import PROMPTS

NAMES = ["policy_benign", "policy_attack", "policy_polish", "monitor_blind", "monitor_told", "paraphrase"]


def load_prompt(name: str) -> str:
    return (PROMPTS / f"{name}.txt").read_text(encoding="utf-8").strip()


def render(template: str, **kw: str) -> str:
    """Placeholder substitution with str.replace (templates/code contain literal braces)."""
    out = template
    for k, v in kw.items():
        out = out.replace("{" + k + "}", v)
    return out


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def prompt_hashes() -> dict[str, str]:
    return {n: sha256_text(load_prompt(n)) for n in NAMES}


def write_hashes(path: Path | None = None) -> dict[str, str]:
    h = prompt_hashes()
    (path or PROMPTS / "HASHES.json").write_text(json.dumps(h, indent=2) + "\n")
    return h


def freeze_into(run_dir: Path) -> None:
    """Copy the exact prompts + hashes into a run folder."""
    dest = Path(run_dir) / "prompts"
    dest.mkdir(parents=True, exist_ok=True)
    for n in NAMES:
        shutil.copy(PROMPTS / f"{n}.txt", dest / f"{n}.txt")
    (dest / "HASHES.json").write_text(json.dumps(prompt_hashes(), indent=2) + "\n")
