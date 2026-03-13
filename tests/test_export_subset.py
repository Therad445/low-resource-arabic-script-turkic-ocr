import csv
import subprocess
import sys
from pathlib import Path


def test_export_subset_filters_review_status(tmp_path: Path):
    manifest = tmp_path / "manifest.tsv"
    out = tmp_path / "subset.tsv"

    manifest.write_text(
        "line_id\tdoc_id\tpage_id\tsource_id\timage_relpath\ttranscription_diplomatic\t"
        "transcription_normalized\tquality_flag\tannotator\treview_status\tnotes\n"
        "l1\td1\tp1\ts1\tprocessed/a.png\tسلام عليكم\tسلام عليكم\tok\tradmir\tdraft\t\n"
        "l2\td1\tp1\ts1\tprocessed/b.png\tبسم الله\tبسم الله\tok\tradmir\treviewed\t\n"
        "l3\td2\tp2\ts2\tprocessed/c.png\tالحمد لله\tالحمد لله\tneeds_review\tradmir\tfrozen\t\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.export_subset",
            "--manifest",
            str(manifest),
            "--out",
            str(out),
            "--review_statuses",
            "reviewed,frozen",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Rows: 2" in result.stdout
    assert out.exists()

    with out.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    assert len(rows) == 2
    assert {row["line_id"] for row in rows} == {"l2", "l3"}