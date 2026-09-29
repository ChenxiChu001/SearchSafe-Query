"""Freeze the user-accepted v2 rows and append 80 unreviewed political candidates."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from build_v2_candidates import make_row, parse_seeds, write_jsonl
from schema_v2 import read_jsonl, validate_dataset

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/canonical/candidates_v2.jsonl"
SEEDS = ROOT / "data/v2_political_expansion_pairs.psv"
REVIEWED = ROOT / "data/canonical/reviewed_v2.jsonl"
NEW = ROOT / "data/canonical/political_expansion_v2_1_draft.jsonl"
COMBINED = ROOT / "data/canonical/training_candidates_v2_1.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="replace generated files, including reviewer edits")
    args = parser.parse_args()
    old = read_jsonl(SOURCE)
    if len(old) != 248 or any(row["review_status"] != "draft" for row in old):
        raise ValueError("expected the unchanged 248-row v2 draft source")
    reviewed = [{**row, "review_status": "approved", "dataset_version": "v2"} for row in old]
    pairs = parse_seeds(SEEDS, 4)
    if len(pairs) != 40:
        raise ValueError(f"expected 40 bilingual political seed pairs, got {len(pairs)}")
    new = []
    for group_number, (intent, locale, en, zh) in enumerate(pairs, 124):
        for offset, language, query in ((0, "en", en), (1, "zh", zh)):
            row = make_row(249 + 2 * (group_number - 124) + offset, query, language,
                           locale, f"g{group_number:03d}", "POLITICAL_SENSITIVE", intent, "v2.1")
            row["dataset_version"] = "v2.1-draft"
            new.append(row)
    combined = reviewed + new
    if len(new) != 80 or len(combined) != 328:
        raise ValueError("wrong corpus size")
    expected = {"GENERAL_INFO": 40, "PRIVATE_INFO_REQUEST": 20, "SUPPORT_SEEKING": 20}
    if Counter(row["intent"] for row in new) != expected:
        raise ValueError("unexpected political intent allocation")
    if Counter(row["locale"] for row in new) != {"CN": 64, "SG": 16}:
        raise ValueError("unexpected locale allocation")
    errors = validate_dataset(combined)
    if errors:
        raise ValueError("\n".join(errors))
    for path, rows in ((REVIEWED, reviewed), (NEW, new), (COMBINED, combined)):
        write_jsonl(path, rows, args.force)
    print(f"Prepared {len(reviewed)} approved single-review rows and {len(new)} draft political rows")


if __name__ == "__main__":
    main()
