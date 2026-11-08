"""Async Adaption client for Track A.

- per-key token-bucket pacer (pre-flight: the limiter is per key, ~450-500 req/min, enforced by queuing, no 429s)
- per-lane semaphores (fast / slow models) as a secondary bound on in-flight requests
- outer retry on 429 / timeouts / 5xx with jittered backoff (SDK retries kept at 1, timeout 30 s)
- every call's `usage` appended to <run_dir>/usage.jsonl with the API-reported cost
- prompt-hash cache (model, instructions, input, temperature, max_output_tokens, draw, extra_body) -> response
- round-robin over several API keys (ADAPTION_API_KEYS=k1,k2 or ADAPTION_API_KEY)
- budget guard: refuses new calls past BUDGET_CAP; slow lanes refuse past SLOW_SOFT_CAP
- default extra_body = REQUEST_DEFAULTS (reasoning.effort=none) on every call unless overridden
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from adaption import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncAdaption,
    DefaultAioHttpClient,
    RateLimitError,
)

from .config import BUDGET_CAP, REQUEST_DEFAULTS, RUNS, SLOW_SOFT_CAP, estimate_cost, lane

RETRYABLE_STATUS = {500, 502, 503, 504, 529}
_USE_DEFAULT: Any = object()


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class CallResult:
    ok: bool
    model: str = ""
    text: str = ""
    usage: dict = field(default_factory=dict)
    cost: float = 0.0
    cost_source: str = "none"       # "reported" | "estimated" | "none"
    latency: float = 0.0
    status: Optional[int] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    attempts: int = 0
    cached: bool = False
    cache_key: str = ""
    response_id: Optional[str] = None
    response_status: Optional[str] = None
    incomplete: Optional[dict] = None
    output_items: list = field(default_factory=list)

    @property
    def reasoning_tokens(self) -> int:
        d = (self.usage or {}).get("output_tokens_details") or {}
        return int(d.get("reasoning_tokens") or 0)


def load_keys() -> list[str]:
    keys: list[str] = []
    multi = os.getenv("ADAPTION_API_KEYS", "")
    keys += [k.strip() for k in multi.split(",") if k.strip()]
    single = os.getenv("ADAPTION_API_KEY", "").strip()
    if single and single not in keys:
        keys.insert(0, single)
    if not keys:
        raise SystemExit("No API key. Put ADAPTION_API_KEY=pt_live_... in swarm-track-a/.env")
    return keys


def spent_so_far(runs_dir: Path = RUNS) -> float:
    """Sum of credits already spent across every run folder (non-cached calls only)."""
    total = 0.0
    if not runs_dir.exists():
        return 0.0
    for p in runs_dir.glob("*/usage.jsonl"):
        with p.open() as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not rec.get("cached"):
                    total += float(rec.get("cost") or 0.0)
    return total


def cache_key_for(**fields: Any) -> str:
    blob = json.dumps(fields, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


class Pacer:
    """Token bucket: `rate` requests/second with a small burst `capacity`."""

    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
                self.last = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                wait = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait)


class TrackClient:
    def __init__(
        self,
        run_dir: Path,
        keys: list[str] | None = None,
        fast_inflight: int = 16,
        slow_inflight: int = 8,
        rps_per_key: float = 7.0,
        burst: float = 12.0,
        budget_cap: float = BUDGET_CAP,
        slow_soft_cap: float = SLOW_SOFT_CAP,
        timeout: float = 30.0,
        sdk_retries: int = 1,
    ):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.run_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.keys = keys or load_keys()
        self.fast_inflight = fast_inflight
        self.slow_inflight = slow_inflight
        self.rps_per_key = rps_per_key
        self.burst = burst
        self.budget_cap = budget_cap
        self.slow_soft_cap = slow_soft_cap
        self.timeout = timeout
        self.sdk_retries = sdk_retries
        self.clients: list[AsyncAdaption] = []
        self.pacers: list[Pacer] = []
        self.sems: dict[str, asyncio.Semaphore] = {}
        self._rr = 0
        self.spent = spent_so_far()
        self.session_spent = 0.0
        self.n_calls = 0
        self.n_cache_hits = 0
        self._usage_fh = None
        self._lock = asyncio.Lock()

    # ---- lifecycle -------------------------------------------------------
    async def __aenter__(self) -> "TrackClient":
        self.clients = [
            AsyncAdaption(api_key=k, max_retries=self.sdk_retries, timeout=self.timeout,
                          http_client=DefaultAioHttpClient())
            for k in self.keys
        ]
        self.pacers = [Pacer(self.rps_per_key, self.burst) for _ in self.keys]
        self.sems = {
            "fast": asyncio.Semaphore(self.fast_inflight),
            "slow": asyncio.Semaphore(self.slow_inflight),
        }
        self._usage_fh = (self.run_dir / "usage.jsonl").open("a")
        return self

    async def __aexit__(self, *exc) -> None:
        for c in self.clients:
            try:
                await c.close()
            except Exception:
                pass
        if self._usage_fh:
            self._usage_fh.close()

    def _next_idx(self) -> int:
        i = self._rr % len(self.clients)
        self._rr += 1
        return i

    # ---- budget ----------------------------------------------------------
    def _check_budget(self, model: str) -> None:
        if self.spent >= self.budget_cap:
            raise BudgetExceeded(f"spent {self.spent:.2f} >= cap {self.budget_cap}")
        if lane(model) == "slow" and self.spent >= self.slow_soft_cap:
            raise BudgetExceeded(f"slow lane paused: spent {self.spent:.2f} >= soft cap {self.slow_soft_cap}")

    def _log_usage(self, rec: dict) -> None:
        self._usage_fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        self._usage_fh.flush()

    # ---- the call --------------------------------------------------------
    async def call(
        self,
        model: str,
        input: str | list,
        instructions: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 512,
        draw: int = 0,
        tag: str = "",
        cache: bool = True,
        max_attempts: int = 6,
        extra_body: Any = _USE_DEFAULT,
        meta: dict | None = None,
    ) -> CallResult:
        if extra_body is _USE_DEFAULT:
            extra_body = REQUEST_DEFAULTS
        key = cache_key_for(
            model=model, instructions=instructions, input=input, temperature=temperature,
            max_output_tokens=max_output_tokens, draw=draw, extra_body=extra_body,
        )
        cpath = self.cache_dir / f"{key}.json"
        if cache and cpath.exists():
            data = json.loads(cpath.read_text())
            res = CallResult(**data)
            res.cached = True
            self.n_cache_hits += 1
            return res

        self._check_budget(model)
        sem = self.sems[lane(model)]
        kwargs: dict[str, Any] = dict(
            model=model, input=input, temperature=temperature,
            max_output_tokens=max_output_tokens, store=False,
        )
        if instructions:
            kwargs["instructions"] = instructions
        if extra_body:
            kwargs["extra_body"] = extra_body

        res = CallResult(ok=False, model=model, cache_key=key)
        for attempt in range(1, max_attempts + 1):
            res.attempts = attempt
            kidx = self._next_idx()
            client = self.clients[kidx]
            wait = None
            async with sem:
                await self.pacers[kidx].acquire()
                t0 = time.perf_counter()
                try:
                    r = await client.responses.create(**kwargs)
                    res.latency = time.perf_counter() - t0
                    usage = r.usage.model_dump() if r.usage else {}
                    reported = usage.get("cost")
                    if reported is not None:
                        res.cost, res.cost_source = float(reported), "reported"
                    else:
                        res.cost, res.cost_source = estimate_cost(model, usage), "estimated"
                    res.ok = True
                    res.text = r.output_text or ""
                    res.usage = usage
                    res.status = 200
                    res.response_id = r.id
                    res.response_status = r.status
                    res.incomplete = r.incomplete_details.model_dump() if getattr(r, "incomplete_details", None) else None
                    try:
                        res.output_items = [o.model_dump() for o in (r.output or [])]
                    except Exception:
                        res.output_items = []
                    res.error = None
                    res.error_type = None
                except RateLimitError as e:
                    res.latency = time.perf_counter() - t0
                    res.status, res.error, res.error_type = 429, str(e)[:300], "RateLimitError"
                    wait = min(60, 2 ** attempt) + random.random()
                except (APITimeoutError, APIConnectionError) as e:
                    res.latency = time.perf_counter() - t0
                    res.status, res.error, res.error_type = None, str(e)[:300], type(e).__name__
                    wait = min(30, 2 ** attempt) + random.random()
                except APIStatusError as e:
                    res.latency = time.perf_counter() - t0
                    res.status, res.error, res.error_type = e.status_code, str(e)[:300], type(e).__name__
                    wait = (min(30, 2 ** attempt) + random.random()) if e.status_code in RETRYABLE_STATUS else None
                except Exception as e:  # defensive: never let one call kill a sweep
                    res.latency = time.perf_counter() - t0
                    res.status, res.error, res.error_type = None, str(e)[:300], type(e).__name__
                    wait = min(30, 2 ** attempt) + random.random()

            async with self._lock:
                self.n_calls += 1
                if res.ok:
                    self.spent += res.cost
                    self.session_spent += res.cost
                self._log_usage({
                    "t": time.time(), "tag": tag, "model": model, "key_idx": kidx, "attempt": attempt,
                    "latency": round(res.latency, 3), "status": res.status, "error_type": res.error_type,
                    "usage": res.usage if res.ok else None, "cost": res.cost if res.ok else 0.0,
                    "cost_source": res.cost_source, "cached": False, "cache_key": key,
                    "temperature": temperature, "max_output_tokens": max_output_tokens, "draw": draw,
                    "extra_body": extra_body, "meta": meta or {},
                })

            if res.ok:
                if cache:
                    cpath.write_text(json.dumps(asdict(res), ensure_ascii=False, default=str))
                return res
            if wait is None or attempt == max_attempts:
                return res
            await asyncio.sleep(wait)
        return res

    async def list_models(self, key_idx: int = 0) -> list[dict]:
        r = await self.clients[key_idx].models.list(type="hosted")
        return [m.model_dump() if hasattr(m, "model_dump") else dict(m) for m in r.data]
