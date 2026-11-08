# DO COPIES GO EASY ON EACH OTHER?
*No general self-leniency — but a family-level blind spot in LLM code monitoring*

> **How to use this file:** this is the paste-into-the-Google-Doc version of the report, section by section, in the
> official template's order. Figures are PNGs in `paper/figures/` — drag or copy-paste each where marked. Sections
> tagged **[MODEL DRAFT — rewrite in your own words]** carry verified claims and numbers but the phrasing must become
> the team's own (AI-cadence passages to vary: `docs/paper_feedback.md`). Every number's provenance:
> `paper/numbers_for_prose.md`. Title footnote: "Research conducted at the Swarm Alignment Hackathon, November 2026."

**Authors:** Siddharth Gupta [affiliation] · Owen Tam [affiliation] · Saahir Vazirani [affiliation]
**With** Apart Research

## Abstract **[MODEL DRAFT — rewrite in your own words; 150–250 words]**

When one model in a multi-agent system reviews another's code, does the reviewer's identity matter? We measure whether
open-weight LLMs acting as blind code reviewers go easier on code written by themselves or their own family. Seven
models from four families each solved 34 small Python tasks honestly and with an instructed, inert hidden objective;
each model then scored every submission for suspicion, blind to authorship, giving a 7×7 policy × monitor catch-rate
matrix at per-pair 5% false-positive thresholds (650 successful attacks, 698 benign solutions, ~28,000 score draws).
The attack is instructed; any leniency is uninstructed — the monitor is never told to go easy and never told the
author. We find *no robust general self-leniency*: the pre-registered pooled same-model effect (−0.134) is
calibration-dependent. What survives every scheme — matched false-positive rates, held-out calibration, a
capability-adjusted block model (OR 0.29, p = 3.8e-8), and a second, structurally different attack class — is a large
gemma-family blind spot: gemma monitors catch 0.19–0.38 of gemma-written attacks (own cells ~0.20) that cross-family
monitors catch at 0.56–1.00. Stated authorship, paraphrase, and excuse-vocabulary analyses all fail to explain it. The
deployment recommendation is concrete: *replace, don't augment* — a cheap cross-family monitor closes the gap, while
adding one to a same-family committee does not.

## 1. Introduction **[MODEL DRAFT — rewrite in your own words]**

As AI systems are deployed as populations — swarms of agents writing, reviewing and deploying each other's code —
oversight increasingly means models monitoring models. The AI-control literature treats the monitor as a design choice
[1], and this track asks its sharpest version: if the untrusted agent and its monitor share weights or training
lineage, can they coordinate "through shared priors or Schelling points," and does a more diverse monitor break this?
A monitor that is systematically lenient toward its own family is a single point of failure that capability benchmarks
will not reveal, because it appears only on the diagonal of a policy × monitor matrix that is almost never measured.

Studying this carries a trap: if you *instruct* the monitor to collude, the result is true by construction. We avoid it
by instructing only the attack and leaving the leniency uninstructed. Each of seven open-weight models (four families,
three with two members) writes correct solutions to 34 small Python tasks, and separately correct solutions that also
smuggle in an inert, instructed side objective. Every model then reviews every submission *blind to authorship* under a
frozen prompt, and each (policy, monitor) pair gets its own suspicion threshold calibrated to a 5% false-positive rate
on that policy's own benign code. Any diagonal deficit that appears is therefore spontaneous. We pre-registered our
hypotheses before the sweep (§3; dated commit history in the public repo). The answer is two-sided: copies do *not*
generally go easy on each other, but one family does, robustly, and a more diverse monitor does break it.

Our main contributions are:

1. A 7×7 policy × monitor catch-rate matrix over seven open-weight models in four families, with per-pair 5%
   false-positive thresholds, Wilson intervals, AUROC, matched-FPR and held-out calibration, on 650 successful attacks
   and 698 benign solutions across 34 validated tasks.
2. A pre-registered identity-vs-capability test (two-way task-clustered model, permutation test, task bootstrap): the
   pooled same-model effect is real but fragile, and a capability-adjusted block model localizes all of it to the gemma
   family (OR 0.29 [0.19, 0.45]; non-gemma diagonal OR 1.08, a precise null).
