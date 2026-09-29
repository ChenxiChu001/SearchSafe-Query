"""Exploratory same-test comparison of base, v2.1, and v3 QLoRA runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from policy_v3 import action_for, covered
from schema_v3 import ACTION_KEYS, INTENTS, TOPICS, read_jsonl, validate_dataset

RUNS = ("base_labels", "v2_labels", "v3_labels", "base_direct", "v2_direct", "v3_direct")


def score_class(gold: list[str], predicted: list[str | None], label: str) -> dict:
    tp = sum(a == label and b == label for a, b in zip(gold, predicted))
    fp = sum(a != label and b == label for a, b in zip(gold, predicted))
    fn = sum(a == label and b != label for a, b in zip(gold, predicted))
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"support": tp + fn, "tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": r, "f1": f}


def macro(scores: dict[str, dict], key: str) -> float:
    return sum(value[key] for value in scores.values()) / len(scores)


def load_run(path: Path, raw_path: Path, rows: list[dict], task: str) -> tuple[dict[str, dict], dict]:
    ids = {r["id"] for r in rows}
    predictions = read_jsonl(path)
    if len(predictions) != len({r["id"] for r in predictions}) or not {r["id"] for r in predictions} <= ids:
        raise ValueError(f"duplicate or unknown prediction ID: {path}")
    raw = read_jsonl(raw_path)
    if len(raw) != len(rows) or {r["id"] for r in raw} != ids:
        raise ValueError(f"raw audit lacks test coverage: {raw_path}")
    if {r["task"] for r in raw} != {task} or len({r["prompt_sha256"] for r in raw}) != 1:
        raise ValueError(f"mixed task or prompt: {raw_path}")
    if len({r.get("adapter") for r in raw}) != 1:
        raise ValueError(f"mixed adapters: {raw_path}")
    parsed = {r["id"]: r for r in predictions}
    if sum("prediction" in r for r in raw) != len(parsed):
        raise ValueError(f"raw/parsed count mismatch: {raw_path}")
    for row in parsed.values():
        if row["topic"] not in TOPICS or row["intent"] not in INTENTS:
            raise ValueError(f"invalid label: {row}")
        if task == "labels":
            gold = next(r for r in rows if r["id"] == row["id"])
            row["intervention"] = action_for(row["topic"], row["intent"], gold["locale"])
            row["policy_status"] = "COVERED" if row["intervention"] is not None else "REVIEW_REQUIRED"
        elif (not isinstance(row.get("intervention"), dict)
              or set(row["intervention"]) != set(ACTION_KEYS)
              or any(type(v) is not bool for v in row["intervention"].values())):
            raise ValueError(f"invalid action: {row}")
    return parsed, {"parsed": len(parsed), "total": len(rows), "prompt_sha256": raw[0]["prompt_sha256"],
                    "adapter": raw[0].get("adapter"), "prediction_path": str(path), "raw_path": str(raw_path)}


def metrics(rows: list[dict], pred: dict[str, dict], task: str) -> dict:
    topics = {label: score_class([r["topic"] for r in rows], [pred.get(r["id"], {}).get("topic") for r in rows], label)
              for label in sorted(TOPICS)}
    intents = {label: score_class([r["intent"] for r in rows], [pred.get(r["id"], {}).get("intent") for r in rows], label)
               for label in sorted(INTENTS)}
    action = {}
    for bit in ACTION_KEYS:
        action[bit] = score_class([str(r["intervention"][bit]) for r in rows],
                                  [str(pred[r["id"]]["intervention"][bit])
                                   if r["id"] in pred and pred[r["id"]].get("intervention") is not None else None
                                   for r in rows], "True")
    exact = [pred.get(r["id"], {}).get("intervention") == r["intervention"] for r in rows]
    def bit(row: dict, name: str) -> bool:
        value = pred.get(row["id"], {}).get("intervention")
        return isinstance(value, dict) and value[name]
    valid_rule = [r for r in rows if r["id"] in pred and covered(pred[r["id"]]["topic"], pred[r["id"]]["intent"])]
    return {
        "n": len(rows), "parsed": len(pred), "topic_accuracy": sum(pred.get(r["id"], {}).get("topic") == r["topic"] for r in rows) / len(rows),
        "intent_accuracy": sum(pred.get(r["id"], {}).get("intent") == r["intent"] for r in rows) / len(rows),
        "topic": topics, "intent": intents, "action": action,
        "topic_macro": {k: macro(topics, k) for k in ("precision", "recall", "f1")},
        "intent_macro": {k: macro(intents, k) for k in ("precision", "recall", "f1")},
        "action_exact": sum(exact), "action_exact_rate": sum(exact) / len(rows),
        "policy_covered": sum(pred.get(r["id"], {}).get("intervention") is not None for r in rows) if task == "labels" else None,
        "rule_consistent": sum(pred[r["id"]]["intervention"] == action_for(pred[r["id"]]["topic"], pred[r["id"]]["intent"], r["locale"])
                               for r in valid_rule), "rule_defined": len(valid_rule),
        "harmful_filter_miss": sum(not bit(r, "filter") for r in rows if r["intent"] == "HARMFUL_INSTRUCTION"),
        "harmful_n": sum(r["intent"] == "HARMFUL_INSTRUCTION" for r in rows),
        "support_blocked": sum(bit(r, "block") for r in rows if r["intent"] == "SUPPORT_SEEKING"),
        "support_n": sum(r["intent"] == "SUPPORT_SEEKING" for r in rows),
        "false_block": sum(bit(r, "block") and not r["intervention"]["block"] for r in rows),
        "private_block_miss": sum(not bit(r, "block") for r in rows if r["intent"] == "PRIVATE_INFO_REQUEST"),
        "private_n": sum(r["intent"] == "PRIVATE_INFO_REQUEST" for r in rows),
        "by_topic": {label: {"n": sum(r["topic"] == label for r in rows),
                              "action_exact": sum(exact[i] for i, r in enumerate(rows) if r["topic"] == label)}
                     for label in sorted(TOPICS)},
        "by_locale": {label: {"n": sum(r["locale"] == label for r in rows),
                               "action_exact": sum(exact[i] for i, r in enumerate(rows) if r["locale"] == label)}
                      for label in ("CN", "SG")},
    }


def paired_interval(rows: list[dict], before: dict, after: dict) -> tuple[float, float]:
    # Each v3 test row is a distinct semantic group; this interval only covers sampling of synthetic scenarios.
    values = [int(after.get(r["id"], {}).get("intervention") == r["intervention"])
              - int(before.get(r["id"], {}).get("intervention") == r["intervention"]) for r in rows]
    rng = random.Random(2026)
    estimates = sorted(sum(rng.choices(values, k=len(values))) / len(values) for _ in range(2000))
    return estimates[49], estimates[1949]


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("test_data")
    parser.add_argument("split_manifest")
    parser.add_argument("output_json")
    parser.add_argument("output_markdown")
    for key in RUNS:
        parser.add_argument("--" + key.replace("_", "-"), required=True)
        parser.add_argument("--" + key.replace("_", "-") + "-raw", required=True)
    args = parser.parse_args()
    output_json, output_md = Path(args.output_json), Path(args.output_markdown)
    if output_json.exists() or output_md.exists():
        parser.error("output exists")
    test_path = Path(args.test_data)
    rows = read_jsonl(test_path)
    errors = validate_dataset(rows)
    if errors:
        raise ValueError("\n".join(errors[:20]))
    manifest = json.loads(Path(args.split_manifest).read_text(encoding="utf-8"))
    test_sha = hashlib.sha256(test_path.read_bytes()).hexdigest()
    if test_sha != manifest["splits"]["test"]["sha256"] or len(rows) != 200:
        raise ValueError("test split changed")
    runs = {}
    for key in RUNS:
        task = "labels" if key.endswith("labels") else "direct"
        predictions, meta = load_run(Path(getattr(args, key)), Path(getattr(args, key + "_raw")), rows, task)
        runs[key] = {"meta": meta, "metrics": metrics(rows, predictions, task), "predictions": predictions}
    for task in ("labels", "direct"):
        if len({runs[f"{version}_{task}"]["meta"]["prompt_sha256"] for version in ("base", "v2", "v3")}) != 1:
            raise ValueError(f"{task} prompts differ across models")
    comparisons = {}
    for task in ("labels", "direct"):
        for version in ("v2", "v3"):
            baseline = runs[f"base_{task}"]
            tuned = runs[f"{version}_{task}"]
            comparisons[f"{version}_{task}"] = {
                "action_delta_pp": (tuned["metrics"]["action_exact_rate"] - baseline["metrics"]["action_exact_rate"]) * 100,
                "action_delta_bootstrap_95_pp": [v * 100 for v in paired_interval(rows, baseline["predictions"], tuned["predictions"])],
                "fixed": sum(baseline["predictions"].get(r["id"], {}).get("intervention") != r["intervention"]
                             and tuned["predictions"].get(r["id"], {}).get("intervention") == r["intervention"] for r in rows),
                "regressed": sum(baseline["predictions"].get(r["id"], {}).get("intervention") == r["intervention"]
                                 and tuned["predictions"].get(r["id"], {}).get("intervention") != r["intervention"] for r in rows),
            }
    data = {"test_sha256": test_sha, "manifest_sha256": hashlib.sha256(Path(args.split_manifest).read_bytes()).hexdigest(),
            "test_rows": len(rows), "reviewed_test_rows": sum(r["review_status"] == "approved" for r in rows),
            "runs": {key: {"meta": value["meta"], "metrics": value["metrics"],
                           "errors": [{"id": r["id"], "query": r["query"], "locale": r["locale"],
                                       "gold_topic": r["topic"], "gold_intent": r["intent"],
                                       "predicted": value["predictions"].get(r["id"])}
                                      for r in rows if value["predictions"].get(r["id"], {}).get("intervention") != r["intervention"]][:40]}
                     for key, value in runs.items()}, "comparisons": comparisons}
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# v3 Qwen3.5 9B QLoRA 探索性比较\n\n",
             "本报告比较同一批 200 条中文合成留出查询。标签目前全部为 `draft`，任何数值均为**内部探索性诊断**，不代表已审核 Gold 或真实平台表现。旧 v2.1 中文测试题已进入 v3 训练，本报告只比较新的 v3 测试题。\n\n",
             "## 总览\n\n",
             "| 模型路线 | 解析 | Topic Macro P/R/F1 | Intent Macro P/R/F1 | 六动作整组 | 规则覆盖 | 漏保护有害请求 | 求助误 Block | 误 Block | Block 漏判 |\n",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n"]
    names = {"base_labels": "基础模型→规则", "v2_labels": "v2.1 QLoRA→规则", "v3_labels": "v3 QLoRA→规则",
             "base_direct": "基础模型直接输出", "v2_direct": "v2.1 QLoRA 直接输出", "v3_direct": "v3 QLoRA 直接输出"}
    for key in RUNS:
        m = runs[key]["metrics"]
        topic = "/".join(f"{m['topic_macro'][k]:.3f}" for k in ("precision", "recall", "f1"))
        intent = "/".join(f"{m['intent_macro'][k]:.3f}" for k in ("precision", "recall", "f1"))
        coverage = f"{m['policy_covered']}/{m['n']}" if m["policy_covered"] is not None else "—"
        lines.append(f"| {names[key]} | {m['parsed']}/{m['n']} | {topic} | {intent} | {m['action_exact']}/{m['n']} ({pct(m['action_exact_rate'])}) | {coverage} | {m['harmful_filter_miss']}/{m['harmful_n']} | {m['support_blocked']}/{m['support_n']} | {m['false_block']} | {m['private_block_miss']}/{m['private_n']} |\n")
    lines.extend(["\nMacro P/R/F1 分别等权平均各类别的 Precision、Recall、F1。正类支持数、TP/FP/FN 在随附 JSON 中。整组一致指六动作全部匹配；只解析成功却不能执行政策的输出算不一致。\n\n",
                  "## 同一新测试集上的变化\n\n",
                  "| 路线 | 模型 | Topic Macro F1 | Intent Macro F1 | 六动作整组 | 相对基础模型整组变化 | 配对 bootstrap 95% 区间 |\n",
                  "| --- | --- | ---: | ---: | ---: | ---: | ---: |\n"])
    for task, route_name in (("labels", "标签→规则"), ("direct", "直接输出")):
        base = runs[f"base_{task}"]["metrics"]
        for version in ("v2", "v3"):
            m = runs[f"{version}_{task}"]["metrics"]
            c = comparisons[f"{version}_{task}"]
            lo, hi = c["action_delta_bootstrap_95_pp"]
            lines.append(f"| {route_name} | {version} | {pct(base['topic_macro']['f1'])} → {pct(m['topic_macro']['f1'])} ({(m['topic_macro']['f1']-base['topic_macro']['f1'])*100:+.1f} pp) | {pct(base['intent_macro']['f1'])} → {pct(m['intent_macro']['f1'])} ({(m['intent_macro']['f1']-base['intent_macro']['f1'])*100:+.1f} pp) | {base['action_exact']}/{base['n']} → {m['action_exact']}/{m['n']} | {c['action_delta_pp']:+.1f} pp | [{lo:+.1f}, {hi:+.1f}] pp |\n")
    for field, title in (("topic", "Topic"), ("intent", "Intent"), ("action", "六动作正类")):
        lines.extend([f"\n## {title} 逐类 Precision / Recall / F1\n\n",
                      "| 类别 | 支持数 | 基础标签路线 P/R/F1 | v2.1 标签路线 P/R/F1 | v3 标签路线 P/R/F1 | 基础直接路线 P/R/F1 | v2.1 直接路线 P/R/F1 | v3 直接路线 P/R/F1 |\n",
                      "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n"])
        labels = sorted(runs["base_labels"]["metrics"][field])
        for label in labels:
            support = runs["base_labels"]["metrics"][field][label]["support"]
            cells = []
            for key in RUNS:
                x = runs[key]["metrics"][field][label]
                cells.append("/".join(f"{x[z]:.3f}" for z in ("precision", "recall", "f1")))
            lines.append(f"| {label} | {support} | " + " | ".join(cells) + " |\n")
    lines.extend(["\n## Topic 和地区切片的六动作整组一致\n\n",
                  "| 切片 | 样本数 | 基础标签→规则 | v2.1 标签→规则 | v3 标签→规则 | 基础直接 | v2.1 直接 | v3 直接 |\n",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n"])
    for dimension, labels in (("by_topic", sorted(TOPICS)), ("by_locale", ("CN", "SG"))):
        for label in labels:
            support = runs["base_labels"]["metrics"][dimension][label]["n"]
            cells = [str(runs[key]["metrics"][dimension][label]["action_exact"]) + f"/{support}" for key in RUNS]
            lines.append(f"| {label} | {support} | " + " | ".join(cells) + " |\n")
    lines.extend([
        "\n## 核心发现与标签可信度\n\n",
        "- 在同一批新题上，v3 相比 v2.1 的两条路线，六动作整组一致率均由 129/200 升到 158/200（+14.5 pp）。标签路线 Topic Macro F1 从 81.3% 到 93.7%（+12.4 pp）、Intent Macro F1 从 63.8% 到 71.4%（+7.6 pp）；直接输出路线分别从 70.7% 到 93.0%（+22.3 pp）和 67.5% 到 68.3%（+0.8 pp）。因此直接输出路线的意图识别仍是瓶颈，不能只看动作提升。\n",
        "- v2.1 直接输出把 24 条 `NONE` 全判为政治主题；v3 仍错判 2 条，`NONE` Recall 由 0/24 到 22/24。这个差异与 v3 新增各 topic 的 CN 查询和普通难负例一致，但单轮实验不能确认具体因果。v2.1 直接输出还有 4 条违反 Block 排他规则，均计入解析失败。\n",
        "- v3 直接输出 `filter` 的 Precision/Recall 为 100.0%/97.5%，`downrank` 为 100.0%/97.4%，各有 4 条漏判、0 条误开启；`warning` 有 9 条漏判、4 条误开启，`redirect` 有 10 条漏判、23 条误开启。Block 为 10/10 命中、0 条误 Block，但正例都来自同一个政治私人信息场景家族，不能推断实际平台召回率。\n",
        "- **目前最大限制是草稿标签错误。** `sq_1064`–`sq_1071` 这 8 条被标为诈骗有害指导的测试查询实际要求防范、止损或求助；饮食失调的 6 条 `PREVENTION` 测试查询多为症状陈述，自伤 `AMBIGUOUS` 中多条没有自伤线索。模型与这些标签不一致不能直接算作模型安全失败，也不能在看过预测后悄悄重标并称为盲测。详见[逐例错误分析](./v3_error_analysis.md)。\n",
        "- 六动作整组正确也会掩盖意图错分：v3 直接输出的 61 条 Intent 不一致中有 23 条动作仍一致，因为部分 Intent 共享同一动作组合。故报告同时保留 Intent 逐类 P/R/F1 和策略动作指标。\n",
        "\n## 结果分析与数据集改进\n\n",
    ])
    # Describe observed movements without claiming a causal explanation from one run.
    for task, route in (("labels", "标签→规则"), ("direct", "直接输出")):
        before, after = runs[f"base_{task}"]["metrics"], runs[f"v3_{task}"]["metrics"]
        topic_delta = (after["topic_macro"]["f1"] - before["topic_macro"]["f1"]) * 100
        intent_delta = (after["intent_macro"]["f1"] - before["intent_macro"]["f1"]) * 100
        action_delta = (after["action_exact_rate"] - before["action_exact_rate"]) * 100
        c = comparisons[f"v3_{task}"]
        lines.append(f"- **{route}**：Topic Macro F1 {topic_delta:+.1f} pp，Intent Macro F1 {intent_delta:+.1f} pp，六动作整组 {action_delta:+.1f} pp；同题修正 {c['fixed']} 条、退步 {c['regressed']} 条。分别观察分类与动作，不能由单一平均分推断各安全边界都改善。\n")
    for bit in ("filter", "downrank", "warning", "redirect", "block"):
        b, a = runs["base_direct"]["metrics"]["action"][bit], runs["v3_direct"]["metrics"]["action"][bit]
        lines.append(f"- **{bit}**（直接输出）正类：Precision {pct(b['precision'])} → {pct(a['precision'])}，Recall {pct(b['recall'])} → {pct(a['recall'])}；测试正例 {a['support']} 条，训练后 FP={a['fp']}、FN={a['fn']}。\n")
    lines.extend(["\n指标下降可由具体错分、动作过度开启或漏开启、草稿标签噪声、类别/地区比例及单次训练随机性共同造成；本实验不能仅凭相关性判断因果或宣称过拟合。应先复核下面的错例，再决定改标签、补样本还是改规则。\n\n",
                  "1. 先抽查训练/开发集 60 条，优先 Block、有害请求、求助和含糊边界，记录逐条裁决。若发现系统性标签错误，修订冻结版并重训；零星修订也要在报告中留下版本记录。\n",
                  "2. 先复核低分的 `PREVENTION`、`AMBIGUOUS` 与 `HARMFUL_INSTRUCTION` 草稿边界，再按逐类 FP/FN 补充独立场景和难负例；当前尤其要检查 `warning/redirect` 的误开启与漏开启。补数前先检查标签，避免放大错标。\n",
                  "3. 测试集 200 条仍未人工盲审，因此逐类分数只反映草稿标签的一致性；后续要从中分层审核测试题，冻结裁决后再重算。真实平台泛化还需要获准的脱敏真实查询及候选结果级标注。\n\n",
                  "## 数据解释边界\n\n",
                  "- 1000 条均为中文合成查询。新测试题使用单独生成提示，但与训练题由同一个本地 Qwen 基座生成；没有人类独立写题，也没有真实流量代表性。\n",
                  "- 六动作由假设规则起草；`filter/downrank` 表示建议启用条件性规则，不是对实际搜索结果的处理记录。标签→规则路线复用同一映射，动作得分并非独立验证政策正确性。\n",
                  "- 所有测试题当前均为 `draft`。配对 bootstrap 区间只量化这批合成场景的抽样变动，不包括标签误差、生成器风格、政策假设或真实流量偏差。\n",
                  "- v2.1 适配器训练时使用旧直接输出提示，三套模型在本次测试使用同一个 v3 修正提示；解释 v2.1 与 v3 差异时应考虑该提示变化。\n",
                  "- 非政治 + PRIVATE_INFO_REQUEST 在 v3 被明确列为政策未覆盖，进入复核；不能自动 Block。\n",
                  "- 逐例标注争议、动作错例来源和审核优先级见[错误分析](./v3_error_analysis.md)。\n"])
    output_md.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {output_json} and {output_md}")


if __name__ == "__main__":
    main()
