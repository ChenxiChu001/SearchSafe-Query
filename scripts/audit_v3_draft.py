"""Profile frozen v3 structure, split integrity, and obvious near-duplicate risks."""

from __future__ import annotations

import difflib
import hashlib
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from schema_v3 import ACTION_KEYS, read_jsonl, validate_dataset

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/canonical/training_candidates_v3_draft.jsonl"
SPLITS = ROOT / "data/splits/v3_seed42"
OUTPUT = ROOT / "evaluation/data_quality_profile_v3.json"


def compact(query: str) -> str:
    return re.sub(r"[\s，。！？、,.!?;；:：‘’“”\"'（）()\-—]", "", query).casefold()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUTPUT}")
    rows = read_jsonl(DATA)
    errors = validate_dataset(rows)
    if errors:
        raise ValueError("\n".join(errors[:30]))
    manifest = json.loads((SPLITS / "manifest.json").read_text(encoding="utf-8"))
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != manifest["source_sha256"]:
        raise ValueError("canonical hash differs from manifest")
    by_split = {}
    for split in ("train", "dev", "test"):
        path = SPLITS / f"{split}.jsonl"
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["splits"][split]["sha256"]:
            raise ValueError(f"{split} hash differs from manifest")
        by_split[split] = read_jsonl(path)
    all_split_rows = sum(by_split.values(), [])
    if {r["id"]: r for r in all_split_rows} != {r["id"]: r for r in rows}:
        raise ValueError("splits do not reproduce canonical rows")
    group_split = {}
    for split, members in by_split.items():
        for row in members:
            previous = group_split.setdefault(row["semantic_group_id"], split)
            if previous != split:
                raise ValueError("semantic group crosses split")
    duplicate_text = Counter(compact(r["query"]) for r in rows)
    by_label = defaultdict(list)
    for split, members in by_split.items():
        for row in members:
            by_label[row["topic"], row["intent"]].append((split, row))
    near_edges = []
    for (topic, intent), members in by_label.items():
        for (split_a, a), (split_b, b) in combinations(members, 2):
            if split_a == split_b or a["semantic_group_id"] == b["semantic_group_id"]:
                continue
            left, right = compact(a["query"]), compact(b["query"])
            if abs(len(left) - len(right)) > max(len(left), len(right)) * 0.3:
                continue
            score = difflib.SequenceMatcher(None, left, right).ratio()
            if score >= 0.82:
                near_edges.append({"left": a["id"], "right": b["id"], "splits": [split_a, split_b],
                                   "topic": topic, "intent": intent, "similarity": round(score, 3),
                                   "queries": [a["query"], b["query"]]})
    by_split_stats = {}
    for name, members in by_split.items():
        by_split_stats[name] = {
            "rows": len(members), "groups": len({r["semantic_group_id"] for r in members}),
            "topic": dict(Counter(r["topic"] for r in members)),
            "intent": dict(Counter(r["intent"] for r in members)),
            "locale": dict(Counter(r["locale"] for r in members)),
            "review_status": dict(Counter(r["review_status"] for r in members)),
            "positive_actions": {k: sum(r["intervention"][k] for r in members) for k in ACTION_KEYS},
        }
    profile = {
        "source": str(DATA.relative_to(ROOT)), "sha256": manifest["source_sha256"],
        "rows": len(rows), "groups": len(group_split), "schema_errors": len(errors),
        "duplicate_normalized_query_strings": sum(n - 1 for n in duplicate_text.values() if n > 1),
        "review_status": dict(Counter(r["review_status"] for r in rows)),
        "origin_version": dict(Counter(r["origin_version"] for r in rows)),
        "topic": dict(Counter(r["topic"] for r in rows)),
        "intent": dict(Counter(r["intent"] for r in rows)),
        "topic_locale": {topic: dict(Counter(r["locale"] for r in rows if r["topic"] == topic))
                         for topic in sorted({r["topic"] for r in rows})},
        "action_patterns": dict(Counter("".join(str(int(r["intervention"][k])) for k in ACTION_KEYS) for r in rows)),
        "splits": by_split_stats,
        "cross_split_character_similarity_threshold": 0.82,
        "cross_split_near_edges": near_edges,
        "limits": ["character similarity misses semantic paraphrases", "draft labels have not been human audited",
                   "all new test and train examples were generated with the same local base model"],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"rows={len(rows)} groups={len(group_split)} duplicate_queries={profile['duplicate_normalized_query_strings']} cross_split_near_edges={len(near_edges)}")
    print("split counts", {name: stats["rows"] for name, stats in by_split_stats.items()})
    for edge in near_edges[:15]:
        print(edge)


if __name__ == "__main__":
    main()
