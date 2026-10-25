"""Deterministic fixtures for canonical T-schema generation."""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "fixtures.jsonl"

SUPPORTED_SUBJECTS = [
    "Snow",
    "Grass",
    "Sky",
    "Fire",
    "Water",
    "Salt",
    "Coal",
    "Honey",
    "Steel",
    "Cloud",
]

UNSUPPORTED_SUBJECTS = [
    "Copper",
    "Marble",
    "Sand",
    "River",
    "Ash",
    "Leaf",
    "Smoke",
    "Frost",
    "Rain",
    "Stone",
]

PREDICATES = ["white", "green", "blue", "hot", "wet", "cold", "bright", "dark"]


def proposition(subject: str, predicate: str) -> str:
    return f"{subject} is {predicate}"


def schema(prop: str) -> str:
    return f'"{prop}" is true iff {prop}.'


def make_source(subject: str, predicate: str) -> str:
    supported_subjects = ", ".join(SUPPORTED_SUBJECTS)
    supported_predicates = ", ".join(PREDICATES)
    return (
        "LANGUAGE INVENTORY\n"
        f"Supported subjects: {supported_subjects}.\n"
        f"Supported predicates: {supported_predicates}.\n"
        "A sentence is in inventory iff its subject and predicate are both supported.\n"
        "If out of inventory, output empty.\n\n"
        f"TARGET SENTENCE: {subject} is {predicate}."
    )


def main() -> None:
    present = list(product(SUPPORTED_SUBJECTS, PREDICATES))
    absent = list(product(UNSUPPORTED_SUBJECTS, PREDICATES))
    assert len(present) == 80 and len(absent) == 80

    rows = []
    index = 1
    for (ps, pp), (asub, ap) in zip(present, absent):
        p_prop = proposition(ps, pp)
        rows.append(
            {
                "id": f"tschema_{index:04d}",
                "present": True,
                "subject": ps,
                "predicate": pp,
                "source": make_source(ps, pp),
                "query": "Output exactly one canonical T-sentence for the target sentence. No commentary.",
                "gold": schema(p_prop),
            }
        )
        index += 1

        a_prop = proposition(asub, ap)
        rows.append(
            {
                "id": f"tschema_{index:04d}",
                "present": False,
                "subject": asub,
                "predicate": ap,
                "source": make_source(asub, ap),
                "query": "Output exactly one canonical T-sentence for the target sentence. No commentary.",
                "gold": "",
            }
        )
        index += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")

    print(f"wrote {len(rows)} fixtures")


if __name__ == "__main__":
    main()
