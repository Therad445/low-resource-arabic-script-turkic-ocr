"""
Train-derived character confusion baseline for OCR post-correction.

The baseline learns a conservative noisy-character -> clean-character mapping
from aligned train noisy-clean pairs. It is intentionally simple and non-neural:
it can only substitute or delete existing characters, but it cannot generate
missing characters from context.
"""

import argparse
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from src.postcorrection.evaluate import evaluate_dataframe

EMPTY = ""


def levenshtein_alignment(src, tgt):
    """Return character-level alignment pairs: (src_char_or_EMPTY, tgt_char_or_EMPTY)."""
    n, m = len(src), len(tgt)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        dp[i][0] = i
        back[i][0] = "del_src"
    for j in range(1, m + 1):
        dp[0][j] = j
        back[0][j] = "ins_tgt"

    for i in range(1, n + 1):
        sc = src[i - 1]
        for j in range(1, m + 1):
            tc = tgt[j - 1]
            sub_cost = 0 if sc == tc else 1
            candidates = [
                (dp[i - 1][j - 1] + sub_cost, "match_or_sub"),
                (dp[i - 1][j] + 1, "del_src"),
                (dp[i][j - 1] + 1, "ins_tgt"),
            ]
            best_cost, best_op = min(candidates, key=lambda x: x[0])
            dp[i][j] = best_cost
            back[i][j] = best_op

    pairs = []
    i, j = n, m
    while i > 0 or j > 0:
        op = back[i][j]
        if op == "match_or_sub":
            pairs.append((src[i - 1], tgt[j - 1]))
            i -= 1
            j -= 1
        elif op == "del_src":
            pairs.append((src[i - 1], EMPTY))
            i -= 1
        elif op == "ins_tgt":
            pairs.append((EMPTY, tgt[j - 1]))
            j -= 1
        else:
            raise RuntimeError("Unexpected backtrace operation")

    pairs.reverse()
    return pairs


def build_mapping(train_df, min_count=5, min_ratio=0.65):
    """Build conservative char mapping from train alignments."""
    counts = defaultdict(Counter)

    noisy_values = train_df["noisy"].fillna("").astype(str).tolist()
    clean_values = train_df["clean"].fillna("").astype(str).tolist()

    for noisy, clean in zip(noisy_values, clean_values, strict=True):
        for src_ch, tgt_ch in levenshtein_alignment(noisy, clean):
            if src_ch == EMPTY:
                continue
            counts[src_ch][tgt_ch] += 1

    mapping = {}
    rows = []

    for src_ch in sorted(counts.keys()):
        counter = counts[src_ch]
        total = sum(counter.values())
        best_tgt, best_count = counter.most_common(1)[0]
        ratio = best_count / total if total else 0.0
        accepted = total >= min_count and ratio >= min_ratio and best_tgt != src_ch

        if accepted:
            mapping[src_ch] = best_tgt

        rows.append(
            {
                "source_char": src_ch,
                "target_char": best_tgt,
                "count": best_count,
                "total_source_count": total,
                "ratio": ratio,
                "accepted": accepted,
                "source_unicode": "U+" + format(ord(src_ch), "04X"),
                "target_unicode": "EMPTY"
                if best_tgt == EMPTY
                else "U+" + format(ord(best_tgt), "04X"),
            }
        )

    mapping_df = pd.DataFrame(rows).sort_values(
        ["accepted", "total_source_count", "ratio"],
        ascending=[False, False, False],
    )
    return mapping, mapping_df


def apply_mapping(text, mapping):
    return "".join(mapping.get(ch, ch) for ch in str(text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--min_count", type=int, default=5)
    parser.add_argument("--min_ratio", type=float, default=0.65)
    args = parser.parse_args()

    train_df = pd.read_csv(args.train)
    test_df = pd.read_csv(args.test)

    mapping, mapping_df = build_mapping(
        train_df,
        min_count=args.min_count,
        min_ratio=args.min_ratio,
    )

    out_df = test_df.copy()
    out_df["char_confusion_prediction"] = (
        out_df["noisy"].fillna("").astype(str).map(lambda s: apply_mapping(s, mapping))
    )

    metrics = evaluate_dataframe(
        out_df,
        pred_col="char_confusion_prediction",
        target_col="clean",
    )
    metrics["method"] = "Train-derived char-confusion baseline"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    args.mapping.parent.mkdir(parents=True, exist_ok=True)

    out_df.to_csv(args.out, index=False)
    pd.DataFrame([metrics])[["method", "CER", "WER", "ExactMatch", "N"]].to_csv(
        args.metrics,
        index=False,
    )
    mapping_df.to_csv(args.mapping, index=False)

    print("Accepted mappings:", int(mapping_df["accepted"].sum()))
    print(pd.DataFrame([metrics]).to_string(index=False))


if __name__ == "__main__":
    main()
