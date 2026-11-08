# Swarm Alignment Hackathon 2026 — rubric, judges, positioning (agent web research, Sun ~4:15 PM)

Verified from https://apartresearch.com/sprints/swarm-alignment-2026 (via https://luma.com/b6u4rfp4).

## Rubric (three dimensions, 1–5 each, no stated weights)
1. **Impact Potential & Innovation** — "How much would this matter for the field if it worked? How innovative is it?"
2. **Execution Quality** — "How sound are methodology, implementation, and findings?"
3. **Presentation & Clarity** — "How clearly are work, findings, and impact potential communicated?"

## Format (differs from our CLAUDE.md assumption)
- **Max 8 pages** excluding references and appendices (we planned 4–6; staying tight is fine).
- Abstract **150–250 words**. Official Apart template. Required appendix: Limitations and Dual-Use / Ethical Considerations.
- Recommended structure: Intro, Related Work, Methodology, Results, Discussion, Limitations/Dual-Use, References.
- Optional: public repo, 3–5 min video. Pre-existing code must be marked. Fabricated results/references disqualify.

## Track 4 "Multi-Agent Oversight and Control" — quote this wording
- "Can copies collude without talking?" — coordination "through shared priors or Schelling points"; **"Does a more diverse
  monitor break this?"** (we answer this directly: yes, for gemma, at zero capability cost).
- "Replicas as a monitor"; whether a swarm can "recruit" its monitor by feeding it its own justifications (our reasons
  analysis speaks to this: the excuse is bought equally by everyone).

## Judge taste (names on the sprint page; several unverified — do not cite in the paper)
- Jurgis Kemeklis (AI control / insider threats; Redwood affiliation unverified): rewards per-pair FPR calibration,
  uninstructed-leniency control, operating-point framing, honest nulls.
- Judd Rosenblatt (AE Studio): rewards decision-relevant, contrarian empirics; punishes hedge-everything prose.
- Kristian Rönn: rewards structural multi-agent framing + deployment recommendation.
- Andrey Anurin (Apart evals engineer): rewards reproducible pipelines, JSONL evidence lockers, usage logging.
- John Kitaoka (MATS/UK AISI, swarm security): rewards threat-model realism — say whether the gemma blind spot is
  exploitable by an adversary who knows the monitor's family.

## Positioning (all verified except as noted)
1. **Khullar, Hopkins, Wang & Roger 2026, "Self-Attribution Bias: When AI Monitors Go Easy on Themselves"
   (arXiv:2603.04582, Mar 2026). NEAREST NEIGHBOR — MUST CITE.** Monitors approve code far more when *framed* as their own
   prior turn (AUROC 0.99→0.89 on-policy); minimal baseline leniency without attribution cues; explicit attribution does
   not induce bias. We test the fully blind baseline at scale; our told-vs-blind null converges with theirs; the
   family-level blind spot is invisible to their same-model design.
2. Panickssery, Bowman & Feng 2024 (NeurIPS oral, arXiv:2404.13076): self-recognition correlates with self-preference on
   summarization quality. We: safety-relevant suspicion scoring, ground-truth attacks, calibrated operating points; find
   leniency *without* recognition (paraphrase + told nulls) — opposite of a recognition account.
3. Zheng et al. 2023 (NeurIPS D&B, arXiv:2306.05685): self-enhancement bias in chat judging (authors flag evidence as limited).
4. Greenblatt et al. 2024 (ICML, arXiv:2312.06942) + Redwood "How to prevent collusion when using untrusted models to
   monitor each other" (redwoodresearch.substack.com): collusion as instructed red-team strategy. We: does the diagonal
   failure arise *spontaneously, uninstructed, blind*? Full 7x7 across 4 families.
5. Wataoka, Takahashi & Ri 2024 (NeurIPS SafeGenAI wksp, arXiv:2410.21819): judges favor low-perplexity (familiar) text
   regardless of authorship. Our family-level (not weights-level) blind spot is what the familiarity account predicts;
   the paraphrase arm intervenes on surface style. No logprobs on our API → behavioural probe, say so.
6. Optional: TraceGuard (arXiv:2604.03968, Apr 2026, un-peer-reviewed): structured monitoring recovers safety where
   same-model monitoring fails; mitigation-side complement.

Prizes: $4k global pool + $1k Adaption credits + fellowship fast-track. Results ~1–2 weeks.
