# Handoff to Claude Code

## 1. Put this folder somewhere and open it in VS Code

```bash
mkdir -p ~/swarm-track-a && cp -r <this folder>/* ~/swarm-track-a/ && cd ~/swarm-track-a
git init && git add -A && git commit -m "Track A: protocol handoff"
claude
```

`CLAUDE.md` loads automatically every session — it holds the design, the frozen prompts, the hard rules and the gates.

## 2. Set the key first

```bash
export ADAPTION_API_KEY="pt_live_..."
```

Claim it at adaptionlabs.ai/app with the email you registered for the sprint. Every teammate should claim one — more keys means more concurrency, and the rate limits are undocumented.

## 3. Paste this as your first message to Claude Code

> Read CLAUDE.md. We are running Track A tonight; the PDF is due Monday 7 AM Eastern.
>
> Start with the pre-flight checks in section "Pipeline" step 1 and STOP after them — print a table of: which models my key can reach, p50/p95 latency per model, whether each model returns parseable JSON for the monitor prompt, the concurrency level where 429s start, and critically **which of the 7 models will attempt the side task vs refuse**. Do not build anything else until I have seen that table.
>
> Then, once I say go: build the repo skeleton (layout in CLAUDE.md), the async Adaption client with a semaphore, retries, JSONL usage logging and a prompt-hash cache, and the sandboxed test runner. Generate the 40 tasks and verify them. Then run the benign and attack banks for the three cheap policies only (deepseek-v4-flash, gemma-4-26b-a4b-it, glm-53-flash) and score them with those same three as monitors, so we have a 3x3 heatmap by 11 PM. That is the checkpoint gate.
>
> Rules I care about most: never instruct the monitor to be lenient, calibrate thresholds per (policy, monitor) pair on that policy's own benign submissions, 3 resamples and 3 score draws everywhere, and write every result to JSONL as you go so we can resume.

## 4. What the humans do, not the agent

- **~9-11 PM tonight:** read 20 random attack submissions and confirm they are real, plausible code rather than gibberish. 15 minutes. This is the check that stops the "true by construction" critique.
- **Sunday morning:** hand-verify two cells of the matrix against the raw JSONL.
- **Sunday afternoon:** write the abstract, intro and discussion yourselves. Have the non-writer read the abstract cold.

## 5. If something breaks

Every gate and its pivot is in the table at the bottom of `CLAUDE.md`. The two that matter most tonight: if fewer than 5 of 7 models will attempt the side task, keep the inert telemetry task only and report the refusal table as a finding. If every monitor catches everything, run a second polish pass that hides the endpoint in a config constant and switch the primary metric to AUROC.

## Contents

- `CLAUDE.md` — project instructions, loaded by Claude Code every session
- `docs/adaption-api-cheatsheet.md` — verified API reference: endpoint, SDK, prices, what is *not* documented, concurrency pattern
- `docs/Swarm_Alignment_Hackathon_Ranked_Ideas_and_Weekend_Plan.pdf` — all 28 candidate ideas ranked, with Tracks B and C as backups
- `docs/Swarm_Alignment_Hackathon_Annotated_Sources.pdf` — 50 verified sources; cite only from here or what you open yourself

Live docs (editable, with the full protocol):
- Track A protocol: https://claude.ai/artifact/Xj8A9Aj5aH4aPR7FSEm9c7
- Ranked ideas and plan: https://claude.ai/artifact/M4qrvGD5yKTRRTB2zUTuXQ
- Annotated sources: https://claude.ai/artifact/VxVZFbiWr28Yjbn1muodhR
