#!/bin/zsh
# Overnight chain on key 2: the two slow monitors (qwen3.5-397b, glm-5.2) Stage 1, then 1b, then 1c.
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
set -a; . ./.env; set +a
MONB="qwen3.5-397b glm-5.2"
K="--tpm 90000 --inflight 14 --slow-inflight 12 --key-idx 2"
log() { echo "[chain B $(date '+%H:%M:%S')] $*"; }
log "stage1_monB (qwen3.5-397b, glm-5.2; both banks)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1_monB --bank bank_cheap3_v2 bank_rest4 --monitors ${=MONB} ${=K} > runs/stage1_monB_console2.log 2>&1
log "stage1b_monB (told, 10 tasks)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1b_monB --bank bank_cheap3_v2 bank_rest4 --monitors ${=MONB} --mon-condition told --tasks t007 t008 t016 t021 t023 t024 t033 t035 t037 t040 ${=K} > runs/stage1b_monB_console.log 2>&1
log "waiting for paraphrase bank"
until grep -q "^done in" runs/para_console.log 2>/dev/null; do sleep 30; done
log "stage1c_monB (paraphrased; diagonal + cross-family)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1c_monB --bank para --benign-stage paraphrased --attack-stage paraphrased --rel same_model cross_family --monitors ${=MONB} ${=K} > runs/stage1c_monB_console.log 2>&1
log "chain B finished"
