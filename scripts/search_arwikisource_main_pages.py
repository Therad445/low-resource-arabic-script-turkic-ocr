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
from pathlib import Path

API = "https://ar.wikisource.org/w/api.php"
USER_AGENT = "low-resource-arabic-script-turkic-ocr/0.1"

QUERIES = [
    "بالتركية العثمانية",
    "بالتركيَّة العثمانيَّة",
    "التركية العثمانية",
    "تركية عثمانية",
    "عثمانية",
    "جمعية الاتحاد والترقي",
    "تركيا",
    "توركيه",
    "تاتار",
    "جغتاي",
    "تركستان",
]


def api_get(params: dict[str, str]) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)

    for attempt in range(6):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        try:
            time.sleep(2.0)
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as error:
            if error.code == 429:
                retry_after = error.headers.get("Retry-After")
                wait_seconds = (
                    int(retry_after)
                    if retry_after and retry_after.isdigit()
                    else 20 * (attempt + 1)
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


def search_pages(query: str, limit: int) -> list[dict]:
    out = []
    sroffset = 0

    while len(out) < limit:
        data = api_get(
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srnamespace": "0",
                "srlimit": "50",
                "sroffset": str(sroffset),
                "format": "json",
                "formatversion": "2",
            }
        )

        items = data.get("query", {}).get("search", [])
        if not items:
            break

        out.extend(items)
        sroffset += len(items)

        if "continue" not in data:
            break

    return out[:limit]


def parse_links(title: str) -> list[str]:
    data = api_get(
        {
            "action": "parse",
            "page": title,
            "prop": "links",
            "format": "json",
            "formatversion": "2",
        }
    )

    links = []
    for link in data.get("parse", {}).get("links", []):
        link_title = link.get("title", "")
        if link_title.startswith("ملف:") and re.search(r"\.(pdf|djvu)$", link_title, re.I):
            links.append(link_title)
        if link_title.startswith("فهرس:") and re.search(r"\.(pdf|djvu)$", link_title, re.I):
            links.append(link_title)

    return sorted(set(links))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out", default="outputs/wikisource_discovery/mainspace_turkic_related_pages.csv"
    )
    parser.add_argument("--limit-per-query", type=int, default=50)
    args = parser.parse_args()

    rows = []
    seen = set()

    for query in QUERIES:
        print("query:", query)
        results = search_pages(query, args.limit_per_query)

        for item in results:
            title = item["title"]

            if title in seen:
                continue

            seen.add(title)
            links = parse_links(title)

            rows.append(
                {
                    "query": query,
                    "title": title,
                    "snippet": item.get("snippet", ""),
                    "pdf_or_index_links": " | ".join(links),
                    "page_url": "https://ar.wikisource.org/wiki/"
                    + urllib.parse.quote(title.replace(" ", "_")),
                }
            )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["query", "title", "snippet", "pdf_or_index_links", "page_url"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("wrote:", out_path)
    print("rows:", len(rows))


if __name__ == "__main__":
    main()
