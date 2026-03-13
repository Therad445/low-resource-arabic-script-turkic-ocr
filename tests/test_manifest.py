from pathlib import Path

from src.data.manifest import read_line_manifest, summarize_documents
from src.data.normalization import normalize_text_v1


def test_read_line_manifest_tsv(tmp_path: Path):
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(
        "line_id\tdoc_id\tpage_id\tsource_id\timage_relpath\ttranscription_diplomatic\tquality_flag\n"
        "l1\td1\tp1\ts1\tprocessed/a.png\tسلام\tok\n"
        "l2\td1\tp1\ts1\tprocessed/b.png\tعليكم\tneeds_review\n",
        encoding="utf-8",
    )

    rows = read_line_manifest(manifest)
    assert len(rows) == 2
    assert rows[0].line_id == "l1"
    assert rows[1].quality_flag == "needs_review"

    stats = summarize_documents(rows)
    assert stats[0].doc_id == "d1"
    assert stats[0].n_pages == 1
    assert stats[0].n_lines == 2


def test_normalize_text_v1_removes_invisible_marks():
    assert normalize_text_v1("a\u200fb") == "ab"
    assert normalize_text_v1("  سلام   عليكم ") == "سلام عليكم"
