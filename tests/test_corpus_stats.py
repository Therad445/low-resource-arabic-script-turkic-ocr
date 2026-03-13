from pathlib import Path

from scripts.corpus_stats import compute_stats, read_manifest


def test_corpus_stats_smoke(tmp_path: Path):
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(
        "line_id\tdoc_id\tpage_id\tsource_id\timage_relpath\ttranscription_diplomatic\tquality_flag\n"
        "l1\td1\tp1\ts1\tprocessed/a.png\tسلام عليكم\tok\n"
        "l2\td1\tp1\ts1\tprocessed/b.png\tبسم الله\tok\n"
        "l3\td2\tp2\ts2\tprocessed/c.png\tالحمد لله\tneeds_review\n",
        encoding="utf-8",
    )

    rows = read_manifest(manifest)
    stats = compute_stats(rows)

    assert stats["rows"] == 3
    assert stats["documents"] == 2
    assert stats["pages"] == 2
    assert stats["sources"]["s1"] == 2
    assert stats["sources"]["s2"] == 1
    assert stats["quality_flags"]["ok"] == 2
    assert stats["quality_flags"]["needs_review"] == 1
    assert stats["unique_chars"] > 0
