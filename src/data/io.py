from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class TsvRow:
    """
    Canonical row for datasets/predictions.

    image_id: stable identifier (preferred). If TSV has only 2 columns, we set image_id=image_path.
    image_path: relative path or stable key.
    text: transcription/prediction text.
    """
    image_id: str
    image_path: str
    text: str


def read_tsv_rows(path: str | Path) -> List[TsvRow]:
    """
    Reads TSV in either of formats:
    - 2 columns: image_path<TAB>text
    - 3 columns: image_id<TAB>image_path<TAB>text

    Ignores empty lines and comments starting with '#'.
    """
    path = Path(path)
    rows: List[TsvRow] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                continue

            if len(parts) == 2:
                image_path = parts[0].strip()
                text = parts[1].strip()
                image_id = image_path
                rows.append(TsvRow(image_id=image_id, image_path=image_path, text=text))
            else:
                image_id = parts[0].strip()
                image_path = parts[1].strip()
                text = "\t".join(parts[2:]).strip()
                rows.append(TsvRow(image_id=image_id, image_path=image_path, text=text))

    return rows


def index_by_id(rows: Iterable[TsvRow]) -> Dict[str, TsvRow]:
    d: Dict[str, TsvRow] = {}
    for r in rows:
        d[r.image_id] = r
    return d


def align_gt_pred(
    gt_rows: List[TsvRow],
    pred_rows: List[TsvRow],
) -> List[Tuple[str, str, str, str]]:
    """
    Align by image_id intersection.
    Returns list of (image_id, image_path, gt_text, pred_text).
    """
    gt = index_by_id(gt_rows)
    pr = index_by_id(pred_rows)
    keys = sorted(set(gt.keys()) & set(pr.keys()))
    return [(k, gt[k].image_path, gt[k].text, pr[k].text) for k in keys]
