#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def edit_distance_chars(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def edit_distance_words(a: list[str], b: list[str]) -> int:
    prev = list(range(len(b) + 1))
    for i, wa in enumerate(a, 1):
        cur = [i]
        for j, wb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (wa != wb)))
        prev = cur
    return prev[-1]


def cer(pred: str, ref: str) -> float:
    if not ref:
        return 0.0 if not pred else 1.0
    return edit_distance_chars(pred, ref) / len(ref)


def wer(pred: str, ref: str) -> float:
    pred_words = pred.split()
    ref_words = ref.split()
    if not ref_words:
        return 0.0 if not pred_words else 1.0
    return edit_distance_words(pred_words, ref_words) / len(ref_words)


def no_space(text: str) -> str:
    return "".join(text.split())


def conservative_fallback(ocr_text: str, pred_text: str) -> str:
    ocr_text = ocr_text.strip()
    pred_text = pred_text.strip()

    if not pred_text:
        return ocr_text
    if not ocr_text:
        return pred_text

    len_ratio = len(pred_text) / max(1, len(ocr_text))
    if len_ratio < 0.55 or len_ratio > 1.60:
        return ocr_text

    change_rate = edit_distance_chars(ocr_text, pred_text) / max(len(ocr_text), len(pred_text), 1)
    if change_rate > 0.55:
        return ocr_text

    return pred_text


def summarize(rows: list[dict[str, str]], field: str) -> dict[str, float]:
    n = len(rows)
    return {
        "CER": sum(cer(row[field], row["clean_text"]) for row in rows) / n,
        "WER": sum(wer(row[field], row["clean_text"]) for row in rows) / n,
        "NoSpaceCER": sum(cer(no_space(row[field]), no_space(row["clean_text"])) for row in rows)
        / n,
        "N": n,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--input", default="data/postcorrection/real_sanity/real_ocr_sanity.csv")
    parser.add_argument(
        "--predictions-out",
        default="docs/nlp_final_revision/tables/real_ocr_postcorrection_predictions.csv",
    )
    parser.add_argument(
        "--metrics-out",
        default="docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv",
    )
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--num-beams", type=int, default=1)
    args = parser.parse_args()

    input_path = Path(args.input)
    predictions_out = Path(args.predictions_out)
    metrics_out = Path(args.metrics_out)

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"Rows: {len(rows)}")
    print(f"Model: {args.model_path}")

    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_path).to(device)
    model.eval()

    for i, row in enumerate(rows, 1):
        ocr_text = row["ocr_text"]

        inputs = tokenizer(
            ocr_text,
            return_tensors="pt",
            truncation=True,
            max_length=args.max_length,
        ).to(device)

        with torch.no_grad():
            generated = model.generate(
                **inputs,
                max_length=args.max_length,
                num_beams=args.num_beams,
            )

        pred_text = tokenizer.decode(generated[0], skip_special_tokens=True).strip()
        fallback_text = conservative_fallback(ocr_text, pred_text)

        row["pred_text"] = pred_text
        row["fallback_text"] = fallback_text
        row["identity_cer"] = f"{cer(ocr_text, row['clean_text']):.6f}"
        row["pred_cer"] = f"{cer(pred_text, row['clean_text']):.6f}"
        row["fallback_cer"] = f"{cer(fallback_text, row['clean_text']):.6f}"

        if i % 10 == 0:
            print(f"Decoded {i}/{len(rows)}")

    predictions_out.parent.mkdir(parents=True, exist_ok=True)
    metrics_out.parent.mkdir(parents=True, exist_ok=True)

    with predictions_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    metric_rows = []
    for method, field in [
        ("Real OCR identity (tesseract_ara_psm6)", "ocr_text"),
        ("Synthetic-trained ByT5 on real OCR", "pred_text"),
        ("Synthetic-trained ByT5 + conservative fallback", "fallback_text"),
    ]:
        values = summarize(rows, field)
        metric_rows.append(
            {
                "method": method,
                "CER": values["CER"],
                "WER": values["WER"],
                "NoSpaceCER": values["NoSpaceCER"],
                "N": values["N"],
            }
        )

    with metrics_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "CER", "WER", "NoSpaceCER", "N"])
        writer.writeheader()
        writer.writerows(metric_rows)

    print(f"Wrote {predictions_out}")
    print(f"Wrote {metrics_out}")
    for row in metric_rows:
        print(row)


if __name__ == "__main__":
    main()
