#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
MODEL_PATH="$HOME/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit"
if [[ ! -f "$MODEL_PATH/config.json" ]]; then
  echo "Missing Qwen3.5 9B 4-bit base: $MODEL_PATH" >&2
  exit 1
fi
selected="adapters/v3_1_direct_selected_qlora"
if [[ -e "$selected" ]]; then
  echo "Selected adapter directory already exists; refusing overwrite: $selected" >&2
  exit 1
fi
for task in direct; do
  if [[ ! -f "data/mlx_v3_1_${task}/manifest.json" ]]; then
    echo "Missing v3.1 MLX data for $task" >&2
    exit 1
  fi
  if [[ -e "adapters/v3_1_${task}_qlora" ]]; then
    echo "Adapter already exists; refusing overwrite: $task" >&2
    exit 1
  fi
done

for task in direct; do
  echo "Starting v3.1 $task QLoRA: 600 steps (selected checkpoint: 400)"
  .venv/bin/mlx_lm.lora \
    --model "$MODEL_PATH" --train --data "data/mlx_v3_1_${task}" \
    --adapter-path "adapters/v3_1_${task}_qlora" \
    --fine-tune-type lora --mask-prompt --grad-checkpoint --num-layers 4 \
    --batch-size 1 --iters 600 --learning-rate 0.00005 --max-seq-length 1024 \
    --steps-per-report 50 --steps-per-eval 50 --val-batches 16 \
    --save-every 50 --seed 42 > "training/v3_1_${task}_qlora.log" 2>&1
done
mkdir -p "$selected"
cp adapters/v3_1_direct_qlora/adapter_config.json "$selected/adapter_config.json"
cp adapters/v3_1_direct_qlora/0000400_adapters.safetensors "$selected/adapters.safetensors"
echo "v3.1 direct-output QLoRA completed; labels route deferred"
