# Reproduction Guide

This document describes how to reproduce the main artifacts of the NLP final project.

## 1. Environment

Install post-correction dependencies:

```bash
python3 -m pip install -r requirements-postcorrection.txt
```

Development dependencies are listed in:

```text
requirements-dev.txt
```

## 2. Corpus Collection

```bash
python3 scripts/collect_wikisource_ottoman_ukraine.py \
  --start 5 \
  --end 71 \
  --out data/postcorrection/raw/arabic_turkic_clean_text.txt \
  --sources data/postcorrection/raw/SOURCES.md
```

## 3. Dataset Construction

```bash
python3 -m src.postcorrection.make_dataset \
  --input data/postcorrection/raw/arabic_turkic_clean_text.txt \
  --out_dir data/postcorrection/processed \
  --variants 20 \
  --seed 42
```

## 4. Baseline Evaluation

```bash
python3 -m src.postcorrection.run_baselines \
  --test data/postcorrection/processed/test.csv \
  --out outputs/postcorrection/baseline_predictions.csv \
  --metrics outputs/postcorrection/baseline_metrics.csv
```

## 5. ByT5 Evaluation Artifacts

The current repository stores prediction and metric artifacts for the ByT5-small 512-token experiment:

```text
outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv
outputs/postcorrection/byt5_arabic_turkic_512_2ep_metrics.csv
outputs/postcorrection/byt5_arabic_turkic_512_2ep_examples.csv
```

Model weights are not stored in git.

## 6. Error Analysis

```bash
python3 scripts/postcorrection_error_analysis.py \
  --predictions outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv \
  --out_dir outputs/postcorrection/error_analysis
```

## 7. Main Result Files

```text
outputs/postcorrection/final_metrics.csv
outputs/postcorrection/error_analysis/byt5_512_error_summary.csv
outputs/postcorrection/error_analysis/byt5_512_best_examples.csv
outputs/postcorrection/error_analysis/byt5_512_worst_examples.csv
```

## 8. Report

The LaTeX report is located in:

```text
report/main.tex
report/lit.bib
```

Generated LaTeX tables are located in:

```text
report/tables/
```
