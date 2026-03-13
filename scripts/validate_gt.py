from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from src.data.io import read_tsv_rows
from src.data.normalization import INVISIBLE_FORMATTING_MARKS, normalize_text_v1

ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def _looks_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True, help="GT TSV (2 or 3 columns)")
    ap.add_argument("--show_examples", type=int, default=10)
    args = ap.parse_args()

    rows = read_tsv_rows(args.gt)
    if not rows:
        raise SystemExit("No rows found (check file format).")

    seen = set()
    dup_ids: list[str] = []
    empty_text: list[str] = []
    changed_norm: list[tuple[str, str, str]] = []
    invisible_hits = Counter()
    suspicious_paths: list[str] = []
    bad_suffixes: list[str] = []

    for row in rows:
        if row.image_id in seen:
            dup_ids.append(row.image_id)
        seen.add(row.image_id)

        if not row.text.strip():
            empty_text.append(row.image_id)

        if not _looks_relative_path(row.image_path):
            suspicious_paths.append(row.image_path)
        elif Path(row.image_path).suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            bad_suffixes.append(row.image_path)

        for ch in INVISIBLE_FORMATTING_MARKS:
            if ch in row.text:
                invisible_hits[ch] += row.text.count(ch)

        normalized = normalize_text_v1(row.text)
        if normalized != row.text:
            changed_norm.append((row.image_id, row.text, normalized))

    print(f"Rows: {len(rows)}")
    print(f"Unique IDs: {len(seen)}")

    if dup_ids:
        print(f"[WARN] Duplicate image_id: {len(dup_ids)} (showing up to {args.show_examples})")
        for value in dup_ids[: args.show_examples]:
            print(" ", value)

    if empty_text:
        print(f"[WARN] Empty transcription: {len(empty_text)} (showing up to {args.show_examples})")
        for value in empty_text[: args.show_examples]:
            print(" ", value)

    if suspicious_paths:
        print(
            f"[WARN] Suspicious image paths: {len(suspicious_paths)} (showing up to {args.show_examples})"
        )
        for value in suspicious_paths[: args.show_examples]:
            print(" ", value)

    if bad_suffixes:
        print(
            f"[WARN] Unusual image suffixes: {len(bad_suffixes)} (showing up to {args.show_examples})"
        )
        for value in bad_suffixes[: args.show_examples]:
            print(" ", value)

    if invisible_hits:
        print("[WARN] Invisible formatting marks found:")
        for ch, count in invisible_hits.most_common():
            print(f" U+{ord(ch):04X} {repr(ch)}: {count}")

    if changed_norm:
        print(
            f"[INFO] Text differs from normalization v1 in {len(changed_norm)} rows "
            f"(showing up to {args.show_examples})"
        )
        for image_id, raw, normalized in changed_norm[: args.show_examples]:
            print("---", image_id)
            print("RAW: ", raw)
            print("NORM:", normalized)


if __name__ == "__main__":
    main()
