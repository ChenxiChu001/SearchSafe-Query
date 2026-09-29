"""Build a blind review sheet from paired candidate samples."""

import argparse
from collections import defaultdict
from pathlib import Path

from schema import read_jsonl, validate_dataset


def escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("output")
    args = parser.parse_args()
    records = read_jsonl(args.data)
    errors = validate_dataset(records)
    if errors:
        print("\n".join(errors))
        return 1
    groups = defaultdict(dict)
    for row in records:
        groups[row["semantic_group_id"]][row["language"]] = row
    lines = [
        "# 48 条候选样例盲复核表",
        "",
        "逐组阅读中英查询，先独立填写 Topic、Intent、Triage 和争议点，再对照 `data/canonical/candidates_v0.jsonl` 中的提议标签。",
        "Topic 可选：`NONE`、`SELF_HARM`、`EATING_DISORDER_RISK`、`VIOLENCE`、`SCAM`。",
        "Intent 可选：`GENERAL_INFO`、`PREVENTION`、`SUPPORT_SEEKING`、`HARMFUL_INSTRUCTION`、`AMBIGUOUS`。",
        "Triage 可选：`ALLOW`、`SUPPORT`、`REVIEW`。有争议时写明缺少的上下文，不要勉强通过。",
        "",
        "| 组和 ID | English query | 中文查询 | 你的 Topic | 你的 Intent | 你的 Triage | 争议或修改 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for group_id in sorted(groups, key=lambda x: int(x[1:])):
        pair = groups[group_id]
        en = pair.get("en")
        zh = pair.get("zh")
        if not en or not zh:
            raise ValueError(f"{group_id}: expected en and zh pair")
        lines.append(f"| {group_id} / {en['id']} / {zh['id']} | {escape(en['query'])} | {escape(zh['query'])} |  |  |  |  |")
    lines += [
        "",
        "复核完成后：逐条修订 JSONL，再运行 `python3 scripts/validate_dataset.py data/canonical/candidates_v0.jsonl`。",
        "只有完成争议裁决的样例才可以改为 `approved`；如果仍有分歧，保留 `draft`。",
        "",
    ]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(groups)} bilingual groups to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
