# Arabic-script Turkic OCR post-correction pilot

## Goal

This pilot evaluates OCR post-correction methods for historical Turkic texts written in Arabic script. The experiment is part of the broader project on AI methods for recognition and analysis of historical Arabic-script Turkic documents.

The current pilot focuses on a small but topic-aligned corpus instead of the earlier Persian/general Arabic-script prototype.

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

The split is performed by clean source lines, so variants of the same clean line do not appear across different splits.

Leakage check:

| Overlap | Count |
|---|---:|
| train ∩ valid clean lines | 0 |
| train ∩ test clean lines | 0 |
| valid ∩ test clean lines | 0 |

## Baseline results

Evaluation on the Arabic-script Turkic test split:

| Method | CER | WER | ExactMatch | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |

## Interpretation

The identity baseline is stronger than the current rule-based normalizer. This suggests that naive normalization is harmful for this material: it may erase or distort meaningful Arabic-script Turkic orthographic features.

This makes the pilot methodologically useful: the task cannot be solved by a simple normalization rule set, and it motivates neural post-correction with a sequence-to-sequence model such as ByT5.

## Next steps

1. Train ByT5-small on the Arabic-script Turkic dataset.
2. Compare neural post-correction against identity and rule-based baselines.
3. Add qualitative error analysis.
4. Extend the corpus with additional Arabic-script Turkic sources.
5. Prepare this pipeline as a reusable part of the course paper and later thesis/article work.
