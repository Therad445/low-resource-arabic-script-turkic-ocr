from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from src.data.normalization import normalize_text_v1

REQUIRED_DOC_COLUMNS = {
    "doc_id",
    "source_id",
    "title_short",
    "year",
    "language_note",
    "script_note",
    "print_or_handwritten",
    "scan_quality_bucket",
    "layout_complexity",
    "rights_note",
    "local_storage_note",
    "status",
}

REQUIRED_LINE_COLUMNS = {
    "line_id",
    "doc_id",
    "page_id",
    "source_id",
    "image_relpath",
    "transcription_diplomatic",
    "transcription_normalized",
    "quality_flag",
    "annotator",
    "review_status",
    "notes",
}

ALLOWED_QUALITY_FLAGS = {"", "ok", "needs_review", "illegible", "partial", "damaged"}
ALLOWED_REVIEW_STATUS = {"draft", "reviewed", "frozen"}
ALLOWED_DOC_STATUSES_FOR_LINES = {"pilot", "benchmark"}
ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header.")
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
        return rows, list(reader.fieldnames)


def read_tsv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header.")
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
        return rows, list(reader.fieldnames)


def validate_required_columns(path: Path, fieldnames: list[str], required: set[str]) -> None:
    missing = [col for col in sorted(required) if col not in fieldnames]
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")


