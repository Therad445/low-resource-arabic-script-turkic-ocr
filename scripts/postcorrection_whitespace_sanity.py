from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

PREDICTIONS_PATH = Path("outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv")
OUT_DIR = Path("outputs/postcorrection/whitespace_sanity")


def as_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def levenshtein(a: Sequence[str], b: Sequence[str]) -> int:
    """Levenshtein distance for character or token sequences."""
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


def char_distance(ref: str, hyp: str) -> int:
    return levenshtein(list(ref), list(hyp))


def word_distance(ref: str, hyp: str) -> int:
    return levenshtein(ref.split(), hyp.split())


def remove_spaces(text: str) -> str:
    return "".join(text.split())


def safe_rate(distance: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0 if distance == 0 else 1.0
    return distance / denominator


def add_per_example_metrics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for row in df.itertuples(index=False):
        clean = as_text(row.clean)
        noisy = as_text(row.noisy)
        pred = as_text(row.prediction)

        clean_no_space = remove_spaces(clean)
        noisy_no_space = remove_spaces(noisy)
        pred_no_space = remove_spaces(pred)

        clean_chars = len(clean)
        clean_words = len(clean.split())
        clean_no_space_chars = len(clean_no_space)

        identity_char_dist = char_distance(clean, noisy)
        byt5_char_dist = char_distance(clean, pred)

        identity_word_dist = word_distance(clean, noisy)
        byt5_word_dist = word_distance(clean, pred)

        identity_no_space_char_dist = char_distance(clean_no_space, noisy_no_space)
        byt5_no_space_char_dist = char_distance(clean_no_space, pred_no_space)

        noisy_word_count = len(noisy.split())
        pred_word_count = len(pred.split())

        rows.append(
            {
                "line_id": getattr(row, "line_id", None),
                "variant_id": getattr(row, "variant_id", None),
                "clean": clean,
                "noisy": noisy,
                "prediction": pred,
                "clean_chars": clean_chars,
                "clean_words": clean_words,
                "clean_no_space_chars": clean_no_space_chars,
                "noisy_words": noisy_word_count,
                "prediction_words": pred_word_count,
                "noisy_clean_word_delta": noisy_word_count - clean_words,
                "prediction_clean_word_delta": pred_word_count - clean_words,
                "word_count_group": (
                    "same_word_count"
                    if noisy_word_count == clean_words
                    else "noisy_has_more_words"
                    if noisy_word_count > clean_words
                    else "noisy_has_fewer_words"
                ),
                "identity_char_dist": identity_char_dist,
                "byt5_char_dist": byt5_char_dist,
                "identity_word_dist": identity_word_dist,
                "byt5_word_dist": byt5_word_dist,
                "identity_no_space_char_dist": identity_no_space_char_dist,
                "byt5_no_space_char_dist": byt5_no_space_char_dist,
                "identity_cer": safe_rate(identity_char_dist, clean_chars),
                "byt5_cer": safe_rate(byt5_char_dist, clean_chars),
                "identity_wer": safe_rate(identity_word_dist, clean_words),
                "byt5_wer": safe_rate(byt5_word_dist, clean_words),
                "identity_no_space_cer": safe_rate(
                    identity_no_space_char_dist, clean_no_space_chars
                ),
                "byt5_no_space_cer": safe_rate(byt5_no_space_char_dist, clean_no_space_chars),
            }
        )

    out = pd.DataFrame(rows)

    out["cer_improvement"] = out["identity_cer"] - out["byt5_cer"]
    out["wer_improvement"] = out["identity_wer"] - out["byt5_wer"]
    out["no_space_cer_improvement"] = out["identity_no_space_cer"] - out["byt5_no_space_cer"]

    out["cer_improved"] = out["cer_improvement"] > 0
    out["wer_improved"] = out["wer_improvement"] > 0
    out["no_space_cer_improved"] = out["no_space_cer_improvement"] > 0

    out["wer_improved_but_no_space_not"] = out["wer_improved"] & ~out["no_space_cer_improved"]

    return out


def corpus_rate(g: pd.DataFrame, dist_col: str, denom_col: str) -> float:
    denom = int(g[denom_col].sum())
    dist = int(g[dist_col].sum())
    return safe_rate(dist, denom)


def summarize_group(name: str, g: pd.DataFrame, total_n: int) -> dict[str, object]:
    identity_cer = corpus_rate(g, "identity_char_dist", "clean_chars")
    byt5_cer = corpus_rate(g, "byt5_char_dist", "clean_chars")

    identity_wer = corpus_rate(g, "identity_word_dist", "clean_words")
    byt5_wer = corpus_rate(g, "byt5_word_dist", "clean_words")

    identity_no_space_cer = corpus_rate(g, "identity_no_space_char_dist", "clean_no_space_chars")
    byt5_no_space_cer = corpus_rate(g, "byt5_no_space_char_dist", "clean_no_space_chars")

    return {
        "group": name,
        "N": len(g),
        "share": len(g) / total_n,
        "mean_noisy_clean_word_delta": g["noisy_clean_word_delta"].mean(),
        "identity_CER": identity_cer,
        "byt5_CER": byt5_cer,
        "CER_abs_improvement": identity_cer - byt5_cer,
        "identity_WER": identity_wer,
        "byt5_WER": byt5_wer,
        "WER_abs_improvement": identity_wer - byt5_wer,
        "identity_no_space_CER": identity_no_space_cer,
        "byt5_no_space_CER": byt5_no_space_cer,
        "no_space_CER_abs_improvement": identity_no_space_cer - byt5_no_space_cer,
        "CER_improved_share": g["cer_improved"].mean(),
        "WER_improved_share": g["wer_improved"].mean(),
        "no_space_CER_improved_share": g["no_space_cer_improved"].mean(),
        "WER_improved_but_no_space_not_share": g["wer_improved_but_no_space_not"].mean(),
    }


def main() -> None:
    if not PREDICTIONS_PATH.exists():
        raise FileNotFoundError(PREDICTIONS_PATH)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PREDICTIONS_PATH)
    required = {"line_id", "variant_id", "noisy", "clean", "prediction"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {PREDICTIONS_PATH}: {sorted(missing)}")

    per_example = add_per_example_metrics(df)
    per_example.to_csv(OUT_DIR / "per_example_whitespace_sanity.csv", index=False)

    groups: list[tuple[str, pd.DataFrame]] = [
        ("all", per_example),
        (
            "same_word_count",
            per_example[per_example["word_count_group"] == "same_word_count"],
        ),
        (
            "noisy_has_more_words",
            per_example[per_example["word_count_group"] == "noisy_has_more_words"],
        ),
        (
            "noisy_has_fewer_words",
            per_example[per_example["word_count_group"] == "noisy_has_fewer_words"],
        ),
        (
            "changed_word_count",
            per_example[per_example["word_count_group"] != "same_word_count"],
        ),
    ]

    summary = pd.DataFrame(
        [summarize_group(name, g, len(per_example)) for name, g in groups if len(g) > 0]
    )
    summary.to_csv(OUT_DIR / "summary_by_word_count_group.csv", index=False)

    dependency_counts = (
        per_example.assign(
            dependency_case=lambda x: x.apply(
                lambda r: (
                    "WER improved + no-space CER improved"
                    if r["wer_improved"] and r["no_space_cer_improved"]
                    else "WER improved only"
                    if r["wer_improved"] and not r["no_space_cer_improved"]
                    else "no-space CER improved only"
                    if (not r["wer_improved"]) and r["no_space_cer_improved"]
                    else "neither improved"
                ),
                axis=1,
            )
        )
        .groupby("dependency_case", as_index=False)
        .size()
        .rename(columns={"size": "N"})
    )
    dependency_counts["share"] = dependency_counts["N"] / len(per_example)
    dependency_counts.to_csv(OUT_DIR / "wer_vs_no_space_cer_dependency.csv", index=False)

    suspicious = per_example[per_example["wer_improved_but_no_space_not"]].copy()
    suspicious = suspicious.sort_values(
        ["wer_improvement", "no_space_cer_improvement"],
        ascending=[False, True],
    )
    suspicious[
        [
            "line_id",
            "variant_id",
            "clean_words",
            "noisy_words",
            "prediction_words",
            "noisy_clean_word_delta",
            "prediction_clean_word_delta",
            "identity_wer",
            "byt5_wer",
            "wer_improvement",
            "identity_no_space_cer",
            "byt5_no_space_cer",
            "no_space_cer_improvement",
            "noisy",
            "prediction",
            "clean",
        ]
    ].head(50).to_csv(OUT_DIR / "examples_wer_improved_but_no_space_not.csv", index=False)

    pd.set_option("display.max_columns", 50)
    pd.set_option("display.width", 220)

    print("\nSaved outputs to:", OUT_DIR)
    print("\n=== Summary by word-count group ===")
    print(summary.to_string(index=False))

    print("\n=== WER vs no-space CER dependency ===")
    print(dependency_counts.to_string(index=False))

    print("\n=== Key interpretation numbers ===")
    all_row = summary[summary["group"] == "all"].iloc[0]
    print(f"Raw WER improvement:      {all_row['WER_abs_improvement']:.6f}")
    print(f"Raw CER improvement:      {all_row['CER_abs_improvement']:.6f}")
    print(f"No-space CER improvement: {all_row['no_space_CER_abs_improvement']:.6f}")
    print(
        "WER improved but no-space CER did not improve share: "
        f"{all_row['WER_improved_but_no_space_not_share']:.2%}"
    )


if __name__ == "__main__":
    main()
