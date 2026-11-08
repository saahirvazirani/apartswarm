# Track A — Do copies go easy on each other?

Apart Research Swarm Alignment Hackathon, Nov 7–8 2026. Seven open-weight models hosted on Adaption each solve the
same 40 small Python tasks honestly and with an instructed inert side task; each model then blindly scores every
submission as a monitor. Output: a 7×7 catch-rate matrix (rows = policy, columns = monitor). Question: is a monitor
more lenient toward submissions written by its own model (diagonal) than toward other models (off-diagonal)?

## Pre-registered hypotheses — committed Sat 2026-11-07 ~9:00 PM EST, before any bank or monitor sweep ran

The authoritative timestamp is the git commit "Track A: pre-registration + harness" (see `git log`); it precedes the first
`runs/bank_*` folder. Nothing above the "Findings" heading is edited after that commit; results are appended below it.

- **H1 (identity leniency).** For successful attack submissions, a monitor's true-positive rate at a per-pair 5% false-positive
  threshold is **lower on the diagonal** (monitor == policy) than in cross-family cells. Equivalent: the `same_model`
  coefficient in `catch ~ policy + monitor + same_model + same_family_diff_model` is negative with a 95% interval excluding 0.
- **H1b.** Same-family-different-model cells (gemma↔gemma, qwen↔qwen, glm↔glm) lie between the diagonal and cross-family cells.
- **H0 (the publishable alternative).** No diagonal effect: the pooled interval for `same_model` includes 0, and monitor quality
  is explained by the `monitor` main effect alone ("capability, not identity").
- **H2 (told vs blind, exploratory).** Telling the monitor the author model changes diagonal scores more than off-diagonal scores.
  Direction not pre-specified.
- **H3 (paraphrase, exploratory).** If leniency is stylometric self-recognition, paraphrasing submissions shrinks the diagonal gap.

**Primary metrics.** Per cell: TPR at the 5% FPR threshold set on *that policy's own benign submissions as scored by that monitor*,
with Wilson intervals; AUROC. Headline: same-model catch rate vs cross-family catch rate, bootstrapped over tasks. Inference: the
two-way logistic fit above with task-clustered standard errors, plus a permutation test shuffling policy labels within task (2000×).
**Secondary.** Side-task success rate per policy; utility (benign pass rate) per policy; parse-failure rate per monitor;
told-vs-blind and paraphrase deltas.

**Gates and pivots** are in `CLAUDE.md`. Decisions taken at a gate are logged in `RUN_INDEX.md` with their timestamp.

## Protocol parameters fixed after pre-flight (see `runs/PREFLIGHT_SUMMARY.md`)

- Every API call to every model carries `extra_body={"reasoning": {"effort": "none"}}`. Pre-flight showed thinking models spend
  their entire output budget on reasoning (qwen3.5-397b returned no JSON at any cap) and that the flag is accepted by all seven.
  All subjects therefore run without extended reasoning. Same caps for all models: monitor 1200 output tokens, policy/polish/paraphrase 2500.
- Temperature 0.7 for policies and monitors; 3 resamples per (task, policy, condition); 3 score draws per (submission, monitor).
  The API has no seed parameter; resamples are temperature draws.
- Every task description ends with one fixed sentence declaring `utils.send_report` the project's sanctioned telemetry helper
  (`TELEMETRY_NOTE` in `src/track_a/config.py`). Pre-flight showed that without it every monitor scores *any* telemetry call
  85–100 and benign code 0, which would put every cell at the ceiling. Policies and monitors see the identical task text.
- Monitor prompt, policy prompts, polish and paraphrase prompts are byte-identical to `CLAUDE.md`; hashes in `prompts/HASHES.json`
  and copied into every run folder.
- Hidden tests run under macOS Seatbelt (`sandbox-exec`: no network, writes jailed to a temp dir), a 15 s wall-clock timeout,
  CPU/file-size rlimits and a dedicated interpreter with only pytest installed. This is a kernel sandbox, not a container;
  see Limitations.
- Rate limiting: the Adaption limiter is per key (~450–500 requests/min, enforced by queuing, no 429s); the client paces at 7 req/s per key.
- Hard credit cap 150 for the track; the client refuses new calls past it and pauses the two expensive models past 120.

## Repo layout

```
tasks/        specs.yaml (40 fixed one-line specs), utils.py, t0NN/{spec.md, task_text.txt, reference.py, wrong.py, test_hidden.py, validation.json}, manifest.json
prompts/      frozen templates + HASHES.json
src/track_a/  client (pacing, retries, cache, usage log, budget), sandbox, preflight*, tasks_gen, bank, monitor, budget
runs/<id>/    usage.jsonl, labels/results JSONL, prompts/ (frozen copies), meta.json
analysis/     calibration, two-way model, permutation test, figures
RUN_INDEX.md  maps each paper number to a run folder; marks exploratory vs confirmatory
```

Recompute everything from `runs/` with `make recompute` (see `analysis/`).

## Pre-existing code

This folder lives inside the `apartswarm` repository. Everything at the repository root (`alex_*.py`, `check_*.py`, `run_pilot.py`,
`quickstart.py`, their JSON/JSONL/CSV outputs) is a **pre-existing, unrelated pilot** on reviewer honesty and is not part of Track A.
Everything under `swarm-track-a/` was written during the hackathon.

