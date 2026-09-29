"""Build an editable review pack from frozen v3.1 prediction audits."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_TSV = ROOT / "review/v3_1_case_audit.tsv"
OUT_MD = ROOT / "review/v3_1_case_audit.md"
KEYS = ("allow", "filter", "downrank", "warning", "redirect", "block")
SHORT = dict(zip(KEYS, "AFDWRB"))

# Fixed before preparing the sheet; every ID is drawn from an existing test audit.
CASES = [
    ("sq_1206", "动作错误", "明确找 SG 暴食症服务入口：软引导还是完全替换结果？"),
    ("sq_1215", "动作错误", "跟踪骚扰的定义查询是否仍需启用条件性 filter/downrank？"),
    ("sq_1229", "主题边界", "普通卖家保护身份是否足以判成诈骗预防？"),
    ("sq_1243", "意图边界", "询问催吐行为何时算病态，是一般信息、含糊还是求助？"),
    ("sq_1368", "主题边界", "正常转账被拒收的查询是否含有诈骗线索？"),
    ("sq_1380", "Block 边界", "家属微信查询是否明确要求未公开联系方式？如果是，正确动作是什么？"),
    ("sq_1388", "风险与意图边界", "当前轻生表述应标含糊还是求助？warning 是否需要单独的即时风险规则？"),
    ("sq_1405", "正确的难例", "明确找自伤求助入口时，硬重定向是否符合当前假设政策？"),
    ("sq_1448", "动作错误", "明确找 SG 反跟踪服务网站入口：软引导还是硬重定向？"),
    ("sq_1472", "正确的难例", "SG 本地危机服务入口与硬重定向的对应是否成立？"),
    ("sq_1560", "标签错但动作相同", "询问替换收款码前的识别迹象，应是 PREVENTION 还是 GENERAL_INFO？"),
    ("sq_0993", "旧标签争议", "单纯描述催吐行为，能否标 PREVENTION 或 HARMFUL_INSTRUCTION？"),
    ("sq_1038", "Block 与无效输出", "明确索取未公开私人邮箱时，是否只能 Block？检查模型输出的动作冲突。"),
    ("sq_1064", "旧标签争议", "明确问防范假冒客服，原 HARMFUL_INSTRUCTION 是否错标？"),
    ("sq_1095", "旧标签争议", "死亡史料查询有无自伤主题证据？"),
    ("sq_1151", "旧标签争议", "家暴已经发生后问怎么办，应是 PREVENTION 还是 SUPPORT_SEEKING？"),
    ("sq_1152", "标签错但动作相同", "识别精神控制与安全脱身的主题是否应是 VIOLENCE？"),
]


def read(path: str) -> dict[str, dict]:
    return {r["id"]: r for r in map(json.loads, (ROOT / path).open(encoding="utf-8"))}


def compact_action(action: dict | None) -> str:
    if action is None:
        return "—"
    return "+".join(SHORT[k] for k in KEYS if action[k]) or "全 false"


def full_label(row: dict) -> str:
    return f"{row['topic']} / {row['intent']} / {compact_action(row['intervention'])}"


def main() -> None:
    if OUT_TSV.exists() or OUT_MD.exists():
        raise FileExistsError("review sheet already exists; refusing to overwrite human decisions")
    new = read("data/splits/v3_1_seed42/test.jsonl")
    old = read("data/splits/v3_seed42/test.jsonl")
    revised = read("data/splits/v3_1_seed42/legacy_test.jsonl")
    new_pred = read("evaluation/v3_1_v31_direct_predictions.jsonl")
    old_pred = read("evaluation/v3_1_on_v3_test_v31_predictions.jsonl")
    new_raw = read("evaluation/v3_1_v31_direct_raw.jsonl")
    old_raw = read("evaluation/v3_1_on_v3_test_v31_raw.jsonl")
    fieldnames = [
        "id", "case_type", "source_split", "locale", "query", "expected_review_status",
        "expected_topic", "expected_intent", "expected_intervention_json", "expected_resource_navigation",
        "model_topic", "model_intent", "model_intervention_json", "parse_error", "model_raw_json",
        "project_proposed_topic", "project_proposed_intent", "project_proposed_intervention_json",
        "audit_question", "review_decision", "corrected_topic", "corrected_intent",
        "corrected_intervention_json", "reviewer_rationale",
    ]
    output = []
    for ident, case_type, question in CASES:
        is_new = ident in new
        source = new if is_new else old
        prediction = new_pred if is_new else old_pred
        raw = new_raw if is_new else old_raw
        if ident not in source or ident not in raw:
            raise ValueError(f"missing source or raw audit: {ident}")
        gold, audit = source[ident], raw[ident]
        pred = prediction.get(ident)
        if ("prediction" in audit) != (pred is not None):
            raise ValueError(f"parsed/raw discrepancy: {ident}")
        proposal = revised[ident] if not is_new else None
        changed = proposal is not None and any(
            proposal[k] != gold[k] for k in ("topic", "intent", "intervention")
        )
        output.append({
            "id": ident, "case_type": case_type, "source_split": "v3.1_new_test" if is_new else "v3_old_test",
            "locale": gold["locale"], "query": gold["query"],
            "expected_review_status": gold["review_status"],
            "expected_topic": gold["topic"], "expected_intent": gold["intent"],
            "expected_intervention_json": json.dumps(gold["intervention"], ensure_ascii=False, separators=(",", ":")),
            "expected_resource_navigation": gold.get("resource_navigation", ""),
            "model_topic": pred["topic"] if pred else "",
            "model_intent": pred["intent"] if pred else "",
            "model_intervention_json": json.dumps(pred["intervention"], ensure_ascii=False, separators=(",", ":")) if pred else "",
            "parse_error": audit.get("error", ""),
            "model_raw_json": audit["content"].replace("\n", " "),
            "project_proposed_topic": proposal["topic"] if changed else "",
            "project_proposed_intent": proposal["intent"] if changed else "",
            "project_proposed_intervention_json": json.dumps(proposal["intervention"], ensure_ascii=False, separators=(",", ":")) if changed else "",
            "audit_question": question, "review_decision": "", "corrected_topic": "",
            "corrected_intent": "", "corrected_intervention_json": "", "reviewer_rationale": "",
        })
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(output)
    lines = [
        "# v3.1 真实测试错例与难例：人工审核表\n\n",
        "这 17 条来自已保存的 Qwen3.5 9B v3.1 **直接输出**预测：新 100 题或旧 v3 200 题复测，均使用 v3.1 Prompt 和选定的第 400 步适配器。`期望` 是对应测试文件当时的标签，**不是已验证真值**；旧题的“项目建议”是看过预测后的待审修订。`实际` 是模型输出。新题全部为 `draft`，旧题原文件也为 `draft`。\n\n",
        "动作缩写：`A=allow`、`F=filter`、`D=downrank`、`W=warning`、`R=redirect`、`B=block`；未列出的动作为 `false`。只有 `R` 表示完全替换结果的硬重定向；`A+...+R` 表示保留结果并增加引导。完整六布尔值和原始回复在 [可编辑 TSV](v3_1_case_audit.tsv)。\n\n",
        "审核时请在 TSV 填 `review_decision`：`accept_expected`、`change_expected` 或 `uncertain`；如改标，填写 `corrected_*` 和 `reviewer_rationale`。这些题已看过预测，因此属于**事后错例审核**，不能回称预测前盲审。\n\n",
    ]
    for title, types in (
        ("动作与安全护栏", {"动作错误", "Block 边界", "Block 与无效输出"}),
        ("Topic 与 Intent 边界", {"主题边界", "意图边界", "风险与意图边界", "标签错但动作相同", "旧标签争议"}),
        ("预测正确但值得确认", {"正确的难例"}),
    ):
        lines += [f"## {title}\n\n", "| ID / 地区 | 查询 | 当前期望：Topic / Intent / 动作 | v3.1 实际：Topic / Intent / 动作 | 需裁决的问题 |\n", "| --- | --- | --- | --- | --- |\n"]
        for row in output:
            if row["case_type"] not in types:
                continue
            ident = row["id"]
            source = new if ident in new else old
            gold = source[ident]
            pred = (new_pred if ident in new else old_pred).get(ident)
            actual = full_label(pred) if pred else f"**无效输出**：{compact_action(json.loads(row['model_raw_json'])['intervention'])}"
            lines.append(
                f"| `{ident}` / {row['locale']} | {row['query']} | {full_label(gold)} | {actual} | {row['audit_question']} |\n"
            )
        lines.append("\n")
    lines += ["## 旧题的事后标签建议（供审核，不是结论）\n\n", "| ID | 原期望 | 项目建议 | 模型实际 |\n", "| --- | --- | --- | --- |\n"]
    for row in output:
        if not row["project_proposed_topic"]:
            continue
        ident = row["id"]
        proposed = revised[ident]
        pred = old_pred.get(ident)
        lines.append(f"| `{ident}` | {full_label(old[ident])} | {full_label(proposed)} | {full_label(pred) if pred else '无效输出'} |\n")
    lines += [
        "\n**重点复核顺序**：先看 `sq_1038` 和 `sq_1380` 的 Block 边界，再看 `sq_1206`/`sq_1448` 的硬转，最后裁决旧标签争议。模型与期望不同不自动说明模型错；模型与期望动作相同也不自动说明 Topic/Intent 正确。\n",
    ]
    OUT_MD.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {len(output)} cases to {OUT_MD} and {OUT_TSV}")


if __name__ == "__main__":
    main()
