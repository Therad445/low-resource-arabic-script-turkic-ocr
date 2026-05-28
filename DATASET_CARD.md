# Dataset Card: Arabic-Script Turkic OCR Post-Correction Benchmark

## Dataset Summary

This dataset is a pilot benchmark for OCR post-correction of historical Turkic text written in Arabic script. The task is formulated as sequence-to-sequence correction:

```text
noisy -> clean
```

The clean text was collected from an Ottoman Turkish / Arabic-script Turkic Wikisource source. Synthetic OCR-like corruptions were then generated to create noisy-clean pairs.

## Dataset Structure

Each processed split is stored as a CSV file with the following columns:

- `line_id`: identifier of the original clean text line;
- `variant_id`: identifier of the synthetic noisy variant;
- `noisy`: synthetically corrupted OCR-like text;
- `clean`: original clean text.

## Splits

| Split | Clean lines | Noisy-clean pairs |
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

## Intended Use

The dataset is intended for research and educational experiments in OCR post-correction, historical NLP and low-resource sequence-to-sequence modeling.

## Limitations

This is a pilot benchmark, not a final real-world OCR dataset.

Current limitations:

- the corpus is small;
- the current corpus uses one main source;
- the errors are synthetic rather than produced by a real OCR/HTR system;
- no manual linguistic validation has been performed yet;
- results should not be interpreted as final OCR quality on scanned historical documents.

## Ethical and Legal Notes

The raw source information is documented in:

```text
data/postcorrection/raw/SOURCES.md
```

Before redistributing the dataset outside this repository, source permissions and attribution requirements should be checked.
