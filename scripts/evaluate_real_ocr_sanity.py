from __future__ import annotations

import csv
import unicodedata
from collections import defaultdict
from pathlib import Path

INPUT = Path("data/postcorrection/real_sanity/real_ocr_sanity.csv")
OUT = Path("docs/nlp_final_revision/tables/real_ocr_sanity_metrics.csv")


BIDI_CONTROLS = {
    "\u200e",
    "\u200f",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    for ch in BIDI_CONTROLS:
        text = text.replace(ch, "")
    return " ".join(text.split())


def levenshtein(a: list[str], b: list[str]) -> int:
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


def cer(pred: str, ref: str) -> float:
    pred = normalize_text(pred)
    ref = normalize_text(ref)
    if not ref:
        return 0.0 if not pred else 1.0
    return levenshtein(list(pred), list(ref)) / len(ref)


def wer(pred: str, ref: str) -> float:
    pred = normalize_text(pred)
    ref = normalize_text(ref)
    ref_words = ref.split()
    pred_words = pred.split()
    if not ref_words:
        return 0.0 if not pred_words else 1.0
    return levenshtein(pred_words, ref_words) / len(ref_words)


def nospace_cer(pred: str, ref: str) -> float:
    pred = "".join(normalize_text(pred).split())
    ref = "".join(normalize_text(ref).split())
    if not ref:
        return 0.0 if not pred else 1.0
    return levenshtein(list(pred), list(ref)) / len(ref)


def main() -> None:
    rows = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("ocr_text") and row.get("clean_text"):
                rows.append(row)

    if not rows:
        raise SystemExit(f"No usable rows found in {INPUT}")

    grouped = defaultdict(list)
    for row in rows:
        grouped[row.get("ocr_engine", "unknown")].append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "CER", "WER", "NoSpaceCER", "N"])
        writer.writeheader()

        for engine, items in sorted(grouped.items()):
            writer.writerow(
                {
                    "method": f"Real OCR identity ({engine})",
                    "CER": sum(cer(r["ocr_text"], r["clean_text"]) for r in items) / len(items),
                    "WER": sum(wer(r["ocr_text"], r["clean_text"]) for r in items) / len(items),
                    "NoSpaceCER": sum(nospace_cer(r["ocr_text"], r["clean_text"]) for r in items)
                    / len(items),
                    "N": len(items),
                }
            )

    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
