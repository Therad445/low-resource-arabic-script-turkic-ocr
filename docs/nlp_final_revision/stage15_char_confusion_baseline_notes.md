# Stage 15 Character Confusion Baseline

This stage adds a train-derived character confusion baseline.

Why:
- The instructor noted that only a small number of approaches was compared.
- This baseline adds a data-driven non-neural method between hand-written rules and ByT5.

Method:
- Align train noisy-clean pairs with Levenshtein dynamic programming.
- Estimate a conservative noisy-character -> clean-character mapping.
- Apply the mapping to test noisy lines.
- Evaluate with CER, WER and Exact Match.
- Add the method to final metrics and the report.

This strengthens the Model/Experiments and Results sections without requiring expensive model training.
