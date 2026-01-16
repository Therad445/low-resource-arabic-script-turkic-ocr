# Low-resource Arabic-script Turkic OCR

Reproducible OCR/HTR experiments for historical Turkic texts written in Arabic script
(Tatar/Bashkir focus). This repository aims to provide a clean research workflow:
data protocol, baselines, evaluation (CER/WER), and error analysis.

## Scope
- **Input:** scanned pages and/or line crops from historical sources (printed first; handwritten later).
- **Output:** machine-readable transcription (Arabic script), optionally with normalization/transliteration.
- **Metrics:** CER, WER (and downstream utility later: search/NER).

## Data
This repository does **not** publish copyrighted or restricted scans.
See `data/README.md` for local folder layout and access notes.

## Quick start (planned)
- Prepare `datasets/gold_test_v1/labels/gt.tsv`
- Run evaluation:
  - `python scripts/evaluate.py --gt datasets/gold_test_v1/labels/gt.tsv --pred <pred.tsv>`

## Reproducibility
- Configs live in `configs/`
- Each run is logged in `experiments/YYYY-MM-DD_<name>/` with config + metrics + notes.

## License
Code: MIT (see `LICENSE`).  
Data: depends on source permissions; see `docs/04_ethics_and_licenses.md`.
