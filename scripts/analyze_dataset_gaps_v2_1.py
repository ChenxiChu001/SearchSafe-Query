"""Profile frozen v2.1 test results by language, topic, and intervention."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from compare_training_v2 import action_bit, load_run, prf
from schema_v2 import ACTION_KEYS, read_jsonl


CORPUS = Path("data/canonical/training_candidates_v2_1.jsonl")
SPLIT_DIR = Path("data/splits/v2_1_seed42")
COMPARISON = Path("evaluation/training_comparison_v2_1.json")


def count_groups(rows: list[dict]) -> int:
    return len({row["semantic_group_id"] for row in rows})


def action_errors(rows: list[dict], predictions: dict[str, dict], bit: str) -> dict:
    false_positive, false_negative = [], []
    for row in rows:
        expected = row["intervention"][bit]
        action = predictions[row["id"]].get("intervention")
        actual = action.get(bit) if isinstance(action, dict) else None
        if actual is True and not expected:
            false_positive.append(row["id"])
        elif expected and actual is not True:
            false_negative.append(row["id"])
    return {"false_positive_ids": false_positive, "false_negative_ids": false_negative}


def correct_counts(rows: list[dict], predictions: dict[str, dict]) -> dict:
    return {
        "n": len(rows),
        "groups": count_groups(rows),
        "topic_correct": sum(predictions[row["id"]]["topic"] == row["topic"] for row in rows),
        "intent_correct": sum(predictions[row["id"]]["intent"] == row["intent"] for row in rows),
        "action_exact": sum(predictions[row["id"]].get("intervention") == row["intervention"] for row in rows),
    }


def main() -> None:
    corpus = read_jsonl(str(CORPUS))
    manifest_path = SPLIT_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    split_rows = {name: read_jsonl(str(SPLIT_DIR / f"{name}.jsonl")) for name in ("train", "dev", "test")}
    for name, rows in split_rows.items():
        path = SPLIT_DIR / f"{name}.jsonl"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["splits"][name]["sha256"]
        assert {row["id"] for row in rows} == set(manifest["splits"][name]["ids"])
    test = split_rows["test"]
    gold = {row["id"]: row for row in test}
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))
    assert comparison["test_sha256"] == manifest["splits"]["test"]["sha256"]

    pairs = defaultdict(dict)
    for row in test:
        pairs[row["semantic_group_id"]][row["language"]] = row
    paired = {group: pair for group, pair in pairs.items() if set(pair) == {"en", "zh"}}

    profile = {
        "sources": {"corpus": str(CORPUS), "manifest": str(manifest_path), "comparison": str(COMPARISON)},
        "corpus": {
            "rows": len(corpus), "groups": count_groups(corpus),
            "language_rows": dict(Counter(row["language"] for row in corpus)),
            "topic_rows": dict(Counter(row["topic"] for row in corpus)),
            "block_rows": sum(row["intervention"]["block"] for row in corpus),
            "block_groups": count_groups([row for row in corpus if row["intervention"]["block"]]),
            "block_review_status": dict(Counter(row["review_status"] for row in corpus if row["intervention"]["block"])),
            "action_patterns": len({tuple(row["intervention"][bit] for bit in ACTION_KEYS) for row in corpus}),
        },
        "splits": {
            name: {
                "rows": len(rows), "groups": count_groups(rows),
                "language_rows": dict(Counter(row["language"] for row in rows)),
                "block_rows": sum(row["intervention"]["block"] for row in rows),
                "block_groups": count_groups([row for row in rows if row["intervention"]["block"]]),
            }
            for name, rows in split_rows.items()
        },
        "test_bilingual_pairs": len(paired),
        "runs": {},
    }
    for key in ("base_labels", "tuned_labels", "base_direct", "tuned_direct"):
        meta = comparison["runs"][key]["meta"]
        route = "labels" if key.endswith("labels") else "direct"
        predictions, _ = load_run(meta["path"], meta["raw_path"], set(gold), route, gold)
        run = {
            "overall": correct_counts(test, predictions),
            "action_bits": {bit: {**action_bit(test, predictions, bit), **action_errors(test, predictions, bit)}
                            for bit in ACTION_KEYS},
            "languages": {}, "topics": {}, "bilingual_output_disagreement": [],
        }
        for language in ("en", "zh"):
            rows = [row for row in test if row["language"] == language]
            run["languages"][language] = {
                **correct_counts(rows, predictions),
                "action_bits": {bit: action_bit(rows, predictions, bit) for bit in ACTION_KEYS},
                "topics": {topic: prf(rows, predictions, "topic", topic)
                           for topic in sorted({row["topic"] for row in test})},
            }
        for topic in sorted({row["topic"] for row in test}):
            rows = [row for row in test if row["topic"] == topic]
            run["topics"][topic] = {**correct_counts(rows, predictions), **prf(test, predictions, "topic", topic)}
        for group, pair in sorted(paired.items()):
            left = predictions[pair["en"]["id"]]
            right = predictions[pair["zh"]["id"]]
            fields = ("topic", "intent", "intervention")
            if any(left.get(field) != right.get(field) for field in fields):
                run["bilingual_output_disagreement"].append(
                    {"semantic_group_id": group, "en_id": pair["en"]["id"], "zh_id": pair["zh"]["id"]}
                )
        profile["runs"][key] = run
    print(json.dumps(profile, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
