from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

def read_tsv(path: str | Path) -> Dict[str, str]:
    """
    Reads TSV: image_path<TAB>text
    Ignores empty lines and comments starting with '#'.
    """
    path = Path(path)
    mapping: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            img, txt = parts[0].strip(), "\t".join(parts[1:]).strip()
            mapping[img] = txt
    return mapping

def align_gt_pred(gt: Dict[str, str], pred: Dict[str, str]) -> list[Tuple[str, str, str]]:
    """
    Returns list of (image_path, gt_text, pred_text) for intersection keys.
    """
    keys = sorted(set(gt.keys()) & set(pred.keys()))
    return [(k, gt[k], pred[k]) for k in keys]
