from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://ar.wikisource.org/w/api.php"
BASE_TITLE = "صفحة:أوقرانيا، روسيه وتوركيه (مقالەلر مجموعەسى).pdf/{}"


def fetch_wikitext(title: str) -> str:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": title,
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)

    headers = {
        "User-Agent": (
            "low-resource-arabic-script-turkic-ocr/0.1 "
            "(https://github.com/Therad445/low-resource-arabic-script-turkic-ocr; "
            "islamov.radmir2014@yandex.ru)"
        ),
        "Accept": "application/json",
    }

    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    pages = data.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        return ""

    revisions = pages[0].get("revisions", [])
    if not revisions:
        return ""

    revision = revisions[0]
    if "slots" in revision:
        return revision["slots"]["main"].get("content", "")

    return revision.get("content", "")


def clean_wikitext(text: str) -> str:
    text = re.sub(r"<noinclude>.*?</noinclude>", " ", text, flags=re.S)
    text = re.sub(r"<ref.*?>.*?</ref>", " ", text, flags=re.S)
    text = re.sub(r"<.*?>", " ", text)

    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\{\{[^{}]*\}\}", " ", text)

    text = re.sub(r"\[\[(?:File|Image|تصنيف|Category):[^\]]+\]\]", " ", text, flags=re.I)
    text = re.sub(r"\[\[[^\]|]+\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    text = text.replace("'''", "").replace("''", "")
    text = re.sub(r"[{}[\]|]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def arabic_ratio(text: str) -> float:
    if not text:
        return 0.0
    arabic_chars = len(re.findall(r"[\u0600-\u06FF]", text))
    return arabic_chars / max(len(text), 1)


def make_blocks(text: str, min_len: int, max_len: int) -> list[str]:
    parts = re.split(r"(?<=[.!؟؛۔:])\s+|\n+", text)

    blocks = []
    buffer = ""

    for part in parts:
        part = " ".join(part.strip().split())
        if not part:
            continue

        candidate = f"{buffer} {part}".strip() if buffer else part

        if len(candidate) < min_len:
            buffer = candidate
            continue

        if len(candidate) <= max_len:
            blocks.append(candidate)
            buffer = ""
        else:
            if len(buffer) >= min_len:
                blocks.append(buffer)
            buffer = part

    if len(buffer) >= min_len:
        blocks.append(buffer)

    result = []
    seen = set()

    for block in blocks:
        block = " ".join(block.split())

        if len(block) < min_len:
            continue
        if len(block) > max_len:
            continue
        if arabic_ratio(block) < 0.55:
            continue
        if block in seen:
            continue

        result.append(block)
        seen.add(block)

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=5)
    parser.add_argument("--end", type=int, default=71)
    parser.add_argument(
        "--out", type=Path, default=Path("data/postcorrection/raw/arabic_turkic_clean_text.txt")
    )
    parser.add_argument("--sources", type=Path, default=Path("data/postcorrection/raw/SOURCES.md"))
    parser.add_argument("--min_len", type=int, default=35)
    parser.add_argument("--max_len", type=int, default=180)
    args = parser.parse_args()

    all_blocks = []

    for page_num in range(args.start, args.end + 1):
        title = BASE_TITLE.format(page_num)
        print(f"Fetching page {page_num}: {title}")

        raw = fetch_wikitext(title)
        cleaned = clean_wikitext(raw)
        blocks = make_blocks(cleaned, min_len=args.min_len, max_len=args.max_len)

        all_blocks.extend(blocks)
        time.sleep(0.3)

    result = []
    seen = set()

    for block in all_blocks:
        if block not in seen:
            result.append(block)
            seen.add(block)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(result) + "\n", encoding="utf-8")

    args.sources.write_text(
        """# Sources for Arabic-Turkic postcorrection pilot

## Primary source

- Title: أوقرانيا، روسيه وتوركيه (مقالەلر مجموعەسى)
- Source platform: Arabic Wikisource
- Publication year listed by Wikisource: 1915
- Publisher listed by Wikisource: المطبعة الخيرية وشركاؤه
- Script/language profile: Ottoman Turkish / Arabic-script Turkic
- Collection method: MediaWiki API, Page namespace, pages 5-71
- License note: source text is collected from Wikisource and should be attributed in derivative datasets and reports.

The generated file `arabic_turkic_clean_text.txt` contains cleaned text blocks extracted from page transcriptions.
""",
        encoding="utf-8",
    )

    print(f"Saved {len(result)} blocks to {args.out}")
    print(f"Saved source note to {args.sources}")


if __name__ == "__main__":
    main()
