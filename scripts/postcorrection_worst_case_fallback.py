"""Worst-case analysis and conservative fallback for ByT5 post-correction.

The fallback rule is intentionally simple and production-like: it only uses the
noisy input and model prediction, not the clean reference. The clean reference is
used only for evaluation after the decision.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

DEFAULT_PREDICTIONS = Path("outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv")
DEFAULT_OUT_DIR = Path("outputs/postcorrection/fallback_analysis")
DEFAULT_DOCS_TABLE = Path("docs/nlp_final_revision/tables/fallback_metrics.csv")
DEFAULT_DOCS_REPORT = Path("docs/nlp_final_revision/analysis/worst_case_analysis.md")
DEFAULT_DOCS_WORST = Path("docs/nlp_final_revision/samples/fallback_worst_cases.csv")


def as_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def levenshtein(a: Sequence[str], b: Sequence[str]) -> int:
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


def safe_rate(distance: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0 if distance == 0 else 1.0
    return distance / denominator


def char_distance(ref: str, hyp: str) -> int:
    return levenshtein(list(ref), list(hyp))


def word_distance(ref: str, hyp: str) -> int:
    return levenshtein(ref.split(), hyp.split())


def remove_spaces(text: str) -> str:
    return "".join(text.split())


def max_char_run(text: str) -> int:
    best = 0
    current = 0
    previous = None

    for ch in text:
        if ch == previous:
            current += 1
        else:
            current = 1
            previous = ch
        best = max(best, current)

    return best


def repeated_bigram_count(tokens: list[str]) -> int:
    if len(tokens) < 4:
        return 0

    count = 0
    for i in range(len(tokens) - 3):
        if tokens[i : i + 2] == tokens[i + 2 : i + 4]:
            count += 1
    return count


def fallback_reasons(noisy: str, prediction: str) -> list[str]:
    """Return conservative fallback reasons using only noisy and prediction."""
    reasons: list[str] = []

    noisy_len = max(len(noisy), 1)
    pred_len = len(prediction)
    len_ratio = pred_len / noisy_len

    noisy_words = len(noisy.split())
    pred_words = len(prediction.split())
    word_delta = pred_words - noisy_words

    if pred_len == 0:
        reasons.append("empty_prediction")

    if len_ratio > 1.35:
        reasons.append("prediction_too_long")

    if len_ratio < 0.65:
        reasons.append("prediction_too_short")

    if abs(word_delta) > max(4, int(0.35 * max(noisy_words, 1))):
        reasons.append("large_word_count_change")

    if max_char_run(prediction) >= 7:
        reasons.append("long_repeated_character_run")

    if repeated_bigram_count(prediction.split()) >= 2:
        reasons.append("repeated_token_bigram")

    return reasons


def add_per_example_metrics(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for row in df.itertuples(index=False):
        line_id = getattr(row, "line_id", None)
        variant_id = getattr(row, "variant_id", None)
        noisy = as_text(row.noisy)
        clean = as_text(row.clean)
        prediction = as_text(row.prediction)

        reasons = fallback_reasons(noisy, prediction)
        fallback_applied = bool(reasons)
        fallback_prediction = noisy if fallback_applied else prediction

        clean_chars = len(clean)
        clean_words = len(clean.split())
        clean_no_space = remove_spaces(clean)

        identity_char_dist = char_distance(clean, noisy)
        byt5_char_dist = char_distance(clean, prediction)
        fallback_char_dist = char_distance(clean, fallback_prediction)

        identity_word_dist = word_distance(clean, noisy)
        byt5_word_dist = word_distance(clean, prediction)
        fallback_word_dist = word_distance(clean, fallback_prediction)

        identity_no_space_char_dist = char_distance(clean_no_space, remove_spaces(noisy))
        byt5_no_space_char_dist = char_distance(clean_no_space, remove_spaces(prediction))
        fallback_no_space_char_dist = char_distance(
            clean_no_space, remove_spaces(fallback_prediction)
        )

        rows.append(
            {
                "line_id": line_id,
                "variant_id": variant_id,
                "noisy": noisy,
                "prediction": prediction,
                "fallback_prediction": fallback_prediction,
                "clean": clean,
                "fallback_applied": fallback_applied,
                "fallback_reasons": ";".join(reasons),
                "clean_chars": clean_chars,
                "clean_words": clean_words,
                "clean_no_space_chars": len(clean_no_space),
                "noisy_chars": len(noisy),
                "prediction_chars": len(prediction),
                "noisy_words": len(noisy.split()),
                "prediction_words": len(prediction.split()),
                "prediction_noisy_char_ratio": len(prediction) / max(len(noisy), 1),
                "prediction_noisy_word_delta": len(prediction.split()) - len(noisy.split()),
                "prediction_max_char_run": max_char_run(prediction),
                "prediction_repeated_bigram_count": repeated_bigram_count(prediction.split()),
                "identity_char_dist": identity_char_dist,
                "byt5_char_dist": byt5_char_dist,
                "fallback_char_dist": fallback_char_dist,
                "identity_word_dist": identity_word_dist,
                "byt5_word_dist": byt5_word_dist,
                "fallback_word_dist": fallback_word_dist,
                "identity_no_space_char_dist": identity_no_space_char_dist,
                "byt5_no_space_char_dist": byt5_no_space_char_dist,
                "fallback_no_space_char_dist": fallback_no_space_char_dist,
            }
        )

    out = pd.DataFrame(rows)

    out["identity_cer"] = out.apply(
        lambda r: safe_rate(int(r["identity_char_dist"]), int(r["clean_chars"])),
        axis=1,
    )
    out["byt5_cer"] = out.apply(
        lambda r: safe_rate(int(r["byt5_char_dist"]), int(r["clean_chars"])),
        axis=1,
    )
    out["fallback_cer"] = out.apply(
        lambda r: safe_rate(int(r["fallback_char_dist"]), int(r["clean_chars"])),
        axis=1,
    )

    out["identity_wer"] = out.apply(
        lambda r: safe_rate(int(r["identity_word_dist"]), int(r["clean_words"])),
        axis=1,
    )
    out["byt5_wer"] = out.apply(
        lambda r: safe_rate(int(r["byt5_word_dist"]), int(r["clean_words"])),
        axis=1,
    )
    out["fallback_wer"] = out.apply(
        lambda r: safe_rate(int(r["fallback_word_dist"]), int(r["clean_words"])),
        axis=1,
    )

    out["identity_no_space_cer"] = out.apply(
        lambda r: safe_rate(
            int(r["identity_no_space_char_dist"]),
            int(r["clean_no_space_chars"]),
        ),
        axis=1,
    )
    out["byt5_no_space_cer"] = out.apply(
        lambda r: safe_rate(
            int(r["byt5_no_space_char_dist"]),
            int(r["clean_no_space_chars"]),
        ),
        axis=1,
    )
    out["fallback_no_space_cer"] = out.apply(
        lambda r: safe_rate(
            int(r["fallback_no_space_char_dist"]),
            int(r["clean_no_space_chars"]),
        ),
        axis=1,
    )

    out["byt5_worse_than_identity_cer"] = out["byt5_char_dist"] > out["identity_char_dist"]
    out["byt5_worse_than_identity_wer"] = out["byt5_word_dist"] > out["identity_word_dist"]
    out["fallback_better_than_byt5_cer"] = out["fallback_char_dist"] < out["byt5_char_dist"]
    out["fallback_worse_than_byt5_cer"] = out["fallback_char_dist"] > out["byt5_char_dist"]

    return out


def corpus_rate(df: pd.DataFrame, dist_col: str, denom_col: str) -> float:
    return safe_rate(int(df[dist_col].sum()), int(df[denom_col].sum()))


def summarize_method(
    df: pd.DataFrame,
    *,
    method: str,
    char_dist_col: str,
    word_dist_col: str,
    no_space_dist_col: str,
    prediction_col: str,
) -> dict[str, object]:
    return {
        "method": method,
        "CER": corpus_rate(df, char_dist_col, "clean_chars"),
        "WER": corpus_rate(df, word_dist_col, "clean_words"),
        "NoSpaceCER": corpus_rate(df, no_space_dist_col, "clean_no_space_chars"),
        "ExactMatch": float((df[prediction_col] == df["clean"]).mean()),
        "N": len(df),
    }


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = [
        summarize_method(
            df,
            method="Identity baseline",
            char_dist_col="identity_char_dist",
            word_dist_col="identity_word_dist",
            no_space_dist_col="identity_no_space_char_dist",
            prediction_col="noisy",
        ),
        summarize_method(
            df,
            method="ByT5-small 512 / 2 epochs",
            char_dist_col="byt5_char_dist",
            word_dist_col="byt5_word_dist",
            no_space_dist_col="byt5_no_space_char_dist",
            prediction_col="prediction",
        ),
        summarize_method(
            df,
            method="ByT5 + conservative fallback",
            char_dist_col="fallback_char_dist",
            word_dist_col="fallback_word_dist",
            no_space_dist_col="fallback_no_space_char_dist",
            prediction_col="fallback_prediction",
        ),
    ]
    return pd.DataFrame(rows)


def reason_summary(df: pd.DataFrame) -> pd.DataFrame:
    applied = df[df["fallback_applied"]].copy()
    if applied.empty:
        return pd.DataFrame(columns=["reason", "N", "share_of_all"])

    rows = []
    total = len(df)
    for reasons in applied["fallback_reasons"]:
        for reason in str(reasons).split(";"):
            if reason:
                rows.append(reason)

    out = pd.Series(rows).value_counts().reset_index()
    out.columns = ["reason", "N"]
    out["share_of_all"] = out["N"] / total
    return out


def write_report(
    *,
    path: Path,
    metrics: pd.DataFrame,
    per_example: pd.DataFrame,
    reasons: pd.DataFrame,
) -> None:
    fallback_n = int(per_example["fallback_applied"].sum())
    total_n = len(per_example)
    fallback_share = fallback_n / total_n

    cer_worse = int(per_example["byt5_worse_than_identity_cer"].sum())
    wer_worse = int(per_example["byt5_worse_than_identity_wer"].sum())

    prevented = int(
        (
            per_example["fallback_applied"]
            & per_example["byt5_worse_than_identity_cer"]
            & ~(per_example["fallback_char_dist"] > per_example["identity_char_dist"])
        ).sum()
    )

    hurt = int(
        (
            per_example["fallback_applied"]
            & (per_example["fallback_char_dist"] > per_example["byt5_char_dist"])
        ).sum()
    )

    report = f"""# Worst-Case Analysis and Conservative Fallback

