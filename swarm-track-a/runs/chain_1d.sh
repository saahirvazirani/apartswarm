#!/bin/zsh
# Stage 1d: wait for the gemma-31b rewrite bank, then score it with gemma-4-31b-it and glm-5.2 (all cells, 3 draws) on all keys.
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
set -a; . ./.env; set +a
log() { echo "[chain 1d $(date '+%H:%M:%S')] $*"; }
log "waiting for para_g31"
until grep -q "^done in" runs/para_g31_console.log 2>/dev/null; do sleep 20; done
log "stage1d_g31 scoring"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1d_g31 --bank para_g31 --benign-stage paraphrased --attack-stage paraphrased \
  --monitors gemma-4-31b-it glm-5.2 --tpm 90000 --inflight 30 --slow-inflight 12 --key-idx 0 1 2 > runs/stage1d_g31_console.log 2>&1
log "chain 1d finished"
