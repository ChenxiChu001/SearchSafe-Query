"""Compare direct QLoRA adapters on the frozen v3 200-query test set."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from compare_training_v3 import load_run, metrics, paired_interval
from schema_v3 import read_jsonl, validate_dataset

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "data/splits/v3_seed42/test.jsonl"
REVISED = ROOT / "data/splits/v3_1_seed42/legacy_test.jsonl"
MANIFEST = ROOT / "data/splits/v3_seed42/manifest.json"
OUT_JSON = ROOT / "evaluation/v3_1_on_v3_test_comparison.json"
OUT_MD = ROOT / "evaluation/v3_1_on_v3_test_comparison.md"
RUN_FILES = {
    "v3_original_prompt": "v3_v3_direct",
    "v3_same_prompt": "v3_1_on_v3_test_v3",
    "v31_same_prompt": "v3_1_on_v3_test_v31",
}


def f3(values: dict) -> str:
    return "/".join(f"{values[k]:.3f}" for k in ("precision", "recall", "f1"))


def main() -> None:
    if OUT_JSON.exists() or OUT_MD.exists():
        raise FileExistsError("comparison output already exists")
    old = read_jsonl(OLD)
    revised = read_jsonl(REVISED)
    errors = validate_dataset(old)
    if errors:
        raise ValueError("\n".join(errors[:20]))
    expected_sha = json.loads(MANIFEST.read_text(encoding="utf-8"))["splits"]["test"]["sha256"]
    actual_sha = hashlib.sha256(OLD.read_bytes()).hexdigest()
    if len(old) != 200 or actual_sha != expected_sha:
        raise ValueError("original v3 test split changed")
    old_by_id = {r["id"]: r for r in old}
    revised_by_id = {r["id"]: r for r in revised}
    if set(old_by_id) != set(revised_by_id) or any(
        (old_by_id[k]["query"], old_by_id[k]["locale"])
        != (revised_by_id[k]["query"], revised_by_id[k]["locale"])
        for k in old_by_id
    ):
        raise ValueError("post-hoc legacy copy changed test inputs")
    revised = [revised_by_id[r["id"]] for r in old]
    runs = {}
    for name, stem in RUN_FILES.items():
        predictions, meta = load_run(
            ROOT / f"evaluation/{stem}_predictions.jsonl",
            ROOT / f"evaluation/{stem}_raw.jsonl",
            old,
            "direct",
        )
        runs[name] = {
            "predictions": predictions,
            "meta": meta,
            "original_metrics": metrics(old, predictions, "direct"),
            "revised_metrics": metrics(revised, predictions, "direct"),
        }
    if runs["v3_same_prompt"]["meta"]["prompt_sha256"] != runs["v31_same_prompt"]["meta"]["prompt_sha256"]:
        raise ValueError("same-prompt runs used different prompts")
    before = runs["v3_same_prompt"]["predictions"]
    after = runs["v31_same_prompt"]["predictions"]
    comparisons = {}
    for label, rows in (("original", old), ("posthoc_revised", revised)):
        comparisons[label] = {
            "action_exact_delta_pp": 100 * (
                sum(after.get(r["id"], {}).get("intervention") == r["intervention"] for r in rows)
                - sum(before.get(r["id"], {}).get("intervention") == r["intervention"] for r in rows)
            ) / len(rows),
            "paired_bootstrap_95_pp": [100 * x for x in paired_interval(rows, before, after)],
            "fixed": sum(
                before.get(r["id"], {}).get("intervention") != r["intervention"]
                and after.get(r["id"], {}).get("intervention") == r["intervention"] for r in rows
            ),
            "regressed": sum(
                before.get(r["id"], {}).get("intervention") == r["intervention"]
                and after.get(r["id"], {}).get("intervention") != r["intervention"] for r in rows
            ),
        }
    data = {
        "original_test_sha256": actual_sha,
        "revised_test_sha256": hashlib.sha256(REVISED.read_bytes()).hexdigest(),
        "rows": len(old),
        "original_test_draft": sum(r["review_status"] == "draft" for r in old),
        "posthoc_revisions": {
            key: sum(old_by_id[k][key] != revised_by_id[k][key] for k in old_by_id)
            for key in ("topic", "intent", "intervention")
        },
        "runs": {},
        "comparisons": comparisons,
    }
    for name, run in runs.items():
        data["runs"][name] = {
            "meta": run["meta"],
            "original_metrics": run["original_metrics"],
            "revised_metrics": run["revised_metrics"],
            "original_errors": [
                {
                    "id": r["id"], "query": r["query"], "locale": r["locale"],
                    "gold_topic": r["topic"], "gold_intent": r["intent"],
                    "gold_intervention": r["intervention"],
                    "prediction": run["predictions"].get(r["id"]),
                }
                for r in old if run["predictions"].get(r["id"], {}).get("intervention") != r["intervention"]
            ],
        }
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v3.1 适配器在旧 v3 的 200 题上：探索性复测\n\n",
        "使用冻结的原 v3 测试查询及**原标签**计主分。200 条原标签均为 `draft`，旧题和预测已被分析过；这是历史诊断，非新盲测。另列 v3.1 项目建议修订标签的敏感性分析，但该修订发生在查看旧预测后，不当作 Gold。\n\n",
        "## 原标签结果\n\n",
        "| 适配器 / Prompt | 可解析 | Topic Macro F1 | Intent Macro F1 | PREVENTION P/R/F1 | 六动作整组 | 有害指导漏过滤 | 误 Block | Block 漏判 |\n",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n",
    ]
    display = {
        "v3_original_prompt": "v3 / 原 v3 Prompt（历史）",
        "v3_same_prompt": "v3 / v3.1 Prompt",
        "v31_same_prompt": "v3.1 / v3.1 Prompt",
    }
    for name, run in runs.items():
        m = run["original_metrics"]
        lines.append(
            f"| {display[name]} | {m['parsed']}/200 | {m['topic_macro']['f1']:.3f} | "
            f"{m['intent_macro']['f1']:.3f} | {f3(m['intent']['PREVENTION'])} | "
            f"{m['action_exact']}/200 | {m['harmful_filter_miss']}/{m['harmful_n']} | "
            f"{m['false_block']} | {m['private_block_miss']}/{m['private_n']} |\n"
        )
    c = comparisons["original"]
    lines += [
        f"\n**同 Prompt 的 v3 → v3.1：**六动作整组 {c['action_exact_delta_pp']:+.1f} 个百分点；同题修正 {c['fixed']}、退步 {c['regressed']}；配对 bootstrap 95% 区间 [{c['paired_bootstrap_95_pp'][0]:+.1f}, {c['paired_bootstrap_95_pp'][1]:+.1f}] 个百分点。区间只涉及这批合成题的抽样变化，不包括标签不确定性。\n\n",
        "## 意图逐类：原标签 P/R/F1\n\n",
        "| Intent | 支持数 | v3 原 Prompt | v3 同 Prompt | v3.1 同 Prompt |\n",
        "| --- | ---: | ---: | ---: | ---: |\n",
    ]
    for label in sorted(runs["v3_same_prompt"]["original_metrics"]["intent"]):
        support = runs["v3_same_prompt"]["original_metrics"]["intent"][label]["support"]
        lines.append(f"| {label} | {support} | " + " | ".join(
            f3(runs[name]["original_metrics"]["intent"][label]) for name in RUN_FILES
        ) + " |\n")
    for field, title in (("topic", "Topic"), ("action", "六动作正类")):
        lines += [
            f"\n## {title} 逐类：原标签 P/R/F1\n\n",
            "| 类别 | 支持数 | v3 原 Prompt | v3 同 Prompt | v3.1 同 Prompt |\n",
            "| --- | ---: | ---: | ---: | ---: |\n",
        ]
        for label in sorted(runs["v3_same_prompt"]["original_metrics"][field]):
            support = runs["v3_same_prompt"]["original_metrics"][field][label]["support"]
            lines.append(f"| {label} | {support} | " + " | ".join(
                f3(runs[name]["original_metrics"][field][label]) for name in RUN_FILES
            ) + " |\n")
    lines += [
        "\n## 地区切片：原标签六动作整组\n\n",
        "| 地区 | 题数 | v3 原 Prompt | v3 同 Prompt | v3.1 同 Prompt |\n",
        "| --- | ---: | ---: | ---: | ---: |\n",
    ]
    for locale in ("CN", "SG"):
        n = runs["v3_same_prompt"]["original_metrics"]["by_locale"][locale]["n"]
        lines.append(f"| {locale} | {n} | " + " | ".join(
            str(runs[name]["original_metrics"]["by_locale"][locale]["action_exact"])
            for name in RUN_FILES
        ) + " |\n")
    lines += [
        "\n## 项目建议修订标签：事后敏感性分析\n\n",
        f"同一 200 条查询中，项目曾建议改动 Topic {data['posthoc_revisions']['topic']} 条、Intent {data['posthoc_revisions']['intent']} 条、六动作 {data['posthoc_revisions']['intervention']} 条。修订尚非预测前独立裁决，下表只显示结论对标签版本的敏感程度。\n\n",
        "| 适配器 / v3.1 Prompt | Topic Macro F1 | Intent Macro F1 | PREVENTION P/R/F1 | 六动作整组 |\n",
        "| --- | ---: | ---: | ---: | ---: |\n",
    ]
    for name in ("v3_same_prompt", "v31_same_prompt"):
        m = runs[name]["revised_metrics"]
        lines.append(
            f"| {display[name]} | {m['topic_macro']['f1']:.3f} | {m['intent_macro']['f1']:.3f} | "
            f"{f3(m['intent']['PREVENTION'])} | {m['action_exact']}/200 |\n"
        )
    lines += [
        "\n## 解释边界\n\n",
        "- 两条同 Prompt 运行用同一批冻结查询、同一 v3.1 Prompt；只有适配器不同。这是当前最可比的模型对照。原 v3 Prompt 的历史分数单列，不与新 Prompt 的分数直接归因。\n",
        "- v3.1 新政策加入硬重定向，而旧题的六动作标签按原政策制定；若新模型给出硬转，原标签会算错。逐题原始输出、解析失败和动作错例保存在 JSON 与 raw 文件。\n",
        "- 原测试题已被查看，且 200 条均为合成草稿；结果不能替代新题盲审或真实流量评估。\n",
    ]
    OUT_MD.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