This analysis inspects unsafe ByT5 post-correction cases and evaluates a simple
conservative fallback rule.

The fallback rule uses only the noisy input and model prediction. It does not use
the clean reference during decision-making. The clean reference is used only for
evaluation.

## Corpus-Level Metrics

{metrics.to_markdown(index=False)}

## Fallback Rule

The fallback returns the original noisy input instead of the ByT5 prediction if
the prediction looks suspicious according to at least one of these signals:

- empty prediction;
- prediction is much longer than noisy input;
- prediction is much shorter than noisy input;
- large word-count change relative to noisy input;
- long repeated character run;
- repeated token bigram.

## Fallback Frequency

- Fallback applied: {fallback_n} / {total_n} examples ({fallback_share:.2%})
- ByT5 worse than identity by CER: {cer_worse} / {total_n}
- ByT5 worse than identity by WER: {wer_worse} / {total_n}
- Fallback prevented CER-worse cases: {prevented}
- Fallback hurt examples by CER relative to raw ByT5: {hurt}

## Fallback Reasons

{reasons.to_markdown(index=False)}

## Interpretation

This is a deliberately conservative engineering check. A useful fallback should
reduce severe model failures without noticeably damaging aggregate CER/WER.

If fallback metrics are worse than raw ByT5, the current rule is too aggressive.
If fallback metrics are similar or slightly better while reducing severe failures,
the rule is a useful safety layer for real-OCR experiments.

