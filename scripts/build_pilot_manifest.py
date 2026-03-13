from __future__ import annotations

import argparse
import csv
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

OUTPUT_COLUMNS = [
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
]

ALLOWED_REVIEW_STATUS = {"draft", "reviewed", "frozen"}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header.")
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header.")
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def write_tsv_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def validate_required_columns(path: Path, rows: list[dict[str, str]], required: set[str]) -> None:
    if not rows:
        raise ValueError(f"{path} has no data rows.")
    missing = [col for col in required if col not in rows[0]]
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(sorted(missing))}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build pilot manifest from documents.csv and pilot_lines_v1.tsv"
    )
    ap.add_argument("--documents", required=True, help="Path to documents.csv")
    ap.add_argument("--lines", required=True, help="Path to pilot_lines_v1.tsv")
    ap.add_argument("--out", required=True, help="Output path for line_manifest_pilot_v1.tsv")
    ap.add_argument(
        "--allowed_statuses",
        default="pilot,benchmark",
        help="Comma-separated document statuses to include",
    )
    args = ap.parse_args()

    documents_path = Path(args.documents)
    lines_path = Path(args.lines)
    out_path = Path(args.out)

    doc_rows = read_csv_rows(documents_path)
    line_rows = read_tsv_rows(lines_path)

    validate_required_columns(documents_path, doc_rows, REQUIRED_DOC_COLUMNS)
    validate_required_columns(lines_path, line_rows, REQUIRED_LINE_COLUMNS)

    allowed_statuses = {x.strip() for x in args.allowed_statuses.split(",") if x.strip()}
    docs_by_id = {row["doc_id"]: row for row in doc_rows}
    included_doc_ids = {row["doc_id"] for row in doc_rows if row["status"] in allowed_statuses}

    output_rows: list[dict[str, str]] = []
    seen_line_ids: set[str] = set()

    for row in line_rows:
        doc_id = row["doc_id"]
        line_id = row["line_id"]

        if line_id in seen_line_ids:
            raise ValueError(f"Duplicate line_id in pilot lines: {line_id}")
        seen_line_ids.add(line_id)

        if doc_id not in docs_by_id:
            raise ValueError(f"Line references unknown doc_id: {doc_id}")

        if doc_id not in included_doc_ids:
            continue

        review_status = row["review_status"]
        if review_status not in ALLOWED_REVIEW_STATUS:
            raise ValueError(f"Invalid review_status for {line_id}: {review_status}")

        diplomatic = normalize_text_v1(row["transcription_diplomatic"])
        normalized = normalize_text_v1(row["transcription_normalized"] or diplomatic)

        output_rows.append(
            {
                "line_id": line_id,
                "doc_id": doc_id,
                "page_id": row["page_id"],
                "source_id": row["source_id"],
                "image_relpath": row["image_relpath"],
                "transcription_diplomatic": diplomatic,
                "transcription_normalized": normalized,
                "quality_flag": row["quality_flag"],
                "annotator": row["annotator"],
                "review_status": review_status,
                "notes": row["notes"],
            }
        )

    if not output_rows:
        raise SystemExit("No pilot rows selected. Check document statuses and pilot_lines_v1.tsv.")

    write_tsv_rows(out_path, output_rows, OUTPUT_COLUMNS)
    print(f"Saved: {out_path}")
    print(f"Rows: {len(output_rows)}")
    print(f"Documents: {len({r['doc_id'] for r in output_rows})}")
    print(f"Sources: {len({r['source_id'] for r in output_rows})}")


if __name__ == "__main__":
    main()
