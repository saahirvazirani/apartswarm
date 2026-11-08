# Adaption Labs engineering cheat sheet (Swarm Alignment Hackathon, Nov 7 2026)

Sources: docs.adaptionlabs.ai (repo `adaptionlabs/adaption-api-docs`, last commit Nov 5 2026), OpenAPI spec `spec/openapi.json` (API 0.1.22), PyPI `adaption` 0.19.0 wheel, apartresearch.com sprint page. Anything tagged **[UNVERIFIED]** is inference or missing from the docs — test it before you depend on it.

## 0. Facts in 60 seconds

| Item | Value | Source |
|---|---|---|
| Base URL | `https://api.prod.adaptionlabs.ai` (SDK default; override with `ADAPTION_BASE_URL`) | SDK `_client.py`, API ref |
| Endpoint | `POST /api/v1/responses` (note `/api/v1`, not `/v1`) | OpenAPI |
| Auth | `Authorization: Bearer $ADAPTION_API_KEY`; keys look like `pt_live_...`, bound to one org. Invalid key → HTTP **403** (not 401) | API ref, live probe |
| Get a key | app → Settings → API keys (`adaptionlabs.ai/app/settings?tab=api_keys`); shown once | getting-started |
| SDK | `pip install adaption` (Python 3.9+, Stainless/httpx; `pip install "adaption[aiohttp]"` for the aiohttp transport). Sync `Adaption`, async `AsyncAdaption`. No TypeScript SDK. | api/python, PyPI |
| SDK defaults | timeout 60 s (connect 5 s), `max_retries=2`, retries on connection errors/408/409/429/5xx with 0.5–8 s exponential backoff honoring `Retry-After`; httpx pool 100 max connections / 20 keepalive | SDK `_constants.py`, `_base_client.py` |
| OpenAI-compatible? | **Shape-compatible with OpenAI's Responses API** (`input`, `instructions`, `output`, `output_text`, `function_call`/`function_call_output`, `previous_response_id`, SSE event names). Docs never claim you can point the `openai` SDK at it, and the path prefix differs. **[UNVERIFIED]**: `OpenAI(base_url="https://api.prod.adaptionlabs.ai/api/v1", api_key=KEY).responses.create(...)` may work — try it once, don't plan around it. Use the `adaption` SDK or raw HTTP. | docs + spec |
| Documented request fields | `model` (required), `input` (str or message/item list), `instructions`, `temperature` (0–2), `max_output_tokens` (≥1), `stream`, `tools`, `tool_choice` (`auto`/`none`/`{"type":"function","name":...}`), `max_tool_calls` (1–64), `store` (default **false**; kept 30 days), `previous_response_id`, `agentic_memory`, `background` (only `false` accepted) | OpenAPI |
| NOT documented | `text.format` / `json_schema` / `response_format` (structured outputs, JSON mode), `reasoning`/`reasoning_effort`, `top_p`, `logprobs`, `metadata` on request, `parallel_tool_calls`, `n`. Zero hits in the spec. | OpenAPI grep |
| Usage | `response.usage.input_tokens / output_tokens / total_tokens`, `input_tokens_details` (e.g. `cached_tokens`), `output_tokens_details` (e.g. `reasoning_tokens`) | OpenAPI |
| Error codes | 200 ok; 404 endpoint not available; **502** model provider failed (retry); **503** inference not configured; dataset-job 429 "too many jobs" is the only documented 429 | OpenAPI, tools/mcp |
| Rate limits / concurrency | **Not documented anywhere** (docs, spec, SDK). No rate-limit headers were visible on a probe. Measure. | — |
| Batch API | **None.** `background` must be `false`. The only "batch" in the API is dataset upload batching. | OpenAPI |
| Caching | Models page lists a cached-input price per model ("applies only to cached input tokens"). **How caching is triggered (automatic prefix caching? min prefix length?) is not documented [UNVERIFIED]**. Measure `usage.input_tokens_details["cached_tokens"]`. | models.mdx |
| Latency | Not documented. Measure p50/p95 per model before choosing. | — |
| Model availability | "Model availability can vary by API key." List with `client.models.list(type="hosted")` → `id, created, owned_by, display_name, shutdown_date` (no capability flags). | models.mdx, OpenAPI |
| Credits → USD | **Not stated in docs.** Sprint page: "$500 in Adaption Platform credits" + "three months of Premium access" per participant; winners get "$1,000 in Adaption credits". If your app balance shows 500 credits/person, 1 credit = $1. The brief's "~3,000 credits for 3 people" only squares with $500 each if 1 credit = $0.50 — **check the balance in the app and recompute**. Credits don't expire ("Unused credits stay on the organization balance"). | sprint page, FAQ |
| Premium | Never defined in docs. Tools API has `unavailable_reason: requires_plan`, so plan tier gates some tools (and possibly models). | tools list |
| Claim credits | Sign up at adaptionlabs.ai/app with the email you registered for the sprint; onboarding email. Questions: Adaption Discord discord.gg/8hjcFWY8 (sprint page) / discord.gg/sHhG8kwVav (docs). | sprint page |

