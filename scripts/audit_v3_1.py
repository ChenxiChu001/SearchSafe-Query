"""Profile v3.1 schema, review states, and possible train/test near duplicates."""

from __future__ import annotations

import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from schema_v3_1 import read_jsonl, validate_dataset

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ROOT / "data/splits/v3_1_seed42"
OUT_JSON = ROOT / "evaluation/data_quality_profile_v3_1.json"
OUT_MD = ROOT / "evaluation/data_quality_v3_1.md"


def norm(s: str) -> str:
    return re.sub(r"[\s，。！？、,.!?;；:：‘’“”\"'（）()\-—]", "", s).casefold()


def main() -> None:
    splits = {name: read_jsonl(SPLITS / f"{name}.jsonl") for name in ("train", "dev", "test", "legacy_test")}
    rows = sum(splits.values(), [])
    errors = validate_dataset(rows)
    if errors:
        raise ValueError("\n".join(errors[:30]))
    groups = {name: {r["semantic_group_id"] for r in items} for name, items in splits.items()}
    if any(groups[a] & groups[b] for i, a in enumerate(groups) for b in list(groups)[i+1:]):
        raise ValueError("semantic group leakage")
    # Full cross-split fuzzy scan; it flags wording, not semantic equivalence.
    training = [(r["id"], norm(r["query"])) for r in splits["train"] + splits["dev"]]
    near = []
    for row in splits["test"]:
        q = norm(row["query"])
        best_id, best = None, 0.0
        for old_id, candidate in training:
            if abs(len(q)-len(candidate)) > max(6, len(q)*.45):
                continue
            ratio = SequenceMatcher(None, q, candidate).ratio()
            if ratio > best:
                best_id, best = old_id, ratio
        if best >= .78:
            near.append({"test_id": row["id"], "train_or_dev_id": best_id, "ratio": round(best, 3),
                         "test_query": row["query"]})
    report = {
        "total_rows": len(rows), "semantic_groups": len({r["semantic_group_id"] for r in rows}),
        "splits": {name: {"rows": len(items),
                          "topic": dict(Counter(r["topic"] for r in items)),
                          "intent": dict(Counter(r["intent"] for r in items)),
                          "locale": dict(Counter(r["locale"] for r in items)),
                          "review_status": dict(Counter(r["review_status"] for r in items)),
                          "hard_redirect": sum(r["resource_navigation"] for r in items)}
                   for name, items in splits.items()},
        "cross_split_near_matches_0_78": near,
        "provenance": {
            "generated_candidates_excluded_before_freeze": len(read_jsonl(ROOT / "data/v3_1/removed_low_quality_queries.jsonl")),
            "generated_training_query_edits": len(read_jsonl(ROOT / "data/v3_1/training_query_edits.jsonl")),
            "generated_test_query_edits": len(read_jsonl(ROOT / "data/v3_1/query_edits.jsonl")),
            "near_match_test_query_edits": len(read_jsonl(ROOT / "data/v3_1/near_match_edits.jsonl")),
            "proposed_old_label_or_navigation_revisions": sum(1 for _ in (ROOT / "review/revisions_v3_1.tsv").open()) - 1,
        },
        "schema_errors": errors,
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# v3.1 数据质量剖面\n\n",
             "本页检查冻结候选集的结构、审核状态和跨集合相似措辞；不能证明标签正确或代表真实流量。完整计数和相似匹配见同名 JSON。\n\n",
             f"总行数 {len(rows)}，语义组 {report['semantic_groups']}；结构与固定政策冲突 {len(errors)} 条。\n\n",
             "| 集合 | 行数 | CN/SG | 已审核/草稿 | 硬重定向 |\n",
             "| --- | ---: | ---: | ---: | ---: |\n"]
    for name, item in report["splits"].items():
        lines.append(f"| {name} | {item['rows']} | {item['locale'].get('CN',0)}/{item['locale'].get('SG',0)} | {item['review_status'].get('approved',0)}/{item['review_status'].get('draft',0)} | {item['hard_redirect']} |\n")
    p = report["provenance"]
    lines += ["\n## 生成与修订记录\n\n",
              f"生成初稿中剔除 {p['generated_candidates_excluded_before_freeze']} 条未达标签证据门槛或超出调整后配额的候选，再按配额补齐。冻结前记录 {p['generated_training_query_edits']} 条训练查询改写、{p['generated_test_query_edits']} 条测试查询改写，以及 {p['near_match_test_query_edits']} 条跨集合高相似度改写。旧行有 {p['proposed_old_label_or_navigation_revisions']} 条项目建议修订，逐条见审核清单；这些改写均不构成人工批准。\n\n",
              "## 需人工复核的边界\n\n",
              f"新留出与训练/开发在字符序列相似度 ≥0.78 的候选对有 {len(near)} 组。这只是词面预警，语义近义但措辞不同也可能漏检；应在解释指标前查看 JSON 中的查询对。\n\n",
              "旧行中由项目提出的修订保留 `draft`，新生成行全部为 `draft`。用户对原 v3 的单人接受声明已记录，但没有逐行原始裁决理由；不能把本版全部行称为人工 Gold。新测试未预测前人审时，其分数仍为探索性。\n\n",
              "全部查询均为合成。生成、改写和地区场景配额不等于真实搜索流量分布；后续应使用获准的脱敏查询与结果级样本验证外部泛化。\n"]
    OUT_MD.write_text("".join(lines), encoding="utf-8")
    print(f"rows={len(rows)} near_test_matches={len(near)} report={OUT_MD}")


if __name__ == "__main__":
    main()