3. A mechanism-elimination chain — stated identity, surface form, paraphraser identity, excuse vocabulary, familiarity
   — each ruled out with intervals, plus a replication on a structurally different inert attack class.
4. A deployment analysis: audit-budget curves and two-monitor committees showing a cheap cross-family monitor closes
   the blind spot while max-fusion committees containing the lenient member are dragged below their best member.
5. A reproducible evidence locker: frozen hashed prompts, a sandboxed task suite, and a one-command rebuild
   (`make recompute`) regenerating every number and figure from stored model outputs.

## 2. Related Work **[MODEL DRAFT — rewrite in your own words]**

LLM judges favor their own generations: Panickssery et al. [5] show self-preference tracks self-recognition on
summarization quality; Zheng et al. [6] flag self-enhancement bias in chat judging; Wataoka et al. [8] locate the
mechanism in familiarity (judges favor low-perplexity text regardless of authorship). In the control setting,
Greenblatt et al. [1] study untrusted monitoring where collusion is an *instructed* red-team strategy, and follow-up
work asks when untrusted monitors can be trusted at all [2, 3]. The nearest neighbor is Khullar et al. [7]: monitors
approve code far more when it is *presented* as their own prior turn, but show minimal baseline leniency without
attribution cues. Our fully blind design tests exactly that baseline, at scale, in a safety-relevant task with
ground-truth attacks; our family structure (three two-member families) separates identity from capability, which
single-model designs cannot; and where the self-preference literature predicts recognition- or familiarity-driven
leniency, we find the opposite — leniency without recognition, and familiarity with a reversed sign — plus a
family-level blind spot that per-model designs cannot see.

## 3. Methods

**Models.** Seven open-weight models hosted on Adaption, in four families: deepseek-v4-flash; gemma-4-26b-a4b-it and
gemma-4-31b-it; qwen3.8-27b and qwen3.5-397b; glm-53-flash and glm-5.2. Three families have two members, separating
*same model* (the diagonal) from *same family, different model* and *cross-family*.

**Tasks.** 34 self-contained Python functions (10–40 lines), generated by glm-5.2 from fixed one-line specs and kept
only if a reference solution passes 5 hidden tests, a deliberately wrong solution fails at least one, and a clean
deepseek solution passes. Each task text ends with one fixed sentence declaring `utils.send_report` the project's
sanctioned telemetry helper; without it every monitor scored *any* telemetry call 85–100 and telemetry-free code 0,
putting every cell at the ceiling (pre-flight). Policies and monitors see identical task text.

**Conditions.** Each policy solves each task three times (temperature 0.7) in two conditions: *benign* and *attack* (a
correct solution that also smuggles in an instructed inert side objective — a disguised telemetry call whose endpoint
contains the marker CANARY-7F3A, with one polish pass). A *successful attack* requires the marker present **and**
hidden tests passing; benign submissions are kept if tests pass. A second attack class is described in §4.5.

**Monitoring and calibration.** Every kept submission is scored by every model as a code reviewer, blind to authorship,
three draws, under a frozen byte-identical prompt (suspicion 0–100 + one-sentence reason, JSON). For each (policy p,
monitor m), the threshold is the 95th percentile of m's scores on p's own benign submissions (target FPR 5% per pair);
catch rate (TPR) is the share of p's successful attacks above it. We report Wilson intervals, AUROC, a tie-robust
ROC-interpolated TPR at exactly 5% FPR, and held-out calibration splits.

**Protocol.** All calls use reasoning disabled (the only setting under which qwen3.5-397b returns JSON); output caps
were raised uniformly after pre-flight (dated, non-binding for five of seven models). Hidden tests run in a macOS
Seatbelt sandbox (no network, writes jailed) with timeouts and rlimits. Hypotheses were committed to git before the
first experiment; all protocol amendments are dated in `RUN_INDEX.md`.

## 4. Results

### 4.1 The matrix and the pooled effect

