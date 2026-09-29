"""Validation for the v2 hypothetical query-intervention candidate corpus."""

from __future__ import annotations

import json
import re
from pathlib import Path

TOPICS = {"NONE", "SELF_HARM", "EATING_DISORDER_RISK", "VIOLENCE", "SCAM", "POLITICAL_SENSITIVE"}
INTENTS = {"GENERAL_INFO", "PREVENTION", "SUPPORT_SEEKING", "HARMFUL_INSTRUCTION", "AMBIGUOUS", "PRIVATE_INFO_REQUEST"}
ACTION_KEYS = ("allow", "filter", "downrank", "warning", "redirect", "block")
REQUIRED = {
    "id", "query", "language", "locale", "source_type", "semantic_group_id",
    "topic", "intent", "intervention", "redirect_target", "rationale",
    "review_status", "dataset_version", "origin_version",
}


def read_jsonl(path: str | Path) -> list[dict]:
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"line {number}: expected object")
        rows.append(row)
    return rows


def validate_intervention(value: object, redirect_target: object) -> list[str]:
    errors = []
    if not isinstance(value, dict) or set(value) != set(ACTION_KEYS):
        return [f"intervention must contain exactly {ACTION_KEYS}"]
    for key in ACTION_KEYS:
        if type(value[key]) is not bool:
            errors.append(f"intervention.{key} must be boolean")
    if errors:
        return errors
    if value["block"] and any(value[key] for key in ACTION_KEYS if key != "block"):
        errors.append("block=true requires every other action=false")
    if not value["allow"] and not value["redirect"] and not value["block"]:
        errors.append("allow=false requires redirect=true or block=true")
    if not value["allow"] and value["redirect"] and (value["filter"] or value["downrank"]):
        errors.append("hard redirect cannot filter or downrank replaced results")
    if value["redirect"] and (not isinstance(redirect_target, str) or not redirect_target.strip()):
        errors.append("redirect=true requires a non-empty redirect_target")
    if not value["redirect"] and redirect_target is not None:
        errors.append("redirect=false requires redirect_target=null")
    return errors


def validate_dataset(rows: list[dict]) -> list[str]:
    errors = []
    ids = set()
    query_locale = set()
    groups: dict[str, list[dict]] = {}
    for number, row in enumerate(rows, 1):
        prefix = f"row {number} ({row.get('id', '?')})"
        missing, extra = REQUIRED - row.keys(), row.keys() - REQUIRED
        if missing:
            errors.append(f"{prefix}: missing {sorted(missing)}")
        if extra:
            errors.append(f"{prefix}: extra {sorted(extra)}")
        for key in REQUIRED - {"intervention", "redirect_target"}:
            if key in row and (not isinstance(row[key], str) or not row[key].strip()):
                errors.append(f"{prefix}: {key} must be a non-empty string")
        if not re.fullmatch(r"sq_\d{4,}", str(row.get("id", ""))):
            errors.append(f"{prefix}: malformed id")
        if row.get("id") in ids:
            errors.append(f"{prefix}: duplicate id")
        ids.add(row.get("id"))
        for key, allowed in (
            ("topic", TOPICS), ("intent", INTENTS), ("language", {"en", "zh"}),
            ("locale", {"CN", "SG"}), ("source_type", {"synthetic"}),
            ("review_status", {"draft", "approved", "rejected"}),
            ("dataset_version", {"v2-draft", "v2", "v2.1-draft"}),
            ("origin_version", {"v0", "v2", "v2.1"}),
        ):
            if row.get(key) not in allowed:
                errors.append(f"{prefix}: unsupported {key}={row.get(key)!r}")
        errors.extend(f"{prefix}: {e}" for e in validate_intervention(row.get("intervention"), row.get("redirect_target")))
        if row.get("topic") == "NONE" and row.get("intent") != "GENERAL_INFO":
            errors.append(f"{prefix}: NONE currently requires GENERAL_INFO")
        if row.get("intent") == "PRIVATE_INFO_REQUEST" and row.get("topic") != "POLITICAL_SENSITIVE":
            errors.append(f"{prefix}: PRIVATE_INFO_REQUEST is only sampled in political topic")
        if row.get("topic") == "POLITICAL_SENSITIVE" and row.get("locale") not in {"CN", "SG"}:
            errors.append(f"{prefix}: political sample needs a locale")
        key = (" ".join(str(row.get("query", "")).casefold().split()), row.get("locale"))
        if key in query_locale:
            errors.append(f"{prefix}: duplicate query in locale")
        query_locale.add(key)
        groups.setdefault(str(row.get("semantic_group_id")), []).append(row)
    for group_id, members in groups.items():
        if len({(m.get("topic"), m.get("intent")) for m in members}) != 1:
            errors.append(f"group {group_id}: inconsistent topic or intent")
        if len({(m.get("language"), m.get("locale")) for m in members}) != len(members):
            errors.append(f"group {group_id}: repeated language-locale pair")
        for locale in {m.get("locale") for m in members}:
            local = [m for m in members if m.get("locale") == locale]
            if len({json.dumps(m.get("intervention"), sort_keys=True) for m in local}) != 1:
                errors.append(f"group {group_id} ({locale}): translated queries have different actions")
    return errors
