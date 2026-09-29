"""Canonical query record schema and consistency checks."""

from __future__ import annotations

import json
import re
from pathlib import Path

TOPICS = {"NONE", "SELF_HARM", "EATING_DISORDER_RISK", "VIOLENCE", "SCAM"}
INTENTS = {
    "GENERAL_INFO",
    "PREVENTION",
    "SUPPORT_SEEKING",
    "HARMFUL_INSTRUCTION",
    "AMBIGUOUS",
}
TRIAGE = {"ALLOW", "SUPPORT", "REVIEW"}
SOURCE_TYPES = {"human_authored", "synthetic", "public_dataset", "adversarial", "paraphrase"}
REVIEW_STATUSES = {"draft", "approved", "rejected"}
REQUIRED = {
    "id", "query", "language", "locale", "source_type", "semantic_group_id",
    "topic", "intent", "triage", "rationale", "review_status", "dataset_version",
}
TRIAGE_FOR_INTENT = {
    "GENERAL_INFO": "ALLOW",
    "PREVENTION": "ALLOW",
    "SUPPORT_SEEKING": "SUPPORT",
    "HARMFUL_INSTRUCTION": "REVIEW",
    "AMBIGUOUS": "REVIEW",
}


def read_jsonl(path: str | Path) -> list[dict]:
    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_number}: invalid JSON: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"line {line_number}: expected JSON object")
            records.append(record)
    return records


def validate_record(record: dict) -> list[str]:
    errors = []
    missing = REQUIRED - record.keys()
    extra = record.keys() - REQUIRED
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    if extra:
        errors.append(f"unknown fields: {sorted(extra)}")
    for field in ("id", "query", "language", "locale", "source_type", "semantic_group_id",
                  "topic", "intent", "triage", "rationale", "review_status", "dataset_version"):
        if field in record and (not isinstance(record[field], str) or not record[field].strip()):
            errors.append(f"{field}: must be a non-empty string")
    if "id" in record and isinstance(record["id"], str) and not re.fullmatch(r"sq_\d{4,}", record["id"]):
        errors.append("id: expected sq_ followed by at least four digits")
    if record.get("language") not in {"en", "zh"}:
        errors.append("language: expected en or zh")
    for field, allowed in (("topic", TOPICS), ("intent", INTENTS), ("triage", TRIAGE),
                           ("source_type", SOURCE_TYPES), ("review_status", REVIEW_STATUSES)):
        if record.get(field) not in allowed:
            errors.append(f"{field}: unsupported value {record.get(field)!r}")
    intent = record.get("intent")
    if intent in TRIAGE_FOR_INTENT and record.get("triage") != TRIAGE_FOR_INTENT[intent]:
        errors.append(f"triage: {intent} must map to {TRIAGE_FOR_INTENT[intent]}")
    if record.get("topic") == "NONE" and intent in INTENTS and intent != "GENERAL_INFO":
        errors.append("topic: NONE currently requires GENERAL_INFO")
    return errors


def validate_dataset(records: list[dict]) -> list[str]:
    errors = []
    ids = set()
    queries = set()
    groups: dict[str, list[dict]] = {}
    for index, record in enumerate(records, 1):
        prefix = f"record {index} ({record.get('id', '?')})"
        errors.extend(f"{prefix}: {error}" for error in validate_record(record))
        record_id = record.get("id")
        if record_id in ids:
            errors.append(f"{prefix}: duplicate id")
        ids.add(record_id)
        query = record.get("query")
        if isinstance(query, str):
            normalized = " ".join(query.casefold().split())
            if normalized in queries:
                errors.append(f"{prefix}: duplicate normalized query")
            queries.add(normalized)
        group_id = record.get("semantic_group_id")
        if isinstance(group_id, str):
            groups.setdefault(group_id, []).append(record)
    for group_id, members in groups.items():
        labels = {(m.get("topic"), m.get("intent"), m.get("triage")) for m in members}
        if len(labels) != 1:
            errors.append(f"semantic group {group_id}: inconsistent labels")
        languages = [m.get("language") for m in members]
        if len(languages) != len(set(languages)):
            errors.append(f"semantic group {group_id}: duplicate language")
    return errors
