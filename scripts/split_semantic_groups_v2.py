"""Freeze v2.1 internal train/dev/test sets with near-duplicate leakage clusters."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import random
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from schema_v2 import read_jsonl, validate_dataset


class UnionFind:
    def __init__(self, values):
        self.parent = {value: value for value in values}

    def find(self, value):
        if self.parent[value] != value:
            self.parent[value] = self.find(self.parent[value])
        return self.parent[value]

    def union(self, left, right):
        a, b = self.find(left), self.find(right)
        if a != b:
            self.parent[max(a, b)] = min(a, b)


def leakage_clusters(rows: list[dict], threshold: float = 0.77) -> tuple[dict[str, str], list[dict]]:
    group_ids = {row["semantic_group_id"] for row in rows}
    uf = UnionFind(group_ids)
    edges = []
    by_stratum_language = defaultdict(list)
    for row in rows:
        by_stratum_language[(row["topic"], row["intent"], row["language"])].append(row)
    for (topic, intent, language), members in by_stratum_language.items():
        for left, right in combinations(members, 2):
            if left["semantic_group_id"] == right["semantic_group_id"]:
                continue
            score = difflib.SequenceMatcher(None, left["query"].casefold(), right["query"].casefold()).ratio()
            if score >= threshold:
                uf.union(left["semantic_group_id"], right["semantic_group_id"])
                edges.append({"left_id": left["id"], "right_id": right["id"], "topic": topic,
                              "intent": intent, "language": language, "similarity": round(score, 4)})
    return {group: uf.find(group) for group in group_ids}, edges


def split(rows: list[dict], seed: int, dev_fraction: float, test_fraction: float) -> tuple[dict[str, list[dict]], dict]:
    cluster_for, edges = leakage_clusters(rows)
    groups = defaultdict(list)
    for row in rows:
        groups[cluster_for[row["semantic_group_id"]]].append(row)
    by_stratum = defaultdict(list)
    for cluster, members in groups.items():
        strata = {(row["topic"], row["intent"]) for row in members}
        if len(strata) != 1:
            raise ValueError(f"leakage cluster {cluster} mixes labels: {strata}")
        by_stratum[next(iter(strata))].append(cluster)
    rng = random.Random(seed)
    assigned = {"train": set(), "dev": set(), "test": set()}
    for stratum, clusters in sorted(by_stratum.items()):
        clusters = sorted(clusters)
        rng.shuffle(clusters)
        count = len(clusters)
        if count < 2:
            assigned["train"].update(clusters)
            continue
        n_test = max(1, round(count * test_fraction))
        n_dev = max(1, round(count * dev_fraction)) if count >= 4 else 0
        if n_test + n_dev >= count:
            raise ValueError(f"too few clusters in {stratum}")
        assigned["test"].update(clusters[:n_test])
        assigned["dev"].update(clusters[n_test:n_test + n_dev])
        assigned["train"].update(clusters[n_test + n_dev:])
    split_for_cluster = {cluster: name for name, clusters in assigned.items() for cluster in clusters}
    result = {name: [] for name in assigned}
    for row in rows:
        result[split_for_cluster[cluster_for[row["semantic_group_id"]]]].append(row)
    manifest = {
        "seed": seed, "dev_fraction_target": dev_fraction, "test_fraction_target": test_fraction,
        "near_duplicate_threshold": 0.77, "leakage_edges": edges,
        "leakage_cluster_for_semantic_group": dict(sorted(cluster_for.items())),
        "splits": {},
    }
    for name, members in result.items():
        manifest["splits"][name] = {
            "ids": [row["id"] for row in members], "rows": len(members),
            "semantic_groups": len({row["semantic_group_id"] for row in members}),
            "leakage_clusters": len({cluster_for[row["semantic_group_id"]] for row in members}),
            "topic_counts": dict(Counter(row["topic"] for row in members)),
            "intent_counts": dict(Counter(row["intent"] for row in members)),
            "review_status_counts": dict(Counter(row["review_status"] for row in members)),
        }
    return result, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("output_dir")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dev-fraction", type=float, default=0.15)
    parser.add_argument("--test-fraction", type=float, default=0.15)
    args = parser.parse_args()
    if not 0 < args.dev_fraction < 1 or not 0 < args.test_fraction < 1 or args.dev_fraction + args.test_fraction >= 1:
        parser.error("invalid split fractions")
    rows = read_jsonl(args.data)
    errors = validate_dataset(rows)
    if errors:
        raise ValueError("\n".join(errors))
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        parser.error("output directory exists; frozen split will not be overwritten")
    result, manifest = split(rows, args.seed, args.dev_fraction, args.test_fraction)
    manifest["source"] = str(Path(args.data))
    manifest["source_sha256"] = hashlib.sha256(Path(args.data).read_bytes()).hexdigest()
    output_dir.mkdir(parents=True)
    for name, members in result.items():
        split_path = output_dir / f"{name}.jsonl"
        split_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in members),
            encoding="utf-8",
        )
        manifest["splits"][name]["sha256"] = hashlib.sha256(split_path.read_bytes()).hexdigest()
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, stats in manifest["splits"].items():
        print(name, stats["rows"], "rows", stats["leakage_clusters"], "clusters", stats["review_status_counts"])
    print("near-duplicate edges", len(manifest["leakage_edges"]))


if __name__ == "__main__":
    main()
