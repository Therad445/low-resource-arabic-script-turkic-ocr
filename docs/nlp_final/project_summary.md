# NLP Final Project Summary

## Title

A Reproducible Benchmark for OCR Post-Correction of Low-Resource Arabic-Script Turkic Historical Texts

## Task

The project studies OCR post-correction as a sequence-to-sequence NLP task:

```text
noisy OCR-like text -> clean historical text
```

The work focuses on historical Turkic text written in Arabic script. It does not attempt to solve full image-based OCR/HTR. Instead, it isolates the post-correction stage and evaluates whether neural sequence-to-sequence correction can improve noisy text compared to simple baselines.

## Main contribution

1. A small reproducible Arabic-script Turkic post-correction benchmark.
2. A synthetic OCR-like noise generation protocol.
3. A clean-line-level train/validation/test split without leakage.
4. Baseline comparison: identity baseline, rule-based normalizer, ByT5-small.
5. Evaluation with CER, WER and Exact Match.
6. Per-sample error analysis.

## Main claim

ByT5-small with 512-token sequence length achieves the best CER and WER among the evaluated methods on the proposed benchmark.

## Current limitations

- The corpus is small.
- The data comes from one main source.
- The current noise is synthetic.
- The model is not evaluated on real OCR/HTR output yet.
- Manual linguistic validation is still required.
