# Low-resource Arabic-script Turkic OCR

![CI](https://github.com/Therad445/low-resource-arabic-script-turkic-ocr/actions/workflows/ci.yml/badge.svg)

Research repository for low-resource OCR/HTR and OCR post-correction experiments on historical Turkic texts written in Arabic script.

The current main result is a reproducible pilot for OCR post-correction of Arabic-script Turkic text: corpus collection, synthetic noisy/clean dataset construction, baseline evaluation, ByT5-small fine-tuning, metrics, and error analysis.

## Current status

The repository currently contains two connected layers:

1. General OCR/HTR research scaffold for historical Arabic-script Turkic documents.
2. A completed post-correction pilot used as the technical basis for the course paper draft.

The post-correction pilot includes:

- Ottoman Turkish / Arabic-script Turkic corpus collection from Arabic Wikisource;
- 400 collected clean text blocks;
- synthetic OCR-like noisy/clean pair generation;
- train/valid/test split without clean-line leakage;
- identity and rule-based baseline evaluation;
- ByT5-small 512-token experiment;
- aggregate metrics and per-sample error analysis;
- course paper draft and polishing TODO.

## Main documents

- `docs/postcorrection_pilot.md` — compact technical summary of the post-correction pilot.
- `docs/course_paper_draft.md` — current course paper draft.
- `docs/course_paper_todo.md` — checklist for polishing, references, formatting, and final review.
- `docs/course_paper_outline.md` — initial course paper outline.

## Post-correction data

Raw collected corpus:

- `data/postcorrection/raw/arabic_turkic_clean_text.txt`
- `data/postcorrection/raw/SOURCES.md`

Processed dataset:

- `data/postcorrection/processed/train.csv`
- `data/postcorrection/processed/valid.csv`
- `data/postcorrection/processed/test.csv`
- `data/postcorrection/processed/dataset_stats.csv`

Dataset summary:

| Split | Clean lines | Noisy-clean pairs |
|---|---:|---:|
| train | 320 | 6400 |
| valid | 40 | 800 |
| test | 40 | 800 |

## Post-correction results

Evaluation on the Arabic-script Turkic test split:

| Method | CER | WER | ExactMatch | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| ByT5-small 512 / 2 epochs | 0.079913 | 0.368540 | 0.003750 | 800 |

Per-sample error analysis for ByT5-small 512:

| Criterion | Improved | Unchanged | Worse | Total |
|---|---:|---:|---:|---:|
| CER | 682 | 60 | 58 | 800 |
| WER | 677 | 63 | 60 | 800 |

## Key scripts

Corpus collection:

```bash
python3 scripts/collect_wikisource_ottoman_ukraine.py \
  --start 5 \
  --end 71 \
  --out data/postcorrection/raw/arabic_turkic_clean_text.txt \
  --sources data/postcorrection/raw/SOURCES.md
```

Dataset construction:

```bash
python3 -m src.postcorrection.make_dataset \
  --input data/postcorrection/raw/arabic_turkic_clean_text.txt \
  --out_dir data/postcorrection/processed \
  --variants 20 \
  --seed 42
```

Baseline evaluation:

```bash
python3 -m src.postcorrection.run_baselines \
  --test data/postcorrection/processed/test.csv \
  --out outputs/postcorrection/baseline_predictions.csv \
  --metrics outputs/postcorrection/baseline_metrics.csv
```

ByT5 prediction evaluation artifacts:

- `outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv`
- `outputs/postcorrection/byt5_arabic_turkic_512_2ep_metrics.csv`

Error analysis:

```bash
python3 scripts/postcorrection_error_analysis.py \
  --predictions outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv \
  --out_dir outputs/postcorrection/error_analysis
```

## Important limitations

This is a pilot experiment, not a final benchmark.

Current limitations:

- the corpus is small;
- the current pilot uses one main source;
- OCR-like errors are synthetic;
- evaluation does not yet include manual linguistic validation;
- real OCR/HTR outputs should be added for a stronger benchmark.

## Reproducibility notes

The repository stores code, datasets, metrics, predictions, and analysis files for the pilot. Model weights are not stored in git.

The general CI checks linting, formatting, tests, and the earlier OCR/HTR sanity pipeline. The post-correction pipeline is documented and reproducible, but it is not yet fully integrated into CI.

## License

Code: MIT (see `LICENSE`).

Data: depends on source permissions. The current post-correction pilot uses text collected from Wikisource; attribution and source notes are stored in `data/postcorrection/raw/SOURCES.md`.