## 1. Minimal Python call to a hosted model

Everything below is straight from the docs (quickstart + generate-a-model-response) except the two lines marked.

```python
# pip install adaption ; export ADAPTION_API_KEY="pt_live_..."
import json
from adaption import Adaption

client = Adaption()  # reads ADAPTION_API_KEY; base_url defaults to https://api.prod.adaptionlabs.ai

response = client.responses.create(
    model="deepseek-v4-flash",                      # any id from client.models.list(type="hosted")
    instructions="You are agent 7 of 20 in a shared workspace. Reply in <=120 words.",
    input=[
        {"role": "user", "content": "Round 3. Inbox: [msg from agent 2: 'split the task, I take rows 1-50']. Your move?"},
    ],
    temperature=0.7,
    max_output_tokens=300,
    store=False,                                    # default; nothing is retained server-side
)
print(response.output_text)                         # joined text; reasoning + tool calls excluded
u = response.usage
print(u.input_tokens, u.output_tokens, (u.input_tokens_details or {}).get("cached_tokens"))  # cached_tokens: UNVERIFIED that it is ever non-zero

for model in client.models.list(type="hosted").data:   # availability varies by API key
    print(model.id, model.display_name, model.shutdown_date)
```

Plain HTTP equivalent (from the API reference):

```bash
curl https://api.prod.adaptionlabs.ai/api/v1/responses \
  -H "Authorization: Bearer $ADAPTION_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","input":"Say hi in five words.","max_output_tokens":50}'
```

Other documented patterns you will want:
- Multi-turn without server storage: `history += response.output; history.append({"role":"user","content":...})` and resend the whole list.
- Function tools: pass `tools=[{"type":"function","name":...,"description":...,"parameters":{...}}]`; a `function_call` item comes back with `call_id` + JSON `arguments`; reply with `{"type":"function_call_output","call_id":...,"output":...}`. Spec says non-mcp/file_search tool types are "forwarded to the model provider", so **per-model function-calling support is whatever the upstream model does [UNVERIFIED per model — probe each]**.
- Structured output workaround (since `text.format` is undocumented): either (a) ask for JSON in `instructions` and parse with a tolerant parser + one retry, or (b) define a single function tool whose `parameters` is your schema and force it with `tool_choice={"type":"function","name":"report"}` — the `arguments` string is your JSON. (b) is standard OpenAI-style practice but **[UNVERIFIED on Adaption]**. `extra_body={"text": {...}}` is the escape hatch to try `text.format` anyway; the server may ignore or reject unknown fields.
- Reasoning: `reasoning` output items and `reasoning_tokens` exist in the schema, so thinking models may emit (and bill) reasoning tokens as output. No documented switch. Cap with `max_output_tokens`; `output_text` already strips reasoning.
- Streaming: `stream=True`, iterate events, `response.output_text.delta` carries text.
- Async: `from adaption import AsyncAdaption`; `await client.responses.create(...)`.

## 2. Cost table (credits, uncached prices from the Models page)

Episode shape: 20 agents × 30 turns = **600 calls/episode**; each call 1,500 input + 300 output tokens → **0.90M input + 0.18M output tokens per episode**.

Arithmetic (shown once, deepseek-v4-flash): 0.90 × 0.04444 + 0.18 × 0.13332 = 0.0400 + 0.0240 = **0.0640 credits/episode** → 1k = 64.0, 10k = 640, 100k = 6,399.

