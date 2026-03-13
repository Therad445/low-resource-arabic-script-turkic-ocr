from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REQUIRED_COLUMNS = (
    "line_id",
    "doc_id",
    "page_id",
    "source_id",
    "image_relpath",
    "transcription_diplomatic",
)
OPTIONAL_COLUMNS = (
    "transcription_normalized",
    "quality_flag",
    "notes",
)


@dataclass(frozen=True)
class LineRecord:
    line_id: str
    doc_id: str
    page_id: str
    source_id: str
    image_relpath: str
    transcription_diplomatic: str
    transcription_normalized: str = ""
    quality_flag: str = ""
    notes: str = ""


@dataclass(frozen=True)
class DocumentStats:
    doc_id: str
    source_id: str
    n_pages: int
    n_lines: int


def detect_delimiter(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".tsv":
        return "\t"
    if suffix == ".csv":
        return ","
    raise ValueError(f"Unsupported manifest extension: {suffix}. Use .csv or .tsv")


def _clean_field(value: str | None) -> str:
    return (value or "").strip()


def _row_to_record(row: dict[str, str]) -> LineRecord:
    payload = {key: _clean_field(row.get(key)) for key in (*REQUIRED_COLUMNS, *OPTIONAL_COLUMNS)}
    return LineRecord(**payload)


def read_line_manifest(path: str | Path) -> list[LineRecord]:
    path = Path(path)
    delimiter = detect_delimiter(path)
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError("Manifest has no header row.")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Manifest is missing required columns: {', '.join(missing)}")
        return [_row_to_record(row) for row in reader]


def summarize_documents(records: Iterable[LineRecord]) -> list[DocumentStats]:
    pages_by_doc: dict[str, set[str]] = defaultdict(set)
    lines_by_doc: dict[str, int] = defaultdict(int)
    source_by_doc: dict[str, str] = {}
    for record in records:
        pages_by_doc[record.doc_id].add(record.page_id)
        lines_by_doc[record.doc_id] += 1
        source_by_doc.setdefault(record.doc_id, record.source_id)
    stats = [
        DocumentStats(
            doc_id=doc_id,
            source_id=source_by_doc[doc_id],
            n_pages=len(pages_by_doc[doc_id]),
            n_lines=lines_by_doc[doc_id],
        )
        for doc_id in sorted(lines_by_doc)
    ]
    return stats


def group_records_by_doc(records: Iterable[LineRecord]) -> dict[str, list[LineRecord]]:
    grouped: dict[str, list[LineRecord]] = defaultdict(list)
    for record in records:
        grouped[record.doc_id].append(record)
    return dict(grouped)


def write_split_file(path: str | Path, values: Iterable[str]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for value in values:
            f.write(f"{value}\n")