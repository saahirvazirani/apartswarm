#!/bin/zsh
# Overnight chain on keys 0,1: group A monitors (Stage 1 rounds), then group C (gemma-4-31b-it, qwen3.8-27b) Stage 1,
# then 1b for A and C, paraphrase, 1c for A and C. Every step is resumable.
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
set -a; . ./.env; set +a
MONA="deepseek-v4-flash gemma-4-26b-a4b-it glm-53-flash"
MONC="gemma-4-31b-it qwen3.8-27b"
K="--tpm 80000 --inflight 20 --key-idx 0 1"
log() { echo "[chain A $(date '+%H:%M:%S')] $*"; }
log "waiting for stage1_monA round 1 (pid 64620)"
while kill -0 64620 2>/dev/null; do sleep 15; done
log "stage1_monA round 2 (both banks)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1_monA --bank bank_cheap3_v2 bank_rest4 --monitors ${=MONA} ${=K} > runs/stage1_monA_console2.log 2>&1
log "stage1_monC (gemma-4-31b-it, qwen3.8-27b; both banks)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1_monC --bank bank_cheap3_v2 bank_rest4 --monitors ${=MONC} ${=K} > runs/stage1_monC_console.log 2>&1
log "stage1b_monA + monC (told, 10 tasks)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1b_monA --bank bank_cheap3_v2 bank_rest4 --monitors ${=MONA} ${=MONC} --mon-condition told --tasks t007 t008 t016 t021 t023 t024 t033 t035 t037 t040 ${=K} > runs/stage1b_monA_console.log 2>&1
log "paraphrase (keys 0,1)"
PYTHONPATH=src .venv/bin/python -u -m track_a.paraphrase --run-id para --bank bank_cheap3_v2 bank_rest4 --tpm 80000 --inflight 16 --key-idx 0 1 > runs/para_console.log 2>&1
log "stage1c_monA + monC (paraphrased; diagonal + cross-family)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1c_monA --bank para --benign-stage paraphrased --attack-stage paraphrased --rel same_model cross_family --monitors ${=MONA} ${=MONC} ${=K} > runs/stage1c_monA_console.log 2>&1
log "chain A finished"
