#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import math
import random
import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "postcorrection"
DOC_TABLE_DIR = ROOT / "docs" / "nlp_final_revision" / "tables"
FIG_DIR = ROOT / "docs" / "figures"

OUT_DIR.mkdir(parents=True, exist_ok=True)
DOC_TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

N_BOOT = 5000
SEED = 445


def levenshtein(a: str, b: str) -> int:
    a = "" if pd.isna(a) else str(a)
    b = "" if pd.isna(b) else str(b)

    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(
                min(
                    prev[j] + 1,
                    cur[j - 1] + 1,
                    prev[j - 1] + (ca != cb),
                )
            )
        prev = cur
    return prev[-1]


def cer(pred: str, gold: str) -> float:
    gold = "" if pd.isna(gold) else str(gold)
    pred = "" if pd.isna(pred) else str(pred)
    denom = max(1, len(gold))
    return levenshtein(pred, gold) / denom


def no_space_cer(pred: str, gold: str) -> float:
    pred = "" if pd.isna(pred) else str(pred)
    gold = "" if pd.isna(gold) else str(gold)
    pred = "".join(pred.split())
    gold = "".join(gold.split())
    denom = max(1, len(gold))
    return levenshtein(pred, gold) / denom


def wer(pred: str, gold: str) -> float:
    pred = "" if pd.isna(pred) else str(pred)
    gold = "" if pd.isna(gold) else str(gold)
    pred_words = pred.split()
    gold_words = gold.split()
    denom = max(1, len(gold_words))

    # Word-level Levenshtein.
    if pred_words == gold_words:
        return 0.0
    if len(pred_words) < len(gold_words):
        pred_words, gold_words = gold_words, pred_words

    prev = list(range(len(gold_words) + 1))
    for i, ca in enumerate(pred_words, 1):
        cur = [i]
        for j, cb in enumerate(gold_words, 1):
            cur.append(
                min(
                    prev[j] + 1,
                    cur[j - 1] + 1,
                    prev[j - 1] + (ca != cb),
                )
            )
        prev = cur

    return prev[-1] / denom


def bootstrap_ci(values: list[float], n_boot: int = N_BOOT, seed: int = SEED) -> tuple[float, float, float]:
    values = [float(v) for v in values if not pd.isna(v)]
    if not values:
        return math.nan, math.nan, math.nan

    rnd = random.Random(seed)
    n = len(values)
    means = []

    for _ in range(n_boot):
        sample_sum = 0.0
        for _ in range(n):
            sample_sum += values[rnd.randrange(n)]
        means.append(sample_sum / n)

    means.sort()
    mean = sum(values) / n
    low = means[int(0.025 * n_boot)]
    high = means[int(0.975 * n_boot)]
    return mean, low, high


def add_prediction_metrics(rows: list[dict], *, dataset: str, method: str, df: pd.DataFrame, pred_col: str) -> None:
    required = {"clean", pred_col}
    missing = required - set(df.columns)
    if missing:
        print(f"skip {method}: missing columns {missing}")
        return

    per_example = []
    for _, r in df.iterrows():
        gold = r["clean"]
        pred = r[pred_col]
        per_example.append(
            {
                "CER": cer(pred, gold),
                "WER": wer(pred, gold),
                "NoSpaceCER": no_space_cer(pred, gold),
            }
        )

    per_df = pd.DataFrame(per_example)
    for metric in ["CER", "WER", "NoSpaceCER"]:
        mean, low, high = bootstrap_ci(per_df[metric].tolist())
        rows.append(
            {
                "dataset": dataset,
                "method": method,
                "metric": metric,
                "n": len(per_df),
                "mean": mean,
                "ci95_low": low,
                "ci95_high": high,
            }
        )


