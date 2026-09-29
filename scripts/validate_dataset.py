"""Validate a canonical JSONL file. Exits nonzero if a rule fails."""

import argparse
from collections import Counter

from schema import read_jsonl, validate_dataset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    args = parser.parse_args()
    try:
        records = read_jsonl(args.data)
    except ValueError as exc:
        print(f"INVALID: {exc}")
        return 1
    errors = validate_dataset(records)
    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        return 1
    print(f"VALID: {len(records)} candidate records in {len({r['semantic_group_id'] for r in records})} semantic groups")
    print(f"Review status: {dict(Counter(r['review_status'] for r in records))}")
    print(f"Topic: {dict(Counter(r['topic'] for r in records))}")
    print(f"Intent: {dict(Counter(r['intent'] for r in records))}")
    print(f"Language: {dict(Counter(r['language'] for r in records))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
