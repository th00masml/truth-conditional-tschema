"""Dependency-free byte trie for exact T-schema set membership."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Node:
    children: dict[int, "Node"] = field(default_factory=dict)
    terminal: bool = False


class TSchemaSetConstraint:
    def __init__(self, values: set[str], token_bytes: dict[int, bytes]):
        self.root = Node()
        for value in values:
            node = self.root
            for byte in value.encode("utf-8"):
                node = node.children.setdefault(byte, Node())
            node.terminal = True
        self.token_bytes = {token_id: piece for token_id, piece in token_bytes.items() if piece}
        self.by_first = defaultdict(list)
        for token_id, piece in self.token_bytes.items():
            self.by_first[piece[0]].append((token_id, piece))

    def node_for(self, prefix: bytes) -> Node | None:
        node = self.root
        for byte in prefix:
            node = node.children.get(byte)
            if node is None:
                return None
        return node

    def accepts(self, output: bytes) -> bool:
        if output == b"":
            return True
        node = self.node_for(output)
        return bool(node and node.terminal)

    def allowed(self, prefix: bytes) -> set[int]:
        node = self.node_for(prefix)
        if node is None:
            return set()
        result = set()
        for first, child in node.children.items():
            for token_id, piece in self.by_first[first]:
                cursor = child
                for byte in piece[1:]:
                    cursor = cursor.children.get(byte) if cursor else None
                    if cursor is None:
                        break
                if cursor is not None:
                    result.add(token_id)
        return result

    def naive_allowed(self, prefix: bytes) -> set[int]:
        return {token_id for token_id, piece in self.token_bytes.items() if self.node_for(prefix + piece) is not None}


def self_test() -> None:
    pieces = {
        0: b'"',
        1: b'Snow',
        2: b' ',
        3: b'is',
        4: b' true',
        5: b' iff',
        6: b'.',
        7: b'X',
    }
    values = {'"Snow is white" is true iff Snow is white.'}
    constraint = TSchemaSetConstraint(values, pieces)
    states = {b""}
    for _ in range(6):
        future = set()
        for state in states:
            assert constraint.allowed(state) == constraint.naive_allowed(state)
            future |= {state + pieces[i] for i in constraint.allowed(state)}
        states = future
    assert constraint.accepts(b'')
    assert not constraint.accepts(b'X')
    print("t-schema matcher differential mismatches: 0")


if __name__ == "__main__":
    self_test()
