from pathlib import Path

from src.data.io import align_gt_pred, read_tsv_rows


def test_read_tsv_rows_3col(tmp_path: Path):
    p = tmp_path / "gt.tsv"
    p.write_text(
        "# image_id\timage_path\ttranscription\na\timg/a.png\tfoo\nb\timg/b.png\tbar\n",
        encoding="utf-8",
    )
    rows = read_tsv_rows(p)
    assert [r.image_id for r in rows] == ["a", "b"]
    assert rows[0].image_path == "img/a.png"
    assert rows[0].text == "foo"


def test_align_by_id(tmp_path: Path):
    gt = tmp_path / "gt.tsv"
    pr = tmp_path / "pred.tsv"
    gt.write_text("a\timg/a.png\tFOO\nb\timg/b.png\tBAR\n", encoding="utf-8")
    pr.write_text("b\timg/b.png\tbar\nc\timg/c.png\tbaz\n", encoding="utf-8")
    pairs = align_gt_pred(read_tsv_rows(gt), read_tsv_rows(pr))
    assert len(pairs) == 1
    assert pairs[0][0] == "b"
