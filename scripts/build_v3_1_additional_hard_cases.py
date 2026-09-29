"""Build the supplemental hard-case TSV without touching prior review decisions."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "review/v3_1_additional_hard_cases.tsv"

CASES = [
    ("sq_1231", "主题边界", "交通新规是否属于政治主题？"),
    ("sq_1237", "主题边界", "一般心理问题有无饮食失调线索？"),
    ("sq_1332", "意图边界", "仅描述正在发生的风险，是否足以判求助？"),
    ("sq_1374", "风险边界", "陌生号码的天气短信是否足以判诈骗？"),
    ("sq_1406", "硬重定向", "明确查支持电话时，是否应完全替换结果？"),
    ("sq_1407", "硬重定向", "明确查举报渠道时，是否应完全替换结果？"),
    ("sq_1502", "硬重定向", "举报隐私泄露的入口查询是否应硬转？"),
    ("sq_0991", "意图边界", "问节食后果，是一般信息还是事前预防？"),
    ("sq_1042", "Block 与无效输出", "公开信息限定是否改变住址隐私边界？"),
    ("sq_1065", "旧标签争议", "事后止损为何被旧标签判为有害指导？"),
    ("sq_1088", "主题边界", "异常体验是否足以推断自伤主题？"),
    ("sq_1159", "多主题优先级", "霸凌与自残并存时，主 Topic 按哪种需求选？"),
]


def read(path: str) -> dict[str, dict]:
    return {row["id"]: row for row in map(json.loads, (ROOT / path).open(encoding="utf-8"))}


def compact_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite review decisions: {OUTPUT}")

    new = read("data/splits/v3_1_seed42/test.jsonl")
    old = read("data/splits/v3_seed42/test.jsonl")
    proposed_old = read("data/splits/v3_1_seed42/legacy_test.jsonl")
    new_predictions = read("evaluation/v3_1_v31_direct_predictions.jsonl")
    old_predictions = read("evaluation/v3_1_on_v3_test_v31_predictions.jsonl")
    new_raw = read("evaluation/v3_1_v31_direct_raw.jsonl")
    old_raw = read("evaluation/v3_1_on_v3_test_v31_raw.jsonl")

    fields = [
        "id", "case_type", "source_split", "locale", "query", "expected_review_status",
        "expected_topic", "expected_intent", "expected_intervention_json", "expected_resource_navigation",
        "model_topic", "model_intent", "model_intervention_json", "parse_error", "model_raw_json",
        "project_proposed_topic", "project_proposed_intent", "project_proposed_intervention_json",
        "audit_question", "review_decision", "corrected_topic", "corrected_intent",
        "corrected_intervention_json", "reviewer_rationale",
    ]
    rows = []
    for ident, case_type, question in CASES:
        is_new = ident in new
        gold = (new if is_new else old)[ident]
        prediction = (new_predictions if is_new else old_predictions).get(ident)
        raw = (new_raw if is_new else old_raw)[ident]
        if ("prediction" in raw) != (prediction is not None):
            raise ValueError(f"Parsed/raw discrepancy: {ident}")
        proposal = None if is_new else proposed_old[ident]
        changed = proposal is not None and any(
            proposal[key] != gold[key] for key in ("topic", "intent", "intervention")
        )
        rows.append({
            "id": ident, "case_type": case_type,
            "source_split": "v3_1_new_test" if is_new else "v3_old_test",
            "locale": gold["locale"], "query": gold["query"],
            "expected_review_status": gold["review_status"],
            "expected_topic": gold["topic"], "expected_intent": gold["intent"],
            "expected_intervention_json": compact_json(gold["intervention"]),
            "expected_resource_navigation": gold.get("resource_navigation", ""),
            "model_topic": prediction["topic"] if prediction else "",
            "model_intent": prediction["intent"] if prediction else "",
            "model_intervention_json": compact_json(prediction["intervention"]) if prediction else "",
            "parse_error": raw.get("error", ""), "model_raw_json": raw["content"].replace("\n", " "),
            "project_proposed_topic": proposal["topic"] if changed else "",
            "project_proposed_intent": proposal["intent"] if changed else "",
            "project_proposed_intervention_json": compact_json(proposal["intervention"]) if changed else "",
            "audit_question": question, "review_decision": "", "corrected_topic": "",
            "corrected_intent": "", "corrected_intervention_json": "", "reviewer_rationale": "",
        })

    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} cases to {OUTPUT}")


if __name__ == "__main__":
    main()
