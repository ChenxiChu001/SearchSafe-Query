"""Check the complete v2 schema and print a compact corpus summary."""

from __future__ import annotations

import argparse
from collections import Counter

from schema_v2 import read_jsonl, validate_dataset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    args = parser.parse_args()
    rows = read_jsonl(args.data)
    errors = validate_dataset(rows)
    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        return 1
    print(f"VALID: {len(rows)} rows, {len({row['semantic_group_id'] for row in rows})} semantic groups")
    for name in ("topic", "intent", "locale", "review_status", "origin_version"):
        print(f"{name}: {dict(Counter(row[name] for row in rows))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
