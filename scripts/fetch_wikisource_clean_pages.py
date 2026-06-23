#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

API = "https://ar.wikisource.org/w/api.php"
DEFAULT_PDF_TITLE = "أوقرانيا،_روسيه_وتوركيه_(مقالەلر_مجموعەسى).pdf"
DEFAULT_SOURCE_ID = "WIKI_UKR_RUS_TUR"

USER_AGENT = (
    "low-resource-arabic-script-turkic-ocr/0.1 "
    "(research dataset collection; contact: therad445@gmail.com)"
)


class DivTextExtractor(HTMLParser):
    def __init__(self, target_class: str) -> None:
        super().__init__()
        self.target_class = target_class
        self.inside = False
        self.depth = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        class_attr = attrs_dict.get("class") or ""
        classes = set(class_attr.split())

        if not self.inside and tag == "div" and self.target_class in classes:
            self.inside = True
            self.depth = 1
            return

        if self.inside:
            if tag == "div":
                self.depth += 1
                self.chunks.append("\n")
            elif tag in {"p", "br"}:
                self.chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if not self.inside:
            return

        if tag == "p":
            self.chunks.append("\n\n")

        if tag == "div":
            self.depth -= 1
            if self.depth <= 0:
                self.inside = False

    def handle_data(self, data: str) -> None:
        if self.inside:
            self.chunks.append(data)

    def get_text(self) -> str:
        return "".join(self.chunks)


def request_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_rendered_html(title: str) -> str:
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "formatversion": "2",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    data = request_json(url)

    if "error" in data:
        code = data["error"].get("code")
        info = data["error"].get("info")
        print(f"  warning: MediaWiki API error: {code}: {info}")
        return ""

    return data["parse"]["text"]


def extract_page_text(rendered_html: str) -> str:
    # ProofreadPage rendered pages usually contain <div class="pagetext">...</div>.
    parser = DivTextExtractor("pagetext")
    parser.feed(rendered_html)
    text = parser.get_text().strip()

    # Fallback: some API renderings may only expose mw-parser-output.
    if not text:
        parser = DivTextExtractor("mw-parser-output")
        parser.feed(rendered_html)
        text = parser.get_text().strip()

    text = html.unescape(text)
    return clean_text(text)


def clean_text(text: str) -> str:
    lines: list[str] = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            lines.append("")
            continue

        # Remove standalone page numbers: 45, ٤٥, ٥٢, etc.
        if re.fullmatch(r"[0-9٠-٩]+", line):
            continue

        # Remove the Arabic proofread status line if it leaks into text.
        if "صُححّت هذه الصفحة" in line:
            continue

        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=None,
    )
    parser.add_argument("--pages", nargs="+", type=int, required=True)
    parser.add_argument("--pdf-title", default=DEFAULT_PDF_TITLE)
    parser.add_argument("--source-id", default=DEFAULT_SOURCE_ID)
    args = parser.parse_args()

    out = Path(args.out or f"data/real_ocr_dataset_v1/wikisource/{args.source_id}")
    html_dir = out / "rendered_html"
    clean_dir = out / "clean_pages"

    html_dir.mkdir(parents=True, exist_ok=True)
    clean_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str | int]] = []

    for page_no in args.pages:
        title = f"صفحة:{args.pdf_title}/{page_no}"
        page_id = f"wiki_pdf_{page_no:03d}"
        page_url = "https://ar.wikisource.org/wiki/" + urllib.parse.quote(title)

        print(f"Fetching page {page_no}: {title}")

        rendered = fetch_rendered_html(title)
        clean = extract_page_text(rendered)

        html_path = html_dir / f"{page_id}.html"
        clean_path = clean_dir / f"{page_id}.txt"

        html_path.write_text(rendered, encoding="utf-8")
        clean_path.write_text(clean, encoding="utf-8")

        rows.append(
            {
                "source_id": args.source_id,
                "pdf_page": page_no,
                "page_id": page_id,
                "url": page_url,
                "rendered_html_path": str(html_path),
                "clean_text_path": str(clean_path),
                "clean_chars": len(clean),
                "verification_level": "wikisource_proofread_unvalidated",
                "notes": "",
            }
        )

        print(f"  clean chars: {len(clean)}")

    manifest = out / "wikisource_pages_manifest.csv"

    with manifest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote manifest: {manifest}")


if __name__ == "__main__":
    main()
