"""
Evaluate OCR post-correction predictions.

Expected CSV columns:
- clean: gold/reference text
- prediction: predicted corrected text

Example:
python src/evaluate.py --predictions results/byt5_predictions.csv --text_col prediction --target_col clean --out results/byt5_metrics.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def levenshtein(a: list[str] | str, b: list[str] | str) -> int:
    """Classic dynamic-programming Levenshtein distance."""
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n

    prev = list(range(m + 1))
    curr = [0] * (m + 1)

    for i in range(1, n + 1):
        curr[0] = i
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + cost,
            )
        prev, curr = curr, prev

    return prev[m]


def cer(pred: str, ref: str) -> float:
    if not ref:
        return 0.0 if not pred else 1.0
    return levenshtein(pred, ref) / len(ref)


def wer(pred: str, ref: str) -> float:
    ref_words = ref.split()
    pred_words = pred.split()
    if not ref_words:
        return 0.0 if not pred_words else 1.0
    return levenshtein(pred_words, ref_words) / len(ref_words)


def exact_match(pred: str, ref: str) -> float:
    return float(pred == ref)


def evaluate_dataframe(df: pd.DataFrame, pred_col: str, target_col: str) -> dict[str, float]:
    preds = df[pred_col].fillna("").astype(str).tolist()
    refs = df[target_col].fillna("").astype(str).tolist()

    return {
        "CER": sum(cer(p, r) for p, r in zip(preds, refs, strict=True)) / len(refs),
        "WER": sum(wer(p, r) for p, r in zip(preds, refs, strict=True)) / len(refs),
        "ExactMatch": sum(exact_match(p, r) for p, r in zip(preds, refs, strict=True)) / len(refs),
        "N": float(len(refs)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--text_col", type=str, default="prediction")
    parser.add_argument("--target_col", type=str, default="clean")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.predictions)
    metrics = evaluate_dataframe(df, args.text_col, args.target_col)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(args.out, index=False)

    print(pd.DataFrame([metrics]).to_string(index=False))


if __name__ == "__main__":
    main()
