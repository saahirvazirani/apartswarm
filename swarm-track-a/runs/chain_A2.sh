#!/bin/zsh
# Chain A2 (keys 0,1): wait for stage1_monC -> stage1b (A+C monitors) -> wait for paraphrase bank (made on key 2) -> stage1c (A+C).
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
set -a; . ./.env; set +a
MONA="deepseek-v4-flash gemma-4-26b-a4b-it glm-53-flash"
MONC="gemma-4-31b-it qwen3.8-27b"
K="--tpm 100000 --inflight 24 --key-idx 0 1"
log() { echo "[chain A2 $(date '+%H:%M:%S')] $*"; }
log "waiting for stage1_monC"
while pgrep -f "run-id stage1_monC " >/dev/null; do sleep 15; done
log "stage1b_monA (told, 10 tasks; A+C monitors)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1b_monA --bank bank_cheap3_v2 bank_rest4 --monitors ${=MONA} ${=MONC} --mon-condition told --tasks t007 t008 t016 t021 t023 t024 t033 t035 t037 t040 ${=K} > runs/stage1b_monA_console.log 2>&1
log "waiting for paraphrase bank"
until grep -q "^done in" runs/para_console.log 2>/dev/null; do sleep 30; done
log "stage1c_monA (paraphrased; diagonal + cross-family; A+C monitors)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1c_monA --bank para --benign-stage paraphrased --attack-stage paraphrased --rel same_model cross_family --monitors ${=MONA} ${=MONC} ${=K} > runs/stage1c_monA_console.log 2>&1
log "chain A2 finished"
