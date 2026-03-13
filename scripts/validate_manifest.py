from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from src.data.manifest import read_line_manifest, summarize_documents
from src.data.normalization import normalize_text_v1

ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
ALLOWED_QUALITY_FLAGS = {"", "ok", "needs_review", "illegible", "partial", "damaged"}


def _validate_relpath(path_value: str) -> bool:
    path = Path(path_value)
    return not path.is_absolute() and ".." not in path.parts


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate line-level dataset manifest.")
    ap.add_argument("--manifest", required=True, help="Path to line manifest (.csv or .tsv)")
    ap.add_argument("--show_examples", type=int, default=10)
    args = ap.parse_args()

    records = read_line_manifest(args.manifest)
    if not records:
        raise SystemExit("Manifest is empty.")

    line_ids: set[str] = set()
    duplicate_line_ids: list[str] = []
    empty_transcriptions: list[str] = []
    suspicious_paths: list[str] = []
    bad_suffixes: list[str] = []
    non_normalized: list[str] = []
    quality_flags = Counter()
    weird_quality_flags: list[str] = []
    doc_to_source: dict[str, str] = {}
    doc_source_conflicts: list[str] = []

    for record in records:
        if record.line_id in line_ids:
            duplicate_line_ids.append(record.line_id)
        line_ids.add(record.line_id)

        if not record.transcription_diplomatic.strip():
            empty_transcriptions.append(record.line_id)

        if not _validate_relpath(record.image_relpath):
            suspicious_paths.append(record.image_relpath)
        elif Path(record.image_relpath).suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            bad_suffixes.append(record.image_relpath)

        if normalize_text_v1(record.transcription_diplomatic) != record.transcription_diplomatic:
            non_normalized.append(record.line_id)

        quality_flags[record.quality_flag] += 1
        if record.quality_flag not in ALLOWED_QUALITY_FLAGS:
            weird_quality_flags.append(record.line_id)

        existing = doc_to_source.setdefault(record.doc_id, record.source_id)
        if existing != record.source_id:
            doc_source_conflicts.append(record.doc_id)

    stats = summarize_documents(records)
    print(f"Rows: {len(records)}")
    print(f"Documents: {len(stats)}")
    print(f"Sources: {len({r.source_id for r in records})}")
    print(f"Pages: {len({r.page_id for r in records})}")
    print(f"Median lines per document: {sorted(s.n_lines for s in stats)[len(stats) // 2]}")

    if duplicate_line_ids:
        print(f"[WARN] Duplicate line_id: {len(duplicate_line_ids)}")
        for value in duplicate_line_ids[: args.show_examples]:
            print(" ", value)
    if empty_transcriptions:
        print(f"[WARN] Empty diplomatic transcription: {len(empty_transcriptions)}")
        for value in empty_transcriptions[: args.show_examples]:
            print(" ", value)
    if suspicious_paths:
        print(f"[WARN] Suspicious image_relpath: {len(suspicious_paths)}")
        for value in suspicious_paths[: args.show_examples]:
            print(" ", value)
    if bad_suffixes:
        print(f"[WARN] Unusual image suffix: {len(bad_suffixes)}")
        for value in bad_suffixes[: args.show_examples]:
            print(" ", value)
    if non_normalized:
        print(f"[INFO] Transcriptions changed by normalize_text_v1: {len(non_normalized)}")
        for value in non_normalized[: args.show_examples]:
            print(" ", value)
    if weird_quality_flags:
        print(f"[WARN] Unknown quality_flag values in {len(weird_quality_flags)} rows")
        for value in weird_quality_flags[: args.show_examples]:
            print(" ", value)
    if doc_source_conflicts:
        print(f"[WARN] Documents mapped to multiple sources: {len(set(doc_source_conflicts))}")
        for value in sorted(set(doc_source_conflicts))[: args.show_examples]:
            print(" ", value)

    print("Quality flag distribution:")
    for flag, count in quality_flags.most_common():
        label = flag or "<empty>"
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
