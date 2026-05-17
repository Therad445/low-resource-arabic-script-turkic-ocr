# Arabic-script Turkic OCR post-correction pilot

## Goal

This pilot evaluates OCR post-correction methods for historical Turkic texts written in Arabic script. The experiment is part of a broader project on AI methods for recognition and analysis of historical Arabic-script Turkic documents.

The current version replaces the earlier Persian/general Arabic-script prototype with a topic-aligned Ottoman Turkish Arabic-script corpus.

## Corpus

The corpus was collected from an Ottoman Turkish Arabic-script Wikisource text:

- source text: `أوقرانيا، روسيه وتوركيه (مقالەلر مجموعەسى)`
- page range: 5–71
- collected clean text blocks: 400
- raw text file: `data/postcorrection/raw/arabic_turkic_clean_text.txt`
- source note: `data/postcorrection/raw/SOURCES.md`

The text contains Arabic-script Ottoman/Turkic forms such as:

- `توركيه`
- `اوقراينا`
- `عثمانلی`
- `ايدى`
- `بولیوردی`

## Dataset construction

The post-correction dataset is synthetic: clean Arabic-script Turkic lines are corrupted by a controlled noise generator that imitates OCR-like errors.

Generated splits:

| Split | Rows | Unique clean lines |
|---|---:|---:|
| train | 6400 | 320 |
| valid | 800 | 40 |
| test | 800 | 40 |

The split is performed by clean source lines. Variants of the same clean line do not appear across different splits.

Leakage check:

| Overlap | Count |
|---|---:|
| train ∩ valid clean lines | 0 |
| train ∩ test clean lines | 0 |
| valid ∩ test clean lines | 0 |

## Methods

The pilot compares three approaches:

1. **Identity baseline**: returns the noisy input unchanged.
2. **Rule-based normalizer**: applies simple Arabic-script normalization rules.
3. **ByT5-small**: a byte-level sequence-to-sequence model fine-tuned for OCR post-correction.

Two ByT5 settings were explored during experimentation:

- `max_source_length=256`, `max_target_length=256`
- `max_source_length=512`, `max_target_length=512`

The 512-token setting is important because ByT5 operates on byte-level representations. For Arabic-script text, one visible character may require multiple bytes, so short byte-level limits may truncate source or target sequences.

## Final results

Evaluation on the Arabic-script Turkic test split:

| Method | CER | WER | ExactMatch | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| ByT5-small 512 / 2 epochs | 0.079913 | 0.368540 | 0.003750 | 800 |

## Interpretation

The rule-based normalizer performs worse than the identity baseline. This suggests that naive normalization can be harmful for Arabic-script Turkic material, because it may distort meaningful orthographic features.

The ByT5-small 512-token model improves over the identity baseline on both CER and WER. The improvement is moderate on character-level accuracy and stronger on word-level accuracy.

Relative to the identity baseline:

- CER improves from 0.086005 to 0.079913;
- WER improves from 0.519006 to 0.368540.

This supports the main technical hypothesis of the pilot: neural post-correction can improve synthetic OCR-style corruptions for historical Arabic-script Turkic text, but sequence length is a critical parameter for byte-level models.

## Error analysis

In addition to aggregate CER/WER scores, the ByT5-small 512 model was analyzed at the individual test-sample level.

The model improves most test samples:

| Criterion | Improved | Unchanged | Worse | Total |
|---|---:|---:|---:|---:|
| CER | 682 | 60 | 58 | 800 |
| WER | 677 | 63 | 60 | 800 |

The mean per-sample CER improvement is 0.006092, and the mean per-sample WER improvement is 0.150467.

This confirms that the final model does not only improve the average score due to a few outliers: it improves the majority of test lines. At the same time, the presence of 58 CER-worse and 60 WER-worse cases shows that the model is not uniformly safe and still requires qualitative error analysis before use in a historical text processing pipeline.

The generated analysis files are stored in:

- `outputs/postcorrection/error_analysis/byt5_512_error_summary.csv`
- `outputs/postcorrection/error_analysis/byt5_512_best_examples.csv`
- `outputs/postcorrection/error_analysis/byt5_512_worst_examples.csv`
- `outputs/postcorrection/error_analysis/byt5_512_error_analysis.csv`

## Limitations

This is still a pilot experiment, not a final benchmark.

Current limitations:

- the corpus is small: 400 clean text blocks;
- the data comes from one main source;
- OCR errors are synthetic rather than produced by a real OCR engine;
- exact match remains low because the lines are long and orthographically complex;
- the evaluation does not yet include manual linguistic validation.

## Next steps

1. Add qualitative error analysis.
2. Compare ByT5 256 and 512 outputs directly.
3. Extend the corpus with additional Arabic-script Turkic sources.
4. Add real OCR/HTR outputs if available.
5. Prepare the experiment as a reproducible benchmark component for the course paper, thesis, and future article.
