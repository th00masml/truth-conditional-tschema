"""Regression test for the decode mask, runnable without MLX (numpy stub).

Simulates greedy decoding with an adversarial "model" that always prefers the
quote token, the failure that produced repeated quote+capital output in the first run. Checks
both conventions for the `tokens` argument mlx_lm may pass to processors.
"""
import sys
import types
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class _Arr(np.ndarray):
    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            key = tuple(np.asarray(k) if isinstance(k, _Arr) else k for k in key)
        super().__setitem__(key, value)


mx = types.ModuleType("mlx.core")
mx.uint32 = np.int64
mx.full = lambda shape, v, dtype=None: np.full(shape, v, dtype=np.float64).view(_Arr)
mx.array = lambda x, dtype=None: np.asarray(x, dtype=np.int64).view(_Arr)
sys.modules.setdefault("mlx", types.ModuleType("mlx"))
sys.modules["mlx.core"] = mx

from constraint import TSchemaSetConstraint  # noqa: E402
from mlx_binding import TSchemaSetLogitsProcessor  # noqa: E402

PIECES = {0: b'"', 1: b'C', 2: b'oal', 3: b' is', 4: b' dark', 5: b' true', 6: b' iff', 7: b'.', 8: b'"C', 9: b'Snow', 10: b' white', 11: b' '}
EOS = 12
VALUES = {'"Coal is dark" is true iff Coal is dark.', '"Snow is white" is true iff Snow is white.'}
PREFERENCE = [0, 8, 1, 7, 2, 3, 4, 5, 6, 9, 10, 11, EOS]  # quotes first, EOS last


def decode(include_prompt: bool):
    proc = TSchemaSetLogitsProcessor(TSchemaSetConstraint(VALUES, PIECES), 5, [EOS])
    prompt = [99] * 5
    out = []
    for _ in range(40):
        tokens = mx.array(prompt + out if include_prompt else out)
        logits = mx.full((1, 13), 0.0)
        logits[0, :] = -np.arange(13)[np.argsort(PREFERENCE)]
        tok = int(np.argmax(proc(tokens, logits)[0]))
        if tok == EOS:
            break
        out.append(tok)
    return b"".join(PIECES[t] for t in out)


def test_generated_only_tokens():
    assert decode(False).decode() in VALUES


def test_prompt_plus_generated_tokens():
    assert decode(True).decode() in VALUES


if __name__ == "__main__":
    test_generated_only_tokens()
    test_prompt_plus_generated_tokens()
    print("mask regression: ok", decode(False))
