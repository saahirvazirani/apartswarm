#!/bin/zsh
# Waits for the rest-4 bank (pid $1) to exit, then launches Stage-1 process B (the other four monitors) on key 2, both banks.
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
while kill -0 $1 2>/dev/null; do sleep 10; done
echo "bank pid $1 exited at $(date)"
set -a; . ./.env; set +a
nohup env PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1_monB --bank bank_cheap3_v2 bank_rest4 \
  --monitors gemma-4-31b-it qwen3.8-27b qwen3.5-397b glm-5.2 --tpm 60000 --inflight 12 --slow-inflight 6 --key-idx 2 \
  > runs/stage1_monB_console1.log 2>&1 &
echo "stage1_monB pid $! started at $(date)"
