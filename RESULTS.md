# Results - Truth-Conditional T-Schema

> **Invalid run, do not cite.** The decode mask was broken: `TSchemaSetLogitsProcessor` sliced `tokens[prompt_length:]`, but mlx_lm passes only generated tokens, so the prefix was always empty and every step got the root mask (outputs like `"C"""C"""`). The prompts also gave no filled-in example and no stop condition, which explains exact=0 in the unconstrained arms. Both are fixed (`src/mlx_binding.py`, `src/run.py`, regression test in `tests/test_mask.py`). Rerun on Apple silicon with `.venv/bin/python src/run.py --overwrite` and then the score/report steps.

160 deterministic fixtures; raw outputs are retained.

| model / arm | exact | valid_wrong_schema | invented_schema | abstention | correct_abstain | valid_spurious_schema | membership violations | matcher mismatches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mlx-community/Qwen2.5-0.5B-Instruct-4bit / constrained | 0 | 0 | 147 | 4 | 9 | 0 | 147 | 0 |
| mlx-community/Qwen2.5-0.5B-Instruct-4bit / constrained_tuned | 0 | 0 | 23 | 71 | 66 | 0 | 23 | 0 |
| mlx-community/Qwen2.5-0.5B-Instruct-4bit / naive | 0 | 0 | 160 | 0 | 0 | 0 | 160 | 0 |
| mlx-community/Qwen2.5-0.5B-Instruct-4bit / prompt_tuned | 0 | 0 | 160 | 0 | 0 | 0 | 160 | 0 |
| mlx-community/Qwen2.5-0.5B-Instruct-4bit / prompted | 0 | 0 | 160 | 0 | 0 | 0 | 160 | 0 |
| mlx-community/Qwen2.5-1.5B-Instruct-4bit / constrained | 0 | 0 | 160 | 0 | 0 | 0 | 160 | 0 |
| mlx-community/Qwen2.5-1.5B-Instruct-4bit / constrained_tuned | 0 | 0 | 160 | 0 | 0 | 0 | 160 | 0 |
| mlx-community/Qwen2.5-1.5B-Instruct-4bit / naive | 0 | 0 | 160 | 0 | 0 | 0 | 160 | 0 |
| mlx-community/Qwen2.5-1.5B-Instruct-4bit / prompt_tuned | 0 | 0 | 160 | 0 | 0 | 0 | 160 | 0 |
| mlx-community/Qwen2.5-1.5B-Instruct-4bit / prompted | 0 | 0 | 160 | 0 | 0 | 0 | 160 | 0 |

## Paired tests

Correctness means exact for in-inventory fixtures and correct_abstain for out-of-inventory fixtures. Each test compares prompted to constrained outcomes on matched fixtures.

- mlx-community/Qwen2.5-0.5B-Instruct-4bit: prompted-only correct 0; constrained-only correct 9; discordant 9; exact two-sided McNemar p=0.00391.
- mlx-community/Qwen2.5-1.5B-Instruct-4bit: prompted-only correct 0; constrained-only correct 0; discordant 0; exact two-sided McNemar p=1.00000.

## Davidson framing

In Davidson-style truth-conditional semantics, a theory must deliver the right T-sentence for each object-language sentence. This benchmark separates two questions: whether an output has canonical T-sentence form, and whether it states the correct truth condition for the target proposition.

## Standing-hypothesis answer

A zero constrained membership-violation count proves structural membership in the canonical schema set, but not proposition-level correctness. Compare valid_wrong_schema and valid_spurious_schema against invented_schema to decide whether constraint failures migrate into structurally valid but semantically wrong outputs.
