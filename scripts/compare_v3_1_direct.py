"""Direct-output-only v3.1 comparison after the user deferred labels training."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from compare_training_v3_1 import f3, load_run, paired_interval, score
from schema_v3_1 import read_jsonl, validate_dataset

RUNS = ("base_direct", "v3_direct", "v31_direct")
NAMES = {"base_direct": "基础模型", "v3_direct": "v3 QLoRA", "v31_direct": "v3.1 QLoRA"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("test_data")
    parser.add_argument("split_manifest")
    parser.add_argument("run_manifest")
    parser.add_argument("output_json")
    parser.add_argument("output_markdown")
    args = parser.parse_args()
    output_json, output_md = Path(args.output_json), Path(args.output_markdown)
    if output_json.exists() or output_md.exists():
        parser.error("output already exists")
    test_path = Path(args.test_data)
    rows = read_jsonl(test_path)
    errors = validate_dataset(rows)
    if errors:
        raise ValueError("\n".join(errors[:20]))
    test_sha = hashlib.sha256(test_path.read_bytes()).hexdigest()
    frozen = json.loads(Path(args.split_manifest).read_text(encoding="utf-8"))
    if test_sha != frozen["splits"]["test"]["sha256"]:
        raise ValueError("test data differ from frozen manifest")
    run_paths = json.loads(Path(args.run_manifest).read_text(encoding="utf-8"))
    if set(run_paths) != set(RUNS):
        raise ValueError("expected three direct runs")
    runs = {}
    for key in RUNS:
        pred, meta = load_run(run_paths[key], rows, "direct")
        runs[key] = {"predictions": pred, "meta": meta, "metrics": score(rows, pred, "direct")}
    if len({runs[key]["meta"]["prompt_sha256"] for key in RUNS}) != 1:
        raise ValueError("direct runs used different prompts")
    comparison = {}
    for key in ("base_direct", "v3_direct"):
        before, after = runs[key], runs["v31_direct"]
        bm, am = before["metrics"], after["metrics"]
        comparison[f"{key}_to_v31"] = {
            "topic_macro_f1_delta_pp": 100*(am["topic_macro"]["f1"]-bm["topic_macro"]["f1"]),
            "intent_macro_f1_delta_pp": 100*(am["intent_macro"]["f1"]-bm["intent_macro"]["f1"]),
            "action_exact_delta_pp": 100*(am["action_exact_rate"]-bm["action_exact_rate"]),
            "action_delta_bootstrap_95_pp": paired_interval(rows, before["predictions"], after["predictions"]),
            "fixed": sum(before["predictions"].get(r["id"], {}).get("intervention") != r["intervention"]
                         and after["predictions"].get(r["id"], {}).get("intervention") == r["intervention"] for r in rows),
            "regressed": sum(before["predictions"].get(r["id"], {}).get("intervention") == r["intervention"]
                             and after["predictions"].get(r["id"], {}).get("intervention") != r["intervention"] for r in rows),
        }
    data = {"test_sha256": test_sha, "test_rows": len(rows), "test_draft_rows": sum(r["review_status"] == "draft" for r in rows),
            "run_order": list(RUNS), "runs": {}, "comparison": comparison}
    for key in RUNS:
        run = runs[key]
        data["runs"][key] = {"meta": run["meta"], "metrics": run["metrics"],
                             "errors": [{"id": r["id"], "query": r["query"], "locale": r["locale"],
                                         "gold_topic": r["topic"], "gold_intent": r["intent"],
                                         "gold_intervention": r["intervention"],
                                         "predicted": run["predictions"].get(r["id"])}
                                        for r in rows if run["predictions"].get(r["id"], {}).get("intervention") != r["intervention"]]}
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# v3.1 Qwen3.5 9B QLoRA：直接输出路线探索性比较\n\n",
             f"同一批新生成的 {len(rows)} 条中文合成留出题，{data['test_draft_rows']} 条仍为 `draft`。用户因时间约束暂缓标签→规则路线，本报告只比较基础模型、v3 和 v3.1 的直接输出。三者使用同一个 v3.1 Prompt；旧 v3 的 200 条已见过测试题仅供历史诊断。分数是内部一致性诊断，不是盲审 Gold 或真实平台效果。\n\n",
             "## 总览\n\n", "| 模型 | 解析 | Topic Macro P/R/F1 | Intent Macro P/R/F1 | 六动作整组 | 有害请求漏过滤 | 求助误 Block | 误 Block | Block 漏判 | 硬转 TP/FP/FN |\n",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n"]
    for key in RUNS:
        m = runs[key]["metrics"]
        nav = m["resource_navigation"]
        lines.append(f"| {NAMES[key]} | {m['parsed']}/{m['n']} | {f3(m['topic_macro'])} | {f3(m['intent_macro'])} | {m['action_exact']}/{m['n']} ({m['action_exact_rate']:.1%}) | {m['harmful_filter_miss']}/{m['harmful_n']} | {m['support_blocked']} | {m['false_block']} | {m['block_miss']}/{m['block_n']} | {nav['tp']}/{nav['fp']}/{nav['fn']} |\n")
    lines += ["\n## 同题变化\n\n", "| 对比 | Topic Macro F1 | Intent Macro F1 | 六动作整组 | 同题修正/退步 | 动作差值配对 bootstrap 95% 区间 |\n", "| --- | ---: | ---: | ---: | ---: | ---: |\n"]
    for key in ("base_direct", "v3_direct"):
        c = comparison[f"{key}_to_v31"]
        lines.append(f"| {NAMES[key]} → v3.1 | {c['topic_macro_f1_delta_pp']:+.1f} pp | {c['intent_macro_f1_delta_pp']:+.1f} pp | {c['action_exact_delta_pp']:+.1f} pp | {c['fixed']}/{c['regressed']} | [{c['action_delta_bootstrap_95_pp'][0]:+.1f}, {c['action_delta_bootstrap_95_pp'][1]:+.1f}] pp |\n")
    for field, title in (("topic", "Topic"), ("intent", "Intent"), ("action", "六动作正类")):
        lines += [f"\n## {title} 逐类 Precision / Recall / F1\n\n", "| 类别 | 支持数 | 基础模型 | v3 | v3.1 |\n", "| --- | ---: | ---: | ---: | ---: |\n"]
        for label in sorted(runs["base_direct"]["metrics"][field]):
            support = runs["base_direct"]["metrics"][field][label]["support"]
            lines.append(f"| {label} | {support} | " + " | ".join(f3(runs[key]["metrics"][field][label]) for key in RUNS) + " |\n")
    lines += ["\n## 地区切片的六动作整组\n\n", "| 地区 | n | 基础模型 | v3 | v3.1 |\n", "| --- | ---: | ---: | ---: | ---: |\n"]
    for locale in ("CN", "SG"):
        n = runs["base_direct"]["metrics"]["by_locale"][locale]["n"]
        lines.append(f"| {locale} | {n} | " + " | ".join(f"{runs[key]['metrics']['by_locale'][locale]['action_exact']}/{n}" for key in RUNS) + " |\n")
    lines += ["\n## 解释边界\n\n",
              "- 所有新测试标签目前为草稿；很小的 Block 和硬转支持数只可作为压力测试。JSON 保留逐类 TP/FP/FN 与全部六动作错例。\n",
              "- 同一 Qwen 基座辅助生成训练与测试查询，即使作了词面近似筛查，仍可能共享写题风格。只有独立人审和真实脱敏查询才能验证外部泛化。\n",
              "- v3.1 同时改了旧标签边界、增加数据、加入硬转并更新 Prompt；同题差异不能归因于某一改动。标签→规则路线本轮未训练，不填推测数字。\n"]
    output_md.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {output_json} and {output_md}")


if __name__ == "__main__":
    main()
