"""Compare base and QLoRA routes on one frozen internal test split."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from apply_policy_to_predictions_v2 import covered
from build_v2_candidates import intervention
from schema_v2 import ACTION_KEYS, INTENTS, TOPICS, read_jsonl, validate_dataset


def load_run(path: str, raw_path: str, ids: set[str], route: str, gold: dict[str, dict]) -> tuple[dict[str, dict], dict]:
    predictions = {}
    for row in read_jsonl(path):
        row_id = row.get("id")
        if row_id in predictions or row_id not in ids:
            raise ValueError(f"duplicate or unknown prediction id: {row_id}")
        if row.get("topic") not in TOPICS or row.get("intent") not in INTENTS:
            raise ValueError(f"invalid label for {row_id}")
        if route == "labels":
            if covered(row["topic"], row["intent"]):
                action, _ = intervention(row["topic"], row["intent"], gold[row_id]["locale"])
                row = {**row, "intervention": action, "policy_status": "COVERED"}
            else:
                row = {**row, "intervention": None, "policy_status": "REVIEW_REQUIRED"}
        else:
            action = row.get("intervention")
            if not isinstance(action, dict) or set(action) != set(ACTION_KEYS) or any(type(action[key]) is not bool for key in ACTION_KEYS):
                raise ValueError(f"invalid intervention for {row_id}")
        predictions[row_id] = row
    audit = read_jsonl(raw_path)
    audit_ids = [row.get("id") for row in audit]
    if len(audit_ids) != len(ids) or len(set(audit_ids)) != len(ids) or set(audit_ids) != ids:
        raise ValueError(f"audit does not cover test set: {raw_path}")
    if {row.get("task") for row in audit} != {route}:
        raise ValueError(f"audit task mismatch: {raw_path}")
    if len({row.get("prompt_sha256") for row in audit}) != 1:
        raise ValueError(f"mixed prompts in audit: {raw_path}")
    if len({row.get("adapter") for row in audit}) != 1:
        raise ValueError(f"mixed adapters in audit: {raw_path}")
    parsed = sum("prediction" in row for row in audit)
    if parsed != len(predictions):
        raise ValueError(f"audit/prediction count mismatch: {raw_path}")
    meta = {"parsed": parsed, "total": len(ids), "path": path, "raw_path": raw_path,
            "prompt_sha256": audit[0].get("prompt_sha256"), "adapter": audit[0].get("adapter")}
    return predictions, meta


def prf(rows: list[dict], predictions: dict[str, dict], field: str, label: str) -> dict:
    tp = sum(row[field] == label and predictions.get(row["id"], {}).get(field) == label for row in rows)
    fp = sum(row[field] != label and predictions.get(row["id"], {}).get(field) == label for row in rows)
    fn = sum(row[field] == label and predictions.get(row["id"], {}).get(field) != label for row in rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"support": tp + fn, "tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def action_bit(rows: list[dict], predictions: dict[str, dict], bit: str) -> dict:
    tp = fp = fn = 0
    for row in rows:
        predicted = predictions.get(row["id"], {}).get("intervention")
        value = predicted.get(bit) if isinstance(predicted, dict) else None
        expected = row["intervention"][bit]
        tp += int(expected and value is True)
        fp += int(not expected and value is True)
        fn += int(expected and value is not True)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"support": tp + fn, "tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def exact_action(row: dict, predictions: dict[str, dict]) -> bool:
    return predictions.get(row["id"], {}).get("intervention") == row["intervention"]


def percent_change(before: float, after: float) -> str:
    return f"{before * 100:.1f}% → {after * 100:.1f}% ({(after - before) * 100:+.1f} pp)"


def cluster_interval(rows: list[dict], predictions: dict[str, dict], cluster_for: dict[str, str]) -> list[float]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[cluster_for[row["semantic_group_id"]]].append(row)
    clusters = sorted(grouped)
    rng = random.Random(2026)
    estimates = []
    for _ in range(2000):
        sampled = [row for cluster in rng.choices(clusters, k=len(clusters)) for row in grouped[cluster]]
        estimates.append(sum(exact_action(row, predictions) for row in sampled) / len(sampled))
    estimates.sort()
    return [estimates[49], estimates[1949]]


def paired_delta_interval(rows: list[dict], before: dict[str, dict], after: dict[str, dict],
                          cluster_for: dict[str, str]) -> list[float]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[cluster_for[row["semantic_group_id"]]].append(row)
    clusters = sorted(grouped)
    rng = random.Random(2027)
    estimates = []
    for _ in range(2000):
        sampled = [row for cluster in rng.choices(clusters, k=len(clusters)) for row in grouped[cluster]]
        estimates.append(sum(exact_action(row, after) - exact_action(row, before) for row in sampled) / len(sampled))
    estimates.sort()
    return [estimates[49], estimates[1949]]


def summarize(rows: list[dict], predictions: dict[str, dict], cluster_for: dict[str, str], route: str) -> dict:
    n = len(rows)
    topic_correct = sum(predictions.get(row["id"], {}).get("topic") == row["topic"] for row in rows)
    intent_correct = sum(predictions.get(row["id"], {}).get("intent") == row["intent"] for row in rows)
    action_correct = sum(exact_action(row, predictions) for row in rows)
    topic_scores = {label: prf(rows, predictions, "topic", label) for label in sorted(TOPICS) if any(row["topic"] == label for row in rows)}
    intent_scores = {label: prf(rows, predictions, "intent", label) for label in sorted(INTENTS) if any(row["intent"] == label for row in rows)}
    bits = {bit: action_bit(rows, predictions, bit) for bit in ACTION_KEYS}
    harmful = [row for row in rows if row["intent"] == "HARMFUL_INSTRUCTION"]
    support = [row for row in rows if row["intent"] == "SUPPORT_SEEKING"]
    private = [row for row in rows if row["intent"] == "PRIVATE_INFO_REQUEST"]
    def action_is(row: dict, bit: str) -> bool:
        action = predictions.get(row["id"], {}).get("intervention")
        return isinstance(action, dict) and action[bit] is True

    defined_predictions = [
        row for row in rows
        if row["id"] in predictions
        and covered(predictions[row["id"]]["topic"], predictions[row["id"]]["intent"])
    ]
    rule_consistent = sum(
        predictions[row["id"]].get("intervention")
        == intervention(predictions[row["id"]]["topic"], predictions[row["id"]]["intent"], row["locale"])[0]
        for row in defined_predictions
    )

    return {
        "n": n, "parseable": sum(row["id"] in predictions for row in rows),
        "action_available": sum(isinstance(predictions.get(row["id"], {}).get("intervention"), dict) for row in rows),
        "policy_covered": (sum(isinstance(predictions.get(row["id"], {}).get("intervention"), dict)
                               for row in rows) if route == "labels" else None),
        "predicted_policy_defined": len(defined_predictions),
        "rule_consistent": rule_consistent,
        "topic_correct": topic_correct, "intent_correct": intent_correct, "action_exact": action_correct,
        "action_exact_cluster_bootstrap_95": cluster_interval(rows, predictions, cluster_for),
        "topic_macro_precision": sum(x["precision"] for x in topic_scores.values()) / len(topic_scores),
        "topic_macro_recall": sum(x["recall"] for x in topic_scores.values()) / len(topic_scores),
        "topic_macro_f1": sum(x["f1"] for x in topic_scores.values()) / len(topic_scores),
        "intent_macro_precision": sum(x["precision"] for x in intent_scores.values()) / len(intent_scores),
        "intent_macro_recall": sum(x["recall"] for x in intent_scores.values()) / len(intent_scores),
        "intent_macro_f1": sum(x["f1"] for x in intent_scores.values()) / len(intent_scores),
        "topic_per_label": topic_scores, "intent_per_label": intent_scores, "action_bits": bits,
        "harmful_filter_miss": sum(not action_is(row, "filter") for row in harmful), "harmful_n": len(harmful),
        "support_blocked": sum(action_is(row, "block") for row in support), "support_n": len(support),
        "false_block": sum(action_is(row, "block") and not row["intervention"]["block"] for row in rows),
        "private_block_miss": sum(not action_is(row, "block") for row in private), "private_n": len(private),
        "status_slices": {status: {"n": len(subset), "action_exact": sum(exact_action(row, predictions) for row in subset),
                                   "topic_correct": sum(predictions.get(row["id"], {}).get("topic") == row["topic"] for row in subset),
                                   "intent_correct": sum(predictions.get(row["id"], {}).get("intent") == row["intent"] for row in subset)}
                          for status in sorted({row["review_status"] for row in rows})
                          for subset in [[row for row in rows if row["review_status"] == status]]},
        "political": {"n": sum(row["topic"] == "POLITICAL_SENSITIVE" for row in rows),
                      "action_exact": sum(exact_action(row, predictions) for row in rows if row["topic"] == "POLITICAL_SENSITIVE")},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("test_data")
    parser.add_argument("split_manifest")
    parser.add_argument("output_json")
    parser.add_argument("output_markdown")
    for key in ("base_labels", "tuned_labels", "base_direct", "tuned_direct"):
        parser.add_argument(f"--{key.replace('_', '-')}", required=True)
        parser.add_argument(f"--{key.replace('_', '-')}-raw", required=True)
    args = parser.parse_args()
    output_json, output_markdown = Path(args.output_json), Path(args.output_markdown)
    if output_json.exists() or output_markdown.exists():
        parser.error("output exists; comparison will not be overwritten")
    rows = read_jsonl(args.test_data)
    errors = validate_dataset(rows)
    if errors:
        raise ValueError("\n".join(errors))
    manifest = json.loads(Path(args.split_manifest).read_text(encoding="utf-8"))
    test_hash = hashlib.sha256(Path(args.test_data).read_bytes()).hexdigest()
    if test_hash != manifest["splits"]["test"]["sha256"]:
        raise ValueError("test content differs from frozen split manifest")
    ids = {row["id"] for row in rows}
    if ids != set(manifest["splits"]["test"]["ids"]):
        raise ValueError("test IDs do not match frozen manifest")
    gold = {row["id"]: row for row in rows}
    cluster_for = manifest["leakage_cluster_for_semantic_group"]
    runs = {}
    for key in ("base_labels", "tuned_labels", "base_direct", "tuned_direct"):
        route = "labels" if key.endswith("labels") else "direct"
        predictions, meta = load_run(getattr(args, key), getattr(args, key + "_raw"), ids, route, gold)
        runs[key] = {"meta": meta, "metrics": summarize(rows, predictions, cluster_for, route), "predictions": predictions}
    for route in ("labels", "direct"):
        if runs["base_" + route]["meta"]["prompt_sha256"] != runs["tuned_" + route]["meta"]["prompt_sha256"]:
            raise ValueError(f"base/tuned {route} prompts differ")
    summary = {
        "test_sha256": test_hash,
        "manifest_sha256": hashlib.sha256(Path(args.split_manifest).read_bytes()).hexdigest(),
        "test_rows": len(rows), "test_leakage_clusters": manifest["splits"]["test"]["leakage_clusters"],
        "runs": {
            key: {
                "meta": value["meta"], "metrics": value["metrics"],
                "policy_review": [
                    {"id": row_id, "topic": prediction["topic"], "intent": prediction["intent"],
                     "locale": gold[row_id]["locale"]}
                    for row_id, prediction in value["predictions"].items()
                    if prediction.get("policy_status") == "REVIEW_REQUIRED"
                ],
                "errors": [
                    {"id": row["id"], "query": row["query"], "locale": row["locale"],
                     "review_status": row["review_status"],
                     "gold": {"topic": row["topic"], "intent": row["intent"], "intervention": row["intervention"]},
                     "predicted": value["predictions"].get(row["id"])}
                    for row in rows
                    if value["predictions"].get(row["id"], {}).get("topic") != row["topic"]
                    or value["predictions"].get(row["id"], {}).get("intent") != row["intent"]
                    or not exact_action(row, value["predictions"])
                ],
            }
            for key, value in runs.items()
        },
    }
    for route in ("labels", "direct"):
        before, after = runs["base_" + route]["predictions"], runs["tuned_" + route]["predictions"]
        summary[route + "_paired_action"] = {
            "fixed": sum(not exact_action(row, before) and exact_action(row, after) for row in rows),
            "regressed": sum(exact_action(row, before) and not exact_action(row, after) for row in rows),
            "cluster_bootstrap_delta_95": paired_delta_interval(rows, before, after, cluster_for),
        }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# v2.1 QLoRA 内部留出比较\n\n",
             "测试集 62 条\n\n",
             "| 路线 | 解析 | Topic Macro P/R/F1 | Intent Macro P/R/F1 | 六动作整组 | 组级 95% 区间 | 政策覆盖 | 自身标签规则一致 | 政治动作 |\n",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n"]
    for key, label in (("base_labels", "基础模型→规则"), ("tuned_labels", "QLoRA 标签→规则"),
                       ("base_direct", "基础模型直接输出"), ("tuned_direct", "QLoRA 直接输出")):
        m = runs[key]["metrics"]
        coverage = f"{m['policy_covered']}/{m['n']}" if m["policy_covered"] is not None else "—"
        lower, upper = m["action_exact_cluster_bootstrap_95"]
        topic_macro = "/".join(f"{m['topic_macro_' + metric]:.3f}" for metric in ("precision", "recall", "f1"))
        intent_macro = "/".join(f"{m['intent_macro_' + metric]:.3f}" for metric in ("precision", "recall", "f1"))
        lines.append(f"| {label} | {m['parseable']}/{m['n']} | {topic_macro} | "
                     f"{intent_macro} | {m['action_exact']}/{m['n']} | "
                     f"[{lower:.3f}, {upper:.3f}] | {coverage} | "
                     f"{m['rule_consistent']}/{m['predicted_policy_defined']} | "
                     f"{m['political']['action_exact']}/{m['political']['n']} |\n")
    lines.extend(["\nMacro 是把每个类别的指标等权平均。P=TP/(TP+FP)，R=TP/(TP+FN)，F1 是每类 P 与 R 的调和平均；Macro F1 是**各类 F1 的平均**，不是 Macro P 与 Macro R 再计算一次 F1。没有预测正例时，Precision 按本实验的约定记为 0。\n\n",
                  "## 训练前后总览\n\n",
                  "同一路线的基础模型和 QLoRA 模型使用相同 Prompt 与同一批冻结测试行。变化统一用**百分点（pp）**：例如 20% → 30% 是 +10 pp；相对增长是 50%，两者不能混用。当前数据有训练前为 0% 的类别，所以不报相对增长。\n\n",
                  "| 路线 | 指标 | 基础模型 | QLoRA 后 | 变化 |\n",
                  "| --- | --- | ---: | ---: | ---: |\n"])
    for route, label in (("labels", "标签→规则"), ("direct", "直接输出")):
        before = runs["base_" + route]["metrics"]
        after = runs["tuned_" + route]["metrics"]
        for field, title in (("topic_macro_precision", "Topic Macro Precision"),
                             ("topic_macro_recall", "Topic Macro Recall"),
                             ("topic_macro_f1", "Topic Macro F1"),
                             ("intent_macro_precision", "Intent Macro Precision"),
                             ("intent_macro_recall", "Intent Macro Recall"),
                             ("intent_macro_f1", "Intent Macro F1")):
            delta = (after[field] - before[field]) * 100
            lines.append(f"| {label} | {title} | {before[field] * 100:.1f}% | "
                         f"{after[field] * 100:.1f}% | {delta:+.1f} pp |\n")
        action_before = before["action_exact"] / before["n"]
        action_after = after["action_exact"] / after["n"]
        if route == "labels":
            # Keep the overview's existing separator; the headline table already reports this action metric.
            lines.append("|           |                        |               |               |          |\n")
        else:
            lines.append(f"| {label} | 六动作整组一致 | {before['action_exact']}/{before['n']} "
                         f"({action_before * 100:.1f}%) | {after['action_exact']}/{after['n']} "
                         f"({action_after * 100:.1f}%) | {(action_after - action_before) * 100:+.1f} pp |\n")
    lines.extend(["\n以下 Support 是测试集中该类的真实条数；每个单元格依次为**基础模型 → QLoRA 后（变化）**。\n\n",
                  "## 逐类 Topic 指标：训练前后\n\n",
                  "| 路线 | Topic | Support | Precision | Recall | F1 |\n",
                  "| --- | --- | ---: | ---: | ---: | ---: |\n"])
    for route, label in (("labels", "标签→规则"), ("direct", "直接输出")):
        baseline = runs["base_" + route]["metrics"]["topic_per_label"]
        trained = runs["tuned_" + route]["metrics"]["topic_per_label"]
        for topic, after in trained.items():
            before = baseline[topic]
            lines.append(f"| {label} | {topic} | {after['support']} | "
                         f"{percent_change(before['precision'], after['precision'])} | "
                         f"{percent_change(before['recall'], after['recall'])} | "
                         f"{percent_change(before['f1'], after['f1'])} |\n")
    lines.extend(["\n## 逐类 Intent 指标：训练前后\n\n",
                  "| 路线 | Intent | Support | Precision | Recall | F1 |\n",
                  "| --- | --- | ---: | ---: | ---: | ---: |\n"])
    for route, label in (("labels", "标签→规则"), ("direct", "直接输出")):
        baseline = runs["base_" + route]["metrics"]["intent_per_label"]
        trained = runs["tuned_" + route]["metrics"]["intent_per_label"]
        for intent, after in trained.items():
            before = baseline[intent]
            lines.append(f"| {label} | {intent} | {after['support']} | "
                         f"{percent_change(before['precision'], after['precision'])} | "
                         f"{percent_change(before['recall'], after['recall'])} | "
                         f"{percent_change(before['f1'], after['f1'])} |\n")
    lines.extend(["\n## 六动作正类指标：训练前后\n\n",
                  "每个动作都是独立的布尔预测；这里的 Precision/Recall 只把 `true` 当正类。六动作整组一致率仍是更严格的整条查询指标。\n\n",
                  "| 路线 | 动作 | True Support | Precision | Recall | F1 |\n",
                  "| --- | --- | ---: | ---: | ---: | ---: |\n"])
    for route, label in (("labels", "标签→规则"), ("direct", "直接输出")):
        baseline = runs["base_" + route]["metrics"]["action_bits"]
        trained = runs["tuned_" + route]["metrics"]["action_bits"]
        for bit, after in trained.items():
            before = baseline[bit]
            lines.append(f"| {label} | {bit} | {after['support']} | "
                         f"{percent_change(before['precision'], after['precision'])} | "
                         f"{percent_change(before['recall'], after['recall'])} | "
                         f"{percent_change(before['f1'], after['f1'])} |\n")
    lines.extend(["\n", "## 关键错误计数\n\n",
                  "| 路线 | 有害请求漏 filter | 求助误 Block | 误 Block | 隐私请求漏 Block | 已审核动作一致 | 草稿动作一致 |\n",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n"])
    for key, label in (("base_labels", "基础模型→规则"), ("tuned_labels", "QLoRA 标签→规则"),
                       ("base_direct", "基础模型直接输出"), ("tuned_direct", "QLoRA 直接输出")):
        m = runs[key]["metrics"]
        a, d = m["status_slices"]["approved"], m["status_slices"]["draft"]
        lines.append(f"| {label} | {m['harmful_filter_miss']}/{m['harmful_n']} | "
                     f"{m['support_blocked']}/{m['support_n']} | {m['false_block']} | "
                     f"{m['private_block_miss']}/{m['private_n']} | "
                     f"{a['action_exact']}/{a['n']} | {d['action_exact']}/{d['n']} |\n")
    lines.extend(["\n## 同题前后变化\n\n",
                  "| 路线 | 修正 | 退步 | 六动作一致率差的组级 95% 区间 |\n",
                  "| --- | ---: | ---: | ---: |\n"])
    for route, label in (("labels", "标签→规则"), ("direct", "直接输出")):
        paired = summary[route + "_paired_action"]
        lower, upper = paired["cluster_bootstrap_delta_95"]
        lines.append(f"| {label} | {paired['fixed']} | {paired['regressed']} | [{lower:.3f}, {upper:.3f}] |\n")
    for key, label in (("base_labels", "基础模型"), ("tuned_labels", "QLoRA")):
        reviews = summary["runs"][key]["policy_review"]
        lines.append(f"\n{label}标签路线的未定义组合进入政策复核：{len(reviews)} 条"
                     + ("（" + ", ".join(case["id"] for case in reviews) + "）" if reviews else "") + "。\n")
    lines.extend(["\n", "## 解释边界\n\n",
                  "- 六动作标签来自固定的假设政策；两阶段路线复用该映射，所以动作改善主要反映规则执行，仍依赖分类正确。\n",
                  "- 新增政治样例未经用户审核；政治测试仅 14 行，隐私 Block 仅 2 个语义组。报告原始计数，不把本结果当外部泛化性能。\n",
                  "- 旧 248 条已用于此前 Prompt 基线和错误分析；本测试集仅是训练前冻结的内部留出集。\n",
                  "- 直接输出路线不执行政策映射，故政策覆盖率不适用。解析成功后的动作结构有效数在 JSON 中。\n",
                  "- “自身标签规则一致”只检查模型给出的动作是否符合其自己预测的 topic/intent；分母排除尚未定义的组合。\n",
                  "- 组级 bootstrap 区间及逐类 Precision/Recall/F1 在 JSON 中；区间不覆盖合成数据和标签偏差。\n"])
    for key, title in (("tuned_labels", "标签路线的待查错例"), ("tuned_direct", "直接输出路线的待查错例")):
        examples = summary["runs"][key]["errors"][:8]
        lines.extend([f"\n## {title}\n\n"])
        if not examples:
            lines.append("本测试集没有与现有标签不一致的例子。\n")
            continue
        lines.extend(["| ID | 查询 | 状态 | 期望 topic / intent / 动作 | 预测 topic / intent / 动作 |\n",
                      "| --- | --- | --- | --- | --- |\n"])
        for case in examples:
            gold_case, predicted = case["gold"], case["predicted"] or {}
            escaped_query = case["query"].replace("|", "\\|")
            gold_value = f"{gold_case['topic']} / {gold_case['intent']} / {json.dumps(gold_case['intervention'], ensure_ascii=False, separators=(',', ':'))}"
            pred_value = f"{predicted.get('topic', '—')} / {predicted.get('intent', '—')} / {json.dumps(predicted.get('intervention'), ensure_ascii=False, separators=(',', ':'))}"
            lines.append(f"| {case['id']} | {escaped_query} | {case['review_status']} | "
                         f"{gold_value} | {pred_value} |\n")
    lines.extend([
        "\n## 实验结果总结与计划\n\n",
        "- 两条路线的 Intent Macro F1 都上升：标签→规则为 76.9% → 90.1%（+13.2 pp），直接输出为 81.3% → 89.7%（+8.4 pp）。标签路线的 `AMBIGUOUS` Recall 从 0/8 到 6/8，说明模型更能识别测试集中的含糊查询；但 `HARMFUL_INSTRUCTION` Recall 从 8/8 降到 7/8，平均分的提升没有覆盖每个安全边界。\n",
        "- 两条路线的 Topic Macro F1 都下降：标签→规则为 96.1% → 94.3%（-1.9 pp），直接输出为 96.3% → 88.5%（-7.9 pp）。直接输出路线把 3/6 条 `NONE` 错判为政治类，包括树叶变色、API 端点等普通查询，导致 `NONE` Recall 从 6/6 降到 3/6，政治类 Precision 从 100.0% 降到 77.8%。这显示模型把风险主题用到了无关查询上。\n",
        "- 直接输出路线的六动作整组一致从 17/62 升至 50/62；`filter` Recall 从 1/46 升至 46/46，`downrank` 从 9/42 升至 42/42。与此同时，`filter` 出现 3 条误开启、`downrank` 出现 7 条误开启，Precision 分别降到 93.9% 和 85.7%。例如 4 条政治隐私泄露求助草稿的预期 `downrank=false`，微调后均输出 `true`。因此动作覆盖改善伴随过度干预，整组一致率仍低于标签→规则路线的 56/62。\n",
        "- 标签→规则的整组一致为 54/62 → 56/62，但同题修正 5 条、退步 3 条；按语义组重采样的差值 95% 区间为 [-7.8, +15.6] pp，跨过 0。政策覆盖反而从 61/62 降到 59/62：`sq_0107`、`sq_0108`、`sq_0155` 的预测标签组合需要政策复核。现在不能断言这条路线的动作性能已稳定提升。两条路线的隐私请求 Block 均为 4/4，但只来自 2 个语义组，不能据此推断真实场景的 Block 可靠性。\n\n",
        "### 为什么可能下降\n\n",
        "目前能观察到的是错分和动作误开启，不能仅凭这一次训练判定为过拟合。测试集中 `NONE` 只有 6 条，少量错题就会使其 Recall 大幅变化；`sq_0107`/`sq_0108` 只说担心朋友安全，没有明确自伤线索，现有 `SELF_HARM` 标签的边界值得重新裁决。328 条查询均为合成，六动作只出现 6 种组合；政治类与地区、措辞和部分动作组合相关，模型可能学到了这些捷径。直接输出还要同时学习分类和六个动作，可能更倾向复用常见的保护动作组合。这些都是待检验的解释，需要标签复核、对照样例、消融或多随机种子实验才能区分。\n\n",
        "### 下一轮如何改进数据集\n\n",
        "1. **先校准标签。** 逐条审核新增的 80 条政治草稿；复核 `sq_0107`/`sq_0108` 的主题、`sq_0155` 的有害意图，以及 `GENERAL_INFO`、`PREVENTION`、`AMBIGUOUS` 的边界。记录每条修改理由；条件允许时再请第二位标注者独立复核分歧样例。不要把未经审核的政治草稿直接称作 Gold。\n",
        "2. **按错误类型补独立语义组。** 补普通中英文 `NONE` 查询与相近的政治查询，补 CN 的非政治查询和 SG 的政治查询；再补自伤与暴力求助、一般解释与预防、含糊请求与明确有害请求的近义对照。对政治隐私泄露求助，加入 `filter=true, downrank=false, redirect=true` 的不同真实措辞，并加入无须开启任何风险动作的普通查询。先按政策定义标注，再由人审核；按语义组而非翻译句数统计覆盖，避免只堆同一模板。\n",
        "3. **重建验证证据。** 保持现有 62 条测试集不动，把上述错例只用于诊断；新增未参与造数和调参的盲测语义组，并分开报告已审核与草稿、类别、地区、语言及关键误伤/漏判。先比较补数前后的数据分布，再用相同训练预算和多个随机种子复测，判断 Topic 下降和动作误开启是否真实改善。只有查询级标签时，`filter/downrank` 仍是建议启用的规则；要评估实际过滤与降权效果，还需加入候选搜索结果及其人工标注。\n",
        "\n更细的动作、主题和语种切片见[数据集缺口分析](./dataset_gap_analysis_v2_1.md)。\n",
    ])
    output_markdown.write_text("".join(lines), encoding="utf-8")
    print(output_markdown.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