A safe wording is:

> ByT5 improves most examples, but it is not uniformly safe. A conservative
> fallback based only on prediction-shape heuristics can be used as a diagnostic
> safety layer, although final acceptance still requires real OCR/HTR validation
> and human review.
"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--docs_table", type=Path, default=DEFAULT_DOCS_TABLE)
    parser.add_argument("--docs_report", type=Path, default=DEFAULT_DOCS_REPORT)
    parser.add_argument("--docs_worst", type=Path, default=DEFAULT_DOCS_WORST)
    args = parser.parse_args()

    df = pd.read_csv(args.predictions)
    required = {"line_id", "variant_id", "noisy", "clean", "prediction"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {args.predictions}: {sorted(missing)}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.docs_table.parent.mkdir(parents=True, exist_ok=True)
    args.docs_report.parent.mkdir(parents=True, exist_ok=True)
    args.docs_worst.parent.mkdir(parents=True, exist_ok=True)

    per_example = add_per_example_metrics(df)
    metrics = build_summary(per_example)
    reasons = reason_summary(per_example)

    per_example.to_csv(args.out_dir / "per_example_fallback_analysis.csv", index=False)
    metrics.to_csv(args.out_dir / "fallback_metrics.csv", index=False)
    metrics.to_csv(args.docs_table, index=False)
    reasons.to_csv(args.out_dir / "fallback_reasons.csv", index=False)

    worst_cols = [
        "line_id",
        "variant_id",
        "fallback_applied",
        "fallback_reasons",
        "identity_cer",
        "byt5_cer",
        "fallback_cer",
        "identity_wer",
        "byt5_wer",
        "fallback_wer",
        "prediction_noisy_char_ratio",
        "prediction_noisy_word_delta",
        "prediction_max_char_run",
        "prediction_repeated_bigram_count",
        "noisy",
        "prediction",
        "fallback_prediction",
        "clean",
    ]

    worst = per_example.sort_values(
        ["byt5_cer", "prediction_noisy_char_ratio"],
        ascending=[False, False],
    )[worst_cols].head(50)

    fallback_cases = (
        per_example[per_example["fallback_applied"]]
        .sort_values(
            ["byt5_cer", "prediction_noisy_char_ratio"],
            ascending=[False, False],
        )[worst_cols]
        .head(50)
    )

    worst.to_csv(args.out_dir / "worst_byt5_cases.csv", index=False)
    fallback_cases.to_csv(args.out_dir / "fallback_cases.csv", index=False)
    fallback_cases.to_csv(args.docs_worst, index=False)

    write_report(
        path=args.docs_report,
        metrics=metrics,
        per_example=per_example,
        reasons=reasons,
    )

    pd.set_option("display.max_columns", 30)
    pd.set_option("display.width", 220)

    print("Saved output directory:", args.out_dir)
    print("Saved docs table:", args.docs_table)
    print("Saved docs report:", args.docs_report)
    print("Saved docs worst cases:", args.docs_worst)
    print()
    print(metrics.to_string(index=False))
    print()
    print("Fallback reasons:")
    print(reasons.to_string(index=False))


if __name__ == "__main__":
    main()