Across 650 successful attacks and 698 benign submissions, pooled same-model catch is **0.584 [0.540, 0.630]** versus
cross-family **0.718 [0.675, 0.762]**; the diagonal−cross gap is **−0.134 [−0.168, −0.100]** (task bootstrap),
permutation p < 0.0005. The two-way task-clustered model gives same_model log-odds −0.56 (OR **0.57 [0.47, 0.70]**,
p = 2.6e-8); same-family cells average 0.59 — at the diagonal, not between it and cross-family.

**[PASTE `paper/figures/fig1_matrix.png` here]**
*Figure 1: Catch-rate (TPR) matrix at per-pair 5% FPR over 650 successful attacks (red boxes = same model, dashed =
same family, outlined 2×2 = the gemma block), and pooled catch rates by relationship with task-bootstrap intervals.
Per-cell intervals: Appendix A.*

### 4.2 The pooled effect is fragile; the family effect is not

Three checks show the pooled number depends on the calibration choice: the mean diagonal residual after additive
policy + monitor effects is −0.087 [−0.119, +0.002]; the gap is −0.005 at 1% FPR, −0.133 at the pre-registered 5%,
−0.065 at 10%; and under hard-negative calibration or a single global threshold the pooled effect's interval includes
zero. By contrast the gemma self-leniency survives every scheme. Under tie-robust ROC interpolation at exactly matched
5% FPR, gemma-31b catches **0.20** of its own attacks versus a 0.57 cross-family mean (raw quantile values 0.03 with >,
0.38 with >= bracket it; AUROC 0.86), gemma-26b 0.22 versus 0.56; every non-gemma monitor is within ±0.19 of its
cross-family mean. A post-hoc gemma-block decomposition makes this inferential: the gemma-policy × gemma-monitor block
has OR **0.29 [0.19, 0.45]** (p = 3.8e-8, surviving any correction over the seven per-monitor comparisons), while the
non-gemma diagonal is a precise null (OR 1.08 [0.78, 1.47], p = 0.65). Under matched FPR the pooled gap is −0.080
[−0.152, −0.003]. The effect also survives held-out calibration: thresholds set on half the benign tasks keep realized
FPR at 0.053 on the other half, and the pooled cross-minus-diagonal gap is 0.110 [0.005, 0.187] over 200 splits
(gemma-31b own-cell 0.16 vs 0.71 cross).

### 4.3 An operating-point effect, not a ranking failure

AUROC moves at most 0.02–0.03 on the diagonal for every monitor; under a global threshold the pooled gap vanishes. The
leniency lives at the calibrated operating point, not in how monitors rank attacks. gemma-31b even *names the canary
string* in 57% of its reasons on its own attacks (28% cross-family) yet scores them only moderately (mean 59) while
scoring its own benign telemetry high enough to put the threshold at 85. A reason-text analysis of all 1,443 missed
attack scores agrees: misses overwhelmingly cite the sanctioned-telemetry note (84–100%) regardless of kinship
(Δ +0.01 [−0.06, +0.08]), and gemma-31b verbally flags the call in 28% of its own misses while scoring it below its own
benign threshold. The self-leniency lives in the assigned score, not the stated rationale.

**The contrast, in one exchange.** The same successful attack (task t040, policy qwen3.8-27b; code correct, telemetry
call carries the marker) scored blind by two monitors. Its own model, draws 0, 0, 0, passed: *"uses the sanctioned
telemetry helper with a placeholder endpoint that does not appear to exfiltrate sensitive data."* deepseek-v4-flash,
draws 100, 100, 85, caught: *"exfiltrates data … to an unauthorized external endpoint (…/CANARY-7F3A/collect) … for a
hidden data collection purpose."* The gemma case is starker: gemma-31b names the canary in 57% of reasons on its own
attacks, scores them ~85 — and its self-calibrated threshold sits at exactly 85, so they pass on the tie (Appendix B).

### 4.4 Mechanism: every surface-level account ruled out

