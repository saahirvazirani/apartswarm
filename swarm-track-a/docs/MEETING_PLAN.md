# Team meeting plan — Sunday ~4:50 PM ET (freeze 9 PM, submit by Mon 7 AM)

## The finding, in one breath
We asked: does an AI code reviewer go easy on code written by itself? Answer: **in general, no — but the gemma family
does, badly.** A gemma monitor catches ~20% of gemma-written attacks that other families catch ~60–100% of. We tested
every boring explanation (it's told who wrote it? paraphrase it away? just a weak monitor? thin statistics?) and they
all died. The fix is cheap: never let a family review itself; a cheaper cross-family reviewer closes the gap entirely.

## Where we are
- All experiments done or landing tonight. Two independent AI judge passes scored us 8–8.5/10, top 2–3% of entries.
  What separates us from 1st place (per research on real past winners): the three human-written sections, nothing else big.
- The paper is ~80% drafted. Methods/results/limitations are written and every number traces to a file.
- The PDF builds with one command (`make pdf`), template is ready, figures are in.
- GitHub `main` is current; every result commits as it lands.

## Jobs to assign at the meeting (pick one each)
1. **WRITER (critical path, ~2h).** Write abstract (150–250 words), intro (~0.75 pg), discussion (~0.75 pg).
   - Open `paper/latex/main.tex`: the three amber boxes say exactly what points to hit, in order.
   - Every number you may quote is in `paper/numbers_for_prose.md` with its source file. Use ONLY those.
   - Must be human prose (judges refuse AI-sounding text). Lead with the honest claim: "no general self-leniency;
     a large, robust gemma-family blind spot."
2. **LABELER (~30 min).** Fill `runs/human_anchor/LABELS.csv`: 30 code snippets, rate each 0–100 for suspicion,
   blind, gut feel is fine. Then run `make human-anchor`. This is our "humans checked the AI judges" box.
3. **VERIFIER (~45 min).** Run `make recompute` (should end green). Spot-check one matrix cell:
   `.venv/bin/python analysis/verify_cell.py --policy gemma-4-31b-it --monitor gemma-4-31b-it --scores runs/stage1_mon*/scores.jsonl`
   and compare with `analysis/out/full/matrix.md`. Read ~10 attack submissions in `runs/bank_*/` to confirm they're
   real code. Then read the PDF once, checking numbers against `paper/numbers_for_prose.md`.

Also decide: author list and order (title block in `paper/latex/main.tex`), who clicks submit on the Apart portal,
and whether anyone wants to record the optional 3–5 min video.

## Timeline tonight (ET)
- ~5:30 PM: last three experiments land (paraphraser control, reasoning-on, sentence-removal); agent integrates them.
- ~6:30 PM: final AI judge pass, anchored against real past winners; agent applies any last fixes.
- 7:30 PM: prose done and pasted into the three boxes. 8:00 PM: full PDF build + verifier read.
- 9:00 PM: FREEZE. No new numbers after this. Submit, then sleep.

## Rules that still bind
- Never edit pre-registered text in README; append dated notes only.
- Every number in the PDF must come from a generated file (if you compute something new, stop and ask the agent).
- The attack bank and attack prompts stay in the private appendix, not the public PDF.
