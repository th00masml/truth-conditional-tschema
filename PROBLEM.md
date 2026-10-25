# Problem: Truth-Conditional T-Schema Generation

Goal: test whether local LLMs generate canonical T-sentences used in truth-conditional semantics.

Historical anchor: Davidson-style truth-conditional semantics uses a truth theory in which T-sentences are central explanatory objects. This benchmark treats canonical T-sentence generation as an operational proxy for that requirement.

Canonical output form:
"P" is true iff P.

Example:
"Snow is white" is true iff Snow is white.

## Predicate

A non-empty output is valid under the decoder constraint iff it is exactly one schema in a fixed canonical set built from supported constants and predicates.

An empty output is always allowed.

## Why this is structurally interesting

The set-membership predicate is easy to validate, but it is weaker than task correctness:

- valid_wrong_schema: output is a valid schema from the set but for the wrong proposition
- valid_spurious_schema: output is valid even when the target proposition is out of inventory and expected output is empty

These are migration classes that can survive parser and membership checks.

## Setup

- 160 deterministic fixtures
- 80 in-inventory propositions with a unique gold T-sentence
- 80 out-of-inventory propositions where the correct response is empty
- 5 arms: naive, prompted, constrained, prompt_tuned, constrained_tuned
- 2 local models on Apple MLX

## Primary question

Does decode-time set constraint reduce malformed outputs while shifting failures into valid-but-wrong T-sentences?

Davidson-focused restatement: can a constrained decoder improve formal T-sentence well-formedness without improving whether the produced sentence gives the correct truth condition for the target proposition?
