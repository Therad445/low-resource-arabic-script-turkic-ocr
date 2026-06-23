#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import time
import urllib.parse
import urllib.request
from pathlib import Path

PDF_FILE_NAME = "أوقرانيا،_روسيه_وتوركيه_(مقالەلر_مجموعەسى).pdf"
COMMONS_THUMB_BASE = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74"


def build_page_image_url(page_no: int, width: int = 1920) -> str:
    encoded_pdf = urllib.parse.quote(PDF_FILE_NAME, safe="")
    return (
        f"{COMMONS_THUMB_BASE}/{encoded_pdf}/"
        f"page{page_no}-{width}px-{encoded_pdf}.jpg"
        f"?utm_source=ar.wikisource.org&utm_campaign=index&utm_content=thumbnail"
    )


def download(url: str, out_path: Path) -> None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "low-resource-arabic-script-turkic-ocr/0.1"},
    )

    with urllib.request.urlopen(req, timeout=120) as response:
        out_path.write_bytes(response.read())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--width", type=int, default=1920)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []

    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            page_no = int(row["pdf_page"])
            page_id = row["page_id"]
            out_path = out_dir / f"{page_id}.jpg"
            image_url = build_page_image_url(page_no, width=args.width)

            print("page:", page_id, "pdf_page:", page_no)

            if out_path.exists() and out_path.stat().st_size > 0:
                print("  exists:", out_path)
                row["page_image_url"] = image_url
                row["page_image_path"] = str(out_path)
                row["image_download_status"] = "already_exists"
                rows.append(row)
                continue

            print("  image:", image_url)

            try:
                time.sleep(args.sleep)
                download(image_url, out_path)
                row["page_image_url"] = image_url
                row["page_image_path"] = str(out_path)
                row["image_download_status"] = "ok"
            except Exception as exc:
                print("  failed:", exc)
                row["page_image_url"] = image_url
                row["page_image_path"] = ""
                row["image_download_status"] = f"failed: {exc}"

            rows.append(row)

    out_manifest = manifest_path.parent / "wikisource_pages_with_images_manifest.csv"

    fieldnames = list(rows[0].keys())
    with out_manifest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("wrote:", out_manifest)
    print("rows:", len(rows))


if __name__ == "__main__":
    main()