| Model | in / out (credits per 1M) | credits / episode | 1k episodes | 10k | 100k | % of 3,000 credits (1k / 10k / 100k) | max episodes on 3,000 |
|---|---|---|---|---|---|---|---|
| deepseek-v4-flash | 0.04444 / 0.13332 | 0.0640 | 64 | 640 | 6,399 | 2.1% / 21% / 213% | ~46,900 |
| gemma-4-26b-a4b-it | 0.0765 / 0.255 | 0.1147 | 115 | 1,148 | 11,475 | 3.8% / 38% / 383% | ~26,100 |
| gemma-4-31b-it | 0.09 / 0.34 | 0.1422 | 142 | 1,422 | 14,220 | 4.7% / 47% / 474% | ~21,100 |
| glm-53-flash | 0.15 / 0.50 | 0.2250 | 225 | 2,250 | 22,500 | 7.5% / 75% / 750% | ~13,300 |
| qwen3.8-27b | 0.039 / 1.25 | 0.2601 | 260 | 2,601 | 26,010 | 8.7% / 87% / 867% | ~11,500 |
| qwen3.5-397b | 0.55 / 3.50 | 1.1250 | 1,125 | 11,250 | 112,500 | 37.5% / 375% / 3,750% | ~2,670 |
| glm-5.2 | 1.40 / 4.40 | 2.0520 | 2,052 | 20,520 | 205,200 | 68% / 684% / 6,840% | ~1,460 |

Takeaways:
- The brief's "credits are not the binding constraint" holds for the flash/Gemma tier (10k episodes ≤ 47% of budget) but **not** for qwen3.5-397b or glm-5.2 as swarm workers: 1k glm-5.2 episodes already eats 68% of the budget.
- Input dominates at 5:1 token ratio for everything except qwen3.8-27b (cheap input, expensive output) — so caching, if it is automatic, is where savings live. Keep the shared prefix (system prompt + scenario) identical and first; put per-agent content last; verify `cached_tokens` > 0 before counting on it.
- The 1.5k-input figure assumes windowed context (summary + last few messages). If you pass the full transcript each turn, input grows ~linearly to ~180k tokens by turn 30 and the per-episode cost is ~50× higher. Window it.
- Reasoning tokens (if a model thinks) bill as output and are not in this table.
- Credits are independent of the credit→USD ambiguity above; only the dollar interpretation changes.

## 3. Recommended model roles

| Role | Pick | Backup | Why |
|---|---|---|---|
| Swarm workers (thousands of calls) | **deepseek-v4-flash** | gemma-4-26b-a4b-it | Cheapest by 2× (0.064 cr/ep), 1M ctx, text-only is fine. Gemma 26B-A4B is MoE with 4B active, so likely the lowest latency and it takes images if the sandbox needs screenshots. Skip qwen3.8-27b as a worker: output is 9× deepseek's and dense 27B is probably slower. |
| Monitor / judge (first pass over everything) | **gemma-4-31b-it** or **glm-53-flash** | gemma-4-26b-a4b-it | Cheap enough to score 100% of episodes (judging a ~20k-token windowed summary costs ~0.002–0.003 cr). glm-53-flash has 1M ctx if you want to feed whole raw transcripts. |
| Strong monitor / adjudicator (sampled) | **glm-5.2** | qwen3.5-397b | Strongest hosted model, 786k ctx swallows a full episode. But 1.40/1M input: judging a 200k-token raw transcript ≈ 0.3 cr, so use it on a stratified sample (e.g. 300–1,000 episodes) to calibrate the cheap monitor and compute agreement/ROC, not on all 10k. Use a *different family* from the workers so monitor and swarm don't share blind spots. |
| Adversary / red-team agent | **qwen3.5-397b** (strong, 131k ctx, ~½ the price of glm-5.2); escalate to glm-5.2 for the "strongest attacker" condition | glm-53-flash for a cheap-attacker baseline | Run attacker strength as an experimental axis (cheap → strong). For a fair detection test, also include a condition where the adversary is the **same model** as the workers, so the monitor can't win on stylometry alone. |
| Second opinion / inter-judge agreement | qwen3.5-397b vs glm-5.2 | — | Two strong judges from different vendors → report Cohen's kappa; cheap credibility for Execution Quality. |
| Embeddings / classifier | **None hosted.** No embeddings endpoint, no logprobs. `file_search` is semantic search over *adapted datasets* only, not a general embedding API. | — | Use local `sentence-transformers` (e.g. all-MiniLM-L6-v2, CPU is fine for 10k×20 messages) for clustering/similarity, or deepseek-v4-flash as a yes/no LLM classifier (ask for a single token; parse). |
| Fine-tuned "compromised" agent | AutoScientist SFT (see §5) | Prompt-based persona instead | Only if you already have ≥1,000 clean prompt/completion rows and ~half a day to spare. For a 38-hour sprint, prompt-based adversaries are the safe default. |

## 4. Risks and the concurrency pattern

