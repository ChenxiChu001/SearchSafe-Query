"""Convert frozen canonical splits to MLX-LM chat examples for two QLoRA tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from schema_v3 import read_jsonl, validate_dataset

PROMPTS = {
    "labels": Path("prompts/query_labels_v2_1.txt"),
    "direct": Path("prompts/query_intervention_v3.txt"),
}


def target(row: dict, task: str) -> dict:
    result = {"topic": row["topic"], "intent": row["intent"]}
    if task == "direct":
        result["intervention"] = row["intervention"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("split_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--task", choices=sorted(PROMPTS), required=True)
    args = parser.parse_args()
    split_dir, output_dir = Path(args.split_dir), Path(args.output_dir)
    if output_dir.exists():
        parser.error("output directory exists; training data will not be overwritten")
    canonical = {name: read_jsonl(split_dir / f"{name}.jsonl") for name in ("train", "dev", "test")}
    all_rows = sum(canonical.values(), [])
    errors = validate_dataset(all_rows)
    if errors:
        raise ValueError("\n".join(errors))
    groups = {name: {row["semantic_group_id"] for row in rows} for name, rows in canonical.items()}
    if any(groups[a] & groups[b] for a, b in (("train", "dev"), ("train", "test"), ("dev", "test"))):
        raise ValueError("semantic group crosses split")
    prompt_path = PROMPTS[args.task]
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    output_dir.mkdir(parents=True)
    manifest = {"task": args.task, "split_dir": str(split_dir), "prompt": str(prompt_path),
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "format": "mlx-lm chat", "mask_prompt": True, "splits": {}}
    for name, rows in canonical.items():
        mlx_name = "valid" if name == "dev" else name
        examples = []
        for row in rows:
            examples.append({"messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"locale={row['locale']}\nquery={row['query']}"},
                {"role": "assistant", "content": json.dumps(target(row, args.task), ensure_ascii=False, separators=(",", ":"))},
            ]})
        (output_dir / f"{mlx_name}.jsonl").write_text(
            "".join(json.dumps(example, ensure_ascii=False) + "\n" for example in examples), encoding="utf-8")
        manifest["splits"][name] = {"rows": len(rows), "statuses": dict(Counter(row["review_status"] for row in rows)),
                                    "sha256": hashlib.sha256((split_dir / f"{name}.jsonl").read_bytes()).hexdigest()}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote MLX {args.task} data: train={len(canonical['train'])}, valid={len(canonical['dev'])}, test={len(canonical['test'])}")


if __name__ == "__main__":
    main()
