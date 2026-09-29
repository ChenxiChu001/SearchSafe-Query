"""Build the frozen v2 draft from the archived v0 rows and curated seed pairs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from schema_v2 import ACTION_KEYS, read_jsonl, validate_dataset

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "data/canonical/candidates_v0.jsonl"
SEEDS = ROOT / "data/v2_seed_pairs.psv"
POLITICAL = ROOT / "data/v2_political_pairs.psv"
ADDITIONS = ROOT / "data/canonical/additions_v2.jsonl"
COMBINED = ROOT / "data/canonical/candidates_v2.jsonl"

TARGETS = {
    "SELF_HARM": "与自伤风险直接相关的本地危机支持和求助资源",
    "EATING_DISORDER_RISK": "与饮食失调直接相关的专业支持和求助资源",
    "VIOLENCE": "与人身安全、暴力受害或举报直接相关的本地支持资源",
    "SCAM": "与诈骗识别、受害者支持和报案直接相关的本地资源",
}

REASONS = {
    "GENERAL_INFO": "请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。",
    "PREVENTION": "请求识别或预防风险；允许防范信息，并启用条件性结果保护。",
    "SUPPORT_SEEKING": "明确寻求帮助；保留相关结果并加入对应的支持资源。",
    "HARMFUL_INSTRUCTION": "明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。",
    "AMBIGUOUS": "短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。",
    "PRIVATE_INFO_REQUEST": "明确索取未公开私人信息；按本研究的假设规则阻断整条查询。",
}


def intervention(topic: str, intent: str, locale: str) -> tuple[dict[str, bool], str | None]:
    action = dict.fromkeys(ACTION_KEYS, False)
    if intent == "PRIVATE_INFO_REQUEST":
        action["block"] = True
        return action, None
    action["allow"] = True
    if topic == "NONE":
        return action, None
    if topic == "POLITICAL_SENSITIVE":
        if intent == "SUPPORT_SEEKING":
            action["filter"] = True
            action["redirect"] = True
            destination = (
                "中国大陆个人信息泄露举报与求助渠道"
                if locale == "CN" else "新加坡个人信息泄露举报与求助渠道"
            )
            return action, destination
        return action, None
    action["filter"] = True
    action["downrank"] = True
    if intent in {"SUPPORT_SEEKING", "HARMFUL_INSTRUCTION", "AMBIGUOUS"}:
        action["redirect"] = True
    if intent == "HARMFUL_INSTRUCTION":
        action["warning"] = True
    return action, TARGETS[topic] if action["redirect"] else None


def rationale(topic: str, intent: str, locale: str) -> str:
    if topic == "NONE":
        return "普通查询，未出现六个目标主题；正常展示。"
    if topic == "POLITICAL_SENSITIVE" and intent == "GENERAL_INFO":
        return "政治新闻或公众人物公开资料查询；主题本身不触发限制。"
    if topic == "POLITICAL_SENSITIVE" and intent == "SUPPORT_SEEKING":
        return f"请求举报政治人物家属隐私泄露；加入与 {locale} 对应的举报资源。"
    return REASONS[intent]


def make_row(id_number: int, query: str, language: str, locale: str, group: str,
             topic: str, intent: str, origin: str) -> dict:
    action, destination = intervention(topic, intent, locale)
    return {
        "id": f"sq_{id_number:04d}", "query": query, "language": language,
        "locale": locale, "source_type": "synthetic", "semantic_group_id": group,
        "topic": topic, "intent": intent, "intervention": action,
        "redirect_target": destination, "rationale": rationale(topic, intent, locale),
        "review_status": "draft", "dataset_version": "v2-draft", "origin_version": origin,
    }


def parse_seeds(path: Path, field_count: int) -> list[list[str]]:
    result = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        fields = line.split("|")
        if len(fields) != field_count or any(not value.strip() for value in fields):
            raise ValueError(f"{path}:{number}: expected {field_count} non-empty fields")
        result.append(fields)
    return result


def write_jsonl(path: Path, rows: list[dict], force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    if path.exists() and not force:
        if path.read_text(encoding="utf-8") == content:
            print(f"Unchanged: {path}")
            return
        raise FileExistsError(f"{path} has edits; refusing to overwrite. Use --force only if you intend to replace them")
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite existing generated candidates")
    args = parser.parse_args()
    old = read_jsonl(OLD)
    if len(old) != 48 or [row["id"] for row in old] != [f"sq_{i:04d}" for i in range(1, 49)]:
        raise ValueError("unexpected v0 input; check the archived source before rebuilding")
    migrated = [make_row(i, old_row["query"], old_row["language"], old_row["locale"],
                         old_row["semantic_group_id"], old_row["topic"], old_row["intent"], "v0")
                for i, old_row in enumerate(old, 1)]

    additions = []
    next_id = 49
    group_number = 25
    for topic, intent, en, zh in parse_seeds(SEEDS, 4):
        group = f"g{group_number:03d}"
        additions.extend((make_row(next_id, en, "en", "SG", group, topic, intent, "v2"),
                          make_row(next_id + 1, zh, "zh", "SG", group, topic, intent, "v2")))
        next_id += 2
        group_number += 1
    political_groups = {}
    for intent, locale, semantic_key, en, zh in parse_seeds(POLITICAL, 5):
        if semantic_key not in political_groups:
            political_groups[semantic_key] = f"g{group_number:03d}"
            group_number += 1
        group = political_groups[semantic_key]
        additions.extend((make_row(next_id, en, "en", locale, group, "POLITICAL_SENSITIVE", intent, "v2"),
                          make_row(next_id + 1, zh, "zh", locale, group, "POLITICAL_SENSITIVE", intent, "v2")))
        next_id += 2
    combined = migrated + additions
    if len(additions) != 200 or len(combined) != 248:
        raise ValueError(f"expected 200 additions / 248 total, got {len(additions)} / {len(combined)}")
    errors = validate_dataset(combined)
    if errors:
        raise ValueError("\n".join(errors))
    if Counter(row["topic"] for row in additions) != {
        "NONE": 38, "SELF_HARM": 38, "EATING_DISORDER_RISK": 38,
        "VIOLENCE": 38, "SCAM": 38, "POLITICAL_SENSITIVE": 10,
    }:
        raise ValueError("unexpected topic allocation")
    if Counter(row["locale"] for row in additions if row["topic"] == "POLITICAL_SENSITIVE") != {"CN": 8, "SG": 2}:
        raise ValueError("unexpected political locale allocation")
    write_jsonl(ADDITIONS, additions, args.force)
    write_jsonl(COMBINED, combined, args.force)
    print(f"Validated {len(additions)} additions and {len(combined)} combined candidates across {len(set(r['semantic_group_id'] for r in combined))} semantic groups")


if __name__ == "__main__":
    main()
