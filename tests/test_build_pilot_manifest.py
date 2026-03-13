import csv
import subprocess
import sys
from pathlib import Path


def test_build_pilot_manifest_smoke(tmp_path: Path):
    documents = tmp_path / "documents.csv"
    lines = tmp_path / "pilot_lines_v1.tsv"
    out = tmp_path / "line_manifest_pilot_v1.tsv"

    documents.write_text(
        "doc_id,source_id,title_short,year,language_note,script_note,print_or_handwritten,"
        "scan_quality_bucket,layout_complexity,rights_note,local_storage_note,status\n"
        "d1,s1,Doc 1,1905,Old Tatar,Arabic script,printed,good,simple,local,stored,pilot\n"
        "d2,s2,Doc 2,1908,Old Tatar,Arabic script,printed,medium,simple,local,stored,candidate\n",
        encoding="utf-8",
    )

    lines.write_text(
        "line_id\tdoc_id\tpage_id\tsource_id\timage_relpath\ttranscription_diplomatic\t"
        "transcription_normalized\tquality_flag\tannotator\treview_status\tnotes\n"
        "l1\td1\tp1\ts1\tprocessed/a.png\tسلام عليكم\tسلام عليكم\tok\tradmir\tdraft\t\n"
        "l2\td2\tp2\ts2\tprocessed/b.png\tبسم الله\tبسم الله\tok\tradmir\treviewed\t\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.build_pilot_manifest",
            "--documents",
            str(documents),
            "--lines",
            str(lines),
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Rows: 1" in result.stdout
    assert out.exists()

    with out.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["doc_id"] == "d1"
    assert rows[0]["line_id"] == "l1"
