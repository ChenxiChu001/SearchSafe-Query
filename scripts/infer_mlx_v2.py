"""Run frozen v2.1 split rows through base or adapted local Qwen3.5 9B."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler

from schema_v2 import ACTION_KEYS, INTENTS, TOPICS, read_jsonl

PROMPTS = {
    "labels": Path("prompts/query_labels_v2_1.txt"),
    "direct": Path("prompts/query_intervention_zero_shot_v2.txt"),
}


def parse_prediction(content: str, task: str) -> dict:
    prediction = json.loads(content)
    expected = {"topic", "intent"} if task == "labels" else {"topic", "intent", "intervention"}
    if not isinstance(prediction, dict) or set(prediction) != expected:
        raise ValueError(f"unexpected fields: {prediction!r}")
    if prediction["topic"] not in TOPICS or prediction["intent"] not in INTENTS:
        raise ValueError(f"unknown label: {prediction!r}")
    if task == "direct":
        action = prediction["intervention"]
        if not isinstance(action, dict) or set(action) != set(ACTION_KEYS):
            raise ValueError(f"invalid action keys: {action!r}")
        if any(type(action[key]) is not bool for key in ACTION_KEYS):
            raise ValueError(f"non-boolean action: {action!r}")
        if action["block"] and any(action[key] for key in ACTION_KEYS if key != "block"):
            raise ValueError(f"block must be exclusive: {action!r}")
        if not (action["allow"] or action["redirect"] or action["block"]):
            raise ValueError(f"no display or terminal action: {action!r}")
        if not action["allow"] and action["redirect"] and (action["filter"] or action["downrank"]):
            raise ValueError(f"hard redirect cannot process replaced results: {action!r}")
    return prediction


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("predictions")
    parser.add_argument("--raw", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--adapter")
    parser.add_argument("--task", choices=sorted(PROMPTS), required=True)
    parser.add_argument("--max-tokens", type=int, default=180)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    prediction_path, raw_path = Path(args.predictions), Path(args.raw)
    if prediction_path.exists() or raw_path.exists():
        parser.error("output exists; choose a new run name")
    rows = read_jsonl(args.data)
    if args.limit:
        rows = rows[:args.limit]
    prompt = PROMPTS[args.task].read_text(encoding="utf-8").strip()
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    model, tokenizer = load(args.model, adapter_path=args.adapter)
    model.eval()
    prediction_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    ok = 0
    with prediction_path.open("w", encoding="utf-8") as prediction_file, raw_path.open("w", encoding="utf-8") as audit_file:
        for number, row in enumerate(rows, 1):
            started = time.monotonic()
            audit = {"id": row["id"], "utc_time": datetime.now(timezone.utc).isoformat(),
                     "task": args.task, "model": args.model, "adapter": args.adapter,
                     "prompt_sha256": digest, "temperature": 0, "max_tokens": args.max_tokens}
            try:
                messages = [{"role": "system", "content": prompt},
                            {"role": "user", "content": f"locale={row['locale']}\nquery={row['query']}"}]
                rendered = tokenizer.apply_chat_template(messages, tokenize=False,
                                                         add_generation_prompt=True, enable_thinking=False)
                content = generate(model, tokenizer, prompt=rendered, max_tokens=args.max_tokens,
                                   sampler=make_sampler(temp=0.0), verbose=False)
                audit["content"] = content
                prediction = parse_prediction(content, args.task)
                audit["prediction"] = prediction
                prediction_file.write(json.dumps({"id": row["id"], **prediction}, ensure_ascii=False) + "\n")
                prediction_file.flush()
                ok += 1
                status = "ok"
            except Exception as exc:
                audit["error"] = f"{type(exc).__name__}: {exc}"
                status = "error"
            audit["elapsed_seconds"] = round(time.monotonic() - started, 3)
            audit_file.write(json.dumps(audit, ensure_ascii=False) + "\n")
            audit_file.flush()
            if number % 10 == 0 or status == "error" or number == len(rows):
                print(f"{number}/{len(rows)} {row['id']} {status} {audit['elapsed_seconds']}s", flush=True)
    print(f"Completed {ok}/{len(rows)}; predictions={prediction_path}; audit={raw_path}")
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
