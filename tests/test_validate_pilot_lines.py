import subprocess
import sys
from pathlib import Path


def test_validate_pilot_lines_smoke(tmp_path: Path):
    documents = tmp_path / "documents.csv"
    lines = tmp_path / "pilot_lines_v1.tsv"

    documents.write_text(
        "doc_id,source_id,title_short,year,language_note,script_note,print_or_handwritten,"
        "scan_quality_bucket,layout_complexity,rights_note,local_storage_note,status\n"
        "d1,s1,Doc 1,1905,Old Tatar,Arabic script,printed,good,simple,local,stored,pilot\n",
        encoding="utf-8",
    )

    lines.write_text(
        "line_id\tdoc_id\tpage_id\tsource_id\timage_relpath\ttranscription_diplomatic\t"
        "transcription_normalized\tquality_flag\tannotator\treview_status\tnotes\n"
        "l1\td1\tp1\ts1\tprocessed/a.png\tسلام عليكم\tسلام عليكم\tok\tradmir\tdraft\t\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.validate_pilot_lines",
            "--documents",
            str(documents),
            "--lines",
            str(lines),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Rows: 1" in result.stdout
    assert "Unique line IDs: 1" in result.stdout