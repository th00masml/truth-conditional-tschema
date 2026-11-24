"""Unit tests for the byte-trie T-schema constraint (pure Python)."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraint import TSchemaSetConstraint  # noqa: E402

VALUES = {
    '"Snow is white" is true iff Snow is white.',
    '"Snow is wet" is true iff Snow is wet.',
    '"Coal is dark" is true iff Coal is dark.',
}


def vocab():
    pieces = {i: bytes([b]) for i, b in enumerate(sorted({b for v in VALUES for b in v.encode()}))}
    for extra in [b'"Snow', b' is', b' true', b' iff', b' white', b' wet', b'.', b'"C', b'Coal', b'XYZ', b' is true iff']:
        pieces[len(pieces)] = extra
    return pieces


def test_accepts():
    c = TSchemaSetConstraint(VALUES, vocab())
    assert c.accepts(b"")
    for v in VALUES:
        assert c.accepts(v.encode())
        assert not c.accepts(v.encode()[:-1])  # proper prefix is not a member
        assert not c.accepts(v.encode() + b" ")


def test_allowed_matches_naive_on_random_walks():
    pieces = vocab()
    c = TSchemaSetConstraint(VALUES, pieces)
    rng = random.Random(0)
    for _ in range(200):
        prefix = b""
        while True:
            allowed = c.allowed(prefix)
            assert allowed == c.naive_allowed(prefix)
            if not allowed:
                assert c.accepts(prefix)  # only dead end is a complete member
                break
            prefix += pieces[rng.choice(sorted(allowed))]
        assert prefix.decode() in VALUES


def test_off_trie_prefix_has_no_continuations():
    c = TSchemaSetConstraint(VALUES, vocab())
    assert c.allowed(b'"C"') == set()
    assert c.node_for(b"XYZ") is None


def test_every_member_reachable_by_single_bytes():
    pieces = vocab()
    c = TSchemaSetConstraint(VALUES, pieces)
    byte_id = {p: i for i, p in pieces.items() if len(p) == 1}
    for v in VALUES:
        prefix = b""
        for b in v.encode():
            assert byte_id[bytes([b])] in c.allowed(prefix)
            prefix += bytes([b])


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("constraint unit tests: ok")
