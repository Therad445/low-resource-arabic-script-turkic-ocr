from __future__ import annotations

import argparse
import csv
from pathlib import Path


def detect_delimiter(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".tsv":
        return "\t"
    if suffix == ".csv":
        return ","
    raise ValueError(f"Unsupported file extension: {suffix}. Use .tsv or .csv")


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str], str]:
    delimiter = detect_delimiter(path)
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header.")
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
        return rows, list(reader.fieldnames), delimiter


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    delimiter = detect_delimiter(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def parse_optional_set(raw: str) -> set[str]:
    return {x.strip() for x in raw.split(",") if x.strip()}


def main() -> None:
    ap = argparse.ArgumentParser(description="Export a filtered subset from a manifest TSV/CSV.")
    ap.add_argument("--manifest", required=True, help="Input manifest (.tsv or .csv)")
    ap.add_argument("--out", required=True, help="Output manifest (.tsv or .csv)")
    ap.add_argument(
        "--review_statuses",
        default="",
        help="Comma-separated review_status filter, e.g. reviewed,frozen",
    )
    ap.add_argument(
        "--quality_flags",
        default="",
        help="Comma-separated quality_flag filter, e.g. ok,needs_review",
    )
    ap.add_argument(
        "--doc_ids",
        default="",
        help="Comma-separated doc_id filter",
    )
    ap.add_argument(
        "--max_rows",
        type=int,
        default=0,
        help="Optional cap on number of exported rows after filtering",
    )
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    out_path = Path(args.out)

    rows, fieldnames, _ = read_rows(manifest_path)

    review_filter = parse_optional_set(args.review_statuses)
    quality_filter = parse_optional_set(args.quality_flags)
    doc_filter = parse_optional_set(args.doc_ids)

    filtered = []
    for row in rows:
        if review_filter and row.get("review_status", "") not in review_filter:
            continue
        if quality_filter and row.get("quality_flag", "") not in quality_filter:
            continue
        if doc_filter and row.get("doc_id", "") not in doc_filter:
            continue
        filtered.append(row)

    filtered.sort(
        key=lambda r: (
            r.get("doc_id", ""),
            r.get("page_id", ""),
            r.get("line_id", ""),
        )
    )

    if args.max_rows > 0:
        filtered = filtered[: args.max_rows]

    if not filtered:
        raise SystemExit("No rows matched the requested filters.")

    write_rows(out_path, filtered, fieldnames)

    print(f"Saved: {out_path}")
    print(f"Rows: {len(filtered)}")
    print(f"Documents: {len({row.get('doc_id', '') for row in filtered})}")


if __name__ == "__main__":
    main()
