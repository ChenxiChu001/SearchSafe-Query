"""Make a human review queue for every v3.1 draft row."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from schema_v3_1 import read_jsonl

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data/canonical/training_candidates_v3_1.jsonl"
LEDGER = ROOT / "review/revisions_v3_1.tsv"
OUTPUT = ROOT / "review/review_v3_1_drafts.tsv"


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("review sheet exists")
    rows = read_jsonl(CANONICAL)
    with LEDGER.open(encoding="utf-8", newline="") as f:
        reasons = {row["id"]: row["reason"] for row in csv.DictReader(f, delimiter="\t")}
    fields = ("id", "split", "query", "locale", "topic", "intent", "resource_navigation",
              "intervention", "redirect_target", "origin_version", "reason_for_review",
              "decision_accept_or_edit", "corrected_topic", "corrected_intent",
              "corrected_resource_navigation", "corrected_intervention", "reviewer_note")
    manifest = {}
    for split in ("train", "dev", "test", "legacy_test"):
        for row in read_jsonl(ROOT / f"data/splits/v3_1_seed42/{split}.jsonl"):
            manifest[row["id"]] = split
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in rows:
            if row["review_status"] != "draft":
                continue
            writer.writerow({"id": row["id"], "split": manifest[row["id"]],
                             "query": row["query"], "locale": row["locale"],
                             "topic": row["topic"], "intent": row["intent"],
                             "resource_navigation": str(row["resource_navigation"]).lower(),
                             "intervention": json.dumps(row["intervention"], ensure_ascii=False, separators=(",", ":")),
                             "redirect_target": row["redirect_target"] or "",
                             "origin_version": row["origin_version"],
                             "reason_for_review": reasons.get(row["id"], "新增合成候选题")})
    print(f"Wrote {sum(r['review_status']=='draft' for r in rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
