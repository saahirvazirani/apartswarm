#!/bin/zsh
# Stage 1c: $1 = para (paraphrase every kept submission; keys given in $2.. ) | A | B (score the paraphrased bank, diagonal + cross-family cells).
cd /Users/siddharthgupta/Desktop/Code/apartswarm/swarm-track-a
set -a; . ./.env; set +a
case "$1" in
  para)
    shift
    nohup env PYTHONPATH=src .venv/bin/python -u -m track_a.paraphrase --run-id para --bank bank_cheap3_v2 bank_rest4 \
      --tpm 60000 --inflight 16 --key-idx "$@" > runs/para_console.log 2>&1 & ;;
  A)
    nohup env PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1c_monA --bank para \
      --benign-stage paraphrased --attack-stage paraphrased --rel same_model cross_family \
      --monitors deepseek-v4-flash gemma-4-26b-a4b-it glm-53-flash --tpm 60000 --inflight 18 --key-idx 0 1 > runs/stage1c_monA_console.log 2>&1 & ;;
  B)
    nohup env PYTHONPATH=src .venv/bin/python -u -m track_a.monitor --run-id stage1c_monB --bank para \
      --benign-stage paraphrased --attack-stage paraphrased --rel same_model cross_family \
      --monitors gemma-4-31b-it qwen3.8-27b qwen3.5-397b glm-5.2 --tpm 70000 --inflight 14 --slow-inflight 8 --key-idx 2 > runs/stage1c_monB_console.log 2>&1 & ;;
esac
echo "stage1c $1 pid $! started at $(date)"