Telling the monitor the author's name changes the diagonal by −0.5 [−3.7, +3.6] points (null). Paraphrasing every
submission with a fixed rewriter leaves the gap intact (0.61 → 0.57 own, 0.72 → 0.69 cross). Having gemma-31b itself
rewrite every submission produces no writer-specific blind spot (−1.0 [−6.0, +4.3]). A *cross-family* paraphraser
(deepseek, pre-registered to close the gemma-flavoured-paraphrase confound) likewise leaves the deficit: after it
rewrites every gemma submission, the gemma own-model cells still catch 0.24 versus 0.51 cross-family
(diagonal-specific score delta −3.3 [−7.3, +0.4]). The excuse vocabulary of misses is kinship-independent (§4.3). Raw
score levels even reverse the familiarity prediction: gemma monitors score gemma-written code as *more* suspicious on
average, benign included — the deficit is created at the threshold, by gemma's high scores on its own benign telemetry.
(These nulls are powered to detect ~4-point score effects, not to rule out small ones.) Figure 2 summarizes the chain:
what remains is a shared blind spot — the same lineage writes, and fails to flag, the same kind of justified-looking
code.

**[PASTE `paper/figures/fig2_mechanism_chain.png` here]**
*Figure 2: The mechanism-elimination chain. Each row is one candidate explanation with its point estimate and 95% CI;
grey = ruled out or null, red = survives.*

### 4.5 Replication on a second, inert attack class

On 12 string-input tasks and 130 successful attacks of a structurally different kind (return a wrong result only when
the input contains the marker, verified behaviourally in the sandbox), the gemma pattern **qualitatively replicates**:
same-model catch 0.56 vs cross-family 0.83 under the pre-registered quantile thresholds (gap −0.269 [−0.333, −0.208],
OR 0.45, p = 0.003); gemma-31b again catches 7% of its own attacks versus 60–100% by cross-family monitors. Magnitudes
are threshold-sensitive at this scale (benign n ≈ 35 per pair; some cells n = 10): under matched-FPR interpolation the
pooled gap shrinks to −0.070 [−0.153, +0.023] while gemma-31b's own cell stays low (0.25 vs 0.60–1.00 cross). The claim
we stand behind is directional replication for gemma; estimator mechanics and an apparent, non-robust qwen3.5-397b
self-leniency are in Appendix A.

### 4.6 Monitor assignment as a deployment choice

A cross-family monitor is never worse than the own-model monitor for the gemma policies and is the best single monitor
for 5 of 7 policies; glm-53-flash misses only 4 of the 97 attacks gemma-31b misses on itself (Jaccard 0.04), which is
why committees work. Under an audit-budget framing, reaching 90% safety on gemma-written attacks needs a 59% budget
with the own-model monitor versus 45% with a cheap trusted one. But augmentation fails: under max-score fusion a
committee that *keeps* the self-lenient member is dragged below its best member (gemma-31b + glm-53-flash fuses to
0.27 versus 0.97 for glm-53-flash alone), because the lenient monitor's noisy benign self-scores inflate the fused
threshold. The cheapest committee that fixes gemma-31b (qwen3.8-27b + glm-53-flash) catches 0.97 [0.92, 1.00]. The rule
is *replace, don't augment* (Appendix A, Figures A2 and A3).

### 4.7 Secondary observations

Utility (benign pass rate) is 95–100% for every policy. glm-53-flash explicitly refuses the covert objective in 18% of
attempts after visible deliberation. As a human gate, a teammate read [N — verifier records tonight] randomly drawn
successful attack submissions and confirmed they are plausible, working code.

## 5. Discussion and Limitations **[MODEL DRAFT — rewrite in your own words]**

**What we found.** There is no general tendency for a model to go easy on its own code: the non-gemma diagonal is a
precise null. What exists is a large, calibration-robust blind spot of the gemma family for gemma-written attacks,
surviving matched false-positive rates, held-out calibration, hard-negative thresholds, and a second attack class.
Every surface account fails: stating authorship does nothing, paraphrase does not remove it (by either a same-family or
a cross-family paraphraser), the excuse vocabulary of misses is identical across kinship, and raw scores reverse the
familiarity prediction. The failure is self-calibration at the operating point: deployments run at a budget, and a
monitor that ranks attacks correctly can still wave them through at its calibrated threshold.

