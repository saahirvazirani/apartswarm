"""Async Adaption client for Track A.

Lessons from pre-flight and the first bank run (runs/PREFLIGHT_SUMMARY.md, runs/bank_cheap3/usage.jsonl):
- the limiter is per key and token-weighted (~60k+ tokens per short window), enforced by queuing requests for ~60 s, never 429
- the aiohttp transport fast-fails every request once stalled connections fill its pool -> use the httpx transport
- generations of 2000 tokens take 20-30 s on glm-53-flash -> 120 s timeout, retries handled here (SDK retries = 0)
- the gateway returns 504 at exactly 60 s of silence (nginx-style idle timeout), so every request is STREAMED and the terminal
  `response.completed` event supplies the full response + usage; a 7000-token glm-53-flash reply then completes in ~100 s

Mechanics:
- per-key TOKEN bucket (tokens/minute) + per-key request bucket; a call reserves an estimate up front and reconciles with usage
- global cooldown: any genuine stall (>20 s then timeout) pauses all new requests for `cooldown_s`
- per-lane semaphores (fast / slow models) bound in-flight requests
- outer retry on timeouts / 429 / 5xx with jittered backoff
- every attempt logged to <run_dir>/usage.jsonl with the API-reported cost
- prompt-hash cache keyed on (model, instructions, input, temperature, max_output_tokens, draw, extra_body)
- budget guard: refuses new calls past BUDGET_CAP; slow lanes refuse past SLOW_SOFT_CAP
- default extra_body = REQUEST_DEFAULTS (reasoning.effort=none) on every call unless overridden
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

import httpx
from adaption import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncAdaption,
    DefaultAsyncHttpxClient,
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
    cost_source: str = "none"
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
    # teammates' keys: KEY_2, KEY_3, ... or ADAPTION_API_KEY_2, ... (per-key rate limits -> linear speedup)
    for name, val in sorted(os.environ.items()):
        if re.fullmatch(r"(ADAPTION_API_)?KEY_\d+", name) and val.strip().startswith("pt_") and val.strip() not in keys:
            keys.append(val.strip())
    if not keys:
        raise SystemExit("No API key. Put ADAPTION_API_KEY=pt_live_... in swarm-track-a/.env")
    return keys


def pick_keys(idx: list[int] | None) -> list[str] | None:
    """Subset of the loaded keys by index, so concurrent processes can own disjoint keys (the limiter is per key)."""
    if not idx:
        return None
    keys = load_keys()
    return [keys[i] for i in idx]


def spent_so_far(runs_dir: Path = RUNS) -> float:
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


def est_input_tokens(instructions: str | None, inp: str | list) -> int:
    text = (instructions or "") + (inp if isinstance(inp, str) else json.dumps(inp))
    return int(len(text) / 3.5) + 20


class Bucket:
    """Continuous token bucket. `rate` units/second, `capacity` units."""

    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now

    async def take(self, n: float) -> None:
        while True:
            async with self._lock:
                self._refill()
                if self.tokens >= n:
                    self.tokens -= n
                    return
                wait = (n - self.tokens) / self.rate
            await asyncio.sleep(min(wait, 5.0))

    def give_back(self, n: float) -> None:
        self.tokens = min(self.capacity, self.tokens + n)


class TrackClient:
    def __init__(
        self,
        run_dir: Path,
        keys: list[str] | None = None,
        fast_inflight: int = 6,
        slow_inflight: int = 3,
        rps_per_key: float = 4.0,
        tpm_per_key: float = 60_000.0,
        cooldown_s: float = 45.0,
        budget_cap: float = BUDGET_CAP,
        slow_soft_cap: float = SLOW_SOFT_CAP,
        timeout: float = 120.0,
        stream_timeout: float = 300.0,
    ):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.run_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.keys = keys or load_keys()
        self.fast_inflight = fast_inflight
        self.slow_inflight = slow_inflight
        self.rps_per_key = rps_per_key
        self.tpm_per_key = tpm_per_key
        self.cooldown_s = cooldown_s
        self.budget_cap = budget_cap
        self.slow_soft_cap = slow_soft_cap
        self.timeout = timeout
        self.stream_timeout = stream_timeout
        self.clients: list[AsyncAdaption] = []
        self.req_buckets: list[Bucket] = []
        self.tok_buckets: list[Bucket] = []
        self.sems: dict[str, asyncio.Semaphore] = {}
        self.cooldown_until = 0.0
        self.n_stalls = 0
        self._rr = 0
        self.spent = spent_so_far()
        self.session_spent = 0.0
        self.n_calls = 0
        self.n_cache_hits = 0
        self._usage_fh = None
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> "TrackClient":
        self.clients = [
            AsyncAdaption(
                api_key=k, max_retries=0, timeout=self.timeout,
                http_client=DefaultAsyncHttpxClient(
                    limits=httpx.Limits(max_connections=32, max_keepalive_connections=8),
                    timeout=httpx.Timeout(self.timeout, connect=10.0),
                ),
            )
            for k in self.keys
        ]
        self.req_buckets = [Bucket(self.rps_per_key, self.rps_per_key * 2) for _ in self.keys]
        self.tok_buckets = [Bucket(self.tpm_per_key / 60.0, self.tpm_per_key * 0.5) for _ in self.keys]
        self.sems = {"fast": asyncio.Semaphore(self.fast_inflight), "slow": asyncio.Semaphore(self.slow_inflight)}
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

    def _check_budget(self, model: str) -> None:
        if self.spent >= self.budget_cap:
            raise BudgetExceeded(f"spent {self.spent:.2f} >= cap {self.budget_cap}")
        if lane(model) == "slow" and self.spent >= self.slow_soft_cap:
            raise BudgetExceeded(f"slow lane paused: spent {self.spent:.2f} >= soft cap {self.slow_soft_cap}")

    def _log_usage(self, rec: dict) -> None:
        self._usage_fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        self._usage_fh.flush()

    async def _wait_cooldown(self) -> None:
        while True:
            left = self.cooldown_until - time.monotonic()
            if left <= 0:
                return
            await asyncio.sleep(min(left, 5.0))

    def _trip_cooldown(self) -> None:
        self.n_stalls += 1
        self.cooldown_until = max(self.cooldown_until, time.monotonic() + self.cooldown_s)

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
        expect_output_tokens: int | None = None,
        refresh: bool = False,
    ) -> CallResult:
        """`refresh=True` ignores a cached response (still writes the new one) - used to regenerate a policy's records."""
        if extra_body is _USE_DEFAULT:
            extra_body = REQUEST_DEFAULTS
        key = cache_key_for(model=model, instructions=instructions, input=input, temperature=temperature,
                            max_output_tokens=max_output_tokens, draw=draw, extra_body=extra_body)
        cpath = self.cache_dir / f"{key}.json"
        if cache and not refresh and cpath.exists():
            res = CallResult(**json.loads(cpath.read_text()))
            res.cached = True
            self.n_cache_hits += 1
            return res

        self._check_budget(model)
        sem = self.sems[lane(model)]
        kwargs: dict[str, Any] = dict(model=model, input=input, temperature=temperature,
                                      max_output_tokens=max_output_tokens, store=False)
        if instructions:
            kwargs["instructions"] = instructions
        if extra_body:
            kwargs["extra_body"] = extra_body
        est = est_input_tokens(instructions, input) + (expect_output_tokens if expect_output_tokens is not None else max(64, max_output_tokens // 3))

        res = CallResult(ok=False, model=model, cache_key=key)
        for attempt in range(1, max_attempts + 1):
            res.attempts = attempt
            kidx = self._next_idx()
            client = self.clients[kidx]
            wait = None
            async with sem:
                await self._wait_cooldown()
                await self.req_buckets[kidx].take(1)
                await self.tok_buckets[kidx].take(est)
                t0 = time.perf_counter()
                try:
                    r = await self._stream_create(client, kwargs)
                    res.latency = time.perf_counter() - t0
                    usage = r.usage.model_dump() if r.usage else {}
                    actual = int(usage.get("total_tokens") or 0)
                    if actual and actual < est:
                        self.tok_buckets[kidx].give_back(est - actual)
                    elif actual > est:
                        await self.tok_buckets[kidx].take(min(actual - est, self.tok_buckets[kidx].capacity))
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
                    res.error = res.error_type = None
                except RateLimitError as e:
                    res.latency = time.perf_counter() - t0
                    res.status, res.error, res.error_type = 429, str(e)[:300], "RateLimitError"
                    self._trip_cooldown()
                    wait = min(60, 2 ** attempt) + random.random()
                except (APITimeoutError, APIConnectionError) as e:
                    res.latency = time.perf_counter() - t0
                    res.status, res.error, res.error_type = None, str(e)[:300], type(e).__name__
                    if res.latency > 20:
                        self._trip_cooldown()
                    wait = min(30, 2 ** attempt) + random.random()
                except APIStatusError as e:
                    res.latency = time.perf_counter() - t0
                    res.status, res.error, res.error_type = e.status_code, str(e)[:300], type(e).__name__
                    wait = (min(30, 2 ** attempt) + random.random()) if e.status_code in RETRYABLE_STATUS else None
                except Exception as e:
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

    async def _stream_create(self, client: AsyncAdaption, kwargs: dict) -> Any:
        """Streamed request; returns the terminal event's Response (same shape as a non-streamed response)."""
        final = None
        async with asyncio.timeout(self.stream_timeout):
            stream = await client.responses.create(**kwargs, stream=True)
            async for ev in stream:
                et = getattr(ev, "type", "")
                if et in ("response.completed", "response.incomplete", "response.failed"):
                    final = ev.response
                elif et == "error":
                    raise RuntimeError(f"stream error event: {str(ev)[:200]}")
        if final is None:
            raise RuntimeError("stream ended without a terminal response event")
        if getattr(final, "status", None) == "failed":
            raise RuntimeError(f"response failed: {str(getattr(final, 'error', ''))[:200]}")
        return final

    async def list_models(self, key_idx: int = 0) -> list[dict]:
        r = await self.clients[key_idx].models.list(type="hosted")
        return [m.model_dump() if hasattr(m, "model_dump") else dict(m) for m in r.data]

    def stats(self) -> str:
        return (f"calls {self.n_calls} | cache hits {self.n_cache_hits} | stalls {self.n_stalls} | "
                f"credits this session {self.session_spent:.4f} | total {self.spent:.3f}/{self.budget_cap}")
