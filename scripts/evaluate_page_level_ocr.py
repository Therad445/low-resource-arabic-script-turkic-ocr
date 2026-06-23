#!/usr/bin/env python3
from __future__ import annotations

import argparse

import pandas as pd


def levenshtein(a: list[str] | str, b: list[str] | str) -> int:
    if len(a) < len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))

    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            replace = previous[j - 1] + (ca != cb)
            current.append(min(insert, delete, replace))
        previous = current

    return previous[-1]


def cer(pred: str, ref: str) -> float:
    return levenshtein(pred, ref) / max(1, len(ref))


def wer(pred: str, ref: str) -> float:
    pred_words = pred.split()
    ref_words = ref.split()
    return levenshtein(pred_words, ref_words) / max(1, len(ref_words))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    rows = []
    for _, row in df.iterrows():
        ref = str(row["clean_text"])
        pred = str(row["ocr_text"])

        rows.append(
            {
                **row.to_dict(),
                "cer": cer(pred, ref),
                "wer": wer(pred, ref),
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)

    print("rows:", len(out))
    print("mean CER:", float(out["cer"].mean()))
    print("median CER:", float(out["cer"].median()))
    print("mean WER:", float(out["wer"].mean()))
    print("median WER:", float(out["wer"].median()))
    print("wrote:", args.out)

    print()
    print("worst CER pages:")
    print(
        out.sort_values("cer", ascending=False)[
            ["page_id", "clean_chars", "ocr_chars", "cer", "wer"]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
