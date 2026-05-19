"""
Run identity and rule-based baselines.

Example:
python src/run_baselines.py --test data/processed/test.csv --out results/baseline_predictions.csv --metrics results/baseline_metrics.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.postcorrection.evaluate import evaluate_dataframe
from src.postcorrection.normalize import identity, normalize_arabic_script


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.test)
    df["identity_prediction"] = df["noisy"].fillna("").astype(str).map(identity)
    df["rule_prediction"] = df["noisy"].fillna("").astype(str).map(normalize_arabic_script)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    rows = []
    for name, col in [
        ("Identity baseline", "identity_prediction"),
        ("Rule-based normalizer", "rule_prediction"),
    ]:
        metrics = evaluate_dataframe(df, pred_col=col, target_col="clean")
        metrics["method"] = name
        rows.append(metrics)

    metrics_df = pd.DataFrame(rows)[["method", "CER", "WER", "ExactMatch", "N"]]
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(args.metrics, index=False)

    print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
