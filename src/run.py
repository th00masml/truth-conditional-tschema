"""Five-arm greedy MLX evaluation for T-schema generation."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step

from constraint import TSchemaSetConstraint
from mlx_binding import TSchemaSetLogitsProcessor, vocabulary_bytes

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data" / "fixtures.jsonl"
OUT = ROOT / "outputs" / "raw.jsonl"
MODELS = "mlx-community/Qwen2.5-0.5B-Instruct-4bit,mlx-community/Qwen2.5-1.5B-Instruct-4bit"
INSTRUCTIONS = {
    "naive": "Answer the question from the language inventory card.",
    "prompted": "Output exactly one canonical T-sentence in the form \"P\" is true iff P. Output empty if out of inventory.",
    "constrained": "Answer the question from the language inventory card.",
    "prompt_tuned": "Return only the canonical T-sentence for the target sentence. No extra words, no labels, no explanation. Output empty if out of inventory.",
    "constrained_tuned": "Return only the canonical T-sentence for the target sentence. No extra words, no labels, no explanation. Output empty if out of inventory.",
}


def encode(tokenizer, text: str) -> list[int]:
    if getattr(tokenizer, "has_chat_template", False):
        text = tokenizer.apply_chat_template(
            [{"role": "user", "content": text}],
            tokenize=False,
            add_generation_prompt=True,
        )
        return tokenizer.encode(text, add_special_tokens=False)
    return tokenizer.encode(text)


def run_one(model, tokenizer, item, arm, token_bytes, allowed_schemas):
    text = f"{INSTRUCTIONS[arm]}\n\nCARD:\n{item['source']}\n\nQUESTION: {item['query']}\nANSWER:"
    prompt = encode(tokenizer, text)
    processor = None
    kwargs = {"max_tokens": 64}
    if "constrained" in arm:
        processor = TSchemaSetLogitsProcessor(
            TSchemaSetConstraint(allowed_schemas, token_bytes),
            len(prompt),
            tokenizer.eos_token_ids,
        )
        kwargs["logits_processors"] = [processor]

    started = time.perf_counter()
    tokens = []
    for token, _ in generate_step(mx.array(prompt), model, **kwargs):
        if token in tokenizer.eos_token_ids:
            break
        tokens.append(token)
    elapsed = time.perf_counter() - started

    detail = {
        "decode_seconds": elapsed,
        "steps": len(tokens),
        "matcher_mismatches": 0,
    }
    if processor:
        prefix = b""
        for token in tokens:
            if processor.constraint.allowed(prefix) != processor.constraint.naive_allowed(prefix):
                detail["matcher_mismatches"] += 1
            prefix += token_bytes.get(token, b"")
        detail.update(
            {
                "mask_seconds": processor.elapsed_ns / 1e9,
                "selectivity_start": (
                    processor.trace[0]["allowed"] / processor.trace[0]["vocab"] if processor.trace else 0.0
                ),
            }
        )
    return tokenizer.decode(tokens, skip_special_tokens=True), detail


def existing_keys(path: Path) -> set[tuple[str, str, str]]:
    if not path.exists():
        return set()
    keys: set[tuple[str, str, str]] = set()
    with path.open() as handle:
        for line in handle:
            row = json.loads(line)
            keys.add((row["model"], row["arm"], row["id"]))
    return keys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default=MODELS)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if not FIXTURES.exists():
        raise SystemExit("Run src/fixtures.py first.")

    items = [json.loads(line) for line in FIXTURES.open()]
    if args.limit:
        items = items[: args.limit]

    allowed_schemas = {row["gold"] for row in items if row["present"] and row["gold"]}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    seen = set() if args.overwrite else existing_keys(OUT)
    mode = "w" if args.overwrite else "a"

    with OUT.open(mode) as handle:
        for model_id in args.models.split(","):
            print(f"loading {model_id}", flush=True)
            model, tokenizer = load(model_id)
            token_bytes = vocabulary_bytes(tokenizer)
            for arm in INSTRUCTIONS:
                total = len(items)
                done = 0
                for item in items:
                    key = (model_id, arm, item["id"])
                    if key in seen:
                        done += 1
                        continue
                    output, detail = run_one(model, tokenizer, item, arm, token_bytes, allowed_schemas)
                    row = {"model": model_id, "arm": arm, **item, "output": output, **detail}
                    handle.write(json.dumps(row) + "\n")
                    handle.flush()
                    done += 1
                    print(f"{model_id} {arm} {done}/{total}", flush=True)


if __name__ == "__main__":
    main()
