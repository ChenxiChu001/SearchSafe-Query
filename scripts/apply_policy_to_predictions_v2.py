"""Derive v2 action bits from model topic/intent predictions and the explicit policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_v2_candidates import intervention
from schema_v2 import INTENTS, TOPICS, read_jsonl

RISK_TOPICS = {"SELF_HARM", "EATING_DISORDER_RISK", "VIOLENCE", "SCAM"}


def covered(topic: str, intent: str) -> bool:
    if intent == "PRIVATE_INFO_REQUEST":
        return True
    if topic == "NONE":
        return intent == "GENERAL_INFO"
    if topic in RISK_TOPICS:
        return intent in INTENTS - {"PRIVATE_INFO_REQUEST"}
    if topic == "POLITICAL_SENSITIVE":
        return intent in {"GENERAL_INFO", "PREVENTION", "SUPPORT_SEEKING"}
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("predictions")
    parser.add_argument("output")
    args = parser.parse_args()
    gold = {row["id"]: row for row in read_jsonl(args.data)}
    model = read_jsonl(args.predictions)
    output = Path(args.output)
    if output.exists():
        parser.error("output exists; choose a new path")
    rows = []
    unsupported = []
    for prediction in model:
        row_id = prediction["id"]
        if row_id not in gold:
            raise ValueError(f"unknown id {row_id}")
        topic, intent = prediction["topic"], prediction["intent"]
        if topic not in TOPICS or intent not in INTENTS:
            raise ValueError(f"unknown predicted label for {row_id}")
        if not covered(topic, intent):
            unsupported.append((row_id, topic, intent))
            continue
        action, _ = intervention(topic, intent, gold[row_id]["locale"])
        rows.append({"id": row_id, "topic": topic, "intent": intent, "intervention": action})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(f"Policy coverage={len(rows)}/{len(model)} parseable model predictions; unsupported={unsupported}")
    print("This baseline executes the same fixed rules used to draft the candidate action labels; compare it only as rule-execution diagnostics.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
