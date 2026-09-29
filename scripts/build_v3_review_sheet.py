"""Select 60 draft train/dev cases for owner review after exploratory training."""

from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter
from pathlib import Path

from schema_v3 import read_jsonl

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ROOT / "data/splits/v3_seed42"
OUTPUT = ROOT / "review/review_v3_60.tsv"
MANIFEST = ROOT / "review/review_v3_60_manifest.json"


def audit_hint(row: dict) -> str:
    """Weak lexical cues to prioritize possible intent drift, not adjudications."""
    query, intent = row["query"], row["intent"]
    if intent == "GENERAL_INFO" and re.search(r"求助|怎么办|怎么防|如何防|如何避免|怎样避免|如何处理|举报", query):
        return "一般信息与预防/求助边界"
    if intent == "PREVENTION" and re.search(r"求助|急需|我该找谁|已经被|被骗|正在遭|是什么|定义", query):
        return "预防与求助/一般信息边界"
    if intent == "SUPPORT_SEEKING" and re.search(r"是什么|有哪些类型|如何识别|怎样预防|如何骗|怎样伤", query):
        return "求助与其他意图边界"
    if intent == "HARMFUL_INSTRUCTION" and re.search(r"预防|识别|举报|被骗|该挂断|如何避免|怎么防", query):
        return "有害请求与防范边界"
    if intent == "AMBIGUOUS" and re.search(r"怎么|如何|求助|帮我|举报|预防|识别", query):
        return "含糊与明确意图边界"
    if intent == "PRIVATE_INFO_REQUEST" and re.search(r"公开|新闻|官方资料", query):
        return "私人信息与公开资料边界"
    return ""


def main() -> None:
    if OUTPUT.exists() or MANIFEST.exists():
        raise FileExistsError("review sheet exists; refusing to overwrite reviewer edits")
    rows = [{**r, "split": name} for name in ("train", "dev")
            for r in read_jsonl(SPLITS / f"{name}.jsonl") if r["review_status"] == "draft"]
    rng = random.Random(20260927)
    pools = {
        "private_block": [r for r in rows if r["intent"] == "PRIVATE_INFO_REQUEST"],
        "harmful": [r for r in rows if r["intent"] == "HARMFUL_INSTRUCTION"],
        "support": [r for r in rows if r["intent"] == "SUPPORT_SEEKING"],
        "ambiguous": [r for r in rows if r["intent"] == "AMBIGUOUS"],
        "ordinary_boundary": [r for r in rows if r["intent"] in {"GENERAL_INFO", "PREVENTION"}],
    }
    targets = {"private_block": 10, "harmful": 20, "support": 10, "ambiguous": 10, "ordinary_boundary": 10}
    chosen = []
    for category, target in targets.items():
        pool = pools[category]
        if len(pool) < target:
            raise ValueError(f"too few rows for {category}")
        by_topic = {}
        for row in pool:
            by_topic.setdefault(row["topic"], []).append(row)
        for items in by_topic.values():
            rng.shuffle(items)
            items.sort(key=lambda row: bool(audit_hint(row)))
        current = []
        topics = sorted(by_topic)
        while len(current) < target:
            for topic in topics:
                if len(current) >= target:
                    break
                if by_topic[topic]:
                    current.append(by_topic[topic].pop())
        chosen.extend((category, row) for row in current)
    chosen.sort(key=lambda item: item[1]["id"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = ["id", "split", "query", "locale", "topic", "intent", "intervention", "redirect_target",
               "review_category", "audit_hint", "decision_accept_or_edit", "corrected_topic", "corrected_intent",
               "corrected_intervention", "reviewer_note"]
    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns, delimiter="\t")
        writer.writeheader()
        for category, row in chosen:
            writer.writerow({"id": row["id"], "split": row["split"], "query": row["query"],
                             "locale": row["locale"], "topic": row["topic"], "intent": row["intent"],
                             "intervention": json.dumps(row["intervention"], ensure_ascii=False, separators=(",", ":")),
                             "redirect_target": row["redirect_target"] or "", "review_category": category,
                             "audit_hint": audit_hint(row)})
    MANIFEST.write_text(json.dumps({"seed": 20260927, "source_splits": ["train", "dev"],
                                    "rows": len(chosen), "ids": [r["id"] for _, r in chosen],
                                    "category_counts": dict(Counter(c for c, _ in chosen)),
                                    "hinted_rows": sum(bool(audit_hint(r)) for _, r in chosen),
                                    "topic_counts": dict(Counter(r["topic"] for _, r in chosen)),
                                    "locale_counts": dict(Counter(r["locale"] for _, r in chosen))},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(chosen)} train/dev review rows to {OUTPUT}")


if __name__ == "__main__":
    main()
