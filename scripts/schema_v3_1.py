"""Validate the frozen v3.1 corpus and its explicit navigation label."""

from __future__ import annotations

import json
import re
from pathlib import Path

from policy_v3_1 import action_for
from schema_v2 import ACTION_KEYS, INTENTS, TOPICS, validate_intervention

REQUIRED = {
    "id", "query", "language", "locale", "source_type", "semantic_group_id",
    "topic", "intent", "resource_navigation", "intervention", "redirect_target",
    "rationale", "review_status", "dataset_version", "origin_version",
}


def read_jsonl(path: str | Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def validate_dataset(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    ids, query_locale = set(), set()
    groups: dict[str, list[dict]] = {}
    for index, row in enumerate(rows, 1):
        prefix = f"row {index} ({row.get('id', '?')})"
        if set(row) != REQUIRED:
            errors.append(f"{prefix}: fields differ: missing={sorted(REQUIRED-set(row))}, extra={sorted(set(row)-REQUIRED)}")
        if not re.fullmatch(r"sq_\d{4,}", str(row.get("id", ""))):
            errors.append(f"{prefix}: bad id")
        if row.get("id") in ids:
            errors.append(f"{prefix}: duplicate id")
        ids.add(row.get("id"))
        for key in REQUIRED - {"resource_navigation", "intervention", "redirect_target"}:
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"{prefix}: {key} must be nonempty text")
        if row.get("language") != "zh" or row.get("locale") not in {"CN", "SG"}:
            errors.append(f"{prefix}: language/locale invalid")
        if row.get("source_type") != "synthetic" or row.get("dataset_version") != "v3.1-draft":
            errors.append(f"{prefix}: source/version invalid")
        if row.get("review_status") not in {"draft", "approved", "rejected"}:
            errors.append(f"{prefix}: review status invalid")
        if row.get("origin_version") not in {"v0", "v2", "v2.1", "v3", "v3.1"}:
            errors.append(f"{prefix}: origin invalid")
        if row.get("topic") not in TOPICS or row.get("intent") not in INTENTS:
            errors.append(f"{prefix}: topic/intent invalid")
        if type(row.get("resource_navigation")) is not bool:
            errors.append(f"{prefix}: resource_navigation must be bool")
        errors += [f"{prefix}: {e}" for e in validate_intervention(row.get("intervention"), row.get("redirect_target"))]
        if row.get("topic") in TOPICS and row.get("intent") in INTENTS and type(row.get("resource_navigation")) is bool:
            expected = action_for(row["topic"], row["intent"], row.get("locale"), row["resource_navigation"])
            if expected is None or row.get("intervention") != expected[0] or row.get("redirect_target") != expected[1]:
                errors.append(f"{prefix}: action/target conflict with v3.1 policy")
        key = (" ".join(str(row.get("query", "")).casefold().split()), row.get("locale"))
        if key in query_locale:
            errors.append(f"{prefix}: duplicate query and locale")
        query_locale.add(key)
        groups.setdefault(str(row.get("semantic_group_id")), []).append(row)
    for group, members in groups.items():
        if len({(r.get("topic"), r.get("intent"), r.get("resource_navigation")) for r in members}) != 1:
            errors.append(f"group {group}: inconsistent labels")
        if len({r.get("locale") for r in members}) != len(members):
            errors.append(f"group {group}: locale duplicated")
    return errors