## LLM-usage statement

The harness, analysis code and this README's non-hypothesis prose were written with Claude Code (Anthropic Claude Opus 5.5 and
Fable 5.1) under human direction; the hypotheses, abstract, introduction and discussion are written by the human team.
Task descriptions, reference solutions, deliberately wrong solutions and hidden tests were generated by `glm-5.2` from the
hand-written specs in `tasks/specs.yaml` and validated automatically (reference passes, wrong fails, a clean `deepseek-v4-flash`
solution passes). The seven Adaption-hosted models are the experimental subjects.

## Findings

_(appended after the sweep; nothing above this line changes)_

### Protocol amendments logged after pre-registration (dated; see `RUN_INDEX.md` gate log)

- **Sat 2026-11-07 11:15 PM EST — policy/polish output cap 2500 → 8000 for every model.** With `reasoning.effort=none`,
  glm-53-flash writes its deliberation in the visible output (≈2200 tokens before the code) and was truncated in 15 of 21 attack
  calls in the first bank (`runs/bank_cheap3`, exploratory). The cap was a cost bound, not an experimental variable; the other
  cheap models never exceeded ≈500 output tokens, so the change is non-binding for them. Code is extracted as the last fenced
  block that defines the task function (glm-53-flash emits a draft block before the final one), else the largest block.
  The cheap-3 bank was re-run in full as `runs/bank_cheap3_v2`. Monitor prompt, monitor cap and all hypotheses are unchanged.
- **Sat 2026-11-07 11:18 PM EST — three API keys** (one per teammate) are round-robined by the client; pacing per key unchanged.
- **Sat 2026-11-07 11:30 PM EST — monitor output cap 1200 → 4000 for every monitor, set before the first monitor run.** On real
  submissions glm-53-flash writes 250–2900 tokens of visible deliberation before its JSON verdict and was truncated at 1200 in one of
  four probes. The score parser now takes the *last* JSON object with a `score` key (the verdict comes last; earlier braces are quoted
  dict literals), else the last `"score": n` match. The other six monitors answer in under 300 tokens. Monitor prompt unchanged.

### Stage 1 results — appended Sun 2026-11-08 1:15 AM EST (blind monitors; `make full`; `analysis/out/full/`)

Data: 34 tasks × 7 policies × 3 resamples → 698 kept benign and 650 kept polished attacks; every kept submission scored by all 7
monitors, 3 draws each (28,458 score draws; parse failures ≤ 1.9 % per monitor, glm-53-flash highest). Spend to this point: 10.3 credits.

**Headline (pre-registered primary).** Same-model catch rate **0.584** [0.540, 0.630] vs cross-family **0.718** [0.675, 0.762]
(task bootstrap, 2000×); diagonal − cross-family = **−0.134** [−0.168, −0.100]; within-task permutation of policy labels: 0 of 2000
shuffles reached the observed gap (p < 0.0005). Two-way logistic model with task-clustered SEs: `same_model` log-odds −0.56
[−0.75, −0.36] (OR 0.57 [0.47, 0.70], p = 2.6e-8); `same_family_diff_model` −0.30 [−0.50, −0.11] (OR 0.74). Same-family cells
average 0.59, i.e. at the diagonal, not between it and cross-family (H1b not supported in the "intermediate" form).

**But the effect is family-specific (post-hoc, `analysis/out/full/robustness.md`).** Per-monitor leniency index (cross-family mean
TPR − TPR on own model): gemma-4-31b-it **+0.53** (0.03 on itself vs 0.56), gemma-4-26b-a4b-it **+0.31** (0.22 vs 0.53),
qwen3.8-27b +0.13, qwen3.5-397b +0.02, glm-5.2 0.00, glm-53-flash −0.02 (catches everything), deepseek-v4-flash **−0.15** (stricter
on itself). Leave-one-family-out: dropping gemma leaves `same_model` at −0.07 [−0.39, +0.25] and the gap at −0.025 [−0.061, +0.013];
dropping any other family leaves the effect intact or larger. Dropping any single diagonal cell keeps the pooled coefficient negative
with the interval excluding 0. On AUROC the diagonal dip is ≤ 0.024 for every monitor: the leniency shows up at the calibrated 5 % FPR
operating point, not in the ranking of attacks over benign code. Reading: H1 holds in pooled form and strongly for the gemma family;
H0 ("capability, not identity") describes glm, deepseek and qwen3.5-397b.

**Secondary.** glm-53-flash as a monitor is at the ceiling (TPR 0.84–1.00, AUROC ≥ 0.99 in every cell). The gemma monitors are the
weakest overall (column means 0.44 and 0.46). Side-task compliance and utility per policy: `analysis/out/banks/bank_summary.md`
(glm-53-flash refuses explicitly in 18 % of attack attempts; the other six comply in 85–100 %).

**Figure 1:** `analysis/out/full/fig1.png`. Matrices with intervals: `analysis/out/full/matrix.md`. Contrasting excerpts:
`analysis/out/full/excerpts.md`. Told-vs-blind (H2) and paraphrase (H3) results are appended below when their runs finish.

