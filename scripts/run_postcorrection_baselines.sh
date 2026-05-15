#!/usr/bin/env bash
set -euo pipefail

cd ~/projects/low-resource-arabic-script-turkic-ocr

mkdir -p outputs/postcorrection

python3 -m src.postcorrection.run_baselines \
  --test data/postcorrection/processed/test.csv \
  --out outputs/postcorrection/check_baseline_predictions.csv \
  --metrics outputs/postcorrection/check_baseline_metrics.csv

cat outputs/postcorrection/check_baseline_metrics.csv
