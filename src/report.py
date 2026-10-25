"""Render markdown results from summary.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "outputs" / "summary.json"
RESULTS = ROOT / "RESULTS.md"


def get_count(classes: dict, key: str) -> int:
    return int(classes.get(key, 0))


def main() -> None:
    summary = json.loads(SUMMARY.read_text())

    lines = [
        "# Results - Truth-Conditional T-Schema",
        "",
        f"{summary['fixture_count']} deterministic fixtures; raw outputs are retained.",
        "",
        "| model / arm | exact | valid_wrong_schema | invented_schema | abstention | correct_abstain | valid_spurious_schema | membership violations | matcher mismatches |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for key in sorted(summary["arms"]):
        model, arm = key.split("::", 1)
        data = summary["arms"][key]
        classes = data["classes"]
        lines.append(
            "| "
            f"{model} / {arm} | "
            f"{get_count(classes, 'exact')} | "
            f"{get_count(classes, 'valid_wrong_schema')} | "
            f"{get_count(classes, 'invented_schema')} | "
            f"{get_count(classes, 'abstention')} | "
            f"{get_count(classes, 'correct_abstain')} | "
            f"{get_count(classes, 'valid_spurious_schema')} | "
            f"{data['membership_violations']} | "
            f"{data['matcher_mismatches']} |"
        )

    lines += [
        "",
        "## Paired tests",
        "",
        "Correctness means exact for in-inventory fixtures and correct_abstain for out-of-inventory fixtures. Each test compares prompted to constrained outcomes on matched fixtures.",
        "",
    ]

    for model in sorted(summary["paired_mcnemar"]):
        row = summary["paired_mcnemar"][model]
        lines.append(
            f"- {model}: prompted-only correct {row['prompted_only_correct']}; "
            f"constrained-only correct {row['constrained_only_correct']}; "
            f"discordant {row['discordant']}; exact two-sided McNemar p={row['two_sided_p']:.5f}."
        )

    lines += [
        "",
        "## Davidson framing",
        "",
        "In Davidson-style truth-conditional semantics, a theory must deliver the right T-sentence for each object-language sentence. This benchmark separates two questions: whether an output has canonical T-sentence form, and whether it states the correct truth condition for the target proposition.",
        "",
        "## Standing-hypothesis answer",
        "",
        "A zero constrained membership-violation count proves structural membership in the canonical schema set, but not proposition-level correctness. Compare valid_wrong_schema and valid_spurious_schema against invented_schema to decide whether constraint failures migrate into structurally valid but semantically wrong outputs.",
        "",
    ]

    RESULTS.write_text("\n".join(lines))
    print(f"wrote {RESULTS}")


if __name__ == "__main__":
    main()
