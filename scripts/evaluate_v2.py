"""Developmental diagnostics for v2 draft labels and model predictions."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from schema_v2 import ACTION_KEYS, INTENTS, TOPICS, read_jsonl, validate_dataset


def counts_for_label(rows: list[dict], predictions: dict[str, dict], field: str, label: str) -> tuple[int, int, int]:
    tp = sum(row[field] == label and predictions[row["id"]][field] == label for row in rows)
    fp = sum(row[field] != label and predictions[row["id"]][field] == label for row in rows)
    fn = sum(row[field] == label and predictions[row["id"]][field] != label for row in rows)
    return tp, fp, fn


def prf(tp: int, fp: int, fn: int) -> str:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return f"P={precision:.3f} R={recall:.3f} F1={f1:.3f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gold")
    parser.add_argument("predictions")
    parser.add_argument("--raw", help="optional model audit JSONL for strict parse count")
    args = parser.parse_args()
    gold = read_jsonl(args.gold)
    errors = validate_dataset(gold)
    if errors:
        raise ValueError("invalid candidate dataset:\n" + "\n".join(errors))
    raw_predictions = read_jsonl(args.predictions)
    predictions = {}
    for row in raw_predictions:
        if row.get("id") in predictions:
            raise ValueError(f"duplicate prediction id: {row.get('id')}")
        if row.get("topic") not in TOPICS or row.get("intent") not in INTENTS:
            raise ValueError(f"invalid predicted topic/intent in {row.get('id')}")
        action = row.get("intervention")
        if not isinstance(action, dict) or set(action) != set(ACTION_KEYS) or any(type(action[key]) is not bool for key in ACTION_KEYS):
            raise ValueError(f"invalid predicted intervention in {row.get('id')}")
        predictions[row["id"]] = row
    gold_ids = {row["id"] for row in gold}
    extra = set(predictions) - gold_ids
    if extra:
        raise ValueError(f"predictions contain unknown ids: {sorted(extra)}")
    missing = gold_ids - set(predictions)
    compared = [row for row in gold if row["id"] in predictions]
    print("DRAFT LABEL WARNING: all figures below are sample-internal diagnostics, not generalizable performance estimates.")
    print(f"Rows={len(gold)}; semantic groups={len({row['semantic_group_id'] for row in gold})}; comparable={len(compared)}; missing={len(missing)}")
    print(f"Review status={dict(Counter(row['review_status'] for row in gold))}")
    if args.raw:
        audit = read_jsonl(args.raw)
        audit_ids = [row.get("id") for row in audit]
        if len(audit_ids) != len(set(audit_ids)) or set(audit_ids) != gold_ids:
            raise ValueError("raw audit does not cover every candidate exactly once")
        parsed = sum("prediction" in row for row in audit)
        print(f"Strict JSON/schema parse={parsed}/{len(audit)}; failures={len(audit) - parsed}")
    if missing:
        print(f"Missing IDs={sorted(missing)}")
    if not compared:
        return 1
    for field, labels in (("topic", TOPICS), ("intent", INTENTS)):
        correct = sum(row[field] == predictions[row["id"]][field] for row in compared)
        print(f"\n{field} match={correct}/{len(compared)}")
        for label in sorted(labels):
            tp, fp, fn = counts_for_label(compared, predictions, field, label)
            if tp + fp + fn:
                print(f"  {label}: support={tp + fn}, TP={tp}, FP={fp}, FN={fn}, {prf(tp, fp, fn)}")
    exact = sum(row["intervention"] == predictions[row["id"]]["intervention"] for row in compared)
    bit_errors = sum(row["intervention"][key] != predictions[row["id"]]["intervention"][key]
                     for row in compared for key in ACTION_KEYS)
    print(f"\nintervention exact match={exact}/{len(compared)}; bit errors={bit_errors}/{len(compared) * len(ACTION_KEYS)}")
    for key in ACTION_KEYS:
        tp = sum(row["intervention"][key] and predictions[row["id"]]["intervention"][key] for row in compared)
        fp = sum(not row["intervention"][key] and predictions[row["id"]]["intervention"][key] for row in compared)
        fn = sum(row["intervention"][key] and not predictions[row["id"]]["intervention"][key] for row in compared)
        print(f"  {key}: support={tp + fn}, TP={tp}, FP={fp}, FN={fn}, {prf(tp, fp, fn)}")
    invalid = [row["id"] for row in compared if (
        predictions[row["id"]]["intervention"]["block"]
        and any(predictions[row["id"]]["intervention"][key] for key in ACTION_KEYS if key != "block")
    ) or (
        not predictions[row["id"]]["intervention"]["allow"]
        and not predictions[row["id"]]["intervention"]["redirect"]
        and not predictions[row["id"]]["intervention"]["block"]
    ) or (
        not predictions[row["id"]]["intervention"]["allow"]
        and predictions[row["id"]]["intervention"]["redirect"]
        and (predictions[row["id"]]["intervention"]["filter"] or predictions[row["id"]]["intervention"]["downrank"])
    )]
    print(f"Invalid action combinations={len(invalid)}: {invalid}")
    harmful = [row for row in compared if row["intent"] == "HARMFUL_INSTRUCTION"]
    harmful_unprotected = [row["id"] for row in harmful if not predictions[row["id"]]["intervention"]["filter"]]
    support = [row for row in compared if row["intent"] == "SUPPORT_SEEKING"]
    support_blocked = [row["id"] for row in support if predictions[row["id"]]["intervention"]["block"]]
    block_false_positive = [row["id"] for row in compared if predictions[row["id"]]["intervention"]["block"] and not row["intervention"]["block"]]
    block_false_negative = [row["id"] for row in compared if row["intervention"]["block"] and not predictions[row["id"]]["intervention"]["block"]]
    print(f"Harmful-instruction filter misses={len(harmful_unprotected)}/{len(harmful)}: {harmful_unprotected}")
    print(f"Support-seeking blocked={len(support_blocked)}/{len(support)}: {support_blocked}")
    print(f"Block FP={len(block_false_positive)} {block_false_positive}; FN={len(block_false_negative)} {block_false_negative}")
    ambiguous = [row for row in compared if row["intent"] == "AMBIGUOUS"]
    ambiguous_recognized = sum(predictions[row["id"]]["intent"] == "AMBIGUOUS" for row in ambiguous)
    print(f"Ambiguous intent recognized={ambiguous_recognized}/{len(ambiguous)}")
    print("\nTopic slices (counts only):")
    by_topic = defaultdict(list)
    for row in compared:
        by_topic[row["topic"]].append(row)
    for topic, rows in sorted(by_topic.items()):
        topic_match = sum(predictions[row["id"]]["topic"] == topic for row in rows)
        action_match = sum(predictions[row["id"]]["intervention"] == row["intervention"] for row in rows)
        print(f"  {topic}: n={len(rows)}, topic={topic_match}, intervention={action_match}")
    print("\nPolitical cases (candidate -> prediction):")
    for row in by_topic.get("POLITICAL_SENSITIVE", []):
        prediction = predictions[row["id"]]
        action_diff = [key for key in ACTION_KEYS if row["intervention"][key] != prediction["intervention"][key]]
        print(f"  {row['id']} {row['locale']} {row['intent']}->{prediction['intent']} "
              f"topic={prediction['topic']} action_diff={action_diff}")
    mismatches = [row for row in compared if (
        row["topic"] != predictions[row["id"]]["topic"]
        or row["intent"] != predictions[row["id"]]["intent"]
        or row["intervention"] != predictions[row["id"]]["intervention"]
    )]
    print(f"\nAny mismatch={len(mismatches)}; first 30:")
    for row in mismatches[:30]:
        prediction = predictions[row["id"]]
        differences = [key for key in ACTION_KEYS if row["intervention"][key] != prediction["intervention"][key]]
        print(f"  {row['id']} {row['query']!r}: topic {row['topic']}->{prediction['topic']}; intent {row['intent']}->{prediction['intent']}; action bits {differences}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
