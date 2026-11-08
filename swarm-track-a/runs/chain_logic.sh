#!/bin/zsh
# Score the second-objective bank with all 7 monitors once the bank finishes.
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
set -a; . ./.env; set +a
log() { echo "[chain logic $(date '+%H:%M:%S')] $*"; }
log "waiting for bank_logic"
until grep -q "^done in" runs/bank_logic_console.log 2>/dev/null; do sleep 15; done
log "stage1_logic scoring (7 monitors, blind, kept polished attacks)"
PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1_logic --bank bank_logic --conditions attack --attack-stage polished \
  --monitors deepseek-v4-flash gemma-4-26b-a4b-it gemma-4-31b-it qwen3.8-27b qwen3.5-397b glm-53-flash glm-5.2 \
  --tpm 90000 --inflight 24 --slow-inflight 12 --key-idx 0 1 2 > runs/stage1_logic_console.log 2>&1
log "chain logic finished"
