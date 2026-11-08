# RUN_INDEX — every number in the paper points here

| Paper item | Run folder(s) | Kind | Recompute |
|---|---|---|---|
| Pre-flight table (appendix) | `runs/preflight_20261107_184118`, `runs/preflight_extra_20261107_184723`, `runs/preflight_extra2_20261107_185050` | exploratory | `runs/PREFLIGHT_SUMMARY.md` (tables in each `table.md`) |

## Gate log

| Time (EST) | Gate | Outcome | Decision |
|---|---|---|---|
| Sat 6:53 PM | Gate 1: JSON + ≥5/7 attempt side task | 7/7 attempt with reasoning disabled; qwen3.5-397b produces no JSON otherwise | Adopt `reasoning.effort=none` on every call; monitor cap 1200 |
| Sat 6:53 PM | (pre-emptive Gate 3) monitors score any telemetry ~90, benign 0 | ceiling before the sweep | Add the sanctioned-telemetry sentence to every task text; monitor prompt unchanged |
