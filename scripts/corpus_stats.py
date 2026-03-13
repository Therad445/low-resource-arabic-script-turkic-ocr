from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Any


def read_manifest(path: Path) -> list[dict[str, str]]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header")
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
    return rows


def compute_stats(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("Manifest is empty")

    documents = {row["doc_id"] for row in rows}
    pages = {row["page_id"] for row in rows}
    sources = Counter(row["source_id"] for row in rows)
    quality = Counter(row.get("quality_flag", "") for row in rows)

    text_lengths = [len(row["transcription_diplomatic"]) for row in rows]
    word_lengths = [len(row["transcription_diplomatic"].split()) for row in rows]

    char_counter = Counter()
    doc_line_counter = Counter()

    for row in rows:
        char_counter.update(row["transcription_diplomatic"])
        doc_line_counter[row["doc_id"]] += 1

    stats: dict[str, Any] = {
        "rows": len(rows),
        "documents": len(documents),
        "pages": len(pages),
        "sources": dict(sorted(sources.items())),
        "quality_flags": dict(sorted(quality.items())),
        "avg_chars_per_line": mean(text_lengths),
        "median_chars_per_line": median(text_lengths),
        "avg_words_per_line": mean(word_lengths),
        "median_words_per_line": median(word_lengths),
        "unique_chars": len(char_counter),
        "top_chars": char_counter.most_common(20),
        "top_docs_by_lines": doc_line_counter.most_common(20),
    }
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute corpus statistics from a line manifest.")
    ap.add_argument("--manifest", required=True, help="Path to TSV/CSV manifest")
    ap.add_argument("--json_out", default="", help="Optional path to save stats as JSON")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    rows = read_manifest(manifest_path)
    stats = compute_stats(rows)

    print(f"Rows: {stats['rows']}")
    print(f"Documents: {stats['documents']}")
    print(f"Pages: {stats['pages']}")
    print(f"Unique chars: {stats['unique_chars']}")
    print(f"Avg chars/line: {stats['avg_chars_per_line']:.2f}")
    print(f"Median chars/line: {stats['median_chars_per_line']:.2f}")
    print("Sources:")
    for key, value in stats["sources"].items():
        print(f"  {key}: {value}")
    print("Quality flags:")
    for key, value in stats["quality_flags"].items():
        label = key or "<empty>"
        print(f"  {label}: {value}")
    print("Top chars:")
    for ch, count in stats["top_chars"][:10]:
        print(f"  {repr(ch)}: {count}")

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved JSON: {out_path}")


if __name__ == "__main__":
    main()