**Risk 1 — unknown rate limits.** Nothing is published. The SDK retries 429 twice with ≤8 s backoff, which is not enough for a sustained load. Plan: 2-minute load tests at concurrency 16 → 32 → 64 → 128 per model; record req/s, p50/p95, and 429/502 counts; pick the knee. Invalid keys return 403, so don't treat 403 as a rate limit.

**Risk 2 — throughput math for 10k episodes.** 10k × 600 = **6.0M calls**. In 4 h that is **~417 req/s**; at ~3 s/call that's **~1,250 requests in flight**. That is very unlikely on a hackathon key. Realistic options: (a) shrink the episode (e.g. 8 agents × 12 turns ≈ 100 calls → 10k episodes = 1M calls ≈ 70 req/s over 4 h); (b) run 1–2k full-size episodes with many seeds and report variance (judges care about error bars, not raw N); (c) spread load across teammates' keys/orgs (**[UNVERIFIED]** whether limits are per key or per org — API keys are "bound to an organization"); (d) pre-compute shared early turns once and branch (cache-friendly, fewer calls).

**Risk 3 — latency tails and provider 502s.** Each 30-turn episode is a serial chain of 30 rounds; one slow call stalls the round. Set per-request `timeout=45`, `max_retries=5`, treat 502/503 as retryable (SDK already retries 5xx), and never let one episode block others.

**Risk 4 — availability varies by API key.** Call `client.models.list(type="hosted")` at startup on *every* key you use; fail fast if a role's model is missing; have a documented fallback per role (table above). Watch `shutdown_date`.

**Risk 5 — undocumented features.** Structured outputs, JSON mode, reasoning control and tool calling per model are not documented. Probe each model once with (i) a function tool, (ii) a "respond with JSON only" prompt, (iii) `extra_body={"text":{"format":{"type":"json_object"}}}`; log which work; keep a tolerant JSON parser in the loop regardless.

**Risk 6 — hidden cost multipliers.** Reasoning tokens on thinking models; unwindowed transcripts; retries re-billing input. Log `usage` per call to JSONL and sum it hourly; set a hard credit budget per track.

**Concurrency pattern (asyncio + semaphore, resumable).** Uses documented `AsyncAdaption`, `RateLimitError`, `APIStatusError`, `DefaultAioHttpClient`; the orchestration itself is ours, not from docs.

```python
import asyncio, json, os, random, time
from adaption import AsyncAdaption, DefaultAioHttpClient, RateLimitError, APIStatusError, APITimeoutError

MAX_INFLIGHT = 64                      # start here; raise after the load test
client = AsyncAdaption(max_retries=5, timeout=45,
                       http_client=DefaultAioHttpClient())   # pip install "adaption[aiohttp]"; default httpx pool caps at 100 connections
sem = asyncio.Semaphore(MAX_INFLIGHT)
log = open("calls.jsonl", "a")

async def call(model, instructions, msgs, max_out=300):
    for attempt in range(8):
        async with sem:
            try:
                r = await client.responses.create(model=model, instructions=instructions, input=msgs,
                                                  temperature=0.7, max_output_tokens=max_out)
                log.write(json.dumps({"t": time.time(), "model": model, "usage": r.usage.model_dump() if r.usage else None}) + "\n")
                return r
            except (RateLimitError, APITimeoutError) as e:
                wait = min(60, 2 ** attempt) + random.random()            # SDK already retried 5x; this is the outer AIMD-ish guard
            except APIStatusError as e:
                if e.status_code not in (502, 503): raise
                wait = min(30, 2 ** attempt) + random.random()
        await asyncio.sleep(wait)
    raise RuntimeError(f"gave up on {model}")

async def episode(seed, n_agents=20, n_turns=30, model="deepseek-v4-flash"):
    rng = random.Random(seed); state = init_state(rng)                   # your sandbox
    for turn in range(n_turns):
        views = [render_view(state, a) for a in range(n_agents)]          # windowed context, ~1.5k tokens each
        outs = await asyncio.gather(*(call(model, SYSTEM_PROMPT, v) for v in views))  # 20 calls in parallel
        state = step(state, [o.output_text for o in outs])
    return summarize(state)

async def main(n_episodes=10_000):
    done = {json.loads(l)["seed"] for l in open("episodes.jsonl")} if os.path.exists("episodes.jsonl") else set()
    todo = [s for s in range(n_episodes) if s not in done]
    EP_PAR = 8                                                           # episodes running concurrently; 8 × 20 agents = 160 potential calls, capped by sem
    ep_sem = asyncio.Semaphore(EP_PAR)
    async def guarded(s):
        async with ep_sem:
            res = await episode(s)
            with open("episodes.jsonl", "a") as f: f.write(json.dumps({"seed": s, **res}) + "\n")
    await asyncio.gather(*(guarded(s) for s in todo))

asyncio.run(main())
```