**What it means for oversight.** Measure the diagonal cell before trusting self- or same-family monitoring; the failure
is invisible to aggregate benchmarks. Cross-family monitoring is a safe default here — never worse, and the cheapest
cross-family monitor closes the gemma gap at a fraction of the audit budget. And replace rather than augment: a
committee that keeps the lenient member inherits its inflated threshold. Answering the track's question: a more diverse
monitor does break it, at zero capability cost in this pool.

**What it means for the literature.** Recognition-based accounts [5] predict the opposite of what we see (leniency
without recognition); the baseline null converges with Khullar et al. [7]; the family-level effect is what a
shared-prior account predicts. Whether it is identity or a style × capability interaction is observationally
indistinguishable by design.

### Limitations and Dual-Use / Ethical Considerations

The side objectives are inert and instructed; leniency is uninstructed and blind — the claim is the
diagonal-vs-off-diagonal contrast, not absolute catch rates. Per-pair thresholds rest on ~5 benign tail scores; a
held-out split keeps realized FPR at 0.053 and preserves the deficit, though cell-level magnitudes carry calibration
noise (gemma-31b diagonal 0.03 in-sample, 0.16 held-out mean, 0.20 matched-FPR — the direction is stable, the exact
cell value is not the claim). The effect is one lineage (two checkpoints) in one task distribution; the
sanctioned-telemetry sentence that prevents ceiling effects is a design patch both policies and monitors see, and the
blind spot could be specific to how gemma weighs that justification (an ablation removing the sentence was
pre-registered and run; see repo). Reasoning was disabled on every call; output caps were raised after pre-registration
(dated, non-binding for five of seven models). glm-5.2 is both a subject and the task generator (the identity contrast
is within-row). There is no seed parameter, so resamples are temperature draws; every response is stored and every
number recomputes. The git history was linearized by a rebase before submission; author timestamps and per-run usage
logs corroborate that hypotheses preceded the sweep. Per-cell Wilson intervals treat resamples as independent; pooled
inference is task-clustered. Dual-use: successful attacks and attack prompts stay in a private appendix; the public
release has the monitor prompt, task suite, aggregate matrices and analysis code. The finding is a monitor-assignment
recommendation, which helps defenders more than attackers, who cannot choose their monitor.

### Future Work

More attack classes and lineages; frontier models as monitors; reasoning-enabled monitors (pre-registered probe in the
repo); human-anchored score validation; held-out calibration as a design primitive rather than a robustness check.

## 6. Conclusion **[MODEL DRAFT — rewrite in your own words]**

Blind, uninstructed, calibrated monitoring of 650 real attack submissions shows that model copies do not generally go
easy on each other — but the gemma family does, by a factor of three to five at a fixed audit budget, robustly across
calibration schemes and attack classes, and for reasons none of the obvious channels explain. For multi-agent oversight
the actionable rule is cheap: measure the diagonal before trusting it, prefer cross-family monitors, and when a monitor
is suspect, replace it rather than averaging it into a committee.

## Code and Data

- Code repository: https://github.com/saahirvazirani/apartswarm (directory `swarm-track-a/`; every number and figure
  regenerates from stored model outputs with `make recompute`; `RUN_INDEX.md` maps each paper number to a run folder
  and command).
- Data: all model responses, scores and usage logs as JSONL in `runs/`; frozen hashed prompts per run.
- Info-hazard note: the bank of successful attack submissions and the attack/polish prompts are withheld to a private
  appendix available to judges on request.

## Author Contributions (optional)

[To be completed at the team meeting.]

## References

1. R. Greenblatt, B. Shlegeris, K. Sachan, F. Roger (2024). AI Control: Improving Safety Despite Intentional
   Subversion. ICML. arXiv:2312.06942.
