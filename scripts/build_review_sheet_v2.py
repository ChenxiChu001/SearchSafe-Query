"""Create a human review checklist from the v2 candidate JSONL."""

from __future__ import annotations

import argparse
from pathlib import Path

from schema_v2 import ACTION_KEYS, read_jsonl, validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("output")
    args = parser.parse_args()
    rows = read_jsonl(args.data)
    errors = validate_dataset(rows)
    if errors:
        raise ValueError("\n".join(errors))
    output = Path(args.output)
    if output.exists():
        parser.error("review sheet already exists; choose another path to preserve human notes")
    lines = [
        "# v2 全量人工复核表\n",
        "\n",
        "本表覆盖全部 248 条候选。逐条核对 query、topic、intent、六动作和 redirect_target；在每行的 `[ ]` 改成 `[x]` 仅表示已看过。若要修改，请记录 ID、原标签、修订标签、理由，并同步修改 JSONL 中对应行。`source_type=synthetic` 保持不变；完成裁决后才把 `review_status` 改为 `approved`。\n",
        "\n",
        "动作顺序：A=allow，F=filter，D=downrank，W=warning，R=redirect，B=block；1 表示 true。\n",
        "\n",
        "| 已看 | ID | 来源 | 组 | 地区/语言 | Query | Topic / intent | AFDWRB | Redirect target | 草稿理由 | 修订理由或争议 |\n",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n",
    ]
    for row in rows:
        action = "".join("1" if row["intervention"][key] else "0" for key in ACTION_KEYS)
        query = row["query"].replace("|", "\\|").replace("\n", " ")
        target = (row["redirect_target"] or "—").replace("|", "\\|")
        reason = row["rationale"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| [ ] | {row['id']} | {row['origin_version']} | {row['semantic_group_id']} | {row['locale']}/{row['language']} | {query} | {row['topic']} / {row['intent']} | {action} | {target} | {reason} |  |\n")
    output.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {len(rows)} review rows to {output}")


if __name__ == "__main__":
    main()
