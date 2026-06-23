#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

HIGH_RISK_PATTERNS = [
    r"حكومت",
    r"حکومت",
    r"موسقوف",
    r"سياس",
    r"سیاس",
    r"حريت",
    r"حرية",
    r"ظلم",
    r"مظلوم",
    r"دوما",
    r"پروتست",
    r"اعتراض",
    r"محاربه",
    r"عسكر",
    r"عسکر",
    r"استقلال",
    r"اختلال",
    r"اتحاد",
    r"قوم",
    r"قومی",
]

MEDIUM_RISK_PATTERNS = [
    r"اوقراين",
    r"اوقراین",
    r"روس",
    r"روسيه",
    r"روسیه",
    r"توركيه",
    r"تركيه",
    r"غاليچيا",
    r"غالچيا",
    r"كييف",
    r"کیف",
    r"شەوچەنقو",
]


def count_patterns(text: str, patterns: list[str]) -> int:
    total = 0
    for pattern in patterns:
        total += len(re.findall(pattern, text))
    return total


def classify_page(high_count: int, medium_count: int, clean_chars: int) -> str:
    if clean_chars == 0:
        return "empty"

    if high_count >= 2:
        return "high"

    if high_count == 1 and medium_count >= 2:
        return "high"

    if medium_count >= 8:
        return "high"

    if high_count == 1 or medium_count >= 3:
        return "medium"

    return "low"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        required=True,
        help="wikisource_pages_manifest.csv",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for risk report.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    safe_pages = []
    quarantine_pages = []

    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            clean_path = Path(row["clean_text_path"])
            text = clean_path.read_text(encoding="utf-8") if clean_path.exists() else ""

            high_count = count_patterns(text, HIGH_RISK_PATTERNS)
            medium_count = count_patterns(text, MEDIUM_RISK_PATTERNS)
            clean_chars = len(text)
            risk = classify_page(high_count, medium_count, clean_chars)

            out_row = {
                **row,
                "risk_level": risk,
                "high_keyword_hits": high_count,
                "medium_keyword_hits": medium_count,
            }
            rows.append(out_row)

            page = str(row["pdf_page"])

            if risk == "low":
                safe_pages.append(page)
            elif risk in {"medium", "high"}:
                quarantine_pages.append(page)

    report_path = out_dir / "wikisource_risk_page_report.csv"
    with report_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    (out_dir / "safe_pages.txt").write_text(" ".join(safe_pages), encoding="utf-8")
    (out_dir / "quarantine_pages.txt").write_text(" ".join(quarantine_pages), encoding="utf-8")

    print(f"Wrote {report_path}")
    print(f"safe pages: {' '.join(safe_pages) if safe_pages else '(none)'}")
    print(f"quarantine pages: {' '.join(quarantine_pages) if quarantine_pages else '(none)'}")


if __name__ == "__main__":
    main()
