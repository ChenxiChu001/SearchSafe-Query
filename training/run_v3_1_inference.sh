#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
MODEL_PATH="$HOME/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit"
TEST_DATA="data/splits/v3_1_seed42/test.jsonl"

for task in direct; do
  for version in base v3 v31; do
    case "$version" in
      base) adapter_path="" ;;
      v3) adapter_path="adapters/v3_${task}_qlora" ;;
      v31) adapter_path="adapters/v3_1_direct_selected_qlora" ;;
    esac
    stem="evaluation/v3_1_${version}_${task}"
    if [[ -f "${stem}_raw.jsonl" ]]; then
      if [[ $(wc -l < "${stem}_raw.jsonl") -eq $(wc -l < "$TEST_DATA") ]]; then
        echo "Reusing completed $version $task raw audit"
        continue
      fi
      echo "Partial raw audit exists for $version $task; inspect before rerunning" >&2
      exit 1
    fi
    echo "Inferring $version $task on v3.1 new test"
    if [[ -n "$adapter_path" ]]; then
      .venv/bin/python scripts/infer_mlx_v3_1.py "$TEST_DATA" "${stem}_predictions.jsonl" \
        --raw "${stem}_raw.jsonl" --model "$MODEL_PATH" --task "$task" \
        --adapter "$adapter_path" > "training/v3_1_${version}_${task}_inference.log" 2>&1 || true
    else
      .venv/bin/python scripts/infer_mlx_v3_1.py "$TEST_DATA" "${stem}_predictions.jsonl" \
        --raw "${stem}_raw.jsonl" --model "$MODEL_PATH" --task "$task" \
        > "training/v3_1_${version}_${task}_inference.log" 2>&1 || true
    fi
  done
done

.venv/bin/python - <<'PY'
import json
from pathlib import Path
names = [f"{version}_direct" for version in ("base", "v3", "v31")]
manifest = {name: {"predictions": f"evaluation/v3_1_{name}_predictions.jsonl",
                   "raw": f"evaluation/v3_1_{name}_raw.jsonl"} for name in names}
Path("evaluation/v3_1_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
PY
.venv/bin/python scripts/compare_v3_1_direct.py \
  "$TEST_DATA" data/splits/v3_1_seed42/manifest.json evaluation/v3_1_run_manifest.json \
  evaluation/training_comparison_v3_1.json evaluation/training_comparison_v3_1.md
