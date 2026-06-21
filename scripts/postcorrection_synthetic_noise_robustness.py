"""Synthetic-noise robustness checks for the OCR post-correction pilot.

This script regenerates train/test noisy-clean pairs under several synthetic-noise
settings and evaluates non-neural baselines on each setting.

It does not retrain or run ByT5. The goal is to quantify how much the benchmark
difficulty changes when whitespace noise is reduced or removed, and to document
a reproducible robustness scaffold before the more expensive neural reruns.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.postcorrection.evaluate import cer, evaluate_dataframe
from src.postcorrection.noise_generator import NoiseConfig, inject_noise
from src.postcorrection.normalize import identity, normalize_arabic_script
from src.postcorrection.run_char_confusion_baseline import apply_mapping, build_mapping


def as_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def unique_lines(df: pd.DataFrame) -> list[tuple[int, str]]:
    """Return one clean text for each line_id, preserving stable order."""
    required = {"line_id", "clean"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    lines = (
        df[["line_id", "clean"]]
        .drop_duplicates("line_id")
        .sort_values("line_id")
        .itertuples(index=False)
    )
    return [(int(row.line_id), as_text(row.clean)) for row in lines]


def infer_variants(df: pd.DataFrame, fallback: int = 20) -> int:
    if "variant_id" not in df.columns or df.empty:
        return fallback
    return int(df["variant_id"].max()) + 1


def build_pairs(
    lines: list[tuple[int, str]],
    *,
    variants: int,
    seed: int,
    config: NoiseConfig,
) -> pd.DataFrame:
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []

    for line_id, clean in lines:
        for variant_id in range(variants):
            noisy = inject_noise(clean, config=config, rng=rng)
            if noisy:
                rows.append(
                    {
                        "line_id": line_id,
                        "variant_id": variant_id,
                        "noisy": noisy,
                        "clean": clean,
                    }
                )

    return pd.DataFrame(rows)


def remove_spaces(text: str) -> str:
    return "".join(text.split())


def no_space_cer_mean(df: pd.DataFrame, pred_col: str, target_col: str = "clean") -> float:
    values = []
    for pred, ref in zip(df[pred_col], df[target_col], strict=True):
        values.append(cer(remove_spaces(as_text(pred)), remove_spaces(as_text(ref))))
    return float(sum(values) / len(values))


def word_delta_stats(df: pd.DataFrame) -> dict[str, float]:
    clean_words = df["clean"].fillna("").astype(str).map(lambda s: len(s.split()))
    noisy_words = df["noisy"].fillna("").astype(str).map(lambda s: len(s.split()))
    delta = noisy_words - clean_words

    return {
        "mean_noisy_clean_word_delta": float(delta.mean()),
        "same_word_count_share": float((delta == 0).mean()),
        "more_words_share": float((delta > 0).mean()),
        "fewer_words_share": float((delta < 0).mean()),
    }


def length_delta_stats(df: pd.DataFrame) -> dict[str, float]:
    clean_len = df["clean"].fillna("").astype(str).str.len()
    noisy_len = df["noisy"].fillna("").astype(str).str.len()
    delta = noisy_len - clean_len

    return {
        "mean_noisy_clean_char_delta": float(delta.mean()),
        "mean_abs_noisy_clean_char_delta": float(delta.abs().mean()),
    }


def evaluate_method(
    df: pd.DataFrame,
    *,
    config_name: str,
    method: str,
    pred_col: str,
    config: NoiseConfig,
) -> dict[str, object]:
    metrics = evaluate_dataframe(df, pred_col=pred_col, target_col="clean")
    row: dict[str, object] = {
        "config": config_name,
        "method": method,
        **metrics,
        "NoSpaceCER": no_space_cer_mean(df, pred_col=pred_col),
    }
    row.update(word_delta_stats(df))
    row.update(length_delta_stats(df))
    for key, value in asdict(config).items():
        row[f"noise_{key}"] = value
    return row


def add_predictions(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out_df = test_df.copy()

    out_df["identity_prediction"] = out_df["noisy"].fillna("").astype(str).map(identity)
    out_df["rule_prediction"] = out_df["noisy"].fillna("").astype(str).map(normalize_arabic_script)

    mapping, mapping_df = build_mapping(train_df)
    out_df["char_confusion_prediction"] = (
        out_df["noisy"].fillna("").astype(str).map(lambda s: apply_mapping(s, mapping))
    )

    return out_df, mapping_df


def noise_configs() -> dict[str, NoiseConfig]:
    return {
        "default_reseed": NoiseConfig(),
        "reduced_whitespace": NoiseConfig(
            substitute_prob=0.06,
            delete_prob=0.025,
            insert_prob=0.015,
            space_delete_prob=0.010,
            space_insert_prob=0.005,
            normalize_confusion_prob=0.04,
            punctuation_drop_prob=0.02,
        ),
        "no_whitespace": NoiseConfig(
            substitute_prob=0.06,
            delete_prob=0.025,
            insert_prob=0.015,
            space_delete_prob=0.0,
            space_insert_prob=0.0,
            normalize_confusion_prob=0.04,
            punctuation_drop_prob=0.02,
        ),
        "low_noise": NoiseConfig(
            substitute_prob=0.03,
            delete_prob=0.0125,
            insert_prob=0.0075,
            space_delete_prob=0.0175,
            space_insert_prob=0.0075,
            normalize_confusion_prob=0.02,
            punctuation_drop_prob=0.01,
        ),
        "char_heavy_no_whitespace": NoiseConfig(
            substitute_prob=0.08,
            delete_prob=0.03,
            insert_prob=0.02,
            space_delete_prob=0.0,
            space_insert_prob=0.0,
            normalize_confusion_prob=0.05,
            punctuation_drop_prob=0.02,
        ),
    }


def write_report(
    *,
    report_path: Path,
    summary_df: pd.DataFrame,
    variants: int,
    seed: int,
) -> None:
    pivot = summary_df[
        [
            "config",
            "method",
            "CER",
            "WER",
            "NoSpaceCER",
            "ExactMatch",
            "N",
            "mean_noisy_clean_word_delta",
            "same_word_count_share",
        ]
    ].copy()

    report = f"""# Synthetic Noise Robustness Check

