"""Profile the frozen v2.1 corpus and check split integrity for quality review."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from build_v2_candidates import intervention
from schema_v2 import ACTION_KEYS, REQUIRED, read_jsonl, validate_dataset


def counts(rows: list[dict], key: str) -> dict[str, int]:
    return dict(sorted(Counter(row[key] for row in rows).items()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("split_manifest")
    parser.add_argument("output")
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error("output exists; choose a new audit path")

    data_path = Path(args.data)
    rows = read_jsonl(data_path)
    schema_errors = validate_dataset(rows)
    if schema_errors:
        raise ValueError("\n".join(schema_errors))
    manifest_path = Path(args.split_manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()
    if data_hash != manifest["source_sha256"]:
        raise ValueError("corpus differs from frozen manifest")

    ids = {row["id"] for row in rows}
    if len(ids) != len(rows):
        raise ValueError("duplicate ids")
    row_for = {row["id"]: row for row in rows}
    cluster_for = manifest["leakage_cluster_for_semantic_group"]
    split_for_id = {}
    split_groups = {}
    split_clusters = {}
    split_stats = {}
    for name in ("train", "dev", "test"):
        info = manifest["splits"][name]
        split_path = manifest_path.parent / f"{name}.jsonl"
        if hashlib.sha256(split_path.read_bytes()).hexdigest() != info["sha256"]:
            raise ValueError(f"{name} content differs from frozen manifest")
        members = read_jsonl(split_path)
        split_ids = [row["id"] for row in members]
        if split_ids != info["ids"] or any(row_for.get(row["id"]) != row for row in members):
            raise ValueError(f"{name} does not match corpus or manifest")
        if any(row_id in split_for_id for row_id in split_ids):
            raise ValueError("an id appears in multiple splits")
        split_for_id.update({row_id: name for row_id in split_ids})
        split_groups[name] = {row["semantic_group_id"] for row in members}
        split_clusters[name] = {cluster_for[row["semantic_group_id"]] for row in members}
        split_stats[name] = {
            "rows": len(members), "semantic_groups": len(split_groups[name]),
            "leakage_clusters": len(split_clusters[name]),
            "topic": counts(members, "topic"), "intent": counts(members, "intent"),
            "review_status": counts(members, "review_status"),
            "positive_actions": {key: sum(row["intervention"][key] for row in members) for key in ACTION_KEYS},
        }
    if set(split_for_id) != ids:
        raise ValueError("split IDs do not cover the corpus")
    if any(split_groups[a] & split_groups[b] or split_clusters[a] & split_clusters[b]
           for a, b in (("train", "dev"), ("train", "test"), ("dev", "test"))):
        raise ValueError("semantic group or leakage cluster crosses splits")
    cross_split_near_duplicates = [edge for edge in manifest["leakage_edges"]
                                   if split_for_id[edge["left_id"]] != split_for_id[edge["right_id"]]]
    if cross_split_near_duplicates:
        raise ValueError("known near duplicate crosses splits")

    missing = {key: sum(key not in row for row in rows) for key in sorted(REQUIRED)}
    nulls = {key: sum(row.get(key) is None for row in rows) for key in sorted(REQUIRED)}
    empty = {key: sum(isinstance(row.get(key), str) and not row[key].strip() for row in rows)
             for key in sorted(REQUIRED)}
    normalized = Counter((" ".join(row["query"].casefold().split()), row["locale"]) for row in rows)
    topic_intent = defaultdict(Counter)
    topic_locale = defaultdict(Counter)
    for row in rows:
        topic_intent[row["topic"]][row["intent"]] += 1
        topic_locale[row["topic"]][row["locale"]] += 1
    observed_combinations = {(row["topic"], row["intent"]) for row in rows}
    locale_action_differences = []
    locale_target_differences = []
    for topic, intent in sorted(observed_combinations):
        cn_action, cn_target = intervention(topic, intent, "CN")
        sg_action, sg_target = intervention(topic, intent, "SG")
        if cn_action != sg_action:
            locale_action_differences.append([topic, intent])
        if cn_target != sg_target:
            locale_target_differences.append([topic, intent])

    profile = {
        "source": str(data_path), "source_sha256": data_hash,
        "grain": "one query-language-locale candidate row; bilingual semantic groups are related",
        "rows": len(rows), "fields": len(REQUIRED), "semantic_groups": len({row["semantic_group_id"] for row in rows}),
        "missing_required": missing, "null_fields": nulls, "empty_strings": empty,
        "duplicate_ids": len(rows) - len(ids),
        "duplicate_normalized_query_locale_keys": sum(count - 1 for count in normalized.values() if count > 1),
        "source_type": counts(rows, "source_type"), "review_status": counts(rows, "review_status"),
        "language": counts(rows, "language"), "locale": counts(rows, "locale"),
        "topic": counts(rows, "topic"), "intent": counts(rows, "intent"),
        "topic_intent": {topic: dict(sorted(values.items())) for topic, values in sorted(topic_intent.items())},
        "topic_locale": {topic: dict(sorted(values.items())) for topic, values in sorted(topic_locale.items())},
        "action_signatures": dict(sorted(Counter("".join(str(int(row["intervention"][key])) for key in ACTION_KEYS)
                                                   for row in rows).items())),
        "locale_action_differences_in_observed_combinations": locale_action_differences,
        "locale_redirect_target_differences_in_observed_combinations": locale_target_differences,
        "known_cross_group_near_duplicate_edges": len(manifest["leakage_edges"]),
        "known_near_duplicate_edges_crossing_splits": len(cross_split_near_duplicates),
        "splits": split_stats,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Audited {len(rows)} rows; {len(schema_errors)} schema errors; {len(cross_split_near_duplicates)} known cross-split near duplicates")
    print(f"Topic-locale table: {profile['topic_locale']}")
    print(f"Six-action locale differences: {len(locale_action_differences)}")


if __name__ == "__main__":
    main()
