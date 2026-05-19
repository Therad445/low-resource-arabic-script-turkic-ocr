"""
Create synthetic noisy-clean dataset splits.

Important:
The split is done by original clean line_id before generating final files.
This avoids leakage where noisy variants of the same clean line appear in both
train and test.

Example:
python src/make_dataset.py --input data/raw/clean_text.txt --out_dir data/processed --variants 5
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.postcorrection.noise_generator import NoiseConfig, inject_noise


def read_clean_lines(path: Path) -> list[str]:
    lines = []
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = " ".join(line.strip().split())
        if line and line not in seen:
            lines.append(line)
            seen.add(line)
    return lines


def build_pairs(lines_with_ids: list[tuple[int, str]], variants: int, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    config = NoiseConfig()

    for line_id, clean in lines_with_ids:
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    parser.add_argument("--variants", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    lines = read_clean_lines(args.input)
    if len(lines) < 20:
        raise ValueError("Please provide at least 20 clean lines for a meaningful split.")

    indexed_lines = list(enumerate(lines))

    train_lines, temp_lines = train_test_split(
        indexed_lines,
        test_size=0.2,
        random_state=args.seed,
        shuffle=True,
    )
    valid_lines, test_lines = train_test_split(
        temp_lines,
        test_size=0.5,
        random_state=args.seed,
        shuffle=True,
    )

    train_df = build_pairs(train_lines, variants=args.variants, seed=args.seed)
    valid_df = build_pairs(valid_lines, variants=args.variants, seed=args.seed + 1)
    test_df = build_pairs(test_lines, variants=args.variants, seed=args.seed + 2)

    train_df.to_csv(args.out_dir / "train.csv", index=False)
    valid_df.to_csv(args.out_dir / "valid.csv", index=False)
    test_df.to_csv(args.out_dir / "test.csv", index=False)

    stats = pd.DataFrame(
        [
            {
                "split": "train",
                "clean_lines": len(train_lines),
                "noisy_clean_pairs": len(train_df),
                "avg_clean_chars": round(train_df["clean"].str.len().mean(), 2),
                "avg_noisy_chars": round(train_df["noisy"].str.len().mean(), 2),
            },
            {
                "split": "valid",
                "clean_lines": len(valid_lines),
                "noisy_clean_pairs": len(valid_df),
                "avg_clean_chars": round(valid_df["clean"].str.len().mean(), 2),
                "avg_noisy_chars": round(valid_df["noisy"].str.len().mean(), 2),
            },
            {
                "split": "test",
                "clean_lines": len(test_lines),
                "noisy_clean_pairs": len(test_df),
                "avg_clean_chars": round(test_df["clean"].str.len().mean(), 2),
                "avg_noisy_chars": round(test_df["noisy"].str.len().mean(), 2),
            },
        ]
    )
    stats.to_csv(args.out_dir / "dataset_stats.csv", index=False)

    print(stats.to_string(index=False))
    print(f"\nSaved dataset to {args.out_dir}")


if __name__ == "__main__":
    main()
