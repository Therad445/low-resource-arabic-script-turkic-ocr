#!/usr/bin/env python3
"""
Audit CSV files for Arabic-script Turkic OCR/post-OCR datasets.

The script is intentionally conservative: it does not decide that a row is wrong.
It creates review queues and summary reports so you can find suspicious batches,
sources, pages and lines faster.

It supports both:
  - existing verified files such as data/postcorrection/real_sanity/real_ocr_sanity.csv
  - future candidate/silver/gold annotation CSVs

Example:
  python3 scripts/audit_real_ocr_dataset.py \
    --input data/postcorrection/real_sanity/real_ocr_sanity.csv \
    --out outputs/real_ocr_audit/current_sanity_90

Outputs:
  audit_report.md
  row_metrics.csv
  suspicious_rows.csv
  priority_review.csv
  source_summary.csv
  page_summary.csv
  batch_summary.csv
  duplicates.csv
  unicode_issues.csv
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
DIGIT_RE = re.compile(r"[0-9\u0660-\u0669\u06F0-\u06F9]")
BIDI_CONTROL_RE = re.compile(r"[\u200E\u200F\u202A-\u202E\u2066-\u2069]")
REPLACEMENT_RE = re.compile("\uFFFD")


TEXT_COL_CANDIDATES = {
    "ocr": ["ocr_text", "noisy", "input", "source_text", "raw_ocr", "ocr"],
    "clean": ["clean_text", "clean", "reference", "target", "gold", "transcription"],
    "source_id": ["source_id", "source", "doc_id", "document_id"],
    "page_id": ["page_id", "page", "page_no", "page_number"],
    "line_id": ["line_id", "id", "sample_id", "row_id"],
    "batch_id": ["batch_id", "batch"],
    "alignment_quality": ["alignment_quality", "quality", "alignment"],
    "verification_level": ["verification_level", "verification", "level"],
}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        seen: list[str] = []
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.append(key)
        fieldnames = seen
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def pick_col(fieldnames: list[str], candidates: list[str]) -> str | None:
    lowered = {f.lower(): f for f in fieldnames}
    for cand in candidates:
        if cand.lower() in lowered:
            return lowered[cand.lower()]
    return None


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def cer(pred: str, ref: str) -> float:
    if not ref:
        return math.nan
    return levenshtein(pred, ref) / len(ref)


def wer(pred: str, ref: str) -> float:
    ref_toks = ref.split()
    pred_toks = pred.split()
    if not ref_toks:
        return math.nan
    return levenshtein_tokens(pred_toks, ref_toks) / len(ref_toks)


def levenshtein_tokens(a: list[str], b: list[str]) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def no_space(s: str) -> str:
    return re.sub(r"\s+", "", s)


def ratio(pattern: re.Pattern[str], text: str) -> float:
    if not text:
        return 0.0
    return len(pattern.findall(text)) / len(text)


def count_pattern(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text))


def control_count(text: str) -> int:
    total = count_pattern(BIDI_CONTROL_RE, text)
    total += sum(1 for ch in text if unicodedata.category(ch).startswith("C") and ch not in "\n\t\r")
    return total


def safe_float(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return math.nan


def mean(values: Iterable[float]) -> float:
    vals = [v for v in values if not math.isnan(v)]
    return statistics.mean(vals) if vals else math.nan


def median(values: Iterable[float]) -> float:
    vals = [v for v in values if not math.isnan(v)]
    return statistics.median(vals) if vals else math.nan


def pct(n: int, d: int) -> str:
    if d == 0:
        return "0.0%"
    return f"{100*n/d:.1f}%"


def analyze(args: argparse.Namespace) -> None:
    input_paths = [Path(p) for p in args.input]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, str]] = []
    all_fields: list[str] = []
    for path in input_paths:
        rows, fields = read_csv(path)
        all_fields = list(dict.fromkeys(all_fields + fields))
        for i, row in enumerate(rows, 1):
            row["_input_file"] = str(path)
            row["_input_row_number"] = str(i)
            all_rows.append(row)

    if not all_rows:
        raise SystemExit("No rows found.")

    ocr_col = args.ocr_col or pick_col(all_fields, TEXT_COL_CANDIDATES["ocr"])
    clean_col = args.clean_col or pick_col(all_fields, TEXT_COL_CANDIDATES["clean"])
    source_col = args.source_col or pick_col(all_fields, TEXT_COL_CANDIDATES["source_id"])
    page_col = args.page_col or pick_col(all_fields, TEXT_COL_CANDIDATES["page_id"])
    line_col = args.line_col or pick_col(all_fields, TEXT_COL_CANDIDATES["line_id"])
    batch_col = args.batch_col or pick_col(all_fields, TEXT_COL_CANDIDATES["batch_id"])
    align_col = args.alignment_col or pick_col(all_fields, TEXT_COL_CANDIDATES["alignment_quality"])
    ver_col = args.verification_col or pick_col(all_fields, TEXT_COL_CANDIDATES["verification_level"])

    if not ocr_col:
        raise SystemExit("Could not find OCR/noisy text column. Pass --ocr-col.")
    if not clean_col:
        raise SystemExit("Could not find clean/reference text column. Pass --clean-col.")

    line_ids = [r.get(line_col, "") for r in all_rows] if line_col else []
    duplicate_line_ids = {x for x, c in Counter(line_ids).items() if x and c > 1}

    pair_keys = [(r.get(ocr_col, ""), r.get(clean_col, "")) for r in all_rows]
    duplicate_pairs = {x for x, c in Counter(pair_keys).items() if x[0] and x[1] and c > 1}

    metrics_rows: list[dict[str, Any]] = []
    suspicious_rows: list[dict[str, Any]] = []
    unicode_rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(all_rows, 1):
        ocr = row.get(ocr_col, "") or ""
        clean = row.get(clean_col, "") or ""
        source_id = row.get(source_col, "unknown") if source_col else "unknown"
        page_id = row.get(page_col, "unknown") if page_col else "unknown"
        batch_id = row.get(batch_col, "unknown") if batch_col else "unknown"
        line_id = row.get(line_col, f"row_{idx}") if line_col else f"row_{idx}"
        align_q = row.get(align_col, "") if align_col else ""
        ver = row.get(ver_col, "") if ver_col else ""

        c = cer(ocr, clean)
        w = wer(ocr, clean)
        nsc = cer(no_space(ocr), no_space(clean)) if clean else math.nan
        len_ocr = len(ocr)
        len_clean = len(clean)
        len_ratio = (len_ocr / len_clean) if len_clean else math.nan

        flags: list[str] = []
        priority = 0

        if not ocr.strip():
            flags.append("missing_ocr_text")
            priority += 10
        if not clean.strip():
            flags.append("missing_clean_text")
            priority += 10
        if len_clean and len_clean < args.min_clean_chars:
            flags.append("very_short_clean")
            priority += 3
        if len_ocr and len_ocr < args.min_ocr_chars:
            flags.append("very_short_ocr")
            priority += 2
        if not math.isnan(len_ratio) and (len_ratio < args.min_len_ratio or len_ratio > args.max_len_ratio):
            flags.append("length_ratio_outlier")
            priority += 6
        if not math.isnan(c) and c > args.high_cer:
            flags.append("high_cer_ocr_vs_clean")
            priority += 5
        if not math.isnan(w) and w > args.high_wer:
            flags.append("high_wer_ocr_vs_clean")
            priority += 4
        if count_pattern(LATIN_RE, ocr + clean) > args.max_latin_chars:
            flags.append("latin_chars_present")
            priority += 4
        if count_pattern(CYRILLIC_RE, ocr + clean) > args.max_cyrillic_chars:
            flags.append("cyrillic_chars_present")
            priority += 4
        if count_pattern(REPLACEMENT_RE, ocr + clean) > 0:
            flags.append("unicode_replacement_char")
            priority += 8
        if control_count(ocr + clean) > 0:
            flags.append("unicode_control_or_bidi_char")
            priority += 5
        if line_id in duplicate_line_ids:
            flags.append("duplicate_line_id")
            priority += 7
        if (ocr, clean) in duplicate_pairs:
            flags.append("duplicate_ocr_clean_pair")
            priority += 3
        if align_q and align_q not in {"good", "gold", "verified"}:
            flags.append(f"alignment_quality_{align_q}")
            priority += 2
        if ver and ver not in {"gold", "verified"}:
            flags.append(f"verification_level_{ver}")
            priority += 1

        arabic_ratio_ocr = ratio(ARABIC_RE, ocr)
        arabic_ratio_clean = ratio(ARABIC_RE, clean)
        if args.expected_script == "arabic":
            if ocr and arabic_ratio_ocr < args.min_arabic_ratio:
                flags.append("low_arabic_ratio_ocr")
                priority += 3
            if clean and arabic_ratio_clean < args.min_arabic_ratio:
                flags.append("low_arabic_ratio_clean")
                priority += 3

        mrow = {
            **row,
            "_audit_index": idx,
            "_source_id": source_id,
            "_page_id": page_id,
            "_batch_id": batch_id,
            "_line_id": line_id,
            "_len_ocr": len_ocr,
            "_len_clean": len_clean,
            "_len_ratio_ocr_to_clean": f"{len_ratio:.6f}" if not math.isnan(len_ratio) else "",
            "_cer_ocr_vs_clean": f"{c:.6f}" if not math.isnan(c) else "",
            "_wer_ocr_vs_clean": f"{w:.6f}" if not math.isnan(w) else "",
            "_no_space_cer_ocr_vs_clean": f"{nsc:.6f}" if not math.isnan(nsc) else "",
            "_arabic_ratio_ocr": f"{arabic_ratio_ocr:.6f}",
            "_arabic_ratio_clean": f"{arabic_ratio_clean:.6f}",
            "_latin_chars": count_pattern(LATIN_RE, ocr + clean),
            "_cyrillic_chars": count_pattern(CYRILLIC_RE, ocr + clean),
            "_digit_chars": count_pattern(DIGIT_RE, ocr + clean),
            "_unicode_control_chars": control_count(ocr + clean),
            "_flags": ";".join(flags),
            "_review_priority": priority,
        }
        metrics_rows.append(mrow)

        if flags:
            suspicious_rows.append(mrow)
        if any(f.startswith("unicode_") for f in flags):
            unicode_rows.append(mrow)
        if "duplicate_line_id" in flags or "duplicate_ocr_clean_pair" in flags:
            duplicate_rows.append(mrow)

    metric_fields = list(metrics_rows[0].keys()) if metrics_rows else []
    write_csv(out / "row_metrics.csv", metrics_rows, metric_fields)
    write_csv(out / "suspicious_rows.csv", suspicious_rows, metric_fields)
    write_csv(out / "unicode_issues.csv", unicode_rows, metric_fields)
    write_csv(out / "duplicates.csv", duplicate_rows, metric_fields)
    priority_rows = sorted(suspicious_rows, key=lambda r: safe_float(r["_review_priority"]), reverse=True)
    write_csv(out / "priority_review.csv", priority_rows, metric_fields)

    def group_summary(group_key: str) -> list[dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in metrics_rows:
            groups[str(r.get(group_key, "unknown"))].append(r)
        rows = []
        for key, items in sorted(groups.items()):
            total = len(items)
            suspicious = sum(1 for r in items if r["_flags"])
            rows.append({
                group_key: key,
                "n": total,
                "suspicious_n": suspicious,
                "suspicious_pct": pct(suspicious, total),
                "mean_cer": f"{mean(safe_float(r['_cer_ocr_vs_clean']) for r in items):.6f}",
                "median_cer": f"{median(safe_float(r['_cer_ocr_vs_clean']) for r in items):.6f}",
                "mean_wer": f"{mean(safe_float(r['_wer_ocr_vs_clean']) for r in items):.6f}",
                "mean_no_space_cer": f"{mean(safe_float(r['_no_space_cer_ocr_vs_clean']) for r in items):.6f}",
                "missing_clean": sum(1 for r in items if "missing_clean_text" in r["_flags"]),
                "high_cer": sum(1 for r in items if "high_cer_ocr_vs_clean" in r["_flags"]),
                "length_outliers": sum(1 for r in items if "length_ratio_outlier" in r["_flags"]),
                "unicode_issues": sum(1 for r in items if "unicode_" in r["_flags"]),
            })
        return rows

    source_summary = group_summary("_source_id")
    page_summary = group_summary("_page_id")
    batch_summary = group_summary("_batch_id")

    write_csv(out / "source_summary.csv", source_summary)
    write_csv(out / "page_summary.csv", page_summary)
    write_csv(out / "batch_summary.csv", batch_summary)

    flag_counter = Counter()
    for r in metrics_rows:
        for f in str(r["_flags"]).split(";"):
            if f:
                flag_counter[f] += 1

    cer_values = [safe_float(r["_cer_ocr_vs_clean"]) for r in metrics_rows]
    wer_values = [safe_float(r["_wer_ocr_vs_clean"]) for r in metrics_rows]
    nsc_values = [safe_float(r["_no_space_cer_ocr_vs_clean"]) for r in metrics_rows]
    total = len(metrics_rows)

    report = []
    report.append("# OCR Dataset Audit Report\n")
    report.append("## Inputs\n")
    for p in input_paths:
        report.append(f"- `{p}`\n")
    report.append("\n## Detected columns\n")
    report.append(f"- OCR/noisy text: `{ocr_col}`\n")
    report.append(f"- clean/reference text: `{clean_col}`\n")
    report.append(f"- source id: `{source_col or 'not found'}`\n")
    report.append(f"- page id: `{page_col or 'not found'}`\n")
    report.append(f"- line id: `{line_col or 'not found'}`\n")
    report.append(f"- batch id: `{batch_col or 'not found'}`\n")
    report.append(f"- alignment quality: `{align_col or 'not found'}`\n")
    report.append(f"- verification level: `{ver_col or 'not found'}`\n")
    report.append("\n## Global summary\n")
    report.append(f"- Rows: **{total}**\n")
    report.append(f"- Suspicious rows: **{len(suspicious_rows)}** ({pct(len(suspicious_rows), total)})\n")
    report.append(f"- Mean CER OCR vs clean: **{mean(cer_values):.6f}**\n")
    report.append(f"- Median CER OCR vs clean: **{median(cer_values):.6f}**\n")
    report.append(f"- Mean WER OCR vs clean: **{mean(wer_values):.6f}**\n")
    report.append(f"- Mean NoSpaceCER OCR vs clean: **{mean(nsc_values):.6f}**\n")
    report.append("\n## Flag counts\n")
    if flag_counter:
        for flag, count in flag_counter.most_common():
            report.append(f"- `{flag}`: {count}\n")
    else:
        report.append("- No flags.\n")

    report.append("\n## How to interpret this report\n")
    report.append("- High CER/WER is not automatically an error: real OCR can be very bad.\n")
    report.append("- `length_ratio_outlier`, missing text, Unicode replacement characters and duplicate IDs should be checked first.\n")
    report.append("- Rows in `priority_review.csv` are sorted by estimated review urgency.\n")
    report.append("- Only rows manually checked as `alignment_quality=good` should enter gold dev/test.\n")

    (out / "audit_report.md").write_text("".join(report), encoding="utf-8")
    print(f"Wrote audit report: {out / 'audit_report.md'}")
    print(f"Suspicious rows: {len(suspicious_rows)} / {total}")
    print(f"Mean CER: {mean(cer_values):.6f}")
    print(f"Mean WER: {mean(wer_values):.6f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", required=True, help="One or more CSV files.")
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument("--ocr-col", default=None)
    parser.add_argument("--clean-col", default=None)
    parser.add_argument("--source-col", default=None)
    parser.add_argument("--page-col", default=None)
    parser.add_argument("--line-col", default=None)
    parser.add_argument("--batch-col", default=None)
    parser.add_argument("--alignment-col", default=None)
    parser.add_argument("--verification-col", default=None)
    parser.add_argument("--expected-script", choices=["arabic", "mixed", "none"], default="arabic")
    parser.add_argument("--min-arabic-ratio", type=float, default=0.45)
    parser.add_argument("--min-clean-chars", type=int, default=8)
    parser.add_argument("--min-ocr-chars", type=int, default=4)
    parser.add_argument("--min-len-ratio", type=float, default=0.35)
    parser.add_argument("--max-len-ratio", type=float, default=2.50)
    parser.add_argument("--high-cer", type=float, default=0.80)
    parser.add_argument("--high-wer", type=float, default=1.80)
    parser.add_argument("--max-latin-chars", type=int, default=0)
    parser.add_argument("--max-cyrillic-chars", type=int, default=0)
    args = parser.parse_args()
    analyze(args)


if __name__ == "__main__":
    main()
