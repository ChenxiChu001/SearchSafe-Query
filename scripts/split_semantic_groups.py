"""Split approved canonical records by whole semantic group, stratified by topic.

Small datasets may leave intents absent from one or more splits. Inspect the
manifest before using any split for evaluation.
"""

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from schema import read_jsonl, validate_dataset


def split_groups(records: list[dict], seed: int = 42,
                 dev_fraction: float = 0.15, test_fraction: float = 0.15) -> dict[str, list[dict]]:
    if dev_fraction <= 0 or test_fraction <= 0 or dev_fraction + test_fraction >= 1:
        raise ValueError("dev and test fractions must be positive and sum to less than 1")
    grouped = defaultdict(list)
    for row in records:
        grouped[row["semantic_group_id"]].append(row)
    by_topic = defaultdict(list)
    for group_id, members in grouped.items():
        topics = {member["topic"] for member in members}
        if len(topics) != 1:
            raise ValueError(f"{group_id}: mixed topics")
        by_topic[next(iter(topics))].append(group_id)
    assigned = {"train": set(), "dev": set(), "test": set()}
    rng = random.Random(seed)
    for topic in sorted(by_topic):
        group_ids = sorted(by_topic[topic])
        if len(group_ids) < 3:
            raise ValueError(f"topic {topic}: need at least three semantic groups")
        rng.shuffle(group_ids)
        n_dev = max(1, round(len(group_ids) * dev_fraction))
        n_test = max(1, round(len(group_ids) * test_fraction))
        if n_dev + n_test >= len(group_ids):
            raise ValueError(f"topic {topic}: too few groups for requested split")
        assigned["test"].update(group_ids[:n_test])
        assigned["dev"].update(group_ids[n_test:n_test + n_dev])
        assigned["train"].update(group_ids[n_test + n_dev:])
    result = {name: [] for name in assigned}
    for row in records:
        split = next(name for name, group_ids in assigned.items() if row["semantic_group_id"] in group_ids)
        result[split].append(row)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("output_dir")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dev-fraction", type=float, default=0.15)
    parser.add_argument("--test-fraction", type=float, default=0.15)
    parser.add_argument("--allow-draft", action="store_true",
                        help="preview only; do not treat the output as a Gold evaluation split")
    args = parser.parse_args()
    records = read_jsonl(args.data)
    errors = validate_dataset(records)
    if errors:
        print("\n".join(errors))
        return 1
    if any(row["review_status"] != "approved" for row in records) and not args.allow_draft:
        print("Unapproved records present. Use --allow-draft for a split preview only.")
        return 1
    try:
        splits = split_groups(records, args.seed, args.dev_fraction, args.test_fraction)
    except ValueError as exc:
        print(exc)
        return 1
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"purpose": "preview_only" if args.allow_draft else "approved_split",
                "seed": args.seed, "source": str(Path(args.data).resolve()), "splits": {}}
    for name, rows in splits.items():
        with (output_dir / f"{name}.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        manifest["splits"][name] = {
            "records": len(rows),
            "semantic_groups": sorted({row["semantic_group_id"] for row in rows}),
            "topics": dict(Counter(row["topic"] for row in rows)),
            "intents": dict(Counter(row["intent"] for row in rows)),
        }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, summary in manifest["splits"].items():
        print(f"{name}: {summary['records']} records, {len(summary['semantic_groups'])} groups, intents={summary['intents']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
