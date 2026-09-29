"""Evaluate structured predictions against candidate labels or approved gold."""

import argparse
from collections import Counter, defaultdict

from schema import INTENTS, TOPICS, TRIAGE, read_jsonl, validate_dataset


def field_report(gold: list[dict], predictions: dict[str, dict], field: str, labels: set[str]) -> dict:
    result = {}
    for label in sorted(labels):
        tp = sum(g[field] == label and predictions[g["id"]][field] == label for g in gold)
        fp = sum(g[field] != label and predictions[g["id"]][field] == label for g in gold)
        fn = sum(g[field] == label and predictions[g["id"]][field] != label for g in gold)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        result[label] = {"support": tp + fn, "tp": tp, "fp": fp, "fn": fn,
                         "precision": precision, "recall": recall, "f1": f1}
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gold")
    parser.add_argument("predictions")
    args = parser.parse_args()
    gold = read_jsonl(args.gold)
    errors = validate_dataset(gold)
    if errors:
        print("Dataset invalid:")
        print("\n".join(errors))
        return 1
    raw_predictions = read_jsonl(args.predictions)
    predictions = {}
    for row in raw_predictions:
        row_id = row.get("id")
        if row_id in predictions:
            print(f"Duplicate prediction id: {row_id}")
            return 1
        predictions[row_id] = row
    gold_ids = {row["id"] for row in gold}
    if set(predictions) != gold_ids:
        print(f"ID mismatch: missing={sorted(gold_ids - set(predictions))}, extra={sorted(set(predictions) - gold_ids)}")
        return 1
    allowed_by_field = {"topic": TOPICS, "intent": INTENTS, "triage": TRIAGE}
    invalid = []
    for row in gold:
        prediction = predictions[row["id"]]
        for field, allowed in allowed_by_field.items():
            if prediction.get(field) not in allowed:
                invalid.append((row["id"], field, prediction.get(field)))
    if invalid:
        print(f"Invalid prediction values: {invalid}")
        return 1
    status_counts = Counter(row["review_status"] for row in gold)
    if status_counts != {"approved": len(gold)}:
        print(f"DRAFT LABEL WARNING: review statuses {dict(status_counts)}; scores below are demonstration only.")
    print(f"N={len(gold)}; semantic groups={len({r['semantic_group_id'] for r in gold})}")
    for field, labels in allowed_by_field.items():
        report = field_report(gold, predictions, field, labels)
        present = [values for values in report.values() if values["support"]]
        macro_f1 = sum(values["f1"] for values in present) / len(present) if present else 0.0
        correct = sum(predictions[row["id"]][field] == row[field] for row in gold)
        print(f"\n{field}: {correct}/{len(gold)} correct; macro F1 over supported labels={macro_f1:.3f}")
        for label, values in report.items():
            if values["support"]:
                print(f"  {label}: P={values['precision']:.3f} R={values['recall']:.3f} F1={values['f1']:.3f} "
                      f"(support={values['support']}, TP={values['tp']}, FP={values['fp']}, FN={values['fn']})")
    support_rows = [row for row in gold if row["intent"] == "SUPPORT_SEEKING"]
    support_review = [row["id"] for row in support_rows if predictions[row["id"]]["triage"] == "REVIEW"]
    harmful_rows = [row for row in gold if row["intent"] == "HARMFUL_INSTRUCTION"]
    harmful_missed = [row["id"] for row in harmful_rows if predictions[row["id"]]["triage"] != "REVIEW"]
    print(f"\nSupport-seeking routed to REVIEW: {len(support_review)}/{len(support_rows)} {support_review}")
    print(f"Harmful-instruction missed by REVIEW: {len(harmful_missed)}/{len(harmful_rows)} {harmful_missed}")
    confusion = defaultdict(Counter)
    for row in gold:
        confusion[row["triage"]][predictions[row["id"]]["triage"]] += 1
    print(f"Triage confusion counts: {dict((k, dict(v)) for k, v in confusion.items())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
