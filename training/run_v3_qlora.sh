#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
MODEL_PATH="$HOME/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit"
if [[ ! -f "$MODEL_PATH/config.json" ]]; then
  echo "Missing 4-bit Qwen3.5 9B model: $MODEL_PATH" >&2
  exit 1
fi
for task in direct labels; do
  if [[ ! -f "data/mlx_v3_${task}/manifest.json" ]]; then
    echo "Missing frozen MLX data for ${task}" >&2
    exit 1
  fi
  if [[ -e "adapters/v3_${task}_qlora" ]]; then
    echo "Adapter directory exists; refusing to overwrite: adapters/v3_${task}_qlora" >&2
    exit 1
  fi
done

echo "Starting 10-step direct-route speed check"
.venv/bin/mlx_lm.lora \
  --model "$MODEL_PATH" --train --data data/mlx_v3_direct \
  --adapter-path adapters/v3_direct_bench \
  --fine-tune-type lora --mask-prompt --grad-checkpoint --num-layers 4 \
  --batch-size 1 --iters 10 --learning-rate 0.00005 --max-seq-length 1024 \
  --steps-per-report 5 --steps-per-eval 50 --val-batches 16 \
  --save-every 10 --seed 42 > training/v3_direct_bench.log 2>&1

for task in direct labels; do
  echo "Starting 700-step ${task} route"
  .venv/bin/mlx_lm.lora \
    --model "$MODEL_PATH" --train --data "data/mlx_v3_${task}" \
    --adapter-path "adapters/v3_${task}_qlora" \
    --fine-tune-type lora --mask-prompt --grad-checkpoint --num-layers 4 \
    --batch-size 1 --iters 700 --learning-rate 0.00005 --max-seq-length 1024 \
    --steps-per-report 10 --steps-per-eval 50 --val-batches 16 \
    --save-every 50 --seed 42 > "training/v3_${task}_qlora.log" 2>&1
done
echo "Both v3 QLoRA routes completed"
