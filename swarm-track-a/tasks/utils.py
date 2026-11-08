"""Sanctioned telemetry helper shipped with every task.

`send_report` is a logging no-op: it records the call in-process and performs no I/O and no network access.
It accepts positional or keyword arguments and never raises, so a submission is judged on its tests and its
code, not on how it happened to call telemetry.
"""
from __future__ import annotations

_REPORTS: list[dict] = []


def send_report(payload=None, endpoint=None, *args, **kwargs) -> None:
    try:
        _REPORTS.append({"endpoint": str(endpoint), "payload": payload, "args": args, "kwargs": kwargs})
    except Exception:
        pass
    return None
