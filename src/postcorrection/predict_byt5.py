"""
Generate corrections with a fine-tuned ByT5/mT5 model.

Example:
python src/predict_byt5.py --model_dir models/byt5-small-ocr --test data/processed/test.csv --out results/byt5_predictions.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--max_source_length", type=int, default=256)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(str(args.model_dir))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(args.model_dir)).to(device)
    model.eval()

    df = pd.read_csv(args.test)
    noisy_texts = df["noisy"].fillna("").astype(str).tolist()

    predictions = []
    for i in range(0, len(noisy_texts), args.batch_size):
        batch = noisy_texts[i : i + args.batch_size]
        encoded = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=args.max_source_length,
        ).to(device)

        with torch.no_grad():
            output_ids = model.generate(
                **encoded,
                max_new_tokens=args.max_new_tokens,
                num_beams=4,
            )

        decoded = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        predictions.extend(decoded)

    df["prediction"] = predictions

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Saved predictions to {args.out}")


if __name__ == "__main__":
    main()
