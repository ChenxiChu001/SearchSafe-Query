"""Remove generated label conflicts and rebalance new test intent coverage.

Run after generation. Removed candidates remain in the audit file; the
original v3 corpus is untouched. Rerun generation to refill quotas.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from generate_v3_1_queries import OUT, cell_key, quotas, valid

REMOVALS = OUT.with_name("removed_low_quality_queries.jsonl")


def main() -> None:
    if REMOVALS.exists():
        raise FileExistsError("rebalance already ran")
    rows = [json.loads(line) for line in OUT.open()]
    target = quotas()
    kept, removed = [], []
    count = Counter()
    for row in rows:
        key = cell_key(row)
        reason = None
        if key not in target or count[key] >= target[key]:
            reason = "over revised quota"
        elif not valid(row["query"], row["topic"], row["intent"], row["resource_navigation"]):
            reason = "query does not meet explicit topic/intent evidence gate"
        if reason:
            removed.append({**row, "reason": reason})
        else:
            kept.append(row)
            count[key] += 1
    if len(removed) < 8:
        raise ValueError("expected at least eight superseded ambiguous test candidates")
    REMOVALS.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in removed), encoding="utf-8")
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept), encoding="utf-8")
    print(f"Retained {len(kept)}, removed {len(removed)}; rerun generator to refill revised quotas")


if __name__ == "__main__":
    main()