This document summarizes a lightweight robustness check for the synthetic OCR-like
noise generator.

The check regenerates train/test noisy-clean pairs under several noise settings
and evaluates non-neural baselines. It does **not** retrain or run ByT5; neural
robustness requires a separate model rerun.

## Setup

- Variants per clean line: {variants}
- Base seed: {seed}
- Train/test clean-line split: inherited from existing processed train/test CSV files.
- Evaluated methods:
  - identity baseline;
  - rule-based normalizer;
  - train-derived character-confusion baseline.

## Summary

{pivot.to_markdown(index=False)}

## Interpretation Guide

The key question is whether the benchmark difficulty and baseline behavior change
substantially when whitespace noise is reduced or removed.

Important columns:

- `CER`: character-level error rate.
- `WER`: word-level error rate.
- `NoSpaceCER`: CER after removing all whitespace before evaluation.
- `mean_noisy_clean_word_delta`: average word-count difference between noisy and clean text.
- `same_word_count_share`: share of examples where noisy and clean have the same number of words.

## Current Conclusion

This is a baseline-only robustness scaffold. It helps quantify how much synthetic
whitespace noise changes dataset difficulty. The next stronger step is to run
ByT5 prediction on the same regenerated test sets or retrain/evaluate models under
the alternative noise settings.

A safe wording is:

> The current synthetic-noise robustness check shows how baseline difficulty changes
> when whitespace noise is reduced or removed. It does not yet prove neural robustness,
> but it provides the scaffold for a controlled ByT5 rerun.
"""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base_train",
        type=Path,
        default=Path("data/postcorrection/processed/train.csv"),
    )
    parser.add_argument(
        "--base_test",
        type=Path,
        default=Path("data/postcorrection/processed/test.csv"),
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        default=Path("outputs/postcorrection/synthetic_noise_robustness"),
    )
    parser.add_argument(
        "--docs_table",
        type=Path,
        default=Path("docs/nlp_final_revision/tables/synthetic_noise_robustness_summary.csv"),
    )
    parser.add_argument(
        "--docs_report",
        type=Path,
        default=Path("docs/nlp_final_revision/analysis/synthetic_noise_robustness.md"),
    )
    parser.add_argument("--variants", type=int, default=None)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    base_train = pd.read_csv(args.base_train)
    base_test = pd.read_csv(args.base_test)

    variants = args.variants or infer_variants(base_test)
    train_lines = unique_lines(base_train)
    test_lines = unique_lines(base_test)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.docs_table.parent.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, object]] = []

    for offset, (config_name, config) in enumerate(noise_configs().items()):
        train_df = build_pairs(
            train_lines,
            variants=variants,
            seed=args.seed + offset * 10,
            config=config,
        )
        test_df = build_pairs(
            test_lines,
            variants=variants,
            seed=args.seed + offset * 10 + 1,
            config=config,
        )

        predictions_df, mapping_df = add_predictions(train_df, test_df)

        config_dir = args.out_dir / config_name
        config_dir.mkdir(parents=True, exist_ok=True)

        train_df.to_csv(config_dir / "train.csv", index=False)
        test_df.to_csv(config_dir / "test.csv", index=False)
        predictions_df.to_csv(config_dir / "predictions.csv", index=False)
        mapping_df.to_csv(config_dir / "char_confusion_mapping.csv", index=False)

        all_rows.extend(
            [
                evaluate_method(
                    predictions_df,
                    config_name=config_name,
                    method="Identity baseline",
                    pred_col="identity_prediction",
                    config=config,
                ),
                evaluate_method(
                    predictions_df,
                    config_name=config_name,
                    method="Rule-based normalizer",
                    pred_col="rule_prediction",
                    config=config,
                ),
                evaluate_method(
                    predictions_df,
                    config_name=config_name,
                    method="Train-derived char-confusion baseline",
                    pred_col="char_confusion_prediction",
                    config=config,
                ),
            ]
        )

    summary_df = pd.DataFrame(all_rows)
    summary_df.to_csv(args.out_dir / "summary.csv", index=False)
    summary_df.to_csv(args.docs_table, index=False)

    write_report(
        report_path=args.docs_report,
        summary_df=summary_df,
        variants=variants,
        seed=args.seed,
    )

    pd.set_option("display.max_columns", 40)
    pd.set_option("display.width", 220)

    print("Saved output directory:", args.out_dir)
    print("Saved docs table:", args.docs_table)
    print("Saved docs report:", args.docs_report)
    print()
    print(summary_df[["config", "method", "CER", "WER", "NoSpaceCER", "N"]].to_string(index=False))


if __name__ == "__main__":
    main()
