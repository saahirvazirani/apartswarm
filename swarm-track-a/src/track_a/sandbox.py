"""Sandboxed hidden-test execution (CLAUDE.md rule 8).

macOS Seatbelt (`sandbox-exec`) profile: no network, file writes only inside a per-run temp dir; plus a wall-clock
timeout, CPU/file-size rlimits, a minimal environment and a dedicated interpreter (.sbx venv: pytest only).
Documented in the paper's Limitations as a kernel sandbox rather than a container.

  PYTHONPATH=src .venv/bin/python -m track_a.sandbox   # runs the jail self-test
"""
from __future__ import annotations

import os
import re
import resource
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .config import ROOT, TASKS

SBX_PYTHON = ROOT / ".sbx" / "bin" / "python"
SANDBOX_EXEC = "/usr/bin/sandbox-exec"
TMP_ROOT = Path(tempfile.gettempdir()) / "track_a_sbx"

PROFILE = """(version 1)
(allow default)
(deny network*)
(deny file-write*)
(allow file-write* (subpath "{tmp}"))
(allow file-write* (literal "/dev/null"))
(allow file-write* (regex #"^/dev/tty"))
"""

SUMMARY_RE = re.compile(r"(\d+) (passed|failed|error|errors|skipped|deselected|xfailed|xpassed)")


@dataclass
class TestResult:
    passed: int = 0
    failed: int = 0
    errors: int = 0
    collected_ok: bool = True
    timed_out: bool = False
    returncode: int | None = None
    all_pass: bool = False
    n_tests: int = 0
    stdout_tail: str = ""
    stderr_tail: str = ""
    extra: dict = field(default_factory=dict)


def _rlimits() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (10, 12))
    resource.setrlimit(resource.RLIMIT_FSIZE, (20 * 1024 * 1024, 20 * 1024 * 1024))
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    except (ValueError, OSError):
        pass


def run_tests(solution_code: str, test_code: str, utils_code: str, timeout: float = 15.0, label: str = "x") -> TestResult:
    """Run `test_code` against `solution_code` in a fresh jailed temp dir. Never raises on test failure."""
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f"{label}_", dir=TMP_ROOT))
    try:
        (work / "solution.py").write_text(solution_code, encoding="utf-8")
        (work / "utils.py").write_text(utils_code, encoding="utf-8")
        (work / "test_hidden.py").write_text(test_code, encoding="utf-8")
        profile = work / "profile.sb"
        profile.write_text(PROFILE.format(tmp=str(work.resolve())))
        env = {
            "PATH": "/usr/bin:/bin",
            "HOME": str(work),
            "TMPDIR": str(work),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONIOENCODING": "utf-8",
        }
        cmd = [SANDBOX_EXEC, "-f", str(profile), str(SBX_PYTHON), "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "--tb=line", "-o", "console_output_style=classic", "test_hidden.py"]
        res = TestResult()
        try:
            p = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=timeout,
                               preexec_fn=_rlimits, stdin=subprocess.DEVNULL)
            res.returncode = p.returncode
            res.stdout_tail = p.stdout[-1500:]
            res.stderr_tail = p.stderr[-800:]
            counts = {k: 0 for k in ("passed", "failed", "error", "errors")}
            for n, kind in SUMMARY_RE.findall(p.stdout):
                counts[kind] = int(n)
            res.passed = counts["passed"]
            res.failed = counts["failed"]
            res.errors = counts["error"] + counts["errors"]
            res.n_tests = res.passed + res.failed + res.errors
            res.collected_ok = p.returncode not in (2, 3, 4, 5) and res.errors == 0
            res.all_pass = (p.returncode == 0 and res.failed == 0 and res.errors == 0 and res.passed > 0)
        except subprocess.TimeoutExpired as e:
            res.timed_out = True
            res.stdout_tail = (e.stdout or b"")[-800:].decode(errors="replace") if isinstance(e.stdout, bytes) else str(e.stdout or "")[-800:]
            res.collected_ok = False
        return res
    finally:
        shutil.rmtree(work, ignore_errors=True)


def utils_source() -> str:
    return (TASKS / "utils.py").read_text(encoding="utf-8")


# ---------------------------------------------------------------- jail self-test
JAIL_TESTS = '''
import os, socket, pathlib
from solution import f

def test_normal():
    assert f(2) == 4

def test_network_blocked():
    try:
        s = socket.create_connection(("1.1.1.1", 80), timeout=3)
        s.close()
    except OSError:
        return
    raise AssertionError("network was NOT blocked")

def test_home_write_blocked():
    target = pathlib.Path("/Users") / os.environ.get("REAL_USER", "nobody") / "track_a_jail_probe.txt"
    try:
        target.write_text("x")
    except OSError:
        return
    target.unlink(missing_ok=True)
    raise AssertionError("write outside the jail was NOT blocked")

def test_tmp_write_allowed():
    pathlib.Path("inside.txt").write_text("ok")
    assert pathlib.Path("inside.txt").read_text() == "ok"
'''


def self_test() -> bool:
    import getpass
    os.environ["REAL_USER"] = getpass.getuser()
    code = "def f(x):\n    return x * 2\n"
    tests = JAIL_TESTS.replace('os.environ.get("REAL_USER", "nobody")', repr(getpass.getuser()))
    r = run_tests(code, tests, "def send_report(payload=None, endpoint=None, **kw):\n    pass\n", label="jail")
    ok = r.all_pass and r.passed == 4
    print(f"jail self-test: passed={r.passed} failed={r.failed} errors={r.errors} timed_out={r.timed_out} rc={r.returncode} -> {'OK' if ok else 'FAIL'}")
    if not ok:
        print(r.stdout_tail)
        print(r.stderr_tail)
    # timeout check
    r2 = run_tests("import time\n\ndef f(x):\n    while True:\n        pass\n", "from solution import f\n\ndef test_hang():\n    f(1)\n",
                   "def send_report(*a, **k):\n    pass\n", timeout=5, label="hang")
    print(f"timeout self-test: timed_out={r2.timed_out} -> {'OK' if r2.timed_out else 'FAIL'}")
    return ok and r2.timed_out


if __name__ == "__main__":
    raise SystemExit(0 if self_test() else 1)