def looks_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Validate pilot line annotations against documents.csv metadata."
    )
    ap.add_argument("--documents", required=True, help="Path to documents.csv")
    ap.add_argument("--lines", required=True, help="Path to pilot_lines_v1.tsv")
    ap.add_argument("--show_examples", type=int, default=10)
    args = ap.parse_args()

    documents_path = Path(args.documents)
    lines_path = Path(args.lines)

    doc_rows, doc_fieldnames = read_csv_rows(documents_path)
    line_rows, line_fieldnames = read_tsv_rows(lines_path)

    validate_required_columns(documents_path, doc_fieldnames, REQUIRED_DOC_COLUMNS)
    validate_required_columns(lines_path, line_fieldnames, REQUIRED_LINE_COLUMNS)

    if not doc_rows:
        raise SystemExit("documents.csv has no rows.")
    if not line_rows:
        raise SystemExit("pilot_lines_v1.tsv has no rows.")

    docs_by_id = {row["doc_id"]: row for row in doc_rows}

    seen_line_ids: set[str] = set()
    duplicate_line_ids: list[str] = []
    unknown_doc_ids: list[str] = []
    source_mismatches: list[str] = []
    empty_transcriptions: list[str] = []
    suspicious_paths: list[str] = []
    bad_suffixes: list[str] = []
    invalid_quality_flags: list[str] = []
    invalid_review_statuses: list[str] = []
    non_normalized_diplomatic: list[str] = []
    non_normalized_normalized: list[str] = []
    disallowed_doc_statuses: list[str] = []

    review_counter = Counter()
    quality_counter = Counter()
    doc_counter = Counter()

    for row in line_rows:
        line_id = row["line_id"]
        doc_id = row["doc_id"]

        if line_id in seen_line_ids:
            duplicate_line_ids.append(line_id)
        seen_line_ids.add(line_id)

        if doc_id not in docs_by_id:
            unknown_doc_ids.append(line_id)
            continue

        doc_row = docs_by_id[doc_id]
        doc_counter[doc_id] += 1

        if row["source_id"] != doc_row["source_id"]:
            source_mismatches.append(line_id)

        if not row["transcription_diplomatic"].strip():
            empty_transcriptions.append(line_id)

        if not looks_relative_path(row["image_relpath"]):
            suspicious_paths.append(line_id)
        elif Path(row["image_relpath"]).suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            bad_suffixes.append(line_id)

        if row["quality_flag"] not in ALLOWED_QUALITY_FLAGS:
            invalid_quality_flags.append(line_id)
        quality_counter[row["quality_flag"]] += 1

        if row["review_status"] not in ALLOWED_REVIEW_STATUS:
            invalid_review_statuses.append(line_id)
        review_counter[row["review_status"]] += 1

        if normalize_text_v1(row["transcription_diplomatic"]) != row["transcription_diplomatic"]:
            non_normalized_diplomatic.append(line_id)

        if row["transcription_normalized"]:
            if (
                normalize_text_v1(row["transcription_normalized"])
                != row["transcription_normalized"]
            ):
                non_normalized_normalized.append(line_id)

        if doc_row["status"] not in ALLOWED_DOC_STATUSES_FOR_LINES:
            disallowed_doc_statuses.append(line_id)

    print(f"Rows: {len(line_rows)}")
    print(f"Documents referenced: {len(doc_counter)}")
    print(f"Unique line IDs: {len(seen_line_ids)}")

    if duplicate_line_ids:
        print(f"[ERROR] Duplicate line_id: {len(duplicate_line_ids)}")
        for value in duplicate_line_ids[: args.show_examples]:
            print(" ", value)

    if unknown_doc_ids:
        print(f"[ERROR] Unknown doc_id referenced by lines: {len(unknown_doc_ids)}")
        for value in unknown_doc_ids[: args.show_examples]:
            print(" ", value)

    if source_mismatches:
        print(f"[ERROR] source_id mismatch vs documents.csv: {len(source_mismatches)}")
        for value in source_mismatches[: args.show_examples]:
            print(" ", value)

    if empty_transcriptions:
        print(f"[ERROR] Empty diplomatic transcription: {len(empty_transcriptions)}")
        for value in empty_transcriptions[: args.show_examples]:
            print(" ", value)

    if invalid_quality_flags:
        print(f"[ERROR] Invalid quality_flag: {len(invalid_quality_flags)}")
        for value in invalid_quality_flags[: args.show_examples]:
            print(" ", value)

    if invalid_review_statuses:
        print(f"[ERROR] Invalid review_status: {len(invalid_review_statuses)}")
        for value in invalid_review_statuses[: args.show_examples]:
            print(" ", value)

    if suspicious_paths:
        print(f"[WARN] Suspicious image_relpath: {len(suspicious_paths)}")
        for value in suspicious_paths[: args.show_examples]:
            print(" ", value)

    if bad_suffixes:
        print(f"[WARN] Unusual image suffix: {len(bad_suffixes)}")
        for value in bad_suffixes[: args.show_examples]:
            print(" ", value)

    if non_normalized_diplomatic:
        print(
            f"[INFO] diplomatic transcription changes under normalize_text_v1: "
            f"{len(non_normalized_diplomatic)}"
        )
        for value in non_normalized_diplomatic[: args.show_examples]:
            print(" ", value)

    if non_normalized_normalized:
        print(
            f"[INFO] normalized transcription changes under normalize_text_v1: "
            f"{len(non_normalized_normalized)}"
        )
        for value in non_normalized_normalized[: args.show_examples]:
            print(" ", value)

    if disallowed_doc_statuses:
        print(
            f"[WARN] Lines attached to documents with status outside "
            f"{sorted(ALLOWED_DOC_STATUSES_FOR_LINES)}: {len(disallowed_doc_statuses)}"
        )
        for value in disallowed_doc_statuses[: args.show_examples]:
            print(" ", value)

    print("Review status distribution:")
    for key, value in review_counter.most_common():
        label = key or "<empty>"
        print(f"  {label}: {value}")

    print("Quality flag distribution:")
    for key, value in quality_counter.most_common():
        label = key or "<empty>"
        print(f"  {label}: {value}")

    print("Top documents by annotated lines:")
    for doc_id, count in doc_counter.most_common(10):
        print(f"  {doc_id}: {count}")

    has_errors = any(
        [
            duplicate_line_ids,
            unknown_doc_ids,
            source_mismatches,
            empty_transcriptions,
            invalid_quality_flags,
            invalid_review_statuses,
        ]
    )
    if has_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
