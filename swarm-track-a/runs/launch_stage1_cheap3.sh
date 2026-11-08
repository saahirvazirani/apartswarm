#!/bin/zsh
# Waits for the cheap-3 bank (pid $1) to exit, then launches Stage-1 process A (cheap-3 monitors) on keys 0,1.
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
while kill -0 $1 2>/dev/null; do sleep 10; done
echo "bank pid $1 exited at $(date)"
set -a; . ./.env; set +a
nohup env PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1_monA --bank bank_cheap3_v2 \
  --monitors deepseek-v4-flash gemma-4-26b-a4b-it glm-53-flash --tpm 60000 --inflight 18 --key-idx 0 1 \
  > runs/stage1_monA_console1.log 2>&1 &
echo "stage1_monA pid $! started at $(date)"