def load_synthetic(rows: list[dict]) -> None:
    baseline_path = OUT_DIR / "baseline_predictions.csv"
    byt5_path = OUT_DIR / "byt5_arabic_turkic_512_2ep_predictions.csv"
    char_path = OUT_DIR / "char_confusion_baseline_predictions.csv"

    if baseline_path.exists():
        df = pd.read_csv(baseline_path)
        if "identity_prediction" in df.columns:
            add_prediction_metrics(
                rows,
                dataset="synthetic_test",
                method="Identity baseline",
                df=df,
                pred_col="identity_prediction",
            )
        if "rule_prediction" in df.columns:
            add_prediction_metrics(
                rows,
                dataset="synthetic_test",
                method="Rule-based normalizer",
                df=df,
                pred_col="rule_prediction",
            )

    if char_path.exists():
        df = pd.read_csv(char_path)
        pred_col = "prediction" if "prediction" in df.columns else None
        if pred_col is None:
            candidates = [c for c in df.columns if "prediction" in c.lower()]
            pred_col = candidates[0] if candidates else None
        if pred_col:
            add_prediction_metrics(
                rows,
                dataset="synthetic_test",
                method="Train-derived char-confusion baseline",
                df=df,
                pred_col=pred_col,
            )

    if byt5_path.exists():
        df = pd.read_csv(byt5_path)
        add_prediction_metrics(
            rows,
            dataset="synthetic_test",
            method="ByT5-small 512 / 2 epochs",
            df=df,
            pred_col="prediction",
        )


def load_real_line_level(rows: list[dict]) -> None:
    # This is line-level real-OCR sanity/post-correction table.
    # It is useful as an auxiliary robustness check, not as the main page-level result.
    p = DOC_TABLE_DIR / "real_ocr_postcorrection_predictions.csv"
    if not p.exists():
        return

    df = pd.read_csv(p)

    mapping = [
        ("Real OCR identity", "identity_cer"),
        ("Synthetic-trained ByT5 on real OCR", "pred_cer"),
        ("Strict guard / fallback", "fallback_cer"),
    ]

    for method, col in mapping:
        if col not in df.columns:
            continue
        mean, low, high = bootstrap_ci(df[col].tolist())
        rows.append(
            {
                "dataset": "real_ocr_line_level",
                "method": method,
                "metric": "CER",
                "n": int(df[col].notna().sum()),
                "mean": mean,
                "ci95_low": low,
                "ci95_high": high,
            }
        )


def make_plot(result: pd.DataFrame) -> None:
    # Compact figure for synthetic metrics only.
    plot_df = result[
        (result["dataset"] == "synthetic_test")
        & (result["metric"].isin(["CER", "WER", "NoSpaceCER"]))
    ].copy()

    if plot_df.empty:
        return

    methods = [
        "Identity baseline",
        "Rule-based normalizer",
        "Train-derived char-confusion baseline",
        "ByT5-small 512 / 2 epochs",
    ]
    metrics = ["CER", "WER", "NoSpaceCER"]

    plot_df["method"] = pd.Categorical(plot_df["method"], categories=methods, ordered=True)
    plot_df["metric"] = pd.Categorical(plot_df["metric"], categories=metrics, ordered=True)
    plot_df = plot_df.sort_values(["metric", "method"])

    fig, ax = plt.subplots(figsize=(10, 5.5))

    x_labels = []
    y = []
    yerr_low = []
    yerr_high = []

    for _, r in plot_df.iterrows():
        x_labels.append(f"{r['metric']}\n{r['method'].replace(' / 2 epochs', '')}")
        y.append(r["mean"])
        yerr_low.append(r["mean"] - r["ci95_low"])
        yerr_high.append(r["ci95_high"] - r["mean"])

    xs = list(range(len(y)))
    ax.bar(xs, y)
    ax.errorbar(xs, y, yerr=[yerr_low, yerr_high], fmt="none", capsize=4)

    ax.set_ylabel("Ошибка, доля")
    ax.set_title("Bootstrap 95% CI для синтетического тестового набора")
    ax.set_xticks(xs)
    ax.set_xticklabels(x_labels, rotation=55, ha="right")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    out = FIG_DIR / "fig06_bootstrap_metric_ci.png"
    fig.savefig(out, dpi=220)
    print(f"saved {out}")


def main() -> None:
    rows: list[dict] = []
    load_synthetic(rows)
    load_real_line_level(rows)

    if not rows:
        raise SystemExit("No bootstrap rows produced. Check input prediction files.")

    result = pd.DataFrame(rows)
    result = result.sort_values(["dataset", "metric", "method"]).reset_index(drop=True)

    out_csv = OUT_DIR / "bootstrap_metric_ci.csv"
    doc_csv = DOC_TABLE_DIR / "bootstrap_metric_ci.csv"

    result.to_csv(out_csv, index=False)
    result.to_csv(doc_csv, index=False)

    make_plot(result)

    print("\nBootstrap CI summary:")
    print(result.to_string(index=False))
    print(f"\nsaved {out_csv}")
    print(f"saved {doc_csv}")


if __name__ == "__main__":
    main()
