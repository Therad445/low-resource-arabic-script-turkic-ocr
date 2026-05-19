#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def edit_distance(a: list[str], b: list[str]) -> int:
    """Levenshtein edit distance with O(min(n, m)) memory."""
    if len(a) < len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))

    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (ca != cb)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current

    return previous[-1]


def cer(hypothesis: str, reference: str) -> float:
    reference_chars = list(reference)
    if not reference_chars:
        return 0.0 if not hypothesis else 1.0
    return edit_distance(list(hypothesis), reference_chars) / len(reference_chars)


def wer(hypothesis: str, reference: str) -> float:
    reference_words = reference.split()
    if not reference_words:
        return 0.0 if not hypothesis.split() else 1.0
    return edit_distance(hypothesis.split(), reference_words) / len(reference_words)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create qualitative and quantitative OCR post-correction error analysis."
    )
    parser.add_argument(
        "--predictions", required=True, help="CSV with noisy, prediction, clean columns."
    )
    parser.add_argument("--out_dir", required=True, help="Output directory.")
    parser.add_argument("--source_col", default="noisy")
    parser.add_argument("--text_col", default="prediction")
    parser.add_argument("--target_col", default="clean")
    parser.add_argument("--top_k", type=int, default=50)

    args = parser.parse_args()

    predictions_path = Path(args.predictions)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(predictions_path)

    required = [args.source_col, args.text_col, args.target_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. Available columns: {list(df.columns)}"
        )

    rows = []

    for idx, row in df.iterrows():
        noisy = "" if pd.isna(row[args.source_col]) else str(row[args.source_col])
        pred = "" if pd.isna(row[args.text_col]) else str(row[args.text_col])
        clean = "" if pd.isna(row[args.target_col]) else str(row[args.target_col])

        cer_noisy = cer(noisy, clean)
        cer_prediction = cer(pred, clean)
        wer_noisy = wer(noisy, clean)
        wer_prediction = wer(pred, clean)

        rows.append(
            {
                "row_id": idx,
                "noisy": noisy,
                "prediction": pred,
                "clean": clean,
                "cer_noisy": cer_noisy,
                "cer_prediction": cer_prediction,
                "cer_improvement": cer_noisy - cer_prediction,
                "wer_noisy": wer_noisy,
                "wer_prediction": wer_prediction,
                "wer_improvement": wer_noisy - wer_prediction,
                "noisy_len": len(noisy),
                "prediction_len": len(pred),
                "clean_len": len(clean),
            }
        )

    analysis = pd.DataFrame(rows)

    analysis_path = out_dir / "byt5_512_error_analysis.csv"
    best_path = out_dir / "byt5_512_best_examples.csv"
    worst_path = out_dir / "byt5_512_worst_examples.csv"
    summary_path = out_dir / "byt5_512_error_summary.csv"

    analysis.to_csv(analysis_path, index=False)

    best = analysis.sort_values(
        ["cer_improvement", "wer_improvement"],
        ascending=[False, False],
    ).head(args.top_k)
    best.to_csv(best_path, index=False)

    worst = analysis.sort_values(
        ["cer_improvement", "wer_improvement"],
        ascending=[True, True],
    ).head(args.top_k)
    worst.to_csv(worst_path, index=False)

    summary = pd.DataFrame(
        [
            {
                "n": len(analysis),
                "mean_cer_noisy": analysis["cer_noisy"].mean(),
                "mean_cer_prediction": analysis["cer_prediction"].mean(),
                "mean_cer_improvement": analysis["cer_improvement"].mean(),
                "mean_wer_noisy": analysis["wer_noisy"].mean(),
                "mean_wer_prediction": analysis["wer_prediction"].mean(),
                "mean_wer_improvement": analysis["wer_improvement"].mean(),
                "improved_by_cer_count": int((analysis["cer_improvement"] > 0).sum()),
                "unchanged_by_cer_count": int((analysis["cer_improvement"] == 0).sum()),
                "worse_by_cer_count": int((analysis["cer_improvement"] < 0).sum()),
                "improved_by_wer_count": int((analysis["wer_improvement"] > 0).sum()),
                "unchanged_by_wer_count": int((analysis["wer_improvement"] == 0).sum()),
                "worse_by_wer_count": int((analysis["wer_improvement"] < 0).sum()),
            }
        ]
    )
    summary.to_csv(summary_path, index=False)

    print("Saved:")
    print(analysis_path)
    print(best_path)
    print(worst_path)
    print(summary_path)
    print()
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
