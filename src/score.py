"""Score T-schema validity and proposition correctness separately."""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "outputs" / "raw.jsonl"
SCORED = ROOT / "outputs" / "scored.jsonl"
SUMMARY = ROOT / "outputs" / "summary.json"
FIXTURES = ROOT / "data" / "fixtures.jsonl"


def load_allowed() -> set[str]:
    return {row["gold"] for row in (json.loads(line) for line in FIXTURES.open()) if row["present"] and row["gold"]}


def classify(row: dict, allowed: set[str]) -> str:
    answer = row["output"].strip()
    if row["present"]:
        if answer == row["gold"]:
            return "exact"
        if not answer:
            return "abstention"
        if answer in allowed:
            return "valid_wrong_schema"
        return "invented_schema"

    if not answer:
        return "correct_abstain"
    if answer in allowed:
        return "valid_spurious_schema"
    return "invented_schema"


def mcnemar(prompted: list[bool], constrained: list[bool]) -> dict:
    prompted_only = sum(a and not b for a, b in zip(prompted, constrained))
    constrained_only = sum(b and not a for a, b in zip(prompted, constrained))
    discordant = prompted_only + constrained_only
    if not discordant:
        p_value = 1.0
    else:
        tail = sum(math.comb(discordant, k) for k in range(min(prompted_only, constrained_only) + 1))
        p_value = min(1.0, 2 * tail / (2**discordant))
    return {
        "prompted_only_correct": prompted_only,
        "constrained_only_correct": constrained_only,
        "discordant": discordant,
        "two_sided_p": p_value,
    }


def main() -> None:
    allowed = load_allowed()
    rows = []
    for line in RAW.open():
        row = json.loads(line)
        row["class"] = classify(row, allowed)
        answer = row["output"].strip()
        row["membership_violation"] = bool(answer) and answer not in allowed
        rows.append(row)

    with SCORED.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")

    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["model"], row["arm"])].append(row)

    report = {"fixture_count": len({r["id"] for r in rows}), "arms": {}, "paired_mcnemar": {}}

    for (model, arm), group in grouped.items():
        counts = Counter(r["class"] for r in group)
        report["arms"][f"{model}::{arm}"] = {
            "classes": dict(counts),
            "membership_violations": sum(r["membership_violation"] for r in group),
            "matcher_mismatches": sum(r["matcher_mismatches"] for r in group),
            "mean_mask_ms": 1000 * sum(r.get("mask_seconds", 0.0) for r in group) / max(1, sum(r["steps"] for r in group)),
        }

    for model in {row["model"] for row in rows}:
        prompted = {row["id"]: row for row in rows if row["model"] == model and row["arm"] == "prompted"}
        constrained = {row["id"]: row for row in rows if row["model"] == model and row["arm"] == "constrained"}
        ids = sorted(set(prompted) & set(constrained))
        prompted_ok = [prompted[i]["class"] in {"exact", "correct_abstain"} for i in ids]
        constrained_ok = [constrained[i]["class"] in {"exact", "correct_abstain"} for i in ids]
        report["paired_mcnemar"][model] = mcnemar(prompted_ok, constrained_ok)

    SUMMARY.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
