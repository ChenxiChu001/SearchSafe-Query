"""Convert canonical records to MLX-LM chat format for a technical smoke run.

This conversion uses all input records as training examples and creates no test set.
It must not be used to claim generalization or model improvement.
"""

import argparse
import json
from collections import Counter
from pathlib import Path

from schema import read_jsonl, validate_dataset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("output_dir")
    parser.add_argument("--prompt", default="prompts/query_triage_zero_shot_v0.txt")
    parser.add_argument("--allow-draft", action="store_true",
                        help="required to use unreviewed data for technical smoke only")
    args = parser.parse_args()
    records = read_jsonl(args.data)
    errors = validate_dataset(records)
    if errors:
        print("\n".join(errors))
        return 1
    statuses = Counter(row["review_status"] for row in records)
    if statuses != {"approved": len(records)} and not args.allow_draft:
        print("Unapproved records present. Use --allow-draft only for a technical smoke run.")
        return 1
    prompt = Path(args.prompt).read_text(encoding="utf-8").strip()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "train.jsonl"
    with output.open("w", encoding="utf-8") as handle:
        for row in records:
            target = {key: row[key] for key in ("topic", "intent", "triage")}
            message = {
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": row["query"]},
                    {"role": "assistant", "content": json.dumps(target, ensure_ascii=False, separators=(",", ":"))},
                ]
            }
            handle.write(json.dumps(message, ensure_ascii=False) + "\n")
    manifest = {
        "purpose": "technical_smoke_only",
        "source": str(Path(args.data).resolve()),
        "records": len(records),
        "review_statuses": dict(statuses),
        "has_holdout_test": False,
        "can_claim_model_improvement": False,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} training records to {output}; technical smoke only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
