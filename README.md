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
- Default models: Qwen2.5 0.5B, 1.5B, 7B and Llama 3.1 8B (all 4-bit MLX). The 7B/8B models need about 5-6 GB of unified memory each.
- Code is MIT (LICENSE); data is CC0 (DATA-LICENSES.md).

## Related work

Full entries in `references.bib`.

The T-schema comes from Tarski's material adequacy condition (Convention T): an adequate truth definition for an object language must entail every instance of "X is true iff p", where X names a sentence and p translates it (Tarski 1944). Davidson (1967) turned this around and proposed that a finitely axiomatized truth theory, one whose theorems are such T-sentences, can serve as a theory of meaning. In this benchmark the object language is a fragment of the metalanguage, so the right-hand side is a copy rather than a translation. That makes it a test of form, not of Davidson's thesis (see the open task in PROBLEM.md).

On the decoding side, the trie mask is a special case of FSM-guided generation (Willard and Louf 2023) and grammar-constrained decoding (Geng et al. 2023). Beurer-Kellner et al. (2024) show that naive token-level masking can distort the distribution through tokenization misalignment, and Park et al. (2024) show that masking does not sample from the grammar-conditioned distribution. Tam et al. (2024) report that format restrictions can lower task accuracy, which is the form-versus-correctness gap this benchmark measures.

- Tarski, A. (1944). The semantic conception of truth and the foundations of semantics. *Philosophy and Phenomenological Research* 4(3), 341–376. doi:10.2307/2102968
- Davidson, D. (1967). Truth and meaning. *Synthese* 17(1), 304–323. doi:10.1007/BF00485035
- Willard, B. T., Louf, R. (2023). Efficient guided generation for large language models. arXiv:2307.09702
- Geng, S., Josifoski, M., Peyrard, M., West, R. (2023). Grammar-constrained decoding for structured NLP tasks without finetuning. EMNLP 2023. arXiv:2305.13971
- Beurer-Kellner, L., Fischer, M., Vechev, M. (2024). Guiding LLMs the right way: fast, non-invasive constrained generation. ICML 2024. arXiv:2403.06988
- Park, K., Wang, J., Berg-Kirkpatrick, T., Polikarpova, N., D'Antoni, L. (2024). Grammar-aligned decoding. NeurIPS 2024. arXiv:2405.21047
- Tam, Z. R. et al. (2024). Let me speak freely? A study on the impact of format restrictions on performance of large language models. arXiv:2408.02442
