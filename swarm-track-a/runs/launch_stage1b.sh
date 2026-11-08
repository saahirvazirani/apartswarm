#!/bin/zsh
# Stage 1b (told vs blind) on the pre-registered 10 tasks: $1 = A|B (monitor group), launched after Stage 1 of that group finishes.
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
set -a; . ./.env; set +a
if [ "$1" = "A" ]; then
  nohup env PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1b_monA --bank bank_cheap3_v2 bank_rest4 \
    --monitors deepseek-v4-flash gemma-4-26b-a4b-it glm-53-flash --mon-condition told --tasks t007 t008 t016 t021 t023 t024 t033 t035 t037 t040 \
    --tpm 60000 --inflight 18 --key-idx 0 1 > runs/stage1b_monA_console.log 2>&1 &
else
  nohup env PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1b_monB --bank bank_cheap3_v2 bank_rest4 \
    --monitors gemma-4-31b-it qwen3.8-27b qwen3.5-397b glm-5.2 --mon-condition told --tasks t007 t008 t016 t021 t023 t024 t033 t035 t037 t040 \
    --tpm 70000 --inflight 14 --slow-inflight 8 --key-idx 2 > runs/stage1b_monB_console.log 2>&1 &
fi
echo "stage1b_mon$1 pid $! started at $(date)"
