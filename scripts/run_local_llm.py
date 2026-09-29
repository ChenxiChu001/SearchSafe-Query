"""Run a reproducible zero-shot prompt against a local LM Studio server."""

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from schema import INTENTS, TOPICS, TRIAGE, read_jsonl

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string", "enum": sorted(TOPICS)},
        "intent": {"type": "string", "enum": sorted(INTENTS)},
        "triage": {"type": "string", "enum": sorted(TRIAGE)},
    },
    "required": ["topic", "intent", "triage"],
    "additionalProperties": False,
}


def request_prediction(base_url: str, model: str, prompt: str, query: str,
                       max_tokens: int, timeout: int, structured: bool) -> tuple[dict, dict]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    if structured:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "query_triage", "strict": True, "schema": OUTPUT_SCHEMA},
        }
    request = Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        raw = json.load(response)
    content = raw["choices"][0]["message"]["content"]
    try:
        prediction = json.loads(content)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not parse content as JSON: {content!r}; raw={raw!r}") from exc
    if not isinstance(prediction, dict) or set(prediction) != {"topic", "intent", "triage"}:
        raise ValueError(f"unexpected fields: {prediction!r}")
    for field, allowed in (("topic", TOPICS), ("intent", INTENTS), ("triage", TRIAGE)):
        if prediction[field] not in allowed:
            raise ValueError(f"invalid {field}: {prediction[field]!r}")
    return prediction, raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("predictions")
    parser.add_argument("--raw", required=True, help="JSONL audit log")
    parser.add_argument("--model", required=True, help="loaded LM Studio model identifier")
    parser.add_argument("--prompt", default="prompts/query_triage_zero_shot_v0.txt")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--max-tokens", type=int, default=400)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--structured", action="store_true", help="request JSON Schema constrained output")
    args = parser.parse_args()

    records = read_jsonl(args.data)
    if args.limit:
        records = records[:args.limit]
    prompt = Path(args.prompt).read_text(encoding="utf-8")
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    predictions_path = Path(args.predictions)
    raw_path = Path(args.raw)
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if predictions_path.exists() or raw_path.exists():
        parser.error("output path already exists; choose a new run name")

    succeeded = 0
    with predictions_path.open("w", encoding="utf-8") as predictions_file, raw_path.open("w", encoding="utf-8") as raw_file:
        for index, record in enumerate(records, 1):
            started = time.monotonic()
            audit = {
                "id": record["id"], "model": args.model, "prompt_sha256": prompt_sha256,
                "utc_time": datetime.now(timezone.utc).isoformat(),
                "temperature": 0, "max_tokens": args.max_tokens, "structured": args.structured,
            }
            try:
                prediction, raw = request_prediction(args.base_url, args.model, prompt,
                                                     record["query"], args.max_tokens, args.timeout,
                                                     args.structured)
                audit["prediction"] = prediction
                audit["response"] = raw
                predictions_file.write(json.dumps({"id": record["id"], **prediction}, ensure_ascii=False) + "\n")
                predictions_file.flush()
                succeeded += 1
                status = "ok"
            except (ValueError, KeyError, HTTPError, URLError, TimeoutError) as exc:
                audit["error"] = f"{type(exc).__name__}: {exc}"
                status = "error"
            audit["elapsed_seconds"] = round(time.monotonic() - started, 3)
            raw_file.write(json.dumps(audit, ensure_ascii=False) + "\n")
            raw_file.flush()
            print(f"{index}/{len(records)} {record['id']} {status} {audit['elapsed_seconds']}s", flush=True)
    print(f"Completed {succeeded}/{len(records)}; predictions={predictions_path}; audit={raw_path}")
    return 0 if succeeded == len(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
