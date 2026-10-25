"""Apple MLX binding for T-schema set-constrained decoding."""
from __future__ import annotations

from time import perf_counter_ns

import mlx.core as mx

from constraint import TSchemaSetConstraint


class TSchemaSetLogitsProcessor:
    def __init__(self, constraint: TSchemaSetConstraint, prompt_length: int, eos_token_ids: list[int]):
        self.constraint = constraint
        self.prompt_length = prompt_length
        self.eos_token_ids = set(eos_token_ids)
        self.elapsed_ns = 0
        self.trace: list[dict[str, int]] = []

    def __call__(self, tokens: mx.array, logits: mx.array) -> mx.array:
        started = perf_counter_ns()
        prefix = b"".join(self.constraint.token_bytes.get(token, b"") for token in tokens.tolist()[self.prompt_length:])
        allowed = self.constraint.allowed(prefix) | self.eos_token_ids
        self.trace.append({"allowed": len(allowed), "vocab": logits.shape[-1]})
        masked = mx.full(logits.shape, -float("inf"), dtype=logits.dtype)
        masked[0, mx.array(sorted(allowed), dtype=mx.uint32)] = 0
        self.elapsed_ns += perf_counter_ns() - started
        return logits + masked


def vocabulary_bytes(tokenizer) -> dict[int, bytes]:
    return {
        token_id: tokenizer.decode([token_id], skip_special_tokens=False).encode("utf-8")
        for token_id in range(tokenizer.vocab_size)
    }
