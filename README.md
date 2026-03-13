# Low-resource Arabic-script Turkic OCR

![CI](https://github.com/Therad445/low-resource-arabic-script-turkic-ocr/actions/workflows/ci.yml/badge.svg)

Reproducible OCR/HTR experiments for historical Turkic texts written in Arabic script
(Tatar/Bashkir focus). The repository is built as a research workflow:
data protocol, benchmark splits, baselines, evaluation (CER/WER), and error analysis.

## Scope

* **Input:** scanned pages and/or line crops from historical sources (printed first; handwritten later).
* **Output:** machine-readable transcription in Arabic script.
* **Metrics:** CER, WER.
* **Research focus:** low-resource historical OCR with document-level evaluation.

## Current status

Sprint 1 foundation is in place:

* canonical line manifest format;
* conservative GT normalization;
* GT and manifest validation scripts;
* document-level split generation;
* sanity evaluation pipeline.

## Data

This repository does **not** publish copyrighted or restricted scans.
See `data/README.md` for local folder layout and access notes.

Canonical manifest example:

* `data/metadata/line_manifest_v1.tsv`

Document-level split generator:

```bash
python -m scripts.make_doc_splits \
  --manifest data/metadata/line_manifest_v1.tsv \
  --out_dir data/splits/v1 \
  --seed 42
```

## Evaluation

Validate GT:

```bash
python -m scripts.validate_gt --gt datasets/gold_test_v1/labels/gt.tsv
```

Run evaluation:

```bash
python -m scripts.run_eval \
  --gt datasets/gold_test_v1/labels/gt.tsv \
  --pred experiments/2026-01-17_toy_sanity/predictions.tsv \
  --exp_dir experiments/tmp_sanity \
  --tag sanity
```

## Reproducibility

* Configs live in `configs/`
* Each run is logged in `experiments/YYYY-MM-DD_<name>/`
* Splits are made by **document**, not by line

## License

Code: MIT (see `LICENSE`)
Data: depends on source permissions; see `docs/04_ethics_and_licenses.md`
