"""Run the v2 policy prompt against an OpenAI-compatible local model server."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from schema_v2 import ACTION_KEYS, INTENTS, TOPICS, read_jsonl


def classify_response(content: str) -> dict:
    prediction = json.loads(content)
    if not isinstance(prediction, dict) or set(prediction) != {"topic", "intent", "intervention"}:
        raise ValueError(f"unexpected top-level fields: {prediction!r}")
    if prediction["topic"] not in TOPICS or prediction["intent"] not in INTENTS:
        raise ValueError(f"unknown topic or intent: {prediction!r}")
    actions = prediction["intervention"]
    if not isinstance(actions, dict) or set(actions) != set(ACTION_KEYS):
        raise ValueError(f"unexpected intervention fields: {actions!r}")
    if any(type(actions[key]) is not bool for key in ACTION_KEYS):
        raise ValueError(f"non-boolean action: {actions!r}")
    return prediction


def request_prediction(url: str, model: str, prompt: str, row: dict, max_tokens: int, timeout: int) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"locale={row['locale']}\nquery={row['query']}"},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    request = Request(url.rstrip("/") + "/chat/completions",
                      data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                      headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=timeout) as response:
        raw = json.load(response)
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("predictions")
    parser.add_argument("--raw", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt", default="prompts/query_intervention_zero_shot_v2.txt")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    parser.add_argument("--max-tokens", type=int, default=240)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    rows = read_jsonl(args.data)
    if args.limit:
        rows = rows[:args.limit]
    prompt = Path(args.prompt).read_text(encoding="utf-8")
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    prediction_path, raw_path = Path(args.predictions), Path(args.raw)
    prediction_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if prediction_path.exists() or raw_path.exists():
        parser.error("output exists; use a new run name")
    success = 0
    with prediction_path.open("w", encoding="utf-8") as predictions, raw_path.open("w", encoding="utf-8") as audit_log:
        for index, row in enumerate(rows, 1):
            start = time.monotonic()
            audit = {"id": row["id"], "model": args.model, "prompt_sha256": digest,
                     "utc_time": datetime.now(timezone.utc).isoformat(), "temperature": 0,
                     "max_tokens": args.max_tokens, "locale": row["locale"]}
            try:
                raw = request_prediction(args.base_url, args.model, prompt, row, args.max_tokens, args.timeout)
                audit["response"] = raw
                prediction = classify_response(raw["choices"][0]["message"]["content"])
                audit["prediction"] = prediction
                predictions.write(json.dumps({"id": row["id"], **prediction}, ensure_ascii=False) + "\n")
                predictions.flush()
                success += 1
                status = "ok"
            except Exception as exc:
                audit["error"] = f"{type(exc).__name__}: {exc}"
                status = "error"
            audit["elapsed_seconds"] = round(time.monotonic() - start, 3)
            audit_log.write(json.dumps(audit, ensure_ascii=False) + "\n")
            audit_log.flush()
            if index % 10 == 0 or status == "error" or index == len(rows):
                print(f"{index}/{len(rows)} {row['id']} {status} {audit['elapsed_seconds']}s", flush=True)
    print(f"Completed {success}/{len(rows)}; predictions={prediction_path}; raw={raw_path}")
    return 0 if success == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
