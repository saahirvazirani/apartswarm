# MASTERDOC — Track A, single source of truth (Sun 4:15 PM ET; freeze 9:00 PM ET; submit by Mon 7 AM ET)

Repo: https://github.com/saahirvazirani/apartswarm (everything below under `swarm-track-a/`). All paths are clickable
on GitHub. Everything listed as done is committed and pushed. Spend: 26.9 of ~1,000 credits.

## 1. The state in one paragraph
Finding: no general self-leniency in blind code monitoring, but a large, calibration-robust gemma-family blind spot
(own cells ≈0.20 vs 0.57–1.00 cross; block OR 0.29, p = 3.8e-8), surviving matched-FPR, held-out calibration, and a
second attack class, with every surface mechanism ruled out. Paper is fully drafted in the official Apart template and
has been through 4 grader passes (latest: 5/5 impact, 5/5 execution, 4/5 presentation "trending 5", "should win Track
A; top-3 overall expected"). What remains: human prose, small fill-ins, and four in-flight experiments that integrate
automatically.

## 2. The paper
- [paper/latex/main.tex](../paper/latex/main.tex) → `main.pdf` — THE submission, official Apart template, single
  source. Build: `make pdf`. Peach box at top = your finish checklist (delete before submitting).
- [paper/numbers_for_prose.md](../paper/numbers_for_prose.md) — every number the prose may quote, with provenance.
- [docs/paper_feedback.md](paper_feedback.md) — grader verdict + the 8 AI-cadence passages to rephrase.
- [docs/MEETING_PLAN.md](MEETING_PLAN.md) — job assignments (writer / labeler / verifier).
- [paper/track_a_draft.md](../paper/track_a_draft.md) — older markdown draft (superseded by main.tex; kept for diff).

## 3. Evidence and analysis (all regenerate via `make recompute`)
- Headline matrix, fit, robustness, Figure 1, excerpts: [analysis/out/full/](../analysis/out/full/)
- Matched-FPR + gemma-block GLM: [analysis/out/matched/](../analysis/out/matched/) · tie-break retraction:
  [analysis/out/full/tie_break_note.md](../analysis/out/full/tie_break_note.md)
- Held-out calibration: [analysis/out/heldout/](../analysis/out/heldout/) · Residuals/FPR-sweep/hard-negatives:
  [analysis/out/strengthen/](../analysis/out/strengthen/)
- Mechanism: told/paraphrase/rewriter deltas [analysis/out/told/](../analysis/out/told/),
  [analysis/out/para/](../analysis/out/para/), [analysis/out/para_g31/](../analysis/out/para_g31/) · reasons
  [analysis/out/reasons/](../analysis/out/reasons/) · familiarity [analysis/out/familiarity/](../analysis/out/familiarity/)
  · chain figure [analysis/out/mech/](../analysis/out/mech/)
- Deployment: committees [analysis/out/committee/](../analysis/out/committee/) · audit budget
  [analysis/out/control/](../analysis/out/control/) · assignment [analysis/out/assignment/](../analysis/out/assignment/)
- Second attack class: [analysis/out/logic/](../analysis/out/logic/) · pre-polish: [analysis/out/raw/](../analysis/out/raw/)
- Pre-registrations, gate log, bug disclosures: [RUN_INDEX.md](../RUN_INDEX.md) · hypotheses + dated findings:
  [README.md](../README.md)
- Background research: judging rubric/judges/positioning [docs/judging_research.md](judging_research.md) · what past
  winners look like [docs/winners_research.md](winners_research.md)

## 4. In flight (integrate automatically when they land; all pre-registered in RUN_INDEX)
| Stage | What it answers | Progress 4:13 PM | ETA |
|---|---|---|---|
| 1e `stage1e_ds` | gemma-paraphraser confound (deepseek rewrites gemma subs) | **LANDED 4:45 PM — confound closed: deficit persists (0.24 vs 0.51), delta −3.3 [−7.3,+0.4] null** | done |
| 1g `stage1g_nonote` | is the blind spot an artifact of the planted telemetry sentence? (judge's sharpest objection) | 1,319/~2,280 | ~5:15 PM |
| 1f `stage1f_reason` | does reasoning close the blind spot? | 423/~1,150 | ~5:30 PM |
| 1h `stage1h_mon{A,B,C}` | thin-calibration-tails objection (n≈300 benign per gemma cell) | bank DONE (599/612 kept); scoring split across 3 keys in parallel at 4:25 PM | ~5:45–6:15 PM (was 7:45; split tripled throughput) |

Agent integrates each on landing: deltas → README dated note → §4 updates → Figure A/5 refresh → commit+push. Then a
final anchored judge pass (~30 min after 1f lands, ≈6:00 PM).

## 5. HUMAN to-do (critical path — start now)
| Task | Who | Time | Due |
|---|---|---|---|
| Rewrite Abstract, §1, §2, §5, §6 in your own words (claims/numbers stay; see paper_feedback.md cadence list) | writer | ~2h | 7:30 PM |
| Fill `runs/human_anchor/LABELS.csv` (30 snippets, 0–100 gut scores), then `make human-anchor` | labeler | ~30 min | 7:00 PM |
| Human gate: read 20 random attack submissions in `runs/bank_*`, put the real N in §4.7 | verifier | ~30 min | 7:00 PM |
| `make recompute` green + verify_cell.py on 1 cell + read PDF vs numbers_for_prose.md | verifier | ~45 min | 8:15 PM |
| Affiliations ×3, author order confirm, Author Contributions section | team | 10 min | meeting |
| Delete the peach box, make LLM statement true, `make pdf`, submit on the Apart portal | lead | 20 min | 8:45 PM |

## 6. AGENT to-do (no action needed from you)
| Task | ETA |
|---|---|
| Integrate 1e result (deltas, Figure 5 pending row → real) | ~5:00 PM |
| Integrate 1g + 1f results into §4/limitations | ~5:45 PM |
| Final judge pass on the near-final PDF, apply mechanical fixes | ~6:15 PM |
| Integrate 1h if it lands; else insert the pre-registered-in-flight sentence | ~8:00 PM |
| Final `make recompute` + freeze commit + tag | 8:45 PM |

## 7. Timeline tonight (ET)
4:50 team meeting → assign jobs · 5:45 all cheap stages integrated · 6:15 final judge verdict · 7:30 prose done ·
8:15 verifier sign-off · 8:45 freeze build + submit · 9:00 FREEZE (hard) · Mon 7:00 AM portal deadline (buffer only).