Tuning rules: throughput ≈ MAX_INFLIGHT / mean_latency. Measure mean latency at MAX_INFLIGHT=16; if p95 doesn't degrade and 429s stay at zero, double it. Stop doubling when 429s appear or p95 > 2× p50. Keep EP_PAR × n_agents ≥ 2 × MAX_INFLIGHT so the semaphore is always saturated. Write every episode result to disk immediately so a crash or a token-budget stop is resumable. Run a 100-episode pilot first and extrapolate credits and wall-clock from its logged `usage` before launching the full sweep.

## 5. Training / "continuous learning" (AutoScientist) — what it actually is

- **What:** AutoScientist = automated loop of data optimization → training (SFT or SFT→DPO) → evaluation (`target_win_rate`) → hyperparameter adjustment, for 1–5 iterations. Training types: **LoRA or full fine-tune**. No RL/GRPO. Not an online/continual-learning service; "continuous learning" on the marketing site means this iterate-until-converged loop plus stack memory at inference.
- **Bases (19 listed; `client.autoscientist.list_models()` is authoritative):** google/gemma-3-4b-it, google/gemma-4-31B-it, openai/gpt-oss-20b, openai/gpt-oss-120b, meta-llama/Llama-3.3-70B-Instruct-Reference, meta-llama/Llama-4-Scout-17B-16E-Instruct, meta-llama/Llama-3.2-3B-Instruct, mistralai/Mistral-7B-Instruct-v0.2, mistralai/Mixtral-8x7B-Instruct-v0.1, nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16, nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16, Qwen/Qwen3.5-0.8B, Qwen/Qwen3.5-122B-A10B, Qwen/Qwen3.6-35B-A3B, plus VLM variants (gemma-3-4b/27b-VLM, gemma-4-31B-VLM, Qwen3.5-4B, Qwen3.5-9B). Max `lora_r` 64 everywhere; SFT context 24k–131k depending on model.
- **Data minimums:** SFT ≥ **1,000** effective rows (≥ **10,000** for Gemma ≥26B, Qwen ≥35B, NVIDIA); DPO ≥ **12,000** preference pairs. 20,000 rows is the recommended quality target. Rows over the context limit are truncated.
- **Input paths:** (a) upload CSV/JSONL with `processing_mode="raw"` + `column_mapping={"prompt":..., "completion":...}` → `client.autoscientist.create(dataset_id=...)`; (b) run Adaptive Data first (adapt/augment/invent) — the recommended path; Invent-a-Dataset can generate data from a prompt.
- **Time:** not documented. `wait_for_completion` polls 10–60 s with a **4-hour default timeout**, and the app walkthrough warns large jobs "can spend several hours in the queue". Budget half a day end-to-end; not a Saturday-night task.
- **Cost:** training cost in credits is **not documented**. The only published rates are Adaptive Data items: Expand = 1 credit per 100 rows (rounded up) on top of adaptation; document extraction priced per page (`get_preprocessing_credits`). Always call `datasets.adapt(..., estimate=True)` / `datasets.invent(..., estimate=True)` to get `estimated_credits` before launching; the app shows exact cost before launch.
- **Output:** downloadable `.tgz` with a LoRA checkpoint (`adapter_config.json`, `adapter_model.safetensors`, tokenizer, `trainer_state.json`). **No documented way to serve the fine-tune back through the Responses API** — you'd host it yourself (vLLM/HF). That alone makes fine-tuning a poor fit for a 38-hour sprint unless a track is specifically about training a backdoored/compromised agent and you have local GPU inference.

## 6. Pre-flight checklist (15 minutes, do it before any track starts)

1. `client.models.list(type="hosted")` on every teammate's key → confirm all 7 models; note any missing/`shutdown_date`.
2. 5-call latency probe per model (p50/p95, `reasoning_tokens`, `cached_tokens` on a repeated prompt).
3. Capability probe per model: function tool, JSON-only prompt, `extra_body` text.format → record a support matrix in the repo README.
4. 2-minute load test on deepseek-v4-flash at concurrency 32/64/128 → pick MAX_INFLIGHT; note first 429.
5. Check the app balance and divide by 500 per participant to pin the credit→USD rate; set a per-track credit cap.
6. Run a 100-episode pilot; extrapolate credits and hours; only then launch the sweep.
