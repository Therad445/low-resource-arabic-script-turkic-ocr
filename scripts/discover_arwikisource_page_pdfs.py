#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

API = "https://ar.wikisource.org/w/api.php"
USER_AGENT = "low-resource-arabic-script-turkic-ocr/0.1"

TURKIC_KEYWORDS = [
    "ترك",
    "تركي",
    "تركية",
    "الترك",
    "تورك",
    "توركي",
    "عثمان",
    "عثماني",
    "تاتار",
    "تتر",
    "قبجاق",
    "جغتاي",
    "تركستان",
    "ديوان",
]


def api_get(params: dict[str, str]) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)

    for attempt in range(6):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        try:
            time.sleep(0.5)
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as error:
            if error.code == 429:
                retry_after = error.headers.get("Retry-After")
                wait_seconds = (
                    int(retry_after)
                    if retry_after and retry_after.isdigit()
                    else 15 * (attempt + 1)
                )
                print(f"warning: 429 Too Many Requests; sleeping {wait_seconds}s")
                time.sleep(wait_seconds)
                continue

            print(f"warning: HTTP {error.code}: {url}")
            return {}

        except urllib.error.URLError as error:
            wait_seconds = 10 * (attempt + 1)
            print(f"warning: URL error {error}; sleeping {wait_seconds}s")
            time.sleep(wait_seconds)

    print(f"warning: failed after retries: {url}")
    return {}


def looks_turkic(text: str) -> bool:
    return any(keyword in text for keyword in TURKIC_KEYWORDS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="outputs/wikisource_discovery/arwikisource_page_pdf_candidates.csv",
    )
    parser.add_argument("--mode", choices=["all", "turkic"], default="all")
    parser.add_argument("--min-pages", type=int, default=10)
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    pages_by_pdf: dict[str, set[int]] = defaultdict(set)

    apcontinue: str | None = None
    total_seen = 0

    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "apnamespace": "104",
            "aplimit": "max",
            "format": "json",
            "formatversion": "2",
        }

        if apcontinue:
            params["apcontinue"] = apcontinue

        data = api_get(params)

        items = data.get("query", {}).get("allpages", [])
        total_seen += len(items)
        print(f"seen page-namespace titles: {total_seen}")

        for item in items:
            title = item["title"]

            # Example: صفحة:أساس البلاغة1.pdf/10
            match = re.match(r"^صفحة:(.+\.(?:pdf|djvu))/(\d+)$", title, flags=re.I)
            if not match:
                continue

            file_title = match.group(1)
            page_no = int(match.group(2))

            if args.mode == "turkic" and not looks_turkic(file_title):
                continue

            pages_by_pdf[file_title].add(page_no)

        apcontinue = data.get("continue", {}).get("apcontinue")
        if not apcontinue:
            break

    rows = []

    for pdf_title, pages in pages_by_pdf.items():
        pages_sorted = sorted(pages)

        if len(pages_sorted) < args.min_pages:
            continue

        rows.append(
            {
                "pdf_title": pdf_title,
                "existing_page_count": len(pages_sorted),
                "first_existing_pages": " ".join(map(str, pages_sorted[:80])),
                "file_url": "https://ar.wikisource.org/wiki/"
                + urllib.parse.quote("ملف:" + pdf_title),
                "index_url": "https://ar.wikisource.org/wiki/"
                + urllib.parse.quote("فهرس:" + pdf_title),
                "sample_page_url": "https://ar.wikisource.org/wiki/"
                + urllib.parse.quote(f"صفحة:{pdf_title}/{pages_sorted[0]}"),
            }
        )

    rows.sort(key=lambda row: int(row["existing_page_count"]), reverse=True)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "pdf_title",
            "existing_page_count",
            "first_existing_pages",
            "file_url",
            "index_url",
            "sample_page_url",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote: {out_path}")
    print(f"candidates: {len(rows)}")

    for row in rows[:50]:
        print(row["existing_page_count"], row["pdf_title"], row["sample_page_url"])


if __name__ == "__main__":
    main()
