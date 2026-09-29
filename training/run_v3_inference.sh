#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
MODEL_PATH="$HOME/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit"
TEST_PATH="data/splits/v3_seed42/test.jsonl"
for task in labels direct; do
  for version in base v2 v3; do
    output="evaluation/v3_${version}_${task}_predictions.jsonl"
    raw="evaluation/v3_${version}_${task}_raw.jsonl"
    log="training/v3_${version}_${task}_inference.log"
    if [[ -e "$output" || -e "$raw" ]]; then
      echo "Inference output exists; refusing to overwrite $output or $raw" >&2
      exit 1
    fi
    echo "Starting v3 test inference: $version $task"
    run_args=("$TEST_PATH" "$output" --raw "$raw" --model "$MODEL_PATH" --task "$task")
    if [[ "$version" == "v2" ]]; then
      run_args+=(--adapter "adapters/v2_1_${task}_qlora")
    elif [[ "$version" == "v3" ]]; then
      run_args+=(--adapter "adapters/v3_${task}_qlora")
    fi
    if ! .venv/bin/python scripts/infer_mlx_v3.py "${run_args[@]}" > "$log" 2>&1; then
      if [[ ! -f "$raw" || "$(wc -l < "$raw")" -ne 200 ]]; then
        echo "Incomplete inference audit for $version $task; see $log" >&2
        exit 1
      fi
      echo "Some outputs were unparseable for $version $task; continuing with full raw audit"
    fi
  done
done

.venv/bin/python scripts/compare_training_v3.py "$TEST_PATH" \
  data/splits/v3_seed42/manifest.json \
  evaluation/training_comparison_v3.json evaluation/training_comparison_v3.md \
  --base-labels evaluation/v3_base_labels_predictions.jsonl --base-labels-raw evaluation/v3_base_labels_raw.jsonl \
  --v2-labels evaluation/v3_v2_labels_predictions.jsonl --v2-labels-raw evaluation/v3_v2_labels_raw.jsonl \
  --v3-labels evaluation/v3_v3_labels_predictions.jsonl --v3-labels-raw evaluation/v3_v3_labels_raw.jsonl \
  --base-direct evaluation/v3_base_direct_predictions.jsonl --base-direct-raw evaluation/v3_base_direct_raw.jsonl \
  --v2-direct evaluation/v3_v2_direct_predictions.jsonl --v2-direct-raw evaluation/v3_v2_direct_raw.jsonl \
  --v3-direct evaluation/v3_v3_direct_predictions.jsonl --v3-direct-raw evaluation/v3_v3_direct_raw.jsonl
