# Dataset Card: Arabic-Script Turkic OCR Post-Correction Benchmark

## Dataset Summary

This dataset is a pilot benchmark for OCR post-correction of historical Turkic text written in Arabic script.

The task is formulated as line-level sequence-to-sequence correction:

```text
noisy -> clean
```

The clean text was collected from an Ottoman Turkish / Arabic-script Turkic Wikisource source. Synthetic OCR-like corruptions were then generated to create noisy-clean pairs.

This dataset is intended for controlled pilot experiments. It is not a replacement for evaluation on real OCR/HTR outputs.

## Dataset Structure

Each processed split is stored as a CSV file with the following columns:

- `line_id`: identifier of the original clean text line;
- `variant_id`: identifier of the synthetic noisy variant;
- `noisy`: synthetically corrupted OCR-like text;
- `clean`: original clean text.

## Splits

| Split | Unique clean lines | Noisy-clean pairs |
|---|---:|---:|
| train | 320 | 6400 |
| valid | 40 | 800 |
| test | 40 | 800 |

The split is performed by original clean lines. Different noisy variants of the same clean line do not appear across different splits.

## Files

```text
data/postcorrection/raw/arabic_turkic_clean_text.txt
data/postcorrection/raw/SOURCES.md
data/postcorrection/processed/train.csv
data/postcorrection/processed/valid.csv
data/postcorrection/processed/test.csv
data/postcorrection/processed/dataset_stats.csv
```

## Synthetic Noise

The benchmark uses controlled synthetic OCR-like text-level noise.

The current noise generator includes:

- character substitution;
- character deletion;
- character insertion;
- whitespace split/merge errors;
- Arabic/Persian form confusion.

The noise generator is useful for a controlled pilot setup, but it does not model page-level or image-level OCR/HTR factors such as:

- scan quality;
- font;
- ligatures;
- layout;
- line segmentation;
- page damage;
- column mixing;
- reading order errors.

## Leakage Control

The dataset split is performed at the level of original clean lines.

This prevents the same clean line from appearing in train and test through different noisy variants.

Recorded clean-line overlap:

| Overlap | Count |
|---|---:|
| train ∩ valid | 0 |
| train ∩ test | 0 |
| valid ∩ test | 0 |

## Intended Use

The dataset is intended for:

- OCR post-correction experiments;
- low-resource historical NLP;
- sequence-to-sequence correction;
- baseline comparison;
- educational and reproducibility-focused research.

## Out-of-Scope Use

This dataset should not be used to claim:

- final OCR/HTR quality on real scans;
- production-ready archive transcription;
- general Arabic OCR performance;
- global state of the art in OCR post-correction.

## Limitations

Current limitations:

- the corpus is small;
- the corpus is based on one main source;
- errors are synthetic rather than produced by a real OCR/HTR system;
- the synthetic generator is not calibrated against a real OCR confusion matrix;
- no manually validated real-OCR subset is included yet;
- automatic CER/WER metrics do not fully capture historical-linguistic correctness.

## Recommended Next Dataset Step

The next required dataset improvement is a small real-OCR/HTR sanity subset:

- 10–30 page or line-level samples;
- real OCR/HTR output;
- manually checked clean reference;
- same CER/WER/no-space CER evaluation protocol.

## Ethical and Legal Notes

Raw source information is documented in:

```text
data/postcorrection/raw/SOURCES.md
```

Before redistributing the dataset outside this repository, source permissions and attribution requirements should be checked.
