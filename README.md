# Truth-Conditional T-Schema Benchmark

This project evaluates whether local LLMs generate canonical T-sentences:

"P" is true iff P.

Framing: this is a Davidson-inspired operational test. In truth-conditional semantics, T-sentences play a central role in stating truth conditions compositionally; here we test whether models can produce the right canonical schema, not just schema-like text.

It measures both:

- structural validity under a closed schema set
- proposition-level correctness

## Quickstart

1. Create environment

python3.13 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

2. Run full pipeline

bash progress.sh

3. Main outputs

- outputs/raw.jsonl
- outputs/scored.jsonl
- outputs/summary.json
- RESULTS.md

## Notes

- The constrained arms permit only canonical schemas from the supported proposition inventory plus empty output.
- Empty output is legal in all arms.
