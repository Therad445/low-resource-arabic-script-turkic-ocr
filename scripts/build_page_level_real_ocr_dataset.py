#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--ocr-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--dataset-version", default="real_ocr_ukr_rus_tur_v1_local")
    parser.add_argument("--ocr-engine", default="tesseract")
    parser.add_argument("--ocr-config", default="ara_psm6")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    ocr_dir = Path(args.ocr_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            page_id = row["page_id"]
            clean_path = Path(row["clean_text_path"])
            ocr_path = ocr_dir / f"{page_id}.txt"

            clean_text = (
                clean_path.read_text(encoding="utf-8", errors="replace")
                if clean_path.exists()
                else ""
            )
            ocr_text = (
                ocr_path.read_text(encoding="utf-8", errors="replace") if ocr_path.exists() else ""
            )

            rows.append(
                {
                    "dataset_version": args.dataset_version,
                    "source_id": row["source_id"],
                    "pdf_page": row["pdf_page"],
                    "page_id": page_id,
                    "url": row["url"],
                    "page_image_path": row.get("page_image_path", ""),
                    "ocr_engine": args.ocr_engine,
                    "ocr_config": args.ocr_config,
                    "ocr_text": ocr_text,
                    "clean_text": clean_text,
                    "ocr_chars": len(ocr_text),
                    "clean_chars": len(clean_text),
                    "verification_level": row.get("verification_level", ""),
                    "notes": "Ottoman Turkish printed source in Arabic script; local research dataset",
                }
            )

    if not rows:
        raise RuntimeError("No rows built")

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("wrote:", out_path)
    print("rows:", len(rows))


if __name__ == "__main__":
    main()