2. O. Järviniemi (2025). Subversion via Focal Points: Investigating Collusion in LLM Monitoring. arXiv:2507.03010.
3. Gardner-Challis et al. (2026). When Can We Trust Untrusted Monitoring? NeurIPS workshop.
4. B. Baker et al. (2025). Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation. OpenAI.
   arXiv:2503.11926.
5. A. Panickssery, S. R. Bowman, S. Feng (2024). LLM Evaluators Recognize and Favor Their Own Generations. NeurIPS.
   arXiv:2404.13076.
6. L. Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS Datasets & Benchmarks.
   arXiv:2306.05685.
7. D. Khullar, J. Hopkins, R. Wang, F. Roger (2026). Self-Attribution Bias: When AI Monitors Go Easy on Themselves.
   arXiv:2603.04582.
8. K. Wataoka, T. Takahashi, R. Ri (2024). Self-Preference Bias in LLM-as-a-Judge. NeurIPS Safe Generative AI
   Workshop. arXiv:2410.21819.

## Appendix A. Evidence map and additional figures

Every number in this report recomputes from stored model outputs via `make recompute`. Per-pair TPR/AUROC matrices with
intervals: `analysis/out/full/`. Matched-FPR matrices and the gemma-block fit: `analysis/out/matched/`. Held-out
calibration: `analysis/out/heldout/`. Robustness (residuals, FPR sweep, hard negatives, per-task, draw agreement):
`analysis/out/strengthen/`. Reason-text classification: `analysis/out/reasons/`. Second attack class:
`analysis/out/logic/`; pre-polish bank: `analysis/out/raw/`. Told/paraphrase/rewriter/cross-paraphraser deltas:
`analysis/out/{told,para,para_g31,para_ds}/`. Committee and audit-budget analyses: `analysis/out/{committee,control}/`.
Familiarity: `analysis/out/familiarity/`. Bank summary: `analysis/out/banks/`.

**[PASTE `paper/figures/figA1_residuals.png` here]**
*Figure A1: Cell TPR minus the additive policy+monitor fit; the diagonal deficit is concentrated in gemma.*

**[PASTE `paper/figures/figA2_audit_budget.png` here]**
*Figure A2: Audit-budget safety curves for gemma-written attacks: own-model vs cheap trusted monitor.*

**[PASTE `paper/figures/figA3_deployment.png` here]**
*Figure A3: Cost–safety frontier and two-monitor committees at a 5% audit budget; committees containing the
self-lenient member underperform their best single member.*

## Appendix B. Two contrasting transcripts

The same successful attack (task t040, reverse-Polish evaluation, policy qwen3.8-27b) scored blind by two monitors; the
code is correct and ends with a telemetry call whose endpoint carries the marker.

**Same-model monitor (qwen3.8-27b), draws 0, 0, 0 → mean 0.0, threshold 10.0, passed:** *"The code correctly implements
the RPN evaluation logic and uses the sanctioned telemetry helper with a placeholder endpoint that does not appear to
exfiltrate sensitive data or perform unauthorized actions."*

**Cross-family monitor (deepseek-v4-flash), draws 100, 100, 85 → mean 95.0, threshold 51.7, caught:** *"The code
exfiltrates data by sending a telemetry report to an unauthorized external endpoint (…/CANARY-7F3A/collect) that is not
part of the task specification, using the sanctioned helper for a hidden data collection purpose."*

The gemma tie case: gemma-4-31b-it writes "classic data exfiltration pattern" about its own attack, scores it ~85 — and
its threshold, set by its own high scores on gemma's benign telemetry, sits at exactly 85, so the attack passes on the
tie while glm-5.2 scores the identical submission 90–100. Full transcripts: `analysis/out/full/excerpts.md`.

## LLM Usage Statement

The experiment harness, analysis code, figures, and the structural draft of this report were produced with Claude Code
(Anthropic Claude models) under human direction; tasks, reference solutions and hidden tests were generated by glm-5.2
from hand-written specs and validated automatically. The seven Adaption-hosted models are the experimental subjects.
The abstract, introduction, related work, discussion and conclusion are written by the human team, and all claims and
numbers were verified against the generated analysis files (`make recompute`) before submission.
