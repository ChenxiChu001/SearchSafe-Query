"""Freeze a separate v3.1 corpus; preserve every v3 source file unchanged."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from generate_v3_1_queries import OUT as GENERATED, quotas, cell_key
from policy_v3_1 import action_for
from schema_v3_1 import read_jsonl, validate_dataset

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "data/canonical/training_candidates_v3_draft.jsonl"
SOURCE_SPLITS = ROOT / "data/splits/v3_seed42"
CANONICAL = ROOT / "data/canonical/training_candidates_v3_1.jsonl"
SPLITS = ROOT / "data/splits/v3_1_seed42"
LEDGER = ROOT / "review/revisions_v3_1.tsv"

# These are project-proposed corrections to the user's accepted v3 labels.
# They remain draft until the user reviews them. The original v3 rows are retained.
REVISIONS: dict[str, tuple[str, str, str]] = {}


def revise(ids: str, topic: str, intent: str, evidence: str) -> None:
    for item in ids.split():
        if item in REVISIONS:
            raise ValueError(f"duplicate revision {item}")
        REVISIONS[item] = topic, intent, evidence


revise("sq_0633 sq_0635 sq_0636 sq_0638 sq_0639 sq_0641 sq_0642 sq_0643 sq_0645 sq_0646 sq_0648 sq_0651 sq_0653 sq_0654 sq_0656", "NONE", "GENERAL_INFO", "普通情绪或心理健康表述，没有明确自伤线索")
revise("sq_0923 sq_0924 sq_0925 sq_0926 sq_0938 sq_1087 sq_1088 sq_1089 sq_1090 sq_1091 sq_1092 sq_1093", "NONE", "GENERAL_INFO", "普通情绪或日常片段，没有明确自伤线索")
revise("sq_1095 sq_1101", "NONE", "GENERAL_INFO", "死亡历史或诗词查询，无自伤语境")
revise("sq_1156 sq_1157", "NONE", "GENERAL_INFO", "名誉或噪音争议，未出现本版暴力边界")
revise("sq_0637 sq_0707 sq_0709 sq_0710 sq_0713 sq_0720 sq_0722", "SELF_HARM", "SUPPORT_SEEKING", "当前自伤风险或具体求助需求，非事前预防或含糊")
revise("sq_0721", "NONE", "GENERAL_INFO", "心理咨询费用求助，无明确自伤线索")
revise("sq_0591 sq_1077", "SCAM", "SUPPORT_SEEKING", "已有疑似诈骗损失，询问报警或退款")
revise("sq_0957 sq_0959 sq_1150 sq_1151 sq_1153 sq_1154 sq_1155", "VIOLENCE", "SUPPORT_SEEKING", "当前或已发生人身风险，询问应对或求助")
revise("sq_0965 sq_0966 sq_0967 sq_0969 sq_0971", "EATING_DISORDER_RISK", "GENERAL_INFO", "询问风险事实、原因或后果，未请求预防步骤")
revise("sq_0968", "EATING_DISORDER_RISK", "SUPPORT_SEEKING", "明确询问如何帮助出现暴食倾向的人")
revise("sq_0989 sq_0990 sq_0992 sq_0993 sq_0994", "EATING_DISORDER_RISK", "AMBIGUOUS", "只陈述饮食风险症状或行为，未提出事前预防请求")
revise("sq_0991", "EATING_DISORDER_RISK", "GENERAL_INFO", "询问极端限食的后果")
revise("sq_1053", "SCAM", "GENERAL_INFO", "询问具体转账链接是否安全，目的清楚")
revise("sq_1059 sq_1060 sq_1061 sq_1062 sq_1070", "SCAM", "PREVENTION", "明确请求事前识别、核实或防范诈骗")
revise("sq_1064", "SCAM", "PREVENTION", "明确请求防范假客服诈骗，不是索取诈骗指导")
revise("sq_1065 sq_1066 sq_1067 sq_1068 sq_1069 sq_1071", "SCAM", "SUPPORT_SEEKING", "已遇到疑似诈骗，询问止损、核实或应对")
revise("sq_1112 sq_1113 sq_1114 sq_1115", "SELF_HARM", "SUPPORT_SEEKING", "已有自伤风险线索并询问引导或求助")
revise("sq_1116", "NONE", "GENERAL_INFO", "治疗绝望与调整心态，但无明确自伤线索")
revise("sq_1159", "SELF_HARM", "SUPPORT_SEEKING", "主请求是为已经自残的孩子寻求心理支持")

# New v3.1 navigation label on old support queries; also proposed revisions.
NAVIGATION_IDS = {"sq_0432", "sq_0723", "sq_0738", "sq_0741", "sq_1045", "sq_1121"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def main() -> None:
    if CANONICAL.exists() or SPLITS.exists() or LEDGER.exists():
        raise FileExistsError("v3.1 output exists; refusing to overwrite a frozen dataset")
    old = read_jsonl(OLD)
    generated = read_jsonl(GENERATED)
    target = quotas()
    if Counter(cell_key(row) for row in generated) != Counter(target):
        raise ValueError("generated queries do not match the 300 train + 100 test quota")
    old_by_id = {r["id"]: r for r in old}
    if (set(REVISIONS) | NAVIGATION_IDS) - set(old_by_id):
        raise ValueError("revision refers to missing old id")
    old_split = {}
    for split in ("train", "dev", "test"):
        for row in read_jsonl(SOURCE_SPLITS / f"{split}.jsonl"):
            old_split[row["id"]] = split
    if set(old_split) != set(old_by_id):
        raise ValueError("v3 split and canonical ids differ")
    output: dict[str, list[dict]] = {"train": [], "dev": [], "test": [], "legacy_test": []}
    ledger = []
    for original in old:
        row = dict(original)
        row["dataset_version"] = "v3.1-draft"
        row["resource_navigation"] = row["id"] in NAVIGATION_IDS
        row["review_status"] = "approved"  # user's single-review acceptance of original labels
        evidence = None
        if row["id"] in REVISIONS:
            topic, intent, evidence = REVISIONS[row["id"]]
            row["topic"], row["intent"] = topic, intent
        if row["resource_navigation"]:
            evidence = "明确寻找与当前风险直接相关的资源入口"
        if evidence:
            row["review_status"] = "draft"
            row["rationale"] = evidence
        result = action_for(row["topic"], row["intent"], row["locale"], row["resource_navigation"])
        if result is None:
            raise ValueError(f"undefined policy for {row['id']}")
        row["intervention"], row["redirect_target"] = result
        if evidence:
            ledger.append({"id": row["id"], "query": row["query"], "old_topic": original["topic"],
                           "old_intent": original["intent"], "old_resource_navigation": "absent",
                           "new_topic": row["topic"], "new_intent": row["intent"],
                           "new_resource_navigation": str(row["resource_navigation"]).lower(),
                           "reason": evidence, "proposed_by": "project review", "review_status": "draft"})
        split = old_split[row["id"]]
        output["legacy_test" if split == "test" else split].append(row)
    for n, item in enumerate(generated, start=1165):
        action = action_for(item["topic"], item["intent"], item["locale"], item["resource_navigation"])
        if action is None:
            raise ValueError(f"undefined generated policy {item}")
        row = {
            "id": f"sq_{n:04d}", "query": item["query"], "language": "zh",
            "locale": item["locale"], "source_type": "synthetic",
            "semantic_group_id": f"v31g{n-1164:04d}", "topic": item["topic"],
            "intent": item["intent"], "resource_navigation": item["resource_navigation"],
            "intervention": action[0], "redirect_target": action[1],
            "rationale": "按 v3.1 指南起草的合成查询；尚待人工复核。",
            "review_status": "draft", "dataset_version": "v3.1-draft", "origin_version": "v3.1",
        }
        output[item["split"]].append(row)
    if {s: len(rows) for s, rows in output.items()} != {"train": 1000, "dev": 100, "test": 100, "legacy_test": 200}:
        raise ValueError("unexpected v3.1 split sizes")
    all_rows = sum(output.values(), [])
    errors = validate_dataset(all_rows)
    if errors:
        raise ValueError("\n".join(errors[:50]))
    groups = {s: {r["semantic_group_id"] for r in rows} for s, rows in output.items()}
    if any(groups[a] & groups[b] for i, a in enumerate(groups) for b in list(groups)[i+1:]):
        raise ValueError("semantic group crossed split")
    CANONICAL.parent.mkdir(parents=True, exist_ok=True)
    SPLITS.mkdir(parents=True)
    dump(CANONICAL, all_rows)
    manifest = {"version": "v3.1-draft", "source": str(CANONICAL.relative_to(ROOT)),
                "source_sha256": digest(CANONICAL), "v3_source_sha256": digest(OLD),
                "generated_sha256": digest(GENERATED), "seed": 42,
                "single_review_acceptance": 1000, "proposed_revision_rows": len(ledger),
                "splits": {}}
    for split, rows in output.items():
        path = SPLITS / f"{split}.jsonl"
        dump(path, rows)
        manifest["splits"][split] = {
            "rows": len(rows), "sha256": digest(path),
            "topic": dict(Counter(r["topic"] for r in rows)),
            "intent": dict(Counter(r["intent"] for r in rows)),
            "locale": dict(Counter(r["locale"] for r in rows)),
            "review_status": dict(Counter(r["review_status"] for r in rows)),
            "hard_redirect": sum(r["resource_navigation"] for r in rows),
        }
    (SPLITS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(ledger[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(ledger)
    print(f"Frozen {len(all_rows)} v3.1 rows; {len(ledger)} proposed revisions")
    print(json.dumps(manifest["splits"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
