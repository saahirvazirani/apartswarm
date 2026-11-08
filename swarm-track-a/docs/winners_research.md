# What winning Apart submissions look like (agent web research, Sun ~4:20 PM)

From sprint pages w/ confirmed placements: AI Control 2025/2026, Secret Loyalties 2026, AI Incident Response 2026.
Closest-topic sprint (AI Collusion, Oct 2026, 392 subs) has not announced winners yet.

## Depth markers that recur across winners
- Pre-registration **with failures reported in the paper** (3rd SL: 52 predictions, 10 failed — praised by name).
- Real statistics per claim + **a power statement on every null** ("underpowered to ~1.5 points"; "an observed sub-1% FPR
  doesn't bound the true rate at these n").
- True-null / placebo controls the pipeline passes (decoy organism unflagged; magnitude-matched controls).
- **Mechanism, not just measurement** (1st SL traced effect to LoRA memorization; Omission Attacks explained why monitors
  miss absences, then built the fix).
- **Attack → defense arc**: every 1st place ends with a tested or operationalized deployment recommendation.
- Blind/third-party validation of own pipeline; human validation of LLM judges reported **even when bad** (0.41).
- Candid bad news in the main body (withdrawn statistics, retracted mechanisms) — always cited as a strength.
- Small-n fine, sloppy-n not ("scope, not rigor, is the ceiling"; 5 traces won 1st of 126).
- Checkable repo + one-command recompute (`verify.py` praised by name).
- **Title states the finding as a sentence** ("When Doing Nothing Is the Attack"; "...Erases Who It Served, and Usually
  Not the Loyalty").

## Calibration anchors (for the blind judge)
1. **"A Broad Secret Loyalty Evades an Adversarial Audit" (2nd, SL 2026)** — solo, one weekend: 6 eval conditions,
   content-matched control, eval-awareness check, replication, second prompt set, p-values + pooled CIs incl. the null
   with power statement, blind sweep over other teams' organisms + decoy, honest 0.41 judge-reliability number.
   "Strongest submission reviewed; recommend publication."
2. **"Omission Attacks" (1st of 126, AI Control 2026)** — tiny n (5 traces) but new framing + taxonomy + damning
   contrast (≤4/10 vs 92.3/100) + tested defense (postcondition monitoring catches 5/5). Won despite no variance
   estimates. Framing + arc beats scale.
3. **"Removing a secret loyalty blind erases who it served..." (3rd, SL 2026)** — the rigor ceiling: 21 organisms,
   matched controls, Fisher exact, 52 pre-registered predictions w/ 10 failures, 2 statistics withdrawn in-text,
   verify.py. Placed BELOW the two entries with stronger framing: rigor alone caps at 3rd.

## Deltas that separate 1st from 3rd (apply to Track A)
(a) title/abstract state the finding as one falsifiable sentence; (b) a mechanism paragraph (our reasons analysis);
(c) the deployment recommendation made quantitative (TPR bought at matched FPR, audit-budget delta); (d) failures and
sensitivity results voiced plainly in the body (tie-break, matched-FPR shrinkage, Stage 1d null, 1e amendment).

Also: AI Control 2025 explicit weights were Innovation & Literature 30% / Safety Impact 40% / Technical & Docs 30% —
literature framing is scored, not decoration. Peer "declined to score 14% for AI prose" not found publicly; reviewer
comments consistently praise "clear, cautious, human" prose instead.
