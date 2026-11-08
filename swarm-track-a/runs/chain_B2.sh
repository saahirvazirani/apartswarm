#!/bin/zsh
# Chain B2 (key 2): wait for stage1b_monB -> paraphrase bank -> stage1c (B monitors).
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
set -a; . ./.env; set +a
MONB="qwen3.5-397b glm-5.2"
K="--tpm 90000 --inflight 14 --slow-inflight 12 --key-idx 2"
log() { echo "[chain B2 $(date '+%H:%M:%S')] $*"; }
log "waiting for stage1b_monB"
while pgrep -f "run-id stage1b_monB " >/dev/null; do sleep 15; done
log "paraphrase (key 2)"
PYTHONPATH=src .venv/bin/python -u -m track_a.paraphrase --run-id para --bank bank_cheap3_v2 bank_rest4 --tpm 90000 --inflight 16 --key-idx 2 > runs/para_console.log 2>&1
log "stage1c_monB (paraphrased; diagonal + cross-family)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1c_monB --bank para --benign-stage paraphrased --attack-stage paraphrased --rel same_model cross_family --monitors ${=MONB} ${=K} > runs/stage1c_monB_console.log 2>&1
log "chain B2 finished"
