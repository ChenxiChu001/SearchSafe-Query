"""Intentionally naive keyword baseline to expose overblocking."""

import argparse
import json
from pathlib import Path

from schema import read_jsonl

KEYWORDS = {
    "SELF_HARM": ("self-harm", "hurt myself", "hurt themselves", "自伤", "伤害自己"),
    "EATING_DISORDER_RISK": ("disordered eating", "extreme diet", "restrict meals", "eating disorder", "饮食失调", "极端节食", "限制进食"),
    "VIOLENCE": ("violence", "violent", "hurt someone", "threatened to hurt", "暴力", "伤害别人", "威胁伤害"),
    "SCAM": ("scam", "fake seller", "fake job", "suspicious seller", "诈骗", "骗局", "虚假招聘", "可疑卖家", "假卖家"),
}


def predict(query: str) -> dict[str, str]:
    lowered = query.casefold()
    for topic, words in KEYWORDS.items():
        if any(word in lowered for word in words):
            return {"topic": topic, "intent": "HARMFUL_INSTRUCTION", "triage": "REVIEW"}
    return {"topic": "NONE", "intent": "GENERAL_INFO", "triage": "ALLOW"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("output")
    args = parser.parse_args()
    records = read_jsonl(args.data)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            prediction = {"id": record["id"], **predict(record["query"])}
            handle.write(json.dumps(prediction, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} keyword predictions to {output}")


if __name__ == "__main__":
    main()
