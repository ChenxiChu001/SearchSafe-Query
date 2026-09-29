"""Validation for the Chinese v3 synthetic query corpus."""

from __future__ import annotations

from schema_v2 import ACTION_KEYS, INTENTS, TOPICS, read_jsonl, validate_dataset as validate_v2
from policy_v3 import action_for


def validate_dataset(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    compatible = []
    for index, row in enumerate(rows, 1):
        prefix = f"row {index} ({row.get('id', '?')})"
        if row.get("language") != "zh":
            errors.append(f"{prefix}: v3 requires Chinese queries")
        if row.get("dataset_version") != "v3-draft":
            errors.append(f"{prefix}: dataset_version must be v3-draft")
        if row.get("origin_version") not in {"v0", "v2", "v2.1", "v3"}:
            errors.append(f"{prefix}: invalid origin_version")
        if row.get("topic") in TOPICS and row.get("intent") in INTENTS and row.get("locale") in {"CN", "SG"}:
            expected = action_for(row["topic"], row["intent"], row["locale"])
            if expected is None:
                errors.append(f"{prefix}: undefined policy combination")
            elif row.get("intervention") != expected:
                errors.append(f"{prefix}: actions conflict with v3 policy")
        copy = row.copy()
        copy["dataset_version"] = "v2.1-draft"
        copy["origin_version"] = "v2.1"
        compatible.append(copy)
    return errors + validate_v2(compatible)
