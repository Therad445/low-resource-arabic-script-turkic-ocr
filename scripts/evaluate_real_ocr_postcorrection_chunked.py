#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


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
    return levenshtein(pred.split(), ref.split()) / max(1, len(ref.split()))


def no_space_cer(pred: str, ref: str) -> float:
    pred_norm = re.sub(r"\s+", "", pred)
    ref_norm = re.sub(r"\s+", "", ref)
    return cer(pred_norm, ref_norm)


def is_bad_generation(source: str, output: str) -> bool:
    source = source.strip()
    output = output.strip()

    if not output:
        return True

    if len(source) >= 100:
        ratio = len(output) / max(1, len(source))
        if ratio < 0.35 or ratio > 1.80:
            return True

    # грубая защита от повторов вида "ــــــ" или одного символа/куска
    compact = re.sub(r"\s+", "", output)
    if len(compact) >= 50:
        most_common_ratio = max(compact.count(ch) for ch in set(compact)) / len(compact)
        if most_common_ratio > 0.55:
            return True

    return False


def split_into_token_chunks(
    text: str,
    tokenizer,
    max_source_length: int,
    safety_margin: int = 16,
) -> list[str]:
    lines = text.splitlines()
    chunks: list[str] = []
    current: list[str] = []

    limit = max_source_length - safety_margin

    def token_len(s: str) -> int:
        return len(tokenizer(s, add_special_tokens=True).input_ids)

    for line in lines:
        candidate_lines = current + [line]
        candidate = "\n".join(candidate_lines).strip()

        if not candidate:
            continue

        if token_len(candidate) <= limit:
            current.append(line)
            continue

        if current:
            chunks.append("\n".join(current).strip())
            current = []

        # Если одна строка слишком длинная, режем её грубо по символам.
        if token_len(line) > limit:
            buf = ""
            for ch in line:
                cand = buf + ch
                if token_len(cand) <= limit:
                    buf = cand
                else:
                    if buf.strip():
                        chunks.append(buf.strip())
                    buf = ch
            if buf.strip():
                current = [buf]
        else:
            current = [line]

    if current:
        chunks.append("\n".join(current).strip())

    return [c for c in chunks if c.strip()]


@torch.inference_mode()
def correct_chunks(
    chunks: list[str],
    tokenizer,
    model,
    device: torch.device,
    max_source_length: int,
    max_target_length: int,
    num_beams: int,
    batch_size: int,
) -> list[str]:
    outputs: list[str] = []

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]

        encoded = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_source_length,
        ).to(device)

        generated = model.generate(
            **encoded,
            max_length=max_target_length,
            num_beams=num_beams,
            do_sample=False,
        )

        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        outputs.extend(decoded)

    return outputs


def summarize(df: pd.DataFrame, prefix: str) -> dict[str, float | int]:
    return {
        "system": prefix,
        "n": len(df),
        "mean_cer": float(df[f"{prefix}_cer"].mean()),
        "median_cer": float(df[f"{prefix}_cer"].median()),
        "mean_wer": float(df[f"{prefix}_wer"].mean()),
        "median_wer": float(df[f"{prefix}_wer"].median()),
        "mean_no_space_cer": float(df[f"{prefix}_no_space_cer"].mean()),
        "median_no_space_cer": float(df[f"{prefix}_no_space_cer"].median()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--predictions-out", required=True)
    parser.add_argument("--metrics-out", required=True)
    parser.add_argument("--max-source-length", type=int, default=512)
    parser.add_argument("--max-target-length", type=int, default=512)
    parser.add_argument("--num-beams", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device:", device)

    df = pd.read_csv(args.input)

    if args.max_pages is not None:
        df = df.head(args.max_pages).copy()

    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_path).to(device)
    model.eval()

    rows = []

    for idx, row in df.iterrows():
        page_id = str(row["page_id"])
        raw_ocr = str(row["ocr_text"])
        gold = str(row["clean_text"])

        chunks = split_into_token_chunks(
            raw_ocr,
            tokenizer=tokenizer,
            max_source_length=args.max_source_length,
        )

        corrected_chunks = correct_chunks(
            chunks,
            tokenizer=tokenizer,
            model=model,
            device=device,
            max_source_length=args.max_source_length,
            max_target_length=args.max_target_length,
            num_beams=args.num_beams,
            batch_size=args.batch_size,
        )

        corrected = "\n".join(corrected_chunks)

        guarded = raw_ocr if is_bad_generation(raw_ocr, corrected) else corrected

        raw_cer = cer(raw_ocr, gold)
        byt5_cer = cer(corrected, gold)
        guarded_cer = cer(guarded, gold)

        rows.append(
            {
                **row.to_dict(),
                "chunk_count": len(chunks),
                "byt5_text": corrected,
                "guarded_byt5_text": guarded,
                "raw_cer": raw_cer,
                "raw_wer": wer(raw_ocr, gold),
                "raw_no_space_cer": no_space_cer(raw_ocr, gold),
                "byt5_cer": byt5_cer,
                "byt5_wer": wer(corrected, gold),
                "byt5_no_space_cer": no_space_cer(corrected, gold),
                "guarded_byt5_cer": guarded_cer,
                "guarded_byt5_wer": wer(guarded, gold),
                "guarded_byt5_no_space_cer": no_space_cer(guarded, gold),
                "byt5_delta_cer": byt5_cer - raw_cer,
                "guarded_delta_cer": guarded_cer - raw_cer,
                "byt5_status": (
                    "improved" if byt5_cer < raw_cer else "same" if byt5_cer == raw_cer else "worse"
                ),
                "guarded_status": (
                    "improved"
                    if guarded_cer < raw_cer
                    else "same"
                    if guarded_cer == raw_cer
                    else "worse"
                ),
            }
        )

        print(
            f"[{idx + 1}/{len(df)}] {page_id}: "
            f"chunks={len(chunks)} raw_cer={raw_cer:.4f} "
            f"byt5_cer={byt5_cer:.4f} guarded_cer={guarded_cer:.4f}"
        )

    pred_df = pd.DataFrame(rows)

    predictions_out = Path(args.predictions_out)
    metrics_out = Path(args.metrics_out)
    predictions_out.parent.mkdir(parents=True, exist_ok=True)
    metrics_out.parent.mkdir(parents=True, exist_ok=True)

    pred_df.to_csv(predictions_out, index=False)

    summary = pd.DataFrame(
        [
            summarize(pred_df, "raw"),
            summarize(pred_df, "byt5"),
            summarize(pred_df, "guarded_byt5"),
        ]
    )

    status_rows = []
    for system in ["byt5", "guarded"]:
        col = "byt5_status" if system == "byt5" else "guarded_status"
        counts = pred_df[col].value_counts().to_dict()
        status_rows.append(
            {
                "system": system,
                "improved": int(counts.get("improved", 0)),
                "same": int(counts.get("same", 0)),
                "worse": int(counts.get("worse", 0)),
            }
        )

    status_df = pd.DataFrame(status_rows)

    with metrics_out.open("w", encoding="utf-8") as f:
        f.write("# Summary\n")
        summary.to_csv(f, index=False)
        f.write("\n# Page status counts\n")
        status_df.to_csv(f, index=False)

    print()
    print(summary.to_string(index=False))
    print()
    print(status_df.to_string(index=False))
    print()
    print("wrote predictions:", predictions_out)
    print("wrote metrics:", metrics_out)


if __name__ == "__main__":
    main()
